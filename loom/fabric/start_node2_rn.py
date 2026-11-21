import json
import time
import urllib.request

job_url = "http://100.74.98.21:8265/api/jobs/"
job_cmd = (
    'python -c "import sys, os; '
    'p = r\'C:\\Users\\natsa\\Documents\\loom-fabric\'; '
    'sys.path.insert(0, p); '
    'os.chdir(p); '
    'import apps.loom_react_native.serve_rn as rn; '
    'rn.run_react_native_server(launch_browser=False)"'
)

# Replace dot with standard path execution
job_cmd = (
    'python loom-fabric/apps/loom-react-native/serve_rn.py --no-browser'
)

req = urllib.request.Request(
    job_url,
    data=json.dumps({"entrypoint": job_cmd}).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST"
)

sub_id = json.loads(urllib.request.urlopen(req, timeout=5).read().decode("utf-8"))["submission_id"]
print("Submitted Node 2 React Native server launch job:", sub_id)
time.sleep(2)

status = json.loads(urllib.request.urlopen(f"{job_url}{sub_id}", timeout=5).read().decode("utf-8"))["status"]
print("Node 2 React Native Job status:", status)
