# Copyright (c) 2026 Najmos Sakib / VectorCore Holdings, LLC.
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
RISC-V 64-bit Architecture Definitions, Registers, Privilege & PMP.
===================================================================
Models RV64 privileged architecture, register files, CSRs, traps, and memory protection.
Specifications referenced:
- RISC-V Instruction Set Manual, Volume I: User-Level ISA (Document Version 20191213).
- RISC-V Instruction Set Manual, Volume II: Privileged Architecture (Version 20211203).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Any, Dict, List, Optional, Tuple

ABI_REG_NAMES = [
    "zero", "ra", "sp", "gp", "tp", "t0", "t1", "t2",
    "s0", "s1", "a0", "a1", "a2", "a3", "a4", "a5",
    "a6", "a7", "s2", "s3", "s4", "s5", "s6", "s7",
    "s8", "s9", "s10", "s11", "t3", "t4", "t5", "t6",
]


class PrivilegeMode(IntEnum):
    USER = 0
    SUPERVISOR = 1
    MACHINE = 3


class TrapCause(IntEnum):
    INSTRUCTION_ADDRESS_MISALIGNED = 0
    INSTRUCTION_ACCESS_FAULT = 1
    ILLEGAL_INSTRUCTION = 2
    BREAKPOINT = 3
    LOAD_ADDRESS_MISALIGNED = 4
    LOAD_ACCESS_FAULT = 5
    STORE_ADDRESS_MISALIGNED = 6
    STORE_ACCESS_FAULT = 7
    ENVIRONMENT_CALL_FROM_U_MODE = 8
    ENVIRONMENT_CALL_FROM_S_MODE = 9
    ENVIRONMENT_CALL_FROM_M_MODE = 11
    INSTRUCTION_PAGE_FAULT = 12
    LOAD_PAGE_FAULT = 13
    STORE_PAGE_FAULT = 15


@dataclass
class PmpEntry:
    """Physical Memory Protection (PMP) entry enforcing access boundaries."""
    base_addr: int
    size_bytes: int
    read: bool = True
    write: bool = True
    execute: bool = False
    locked: bool = False

    def allows(self, addr: int, size: int, is_write: bool, is_exec: bool) -> bool:
        if self.base_addr <= addr and (addr + size) <= (self.base_addr + self.size_bytes):
            if is_exec and not self.execute: return False
            if is_write and not self.write: return False
            if not is_write and not is_exec and not self.read: return False
            return True
        return False


class RiscvRegisterFile:
    """Standard 32 general-purpose 64-bit integer registers (x0 hardwired to 0)."""

    def __init__(self):
        self._regs = [0] * 32

    def read(self, reg_idx: int) -> int:
        if reg_idx == 0:
            return 0
        return self._regs[reg_idx & 0x1F]

    def write(self, reg_idx: int, value: int) -> None:
        if reg_idx == 0:
            return # x0 is hardwired zero
        # 64-bit clamp
        self._regs[reg_idx & 0x1F] = value & 0xFFFFFFFFFFFFFFFF

    def dump(self) -> Dict[str, str]:
        return {f"{ABI_REG_NAMES[i]} (x{i})": f"0x{self._regs[i]:016X}" for i in range(32)}
