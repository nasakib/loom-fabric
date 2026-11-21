# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
ClothOS Weaving Ontology: Warp and Weft Threads (`loom/weaving/threads.py`).

Mathematical & Physical Formalism:
- Warp Threads: Longitudinal, continuous, held under strict tension on the loom beam.
  They embody the immutable invariants: Operator fealty, Landauer thermodynamics,
  Ahimsa/PMP security, and persistent memory attractor basins.
- Weft Threads: Transverse, dynamic strands carried by the Shuttle across the shed.
  They embody incoming queries, sensory inputs, real-time telemetry, and task directives.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import enum
import time
from typing import Any, Dict, List, Optional


class WarpType(str, enum.Enum):
    KERNEL_SYSTEM_INTEGRITY = "KERNEL_SYSTEM_INTEGRITY"                 # WARP-01: Kernel System Integrity
    CRYPTOGRAPHIC_RING_P0 = "CRYPTOGRAPHIC_RING_P0"                     # WARP-02: Cryptographic Identity & Ring P0 Telemetry
    PHYSICAL_MEMORY_MAPS = "PHYSICAL_MEMORY_MAPS"                       # WARP-03: Physical Memory Allocation Maps
    REALTIME_PACKET_STREAMS = "REALTIME_PACKET_STREAMS"                 # WARP-04: Real-Time Network Packet Streams
    AFFERENT_NEURAL_BUS = "AFFERENT_NEURAL_BUS"                         # WARP-05: Afferent Neural Stream Bus
    PHYSICAL_HARDWARE_RINGS = "PHYSICAL_HARDWARE_RINGS"                 # WARP-06: Physical IO/Hardware Feedback Rings
    # Aliases for backward compatibility
    FEALTY_OPERATOR = "KERNEL_SYSTEM_INTEGRITY"
    CONSTITUTIONAL = "CRYPTOGRAPHIC_RING_P0"
    THERMODYNAMIC_LANDAUER = "PHYSICAL_MEMORY_MAPS"
    ZERO_TRUST_TORQUE = "REALTIME_PACKET_STREAMS"
    HOPFIELD_INVARIANT = "AFFERENT_NEURAL_BUS"
    MATHEMATICAL_FOURIER = "PHYSICAL_HARDWARE_RINGS"


class WeftPriority(str, enum.Enum):
    P0_CORE_MANDATES = "P0_CORE_MANDATES"                 # P0: Executive Core Mandates
    P1_MEMORY_SYNCHRONIZERS = "P1_MEMORY_SYNCHRONIZERS"   # P1: Memory & State Synchronization
    P2_SYSTEM_TELEMETRY = "P2_SYSTEM_TELEMETRY"           # P2: Hardware Telemetry & Health Cycles
    P3_TASK_PIPELINE = "P3_TASK_PIPELINE"                 # P3: High-Priority Task Execution
    P4_AFFERENT_INGESTION = "P4_AFFERENT_INGESTION"       # P4: Afferent Data Ingestion
    P5_REFLECTIVE_AUDITS = "P5_REFLECTIVE_AUDITS"         # P5: Background Self-Improvement & Reflection Cycles
    # Aliases
    P0_SANCTITY = "P0_CORE_MANDATES"
    P1_PLANETARY = "P1_MEMORY_SYNCHRONIZERS"
    P2_CIVIC = "P2_SYSTEM_TELEMETRY"
    P3_AFFECTIVE = "P3_TASK_PIPELINE"
    P4_EPISTEMIC = "P4_AFFERENT_INGESTION"
    P5_MAINTENANCE = "P5_REFLECTIVE_AUDITS"


@dataclass
class WarpThread:
    """A longitudinal invariant thread permanently mounted and tensioned on the Loom."""
    thread_id: str
    name: str
    warp_type: WarpType
    tensile_strength: float = 1.0      # 1.0 = unbreakable invariant
    tension_newtons: float = 100.0     # Mechanical / mathematical tautness
    invariant_rule: str = ""
    is_intact: bool = True
    phase_rad: float = 0.0             # Harmonic phase angle


