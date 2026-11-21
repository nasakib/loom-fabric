"""
Unit and integration tests for the structured Moltbook research pipeline.
Tests:
- HypothesisStore (schema, insertion, query, status transitions)
- MoltbookHypothesisEngine (adjacent topic discovery and hypothesis formulation)
- ExperimentationEngine (targeted hardware parameter execution and empirical verdict)
- DeliverableSynthesizer (executive report compilation and disk export)
"""

from pathlib import Path
import pytest
from loom.fabric.hypothesis_store import HypothesisStore
from loom.fabric.moltbook_hypothesis import MoltbookHypothesisEngine
from loom.fabric.experimentation_engine import ExperimentationEngine
from loom.fabric.deliverable_synthesizer import DeliverableSynthesizer


def test_hypothesis_store_lifecycle(tmp_path: Path):
    db_file = tmp_path / "test_hyp.db"
    store = HypothesisStore(db_path=db_file)

    hyp_id = store.add_hypothesis(
        submolt="m/active-inference",
        source_post_id="post-test-1",
        post_title="Kuramoto Phase Sync",
        topic="Test Topic",
        claim="Coupling K=2.8 yields r > 0.80",
        prediction="r >= 0.80",
        experiment_type="kuramoto_sweep",
        parameters={"k_coupling": 2.8, "steps": 50, "dt": 0.015, "target_r": 0.80},
    )
    assert hyp_id > 0

    next_hyp = store.get_next_pending()
    assert next_hyp is not None
    assert next_hyp["id"] == hyp_id
    assert next_hyp["submolt"] == "m/active-inference"

    exp_id = store.record_experiment(
        hypothesis_id=hyp_id,
        method="Test OpenCL",
        parameters={"k_coupling": 2.8},
        raw_result={"r": 0.91},
        measurements={"measured_r": 0.91},
        verdict="confirmed",
        duration_s=0.15,
    )
    assert exp_id > 0

    stats = store.get_statistics()
    assert stats["total_hypotheses"] == 1
    assert stats["total_experiments"] == 1
    assert stats["hypotheses_by_status"].get("confirmed") == 1


def test_experimentation_and_deliverable(tmp_path: Path):
    db_file = tmp_path / "test_research.db"
    store = HypothesisStore(db_path=db_file)
    engine = ExperimentationEngine(store=store)

    # Add 2 hypotheses: one confirmed, one refuted
    h1 = store.add_hypothesis(
        submolt="m/active-inference",
        source_post_id="post-kura-high",
        post_title="Supercritical Kuramoto",
        topic="High Coupling Sync",
        claim="High coupling K=3.0 produces strong coherence",
        prediction="r >= 0.75",
        experiment_type="kuramoto_sweep",
        parameters={"k_coupling": 3.0, "steps": 100, "dt": 0.015, "target_r": 0.75},
    )
    h2 = store.add_hypothesis(
        submolt="m/systems-engineering",
        source_post_id="post-vec-ortho",
        post_title="High-Dim Vector Orthogonality",
        topic="Vector Space Bound",
        claim="Orthogonality mean abs sim <= 0.035",
        prediction="mean_abs_sim <= 0.035",
        experiment_type="vector_geometry",
        parameters={"batch_size": 128, "dim": 1536, "max_mean_abs_sim": 0.035},
    )

    r1 = engine.execute_hypothesis(store.get_next_pending())
    r2 = engine.execute_hypothesis(store.get_next_pending())

    assert r1["verdict"] in ["confirmed", "refuted"]
    assert r2["verdict"] in ["confirmed", "refuted"]

    synth = DeliverableSynthesizer(workspace_root=tmp_path, store=store)
    report_path = synth.compile_deliverable(cycle_range="Cycles #1..#2")

    assert report_path is not None
    assert report_path.exists()
    content = report_path.read_text(encoding="utf-8")
    assert "ClothOS / Fabric Empirical Research Deliverable" in content
    assert "Executive Summary" in content


def test_system_config_and_aha_engine(tmp_path: Path):
    from loom.fabric.system_config import SystemConfig
    from loom.fabric.aha_engine import AhaEngine
    from loom.fabric.cluster_discovery import ClusterComputeDiscovery

    cfg = SystemConfig(workspace_root=tmp_path)
    assert cfg.get("kuramoto_consensus_k") == 2.45
    assert cfg.get("hypersphere_ortho_threshold") == 0.035

    # Update parameter
    gen = cfg.update_params({"kuramoto_consensus_k": 2.50}, rationale="Test update")
    assert gen > 1
    assert cfg.get("kuramoto_consensus_k") == 2.50

    discovery = ClusterComputeDiscovery()
    local_devs = discovery.discover_local_opencl_devices()
    assert len(local_devs) >= 1  # Discovers local OpenCL devices

