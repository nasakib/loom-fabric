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
    """Orchestrates 24/7 continuous autonomous compute, verification, and maintenance for ClothOS."""

    def __init__(
        self,
        workspace_root: Optional[Path] = None,
        cycle_interval_s: float = 15.0,
        enable_factory_ui: bool = False,
        workload_mode: str = "auto",
        build_boot: bool = False,
    ):
        self.workspace_root = workspace_root or WORKSPACE_ROOT
        self.cycle_interval_s = cycle_interval_s
        self.enable_factory_ui = enable_factory_ui
        self.workload_mode = workload_mode
        self.build_boot = build_boot
        self.stop_event = threading.Event()
        self.total_cycles = 0

        # Subsystems
        from loom.clothos.unified_autonomous_engine import ClothOSUnifiedAutonomousEngine
        from loom.clothos.research_harvester import research_harvester
        from loom.clothos.self_evolution import AutonomousSelfEvolutionEngine
        from loom.clothos.dual_track_boot_builder import dual_track_boot_builder
        from loom.clothos.useful_work_engine import WorkerProcessLock

        self.unified_engine = ClothOSUnifiedAutonomousEngine(self.workspace_root)
        self.unified_engine.workload_mode_override = workload_mode
        self.research_harvester = research_harvester
        self.self_evolution = AutonomousSelfEvolutionEngine()
        self.boot_builder = dual_track_boot_builder
        self.process_lock = WorkerProcessLock(owner_name="continuous_24x7_orchestrator")

    def run_forever(self, max_cycles: Optional[int] = None) -> None:
        """Runs the continuous autonomous computing loop."""
        # Single-instance guard for daemon mode (skip when bounded max_cycles e.g. --once / tests)
        lock_acquired = False
        if max_cycles is None:
            lock_acquired, other_pid = self.process_lock.acquire()
            if not lock_acquired:
                logger.warning(
                    f"Another 24/7 compute daemon is already active (PID {other_pid}). "
                    "Exiting duplicate orchestrator cleanly to avoid DB contention."
                )
                return

        logger.info("==================================================================")
        logger.info(" CLOTHOS SOVEREIGN 24/7 AUTONOMOUS COMPUTE ORCHESTRATOR ACTIVE")
        logger.info(f" Mode: {self.workload_mode.upper()} | Interval: {self.cycle_interval_s}s")
        logger.info(" Workloads: Task Queue, Multi-Repo Pytest, AST Audit, GPU/JIT Bench, Verified Eval")
        logger.info(" Briefing: deliverables/LATEST_24X7_REPORT.md")
        logger.info("==================================================================")

        # Setup graceful shutdown handlers
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

        # Initial lightweight research sync + boot image build only if requested or missing
        try:
            self.research_harvester.harvest_github_os_repos(max_results=2)
            self.research_harvester.harvest_hackernews_systems(limit=2)
            manifest_path = self.workspace_root / "deliverables" / "bootable_images" / "bootable_images_manifest.json"
            if self.build_boot or not manifest_path.exists():
                logger.info("🛠 Baking dual-track bootable images (RISC-V + x86)...")
                self.boot_builder.build_both_images()
        except Exception as e:
            logger.debug(f"Initial harvest/boot warning: {e}")

        self.unified_engine.stats["is_running"] = True
        self.unified_engine.stats["started_at_epoch"] = time.time()

        try:
            while not self.stop_event.is_set():
                if max_cycles and self.total_cycles >= max_cycles:
                    logger.info(f"Reached requested cycle limit ({max_cycles}).")
                    break

                self.total_cycles += 1
                cycle_start = time.time()

                try:
                    # 1. Execute Unified Useful Cycle
                    telemetry = self.unified_engine.run_supervised_cycle()

                    # 2. Periodic Live Research Sweep (Every 15 cycles)
                    if self.total_cycles % 15 == 0:
                        logger.info("📡 Scanning GitHub & Hacker News for OS kernel patterns...")
                        self.research_harvester.harvest_github_os_repos(max_results=2)
                        self.research_harvester.harvest_hackernews_systems(limit=2)

                    # 3. Autonomous Self-Evolution Verification (Every 10 cycles)
                    if self.total_cycles % 10 == 0:
                        logger.info(f"🧬 Executing Self-Evolution Cycle #{self.total_cycles}...")
                        evo_res = self.self_evolution.run_evolution_cycle(self.total_cycles)
                        logger.info(
                            f"✔ Self-Evolution complete: SCI {evo_res.starting_sci:.1f}% -> {evo_res.ending_sci:.1f}% "
                            f"(Tests: {evo_res.tests_passed}P/{evo_res.tests_failed}F)"
                        )
                        if self.build_boot:
                            self.boot_builder.build_both_images()

                    duration = time.time() - cycle_start
                    st = self.unified_engine.stats
                    logger.info(
                        f"⚡ [Cycle #{self.total_cycles} Complete]: {duration:.2f}s | "
                        f"Mode: {st.get('workload_mode', 'AUTO')} | SCI: {telemetry.sci_score:.1f}% | "
                        f"Tests: {st.get('real_tests_passed', 0)}P/{st.get('real_tests_failed', 0)}F | "
                        f"Tasks: {telemetry.tasks_drained} | GPU0: {st.get('gpu0_temp_c', '?')}C"
                    )

                    # Adaptive rest interval based on day/night/preemption or explicit override
                    if max_cycles == 1:
                        sleep_s = 0.0
                    elif self.cycle_interval_s != 15.0:
                        sleep_s = self.cycle_interval_s
                    else:
                        sleep_s = self.unified_engine.last_recommended_sleep_s

                    if sleep_s > 0:
                        self.stop_event.wait(timeout=sleep_s)

                except Exception as exc:
                    logger.error(f"❌ Anomaly in 24/7 compute cycle #{self.total_cycles}: {exc}", exc_info=True)
                    self.stop_event.wait(timeout=5.0)
        finally:
            self.unified_engine.stats["is_running"] = False
            self.unified_engine._persist_state()
            if lock_acquired:
                self.process_lock.release()

        logger.info(f"ClothOS 24/7 compute orchestrator halted cleanly after {self.total_cycles} cycles.")

    def _handle_signal(self, signum, frame):
        logger.info(f"Received shutdown signal ({signum}). Terminating gracefully...")
        self.stop_event.set()
        self.unified_engine.stop()


