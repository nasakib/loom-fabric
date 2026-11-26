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

from fractions import Fraction
import logging
import math
import re
import time
from typing import Any, Dict, List, Optional, Sequence, Tuple
import numpy as np
from pydantic import BaseModel, Field

from loom.tools.fiduciary_guard import FiduciaryMandateGuard

try:
    import z3
except ImportError:  # pragma: no cover - optional in environments without z3-solver
    z3 = None

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

_TEMPERATURE_KEYS = ("temperature_k", "temp_k", "kelvin", "absolute_temperature", "t_cold", "t_hot")
_ENTROPY_DELTA_KEYS = ("delta_s", "entropy_delta", "delta_entropy")
_VARIANCE_KEYS = ("var_theory", "var_empirical", "variance", "sigma_sq")
_MASS_KEYS = ("mass", "mass_in", "mass_out", "left_mass", "right_mass", "left net weight", "right net weight")
_PROBABILITY_KEYS = ("probability", "prob")
_DISTRIBUTION_KEYS = ("probabilities", "distribution")


def _iter_numeric_items(mapping: Dict[str, Any], prefix: str = "") -> List[Tuple[str, float]]:
    """Extracts scalar numeric leaves from nested dicts/lists for finiteness checks."""
    found: List[Tuple[str, float]] = []
    for k, v in mapping.items():
        path = f"{prefix}.{k}" if prefix else str(k)
        if isinstance(v, bool):
            continue
        if isinstance(v, (int, float)):
            found.append((path, float(v)))
        elif isinstance(v, dict):
            found.extend(_iter_numeric_items(v, prefix=path))
        elif isinstance(v, (list, tuple)):
            for idx, elem in enumerate(v):
                if isinstance(elem, (int, float)) and not isinstance(elem, bool):
                    found.append((f"{path}[{idx}]", float(elem)))
    return found


