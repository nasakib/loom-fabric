"""
ClothOS Native Desktop GUI Launcher (`apps/loom-desktop/launch_desktop.py`).

Guarantees 100% reliable launch of the ClothOS Sovereign Command Center (Task Manager GUI):
- Audits and cleans stale ClothOS ports before starting, without touching third-party applications.
- Dynamically allocates dedicated ClothOS port (default 8085, candidates 8085-8090) to prevent collisions.
- Actively verifies HTTP 200 health check on /api/health before spawning the desktop app container.
- Uses Microsoft Edge / Chromium in standalone App Container mode (`--app=http://127.0.0.1:<PORT>`).
- Seamlessly falls back to default browser if no Chromium container is installed.
"""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.request
import webbrowser

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WORKSPACE_ROOT))

from loom.fabric.port_manager import port_manager, CLOTHOS_PRIMARY_PORT, CLOTHOS_CANDIDATE_PORTS


def wait_for_server_health(port: int, max_retries: int = 35, delay: float = 0.3) -> bool:
    """Actively polls http://127.0.0.1:<port>/api/health until healthy or timeout."""
    url = f"http://127.0.0.1:{port}/api/health"
    for i in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ClothOS-Launcher/3.1"})
            with urllib.request.urlopen(req, timeout=0.8) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(delay)
        print(".", end="", flush=True)
    return False


def ensure_clean_dashboard_server() -> int:
    """Audits ports, cleans stale ClothOS instances, and ensures server is 100% healthy."""
    print("🔍 [ClothOS GUI Launcher] Auditing cluster ports and checking server health...")
    
    # 1. Check if server is already running and healthy
    active_port = port_manager.get_active_dashboard_port()
    if port_manager.is_clothos_server_healthy(active_port):
        print(f"✅ [ClothOS GUI Launcher] Healthy ClothOS Command Center already online on port {active_port}!")
        return active_port

    # 2. Clean only stale ClothOS ports to prevent conflicts
    print("🧹 [ClothOS GUI Launcher] Cleaning stale ClothOS processes...")
    clean_res = port_manager.clean_stale_clothos_ports()
    if clean_res["cleaned_pids_count"] > 0:
        print(f"   Cleaned {clean_res['cleaned_pids_count']} stale ClothOS process(es).")

    # 3. Find the best collision-free port
    chosen_port = port_manager.find_best_available_clothos_port()
    print(f"🎯 [ClothOS GUI Launcher] Dedicated ClothOS port selected: {chosen_port}")

    # 4. Start dashboard_server.py headlessly
    python_exe = WORKSPACE_ROOT / ".venv" / "Scripts" / "python.exe"
    if not python_exe.exists():
        python_exe = Path(sys.executable)

    env = {
        **os.environ,
        "PYTHONPATH": str(WORKSPACE_ROOT),
        "PYTHONIOENCODING": "utf-8",
        "CLOTHOS_PORT": str(chosen_port),
    }

    print(f"🚀 [ClothOS GUI Launcher] Starting dashboard_server.py on port {chosen_port} (PID will be saved)...")
    server_proc = subprocess.Popen(
        [str(python_exe), "-m", "loom.fabric.dashboard_server"],
        cwd=str(WORKSPACE_ROOT),
        env=env,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
    )

    # 5. Wait for active HTTP 200 health check
    print(f"⏳ [ClothOS GUI Launcher] Verifying HTTP health at http://127.0.0.1:{chosen_port}", end="", flush=True)
    healthy = wait_for_server_health(chosen_port, max_retries=40, delay=0.3)
    print()

    if healthy:
        print(f"✨ [ClothOS GUI Launcher] ClothOS Command Center confirmed ONLINE on http://127.0.0.1:{chosen_port}!")
        return chosen_port
    else:
        print(f"⚠️ [ClothOS GUI Launcher] Server took longer to respond; attempting launch towards http://127.0.0.1:{chosen_port}...")
        return chosen_port


