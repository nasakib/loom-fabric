#!/usr/bin/env python3
"""
ClothOS // Desktop Glassmorphic HUD Launcher
Launches the minimal floating HUD sidecar in standalone app mode.
"""

import os
import sys
import webbrowser
import subprocess

def launch():
    hud_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "index.html"))
    file_url = f"file:///{hud_path.replace(os.sep, '/')}"

    # Try launching with Chrome or Edge in --app mode for a borderless window
    browser_commands = [
        ["msedge", f"--app={file_url}", "--window-size=420,100", "--window-position=50,50"],
        ["chrome", f"--app={file_url}", "--window-size=420,100", "--window-position=50,50"],
    ]

    launched = False
    for cmd in browser_commands:
        try:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"Launched Desktop HUD in app window mode: {' '.join(cmd)}")
            launched = True
            break
        except FileNotFoundError:
            continue

    if not launched:
        print(f"Opening Desktop HUD in default browser: {file_url}")
        webbrowser.open(file_url)

if __name__ == "__main__":
    launch()
