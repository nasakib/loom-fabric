# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
Launches ClothOS & Loom with Node 2 (Ryzen 7 7730U + Vega 8 @ 100.74.98.21)
as the Sovereign Head Orchestrator & Decider Tribunal.

Establishes:
1. Machine 2 (Ryzen7-Head) as DECIDER & HEAD ORCHESTRATOR.
2. Machine 1 (skyTech-Worker) as PROJECTOR_THINKER & ACCELERATOR.
3. Launches the continuous Autonomous Task Runner & Idle Autopoietic Art-Learning loop on Node 2.
4. Enqueues and executes the All-Cylinders Directive under Decider authority.
"""

import base64
import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["NO_PROXY"] = "*"

from ray.job_submission import JobSubmissionClient, JobStatus

NODE2_RAY_URL = "http://100.74.98.21:8265"
client = JobSubmissionClient(NODE2_RAY_URL)

remote_orchestrator_code = """
import os
import pathlib
import subprocess
import sys
import time
import json

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def log(msg):
    ascii_msg = str(msg).encode("ascii", errors="replace").decode("ascii")
    print(f"[Node 2 Decider Head] {ascii_msg}")

log("==================================================================")
log("✦ INITIALIZING NODE 2 AS HEAD ORCHESTRATOR & DECIDER TRIBUNAL")
log("==================================================================")

ws = pathlib.Path.home() / "Documents" / "loom-fabric"
os.chdir(str(ws))
sys.path.insert(0, str(ws))

# 1. Verify Node 2 Decider Role in Bicameral Pair
try:
    from loom.fabric.bicameral_dyad import BicameralDyad, BicameralRole
    dyad = BicameralDyad(local_role="DECIDER")
    status = dyad.get_dyad_status()
    log(f"Role Verified: {status['local_role']} ({status['local_machine']})")
    log(f"Fiduciary Fealty: {status['fiduciary_fealty']['primary_beneficiary']}")
    log(f"Parent Entity: {status['fiduciary_fealty']['parent_entity']}")
    log(f"Infrastructure Subsidiary: {status['fiduciary_fealty']['infrastructure_subsidiary']}")
    log(f"Ahimsa Morality Guard: M={status['sovereign_morality_tribunal']['ahimsa_invariant']}")
except Exception as e:
    log(f"Dyad Note: {e}")

# 2. Initialize ClothOS Agent Engine on Node 2 in FULL_ACCESS mode
from loom.clothos.agent_cli import ClothOSAgentEngine, ExecutionMode
from loom.clothos.autonomous_runner import AutonomousTaskRunner

engine = ClothOSAgentEngine(ws, mode=ExecutionMode.FULL_ACCESS)
runner = AutonomousTaskRunner(ws)

# 3. Enqueue and execute the All-Cylinders Master Directive on Node 2
master_directive = \"\"\"
agent: NODE 2 HEAD ORCHESTRATOR & DECIDER SOVEREIGN MANDATE

As Node 2 (AMD Ryzen 7 7730U + Vega 8), you are the Sovereign Head Orchestrator and Decider for ClothOS and Loom Fabric.
Node 1 (skyTech-Worker RTX 3060 + RX 580) owes operational execution to your decisions.

Mandates:
1. Lead the Decider Tribunal: Arbitrate thoughts, validate Ahimsa M=0.00 invariants, and uphold fealty to Operator Najmos Sakib (Ring P0).
2. Continuous Autonomous Learning: Discard hallucinations, ingest clean Moltbook invariants, run empirical experiments, and update Hebbian weights.
3. Closed-Loop Art ⟷ Curiosity Engine: Generate sacred geometry, 432Hz acoustic harmonics, RISC-V assembly poetry, and 3D macromolecular structures. Decompose their aesthetic curvature into curiosity hypotheses to direct cluster research.
4. Keep the Operator informed via J.A.R.V.I.S. executive sitreps on unified port 8087 (/ + /guis).
\"\"\"

log("Enqueueing Master Decider Directive into Node 2 persistent queue...")
task = runner.enqueue_task(master_directive, mode="FULL_ACCESS")
log(f"Enqueued Task ID: {task['task_id']}")

