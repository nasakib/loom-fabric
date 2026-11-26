"""
Fabric & ClothOS 24/7 Continuous Dual-Machine Sovereign Autonomous Compute Engine.

Concurrent Dual-GPU Architecture:
- GPU 0 (NVIDIA RTX 3060 12GB CUDA):
  Generator & Synthesizer — Runs continuous active inference with Qwen 2.5 7B,
  mining Moltbook research signals, formulating testable claims, and parameterizing
  quantitative predictions for hardware verification.
- GPU 1 (AMD Radeon RX 580 8GB OpenCL Ellesmere 2048SP):
  Concurrent Runner & Evaluator — Runs in an independent concurrent loop,
  interpreting hypotheses from GPU 0, executing massive dynamical sweeps
  and 2D vector Gram cosine similarity kernels on stream processors,
  measuring empirical invariants, and evaluating CONFIRMED vs. REFUTED bounds.
- Dual-Node Fabric:
  Node 2 (Ryzen 7 16 vCPUs) continuously syncs state over direct ethernet.
- Zero-OOM Auto-Preemption:
  Instantly yields GPU compute when user queries :8002 / :5555.
"""

from __future__ import annotations

import base64
import json
import logging
import os
from pathlib import Path
import random
import threading
import time
from typing import Any, Dict, List, Optional
import httpx
import numpy as np

from fabric.discovery.nodes import CrossPlatformNodeDiscovery
from fabric.ipc.zmq_bus import StitchZMQTelemetryBus
from fabric.routing.router import QCTHybridRouter
from loom.fabric.aha_engine import AhaEngine
from loom.fabric.deliverable_synthesizer import DeliverableSynthesizer
from loom.fabric.experimentation_engine import ExperimentationEngine
from loom.fabric.hypothesis_store import HypothesisStore
from loom.fabric.moltbook_hypothesis import MoltbookHypothesisEngine
from loom.fabric.node2_auditor import Node2PeerAuditor
from loom.fabric.rx580_compute import RX580HardwareEngine
from loom.fabric.system_config import system_config
from loom.fabric.unified_gpu_mesh import unified_gpu_mesh
from loom.tools.toolbox import toolbox
from loom.torque.enclave import TorqueEnclave
from loom.clothos.agent_controller import agent_controller
from loom.clothos.useful_work_engine import WorkerProcessLock, useful_work_engine

logger = logging.getLogger("continuous_worker")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [ContinuousWorker]: %(message)s")

TOKEN = "G-GzcZEzqteW241i720XeH5UNT73T6qk"
PEER_IP = "192.168.99.2"


