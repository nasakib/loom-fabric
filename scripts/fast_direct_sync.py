import base64
import json
import pathlib
import time
import urllib.request

ws = pathlib.Path(__file__).resolve().parents[1]
bundle_path = ws / "loom" / "fabric" / "sync_bundle.zip"
if not bundle_path.exists():
    from loom.fabric.node2_sync import build_bundle
    data, sha, packed = build_bundle()
    bundle_path.write_bytes(data)
else:
    data = bundle_path.read_bytes()

b64_str = base64.b64encode(data).decode("ascii")
print(f"Sync bundle size: {len(data):,} bytes (b64: {len(b64_str):,} chars)")

# Submit self-extracting Ray job to Node 2
remote_script = f'''
import base64, zipfile, io, os, pathlib

raw = base64.b64decode("{b64_str}")
target = pathlib.Path.home() / "Documents" / "loom-fabric"
target.mkdir(parents=True, exist_ok=True)
zf = zipfile.ZipFile(io.BytesIO(raw))
zf.extractall(str(target))
print(f"FAST_SYNC_EXTRACTED_{{len(zf.namelist())}}_FILES_TO_{{target}}")

# Run launcher script
import subprocess, sys
run_script = target / "loom" / "fabric" / "run_node2_server.py"
if run_script.exists():
    print("Executing run_node2_server.py...")
    p = subprocess.run([sys.executable, str(run_script)], capture_output=True, text=True)
    print("STDOUT:", p.stdout)
    print("STDERR:", p.stderr)
'''

job_payload = {
    "entrypoint": f'python -c "{remote_script}"'
}

req = urllib.request.Request(
    "http://100.74.98.21:8265/api/jobs/",
    data=json.dumps(job_payload).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)

with urllib.request.urlopen(req, timeout=30) as resp:
    res = json.loads(resp.read().decode())
    sub_id = res["submission_id"]
    print("Submitted fast direct sync job to Node 2:", sub_id)

for _ in range(30):
    time.sleep(1.5)
    status_req = urllib.request.Request(f"http://100.74.98.21:8265/api/jobs/{sub_id}")
    st = json.loads(urllib.request.urlopen(status_req).read().decode())
    print("Status:", st["status"])
    if st["status"] == "SUCCEEDED":
        log_req = urllib.request.Request(f"http://100.74.98.21:8265/api/jobs/{sub_id}/logs")
        logs = json.loads(urllib.request.urlopen(log_req).read().decode())["logs"]
        print("=== Node 2 Extraction & Run Output ===")
        print(logs.strip())
        break
    elif st["status"] in ["FAILED", "STOPPED"]:
        log_req = urllib.request.Request(f"http://100.74.98.21:8265/api/jobs/{sub_id}/logs")
        logs = json.loads(urllib.request.urlopen(log_req).read().decode())["logs"]
        print("FAILED:", logs.strip())
        break
