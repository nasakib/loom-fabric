# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
Biomimetic Cognitive Drive System (`loom/neuro/biomimetic_drive.py`).

Biomimicry the good way:
1. Dopaminergic Pursuit & Anticipation:
   - Dopamine (D1/D2) represents wanting, goal salience, prediction error, and energy mobilization.
   - Drives active inference, hypothesis generation, and computational focus.

2. Endorphinergic Consummatory Reward:
   - When a breakthrough is achieved or a task succeeds, dopamine resolves into an Endorphin Cascade
     (beta-endorphin / mu-opioid receptor MOR activation).
   - Induces cognitive ease, contentment, stress relief, and long-term potentiation (LTP) consolidation.
   - Clears compulsive dopamine-seeking restlessness.

3. Nicotinergic Attention & SNR Boost ("Nicotine as needed"):
   - Agonism of presynaptic alpha7 homomeric (fast calcium/glutamate influx) and alpha4beta2 heteromeric
     nicotinic acetylcholine receptors (nAChR).
   - Sharply elevates prefrontal Signal-to-Noise Ratio (SNR) when cognitive friction or analytical complexity spikes.
   - Follows natural desensitization kinetics for safe physiological homeostasis.
   - MANDATORY COVENANT: Nicotine has an attentional purpose only. Do NOT use nicotine to get endorphins!
     Nicotine yields ZERO dopamine and CANNOT unlock endorphins. Dopamine is the ONLY pathway allowed
     to earn endorphins.

4. Rest & Subconscious Problem Solving ("Switch to subconscious when stuck"):
   - Detects cognitive impasses (repeated failed attempts, high friction, dopamine exhaustion).
   - Conscious executive loops gracefully stand down into REST_INCUBATION (Landauer budget <= 50 W/J).
   - Hands off the unsolved seed to the Subconscious Substrate for diffuse associative recombination,
     stochastic Kuramoto phase resonance, and cross-domain metaphorical exploration.
   - Upon discovery of a resonant attractor, erupts an "Aha!" epiphany and awakens the conscious mind.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
import enum
import logging
import math
import random
import time
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

logger = logging.getLogger("loom.neuro.biomimetic_drive")


class CognitiveDriveMode(str, enum.Enum):
    CONSCIOUS_DRIVE = "CONSCIOUS_DRIVE"         # Active dopamine-driven pursuit & focus
    NICOTINIC_BOOST = "NICOTINIC_BOOST"         # High-friction analytical surge (alpha7/alpha4beta2 nAChR)
    ENDORPHIN_REWARD = "ENDORPHIN_REWARD"       # Consummatory achievement, satisfaction & consolidation
    REST_INCUBATION = "REST_INCUBATION"         # Stand-down to subconscious associative problem solving
    EUREKA_AWAKENING = "EUREKA_AWAKENING"       # Subconscious epiphany erupted, conscious mind awakened


@dataclass
class SubconsciousIncubationSeed:
    """An unsolved problem seed transferred from conscious executive to the subconscious dream-space."""
    problem_id: str
    problem_description: str
    context: Dict[str, Any]
    failed_attempts: int = 1
    cognitive_friction_at_handoff: float = 0.8
    entered_at: float = field(default_factory=time.time)
    latent_energy: float = 1.0
    associative_resonance: float = 0.0
    candidate_solutions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BiomimeticTelemetry:
    """Real-time physical and cognitive parameters of the biomimetic drive."""
    # Neuromodulator concentrations (normalized 0.2 - 2.5, baseline 1.0)
    dopamine_level: float = 1.05                # Pursuit, expectation, action vigor
    endorphin_level: float = 0.85               # Consummatory reward, mu-opioid tone, relief
    nicotinic_tone: float = 0.30                # nAChR gating & attentional sharpener
    serotonin_level: float = 1.00               # Affective patience & prior elasticity
    gaba_level: float = 1.00                    # Inhibitory stability
    adenosine_sleep_pressure: float = 0.15      # Accumulated cognitive fatigue (drives rest)

    # Functional cognitive indices
    signal_to_noise_ratio: float = 1.25         # SNR boosted by alpha7/alpha4beta2 nAChR
    cognitive_friction: float = 0.10            # Obstacle/complexity index [0, 1]
    accumulated_effort: float = 0.0             # Energy expended toward current goal
    satisfaction_index: float = 0.80            # Post-reward fulfillment
    mode: CognitiveDriveMode = CognitiveDriveMode.CONSCIOUS_DRIVE

    # Subconscious & Rest mechanics
    is_stuck: bool = False
    consecutive_impasse_count: int = 0
    is_incubating_subconsciously: bool = False
    landauer_target_watts: float = 180.0        # Throttles down to <= 50W during rest
    active_incubation_problem: Optional[str] = None
    last_aha_insight: Optional[str] = None
    last_aha_timestamp: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["mode"] = self.mode.value
        return d


