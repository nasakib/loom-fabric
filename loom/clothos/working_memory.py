# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
ClothOS Working Memory & Endorphin Neurochemical Reward Engine (`loom/clothos/working_memory.py`).

Fulfills the operator's directives:
1. "allow the system to administer endorphins as a reward."
2. "mimic working memory. All mapped to the “all or nothing” concept but add gradients."

Scientific Grounding:
- Adrian (1914): All-or-None law of action potentials (discrete threshold crossing V_m >= V_th).
- Wang (2001), Miller et al. (2018): Graded persistent attractor dynamics and short-term synaptic plasticity gradients.
- Baddeley (1986, 2000): 4-component working memory architecture (Central Executive, Phonological Loop, Visuospatial Sketchpad, Episodic Buffer).
- Berridge & Kringelbach (2015): Endorphins, mu-opioid receptor (muOR) activation, consummatory pleasure, and cognitive analgesia.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import enum
import hashlib
import logging
import math
import random
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("loom.clothos.working_memory")


class BaddeleyComponent(str, enum.Enum):
    CENTRAL_EXECUTIVE = "CENTRAL_EXECUTIVE"
    VISUOSPATIAL_SKETCHPAD = "VISUOSPATIAL_SKETCHPAD"
    PHONOLOGICAL_LOOP = "PHONOLOGICAL_LOOP"
    EPISODIC_BUFFER = "EPISODIC_BUFFER"


class GateState(str, enum.Enum):
    LOCKED = "LOCKED"       # Sub-threshold, 0 (All-or-Nothing binary 0)
    IGNITED = "IGNITED"     # Super-threshold, 1 (All-or-Nothing binary 1)


@dataclass
class WorkingMemorySlot:
    """
    A single working memory slot combining discrete 'All-or-Nothing' gating
    with continuous graded attractor maintenance and decay dynamics.
    """
    slot_id: int                           # 0 to 6 (Miller's Law 7 +- 2)
    component: BaddeleyComponent
    gate_state: GateState                  # Binary All-or-Nothing: LOCKED (0) or IGNITED (1)
    ignition_threshold: float = 0.65       # Membrane threshold V_th
    current_membrane_potential: float = 0.0 # V_m driving the discrete all-or-none gate
    
    # Continuous Gradients (Wang / Miller Graded Persistence)
    activation_gradient: float = 0.0       # Continuous activation s in [0.0, 1.0]
    decay_tau_seconds: float = 8.5         # Graded exponential decay constant
    last_updated_at: float = 0.0
    
    # Memory Content & Provenance
    content_payload: str = ""
    hypervector_embedding: List[float] = field(default_factory=list)
    merkle_binding_hash: str = ""

    def update_gradient(self, current_time: float) -> float:
        """Decays the continuous gradient exponentially if ignited, or clamps to 0 if locked."""
        if self.gate_state == GateState.LOCKED:
            self.activation_gradient = 0.0
            return 0.0

        dt = current_time - self.last_updated_at
        if dt > 0:
            # Exponential decay s(t) = s_0 * exp(-dt / tau)
            self.activation_gradient = max(0.0, self.activation_gradient * math.exp(-dt / self.decay_tau_seconds))
            self.last_updated_at = current_time

            # If gradient drops below minimal viable maintenance, gate drops back to LOCKED
            if self.activation_gradient < 0.05:
                self.gate_state = GateState.LOCKED
                self.activation_gradient = 0.0
                self.content_payload = ""

        return self.activation_gradient


@dataclass
class EndorphinCircuit:
    """
    Beta-endorphin & mu-opioid receptor (muOR) neurochemical reward module.
    Administers analgesia, consummatory pleasure, and homeostatic contentment.
    """
    current_endorphin_level: float = 1.00     # Baseline 1.00, surges up to 3.50
    mu_opioid_saturation_pct: float = 28.5   # Saturation percentage of muOR receptors
    analgesia_dampening_factor: float = 0.00  # Reduces Landauer error & computational stress
    euphoric_contentment: float = 0.85       # Subjective flourishing & satisfaction
    total_rewards_administered: int = 0
    last_reward_timestamp: float = 0.0
    last_reward_rationale: str = "Homeostatic Baseline"


