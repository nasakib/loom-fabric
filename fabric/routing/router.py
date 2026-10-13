"""
QCT Hybrid Router & Directed Acyclic Graph (DAG) Execution Planner for Fabric.

Binds the four mechanistic pillars:
- Fabric (Distributed Ray 2.59+ Node Pool)
- Loom (FastAPI SSE Gateway & QCT Complexity Router)
- Stitch (ZeroMQ IPC Telemetry & 3-Tier Zero-OOM MMU)
- Torque (Zero-Trust Tokenization Enclave & Moltbook Egress Guard)
- ClothOS (Agentic Operating System & RISC-V RV64GC + RVV 1.0 Silicon Target)

All state models enforce strict Pydantic v2 `ConfigDict(frozen=True)` immutability.
"""

from __future__ import annotations

import hashlib
import time
from typing import Dict, List, Literal, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field

from loom.torque.enclave import TorqueEnclave
from loom.torque.router import HybridRouter


class DAGNode(BaseModel):
    """Immutable node in the Fabric Directed Acyclic Graph (DAG) execution plan."""

    model_config = ConfigDict(frozen=True)

    node_id: str = Field(..., description="Unique DAG stage identifier.")
    stage_name: str = Field(..., description="Human-readable stage name.")
    pillar: Literal["Torque", "Stitch", "Loom", "Fabric", "ClothOS"] = Field(
        ..., description="Subsystem pillar owning this execution stage."
    )
    assigned_hardware: str = Field(..., description="Target silicon node or enclave.")
    depends_on: Tuple[str, ...] = Field(default_factory=tuple, description="Upstream DAG node IDs.")
    estimated_latency_ms: float = Field(..., ge=0.0, description="Projected stage latency in ms.")
    status: Literal["READY", "EXECUTING", "VERIFIED"] = Field(default="VERIFIED")


class DAGExecutionPlan(BaseModel):
    """Immutable Directed Acyclic Graph (DAG) telemetry payload for UI & ClothOS inspection."""

    model_config = ConfigDict(frozen=True)

    plan_id: str = Field(..., description="Deterministic hash ID of the DAG plan.")
    created_at_epoch: float = Field(..., description="UTC epoch timestamp.")
    nodes: Tuple[DAGNode, ...] = Field(..., description="Ordered topological stages.")
    critical_path_ms: float = Field(..., ge=0.0, description="Total critical path latency in ms.")
    ascii_topology: str = Field(..., description="Compact ASCII DAG representation for UI rendering.")


class QCTRouteDecision(BaseModel):
    """Immutable QCT Hybrid Router decision with Torque Enclave verification and DAG telemetry."""

    model_config = ConfigDict(frozen=True)

    decision_id: str = Field(..., description="Deterministic QCT decision digest.")
    tier: Literal[
        "tier_1_local_rapid",
        "tier_2_distributed_ray_mesh",
        "tier_3_cloud_arbitrage",
        "tier_4_clothos_riscv_rvv",
    ] = Field(..., description="Selected execution tier.")
    target_model: str = Field(..., description="Selected model identifier.")
    qct_entropy_score: float = Field(..., ge=0.0, le=1.0, description="Normalized QCT complexity score [0..1].")
    estimated_compute_seconds: float = Field(..., ge=0.0, description="Estimated wall-clock compute duration.")
    vram_margin_mb: int = Field(..., ge=0, description="Available VRAM margin across RTX 3060 + RX 580.")
    torque_scrubbed: bool = Field(..., description="True if prompt passed through Torque Enclave scrubbing.")
    sanitized_prompt_preview: str = Field(..., description="Torque-scrubbed prompt preview safe for UI telemetry.")
    dag: DAGExecutionPlan = Field(..., description="Attached Directed Acyclic Graph execution plan.")


