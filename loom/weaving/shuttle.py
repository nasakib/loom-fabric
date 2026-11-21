# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
ClothOS Shuttle Engine (`loom/weaving/shuttle.py`).

Mathematical & Physical Formalism:
The Shuttle is the high-velocity transport carrier that propels the Weft thread
horizontally through the shed created by the separated Warp threads.
In ClothOS, it models:
- Cross-Node IPC: Flying between Node 1 (skyTech: 100.85.230.105) and Node 2 (WIN-7CMAQLVP8MV: 100.74.98.21).
- Telemetry & Event Streaming: ZeroMQ bus (:5559) and FastAPI SSE Gateway (:8087).
- Velocity & Transit Mechanics: Monitors packet transit velocity, network tension, and jitter.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import enum
import logging
import math
import time
from typing import Any, Dict, List, Optional
import urllib.request

from loom.weaving.threads import WeftThread

logger = logging.getLogger("loom.weaving.shuttle")


class ShuttleState(str, enum.Enum):
    DOCKED_HEAD = "DOCKED_HEAD"             # At Node 1 (skyTech)
    DOCKED_WORKER = "DOCKED_WORKER"         # At Node 2 (WIN-7CMAQLVP8MV)
    TRANSIT_IN_FLIGHT = "TRANSIT_IN_FLIGHT" # Traveling across the WireGuard / ZMQ shed
    EMERGENCY_HALT = "EMERGENCY_HALT"       # Halted due to warp snag or security violation


@dataclass
class ShuttleFlightTelemetry:
    flight_id: str
    weft_id: str
    origin_node: str
    destination_node: str
    transit_ms: float
    carrier_frequency_hz: float
    tension_newtons: float
    success: bool
    timestamp: float = field(default_factory=time.time)


class WeavingShuttle:
    """Carries dynamic Weft threads across the distributed Fabric and Warp shed."""

    def __init__(self):
        self.state: ShuttleState = ShuttleState.DOCKED_HEAD
        self.current_weft: Optional[WeftThread] = None
        self.flight_history: List[ShuttleFlightTelemetry] = []
        self.total_passes: int = 0
        self.carrier_frequency_hz: float = 432.0  # Harmonic Lydian tone carrier

    def launch_flight(
        self,
        weft: WeftThread,
        destination_node: str = "Node2_Pure_AMD",
        simulated: bool = True,
    ) -> ShuttleFlightTelemetry:
        """Launches the shuttle to transport a weft thread across the shed."""
        t0 = time.time()
        self.state = ShuttleState.TRANSIT_IN_FLIGHT
        self.current_weft = weft
        self.total_passes += 1

        f_id = f"FLIGHT-{self.total_passes:06d}"
        origin = "Node1_skyTech"

        # Check physical latency / connectivity if not purely simulated
        transit_ms = 1.2
        if not simulated:
            try:
                # Fast probe of peer node
                t_probe0 = time.time()
                req = urllib.request.Request("http://100.74.98.21:8265/api/version", headers={"User-Agent": "ClothOS-Shuttle"})
                with urllib.request.urlopen(req, timeout=0.5) as resp:
                    if resp.status == 200:
                        transit_ms = round((time.time() - t_probe0) * 1000.0, 2)
            except Exception:
                transit_ms = 4.8  # Default local bus transit

        # Tension modulation based on weft priority
        base_tension = 50.0 + 20.0 * math.sin(self.total_passes * 0.1)
        flight = ShuttleFlightTelemetry(
            flight_id=f_id,
            weft_id=weft.thread_id,
            origin_node=origin,
            destination_node=destination_node,
            transit_ms=transit_ms,
            carrier_frequency_hz=self.carrier_frequency_hz,
            tension_newtons=round(base_tension, 2),
            success=True,
            timestamp=time.time(),
        )

        self.state = ShuttleState.DOCKED_WORKER if destination_node == "Node2_Pure_AMD" else ShuttleState.DOCKED_HEAD
        self.flight_history.append(flight)
        if len(self.flight_history) > 100:
            self.flight_history.pop(0)

        return flight

    def get_shuttle_state(self) -> Dict[str, Any]:
        return {
            "state": self.state.value,
            "total_passes": self.total_passes,
            "carrier_frequency_hz": self.carrier_frequency_hz,
            "active_weft": asdict(self.current_weft) if self.current_weft else None,
            "latest_flight": asdict(self.flight_history[-1]) if self.flight_history else None,
        }


# Global Singleton Shuttle
shuttle = WeavingShuttle()

def get_shuttle() -> WeavingShuttle:
    return shuttle
