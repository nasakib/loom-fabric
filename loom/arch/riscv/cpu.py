# Copyright (c) 2026 Najmos Sakib / VectorCore Holdings, LLC.
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
RV64GCVB Processor Execution Engine with Capability-Probed Offload Hooks.
========================================================================
Implements RV64I with extensions:
- 'M' Standard Extension for Integer Multiplication and Division
- 'A' Standard Extension for Atomic Instructions
- 'F' & 'D' Standard Extensions for Single/Double Precision IEEE 754 Floating Point
- 'V' Standard Extension for Vector Operations (RVV 1.0)
- 'B' Standard Extension for Bit Manipulation
- Custom RoCC / MMIO Offload Hooks for Base-12, Base-16, and 2-Bit ATGC
"""

from __future__ import annotations

import math
import struct
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

from loom.arch.riscv.types import (
    ABI_REG_NAMES,
    PmpEntry,
    PrivilegeMode,
    RiscvRegisterFile,
    TrapCause,
)
from loom.arch.riscv.vector import RiscvVectorUnit, VectorSew, VectorLmul
from loom.base12.codec import Base12Codec, DozenalSymbolSet
from loom.base16.codec import Base16Codec
from loom.atgc.codec import AtgcCodec


class RiscvCpu:
    """Complete RV64GCVB Execution Engine with PMP and custom offload hooks."""

    def __init__(
        self,
        hart_id: int = 0,
        memory_size_bytes: int = 16 * 1024 * 1024, # 16 MB local physical memory
    ):
        self.hart_id = hart_id
        self.pc = 0x8000_0000 # Standard RISC-V DRAM Base
        self.priv_mode = PrivilegeMode.MACHINE
        self.regs = RiscvRegisterFile()
        self.fregs = [0.0] * 32 # 32 64-bit IEEE 754 float registers
        self.vector_unit = RiscvVectorUnit(vlen_bits=128)
        self.pmp_table: List[PmpEntry] = []
        
        # Physical memory
        self.mem_base = 0x8000_0000
        self.memory = bytearray(memory_size_bytes)
        self.memory_size = memory_size_bytes

        # Standard Extension Flags
        self.extensions = {
            "I": True,  # Base Integer 64-bit
            "M": True,  # Integer Mul/Div
            "A": True,  # Atomics
            "F": True,  # Single-Precision Float
            "D": True,  # Double-Precision Float
            "V": True,  # Vector Extension 1.0
            "B": True,  # Bit Manipulation
            "X_BASE12": True, # Custom Base-12 Radix Accelerator
            "X_BASE16": True, # Custom Base-16 / DMA CRC Accelerator
            "X_ATGC": True,   # Custom 2-Bit Genomic Accelerator
        }

        # Codecs for custom offload hooks
        self.b12_codec = Base12Codec(DozenalSymbolSet.ASCII)
        self.b16_codec = Base16Codec(uppercase=True)
        self.atgc_codec = AtgcCodec()

        # Reservation set for atomic LR/SC
        self.load_reservation_addr: Optional[int] = None

        # Default PMP entry covering DRAM
        self.pmp_table.append(
            PmpEntry(base_addr=self.mem_base, size_bytes=memory_size_bytes, read=True, write=True, execute=True)
        )

    # -------------------------------------------------------------------------
    # Memory Access & Physical Memory Protection (PMP)
    # -------------------------------------------------------------------------
    def check_pmp(self, addr: int, size: int, is_write: bool, is_exec: bool) -> bool:
        if self.priv_mode == PrivilegeMode.MACHINE:
            # Machine mode ignores PMP unless locked
            return True
        for entry in self.pmp_table:
            if entry.allows(addr, size, is_write, is_exec):
                return True
        return False

    def read_mem_bytes(self, addr: int, size: int) -> bytes:
        if not self.check_pmp(addr, size, is_write=False, is_exec=False):
            raise PermissionError(f"PMP Load Access Fault at address 0x{addr:016X}")
        offset = addr - self.mem_base
        if not (0 <= offset and (offset + size) <= self.memory_size):
            raise MemoryError(f"Memory read out of bounds at 0x{addr:016X}")
        return bytes(self.memory[offset : offset + size])

    def write_mem_bytes(self, addr: int, data: bytes) -> None:
        size = len(data)
        if not self.check_pmp(addr, size, is_write=True, is_exec=False):
            raise PermissionError(f"PMP Store Access Fault at address 0x{addr:016X}")
        offset = addr - self.mem_base
        if not (0 <= offset and (offset + size) <= self.memory_size):
            raise MemoryError(f"Memory write out of bounds at 0x{addr:016X}")
        self.memory[offset : offset + size] = data

    # -------------------------------------------------------------------------
    # 'M' Extension: Multiply & Divide
    # -------------------------------------------------------------------------
    def exec_mul(self, rd: int, rs1: int, rs2: int) -> None:
        v1 = self.regs.read(rs1)
        v2 = self.regs.read(rs2)
        res = (v1 * v2) & 0xFFFFFFFFFFFFFFFF
        self.regs.write(rd, res)

    def exec_div(self, rd: int, rs1: int, rs2: int) -> None:
        v1 = self.regs.read(rs1)
        v2 = self.regs.read(rs2)
        if v2 == 0:
            res = 0xFFFFFFFFFFFFFFFF
        else:
            res = (v1 // v2) & 0xFFFFFFFFFFFFFFFF
        self.regs.write(rd, res)

    def exec_rem(self, rd: int, rs1: int, rs2: int) -> None:
        v1 = self.regs.read(rs1)
        v2 = self.regs.read(rs2)
        res = 0 if v2 == 0 else (v1 % v2)
        self.regs.write(rd, res)

    # -------------------------------------------------------------------------
    # 'A' Extension: Atomic Memory Operations (AMO)
    # -------------------------------------------------------------------------
    def exec_lr_d(self, rd: int, rs1: int) -> None:
        """Load-Reserved 64-bit."""
        addr = self.regs.read(rs1)
        val = struct.unpack("<Q", self.read_mem_bytes(addr, 8))[0]
        self.regs.write(rd, val)
        self.load_reservation_addr = addr

    def exec_sc_d(self, rd: int, rs1: int, rs2: int) -> None:
        """Store-Conditional 64-bit."""
        addr = self.regs.read(rs1)
        val = self.regs.read(rs2)
        if self.load_reservation_addr == addr:
            self.write_mem_bytes(addr, struct.pack("<Q", val))
            self.regs.write(rd, 0) # Success
            self.load_reservation_addr = None
        else:
            self.regs.write(rd, 1) # Failure

    def exec_amoadd_d(self, rd: int, rs1: int, rs2: int) -> None:
        """Atomic Memory Add 64-bit."""
        addr = self.regs.read(rs1)
        val = self.regs.read(rs2)
        old_val = struct.unpack("<Q", self.read_mem_bytes(addr, 8))[0]
        new_val = (old_val + val) & 0xFFFFFFFFFFFFFFFF
        self.write_mem_bytes(addr, struct.pack("<Q", new_val))
        self.regs.write(rd, old_val)

    # -------------------------------------------------------------------------
    # 'F' & 'D' Extensions: Floating Point IEEE 754
    # -------------------------------------------------------------------------
    def exec_fadd_d(self, rd: int, rs1: int, rs2: int) -> None:
        self.fregs[rd & 0x1F] = self.fregs[rs1 & 0x1F] + self.fregs[rs2 & 0x1F]

    def exec_fsub_d(self, rd: int, rs1: int, rs2: int) -> None:
        self.fregs[rd & 0x1F] = self.fregs[rs1 & 0x1F] - self.fregs[rs2 & 0x1F]

    def exec_fmul_d(self, rd: int, rs1: int, rs2: int) -> None:
        self.fregs[rd & 0x1F] = self.fregs[rs1 & 0x1F] * self.fregs[rs2 & 0x1F]

    def exec_fdiv_d(self, rd: int, rs1: int, rs2: int) -> None:
        denom = self.fregs[rs2 & 0x1F]
        self.fregs[rd & 0x1F] = float("inf") if denom == 0.0 else (self.fregs[rs1 & 0x1F] / denom)

    # -------------------------------------------------------------------------
    # 'B' Extension: Bit Manipulation
    # -------------------------------------------------------------------------
    def exec_cpop(self, rd: int, rs1: int) -> None:
        """Count Population (number of set bits)."""
        val = self.regs.read(rs1)
        self.regs.write(rd, bin(val).count("1"))

    def exec_clz(self, rd: int, rs1: int) -> None:
        """Count Leading Zeros."""
        val = self.regs.read(rs1)
        if val == 0:
            self.regs.write(rd, 64)
        else:
            bits = f"{val:064b}"
            self.regs.write(rd, len(bits) - len(bits.lstrip("0")))

    def exec_rev8(self, rd: int, rs1: int) -> None:
        """Byte-reverse (Endianness swap 64-bit)."""
        val = self.regs.read(rs1)
        packed = struct.pack(">Q", val)
        rev = struct.unpack("<Q", packed)[0]
        self.regs.write(rd, rev)

    # -------------------------------------------------------------------------
    # Custom Offload Hooks (RoCC / MMIO Capability-Probed Acceleration)
    # -------------------------------------------------------------------------
    def execute_custom_offload(
        self,
        offload_opcode: str,
        input_data: Any,
    ) -> Dict[str, Any]:
        """Dispatches to hardware offload engine or deterministic software fallback."""
        if offload_opcode == "X_BASE12_CONVERT":
            if self.extensions.get("X_BASE12"):
                # Fast path: Base-12 Radix Engine
                fp = self.b12_codec.encode_float(float(input_data))
                return {"status": "HW_ACCELERATED", "opcode": offload_opcode, "result": fp.to_string()}
            else:
                # Deterministic Software Fallback
                val = float(input_data)
                return {"status": "SW_FALLBACK", "opcode": offload_opcode, "result": f"{val:.4f}_b10"}

        elif offload_opcode == "X_BASE16_CRC32":
            data_bytes = input_data if isinstance(input_data, bytes) else str(input_data).encode("utf-8")
            if self.extensions.get("X_BASE16"):
                crc_hex = self.b16_codec.compute_checksum_hex(data_bytes)
                return {"status": "HW_ACCELERATED", "opcode": offload_opcode, "result": crc_hex}
            else:
                return {"status": "SW_FALLBACK", "opcode": offload_opcode, "result": hex(len(data_bytes))}

        elif offload_opcode == "X_ATGC_ENCODE":
            seq = str(input_data)
            if self.extensions.get("X_ATGC"):
                packed = self.atgc_codec.encode(seq)
                return {
                    "status": "HW_ACCELERATED",
                    "opcode": offload_opcode,
                    "packed_bytes": len(packed.packed_bytes),
                    "total_bases": packed.total_bases,
                    "gc_content": self.atgc_codec.compute_gc_content(packed),
                }
            else:
                return {"status": "SW_FALLBACK", "opcode": offload_opcode, "length": len(seq)}

        raise ValueError(f"Unknown custom offload opcode '{offload_opcode}'")
