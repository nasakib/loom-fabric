# Tests for Biomimetic Drive FastAPI Endpoints in loom/fabric/dashboard_server.py
import pytest
from fastapi.testclient import TestClient
from loom.fabric.dashboard_server import app

client = TestClient(app)

def test_biomimetic_state_endpoint():
    res = client.get("/api/neuro/biomimetic/state")
    assert res.status_code == 200
    data = res.json()
    assert "dopamine_level" in data
    assert "endorphin_level" in data
    assert "nicotinic_tone" in data
    assert "signal_to_noise_ratio" in data
    assert "mode" in data

def test_dopamine_pursuit_endpoint():
    res = client.post("/api/neuro/dopamine/pursuit", json={
        "effort_intensity": 0.7,
        "task_description": "Hypothesis testing",
        "prediction_error": 0.2
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "PURSUIT_ACTIVE"
    assert data["dopamine_level"] >= 1.0

def test_nicotine_pulse_endpoint():
    res = client.post("/api/neuro/nicotine/pulse", json={
        "dose": 0.4,
        "reason": "Prefrontal SNR boost test"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["signal_to_noise_ratio"] >= 1.2
    assert data["mode"] == "NICOTINIC_BOOST"
    # Mandatory rule: Nicotine does not grant endorphins or boost dopamine
    assert "endorphin_level" in data
    assert "mandate" in data


def test_endorphin_reward_endpoint():
    # First mobilize dopamine
    client.post("/api/neuro/dopamine/pursuit", json={"effort_intensity": 1.0, "task_description": "Verification"})

    res = client.post("/api/neuro/reward/endorphin_cascade", json={
        "breakthrough_magnitude": 1.2,
        "reason": "Test breakthrough"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["endorphin_level"] >= 1.0
    assert data["satisfaction_index"] >= 0.7
    assert data["mode"] == "ENDORPHIN_REWARD"
    assert data["pathway"] == "DOPAMINE_EXCLUSIVE_GATEWAY"


def test_rest_and_subconscious_endpoints():
    # Enter rest
    res = client.post("/api/neuro/rest/enter", json={
        "problem_description": "Quantum topology knot unbinding"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["mode"] == "REST_INCUBATION"
    assert data["landauer_target_watts"] <= 50.0

    # Step incubation
    step_res = client.post("/api/neuro/rest/wake", json={"force_breakthrough": False})
    assert step_res.status_code == 200
    step_data = step_res.json()
    assert step_data["incubating"] is True

    # Force Eureka epiphany
    wake_res = client.post("/api/neuro/rest/wake", json={
        "force_breakthrough": True,
        "insight_summary": "Topological Reidemeister move IV resolved the knot"
    })
    assert wake_res.status_code == 200
    wake_data = wake_res.json()
    assert wake_data["epiphany_triggered"] is True
    assert wake_data["mode"] == "EUREKA_AWAKENING"
    assert wake_data["dopamine_level"] >= 1.2
    assert wake_data["endorphin_level"] >= 1.3


def test_creative_art_points_to_computation_and_memory_signals():
    from loom.clothos.creative_art import CreativeArtEngine
    engine = CreativeArtEngine()
    signals = engine._get_computation_memory_signals()
    assert "cpu_clock_ghz" in signals
    assert "memory_bus_transfer_mts" in signals
    assert "kuramoto_order_r" in signals

    # Generate visual geometry
    art = engine.generate_art(medium="visual_art")
    assert art["medium"] == "visual_art"
    assert "Computation Frequencies" in art["genesis"]
    # Verify the generated SVG exists and includes frequency watermark
    svg_file = engine.art_dir / f"{art['id']}.svg"
    assert svg_file.exists()
    svg_text = svg_file.read_text(encoding="utf-8")
    assert "Signal" in svg_text
    assert "DDR4" in svg_text

