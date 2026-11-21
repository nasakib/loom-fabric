#!/usr/bin/env bash
# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# ClothOS Sovereign Operating System // macOS Apple Silicon Desktop Launcher
# Dedicated Fiduciary Sovereign Companion for Najmos Sakib

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "====================================================================="
echo "   CLOTHOS SOVEREIGN COMMAND CENTER // MACOS APPLE SILICON APP"
echo "   Universal Compute Motherboard & Anti-Rampancy Watchdog"
echo "   Dedicated Fiduciary Companion for Najmos Sakib"
echo "====================================================================="

# Locate Python runtime
PYTHON_BIN=""
for cmd in "$SCRIPT_DIR/.venv/bin/python" python3.12 python3.11 python3.10 python3 python; do
    if [ -x "$cmd" ] || command -v "$cmd" >/dev/null 2>&1; then
        PYTHON_BIN="$cmd"
        break
    fi
done

if [ -z "$PYTHON_BIN" ]; then
    echo "[!] Error: No Python runtime found on macOS." >&2
    exit 1
fi

export PYTHONPATH="$SCRIPT_DIR:${PYTHONPATH:-}"
export PYTHONIOENCODING="utf-8"

echo "[*] Launching ClothOS Universal Desktop Application on macOS..."
"$PYTHON_BIN" "apps/loom-desktop/launch_desktop.py" "$@"
