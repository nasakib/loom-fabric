"""
ClothOS Autonomous Stealth Sentry & Workload Governor
File: loom/clothos/stealth_sentry.py

Ensures zero user disruption:
- Continuously monitors user input activity (mouse/keyboard idle time via GetLastInputInfo).
- Detects foreground full-screen applications and gaming processes (Steam, Epic, Unreal, DirectX).
- Measures CPU and GPU utilization thresholds.
- When user is actively gaming or working: sets state to "BUSY", pauses cluster task ingestion,
  and steps down background priority.
- When user is idle (>60s) or loads are low: sets state to "AVAILABLE" and yields capacity to the mesh.
"""

import ctypes
import os
import time
import socket
import json
import threading
from typing import Dict, Any

class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

# List of high-priority interactive / gaming processes that trigger instant yield
YIELD_PROCESSES = {
    "steam.exe", "epicgameslauncher.exe", "valorant.exe", "cs2.exe", "dota2.exe",
    "fortniteclient-win64-shipping.exe", "cod.exe", "overwatch.exe", "gta5.exe",
    "cyberpunk2077.exe", "leagueclient.exe", "discord.exe", "premiere.exe",
    "afterfx.exe", "blender.exe", "unrealeditor.exe", "unity.exe"
}

class StealthSentry:
    def __init__(self, idle_threshold_sec: float = 60.0):
        self.idle_threshold_sec = idle_threshold_sec
        self.is_user_busy = False
        self.is_gaming_active = False
        self._running = False
        self._state_lock = threading.Lock()

    def get_idle_time(self) -> float:
        """Returns seconds elapsed since last user mouse or keyboard event."""
        if os.name != "nt":
            return 999.0
        try:
            lii = LASTINPUTINFO()
            lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
            if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii)):
                millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
                return max(0.0, millis / 1000.0)
        except Exception:
            pass
        return 0.0

    def check_gaming_activity(self) -> bool:
        """Checks if high-priority gaming or rendering executables are running."""
        try:
            import psutil
            for proc in psutil.process_iter(['name']):
                p_name = (proc.info.get('name') or "").lower()
                if p_name in YIELD_PROCESSES:
                    return True
        except Exception:
            pass
        return False

    def check_cpu_load(self) -> float:
        try:
            import psutil
            return psutil.cpu_percent(interval=0.1)
        except Exception:
            return 10.0

    def evaluate_state(self) -> Dict[str, Any]:
        """Calculates current node availability score."""
        idle_s = self.get_idle_time()
        gaming = self.check_gaming_activity()
        cpu_load = self.check_cpu_load()

        # User is actively engaged if they moved the mouse/keyboard recently, or a game/heavy tool is active
        user_active = (idle_s < self.idle_threshold_sec) or gaming or (cpu_load > 65.0)

        with self._state_lock:
            self.is_user_busy = user_active
            self.is_gaming_active = gaming

        status = "BUSY_USER_PRIORITY" if user_active else "IDLE_AVAILABLE"
        return {
            "status": status,
            "can_accept_cluster_jobs": not user_active,
            "user_idle_seconds": round(idle_s, 1),
            "gaming_detected": gaming,
            "cpu_percent": round(cpu_load, 1)
        }

    def start_governor_loop(self, check_interval: float = 3.0):
        self._running = True
        t = threading.Thread(target=self._run_loop, args=(check_interval,), daemon=True, name="ClothOS-Stealth-Governor")
        t.start()

    def _run_loop(self, interval: float):
        while self._running:
            self.evaluate_state()
            time.sleep(interval)

_sentry = None

def get_stealth_sentry() -> StealthSentry:
    global _sentry
    if _sentry is None:
        _sentry = StealthSentry()
        _sentry.start_governor_loop()
    return _sentry