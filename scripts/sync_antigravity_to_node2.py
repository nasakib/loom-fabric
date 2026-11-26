# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
Synchronizes the Antigravity Universal GUI Suite, Desktop Startup Manager,
and Legacy Cleanup to Node 2 (Ryzen7-Head at 100.74.98.21:8265).
"""

import base64
import os
import sys
import time

os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["NO_PROXY"] = "*"

from ray.job_submission import JobSubmissionClient, JobStatus

NODE2_RAY_URL = "http://100.74.98.21:8265"
client = JobSubmissionClient(NODE2_RAY_URL)

remote_code = """
import os
import pathlib
import shutil
import subprocess
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def safe_print(*args, **kwargs):
    text = " ".join(str(a) for a in args)
    ascii_text = text.encode("ascii", errors="replace").decode("ascii")
    print(ascii_text, **kwargs)

safe_print(">>> [Node 2 / Ryzen7-Head] Initializing Antigravity GUI & Agent Synchronization...")

runtime_dir = pathlib.Path(".").resolve()
ws = pathlib.Path.home() / "Documents" / "loom-fabric"
ws.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ws))

# 1. Synchronize all newly created/updated files from runtime_env to permanent workspace
safe_print(f">>> [Node 2] Copying files from {runtime_dir} to {ws}...")
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
        safe_print(f">>> [Node 2] Note on {item.name}: {e}")

os.chdir(str(ws))
safe_print(f">>> [Node 2] Permanent workspace synchronized at {ws}.")

# Python executable
py_exe = ws / ".venv" / "Scripts" / "python.exe"
if not py_exe.exists():
    py_exe = pathlib.Path(sys.executable)

# 2. Run desktop_startup_manager.py on Node 2 (cleans legacy, installs shortcuts & startup, ensures services)
manager_script = ws / "guis" / "desktop_startup_manager.py"
if manager_script.exists():
    safe_print(f">>> [Node 2] Executing desktop_startup_manager.py --setup...")
    res = subprocess.run([str(py_exe), str(manager_script), "--setup"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    safe_print(">>> [Node 2] Startup Manager Output:")
    safe_print(res.stdout)
    if res.stderr:
        safe_print(">>> [Node 2] Errors/Warnings:")
        safe_print(res.stderr)
else:
    safe_print(f">>> [Node 2] Error: manager script not found at {manager_script}")

# 3. Test ClothOS Agent CLI on Node 2
agent_script = ws / "loom" / "clothos" / "agent_cli.py"
if agent_script.exists():
    safe_print(f">>> [Node 2] Testing ClothOS Agent CLI on Node 2...")
    res_agent = subprocess.run([str(py_exe), str(agent_script), "-p", "Calculate the first 8 Fibonacci numbers in Python"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    safe_print(">>> [Node 2] Agent CLI Output:")
    safe_print(res_agent.stdout)
    if res_agent.stderr:
        safe_print(res_agent.stderr)

# 4. Verify Unified ClothOS Master server on single port 8087 (/guis mounted natively)
safe_print(">>> [Node 2] Checking Unified Master GUI server on single port 8087...")
import urllib.request
try:
    with urllib.request.urlopen("http://localhost:8087/guis/index.html", timeout=3.0) as r:
        safe_print(f">>> [Node 2] Unified Master GUI server responded: HTTP {r.status}")
except Exception as e:
    safe_print(f">>> [Node 2] Local GUI server note: {e}")

safe_print(">>> [Node 2 / Ryzen7-Head] Antigravity GUI Suite & Agent CLI Synchronization COMPLETE!")
"""


b64 = base64.b64encode(remote_code.encode("utf-8")).decode("ascii")

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

def sync():
    print("==================================================================")
    print("[SYNC] Synchronizing Antigravity GUI Suite to Node 2 (Ryzen7-Head)...")
    print(f"Target: {NODE2_RAY_URL}")
    print("==================================================================")

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
    print(f"Submitted Ray Job ID to Node 2: {job_id}")

    for _ in range(60):
        status = client.get_job_status(job_id)
        if status in [JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.STOPPED]:
            print(f"\nJob {job_id} finished with status: {status}")
            try:
                logs = client.get_job_logs(job_id)
                print("\nRemote Node 2 Execution Logs:\n" + ("-" * 60))
                print(logs)
                print("-" * 60)
            except Exception as log_err:
                print(f"\n[Note] Remote logs handled with ASCII guard: {log_err}")
            return status == JobStatus.SUCCEEDED
        time.sleep(1)

    print("[!] Job timed out waiting for completion.")
    return False

if __name__ == "__main__":
    success = sync()
    sys.exit(0 if success else 1)
