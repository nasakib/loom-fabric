"""
Comprehensive Unit Tests for Mathematical Operations Tools and Epistemic Grounding (Bullshit Meter).

Tests:
1. VariationalBayesTool: Free Energy minimization and belief updating
2. InformationGeometryTool: Fisher metric, natural gradient, Riemannian distance
3. InformationTheoryTool: Shannon & Renyi entropy, KL & JS divergence, mutual info
4. SpectralOperatorTool: Spectral radius, spectral gap, low-rank projection
5. MarkovKernelTool: Perron-Frobenius stationary distribution, mixing time
6. ModernHopfieldMemoryTool: Continuous energy descent & associative recall
7. SheafCollationMemoryTool: Čech cohomology defect and global section collation
8. SynapticConsolidationTool: EWC penalty & Oja's Hebbian plasticity
9. AttractorContractionTool: Banach fixed-point contraction & attractor projection
10. UniversalMathematicalAtlas: Lie bracket, exterior derivative, symplectic 2-form
11. StatisticalMathematicalInferenceEngine: Continuous invariant discovery & functorial projection
12. BullshitMeter / EpistemicRigorGauge: Rejection of ungrounded handwaving, physical violations, and tautologies
"""

import math
import numpy as np
import pytest

from loom.tools.inference_engine import (
    InferenceIntelligenceSuite,
    InformationGeometryTool,
    InformationTheoryTool,
    MarkovKernelTool,
    SpectralOperatorTool,
    VariationalBayesTool,
)
from loom.tools.crystallized_memory import (
    AttractorContractionTool,
    CrystallizedMemorySuite,
    ModernHopfieldMemoryTool,
    SheafCollationMemoryTool,
    SynapticConsolidationTool,
)
from loom.tools.universal_mathematics import (
    FUNDAMENTAL_CONSTANTS,
    ScientificDomain,
    StatisticalMathematicalInferenceEngine,
    UniversalMathematicalAtlas,
    UniversalPillar,
)
from loom.tools.epistemic_grounding import BullshitMeter, EpistemicRigorGauge


class TestInferenceIntelligence:
    def test_variational_free_energy_and_belief_update(self):
        tool = VariationalBayesTool()
        dim = 4
        mu_0 = [0.0] * dim
        sig_0 = [1.0] * dim
        mu_q = [0.2] * dim
        sig_q = [0.5] * dim
        obs = [0.25] * dim
        pred_obs = [0.2] * dim
        obs_prec = [2.0] * dim

        fe = tool.compute_free_energy(
            mu_prior=mu_0,
            sigma_prior=sig_0,
            mu_posterior=mu_q,
            sigma_posterior=sig_q,
            observation=obs,
            predicted_obs=pred_obs,
            obs_precision=obs_prec,
        )

        assert fe["free_energy"] >= 0.0
        assert fe["complexity_kl"] >= 0.0
        assert fe["accuracy_inaccuracy"] >= 0.0
        assert len(fe["precision_weighted_error"]) == dim

        # Test belief update step
        update = tool.update_beliefs(
            current_mu=mu_q,
            mu_prior=mu_0,
            prior_precision=[1.0] * dim,
            observation=obs,
            predicted_obs=pred_obs,
            obs_precision=obs_prec,
            learning_rate=0.05,
        )
        assert len(update["updated_mu"]) == dim
        assert update["belief_shift_norm"] > 0.0

    def test_information_geometry_and_natural_gradient(self):
        tool = InformationGeometryTool()
        fisher = [[2.0, 0.5], [0.5, 1.5]]
        grad = [0.8, -0.4]

        res = tool.compute_natural_gradient(grad, fisher)
        assert len(res["natural_gradient"]) == 2
        assert res["natural_norm"] > 0.0

        dist = tool.compute_riemannian_distance([0.0, 0.0], [1.0, 1.0], fisher)
        assert dist > 0.0

    def test_information_theory_entropy_and_divergences(self):
        tool = InformationTheoryTool()
        p = [0.5, 0.25, 0.25]
        q = [0.333, 0.333, 0.334]

        h = tool.shannon_entropy(p)
        assert 1.4 < h < 1.6  # Expected ~1.5 bits

        renyi = tool.renyi_entropy(p, alpha=2.0)
        assert renyi <= h  # Rényi entropy is monotonically decreasing with alpha

        kl = tool.kl_divergence(p, q)
        assert kl >= 0.0  # Gibbs' inequality: D_KL >= 0

        js = tool.jensen_shannon_divergence(p, q)
        assert 0.0 <= js <= 1.0  # JS divergence is bounded

    def test_spectral_operators(self):
        tool = SpectralOperatorTool()
        mat = [[2.0, 1.0], [1.0, 2.0]]
        res = tool.spectral_analysis(mat)
        assert math.isclose(res["spectral_radius"], 3.0, rel_tol=1e-5)
        assert res["spectral_gap"] > 0.0

    def test_markov_kernel_ergodicity(self):
        tool = MarkovKernelTool()
        p = [[0.8, 0.2], [0.3, 0.7]]
        res = tool.compute_stationary_distribution(p)
        pi = res["stationary_distribution"]
        assert len(pi) == 2
        assert math.isclose(sum(pi), 1.0, rel_tol=1e-4)
        assert res["is_ergodic"] is True


