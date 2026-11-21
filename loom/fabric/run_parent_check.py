import json
import time
import urllib.request
from loom.fabric.bandwidth_mesh import bandwidth_mesh

print("Syncing node2_parent_check.py...")
res = bandwidth_mesh.sync_payload_to_headnode(["loom/fabric/node2_parent_check.py"])
print("Sync result:", res)
time.sleep(1)

job_url = "http://100.74.98.21:8265/api/jobs/"
job_cmd = (
    'python -c "import sys, os; '
    'p = r\'C:\\Users\\natsa\\Documents\\loom-fabric\'; '
    'sys.path.insert(0, p); '
    'os.chdir(p); '
    'import loom.fabric.node2_parent_check"'
)

req = urllib.request.Request(
    job_url,
    data=json.dumps({"entrypoint": job_cmd}).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST"
)

sub_id = json.loads(urllib.request.urlopen(req, timeout=5).read().decode("utf-8"))["submission_id"]
print("Submitted job:", sub_id)

for _ in range(30):
    time.sleep(1)
    status = json.loads(urllib.request.urlopen(f"{job_url}{sub_id}", timeout=5).read().decode("utf-8"))["status"]
    if status in ["SUCCEEDED", "FAILED", "STOPPED"]:
        logs = urllib.request.urlopen(f"{job_url}{sub_id}/logs", timeout=5).read().decode("utf-8")
        parsed = json.loads(logs).get("logs", logs)
        print("\n" + parsed)
        break
