"""ClothOS Autonomous Continuous 24/7 Compute Orchestrator.

Main loop powering Start-24-7-Compute.bat.
Orchestrates:
1. Pipelined asynchronous execution of ClothOS Unified Autonomous Engine.
2. Real-time OS research ingestion from Reddit (/r/osdev, /r/kernel) and GitHub repositories.
3. Full documentation and citation logging to deliverables/research_library/.
4. Direct autonomous self-evolution on the 'clothos/autonomous-evolution' branch.
"""

from __future__ import annotations
import argparse
import logging
import os
import signal
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("ClothOS.24x7Compute")

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent


class ClothOSContinuousComputeManager:
    """Orchestrates 24/7 continuous autonomous self-evolution for ClothOS."""

    def __init__(
        self,
        workspace_root: Optional[Path] = None,
        cycle_interval_s: float = 2.0,
        enable_factory_ui: bool = False,
    ):
        self.workspace_root = workspace_root or WORKSPACE_ROOT
        self.cycle_interval_s = cycle_interval_s
        self.enable_factory_ui = enable_factory_ui
        self.stop_event = threading.Event()
        self.total_cycles = 0

        # Subsystems
        from loom.clothos.unified_autonomous_engine import ClothOSUnifiedAutonomousEngine
        from loom.clothos.research_harvester import research_harvester
        from loom.clothos.self_evolution import AutonomousSelfEvolutionEngine
        from loom.clothos.dual_track_boot_builder import dual_track_boot_builder

        self.unified_engine = ClothOSUnifiedAutonomousEngine(self.workspace_root)
        self.research_harvester = research_harvester
        self.self_evolution = AutonomousSelfEvolutionEngine()
        self.boot_builder = dual_track_boot_builder

    def run_forever(self, max_cycles: Optional[int] = None) -> None:
        """Runs the continuous autonomous computing loop."""
        logger.info("==================================================================")
        logger.info(" CLOTHOS SOVEREIGN 24/7 AUTONOMOUS COMPUTE ORCHESTRATOR ACTIVE")
        logger.info(" Branch: clothos/autonomous-evolution (Unbounded Self-Modification)")
        logger.info(" Research Harvester: Reddit (/r/osdev, /r/kernel) + GitHub OSDev")
        logger.info(" Citations Library: deliverables/research_library/OS_RESEARCH_CITATIONS.md")
        logger.info("==================================================================")

        # Setup graceful shutdown handlers
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

        # Trigger initial research sync and dual-track boot image verification
        try:
            logger.info("🔍 Ingesting initial OS research signals from GitHub & Reddit...")
            self.research_harvester.harvest_github_os_repos(max_results=3)
            self.research_harvester.harvest_hackernews_systems(limit=3)
            logger.info("🛠 Baking initial dual-track bootable images (RISC-V + x86)...")
            self.boot_builder.build_both_images()
        except Exception as e:
            logger.debug(f"Initial harvest/boot warning: {e}")

        while not self.stop_event.is_set():
            if max_cycles and self.total_cycles >= max_cycles:
                logger.info(f"Reached requested cycle limit ({max_cycles}).")
                break

            self.total_cycles += 1
            cycle_start = time.time()

            try:
                # 1. Execute Unified Autonomous Cycle (Proprioception -> Tasks -> Health -> Ingest -> Silicon -> Ratchet)
                telemetry = self.unified_engine.run_supervised_cycle()

                # 2. Periodic Live Research Sweep (Every 5 cycles)
                if self.total_cycles % 5 == 0:
                    logger.info("📡 Scanning Reddit & GitHub for trending OS kernel patterns...")
                    self.research_harvester.harvest_github_os_repos(max_results=2)
                    self.research_harvester.harvest_hackernews_systems(limit=2)

                # 3. Autonomous Self-Evolution Verification (Every 10 cycles)
                if self.total_cycles % 10 == 0:
                    logger.info(f"🧬 Executing Self-Evolution Cycle #{self.total_cycles}...")
                    evo_res = self.self_evolution.run_evolution_cycle(self.total_cycles)
                    logger.info(f"✔ Self-Evolution complete: SCI {evo_res.sci_start:.1f}% -> {evo_res.sci_end:.1f}%")
                    logger.info("🛠 Updating dual-track bootable images (RISC-V + x86)...")
                    self.boot_builder.build_both_images()

                duration = time.time() - cycle_start
                logger.info(
                    f"⚡ [Cycle #{self.total_cycles} Complete]: {duration:.2f}s | "
                    f"SCI: {telemetry.sci_score:.1f}% | Invariants: {telemetry.invariants_ratified} | "
                    f"Crystallized: {self.unified_engine.problems_resolved_and_crystallized}"
                )

                # Rest interval
                if self.cycle_interval_s > 0:
                    time.sleep(self.cycle_interval_s)

            except Exception as exc:
                logger.error(f"❌ Anomaly in 24/7 compute cycle #{self.total_cycles}: {exc}", exc_info=True)
                time.sleep(5.0)

        logger.info(f"ClothOS 24/7 compute orchestrator halted cleanly after {self.total_cycles} cycles.")

    def _handle_signal(self, signum, frame):
        logger.info(f"Received shutdown signal ({signum}). Terminating gracefully...")
        self.stop_event.set()
        self.unified_engine.stop()


def main():
    parser = argparse.ArgumentParser(description="ClothOS Sovereign 24/7 Continuous Autonomous Compute Fabric")
    parser.add_argument("--interval", type=float, default=2.0, help="Interval between compute cycles in seconds")
    parser.add_argument("--cycles", type=int, default=None, help="Maximum number of cycles to execute (default: infinite)")
    parser.add_argument("--once", action="store_true", help="Execute single supervised cycle and exit")
    parser.add_argument("--factory", "-f", action="store_true", help="Show animated factory terminal floor")
    args = parser.parse_args()

    mgr = ClothOSContinuousComputeManager(
        cycle_interval_s=0.5 if args.once else args.interval,
        enable_factory_ui=args.factory,
    )

    if args.once:
        mgr.run_forever(max_cycles=1)
    else:
        mgr.run_forever(max_cycles=args.cycles)


if __name__ == "__main__":
    main()
