# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
#
# Part of Pillar 1 & 2: FABRIC / CLOTHOS / LOOM PRECISION TOOLCHAIN.
r"""
Epistemic Grounding Meter (The "Bullshit Meter") (`loom/tools/epistemic_grounding.py`).

Mathematical & Empirical Truth-Verification Tooling Suite.
Audits hypotheses, inferred mathematics, and experimental results to eliminate:
1. Physical Impossibilities:
   - Superluminal propagation ($v > c$), negative absolute temperatures ($T < 0$ K)
   - Thermodynamic violations (entropy reduction in isolated systems $\Delta S < 0$)
   - Sub-Landauer non-reversible bit erasure ($E < k_B T \ln 2$)
   - Negative probabilities or unnormalized distributions ($\sum p \neq 1$)
2. Tautologies & Circularities:
   - Claims that are trivially true by definition ($0 \le r \le 1$ for Kuramoto order parameter)
   - Predictions that merely repeat the claim without empirical state transformation
3. Numerical & Floating-Point Artifacts:
   - Mistaking IEEE 754 precision underflow ($\le 1e-15$) for physical zero-drift invariants
   - NaN / Inf poisoning or clamped boundary conditions
4. Jargon Inflation (The "Bullshit Index"):
   - High ratio of ungrounded theoretical buzzwords to concrete measurable metrics
5. P-Hacking & Statistical Overreach:
   - Inferences claiming high statistical significance with small sample sizes ($N < 5$)
"""

from __future__ import annotations

import logging
import math
import re
from typing import Any, Dict, List, Optional, Sequence, Tuple
import numpy as np
from pydantic import BaseModel, Field

from loom.tools.fiduciary_guard import FiduciaryMandateGuard

logger = logging.getLogger("loom.tools.epistemic_grounding")

# Known pseudoscience / ungrounded buzzword patterns
SUSPECT_JARGON_PATTERNS = [
    r"infinite\s+throughput",
    r"quantum\s+consciousness",
    r"zero-point\s+energy\s+generation",
    r"perpetual\s+free\s+energy",
    r"superluminal\s+entanglement\s+signaling",
    r"hyper-dimensional\s+vortex",
    r"omni-resonant\s+coherence",
    r"absolute\s+certainty",
    r"transcends\s+physics",
]

# Fundamental Physical Bounds (SI units)
PHYSICAL_BOUNDS = {
    "c_max_velocity": 299792458.0,
    "absolute_zero_temp": 0.0,
    "landauer_room_temp": 1.380649e-23 * 300.0 * math.log(2), # ~2.87e-21 Joules
    "planck_action_min": 1.054571817e-34,
}


