"""
Fabric Native Screensaver Runner (`loom/fabric/screensaver_runner.py`).

Part of the Fabric core architecture. Launches the 3D Living Geometries & Digital Brain screensaver
in fullscreen kiosk mode with 100% reliability, zero dependencies, and automatic port detection.
"""

from __future__ import annotations

import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import webbrowser

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def is_port_open(host: str, port: int, timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


def get_active_port() -> int:
    from loom.fabric.port_manager import port_manager
    return port_manager.get_active_dashboard_port()


def get_inline_screensaver_html() -> str:
    """Returns self-contained screensaver HTML from file or embedded source."""
    candidates = [
        Path(__file__).parent / "screensaver.html",
        Path(__file__).resolve().parents[2] / "apps" / "loom-screensaver" / "screensaver.html",
        Path(r"c:\Users\natsa\Documents\loom-fabric\loom\fabric\screensaver.html"),
    ]
    for c in candidates:
        if c.exists():
            try:
                return c.read_text(encoding="utf-8")
            except Exception:
                pass
    return "<html><body style='background:#020408;color:#38bdf8;display:flex;align-items:center;justify-content:center;height:100vh;font-family:sans-serif;'><h1>ClothOS Neuro-Screensaver Active</h1></body></html>"


def launch_screensaver(fullscreen: bool = True):
    root_dir = Path(__file__).resolve().parents[2]
    html_file = Path(__file__).parent / "screensaver.html"
    if not html_file.exists():
        html_file = root_dir / "apps" / "loom-screensaver" / "screensaver.html"

    port = get_active_port()
    if is_port_open("127.0.0.1", port):
        target_url = f"http://127.0.0.1:{port}/screensaver"
    else:
        # Start dashboard server headlessly
        python_exe = root_dir / ".venv" / "Scripts" / "python.exe"
        if not python_exe.exists():
            python_exe = Path(sys.executable)

        subprocess.Popen(
            [str(python_exe), "-m", "loom.fabric.dashboard_server"],
            cwd=str(root_dir),
            env={**os.environ, "PYTHONPATH": str(root_dir), "PYTHONIOENCODING": "utf-8"},
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )

        for _ in range(12):
            time.sleep(0.25)
            if is_port_open("127.0.0.1", port):
                break

        if is_port_open("127.0.0.1", port):
            target_url = f"http://127.0.0.1:{port}/screensaver"
        else:
            target_url = html_file.resolve().as_uri()

    app_data = Path(os.environ.get("TEMP", ".")) / "ClothOSScreensaverProfile"
    app_data.mkdir(parents=True, exist_ok=True)

    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]

    chosen_exe = None
    for cand in candidates:
        if os.path.exists(cand):
            chosen_exe = cand
            break

    if chosen_exe:
        cmd = [
            chosen_exe,
            f"--app={target_url}",
            f"--user-data-dir={app_data}",
            "--disable-features=Translate",
            "--enable-gpu-rasterization",
            "--enable-zero-copy",
        ]
        if fullscreen:
            cmd.extend(["--start-fullscreen", "--kiosk"])
        else:
            cmd.append("--window-size=1280,800")

        print(f"[Fabric Screensaver] Spawning 3D Screensaver via {chosen_exe} -> {target_url}")
        subprocess.Popen(cmd)
    else:
        print(f"[Fabric Screensaver] Opening in default browser: {target_url}")
        webbrowser.open(target_url)


if __name__ == "__main__":
    is_kiosk = True
    if len(sys.argv) > 1 and sys.argv[1].lower() in ["/c", "--config"]:
        is_kiosk = False
    launch_screensaver(fullscreen=is_kiosk)
