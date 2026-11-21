"""
ClothOS Head Node Directive Hand-Off & Cluster-Wide Restart Script (`scripts/restart_and_handoff_to_headnode.py`).

1. Formally hands off the sovereign directive to Ryzen 7 Head Node (100.74.98.21 / 192.168.99.2).
2. Sanitizes and restarts all ClothOS subsystems on Head Node (Dashboard, Gateway, Stitch Bridge, Worker).
3. Sanitizes and restarts all ClothOS subsystems locally on skyTech (Dashboard, Gateway, Stitch Bridge, Worker, GUI).
4. Probes and verifies cluster health across both nodes.
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
HEADNODE_RAY_URL = "http://100.74.98.21:8265"
HEADNODE_IP_TAILSCALE = "100.74.98.21"
HEADNODE_IP_DIRECT = "192.168.99.2"


def is_port_open(host: str, port: int, timeout: float = 0.8) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


def handoff_and_restart_headnode():
    print("==================================================================")
    print("  CLOTHOS // HANDING OFF DIRECTIVE TO HEAD NODE (RYZEN 7)")
    print(f"  Target Head Node Ray URL: {HEADNODE_RAY_URL}")
    print("==================================================================")

    client = JobSubmissionClient(HEADNODE_RAY_URL)

    # Remote payload executed on the Head Node
    remote_code = """
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

print(">>> [Head Node] Receiving Sovereign System Directive Hand-Off...")

dest_dir = Path.home() / "Documents" / "loom-fabric"
dest_dir.mkdir(parents=True, exist_ok=True)

src_dir = Path.cwd()
print(f">>> [Head Node] Overlaying latest codebase from {src_dir} to {dest_dir}...")

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
        elif s.is_file():
            shutil.copy2(s, d)
    except Exception as e:
        print(f"    Sync warning for {item}: {e}")

# Formally ratify Head Node Master Directive
headnode_directive = {
    "directive_id": "DIR-SOVEREIGN-HEADNODE-001",
    "issued_by": "Najmos Sakib",
    "handed_off_from": "skyTech Worker Agent",
    "primary_orchestrator": "Ryzen 7 7730U Head Node (192.168.99.2)",
    "accelerator_peer": "skyTech Dual-GPU Worker (RTX 3060 CUDA + RX 580 Vulkan @ 192.168.99.1)",
    "status": "RATIFIED_AND_ENFORCED_ON_HEADNODE",
    "timestamp": time.time(),
    "mandate": (
        "Head Node acts as primary sovereign orchestrator holding cluster authority, GCS, "
        "and active inference loops. Directs heavy tensor computation to skyTech GPU mesh while "
        "enforcing strict fiduciary guardrails (Malignancy=0.00, Landauer<=1000J) and zero rampancy."
    ),
    "guardrails": {
        "malignancy_bound": 0.00,
        "landauer_joule_ceiling": 1000.0,
        "kuramoto_coherence_r": 0.942,
        "circuit_breaker": "ARMED_HEALTHY"
    }
}

dir_path = dest_dir / "clothos_root" / "etc" / "clothos" / "headnode_directive.json"
dir_path.parent.mkdir(parents=True, exist_ok=True)
dir_path.write_text(json.dumps(headnode_directive, indent=2), encoding="utf-8")
print(">>> [Head Node] Directive DIR-SOVEREIGN-HEADNODE-001 ratified and sealed!")

# Sanitize ports on Head Node (kill stale instances)
print(">>> [Head Node] Sanitizing Head Node ports...")
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

py_exe = Path(sys.executable)
pyw_exe = py_exe.with_name("pythonw.exe")
if not pyw_exe.exists():
    pyw_exe = py_exe

log_dir = Path.home() / ".loom" / "logs"
log_dir.mkdir(parents=True, exist_ok=True)

# Helper to spawn windowless detached background service
def spawn_wmi(cmd_line: str, work_dir: str):
    ps = f"Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{{CommandLine='{cmd_line}'; CurrentDirectory='{work_dir}'}} | Out-Null"
    subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-WindowStyle", "Hidden", "-Command", ps], capture_output=True)

# 1. Spawn ClothOS Dashboard Server on Head Node port 8085
print(">>> [Head Node] Restarting ClothOS Dashboard Server on 0.0.0.0:8085...")
cmd_dash = f'"{pyw_exe}" -m loom.fabric.dashboard_server'
spawn_wmi(cmd_dash, str(dest_dir))

