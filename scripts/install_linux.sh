#!/usr/bin/env bash
# ==============================================================================
# Loom Fabric — Linux & WSL2 Native 1-Click Installer
# Supports: Ubuntu, Debian, Fedora, RHEL, CentOS, Arch Linux, and WSL2
# ==============================================================================

set -euo pipefail

PURPLE='\033[0;35m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${PURPLE}==========================================================${NC}"
echo -e "${GREEN}   LOOM FABRIC — LINUX / WSL2 NATIVE INSTALLER            ${NC}"
echo -e "${PURPLE}==========================================================${NC}"

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "${HOME}/.loom/bin" "${HOME}/.local/bin"

# 1. Determine Python runtime (Native venv, uv, or WSL interop venv)
VENV_DIR="${HOME}/.loom/env"
VENV_PYTHON=""

if command -v uv &> /dev/null; then
    echo -e "${CYAN}[*] Found uv package manager. Provisioning environment...${NC}"
    (cd "${REPO_DIR}" && uv venv "${VENV_DIR}" && uv pip install --python "${VENV_DIR}/bin/python" -e "${REPO_DIR}") || true
    if [ -x "${VENV_DIR}/bin/python" ]; then
        VENV_PYTHON="${VENV_DIR}/bin/python"
    fi
fi

if [ -z "${VENV_PYTHON}" ] && python3 -m venv "${VENV_DIR}" 2>/dev/null; then
    echo -e "${CYAN}[*] Created virtual environment at ${VENV_DIR}${NC}"
    "${VENV_DIR}/bin/pip" install --upgrade pip || true
    "${VENV_DIR}/bin/pip" install fastapi "uvicorn[standard]" pydantic typer rich psutil httpx nvidia-ml-py || true
    "${VENV_DIR}/bin/pip" install -e "${REPO_DIR}" || true
    VENV_PYTHON="${VENV_DIR}/bin/python"
fi

# Fallback for WSL2 when offline or python3-venv package is not installed
if [ -z "${VENV_PYTHON}" ] && [ -f "/mnt/c/Users/natsa/Documents/loom-fabric/.venv/Scripts/python.exe" ]; then
    echo -e "${CYAN}[*] Using shared Loom Fabric virtual environment via WSL2 interop...${NC}"
    VENV_PYTHON="/mnt/c/Users/natsa/Documents/loom-fabric/.venv/Scripts/python.exe"
elif [ -z "${VENV_PYTHON}" ]; then
    VENV_PYTHON="$(command -v python3)"
fi

# 2. Create CLI wrapper in both ~/.loom/bin/loom and ~/.local/bin/loom
for TARGET_BIN in "${HOME}/.loom/bin/loom" "${HOME}/.local/bin/loom"; do
cat << EOF > "${TARGET_BIN}"
#!/usr/bin/env bash
export PYTHONPATH="${REPO_DIR}:\${PYTHONPATH:-}"
export PYTHONIOENCODING="utf-8"
export WSLENV="PYTHONPATH:PYTHONIOENCODING:\${WSLENV:-}"
exec "${VENV_PYTHON}" -m loom.cli.main "\$@"
EOF
chmod +x "${TARGET_BIN}"
done

# 3. Ensure ~/.local/bin and ~/.loom/bin are on PATH in ~/.bashrc
if [ -f "${HOME}/.bashrc" ] && ! grep -q ".loom/bin" "${HOME}/.bashrc"; then
    echo 'export PATH="$HOME/.local/bin:$HOME/.loom/bin:$PATH"' >> "${HOME}/.bashrc"
fi

# 4. Create Desktop Entry if running on Linux Desktop
APP_DIR="${HOME}/.local/share/applications"
mkdir -p "${APP_DIR}"
cat << EOF > "${APP_DIR}/loom-fabric.desktop"
[Desktop Entry]
Name=Loom Fabric Commander
Comment=Mechanistic Heterogeneous AI Operating System
Exec=${HOME}/.local/bin/loom gui
Terminal=false
Type=Application
Categories=Development;Science;ArtificialIntelligence;
EOF
chmod +x "${APP_DIR}/loom-fabric.desktop"

echo -e "${GREEN}[OK] Loom Fabric successfully installed on Linux / WSL2!${NC}"
echo -e "${PURPLE}[i] CLI installed at: ~/.local/bin/loom and ~/.loom/bin/loom${NC}"
echo -e ""
echo -e "[*] Executing initial hardware probe..."
"${HOME}/.local/bin/loom" probe
