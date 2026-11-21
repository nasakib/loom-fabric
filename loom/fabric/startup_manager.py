# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
ClothOS Windows Startup Manager (`loom/fabric/startup_manager.py`).

Guarantees 100% silent, headless auto-start of ClothOS on Windows login:
- Creates a zero-window VBScript launcher in `%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\`.
- Launches the ClothOS Sovereign Command Center without any flashing console windows (WshShell.Run ..., 0, False).
- Can configure local Node 1 and remote Node 2 for persistent cluster resilience.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
import sys
from typing import Any, Dict

logger = logging.getLogger("loom.fabric.startup_manager")

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]


class WindowsStartupManager:
    """Manages automatic startup registration for ClothOS across Windows sessions."""

    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = workspace_root or WORKSPACE_ROOT
        appdata = os.environ.get("APPDATA")
        if appdata:
            self.startup_folder = Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        else:
            self.startup_folder = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"

        self.vbs_path = self.startup_folder / "ClothOS_AutoStart.vbs"
        self.bat_path = self.workspace_root / "Launch-Loom-GUI.bat"

    def is_startup_enabled(self) -> bool:
        """Checks if ClothOS is currently registered in Windows Startup."""
        return self.vbs_path.exists()

    def enable_startup(self) -> Dict[str, Any]:
        """Creates the silent zero-window VBScript startup launcher."""
        try:
            if not self.startup_folder.exists():
                self.startup_folder.mkdir(parents=True, exist_ok=True)
            python_exe = self.workspace_root / ".venv" / "Scripts" / "python.exe"
            if not python_exe.exists():
                python_exe = Path(sys.executable)

            script_target = self.workspace_root / "apps" / "loom-desktop" / "launch_desktop.py"

            vbs_content = (
                'Set WshShell = CreateObject("WScript.Shell")\r\n'
                f'WshShell.CurrentDirectory = "{self.workspace_root}"\r\n'
                f'WshShell.Run """{python_exe}""" & " """{script_target}""" --mode=command-center", 0, False\r\n'
            )

            self.vbs_path.write_text(vbs_content, encoding="utf-8")
            logger.info(f"ClothOS Windows Startup enabled successfully at: {self.vbs_path}")
            return {
                "success": True,
                "startup_path": str(self.vbs_path),
                "workspace": str(self.workspace_root),
                "silent_mode": "Zero-Window VBScript (WshShell.Run ..., 0, False)",
            }
        except Exception as e:
            logger.error(f"Failed to enable ClothOS startup: {e}")
            return {"success": False, "error": str(e)}

    def disable_startup(self) -> Dict[str, Any]:
        """Removes the ClothOS startup launcher."""
        try:
            if self.vbs_path.exists():
                self.vbs_path.unlink()
            return {"success": True, "message": "ClothOS startup launcher removed."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_status(self) -> Dict[str, Any]:
        return {
            "enabled": self.is_startup_enabled(),
            "startup_folder": str(self.startup_folder),
            "vbs_file": str(self.vbs_path),
        }


# Singleton instance
startup_manager = WindowsStartupManager()

if __name__ == "__main__":
    res = startup_manager.enable_startup()
    print("Startup Manager Result:", res)
