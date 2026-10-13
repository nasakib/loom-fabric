# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
Comprehensive tests for Sovereign Precision Tooling Suite:
Torque, Ratchet, Wrench, Drill, Vise, Lathe, Caliper, Chisel, Tap & Die, Winch.
"""

import numpy as np
import pytest
from pydantic import BaseModel

from loom.tools.caliper import CaliperGauge
from loom.tools.chisel import ChiselAblator
from loom.tools.drill import DrillInspector
from loom.tools.lathe import LatheShaper
from loom.tools.ratchet import RatchetEngine
from loom.tools.tap_die import TapDieThreader
from loom.tools.toolbox import SovereignToolbox
from loom.tools.vise import ViseLock
from loom.tools.winch import WinchHoist
from loom.tools.wrench import WrenchCoupler


class SampleRigidModel(BaseModel, frozen=True):
    name: str
    confidence: float


def test_ratchet_monotonicity(tmp_path):
    engine = RatchetEngine(
        workspace_root=tmp_path,
        ledger_file=tmp_path / "test_ratchet.json",
        home_ledger=tmp_path / "test_home_ratchet.json",
    )

    # 1. Click forward
    assert engine.click("AX_101", "Invariant 101", "proof_payload_101", 0.95) is True
    assert engine.tooth_count == 1
    assert "AX_101" in engine.axioms

    # 2. Monotonicity: cannot overwrite or regress
    assert engine.click("AX_101", "Mutated 101", "bad_payload", 0.99) is False
    assert engine.tooth_count == 1

    # 3. Thermodynamic diode: reject free energy increase
    assert engine.free_energy_diode(delta_free_energy=-0.5, delta_coherence=0.1) is True
    assert engine.free_energy_diode(delta_free_energy=1.2, delta_coherence=-0.4) is False

    # 4. Preemption catch
    engine.catch_file = tmp_path / "test_catch.json"
    snap_id = engine.preemption_catch(cycle=42, oscillator_offset=1024, payload={"test": True})
    assert snap_id.startswith("snap-")
    restored = engine.release_catch()
    assert restored is not None
    assert restored.cycle == 42
    assert restored.oscillator_offset == 1024


def test_wrench_coupling():
    wrench = WrenchCoupler()

    # 1. Tighten schema with loose/extra keys
    raw = {"name": "CoupledJoint", "confidence": 0.99, "extra_hallucination": "delete_me"}
    rigid = wrench.tighten_schema(raw, SampleRigidModel)
    assert isinstance(rigid, SampleRigidModel)
    assert rigid.name == "CoupledJoint"
    assert rigid.confidence == 0.99

    # 2. Clamped temperature
    assert wrench.clamp_temperature("formal_proof") == 0.0
    assert wrench.clamp_temperature("creative_poetry") == 0.7

    # 3. Torque joint
    joint = wrench.torque_joint({"total_cycles_completed": 100}, {"invariants_mined_node2": 95})
    assert joint["joint_tight"] is True
    assert joint["synchronization_skew"] == 5


def test_drill_vertical_trace():
    drill = DrillInspector()
    trace = drill.bore_vertical_trace("Prove Fourier symmetry over L2 space")
    assert trace["depth_layers_count"] == 5
    assert trace["silicon_enclave_reached"] is True

    probe = drill.probe_proof_depth("AXIOM_FOURIER_01", max_depth=4)
    assert probe["drilled_depth"] == 4
    assert probe["status"] == "VALIDATED_AT_DEPTH"


def test_vise_workholding():
    vise = ViseLock()

    # Context manager locking
    with vise.clamp("AST_NODE_CORE", timeout_sec=1.0):
        assert "AST_NODE_CORE" in vise._held_resources

    assert "AST_NODE_CORE" not in vise._held_resources
    assert vise.clamps_executed == 1

    pmp = vise.lock_pmp_napot()
    assert pmp["pmp_csr"] == "0x9B"
    assert pmp["clamped"] is True


def test_lathe_shaping():
    lathe = LatheShaper()

    # 1. Turn embeddings onto unitary hypersphere
    raw_vecs = np.array([[3.0, 4.0, 0.0], [1.0, 2.0, 3.0], [5.0, 1.0, 2.0]], dtype=np.float32)
    turned = lathe.turn_embeddings(raw_vecs, target_dim=3)
    norms = np.linalg.norm(turned, axis=-1)
    assert np.allclose(norms, 1.0, atol=1e-5)

    # 2. Balance Kuramoto oscillators
    phases = np.array([0.1, 0.12, 0.09, 0.11], dtype=np.float32)
    bal = lathe.balance_kuramoto_oscillators(phases)
    assert bal["is_synchronized"] is True
    assert bal["coherence_order_parameter_r"] > 0.99


def test_caliper_metrology():
    caliper = CaliperGauge()

    # Error margin
    m_pass = caliper.measure_error_margin([1.0, 0.0], [1.0, 0.00005], epsilon=1e-4)
    assert m_pass["within_tolerance"] is True
    assert m_pass["metrology_grade"] == "VERIFIED_MICRON"

    m_fail = caliper.measure_error_margin([1.0, 0.0], [1.0, 0.05], epsilon=1e-4)
    assert m_fail["within_tolerance"] is False

    # Entropy gauge
    ent_crisp = caliper.gauge_routing_entropy([0.98, 0.02])
    assert ent_crisp["decision_grade"] == "CRISP_DETERMINISTIC"

    ent_diff = caliper.gauge_routing_entropy([0.25, 0.25, 0.25, 0.25])
    assert ent_diff["requires_torque_escalation"] is True

    # PII purity
    pure = caliper.verify_pii_purity("Normal text with internal node 192.168.99.1:8002")
    assert pure["is_pure"] is True


def test_chisel_ablation():
    chisel = ChiselAblator()

    # Context ablation
    text = (
        "Sure, I understand. Here is the theorem:\n"
        "Theorem 1: Invariant holds.\n"
        "```python\nx = 1\n```\n"
        "Certainly, let me know if you need anything else."
    )
    ablated = chisel.ablate_context(text, max_chars=120)
    assert "Theorem 1:" in ablated
    assert "x = 1" in ablated

    # AST slicing
    code = (
        "def compute_foo():\n"
        "    return 42\n\n"
        "def compute_bar():\n"
        "    return 99\n"
    )
    sliced = chisel.slice_ast_definition(code, "compute_bar")
    assert sliced is not None
    assert "def compute_bar():" in sliced
    assert "return 99" in sliced


def test_tap_die_protocol_framing():
    td = TapDieThreader()

    endpoint = td.tap_socket_endpoint("127.0.0.1", 5559)
    assert endpoint == "tcp://127.0.0.1:5559"

    framed = td.die_payload({"action": "RATIFIED", "cycle": 375}, topic="clothos.axioms")
    ok, topic, data = td.verify_and_unwrap(framed)
    assert ok is True
    assert topic == "clothos.axioms"
    assert data["action"] == "RATIFIED"
    assert data["cycle"] == 375


def test_winch_hoisting():
    winch = WinchHoist()

    adv = winch.calculate_mechanical_advantage("tier_0_edge_cpu", "tier_2_distributed")
    assert adv == 16.0

    hoist = winch.hoist_workload("task-smt-99", {"matrix": [1, 2, 3]}, source_tier="tier_0_edge_cpu", target_tier="tier_1_local_rapid")
    assert hoist["mechanical_advantage"] == 4.5
    assert hoist["cable_status"] == "TENSIONED_ELEVATED"

    spooled = winch.spool_down("task-smt-99", {"result": "PROVED"})
    assert spooled["cable_status"] == "SPOOLED_REST"
    assert spooled["result"]["result"] == "PROVED"


def test_hammer_forge_and_impulse():
    from loom.tools.hammer import HammerForge
    hammer = HammerForge()

    # 1. Weight Forge: INT4 and BitNet ternary cold-forging
    weights = np.random.normal(loc=0.0, scale=1.0, size=(64, 64)).astype(np.float32)
    forged_int4 = hammer.forge(weights, bits=4, tensor_id="tensor_fc1")
    assert forged_int4.bits == 4
    assert forged_int4.compression_ratio >= 7.0
    assert forged_int4.frobenius_error < 0.25

    forged_ternary = hammer.forge(weights, bits=2, tensor_id="tensor_fc2")
    assert forged_ternary.bits == 2
    assert forged_ternary.compression_ratio >= 15.0

    # 2. Riveter: Permanent silicon PMP hardware lock
    seal = hammer.rivet("AXIOM_FOURIER_CONVERGENCE", {"theorem": "r >= 0.80", "proof": "SMT_OK"})
    assert seal.hardware_csr == "pmpcfg0[7:7]=LOCKED(1)"
    assert seal.immutable is True
    # Verify idempotency / irrevocability
    seal_dup = hammer.rivet("AXIOM_FOURIER_CONVERGENCE", {"new": "data"})
    assert seal_dup.rivet_id == seal.rivet_id
    assert hammer.get_rivet("AXIOM_FOURIER_CONVERGENCE") is not None

    # 3. The Sledge: Deadlock smashing
    smash = hammer.smash_deadlock("gpu_stream_mutex_0")
    assert smash.deadlock_broken is True
    assert smash.impulse_magnitude > 1000.0

    # 4. Dead-Blow: Stochastic kinetic shock without ringing
    phases = np.array([0.5, 0.5, 0.51, 0.49], dtype=np.float64)
    shock = hammer.dead_blow(phases, impulse_scale=0.2, damping=0.98)
    assert shock.escaped_local_minimum is True
    assert shock.residual_ringing_energy < 0.05

    # 5. Ball-Peen: Memory bus stress test
    stress = hammer.peen_stress_test(buffer_size_bytes=65536, cycles=20)
    assert stress.integrity_verified is True
    assert stress.bit_flips_detected == 0

    assert hammer.forged_tensors_count == 2
    assert hammer.rivets_driven == 1
    assert hammer.deadlocks_smashed == 1
    assert hammer.dead_blow_strikes == 1
    assert hammer.peen_tests_conducted == 1


def test_sovereign_toolbox_unified():
    box = SovereignToolbox()
    status = box.get_full_tooling_status()

    expected_tools = [
        "torque",
        "ratchet",
        "wrench",
        "drill",
        "vise",
        "lathe",
        "caliper",
        "chisel",
        "tap_die",
        "winch",
        "hammer",
    ]
    for t in expected_tools:
        assert t in status
        assert isinstance(status[t], dict)
