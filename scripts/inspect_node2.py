import base64
import os
import sys
import time

os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["NO_PROXY"] = "*"

from ray.job_submission import JobSubmissionClient, JobStatus

client = JobSubmissionClient("http://100.74.98.21:8265")

code = """
import os, sys, platform, socket, pathlib, subprocess

print("=== NODE 2 SYSTEM REPORT ===")
print("Hostname:", socket.gethostname())
print("Platform:", platform.platform())
print("Python:", sys.executable)
print("CWD:", os.getcwd())
user_docs = pathlib.Path.home() / "Documents" / "loom-fabric"
print(f"User docs exists ({user_docs}):", user_docs.exists())
if user_docs.exists():
    print("Files in loom-fabric:", len(list(user_docs.iterdir())))
    pf = user_docs / ".loom_dashboard_port"
    if pf.exists():
        print("Dashboard port in file:", pf.read_text())
    pidf = user_docs / ".loom_dashboard_pid"
    if pidf.exists():
        print("Dashboard PID in file:", pidf.read_text())

print("=== Spawning dashboard_server with log redirection on Node 2 ===")
log_file = user_docs / "node2_dashboard.log"
cmd = f'powershell.exe -NoProfile -Command "Start-Process \'{py_exe}\' -ArgumentList \'-m\', \'loom.fabric.dashboard_server\' -WorkingDirectory \'{user_docs}\' -RedirectStandardOutput \'{log_file}\' -RedirectStandardError \'{user_docs / \"node2_dashboard_err.log\"}\'"'

print("Running command:", cmd)
p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
print("Start-Process stdout:", p.stdout)
print("Start-Process stderr:", p.stderr)

import time
time.sleep(4.0)

print("=== Checking if localhost:8087 responds locally on Node 2 ===")
import urllib.request
try:
    with urllib.request.urlopen("http://127.0.0.1:8087/api/health", timeout=3) as r:
        print("Local 8087 response:", r.read().decode())
except Exception as e:
    print("Local 8087 error:", e)

if log_file.exists():
    print("=== Dashboard Log ===")
    print(log_file.read_text(encoding="utf-8", errors="replace"))

err_file = user_docs / "node2_dashboard_err.log"
if err_file.exists():
    print("=== Dashboard Err Log ===")
    print(err_file.read_text(encoding="utf-8", errors="replace"))


"""

b64 = base64.b64encode(code.encode("utf-8")).decode("ascii")

job_id = client.submit_job(
    entrypoint=f'python -c "import base64; exec(base64.b64decode(\'{b64}\').decode(\'utf-8\'))"',
)
print(f"Submitted inspection job: {job_id}")

for _ in range(30):
    status = client.get_job_status(job_id)
    if status in [JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.STOPPED]:
        print(f"Status: {status}")
        print("Logs:\n", client.get_job_logs(job_id))
        break
    time.sleep(1)
