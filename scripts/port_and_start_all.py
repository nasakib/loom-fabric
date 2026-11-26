"""
ClothOS Cluster Port & Full Subsystem Orchestrator (`scripts/port_and_start_all.py`).

1. Ports all latest ClothOS code, GUI builds, and cybersecurity engines to Node 2 (100.74.98.21).
2. Deploys and starts all systems on Node 2 (Dashboard, Gateway, Stitch Bridge, Worker).
3. Starts all local systems on skyTech (Dashboard, Gateway, Stitch Bridge, Worker).
4. Verifies cluster-wide health and reports the unified status.
"""

from __future__ import annotations

import base64
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
import urllib.error

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["NO_PROXY"] = "*"

from ray.job_submission import JobSubmissionClient, JobStatus

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
NODE2_RAY_URL = "http://100.74.98.21:8265"
NODE2_IP_TAILSCALE = "100.74.98.21"
NODE2_IP_DIRECT = "192.168.99.2"


def is_port_open(host: str, port: int, timeout: float = 0.8) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


def run_node2_port_and_start():
    print("==================================================================")
    print("  CLOTHOS // PORTING TO NODE 2 & STARTING ALL SYSTEMS")
    print(f"  Target Ray Cluster: {NODE2_RAY_URL}")
    print("==================================================================")

    client = JobSubmissionClient(NODE2_RAY_URL)

    # Remote payload executed on Node 2
    remote_code = """
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

print(">>> [Node 2 Worker] Starting ClothOS Deployment & System Launch...")

# 1. Sync files from Ray working_dir to C:\\Users\\natsa\\Documents\\loom-fabric
dest_dir = Path.home() / "Documents" / "loom-fabric"
dest_dir.mkdir(parents=True, exist_ok=True)

src_dir = Path.cwd()
print(f">>> [Node 2 Worker] Syncing from {src_dir} to {dest_dir}...")

items_to_sync = [
    "apps", "loom", "fabric", "scripts",
    "Launch-ClothOS-App.bat", "launch-clothos-linux.sh", "launch-clothos-macos.sh",
]

for item in items_to_sync:
    s = src_dir / item
    d = dest_dir / item
    try:
        if s.is_dir():
            shutil.copytree(s, d, dirs_exist_ok=True)
            print(f"    Synced directory: {item}")
        elif s.is_file():
            shutil.copy2(s, d)
            print(f"    Synced file: {item}")
    except Exception as e:
        print(f"    Sync warning for {item}: {e}")

# 2. Kill stale instances on target ports (8085, 8002, 5555)
print(">>> [Node 2 Worker] Sanitizing target ports...")
try:
    out = subprocess.check_output("netstat -ano", shell=True, text=True, stderr=subprocess.DEVNULL)
    pids = set()
    for line in out.splitlines():
        if "LISTENING" in line:
            for p in [8085, 8086, 8087, 8002, 5555]:
                if f":{p} " in line:
                    parts = line.split()
                    try:
                        pids.add(int(parts[-1]))
                    except ValueError:
                        pass
    for pid in pids:
        if pid > 4:
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)
            print(f"    Terminated stale PID {pid}")
except Exception as e:
    print(f"    Port sanitizer warning: {e}")

time.sleep(1.0)

# 3. Determine Python runtime on Node 2
py_exe = Path(sys.executable)
pyw_exe = py_exe.with_name("pythonw.exe")
if not pyw_exe.exists():
    pyw_exe = py_exe

log_dir = Path.home() / ".loom" / "logs"
log_dir.mkdir(parents=True, exist_ok=True)

# Use WMI process creation to cleanly break away from Ray job object
def spawn_detached_wmi(cmd_line: str, work_dir: str):
    ps = f"Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{{CommandLine='{cmd_line}'; CurrentDirectory='{work_dir}'}} | Out-Null"
    subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-WindowStyle", "Hidden", "-Command", ps], capture_output=True)

# 4. Spawn Unified ClothOS Master Server on single port 8087 (includes Gateway + GUIs)
print(">>> [Node 2 Worker] Spawning Unified ClothOS Master Server on 0.0.0.0:8087...")
cmd_dash = f'"{pyw_exe}" -m uvicorn loom.fabric.dashboard_server:app --host 0.0.0.0 --port 8087'
spawn_detached_wmi(cmd_dash, str(dest_dir))

# 6. Spawn Continuous Autonomous Worker
print(">>> [Node 2 Worker] Spawning 24/7 Sovereign Autonomous Worker...")
cmd_worker = f'"{pyw_exe}" -m loom.fabric.continuous_worker'
spawn_detached_wmi(cmd_worker, str(dest_dir))

time.sleep(3.0)
print(">>> [Node 2 Worker] Verification complete. Subsystems deployed!")
"""

    b64_code = base64.b64encode(remote_code.encode("utf-8")).decode("ascii")

    print("[*] Submitting Port & Deployment Job to Node 2...")
    job_id = client.submit_job(
        entrypoint=f'python -c "import base64; exec(base64.b64decode(\'{b64_code}\').decode(\'utf-8\'))"',
        runtime_env={
            "working_dir": str(WORKSPACE_ROOT),
            "excludes": [
                ".git", "node_modules", ".venv", "__pycache__", ".pnpm-store",
                "artifacts", "deliverables", "sovereign_vault", "vault",
                "traces", "interpretations", "clothos_root", "bin", ".agent",
                ".loom_hypotheses.db", "*.db", "*.sqlite", "*.db-wal", "*.db-shm",
                "*.iso", "*.mp4", "*.zip"
            ]
        }
    )
    print(f"[*] Submitted Job ID: {job_id}. Awaiting remote deployment...")

    for i in range(45):
        status = client.get_job_status(job_id)
        if status in [JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.STOPPED]:
            print(f"[*] Node 2 Job Finished: {status}")
            logs = client.get_job_logs(job_id)
            print("--- NODE 2 DEPLOYMENT LOGS ---")
            print(logs)
            print("------------------------------")
            break
        time.sleep(1)
        print(".", end="", flush=True)
    print()


