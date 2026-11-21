# Copyright (c) 2026 Najmos Sakib / VectorCore Holdings, LLC.
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Automated Verification Suite for the Loom Fabric Modem & Seamless Mesh Router.
==============================================================================
Tests:
1. Physical Transceiver RF propagation, SNR, and modulation degradation.
2. Fabric Modem beaconing, peer scanning, and association.
3. Zero-Copy DMA tensor streaming over simulated PCIe.
4. SeamlessComputeGateway default routing.
5. FastAPI REST endpoints on /v1/fabric/modem/*.
"""

import pytest
from fastapi.testclient import TestClient

from loom.hardware.transceiver import (
    FabricTransceiver,
    LinkQuality,
    ModulationScheme,
    TransceiverBand,
)
from loom.hardware.fabric_modem import (
    FabricPeerNode,
    LoomFabricModem,
    ModemState,
)
from loom.hardware.seamless_gateway import (
    SeamlessComputeGateway,
    SeamlessComputeRequest,
    SeamlessComputeResult,
)
from loom.gateway.app import app


def test_transceiver_rf_propagation_and_bars():
    phy = FabricTransceiver(band=TransceiverBand.MMWAVE_60GHZ)
    
    # 1. Close proximity (1 meter, no obstacles) -> Strong signal (5 bars)
    l1 = phy.calculate_link_quality(distance_meters=1.0, obstacles_count=0)
    assert l1.is_viable is True
    assert l1.signal_bars == "●●●●●"
    assert l1.snr_db > 30.0
    assert l1.modulation == ModulationScheme.QAM4096
    assert l1.effective_bandwidth_gbps >= 30.0

    # 2. Medium distance (10 meters, 1 obstacle) -> Attenuated signal
    l2 = phy.calculate_link_quality(distance_meters=10.0, obstacles_count=1)
    assert l2.rssi_dbm < l1.rssi_dbm
    assert l2.effective_bandwidth_gbps < l1.effective_bandwidth_gbps

    # 3. Direct PCIe cable -> Maximum throughput and sub-millisecond latency
    phy_cable = FabricTransceiver(band=TransceiverBand.PCIE_DIRECT)
    l_cable = phy_cable.calculate_link_quality()
    assert l_cable.latency_ms <= 0.5
    assert l_cable.signal_bars == "●●●●●"


def test_zero_copy_dma_transfer():
    phy = FabricTransceiver(band=TransceiverBand.MMWAVE_60GHZ)
    link = phy.calculate_link_quality(distance_meters=2.0)
    
    # Transfer 10MB tensor activation buffer
    payload_size = 10 * 1024 * 1024
    transfer_ms = phy.execute_dma_transfer(payload_size, link)
    assert transfer_ms > 0.0
    assert transfer_ms < 20.0 # Under 20ms over 40 Gbps link


def test_fabric_modem_scan_and_association():
    modem = LoomFabricModem(auto_scan=False)
    assert modem.state == ModemState.OFFLINE

    # Scan airwaves
    networks = modem.scan_airwaves()
    assert len(networks) >= 2
    ssids = [n["ssid"] for n in networks]
    assert "LoomMesh-SkyTech" in ssids
    assert "LoomMesh-RyzenHead" in ssids

    # Associate with SkyTech
    success = modem.associate("LoomMesh-SkyTech")
    assert success is True
    assert modem.state == ModemState.ONLINE_MESH
    assert modem.associated_peer is not None
    assert modem.associated_peer.node_id == "skyTech-Worker"

    # Verify telemetry
    telem = modem.get_telemetry()
    assert telem["connected"] is True
    assert telem["associated_peer"]["ssid"] == "LoomMesh-SkyTech"
    assert telem["pooled_mesh_vram_gb"] > 0.0


def test_seamless_compute_dispatch():
    gw = SeamlessComputeGateway()
    # Ensure modem is online
    gw.modem.associate("LoomMesh-SkyTech")

    result = gw.dispatch(
        prompt_or_payload="Explain how Fabric Mesh mimics Wi-Fi routing",
        target_model="auto",
        required_vram_gb=4.0,
    )
    assert result.status == "SUCCESS"
    assert "Fabric Mesh" in result.execution_route
    assert "LoomMesh-SkyTech" in result.execution_route
    assert result.total_latency_ms > 0.0
    assert result.dma_transit_time_ms > 0.0
    assert len(result.result_text) > 0

    # Verify formatted card
    card = gw.get_mesh_status_card()
    assert "FABRIC COMPUTE MESH: CONNECTED" in card
    assert "LoomMesh-SkyTech" in card


def test_seamless_offline_fallback():
    modem = LoomFabricModem(auto_scan=False)
    modem.state = ModemState.OFFLINE
    gw = SeamlessComputeGateway(modem=modem)

    result = gw.dispatch(
        prompt_or_payload="Isolated query",
        required_vram_gb=2.0,
    )
    assert result.status == "OFFLINE_FALLBACK"
    assert "Local Fallback" in result.execution_route
    assert result.carrier_link_bars == "○○○○○"


def test_fastapi_modem_endpoints():
    client = TestClient(app)

    # 1. GET /v1/fabric/modem/status
    r_status = client.get("/v1/fabric/modem/status")
    assert r_status.status_code == 200
    assert "state" in r_status.json()
    assert "pcie_link" in r_status.json()

    # 2. GET /v1/fabric/modem/scan
    r_scan = client.get("/v1/fabric/modem/scan")
    assert r_scan.status_code == 200
    assert isinstance(r_scan.json(), list)
    assert len(r_scan.json()) >= 2

    # 3. POST /v1/fabric/modem/connect
    r_connect = client.post("/v1/fabric/modem/connect", json={"ssid": "LoomMesh-SkyTech"})
    assert r_connect.status_code == 200
    assert r_connect.json()["status"] == "connected"

    # 4. POST /v1/fabric/modem/dispatch
    r_dispatch = client.post("/v1/fabric/modem/dispatch", json={
        "prompt": "Evaluate Landauer dissipation across distributed mesh",
        "model": "auto",
        "required_vram_gb": 4.0,
        "workload_type": "llm_inference"
    })
    assert r_dispatch.status_code == 200
    assert r_dispatch.json()["status"] == "SUCCESS"
    assert "route" in r_dispatch.json()
    assert "total_latency_ms" in r_dispatch.json()

    # 5. GET /v1/fabric/modem/card
    r_card = client.get("/v1/fabric/modem/card")
    assert r_card.status_code == 200
    assert "FABRIC COMPUTE MESH" in r_card.json()["card"]