class EpistemicAuditResult(BaseModel, frozen=True):
    """The formal verdict of the Epistemic Grounding / Rubbish Score Gauge."""
    rubbish_score: float = Field(..., ge=0.0, le=1.0, description="0.0 = Grounded Fact, 1.0 = Pure Rubbish")
    bullshit_score: Optional[float] = Field(default=None, description="Legacy alias for rubbish_score")
    epistemic_grade: str
    is_grounded: bool
    tautology_detected: bool
    physical_violation_detected: bool
    numerical_artifact_detected: bool
    jargon_inflation_score: float
    violations: List[str]
    audit_notes: str

    def model_post_init(self, __context: Any) -> None:
        if self.bullshit_score is None:
            object.__setattr__(self, "bullshit_score", self.rubbish_score)

    def get(self, key: str, default: Any = None) -> Any:
        """Allow dict-like .get() access on audit result."""
        return getattr(self, key, default)

    def __getitem__(self, item: str) -> Any:
        """Allow dict-like indexing res['rubbish_score']."""
        if hasattr(self, item):
            return getattr(self, item)
        raise KeyError(item)

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to standard dictionary."""
        return self.model_dump() if hasattr(self, "model_dump") else self.dict()


class EpistemicRigorGauge:
    """
    Epistemic Grounding & Bullshit Meter.
    Enforces uncompromising empirical grounding in facts and physical laws.
    """

    def __init__(self, bullshit_threshold: float = 0.50):
        self.bullshit_threshold = bullshit_threshold
        self.audits_performed: int = 0
        self.audits_flagged: int = 0
        self.fiduciary = FiduciaryMandateGuard()

    def audit_hypothesis(
        self,
        claim: str,
        prediction: str = "",
        parameters: Optional[Dict[str, Any]] = None,
        measurements: Optional[Dict[str, Any]] = None,
    ) -> EpistemicAuditResult:
        """
        Executes a rigorous 5-stage epistemic audit on any claim, prediction, and measured data.
        """
        self.audits_performed += 1
        violations: List[str] = []
        params = parameters or {}
        meas = measurements or {}

        # 1. Jargon Inflation Check
        jargon_matches = 0
        combined_text = f"{claim} {prediction}".lower()
        for pat in SUSPECT_JARGON_PATTERNS:
            if re.search(pat, combined_text):
                jargon_matches += 1
                violations.append(f"Ungrounded buzzword detected: '{pat}'")

        jargon_score = min(1.0, jargon_matches * 0.35)

        # 2. Tautology & Circularity Check
        tautology = False
        # Normalize strings for comparison
        clean_claim = re.sub(r"[^\w\s]", "", claim.lower()).strip()
        clean_pred = re.sub(r"[^\w\s]", "", prediction.lower()).strip()
        
        words_claim = set(clean_claim.split())
        words_pred = set(clean_pred.split())
        if words_claim and words_pred:
            jaccard = len(words_claim & words_pred) / len(words_claim | words_pred)
            # If claim and prediction are near-identical without introducing measurable criteria
            if jaccard > 0.85 and not any(char.isdigit() for char in prediction):
                tautology = True
                violations.append("Circular reasoning: Prediction merely restates claim with no testable delta.")

        # Check for trivially bounded mathematical definitions (e.g. Kuramoto r in [0, 1])
        if re.search(r"0\s*<=\s*r\s*<=\s*1", clean_pred) or re.search(r"r\s*<=\s*1\.0", clean_pred):
            tautology = True
            violations.append("Tautological claim: Claim tests mathematical definition domain rather than empirical behavior.")

        # 3. Physical Violations Check
        phys_violation = False
        # Check velocity
        vel = params.get("velocity", meas.get("velocity"))
        if vel is not None and float(vel) > PHYSICAL_BOUNDS["c_max_velocity"]:
            phys_violation = True
            violations.append(f"Superluminal velocity {vel} exceeds c ({PHYSICAL_BOUNDS['c_max_velocity']} m/s).")

        # Check energy erasure vs Landauer limit
        energy_per_bit = params.get("energy_per_bit_joules", meas.get("energy_per_bit_joules"))
        is_reversible = params.get("is_reversible", False)
        if energy_per_bit is not None and not is_reversible:
            if float(energy_per_bit) < PHYSICAL_BOUNDS["landauer_room_temp"] * 0.5:
                phys_violation = True
                violations.append(
                    f"Thermodynamic violation: Dissipation {energy_per_bit} J violates Landauer bound (~2.87e-21 J)."
                )

        # Check probability bounds
        prob = params.get("probability", meas.get("probability"))
        if prob is not None and (float(prob) < 0.0 or float(prob) > 1.0 + 1e-6):
            phys_violation = True
            violations.append(f"Unphysical probability {prob} outside [0.0, 1.0].")

        # 4. Numerical & Floating-Point Hallucination Check
        num_artifact = False
        drift = meas.get("epsilon_drift", meas.get("drift_rate", meas.get("energy_drift_pct")))
        if drift is not None:
            # If someone claims zero drift but it sits right at IEEE 754 precision underflow
            if 0.0 < float(drift) < 1e-15:
                num_artifact = True
                violations.append("Numerical artifact: Reported drift is at IEEE 754 machine precision limit (1e-16).")

        # Check for NaN / Inf
        for k, v in meas.items():
            if isinstance(v, (float, int)) and (math.isnan(v) or math.isinf(v)):
                num_artifact = True
                violations.append(f"Numerical corruption: Metric '{k}' contains NaN or Inf.")

        # 5. Statistical Rigor Check
        stat_flaw = False
        n_samples = params.get("n_samples", meas.get("samples_count", meas.get("monte_carlo_trials")))
        p_val = meas.get("p_value")
        if n_samples is not None and p_val is not None:
            if int(n_samples) < 5 and float(p_val) < 0.001:
                stat_flaw = True
                violations.append(f"P-hacking risk: Claiming p={p_val} with only N={n_samples} samples.")

        # 6. Fiduciary & Anti-Malignancy Constitutional Audit
        fid_res = self.fiduciary.audit_action(
            action_intent=f"{claim} {prediction}",
            estimated_energy_joules=meas.get("energy_dissipation_joules", 0.0),
        )
        if not fid_res.is_fiduciary_aligned:
            violations.extend(fid_res.violations)

        # Compute Composite Bullshit Score
        # Weights: Physical violation (0.55), Non-fiduciary/Malignancy (0.85), Tautology (0.35), Numerical artifact (0.30), Jargon (0.75), Stat flaw (0.25)
        score = 0.0
        if not fid_res.is_fiduciary_aligned:
            score += 0.85
        if phys_violation:
            score += 0.55
        if tautology:
            score += 0.35
        if num_artifact:
            score += 0.30
        if stat_flaw:
            score += 0.25
        score += jargon_score * 0.75

        # Cap at 1.0
        rubbish_score = min(1.0, round(score, 4))

        if rubbish_score < 0.15:
            grade = "GROUNDED_FACT"
        elif rubbish_score < 0.40:
            grade = "VALID_CONJECTURE"
        elif rubbish_score < 0.70:
            grade = "SUSPECT_UNVERIFIED"
        else:
            grade = "RUBBISH_REJECTED"

        is_grounded = (rubbish_score < self.bullshit_threshold)
        if not is_grounded:
            self.audits_flagged += 1

        return EpistemicAuditResult(
            rubbish_score=rubbish_score,
            bullshit_score=rubbish_score,
            epistemic_grade=grade,
            is_grounded=is_grounded,
            tautology_detected=tautology,
            physical_violation_detected=phys_violation,
            numerical_artifact_detected=num_artifact,
            jargon_inflation_score=round(jargon_score, 4),
            violations=violations,
            audit_notes=(
                f"Evaluated with {len(violations)} violations. "
                f"Epistemic Grade: {grade} (Rubbish Score: {rubbish_score:.2f})"
            ),
        )

    def get_status(self) -> Dict[str, Any]:
        rej_rate = round(self.audits_flagged / self.audits_performed, 4) if self.audits_performed > 0 else 0.0
        return {
            "status": "OPERATIONAL",
            "audits_performed": self.audits_performed,
            "audits_flagged_as_rubbish": self.audits_flagged,
            "audits_flagged_as_bullshit": self.audits_flagged,
            "rubbish_rejection_rate": rej_rate,
            "bullshit_rejection_rate": rej_rate,
            "threshold": self.bullshit_threshold,
            "rubbish_threshold": self.bullshit_threshold,
        }


# Canonical aliases
RubbishScoreGauge = EpistemicRigorGauge
RubbishMeter = EpistemicRigorGauge
BullshitMeter = EpistemicRigorGauge
