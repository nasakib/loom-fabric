"""
Tests for ClothOS Desktop Startup & Legacy Cleanup Manager
Verifies shortcut creation, port check, and clean startup logic.
"""

import os
import unittest
from pathlib import Path
from guis.desktop_startup_manager import (
    is_port_listening,
    get_workspace_root,
    get_desktop_dirs,
    get_startup_dir,
    PORT_CLOTHOS_DAEMON,
    PORT_GUI_SERVER
)

class TestDesktopStartupManager(unittest.TestCase):

    def test_workspace_and_paths(self):
        ws = get_workspace_root()
        self.assertTrue(ws.exists())
        self.assertTrue((ws / "guis").exists())
        self.assertTrue((ws / "guis" / "desktop_startup_manager.py").exists())

    def test_desktop_and_startup_dirs(self):
        desktops = get_desktop_dirs()
        self.assertGreater(len(desktops), 0)
        for d in desktops:
            self.assertTrue(d.exists(), f"Desktop dir does not exist: {d}")

        startup = get_startup_dir()
        self.assertTrue(startup.exists(), f"Startup dir does not exist: {startup}")

    def test_service_ports_active(self):
        # We verified earlier that both 8087 (ClothOS daemon) and 8090 (GUI server) are up
        self.assertTrue(is_port_listening(PORT_CLOTHOS_DAEMON), "ClothOS daemon on port 8087 is not listening")
        self.assertTrue(is_port_listening(PORT_GUI_SERVER), "GUI server on port 8090 is not listening")

    def test_startup_vbs_installed(self):
        startup = get_startup_dir()
        vbs = startup / "ClothOS_Antigravity_Startup.vbs"
        self.assertTrue(vbs.exists(), "ClothOS_Antigravity_Startup.vbs was not installed to Startup")
        content = vbs.read_text(encoding="utf-8")
        self.assertIn("desktop_startup_manager.py", content)
        self.assertIn("--on-startup", content)

    def test_legacy_autostart_removed(self):
        startup = get_startup_dir()
        legacy_vbs = startup / "ClothOS_AutoStart.vbs"
        self.assertFalse(legacy_vbs.exists(), "Legacy ClothOS_AutoStart.vbs was not removed!")

    def test_modern_shortcuts_exist(self):
        for d in get_desktop_dirs():
            shortcuts = [f.name for f in d.glob("ClothOS*.lnk")]
            self.assertTrue(any("Command Center" in s for s in shortcuts), f"Missing Command Center shortcut on {d}")
            self.assertTrue(any("Desktop HUD" in s for s in shortcuts), f"Missing Desktop HUD shortcut on {d}")

if __name__ == "__main__":
    unittest.main()