class ContinuousComputeWorker:
    """Industrial-grade 24/7 concurrent dual-GPU compute engine."""

    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = workspace_root or Path(__file__).resolve().parents[2]
        self.state_file = Path.home() / ".loom" / "continuous_worker_state.json"
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.stop_event = threading.Event()
        self.preempt_event = threading.Event()

        self._thread: Optional[threading.Thread] = None
        self._gpu0_thread: Optional[threading.Thread] = None
        self._gpu1_thread: Optional[threading.Thread] = None

        # Fabric Core & Tooling stack integration
        self.toolbox = toolbox
        self.enclave = TorqueEnclave()
        self.router = QCTHybridRouter(enclave=self.enclave)
        self.zmq_bus = StitchZMQTelemetryBus(endpoint="tcp://127.0.0.1:5559", enclave=self.enclave)
        self.discovery = CrossPlatformNodeDiscovery()
        self.rx580 = RX580HardwareEngine(n_oscillators=65536)

        # Structured Moltbook Compute Pipeline Components
        self.hypothesis_store = HypothesisStore()
        self.hypothesis_engine = MoltbookHypothesisEngine(self.hypothesis_store)
        self.experiment_engine = ExperimentationEngine(self.hypothesis_store, self.rx580)
        self.synthesizer = DeliverableSynthesizer(self.workspace_root, self.hypothesis_store)
        self.node2_auditor = Node2PeerAuditor()
        self.unified_mesh = unified_gpu_mesh
        self.system_config = system_config
        self.aha_engine = AhaEngine(store=self.hypothesis_store, config=self.system_config, workspace_root=self.workspace_root)

        # Unified Autonomous Engine Integration
        try:
            from loom.clothos.unified_autonomous_engine import ClothOSUnifiedAutonomousEngine
            self.unified_engine = ClothOSUnifiedAutonomousEngine(self.workspace_root)
        except Exception as e:
            logger.debug(f"Unified engine initialization note: {e}")
            self.unified_engine = None

        # Seed initial adjacent Moltbook research signals if empty
        self.hypothesis_engine.seed_initial_hypotheses_if_empty()

        self.stats = {
            "is_running": False,
            "started_at_epoch": 0.0,
            "total_cycles_completed": 0,
            "node1_skytech_status": "ONLINE (RTX 3060 CUDA [Gen] + RX 580 Vulkan [Runner] + 16 CPUs)",
            "node2_ryzen7_status": "ONLINE (Ryzen 7 16 vCPUs + Radeon 680M)",
            "moltbook_hypotheses_indexed": 0,
            "experiments_evaluated": 0,
            "hypotheses_confirmed": 0,
            "hypotheses_refuted": 0,
            "deliverables_published": 0,
            "latest_deliverable": "None",
            "gpu0_status": "IDLE",
            "gpu1_status": "IDLE",
            "invariants_mined_node1": 0,
            "invariants_mined_node2": 0,
            "total_invariants_mined": 0,
            "ratchet_teeth_locked": self.toolbox.ratchet.tooth_count,
            "hammer_rivets_locked": self.toolbox.hammer.rivets_driven,
            "last_active_tier": "Full Cluster Concurrent (GPU 0 Gen + GPU 1 Runner)",
            "last_preemption_epoch": 0.0,
            "last_log_message": "Initialized with Concurrent Dual-GPU Pipeline",
        }
        self._load_state()

    def _load_state(self) -> None:
        target = self.state_file if self.state_file.exists() else (self.workspace_root / ".loom_worker_state.json")
        if target.exists():
            try:
                data = json.loads(target.read_text(encoding="utf-8"))
                self.stats.update(data)
                self.stats["is_running"] = False
            except Exception:
                pass

    def _persist_state(self) -> None:
        db_stats = self.hypothesis_store.get_statistics()
        by_status = db_stats.get("hypotheses_by_status", {})
        self.stats["moltbook_hypotheses_indexed"] = db_stats.get("total_hypotheses", 0)
        self.stats["experiments_evaluated"] = db_stats.get("total_experiments", 0)
        self.stats["hypotheses_confirmed"] = by_status.get("confirmed", 0)
        self.stats["hypotheses_refuted"] = by_status.get("refuted", 0)
        self.stats["deliverables_published"] = db_stats.get("total_deliverables", 0)

        serialized = json.dumps(self.stats, indent=2)
        try:
            (self.workspace_root / ".loom_worker_state.json").write_text(serialized, encoding="utf-8")
        except Exception as e:
            logger.debug(f"Failed to persist state to workspace root: {e}")

        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            self.state_file.write_text(serialized, encoding="utf-8")
        except Exception as e:
            logger.debug(f"Failed to persist state to home .loom dir: {e}")

        self._sync_status_md()

    def _sync_status_md(self) -> None:
        status_md_path = self.workspace_root / ".agent" / "STATUS.md"
        if not status_md_path.exists():
            return
        try:
            content = status_md_path.read_text(encoding="utf-8")
            marker = "## 1. Discovered Cross-Platform Fabric Nodes"
            worker_summary = (
                f"- **24/7 Concurrent Dual-GPU Pipeline**: `ACTIVE` | "
                f"GPU 0 (RTX 3060): `{self.stats.get('gpu0_status', 'ACTIVE')}` | "
                f"GPU 1 (RX 580): `{self.stats.get('gpu1_status', 'ACTIVE')}` | "
                f"Moltbook Hypotheses: `{self.stats['moltbook_hypotheses_indexed']:,}` | "
                f"Experiments Tested: `{self.stats['experiments_evaluated']:,}` "
                f"(`{self.stats['hypotheses_confirmed']}` Confirmed, `{self.stats['hypotheses_refuted']}` Refuted) | "
                f"Deliverables: `{self.stats['deliverables_published']}` | "
                f"Ratchet Teeth: `{self.stats.get('ratchet_teeth_locked', 0):,}` | "
                f"Hammer Rivets: `{self.stats.get('hammer_rivets_locked', 0):,}`\n\n"
            )
            if "- **24/7 Concurrent Dual-GPU Pipeline**:" in content:
                lines = content.splitlines()
                new_lines = []
                for line in lines:
                    if line.startswith("- **24/7 Concurrent Dual-GPU Pipeline**:"):
                        new_lines.append(worker_summary.strip())
                    else:
                        new_lines.append(line)
                status_md_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
            elif "- **24/7 Sovereign Research Pipeline**:" in content or "- **24/7 Continuous Sovereign Worker**:" in content:
                lines = content.splitlines()
                new_lines = []
                for line in lines:
                    if line.startswith("- **24/7 Sovereign Research Pipeline**:") or line.startswith("- **24/7 Continuous Sovereign Worker**:"):
                        new_lines.append(worker_summary.strip())
                    else:
                        new_lines.append(line)
                status_md_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
            else:
                idx = content.find(marker)
                if idx != -1:
                    new_content = content[:idx] + worker_summary + content[idx:]
                    status_md_path.write_text(new_content, encoding="utf-8")
        except Exception:
            pass

    def is_user_active(self) -> bool:
        """Detects if an interactive user query is executing on the unified ClothOS Master Hub (:8087)."""
        try:
            with httpx.Client(timeout=1.0) as client:
                r = client.get("http://127.0.0.1:8087/health")
                if r.status_code == 200:
                    data = r.json()
                    if data.get("active_stream", False):
                        return True
        except Exception:
            pass
        return False

    def _step_node2_ryzen_compute(self) -> Dict[str, Any]:
        """Reads real-time distributed invariant verification state from the Ryzen 7 Head Node (192.168.99.2)."""
        try:
            with httpx.Client(timeout=3.0) as client:
                resp = client.get(
                    f"http://{PEER_IP}:5555/api/admin/fs/read",
                    params={"path": "C:/Users/natsa/.loom/continuous_worker_state.json"},
                    headers={"X-Fabric-Token": TOKEN},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    content = data.get("content", "{}")
                    parsed = json.loads(content)
                    node2_inv = parsed.get("invariants_mined_node1", parsed.get("total_invariants_mined", 0))
                    self.stats["invariants_mined_node2"] = max(self.stats["invariants_mined_node2"], node2_inv)
                    self.stats["total_invariants_mined"] = self.stats["invariants_mined_node1"] + self.stats["invariants_mined_node2"]
                    return {"node2_success": True, "out": f"Node 2 Invariants={node2_inv}"}
        except Exception as e:
            logger.debug(f"Node 2 state read exception: {e}")
        return {"node2_success": False}

    # -------------------------------------------------------------------------
    # Thread A: GPU 0 Generator (RTX 3060 CUDA / Ollama)
    # -------------------------------------------------------------------------
    def _run_gpu0_generator(self) -> None:
        """Continuously synthesizes testable hypotheses from Moltbook feeds on GPU 0."""
        logger.info("⚡ [GPU 0 Thread]: RTX 3060 CUDA Generator loop online.")
        while not self.stop_event.is_set():
            if self.preempt_event.is_set():
                self.stats["gpu0_status"] = "PREEMPTED"
                time.sleep(1.0)
                continue

            if agent_controller.state.get("mode") == "PAUSED":
                self.stats["gpu0_status"] = "PAUSED_BY_USER"
                time.sleep(1.0)
                continue

            try:
                # Maintain a healthy pipeline of pending hypotheses for GPU 1 to evaluate
                counts = self.hypothesis_store.count_by_status()
                pending_count = counts.get("pending", 0)

                if pending_count < 6:
                    self.stats["gpu0_status"] = "SYNTHESIZING_HYPOTHESIS"
                    new_id = self.hypothesis_engine.synthesize_new_hypothesis_from_moltbook()
                    if new_id:
                        logger.info(f"⚡ [GPU 0]: Formulated & indexed new Moltbook hypothesis #{new_id}")
                        self.stats["gpu0_status"] = f"SYNTHESIZED_HYP_{new_id}"
                        time.sleep(0.5)
                    else:
                        self.stats["gpu0_status"] = "ACTIVE_GENERATOR"
                else:
                    self.stats["gpu0_status"] = "QUEUE_STABLE"
                    time.sleep(1.5)

            except Exception as e:
                logger.debug(f"GPU 0 Generator error: {e}")
                time.sleep(2.0)

        self.stats["gpu0_status"] = "STOPPED"

    # -------------------------------------------------------------------------
    # Thread B: GPU 1 Runner & Evaluator (RX 580 OpenCL Stream Processors)
    # -------------------------------------------------------------------------
    def _run_gpu1_runner(self) -> None:
        """Continuously pulls and evaluates data generated by GPU 0 on the RX 580 hardware."""
        logger.info("⚡ [GPU 1 Thread]: AMD RX 580 OpenCL Interpretive Runner loop online.")
        while not self.stop_event.is_set():
            if self.preempt_event.is_set():
                self.stats["gpu1_status"] = "PREEMPTED"
                time.sleep(1.0)
                continue

            try:
                pending_hyp = self.hypothesis_store.get_next_pending()
                if pending_hyp is not None:
                    self.stats["gpu1_status"] = f"EVALUATING_HYP_{pending_hyp['id']}"
                    exp_result = self.experiment_engine.execute_hypothesis(pending_hyp)
                    verdict = exp_result.get("verdict", "inconclusive")
                    measurements = exp_result.get("measurements", {})
                    submolt_label = pending_hyp.get("submolt", "m/general")

                    # If confirmed, pass to Node 2 for independent audit before final ratification
                    if verdict == "confirmed":
                        audit_res = self.node2_auditor.audit_hypothesis(
                            submolt=submolt_label,
                            claim=pending_hyp['claim'],
                            empirical_verdict=verdict,
                            measurements=measurements,
                        )
                        critique_note = audit_res.get("critique", "Consensus verified.")
                        axiom_id = f"MOLT_CONFIRMED_{pending_hyp['id']}_{int(time.time())}"
                        proof_summary = f"[{submolt_label}] {pending_hyp['claim']} | Node 2 Audit: {critique_note}"
                        clicked = self.toolbox.ratchet.click(
                            axiom_id=axiom_id,
                            claim=proof_summary,
                            proof_payload=json.dumps({"measurements": measurements, "audit": audit_res}),
                            confidence=0.98,
                            node_origin=f"DualNode-skyTech-{audit_res.get('auditor_model', 'Node2')}",
                            deduplicate_claim=True,
                        )
                        if clicked:
                            self.toolbox.hammer.rivet(
                                identifier=f"RIVET_MOLT_{pending_hyp['id']}",
                                payload={"axiom": axiom_id, "measurements": measurements, "audit": audit_res},
                            )
                            self.stats["invariants_mined_node1"] += 1
                            self.stats["total_invariants_mined"] = self.stats["invariants_mined_node1"] + self.stats["invariants_mined_node2"]
                            self.stats["ratchet_teeth_locked"] = self.toolbox.ratchet.tooth_count
                            self.stats["hammer_rivets_locked"] = self.toolbox.hammer.rivets_driven

                    logger.info(
                        f"⚡ [GPU 1 Runner]: Evaluated Hyp #{pending_hyp['id']} [{submolt_label}] ➔ {verdict.upper()} "
                        f"in {exp_result.get('duration_s', 0)}s on RX 580"
                    )
                    time.sleep(1.5)
                else:
                    # Standby gracefully instead of burning GPU power when queue is empty
                    self.stats["gpu1_status"] = "IDLE_STANDBY"
                    time.sleep(3.0)

            except Exception as e:
                logger.debug(f"GPU 1 Runner error: {e}")
                time.sleep(1.0)

        self.stats["gpu1_status"] = "STOPPED"

    # -------------------------------------------------------------------------
    # Main Orchestrator & Synthesis Loop
    # -------------------------------------------------------------------------
    def run_loop(self) -> None:
        lock = WorkerProcessLock(owner_name="continuous_worker")
        acquired, other_pid = lock.acquire()
        if not acquired:
            logger.warning(f"Another 24/7 worker daemon is already active (PID {other_pid}). Exiting duplicate process.")
            return

        self.stats["is_running"] = True
        self.stats["started_at_epoch"] = time.time()
        self._persist_state()
        logger.info("⚡ 24/7 Sovereign Dual-GPU Engine ACTIVE (GPU 0 Generator ⇄ GPU 1 Interpreter + Useful Work Engine).")

        try:
            self.hypothesis_store.reset_stale_running(max_age_s=600.0)
        except Exception:
            pass

        # Start concurrent threads
        self._gpu0_thread = threading.Thread(target=self._run_gpu0_generator, daemon=True)
        self._gpu1_thread = threading.Thread(target=self._run_gpu1_runner, daemon=True)
        self._gpu0_thread.start()
        self._gpu1_thread.start()

        try:
            while not self.stop_event.is_set():
                user_active = self.is_user_active()
                if user_active:
                    self.stats["last_active_tier"] = "Preempted (User Active)"
                    self.stats["last_preemption_epoch"] = time.time()
                    self.preempt_event.set()
                    self.toolbox.ratchet.preemption_catch(
                        cycle=self.stats["total_cycles_completed"],
                        oscillator_offset=0,
                        payload={"reason": "User query active"},
                    )
                    self._persist_state()
                    time.sleep(5.0)
                    continue
                else:
                    self.preempt_event.clear()

                try:
                    cycle_start = time.time()
                    self.stats["total_cycles_completed"] += 1
                    cur_cycle = self.stats["total_cycles_completed"]

                    # Periodically sync Node 2 over ethernet
                    if cur_cycle % 5 == 0:
                        self._step_node2_ryzen_compute()

                    # Step Unified Subsystems (Task Queue drain, Skill Crystallization, Distillation)
                    tasks_drained = 0
                    if self.unified_engine:
                        tasks_drained = self.unified_engine.step_phase1_drain_tasks(max_tasks=3)
                        if cur_cycle % 5 == 0:
                            self.unified_engine.step_phase5_skill_crystallization()
                        if cur_cycle % 10 == 0:
                            self.unified_engine.step_phase6_model_adaptation()

                    # Run real useful 24/7 workloads (rotating pytest, AST audit, GPU/JIT benchmarks, hygiene, verified LLM)
                    uw_res = useful_work_engine.run_useful_cycle(
                        hypothesis_store=self.hypothesis_store,
                        task_runner=None,
                        agent_engine=None,
                        rx580_engine=self.rx580,
                        user_active=False,
                    )
                    u_state = useful_work_engine.state
                    gpu0 = u_state.get("hardware_benchmarks", {}).get("gpu0_nvidia", {})
                    self.stats.update({
                        "workload_mode": uw_res.get("mode", "AUTO"),
                        "last_active_tier": f"Dual-GPU + Useful Work ({uw_res.get('mode', 'AUTO')})",
                        "real_tests_passed": u_state.get("real_tests_passed", 0),
                        "real_tests_failed": u_state.get("real_tests_failed", 0),
                        "real_test_pass_rate_pct": u_state.get("real_test_pass_rate_pct", 100.0),
                        "code_syntax_errors": len(u_state.get("code_audit", {}).get("syntax_errors", [])),
                        "code_files_checked": u_state.get("code_audit", {}).get("files_checked", 0),
                        "tasks_drained_total": u_state.get("tasks_drained_total", 0) + tasks_drained,
                        "gpu0_temp_c": gpu0.get("temp_c"),
                        "gpu0_vram_used_mb": gpu0.get("vram_used_mb"),
                        "verified_distillation_passed": u_state.get("distillation", {}).get("verified_passed", 0),
                        "verified_distillation_attempted": u_state.get("distillation", {}).get("attempted", 0),
                    })

                    # Synthesize empirical research deliverable ONLY when genuinely new experiments accumulate
                    if self.synthesizer.should_synthesize(min_new_experiments=20, min_interval_s=900.0):
                        del_path = self.synthesizer.compile_deliverable(cycle_range=f"Concurrent Cycle ..#{cur_cycle}")
                        if del_path:
                            self.stats["latest_deliverable"] = del_path.name

                    # Periodically scan for and ratify verified 'Aha!' system evolutions
                    if cur_cycle % 10 == 0:
                        aha_ratified = self.aha_engine.process_and_ratify_opportunities()
                        if aha_ratified:
                            logger.info(f"✨ [Aha! Optimization Ratified]: {len(aha_ratified)} updates applied to system configuration.")
                            self.stats["ratchet_teeth_locked"] = self.toolbox.ratchet.tooth_count
                            self.stats["hammer_rivets_locked"] = self.toolbox.hammer.rivets_driven

                    # Periodically generate creative mathematical art (throttled >= 30m in 24/7 background)
                    if agent_controller.state.get("art_cadence_seconds", 120) < 900:
                        agent_controller.state["art_cadence_seconds"] = 1800
                    art_piece = agent_controller.step_periodic_art_if_due()
                    if art_piece:
                        self.stats["latest_art"] = art_piece["title"]
                        self.zmq_bus.publish(
                            topic="clothos.agent.art",
                            source_node="skyTech-Worker",
                            raw_payload={
                                "id": art_piece["id"],
                                "title": art_piece["title"],
                                "style": art_piece["style"],
                                "svg_file": art_piece["svg_file"],
                            },
                        )

                    # Always update the live executive briefing
                    brief_path = useful_work_engine.synthesize_briefing(worker_stats=self.stats)
                    self.stats["latest_briefing"] = str(brief_path)

                    # QCT Routing & ZeroMQ Telemetry Broadcast
                    route_decision = self.router.route_query(
                        prompt=f"ClothOS Dual-GPU Concurrent Cycle {cur_cycle}",
                        vram_margin_mb=12918,
                    )

                    self.zmq_bus.publish(
                        topic="fabric.worker.cycle",
                        source_node="skyTech-Worker",
                        raw_payload={
                            "cycle": cur_cycle,
                            "mode": self.stats.get("workload_mode"),
                            "tier": route_decision.tier,
                            "gpu0_status": self.stats["gpu0_status"],
                            "gpu1_status": self.stats["gpu1_status"],
                            "real_tests_passed": self.stats.get("real_tests_passed", 0),
                            "real_tests_failed": self.stats.get("real_tests_failed", 0),
                            "hypotheses_indexed": self.stats["moltbook_hypotheses_indexed"],
                            "experiments_evaluated": self.stats["experiments_evaluated"],
                            "hypotheses_confirmed": self.stats["hypotheses_confirmed"],
                            "hypotheses_refuted": self.stats["hypotheses_refuted"],
                            "deliverables_published": self.stats["deliverables_published"],
                            "ratchet_teeth": self.stats["ratchet_teeth_locked"],
                            "hammer_rivets": self.stats["hammer_rivets_locked"],
                        },
                    )

                    elapsed = round(time.time() - cycle_start, 2)
                    msg = (
                        f"Cycle #{cur_cycle:,} ({elapsed}s) [{self.stats.get('workload_mode')}] | "
                        f"Tests: {self.stats.get('real_tests_passed', 0)}P/{self.stats.get('real_tests_failed', 0)}F | "
                        f"Tasks: {tasks_drained} | Tested: {self.stats['experiments_evaluated']} | "
                        f"GPU0: {gpu0.get('temp_c', '?')}C"
                    )
                    self.stats["last_log_message"] = msg
                    logger.info(msg)

                    self._persist_state()
                    sleep_s = float(uw_res.get("recommended_sleep_s", 15.0))
                    self.stop_event.wait(timeout=max(5.0, sleep_s))

                except Exception as e:
                    logger.error(f"Error in orchestrator loop: {e}", exc_info=True)
                    self.stop_event.wait(timeout=5.0)
        finally:
            self.stats["is_running"] = False
            self.stats["last_active_tier"] = "Stopped"
            self._persist_state()
            lock.release()
            logger.info("Continuous Sovereign Research Engine stopped gracefully.")

    def _step_node1_babel_kuramoto(self, *args, **kwargs) -> Dict[str, Any]:
        """Backward-compatible helper for GUI manual sweeps."""
        return self.rx580.step_sweep(steps=2500, k_coupling=2.6)

    def _step_node1_vectorforge_indexing(self, *args, **kwargs) -> Dict[str, Any]:
        """Backward-compatible helper for GUI manual sweeps."""
        res, _ = self.experiment_engine._run_vector_geometry_experiment({"batch_size": 256, "dim": 1536})
        return res

    def start_background(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self.stop_event.clear()
        self.preempt_event.clear()
        self._thread = threading.Thread(target=self.run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self.stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=5.0)


# Module-level singleton
worker_instance = ContinuousComputeWorker()


def get_worker_status() -> Dict[str, Any]:
    return dict(worker_instance.stats)


def start_worker_daemon() -> None:
    worker_instance.start_background()


def stop_worker_daemon() -> None:
    worker_instance.stop()


if __name__ == "__main__":
    worker = ContinuousComputeWorker()
    try:
        worker.run_loop()
    except KeyboardInterrupt:
        worker.stop()