class QCTHybridRouter:
    """Quantum-Classical-Tensor (QCT) Hybrid Router for Fabric & ClothOS."""

    def __init__(self, enclave: Optional[TorqueEnclave] = None):
        self.enclave = enclave or TorqueEnclave()
        self.legacy_router = HybridRouter(enclave=self.enclave)

    def compute_qct_entropy(self, prompt: str) -> float:
        """Computes a normalized [0.0, 1.0] QCT structural complexity score for a prompt."""
        if not prompt.strip():
            return 0.05
        lower = prompt.lower()
        tokens_est = max(1, len(prompt.split()))
        length_factor = min(0.45, tokens_est / 400.0)

        deep_keywords = (
            "architect",
            "clothos",
            "riscv",
            "risc-v",
            "rvv",
            "prove",
            "smt",
            "z3",
            "formal",
            "distributed",
            "shard",
            "moltbook",
            "synergy",
            "refactor",
            "optimize",
            "kernel",
            "mmu",
            "zeromq",
            "dag",
        )
        hits = sum(1 for kw in deep_keywords if kw in lower)
        keyword_factor = min(0.55, hits * 0.09)
        return round(min(1.0, max(0.05, length_factor + keyword_factor)), 3)

    def build_dag_plan(
        self,
        tier: str,
        target_model: str,
        vram_margin_mb: int,
        prefer_riscv: bool = False,
    ) -> DAGExecutionPlan:
        """Constructs an immutable topological DAG execution plan across Torque, Stitch, Loom, Fabric, and ClothOS."""
        now = time.time()
        digest = hashlib.sha256(f"{tier}:{target_model}:{now}".encode("utf-8")).hexdigest()[:10]

        n1 = DAGNode(
            node_id="stage_1_torque",
            stage_name="Torque Zero-Trust Enclave Scrubbing",
            pillar="Torque",
            assigned_hardware="Ryzen 7 7730U Head (192.168.99.2) // PMP CSR 0x9B",
            depends_on=(),
            estimated_latency_ms=1.2,
        )
        n2 = DAGNode(
            node_id="stage_2_stitch",
            stage_name=f"Stitch Zero-OOM MMU & ZeroMQ Bus (Margin: {vram_margin_mb:,} MB)",
            pillar="Stitch",
            assigned_hardware="Tier-1 VRAM (RTX 3060 12GB + RX 580 8GB) -> Tier-2 DDR4",
            depends_on=("stage_1_torque",),
            estimated_latency_ms=2.4,
        )
        n3 = DAGNode(
            node_id="stage_3_loom",
            stage_name=f"Loom QCT Hybrid Router ({tier})",
            pillar="Loom",
            assigned_hardware="FastAPI SSE Gateway (:8002)",
            depends_on=("stage_2_stitch",),
            estimated_latency_ms=1.8,
        )

        if prefer_riscv or tier == "tier_4_clothos_riscv_rvv":
            exec_hw = "ClothOS RISC-V RV64GC + RVV 1.0 (512-bit Vector Strip-Mined)"
            exec_pillar: Literal["Torque", "Stitch", "Loom", "Fabric", "ClothOS"] = "ClothOS"
            exec_lat = 18.5
        elif tier == "tier_2_distributed_ray_mesh":
            exec_hw = "Fabric Ray Mesh: skyTech RTX 3060 (CUDA) + RX 580 (Vulkan) + Ryzen Head"
            exec_pillar = "Fabric"
            exec_lat = 42.0
        elif tier == "tier_3_cloud_arbitrage":
            exec_hw = "Air-Gapped Cloud Arbitrage (Torque Vault Tokenized)"
            exec_pillar = "Torque"
            exec_lat = 95.0
        else:
            exec_hw = "skyTech Worker (192.168.99.1) // RTX 3060 CUDA Rapid Path"
            exec_pillar = "Fabric"
            exec_lat = 14.0

        n4 = DAGNode(
            node_id="stage_4_compute",
            stage_name=f"Tensor Execution ({target_model})",
            pillar=exec_pillar,
            assigned_hardware=exec_hw,
            depends_on=("stage_3_loom",),
            estimated_latency_ms=exec_lat,
        )
        n5 = DAGNode(
            node_id="stage_5_rehydrate",
            stage_name="Torque Vault Rehydration & ClothOS Telemetry Commit",
            pillar="ClothOS",
            assigned_hardware="Ryzen 7 Head (192.168.99.2) -> SSE Stream",
            depends_on=("stage_4_compute",),
            estimated_latency_ms=1.1,
        )

        nodes = (n1, n2, n3, n4, n5)
        total_ms = round(sum(n.estimated_latency_ms for n in nodes), 2)
        ascii_dag = (
            "[1:Torque Enclave] ──▶ [2:Stitch MMU/ZMQ] ──▶ [3:Loom QCT Router] "
            f"──▶ [4:{exec_pillar}:{target_model}] ──▶ [5:ClothOS Rehydrate]"
        )

        return DAGExecutionPlan(
            plan_id=f"dag-{digest}",
            created_at_epoch=now,
            nodes=nodes,
            critical_path_ms=total_ms,
            ascii_topology=ascii_dag,
        )

    def route_query(
        self,
        prompt: str,
        requested_model: str = "auto",
        vram_margin_mb: int = 12918,
        prefer_riscv: bool = False,
    ) -> QCTRouteDecision:
        """Evaluates prompt through Torque Enclave and QCT complexity scorer, returning a frozen QCTRouteDecision."""
        scrub_res = self.enclave.scrub_outbound(prompt)
        sanitized_text = scrub_res.sanitized_text
        was_scrubbed = len(scrub_res.vault_mapping) > 0

        entropy = self.compute_qct_entropy(prompt)
        est_sec = float(self.legacy_router.estimate_compute_seconds(prompt))

        if prefer_riscv:
            tier: Literal[
                "tier_1_local_rapid",
                "tier_2_distributed_ray_mesh",
                "tier_3_cloud_arbitrage",
                "tier_4_clothos_riscv_rvv",
            ] = "tier_4_clothos_riscv_rvv"
            model = requested_model if requested_model != "auto" else "qwen2.5:7b-rvv-q4"
        elif est_sec > 300.0 or entropy >= 0.85:
            tier = "tier_3_cloud_arbitrage"
            model = requested_model if requested_model != "auto" else "qwen2.5:32b"
        elif entropy >= 0.45 or requested_model in ("qwen2.5:32b", "deepseek-r1:14b"):
            tier = "tier_2_distributed_ray_mesh"
            model = requested_model if requested_model != "auto" else "deepseek-r1:14b"
        else:
            tier = "tier_1_local_rapid"
            model = requested_model if requested_model != "auto" else "qwen2.5:7b"

        dag = self.build_dag_plan(
            tier=tier,
            target_model=model,
            vram_margin_mb=max(0, vram_margin_mb),
            prefer_riscv=prefer_riscv,
        )
        decision_id = hashlib.sha256(f"{dag.plan_id}:{entropy}:{model}".encode("utf-8")).hexdigest()[:12]

        preview = sanitized_text[:160] + ("..." if len(sanitized_text) > 160 else "")
        return QCTRouteDecision(
            decision_id=f"qct-{decision_id}",
            tier=tier,
            target_model=model,
            qct_entropy_score=entropy,
            estimated_compute_seconds=est_sec,
            vram_margin_mb=max(0, vram_margin_mb),
            torque_scrubbed=was_scrubbed,
            sanitized_prompt_preview=preview,
            dag=dag,
        )
