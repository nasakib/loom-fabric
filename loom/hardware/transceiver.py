# Copyright (c) 2026 Najmos Sakib / VectorCore Holdings, LLC.
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Loom Fabric Hardware Transceiver & Physical (PHY) Emulation Layer.
==================================================================
Simulates a dedicated Fabric Modem chip operating alongside host silicon.
Models:
1. Multi-band RF / Optical PHY (60 GHz mmWave, 5.8 GHz Wi-Fi 7, PCIe Direct).
2. Carrier metrics: RSSI (dBm), SNR (dB), Modulation (QAM-4096 to BPSK).
3. Zero-Copy Host PCIe DMA Transfer engine with hardware queue backpressure.
4. Adaptive Link Constellation based on real-time distance and attenuation.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class TransceiverBand(str, Enum):
    MMWAVE_60GHZ = "60GHz_mmWave"         # Ultra-high throughput line-of-sight (up to 40 Gbps, sub-ms)
    WIFI7_5GHZ = "5.8GHz_Wi-Fi7"          # High throughput room-to-room (up to 15 Gbps)
    PCIE_DIRECT = "PCIe_Direct_Cable"     # Direct copper/optical tether (up to 64 GB/s)
    LOOPBACK_EMU = "Loopback_PCIe4"       # Local virtual test harness
    FIBER_BIDI_100G = "100G_BiDi_Fiber"   # Dedicated single-strand optical lambda link (100 Gbps, 4.9 us/km)
    FIBER_PON_10G = "10G_XGSPON_Fiber"    # Neighborhood passive optical network (10 Gbps, sub-ms)
    CELLULAR_5G_URLLC = "5G_NR_URLLC"     # 5G Standalone Ultra-Reliable Low-Latency Slice (sub-10ms, 2.5 Gbps)
    CELLULAR_5G_CBRS = "5G_Private_CBRS"  # Private 5G Band 48 Local Small Cell Mesh (3.5 GHz, 1 Gbps)
    CELLULAR_5G_FWA = "5G_Home_FWA"       # Commercial 5G Fixed Wireless Access (T-Mobile/Verizon, 1 Gbps)


class ModulationScheme(str, Enum):
    QAM4096 = "4096-QAM" # Max SNR (>35 dB), Peak Bitrate (100% capacity)
    QAM1024 = "1024-QAM" # SNR > 28 dB (85% capacity)
    QAM256 = "256-QAM"   # SNR > 20 dB (65% capacity)
    QAM64 = "64-QAM"     # SNR > 14 dB (45% capacity)
    QPSK = "QPSK"        # SNR > 6 dB (20% capacity)
    BPSK = "BPSK"        # Severe attenuation / noise floor (5% capacity)


@dataclass
class LinkQuality:
    rssi_dbm: float               # Received Signal Strength Indicator (-30 to -95 dBm)
    snr_db: float                 # Signal-to-Noise Ratio (0 to 45 dB)
    modulation: ModulationScheme
    effective_bandwidth_gbps: float
    latency_ms: float
    packet_loss_rate: float
    signal_bars: str              # e.g. "●●●●●" (5 bars) or "●●○○○"
    backpressure_factor: float = 1.0 # 1.0 = normal, >1.0 = queue congested

    @property
    def is_viable(self) -> bool:
        return self.rssi_dbm > -88.0 and self.snr_db > 5.0 and self.packet_loss_rate < 0.15