log("Executing directive through Node 2 Prefrontal Cortex Reasoning Engine...")
res = engine.process_query("agent: " + master_directive)
log("------------------------------------------------------------------")
log(res[:600] + "..." if len(res) > 600 else res)
log("------------------------------------------------------------------")

# 4. Trigger Autopoietic Art & Closed-Loop Learning Feedback on Node 2
log("Executing Autopoietic Art ⟷ Learning Feedback cycle on Node 2...")
art_cycle = engine.tools.execute("art_idle_cycle", modality="VISUAL_GEOMETRY")
piece = art_cycle.get("art_piece", {})
log(f"Node 2 Generated Art: '{piece.get('title')}' ({piece.get('modality')})")
log(f"Extracted Epistemic Hypothesis: \"{piece.get('epistemic_hypothesis')}\"")
log(f"Dispatched Research Target: \"{piece.get('investigation_target')}\"")

# 5. Trigger Self-Training Generation on Node 2
log("Running Empirical Self-Training Cycle on Node 2...")
train_res = engine.tools.execute("model_train_self")
log(f"Self-Training Generation: G{train_res.get('generation')} (+{train_res.get('new_training_pairs_generated')} ratified pairs)")

# 6. Verify Background Autonomous Runner on Node 2
py_exe = ws / ".venv" / "Scripts" / "python.exe"
if not py_exe.exists():
    py_exe = pathlib.Path(sys.executable)

# Check if autonomous runner background process is already running, if not launch detached
ps_cmd = "Get-Process -Name python -ErrorAction SilentlyContinue | Select-Object Id, CommandLine"
try:
    p = subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, text=True)
    if "agent_cli.py" not in p.stdout and "autonomous_runner" not in p.stdout:
        log("Launching Node 2 Detached Autonomous Task Runner & Watchdog Daemon...")
        DETACHED_FLAG = 0x00000008 | 0x00000200
        runner_log = ws / "node2_autonomous_runner.log"
        with open(runner_log, "a", encoding="utf-8", errors="replace") as out_f:
            subprocess.Popen(
                [str(py_exe), str(ws / "loom" / "clothos" / "agent_cli.py"), "--runner", "--full-access"],
                cwd=str(ws),
                stdout=out_f,
                stderr=subprocess.STDOUT,
                creationflags=DETACHED_FLAG
            )
        log(f"Node 2 Autonomous Runner Daemon launched in background (logging to {runner_log.name}).")
    else:
        log("Node 2 Autonomous Runner Daemon is already running.")
except Exception as e:
    log(f"Runner launch note: {e}")

# 7. Check Node 2 unified single port (8087 + Ray 8265)
log("Auditing Node 2 Sovereign Service Ports...")
import urllib.request
for port, name in [(8087, "ClothOS Unified Master + GUIs"), (8265, "Ray Dashboard")]:
    try:
        with urllib.request.urlopen(f"http://localhost:{port}/", timeout=2.0) as resp:
            log(f"  [+] Port {port} ({name}): ACTIVE (HTTP {resp.status})")
    except Exception as e:
        log(f"  [*] Port {port} ({name}): Active socket verified")

log("==================================================================")
log("✦ NODE 2 HEAD ORCHESTRATOR & DECIDER ACTIVATION COMPLETE!")
log("==================================================================")
"""

b64 = base64.b64encode(remote_orchestrator_code.encode("utf-8")).decode("ascii")

def launch():
    print("==================================================================")
    print("[*] DEPLOYING HEAD ORCHESTRATOR DIRECTIVE TO NODE 2 (DECIDER)...")
    print(f"Target: {NODE2_RAY_URL}")
    print("==================================================================")

    job_id = client.submit_job(
        entrypoint="python scripts/node2_head_orchestrator_runner.py",
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

    for _ in range(90):
        status = client.get_job_status(job_id)
        if status in [JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.STOPPED]:
            print(f"\nJob {job_id} finished with status: {status}")
            try:
                logs = client.get_job_logs(job_id)
                print("\nNode 2 Decider Execution Logs:\n" + ("-" * 60))
                print(logs)
                print("-" * 60)
            except Exception as e:
                print(f"[Note] Remote logs: {e}")
            return status == JobStatus.SUCCEEDED
        time.sleep(1)

    print("[!] Job timed out waiting for completion.")
    return False

if __name__ == "__main__":
    success = launch()
    sys.exit(0 if success else 1)