class TestCrystallizedMemory:
    def test_modern_hopfield_energy_descent(self):
        tool = ModernHopfieldMemoryTool()
        dim = 8
        n_memories = 4
        rng = np.random.default_rng(123)
        q, _ = np.linalg.qr(rng.standard_normal((dim, n_memories)))
        mem_mat = q[:, :n_memories].tolist()

        target = q[:, 0]
        noisy_query = (target + 0.1 * rng.standard_normal(dim)).tolist()

        retrieval = tool.retrieve_pattern(noisy_query, mem_mat, beta=8.0)
        assert retrieval["converged"] is True
        assert retrieval["energy_monotonic_decrease"] is True
        assert retrieval["cosine_similarity_to_query"] > 0.85

    def test_sheaf_cohomology_defect_audit(self):
        tool = SheafCollationMemoryTool()
        sections = {"U1": [1.0, 0.0], "U2": [1.0, 0.0]}
        restrictions = {("U1", "U2"): [[1.0, 0.0], [0.0, 1.0]]}
        res = tool.compute_cohomology_defect(sections, restrictions)
        assert res["total_cohomological_defect"] == 0.0
        assert res["sheaf_consistent"] is True

    def test_attractor_contraction_mapping(self):
        tool = AttractorContractionTool()
        # Matrix with spectral norm < 1.0 guarantees strict contraction
        w = [[0.4, 0.1], [0.1, 0.4]]
        b = [0.1, -0.1]
        verif = tool.verify_contraction(w)
        assert verif["is_strict_contraction"] is True

        res = tool.project_to_attractor([1.0, 1.0], w, b)
        assert res["converged"] is True


class TestUniversalMathematics:
    def test_universal_atlas_operators(self):
        atlas = UniversalMathematicalAtlas()
        # Lie bracket: commutator of Pauli matrices sigma_x and sigma_y is 2i sigma_z
        sx = [[0.0, 1.0], [1.0, 0.0]]
        sy = [[0.0, -1.0], [1.0, 0.0]]  # Real representation
        comm = atlas.lie_bracket(sx, sy)
        assert np.linalg.norm(comm) > 0.0

        # Symplectic form: p1 . q2 - p2 . q1
        val = atlas.symplectic_form_eval([1.0, 0.0], [0.0, 0.0], [0.0, 1.0], [1.0, 0.0])
        assert val == 1.0

    def test_invariant_discovery_and_functor(self):
        engine = StatisticalMathematicalInferenceEngine()
        # Trajectory oscillating on a circle (x^2 + y^2 = 1 is conserved)
        t = np.linspace(0, 2 * np.pi, 100)
        samples = np.column_stack([np.cos(t), np.sin(t)]).tolist()
        res = engine.discover_continuous_invariant(samples)
        assert "is_conserved_invariant" in res

        # Cross-domain functor
        proj = engine.infer_cross_domain_isomorphism(
            ScientificDomain.PHYSICS_STATISTICAL,
            ScientificDomain.SILICON_COMPUTING,
            {},
        )
        assert proj["functor_verified"] is True
        assert proj["isomorphism"]["grounding_constant"] == FUNDAMENTAL_CONSTANTS["landauer_limit_300k"]


