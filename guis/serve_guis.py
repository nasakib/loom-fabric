#!/usr/bin/env python3
"""
ClothOS // Loom Fabric — Multi-GUI Compatibility Server
Serves the Antigravity Universal GUI Suite and reverse-proxies API endpoints to port 8087.
(Primary entry point is unified single-port Master App on http://localhost:8087/guis/)
"""

import sys
import os
import argparse
import urllib.request
import urllib.error
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json

DEFAULT_PORT = 8087
CLOTHOS_DAEMON_URL = "http://localhost:8087"

class AntigravityGUIHandler(SimpleHTTPRequestHandler):
    """Custom request handler serving GUI files and reverse-proxying ClothOS API."""

    def __init__(self, *args, directory=None, **kwargs):
        if directory is None:
            directory = os.path.dirname(os.path.abspath(__file__))
        super().__init__(*args, directory=directory, **kwargs)

    def do_GET(self):
        # Reverse-proxy /api/* requests to ClothOS daemon
        if self.path.startswith("/api/"):
            self.proxy_request("GET")
            return
        super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/"):
            self.proxy_request("POST")
            return
        self.send_error(405, "Method Not Allowed")

    def proxy_request(self, method):
        target_url = f"{CLOTHOS_DAEMON_URL}{self.path}"
        data = None
        if method == "POST":
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                data = self.rfile.read(content_length)

        headers = {
            'Content-Type': self.headers.get('Content-Type', 'application/json')
        }

        req = urllib.request.Request(target_url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=1.2) as resp:
                resp_data = resp.read()
                self.send_response(resp.status)
                self.send_header('Content-Type', resp.headers.get('Content-Type', 'application/json'))
                self.send_header('Content-Length', str(len(resp_data)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(resp_data)
        except urllib.error.HTTPError as he:
            err_body = he.read()
            self.send_response(he.code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(err_body)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(err_body)
        except Exception as e:
            # Fallback mock for autonomous standalone operation
            fallback = {
                "status": "FALLBACK_AUTONOMOUS",
                "message": f"Daemon proxy simulated: {str(e)}",
                "resonance": 0.984,
                "coherence": 0.992,
                "cycle_count": 1421,
                "node1": {"name": "skyTech-Worker", "role": "PROJECTOR_THINKER", "load": 28.4},
                "node2": {"name": "Ryzen7-Head", "role": "DECIDER", "load": 34.2}
            }
            body = json.dumps(fallback).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(body)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()


def run_server(port=DEFAULT_PORT, host="0.0.0.0"):
    # Ensure stdout handles UTF-8 on Windows
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass

    gui_dir = os.path.dirname(os.path.abspath(__file__))
    handler = lambda *args, **kwargs: AntigravityGUIHandler(*args, directory=gui_dir, **kwargs)
    server = HTTPServer((host, port), handler)
    print("==================================================================")
    print("[CLOTHOS] Antigravity Universal GUI Suite Server Running")
    print("==================================================================")
    print(f"Portal URL:          http://localhost:{port}/index.html")
    print(f"Web App Command:     http://localhost:{port}/web-app/index.html")
    print(f"React Native Mobile: http://localhost:{port}/react-native-app/dist/index.html")
    print(f"Desktop HUD:         http://localhost:{port}/desktop-hud/index.html")
    print(f"Neuro-Screensaver:   http://localhost:{port}/neuro-screensaver/index.html")
    print(f"Reverse Proxy:       {CLOTHOS_DAEMON_URL}/api/*")
    print("==================================================================")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping GUI Server.")
        server.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ClothOS GUI Suite Server")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port to bind (default 8090)")
    parser.add_argument("--host", default="0.0.0.0", help="Host interface (default 0.0.0.0)")
    args = parser.parse_args()
    run_server(port=args.port, host=args.host)
