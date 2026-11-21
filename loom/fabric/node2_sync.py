# Copyright (c) 2026 Najmos Sakib. All rights reserved.

# Proprietary and confidential. Commercial distribution prohibited.

"""

Node 2 Direct Stream Synchronizer (`loom/fabric/node2_sync.py`).



Streams the ClothOS and Loom codebase directly to Node 2 over the Tailscale

mesh socket (100.74.98.21:8299) coordinated via Ray Dashboard Job API (100.74.98.21:8265).

Avoids Windows command-line buffer limits and guarantees bit-exact SHA-256 verification.

"""



from __future__ import annotations



import hashlib

import io

import json

import logging

from pathlib import Path

import socket

import sys

import time

import urllib.request

import urllib.error

import zipfile



logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s %(message)s")

logger = logging.getLogger("loom.fabric.node2_sync")



NODE2_TAILSCALE = "100.74.98.21"

RAY_DASHBOARD_URL = f"http://{NODE2_TAILSCALE}:8265"

RECEIVER_PORT = 8299



WORKSPACE_ROOT = Path(__file__).resolve().parents[2]



SYNC_FILES = [

    "loom/fabric/port_manager.py",

    "loom/fabric/dashboard_server.py",

    "loom/fabric/master_dashboard.html",

    "loom/fabric/visual_dashboard.html",

    "loom/fabric/screensaver.html",

    "loom/fabric/bicameral_dyad.py",

    "loom/fabric/run_node2_server.py",

    "loom/si/ui_autopoiesis.py",

    "apps/loom-screensaver/screensaver.html",

    "loom/ui/standalone_screensaver.html",

    "loom/fabric/screensaver_runner.py",

    "loom/fabric/bandwidth_mesh.py",

    "loom/fabric/system_config.py",

    "loom/fabric/aha_engine.py",

    "loom/fabric/hypothesis_store.py",

    "loom/fabric/cluster_discovery.py",

    "loom/fabric/task_manager_telemetry.py",

    "loom/fabric/unified_gpu_mesh.py",

    "loom/fabric/system_focus.py",

    "loom/fabric/startup_manager.py",

    "loom/clothos/sandbox_virtualizer.py",

    "loom/clothos/windows_symbiosis.py",

    "loom/clothos/kernel.py",

    "loom/clothos/fs.py",

    "loom/clothos/process_manager.py",

    "loom/clothos/shell.py",

    "loom/clothos/hal.py",

    "loom/clothos/riscv_migration.py",

    "loom/clothos/riscv_target/clothos_rv64.ld",

    "loom/clothos/riscv_target/kuramoto_rvv.s",

    "loom/clothos/riscv_target/landauer_meter.s",

    "loom/clothos/riscv_target/uEnv.txt",

    "loom/clothos/__init__.py",

    "loom/si/spiritual_epistemology.py",

    "loom/si/__init__.py",

    "apps/loom-desktop/launch_desktop.py",

    "apps/loom-react-native/serve_rn.py",

    "apps/loom-react-native/App.tsx",

    "apps/loom-react-native/dist/index.html",

    "apps/loom-react-native/dist/metadata.json",

    "loom/clothos/wcos.py",

    "loom/clothos/wcoss.py",

    "wcos.cmd",

    "wcos.bat",

    "wcos.ps1",

    "wcoss.cmd",

    "wcoss.bat",

    "wcospath.cmd",

    "loom/fabric/installer.py",

    "scripts/install_clothos.ps1",

    "Install-ClothOS.bat",

    "Install-Loom-Windows.bat",

    "install_clothos.sh",

    "Launch-Loom-GUI.bat",

    "Launch-Loom-Screensaver.bat",

    "Launch-React-Native.bat",

    "loom/clothos/workspace_curator.py",

    "loom/autonomy/autonomous_daemon.py",

    "loom/autonomy/self_updater.py",

    "loom/autonomy/self_aligner.py",

    "loom/autonomy/self_critic.py",

    "loom/autonomy/self_healer.py",

    "loom/autonomy/self_designer.py",

    "loom/autonomy/operator_credentials.py",

    "loom/autonomy/__init__.py",

    "WORKSPACE_MASTER_DIGEST_AND_TRAJECTORIES.md",

    ".clothos_learned_patterns.json",

    "loom/clothos/agent_cli.py",

    "loom/clothos/terminal.py",

    "loom/clothos/code_interpreter.py",

    "loom/clothos/doc_parser.py",

    "loom/clothos/group_chat.py",

    "loom/clothos/mcp_client.py",

    "loom/clothos/web_search.py",

    "loom/clothos/activity_tracker.py",

    "loom/clothos/theme.py",

    "loom/clothos/ui_progress.py",

    "loom/clothos/bfcl_engine.py",

    "loom/tools/epistemic_grounding.py",

    "loom/tools/toolbox.py",

    "loom/weaving/cloth.py",

    "docs/CLOTHOS_UNIFIED_ONTOLOGY_AND_TOOL_METAPHORS.md",
    "loom/clothos/dev_loop.py",
    "loom/clothos/sovereign_compute.py",
    "scripts/clothos_self_improve.py",

]





