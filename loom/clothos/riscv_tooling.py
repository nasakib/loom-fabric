# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
ClothOS RISC-V Tooling & Assembly Generator (`loom/clothos/riscv_tooling.py`).
Provides:
1. Deep AST & instruction parsing for RISC-V assembly (.s / .asm / .riscv).
2. Classification of instructions across RV64I (Base), RV64M (Multiply), RV64F/D (Float), RV64V (Vector), and RoCC TPU Systolic opcodes.
3. Automated template generation for RISC-V compute kernels: Matrix Multiply, TPU Systolic Wavefront, Vector Add, and Fibonacci.
"""

from __future__ import annotations

import os
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Set, Tuple


# Known RISC-V Instruction Sets
RV64I_INSTRUCTIONS: Set[str] = {
    "add", "addi", "sub", "lui", "auipc", "jal", "jalr", "beq", "bne", "blt", "bge",
    "bltu", "bgeu", "lb", "lh", "lw", "ld", "lbu", "lhu", "lwu", "sb", "sh", "sw", "sd",
    "sll", "slli", "srl", "srli", "sra", "srai", "slt", "slti", "sltu", "sltiu",
    "xor", "xori", "or", "ori", "and", "andi", "fence", "ecall", "ebreak",
    # Pseudo-instructions
    "nop", "li", "la", "mv", "not", "neg", "negw", "sext.w", "seqz", "snez", "sltz", "sgtz",
    "j", "jr", "ret", "call", "tail"
}

RV64M_INSTRUCTIONS: Set[str] = {
    "mul", "mulh", "mulhsu", "mulhu", "div", "divu", "rem", "remu",
    "mulw", "divw", "divuw", "remw", "remuw"
}

RV64FD_INSTRUCTIONS: Set[str] = {
    "flw", "fsw", "fld", "fsd", "fadd.s", "fsub.s", "fmul.s", "fdiv.s", "fsqrt.s",
    "fadd.d", "fsub.d", "fmul.d", "fdiv.d", "fsqrt.d", "fmadd.s", "fmsub.s", "fmadd.d", "fmsub.d"
}

RV64V_INSTRUCTIONS: Set[str] = {
    "vsetvli", "vsetivli", "vsetvl", "vle8.v", "vle16.v", "vle32.v", "vle64.v",
    "vse8.v", "vse16.v", "vse32.v", "vse64.v", "vadd.vv", "vadd.vx", "vadd.vi",
    "vsub.vv", "vsub.vx", "vmul.vv", "vmul.vx", "vfmacc.vv", "vfmacc.vf"
}

ROCC_TPU_OPCODES: Set[str] = {
    "tpu_load_weights", "tpu_matmul_acc", "tpu_activate_relu", "tpu_sync_ub", "tpu_landauer_cool",
    "custom0", "custom1", "custom2", "custom3"
}


def inspect_riscv_code(source_or_path: str | Path) -> Dict[str, Any]:
    """
    Parses and analyzes RISC-V assembly source code.
    Identifies labels, sections, register utilization, and instruction breakdown by family.
    """
    if isinstance(source_or_path, Path) or (isinstance(source_or_path, str) and "\n" not in source_or_path and Path(source_or_path).exists()):
        p = Path(source_or_path)
        raw_text = p.read_text(encoding="utf-8", errors="replace")
        filename = p.name
    else:
        raw_text = str(source_or_path)
        filename = "<inline_asm>"

    lines = raw_text.splitlines()
    labels: List[str] = []
    sections: List[str] = []
    instructions_found: List[Dict[str, str]] = []
    reg_usage: Dict[str, int] = {}

    category_counts: Dict[str, int] = {
        "RV64I (Base Integer)": 0,
        "RV64M (Multiply/Divide)": 0,
        "RV64FD (Floating Point)": 0,
        "RV64V (Vector)": 0,
        "RoCC TPU Systolic (Custom)": 0,
        "Other / Pseudo": 0,
    }

    reg_pattern = re.compile(r"\b([xvtfa][0-9]{1,2}|sp|ra|fp|gp|tp|zero)\b", re.IGNORECASE)

    for line_num, line in enumerate(lines, 1):
        clean = line.strip()
        # Remove comments (; or #)
        clean = re.sub(r"[#;].*$", "", clean).strip()
        if not clean:
            continue

        # Check section directive
        if clean.startswith("."):
            sec_match = re.match(r"^(\.[a-zA-Z0-9_\.\-]+)", clean)
            if sec_match:
                sections.append(sec_match.group(1))
            continue

        # Check label
        if ":" in clean:
            label_match = re.match(r"^([a-zA-Z0-9_\.\-]+):", clean)
            if label_match:
                labels.append(label_match.group(1))
                clean = clean[len(label_match.group(0)):].strip()
                if not clean:
                    continue

        # Parse instruction mnemonic
        parts = clean.split(None, 1)
        mnemonic = parts[0].lower()
        operands = parts[1] if len(parts) > 1 else ""

        # Classify instruction
        if mnemonic in RV64I_INSTRUCTIONS:
            category = "RV64I (Base Integer)"
        elif mnemonic in RV64M_INSTRUCTIONS:
            category = "RV64M (Multiply/Divide)"
        elif mnemonic in RV64FD_INSTRUCTIONS:
            category = "RV64FD (Floating Point)"
        elif mnemonic in RV64V_INSTRUCTIONS:
            category = "RV64V (Vector)"
        elif mnemonic in ROCC_TPU_OPCODES:
            category = "RoCC TPU Systolic (Custom)"
        else:
            category = "Other / Pseudo"

        category_counts[category] += 1
        instructions_found.append({
            "line": line_num,
            "mnemonic": mnemonic,
            "operands": operands,
            "category": category
        })

        # Register extraction
        for reg in reg_pattern.findall(operands):
            r_lower = reg.lower()
            reg_usage[r_lower] = reg_usage.get(r_lower, 0) + 1

    return {
        "filename": filename,
        "total_lines": len(lines),
        "total_instructions": len(instructions_found),
        "labels": labels,
        "sections": list(dict.fromkeys(sections)),
        "category_distribution": category_counts,
        "registers_utilized": dict(sorted(reg_usage.items(), key=lambda kv: kv[1], reverse=True)),
        "has_custom_tpu_opcodes": category_counts["RoCC TPU Systolic (Custom)"] > 0,
        "instructions_sample": instructions_found[:25],
    }


def generate_riscv_template(template_name: str, matrix_dim: int = 16) -> str:
    """
    Generates standard, syntactically clean RISC-V 64 assembly templates.
    Supported templates: 'matmul', 'tpu_systolic', 'vector_add', 'fibonacci', 'primes'.
    """
    tmpl = template_name.lower().strip()

    if tmpl in ["matmul", "matrix_multiply", "gemm"]:
        return f"""# ==============================================================================
