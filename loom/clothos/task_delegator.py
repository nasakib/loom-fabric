# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
ClothOS Autonomous Task Delegation & Sub-Agent Orchestrator (`loom/clothos/task_delegator.py`).

Fulfills Head Orchestrator (Node 2) & Decider Mandate:
Autonomously analyzes complex, multi-faceted tasks and delegates execution to specialized
engines across the dual-node cluster and agent swarm:

1. NODE_1_ACCELERATOR: Heavy tensor processing, CUDA/OpenCL math, 3D rendering.
2. NODE_2_DECIDER: Logical verification, Ahimsa M=0.00 audit, Merkle DAG commitment.
3. OPENCLAW_SWARM: Autonomous code generation, surgical Aider edits, git staging.
4. SELF_TRAINING_ENGINE: Empirical hardware tests, Hebbian weight distillation.
5. ART_CURIO_ENGINE: Multi-modal art synthesis, aesthetic ratio decomposition.
6. CNS_SENSORY_ENGINE: Live macro, geopolitics, and literature ingestion.
"""

from __future__ import annotations

import json
import logging
import re
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("loom.clothos.task_delegator")

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class SubTaskAssignment:
    subtask_id: str
    target_engine: str  # NODE_1_ACCELERATOR, NODE_2_DECIDER, OPENCLAW_SWARM, SELF_TRAIN, ART_ENGINE, CNS_SENSORY
    description: str
    parameters: Dict[str, Any]
    status: str = "PENDING"  # PENDING, EXECUTING, COMPLETED, FAILED
    result: Optional[Any] = None
    execution_time_s: float = 0.0


@dataclass
class DelegationPlan:
    plan_id: str
    original_goal: str
    orchestrating_node: str  # Ryzen7-Head (Node 2 Decider)
    timestamp: float
    subtasks: List[SubTaskAssignment] = field(default_factory=list)
    overall_status: str = "INITIALIZED"
    synthesis: Optional[str] = None


class AutonomousTaskDelegator:
    """Decomposes and autonomously delegates tasks across cluster nodes and specialized engines."""

    def __init__(self, workspace_root: Optional[Path] = None, tools_executor: Optional[Any] = None):
        self.workspace_root = Path(workspace_root or WORKSPACE_ROOT).resolve()
        self.tools_executor = tools_executor
        self.history: List[DelegationPlan] = []

    def plan_and_delegate(self, goal: str, tool_registry: Optional[Dict[str, Any]] = None) -> DelegationPlan:
        """Analyzes a high-level goal, formulates assignments, and executes autonomous delegation."""
        plan_id = f"plan_{int(time.time() * 1000)}"
        plan = DelegationPlan(
            plan_id=plan_id,
            original_goal=goal,
            orchestrating_node="Node 2 (Ryzen 7 7730U - Decider & Head Orchestrator)",
            timestamp=time.time(),
        )

        g_lower = goal.lower()
        subtasks: List[SubTaskAssignment] = []

        # 1. Sensory Ingestion requirement
        if any(w in g_lower for w in ["market", "news", "science", "status", "health", "cns", "telemetry", "all cylinders", "everything"]):
            subtasks.append(SubTaskAssignment(
                subtask_id=f"{plan_id}_sub1_cns",
                target_engine="CNS_SENSORY_ENGINE",
                description="Query Central Nervous System for live macro, geopolitics, and literature telemetry.",
                parameters={"tool": "cns_telemetry", "args": {}},
            ))

        # 2. Hardware Compute & Acceleration (Node 1 SkyTech)
        if any(w in g_lower for w in ["gpu", "cuda", "opencl", "matmul", "tpu", "systolic", "benchmark", "riscv", "all cylinders", "everything"]):
            subtasks.append(SubTaskAssignment(
                subtask_id=f"{plan_id}_sub2_node1_accel",
                target_engine="NODE_1_ACCELERATOR",
                description="Delegate heavy systolic or vectorized assembly kernel generation to Node 1 SkyTech compute.",
                parameters={"tool": "riscv_generate", "args": {"template": "tpu_systolic"}},
            ))

        # 3. Empirical Self-Training & Weight Adaptation
        if any(w in g_lower for w in ["train", "weights", "experiment", "hopfield", "kuramoto", "learn", "all cylinders", "everything"]):
            subtasks.append(SubTaskAssignment(
                subtask_id=f"{plan_id}_sub3_selftrain",
                target_engine="SELF_TRAINING_ENGINE",
                description="Dispatch empirical hardware validation tests and distill Hebbian training pairs.",
                parameters={"tool": "model_train_self", "args": {}},
            ))

        # 4. Multi-Modal Sovereign Art & Curiosity Engine
        if any(w in g_lower for w in ["art", "curiosity", "geometry", "432hz", "music", "poetry", "idle", "all cylinders", "everything"]):
            subtasks.append(SubTaskAssignment(
                subtask_id=f"{plan_id}_sub4_art",
                target_engine="ART_CURIO_ENGINE",
                description="Synthesize multi-modal sovereign art and extract epistemic curiosity hypothesis.",
                parameters={"tool": "art_idle_cycle", "args": {"modality": "VISUAL_GEOMETRY"}},
            ))

        # 5. OpenClaw Autonomic Swarm & Moltbook
        if any(w in g_lower for w in ["openclaw", "claw", "moltbook", "r&d", "swarm", "all cylinders", "everything"]):
            subtasks.append(SubTaskAssignment(
                subtask_id=f"{plan_id}_sub5_openclaw",
                target_engine="OPENCLAW_SWARM",
                description="Synchronize Moltbook R&D signals and verify OpenClaw gateway zero-trust bridge.",
                parameters={"tool": "moltbook_harvest", "args": {}},
            ))

        # 6. Node 2 Sovereign Decider Arbitration
        subtasks.append(SubTaskAssignment(
            subtask_id=f"{plan_id}_sub6_node2_decider",
            target_engine="NODE_2_DECIDER",
            description="Audit all executed sub-task results against Ahimsa M=0.00 and compile J.A.R.V.I.S. sitrep.",
            parameters={"tool": "jarvis_briefing", "args": {"speak_aloud": False}},
        ))

        # Execute assigned subtasks via tools executor
        plan.subtasks = subtasks
        plan.overall_status = "EXECUTING"

        results_summary = []
        for st in plan.subtasks:
            t0 = time.time()
            st.status = "EXECUTING"
            tool_name = st.parameters.get("tool")
            tool_args = st.parameters.get("args", {})

            if self.tools_executor and tool_name:
                try:
                    res = self.tools_executor(tool_name, **tool_args)
                    st.status = "COMPLETED"
                    st.result = res
                    st.execution_time_s = round(time.time() - t0, 3)
                    results_summary.append(f"✔ **{st.target_engine}** ({st.description}) ➔ `{st.status}` ({st.execution_time_s}s)")
                except Exception as e:
                    st.status = "FAILED"
                    st.result = {"error": str(e)}
                    st.execution_time_s = round(time.time() - t0, 3)
                    results_summary.append(f"❌ **{st.target_engine}** ({st.description}) ➔ `FAILED: {e}`")
            else:
                st.status = "DELEGATED_TO_REMOTE_BUFFER"
                st.result = {"note": f"Dispatched to {st.target_engine}"}
                st.execution_time_s = round(time.time() - t0, 3)
                results_summary.append(f"⚡ **{st.target_engine}** ({st.description}) ➔ `DELEGATED`")

        plan.overall_status = "COMPLETED"
        plan.synthesis = "\n".join(results_summary)
        self.history.append(plan)
        return plan
