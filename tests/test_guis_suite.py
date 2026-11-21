"""
Tests for ClothOS Universal GUI Suite
Verifies structure, syntax, token coherence, and daemon serving.
"""

import os
import unittest
import urllib.request
import threading
import time
from guis.serve_guis import AntigravityGUIHandler, HTTPServer

class TestGuisSuite(unittest.TestCase):

    def setUp(self):
        self.workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.guis_dir = os.path.join(self.workspace_root, "guis")

    def test_all_gui_artifacts_exist(self):
        """Ensure all required GUI files and directories exist."""
        required_paths = [
            "index.html",
            "serve_guis.py",
            "shared/tokens.css",
            "shared/bicameral-client.js",
            "web-app/index.html",
            "web-app/styles/main.css",
            "web-app/scripts/cad-engine.js",
            "web-app/scripts/app.js",
            "react-native-app/package.json",
            "react-native-app/app.json",
            "react-native-app/tsconfig.json",
            "react-native-app/src/App.tsx",
            "react-native-app/dist/index.html",
            "desktop-hud/index.html",
            "desktop-hud/launch_hud.py",
            "neuro-screensaver/index.html",
        ]

        for rel_path in required_paths:
            full_path = os.path.join(self.guis_dir, rel_path)
            self.assertTrue(os.path.exists(full_path), f"Missing required GUI asset: {rel_path}")
            self.assertGreater(os.path.getsize(full_path), 50, f"Asset is too small/empty: {rel_path}")

    def test_css_tokens_referenced(self):
        """Ensure all HTML files reference tokens.css for antigravity visual coherence."""
        html_files = [
            "index.html",
            "web-app/index.html",
            "react-native-app/dist/index.html",
            "desktop-hud/index.html",
            "neuro-screensaver/index.html",
        ]
        for rel_path in html_files:
            full_path = os.path.join(self.guis_dir, rel_path)
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("tokens.css", content, f"{rel_path} does not import tokens.css")

    def test_bicameral_client_referenced(self):
        """Ensure bicameral client is imported in all active GUIs."""
        guis = [
            "index.html",
            "web-app/index.html",
            "react-native-app/dist/index.html",
            "desktop-hud/index.html",
            "neuro-screensaver/index.html",
        ]
        for rel_path in guis:
            full_path = os.path.join(self.guis_dir, rel_path)
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("bicameral-client.js", content, f"{rel_path} does not import bicameral-client.js")

    def test_gui_server_serves_pages(self):
        """Test that the serve_guis server starts and serves files."""
        port = 8092  # Dedicated test port
        handler = lambda *args, **kwargs: AntigravityGUIHandler(*args, directory=self.guis_dir, **kwargs)
        server = HTTPServer(("127.0.0.1", port), handler)
        server_thread = threading.Thread(target=server.serve_forever, daemon=True)
        server_thread.start()

        time.sleep(0.3)

        try:
            # Check portal
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/index.html", timeout=5.0) as resp:
                self.assertEqual(resp.status, 200)
                html = resp.read().decode("utf-8")
                self.assertIn("Universal Antigravity GUI Suite", html)

            # Check web app
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/web-app/index.html", timeout=5.0) as resp:
                self.assertEqual(resp.status, 200)
                html = resp.read().decode("utf-8")
                self.assertIn("STEM 3D CAD ENGINE", html)

            # Check react native universal simulator
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/react-native-app/dist/index.html", timeout=5.0) as resp:
                self.assertEqual(resp.status, 200)
                html = resp.read().decode("utf-8")
                self.assertIn("React Native Mobile Universal App", html)

            # Check screensaver
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/neuro-screensaver/index.html", timeout=5.0) as resp:
                self.assertEqual(resp.status, 200)

            # Check API proxy fallback
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/bicameral/status", timeout=5.0) as resp:
                self.assertIn(resp.status, [200, 404])

        finally:
            server.shutdown()
            server.server_close()

if __name__ == "__main__":
    unittest.main()