# RISC-V 64 (RV64IM) General Matrix Multiply (GEMM) Kernel
# Dimensions: {matrix_dim}x{matrix_dim} integer matrix multiplication
# Computes: C[i][j] = sum(A[i][k] * B[k][j])
# ==============================================================================

.section .text
.globl matmul_kernel
.type matmul_kernel, @function

# Arguments:
#   a0 = pointer to Matrix A (int64_t*)
#   a1 = pointer to Matrix B (int64_t*)
#   a2 = pointer to Matrix C (int64_t*)
#   a3 = dimension N ({matrix_dim})

matmul_kernel:
    addi sp, sp, -48
    sd   s0, 0(sp)
    sd   s1, 8(sp)
    sd   s2, 16(sp)
    sd   s3, 24(sp)
    sd   s4, 32(sp)
    sd   ra, 40(sp)

    li   s0, 0                  # i = 0 (row index)

loop_i:
    bge  s0, a3, end_i          # if i >= N, finish
    li   s1, 0                  # j = 0 (col index)

loop_j:
    bge  s1, a3, end_j          # if j >= N, next row
    li   s2, 0                  # k = 0 (inner product index)
    li   t0, 0                  # accumulator sum = 0

loop_k:
    bge  s2, a3, store_c        # if k >= N, store result

    # Compute address of A[i][k]: a0 + (i * N + k) * 8
    mul  t1, s0, a3             # i * N
    add  t1, t1, s2             # i * N + k
    slli t1, t1, 3              # byte offset (* 8)
    add  t1, a0, t1             # &A[i][k]
    ld   t2, 0(t1)              # load A[i][k]

    # Compute address of B[k][j]: a1 + (k * N + j) * 8
    mul  t3, s2, a3             # k * N
    add  t3, t3, s1             # k * N + j
    slli t3, t3, 3              # byte offset (* 8)
    add  t3, a1, t3             # &B[k][j]
    ld   t4, 0(t3)              # load B[k][j]

    # MAC Operation: sum += A[i][k] * B[k][j]
    mul  t5, t2, t4
    add  t0, t0, t5

    addi s2, s2, 1              # k++
    j    loop_k

store_c:
    # Compute address of C[i][j]: a2 + (i * N + j) * 8
    mul  t1, s0, a3
    add  t1, t1, s1
    slli t1, t1, 3
    add  t1, a2, t1
    sd   t0, 0(t1)              # store C[i][j] = sum

    addi s1, s1, 1              # j++
    j    loop_j

end_j:
    addi s0, s0, 1              # i++
    j    loop_i

end_i:
    ld   s0, 0(sp)
    ld   s1, 8(sp)
    ld   s2, 16(sp)
    ld   s3, 24(sp)
    ld   s4, 32(sp)
    ld   ra, 40(sp)
    addi sp, sp, 48
    ret
"""

    if tmpl in ["tpu_systolic", "tpu", "systolic"]:
        return f"""# ==============================================================================
# RISC-V 64 Custom RoCC Coprocessor: TPU Systolic Array MatMul Wavefront
# Coupled with 2D Systolic Processing Elements (16x16 Tile)
# Uses Custom RoCC Opcodes: tpu_load_weights, tpu_matmul_acc, tpu_sync_ub
# ==============================================================================