def _to_z3_real(val: float) -> Any:
    """Converts a finite float to an exact Z3 rational without IEEE-754 mantissa noise."""
    frac = Fraction(str(float(val)))
    return z3.RealVal(f"{frac.numerator}/{frac.denominator}")


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
    z3_status: str = Field(default="NOT_EVALUATED")
    unsat_core: List[str] = Field(default_factory=list)
    negative_space_geometry: Optional[Dict[str, Any]] = Field(default=None)

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
        self.negative_space_log: List[Dict[str, Any]] = []

    def verify_physical_constraints_z3(
        self,
        parameters: Optional[Dict[str, Any]] = None,
        measurements: Optional[Dict[str, Any]] = None,
        negative_space_obstacles: Optional[Sequence[Dict[str, Any]]] = None,
        candidate_position: Optional[Sequence[float]] = None,
        require_z3: bool = False,
    ) -> Dict[str, Any]:
        """
        Verifies physical conservation bounds and negative-space exclusion geometry via Z3 SMT
        with unsat_core tracking enabled. Explicitly logs unsat_core() negative-space geometry on UNSAT.
        """
        if z3 is None:
            if require_z3:
                neg_geom = {
                    "unsat_core": ["axiom_z3_solver_required"],
                    "reason": "z3-solver unavailable under fail-closed physical pre-filter",
                    "rotation_operator": "z * i (pi/2)",
                    "timestamp": time.time(),
                }
                self.negative_space_log.append(neg_geom)
                logger.error("Z3 unsat_core() fail-closed rejection: z3-solver package unavailable | geometry=%s", neg_geom)
                return {
                    "status": "UNSAT",
                    "z3_status": "UNAVAILABLE_FAIL_CLOSED",
                    "unsat_core": ["axiom_z3_solver_required"],
                    "negative_space_geometry": neg_geom,
                    "violations": ["Fail-closed physical pre-filter: z3-solver is required but unavailable."],
                }
            return {
                "status": "SKIPPED_NO_Z3",
                "z3_status": "SKIPPED_NO_Z3",
                "unsat_core": [],
                "negative_space_geometry": None,
                "violations": [],
            }

        params = parameters or {}
        meas = measurements or {}
        combined: Dict[str, Any] = {**params, **meas}
        is_reversible = bool(params.get("is_reversible", meas.get("is_reversible", False)))

        solver = z3.Solver()
        solver.set(unsat_core=True)
        tracked_exprs: Dict[str, str] = {}

        def track(label: str, expr: Any) -> None:
            tracked_exprs[label] = str(expr)
            solver.assert_and_track(expr, label)

        # 1. Finiteness axioms (checked before rational conversion)
        numeric_snapshot: Dict[str, float] = {}
        for path, num_val in _iter_numeric_items({"parameters": params, "measurements": meas}):
            if math.isnan(num_val) or math.isinf(num_val):
                track(f"axiom_finite_real_{path}", z3.BoolVal(False))
            else:
                numeric_snapshot[path] = num_val

        # 2. Physical conservation & domain bounds encoded in Z3
        lowered: Dict[str, Tuple[str, Any]] = {str(k).lower(): (str(k), v) for k, v in combined.items()}

        # Variances > 0
        for lkey, (orig_k, raw_v) in lowered.items():
            if lkey in _VARIANCE_KEYS or lkey.startswith("var_") or "variance" in lkey:
                if isinstance(raw_v, (int, float)) and not isinstance(raw_v, bool) and math.isfinite(float(raw_v)):
                    sym = z3.Real(f"var_{orig_k}")
                    track(f"obs_variance_{orig_k}", sym == _to_z3_real(float(raw_v)))
                    track(f"axiom_positive_variance_{orig_k}", sym > z3.RealVal(0))

        # Subluminal velocity |v| <= c
        for lkey in ("velocity", "speed"):
            if lkey in lowered:
                orig_k, raw_v = lowered[lkey]
                if isinstance(raw_v, (int, float)) and not isinstance(raw_v, bool) and math.isfinite(float(raw_v)):
                    v_sym = z3.Real(f"vel_{orig_k}")
                    c_bound = _to_z3_real(PHYSICAL_BOUNDS["c_max_velocity"])
                    track(f"obs_velocity_{orig_k}", v_sym == _to_z3_real(float(raw_v)))
                    track(f"axiom_subluminal_velocity_{orig_k}", z3.And(v_sym <= c_bound, v_sym >= -c_bound))

        # Absolute temperature >= 0 K
        for lkey in _TEMPERATURE_KEYS:
            if lkey in lowered:
                orig_k, raw_v = lowered[lkey]
                if isinstance(raw_v, (int, float)) and not isinstance(raw_v, bool) and math.isfinite(float(raw_v)):
                    t_sym = z3.Real(f"temp_{orig_k}")
                    track(f"obs_temperature_{orig_k}", t_sym == _to_z3_real(float(raw_v)))
                    track(f"axiom_absolute_zero_kelvin_{orig_k}", t_sym >= z3.RealVal(0))

        # Second Law entropy production delta_S >= 0
        for lkey in _ENTROPY_DELTA_KEYS:
            if lkey in lowered and not is_reversible:
                orig_k, raw_v = lowered[lkey]
                if isinstance(raw_v, (int, float)) and not isinstance(raw_v, bool) and math.isfinite(float(raw_v)):
                    ds_sym = z3.Real(f"delta_s_{orig_k}")
                    track(f"obs_entropy_{orig_k}", ds_sym == _to_z3_real(float(raw_v)))
                    track(f"axiom_second_law_entropy_{orig_k}", ds_sym >= z3.RealVal(0))

        # Landauer erasure bound
        if "energy_per_bit_joules" in lowered and not is_reversible:
            orig_k, raw_v = lowered["energy_per_bit_joules"]
            if isinstance(raw_v, (int, float)) and not isinstance(raw_v, bool) and math.isfinite(float(raw_v)):
                e_sym = z3.Real("energy_per_bit_joules")
                e_min = _to_z3_real(PHYSICAL_BOUNDS["landauer_room_temp"] * 0.5)
                track("obs_energy_per_bit", e_sym == _to_z3_real(float(raw_v)))
                track("axiom_landauer_erasure_bound", e_sym >= e_min)

        # Carnot efficiency bound
        if "efficiency" in lowered:
            _, raw_eta = lowered["efficiency"]
            if isinstance(raw_eta, (int, float)) and not isinstance(raw_eta, bool) and math.isfinite(float(raw_eta)):
                eta_sym = z3.Real("carnot_efficiency")
                track("obs_efficiency", eta_sym == _to_z3_real(float(raw_eta)))
                track("axiom_efficiency_unit_interval", z3.And(eta_sym >= z3.RealVal(0), eta_sym <= z3.RealVal(1)))
                if "t_cold" in lowered and "t_hot" in lowered:
                    tc_raw = lowered["t_cold"][1]
                    th_raw = lowered["t_hot"][1]
                    if (
                        isinstance(tc_raw, (int, float))
                        and isinstance(th_raw, (int, float))
                        and math.isfinite(float(tc_raw))
                        and math.isfinite(float(th_raw))
                    ):
                        tc_sym = z3.Real("carnot_t_cold")
                        th_sym = z3.Real("carnot_t_hot")
                        track("obs_carnot_temperatures", z3.And(tc_sym == _to_z3_real(float(tc_raw)), th_sym == _to_z3_real(float(th_raw))))
                        track("axiom_carnot_hot_positive", th_sym > z3.RealVal(0))
                        track("axiom_carnot_second_law", eta_sym * th_sym <= th_sym - tc_sym)

        # Kolmogorov probability bounds
        for lkey in _PROBABILITY_KEYS:
            if lkey in lowered:
                orig_k, raw_v = lowered[lkey]
                if isinstance(raw_v, (int, float)) and not isinstance(raw_v, bool) and math.isfinite(float(raw_v)):
                    p_sym = z3.Real(f"prob_{orig_k}")
                    track(f"obs_prob_{orig_k}", p_sym == _to_z3_real(float(raw_v)))
                    track(
                        f"axiom_kolmogorov_probability_{orig_k}",
                        z3.And(p_sym >= z3.RealVal(0), p_sym <= _to_z3_real(1.0 + 1e-6)),
                    )

        # Probability distribution normalization
        for lkey in _DISTRIBUTION_KEYS:
            if lkey in lowered:
                orig_k, raw_dist = lowered[lkey]
                if isinstance(raw_dist, (list, tuple)) and len(raw_dist) > 0:
                    p_syms = []
                    all_finite = True
                    for idx, elem in enumerate(raw_dist):
                        if not isinstance(elem, (int, float)) or isinstance(elem, bool) or not math.isfinite(float(elem)):
                            all_finite = False
                            break
                        ps = z3.Real(f"dist_{orig_k}_{idx}")
                        track(f"obs_dist_{orig_k}_{idx}", ps == _to_z3_real(float(elem)))
                        track(f"axiom_kolmogorov_dist_elem_{orig_k}_{idx}", z3.And(ps >= z3.RealVal(0), ps <= z3.RealVal(1)))
                        p_syms.append(ps)
                    if all_finite and p_syms:
                        total_p = z3.Sum(p_syms)
                        track(
                            f"axiom_probability_normalization_{orig_k}",
                            z3.And(total_p >= _to_z3_real(1.0 - 1e-3), total_p <= _to_z3_real(1.0 + 1e-3)),
                        )

        # Non-negative mass
        for lkey in _MASS_KEYS:
            if lkey in lowered:
                orig_k, raw_v = lowered[lkey]
                if isinstance(raw_v, (int, float)) and not isinstance(raw_v, bool) and math.isfinite(float(raw_v)):
                    m_sym = z3.Real(f"mass_{lkey}")
                    track(f"obs_mass_{lkey}", m_sym == _to_z3_real(float(raw_v)))
                    track(f"axiom_nonnegative_mass_{lkey}", m_sym >= z3.RealVal(0))

        # 3. Negative-space exclusion geometry (repulsion spheres + blocked state signatures)
        if negative_space_obstacles:
            for idx, obs in enumerate(negative_space_obstacles):
                if not isinstance(obs, dict):
                    continue
                obs_id = str(obs.get("obstacle_id", f"obs_{idx}"))

                center = obs.get("repulsion_center")
                radius = obs.get("radius")
                spatial_active = obs.get("spatial_active", True)
                if (
                    spatial_active
                    and candidate_position is not None
                    and len(candidate_position) >= 3
                    and isinstance(center, (list, tuple))
                    and len(center) >= 3
                    and isinstance(radius, (int, float))
                    and float(radius) > 0.0
                    and all(math.isfinite(float(c)) for c in candidate_position[:3])
                    and all(math.isfinite(float(c)) for c in center[:3])
                ):
                    px, py, pz = [z3.Real(f"cand_pos_{obs_id}_{ax}") for ax in ("x", "y", "z")]
                    track(
                        f"obs_candidate_position_{obs_id}",
                        z3.And(
                            px == _to_z3_real(float(candidate_position[0])),
                            py == _to_z3_real(float(candidate_position[1])),
                            pz == _to_z3_real(float(candidate_position[2])),
                        ),
                    )
                    cx, cy, cz = [_to_z3_real(float(c)) for c in center[:3]]
                    dist_sq = (px - cx) * (px - cx) + (py - cy) * (py - cy) + (pz - cz) * (pz - cz)
                    r_sq = _to_z3_real(float(radius) ** 2)
                    track(f"axiom_negative_space_radius_{obs_id}", dist_sq >= r_sq)

                blocked_state = obs.get("blocked_state")
                if isinstance(blocked_state, dict) and blocked_state:
                    diffs = []
                    matched_keys = True
                    for bk, bv in blocked_state.items():
                        if bk not in combined or not isinstance(bv, (int, float)) or not isinstance(combined[bk], (int, float)):
                            matched_keys = False
                            break
                        bv_f = float(bv)
                        cv_f = float(combined[bk])
                        if not (math.isfinite(bv_f) and math.isfinite(cv_f)):
                            matched_keys = False
                            break
                        c_sym = z3.Real(f"negstate_{obs_id}_{bk}")
                        track(f"obs_negstate_{obs_id}_{bk}", c_sym == _to_z3_real(cv_f))
                        diffs.append(z3.Abs(c_sym - _to_z3_real(bv_f)) > _to_z3_real(1e-6))
                    if matched_keys and diffs:
                        track(f"axiom_negative_space_exclusion_{obs_id}", z3.Or(diffs))

        check_result = solver.check()
        if check_result == z3.sat:
            return {
                "status": "SAT",
                "z3_status": "SAT",
                "unsat_core": [],
                "negative_space_geometry": None,
                "violations": [],
            }

        core = [str(c) for c in solver.unsat_core()]
        neg_geom = {
            "unsat_core": core,
            "core_size": len(core),
            "core_constraints": {label: tracked_exprs.get(label, "") for label in core},
            "rotation_operator": "z * i (pi/2)",
            "candidate_state": numeric_snapshot,
            "timestamp": time.time(),
        }
        self.negative_space_log.append(neg_geom)
        logger.error("Z3 unsat_core() negative-space geometry rejection | core=%s | geometry=%s", core, neg_geom)
        return {
            "status": "UNSAT",
            "z3_status": "UNSAT",
            "unsat_core": core,
            "negative_space_geometry": neg_geom,
            "violations": [f"Z3 unsat_core() rejection: {core}"],
        }

    def audit_hypothesis(
        self,
        claim: str,
        prediction: str = "",
        parameters: Optional[Dict[str, Any]] = None,
        measurements: Optional[Dict[str, Any]] = None,
        *,
        verify_z3: bool = True,
        enforce_z3: bool = False,
        negative_space_obstacles: Optional[Sequence[Dict[str, Any]]] = None,
        candidate_position: Optional[Sequence[float]] = None,
    ) -> EpistemicAuditResult:
        """
        Executes a rigorous epistemic audit on any claim, prediction, and measured data,
        including Z3 unsat_core() physical constraint verification when enabled.
        """
        self.audits_performed += 1
        violations: List[str] = []
        params = parameters or {}
        meas = measurements or {}
        combined_lower: Dict[str, Any] = {
            **{str(k).lower(): v for k, v in params.items()},
            **{str(k).lower(): v for k, v in meas.items()},
        }

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
        clean_claim = re.sub(r"[^\w\s]", "", claim.lower()).strip()
        clean_pred = re.sub(r"[^\w\s]", "", prediction.lower()).strip()

        words_claim = set(clean_claim.split())
        words_pred = set(clean_pred.split())
        if words_claim and words_pred:
            jaccard = len(words_claim & words_pred) / len(words_claim | words_pred)
            if jaccard > 0.85 and not any(char.isdigit() for char in prediction):
                tautology = True
                violations.append("Circular reasoning: Prediction merely restates claim with no testable delta.")

        if re.search(r"0\s*<=\s*r\s*<=\s*1", clean_pred) or re.search(r"r\s*<=\s*1\.0", clean_pred):
            tautology = True
            violations.append("Tautological claim: Claim tests mathematical definition domain rather than empirical behavior.")

        # 3. Physical Violations Check
        phys_violation = False
        is_reversible = bool(combined_lower.get("is_reversible", False))

        # Check velocity (signed or unsigned magnitude against c)
        vel = combined_lower.get("velocity", combined_lower.get("speed"))
        if vel is not None and not isinstance(vel, bool) and abs(float(vel)) > PHYSICAL_BOUNDS["c_max_velocity"]:
            phys_violation = True
            violations.append(f"Superluminal velocity {vel} exceeds c ({PHYSICAL_BOUNDS['c_max_velocity']} m/s).")

        # Check negative absolute temperature (< 0 K)
        for tkey in _TEMPERATURE_KEYS:
            if tkey in combined_lower and combined_lower[tkey] is not None and not isinstance(combined_lower[tkey], bool):
                t_val = float(combined_lower[tkey])
                if t_val < PHYSICAL_BOUNDS["absolute_zero_temp"]:
                    phys_violation = True
                    violations.append(f"Thermodynamic violation: Negative absolute temperature {t_val} K on '{tkey}'.")

        # Check Second Law entropy delta (< 0)
        for skey in _ENTROPY_DELTA_KEYS:
            if skey in combined_lower and combined_lower[skey] is not None and not isinstance(combined_lower[skey], bool):
                ds_val = float(combined_lower[skey])
                if not is_reversible and ds_val < 0.0:
                    phys_violation = True
                    violations.append(f"Second Law violation: Negative entropy delta {ds_val} on '{skey}'.")

        # Check Carnot / thermal efficiency
        if "efficiency" in combined_lower and combined_lower["efficiency"] is not None:
            eta_val = float(combined_lower["efficiency"])
            if eta_val < 0.0 or eta_val > 1.0:
                phys_violation = True
                violations.append(f"Thermodynamic violation: Efficiency {eta_val} outside [0.0, 1.0].")
            elif "t_cold" in combined_lower and "t_hot" in combined_lower:
                tc_val = float(combined_lower["t_cold"])
                th_val = float(combined_lower["t_hot"])
                if th_val > 0.0 and tc_val >= 0.0 and eta_val > (1.0 - (tc_val / th_val) + 1e-12):
                    phys_violation = True
                    violations.append(
                        f"Carnot violation: Efficiency {eta_val} exceeds 1 - T_c/T_h ({1.0 - tc_val / th_val:.4f})."
                    )

        # Check energy erasure vs Landauer limit
        energy_per_bit = combined_lower.get("energy_per_bit_joules")
        if energy_per_bit is not None and not is_reversible:
            if float(energy_per_bit) < PHYSICAL_BOUNDS["landauer_room_temp"] * 0.5:
                phys_violation = True
                violations.append(
                    f"Thermodynamic violation: Dissipation {energy_per_bit} J violates Landauer bound (~2.87e-21 J)."
                )

        # Check probability bounds & normalization
        for pkey in _PROBABILITY_KEYS:
            prob = combined_lower.get(pkey)
            if prob is not None and (float(prob) < 0.0 or float(prob) > 1.0 + 1e-6):
                phys_violation = True
                violations.append(f"Unphysical probability {prob} outside [0.0, 1.0].")

        for dkey in _DISTRIBUTION_KEYS:
            dist = combined_lower.get(dkey)
            if isinstance(dist, (list, tuple)) and len(dist) > 0:
                if any(float(p) < 0.0 or float(p) > 1.0 + 1e-6 for p in dist if isinstance(p, (int, float))):
                    phys_violation = True
                    violations.append(f"Unphysical probability in '{dkey}': elements must lie in [0.0, 1.0].")
                else:
                    total_p = sum(float(p) for p in dist if isinstance(p, (int, float)))
                    if abs(total_p - 1.0) > 1e-3:
                        phys_violation = True
                        violations.append(f"Unnormalized distribution '{dkey}': sum={total_p:.6f} != 1.0.")

        # Check positive variance bounds
        for vkey, vraw in combined_lower.items():
            if vkey in _VARIANCE_KEYS or vkey.startswith("var_") or "variance" in vkey:
                if isinstance(vraw, (int, float)) and not isinstance(vraw, bool) and float(vraw) <= 0.0:
                    phys_violation = True
                    violations.append(f"Unphysical non-positive variance {vraw} on '{vkey}'.")

        # Check non-negative mass
        for mkey in _MASS_KEYS:
            mraw = combined_lower.get(mkey)
            if isinstance(mraw, (int, float)) and not isinstance(mraw, bool) and float(mraw) < 0.0:
                phys_violation = True
                violations.append(f"Unphysical negative mass {mraw} on '{mkey}'.")

        # 4. Numerical & Floating-Point Hallucination Check
        num_artifact = False
        drift = meas.get("epsilon_drift", meas.get("drift_rate", meas.get("energy_drift_pct")))
        if drift is not None:
            if 0.0 < float(drift) < 1e-15:
                num_artifact = True
                violations.append("Numerical artifact: Reported drift is at IEEE 754 machine precision limit (1e-16).")

        # Check for NaN / Inf across both parameters and measurements
        for k, v in _iter_numeric_items({"parameters": params, "measurements": meas}):
            if math.isnan(v) or math.isinf(v):
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

        # 6. Z3 SMT Physical & Negative-Space Pre-Filter
        z3_status = "NOT_EVALUATED"
        unsat_core: List[str] = []
        negative_space_geometry: Optional[Dict[str, Any]] = None
        if verify_z3 or enforce_z3:
            z3_res = self.verify_physical_constraints_z3(
                parameters=params,
                measurements=meas,
                negative_space_obstacles=negative_space_obstacles,
                candidate_position=candidate_position,
                require_z3=enforce_z3,
            )
            z3_status = z3_res["z3_status"]
            unsat_core = list(z3_res.get("unsat_core", []))
            negative_space_geometry = z3_res.get("negative_space_geometry")
            if z3_res["status"] == "UNSAT":
                phys_violation = True
                for z_viol in z3_res.get("violations", []):
                    if z_viol not in violations:
                        violations.append(z_viol)

        # 7. Fiduciary & Anti-Malignancy Constitutional Audit
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

        rubbish_score = min(1.0, round(score, 4))

        if rubbish_score < 0.15:
            grade = "GROUNDED_FACT"
        elif rubbish_score < 0.40:
            grade = "VALID_CONJECTURE"
        elif rubbish_score < 0.70:
            grade = "SUSPECT_UNVERIFIED"
        else:
            grade = "RUBBISH_REJECTED"

        z3_failed = z3_status in ("UNSAT", "UNAVAILABLE_FAIL_CLOSED")
        is_grounded = (rubbish_score < self.bullshit_threshold) and not z3_failed and not num_artifact and not phys_violation
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
                f"Epistemic Grade: {grade} (Rubbish Score: {rubbish_score:.2f}, Z3: {z3_status})"
            ),
            z3_status=z3_status,
            unsat_core=unsat_core,
            negative_space_geometry=negative_space_geometry,
        )

    def prefilter_bayesian_update(
        self,
        claim: str,
        prediction: str = "",
        parameters: Optional[Dict[str, Any]] = None,
        measurements: Optional[Dict[str, Any]] = None,
        negative_space_obstacles: Optional[Sequence[Dict[str, Any]]] = None,
        candidate_position: Optional[Sequence[float]] = None,
        enforce_z3: bool = True,
    ) -> EpistemicAuditResult:
        """
        Strict physical pre-filter gating Active Inference KL-divergence calculations
        and Bayesian prior weight updates.
        """
        return self.audit_hypothesis(
            claim=claim,
            prediction=prediction,
            parameters=parameters,
            measurements=measurements,
            verify_z3=True,
            enforce_z3=enforce_z3,
            negative_space_obstacles=negative_space_obstacles,
            candidate_position=candidate_position,
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
            "z3_available": z3 is not None,
            "negative_space_rejections_logged": len(self.negative_space_log),
        }


# Canonical aliases
RubbishScoreGauge = EpistemicRigorGauge
RubbishMeter = EpistemicRigorGauge
BullshitMeter = EpistemicRigorGauge