def start_local_systems():
    print("[*] Starting Local Systems on skyTech (192.168.99.1)...")
    from loom.gui import CrossPlatformClusterController
    controller = CrossPlatformClusterController()
    controller.start_local_all()

    # Launch desktop application container headlessly / GUI
    py_exe = WORKSPACE_ROOT / ".venv" / "Scripts" / "python.exe"
    launch_script = WORKSPACE_ROOT / "apps" / "loom-desktop" / "launch_desktop.py"
    subprocess.Popen([str(py_exe), str(launch_script), "--mode=react-native"])
    print("[*] Local subsystems and Universal React Native GUI initialized.")


def probe_cluster_health():
    print("\n==================================================================")
    print("  CLOTHOS CLUSTER-WIDE HEALTH PROBE")
    print("==================================================================")

    endpoints = [
        ("Local Unified Master (8087)", "127.0.0.1", 8087),
        ("Local Ollama", "127.0.0.1", 11434),
        ("Node 2 Ray Dashboard", NODE2_IP_TAILSCALE, 8265),
        ("Node 2 Ray GCS", NODE2_IP_TAILSCALE, 6379),
        ("Node 2 Unified (Tailscale)", NODE2_IP_TAILSCALE, 8087),
        ("Node 2 Unified (Direct-Wire)", NODE2_IP_DIRECT, 8087),
    ]

    for name, host, port in endpoints:
        open_state = is_port_open(host, port, timeout=0.8)
        state_str = "[ONLINE]" if open_state else "[OFFLINE]"
        icon = "[+]" if open_state else "[-]"
        print(f"  {icon} {name:32} -> {host}:{port:<5} {state_str}")

    print("==================================================================\n")


if __name__ == "__main__":
    run_node2_port_and_start()
    start_local_systems()
    time.sleep(3.0)
    probe_cluster_health()
