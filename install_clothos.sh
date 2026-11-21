#!/usr/bin/env bash
# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
#
# ClothOS & Loom Fabric -- Universal Linux & Apple Silicon Installer
# Supports x86_64 Linux, aarch64 Linux, and macOS Apple Silicon (M1/M2/M3/M4).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "====================================================================="
echo "   CLOTHOS & LOOM FABRIC -- UNIVERSAL POSIX / APPLE SILICON INSTALLER"
echo "   Architect: Najmos Sakib | Fiduciary 0.00 Bound"
echo "====================================================================="

OS="$(uname -s)"
ARCH="$(uname -m)"
echo "[*] Detected Host Platform: $OS ($ARCH)"

# 1. Locate Python 3.10+
PYTHON_BIN=""
for cmd in python3.12 python3.11 python3.10 python3 python; do
    if command -v "$cmd" >/dev/null 2>&1; then
        PYTHON_BIN="$(command -v "$cmd")"
        break
    fi
done

if [ -z "$PYTHON_BIN" ]; then
    echo "[!] Error: No suitable Python 3.10+ runtime found. Please install Python 3.10+." >&2
    exit 1
fi

echo "[*] Using Python: $PYTHON_BIN ($($PYTHON_BIN --version))"

# 2. Virtual Environment Setup
VENV_DIR="$SCRIPT_DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "[*] Creating workspace virtual environment at $VENV_DIR..."
    "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

VENV_PY="$VENV_DIR/bin/python"
"$VENV_PY" -m pip install --upgrade pip >/dev/null 2>&1 || true

# 3. Run Sovereign Python Installer
echo "[*] Executing ClothOS Sovereign Installation Engine..."
"$VENV_PY" -m loom.fabric.installer "$@"

# 4. Create ~/.local/bin Symlinks
LOCAL_BIN="$HOME/.local/bin"
mkdir -p "$LOCAL_BIN"

for cmd in clothos clothsh loom; do
    cat <<EOF > "$LOCAL_BIN/$cmd"
#!/usr/bin/env bash
export PYTHONPATH="$SCRIPT_DIR:\$PYTHONPATH"
exec "$VENV_PY" -m loom.clothos.shell "\$@"
EOF
    chmod +x "$LOCAL_BIN/$cmd"
done

# 5. OS-Specific Daemon / Service Configuration
if [ "$OS" = "Darwin" ]; then
    # Apple Silicon LaunchAgent
    PLIST_DIR="$HOME/Library/LaunchAgents"
    mkdir -p "$PLIST_DIR"
    PLIST_PATH="$PLIST_DIR/com.clothos.agent.plist"
    cat <<EOF > "$PLIST_PATH"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.clothos.agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>$VENV_PY</string>
        <string>-m</string>
        <string>loom.fabric.dashboard_server</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$SCRIPT_DIR</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$SCRIPT_DIR/clothos_apple_silicon.log</string>
    <key>StandardErrorPath</key>
    <string>$SCRIPT_DIR/clothos_apple_silicon_err.log</string>
</dict>
</plist>
EOF
    echo "[OK] Registered Apple Silicon launchd daemon: $PLIST_PATH"
elif [ "$OS" = "Linux" ]; then
    echo "[*] Generated systemd unit template available via 'clothos hal'."
fi

echo "====================================================================="
echo "[OK] ClothOS & Loom Fabric Installation Complete on $OS ($ARCH)!"
echo "Launch with: clothsh (or $SCRIPT_DIR/.venv/bin/python -m loom.clothos.shell)"
echo "====================================================================="
