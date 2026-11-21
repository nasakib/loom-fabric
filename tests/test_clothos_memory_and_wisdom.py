# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
Comprehensive Unit Tests for ClothOS Memory Continuum, Salience Engine, and Wisdom Engine.

Tests:
1. Episodic memory storage, retrieval, and serialization
2. Semantic memory associative retrieval via hypervectors
3. Salience scoring across fiduciary, safety, epistemic, and thermodynamic weights
4. Temporal salience decay and reinforcement
5. Wisdom Engine invariant extraction and axiom ratification
6. Unitary complex plane rotation (intelligent forgetting) and Hermitian adjoint restoration
7. Autonomous self-evolution iteration with cognitive loop.
"""

import math
import pytest
import time

from loom.clothos.memory_continuum import memory_continuum
from loom.clothos.salience_engine import salience_engine
from loom.clothos.wisdom_engine import wisdom_engine
from loom.clothos.self_evolution import AutonomousSelfEvolutionEngine


class TestClothOSMemoryAndWisdom:
    def test_episodic_memory_recording(self):
        rec = memory_continuum.record_episodic_event(
            category="EXPERIMENT",
            summary="Unit test trajectory planning validation",
            details={"step": 1, "status": "OK"},
            salience=0.85,
        )
        assert rec.event_id in memory_continuum.episodic_store
        assert rec.salience_score == 0.85
        assert rec.summary == "Unit test trajectory planning validation"

    def test_semantic_associative_recall(self):
        recalled = memory_continuum.recall_semantic("human life safety preemption", top_k=2)
        assert len(recalled) > 0
        top_concept, sim = recalled[0]
        assert top_concept.domain in ("ETHICS", "ROBOTICS", "KERNEL", "CLUSTER", "THERMODYNAMICS")
        assert sim is not None

    def test_salience_scoring_and_weights(self):
        # High-fiduciary, high-safety event
        profile = salience_engine.compute_salience(
            entity_id="TEST-ENT-001",
            fiduciary=1.0,
            safety=1.0,
            epistemic=0.5,
            thermo=0.5,
        )
        # Expected: 0.35*1 + 0.25*1 + 0.25*0.5 + 0.15*0.5 = 0.35 + 0.25 + 0.125 + 0.075 = 0.80
        assert math.isclose(profile.composite_salience, 0.80, abs_tol=0.01)
        assert salience_engine.is_eligible_for_wisdom("TEST-ENT-001") is True

    def test_salience_reinforcement(self):
        salience_engine.compute_salience("TEST-ENT-002", 0.5, 0.5, 0.5, 0.5)
        before = salience_engine.get_decayed_salience("TEST-ENT-002")
        reinforced = salience_engine.reinforce("TEST-ENT-002", bonus=0.20)
        assert reinforced > before

    def test_wisdom_engine_foundational_axioms(self):
        summary = wisdom_engine.get_wisdom_summary()
        assert summary["total_axioms_count"] >= 4
        assert "Microsecond Preemption Invariant" in summary["foundational_axioms"]
        assert "Zero Malignancy Invariant" in summary["foundational_axioms"]

    def test_unitary_complex_plane_rotation_and_restoration(self):
        mock_rec = {"id": "TEST-ROT-001", "salience_score": 0.88, "data": "trace"}
        rot = wisdom_engine.rotate_into_orthogonal_nullspace("TEST-ROT-001", mock_rec)
        assert math.isclose(rot.rotation_angle_rad, math.pi / 2.0, abs_tol=0.001)
        assert rot.status == "DORMANT_ORTHOGONAL"
        assert rot.real_projection_after < 0.01
        assert "TEST-ROT-001" in wisdom_engine.rotated_nullspace

        # Restore via Hermitian adjoint
        restored = wisdom_engine.restore_from_nullspace("TEST-ROT-001")
        assert restored is not None
        assert restored["salience_score"] == 0.88
        assert "TEST-ROT-001" not in wisdom_engine.rotated_nullspace

    def test_autonomous_evolution_cycle_with_cognitive_loop(self):
        engine = AutonomousSelfEvolutionEngine()
        iteration = engine.run_evolution_cycle(iteration_num=99)
        assert iteration.ending_sci >= 90.0
        assert iteration.tests_passed >= 1
        assert iteration.tests_failed == 0
        assert any("Recorded episodic memory" in a for a in iteration.actions_taken)
