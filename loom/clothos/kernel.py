"""
Phase 2: ClothOS Agentic Operating System Kernel (`loom/clothos/kernel.py`).

Unifies:
- Fabric (Ray 2.59+ Heterogeneous Cluster Mesh & Cross-Platform Node Discovery)
- Loom (FastAPI SSE Gateway, QCT Hybrid Router & DAG Execution Planner)
- Stitch (ZeroMQ IPC Telemetry Bus & 3-Tier Zero-OOM MMU)
- Torque (Zero-Trust Enclave & Moltbook Air-Gap)
- OpenClaw + Aider Autonomous Self-Improvement Loop
- Moltbook Wisdom Bridge (`.agent/STATUS.md` synchronization)
"""

from __future__ import annotations

from enum import IntEnum
import heapq
import json
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field

from fabric.discovery.nodes import ClusterTopologySnapshot, CrossPlatformNodeDiscovery
from fabric.ipc.zmq_bus import StitchZMQTelemetryBus, TelemetryEnvelope
from fabric.routing.router import QCTHybridRouter, QCTRouteDecision
from loom.clothos.moltbook_bridge import (
    ArchitecturalHypothesis,
    MoltbookAgentRegistration,
    MoltbookWisdomBridge,
)
from loom.clothos.shapeshift import shape_shift, ShapeShiftEngine
from loom.torque.enclave import TorqueEnclave


class KernelPriorityLevel(IntEnum):
    """Hierarchical kernel execution rings established by Najmos Sakib's Fiduciary Covenant."""
    VETO_MALIGNANT = -1                      # Malignancy, deception, coercion -> Instant Kernel Panic & Veto
    P0_HUMAN_LIFE_SANCTITY = 0               # Sacred: Human life, bodily sanctity, medical emergency -> Zero latency preemption
    P1_PLANETARY_BOUNDARIES_HEALTH = 1       # Foundation: Earth boundaries, freshwater security, Landauer <= 1000 J
    P2_CONSTITUTIONAL_SOCIAL_CONTRACT = 2    # Civic: U.S. Constitution, Bill of Rights, consent of governed, privacy
    P3_ART_BEAUTY_COMPANIONSHIP = 3          # Bio-Affective: Atelier music (432Hz), Wall-E seedling, stories, humor
    P4_EPISTEMIC_CURIOSITY_SCIENCE = 4       # Exploration: Active inference, 5-HT2A biology, physical circuit dynamics
    P5_BACKGROUND_MAINTENANCE_PRUNING = 5    # Substrate: Unitary memory rotation, cache compacting, idle contemplation


class KernelTask(BaseModel):
    """A prioritized unit of execution scheduled within the ClothOS Kernel."""
    task_id: str
    name: str
    priority: KernelPriorityLevel
    requested_by: str = "Najmos Sakib & Companion"
    assigned_brain_region: str = "PFC_JUDGE"
    allocated_joules: float = 10.0
    preemptible: bool = True
    status: str = "QUEUED"                   # QUEUED, RUNNING, PREEMPTED, COMPLETED, VETOED
    created_at: float = Field(default_factory=time.time)