def main():
    parser = argparse.ArgumentParser(description="ClothOS Sovereign 24/7 Continuous Autonomous Compute Fabric")
    parser.add_argument("--interval", type=float, default=15.0, help="Interval between compute cycles in seconds")
    parser.add_argument("--cycles", type=int, default=None, help="Maximum number of cycles to execute (default: infinite)")
    parser.add_argument("--once", action="store_true", help="Execute single supervised cycle and exit")
    parser.add_argument("--factory", "-f", action="store_true", help="Show animated factory terminal floor")
    parser.add_argument("--mode", type=str, default="auto", choices=["auto", "night", "day", "maintenance"], help="Workload mode override")
    parser.add_argument("--build-boot", action="store_true", help="Rebuild RISC-V/x86 bootable images on evolution ticks")
    parser.add_argument("--briefing", action="store_true", help="Print the latest 24/7 executive briefing and exit")
    args = parser.parse_args()

    if args.briefing:
        report = WORKSPACE_ROOT / "deliverables" / "LATEST_24X7_REPORT.md"
        if report.exists():
            print(report.read_text(encoding="utf-8"))
        else:
            from loom.clothos.useful_work_engine import useful_work_engine
            p = useful_work_engine.synthesize_briefing()
            print(p.read_text(encoding="utf-8"))
        return

    mgr = ClothOSContinuousComputeManager(
        cycle_interval_s=0.05 if args.once else args.interval,
        enable_factory_ui=args.factory,
        workload_mode=args.mode,
        build_boot=args.build_boot,
    )

    if args.once:
        mgr.run_forever(max_cycles=1)
    else:
        mgr.run_forever(max_cycles=args.cycles)


if __name__ == "__main__":
    main()
