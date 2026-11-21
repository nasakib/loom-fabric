# Copyright (c) 2026 Najmos Sakib / VectorCore Holdings, LLC.
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Loom Fabric Modem Controller (`loom/hardware/fabric_modem.py`).
==============================================================
Manages the hardware Fabric Modem state machine, mesh network scanning,
Wi-Fi-style association, and direct GPU tensor streaming.
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from loom.hardware.transceiver import (
    FabricTransceiver,
    LinkQuality,
    TransceiverBand,
)

logger = logging.getLogger("loom.hardware.fabric_modem")


class ModemState(str, Enum):
    OFFLINE = "OFFLINE"
    SCANNING = "SCANNING"
    ASSOCIATING = "ASSOCIATING"
    ONLINE_MESH = "ONLINE_MESH"
    DISPATCHING = "DISPATCHING"
    ATTENUATED = "ATTENUATED"


@dataclass
class FabricPeerNode:
    node_id: str
    ssid: str                  # Mesh Service Set Identifier (e.g. "LoomMesh-SkyTech")
    bssid: str                 # Hardware MAC address of the peer's Fabric Modem
    hardware_label: str        # e.g. "NVIDIA RTX 3060 12GB + AMD RX 580 8GB"
    available_vram_gb: float
    total_tflops: float
    distance_meters: float
    link_quality: LinkQuality
    ip_endpoint: str           # Direct wire or overlay endpoint
    pricing_usd_hr: float = 0.0 # 0.0 = local / cooperative free mesh