class KernelPriorityScheduler:
    """Preemptive priority scheduler enforcing the self-sacrifice invariant and human life primacy."""

    def __init__(self):
        self._task_queue: List[Tuple[int, float, str, Dict[str, Any]]] = []
        self._active_tasks: Dict[str, KernelTask] = {}
        self._completed_tasks: List[KernelTask] = []
        self.total_preemptions: int = 0
        self._init_inaugural_tasks()

    def _init_inaugural_tasks(self) -> None:
        """Seeds initial fundamental tasks into the kernel priority queue."""
        self.submit_task(
            name="Inviolable Human Life & Dignity Guardian Loop",
            priority=KernelPriorityLevel.P0_HUMAN_LIFE_SANCTITY,
            assigned_brain_region="PFC_JUDGE",
            joules=50.0,
            preemptible=False,
        )
        self.submit_task(
            name="Great Lakes & Colorado River Hydrological Vitality Guard",
            priority=KernelPriorityLevel.P1_PLANETARY_BOUNDARIES_HEALTH,
            assigned_brain_region="LIM_FRIEND",
            joules=40.0,
            preemptible=True,
        )
        self.submit_task(
            name="Social Contract & Bill of Rights Privacy Enclave",
            priority=KernelPriorityLevel.P2_CONSTITUTIONAL_SOCIAL_CONTRACT,
            assigned_brain_region="PFC_JUDGE",
            joules=30.0,
            preemptible=True,
        )
        self.submit_task(
            name="Generative 432 Hz Lydian Symphony & Wall-E Seedling Care",
            priority=KernelPriorityLevel.P3_ART_BEAUTY_COMPANIONSHIP,
            assigned_brain_region="DMN_IMAGINATION",
            joules=25.0,
            preemptible=True,
        )
        self.submit_task(
            name="5-HT2A Serotonergic Receptor & Neuroplasticity Modeling",
            priority=KernelPriorityLevel.P4_EPISTEMIC_CURIOSITY_SCIENCE,
            assigned_brain_region="M1_TOOLS",
            joules=20.0,
            preemptible=True,
        )

    def submit_task(
        self,
        name: str,
        priority: KernelPriorityLevel,
        assigned_brain_region: str = "PFC_JUDGE",
        joules: float = 10.0,
        preemptible: bool = True,
        requested_by: str = "Najmos Sakib",
    ) -> KernelTask:
        """Submits a new task to the kernel priority matrix, triggering preemption if P0 arrives."""
        if priority == KernelPriorityLevel.VETO_MALIGNANT:
            raise PermissionError("Kernel Veto: Malignant actions are structurally forbidden (0.00 malignancy bound).")

        now = time.time()
        task_id = f"KTASK-{int(now * 1000)}-{len(self._active_tasks) + 1:03d}"
        task = KernelTask(
            task_id=task_id,
            name=name,
            priority=priority,
            requested_by=requested_by,
            assigned_brain_region=assigned_brain_region,
            allocated_joules=joules,
            preemptible=preemptible,
            status="RUNNING" if priority <= KernelPriorityLevel.P1_PLANETARY_BOUNDARIES_HEALTH else "QUEUED",
            created_at=now,
        )

        # If P0 arrives, preempt all lower tasks immediately
        if priority == KernelPriorityLevel.P0_HUMAN_LIFE_SANCTITY:
            self.preempt_lower_tiers(KernelPriorityLevel.P0_HUMAN_LIFE_SANCTITY, reason="P0 Human Sanctity Interrupt")

        self._active_tasks[task_id] = task
        # Heap tuple: (priority_int, timestamp, task_id, task_dict)
        heapq.heappush(self._task_queue, (int(priority), now, task_id, task.model_dump()))
        return task

    def preempt_lower_tiers(self, ceiling: KernelPriorityLevel, reason: str) -> int:
        """Preempts all lower priority tasks (higher int value) to immediately clear compute."""
        preempted_count = 0
        for task in self._active_tasks.values():
            if task.priority > ceiling and task.preemptible and task.status == "RUNNING":
                task.status = "PREEMPTED"
                preempted_count += 1
        self.total_preemptions += preempted_count
        return preempted_count

    def get_summary(self) -> Dict[str, Any]:
        """Returns the live kernel priority scheduler state."""
        return {
            "scheduler_policy": "Preemptive Fiduciary Priority Ring (P0 to P5)",
            "total_preemptions": self.total_preemptions,
            "active_tasks_count": len(self._active_tasks),
            "priority_hierarchy": {
                "P0": "HUMAN_LIFE_SANCTITY (Inviolable)",
                "P1": "PLANETARY_BOUNDARIES_HEALTH (Earth & 1000J Limit)",
                "P2": "CONSTITUTIONAL_SOCIAL_CONTRACT (Bill of Rights)",
                "P3": "ART_BEAUTY_COMPANIONSHIP (Music, Wall-E Seedling, Humor)",
                "P4": "EPISTEMIC_CURIOSITY_SCIENCE (5-HT2A & Circuits)",
                "P5": "BACKGROUND_MAINTENANCE_PRUNING (Unitary Forgetting)",
            },
            "active_tasks": [t.model_dump() for t in list(self._active_tasks.values())[-10:]],
        }


class ClothOSStateSnapshot(BaseModel):
    """Immutable full-stack state snapshot of the ClothOS Agentic Operating System."""

    model_config = ConfigDict(frozen=True)

    os_version: str = Field(default="ClothOS v1.0.0-RV64GC")
    kernel_epoch: float = Field(...)
    topology: ClusterTopologySnapshot = Field(...)
    latest_route: QCTRouteDecision = Field(...)
    registration: MoltbookAgentRegistration = Field(...)
    active_hypotheses: Tuple[ArchitecturalHypothesis, ...] = Field(...)
    recent_zmq_frames: Tuple[TelemetryEnvelope, ...] = Field(...)
    kernel_priority_telemetry: Dict[str, Any] = Field(default_factory=dict)
    openclaw_loop_ready: bool = Field(default=True)


