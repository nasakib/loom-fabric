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

import json
from pathlib import Path
import time
from typing import Dict, Optional, Tuple
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
    openclaw_loop_ready: bool = Field(default=True)


class ClothOSKernel:
    """Sovereign Agentic OS Kernel managing Fabric, Loom, Stitch, Torque, OpenClaw, Moltbook, and shapeShift."""

    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = workspace_root or Path(__file__).resolve().parents[2]
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
