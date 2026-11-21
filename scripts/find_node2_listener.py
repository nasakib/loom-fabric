import json
import time
import urllib.request

remote_code = """
import os, psutil, subprocess

for conn in psutil.net_connections(kind='inet'):
    if conn.laddr.port == 8087 and conn.status == 'LISTEN':
        p = psutil.Process(conn.pid)
        print('LISTEN_PID:', conn.pid)
        print('EXE:', p.exe())
        print('CMDLINE:', p.cmdline())
        print('CWD:', p.cwd())
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
