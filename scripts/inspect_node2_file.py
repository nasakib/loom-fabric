import json
import time
import urllib.request

job_payload = {
    "entrypoint": "python -c \"import pathlib; ws = pathlib.Path.home() / 'Documents' / 'loom-fabric'; f = ws / 'loom' / 'fabric' / 'dashboard_server.py'; print('EXISTS:', f.exists()); content = f.read_text(encoding='utf-8', errors='ignore') if f.exists() else ''; print('HAS_BICAMERAL:', 'bicameral' in content); print('LINES:', len(content.splitlines()))\""
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
