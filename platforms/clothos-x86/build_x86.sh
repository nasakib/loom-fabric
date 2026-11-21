#!/usr/bin/env bash
# ClothOS x86 / x86_64 Multiboot Builder & Launcher
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Loom Fabric: ClothOS x86_64 / x86_32 Builder ==="
if command -v cargo >/dev/null 2>&1; then
    cargo build --release
else
    python3 -m loom.clothos.x86_hal_emulator
fi
