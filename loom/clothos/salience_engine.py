# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
ClothOS Weighted Importances & Dynamic Salience Engine (`loom/clothos/salience_engine.py`).

Provides quantitative attention allocation and memory prioritization:
1. Multi-Factor Salience Scoring:
   - Fiduciary Alignment (wf = 0.35): Direct benefit to operator Najmos Sakib and human agency.
   - Safety & Inviolability (ws = 0.25): Criticality to P0 Life Sanctity and 0.00 Malignancy.
   - Epistemic Value (we = 0.25): Reduction in predictive error / active inference surprise.
   - Thermodynamic Conservation (wt = 0.15): Compute efficiency (Joules spent per utility).
2. Dynamic Salience Decay & Reinforcement:
   - Routines and noise decay exponentially: S(t) = S_0 * exp(-lambda * delta_t).
   - High-salience memories resist decay and are prioritized for distillation into Wisdom Axioms.
   - Memories dropping below the pruning threshold are marked for Unitary Complex Plane Forgetting.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import logging
import math
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger("loom.clothos.salience")


@dataclass
class SalienceProfile:
    entity_id: str
    fiduciary_score: float       # 0.0 to 1.0
    safety_score: float          # 0.0 to 1.0
    epistemic_score: float       # 0.0 to 1.0
    thermodynamic_score: float   # 0.0 to 1.0
    composite_salience: float = 0.5
    decay_rate: float = 0.05
    last_reinforced: float = field(default_factory=time.time)
    reinforcement_count: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SalienceEngine:
    """Evaluates and dynamically modulates the importance of memories, tasks, and hypotheses."""

    # Canonical Weights
    W_FIDUCIARY = 0.35
    W_SAFETY = 0.25
    W_EPISTEMIC = 0.25
    W_THERMO = 0.15

    PRUNING_THRESHOLD = 0.18
    WISDOM_PROMOTION_THRESHOLD = 0.72

    def __init__(self):
        self.profiles: Dict[str, SalienceProfile] = {}

    def compute_salience(
        self,
        entity_id: str,
        fiduciary: float,
        safety: float,
        epistemic: float,
        thermo: float,
        decay_rate: float = 0.05,
    ) -> SalienceProfile:
        """Calculates normalized composite salience score in [0.0, 1.0]."""
        f = max(0.0, min(1.0, fiduciary))
        s = max(0.0, min(1.0, safety))
        e = max(0.0, min(1.0, epistemic))
        t = max(0.0, min(1.0, thermo))

        composite = (
            self.W_FIDUCIARY * f
            + self.W_SAFETY * s
            + self.W_EPISTEMIC * e
            + self.W_THERMO * t
        )

        profile = SalienceProfile(
            entity_id=entity_id,
            fiduciary_score=f,
            safety_score=s,
            epistemic_score=e,
            thermodynamic_score=t,
            composite_salience=round(composite, 4),
            decay_rate=decay_rate,
            last_reinforced=time.time(),
        )

        self.profiles[entity_id] = profile
        return profile

    def reinforce(self, entity_id: str, bonus: float = 0.15) -> float:
        """Reinforces salience upon successful usage, resetting decay clock."""
        if entity_id in self.profiles:
            p = self.profiles[entity_id]
            p.composite_salience = min(1.0, p.composite_salience + bonus)
            p.last_reinforced = time.time()
            p.reinforcement_count += 1
            return p.composite_salience
        return 0.5

    def get_decayed_salience(self, entity_id: str) -> float:
        """Computes current salience after temporal exponential decay."""
        if entity_id not in self.profiles:
            return 0.5
        p = self.profiles[entity_id]
        delta_hours = (time.time() - p.last_reinforced) / 3600.0
        # High safety memories resist decay (half-life extended by safety factor)
        resistance = 1.0 + (p.safety_score * 3.0)
        effective_decay = p.decay_rate / resistance
        decayed = p.composite_salience * math.exp(-effective_decay * delta_hours)
        return round(max(0.01, decayed), 4)

    def is_eligible_for_wisdom(self, entity_id: str) -> bool:
        """Checks if memory qualifies for permanent distillation into a Wisdom Axiom."""
        return self.get_decayed_salience(entity_id) >= self.WISDOM_PROMOTION_THRESHOLD

    def is_eligible_for_forgetting(self, entity_id: str) -> bool:
        """Checks if memory is transient noise eligible for unitary complex plane rotation."""
        return self.get_decayed_salience(entity_id) < self.PRUNING_THRESHOLD


salience_engine = SalienceEngine()
