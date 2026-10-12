"""
Test Suite: OpenClaw API Bridge (`loom/gateway/openclaw_bridge.py`).

Tests:
1. POST `/v1/openclaw/dispatch`:
   - Scrambles/scrubs protected IP via Enclave.Scrubber.
   - Routes through QCTRouter.
   - Returns immediate ACK: `{"task_id": ..., "status": "QUEUED", "scrubbed": bool}`.
2. GET `/v1/openclaw/telemetry`:
   - Returns Ray cluster node states, accelerator counts (`GPU_NVIDIA`, `GPU_AMD`), and VRAM headroom.
"""

import pytest
from fastapi.testclient import TestClient

from loom.gateway.app import app


@pytest.fixture
def client():
    return TestClient(app)


def test_openclaw_dispatch_scrubbed_payload(client):
    """Verify POST /v1/openclaw/dispatch scrubs protected IP and returns QUEUED ack."""
    payload = {
        "session_id": "sess_test_12345",
        "task_type": "inference",
        "raw_prompt": (
            "We are evaluating ClothOS microkernel alongside VectorForge and fouriersLibrary. "
            "Please analyze performance on our local nodes."
        ),
        "execution_tier": "deterministic",
        "webhook_url": "http://127.0.0.1:18789/webhook",
    }

    response = client.post("/v1/openclaw/dispatch", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "task_id" in data
    assert data["task_id"].startswith("claw_")
    assert data["status"] == "QUEUED"
    assert data["scrubbed"] is True


def test_openclaw_dispatch_clean_payload(client):
    """Verify clean payload dispatch without IP leaks still returns QUEUED ack."""
    payload = {
        "session_id": "sess_clean_999",
        "task_type": "qubo",
        "raw_prompt": "Optimize energy minimization on simulated p-bit lattice.",
        "execution_tier": "thermodynamic",
    }

    response = client.post("/v1/openclaw/dispatch", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "QUEUED"
    assert data["scrubbed"] is False


def test_openclaw_telemetry(client):
    """Verify GET /v1/openclaw/telemetry returns cluster nodes, accelerator counts, and VRAM headroom."""
    response = client.get("/v1/openclaw/telemetry")
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ONLINE"
    assert "nodes" in data
    assert len(data["nodes"]) >= 2

    # Verify accelerator descriptors
    acc = data["accelerators"]
    assert "GPU_NVIDIA" in acc
    assert "GPU_AMD" in acc
    assert "CPU_HEAD" in acc

    # Verify VRAM headroom
    assert "vram_headroom_mb" in data
    assert data["vram_headroom_mb"] > 0
    assert "total_vram_mb" in data
    assert data["total_vram_mb"] > 0


def test_openclaw_models_for_aider(client):
    """Verify GET /v1/openclaw/models exposes loom-fabric-qct for Aider headless orchestration."""
    response = client.get("/v1/openclaw/models")
    assert response.status_code == 200
    data = response.json()
    assert data["object"] == "list"
    model_ids = [m["id"] for m in data["data"]]
    assert "loom-fabric-qct" in model_ids

