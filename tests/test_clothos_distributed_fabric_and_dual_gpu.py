"""
Unit Test Suite for ClothOS Distributed Fabric Optimizer, Dual-GPU Paired VRAM Engine,
Crystallized Knowledgebase (Gc), and Test-Driven Skill Evolver (TDSA).
"""

import math
from pathlib import Path
import pytest

from loom.clothos.dual_gpu_runner import ClothOSDualGPURunner, DualGPURunner
from loom.clothos.fabric_optimizer import FabricWorkloadOptimizer
from loom.clothos.crystallized_engine import CrystallizedKnowledgeEngine
from loom.clothos.skill_evolver import SkillEvolver, ClothOSSkill


# ==============================================================================
# DualGPURunner Test Suite
# ==============================================================================

def test_dual_gpu_topology_and_vram_pooling():
    topo = ClothOSDualGPURunner.get_topology()
    assert topo["status"] == "PAIRED_ONLINE"
    assert topo["node1_paired_vram_gb"] == 20.0
    assert topo["cluster_pooled_vram_gb"] == 32.1
    assert "5.9x faster" in topo["rx580_bandwidth_advantage"]
    assert "9.5x faster" in topo["rtx3060_bandwidth_advantage"]
    assert len(topo["node1_gpus"]) == 2
    assert topo["node1_gpus"][0]["vendor"] == "NVIDIA"
    assert topo["node1_gpus"][1]["vendor"] == "AMD"


def test_dual_gpu_model_partitions():
    # 1. loom-sovereign (32B) -> 100% in VRAM, 38 layers on 3060, 26 on RX 580
    part_32b = ClothOSDualGPURunner.get_partition("loom-sovereign")
    assert part_32b is not None
    assert part_32b.total_layers == 64
    assert part_32b.gpu0_layers == 38
    assert part_32b.gpu1_layers == 26
    assert part_32b.in_vram_pct == 100.0
    assert part_32b.split_ratio_str == "59:41 (12GB : 8GB)"

    # 2. loom-sovereign-70b (70B) -> Tri-GPU Mesh
    part_70b = ClothOSDualGPURunner.get_partition("loom-sovereign-70b")
    assert part_70b is not None
    assert part_70b.total_layers == 80
    assert part_70b.gpu0_layers == 22
    assert part_70b.gpu1_layers == 15
    assert part_70b.node2_apu_layers == 20
    assert part_70b.sys_ram_layers == 23
    assert part_70b.in_vram_pct == 71.2

    # 3. loom-coder (7B)
    part_coder = ClothOSDualGPURunner.get_partition("loom-coder")
    assert part_coder is not None
    assert part_coder.gpu0_layers == 28
    assert part_coder.gpu1_layers == 0
    assert part_coder.in_vram_pct == 100.0

    # 4. Fallback matching
    assert ClothOSDualGPURunner.get_partition("32b") == part_32b
    assert ClothOSDualGPURunner.get_partition("fast") is not None


def test_vulkan_launch_command_generation():
    res = ClothOSDualGPURunner.generate_vulkan_launch_command("loom-sovereign", port=8002)
    assert res["success"] is True
    assert res["port"] == 8002
    assert "--split-mode layer" in res["command"]
    assert "--tensor-split 60,40" in res["command"]
    assert "-ngl 64" in res["command"]


# ==============================================================================
# FabricWorkloadOptimizer Test Suite
# ==============================================================================

def test_fabric_optimizer_silicon_and_link_discovery():
    FabricWorkloadOptimizer.initialize()
    components = FabricWorkloadOptimizer._components
    links = FabricWorkloadOptimizer._links
    assert len(components) >= 6
    assert "node1_rtx3060" in components
    assert "node1_rx580" in components
    assert "node2_apu" in components
    assert "systolic_tpu" in components

    # Verify high-speed PCIe and LAN links
    assert ("node1", "node1") in links
    assert links[("node1", "node1")].bandwidth_mb_per_sec == 15800.0
    assert ("node1", "node2") in links
    assert links[("node1", "node2")].bandwidth_mb_per_sec == 285.0


def test_fabric_optimizer_routing_decisions():
    # 1. Heavy compute task originating on Node 2
    # Should offload to idle high-speed silicon on Node 1 (RTX 3060 or RX 580)
    decision = FabricWorkloadOptimizer.solve_optimal_delegation(
        task_name="Heavy Matrix Factorization",
        estimated_ops=50_000_000_000,  # 50 GFLOPS
        payload_bytes=100_000,         # 100 KB
        required_vram_mb=500.0,
        origin_node="node2",
    )
    assert decision.assigned_node == "node1"
    assert decision.strategy in ["REMOTE_IDLE_OFFLOAD", "LOCAL_GPU_OFFLOAD"]
    assert decision.speedup_vs_local > 1.0

    # 2. Ultra-light task on Node 2 should stay local to avoid transit latency
    decision_tiny = FabricWorkloadOptimizer.solve_optimal_delegation(
        task_name="Tiny Scalar Increment",
        estimated_ops=100,
        payload_bytes=10,
        required_vram_mb=1.0,
        origin_node="node2",
    )
    assert decision_tiny.strategy in ["LOCAL_IMMEDIATE", "LOCAL_FALLBACK"]
    assert decision_tiny.assigned_node == "node2"


