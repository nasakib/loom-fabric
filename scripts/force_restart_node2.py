import json
import time
import urllib.request

kill_code = """
import os, subprocess, time, pathlib

print("Killing PID 8684...")
subprocess.run("taskkill /F /PID 8684", shell=True)
subprocess.run("taskkill /F /IM python.exe /FI \\"WINDOWTITLE eq *dashboard*\\"", shell=True)
time.sleep(2)

ws = pathlib.Path.home() / "Documents" / "loom-fabric"
py_exe = ws / ".venv" / "Scripts" / "python.exe"
if not py_exe.exists():
    import sys
    py_exe = pathlib.Path(sys.executable)

print("Starting dashboard server with fresh code...")
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
print("Spawned PID:", proc.pid)

time.sleep(3)
import urllib.request
try:
    with urllib.request.urlopen("http://127.0.0.1:8087/api/bicameral/status", timeout=3) as r:
        print("BICAMERAL STATUS CHECK:", r.status, r.read().decode())
except Exception as e:
    print("CHECK ERROR:", e)
    if log_file.exists():
        print("LOG TAIL:", log_file.read_text(encoding="utf-8", errors="replace")[-1000:])
"""

job_payload = {"entrypoint": f'python -c "{kill_code}"'}
req = urllib.request.Request(
    "http://100.74.98.21:8265/api/jobs/",
    data=json.dumps(job_payload).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)
res = json.loads(urllib.request.urlopen(req).read().decode())
sub_id = res["submission_id"]
print("Submitted job:", sub_id)

for _ in range(15):
    time.sleep(1.0)
    status_req = urllib.request.Request(f"http://100.74.98.21:8265/api/jobs/{sub_id}")
    st = json.loads(urllib.request.urlopen(status_req).read().decode())
    print("Status:", st["status"])
    if st["status"] == "SUCCEEDED":
        log_req = urllib.request.Request(f"http://100.74.98.21:8265/api/jobs/{sub_id}/logs")
        logs = json.loads(urllib.request.urlopen(log_req).read().decode())["logs"]
        print(logs.strip())
        break
    elif st["status"] in ["FAILED", "STOPPED"]:
        log_req = urllib.request.Request(f"http://100.74.98.21:8265/api/jobs/{sub_id}/logs")
        logs = json.loads(urllib.request.urlopen(log_req).read().decode())["logs"]
        print("FAILED:", logs.strip())
        break
