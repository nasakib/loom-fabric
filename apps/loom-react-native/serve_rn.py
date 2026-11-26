# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
ClothOS React Native Universal App Server (`apps/loom-react-native/serve_rn.py`).

Serves the pre-compiled universal React Native web build (unified on port 8087 by default):
- Zero port collisions with Unified ClothOS Master Hub (8087).
- Compatible with Chrome/Edge standalone app container mode (`--app=http://127.0.0.1:8087/guis/react-native-app/`).
- Serves living mind screensaver geometries, Task Manager telemetry, and Torque scrubbing.
"""

from __future__ import annotations

import http.server
import logging
import os
from pathlib import Path
import socketserver
import subprocess
import sys
import webbrowser

PORT = 8087
DIST_DIR = Path(__file__).resolve().parent / "dist"

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s %(message)s")
logger = logging.getLogger("loom.react_native.server")


class SPAHandler(http.server.SimpleHTTPRequestHandler):
    """Serves Single Page Application assets, falling back to index.html."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIST_DIR), **kwargs)

    def do_GET(self):
        # Resolve requested path relative to DIST_DIR
        path_without_query = self.path.split("?")[0].lstrip("/")
        target_file = DIST_DIR / path_without_query

        # If file does not exist and does not look like a static asset, serve index.html
        if not target_file.exists() and not any(target_file.name.endswith(ext) for ext in [".js", ".css", ".png", ".svg", ".json", ".ico"]):
            self.path = "/index.html"

        return super().do_GET()


def run_react_native_server(launch_browser: bool = True):
    if not DIST_DIR.exists():
        logger.error(f"React Native dist directory not found at: {DIST_DIR}")
        sys.exit(1)

    os.chdir(str(DIST_DIR))

    class ReusableTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    try:
        with ReusableTCPServer(("0.0.0.0", PORT), SPAHandler) as httpd:
            url = f"http://127.0.0.1:{PORT}/"
            logger.info("==================================================================")
            logger.info(f"CLOTHOS REACT NATIVE UNIVERSAL APP ONLINE -> {url}")
            logger.info(f"Serving from: {DIST_DIR}")
            logger.info("==================================================================")

            if launch_browser:
                candidates = [
                    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                ]
                chosen = next((c for c in candidates if os.path.exists(c)), None)
                if chosen:
                    app_data = Path(os.environ.get("TEMP", ".")) / "ClothOS_RN_Profile"
                    app_data.mkdir(parents=True, exist_ok=True)
                    cmd = [
                        chosen,
                        f"--app={url}",
                        f"--user-data-dir={app_data}",
                        "--window-size=1400,900",
                    ]
                    subprocess.Popen(cmd)
                else:
                    webbrowser.open(url)

            httpd.serve_forever()
    except OSError as e:
        if "address already in use" in str(e).lower() or getattr(e, "winerror", 0) == 10048:
            logger.warning(f"Port {PORT} already listening. React Native app is already active.")
        else:
            raise


if __name__ == "__main__":
    should_launch = "--no-browser" not in sys.argv
    run_react_native_server(launch_browser=should_launch)