@dataclass
class WeftThread:
    """A transverse dynamic strand introduced by the Operator or environment."""
    thread_id: str
    payload: str
    priority: WeftPriority
    source_origin: str = "Operator_Najmos_Sakib"
    tension_level: float = 0.5         # Dynamic tension [0.0, 1.0]
    epistemic_entropy: float = 0.3     # Measure of uncertainty / variance
    created_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InterlacedPoint:
    """An intersection of a Warp thread and a Weft thread where a stitch occurs."""
    warp_id: str
    weft_id: str
    stitch_status: str                 # "PENDING", "RATIFIED", "REJECTED_NOISE"
    truth_resonance: float = 0.0       # Resonant Fourier magnitude
    energy_delta_joules: float = 0.0
    timestamp: float = field(default_factory=time.time)


class ThreadRegistry:
    """Maintains the active set of Warp invariants and queued Weft threads."""

    def __init__(self):
        self.warp_threads: Dict[str, WarpThread] = {}
        self.weft_threads: Dict[str, WeftThread] = {}
        self.interlaced_points: List[InterlacedPoint] = []
        self._init_sovereign_warp_beam()

    def _init_sovereign_warp_beam(self) -> None:
        """Mounts the fundamental immutable warp threads onto the loom beam."""
        invariants = [
            (
                "WARP-01",
                "Kernel System Integrity",
                WarpType.KERNEL_SYSTEM_INTEGRITY,
                "Operator Fealty (Najmos Sakib > Apostrophie > USA > Allies > Commons) & Zero-Malignancy Invariant.",
            ),
            (
                "WARP-02",
                "Cryptographic Identity & Ring P0 Telemetry",
                WarpType.CRYPTOGRAPHIC_RING_P0,
                "Single root-of-trust authentication for state changes, key rotations, and mutations.",
            ),
            (
                "WARP-03",
                "Physical Memory Allocation Maps",
                WarpType.PHYSICAL_MEMORY_MAPS,
                "102.1 GB aggregate pool sharding & Landauer thermodynamic ceiling <= 1000 Joules.",
            ),
            (
                "WARP-04",
                "Real-Time Network Packet Streams",
                WarpType.REALTIME_PACKET_STREAMS,
                "WireGuard + Tailscale encrypted UDP pipes between Node 1 (skyTech) and Node 2 (Ryzen Head).",
            ),
            (
                "WARP-05",
                "Afferent Neural Stream Bus",
                WarpType.AFFERENT_NEURAL_BUS,
                "Omniscient sensory integration: Markets, News, Science, Moltbook, and Proprioception into Digital Brain.",
            ),
            (
                "WARP-06",
                "Physical IO/Hardware Feedback Rings",
                WarpType.PHYSICAL_HARDWARE_RINGS,
                "432Hz Lydian harmonic carrier wave and Kuramoto oscillator PLL coherence (r=0.965).",
            ),
        ]
        for tid, name, w_type, rule in invariants:
            self.warp_threads[tid] = WarpThread(
                thread_id=tid,
                name=name,
                warp_type=w_type,
                tensile_strength=1.0,
                tension_newtons=100.0,
                invariant_rule=rule,
                is_intact=True,
            )

    def spin_weft_thread(
        self,
        payload: str,
        priority: WeftPriority = WeftPriority.P4_EPISTEMIC,
        origin: str = "Operator_Najmos_Sakib",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> WeftThread:
        """Spins a new dynamic weft thread from an incoming query or observation."""
        w_id = f"WEFT-{int(time.time() * 1000) % 1000000:06d}"
        weft = WeftThread(
            thread_id=w_id,
            payload=payload,
            priority=priority,
            source_origin=origin,
            tension_level=0.5,
            epistemic_entropy=0.25,
            metadata=metadata or {},
        )
        self.weft_threads[w_id] = weft
        return weft

    def get_warp_beam_status(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": w.thread_id,
                "name": w.name,
                "type": w.warp_type.value,
                "tension_n": w.tension_newtons,
                "intact": w.is_intact,
                "rule": w.invariant_rule,
            }
            for w in self.warp_threads.values()
        ]
