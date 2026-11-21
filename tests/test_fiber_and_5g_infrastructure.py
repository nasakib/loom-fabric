# Copyright (c) 2026 Najmos Sakib / VectorCore Holdings, LLC.
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Verification Suite: Leased Commercial Fiber & 5G Infrastructure Subsystems.
==========================================================================
Tests:
1. Fiber Lease Manager: Carrier Catalog, Geohash Matchmaking & Circuit Provisioning.
2. Silica Optical Propagation Latency Math (4.897 us/km) & Cost Amortization.
3. 5G Cellular PHY Models: 3GPP Standalone URLLC Slicing, Private CBRS Band 48, and FWA.
4. CLI Integration: `fiber providers`, `fiber circuits`, `fiber lease`, and `5g`.
"""

import pytest

from loom.csp.fiber_lease import (
    FiberLeaseManager,
    FiberCarrier,
    LeasedFiberCircuit,
    FiberLeaseType,
    FiberCarrierTier,
)
from loom.hardware.transceiver import (
    FabricTransceiver,
    TransceiverBand,
    ModulationScheme,
)
from loom.hardware.cli import main as cli_main


# =============================================================================
# 1. Commercial Dark Fiber & Open-Access Leasing
# =============================================================================

def test_fiber_lease_manager_catalog():
    fm = FiberLeaseManager(persistence_file=None)
    assert len(fm.known_carriers) >= 4
    assert "zayo_metro" in fm.known_carriers
    assert "crown_castle" in fm.known_carriers
    assert "open_access_metro" in fm.known_carriers
    assert "coop_fiber" in fm.known_carriers

    # Check default active circuit
    assert len(fm.active_circuits) >= 1
    default_cir = list(fm.active_circuits.values())[0]
    assert default_cir.committed_bandwidth_gbps >= 100.0
    assert default_cir.optical_propagation_latency_ms < 0.05
    assert default_cir.is_active is True


def test_geohash_carrier_filtering():
    fm = FiberLeaseManager(persistence_file=None)
    # Atlanta Downtown/Inman Park geohash
    carriers = fm.get_available_carriers(geohash="dn5bpq")
    assert len(carriers) >= 3
    carrier_ids = [c.carrier_id for c in carriers]
    assert "zayo_metro" in carrier_ids
    assert "crown_castle" in carrier_ids


def test_circuit_provisioning_and_optical_latency():
    fm = FiberLeaseManager(persistence_file=None)
    circuit = fm.provision_lease(
        carrier_id="crown_castle",
        lease_type=FiberLeaseType.DARK_FIBER_STRAND,
        endpoint_a="skyTech-Worker",
        endpoint_b="midtown-datacenter-node",
        length_km=4.8,
        bandwidth_gbps=100.0,
    )

    assert circuit.circuit_id.startswith("cir-sl-")
    assert circuit.physical_length_km == 4.8
    assert circuit.committed_bandwidth_gbps == 100.0

    # Test exact speed of light in silica fiber: ~4.897 us/km -> 4.8 km * 0.004897 ms = ~0.0235 ms
    assert 0.020 < circuit.optical_propagation_latency_ms < 0.030
    assert circuit.monthly_lease_cost_usd > 0.0
    assert circuit.hourly_amortized_cost_usd == pytest.approx(circuit.monthly_lease_cost_usd / 720.0, rel=1e-3)


def test_fiber_lease_amortization_surcharge():
    fm = FiberLeaseManager(persistence_file=None)
    # Surcharge for a 30-second compute task
    surcharge_30s = fm.calculate_compute_lease_surcharge(duration_seconds=30.0)
    assert surcharge_30s > 0.0
    assert surcharge_30s < 0.01 # Fractions of a cent per short task


# =============================================================================
# 2. 5G Cellular Infrastructure & Network Slicing
# =============================================================================

def test_cellular_5g_urllc_transceiver():
    phy = FabricTransceiver(band=TransceiverBand.CELLULAR_5G_URLLC)
    link = phy.calculate_link_quality()
    assert link.is_viable is True
    assert link.signal_bars == "●●●●○" # -68 dBm RSRP
    assert link.latency_ms <= 10.0 # Sub-10ms URLLC air interface
    assert link.effective_bandwidth_gbps >= 2.0
    assert link.packet_loss_rate < 0.0001
    assert link.modulation == ModulationScheme.QAM256


def test_cellular_5g_cbrs_private_mesh():
    phy = FabricTransceiver(band=TransceiverBand.CELLULAR_5G_CBRS)
    link = phy.calculate_link_quality()
    assert link.is_viable is True
    assert link.latency_ms <= 12.0
    assert link.effective_bandwidth_gbps >= 0.8
    assert link.modulation == ModulationScheme.QAM256


def test_cellular_5g_fwa_broadband():
    phy = FabricTransceiver(band=TransceiverBand.CELLULAR_5G_FWA)
    link = phy.calculate_link_quality()
    assert link.is_viable is True
    assert 12.0 < link.latency_ms < 25.0
    assert link.effective_bandwidth_gbps >= 0.5


# =============================================================================
# 3. CLI Integration
# =============================================================================

def test_cli_fiber_and_5g(capsys):
    # 1. fiber providers
    assert cli_main(["fiber", "providers"]) == 0
    captured = capsys.readouterr().out
    assert "Zayo Group Metro Dark Fiber" in captured
    assert "Crown Castle Fiber Solutions" in captured

    # 2. fiber circuits
    assert cli_main(["fiber", "circuits"]) == 0
    captured = capsys.readouterr().out
    assert "Active Leased Commercial Fiber Circuits" in captured
    assert "100.0 Gbps" in captured

    # 3. fiber lease
    assert cli_main(["fiber", "lease", "--carrier", "zayo_metro", "--km", "5.0"]) == 0
    captured = capsys.readouterr().out
    assert "Successfully provisioned leased fiber circuit" in captured
    assert "Speed of light in silica" in captured

    # 4. 5g status
    assert cli_main(["5g"]) == 0
    captured = capsys.readouterr().out
    assert "5G Cellular Infrastructure & Network Slicing Status" in captured
    assert "URLLC Network Slice" in captured
    assert "Private 5G CBRS Band 48" in captured

    # 5. status card shows leased fiber & 5G
    assert cli_main(["status"]) == 0
    captured = capsys.readouterr().out
    assert "Leased Metro Fiber" in captured
    assert "5G Slices" in captured
