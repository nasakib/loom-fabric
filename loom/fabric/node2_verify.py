import json
import time
import urllib.request

job_url = 'http://100.74.98.21:8265/api/jobs/'
check_cmd = 'python -c "import os; p=r\'C:\\Users\\natsa\\Documents\\loom-fabric\'; [print(f, os.path.exists(os.path.join(p, f))) for f in [\'loom/fabric/port_manager.py\', \'loom/fabric/dashboard_server.py\', \'loom/si/spiritual_epistemology.py\', \'apps/loom-desktop/launch_desktop.py\']]"'
req = urllib.request.Request(
    job_url,
    data=json.dumps({'entrypoint': check_cmd}).encode('utf-8'),
    headers={'Content-Type': 'application/json'},
    method='POST'
)
sub_id = json.loads(urllib.request.urlopen(req, timeout=5).read().decode('utf-8'))['submission_id']
print('Submitted verification job:', sub_id)
time.sleep(3)
logs = urllib.request.urlopen(f'{job_url}{sub_id}/logs', timeout=5).read().decode('utf-8')
print('Verification logs from Node 2:\n', logs)
