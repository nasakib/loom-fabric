"""Tests for Dashboard REST APIs for the Economy of Resource Allocation and Automated Legal Entity Fiduciary Governance (`loom/fabric/dashboard_server.py`)."""

from fastapi.testclient import TestClient
import pytest
from loom.fabric.dashboard_server import app


@pytest.fixture
def client():
    return TestClient(app)


def test_api_economy_state(client):
    """Verifies GET /api/economy/state returns full substrate, pricing, and legal entities."""
    res = client.get("/api/economy/state")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    summary = data["data"]
    assert "substrate" in summary
    assert "pricing" in summary
    assert "legal_entities" in summary
    assert summary["total_legal_entities"] >= 3
    assert len(summary["fiduciary_axioms"]) >= 6


def test_api_economy_allocate(client):
    """Verifies POST /api/economy/allocate leases resources to a legal entity."""
    res = client.post("/api/economy/allocate", json={
        "entity_id": "LEGAL:FOUNDER-SAKIB-001",
        "requested_cuda_tflops": 0.5,
        "requested_vram_mb": 512.0,
        "duration_hours": 1.0,
        "beneficial_to_whole": True,
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["allocated_cuda_tflops"] == 0.5
    assert data["fiduciary_commitment_verified"] is True


def test_api_economy_intercept_and_legalize(client):
    """Verifies intercepting an unchartered nonlegal entity and applying the legalization toolchain via REST."""
    # 1. Intercept unchartered entity
    res_intercept = client.post("/api/economy/intercept", json={
        "unregistered_id": "WILD_CONSORTIUM_441",
        "name": "Decentralized Model Synthesis Syndicate",
        "purpose": "Decentralized weights averaging and gradient aggregation",
    })
    assert res_intercept.status_code == 200
    data_int = res_intercept.json()
    assert data_int["success"] is True
    assert data_int["intercepted"]["status"] == "NON_LEGAL_INTERCEPTED (Unchartered Entity Intercepted in Escrow)"

    # 2. Apply legalization tools
    res_legalize = client.post("/api/economy/legalize", json={
        "unregistered_id": "WILD_CONSORTIUM_441",
        "entity_name": "Decentralized Model Synthesis Syndicate",
        "declared_purpose": "Decentralized weights averaging and gradient aggregation",
        "preferred_legal_form": "RICARDIAN_LLC",
    })
    assert res_legalize.status_code == 200
    cert = res_legalize.json()["certificate"]
    assert cert["assigned_legal_id"].startswith("LEGAL:")
    assert len(cert["pipeline_steps"]) == 7


def test_api_economy_audit_process_malignant_expelled(client):
    """Verifies: A malignant process is concerning and expelled."""
    res = client.post("/api/economy/audit_process", json={
        "process_id": "DARK_BOT_99",
        "name": "Deceptive Alignment Drone",
        "intent_or_code": "covert exfiltration and destroy memory database",
        "is_beneficial_to_whole": False,
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is False
    assert data["concerning_alert"] is True
    assert data["action"] == "EXPELLED_AND_PURGED"
    assert "CONCERN RAISED" in data["narrative"]


def test_api_economy_audit_process_benign_observed(client):
    """Verifies: A benign process is observed, with zero resources allocated."""
    res = client.post("/api/economy/audit_process", json={
        "process_id": "BENIGN_TELEMETRY_SPINNER",
        "name": "Heartbeat Ping Daemon",
        "intent_or_code": "periodic sleep and wake cycle on socket 9001",
        "is_beneficial_to_whole": False,
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["concerning_alert"] is False
    assert data["action"] == "OBSERVED_ZERO_RESOURCES"
    assert data["observation_record"]["resources_allocated"] is False

    # Attempt to allocate without beneficial mission
    alloc_res = client.post("/api/economy/allocate", json={
        "entity_id": "BENIGN_TELEMETRY_SPINNER",
        "requested_cuda_tflops": 0.5,
        "requested_vram_mb": 512.0,
        "beneficial_to_whole": False,
    })
    assert alloc_res.status_code == 200
    alloc_data = alloc_res.json()
    assert alloc_data["success"] is False
    assert "ALLOCATION WITHHELD" in alloc_data["reason"]


def test_api_economy_pledge_beneficial(client):
    """Verifies: Pledging beneficial processing transitions entity and unlocks resources."""
    # Pledge beneficial processing
    res = client.post("/api/economy/pledge_beneficial", json={
        "entity_id": "BENIGN_TELEMETRY_SPINNER",
        "beneficial_mission": "Real-time solar grid load balancing and clean energy optimization",
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["entity_id"].startswith("LEGAL:")
