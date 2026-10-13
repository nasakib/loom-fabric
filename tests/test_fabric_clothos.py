"""Unit & Integration tests for the Fabric stack and ClothOS Moltbook Synergy."""

import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient

from fabric.routing.router import (
    QCTHybridRouter,
    QCTRouteDecision,
    DAGExecutionPlan,
)
from fabric.ipc.zmq_bus import StitchZMQTelemetryBus, TelemetryEnvelope
from fabric.discovery.nodes import CrossPlatformNodeDiscovery, ClusterTopologySnapshot
from loom.clothos.moltbook_bridge import MoltbookWisdomBridge
from loom.clothos.kernel import ClothOSKernel
from loom.gateway.app import app


def test_qct_router_frozen_models_and_dag():
    router = QCTHybridRouter()
    decision = router.route_query(
        prompt="Verify Z3 SMT formal proof and generate CUDA kernel across RTX 3060 Ti",
        vram_margin_mb=12288,
    )
    assert isinstance(decision, QCTRouteDecision)
    assert decision.qct_entropy_score > 0.25
    assert decision.tier in (
        "tier_1_local_rapid",
        "tier_2_distributed_ray_mesh",
        "tier_3_cloud_arbitrage",
        "tier_4_clothos_riscv_rvv",
    )

    # Verify strict Pydantic v2 frozen=True immutability
    with pytest.raises(ValidationError):
        decision.qct_entropy_score = 0.0  # type: ignore[misc]

    dag = decision.dag
    assert isinstance(dag, DAGExecutionPlan)
    assert len(dag.nodes) == 5
    with pytest.raises(ValidationError):
        dag.critical_path_ms = 0.0  # type: ignore[misc]


def test_stitch_zmq_telemetry_bus_torque_scrubbing():
    bus = StitchZMQTelemetryBus()
    envelope = bus.publish(
        topic="stitch.vram",
        source_node="skyTech-192.168.99.1",
        raw_payload={
            "role": "Dual-GPU Worker",
            "vram_free_mb": 15200.0,
            "note": "contact user@example.com or Project Stitch internal",
        },
    )
    assert isinstance(envelope, TelemetryEnvelope)
    assert envelope.torque_verified is True
    assert "user@example.com" not in envelope.payload_json

    with pytest.raises(ValidationError):
        envelope.sequence_id = 999  # type: ignore[misc]


def test_cross_platform_node_discovery():
    discovery = CrossPlatformNodeDiscovery()
    snapshot = discovery.discover_all(probe_network=False)
    assert isinstance(snapshot, ClusterTopologySnapshot)
    assert snapshot.total_cluster_vram_mb >= 16384
    platforms = {n.platform_family for n in snapshot.nodes}
    assert "Windows" in platforms
    assert "ClothOS-RISCV" in platforms


def test_clothos_kernel_and_moltbook_bridge(tmp_path):
    bridge = MoltbookWisdomBridge(workspace_root=tmp_path)
    signals = bridge.ingest_submolt_signals(min_upvotes=80)
    assert len(signals) >= 4
    hypotheses = bridge.formulate_hypotheses(signals)
    assert len(hypotheses) == len(signals)
    assert all(h.sandbox_status == "VALIDATED" for h in hypotheses)

    kernel = ClothOSKernel(workspace_root=tmp_path)
    snap = kernel.snapshot(
        sample_prompt="Optimize Stitch ZeroMQ IPC and QCT DAG routing",
        probe_network=False,
    )
    assert snap.os_version.startswith("ClothOS")
    assert snap.latest_route.dag.plan_id.startswith("dag-")
    assert len(snap.active_hypotheses) >= 4

    status_md = kernel.sync_agent_status_markdown(probe_network=False)
    assert status_md.exists()
    content = status_md.read_text(encoding="utf-8")
    assert "ClothOS & Fabric Autonomous Architecture Status" in content
    assert "Moltbook R&D Wisdom Bridge" in content


def test_gateway_clothos_endpoints():
    from loom.gateway.app import clothos_status, clothos_dag_get, clothos_moltbook_synergy

    data = clothos_status()
    assert "os_version" in data
    assert "latest_route" in data

    dag_data = clothos_dag_get(prompt="Synthesize RISC-V kernel", prefer_riscv=True)
    assert dag_data["tier"] == "tier_4_clothos_riscv_rvv"
    assert "dag" in dag_data

    syn_data = clothos_moltbook_synergy()
    assert "registration" in syn_data
    assert "hypotheses" in syn_data
