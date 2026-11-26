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
import os, sys, pathlib, subprocess

ws = pathlib.Path.home() / "Documents" / "loom-fabric"
sys.path.insert(0, str(ws))
os.chdir(str(ws))

print(">>> [Node 2] Starting all services via loom.gui CrossPlatformClusterController...")
from loom.gui import CrossPlatformClusterController

ctrl = CrossPlatformClusterController()
ctrl.start_local_all()

# Ensure ClothOS Unified Master Server runs on single port 8087
print(">>> [Node 2] Spawning Unified ClothOS Master Server on 8087...")
py_exe = sys.executable
log_dir = pathlib.Path.home() / ".loom" / "logs"

ctrl.spawn_background_service(
    [py_exe, "-m", "uvicorn", "loom.fabric.dashboard_server:app", "--host", "0.0.0.0", "--port", "8087"],
    cwd=ws,
    env={"PYTHONPATH": str(ws), "PYTHONIOENCODING": "utf-8", "CLOTHOS_PORT": "8087"},
    log_name="clothos_dashboard.log",
)

time.sleep(2.0)
print(">>> [Node 2] Services started.")
"""

b64 = base64.b64encode(code.encode("utf-8")).decode("ascii")

job_id = client.submit_job(
    entrypoint=f'python -c "import base64; exec(base64.b64decode(\'{b64}\').decode(\'utf-8\'))"',
)
print(f"Submitted start-all job: {job_id}")

for _ in range(30):
    status = client.get_job_status(job_id)
    if status in [JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.STOPPED]:
        print(f"Status: {status}")
        print("Logs:\n", client.get_job_logs(job_id))
        break
    time.sleep(1)
