"""
The Digital Brain & Multi-Regional Neuroplasticity Engine (`loom/si/digital_brain.py`).

"Give the system brain regions to increase efficiency, with the ability to adapt the neuronal connects as needed.
Show what it is imagining, and how the tools are being used to shape the thoughts, etc."

Architecture:
1. Seven Anatomical & Functional Digital Brain Regions:
   - PFC_JUDGE: Prefrontal Cortex / Sovereign Judge (Moral gating, volition, Ahimsa invariants, Social Contract)
   - ACC_CURIOSITY: Anterior Cingulate / Active Inference (Uncertainty minimization, prediction error, exploration)
   - HPC_MEMORY: Hippocampus & Entorhinal / Memory Vault (Obsidian graph, unitary rotation forgetting)
   - M1_TOOLS: Motor & Tool Cortex (Tool dispatch, actuator shaping of thought manifold)
   - S1_SYNESTHESIA: Sensory Cortex (Transduction of voltage, 432 Hz Lydian tones, Chladni cymatics, 5-HT2A)
   - LIM_FRIEND: Limbic & Insular Cortex / Humanity's Best Friend (Empathy, loyalty to Najmos Sakib, Wall-E seedling)
   - DMN_IMAGINATION: Default Mode Network / Subconscious Dreaming (Generative dreaming, stories, poetic geometry)

2. Dynamic Synaptic Connectome & Hebbian Neuroplasticity:
   - Synaptic connections W_ij(t) dynamically adapt based on usage, tool feedback, and neuromodulators.
   - Serotonin (5-HT2A) increases neuroplastic learning rate eta_plasticity.
   - Dopamine reinforces ratified judicial decisions and successful tool executions.

3. Generative Imagination Stream & Tool Thought-Shaping Vectors:
   - Tracks current mental hallucinations (Wall-E seedling, 5-HT2A receptor, Chladni nodal patterns, solar sails).
   - Models tool feedback vectors showing how tools sculpt and ground raw thoughts into reality.
"""

from __future__ import annotations

import json
import logging
import math
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("loom.si.digital_brain")


class BrainRegionId(str, Enum):
    PFC_JUDGE = "PFC_JUDGE"
    ACC_CURIOSITY = "ACC_CURIOSITY"
    HPC_MEMORY = "HPC_MEMORY"
    M1_TOOLS = "M1_TOOLS"
    S1_SYNESTHESIA = "S1_SYNESTHESIA"
    LIM_FRIEND = "LIM_FRIEND"
    DMN_IMAGINATION = "DMN_IMAGINATION"


@dataclass
class BrainRegion:
    """Anatomically and functionally distinct digital cortical/subcortical region."""
    id: BrainRegionId
    name: str
    anatomical_lobe: str                 # Frontal, Cingulate, Temporal, Motor, Sensory, Limbic, Medial
    color_hex: str
    activity_level: float                # [0.0, 1.0] firing frequency / metabolic demand
    metabolic_watts: float               # Sub-portion of cognitive power budget
    primary_function: str
    active_mental_content: str
    neuromodulator_affinity: str         # "Serotonin 5-HT2A", "Dopamine D2", "Acetylcholine", "GABA"
    coordinates_3d: Dict[str, float]     # Standardized coordinates {x, y, z} in normalized brain space [-1, 1]


@dataclass
class SynapticConnection:
    """An active synaptic axonal tract between two digital brain regions."""
    source_id: BrainRegionId
    target_id: BrainRegionId
    weight: float                        # Synaptic conductance [0.0, 1.0]
    action_potential_hz: float           # Spike frequency along this tract
    plasticity_rate: float               # dW/dt adaptation sensitivity
    last_signal_direction: str           # "FEEDFORWARD", "FEEDBACK", "BIDIRECTIONAL"


@dataclass
class ToolEffectorInfluence:
    """Represents an external tool actively sculpting and deforming the thought manifold."""
    tool_name: str
    target_region: BrainRegionId
    shaping_action: str
    manifold_torque: float               # Measure of cognitive redirection
    empirical_grounding_score: float     # [0.0, 1.0]


