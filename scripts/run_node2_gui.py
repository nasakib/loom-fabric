# Copyright (c) 2026 Najmos Sakib. All rights reserved.
"""Node 2 GUI and Dashboard Verification Runner."""

import base64
import os
import sys
import time

os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["NO_PROXY"] = "*"

from ray.job_submission import JobSubmissionClient, JobStatus

client = JobSubmissionClient("http://100.74.98.21:8265")

remote_code = '''
import os
import pathlib
import shutil
import subprocess
import sys
import time
import urllib.request
import json

runtime_dir = pathlib.Path(".").resolve()
ws = pathlib.Path.home() / "Documents" / "loom-fabric"
ws.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ws))

# Copy synced files from Ray runtime_env
print(f">>> [Node 2] Overlaying synced files from {runtime_dir} into {ws}...")
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

# Clean up corrupted hypothesis db if present
for db_file in [ws / ".loom_hypotheses.db", pathlib.Path.home() / ".loom" / "hypotheses.db"]:
    if db_file.exists():
        try:
            import sqlite3
            c = sqlite3.connect(str(db_file))
            c.execute("SELECT count(*) FROM hypotheses")
            c.close()
        except Exception as e:
            print(f">>> [Node 2] Removing corrupt DB {db_file}: {e}")
            try:
                db_file.unlink(missing_ok=True)
            except Exception:
                pass

py_exe = ws / ".venv" / "Scripts" / "python.exe"
if not py_exe.exists():
    py_exe = pathlib.Path(sys.executable)

print(">>> [Node 2] Python exe:", py_exe)
print(">>> [Node 2] Workspace:", ws)

# Check if dashboard server is alive
healthy = False
try:
    with urllib.request.urlopen("http://127.0.0.1:8087/api/health", timeout=1.5) as r:
        if r.status == 200:
            data = json.loads(r.read().decode())
            print(">>> [Node 2] Server is already healthy on 8087:", data.get("status"))
            healthy = True
except Exception as e:
    print(">>> [Node 2] Server not healthy on 8087 yet:", e)

if not healthy:
    print(">>> [Node 2] Launching dashboard server as detached background process...")
    DETACHED = 0x00000008 | 0x00000200
    env = {**os.environ, "PYTHONPATH": str(ws), "PYTHONIOENCODING": "utf-8", "CLOTHOS_PORT": "8087"}
    log_file = ws / "node2_server_out.log"
    out_f = open(log_file, "a", encoding="utf-8", errors="replace")
    proc = subprocess.Popen(
        [str(py_exe), "-m", "loom.fabric.dashboard_server"],
        cwd=str(ws),
        env=env,
        stdout=out_f,
        stderr=subprocess.STDOUT,
        creationflags=DETACHED
    )
    print(f">>> [Node 2] Spawned dashboard_server PID {proc.pid}")
    
    # Wait for it to become healthy
    for i in range(15):
        time.sleep(1.0)
        try:
            with urllib.request.urlopen("http://127.0.0.1:8087/api/health", timeout=1.0) as r:
                if r.status == 200:
                    print(f">>> [Node 2] Confirmed server healthy on port 8087 after {i+1}s!")
                    healthy = True
                    break
        except Exception:
            pass

    if not healthy:
        print(">>> [Node 2] Warning: server did not respond healthy in 15s. Recent logs:")
        if log_file.exists():
            print(log_file.read_text(encoding="utf-8", errors="replace")[-1000:])

# Launch desktop GUI
launcher = ws / "apps" / "loom-desktop" / "launch_desktop.py"
if launcher.exists():
    print(">>> [Node 2] Launching Desktop GUI window (--visuals)...")
    DETACHED = 0x00000008 | 0x00000200
    subprocess.Popen(
        [str(py_exe), str(launcher), "--visuals"],
        cwd=str(ws),
        creationflags=DETACHED
    )
    print(">>> [Node 2] Desktop GUI spawned.")

print(">>> [Node 2] All done!")
'''

b64 = base64.b64encode(remote_code.encode("utf-8")).decode("ascii")

job_id = client.submit_job(
    entrypoint=f'python -c "import base64; exec(base64.b64decode(\'{b64}\').decode(\'utf-8\'))"',
    runtime_env={
        "working_dir": ".",
        "excludes": [
            ".git", "node_modules", ".venv", "__pycache__", ".pnpm-store",
            "apps/loom-react-native/node_modules", "artifacts", "deliverables",
            "sovereign_vault", "vault", "traces", "interpretations",
            "clothos_root", "bin", ".agent", "*.db", "*.sqlite", "*.db-wal", "*.db-shm"
        ]
    }
)
print(f"Submitted job: {job_id}")

for _ in range(40):
    status = client.get_job_status(job_id)
    if status in [JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.STOPPED]:
        print(f"Job finished with status: {status}")
        print("Logs:\n", client.get_job_logs(job_id))
        break
    time.sleep(1)
