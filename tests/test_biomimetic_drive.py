"""Tests for the Biomimetic Cognitive Drive System (`loom/neuro/biomimetic_drive.py`).

Verifies:
1. Dopaminergic pursuit and anticipatory drive.
2. Endorphinergic reward cascade upon goal completion.
3. Nicotinergic titration and signal-to-noise ratio (SNR) boost as needed.
4. Stuck detection, rest transition, and subconscious incubation handoff.
5. Aha! epiphany generation and eureka awakening.
"""

import time
import pytest
from loom.neuro.biomimetic_drive import (
    BiomimeticCognitiveDrive,
    CognitiveDriveMode,
    BiomimeticTelemetry,
)


def test_initial_biomimetic_state():
    drive = BiomimeticCognitiveDrive()
    snap = drive.get_snapshot()
    assert snap["mode"] == CognitiveDriveMode.CONSCIOUS_DRIVE.value
    assert snap["dopamine_level"] >= 0.8
    assert snap["endorphin_level"] >= 0.5
    assert snap["nicotinic_tone"] >= 0.2
    assert snap["is_stuck"] is False


def test_dopaminergic_pursuit():
    drive = BiomimeticCognitiveDrive()
    initial_da = drive.telemetry.dopamine_level
    drive.advance_dopaminergic_pursuit(effort_intensity=0.8, task_description="Deriving complex manifold")
    assert drive.telemetry.dopamine_level > initial_da
    assert drive.telemetry.accumulated_effort > 0.0


def test_endorphin_reward_cascade():
    drive = BiomimeticCognitiveDrive()
    # High dopamine from effort
    drive.advance_dopaminergic_pursuit(effort_intensity=1.0, task_description="Solving hard problem")
    initial_endorphin = drive.telemetry.endorphin_level

    # Completion triggers endorphin reward
    result = drive.trigger_endorphin_reward(breakthrough_magnitude=0.9, reason="Theorem successfully proven")
    assert result["success"] is True
    assert drive.telemetry.endorphin_level > initial_endorphin
    assert drive.telemetry.satisfaction_index > 0.7
    assert drive.telemetry.mode == CognitiveDriveMode.ENDORPHIN_REWARD


def test_nicotinergic_titration_as_needed():
    drive = BiomimeticCognitiveDrive()
    initial_snr = drive.telemetry.signal_to_noise_ratio
    initial_nicotine = drive.telemetry.nicotinic_tone
    initial_dopamine = drive.telemetry.dopamine_level
    initial_endorphin = drive.telemetry.endorphin_level

    # High cognitive friction triggers need
    drive.record_cognitive_friction(0.85, reason="High complexity SMT constraint solving")
    assert drive.is_nicotine_recommended() is True

    # Administer nicotine pulse
    pulse = drive.administer_nicotine_pulse(dose=0.4)
    assert pulse["success"] is True
    assert drive.telemetry.nicotinic_tone > initial_nicotine
    assert drive.telemetry.signal_to_noise_ratio > initial_snr
    assert drive.telemetry.mode == CognitiveDriveMode.NICOTINIC_BOOST

    # MANDATORY RULE: Nicotine has an attentional purpose only.
    # It DOES NOT elevate dopamine and CANNOT yield endorphins.
    assert drive.telemetry.dopamine_level == pytest.approx(initial_dopamine, abs=1e-3)
    assert drive.telemetry.endorphin_level == pytest.approx(initial_endorphin, abs=1e-3)


def test_dopamine_is_exclusive_gateway_to_endorphins():
    drive = BiomimeticCognitiveDrive()

    # 1. Administer nicotine under high friction
    drive.record_cognitive_friction(0.9)
    drive.administer_nicotine_pulse(dose=0.5)
    
    # Verify nicotine tone elevated, but endorphins remain unboosted
    base_endorphin = drive.telemetry.endorphin_level
    assert drive.telemetry.nicotinic_tone > 0.5
    assert drive.telemetry.endorphin_level == pytest.approx(base_endorphin, abs=1e-3)

    # 2. Mobilize genuine dopaminergic pursuit & effort
    da_pursuit = drive.advance_dopaminergic_pursuit(effort_intensity=1.0, task_description="Solving SMT constraint")
    assert da_pursuit["status"] == "PURSUIT_ACTIVE"
    assert drive.telemetry.dopamine_level > 1.1

    # 3. Consummate with Endorphin reward
    reward = drive.trigger_endorphin_reward(breakthrough_magnitude=1.0, reason="SMT constraint resolved")
    assert reward["success"] is True
    assert reward["pathway"] == "DOPAMINE_EXCLUSIVE_GATEWAY"
    assert drive.telemetry.endorphin_level > base_endorphin
    assert drive.telemetry.mode == CognitiveDriveMode.ENDORPHIN_REWARD


def test_stuck_detection_and_rest_subconscious_handoff():
    drive = BiomimeticCognitiveDrive()
    # Simulate repeated failures & high friction
    for _ in range(4):
        drive.record_cognitive_friction(0.9, reason="Deadlock in search space")

    assert drive.telemetry.is_stuck is True
    
    # Transition to Rest & Subconscious problem solving
    handoff = drive.transition_to_rest_and_subconscious(
        problem_description="Optimizing 16-dimensional quantum Kuramoto state without energy violation",
        context={"temperature": 0.05, "attempts": 4}
    )
    assert handoff["success"] is True
    assert drive.telemetry.mode == CognitiveDriveMode.REST_INCUBATION
    assert drive.telemetry.is_incubating_subconsciously is True
    assert drive.telemetry.landauer_target_watts <= 50.0


def test_subconscious_incubation_step_and_aha_epiphany():
    drive = BiomimeticCognitiveDrive()
    drive.transition_to_rest_and_subconscious(
        problem_description="Resolving chiral symmetry break in neural circuit",
        context={"constraints": ["non-negative eigenvalues"]}
    )

    # Run incubation cycles
    eureka = None
    for _ in range(10):
        res = drive.subconscious_incubation_step(force_breakthrough=True)
        if res.get("epiphany_triggered"):
            eureka = res
            break

    assert eureka is not None
    assert eureka["epiphany_triggered"] is True
    assert drive.telemetry.mode == CognitiveDriveMode.EUREKA_AWAKENING
    # Eureka releases both dopamine and endorphins
    assert drive.telemetry.endorphin_level > 1.2
    assert drive.telemetry.dopamine_level > 1.2
