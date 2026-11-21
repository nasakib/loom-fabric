# Copyright (c) 2026 Najmos Sakib. All rights reserved.
"""Node 2 Server Cleaner & Runner (`loom/fabric/run_node2_server.py`)."""

import os
import pathlib
import subprocess
import sys
import time
import urllib.request
import json

ws = pathlib.Path.home() / "Documents" / "loom-fabric"
os.chdir(str(ws))

print("=== NODE 2 SERVER LAUNCHER ===")
print("Workspace:", ws)

# 1. Kill any existing process on 8087
p = subprocess.run("netstat -ano", shell=True, capture_output=True, text=True)
for line in p.stdout.splitlines():
    if ":8087" in line and "LISTENING" in line:
        parts = line.strip().split()
        pid = parts[-1]
        print(f"Killing port 8087 process PID {pid}...")
        subprocess.run(f"taskkill /F /PID {pid}", shell=True)

# Also kill any python process running dashboard_server
subprocess.run('taskkill /F /IM python.exe /FI "WINDOWTITLE eq *dashboard_server*"', shell=True)
time.sleep(2)

# 2. Clean corrupt DB files if any
for f in ws.glob(".loom_hypotheses*"):
    try:
        f.unlink(missing_ok=True)
        print("Cleaned:", f.name)
    except Exception as e:
        print("Note on cleanup:", e)

for f in (pathlib.Path.home() / ".loom").glob("hypotheses*"):
    try:
        f.unlink(missing_ok=True)
    except Exception:
        pass

# 3. Identify Python exe
py_exe = ws / ".venv" / "Scripts" / "python.exe"
if not py_exe.exists():
    py_exe = pathlib.Path(sys.executable)

print("Starting server with:", py_exe)

# 4. Launch detached dashboard_server
log_file = ws / "node2_server_out.log"
out_f = open(log_file, "w", encoding="utf-8", errors="replace")
DETACHED = 0x00000008 | 0x00000200
env = {
    **os.environ,
    "PYTHONPATH": str(ws),
    "PYTHONIOENCODING": "utf-8",
    "CLOTHOS_PORT": "8087"
}

proc = subprocess.Popen(
    [str(py_exe), "-m", "loom.fabric.dashboard_server"],
    cwd=str(ws),
    env=env,
    stdout=out_f,
    stderr=subprocess.STDOUT,
    creationflags=DETACHED
)
print(f"Spawned dashboard_server PID {proc.pid}")

# 5. Wait for bicameral status to be online
for i in range(20):
    time.sleep(1.0)
    try:
        with urllib.request.urlopen("http://127.0.0.1:8087/api/bicameral/status", timeout=2) as r:
            if r.status == 200:
                data = json.loads(r.read().decode())
                print("SUCCESS: Node 2 Bicameral Command Center is ONLINE!")
                print("Local Role:", data.get("local_role"))
                print("Peer Node:", data.get("peer_node_id"))
                sys.exit(0)
    except Exception as e:
        print(f"Waiting for endpoint... ({e})")

print("Failed to reach 8087 within timeout. Log tail:")
if log_file.exists():
    print(log_file.read_text(encoding="utf-8", errors="replace")[-2000:])
sys.exit(1)