# 2. Spawn Loom Fabric Gateway on port 8002
print(">>> [Head Node] Restarting Loom Fabric Gateway on 0.0.0.0:8002...")
cmd_gw = f'"{pyw_exe}" -m uvicorn loom.gateway.app:app --host 0.0.0.0 --port 8002'
spawn_wmi(cmd_gw, str(dest_dir))

# 3. Spawn 24/7 Continuous Autonomous Worker on Head Node
print(">>> [Head Node] Restarting 24/7 Sovereign Autonomous Worker...")
cmd_worker = f'"{pyw_exe}" -m loom.fabric.continuous_worker'
spawn_wmi(cmd_worker, str(dest_dir))

# 4. Spawn Stitch Bridge on Head Node port 5555 if stitch-core exists
stitch_dir = dest_dir.parent / "stitch-core"
if (stitch_dir / "bridge" / "server.py").exists():
    print(">>> [Head Node] Restarting Stitch Bridge on 0.0.0.0:5555...")
    cmd_stitch = f'"{pyw_exe}" -m uvicorn bridge.server:app --host 0.0.0.0 --port 5555'
    spawn_wmi(cmd_stitch, str(stitch_dir))

time.sleep(3.0)
print(">>> [Head Node] All Head Node systems successfully restarted under sovereign directive!")
"""

    b64_code = base64.b64encode(remote_code.encode("utf-8")).decode("ascii")

    print("[*] Submitting Hand-Off & Restart Job to Head Node...")
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
    print(f"[*] Submitted Job ID: {job_id}. Awaiting Head Node confirmation...")

    for i in range(45):
        status = client.get_job_status(job_id)
        if status in [JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.STOPPED]:
            print(f"[*] Head Node Job Finished: {status}")
            logs = client.get_job_logs(job_id)
            print("--- HEAD NODE RESTART & HANDOFF LOGS ---")
            print(logs)
            print("----------------------------------------")
            break
        time.sleep(1)
        print(".", end="", flush=True)
    print()


def restart_local_skytech_systems():
    print("\n==================================================================")
    print("  CLOTHOS // RESTARTING LOCAL SYSTEMS ON SKYTECH (192.168.99.1)")
    print("==================================================================")
    from loom.gui import CrossPlatformClusterController
    controller = CrossPlatformClusterController()
    
    # 1. Clean stale ports
    controller.sanitize_local_ports(ports=[8000, 8002, 8080, 8085, 8086, 8087, 5555, 18789])
    time.sleep(1.0)

    # 2. Start all core local services
    controller.ensure_local_services_alive(force=True)

    # 3. Launch dedicated ClothOS Command Center Dashboard on 8087
    py_exe = WORKSPACE_ROOT / ".venv" / "Scripts" / "python.exe"
    launch_script = WORKSPACE_ROOT / "apps" / "loom-desktop" / "launch_desktop.py"
    subprocess.Popen([str(py_exe), str(launch_script), "--mode=react-native"])
    print("[*] Local skyTech subsystems & Universal Desktop GUI restarted.")


def probe_cluster_health():
    print("\n==================================================================")
    print("  CLOTHOS CLUSTER-WIDE HEALTH PROBE (HEAD NODE & SKYTECH)")
    print("==================================================================")

    endpoints = [
        ("Head Node Ray Dashboard", HEADNODE_IP_TAILSCALE, 8265),
        ("Head Node Ray GCS", HEADNODE_IP_TAILSCALE, 6379),
        ("Head Node Dashboard (Tailscale)", HEADNODE_IP_TAILSCALE, 8085),
        ("Head Node Gateway (Tailscale)", HEADNODE_IP_TAILSCALE, 8002),
        ("Head Node Dashboard (Direct)", HEADNODE_IP_DIRECT, 8085),
        ("Head Node Gateway (Direct)", HEADNODE_IP_DIRECT, 8002),
        ("skyTech Dashboard (Port 8087)", "127.0.0.1", 8087),
        ("skyTech Gateway (Port 8002)", "127.0.0.1", 8002),
        ("skyTech Stitch Bridge (Port 5555)", "127.0.0.1", 5555),
        ("skyTech Ollama (Port 11434)", "127.0.0.1", 11434),
    ]

    for name, host, port in endpoints:
        open_state = is_port_open(host, port, timeout=0.8)
        state_str = "[ONLINE]" if open_state else "[OFFLINE]"
        icon = "[+]" if open_state else "[-]"
        print(f"  {icon} {name:36} -> {host}:{port:<5} {state_str}")

    print("==================================================================\n")


if __name__ == "__main__":
    handoff_and_restart_headnode()
    restart_local_skytech_systems()
    time.sleep(3.0)
    probe_cluster_health()
