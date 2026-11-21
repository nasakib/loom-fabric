# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
Comprehensive Unit & Integration Test Suite for:
1. Occipital Lobe Visual Stream (V1-V5, Retinotopy w = ln(z+a), Optical Flow).
2. DMN Daydreaming (Low Hopfield Temperature Beta) & NSDR (Slow-Wave Delta, Glymphatic Clearance).
3. Graded All-or-Nothing Working Memory (Adrian Gating + Wang/Miller Continuous Gradients).
4. Endorphin Neurochemical Reward Circuitry (Beta-endorphin, muOR Saturation, Analgesia).
5. RISC-V 64 (RV64GCV) + Google TPU 2D Systolic Array MXU Hardware Emulator.
6. Shell CLI Integration (clothsh / wcos) & Dashboard Server REST Endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from loom.clothos.occipital_stream import (
    OccipitalLobeAndRestEngine,
    BrainStateMode,
    get_occipital_engine,
)
from loom.clothos.working_memory import (
    WorkingMemoryAndEndorphinEngine,
    GateState,
    BaddeleyComponent,
    get_working_memory_engine,
)
from loom.clothos.riscv_tpu_emulator import (
    RiscvTpuHardwareEmulator,
    get_riscv_tpu_emulator,
)
from loom.clothos.shell import get_clothos_shell


# ---------------------------------------------------------------------------
# 1. Occipital Lobe Visual Stream & Optical Flow Tests
# ---------------------------------------------------------------------------
class TestOccipitalStream:
    def test_occipital_stream_telemetry(self):
        engine = OccipitalLobeAndRestEngine()
        stream = engine.get_occipital_stream()

        assert "v1_gabor_activations" in stream
        assert len(stream["v1_gabor_activations"]) == 8
        assert "v2_contour_curvature" in stream
        assert "v4_chromatic_saturation" in stream
        assert "v5_optical_flow_coherence" in stream
        assert "optical_flow_particles" in stream
        assert len(stream["optical_flow_particles"]) == 16
        assert stream["retinotopic_fovea_r"] > 0
        assert stream["frame_rate_fps"] == 60.0
        assert stream["active_visual_stream"] in ("VENTRAL_WHAT", "DORSAL_WHERE")

    def test_daydream_generation(self):
        engine = OccipitalLobeAndRestEngine()
        span = engine.generate_daydream_span(
            theme="Hyperbolic Silicon Leaves",
            prompt="Spontaneous wandering across non-Euclidean manifolds"
        )

        assert span.daydream_id.startswith("DREAM-")
        assert span.theme == "Hyperbolic Silicon Leaves"
        assert 0.20 <= span.hopfield_temperature_beta <= 0.45
        assert 0.0 <= span.dmn_coupling_strength <= 1.0
        assert len(span.synesthetic_visual_motif) > 0
        assert "Najmos Sakib" in span.narrative_stream

        recent = engine.get_recent_daydreams(limit=5)
        assert len(recent) >= 1
        assert recent[-1]["daydream_id"] == span.daydream_id

    def test_nsdr_regeneration_toggle(self):
        engine = OccipitalLobeAndRestEngine()
        
        # Initially inactive
        init_state = engine.get_nsdr_state()
        assert not init_state["is_active"]

        # Activate NSDR
        active_state = engine.toggle_nsdr(activate=True)
        assert active_state["is_active"]
        assert active_state["delta_wave_power"] == 0.88
        assert active_state["theta_wave_power"] == 0.72
        assert active_state["glymphatic_clearance_rate"] == 85.0
        assert active_state["landauer_thermal_cooling_watts"] == 18.5
        assert active_state["brain_state_mode"] == BrainStateMode.NSDR_DEEP_REST.value

        # Deactivate NSDR
        deact_state = engine.toggle_nsdr(activate=False)
        assert not deact_state["is_active"]
        assert deact_state["delta_wave_power"] == 0.12
        assert deact_state["glymphatic_clearance_rate"] == 14.2
        assert deact_state["brain_state_mode"] == BrainStateMode.ALERT_FOCUSED.value