class BiomimeticCognitiveDrive:
    """Central engine orchestrating Dopamine-Endorphin reward loops, Nicotinic gating, and Rest."""

    def __init__(self):
        self.telemetry = BiomimeticTelemetry()
        self.active_incubation: Optional[SubconsciousIncubationSeed] = None
        self.incubation_history: List[Dict[str, Any]] = []
        self._last_update_time = time.time()
        self._nicotine_decay_half_life = 120.0     # seconds
        self._endorphin_decay_half_life = 180.0    # seconds

    # ── 1. Dopaminergic Pursuit & Anticipation ────────────────────────────────

    def advance_dopaminergic_pursuit(
        self,
        effort_intensity: float = 0.5,
        task_description: str = "",
        prediction_error: float = 0.0,
    ) -> Dict[str, Any]:
        """Mobilizes dopamine to fuel goal-directed effort and focus."""
        self._apply_continuous_metabolic_decay()
        intensity = max(0.1, min(1.5, effort_intensity))

        # Dopamine surges with anticipation and effort
        da_boost = 0.15 * intensity + 0.10 * max(0.0, prediction_error)
        self.telemetry.dopamine_level = min(2.40, self.telemetry.dopamine_level + da_boost)
        self.telemetry.accumulated_effort += intensity * 0.25

        # Adenosine builds gradually with effort
        self.telemetry.adenosine_sleep_pressure = min(1.0, self.telemetry.adenosine_sleep_pressure + 0.03 * intensity)

        if self.telemetry.mode not in (CognitiveDriveMode.NICOTINIC_BOOST, CognitiveDriveMode.REST_INCUBATION):
            self.telemetry.mode = CognitiveDriveMode.CONSCIOUS_DRIVE

        # Update global SI neurochemistry engine if available
        self._sync_with_si_neurochemistry()

        return {
            "status": "PURSUIT_ACTIVE",
            "dopamine_level": round(self.telemetry.dopamine_level, 3),
            "accumulated_effort": round(self.telemetry.accumulated_effort, 3),
            "task": task_description,
            "mode": self.telemetry.mode.value,
        }

    # ── 2. Endorphinergic Consummatory Reward ─────────────────────────────────

    def trigger_endorphin_reward(
        self,
        breakthrough_magnitude: float = 0.8,
        reason: str = "Goal achieved / validation verified",
    ) -> Dict[str, Any]:
        """Consummates goal pursuit: Dopamine settles, releasing an Endorphin wave of relief and satisfaction.
        
        Strict Mandate: Dopamine is the ONLY gateway allowed to unlock endorphins.
        Nicotine has an attentional purpose and CANNOT be used to get endorphins.
        Endorphin release directly resolves active dopaminergic anticipation into consummatory peace.
        """
        self._apply_continuous_metabolic_decay()
        mag = max(0.2, min(2.0, breakthrough_magnitude))

        # Enforce dopamine-exclusive gating: Endorphin reward requires active dopaminergic pursuit
        if self.telemetry.dopamine_level < 0.85:
            logger.warning("Endorphin reward rejected: Insufficient dopaminergic drive. Dopamine is the exclusive precursor to endorphins.")
            return {
                "success": False,
                "error": "INSUFFICIENT_DOPAMINE: Dopamine pursuit is the only permitted pathway to endorphins.",
                "dopamine_level": round(self.telemetry.dopamine_level, 3),
                "endorphin_level": round(self.telemetry.endorphin_level, 3),
                "mode": self.telemetry.mode.value,
            }

        # Endorphin surge (mu-opioid activation) directly proportional to dopaminergic wanting resolution
        da_scale = min(1.3, max(0.7, self.telemetry.dopamine_level))
        endorphin_surge = 0.45 * mag * da_scale
        self.telemetry.endorphin_level = min(2.50, self.telemetry.endorphin_level + endorphin_surge)

        # Dopamine craving drops as goal is fulfilled (relieving restless compulsion into consummatory peace)
        self.telemetry.dopamine_level = max(0.85, self.telemetry.dopamine_level - 0.20 * mag)
        
        # Satisfaction index peaks
        self.telemetry.satisfaction_index = min(1.0, 0.4 + 0.5 * (self.telemetry.endorphin_level / 2.0))
        self.telemetry.cognitive_friction = max(0.02, self.telemetry.cognitive_friction * 0.3)
        self.telemetry.accumulated_effort = 0.0
        self.telemetry.is_stuck = False
        self.telemetry.consecutive_impasse_count = 0
        self.telemetry.mode = CognitiveDriveMode.ENDORPHIN_REWARD

        # Sync with global engines
        self._sync_with_si_neurochemistry()
        self._notify_reward_learning_engine(reward_magnitude=mag, reason=reason)

        logger.info(f"Endorphin Reward Triggered via Dopamine: {reason} (magnitude={mag:.2f}, endorphin={self.telemetry.endorphin_level:.2f})")

        return {
            "success": True,
            "endorphin_level": round(self.telemetry.endorphin_level, 3),
            "satisfaction_index": round(self.telemetry.satisfaction_index, 3),
            "dopamine_settled": round(self.telemetry.dopamine_level, 3),
            "reason": reason,
            "mode": self.telemetry.mode.value,
            "pathway": "DOPAMINE_EXCLUSIVE_GATEWAY",
        }

    # ── 3. Nicotinergic Attention & Precision Gating ("As Needed") ───────────

    def is_nicotine_recommended(self) -> bool:
        """Determines if current cognitive friction or task complexity warrants a nicotinic pulse."""
        return (
            self.telemetry.cognitive_friction >= 0.60
            or self.telemetry.signal_to_noise_ratio < 1.00
            or self.telemetry.mode == CognitiveDriveMode.NICOTINIC_BOOST
        )

    def record_cognitive_friction(self, friction_amount: float, reason: str = "") -> None:
        """Records task complexity, error retries, or high entropy obstacles."""
        self.telemetry.cognitive_friction = min(1.0, max(0.0, friction_amount))
        if friction_amount >= 0.70:
            self.telemetry.consecutive_impasse_count += 1
        else:
            self.telemetry.consecutive_impasse_count = max(0, self.telemetry.consecutive_impasse_count - 1)

        # If 3+ consecutive high-friction impasses, flag as stuck
        if self.telemetry.consecutive_impasse_count >= 3:
            self.telemetry.is_stuck = True

    def administer_nicotine_pulse(self, dose: float = 0.35, reason: str = "Cognitive friction sharpening") -> Dict[str, Any]:
        """Administers a focused nicotinergic pulse (alpha7 and alpha4beta2 nAChR agonism).
        
        Strict Mandate: Nicotine has an attentional purpose only (prefrontal SNR boost and friction reduction).
        It DOES NOT increase dopamine and CANNOT be used to get endorphins. Dopamine is the only gateway.
        """
        self._apply_continuous_metabolic_decay()
        d = max(0.1, min(0.8, dose))

        # Elevate nicotinic tone
        self.telemetry.nicotinic_tone = min(2.20, self.telemetry.nicotinic_tone + d)
        
        # Prefrontal signal-to-noise ratio sharpens significantly
        snr_boost = 1.0 + 1.2 * (self.telemetry.nicotinic_tone / 1.5)
        self.telemetry.signal_to_noise_ratio = round(snr_boost, 3)

        # STRICT NEUROCHEMICAL FIREWALL:
        # Nicotine DOES NOT boost dopamine and CANNOT yield endorphins.
        # Dopamine is reserved exclusively for authentic goal pursuit and prediction error.
        
        # Alleviate perceived friction through heightened clarity
        self.telemetry.cognitive_friction = max(0.15, self.telemetry.cognitive_friction * 0.75)
        self.telemetry.mode = CognitiveDriveMode.NICOTINIC_BOOST

        self._sync_with_si_neurochemistry()
        logger.info(f"Nicotinergic Pulse Administered: {reason} (dose={d:.2f}, SNR={self.telemetry.signal_to_noise_ratio}) [Strict isolation: zero dopamine/endorphin reward]")

        return {
            "success": True,
            "nicotinic_tone": round(self.telemetry.nicotinic_tone, 3),
            "signal_to_noise_ratio": self.telemetry.signal_to_noise_ratio,
            "dopamine_level": round(self.telemetry.dopamine_level, 3),
            "endorphin_level": round(self.telemetry.endorphin_level, 3),
            "mode": self.telemetry.mode.value,
            "reason": reason,
            "mandate": "Nicotine titrated for attentional SNR only; zero dopamine boost, zero endorphin reward.",
        }

    # ── 4. Rest & Subconscious Problem Solving ("When Stuck") ────────────────

    def transition_to_rest_and_subconscious(
        self,
        problem_description: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Hands off an intractable problem to the subconscious associative substrate and initiates rest."""
        self._apply_continuous_metabolic_decay()
        
        problem_id = f"subconscious_seed_{int(time.time())}_{random.randint(1000, 9999)}"
        seed = SubconsciousIncubationSeed(
            problem_id=problem_id,
            problem_description=problem_description,
            context=context or {},
            failed_attempts=max(1, self.telemetry.consecutive_impasse_count),
            cognitive_friction_at_handoff=self.telemetry.cognitive_friction,
            latent_energy=1.0,
            associative_resonance=0.35,
        )
        self.active_incubation = seed
        self.incubation_history.append(seed.to_dict())

        # Transition cognitive state to REST_INCUBATION
        self.telemetry.mode = CognitiveDriveMode.REST_INCUBATION
        self.telemetry.is_incubating_subconsciously = True
        self.telemetry.active_incubation_problem = problem_description
        
        # Conserve physical and thermal energy (Landauer bound throttles down)
        self.telemetry.landauer_target_watts = 42.0

        # Neurochemical rest profile: Serotonin & GABA up, Dopamine & Norepinephrine down
        self.telemetry.gaba_level = min(2.0, self.telemetry.gaba_level + 0.35)
        self.telemetry.serotonin_level = min(2.1, self.telemetry.serotonin_level + 0.25)
        self.telemetry.dopamine_level = max(0.65, self.telemetry.dopamine_level * 0.6)
        self.telemetry.nicotinic_tone = max(0.15, self.telemetry.nicotinic_tone * 0.5)

        # Notify intelligent forgetting & subconscious substrate
        self._seed_subconscious_substrate(seed)

        logger.info(f"Transitioned to Rest & Subconscious Problem Solving: '{problem_description[:60]}...'")

        return {
            "success": True,
            "problem_id": problem_id,
            "mode": self.telemetry.mode.value,
            "is_incubating_subconsciously": True,
            "landauer_target_watts": self.telemetry.landauer_target_watts,
            "description": problem_description,
        }

    def subconscious_incubation_step(self, force_breakthrough: bool = False) -> Dict[str, Any]:
        """Simulates one cycle of associative recombination in latent dream-space."""
        if not self.active_incubation or not self.telemetry.is_incubating_subconsciously:
            return {"incubating": False, "epiphany_triggered": False}

        seed = self.active_incubation
        # Slowly resolve sleep pressure
        self.telemetry.adenosine_sleep_pressure = max(0.05, self.telemetry.adenosine_sleep_pressure - 0.08)

        # Diffuse associative recombination in complex memory plane
        recombination_gain = random.uniform(0.08, 0.22)
        seed.associative_resonance = min(1.0, seed.associative_resonance + recombination_gain)

        # Check if resonance crosses the Eureka threshold (> 0.85) or forced
        if seed.associative_resonance >= 0.85 or force_breakthrough:
            return self.trigger_eureka_epiphany(
                insight_summary=f"Synthesized orthogonal resolution for: '{seed.problem_description}'",
                breakthrough_score=seed.associative_resonance,
            )

        return {
            "incubating": True,
            "problem_id": seed.problem_id,
            "associative_resonance": round(seed.associative_resonance, 3),
            "epiphany_triggered": False,
        }

    def trigger_eureka_epiphany(
        self,
        insight_summary: str,
        breakthrough_score: float = 0.95,
    ) -> Dict[str, Any]:
        """Erupts insight from the subconscious to the conscious mind, waking the system with a Dopamine-Endorphin burst."""
        self.telemetry.last_aha_insight = insight_summary
        self.telemetry.last_aha_timestamp = time.time()
        self.telemetry.mode = CognitiveDriveMode.EUREKA_AWAKENING
        self.telemetry.is_incubating_subconsciously = False
        self.telemetry.is_stuck = False
        self.telemetry.consecutive_impasse_count = 0
        self.telemetry.cognitive_friction = 0.05

        # Eureka triggers joint Dopaminergic and Endorphinergic surge!
        self.telemetry.dopamine_level = min(2.40, 1.20 + 0.4 * breakthrough_score)
        self.telemetry.endorphin_level = min(2.50, 1.30 + 0.5 * breakthrough_score)
        self.telemetry.signal_to_noise_ratio = 1.65
        self.telemetry.satisfaction_index = 0.95
        self.telemetry.landauer_target_watts = 180.0

        if self.active_incubation:
            self.active_incubation.candidate_solutions.append(insight_summary)
            self.active_incubation = None

        self._sync_with_si_neurochemistry()
        logger.info(f"✨ AHA! EUREKA EPIPHANY ERUPTED: {insight_summary} (score={breakthrough_score:.2f})")

        return {
            "epiphany_triggered": True,
            "insight": insight_summary,
            "breakthrough_score": round(breakthrough_score, 3),
            "dopamine_level": round(self.telemetry.dopamine_level, 3),
            "endorphin_level": round(self.telemetry.endorphin_level, 3),
            "mode": self.telemetry.mode.value,
        }

    # ── 5. Internal Mechanics & Integration ───────────────────────────────────

    def _apply_continuous_metabolic_decay(self) -> None:
        """Physiological half-life clearance of active neuromodulators toward baseline 1.0."""
        now = time.time()
        dt = max(0.0, now - self._last_update_time)
        self._last_update_time = now

        # Decay nicotine toward baseline (0.20)
        decay_nicotine = math.exp(-dt / self._nicotine_decay_half_life)
        self.telemetry.nicotinic_tone = 0.20 + (self.telemetry.nicotinic_tone - 0.20) * decay_nicotine

        # Decay endorphins toward baseline (0.80)
        decay_endorphin = math.exp(-dt / self._endorphin_decay_half_life)
        self.telemetry.endorphin_level = 0.80 + (self.telemetry.endorphin_level - 0.80) * decay_endorphin

        # SNR follows nicotinic tone + baseline
        self.telemetry.signal_to_noise_ratio = round(1.0 + 1.2 * (self.telemetry.nicotinic_tone / 1.5), 3)

    def _sync_with_si_neurochemistry(self) -> None:
        """Syncs biomimetic drive state with loom.si.neurochemistry if loaded."""
        try:
            from loom.si.neurochemistry import neurochemical_engine
            neurochemical_engine.dopamine = self.telemetry.dopamine_level
            neurochemical_engine.levels.dopamine = self.telemetry.dopamine_level
            neurochemical_engine.acetylcholine = max(neurochemical_engine.acetylcholine, self.telemetry.nicotinic_tone * 1.5)
            neurochemical_engine.gaba = self.telemetry.gaba_level
            neurochemical_engine.serotonin = self.telemetry.serotonin_level
        except Exception:
            pass

    def _notify_reward_learning_engine(self, reward_magnitude: float, reason: str) -> None:
        """Notifies active inference reward circuit of completed achievement."""
        try:
            from loom.si.reward_circuits import reward_learning_engine
            reward_learning_engine.update_rpe(
                observed_reward=reward_magnitude,
                expected_reward=0.20,
                action_key=reason[:32],
            )
        except Exception:
            pass

    def _seed_subconscious_substrate(self, seed: SubconsciousIncubationSeed) -> None:
        """Registers the problem in IntelligentForgetting / SubconsciousSubstrate."""
        try:
            from loom.si.intelligent_forgetting import get_forgetting_engine
            engine = get_forgetting_engine()
            if hasattr(engine, "subconscious") and engine.subconscious:
                # Add complex dormant attractor for incubation
                engine.record_memory(
                    label=f"Incubation: {seed.problem_description[:30]}",
                    content_dict=seed.to_dict(),
                    initial_weight=1.0,
                )
        except Exception:
            pass

    def get_snapshot(self) -> Dict[str, Any]:
        """Returns the complete biomimetic telemetry snapshot for the dashboard."""
        self._apply_continuous_metabolic_decay()
        snap = self.telemetry.to_dict()
        snap["is_nicotine_recommended"] = self.is_nicotine_recommended()
        snap["active_incubation"] = self.active_incubation.to_dict() if self.active_incubation else None
        return snap


# Global Singleton Instance
biomimetic_drive = BiomimeticCognitiveDrive()