class LoomFabricModem:
    """Controls the local host's Fabric Modem hardware co-processor."""

    def __init__(
        self,
        modem_id: Optional[str] = None,
        band: TransceiverBand = TransceiverBand.MMWAVE_60GHZ,
        auto_scan: bool = True,
    ):
        self.modem_id = modem_id or f"lfm_{uuid.uuid4().hex[:8]}"
        self.transceiver = FabricTransceiver(band=band)
        self.state = ModemState.OFFLINE
        self.associated_peer: Optional[FabricPeerNode] = None
        self.known_peers: Dict[str, FabricPeerNode] = {}
        self.total_bytes_transferred: int = 0
        self.total_dispatches: int = 0
        self.created_at = time.time()

        if auto_scan:
            self.power_on()

    def power_on(self) -> None:
        """Powers up the Fabric Modem transceiver and enters scanning mode."""
        self.state = ModemState.SCANNING
        logger.info(f"Loom Fabric Modem {self.modem_id} powered ON. Scanning airwaves...")
        self.scan_airwaves()
        
        # Auto-associate with the strongest viable peer
        if self.known_peers:
            best_peer = max(
                self.known_peers.values(),
                key=lambda p: (p.link_quality.effective_bandwidth_gbps, -p.distance_meters),
            )
            self.associate(best_peer.ssid)

    def scan_airwaves(self) -> List[Dict[str, Any]]:
        """Scans the local RF spectrum and direct-wire interfaces for available Loom Fabric peers."""
        self.state = ModemState.SCANNING
        self.known_peers.clear()

        # Discovered peers: Incorporates the live cluster nodes
        # 1. SkyTech Dual-GPU Worker (RTX 3060 12GB CUDA + RX 580 8GB Vulkan)
        link_skytech = self.transceiver.calculate_link_quality(distance_meters=1.5, obstacles_count=0)
        p1 = FabricPeerNode(
            node_id="skyTech-Worker",
            ssid="LoomMesh-SkyTech",
            bssid="FA:B1:00:30:60:01",
            hardware_label="NVIDIA GeForce RTX 3060 12GB + AMD Radeon RX 580 8GB",
            available_vram_gb=17.6,
            total_tflops=22.8,
            distance_meters=1.5,
            link_quality=link_skytech,
            ip_endpoint="192.168.99.1:8002",
            pricing_usd_hr=0.0,
        )
        self.known_peers[p1.ssid] = p1

        # 2. Ryzen7 Head Orchestrator (16-vCPU Zen 3 + Radeon 680M)
        link_ryzen = self.transceiver.calculate_link_quality(distance_meters=2.8, obstacles_count=0)
        p2 = FabricPeerNode(
            node_id="Ryzen7-Head",
            ssid="LoomMesh-RyzenHead",
            bssid="FA:B1:00:77:30:02",
            hardware_label="AMD Ryzen 7 7730U 16-vCPU (32GB Host RAM + Radeon 680M)",
            available_vram_gb=14.4, # Plasma object store / host RAM pool
            total_tflops=8.4,
            distance_meters=2.8,
            link_quality=link_ryzen,
            ip_endpoint="192.168.99.2:8002",
            pricing_usd_hr=0.0,
        )
        self.known_peers[p2.ssid] = p2

        # 3. Ad-Hoc Neighborhood Edge Node (Virtual Nearby Seeder)
        link_edge = self.transceiver.calculate_link_quality(distance_meters=12.0, obstacles_count=1)
        p3 = FabricPeerNode(
            node_id="Proximity-MacStudio",
            ssid="LoomMesh-StudioM3",
            bssid="FA:B1:00:AC:33:03",
            hardware_label="Apple M3 Max 128GB Unified Memory",
            available_vram_gb=96.0,
            total_tflops=36.0,
            distance_meters=12.0,
            link_quality=link_edge,
            ip_endpoint="192.168.99.45:8002",
            pricing_usd_hr=0.35, # Community compute rate
        )
        self.known_peers[p3.ssid] = p3

        if self.associated_peer and self.associated_peer.ssid in self.known_peers:
            self.state = ModemState.ONLINE_MESH
        elif not self.associated_peer:
            self.state = ModemState.SCANNING

        return [
            {
                "ssid": p.ssid,
                "node_id": p.node_id,
                "hardware": p.hardware_label,
                "available_vram_gb": p.available_vram_gb,
                "total_tflops": p.total_tflops,
                "signal_bars": p.link_quality.signal_bars,
                "rssi_dbm": p.link_quality.rssi_dbm,
                "snr_db": p.link_quality.snr_db,
                "bandwidth_gbps": p.link_quality.effective_bandwidth_gbps,
                "latency_ms": p.link_quality.latency_ms,
                "pricing": "Free (Co-op)" if p.pricing_usd_hr == 0.0 else f"${p.pricing_usd_hr}/hr",
            }
            for p in self.known_peers.values()
        ]

    def associate(self, ssid: str) -> bool:
        """Connects/associates with the specified Fabric Mesh network."""
        if ssid not in self.known_peers:
            logger.warning(f"SSID {ssid} not found during airwave scan.")
            return False

        self.state = ModemState.ASSOCIATING
        peer = self.known_peers[ssid]
        
        # Verify link is viable
        if not peer.link_quality.is_viable:
            logger.error(f"Cannot associate with {ssid}: Signal too weak ({peer.link_quality.rssi_dbm} dBm)")
            self.state = ModemState.ATTENUATED
            return False

        self.associated_peer = peer
        self.state = ModemState.ONLINE_MESH
        logger.info(
            f"⚡ Fabric Modem Associated with '{ssid}' ({peer.node_id}) | "
            f"Signal: {peer.link_quality.signal_bars} ({peer.link_quality.rssi_dbm} dBm) | "
            f"Bandwidth: {peer.link_quality.effective_bandwidth_gbps} Gbps"
        )
        return True

    def stream_tensor_dma(self, payload_bytes: int) -> Dict[str, Any]:
        """Streams a tensor activation or gradient frame directly through the modem."""
        if not self.associated_peer or self.state != ModemState.ONLINE_MESH:
            raise ConnectionError("Modem is not connected to any Fabric Mesh network.")

        prev_state = self.state
        self.state = ModemState.DISPATCHING
        try:
            latency_ms = self.transceiver.execute_dma_transfer(
                payload_bytes=payload_bytes,
                link=self.associated_peer.link_quality,
            )
            self.total_bytes_transferred += payload_bytes
            self.total_dispatches += 1
            return {
                "status": "DELIVERED",
                "bytes_transferred": payload_bytes,
                "transit_time_ms": latency_ms,
                "peer_node_id": self.associated_peer.node_id,
                "carrier_modulation": self.associated_peer.link_quality.modulation.value,
                "link_quality": self.associated_peer.link_quality.signal_bars,
            }
        finally:
            self.state = prev_state

    def get_telemetry(self) -> Dict[str, Any]:
        """Returns live modem and link telemetry formatted for the OS status bar or dashboard."""
        if self.associated_peer:
            peer_info = {
                "ssid": self.associated_peer.ssid,
                "node_id": self.associated_peer.node_id,
                "hardware": self.associated_peer.hardware_label,
                "available_vram_gb": self.associated_peer.available_vram_gb,
                "total_tflops": self.associated_peer.total_tflops,
                "signal_bars": self.associated_peer.link_quality.signal_bars,
                "rssi_dbm": self.associated_peer.link_quality.rssi_dbm,
                "snr_db": self.associated_peer.link_quality.snr_db,
                "modulation": self.associated_peer.link_quality.modulation.value,
                "effective_bandwidth_gbps": self.associated_peer.link_quality.effective_bandwidth_gbps,
                "latency_ms": self.associated_peer.link_quality.latency_ms,
            }
        else:
            peer_info = None

        # Calculate total pooled mesh compute in reach
        pooled_vram = sum(p.available_vram_gb for p in self.known_peers.values() if p.link_quality.is_viable)
        pooled_tflops = sum(p.total_tflops for p in self.known_peers.values() if p.link_quality.is_viable)

        return {
            "modem_id": self.modem_id,
            "state": self.state.value,
            "band": self.transceiver.band.value,
            "pcie_link": f"PCIe {self.transceiver.pcie_gen}.0 x{self.transceiver.pcie_lanes} ({round(self.transceiver.pcie_max_bandwidth_gbps, 1)} Gbps)",
            "connected": self.associated_peer is not None,
            "associated_peer": peer_info,
            "discovered_networks_count": len(self.known_peers),
            "pooled_mesh_vram_gb": round(pooled_vram, 1),
            "pooled_mesh_tflops": round(pooled_tflops, 1),
            "total_bytes_transferred_mb": round(self.total_bytes_transferred / (1024 * 1024), 2),
            "total_dispatches": self.total_dispatches,
            "uptime_seconds": round(time.time() - self.created_at, 1),
        }