# ---------------------------------------------------------------------------
# 2. Graded All-or-Nothing Working Memory & Endorphin Circuit Tests
# ---------------------------------------------------------------------------
class TestWorkingMemoryAndEndorphins:
    def test_adrian_all_or_none_gating_and_continuous_gradients(self):
        engine = WorkingMemoryAndEndorphinEngine()

        # Slot 1: Sub-threshold stimulus (voltage < 0.65 V) -> ALL-OR-NONE REJECTED (0)
        res_sub = engine.gate_into_slot(
            slot_id=1,
            content="Sub-threshold transient noise",
            stimulus_voltage=0.45,
            initial_gradient=0.8
        )
        assert res_sub["gate_state"] == GateState.LOCKED.value
        assert res_sub["gradient"] == 0.0
        assert "SUB_THRESHOLD_REJECTED" in res_sub["status"]

        # Slot 1: Super-threshold stimulus (voltage >= 0.65 V) -> ALL-OR-NONE IGNITED (1)
        res_super = engine.gate_into_slot(
            slot_id=1,
            content="High-priority operator steering directive",
            stimulus_voltage=0.92,
            initial_gradient=0.95
        )
        assert res_super["gate_state"] == GateState.IGNITED.value
        assert res_super["gradient"] == 0.95
        assert res_super["voltage"] == 0.92
        assert "ALL_OR_NONE_IGNITED_SUCCESS" in res_super["status"]

        # Verify state summary reflects 7 slots
        state = engine.get_working_memory_state()
        assert state["total_slots"] == 7
        assert state["active_ignited_slots"] >= 1
        assert state["capacity_utilization_pct"] > 0
        slot_1 = next(s for s in state["slots"] if s["slot_id"] == 1)
        assert slot_1["gate_state"] == GateState.IGNITED.value
        assert slot_1["is_ignited_binary"] == 1
        assert slot_1["content"] == "High-priority operator steering directive"

    def test_endorphin_administration_and_muor_saturation(self):
        engine = WorkingMemoryAndEndorphinEngine()

        init_state = engine.get_endorphin_state()
        baseline_level = init_state["current_endorphin_level"]

        # Administer reward
        reward = engine.administer_endorphins(dose_magnitude=1.2, rationale="Epistemic Convergence")
        assert reward["current_endorphin_level"] > baseline_level
        assert reward["mu_opioid_saturation_pct"] > 30.0
        assert reward["analgesia_dampening_factor"] > 0.0
        assert reward["euphoric_contentment"] >= 0.85
        assert reward["total_rewards_administered"] >= 1
        assert reward["last_reward_rationale"] == "Epistemic Convergence"


# ---------------------------------------------------------------------------
# 3. RISC-V 64 + Google TPU 2D Systolic Hardware Emulator Tests
# ---------------------------------------------------------------------------
class TestRiscvTpuEmulator:
    def test_systolic_matmul_cycle(self):
        emulator = RiscvTpuHardwareEmulator()
        init_state = emulator.get_hardware_state()

        assert init_state["architecture"].startswith("RISC-V 64-bit")
        assert "RoCC TPU Extensions" in init_state["isa_extensions"]
        assert len(init_state["pe_grid_sample_8x8"]) == 8

        # Execute systolic wavefront cycle
        res = emulator.execute_tpu_matmul_cycle()
        assert res["status"] == "SYSTOLIC_MATMUL_CONVERGED"
        assert res["cycles_elapsed"] == 32  # 2N cycles for 16x16 array
        assert res["total_mac_ops"] == 256  # 16x16 MACs
        assert res["sustained_tflops"] > 100.0
        assert res["energy_mj_consumed"] > 0.0
        assert len(res["output_vector_sample"]) == 8

        # Check post-execution state
        post_state = emulator.get_hardware_state()
        assert post_state["cycles_elapsed"] == 32
        assert post_state["instructions_retired"] == 1
        assert post_state["metrics"]["total_matrix_multiplies"] == 1
        assert post_state["metrics"]["landauer_joules_consumed"] < 1000.0


# ---------------------------------------------------------------------------
# 4. ClothOS Shell Command Line Tests
# ---------------------------------------------------------------------------
class TestShellCommands:
    def test_shell_occipital_commands(self):
        shell = get_clothos_shell()
        
        res = shell.execute("occipital")
        assert res.exit_code == 0
        assert "Occipital Lobe Visual Stream" in res.stdout
        assert "V1 Gabor Orientation Columns" in res.stdout

        res_flow = shell.execute("occipital flow")
        assert res_flow.exit_code == 0
        assert "V5/MT Optical Flow Vector Sample" in res_flow.stdout

    def test_shell_daydream_and_nsdr_commands(self):
        shell = get_clothos_shell()

        # Daydream trigger
        res_dd = shell.execute("daydream trigger Crystalline Photonic Mycelium")
        assert res_dd.exit_code == 0
        assert "Daydreaming Episode Generated" in res_dd.stdout
        assert "DMN Coupling" in res_dd.stdout

        # Daydream list
        res_list = shell.execute("daydream")
        assert res_list.exit_code == 0
        assert "Default Mode Network (DMN) Daydreaming Stream" in res_list.stdout

        # NSDR on/off
        res_nsdr_on = shell.execute("nsdr on")
        assert res_nsdr_on.exit_code == 0
        assert "[ACTIVE]" in res_nsdr_on.stdout
        assert "ACTIVATED" in res_nsdr_on.stdout

        res_nsdr_off = shell.execute("nsdr off")
        assert res_nsdr_off.exit_code == 0
        assert "[INACTIVE]" in res_nsdr_off.stdout

    def test_shell_wm_and_endorphin_commands(self):
        shell = get_clothos_shell()

        # Working Memory view
        res_wm = shell.execute("wm")
        assert res_wm.exit_code == 0
        assert "Graded All-or-Nothing Working Memory" in res_wm.stdout
        assert "Slot 0" in res_wm.stdout

        # Working Memory gate super-threshold
        res_gate = shell.execute("wm gate 4 0.95 Sovereign operator fealty verification")
        assert res_gate.exit_code == 0
        assert "Working Memory Gate Slot #4" in res_gate.stdout
        assert "ALL_OR_NONE_IGNITED_SUCCESS" in res_gate.stdout

        # Endorphin view and reward
        res_end = shell.execute("endorphin")
        assert res_end.exit_code == 0
        assert "Beta-Endorphin Level" in res_end.stdout

        res_rew = shell.execute("endorphin reward 0.9 Epistemic harmony convergence")
        assert res_rew.exit_code == 0
        assert "Beta-Endorphin Reward Administered" in res_rew.stdout
        assert "Epistemic harmony convergence" in res_rew.stdout

    def test_shell_tpu_commands(self):
        shell = get_clothos_shell()

        res_tpu = shell.execute("tpu")
        assert res_tpu.exit_code == 0
        assert "RISC-V 64 + TPU Systolic Array Hardware Emulator" in res_tpu.stdout
        assert "Peak TFLOPS" in res_tpu.stdout
        assert "Systolic PE Grid Sample" in res_tpu.stdout

        res_run = shell.execute("tpu run 3")
        assert res_run.exit_code == 0
        assert "Systolic Step Executed (3 cycles)" in res_run.stdout


