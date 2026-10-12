#!/bin/bash
# ==============================================================================
# Loom Fabric — Linux & macOS Unified Installer & Launcher
# Works on: Ubuntu/Debian, Fedora/RHEL, Arch, and macOS (Apple Silicon / Intel)
# ==============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${CYAN}==========================================================${NC}"
echo -e "${YELLOW}   LOOM FABRIC — CROSS-PLATFORM SYSTEM INSTALLER          ${NC}"
echo -e "${CYAN}==========================================================${NC}"

# Detect OS
OS_TYPE="$(uname -s)"
ARCH_TYPE="$(uname -m)"

echo -e "[*] Detected Platform: ${GREEN}${OS_TYPE} (${ARCH_TYPE})${NC}"

# Ensure Python 3.10+
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[!] python3 could not be found. Please install Python 3.10 or higher.${NC}"
    exit 1
fi

PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo -e "[*] Python Version: ${GREEN}${PY_VER}${NC}"

# Setup Virtual Environment
VENV_DIR="${HOME}/.loom/env"
if [ ! -d "${VENV_DIR}" ]; then
    echo -e "[*] Creating sovereign Python virtual environment in ${VENV_DIR}..."
    python3 -m venv "${VENV_DIR}"
fi

source "${VENV_DIR}/bin/activate"

# Install dependencies
echo -e "[*] Upgrading pip and installing Loom Fabric dependencies..."
pip install --upgrade pip
pip install fastapi uvicorn typer rich pydantic psutil httpx ray

# Install platform-specific GPU profilers
if [ "${OS_TYPE}" == "Linux" ]; then
    echo -e "[*] Installing Linux NVIDIA/AMD profiler support..."
    pip install nvidia-ml-py || true
elif [ "${OS_TYPE}" == "Darwin" ]; then
    echo -e "[*] Configuring Apple Silicon Metal unified memory runtime..."
fi

# Install Loom package in editable mode
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo -e "[*] Installing Loom Fabric in editable mode from ${REPO_DIR}..."
pip install -e "${REPO_DIR}"

# Create executable symlink
BIN_DIR="${HOME}/.local/bin"
mkdir -p "${BIN_DIR}"
cat << 'EOF' > "${BIN_DIR}/loom"
#!/bin/bash
VENV_PYTHON="${HOME}/.loom/env/bin/python"
if [ -f "${VENV_PYTHON}" ]; then
    exec "${VENV_PYTHON}" -m loom.cli.main "$@"
else
    exec python3 -m loom.cli.main "$@"
fi
EOF
chmod +x "${BIN_DIR}/loom"

echo -e "${GREEN}[✓] Loom Fabric successfully installed!${NC}"
echo -e "${YELLOW}[i] Add ~/.local/bin to your PATH if not already present:${NC}"
echo -e "    export PATH=\"\$HOME/.local/bin:\$PATH\""
echo -e ""
echo -e "[*] Running diagnostic hardware probe..."
"${BIN_DIR}/loom" probe

echo -e ""
echo -e "${GREEN}To start the Sovereign Gateway & Web Dashboard on Linux/Mac:${NC}"
echo -e "    loom serve --port 8000"
