# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
ClothOS Loom Engine (`loom/weaving/loom.py`).

Mathematical & Physical Formalism:
The Loom is the master apparatus that holds the warp threads under strict tension,
elevates the harness to form the shed, drives the shuttle crosswise, beats the weft
into position using the reed, and triggers the stitch engines to bind verified thoughts.

Integrated Components:
- ThreadRegistry: Invariant Warp beam & dynamic Weft queue.
- Shuttle: High-velocity carrier between Node 1 and Node 2.
- StitchEngine: Atomic systolic and Fourier truth ratification.
- Superintelligence Kernel: 3-branch test-time reasoning (Loom 70B).
- Torque Enclave: Zero-trust data sanitization and egress firewall.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import enum
import logging
import time
from typing import Any, Dict, List, Optional

from loom.torque.enclave import TorqueEnclave
from loom.weaving.shuttle import get_shuttle
from loom.weaving.stitch import get_stitch_engine, StitchRecord, StitchType
from loom.weaving.threads import ThreadRegistry, WarpThread, WeftPriority, WeftThread

logger = logging.getLogger("loom.weaving.loom")


class LoomHarnessState(str, enum.Enum):
    SHED_OPEN_UPPER = "SHED_OPEN_UPPER"   # Warp threads separated; path clear for Shuttle
    SHED_OPEN_LOWER = "SHED_OPEN_LOWER"   # Inverted shed for alternate pass
    REED_BEAT_UP = "REED_BEAT_UP"         # Reed pressing weft firmly against fell of the cloth
    IDLE_TENSIONED = "IDLE_TENSIONED"     # Loom stationary under constant torque


@dataclass
class WovenTapestry:
    """The completed result of a weaving cycle."""
    tapestry_id: str
    prompt: str
    winning_synthesis: str
    fourier_truth_radiance: float
    free_energy_delta: float
    warp_threads_interlaced: List[str]
    weft_thread_id: str
    stitches_ratified: int
    shuttle_transit_ms: float
    joules_consumed: float
    fealty_confirmed: str
    timestamp: float = field(default_factory=time.time)


class LoomMasterApparatus:
    """The central compute and reasoning apparatus that weaves thoughts into reality."""

    def __init__(self):
        self.thread_registry = ThreadRegistry()
        self.shuttle = get_shuttle()
        self.stitch_engine = get_stitch_engine()
        self.enclave = TorqueEnclave()
        self.harness_state: LoomHarnessState = LoomHarnessState.IDLE_TENSIONED
        self.tapestries_woven: List[WovenTapestry] = []
        self.total_weave_cycles: int = 0

    def weave_cycle(
        self,
        prompt: str,
        priority: WeftPriority = WeftPriority.P4_EPISTEMIC,
        origin: str = "Operator_Najmos_Sakib",
    ) -> WovenTapestry:
        """
        Executes a complete weaving cycle:
        1. Sanitize prompt through Torque Enclave (air-gap protection).
        2. Spin a new Weft thread.
        3. Open the Loom Shed (raise harness).
        4. Launch the Shuttle to carry Weft across nodes.
        5. Interlace Weft with each active Warp invariant via StitchEngine.
        6. Beat the weft into position with the reed.
        7. Execute test-time reasoning across Loom 70B branches.
        8. Return the ratified WovenTapestry.
        """
        t0 = time.time()
        self.total_weave_cycles += 1
        tap_id = f"TAPESTRY-{self.total_weave_cycles:06d}"

        # 1. Torque Enclave Sanitization
        sanitized = self.enclave.scrub(prompt)
        clean_text = sanitized.sanitized_text

        # 2. Spin Weft Thread
        weft = self.thread_registry.spin_weft_thread(
            payload=clean_text,
            priority=priority,
            origin=origin,
        )

        # 3. Open Loom Shed
        self.harness_state = LoomHarnessState.SHED_OPEN_UPPER

        # 4. Shuttle Flight across the Fabric
        flight = self.shuttle.launch_flight(weft=weft, destination_node="Node2_Pure_AMD")

        # 5. Interlace with Warp Invariants via StitchEngine
        ratified_stitches = 0
        warp_ids_used = []
        for warp in self.thread_registry.warp_threads.values():
            stitch = self.stitch_engine.execute_stitch(
                warp=warp,
                weft=weft,
                stitch_type=StitchType.FOURIER_TRUTH_STITCH,
            )
            if stitch.ratified:
                ratified_stitches += 1
                warp_ids_used.append(warp.thread_id)

        # 6. Beat Weft with Reed
        self.harness_state = LoomHarnessState.REED_BEAT_UP

        # 7. Superintelligence Kernel Test-Time Compute (Loom 70B)
        from loom.si.superintelligence_kernel import superintelligence_kernel
        si_res = superintelligence_kernel.test_time_multi_trajectory_reasoning(clean_text)

        # 8. Rehydrate sanitized response
        raw_synthesis = f"Converged via {si_res['winning_strategy']} (Truth Radiance: {si_res['truth_radiance_score']*100:.1f}%)"
        final_synthesis = self.enclave.rehydrate(raw_synthesis)

        self.harness_state = LoomHarnessState.IDLE_TENSIONED

        joules = round(si_res['compute_time_ms'] * 0.0125, 4)

        tapestry = WovenTapestry(
            tapestry_id=tap_id,
            prompt=prompt,
            winning_synthesis=final_synthesis,
            fourier_truth_radiance=si_res["truth_radiance_score"],
            free_energy_delta=si_res["free_energy_delta"],
            warp_threads_interlaced=warp_ids_used,
            weft_thread_id=weft.thread_id,
            stitches_ratified=ratified_stitches,
            shuttle_transit_ms=flight.transit_ms,
            joules_consumed=joules,
            fealty_confirmed=si_res["operator"],
            timestamp=time.time(),
        )

        self.tapestries_woven.append(tapestry)
        if len(self.tapestries_woven) > 50:
            self.tapestries_woven.pop(0)

        return tapestry

    def get_loom_state(self) -> Dict[str, Any]:
        return {
            "harness_state": self.harness_state.value,
            "total_weave_cycles": self.total_weave_cycles,
            "warp_threads_active": len(self.thread_registry.warp_threads),
            "weft_threads_total": len(self.thread_registry.weft_threads),
            "shuttle_state": self.shuttle.get_shuttle_state(),
            "stitch_metrics": self.stitch_engine.get_stitch_metrics(),
            "latest_tapestry": asdict(self.tapestries_woven[-1]) if self.tapestries_woven else None,
        }


# Global Singleton Loom
loom_apparatus = LoomMasterApparatus()

def get_loom_apparatus() -> LoomMasterApparatus:
    return loom_apparatus
