# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
Remote Node 2 GUI & Desktop Shortcut Provisioner (`scripts/setup_node2_gui_and_shortcuts.py`).

Submits a Ray job to Node 2 (100.74.98.21:8265) to:
1. Copy updated files from the Ray runtime_env into the permanent workspace `~/Documents/loom-fabric`.
2. Generate all desktop shortcuts on Node 2's desktop (pointing to local Node 2 server and Node 1 remote).
3. Ensure ClothOS Dashboard Server is running on Node 2.
4. Launch the desktop GUI window on Node 2.
"""

import base64
import os
import sys
import time

os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["NO_PROXY"] = "*"

from ray.job_submission import JobSubmissionClient, JobStatus

client = JobSubmissionClient("http://100.74.98.21:8265")

remote_code = """
import os
import pathlib
import shutil
import subprocess
import sys
import time

print(">>> [Node 2] Initializing GUI & Shortcut Provisioning...")

runtime_dir = pathlib.Path(".").resolve()
ws = pathlib.Path.home() / "Documents" / "loom-fabric"
ws.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ws))

# 1. Ensure latest scripts and files are present
print(f">>> [Node 2] Copying synced files from Ray runtime_env {runtime_dir} to permanent workspace {ws}...")
for item in runtime_dir.iterdir():
    if item.name.startswith(".git") or item.name == "__pycache__":
        continue
    dest = ws / item.name
    try:
        if item.is_dir():
            shutil.copytree(item, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dest)
    except Exception as e:
        print(f">>> [Node 2] Warning copying {item.name}: {e}")

os.chdir(str(ws))
print(f">>> [Node 2] Permanent workspace successfully synchronized at {ws}.")

# Helper to spawn detached background process via WMI
def spawn_wmi(cmd_line: str, work_dir: str):
    ps = f"Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{{CommandLine='{cmd_line}'; CurrentDirectory='{work_dir}'}} | Out-Null"
    subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-WindowStyle", "Hidden", "-Command", ps], capture_output=True)

py_exe = ws / ".venv" / "Scripts" / "python.exe"
if not py_exe.exists():
    py_exe = pathlib.Path(sys.executable)

# 2. Run shortcut generator on Node 2
shortcut_script = ws / "scripts" / "create_desktop_shortcuts.py"
if shortcut_script.exists():
    print(f">>> [Node 2] Executing {shortcut_script}...")
    res = subprocess.run([str(py_exe), str(shortcut_script)], capture_output=True, text=True)
    print(">>> [Node 2] Shortcut Generator Output:")
    print(res.stdout)
    if res.stderr:
        print(">>> [Node 2] Shortcut Generator Stderr:")
        print(res.stderr)
else:
    print(f">>> [Node 2] Shortcut script not found at {shortcut_script}")

# 3. Clean any stale processes holding 8087 on Node 2 and spawn Dashboard Server
print(">>> [Node 2] Ensuring Dashboard Server is running on Node 2 (port 8087)...")
try:
    out = subprocess.check_output("netstat -ano", shell=True, text=True, stderr=subprocess.DEVNULL)
    for line in out.splitlines():
        if "LISTENING" in line and ":8087 " in line:
            parts = line.split()
            try:
                pid = int(parts[-1])
                if pid > 4:
                    subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)
                    print(f">>> [Node 2] Terminated stale PID {pid} on 8087")
            except ValueError:
                pass
except Exception as e:
    print(f">>> [Node 2] Netstat scan note: {e}")

cmd_dash = f'"{py_exe}" -m loom.fabric.dashboard_server'
print(f">>> [Node 2] Spawning Dashboard Server via WMI: {cmd_dash}")
spawn_wmi(cmd_dash, str(ws))

# 4. Launch Desktop GUI on Node 2
desktop_launcher = ws / "apps" / "loom-desktop" / "launch_desktop.py"
if desktop_launcher.exists():
    cmd_gui = f'"{py_exe}" "{desktop_launcher}" --visuals'
    print(f">>> [Node 2] Spawning ClothOS Desktop GUI via WMI: {cmd_gui}")
    spawn_wmi(cmd_gui, str(ws))
    print(">>> [Node 2] Desktop GUI spawned via WMI.")

print(">>> [Node 2] GUI and shortcuts provisioning complete!")
"""

b64 = base64.b64encode(remote_code.encode("utf-8")).decode("ascii")

print("Submitting Node 2 GUI & Desktop Setup job to Ray cluster...")
job_id = client.submit_job(
    entrypoint=f'python -c "import base64; exec(base64.b64decode(\'{b64}\').decode(\'utf-8\'))"',
    runtime_env={
        "working_dir": ".",
        "excludes": [
            ".git", "node_modules", ".venv", "__pycache__", ".pnpm-store",
            "apps/loom-react-native/node_modules", "artifacts", "deliverables",
            "sovereign_vault", "vault", "traces", "interpretations",
            "clothos_root", "bin", ".agent", ".loom_hypotheses.db",
            "*.db", "*.sqlite", "*.db-wal", "*.db-shm"
        ]
    }
)
print(f"Submitted Node 2 Job ID: {job_id}")

for _ in range(40):
    status = client.get_job_status(job_id)
    if status in [JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.STOPPED]:
        print(f"Job {job_id} finished with status: {status}")
        logs = client.get_job_logs(job_id)
        print("Remote Node 2 Execution Logs:\n", logs)
        break
    time.sleep(1)
