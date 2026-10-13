#!/usr/bin/env bash
# ==============================================================================
# Loom Fabric — macOS Native App Bundle & CLI Installer (Apple Silicon & Intel)
# Creates ~/Applications/Loom Fabric Commander.app (Zero Terminal Windows) + `loom` CLI.
# ==============================================================================

set -euo pipefail

PURPLE='\033[0;35m'
CYAN='\033[0;36m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${PURPLE}==========================================================${NC}"
echo -e "${GREEN}   LOOM FABRIC — macOS NATIVE APP & CLI INSTALLER         ${NC}"
echo -e "${PURPLE}==========================================================${NC}"

ARCH="$(uname -m)"
echo -e "[*] Target Architecture: ${GREEN}${ARCH}${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "[!] Python 3 not found. Installing via Homebrew or Xcode Command Line Tools..."
    if command -v brew &> /dev/null; then
        brew install python@3.12 python-tk@3.12
    else
        xcode-select --install || true
    fi
fi

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${HOME}/.loom/env"
mkdir -p "${HOME}/.loom/bin" "${HOME}/.local/bin" "${HOME}/.loom/logs"

if [ ! -d "${VENV_DIR}" ]; then
    echo -e "[*] Creating sovereign Python environment at ${VENV_DIR}..."
    python3 -m venv "${VENV_DIR}"
fi

source "${VENV_DIR}/bin/activate"

echo -e "[*] Installing Loom Fabric dependencies..."
pip install --upgrade pip
pip install fastapi "uvicorn[standard]" pydantic typer rich psutil httpx
pip install -e "${REPO_DIR}"

for TARGET_BIN in "${HOME}/.loom/bin/loom" "${HOME}/.local/bin/loom"; do
cat << EOF > "${TARGET_BIN}"
#!/usr/bin/env bash
export PYTHONPATH="${REPO_DIR}:\${PYTHONPATH:-}"
export PYTHONIOENCODING="utf-8"
exec "${VENV_DIR}/bin/python" -m loom.cli.main "\$@"
EOF
chmod +x "${TARGET_BIN}"
done

# Create native macOS .app bundle (Zero Terminal Windows when opened from Finder/Dock/Spotlight)
APP_BUNDLE="${HOME}/Applications/Loom Fabric Commander.app"
mkdir -p "${APP_BUNDLE}/Contents/MacOS" "${APP_BUNDLE}/Contents/Resources"

cat << EOF > "${APP_BUNDLE}/Contents/Info.plist"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>LoomFabricCommander</string>
    <key>CFBundleIdentifier</key>
    <string>ai.loomfabric.commander</string>
    <key>CFBundleName</key>
    <string>Loom Fabric Commander</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>LSUIElement</key>
    <false/>
</dict>
</plist>
EOF

cat << EOF > "${APP_BUNDLE}/Contents/MacOS/LoomFabricCommander"
#!/usr/bin/env bash
export PYTHONPATH="${REPO_DIR}:\${PYTHONPATH:-}"
export PYTHONIOENCODING="utf-8"
exec "${VENV_DIR}/bin/python" -m loom.gui >> "${HOME}/.loom/logs/gui.log" 2>&1
EOF
chmod +x "${APP_BUNDLE}/Contents/MacOS/LoomFabricCommander"

echo -e "${GREEN}[OK] Loom Fabric Commander.app installed to ~/Applications!${NC}"
echo -e "${PURPLE}[i] CLI installed at: ~/.local/bin/loom (try 'loom', 'loom -p \"hello\"', 'loom status')${NC}"
