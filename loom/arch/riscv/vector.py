# Copyright (c) 2026 Najmos Sakib / VectorCore Holdings, LLC.
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
RISC-V Vector Extension (RVV 1.0) Execution Engine.
===================================================
Models the 32 vector registers (v0-v31), vector CSRs (vtype, vl, vlenb),
vector configuration (vsetvli), and SIMD/vectorized arithmetic operations.

Reference:
- RISC-V "V" Vector Extension Specification Version 1.0 (2021).
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Dict, List, Optional, Tuple, Union


class VectorSew(IntEnum):
    SEW_8 = 8    # 8-bit elements
    SEW_16 = 16  # 16-bit elements
    SEW_32 = 32  # 32-bit elements
    SEW_64 = 64  # 64-bit elements


class VectorLmul(IntEnum):
    LMUL_1 = 1
    LMUL_2 = 2
    LMUL_4 = 4
    LMUL_8 = 8


class RiscvVectorUnit:
    """Implements RVV 1.0 Vector Processing Unit with 32 vector registers."""

    def __init__(self, vlen_bits: int = 128, elen_bits: int = 64):
        self.vlen_bits = vlen_bits
        self.vlen_bytes = vlen_bits // 8
        self.elen_bits = elen_bits
        
        # 32 Vector registers, each of vlen_bytes
        self.vregs = [bytearray(self.vlen_bytes) for _ in range(32)]
        
        # Vector CSRs
        self.vsew = VectorSew.SEW_32
        self.vlmul = VectorLmul.LMUL_1
        self.vl = 0
        self.vstart = 0
        self.vlenb = self.vlen_bytes

    def vsetvli(self, avl: int, vsew: VectorSew, vlmul: VectorLmul) -> int:
        """Configures vector type and computes active vector length (vl)."""
        self.vsew = vsew
        self.vlmul = vlmul
        elem_bytes = vsew // 8
        vlmax = (self.vlen_bytes * int(vlmul)) // elem_bytes
        
        if avl <= vlmax:
            self.vl = avl
        elif avl < 2 * vlmax:
            self.vl = (avl + 1) // 2
        else:
            self.vl = vlmax
        return self.vl

    def write_elements(self, reg_idx: int, values: List[Union[int, float]]) -> None:
        """Writes up to vl elements into vector register."""
        reg = self.vregs[reg_idx & 0x1F]
        elem_bytes = self.vsew // 8
        
        for i, val in enumerate(values[:self.vl]):
            offset = i * elem_bytes
            if offset + elem_bytes > self.vlen_bytes:
                break
            if self.vsew == VectorSew.SEW_8:
                struct.pack_into("<B", reg, offset, int(val) & 0xFF)
            elif self.vsew == VectorSew.SEW_16:
                struct.pack_into("<H", reg, offset, int(val) & 0xFFFF)
            elif self.vsew == VectorSew.SEW_32:
                if isinstance(val, float):
                    struct.pack_into("<f", reg, offset, val)
                else:
                    struct.pack_into("<I", reg, offset, int(val) & 0xFFFFFFFF)
            elif self.vsew == VectorSew.SEW_64:
                if isinstance(val, float):
                    struct.pack_into("<d", reg, offset, val)
                else:
                    struct.pack_into("<Q", reg, offset, int(val) & 0xFFFFFFFFFFFFFFFF)

    def read_elements(self, reg_idx: int, as_float: bool = False) -> List[Any]:
        """Reads up to vl elements from vector register."""
        reg = self.vregs[reg_idx & 0x1F]
        elem_bytes = self.vsew // 8
        elements = []
        
        for i in range(self.vl):
            offset = i * elem_bytes
            if offset + elem_bytes > self.vlen_bytes:
                break
            if self.vsew == VectorSew.SEW_8:
                elements.append(struct.unpack_from("<B", reg, offset)[0])
            elif self.vsew == VectorSew.SEW_16:
                elements.append(struct.unpack_from("<H", reg, offset)[0])
            elif self.vsew == VectorSew.SEW_32:
                fmt = "<f" if as_float else "<I"
                elements.append(struct.unpack_from(fmt, reg, offset)[0])
            elif self.vsew == VectorSew.SEW_64:
                fmt = "<d" if as_float else "<Q"
                elements.append(struct.unpack_from(fmt, reg, offset)[0])
        return elements

    def execute_vadd(self, vd: int, vs1: int, vs2: int, as_float: bool = False) -> None:
        """Executes elementwise vector addition: vd[i] = vs1[i] + vs2[i]."""
        e1 = self.read_elements(vs1, as_float=as_float)
        e2 = self.read_elements(vs2, as_float=as_float)
        res = [a + b for a, b in zip(e1, e2)]
        self.write_elements(vd, res)

    def execute_vsub(self, vd: int, vs1: int, vs2: int, as_float: bool = False) -> None:
        """Executes elementwise vector subtraction: vd[i] = vs1[i] - vs2[i]."""
        e1 = self.read_elements(vs1, as_float=as_float)
        e2 = self.read_elements(vs2, as_float=as_float)
        res = [a - b for a, b in zip(e1, e2)]
        self.write_elements(vd, res)

    def execute_vmul(self, vd: int, vs1: int, vs2: int, as_float: bool = False) -> None:
        """Executes elementwise vector multiplication: vd[i] = vs1[i] * vs2[i]."""
        e1 = self.read_elements(vs1, as_float=as_float)
        e2 = self.read_elements(vs2, as_float=as_float)
        res = [a * b for a, b in zip(e1, e2)]
        self.write_elements(vd, res)

    def execute_vdot(self, vs1: int, vs2: int, as_float: bool = False) -> Union[int, float]:
        """Executes vector dot product reduction: sum(vs1[i] * vs2[i])."""
        e1 = self.read_elements(vs1, as_float=as_float)
        e2 = self.read_elements(vs2, as_float=as_float)
        return sum(a * b for a, b in zip(e1, e2))