.section .text
.globl tpu_systolic_wavefront
.type tpu_systolic_wavefront, @function

# Arguments:
#   a0 = pointer to Weight Matrix W in Unified Buffer SRAM (16x16)
#   a1 = pointer to Input Activation Vector X
#   a2 = pointer to Output Buffer Y

tpu_systolic_wavefront:
    addi sp, sp, -32
    sd   s0, 0(sp)
    sd   ra, 8(sp)

    # 1. Preload stationary weights into the 2D Systolic Array PEs
    # Custom opcode: tpu_load_weights (Custom-0: rd=zero, rs1=a0, rs2=16)
    li   t0, {matrix_dim}
    tpu_load_weights a0, t0

    # 2. Inject activation wavefront through PE columns
    # Custom opcode: tpu_matmul_acc (Custom-1: rd=t1, rs1=a1, rs2=t0)
    tpu_matmul_acc   t1, a1, t0

    # 3. Post-activation pipeline: ReLU activation
    # Custom opcode: tpu_activate_relu (Custom-2: rd=t2, rs1=t1)
    tpu_activate_relu t2, t1

    # 4. Synchronize output tile to Unified Buffer SRAM
    # Custom opcode: tpu_sync_ub (Custom-3: rd=a2, rs1=t2)
    tpu_sync_ub       a2, t2

    # 5. Landauer thermal energy verification
    tpu_landauer_cool zero, zero

    ld   s0, 0(sp)
    ld   ra, 8(sp)
    addi sp, sp, 32
    ret
"""

    if tmpl in ["vector_add", "vec_add", "rvv"]:
        return """# ==============================================================================
# RISC-V 64 Vector Extension (RV64V 1.0) Vector Addition Kernel
# Computes: C[i] = A[i] + B[i] for N elements using vector stripmining
# ==============================================================================

.section .text
.globl vec_add_rvv
.type vec_add_rvv, @function

# Arguments:
#   a0 = pointer to A (double* / 64-bit float)
#   a1 = pointer to B (double* / 64-bit float)
#   a2 = pointer to C (double* / 64-bit float)
#   a3 = N (element count)

vec_add_rvv:
loop_vec:
    vsetvli t0, a3, e64, m1, ta, ma   # Configure vector length for 64-bit floats
    vle64.v v0, (a0)                  # Load vector A
    vle64.v v1, (a1)                  # Load vector B
    vfadd.vv v2, v0, v1               # Vector Float Add: v2 = v0 + v1
    vse64.v v2, (a2)                  # Store vector C

    slli t1, t0, 3                    # Byte stride = elements * 8
    add  a0, a0, t1                   # Advance pointer A
    add  a1, a1, t1                   # Advance pointer B
    add  a2, a2, t1                   # Advance pointer C
    sub  a3, a3, t0                   # Remaining elements = N - vl
    bnez a3, loop_vec                 # Repeat until all elements processed

    ret
"""

    if tmpl in ["fibonacci", "fib"]:
        return """# ==============================================================================
# RISC-V 64 Base Integer (RV64I) Fibonacci Sequence Generator
# Arguments: a0 = N (number of terms to generate), a1 = pointer to buffer (int64_t*)
# ==============================================================================

.section .text
.globl fibonacci_rv64
.type fibonacci_rv64, @function

fibonacci_rv64:
    blez a0, fib_done
    li   t0, 0              # fib(0) = 0
    sd   t0, 0(a1)
    li   t1, 1
    beq  a0, t1, fib_done

    li   t1, 1              # fib(1) = 1
    sd   t1, 8(a1)
    li   t2, 2              # counter i = 2
    addi a1, a1, 16

fib_loop:
    bge  t2, a0, fib_done
    add  t3, t0, t1         # next = fib(i-1) + fib(i-2)
    sd   t3, 0(a1)          # buffer[i] = next
    mv   t0, t1             # fib(i-2) = fib(i-1)
    mv   t1, t3             # fib(i-1) = next
    addi a1, a1, 8
    addi t2, t2, 1
    j    fib_loop

fib_done:
    ret
"""

    # Default fallback: Prime number trial division
    return """# ==============================================================================
# RISC-V 64 Base Integer (RV64I) Prime Number Check
# Argument: a0 = integer N
# Return:   a0 = 1 if prime, 0 if composite
# ==============================================================================

.section .text
.globl is_prime_rv64
.type is_prime_rv64, @function

is_prime_rv64:
    li   t0, 2
    blt  a0, t0, not_prime  # if N < 2, return 0
    beq  a0, t0, is_prime   # if N == 2, return 1

    # Check even numbers
    andi t1, a0, 1
    beqz t1, not_prime

    li   t2, 3              # divisor d = 3

check_loop:
    mul  t3, t2, t2         # d * d
    bgt  t3, a0, is_prime   # if d * d > N, N is prime
    rem  t4, a0, t2         # N % d
    beqz t4, not_prime      # if N % d == 0, not prime
    addi t2, t2, 2          # d += 2 (test odd numbers only)
    j    check_loop

is_prime:
    li   a0, 1
    ret

not_prime:
    li   a0, 0
    ret
"""