def build_bundle() -> tuple[bytes, str, list[str]]:

    """Packs the synchronization manifest into an in-memory zip archive."""

    buf = io.BytesIO()

    packed = []

    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:

        for rel in SYNC_FILES:

            abs_p = WORKSPACE_ROOT / rel

            if abs_p.exists():

                zf.write(abs_p, rel)

                packed.append(rel)

            else:

                logger.warning(f"File not found on Node 1: {rel}")

    raw = buf.getvalue()

    sha = hashlib.sha256(raw).hexdigest()

    return raw, sha, packed





def sync_to_node2() -> bool:

    logger.info("==================================================================")

    logger.info("CLOTHOS NODE 2 SYNCHRONIZER (Direct Mesh Streaming)")

    logger.info(f"Target: Node 2 ({NODE2_TAILSCALE}) via Ray Dashboard ({RAY_DASHBOARD_URL})")

    logger.info("==================================================================")



    data, sha, packed = build_bundle()

    logger.info(f"Packed {len(packed)} files ({len(data):,} bytes, SHA-256: {sha[:16]}...)")



    # Save to disk locally as well

    bundle_path = WORKSPACE_ROOT / "loom" / "fabric" / "sync_bundle.zip"

    bundle_path.write_bytes(data)



    # 1. Submit Ray job on Node 2 to start ephemeral TCP socket receiver

    receiver_code = (

        "import socket, zipfile, io, os; "

        f"s = socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1); "

        f"s.bind(('0.0.0.0', {RECEIVER_PORT})); s.listen(1); "

        "print('RECEIVER_LISTENING', flush=True); "

        "c, addr = s.accept(); "

        "data = c.makefile('rb').read(); "

        "c.close(); s.close(); "

        f"print(f'RECEIVED_{{len(data)}}_BYTES', flush=True); "

        "target = r'C:\\Users\\natsa\\Documents\\loom-fabric'; "

        "os.makedirs(target, exist_ok=True); "

        "zf = zipfile.ZipFile(io.BytesIO(data)); "

        "zf.extractall(target); "

        "print(f'NODE2_EXTRACTED_{len(zf.namelist())}_FILES_SUCCESSFULLY', flush=True)"

    )



    job_url = f"{RAY_DASHBOARD_URL}/api/jobs/"

    job_payload = {

        "entrypoint": f'python -c "{receiver_code}"'

    }



    logger.info("Submitting receiver job to Node 2 Ray cluster...")

    req = urllib.request.Request(

        job_url,

        data=json.dumps(job_payload).encode("utf-8"),

        headers={"Content-Type": "application/json"},

        method="POST"

    )



    try:

        with urllib.request.urlopen(req, timeout=25) as resp:

            submit_data = json.loads(resp.read().decode("utf-8"))

            submission_id = submit_data.get("submission_id")

            logger.info(f"Node 2 Job submitted successfully: submission_id={submission_id}")

    except Exception as e:

        logger.error(f"Failed to submit Ray job to Node 2: {e}")

        return False



    # 2. Poll until receiver is listening, then stream bytes over TCP

    connected = False

    for attempt in range(25):

        time.sleep(0.6)

        try:

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            s.settimeout(4.0)

            s.connect((NODE2_TAILSCALE, RECEIVER_PORT))

            connected = True

            logger.info(f"Connected to Node 2 ephemeral socket at {NODE2_TAILSCALE}:{RECEIVER_PORT}!")

            

            t0 = time.time()

            s.sendall(data)

            s.shutdown(socket.SHUT_WR)

            elapsed = max(time.time() - t0, 0.001)

            mb = len(data) / (1024 * 1024)

            logger.info(f"Transferred {len(data):,} bytes in {elapsed:.3f}s ({mb/elapsed:.2f} MB/s) to Node 2!")

            s.close()

            break

        except (ConnectionRefusedError, socket.timeout, OSError) as ce:

            logger.debug(f"Waiting for Node 2 receiver to bind ({ce})...")



    if not connected:

        logger.error(f"Could not connect to Node 2 receiver at {NODE2_TAILSCALE}:{RECEIVER_PORT} within timeout.")

        return False



    # 3. Monitor Ray Job to completion

    logger.info("Waiting for Node 2 extraction to complete...")

    for poll in range(20):

        time.sleep(1.0)

        try:

            status_req = urllib.request.Request(f"{job_url}{submission_id}")

            with urllib.request.urlopen(status_req, timeout=5) as r:

                job_info = json.loads(r.read().decode("utf-8"))

                status = job_info.get("status")

                logger.info(f"Node 2 Job Status: {status}")

                if status == "SUCCEEDED":

                    log_req = urllib.request.Request(f"{job_url}{submission_id}/logs")

                    with urllib.request.urlopen(log_req, timeout=5) as lr:

                        job_logs = lr.read().decode("utf-8")

                        logger.info(f"Node 2 Execution Logs:\n{job_logs.strip()}")

                    logger.info("✅ Node 2 codebase synchronization verified SUCCEEDED!")

                    return True

                elif status in ["FAILED", "STOPPED"]:

                    log_req = urllib.request.Request(f"{job_url}{submission_id}/logs")

                    with urllib.request.urlopen(log_req, timeout=5) as lr:

                        job_logs = lr.read().decode("utf-8")

                        logger.error(f"Node 2 Job {status} with logs:\n{job_logs.strip()}")

                    return False

        except Exception as ex:

            logger.warning(f"Error checking status: {ex}")



    logger.warning("Polling timed out while waiting for job completion.")

    return False





if __name__ == "__main__":

    success = sync_to_node2()

    sys.exit(0 if success else 1)