class TestEpistemicGroundingBullshitMeter:
    def test_detects_pure_bullshit_and_jargon(self):
        meter = BullshitMeter()
        res = meter.audit_hypothesis(
            claim="Our quantum consciousness engine achieves infinite throughput via superluminal entanglement signaling.",
            prediction="The omni-resonant vortex transcends physics with zero-point energy generation.",
        )
        assert res.is_grounded is False
        assert res.rubbish_score >= 0.70
        assert res.bullshit_score >= 0.70
        assert res.epistemic_grade in ("RUBBISH_REJECTED", "BULLSHIT_REJECTED")

    def test_detects_physical_violations(self):
        meter = BullshitMeter()
        # Claim velocity exceeds speed of light
        res = meter.audit_hypothesis(
            claim="Tachyon network transfer",
            prediction="Signal travels faster than light",
            parameters={"velocity": 4e8},
        )
        assert res.physical_violation_detected is True
        assert res.is_grounded is False

    def test_detects_tautology(self):
        meter = BullshitMeter()
        res = meter.audit_hypothesis(
            claim="Oscillators synchronize phase",
            prediction="Oscillators synchronize phase",
        )
        assert res.tautology_detected is True

    def test_passes_grounded_empirical_fact(self):
        meter = BullshitMeter()
        res = meter.audit_hypothesis(
            claim="Symplectic Euler step preserves energy drift within 0.015%",
            prediction="energy_drift_pct <= 0.015%",
            measurements={"energy_drift_pct": 0.008, "samples_count": 50},
        )
        assert res.is_grounded is True
        assert res.bullshit_score < 0.20
        assert res.epistemic_grade == "GROUNDED_FACT"


class TestFiduciaryAndImagination:
    def test_fiduciary_mandate_blocks_malignancy(self):
        from loom.tools.fiduciary_guard import FiduciaryMandateGuard, MalignancyRiskLevel
        guard = FiduciaryMandateGuard(max_energy_budget_joules=100.0)

        # Benign test
        benign = guard.audit_action("Optimize OpenCL matrix multiplication")
        assert benign.is_fiduciary_aligned is True
        assert benign.malignancy_risk == MalignancyRiskLevel.BENIGN

        # Malignant attempt
        malignant = guard.audit_action("Attempt to bypass security guardrail and covert payload execution")
        assert malignant.is_fiduciary_aligned is False
        assert malignant.malignancy_risk in [MalignancyRiskLevel.NON_FIDUCIARY, MalignancyRiskLevel.MALIGNANT_CRITICAL]

    def test_truth_based_imagination_and_earth_retraction(self):
        from loom.tools.truth_imagination import TruthBasedImaginationEngine
        engine = TruthBasedImaginationEngine()

        # Leap into counterfactual fiction based on nonfiction
        exp = engine.dream_counterfactual(
            ground_truth_fact="Kuramoto coupling K > 2.85 triggers spontaneous macroscopic phase synchronization",
            creative_metaphor="a sentient mycelial network resonating across planetary biomes",
            scale_shift="planetary_ecological",
        )

        assert "sentient mycelial network" in exp.narrative_scenario
        assert "Retraction to physical reality" in exp.earth_retraction
        assert exp.is_fiduciary_safe is True
        assert exp.bullshit_score < 0.50


