import json
import time
import urllib.request

job_url = "http://100.74.98.21:8265/api/jobs/"
script = (
    "import subprocess; "
    "ps_cmd = 'Get-CimInstance Win32_Process -Filter \"ProcessId = 38636\" | Select-Object ProcessId, ParentProcessId, Name, CommandLine, Path | Format-List'; "
    "out = subprocess.check_output(['powershell', '-NoProfile', '-Command', ps_cmd], text=True); "
    "print(out)"
)

req = urllib.request.Request(
    job_url,
    data=json.dumps({"entrypoint": f'python -c "{script}"'}).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST"
)
sub_id = json.loads(urllib.request.urlopen(req, timeout=5).read().decode("utf-8"))["submission_id"]
time.sleep(3)
logs = urllib.request.urlopen(f"{job_url}{sub_id}/logs", timeout=5).read().decode("utf-8")
print("Process 38636 info:\n", json.loads(logs).get("logs", logs))
