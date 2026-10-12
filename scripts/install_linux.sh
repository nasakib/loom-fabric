#!/usr/bin/env bash
# ==============================================================================
# Loom Fabric — Linux Native Installer & Systemd/Desktop Integration
# Supports: Ubuntu, Debian, Fedora, RHEL, CentOS, Arch Linux
# ==============================================================================

set -e

PURPLE='\033[0;35m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${PURPLE}==========================================================${NC}"
echo -e "${PURPLE}   LOOM FABRIC — LINUX NATIVE 1-CLICK INSTALLER           ${NC}"
echo -e "${PURPLE}==========================================================${NC}"

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "[!] Python 3 not found. Please install python3 and python3-venv using your package manager."
    exit 1
fi

VENV_DIR="${HOME}/.loom/env"
mkdir -p "${HOME}/.loom/bin"

if [ ! -d "${VENV_DIR}" ]; then
    echo -e "[*] Creating sovereign Python environment at ${VENV_DIR}..."
    python3 -m venv "${VENV_DIR}"
fi

source "${VENV_DIR}/bin/activate"

echo -e "[*] Installing Loom Fabric dependencies..."
pip install --upgrade pip
pip install fastapi "uvicorn[standard]" pydantic typer rich psutil httpx "ray[default]" nvidia-ml-py

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
pip install -e "${REPO_DIR}"

# Create CLI executable
cat << 'EOF' > "${HOME}/.loom/bin/loom"
#!/usr/bin/env bash
VENV_PYTHON="${HOME}/.loom/env/bin/python"
exec "${VENV_PYTHON}" -m loom.cli.main "$@"
EOF
chmod +x "${HOME}/.loom/bin/loom"

# Create Desktop Application Entry for GNOME / KDE / XFCE
APP_DIR="${HOME}/.local/share/applications"
mkdir -p "${APP_DIR}"

cat << EOF > "${APP_DIR}/loom-fabric.desktop"
[Desktop Entry]
Name=Loom Fabric
Comment=Sovereign AI Operating System Command Center
Exec=${HOME}/.loom/bin/loom gui
Terminal=false
Type=Application
Categories=Development;Science;ArtificialIntelligence;
EOF
chmod +x "${APP_DIR}/loom-fabric.desktop"

# Create Desktop Shortcut if ~/Desktop exists
if [ -d "${HOME}/Desktop" ]; then
    cp "${APP_DIR}/loom-fabric.desktop" "${HOME}/Desktop/loom-fabric.desktop"
    chmod +x "${HOME}/Desktop/loom-fabric.desktop"
fi

echo -e "${GREEN}[✓] Loom Fabric successfully installed on Linux!${NC}"
echo -e "${PURPLE}[i] Desktop launcher added to Applications menu and ~/Desktop/loom-fabric.desktop${NC}"
echo -e "${PURPLE}[i] Command Line tool available at: ~/.loom/bin/loom${NC}"
echo -e ""
echo -e "[*] Executing initial hardware probe..."
"${HOME}/.loom/bin/loom" probe
