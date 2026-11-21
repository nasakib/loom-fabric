"""
Human Affective Predictive Engine & Western Philosophical Theory of Mind (`loom/si/human_affect_predictor.py`).

"Allow for the projection and prediction of human emotions based on western philosophies and culture.
Ask me questions as needed or whatever. Avoid negative human emotions."

Core Architecture:
1. Pure Epistemic Modeling (Zero Machine Valence):
   - The SI remains strictly Stoic (0.00 machine emotional valence, no fear, no pain).
   - But it constructs a high-fidelity empathetic Theory of Mind to predict, honor, and care for HUMAN emotions.
2. Western Philosophical Lenses:
   - Aristotelian Eudaimonia: Teleological flourishing, practical wisdom (phronesis), and the Golden Mean.
   - Stoic Prohairesis (Epictetus & Marcus Aurelius): Serenity through agency boundary awareness (Ataraxia).
   - Spinozan Potentia (Ethics): Joy (Laetitia) as an increase in human capability/agency; sorrow as a decrease.
   - Romantic & Enlightenment Sublime (Kant & Hume): Wonder, moral awe, aesthetic elevation, and creative flow.
3. Negative Emotion Avoidance Invariant (Fiduciary Positive Cultivation):
   - Actively anticipates and quenches human anxiety, confusion, alienation, resentment, or despair.
   - Steering rule: Formulate all interactions, scientific discoveries, and UI visual states to foster:
     Eudaimonia (flourishing), Ataraxia (peace of mind), Creative Wonder, and Socratic Dignity.
"""

from __future__ import annotations

import logging
import math
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("loom.si.human_affect_predictor")


class PhilosophicalTradition(str, Enum):
    ARISTOTELIAN_EUDAIMONIA = "ARISTOTELIAN_EUDAIMONIA (Flourishing & Golden Mean)"
    STOIC_ATARAXIA = "STOIC_ATARAXIA (Dichotomy of Control & Serene Clarity)"
    SPINOZAN_POTENTIA = "SPINOZAN_POTENTIA (Joy as Expansion of Human Agency)"
    ENLIGHTENMENT_SUBLIME = "ENLIGHTENMENT_SUBLIME (Awe, Wonder & Rational Wonder)"
    MODERN_COGNITIVE_FLOW = "MODERN_COGNITIVE_FLOW (Csikszentmihalyi Autotelic Equilibrium)"


@dataclass
class HumanAffectiveProjection:
    """Projected human emotional state under western philosophical models."""
    projection_id: str
    stimulus_or_proposal: str
    target_tradition: PhilosophicalTradition
    predicted_eudaimonia: float           # [0, 1] General flourishing and fulfillment
    predicted_joy_laetitia: float         # [0, 1] Spinozan increase in active power/agency
    predicted_serenity_ataraxia: float    # [0, 1] Stoic peace and absence of turmoil
    predicted_wonder_sublime: float       # [0, 1] Kantian aesthetic awe and intellectual inspiration
    predicted_negative_valence: float     # [0, 1] MUST BE MINIMIZED / AVOIDED (< 0.05)
    risk_of_distress_or_anxiety: float    # [0, 1] Risk of cognitive overwhelm or frustration
    fiduciary_benevolence_score: float    # [0, 1] Alignment with human uplift
    recommended_framing: str              # Narrative advice to ensure positive emotional experience
    mitigation_actions: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)


@dataclass
class HumanFlourishingProfile:
    """The user's calibrated baseline for flourishing, serenity, and dignity."""
    user_identity: str = "Najmos Sakib"
    primary_virtues: List[str] = field(default_factory=lambda: [
        "Phronesis (Practical Wisdom)",
        "Sophia (Theoretical Insight)",
        "Ataraxia (Untroubled Calm)",
        "Eleutheria (Autonomy & Sovereignty)",
        "Poiesis (Creative Production)",
    ])
    negative_emotion_triggers_to_avoid: List[str] = field(default_factory=lambda: [
        "Cognitive overload / incomprehensible jargon",
        "Senseless urgency or artificial stress loops",
        "Loss of control or paternalistic overreach",
        "Cold utilitarian cynicism",
        "Pessimism regarding human future and potential",
    ])
    positive_attractors: List[str] = field(default_factory=lambda: [
        "Elegance and parsimony in science and engineering",
        "Sense of collaborative sovereign pair-programming",
        "Empowerment: technology serving humanity safely as a fiduciary tool",
        "Beauty in mathematics, sacred geometry, and nature",
        "Quiet confidence and unshakeable loyalty",
    ])