# ==============================================================================
# CrystallizedKnowledgeEngine Test Suite
# ==============================================================================

def test_crystallized_engine_builtins_and_zero_token_execution():
    CrystallizedKnowledgeEngine.initialize()

    # 1. Fibonacci
    res_fib = CrystallizedKnowledgeEngine.execute_kernel("calc_matrix_fibonacci", None, 10)
    assert res_fib == 55

    # 2. Shannon Entropy
    res_entropy = CrystallizedKnowledgeEngine.execute_kernel("calc_shannon_entropy", None, [0.5, 0.5])
    assert math.isclose(res_entropy, 1.0, rel_tol=1e-5)

    # 3. Tensor Bandwidth Splits
    res_splits = CrystallizedKnowledgeEngine.execute_kernel(
        "calc_tensor_bandwidth_splits",
        None,
        {"rtx3060": 360.0, "rx580": 224.0, "apu": 50.0},
    )
    assert len(res_splits) == 3
    assert math.isclose(sum(res_splits.values()), 1.0, rel_tol=1e-4)


def test_crystallized_engine_skill_compilation():
    CrystallizedKnowledgeEngine.initialize()

    code = """def compute_determinant_2x2(a: float, b: float, c: float, d: float) -> float:
    return a * d - b * c
"""
    test_code = """def test_kernel():
    assert compute_determinant_2x2(1, 2, 3, 4) == -2.0
    assert compute_determinant_2x2(2, 0, 0, 2) == 4.0
"""
    ok, msg, kernel = CrystallizedKnowledgeEngine.crystallize_skill(
        kernel_id="calc_det_2x2",
        name="2x2 Determinant",
        category="MATH",
        description="Determinant of a 2x2 matrix",
        python_code=code,
        unit_test_code=test_code,
    )
    assert ok is True
    assert kernel is not None

    # Execute newly crystallized kernel
    res = CrystallizedKnowledgeEngine.execute_kernel("calc_det_2x2", None, 5.0, 2.0, 1.0, 3.0)
    assert res == 13.0


# ==============================================================================
# SkillEvolver Test Suite (TDSA)
# ==============================================================================

def test_skill_evolver_tdsa_ratchet_and_rejection():
    SkillEvolver.initialize()

    # 1. Create candidate skill
    test_skill_id = "test_vector_norm"
    test_skill = ClothOSSkill(
        skill_id=test_skill_id,
        name="Vector Euclidean Norm",
        version="1.0.0",
        domain="MATH",
        description="Computes euclidean norm",
        principles=["Use sum of squares"],
        code_templates={"norm": "def vector_norm(v):\n    return sum(x**2 for x in v) ** 0.5\n"},
        verification_test="def test_norm():\n    assert vector_norm([3, 4]) == 5.0\n",
    )
    SkillEvolver.save_skill(test_skill)

    # 2. Attempt bad update -> Should be REJECTED by unit test gate
    bad_templates = {"norm": "def vector_norm(v):\n    return sum(v) # WRONG\n"}
    bad_test = "assert vector_norm([3, 4]) == 5.0"
    ok, msg, updated = SkillEvolver.improve_skill_with_unit_test(
        skill_id=test_skill_id,
        proposed_principles=["Wrong approach"],
        proposed_code_templates=bad_templates,
        unit_test_code=bad_test,
    )
    assert ok is False
    assert "GATE REJECTED" in msg
    assert updated is None

    # Verify version did not change
    persisted = SkillEvolver.get_skill(test_skill_id)
    assert persisted.version == "1.0.0"

    # 3. Attempt good update with math.hypot -> Should PASS and ratchet version to 1.1.0
    good_templates = {"norm": "import math\ndef vector_norm(v):\n    return math.hypot(*v)\n"}
    good_test = "assert math.isclose(vector_norm([3, 4]), 5.0)"
    ok_good, msg_good, updated_good = SkillEvolver.improve_skill_with_unit_test(
        skill_id=test_skill_id,
        proposed_principles=["Use math.hypot for numerical stability"],
        proposed_code_templates=good_templates,
        unit_test_code=good_test,
    )
    assert ok_good is True
    assert "GATE PASSED" in msg_good
    assert updated_good is not None
    assert updated_good.version == "1.1.0"