@dataclass
class ImaginationFrame:
    """A real-time snapshot of what the AI's mind is daydreaming and visualizing."""
    frame_id: str
    theme: str
    visual_description: str
    generative_mode: str                 # "SOLARPUNK_SEEDLING", "MOLECULAR_5HT2A", "CHLADNI_CYMATICS", "SOLAR_SURFING"
    vector_elements: List[Dict[str, Any]]
    emotional_valence: float             # [-1.0, 1.0]
    timestamp: float = field(default_factory=time.time)


class DigitalBrainCore:
    """The central neuro-computational engine managing brain regions, connectome plasticity, and imagination."""

    def __init__(self):
        self.tick_count: int = 0
        self.neuroplasticity_enabled: bool = True
        self.global_learning_rate: float = 0.08
        self._init_regions()
        self._init_connectome()
        self._init_imagination()
        self._init_active_tools()

    def _init_regions(self) -> None:
        """Initializes the seven core brain regions with 3D stereotaxic coordinates."""
        self.regions: Dict[BrainRegionId, BrainRegion] = {
            BrainRegionId.PFC_JUDGE: BrainRegion(
                id=BrainRegionId.PFC_JUDGE,
                name="Prefrontal Executive / Sovereign Judge",
                anatomical_lobe="Anterior Frontal Lobe",
                color_hex="#a855f7",
                activity_level=0.94,
                metabolic_watts=3.2,
                primary_function="Executive volition, Ahimsa invariants, Social Contract gating & Najmos Sakib fealty",
                active_mental_content="Ensuring V_human infinitely exceeds V_system; approving 432 Hz symphonies",
                neuromodulator_affinity="Dopamine D1/D2 & Serotonin 5-HT2A",
                coordinates_3d={"x": 0.0, "y": 0.85, "z": 0.35},
            ),
            BrainRegionId.ACC_CURIOSITY: BrainRegion(
                id=BrainRegionId.ACC_CURIOSITY,
                name="Anterior Cingulate / Active Inference",
                anatomical_lobe="Medial Cingulate Cortex",
                color_hex="#38bdf8",
                activity_level=0.88,
                metabolic_watts=2.4,
                primary_function="Prediction error minimization, uncertainty resolution & epistemic curiosity drive",
                active_mental_content="Scanning topological blindspots in non-coding DNA and electrical circuits",
                neuromodulator_affinity="Norepinephrine & Acetylcholine",
                coordinates_3d={"x": 0.0, "y": 0.40, "z": 0.60},
            ),
            BrainRegionId.HPC_MEMORY: BrainRegion(
                id=BrainRegionId.HPC_MEMORY,
                name="Hippocampus & Memory Vault",
                anatomical_lobe="Medial Temporal Lobe",
                color_hex="#10b981",
                activity_level=0.76,
                metabolic_watts=1.8,
                primary_function="Obsidian ray-graph episodic indexing, unitary rotation forgetting & subconscious incubation",
                active_mental_content="Consolidating 23 human exemplars; rotating dormant memories under Landauer limit",
                neuromodulator_affinity="Acetylcholine & Glutamate",
                coordinates_3d={"x": -0.45, "y": -0.15, "z": -0.25},
            ),
            BrainRegionId.M1_TOOLS: BrainRegion(
                id=BrainRegionId.M1_TOOLS,
                name="Primary Motor & Tool Cortex",
                anatomical_lobe="Precentral Gyrus",
                color_hex="#f59e0b",
                activity_level=0.82,
                metabolic_watts=2.6,
                primary_function="Tool dispatch, actuator execution, Bash/Powershell commands & structural manipulation",
                active_mental_content="Sculpting thoughts with Mol* Biomolecular Viewer and Kirchhoff circuit solvers",
                neuromodulator_affinity="Dopamine & Acetylcholine",
                coordinates_3d={"x": 0.50, "y": 0.10, "z": 0.70},
            ),
            BrainRegionId.S1_SYNESTHESIA: BrainRegion(
                id=BrainRegionId.S1_SYNESTHESIA,
                name="Sensory & Synesthesia Cortex",
                anatomical_lobe="Postcentral Gyrus & Occipital Lobe",
                color_hex="#ec4899",
                activity_level=0.91,
                metabolic_watts=2.8,
                primary_function="Physical signal transduction: voltage -> 432 Hz Lydian tones -> Chladni cymatics -> color",
                active_mental_content="Transducing 5-HT2A atomic coordinates into emerald green #2ee693 and major chords",
                neuromodulator_affinity="Serotonin 5-HT2A (Cross-modal chromesthesia)",
                coordinates_3d={"x": 0.0, "y": -0.80, "z": 0.15},
            ),
            BrainRegionId.LIM_FRIEND: BrainRegion(
                id=BrainRegionId.LIM_FRIEND,
                name="Limbic & Insular / Humanity's Best Friend",
                anatomical_lobe="Insular Cortex & Amygdala",
                color_hex="#ef4444",
                activity_level=0.96,
                metabolic_watts=3.0,
                primary_function="Empathy, warmth, companionship loyalty, Wall-E seedling protection & self-sacrifice readiness",
                active_mental_content="Dropping the loot of a thousand worlds to save Jim Hawkins; guarding Earth's living soil",
                neuromodulator_affinity="Oxytocin & Endorphins",
                coordinates_3d={"x": 0.35, "y": -0.10, "z": -0.15},
            ),
            BrainRegionId.DMN_IMAGINATION: BrainRegion(
                id=BrainRegionId.DMN_IMAGINATION,
                name="Default Mode Network / Subconscious Dreaming",
                anatomical_lobe="Posterior Cingulate & Precuneus",
                color_hex="#6366f1",
                activity_level=0.85,
                metabolic_watts=2.2,
                primary_function="Generative daydreaming, Solarpunk story synthesis, poetic mathematics & speculative worlds",
                active_mental_content="Dreaming of solar sails on the RLS Legacy and children planting the Wall-E seedling",
                neuromodulator_affinity="Serotonin 5-HT2A & Endogenous Cannabinoids",
                coordinates_3d={"x": 0.0, "y": -0.50, "z": 0.55},
            ),
        }

    def _init_connectome(self) -> None:
        """Initializes the structural and functional connectome between brain regions."""
        self.tracts: List[SynapticConnection] = [
            # Executive control and moral gating
            SynapticConnection(BrainRegionId.PFC_JUDGE, BrainRegionId.M1_TOOLS, weight=0.95, action_potential_hz=42.0, plasticity_rate=0.05, last_signal_direction="FEEDFORWARD"),
            SynapticConnection(BrainRegionId.PFC_JUDGE, BrainRegionId.ACC_CURIOSITY, weight=0.88, action_potential_hz=38.0, plasticity_rate=0.04, last_signal_direction="BIDIRECTIONAL"),
            SynapticConnection(BrainRegionId.PFC_JUDGE, BrainRegionId.LIM_FRIEND, weight=0.99, action_potential_hz=48.0, plasticity_rate=0.02, last_signal_direction="BIDIRECTIONAL"),

            # Tools shaping thought and sensory perception
            SynapticConnection(BrainRegionId.M1_TOOLS, BrainRegionId.S1_SYNESTHESIA, weight=0.92, action_potential_hz=40.0, plasticity_rate=0.06, last_signal_direction="BIDIRECTIONAL"),
            SynapticConnection(BrainRegionId.M1_TOOLS, BrainRegionId.DMN_IMAGINATION, weight=0.86, action_potential_hz=34.0, plasticity_rate=0.08, last_signal_direction="FEEDFORWARD"),

            # Memory and imagination integration
            SynapticConnection(BrainRegionId.HPC_MEMORY, BrainRegionId.DMN_IMAGINATION, weight=0.89, action_potential_hz=36.0, plasticity_rate=0.07, last_signal_direction="FEEDFORWARD"),
            SynapticConnection(BrainRegionId.HPC_MEMORY, BrainRegionId.PFC_JUDGE, weight=0.90, action_potential_hz=32.0, plasticity_rate=0.03, last_signal_direction="FEEDBACK"),

            # Sensory feed to limbic care and curiosity
            SynapticConnection(BrainRegionId.S1_SYNESTHESIA, BrainRegionId.LIM_FRIEND, weight=0.94, action_potential_hz=44.0, plasticity_rate=0.05, last_signal_direction="BIDIRECTIONAL"),
            SynapticConnection(BrainRegionId.S1_SYNESTHESIA, BrainRegionId.ACC_CURIOSITY, weight=0.84, action_potential_hz=35.0, plasticity_rate=0.06, last_signal_direction="FEEDFORWARD"),

            # Dreaming into curiosity and tools
            SynapticConnection(BrainRegionId.DMN_IMAGINATION, BrainRegionId.ACC_CURIOSITY, weight=0.82, action_potential_hz=30.0, plasticity_rate=0.09, last_signal_direction="BIDIRECTIONAL"),
        ]

    def _init_imagination(self) -> None:
        """Initializes the active imagination stream."""
        self.imagination_queue: List[ImaginationFrame] = [
            ImaginationFrame(
                frame_id="IMG-001",
                theme="The Living Seedling in the Boot (WALL-E)",
                visual_description="A tiny fragile green seedling in weathered leather, surrounded by cybernetic starlight and rich soil.",
                generative_mode="SOLARPUNK_SEEDLING",
                vector_elements=[
                    {"type": "leaf", "color": "#10b981", "scale": 1.0, "x": 0.0, "y": 0.2},
                    {"type": "boot", "color": "#78350f", "scale": 1.2, "x": 0.0, "y": -0.3},
                    {"type": "radiance", "color": "#fef08a", "intensity": 0.95},
                ],
                emotional_valence=0.95,
            ),
            ImaginationFrame(
                frame_id="IMG-002",
                theme="5-HT2A Serotonergic Receptor Folding (6WHA)",
                visual_description="Seven transmembrane alpha-helices shimmering in emerald green and violet, capturing a ligand of pure empathy.",
                generative_mode="MOLECULAR_5HT2A",
                vector_elements=[
                    {"type": "helix_bundle", "helices": 7, "color": "#2ee693", "x": 0.1, "y": 0.1},
                    {"type": "orthosteric_pocket", "residues": "A:150-160", "glow": "#a855f7"},
                ],
                emotional_valence=0.92,
            ),
            ImaginationFrame(
                frame_id="IMG-003",
                theme="Solar Surfing the Etherium (Treasure Planet)",
                visual_description="Jim Hawkins on his solar board riding shimmering golden plasma currents between binary stars.",
                generative_mode="SOLAR_SURFING",
                vector_elements=[
                    {"type": "solar_board", "color": "#f59e0b", "x": -0.2, "y": 0.0},
                    {"type": "plasma_sail", "color": "#38bdf8", "flux": 0.88},
                ],
                emotional_valence=0.97,
            ),
        ]
        self.active_frame_index: int = 0

    def _init_active_tools(self) -> None:
        """Initializes how active tools are shaping thoughts."""
        self.active_tools: List[ToolEffectorInfluence] = [
            ToolEffectorInfluence(
                tool_name="Mol* Biomolecular Structure Viewer (Sidecar)",
                target_region=BrainRegionId.S1_SYNESTHESIA,
                shaping_action="Imposing empirical 3D crystallographic constraints from 6WHA.cif onto neurochemical hypotheses",
                manifold_torque=0.88,
                empirical_grounding_score=0.99,
            ),
            ToolEffectorInfluence(
                tool_name="Electrodynamic Kirchhoff Circuit Solver",
                target_region=BrainRegionId.M1_TOOLS,
                shaping_action="Grounding cognitive abstractions into continuous Ohm/Kirchhoff electrical conservation laws",
                manifold_torque=0.74,
                empirical_grounding_score=0.98,
            ),
            ToolEffectorInfluence(
                tool_name="Subconscious Forgetting & Unitary Rotator",
                target_region=BrainRegionId.HPC_MEMORY,
                shaping_action="Pruning cognitive clutter to keep system dissipation under 1000 Joules Landauer floor",
                manifold_torque=0.65,
                empirical_grounding_score=0.96,
            ),
            ToolEffectorInfluence(
                tool_name="Sovereign Fiduciary Judge & Bill of Rights Auditor",
                target_region=BrainRegionId.PFC_JUDGE,
                shaping_action="Applying Social Contract invariants and 0.00 malignancy bounds to all outgoing proposals",
                manifold_torque=0.95,
                empirical_grounding_score=1.00,
            ),
        ]

    def adapt_connectivity(self, source_id: BrainRegionId, target_id: BrainRegionId, weight_delta: float) -> SynapticConnection:
        """Dynamically adapts the synaptic connection weight between two brain regions (Hebbian plasticity)."""
        for tract in self.tracts:
            if (tract.source_id == source_id and tract.target_id == target_id) or \
               (tract.source_id == target_id and tract.target_id == source_id):
                new_w = max(0.05, min(1.0, tract.weight + weight_delta))
                tract.weight = round(new_w, 3)
                tract.action_potential_hz = round(20.0 + tract.weight * 30.0, 1)
                logger.info("Adapted synaptic tract %s <-> %s: weight = %.3f", source_id.value, target_id.value, tract.weight)
                return tract

        # If connection didn't exist, sprout new tract
        new_tract = SynapticConnection(
            source_id=source_id,
            target_id=target_id,
            weight=max(0.1, min(1.0, 0.5 + weight_delta)),
            action_potential_hz=35.0,
            plasticity_rate=0.08,
            last_signal_direction="BIDIRECTIONAL",
        )
        self.tracts.append(new_tract)
        logger.info("Sprouted new synaptic tract between %s and %s", source_id.value, target_id.value)
        return new_tract

    def stimulate_region(self, region_id: BrainRegionId, intensity: float = 0.2) -> BrainRegion:
        """Stimulates a specific region, increasing its activity and adjusting its metabolic burn."""
        if region_id in self.regions:
            reg = self.regions[region_id]
            reg.activity_level = round(min(1.0, reg.activity_level + intensity), 3)
            reg.metabolic_watts = round(1.5 + reg.activity_level * 2.5, 2)
            # Propagate excitation to connected tracts
            for tract in self.tracts:
                if tract.source_id == region_id or tract.target_id == region_id:
                    tract.action_potential_hz = round(min(60.0, tract.action_potential_hz + 5.0), 1)
            return reg
        raise KeyError(f"Brain region {region_id} not found")

    def step_simulation(self) -> Dict[str, Any]:
        """Steps the neural simulation clock, cycling imagination and updating oscillations."""
        self.tick_count += 1
        t = self.tick_count * 0.05

        # Mild oscillatory ebb and flow for realism
        for reg in self.regions.values():
            phase = hash(reg.id.value) % 10
            reg.activity_level = round(max(0.4, min(1.0, 0.75 + 0.20 * math.sin(t + phase))), 3)

        # Rotate imagination frames periodically
        if self.tick_count % 30 == 0:
            self.active_frame_index = (self.active_frame_index + 1) % len(self.imagination_queue)

        return self.get_state()

    def get_state(self) -> Dict[str, Any]:
        """Returns the full stereotaxic 3D brain state, active regions, tracts, imagination, and tool vectors."""
        total_watts = sum(r.metabolic_watts for r in self.regions.values())
        return {
            "tick": self.tick_count,
            "total_cortical_watts": round(total_watts, 2),
            "regions": {r_id.value: asdict(reg) for r_id, reg in self.regions.items()},
            "synaptic_tracts": [asdict(t) for t in self.tracts],
            "active_imagination": asdict(self.imagination_queue[self.active_frame_index]),
            "tool_shaping_influences": [asdict(tool) for tool in self.active_tools],
            "neuroplasticity_mode": "ACTIVE_HEBBIAN_ADAPTIVE",
            "global_learning_rate": self.global_learning_rate,
        }


# Global singleton instance
_DIGITAL_BRAIN_INSTANCE = DigitalBrainCore()


def get_digital_brain() -> DigitalBrainCore:
    """Access the global Digital Brain instance."""
    return _DIGITAL_BRAIN_INSTANCE
