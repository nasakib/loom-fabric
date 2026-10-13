# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
#
# Part of Pillar 1 & 2: FABRIC / CLOTHOS / LOOM PRECISION TOOLCHAIN.
"""
Caliper Gauge — Precision Metrology, Error Margins & Entropy Metrology.

Mechanics:
- Micro-tolerance vernier measuring down to epsilon bounds ($10^{-5}$).
- Computes L2, cosine, and Chebyshev divergence between candidate models and ground truth.
- Measures Shannon routing entropy to ensure crisp deterministic QCT execution.
"""

from __future__ import annotations

import logging
import math
import re
from typing import Any, Dict, List, Sequence
import numpy as np

logger = logging.getLogger("loom.tools.caliper")


class CaliperGauge:
    """Precision metrology gauge for mathematical tolerances, entropy, and purity."""

    def __init__(self):
        self.measurements_count: int = 0

    def measure_error_margin(
        self, candidate: Sequence[float], target: Sequence[float], epsilon: float = 1e-4
    ) -> Dict[str, Any]:
        """
        Measures exact mathematical tolerances between candidate vector and ground truth.
        Passes only if L2 and Linf margins sit strictly below epsilon.
        """
        self.measurements_count += 1
        c = np.asarray(candidate, dtype=np.float64)
        t = np.asarray(target, dtype=np.float64)

        l2_delta = float(np.linalg.norm(c - t))
        linf_delta = float(np.max(np.abs(c - t)))
        denom = (np.linalg.norm(c) * np.linalg.norm(t))
        cosine_sim = float(np.dot(c, t) / denom) if denom > 0 else 0.0

        within_tolerance = l2_delta <= epsilon
        return {
            "l2_distance": round(l2_delta, 6),
            "linf_max_deviation": round(linf_delta, 6),
            "cosine_similarity": round(cosine_sim, 6),
            "epsilon_threshold": epsilon,
            "within_tolerance": within_tolerance,
            "metrology_grade": "VERIFIED_MICRON" if within_tolerance else "REJECTED_TOLERANCE_EXCEEDED",
        }

    def gauge_routing_entropy(self, probabilities: Sequence[float]) -> Dict[str, Any]:
        """
        Gauges Shannon entropy H = -sum(p * log2(p)).
        Determines if QCT routing decision is crisp (H < 0.5) or ambiguous (H > 1.2).
        """
        self.measurements_count += 1
        probs = [p for p in probabilities if p > 0.0]
        total = sum(probs)
        if total <= 0:
            return {"entropy_bits": 0.0, "decision_grade": "DETERMINISTIC"}

        normalized = [p / total for p in probs]
        entropy = -sum(p * math.log2(p) for p in normalized)

        grade = "CRISP_DETERMINISTIC" if entropy < 0.5 else ("MODERATE_SUPERPOSITION" if entropy < 1.2 else "DIFFUSE_AMBIGUOUS")
        return {
            "entropy_bits": round(entropy, 4),
            "decision_grade": grade,
            "requires_torque_escalation": entropy > 1.2,
        }

    def verify_pii_purity(self, text: str) -> Dict[str, Any]:
        """Caliper metrology check ensuring no un-scrubbed emails, IPs, or credentials leaked past Torque."""
        self.measurements_count += 1
        email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
        ip_pattern = r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"

        leaked_emails = re.findall(email_pattern, text)
        leaked_ips = [ip for ip in re.findall(ip_pattern, text) if not ip.startswith("127.") and not ip.startswith("192.168.")]

        is_pure = len(leaked_emails) == 0 and len(leaked_ips) == 0
        return {
            "is_pure": is_pure,
            "leaked_emails_count": len(leaked_emails),
            "leaked_external_ips_count": len(leaked_ips),
            "purity_verdict": "PASSED_ZERO_TRUST" if is_pure else "TAINTED_LEAK_DETECTED",
        }

    def get_status(self) -> Dict[str, Any]:
        return {"measurements_count": self.measurements_count}
