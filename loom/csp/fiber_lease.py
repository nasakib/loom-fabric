# Copyright (c) 2026 Najmos Sakib / VectorCore Holdings, LLC.
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Existing Fiber Infrastructure Leasing & Brokerage Subsystem (`loom/csp/fiber_lease.py`).
======================================================================================
Enables ClothOS to lease, rent, and orchestrate existing commercial dark fiber,
lit DWDM alien wavelengths, municipal open-access networks, and coexistence PON
overlays instead of trenching new physical fiber from scratch.

Supported Infrastructure Models:
1. Dark Fiber IRU / Monthly Strand Lease (Zayo, Crown Castle, Lumen, neutral middle-mile).
2. DWDM Alien Wavelength (10G/25G/100G optical lambda on existing carrier ROADM lines).
3. Municipal Open-Access Networks (OAN) (UTOPIA Fiber, Ammon Fiber, EPB, electric co-ops).
4. WDM-PON Coexistence Overlay (Utilizing NGPON2 unlit wavelength windows on existing GPON/XGS-PON drops).
5. Metro Ethernet E-Line Layer 2 Virtual Private Circuit.
"""

from __future__ import annotations

import enum
import hashlib
import json
import logging
import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger("loom.csp.fiber_lease")


class FiberLeaseType(str, enum.Enum):
    DARK_FIBER_STRAND = "DARK_FIBER_STRAND"             # Unlit single-mode strand leased monthly ($200-$600/mo)
    DARK_FIBER_IRU = "DARK_FIBER_IRU"                   # Long-term Indefeasible Right of Use (10-20 yr upfront)
    DWDM_ALIEN_WAVELENGTH = "DWDM_ALIEN_WAVELENGTH"     # Dedicated 100G/25G optical channel on carrier ROADM
    MUNICIPAL_OPEN_ACCESS = "MUNICIPAL_OPEN_ACCESS"     # Layer 1/2 lease on city fiber (UTOPIA, EPB, Co-op)
    WDM_PON_COEXISTENCE = "WDM_PON_COEXISTENCE"         # NGPON2 overlay lambda on existing residential drop
    METRO_E_LINE = "METRO_E_LINE"                       # Carrier Ethernet Layer 2 point-to-point circuit


class FiberCarrierTier(str, enum.Enum):
    TIER_1_NATIONAL = "TIER_1_NATIONAL"                 # National fiber backbones (Zayo, Lumen, Crown Castle)
    REGIONAL_MIDDLE_MILE = "REGIONAL_MIDDLE_MILE"       # State/regional optical transport networks
    MUNICIPAL_OPEN_ACCESS = "MUNICIPAL_OPEN_ACCESS"     # City/utility-owned open fiber infrastructure
    ELECTRIC_COOPERATIVE = "ELECTRIC_COOPERATIVE"       # Rural/suburban electric co-op broadband fiber


@dataclass
class FiberCarrier:
    """Represents a commercial or municipal fiber infrastructure provider."""
    carrier_id: str
    name: str
    tier: FiberCarrierTier
    supported_lease_types: List[FiberLeaseType]
    coverage_geohashes: List[str]                      # Spatial coverage area (e.g. 'dn5bpq' for Atlanta)
    metro_presence: str                                # e.g. "Atlanta Metro / Inman Park / Midtown"
    typical_strand_cost_usd_mo: float                  # Average cost per strand-mile per month
    minimum_lease_term_months: int = 1
    carrier_sla_availability_pct: float = 99.999
    supports_alien_wave: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "carrier_id": self.carrier_id,
            "name": self.name,
            "tier": self.tier.value,
            "supported_lease_types": [t.value for t in self.supported_lease_types],
            "metro_presence": self.metro_presence,
            "typical_strand_cost_usd_mo": self.typical_strand_cost_usd_mo,
            "minimum_term_months": self.minimum_lease_term_months,
            "sla": f"{self.carrier_sla_availability_pct}%",
            "supports_alien_wave": self.supports_alien_wave,
        }


@dataclass
class LeasedFiberCircuit:
    """An active or provisioned leased fiber circuit connecting ClothOS nodes."""
    circuit_id: str
    carrier_id: str
    carrier_name: str
    lease_type: FiberLeaseType
    endpoint_a_node_id: str
    endpoint_b_node_id: str
    physical_length_km: float
    committed_bandwidth_gbps: float
    optical_wavelength_nm: Optional[float]              # e.g. 1310.0, 1550.12 (DWDM ch 34), or 1270/1330 BiDi
    monthly_lease_cost_usd: float
    hourly_amortized_cost_usd: float
    optical_propagation_latency_ms: float               # Calculated from physical fiber length (4.897 us/km)
    is_active: bool = True
    provisioned_epoch: float = field(default_factory=time.time)
    contract_expiration_epoch: float = field(default_factory=lambda: time.time() + (30 * 86400))
    circuit_telemetry: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        carrier: FiberCarrier,
        lease_type: FiberLeaseType,
        endpoint_a: str,
        endpoint_b: str,
        length_km: float,
        bandwidth_gbps: float = 100.0,
        monthly_cost_usd: Optional[float] = None,
        wavelength_nm: Optional[float] = None,
    ) -> LeasedFiberCircuit:
        circuit_id = f"cir-sl-{uuid.uuid4().hex[:10]}"
        cost = monthly_cost_usd if monthly_cost_usd is not None else (carrier.typical_strand_cost_usd_mo * max(1.0, length_km))
        hourly_cost = round(cost / (30.0 * 24.0), 4)
        # Propagation latency in silica: ~4.897 us/km -> 0.004897 ms/km
        prop_latency = round(length_km * 0.004897, 4)
        return cls(
            circuit_id=circuit_id,
            carrier_id=carrier.carrier_id,
            carrier_name=carrier.name,
            lease_type=lease_type,
            endpoint_a_node_id=endpoint_a,
            endpoint_b_node_id=endpoint_b,
            physical_length_km=length_km,
            committed_bandwidth_gbps=bandwidth_gbps,
            optical_wavelength_nm=wavelength_nm or (1310.0 if lease_type == FiberLeaseType.DARK_FIBER_STRAND else 1550.12),
            monthly_lease_cost_usd=round(cost, 2),
            hourly_amortized_cost_usd=hourly_cost,
            optical_propagation_latency_ms=prop_latency,
            circuit_telemetry={
                "rx_power_dbm": -2.5,
                "tx_power_dbm": 3.0,
                "optical_snr_db": 44.0,
                "bit_error_rate": 1e-12,
                "laser_temperature_c": 38.5,
            },
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "circuit_id": self.circuit_id,
            "carrier": self.carrier_name,
            "lease_type": self.lease_type.value,
            "route": f"{self.endpoint_a_node_id} <──({self.physical_length_km} km)──> {self.endpoint_b_node_id}",
            "bandwidth_gbps": self.committed_bandwidth_gbps,
            "optical_wavelength": f"{self.optical_wavelength_nm} nm" if self.optical_wavelength_nm else "Broadband SMF",
            "latency_ms": self.optical_propagation_latency_ms,
            "monthly_cost_usd": f"${self.monthly_lease_cost_usd:.2f}",
            "hourly_amortized_usd": f"${self.hourly_amortized_cost_usd:.4f}",
            "status": "ONLINE_ACTIVE" if self.is_active else "SUSPENDED",
        }


class FiberLeaseManager:
    """
    Manages discovery, provisioning, and gas-tax amortization of existing
    commercial and municipal fiber assets.
    """

    def __init__(self, persistence_file: Optional[str] = "data/fiber_leases.json"):
        self.persistence_file = persistence_file
        self.known_carriers: Dict[str, FiberCarrier] = {}
        self.active_circuits: Dict[str, LeasedFiberCircuit] = {}
        self._initialize_catalog()
        self._load_state()

    def _initialize_catalog(self) -> None:
        """Seeds real-world commercial dark fiber and open-access networks."""
        # 1. Zayo Metro Dark Fiber (Tier 1 National)
        self.known_carriers["zayo_metro"] = FiberCarrier(
            carrier_id="zayo_metro",
            name="Zayo Group Metro Dark Fiber",
            tier=FiberCarrierTier.TIER_1_NATIONAL,
            supported_lease_types=[FiberLeaseType.DARK_FIBER_STRAND, FiberLeaseType.DWDM_ALIEN_WAVELENGTH, FiberLeaseType.DARK_FIBER_IRU],
            coverage_geohashes=["dn5bpq", "dn5", "dnh", "dr5", "9q8"],
            metro_presence="Atlanta, NYC, Dallas, Chicago, SF Bay Area, Seattle",
            typical_strand_cost_usd_mo=320.0,
            minimum_lease_term_months=1,
            supports_alien_wave=True,
        )
        # 2. Crown Castle Fiber (Neutral Middle-Mile & Small Cell Backbone)
        self.known_carriers["crown_castle"] = FiberCarrier(
            carrier_id="crown_castle",
            name="Crown Castle Fiber Solutions",
            tier=FiberCarrierTier.TIER_1_NATIONAL,
            supported_lease_types=[FiberLeaseType.DARK_FIBER_STRAND, FiberLeaseType.METRO_E_LINE, FiberLeaseType.DWDM_ALIEN_WAVELENGTH],
            coverage_geohashes=["dn5bpq", "dn5", "dj7", "c20"],
            metro_presence="Atlanta (56 Marietta / Tech Square), Boston, Houston",
            typical_strand_cost_usd_mo=285.0,
            minimum_lease_term_months=1,
            supports_alien_wave=True,
        )
        # 3. Municipal Open-Access Network (UTOPIA / Municipal Utility Model)
        self.known_carriers["open_access_metro"] = FiberCarrier(
            carrier_id="open_access_metro",
            name="Municipal Open Access Fiber Network (UTOPIA / Ammon / EPB Model)",
            tier=FiberCarrierTier.MUNICIPAL_OPEN_ACCESS,
            supported_lease_types=[FiberLeaseType.MUNICIPAL_OPEN_ACCESS, FiberLeaseType.WDM_PON_COEXISTENCE, FiberLeaseType.DARK_FIBER_STRAND],
            coverage_geohashes=["dn5bpq", "9x0", "9xj", "dn7"],
            metro_presence="Metro Open-Access Rings & Municipal Utility Conduits",
            typical_strand_cost_usd_mo=145.0,
            minimum_lease_term_months=1,
            supports_alien_wave=False,
        )
        # 4. Regional Electric Cooperative Broadband (Rural / Suburban Middle-Mile)
        self.known_carriers["coop_fiber"] = FiberCarrier(
            carrier_id="coop_fiber",
            name="Regional Electric Cooperative Fiber (EMC / Co-op)",
            tier=FiberCarrierTier.ELECTRIC_COOPERATIVE,
            supported_lease_types=[FiberLeaseType.DARK_FIBER_STRAND, FiberLeaseType.WDM_PON_COEXISTENCE],
            coverage_geohashes=["dn5", "dnh", "dnh0"],
            metro_presence="Suburban & Exurban Co-op Electric Rights-of-Way",
            typical_strand_cost_usd_mo=95.0,
            minimum_lease_term_months=1,
            supports_alien_wave=False,
        )

        # Default Active Leased Circuit: Primary Metro Interconnect connecting local nodes to neighborhood fiber anchor
        default_circuit = LeasedFiberCircuit.create(
            carrier=self.known_carriers["zayo_metro"],
            lease_type=FiberLeaseType.DARK_FIBER_STRAND,
            endpoint_a="skyTech-Worker",
            endpoint_b="Ryzen7-Head",
            length_km=2.4,
            bandwidth_gbps=100.0,
            monthly_cost_usd=250.0,
            wavelength_nm=1310.0,
        )
        self.active_circuits[default_circuit.circuit_id] = default_circuit

    def get_available_carriers(self, geohash: str = "dn5bpq") -> List[FiberCarrier]:
        """Filters fiber providers covering the node's geographic coordinates."""
        matching = []
        for carrier in self.known_carriers.values():
            if any(geohash.startswith(prefix) or prefix.startswith(geohash[:3]) for prefix in carrier.coverage_geohashes):
                matching.append(carrier)
        return matching or list(self.known_carriers.values())

    def provision_lease(
        self,
        carrier_id: str,
        lease_type: FiberLeaseType,
        endpoint_a: str,
        endpoint_b: str,
        length_km: float = 3.5,
        bandwidth_gbps: float = 100.0,
    ) -> LeasedFiberCircuit:
        """
        Provisions a lease on existing commercial fiber infrastructure.
        Generates an active circuit record and calculates amortized gas surcharges.
        """
        carrier = self.known_carriers.get(carrier_id)
        if not carrier:
            raise KeyError(f"Fiber carrier '{carrier_id}' not found in registry.")

        if lease_type not in carrier.supported_lease_types:
            raise ValueError(f"Carrier {carrier.name} does not support lease type {lease_type.value}.")

        circuit = LeasedFiberCircuit.create(
            carrier=carrier,
            lease_type=lease_type,
            endpoint_a=endpoint_a,
            endpoint_b=endpoint_b,
            length_km=length_km,
            bandwidth_gbps=bandwidth_gbps,
        )

        self.active_circuits[circuit.circuit_id] = circuit
        self._save_state()
        logger.info(
            f"Fiber Lease Provisioned: Circuit {circuit.circuit_id} via {carrier.name} "
            f"({circuit.physical_length_km} km, ${circuit.monthly_lease_cost_usd}/mo, ${circuit.hourly_amortized_cost_usd}/hr)"
        )
        return circuit

    def calculate_compute_lease_surcharge(self, duration_seconds: float) -> float:
        """
        Calculates the amortized fiber lease surcharge to include in the Spotlight-Local gas bill.
        Amortizes monthly fiber leases into microsecond compute jobs.
        """
        total_hourly_lease = sum(c.hourly_amortized_cost_usd for c in self.active_circuits.values() if c.is_active)
        hours = duration_seconds / 3600.0
        # Assume costs are distributed across an active pool of 10 concurrent compute streams
        pool_concurrency = max(1, len(self.active_circuits) * 5)
        job_surcharge_usd = (total_hourly_lease * hours) / pool_concurrency
        return round(job_surcharge_usd, 6)

    def _save_state(self) -> None:
        if not self.persistence_file:
            return
        try:
            from pathlib import Path
            from loom.fabric.state_store import state_store
            data = {
                "active_circuits": {k: asdict(v) for k, v in self.active_circuits.items()}
            }
            state_store.set_state("fiber_leases", data)
        except Exception as e:
            logger.debug(f"Fiber lease state save skipped: {e}")

    def _load_state(self) -> None:
        if not self.persistence_file:
            return
        try:
            from pathlib import Path
            from loom.fabric.state_store import state_store
            data = state_store.get_state("fiber_leases", legacy_path=Path(self.persistence_file))
            if "active_circuits" in data:
                self.active_circuits.clear()
                for k, v in data["active_circuits"].items():
                    v["lease_type"] = FiberLeaseType(v["lease_type"])
                    self.active_circuits[k] = LeasedFiberCircuit(**v)
        except Exception as e:
            logger.debug(f"Fiber lease state load skipped: {e}")