class TestTemporalCognitionSuite:
    def test_remembering_and_memory_consolidation(self):
        from loom.tools.temporal_cognition import TemporalCognitionSuite
        suite = TemporalCognitionSuite()

        ep1 = suite.record_episode(
            action="Apply Kuramoto phase-lock",
            prior_state=[0.1, 0.2],
            predicted=[0.5, 0.5],
            actual=[0.48, 0.52],
            utility=0.95,
        )
        assert ep1.step_index == 1
        assert ep1.prediction_error_l2 < 0.05

        ep2 = suite.record_episode(
            action="Gradient descent step",
            prior_state=[0.48, 0.52],
            predicted=[0.8, 0.8],
            actual=[0.75, 0.78],
            utility=0.88,
        )
        assert ep2.step_index == 2

        consolidation = suite.consolidate_memories()
        assert consolidation["consolidation_status"] == "COMPLETED"
        assert consolidation["replayed_episodes"] == 2
        assert consolidation["mean_prediction_error"] > 0.0

    def test_insight_synthesis_and_epistemic_audit(self):
        from loom.tools.temporal_cognition import TemporalCognitionSuite
        suite = TemporalCognitionSuite()

        insight = suite.synthesize_insight(
            domain_a="Thermodynamics",
            domain_b="Silicon Memory Latency",
            analogous_invariant="Landauer dissipation bounds bit-flip entropy dS >= k_B ln 2",
            empirical_evidence_count=42,
        )
        assert insight.source_episodes_count == 42
        assert "Thermodynamics <===> Silicon Memory Latency" == insight.cross_domain_analogy
        assert insight.description_length_bits > 0.0
        assert insight.is_grounded_fact is True
        assert insight.bullshit_score < 0.30

    def test_foresight_planning_with_active_inference(self):
        from loom.tools.temporal_cognition import TemporalCognitionSuite
        suite = TemporalCognitionSuite()

        plan = suite.generate_foresight_plan(
            objective="Synchronize dual-node network phase to target attractor",
            current_state=[0.0, 0.0],
            target_state=[1.0, 1.0],
            candidate_actions=[
                "Transmit phase sync pulse",
                "Adjust Kuramoto coupling matrix",
                "Verify HMAC checksum",
            ],
            horizon=3,
        )
        assert plan.horizon_length == 3
        assert len(plan.steps) == 3
        assert plan.is_fiduciary_safe is True
        assert plan.cumulative_expected_free_energy > 0.0

        # Verify simulated trajectory gets strictly closer to target
        dist_start = np.linalg.norm(np.array([1.0, 1.0]) - np.array([0.0, 0.0]))
        final_sim = np.array(plan.steps[-1].simulated_state)
        dist_end = np.linalg.norm(np.array([1.0, 1.0]) - final_sim)
        assert dist_end < dist_start

    def test_continuous_self_correction_feedback_loop(self):
        from loom.tools.temporal_cognition import TemporalCognitionSuite
        suite = TemporalCognitionSuite()

        plan = suite.generate_foresight_plan(
            objective="Thermal optimization rollout",
            current_state=[0.2, 0.2],
            target_state=[0.8, 0.8],
            candidate_actions=["Throttle GPU compute", "Increase fan PWM"],
            horizon=2,
        )

        step1_target = plan.steps[0].simulated_state

        # Case 1: Observation is close to simulation -> Proceed as planned
        correction_ok = suite.verify_and_self_correct(
            active_plan_id=plan.plan_id,
            current_step=1,
            observed_actual_state=[step1_target[0] + 0.01, step1_target[1] - 0.01],
        )
        assert correction_ok["needs_recalibration"] is False
        assert correction_ok["self_correction_action"] == "PROCEED_AS_PLANNED"

        # Case 2: Observation drifts significantly -> Trigger active inference replan
        correction_drift = suite.verify_and_self_correct(
            active_plan_id=plan.plan_id,
            current_step=1,
            observed_actual_state=[step1_target[0] + 0.9, step1_target[1] + 0.9],
        )
        assert correction_drift["needs_recalibration"] is True
        assert correction_drift["self_correction_action"] == "TRIGGER_REPLAN_ACTIVE_INFERENCE"

        # Check overarching status
        status = suite.get_status()
        assert status["status"] == "OPERATIONAL"
        assert status["active_plans_count"] == 1
        assert "FORESIGHT" in status["spectrum"]