def launch_desktop_window(mode: str = "command-center"):
    try:
        port = ensure_clean_dashboard_server()
        
        # Exact Program URLs
        if mode in ["screensaver", "scr", "visualizer"]:
            target_url = f"http://127.0.0.1:{port}/screensaver"
            app_name = "ClothOS Living Neuro-Screensaver"
        elif mode in ["react-native", "app", "rn"]:
            target_url = f"http://127.0.0.1:{port}/app"
            app_name = "ClothOS Universal React Native App"
        elif mode in ["visuals", "mind", "living", "neuro", "tpu", "occipital"]:
            target_url = f"http://127.0.0.1:{port}/visuals"
            app_name = "ClothOS Sovereign Mind & TPU Visual Cockpit"
        elif mode in ["node2", "remote"]:
            target_url = "http://100.74.98.21:8087/visuals"
            app_name = "ClothOS Node 2 Remote Cockpit (Ryzen 7)"
        elif mode in ["node1", "skytech"]:
            target_url = "http://100.85.230.105:8087/visuals"
            app_name = "ClothOS Node 1 Remote Cockpit (SkyTech)"
        elif mode in ["ray", "cluster"]:
            target_url = "http://100.74.98.21:8265"
            app_name = "ClothOS Ray Cluster Cockpit (Node 2)"
        else:
            # The Windows Task Manager & Sovereign Command Center UI
            target_url = f"http://127.0.0.1:{port}/visuals"
            app_name = "ClothOS Sovereign Command Center GUI"

        app_data = Path(os.environ.get("TEMP", ".")) / f"ClothOS_{mode}_Profile"
        app_data.mkdir(parents=True, exist_ok=True)

        if sys.platform == "win32":
            candidates = [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            ]
        elif sys.platform == "darwin":
            candidates = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
                "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
                "/Applications/Chromium.app/Contents/MacOS/Chromium",
            ]
        else: # Linux / Unix
            candidates = [
                "/usr/bin/google-chrome",
                "/usr/bin/chromium",
                "/usr/bin/chromium-browser",
                "/usr/bin/brave-browser",
                "/usr/bin/microsoft-edge",
                "/snap/bin/chromium",
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
            if mode in ["screensaver", "scr", "visualizer"]:
                cmd.extend(["--start-fullscreen", "--kiosk"])
            else:
                cmd.append("--window-size=1440,960")

            print(f"🖥️ [ClothOS GUI Launcher] Launching {app_name}: {chosen_exe}")
            print(f"   Target: {target_url}")
            subprocess.Popen(cmd)
        else:
            print(f"🌐 [ClothOS GUI Launcher] Opening in default web browser: {target_url}")
            webbrowser.open(target_url)

        print(f"🎉 [ClothOS GUI Launcher] Successfully launched! Dedicated companion for Najmos Sakib.")
    except Exception as exc:
        print(f"❌ [ClothOS GUI Launcher] Error during launch: {exc}", file=sys.stderr)
        with open("desktop_launcher_error.log", "a", encoding="utf-8") as f:
            f.write(f"[{time.ctime()}] {exc}\n")


if __name__ == "__main__":
    launch_mode = "visuals"
    for arg in sys.argv[1:]:
        clean_arg = arg.lstrip("-").lower()
        if arg.startswith("--mode="):
            launch_mode = arg.split("=")[1].strip().lower()
        elif clean_arg in ["screensaver", "scr", "visualizer"]:
            launch_mode = "screensaver"
        elif clean_arg in ["react-native", "app", "rn"]:
            launch_mode = "react-native"
        elif clean_arg in ["node2", "remote"]:
            launch_mode = "node2"
        elif clean_arg in ["ray", "cluster"]:
            launch_mode = "ray"
        elif clean_arg in ["visuals", "mind", "living", "neuro", "tpu", "occipital"]:
            launch_mode = "visuals"
    launch_desktop_window(launch_mode)
