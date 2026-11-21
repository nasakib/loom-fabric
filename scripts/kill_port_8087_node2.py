import json
import time
import urllib.request

remote_code = """
import subprocess

p = subprocess.run("netstat -ano | findstr :8087", shell=True, capture_output=True, text=True)
print("NETSTAT OUTPUT:")
print(p.stdout)
for line in p.stdout.strip().splitlines():
    if "LISTENING" in line:
        pid = line.strip().split()[-1]
        print("Found LISTENING PID:", pid)
        # Kill it!
        k = subprocess.run(f"taskkill /F /PID {pid}", shell=True, capture_output=True, text=True)
        print("Kill result:", k.stdout, k.stderr)
"""

job_payload = {"entrypoint": f'python -c "{remote_code}"'}
req = urllib.request.Request(
    "http://100.74.98.21:8265/api/jobs/",
    data=json.dumps(job_payload).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)
res = json.loads(urllib.request.urlopen(req).read().decode())
sub_id = res["submission_id"]

for _ in range(10):
    time.sleep(1.0)
    status_req = urllib.request.Request(f"http://100.74.98.21:8265/api/jobs/{sub_id}")
    st = json.loads(urllib.request.urlopen(status_req).read().decode())
    if st["status"] == "SUCCEEDED":
        log_req = urllib.request.Request(f"http://100.74.98.21:8265/api/jobs/{sub_id}/logs")
        logs = json.loads(urllib.request.urlopen(log_req).read().decode())["logs"]
        print(logs.strip())
        break
