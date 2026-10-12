#!/usr/bin/env bash
# ==============================================================================
# Loom Fabric — macOS Native App & CLI Installer (Apple Silicon & Intel)
# Configures sovereign virtual environment, desktop launcher, and purple theme.
# ==============================================================================

set -e

PURPLE='\033[0;35m'
CYAN='\033[0;36m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${PURPLE}==========================================================${NC}"
echo -e "${PURPLE}   LOOM FABRIC — macOS NATIVE 1-CLICK INSTALLER           ${NC}"
echo -e "${PURPLE}==========================================================${NC}"

# Detect Apple Silicon vs Intel
ARCH="$(uname -m)"
echo -e "[*] Target Architecture: ${GREEN}${ARCH}${NC}"

# Ensure Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "[!] Python 3 not found. Installing via Homebrew or Xcode Command Line Tools..."
    if command -v brew &> /dev/null; then
        brew install python@3.12
    else
        xcode-select --install || true
    fi
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
pip install fastapi "uvicorn[standard]" pydantic typer rich psutil httpx "ray[default]"

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
pip install -e "${REPO_DIR}"

# Create CLI executable
cat << 'EOF' > "${HOME}/.loom/bin/loom"
#!/usr/bin/env bash
VENV_PYTHON="${HOME}/.loom/env/bin/python"
exec "${VENV_PYTHON}" -m loom.cli.main "$@"
EOF
chmod +x "${HOME}/.loom/bin/loom"

# Create Desktop Application Launcher (.command) for macOS Finder
DESKTOP_DIR="${HOME}/Desktop"
cat << 'EOF' > "${DESKTOP_DIR}/Loom Fabric.command"
#!/usr/bin/env bash
DIR="$(cd "$(dirname "$0")" && pwd)"
source "${HOME}/.loom/env/bin/activate"
python -m loom.cli.main gui
EOF
chmod +x "${DESKTOP_DIR}/Loom Fabric.command"

echo -e "${GREEN}[✓] Loom Fabric successfully installed on macOS!${NC}"
echo -e "${PURPLE}[i] Desktop launcher created at: ~/Desktop/Loom Fabric.command${NC}"
echo -e "${PURPLE}[i] Command Line tool available at: ~/.loom/bin/loom${NC}"
echo -e ""
echo -e "[*] Executing initial hardware probe..."
"${HOME}/.loom/bin/loom" probe