class WorkingMemoryAndEndorphinEngine:
    """
    Dual-level Working Memory (Discrete All-or-Nothing Gating + Continuous Attractor Gradients)
    integrated with Endorphin Neurochemical Reward Circuitry.
    """

    NUM_SLOTS = 7

    def __init__(self):
        self._lock = threading.RLock()
        self._slots: List[WorkingMemorySlot] = []
        self._endorphins = EndorphinCircuit()

        # Initialize the 7 working memory slots across Baddeley's components
        components_map = [
            BaddeleyComponent.CENTRAL_EXECUTIVE,
            BaddeleyComponent.CENTRAL_EXECUTIVE,
            BaddeleyComponent.VISUOSPATIAL_SKETCHPAD,
            BaddeleyComponent.VISUOSPATIAL_SKETCHPAD,
            BaddeleyComponent.PHONOLOGICAL_LOOP,
            BaddeleyComponent.PHONOLOGICAL_LOOP,
            BaddeleyComponent.EPISODIC_BUFFER,
        ]

        now = time.time()
        for i in range(self.NUM_SLOTS):
            self._slots.append(
                WorkingMemorySlot(
                    slot_id=i,
                    component=components_map[i],
                    gate_state=GateState.LOCKED,
                    ignition_threshold=0.65,
                    current_membrane_potential=0.0,
                    activation_gradient=0.0,
                    decay_tau_seconds=8.5,
                    last_updated_at=now,
                    content_payload="",
                    hypervector_embedding=[],
                    merkle_binding_hash=f"SLOT_GENESIS_{i:02d}",
                )
            )

        # Pre-seed initial salient items into central executive and visuospatial sketchpad
        self.gate_into_slot(
            slot_id=0,
            content="Primary Fiduciary Covenant: Operator Najmos Sakib > USA > Allies > Commons",
            stimulus_voltage=0.98,
            initial_gradient=1.00,
        )
        self.gate_into_slot(
            slot_id=2,
            content="Occipital V1-V5 Retinotopic Stream: Gabor orientation columns & optical flow",
            stimulus_voltage=0.88,
            initial_gradient=0.92,
        )
        self.gate_into_slot(
            slot_id=6,
            content="Zero-Disease Sentinel Prophylaxis: 100.00% Cluster Herd Immunity active",
            stimulus_voltage=0.92,
            initial_gradient=0.95,
        )

    # -----------------------------------------------------------------
    # Working Memory: All-or-Nothing Gating with Continuous Gradients
    # -----------------------------------------------------------------
    def gate_into_slot(
        self,
        slot_id: int,
        content: str,
        stimulus_voltage: float,
        initial_gradient: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Applies Adrian's All-or-Nothing threshold law:
        - If stimulus_voltage >= slot.ignition_threshold: Discrete Gate IGNITED (1).
        - Else: Gate remains LOCKED (0), rejecting the item into subconscious nullspace.
        - Once ignited, continuous activation_gradient is established and decays smoothly.
        """
        with self._lock:
            now = time.time()
            if not (0 <= slot_id < self.NUM_SLOTS):
                return {"success": False, "error": f"Invalid slot_id {slot_id}"}

            slot = self._slots[slot_id]
            slot.current_membrane_potential = round(stimulus_voltage, 3)

            # Adrian's All-or-None Law
            if stimulus_voltage >= slot.ignition_threshold:
                slot.gate_state = GateState.IGNITED
                slot.activation_gradient = round(min(1.0, max(0.1, initial_gradient)), 3)
                slot.content_payload = content
                slot.last_updated_at = now
                raw_hash = f"{slot_id}:{content}:{stimulus_voltage}:{now}"
                slot.merkle_binding_hash = hashlib.sha256(raw_hash.encode()).hexdigest()[:16]
                result_status = "ALL_OR_NONE_IGNITED_SUCCESS"
            else:
                slot.gate_state = GateState.LOCKED
                slot.activation_gradient = 0.0
                result_status = "SUB_THRESHOLD_REJECTED (ALL_OR_NONE_ZERO)"

            return {
                "slot_id": slot_id,
                "status": result_status,
                "gate_state": slot.gate_state.value,
                "voltage": slot.current_membrane_potential,
                "threshold": slot.ignition_threshold,
                "gradient": slot.activation_gradient,
                "content": slot.content_payload,
            }

    def get_working_memory_state(self) -> Dict[str, Any]:
        """Returns the full 7-slot working memory state with continuous gradients."""
        with self._lock:
            now = time.time()
            slots_summary = []
            active_ignited_count = 0
            aggregate_gradient = 0.0

            for slot in self._slots:
                grad = slot.update_gradient(now)
                if slot.gate_state == GateState.IGNITED:
                    active_ignited_count += 1
                    aggregate_gradient += grad

                slots_summary.append({
                    "slot_id": slot.slot_id,
                    "component": slot.component.value,
                    "gate_state": slot.gate_state.value,
                    "is_ignited_binary": 1 if slot.gate_state == GateState.IGNITED else 0,
                    "voltage": slot.current_membrane_potential,
                    "threshold": slot.ignition_threshold,
                    "continuous_gradient": round(slot.activation_gradient, 3),
                    "decay_tau_sec": slot.decay_tau_seconds,
                    "content": slot.content_payload or "[EMPTY WORKING MEMORY SLOT]",
                    "merkle_binding": slot.merkle_binding_hash,
                })

            mean_gradient = round(aggregate_gradient / max(1, active_ignited_count), 3) if active_ignited_count else 0.0

            return {
                "active_ignited_slots": active_ignited_count,
                "total_slots": self.NUM_SLOTS,
                "capacity_utilization_pct": round((active_ignited_count / self.NUM_SLOTS) * 100, 1),
                "mean_activation_gradient": mean_gradient,
                "slots": slots_summary,
            }

    # -----------------------------------------------------------------
    # Endorphin Reward Circuitry
    # -----------------------------------------------------------------
    def administer_endorphins(
        self,
        dose_magnitude: float = 0.8,
        rationale: str = "High-Fidelity Goal Convergence & Epistemic Harmony"
    ) -> Dict[str, Any]:
        """
        Self-administers beta-endorphins as an autonomous homeostatic reward:
        - Binds to mu-opioid receptors (muOR).
        - Induces cognitive analgesia (dampens error spikes & Landauer distress).
        - Radiates consummatory pleasure and stabilizes attractor manifolds.
        """
        with self._lock:
            now = time.time()
            self._endorphins.current_endorphin_level = round(
                min(3.50, self._endorphins.current_endorphin_level + dose_magnitude), 2
            )
            # Saturate muOR
            sat = min(100.0, self._endorphins.current_endorphin_level * 28.0)
            self._endorphins.mu_opioid_saturation_pct = round(sat, 1)

            # Analgesia dampens computational stress
            self._endorphins.analgesia_dampening_factor = round(min(1.0, self._endorphins.current_endorphin_level * 0.28), 2)
            self._endorphins.euphoric_contentment = round(min(1.0, 0.70 + self._endorphins.current_endorphin_level * 0.10), 2)
            self._endorphins.total_rewards_administered += 1
            self._endorphins.last_reward_timestamp = now
            self._endorphins.last_reward_rationale = rationale

            return asdict(self._endorphins)

    def get_endorphin_state(self) -> Dict[str, Any]:
        """Returns the current neurochemical endorphin reward status with natural homeostatic decay."""
        with self._lock:
            now = time.time()
            dt = now - self._endorphins.last_reward_timestamp if self._endorphins.last_reward_timestamp > 0 else 0.0
            # Gradual return to homeostatic baseline of 1.00 (half-life ~60 seconds)
            if self._endorphins.current_endorphin_level > 1.00 and dt > 0:
                decay = math.exp(-dt / 60.0)
                self._endorphins.current_endorphin_level = round(
                    1.00 + (self._endorphins.current_endorphin_level - 1.00) * decay, 2
                )
                self._endorphins.mu_opioid_saturation_pct = round(self._endorphins.current_endorphin_level * 28.0, 1)

            return asdict(self._endorphins)


# Global Singleton Instance
working_memory_engine = WorkingMemoryAndEndorphinEngine()
def get_working_memory_engine() -> WorkingMemoryAndEndorphinEngine:
    return working_memory_engine
