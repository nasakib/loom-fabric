"""
Unified Sovereign Nexus Launcher & Mesh Inspector (`scripts/launch_unified_nexus.py`).

Checks all VectorCore / ClothOS / Loom ecosystem services, starts the unified
single-port ClothOS Master Application (:8087 with Anthropic /v1/messages +
OpenAI /v1/chat/completions + /v1/sovereign/*) if not already listening,
and prints client integration snippets.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

LOOM_ROOT = Path(__file__).resolve().parents[1]
if str(LOOM_ROOT) not in sys.path:
    sys.path.insert(0, str(LOOM_ROOT))

from loom.unified_nexus import get_sovereign_nexus


def main() -> int:
    nexus = get_sovereign_nexus()
    mesh = nexus.get_ecosystem_mesh_status(include_http_details=False)
    gw = mesh["services"]["loom_gateway"]

    if not gw["online"]:
        print("[Unified Nexus] Starting Unified ClothOS + Loom Master Hub on http://127.0.0.1:8087 ...")
        env = os.environ.copy()
        for var in ("PYTHONHOME", "PYTHONPATH", "VIRTUAL_ENV"):
            env.pop(var, None)
        env["CLOTHOS_PORT"] = "8087"
        python_exe = str(LOOM_ROOT / ".venv" / "Scripts" / "python.exe")
        if not Path(python_exe).exists():
            python_exe = sys.executable

        flags = 0x08000000 if os.name == "nt" else 0  # CREATE_NO_WINDOW
        log_out = open(LOOM_ROOT / "gateway_out.log", "a", encoding="utf-8")
        log_err = open(LOOM_ROOT / "gateway_error.log", "a", encoding="utf-8")
        subprocess.Popen(
            [python_exe, "-m", "uvicorn", "loom.fabric.dashboard_server:app", "--host", "0.0.0.0", "--port", "8087"],
            cwd=str(LOOM_ROOT),
            env=env,
            stdout=log_out,
            stderr=log_err,
            creationflags=flags,
        )
        for _ in range(20):
            time.sleep(0.4)
            mesh = nexus.get_ecosystem_mesh_status(include_http_details=False)
            if mesh["services"]["loom_gateway"]["online"]:
                break

    mesh = nexus.get_ecosystem_mesh_status(include_http_details=True)
    print(json.dumps(mesh, indent=2, default=str))
    print("\n--- Drop-In Anthropic & Claude Code Environment ---")
    print("set ANTHROPIC_BASE_URL=http://127.0.0.1:8087")
    print("set ANTHROPIC_API_KEY=loom-sovereign-local")
    print("\n--- Unified Sovereign MCP Server ---")
    print(f"{LOOM_ROOT / '.venv' / 'Scripts' / 'python.exe'} -m servers.sovereign_mcp")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