class FabricTransceiver:
    """Emulates a physical RF / PCIe transceiver chip mounted on an add-in card or motherboard."""

    def __init__(
        self,
        device_id: str = "phy_0",
        band: TransceiverBand = TransceiverBand.MMWAVE_60GHZ,
        pcie_gen: int = 4,
        pcie_lanes: int = 16,
        tx_power_dbm: float = 23.0,
        max_dma_queue_depth: int = 32,
    ):
        self.device_id = device_id
        self.band = band
        self.pcie_gen = pcie_gen
        self.pcie_lanes = pcie_lanes
        self.tx_power_dbm = tx_power_dbm
        self.max_dma_queue_depth = max_dma_queue_depth
        self.current_queue_depth = 0

        # Theoretical PCIe Bus Capacity in GB/s
        # PCIe 4.0: ~1.969 GB/s per lane (x16 = ~31.5 GB/s)
        # PCIe 5.0: ~3.938 GB/s per lane (x16 = ~63.0 GB/s)
        bytes_per_lane_gb = 1.969 if pcie_gen == 4 else (3.938 if pcie_gen == 5 else 0.985)
        self.pcie_max_bandwidth_gbps = bytes_per_lane_gb * pcie_lanes * 8.0

        # RF / Optical / Cellular Base Bandwidth Limits
        self.rf_peak_bandwidth_gbps = {
            TransceiverBand.MMWAVE_60GHZ: 40.0,
            TransceiverBand.WIFI7_5GHZ: 15.0,
            TransceiverBand.PCIE_DIRECT: self.pcie_max_bandwidth_gbps,
            TransceiverBand.LOOPBACK_EMU: self.pcie_max_bandwidth_gbps,
            TransceiverBand.FIBER_BIDI_100G: 100.0,
            TransceiverBand.FIBER_PON_10G: 10.0,
            TransceiverBand.CELLULAR_5G_URLLC: 2.5,
            TransceiverBand.CELLULAR_5G_CBRS: 1.0,
            TransceiverBand.CELLULAR_5G_FWA: 1.0,
        }[band]

    def calculate_link_quality(
        self,
        distance_meters: float = 3.5,
        obstacles_count: int = 0,
        noise_floor_dbm: float = -95.0,
    ) -> LinkQuality:
        """Calculates link quality based on free-space path loss, optical attenuation, or PCIe bus."""
        if self.band in (TransceiverBand.PCIE_DIRECT, TransceiverBand.LOOPBACK_EMU):
            # Cabled / Direct: near-flawless signal
            rssi = -32.0
            snr = 42.0
            mod = ModulationScheme.QAM4096
            loss = 0.0
            latency = 0.35 # sub-millisecond
            bw = min(self.pcie_max_bandwidth_gbps, self.rf_peak_bandwidth_gbps)
        elif self.band in (TransceiverBand.FIBER_BIDI_100G, TransceiverBand.FIBER_PON_10G):
            # Single-mode optical fiber propagation model
            # Attenuation: 0.35 dB/km @ 1310nm single mode + 0.5 dB connector insertion loss
            dist_km = max(0.001, distance_meters / 1000.0)
            optical_loss_db = (dist_km * 0.35) + 0.5
            tx_opt_power_dbm = 3.0 # +3 dBm DFB laser
            rx_opt_power_dbm = tx_opt_power_dbm - optical_loss_db
            rssi = rx_opt_power_dbm # Optical RX power in dBm
            snr = max(10.0, 48.0 - optical_loss_db)
            mod = ModulationScheme.QAM4096 # Digital PAM4 / coherent optical constellation
            loss = 0.000001
            # Speed of light in silica: c / n = 299792 / 1.4682 = ~204,190 km/s -> ~4.897 us/km
            fiber_delay_ms = dist_km * 0.0049
            phy_serdes_ms = 0.12 # SerDes framing + KP4 RS(544,514) FEC latency
            latency = phy_serdes_ms + fiber_delay_ms
            bw = self.rf_peak_bandwidth_gbps
        elif self.band in (TransceiverBand.CELLULAR_5G_URLLC, TransceiverBand.CELLULAR_5G_CBRS, TransceiverBand.CELLULAR_5G_FWA):
            # 5G Cellular NR & CBRS Model
            if self.band == TransceiverBand.CELLULAR_5G_URLLC:
                # 3GPP Rel-16 Standalone Low-Latency Slice (5QI 82/83)
                rssi = -58.0 # Strong RSRP dBm
                snr = 32.0
                mod = ModulationScheme.QAM256
                loss = 0.00001
                latency = 6.5 # sub-10ms air interface
                bw = 2.5
            elif self.band == TransceiverBand.CELLULAR_5G_CBRS:
                # Private 5G Band 48 Local Small Cell
                rssi = -72.0
                snr = 24.0
                mod = ModulationScheme.QAM256
                loss = 0.0001
                latency = 9.5
                bw = 1.0
            else: # CELLULAR_5G_FWA
                # Commercial Mid-band 5G Fixed Wireless Access (T-Mobile / Verizon)
                rssi = -80.0
                snr = 18.0
                mod = ModulationScheme.QAM64
                loss = 0.001
                latency = 18.0
                bw = 0.85
        else:
            # Wireless RF propagation model
            # Free-space path loss (FSPL) in dB: FSPL = 20*log10(d) + 20*log10(f) + 32.44
            freq_ghz = 60.0 if self.band == TransceiverBand.MMWAVE_60GHZ else 5.8
            d_clamped = max(distance_meters, 0.5)
            fspl = 20.0 * math.log10(d_clamped) + 20.0 * math.log10(freq_ghz * 1000.0) - 27.55
            
            # Attenuation per wall/obstacle
            obstacle_penalty = obstacles_count * (18.0 if self.band == TransceiverBand.MMWAVE_60GHZ else 5.0)
            
            rssi = self.tx_power_dbm - fspl - obstacle_penalty
            rssi = max(-105.0, min(-25.0, rssi))
            snr = max(0.0, rssi - noise_floor_dbm)

            # Modulation selection by SNR
            if snr >= 34.0:
                mod = ModulationScheme.QAM4096
                eff_factor = 1.0
                loss = 0.0001
                latency = 0.8
            elif snr >= 26.0:
                mod = ModulationScheme.QAM1024
                eff_factor = 0.82
                loss = 0.001
                latency = 1.2
            elif snr >= 18.0:
                mod = ModulationScheme.QAM256
                eff_factor = 0.62
                loss = 0.005
                latency = 1.8
            elif snr >= 12.0:
                mod = ModulationScheme.QAM64
                eff_factor = 0.40
                loss = 0.02
                latency = 2.6
            elif snr >= 6.0:
                mod = ModulationScheme.QPSK
                eff_factor = 0.18
                loss = 0.06
                latency = 4.5
            else:
                mod = ModulationScheme.BPSK
                eff_factor = 0.05
                loss = 0.18
                latency = 9.0

            # Effective bandwidth is bounded by RF link and host PCIe slot
            rf_bw = self.rf_peak_bandwidth_gbps * eff_factor
            bw = min(rf_bw, self.pcie_max_bandwidth_gbps)

        # Queue backpressure adjustment
        bp_factor = 1.0 + (self.current_queue_depth / max(1, self.max_dma_queue_depth)) * 0.5
        latency *= bp_factor

        # Generate visual Wi-Fi style bars
        if rssi >= -50.0:
            bars = "●●●●●" # 5 bars
        elif rssi >= -62.0:
            bars = "●●●●○" # 4 bars
        elif rssi >= -74.0:
            bars = "●●●○○" # 3 bars
        elif rssi >= -84.0:
            bars = "●●○○○" # 2 bars
        elif rssi >= -92.0:
            bars = "●○○○○" # 1 bar
        else:
            bars = "○○○○○" # 0 bars / out of range

        return LinkQuality(
            rssi_dbm=round(rssi, 1),
            snr_db=round(snr, 1),
            modulation=mod,
            effective_bandwidth_gbps=round(bw, 2),
            latency_ms=round(latency, 2),
            packet_loss_rate=round(loss, 4),
            signal_bars=bars,
            backpressure_factor=round(bp_factor, 2),
        )

    def execute_dma_transfer(self, payload_bytes: int, link: LinkQuality) -> float:
        """Simulates zero-copy direct memory transfer over PCIe to the RF transceiver.
        Returns the hardware transmission latency in milliseconds with backpressure accounting.
        """
        if not link.is_viable:
            raise ConnectionError(f"Fabric Link not viable: RSSI={link.rssi_dbm} dBm, Loss={link.packet_loss_rate*100}%")
        
        # Enforce queue limit to prevent DMA buffer starvation
        if self.current_queue_depth >= self.max_dma_queue_depth:
            # Backpressure throttle: wait for virtual slot
            throttle_penalty_ms = 5.0 * (self.current_queue_depth - self.max_dma_queue_depth + 1)
        else:
            throttle_penalty_ms = 0.0

        self.current_queue_depth += 1
        try:
            # Bytes -> Bits -> Gigabits
            payload_gigabits = (payload_bytes * 8.0) / 1e9
            transfer_seconds = payload_gigabits / max(0.001, link.effective_bandwidth_gbps)
            total_time_ms = link.latency_ms + (transfer_seconds * 1000.0) + throttle_penalty_ms
            return round(total_time_ms, 3)
        finally:
            self.current_queue_depth = max(0, self.current_queue_depth - 1)
