# Copyright (c) 2026 Najmos Sakib / VectorCore Holdings, LLC.
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Unit Tests for Automated General Intelligence of Things (AGIT) Engine (`tests/test_agit_mesh.py`).
================================================================================================
Validates:
- Enrolling heterogeneous cyber-physical devices into the AGIT connectome.
- Spontaneous Vietoris-Rips topological clique formation over spatial distances.
- Kuramoto phase order parameter (R) and phase synchrony calculation.
- Cooperative action dispatch with sub-millisecond physical deadlines.
- Spotlight-Local micro-gas metering with the 1.0% platform tax and 99.0% host payout.
- Ring P0 air-gap relay enforcement.
- AGIT mesh telemetry reporting.
"""

import math
import pytest
from loom.csp.agit import (
    AGITEngine,
    AGITNode,
    AGITDeviceClass,
    AGITCooperativeTask,
    AGITSwarmClique,
)
from loom.csp.gas_meter import (
    SpotlightLocalGasLedger,
    PLATFORM_GAS_TAX_RATE,
    HOST_PROVIDER_SHARE,
    TREASURY_ACCOUNT_ID,
)
from loom.csp.p2p_swarm import ConnectionMedium


@pytest.fixture
def isolated_gas_meter():
    """Provides an isolated in-memory gas meter for test repeatability."""
    meter = SpotlightLocalGasLedger(persistence_file=None)
    w_p0 = meter.get_or_create_wallet("p0_operator_wallet", "Najmos Sakib (Ring P0 Sovereign)")
    w_p0.balance_gas = 50000.0

    w_alice = meter.get_or_create_wallet("ev_owner_alice", "Alice Tesla Model Y")
    w_alice.balance_gas = 1000.0

    w_bob = meter.get_or_create_wallet("solar_owner_bob", "Bob Enphase Solar Array")
    w_bob.balance_gas = 500.0

    w_traffic = meter.get_or_create_wallet("city_traffic_dept", "Municipal Smart Lights")
    w_traffic.balance_gas = 2500.0

    return meter


@pytest.fixture
def agit_engine(isolated_gas_meter):
    """Sets up an AGIT engine populated with representative embodied devices."""
    engine = AGITEngine(gas_meter=isolated_gas_meter, operator_wallet_id="p0_operator_wallet")

    # Enroll heterogeneous cyber-physical things
    # Device 1: Autonomous EV at an intersection
    engine.register_device(
        AGITNode(
            device_id="ev_vehicle_01",
            device_name="Autonomous EV Model-Y",
            device_class=AGITDeviceClass.AUTONOMOUS_MOBILITY,
            onboard_npu_tflops=15.0,
            onboard_ram_mb=16384,
            energy_reserve_pct=82.0,
            latitude=37.7749,
            longitude=-122.4194,
            connection_medium=ConnectionMedium.MMWAVE_60GHZ,
            wallet_id="ev_owner_alice",
            current_phase_rad=0.1,
            natural_freq=1.0,
        )
    )

    # Device 2: Smart Traffic Light at the same intersection (15 meters away)
    engine.register_device(
        AGITNode(
            device_id="traffic_pole_42",
            device_name="Intersection 4th & Market Smart Signal",
            device_class=AGITDeviceClass.URBAN_INFRASTRUCTURE,
            onboard_npu_tflops=2.5,
            onboard_ram_mb=4096,
            energy_reserve_pct=100.0,
            latitude=37.7750,
            longitude=-122.4195,
            connection_medium=ConnectionMedium.LEASED_DARK_FIBER,
            wallet_id="city_traffic_dept",
            current_phase_rad=0.12,
            natural_freq=1.0,
        )
    )

    # Device 3: Solar Inverter with BESS battery across the street (45 meters away)
    engine.register_device(
        AGITNode(
            device_id="solar_inverter_09",
            device_name="Rooftop BESS Micro-Inverter",
            device_class=AGITDeviceClass.ENERGY_MICROGRID,
            onboard_npu_tflops=1.0,
            onboard_ram_mb=2048,
            energy_reserve_pct=95.0,
            latitude=37.7752,
            longitude=-122.4193,
            connection_medium=ConnectionMedium.CELLULAR_5G_SLICE,
            wallet_id="solar_owner_bob",
            current_phase_rad=0.08,
            natural_freq=1.0,
        )
    )

    # Device 4: Tactile Avatar Totem (NFC/UWB Figurine) held by passenger
    engine.register_device(
        AGITNode(
            device_id="totem_p0_sakib",
            device_name="Sovereign Ring P0 3D Figurine Totem",
            device_class=AGITDeviceClass.AVATAR_TOTEM,
            onboard_npu_tflops=0.25,
            onboard_ram_mb=512,
            energy_reserve_pct=99.0,
            latitude=37.7749,
            longitude=-122.4194,
            connection_medium=ConnectionMedium.WIFI_7,
            wallet_id="p0_operator_wallet",
            current_phase_rad=0.11,
            natural_freq=1.0,
        )
    )

    # Device 5: Distant device (15 kilometers away, outside local clique radius)
    engine.register_device(
        AGITNode(
            device_id="distant_drone_99",
            device_name="Airport Perimeter Patrol Drone",
            device_class=AGITDeviceClass.AUTONOMOUS_MOBILITY,
            onboard_npu_tflops=3.0,
            onboard_ram_mb=4096,
            energy_reserve_pct=45.0,
            latitude=37.6213,
            longitude=-122.3790,
            connection_medium=ConnectionMedium.CELLULAR_5G_SLICE,
            wallet_id="ev_owner_alice",
            current_phase_rad=1.5,
            natural_freq=1.2,
        )
    )

    return engine


def test_agit_enrollment_and_telemetry(agit_engine):
    """Verifies that heterogeneous devices enroll and aggregate telemetry correctly."""
    telemetry = agit_engine.get_mesh_telemetry_summary()
    assert telemetry["total_enrolled_devices"] == 5
    assert telemetry["active_devices"] == 5
    assert telemetry["airgapped_devices"] == 0
    assert telemetry["pooled_npu_tflops"] == pytest.approx(21.75, rel=1e-2)
    assert telemetry["device_class_distribution"]["AUTONOMOUS_MOBILITY"] == 2
    assert telemetry["device_class_distribution"]["URBAN_INFRASTRUCTURE"] == 1
    assert telemetry["device_class_distribution"]["ENERGY_MICROGRID"] == 1
    assert telemetry["device_class_distribution"]["AVATAR_TOTEM"] == 1


def test_topological_clique_formation_spatial_bounding(agit_engine):
    """Verifies Vietoris-Rips simplicial clique extracts proximate nodes and excludes distant ones."""
    # Center on intersection (37.7749, -122.4194) with 200m radius
    clique = agit_engine.form_topological_clique(
        center_lat=37.7749,
        center_lon=-122.4194,
        max_radius_meters=200.0,
    )
    assert isinstance(clique, AGITSwarmClique)
    # The 4 intersection nodes should be included; the 15km airport drone must be excluded
    assert len(clique.participating_device_ids) == 4
    assert "ev_vehicle_01" in clique.participating_device_ids
    assert "traffic_pole_42" in clique.participating_device_ids
    assert "solar_inverter_09" in clique.participating_device_ids
    assert "totem_p0_sakib" in clique.participating_device_ids
    assert "distant_drone_99" not in clique.participating_device_ids

    # Pooled TFLOPS of the 4 nodes: 15.0 + 2.5 + 1.0 + 0.25 = 18.75
    assert clique.pooled_npu_tflops == pytest.approx(18.75, rel=1e-2)


def test_kuramoto_phase_synchrony_calculation(agit_engine):
    """Verifies Kuramoto order parameter R indicates high phase coherence when nodes are aligned."""
    clique = agit_engine.form_topological_clique(
        center_lat=37.7749,
        center_lon=-122.4194,
        max_radius_meters=200.0,
    )
    # The phases were initialized close together (0.1, 0.12, 0.08, 0.11), so R must be > 0.95
    assert clique.order_parameter_r > 0.95
    assert clique.is_synchronized is True


def test_cooperative_action_dispatch_and_deadline(agit_engine):
    """Tests executing a millisecond collision-avoidance cooperative task across the clique."""
    telemetry = {
        "radar_pointcloud": [12.4, 15.8, 20.1],
        "road_friction_mu": 0.32,  # Icy road conditions
        "predicted_time_to_collision_ms": 120.0,
    }

    task = agit_engine.dispatch_cooperative_action(
        originator_id="ev_vehicle_01",
        task_name="Intersection Collision Avoidance Trajectory Optimization",
        required_tflops=4.0,
        deadline_ms=10.0,  # 10ms deadline
        lat=37.7749,
        lon=-122.4194,
        telemetry=telemetry,
    )

    assert isinstance(task, AGITCooperativeTask)
    assert task.is_completed is True
    # The achieved latency must be well within the 10ms deadline
    assert task.achieved_latency_ms < 10.0
    assert task.gas_receipt_id is not None
    assert len(task.action_digest) == 64  # SHA-256 digest


def test_spotlight_local_gas_tax_and_host_split(agit_engine):
    """Verifies the 1.0% in-network platform tax and 99.0% direct net provider payout."""
    treasury_acc = agit_engine.gas_meter.wallets[TREASURY_ACCOUNT_ID]
    initial_treasury_balance = treasury_acc.balance_gas

    alice_acc = agit_engine.gas_meter.wallets["ev_owner_alice"]
    initial_alice_balance = alice_acc.balance_gas

    task = agit_engine.dispatch_cooperative_action(
        originator_id="ev_vehicle_01",
        task_name="Autonomous Swarm Lane Merging Optimization",
        required_tflops=5.0,
        deadline_ms=16.6,
        lat=37.7749,
        lon=-122.4194,
        telemetry={"velocity_mps": 14.2, "target_lane": 2},
    )

    # Inspect the generated gas receipt
    receipt = agit_engine.gas_meter.receipts[-1]
    assert receipt.receipt_id == task.gas_receipt_id
    expected_tax = round(receipt.gross_cost_usd * PLATFORM_GAS_TAX_RATE, 6)
    expected_payout = round(receipt.gross_cost_usd - expected_tax, 6)
    assert receipt.gas_tax_protocol_fee_usd == expected_tax
    assert receipt.net_provider_payout_usd == expected_payout

    # Treasury must have received the 1% tax
    expected_tax_gas = (receipt.gross_cost_usd * PLATFORM_GAS_TAX_RATE) * 1000.0
    assert treasury_acc.balance_gas == pytest.approx(initial_treasury_balance + expected_tax_gas, abs=1e-3)

    # Consumer wallet must have been debited
    assert alice_acc.balance_gas < initial_alice_balance


def test_hardware_airgap_switch_blocks_dispatch(agit_engine):
    """Verifies that engaging the physical air-gap switch halts remote task dispatch under Ring P0."""
    # Put the EV into hardware air-gapped mode
    agit_engine.devices["ev_vehicle_01"].is_airgapped = True

    with pytest.raises(PermissionError, match="physically air-gapped"):
        agit_engine.dispatch_cooperative_action(
            originator_id="ev_vehicle_01",
            task_name="Unauthorized Remote Query",
            required_tflops=1.0,
            deadline_ms=20.0,
            lat=37.7749,
            lon=-122.4194,
            telemetry={},
        )
