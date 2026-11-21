import json
import time
import urllib.request

job_url = "http://100.74.98.21:8265/api/jobs/"
script = """
import subprocess
try:
    cmd = 'powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.ProcessId -in @(38636, 26920) } | Select-Object ProcessId, ParentProcessId, Name, CommandLine | Format-List"'
    out = subprocess.check_output(cmd, shell=True, text=True)
    print(out)
except Exception as e:
    print('Error:', e)
"""

req = urllib.request.Request(
    job_url,
    data=json.dumps({"entrypoint": f'python -c "{"; ".join([l.strip() for l in script.strip().splitlines() if l.strip()])}"'}).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST"
)
sub_id = json.loads(urllib.request.urlopen(req, timeout=5).read().decode("utf-8"))["submission_id"]
time.sleep(3)
logs = urllib.request.urlopen(f"{job_url}{sub_id}/logs", timeout=5).read().decode("utf-8")
print(json.loads(logs).get("logs", logs))
