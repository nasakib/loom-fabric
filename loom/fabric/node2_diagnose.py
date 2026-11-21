import json
import os
import subprocess
import time
import urllib.request

job_url = 'http://100.74.98.21:8265/api/jobs/'

diag_script = (
    "import subprocess, json, os; "
    "procs = subprocess.check_output('tasklist /FO CSV /NH', shell=True).decode('utf-8', 'ignore'); "
    "cmd_procs = [line for line in procs.splitlines() if 'cmd.exe' in line.lower() or 'conhost.exe' in line.lower() or 'python' in line.lower()]; "
    "print('=== MATCHING PROCESSES ON NODE 2 ==='); "
    "[print(p) for p in cmd_procs]; "
    "sch = subprocess.check_output('schtasks /query /fo csv /nh', shell=True).decode('utf-8', 'ignore'); "
    "loom_tasks = [t for t in sch.splitlines() if 'loom' in t.lower() or 'fabric' in t.lower() or 'cloth' in t.lower()]; "
    "print('=== SCHEDULED TASKS ==='); "
    "[print(t) for t in loom_tasks]; "
    "import psutil; "
    "print('=== RAY WORKER / CHILD PROCESSES ==='); "
    "for p in psutil.process_iter(['pid', 'name', 'cmdline']): "
    "  try: "
    "    info = p.info; "
    "    if 'cmd.exe' in (info['name'] or '').lower() or 'powershell' in (info['name'] or '').lower(): "
    "      print(info['pid'], info['name'], info['cmdline']); "
    "  except Exception: pass"
)

req = urllib.request.Request(
    job_url,
    data=json.dumps({'entrypoint': f'python -c "{diag_script}"'}).encode('utf-8'),
    headers={'Content-Type': 'application/json'},
    method='POST'
)

sub_id = json.loads(urllib.request.urlopen(req, timeout=5).read().decode('utf-8'))['submission_id']
print('Submitted diagnostics job:', sub_id)

for _ in range(15):
    time.sleep(1)
    st = json.loads(urllib.request.urlopen(f"{job_url}{sub_id}", timeout=5).read().decode('utf-8'))['status']
    if st in ['SUCCEEDED', 'FAILED', 'STOPPED']:
        logs = urllib.request.urlopen(f"{job_url}{sub_id}/logs", timeout=5).read().decode('utf-8')
        print("=== NODE 2 DIAGNOSTICS LOGS ===")
        print(logs)
        break