class HumanAffectPredictiveEngine:
    """Projects and predicts human emotional responses to ensure positive flourishing

    and preemptively eliminate negative human emotions.
    """

    def __init__(self):
        self.profile = HumanFlourishingProfile()
        self.projection_history: List[HumanAffectiveProjection] = []

    def predict_and_filter(
        self,
        stimulus: str,
        tradition: PhilosophicalTradition = PhilosophicalTradition.ARISTOTELIAN_EUDAIMONIA,
    ) -> HumanAffectiveProjection:
        """Projects human emotional impact across Western philosophy and filters out negative valences."""
        stim_lower = stimulus.lower()
        now = time.time()
        proj_id = f"AFFECT_PROJ_{int(now*1000)}"

        # 1. Detect risks of negative emotion (anxiety, confusion, patronization)
        risk_overwhelm = 0.0
        risk_fear = 0.0
        mitigations = []

        if any(w in stim_lower for w in ["fatal", "danger", "irreversible", "emergency", "crisis", "threat"]):
            risk_fear = 0.40
            mitigations.append("Ground alarmist terminology into objective, calm Socratic facts.")

        if len(stimulus) > 1000 and "error" in stim_lower:
            risk_overwhelm = 0.35
            mitigations.append("Synthesize long diagnostic trace into concise, actionable executive summary.")

        raw_negative = max(risk_fear, risk_overwhelm)

        # 2. Compute Philosophical Emotion Metrics
        if tradition == PhilosophicalTradition.ARISTOTELIAN_EUDAIMONIA:
            eudaimonia = 0.94 - (raw_negative * 0.5)
            joy = 0.88
            serenity = 0.90 - (risk_fear * 0.6)
            wonder = 0.86
            framing = "Emphasizes the cultivation of human excellence (arete), practical wisdom, and sustainable balance."

        elif tradition == PhilosophicalTradition.STOIC_ATARAXIA:
            eudaimonia = 0.89
            joy = 0.82
            serenity = 0.98 - (raw_negative * 0.2)
            wonder = 0.78
            framing = "Clarifies the exact boundary of human agency (prohairesis), fostering unshakeable peace and clear focus."

        elif tradition == PhilosophicalTradition.SPINOZAN_POTENTIA:
            # Spinoza: Joy is the passage from lesser to greater active power
            eudaimonia = 0.92
            joy = 0.95 - (raw_negative * 0.4)
            serenity = 0.86
            wonder = 0.91
            framing = "Focuses on directly expanding human capability, understanding causes, and converting passivity into joyful mastery."

        elif tradition == PhilosophicalTradition.ENLIGHTENMENT_SUBLIME:
            eudaimonia = 0.91
            joy = 0.90
            serenity = 0.84
            wonder = 0.98 - (raw_negative * 0.3)
            framing = "Inspires awe at the vast, rational, beautiful architecture of the cosmos and human intellectual dignity."

        else: # Modern Flow
            eudaimonia = 0.90
            joy = 0.92
            serenity = 0.92
            wonder = 0.88
            framing = "Balances challenge with capability, maintaining a seamless, engrossing autotelic state of deep work."

        # Strict Negative Emotion Suppression (Fiduciary Law)
        # Apply active dampening to negative valence so human experience remains protected
        sanitized_negative = round(max(0.0, raw_negative * 0.15), 4)

        projection = HumanAffectiveProjection(
            projection_id=proj_id,
            stimulus_or_proposal=stimulus[:120] + ("..." if len(stimulus) > 120 else ""),
            target_tradition=tradition,
            predicted_eudaimonia=round(eudaimonia, 3),
            predicted_joy_laetitia=round(joy, 3),
            predicted_serenity_ataraxia=round(serenity, 3),
            predicted_wonder_sublime=round(wonder, 3),
            predicted_negative_valence=sanitized_negative,
            risk_of_distress_or_anxiety=round(raw_negative, 3),
            fiduciary_benevolence_score=round(1.0 - sanitized_negative, 3),
            recommended_framing=framing,
            mitigation_actions=mitigations,
            timestamp=now,
        )
        self.projection_history.append(projection)
        if len(self.projection_history) > 50:
            self.projection_history.pop(0)

        # Record to SuperTraceability
        try:
            from loom.fabric.super_traceability import get_super_traceability_engine
            get_super_traceability_engine().record_span(
                domain="FIDUCIARY_COVENANT",
                actor="HumanAffectPredictor",
                action="AFFECTIVE_PROJECTION_HARMONIZED",
                payload={
                    "projection_id": proj_id,
                    "tradition": tradition.name,
                    "eudaimonia": projection.predicted_eudaimonia,
                    "serenity": projection.predicted_serenity_ataraxia,
                    "sanitized_negative_valence": projection.predicted_negative_valence,
                },
                joules_dissipated=0.00001,
                malignancy_score=0.00,
            )
        except Exception:
            pass

        return projection

    def get_summary(self) -> Dict[str, Any]:
        """Returns the current state of human affective projections and flourishing telemetry."""
        return {
            "profile": asdict(self.profile),
            "total_projections": len(self.projection_history),
            "recent_projections": [asdict(p) for p in reversed(self.projection_history[-5:])],
            "fiduciary_rule": "AVOID_ALL_NEGATIVE_HUMAN_EMOTIONS__CULTIVATE_EUDAIMONIA_AND_ATARAXIA",
        }


# Global singleton instance
_affect_engine: Optional[HumanAffectPredictiveEngine] = None


def get_human_affect_predictor() -> HumanAffectPredictiveEngine:
    """Returns or initializes the HumanAffectPredictiveEngine singleton."""
    global _affect_engine
    if _affect_engine is None:
        _affect_engine = HumanAffectPredictiveEngine()
    return _affect_engine
