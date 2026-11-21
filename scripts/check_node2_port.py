import json
import time
import urllib.request

job_payload = {
    "entrypoint": "python -c \"import pathlib, json; ws = pathlib.Path.home() / 'Documents' / 'loom-fabric'; pf = ws / '.loom_dashboard_port'; pidf = ws / '.loom_dashboard_pid'; print('DASHBOARD_PORT:', pf.read_text().strip() if pf.exists() else 'NONE'); print('DASHBOARD_PID:', pidf.read_text().strip() if pidf.exists() else 'NONE')\""
}

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
