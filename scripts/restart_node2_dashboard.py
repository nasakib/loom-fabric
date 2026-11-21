import os
import sys
import time
import json
import urllib.request
import urllib.error

RAY_DASHBOARD_URL = "http://100.74.98.21:8265"

remote_code = '''
import os
import pathlib
import subprocess
import sys
import time
import urllib.request
import json

ws = pathlib.Path.home() / "Documents" / "loom-fabric"
print(">>> [Node 2] Workspace:", ws)
os.chdir(str(ws))

# 1. Kill any existing dashboard process on port 8087
print(">>> [Node 2] Terminating old dashboard processes...")
try:
    import psutil
    for p in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmd = " ".join(p.info['cmdline'] or [])
            if "loom.fabric.dashboard_server" in cmd:
                print(f">>> [Node 2] Killing old dashboard PID {p.info['pid']}")
                p.kill()
        except Exception:
            pass
except Exception as e:
    print("psutil kill warning:", e)

# Also kill via PowerShell
subprocess.run("powershell.exe -Command \\"Get-NetTCPConnection -LocalPort 8087 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }\\"", shell=True)

time.sleep(1.5)

py_exe = ws / ".venv" / "Scripts" / "python.exe"
if not py_exe.exists():
    py_exe = pathlib.Path(sys.executable)

print(">>> [Node 2] Using Python:", py_exe)

# 2. Launch updated dashboard_server as background detached process
log_file = ws / "node2_server_out.log"
out_f = open(log_file, "w", encoding="utf-8", errors="replace")
DETACHED = 0x00000008 | 0x00000200
env = {**os.environ, "PYTHONPATH": str(ws), "PYTHONIOENCODING": "utf-8", "CLOTHOS_PORT": "8087"}

proc = subprocess.Popen(
    [str(py_exe), "-m", "loom.fabric.dashboard_server"],
    cwd=str(ws),
    env=env,
    stdout=out_f,
    stderr=subprocess.STDOUT,
    creationflags=DETACHED
)
print(f">>> [Node 2] Spawned fresh dashboard_server PID {proc.pid}")

# 3. Wait for it to become healthy and verify bicameral status
healthy = False
for i in range(20):
    time.sleep(1.0)
    try:
        with urllib.request.urlopen("http://127.0.0.1:8087/api/bicameral/status", timeout=2) as r:
            if r.status == 200:
                data = json.loads(r.read().decode())
                print(">>> [Node 2] FRESH BICAMERAL SERVER ONLINE! Local Role:", data.get("local_role"))
                healthy = True
                break
    except Exception as e:
        print(f">>> [Node 2] Waiting for server... ({e})")

if not healthy:
    print(">>> [Node 2] FAILED to reach 8087. Log tail:")
    if log_file.exists():
        print(log_file.read_text(encoding="utf-8", errors="replace")[-2000:])
    sys.exit(1)
'''

job_url = f"{RAY_DASHBOARD_URL}/api/jobs/"
job_payload = {
    "entrypoint": f'python -c "{remote_code}"'
}

print("Submitting restart job to Node 2 Ray cluster...")
req = urllib.request.Request(
    job_url,
    data=json.dumps(job_payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST"
)

with urllib.request.urlopen(req, timeout=10) as resp:
    submit_data = json.loads(resp.read().decode("utf-8"))
    submission_id = submit_data.get("submission_id")
    print(f"Node 2 Job submitted successfully: submission_id={submission_id}")

print("Waiting for Node 2 restart to complete...")
for poll in range(30):
    time.sleep(1.0)
    try:
        status_req = urllib.request.Request(f"{job_url}{submission_id}")
        with urllib.request.urlopen(status_req, timeout=5) as r:
            job_info = json.loads(r.read().decode("utf-8"))
            status = job_info.get("status")
            print(f"Node 2 Job Status: {status}")
            if status == "SUCCEEDED":
                log_req = urllib.request.Request(f"{job_url}{submission_id}/logs")
                with urllib.request.urlopen(log_req, timeout=5) as lr:
                    job_logs = lr.read().decode("utf-8")
                print(f"Node 2 Execution Logs:\n{job_logs.strip()}")
                print("✅ NODE 2 COMMAND CENTER RESTARTED & CONCURRENTLY RUNNING!")
                sys.exit(0)
            elif status in ["FAILED", "STOPPED"]:
                log_req = urllib.request.Request(f"{job_url}{submission_id}/logs")
                with urllib.request.urlopen(log_req, timeout=5) as lr:
                    job_logs = lr.read().decode("utf-8")
                print(f"Node 2 Job {status} with logs:\n{job_logs.strip()}")
                sys.exit(1)
    except Exception as ex:
        print(f"Polling error: {ex}")

print("Restart job timed out!")
sys.exit(1)
