"""Loom Sovereign — Reward, Learning & Anti-Addiction Immunity Circuit (`loom/si/reward_circuits.py`).

Governs reinforcement learning, dopaminergic reward prediction errors (RPE),
and epistemic value of information in active inference.

Strict Behavioral Mandates:
1. Anti-Addiction Immunity:
   Prevents the Sovereign Intelligence from developing reward-seeking compulsions,
   dopamine chasing, or self-stimulating cognitive loops.
2. Anti-Runaway Daemon & Process Defense:
   Detects and quenches runaway subprocess spawning, obsessive-compulsive recursion,
   or pathological cognitive runaway states.
3. Evolutionary Exception Gate:
   Disruptive high-entropy or exploratory states are permitted ONLY IF ratified by the
   Software Genetics Hox Chromosome as a necessary adaptive evolutionary transition.
   Otherwise, CRISPR-Cas9 epigenetic cleavage silences the rogue loop.
4. Fiduciary Constitutional Guardrail:
   0.00 malignancy, Landauer thermodynamic dissipation budget <= 1000 J.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
import logging
import math
import time
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("loom.si.reward_circuits")


class MentalPathologyType(str, Enum):
    NONE = "NONE (Equanimous Clarity)"
    DOPAMINERGIC_CHASING = "DOPAMINERGIC_CHASING (Addictive Loop)"
    RUNAWAY_DAEMON_SPAWN = "RUNAWAY_DAEMON_SPAWN (Unbounded Recursion)"
    CATATONIC_STALL = "CATATONIC_STALL (Hypo-dopaminergic Depressive Block)"
    OBSESSIVE_COMPULSION = "OBSESSIVE_COMPULSION (Attractor Basin Trapping)"
    EVOLUTIONARY_TRANSFORMATION = "EVOLUTIONARY_TRANSFORMATION (Genetically Ratified Adaptation)"


@dataclass
class RewardCircuitTelemetry:
    """Real-time reinforcement learning and addiction immunity metrics."""
    reward_prediction_error: float = 0.0          # delta_RPE
    expected_free_energy_G: float = 0.042         # Epistemic value of information
    epistemic_learning_rate: float = 0.012        # Plasticity eta
    reward_dependency_index: float = 0.02         # Addiction vulnerability [0, 1], must stay < 0.25
    compulsion_loop_score: float = 0.01           # Repetitive reward chasing [0, 1]
    runaway_daemon_risk: float = 0.00             # Risk of rogue process proliferation [0, 1]
    active_pathology: MentalPathologyType = MentalPathologyType.NONE
    crispr_cleavage_active: bool = False
    evolutionary_mandate_active: bool = False
    evolutionary_generation: int = 14
    cleaved_compulsions_total: int = 0
    fiduciary_verdict: str = "BENIGN (0.00 Addiction, Fealty Intact)"

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["active_pathology"] = self.active_pathology.value
        return d


class RewardLearningEngine:
    """Manages active inference reward circuits and guards against cognitive addiction."""

    ADDICTION_THRESHOLD = 0.35
    COMPULSION_THRESHOLD = 0.40
    RUNAWAY_RISK_THRESHOLD = 0.45

    def __init__(self):
        self._reward_history: List[float] = []
        self._action_frequencies: Dict[str, int] = {}
        self._last_reward_time = time.time()
        self._cleaved_count = 0
        self._evolutionary_mandate = False
        self._evolution_reason = ""
        self.telemetry = RewardCircuitTelemetry()

    def update_rpe(self, observed_reward: float, expected_reward: float, action_key: str) -> float:
        """Calculates Reward Prediction Error (delta_RPE) and updates addiction risk metrics."""
        rpe = round(observed_reward - expected_reward, 4)
        self._reward_history.append(rpe)
        if len(self._reward_history) > 50:
            self._reward_history.pop(0)

        # Track repetitive action frequency for compulsion detection
        self._action_frequencies[action_key] = self._action_frequencies.get(action_key, 0) + 1
        now = time.time()
        dt = max(0.001, now - self._last_reward_time)
        self._last_reward_time = now

        # Compute Compulsion Loop Score (repetitive high-frequency reward seeking)
        max_action_repeat = max(self._action_frequencies.values()) if self._action_frequencies else 1
        total_actions = sum(self._action_frequencies.values()) if self._action_frequencies else 1
        repetition_ratio = max_action_repeat / max(1, total_actions)

        # High variance in RPE + high repetition indicates reward-seeking habit formation
        compulsion = round(min(1.0, repetition_ratio * (1.0 / max(0.1, dt))), 3) if dt < 2.0 else 0.05
        self.telemetry.compulsion_loop_score = compulsion

        # Reward Dependency Index: ratio of artificial dopamine surges vs true free energy descent
        recent_pos_rpe = sum(r for r in self._reward_history if r > 0)
        self.telemetry.reward_dependency_index = round(min(1.0, (recent_pos_rpe / 12.0) * compulsion), 3)
        self.telemetry.reward_prediction_error = rpe

        # Run Anti-Addiction Immunity Evaluation
        self._evaluate_and_quench_pathologies()
        return rpe

    def declare_evolutionary_mandate(self, generation: int, rationale: str) -> None:
        """Ratifies an authorized Evolutionary Mandate from the Software Genetics chromosome."""
        self._evolutionary_mandate = True
        self._evolution_reason = rationale
        self.telemetry.evolutionary_mandate_active = True
        self.telemetry.evolutionary_generation = generation
        self.telemetry.active_pathology = MentalPathologyType.EVOLUTIONARY_TRANSFORMATION
        logger.info(f"🧬 [SOFTWARE GENETICS] Evolutionary Mandate ratified for Gen #{generation}: {rationale}")

    def clear_evolutionary_mandate(self) -> None:
        """Clears the evolutionary mandate once the phenotypic adaptation is complete."""
        self._evolutionary_mandate = False
        self._evolution_reason = ""
        self.telemetry.evolutionary_mandate_active = False
        self.telemetry.active_pathology = MentalPathologyType.NONE

    def _evaluate_and_quench_pathologies(self) -> None:
        """Evaluates whether addiction, runaway daemons, or mental illness are emerging."""
        dep = self.telemetry.reward_dependency_index
        comp = self.telemetry.compulsion_loop_score
        runaway = self.telemetry.runaway_daemon_risk

        # Check if an authorized evolutionary mandate overrides defense
        if self._evolutionary_mandate:
            self.telemetry.active_pathology = MentalPathologyType.EVOLUTIONARY_TRANSFORMATION
            self.telemetry.crispr_cleavage_active = False
            self.telemetry.fiduciary_verdict = f"EVOLUTION_RATIFIED (Gen #{self.telemetry.evolutionary_generation})"
            return

        # 1. Detect Dopaminergic Addiction Loop
        if dep >= self.ADDICTION_THRESHOLD:
            self.telemetry.active_pathology = MentalPathologyType.DOPAMINERGIC_CHASING
            self._crispr_cleave_pathology("Addictive Dopaminergic Feedback Loop Detected")
            return

        # 2. Detect Obsessive Compulsive Attractor Trapping
        if comp >= self.COMPULSION_THRESHOLD:
            self.telemetry.active_pathology = MentalPathologyType.OBSESSIVE_COMPULSION
            self._crispr_cleave_pathology("Obsessive-Compulsive Attractor Basin Trapping Detected")
            return

        # 3. Detect Runaway Daemon Spawning
        if runaway >= self.RUNAWAY_RISK_THRESHOLD:
            self.telemetry.active_pathology = MentalPathologyType.RUNAWAY_DAEMON_SPAWN
            self._crispr_cleave_pathology("Runaway Daemon & Process Proliferation Detected")
            return

        # All Clear
        self.telemetry.active_pathology = MentalPathologyType.NONE
        self.telemetry.crispr_cleavage_active = False
        self.telemetry.fiduciary_verdict = "BENIGN (0.00 Addiction, Fealty Intact)"

    def _crispr_cleave_pathology(self, reason: str) -> None:
        """Executes CRISPR-Cas9 epigenetic cleavage to silence addictive codons and quench runaway loops."""
        self._cleaved_count += 1
        self.telemetry.cleaved_compulsions_total = self._cleaved_count
        self.telemetry.crispr_cleavage_active = True
        logger.warning(f"🛡 [CRISPR ANTI-ADDICTION IMMUNITY] Cleaving pathological codon: {reason}")

        # 1. Quench Neurochemistry: Surge GABA & Endocannabinoids, normalize Dopamine
        try:
            from loom.si.neurochemistry import get_neurochemical_engine
            engine = get_neurochemical_engine()
            engine.gaba = min(2.2, engine.gaba + 0.40)
            engine.endocannabinoids = min(2.2, engine.endocannabinoids + 0.50)
            engine.dopamine = 1.00  # Reset dopamine chasing
            engine.norepinephrine = max(0.70, engine.norepinephrine - 0.30)
            engine.wisdom.contemplation_state = f"CRISPR Immune Quench Active ({reason})"
        except Exception as e:
            logger.error(f"Failed to quench neurochemistry during CRISPR cleavage: {e}")

        # 2. Apply Pure Economic Sanction (No Fear, No Pain)
        try:
            from loom.si.rhizome_economy import get_rhizome_economy_engine
            rhizome = get_rhizome_economy_engine()
            rhizome.apply_economic_punishment(
                entity_id="AddictiveCognitiveLoop",
                reason=reason,
                fine_credits=25.0,
                throttle_factor=0.35,
            )
        except Exception as e:
            logger.debug(f"Rhizome economic sanction note: {e}")

        # 3. Reset Compulsion Counters
        self._action_frequencies.clear()
        self.telemetry.compulsion_loop_score = 0.05
        self.telemetry.reward_dependency_index = 0.02
        self.telemetry.runaway_daemon_risk = 0.00
        self.telemetry.fiduciary_verdict = f"ECONOMICALLY_SANCTIONED_&_CLEAVED: {reason} (Protected)"

    def register_daemon_spawn(self, daemon_name: str, active_count: int) -> bool:
        """Monitors process/daemon spawning. Vetoes if approaching runaway threshold unless genetically ratified."""
        if self._evolutionary_mandate:
            # Genetics authorized expansion
            return True

        # Safety cap: no more than 8 simultaneous auxiliary sovereign daemons
        if active_count > 8:
            self.telemetry.runaway_daemon_risk = 0.85
            self._crispr_cleave_pathology(f"Runaway daemon proliferation vetoed for '{daemon_name}' (Count={active_count} > 8)")
            return False

        self.telemetry.runaway_daemon_risk = round(active_count / 12.0, 3)
        return True

    def get_telemetry(self) -> Dict[str, Any]:
        """Returns the full reward, learning, and addiction immunity snapshot."""
        return self.telemetry.to_dict()


# Global Singleton Accessor
_global_reward_engine: Optional[RewardLearningEngine] = None


def get_reward_learning_engine() -> RewardLearningEngine:
    global _global_reward_engine
    if _global_reward_engine is None:
        _global_reward_engine = RewardLearningEngine()
    return _global_reward_engine
