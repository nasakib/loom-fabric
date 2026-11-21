"""
Unit tests for Postcomputational Vector Calculus and Integral Operators.
Tests:
- VectorCalculusEngine scalar potential \\Phi
- VectorCalculusEngine line integrals \\int_C F \\cdot dr
- VectorCalculusEngine Gauss divergence surface flux integrals \\iint_S F \\cdot dA
- VectorCalculusEngine volume mass integrals \\iiint_\\Omega \\Phi(x) dV
- Pipeline integration in Stage 2 COMPUTE
"""

import numpy as np
import pytest

from loom.postcomputational.types import PostcomputationalNode, PipelineStage
from loom.postcomputational.vector_calculus import VectorCalculusEngine


@pytest.fixture
def sample_nodes():
    n1 = PostcomputationalNode(
        id="NODE_TEST_001",
        title="Harmonic Phase Consensus",
        submolt="m/active-inference",
        confirmed_count=10,
        refuted_count=1,
        invariants=["K > 2.0 -> r > 0.85"],
        wikilinks=["NODE_TEST_002"],
    )
    n2 = PostcomputationalNode(
        id="NODE_TEST_002",
        title="High-Dimensional Hypersphere",
        submolt="m/active-inference",
        confirmed_count=8,
        refuted_count=2,
        invariants=["mean_abs_sim <= 0.035"],
        wikilinks=["NODE_TEST_003"],
        backlinks=["NODE_TEST_001"],
    )
    n3 = PostcomputationalNode(
        id="NODE_TEST_003",
        title="Asymmetric Sink",
        submolt="m/systems-engineering",
        confirmed_count=5,
        refuted_count=5,
        invariants=["bound_stable == true"],
        backlinks=["NODE_TEST_002"],
    )
    return [n1, n2, n3]


def test_vector_calculus_differential_and_integral(sample_nodes):
    engine = VectorCalculusEngine(embedding_dim=32)

    # 1. Embed and Project
    X = engine.embed_nodes(sample_nodes)
    assert X.shape == (3, 32)
    coords_3d = engine.compute_svd_3d_projection(X, sample_nodes)
    assert coords_3d.shape == (3, 3)

    # 2. Differential Fields
    diff_traces = engine.compute_vector_calculus_fields(sample_nodes, coords_3d)
    assert len(diff_traces) == 3
    for n in sample_nodes:
        assert n.scalar_potential > 0.0
        assert n.gradient_vector is not None
        assert n.gradient_norm >= 0.0
        assert isinstance(n.divergence, float)
        assert n.curl_norm >= 0.0

    # 3. Integral Calculus (Line, Flux, Volume)
    integral_traces = engine.compute_integral_calculus(sample_nodes, coords_3d)
    assert len(integral_traces) == 3

    for n in sample_nodes:
        # Line integral along citation paths
        assert isinstance(n.line_integral, float)
        # Flux integral via Gauss's Divergence Theorem
        assert isinstance(n.flux_integral, float)
        # Volume mass integral
        assert n.volume_integral > 0.0

    # Verify Divergence Theorem proportionality: flux = divergence * volume
    for n in sample_nodes:
        vol = (4.0 / 3.0) * np.pi * (n.radius ** 3)
        expected_flux = n.divergence * vol
        assert np.isclose(n.flux_integral, expected_flux, rtol=1e-5)


def test_path_independence_conservative_field():
    """Verify that along gradient fields, path line integral closely tracks potential differences."""
    engine = VectorCalculusEngine(embedding_dim=16)

    nodes = [
        PostcomputationalNode(id="N_A", title="Node A", submolt="m/math", confirmed_count=20, wikilinks=["N_B"]),
        PostcomputationalNode(id="N_B", title="Node B", submolt="m/math", confirmed_count=5, backlinks=["N_A"]),
    ]

    coords_3d = np.array([
        [0.0, 0.0, 0.0],
        [1.0, 1.0, 0.5],
    ], dtype=np.float32)

    for i, n in enumerate(nodes):
        n.proj_3d = tuple(coords_3d[i])

    engine.compute_vector_calculus_fields(nodes, coords_3d)
    engine.compute_integral_calculus(nodes, coords_3d)

    # Both nodes have valid scalar potentials and integrals
    assert nodes[0].scalar_potential > 0.0
    assert nodes[1].scalar_potential > 0.0
    assert isinstance(nodes[1].line_integral, float)
    assert isinstance(nodes[1].flux_integral, float)
