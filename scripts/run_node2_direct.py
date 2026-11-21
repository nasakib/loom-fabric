import json
import time
import urllib.request

job_payload = {
    "entrypoint": "python C:/Users/natsa/Documents/loom-fabric/loom/fabric/run_node2_server.py"
}

req = urllib.request.Request(
    "http://100.74.98.21:8265/api/jobs/",
    data=json.dumps(job_payload).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)

with urllib.request.urlopen(req, timeout=10) as resp:
    res = json.loads(resp.read().decode())
    sub_id = res["submission_id"]
    print("Submitted run_node2_server.py job:", sub_id)

for _ in range(25):
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
        print("FAILED logs:")
        print(logs.strip())
        break
