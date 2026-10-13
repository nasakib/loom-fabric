#!/usr/bin/env bash
# ==============================================================================
# Loom Fabric — Unified Linux, WSL2 & macOS Installer
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OS_TYPE="$(uname -s)"

if [ "${OS_TYPE}" = "Darwin" ]; then
    exec bash "${SCRIPT_DIR}/install_macos.sh" "$@"
else
    exec bash "${SCRIPT_DIR}/install_linux.sh" "$@"
fi
