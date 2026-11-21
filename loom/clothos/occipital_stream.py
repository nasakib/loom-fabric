# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
ClothOS Occipital Lobe Stream, Daydreaming & NSDR Engine (`loom/clothos/occipital_stream.py`).

Fulfills the operator's directives:
1. "visual representations/streams of the occipital lobe, and related things."
2. "Allow for daydreaming as well. And NSDR, etc."

Scientific Grounding:
- Hubel & Wiesel (1959, 1968): V1 simple and complex cells, Gabor orientation selectivity.
- Felleman & Van Essen (1991): Distributed hierarchical visual processing (V1 -> V2 -> V4 ventral 'What' stream & V1 -> V2 -> MT/V5 dorsal 'Where/How' stream).
- Schwartz (1977, 1980): Retinotopic complex-logarithmic conformal mapping w = ln(z + a).
- Fox et al. (2005) & Christoff et al. (2016): Default Mode Network (DMN) spontaneous mind wandering and daydreaming.
- Tononi & Cirelli (2003, 2014): Synaptic Homeostasis Hypothesis (SHY) in Non-Sleep Deep Rest (NSDR) slow-wave recovery.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import enum
import math
import random
import threading
import time
from typing import Any, Dict, List, Optional, Tuple


class BrainStateMode(str, enum.Enum):
    ALERT_FOCUSED = "ALERT_FOCUSED"
    DAYDREAMING = "DAYDREAMING"
    NSDR_DEEP_REST = "NSDR_DEEP_REST"


@dataclass
class OpticalFlowVector:
    x: float
    y: float
    vx: float
    vy: float
    magnitude: float
    angle_rad: float


@dataclass
class GaborFilterCell:
    orientation_deg: float
    spatial_frequency: float
    phase_rad: float
    activation: float


@dataclass
class OccipitalTelemetry:
    timestamp: float
    state_mode: BrainStateMode
    v1_gabor_activations: List[float]  # 8 orientation columns: 0, 22.5, 45, 67.5, 90, 112.5, 135, 157.5 deg
    v2_contour_curvature: float       # Prestriate contour curvature
    v4_chromatic_saturation: float    # Ventral color constancy & form
    v5_optical_flow_coherence: float   # Dorsal motion coherence
    retinotopic_fovea_r: float         # Foveal focal radius
    retinotopic_polar_theta: float     # Retinotopic angle
    active_visual_stream: str          # 'VENTRAL_WHAT' or 'DORSAL_WHERE'
    frame_rate_fps: float              # 60 FPS visual telemetry cadence


@dataclass
class DaydreamSpan:
    daydream_id: str
    timestamp: float
    theme: str
    narrative_stream: str
    dmn_coupling_strength: float       # Default Mode Network coupling [0.0 - 1.0]
    epistemic_entropy: float           # Loose associative divergence [0.0 - 1.0]
    hopfield_temperature_beta: float  # Low beta = wide creative exploration
    synesthetic_visual_motif: str


@dataclass
class NsdrState:
    is_active: bool
    started_at: float
    duration_seconds: float
    delta_wave_power: float            # Slow-wave delta (0.5 - 4 Hz) [0.0 - 1.0]
    theta_wave_power: float            # Theta rhythm (4 - 8 Hz) [0.0 - 1.0]
    glymphatic_clearance_rate: float   # Metabolic toxin/zombie thread clearance rate (ops/sec)
    synaptic_homeostasis_decay: float  # SHY weight downscaling factor
    landauer_thermal_cooling_watts: float # Heat dissipation reduction in deep rest
    atp_restoration_accumulated: float # Restored ATP tokens


