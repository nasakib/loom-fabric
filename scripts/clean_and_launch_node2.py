import json
import time
import urllib.request

remote_code = '''
import os
import pathlib
import subprocess
import sys
import time

ws = pathlib.Path.home() / "Documents" / "loom-fabric"
os.chdir(str(ws))

# 1. Kill any existing dashboard_server process
print("Killing old dashboard processes...")
subprocess.run("powershell.exe -Command \\"Get-Process python* -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like '*dashboard_server*' } | Stop-Process -Force -ErrorAction SilentlyContinue\\"", shell=True)
subprocess.run("taskkill /F /IM python.exe /FI \\"WINDOWTITLE eq *dashboard*\\"", shell=True)
time.sleep(2)

# 2. Clean corrupt DB files
for f in ws.glob(".loom_hypotheses*"):
    try:
        f.unlink(missing_ok=True)
        print("Removed corrupt DB:", f.name)
    except Exception as e:
        print("Could not remove:", f.name, e)

for f in (pathlib.Path.home() / ".loom").glob("hypotheses*"):
    try:
        f.unlink(missing_ok=True)
        print("Removed corrupt DB:", f.name)
    except Exception as e:
        print("Could not remove:", f.name, e)

# 3. Launch fresh dashboard_server
py_exe = ws / ".venv" / "Scripts" / "python.exe"
if not py_exe.exists():
    py_exe = pathlib.Path(sys.executable)

print("Starting dashboard server with Python:", py_exe)
DETACHED = 0x00000008 | 0x00000200
env = {**os.environ, "PYTHONPATH": str(ws), "PYTHONIOENCODING": "utf-8", "CLOTHOS_PORT": "8087"}
log_file = ws / "node2_server_out.log"
out_f = open(log_file, "w", encoding="utf-8", errors="replace")

proc = subprocess.Popen(
    [str(py_exe), "-m", "loom.fabric.dashboard_server"],
    cwd=str(ws),
    env=env,
    stdout=out_f,
    stderr=subprocess.STDOUT,
    creationflags=DETACHED
)
print("Spawned new dashboard PID:", proc.pid)

time.sleep(4)

# 4. Verify locally
import urllib.request
try:
    with urllib.request.urlopen("http://127.0.0.1:8087/api/bicameral/status", timeout=3) as r:
        print("NODE 2 LOCAL BICAMERAL STATUS SUCCESS:", r.status, r.read().decode())
except Exception as e:
    print("LOCAL BICAMERAL CHECK FAILED:", e)
    if log_file.exists():
        print("LOG TAIL:", log_file.read_text(encoding="utf-8", errors="replace")[-1500:])
'''

job_payload = {"entrypoint": f'python -c "{remote_code}"'}
req = urllib.request.Request(
    "http://100.74.98.21:8265/api/jobs/",
    data=json.dumps(job_payload).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)
res = json.loads(urllib.request.urlopen(req).read().decode())
sub_id = res["submission_id"]
print("Submitted launch job to Node 2:", sub_id)

for _ in range(20):
    time.sleep(1.0)
    status_req = urllib.request.Request(f"http://100.74.98.21:8265/api/jobs/{sub_id}")
    st = json.loads(urllib.request.urlopen(status_req).read().decode())
    print("Status:", st["status"])
    if st["status"] == "SUCCEEDED":
        log_req = urllib.request.Request(f"http://100.74.98.21:8265/api/jobs/{sub_id}/logs")
        logs = json.loads(urllib.request.urlopen(log_req).read().decode())["logs"]
        print("=== Node 2 Output ===")
        print(logs.strip())
        break
    elif st["status"] in ["FAILED", "STOPPED"]:
        log_req = urllib.request.Request(f"http://100.74.98.21:8265/api/jobs/{sub_id}/logs")
        logs = json.loads(urllib.request.urlopen(log_req).read().decode())["logs"]
        print("FAILED:", logs.strip())
        break
