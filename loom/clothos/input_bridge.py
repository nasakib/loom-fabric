# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
ClothOS Distributed Input Bridge (`loom/clothos/input_bridge.py`).

Provides software KVM input sharing and cluster-wide input dispatch:
- Mouse Without Borders configuration and status helpers.
- Programmatic input injection via Windows User32 (SendInput, mouse_event, keybd_event).
- Cross-node input routing over the Stitch REST Bridge.
"""

from __future__ import annotations

import os
import sys
import time
import json
import socket
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

if os.name == "nt":
    import ctypes
    from ctypes import wintypes
    user32 = ctypes.windll.user32
else:
    user32 = None


# ── Windows Virtual Key Codes ────────────────────────────────────────────────
VK_CODES = {
    "enter": 0x0D, "return": 0x0D,
    "tab": 0x09, "space": 0x20,
    "esc": 0x1B, "escape": 0x1B,
    "backspace": 0x08, "delete": 0x2E,
    "up": 0x26, "down": 0x28, "left": 0x25, "right": 0x27,
    "win": 0x5B, "windows": 0x5B,
    "ctrl": 0x11, "control": 0x11,
    "alt": 0x12, "shift": 0x10,
    "f1": 0x70, "f2": 0x71, "f3": 0x72, "f4": 0x73, "f5": 0x74, "f6": 0x75,
    "f7": 0x76, "f8": 0x77, "f9": 0x78, "f10": 0x79, "f11": 0x7A, "f12": 0x7B
}


def send_key_press(vk_code: int):
    """Sends a single key down and up event."""
    if not user32:
        return
    user32.keybd_event(vk_code, 0, 0, 0)
    time.sleep(0.02)
    user32.keybd_event(vk_code, 0, 2, 0) # KEYEVENTF_KEYUP = 2


def send_hotkey(keys: List[str]):
    """Presses a combination of keys (e.g. ['ctrl', 'c'] or ['win', 'd'])."""
    if not user32:
        return
    codes = [VK_CODES.get(k.lower(), ord(k.upper())) if len(k) == 1 else VK_CODES.get(k.lower(), 0) for k in keys]
    # Press down in order
    for code in codes:
        if code:
            user32.keybd_event(code, 0, 0, 0)
            time.sleep(0.01)
    time.sleep(0.05)
    # Release in reverse order
    for code in reversed(codes):
        if code:
            user32.keybd_event(code, 0, 2, 0)


def send_type_text(text: str):
    """Types plain text character by character using SendInput unicode events."""
    if not user32:
        return
    for char in text:
        # Send unicode char
        vk = ord(char)
        if char == "\n":
            send_key_press(VK_CODES["enter"])
        elif char == "\t":
            send_key_press(VK_CODES["tab"])
        else:
            # Send character via Windows keybd_event
            user32.keybd_event(0, vk, 4, 0) # KEYEVENTF_UNICODE = 4
            user32.keybd_event(0, vk, 6, 0) # KEYEVENTF_UNICODE | KEYEVENTF_KEYUP = 6
        time.sleep(0.005)


def send_mouse_click(x: Optional[int] = None, y: Optional[int] = None, button: str = "left"):
    """Clicks the mouse at specified coordinates or current cursor position."""
    if not user32:
        return
    if x is not None and y is not None:
        user32.SetCursorPos(int(x), int(y))
        time.sleep(0.02)

    MOUSEEVENTF_LEFTDOWN = 0x0002
    MOUSEEVENTF_LEFTUP = 0x0004
    MOUSEEVENTF_RIGHTDOWN = 0x0008
    MOUSEEVENTF_RIGHTUP = 0x0010

    if button.lower() == "right":
        user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
        time.sleep(0.02)
        user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
    else:
        user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.02)
        user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


def get_kvm_status() -> Dict[str, Any]:
    """Inspects Mouse Without Borders installation and running status."""
    mwb_path = Path("C:/Program Files (x86)/Microsoft Garage/Mouse without Borders/MouseWithoutBorders.exe")
    is_installed = mwb_path.exists()
    is_running = False

    try:
        import psutil
        for p in psutil.process_iter(['name']):
            if "mousewithoutborders" in p.info['name'].lower():
                is_running = True
                break
    except Exception:
        pass

    return {
        "installed": is_installed,
        "running": is_running,
        "executable": str(mwb_path) if is_installed else None,
        "hostname": socket.gethostname()
    }


def launch_mouse_without_borders():
    """Launches the Mouse Without Borders GUI application."""
    mwb_path = Path("C:/Program Files (x86)/Microsoft Garage/Mouse without Borders/MouseWithoutBorders.exe")
    if mwb_path.exists():
        subprocess.Popen([str(mwb_path)], shell=False)
        return True
    return False