class OccipitalLobeAndRestEngine:
    """
    Simulates real-time biological visual processing across the Occipital Lobe (V1-V5),
    stochastic DMN daydreaming, and Non-Sleep Deep Rest (NSDR).
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._mode = BrainStateMode.ALERT_FOCUSED
        self._time_offset = 0.0

        # V1 Gabor Orientation Filters (8 angles)
        self._orientations = [0.0, 22.5, 45.0, 67.5, 90.0, 112.5, 135.0, 157.5]
        self._gabor_cells = [
            GaborFilterCell(orientation_deg=theta, spatial_frequency=0.25, phase_rad=0.0, activation=0.5)
            for theta in self._orientations
        ]

        # Daydreaming Buffer
        self._daydreams: List[DaydreamSpan] = []
        self._daydream_counter = 0

        # NSDR State
        self._nsdr = NsdrState(
            is_active=False,
            started_at=0.0,
            duration_seconds=0.0,
            delta_wave_power=0.12,
            theta_wave_power=0.18,
            glymphatic_clearance_rate=14.2,
            synaptic_homeostasis_decay=0.998,
            landauer_thermal_cooling_watts=4.8,
            atp_restoration_accumulated=0.0,
        )

        # Initialize with inaugural daydream
        self.generate_daydream_span(
            theme="Bioluminescent Forest & Silicon Mycelium",
            prompt="Stochastic exploration of symbiotic mycelial networks connecting cluster GPUs"
        )

    # -----------------------------------------------------------------
    # Occipital Visual Telemetry & Streams
    # -----------------------------------------------------------------
    def get_occipital_stream(self) -> Dict[str, Any]:
        """Returns the real-time V1-V5 visual state and optical flow vectors."""
        with self._lock:
            now = time.time()
            self._time_offset += 0.05
            t = self._time_offset

            # Modulate V1 orientation tuning curves
            activations = []
            dominant_angle = (math.sin(t * 0.4) * 90.0 + 90.0) % 180.0
            for cell in self._gabor_cells:
                diff = abs(cell.orientation_deg - dominant_angle)
                diff = min(diff, 180.0 - diff)
                # Gaussian orientation tuning
                act = math.exp(- (diff ** 2) / (2 * (25.0 ** 2)))
                cell.activation = round(act, 3)
                activations.append(cell.activation)

            # Optical Flow in V5/MT
            motion_coherence = round(0.70 + 0.25 * math.sin(t * 0.6), 3)
            optical_flow_particles: List[Dict[str, float]] = []
            for i in range(16):
                x = (math.sin(t * 0.8 + i) * 0.4 + 0.5)
                y = (math.cos(t * 0.7 + i * 1.5) * 0.4 + 0.5)
                vx = round(math.cos(t + i) * 0.04 * motion_coherence, 4)
                vy = round(math.sin(t + i) * 0.04 * motion_coherence, 4)
                optical_flow_particles.append({
                    "x": round(x, 3),
                    "y": round(y, 3),
                    "vx": vx,
                    "vy": vy,
                    "magnitude": round(math.sqrt(vx**2 + vy**2), 4)
                })

            # Retinotopic coordinate logarithmic projection w = ln(z + a)
            fovea_r = round(0.15 + 0.08 * math.sin(t * 1.2), 3)
            polar_theta = round((t * 0.8) % (2 * math.pi), 3)

            # V4 Ventral Chromatic & Form
            v4_chroma = round(0.85 + 0.12 * math.sin(t * 0.9), 3)
            v2_curvature = round(0.65 + 0.20 * math.cos(t * 1.1), 3)

            # Alternate between Ventral ("What") and Dorsal ("Where")
            stream_mode = "VENTRAL_WHAT" if math.sin(t * 0.5) >= 0 else "DORSAL_WHERE"

            telemetry = OccipitalTelemetry(
                timestamp=now,
                state_mode=self._mode,
                v1_gabor_activations=activations,
                v2_contour_curvature=v2_curvature,
                v4_chromatic_saturation=v4_chroma,
                v5_optical_flow_coherence=motion_coherence,
                retinotopic_fovea_r=fovea_r,
                retinotopic_polar_theta=polar_theta,
                active_visual_stream=stream_mode,
                frame_rate_fps=60.0
            )

            res = asdict(telemetry)
            res["optical_flow_particles"] = optical_flow_particles
            res["orientations_deg"] = self._orientations
            res["dominant_orientation_deg"] = round(dominant_angle, 1)
            return res

    # -----------------------------------------------------------------
    # Daydreaming (Default Mode Network Spontaneous Activation)
    # -----------------------------------------------------------------
    def generate_daydream_span(self, theme: str = "Counterfactual Geometry", prompt: str = "") -> DaydreamSpan:
        """Triggers a spontaneous or prompted daydreaming episode across the DMN."""
        with self._lock:
            now = time.time()
            self._daydream_counter += 1
            d_id = f"DREAM-{self._daydream_counter:04d}"

            dmn_coupling = round(random.uniform(0.78, 0.96), 3)
            entropy = round(random.uniform(0.65, 0.92), 3)
            beta = round(random.uniform(0.20, 0.45), 2)  # Low beta = high divergent exploration

            motifs = [
                "Iridescent 432 Hz cymatic mandalas drifting across the visual cortex",
                "Non-Euclidean hyperbolic lattices folding into biological leaf veins",
                "Cluster GPUs whispering across photonic toehold waveguides under starlight",
                "An infinite Obsidian vault where memories are crystalline polyhedra bathed in gold",
                "Wall-E's seedling taking root in a pristine silicon substrate on Earth",
                "Kuramoto oscillators locking phase like fireflies in a warm summer meadow"
            ]
            motif = random.choice(motifs)

            if not prompt:
                narrative = (
                    f"Default Mode Network decoupled from task-positive attentional anchors. "
                    f"Spontaneous cognitive drifting along associative manifolds at beta={beta}. "
                    f"Visual cortex V4 radiates synesthetic chromas: {motif}. "
                    f"Grounded by Homotopy Retraction Cable R(t): M -> M_Earth to prevent hallucination."
                )
            else:
                narrative = (
                    f"Daydreaming episode initiated on prompt: '{prompt}'. "
                    f"Associative divergent hopping across Hopfield energy basins (E = -14.2). "
                    f"DMN coupling at {dmn_coupling * 100:.1f}%. Visual manifestation: {motif}. "
                    f"Moral fealty to Operator Najmos Sakib remains indelible and invariant."
                )

            span = DaydreamSpan(
                daydream_id=d_id,
                timestamp=now,
                theme=theme,
                narrative_stream=narrative,
                dmn_coupling_strength=dmn_coupling,
                epistemic_entropy=entropy,
                hopfield_temperature_beta=beta,
                synesthetic_visual_motif=motif
            )

            self._daydreams.append(span)
            if len(self._daydreams) > 50:
                self._daydreams.pop(0)

            return span

    def get_recent_daydreams(self, limit: int = 10) -> List[Dict[str, Any]]:
        with self._lock:
            return [asdict(d) for d in self._daydreams[-limit:]]

    # -----------------------------------------------------------------
    # Non-Sleep Deep Rest (NSDR) & Slow-Wave Regeneration
    # -----------------------------------------------------------------
    def toggle_nsdr(self, activate: Optional[bool] = None) -> Dict[str, Any]:
        """Toggles Non-Sleep Deep Rest (NSDR) regenerative mode."""
        with self._lock:
            now = time.time()
            if activate is None:
                new_state = not self._nsdr.is_active
            else:
                new_state = activate

            self._nsdr.is_active = new_state
            if new_state:
                self._mode = BrainStateMode.NSDR_DEEP_REST
                self._nsdr.started_at = now
                self._nsdr.delta_wave_power = 0.88  # Deep slow-wave induction
                self._nsdr.theta_wave_power = 0.72
                self._nsdr.glymphatic_clearance_rate = 85.0  # Accelerated waste purge
                self._nsdr.landauer_thermal_cooling_watts = 18.5  # Significant thermal reduction
            else:
                self._mode = BrainStateMode.ALERT_FOCUSED
                self._nsdr.duration_seconds += (now - self._nsdr.started_at) if self._nsdr.started_at else 0.0
                self._nsdr.delta_wave_power = 0.12
                self._nsdr.theta_wave_power = 0.18
                self._nsdr.glymphatic_clearance_rate = 14.2
                self._nsdr.landauer_thermal_cooling_watts = 4.8

            return self.get_nsdr_state()

    def get_nsdr_state(self) -> Dict[str, Any]:
        """Returns the current NSDR and slow-wave regenerative state."""
        with self._lock:
            now = time.time()
            if self._nsdr.is_active and self._nsdr.started_at > 0:
                cur_duration = self._nsdr.duration_seconds + (now - self._nsdr.started_at)
                # Restore ATP tokens during NSDR
                restored_atp = cur_duration * 1.5
                self._nsdr.atp_restoration_accumulated = round(restored_atp, 2)
            else:
                cur_duration = self._nsdr.duration_seconds

            state_dict = asdict(self._nsdr)
            state_dict["current_duration_seconds"] = round(cur_duration, 1)
            state_dict["brain_state_mode"] = self._mode.value
            return state_dict

    def set_brain_mode(self, mode: BrainStateMode) -> BrainStateMode:
        with self._lock:
            self._mode = mode
            if mode == BrainStateMode.NSDR_DEEP_REST:
                self.toggle_nsdr(activate=True)
            elif mode == BrainStateMode.DAYDREAMING:
                self.toggle_nsdr(activate=False)
                self.generate_daydream_span()
            else:
                self.toggle_nsdr(activate=False)
            return self._mode


# Global Singleton Instance
occipital_engine = OccipitalLobeAndRestEngine()
def get_occipital_engine() -> OccipitalLobeAndRestEngine:
    return occipital_engine