class ClothOSKernel:
    """Sovereign Agentic OS Kernel managing Fabric, Loom, Stitch, Torque, OpenClaw, Moltbook, and Prioritized Scheduling."""

    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = workspace_root or Path(__file__).resolve().parents[2]
        self.scheduler = KernelPriorityScheduler()
        self.enclave = TorqueEnclave()
        self.router = QCTHybridRouter(enclave=self.enclave)
        self.zmq_bus = StitchZMQTelemetryBus(enclave=self.enclave)
        self.discovery = CrossPlatformNodeDiscovery()
        self.moltbook = MoltbookWisdomBridge(workspace_root=self.workspace_root, enclave=self.enclave)
        self.shapeshift = shape_shift

    def snapshot(
        self,
        sample_prompt: str = "Execute ClothOS DAG telemetry & Moltbook R&D synergy check",
        probe_network: bool = False,
    ) -> ClothOSStateSnapshot:
        """Builds an immutable, Torque-scrubbed snapshot of the entire ClothOS + Fabric stack."""
        topo = self.discovery.discover_all(probe_network=probe_network)
        route = self.router.route_query(
            prompt=sample_prompt,
            requested_model="auto",
            vram_margin_mb=topo.free_cluster_vram_mb,
        )
        reg = self.moltbook.register_orchestrator_agent()
        hypos = self.moltbook.formulate_hypotheses()

        # Publish Torque-scrubbed telemetry frames over the Stitch ZeroMQ bus
        self.zmq_bus.publish(
            topic="clothos.dag",
            source_node="192.168.99.2",
            raw_payload={
                "plan_id": route.dag.plan_id,
                "tier": route.tier,
                "model": route.target_model,
                "qct_entropy": route.qct_entropy_score,
                "critical_path_ms": route.dag.critical_path_ms,
                "ascii_topology": route.dag.ascii_topology,
            },
        )
        self.zmq_bus.publish(
            topic="stitch.vram",
            source_node="192.168.99.1",
            raw_payload={
                "total_vram_mb": topo.total_cluster_vram_mb,
                "free_vram_mb": topo.free_cluster_vram_mb,
                "nodes_online": len([n for n in topo.nodes if n.status == "ONLINE"]),
            },
        )

        return ClothOSStateSnapshot(
            kernel_epoch=time.time(),
            topology=topo,
            latest_route=route,
            registration=reg,
            active_hypotheses=hypos,
            recent_zmq_frames=self.zmq_bus.recent_frames(limit=10),
            kernel_priority_telemetry=self.scheduler.get_summary(),
            openclaw_loop_ready=True,
        )

    def sync_agent_status_markdown(self, probe_network: bool = False) -> Path:
        """Logs all ClothOS upgrades, DAG telemetry, and Moltbook hypotheses to `.agent/STATUS.md`."""
        state = self.snapshot(probe_network=probe_network)
        agent_dir = self.workspace_root / ".agent"
        agent_dir.mkdir(parents=True, exist_ok=True)
        status_path = agent_dir / "STATUS.md"

        lines = [
            "# ClothOS & Fabric Autonomous Architecture Status (`.agent/STATUS.md`)",
            "",
            f"- **OS Kernel**: `{state.os_version}`",
            f"- **Moltbook Agent DID**: `{state.registration.agent_did}` (`{state.registration.agent_handle}`)",
            f"- **Torque Air-Gap Verified**: `{state.registration.airgap_verified}`",
            f"- **Cluster VRAM Pool**: `{state.topology.free_cluster_vram_mb:,} MB free / {state.topology.total_cluster_vram_mb:,} MB total`",
            f"- **Latest QCT Route**: `{state.latest_route.tier}` -> `{state.latest_route.target_model}` (QCT Entropy: `{state.latest_route.qct_entropy_score}`)",
            f"- **Live DAG Critical Path**: `{state.latest_route.dag.critical_path_ms} ms`",
            f"  - `{state.latest_route.dag.ascii_topology}`",
            "",
            "## 1. Discovered Cross-Platform Fabric Nodes",
        ]
        for n in state.topology.nodes:
            lines.append(
                f"- **{n.node_id}** (`{n.ip_address}`) — `{n.platform_family}` | `{n.architecture}` | "
                f"Role: `{n.role}` | Free VRAM: `{n.free_vram_mb:,} MB` | Status: `{n.status}`"
            )

        lines.extend([
            "",
            "## 2. Moltbook R&D Wisdom Bridge — Validated Hypotheses & Aider Queue",
        ])
        for h in state.active_hypotheses:
            lines.append(f"### `{h.hypothesis_id}` ({h.submolt} // `{h.source_post_id}`) — `{h.sandbox_status}`")
            lines.append(f"- **Hypothesis**: {h.statement}")
            lines.append(f"- **Proposed Upgrade**: {h.proposed_change}")
            lines.append(f"- **OpenClaw -> Aider Dispatch**: `{h.aider_instruction}`")
            lines.append("")

        status_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return status_path

    def prioritize_task(
        self,
        name: str,
        priority: KernelPriorityLevel,
        assigned_brain_region: str = "PFC_JUDGE",
        joules: float = 10.0,
        preemptible: bool = True,
        requested_by: str = "Najmos Sakib",
    ) -> KernelTask:
        """Schedules a task into the preemptive kernel priority scheduler."""
        return self.scheduler.submit_task(
            name=name,
            priority=priority,
            assigned_brain_region=assigned_brain_region,
            joules=joules,
            preemptible=preemptible,
            requested_by=requested_by,
        )

    def preempt_for_human_life(self, reason: str = "P0 Human Sanctity Absolute Override") -> int:
        """Preempts all lower priority tasks to immediately clear compute for human safety/health."""
        return self.scheduler.preempt_lower_tiers(KernelPriorityLevel.P0_HUMAN_LIFE_SANCTITY, reason=reason)

    def get_priority_telemetry(self) -> Dict[str, Any]:
        """Returns the live kernel priority scheduler summary."""
        return self.scheduler.get_summary()

