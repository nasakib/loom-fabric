"""
ClothOS BRAND Sovereign Agent Head Node Daemon (`scripts/start_brand_headnode.py`).
Continuously runs on the AMD Ryzen 7 7730U Head Node (192.168.99.2):
- Context-aware surveying across loom-fabric, core-compute-fabric, fabric-core, stitch-core
- Proactive contemplation and inspiration generation into vault/brand/
- Dynamic task delegation across the 1Gbps direct wire to Node 1 (skyTech GPU Rig)
"""
import logging
import sys
import time
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WORKSPACE_ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [BRAND-Daemon]: %(message)s")
logger = logging.getLogger("brand_daemon")

from loom.clothos.brand import get_brand
from loom.clothos.cluster_worker import get_cluster_worker

def main():
    logger.info("==================================================================")
    logger.info("   CLOTHOS BRAND SOVEREIGN HEAD NODE AGENT (Ryzen 7 7730U)")
    logger.info("   Keys to the Kingdom: ACTIVE | Dual-Node Dynamic Delegator")
    logger.info("==================================================================")

    brand = get_brand()
    cluster_worker = get_cluster_worker()

    # Start cluster worker background thread
    cluster_worker.start_background()

    # Initial inaugural contemplation
    ins = brand.contemplate(focus_override="Inaugural Sovereign Dual-Node Activation & Silicon Pooling")
    logger.info(f"[*] Inaugural BRAND Contemplation: '{ins.title}'")

    # Run continuous awareness and delegation loop
    cycle = 0
    while True:
        try:
            cycle += 1
            time.sleep(30)

            # Every 60s, run a contemplation cycle
            if cycle % 2 == 0:
                insight = brand.contemplate()
                logger.info(f"✨ [BRAND #{cycle}]: Formulated insight '{insight.title}'")

            # Every 90s, delegate a distributed calculation to Node 1
            if cycle % 3 == 0:
                res = brand.delegate_task(
                    task_type="gpu_tensor",
                    payload={"dim": 2048, "iterations": 50},
                    target_node="node1"
                )
                logger.info(f"🚀 [BRAND Delegation #{cycle}]: Dispatched task {res.get('delegation_id')} to Node 1")

            # Every 150s, trigger cluster synchronization
            if cycle % 5 == 0:
                sync_res = cluster_worker.synchronize_cluster()
                logger.info(f"🔄 [BRAND Cluster Sync #{cycle}]: Synced {sync_res.get('items_synced', 0)} items")

        except KeyboardInterrupt:
            logger.info("BRAND daemon shutting down gracefully.")
            break
        except Exception as e:
            logger.error(f"Error in BRAND loop: {e}", exc_info=True)
            time.sleep(5)

if __name__ == "__main__":
    main()
