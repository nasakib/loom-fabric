import os
import sys
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress logging to prevent console spam
        pass

def serve(port=8087):
    dist_dir = os.path.abspath(r"c:\Users\natsa\Documents\loom-fabric\apps\loom-react-native\dist")
    if not os.path.isdir(dist_dir):
        print(f"Error: Directory not found: {dist_dir}")
        sys.exit(1)
        
    os.chdir(dist_dir)
    server = ThreadingHTTPServer(("0.0.0.0", port), QuietHandler)
    print(f"Loom React Native Universal GUI running at http://localhost:{port} ...")
    try:
        webbrowser.open(f"http://localhost:{port}")
    except Exception:
        pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped.")

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8087
    serve(port)
