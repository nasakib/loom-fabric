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
import os, sys, pathlib

log_dir = pathlib.Path.home() / ".loom" / "logs"
print("=== LOG FILES IN ~/.loom/logs ===")
if log_dir.exists():
    for f in log_dir.iterdir():
        if f.is_file():
            print(f"--- {f.name} (size: {f.stat().st_size} bytes) ---")
            try:
                content = f.read_text(encoding='utf-8', errors='replace')
                print(content[-1000:] if len(content) > 1000 else content)
            except Exception as e:
                print(f"Error reading {f.name}: {e}")
else:
    print("Log dir does not exist!")

print("=== CHECKING PYTHON PROCESSES ===")
try:
    import subprocess
    out = subprocess.check_output("tasklist /FI \\\"IMAGENAME eq python*\\\"", shell=True, text=True)
    print(out)
except Exception as e:
    print("Tasklist error:", e)
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