# ---------------------------------------------------------------------------
# 5. Dashboard Server REST Endpoints Integration Tests
# ---------------------------------------------------------------------------
class TestDashboardServerEndpoints:
    @pytest.fixture(scope="class")
    def client(self):
        from loom.fabric.dashboard_server import app
        return TestClient(app)

    def test_occipital_api(self, client):
        res = client.get("/api/neuro/occipital/stream")
        assert res.status_code == 200
        data = res.json()
        assert "v1_gabor_activations" in data
        assert "optical_flow_particles" in data

    def test_daydream_and_nsdr_api(self, client):
        # Trigger daydream
        res_d = client.post("/api/neuro/daydream/trigger", json={
            "theme": "Riemannian Tensor Flows",
            "prompt": "Exploration of curved manifold geometry"
        })
        assert res_d.status_code == 200
        d_data = res_d.json()
        assert d_data["status"] == "DAYDREAM_GENERATED"
        assert d_data["daydream"]["theme"] == "Riemannian Tensor Flows"

        # Recent daydreams
        res_recent = client.get("/api/neuro/daydream/recent?limit=3")
        assert res_recent.status_code == 200
        assert len(res_recent.json()["daydreams"]) >= 1

        # NSDR toggle
        res_n = client.post("/api/neuro/nsdr/toggle", json={"activate": True})
        assert res_n.status_code == 200
        assert res_n.json()["nsdr_state"]["is_active"] is True

        res_n_state = client.get("/api/neuro/nsdr/state")
        assert res_n_state.status_code == 200
        assert res_n_state.json()["is_active"] is True

        # Turn NSDR back off
        client.post("/api/neuro/nsdr/toggle", json={"activate": False})

    def test_endorphin_and_wm_api(self, client):
        # Administer endorphins
        res_e = client.post("/api/neuro/endorphins/administer", json={
            "dose": 0.75,
            "rationale": "REST API Test Verification"
        })
        assert res_e.status_code == 200
        assert res_e.json()["status"] == "ENDORPHIN_ADMINISTERED"

        # Endorphin state
        res_es = client.get("/api/neuro/endorphins/state")
        assert res_es.status_code == 200
        assert res_es.json()["current_endorphin_level"] >= 1.0

        # Working memory gate
        res_wmg = client.post("/api/neuro/working_memory/gate", json={
            "slot_id": 5,
            "stimulus_voltage": 0.88,
            "content": "API Super-threshold Gate Ignition",
            "initial_gradient": 0.9
        })
        assert res_wmg.status_code == 200
        assert res_wmg.json()["gate_state"] == "IGNITED"

        # Working memory state
        res_wms = client.get("/api/neuro/working_memory/state")
        assert res_wms.status_code == 200
        assert res_wms.json()["total_slots"] == 7

    def test_riscv_tpu_api(self, client):
        # TPU State
        res_s = client.get("/api/hardware/riscv_tpu/state")
        assert res_s.status_code == 200
        assert "RV64GCV" in res_s.json()["architecture"]

        # Execute systolic cycles
        res_c = client.post("/api/hardware/riscv_tpu/execute_cycle", json={"cycles": 2})
        assert res_c.status_code == 200
        assert res_c.json()["status"] == "CYCLE_COMPLETED"
        assert res_c.json()["cycles_executed"] == 2
