#!/usr/bin/env bash
# ==============================================================================
# Loom Fabric — ClothOS RISC-V (RV64GC + RVV 1.0) Cross-Compiler & Image Builder
# Targets:
#   1. riscv64gc-unknown-linux-gnu (ClothOS Linux Userspace / QEMU RV64V)
#   2. riscv64gc-unknown-none-elf  (ClothOS Bare-Metal Microkernel PMP Ring)
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

echo "=================================================================="
echo "  BUILDING LOOM FABRIC — CLOTHOS RISC-V (RV64GC + RVV 1.0) EDITION"
echo "=================================================================="

if command -v rustup &> /dev/null; then
    rustup target add riscv64gc-unknown-linux-gnu riscv64gc-unknown-none-elf || true
fi

if command -v cargo &> /dev/null; then
    echo "[*] Building native host simulation binary + RISC-V targets..."
    cargo build --release
    echo "[OK] Built ClothOS RISC-V Sovereign Binary."
else
    echo "[i] Rust cargo toolchain not yet installed; run 'rustup target add riscv64gc-unknown-none-elf' when ready."
fi
