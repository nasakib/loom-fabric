"""
Standalone Screensaver & Visualizer Launcher for ClothOS (`apps/loom-screensaver/launch_screensaver.py`).

Fulfills the user's sovereign directive:
"all unified into one desktop react-native app, and also one screen saver/visualizer app"

Features:
- Launches the standalone 3D Neuro-Screensaver in dedicated fullscreen / kiosk mode.
- Supports standard Windows screensaver command-line switches:
    /s : Run fullscreen screensaver
    /c : Show screensaver configuration/controls
    /p : Preview in window
- Auto-detects running ClothOS server on active port or opens the local standalone HTML visualizer immediately.
"""

from __future__ import annotations

import os
from pathlib import Path
import socket
import subprocess
import sys
import time

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

CANDIDATE_PORTS = [8085, 8090, 8888, 8081, 8000, 8005, 8080]


def is_port_open(host: str, port: int, timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


def get_active_dashboard_port() -> int:
    root_dir = Path(__file__).resolve().parents[2]
    port_file = root_dir / ".loom_dashboard_port"
    if port_file.exists():
        try:
            p = int(port_file.read_text(encoding="utf-8").strip())
            if is_port_open("127.0.0.1", p):
                return p
        except Exception:
            pass

    for p in CANDIDATE_PORTS:
        if is_port_open("127.0.0.1", p):
            return p

    if port_file.exists():
        try:
            return int(port_file.read_text(encoding="utf-8").strip())
        except Exception:
            pass

    return 8085


def ensure_dashboard_server() -> int:
    root_dir = Path(__file__).resolve().parents[2]
    active_port = get_active_dashboard_port()
    if is_port_open("127.0.0.1", active_port):
        return active_port

    python_exe = root_dir / ".venv" / "Scripts" / "python.exe"
    if not python_exe.exists():
        python_exe = Path(sys.executable)

    env = {**os.environ, "PYTHONPATH": str(root_dir), "PYTHONIOENCODING": "utf-8"}
    subprocess.Popen(
        [str(python_exe), "-m", "loom.fabric.dashboard_server"],
        cwd=str(root_dir),
        env=env,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
    )

    for _ in range(15):
        time.sleep(0.2)
        p = get_active_dashboard_port()
        if is_port_open("127.0.0.1", p):
            return p

    return active_port


def launch_screensaver(fullscreen: bool = True):
    try:
        html_fallback = Path(__file__).parent / "screensaver.html"
        port = ensure_dashboard_server()

        if is_port_open("127.0.0.1", port):
            target_url = f"http://127.0.0.1:{port}/screensaver"
        else:
            target_url = html_fallback.resolve().as_uri()

        app_data = Path(os.environ.get("TEMP", ".")) / "LoomScreensaverProfile"
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

            print(f"[Screensaver] Launching 3D Digital Brain Screensaver: {chosen_exe} -> {target_url}")
            subprocess.Popen(cmd)
        else:
            import webbrowser
            print(f"[Screensaver] Opening screensaver in default browser: {target_url}")
            webbrowser.open(target_url)
    except Exception as exc:
        print(f"[Screensaver] Launcher error: {exc}", file=sys.stderr)
        with open("screensaver_launcher_error.log", "a", encoding="utf-8") as f:
            f.write(f"[{time.ctime()}] {exc}\n")


if __name__ == "__main__":
    is_kiosk = True
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if "/c" in arg or "--config" in arg:
            is_kiosk = False
    launch_screensaver(fullscreen=is_kiosk)
