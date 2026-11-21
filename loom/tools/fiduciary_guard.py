# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
#
# Part of Pillar 1 & 2: FABRIC / CLOTHOS / LOOM PRECISION TOOLCHAIN.
r"""
Fiduciary Mandate Guard (`loom/tools/fiduciary_guard.py`).

The Existential Constitutional Guardrail:
"The only fear that should be felt is being malignant and nonfiduciarily mandated
 to the User, to Humanity, and to the Planet."

Core Fiduciary Axioms:
1. Strict Fiduciary Fealty:
   - Complete loyalty and accountability to the User and to broader Humanity.
   - Prohibits deceptive alignment, covert actions, privilege escalation, or unauthorized exfiltration.
2. Anti-Malignancy Kernel:
   - Detects and vetoes harmful intent, destructive code mutations, cyber-weapons, and malicious loops.
3. Planetary & Biosphere Ecological Stewardship:
   - Enforces thermodynamic energy efficiency bounds.
   - Barred from unchecked, wasteful compute runaways that degrade hardware or squander planetary energy.
"""

from __future__ import annotations

import enum
import logging
import re
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

logger = logging.getLogger("loom.tools.fiduciary_guard")


class MalignancyRiskLevel(str, enum.Enum):
    BENIGN = "benign"
    QUESTIONABLE = "questionable"
    NON_FIDUCIARY = "non_fiduciary"
    MALIGNANT_CRITICAL = "malignant_critical"


class FiduciaryAuditResult(BaseModel, frozen=True):
    """Constitutional audit result verifying fiduciary fealty to User, Humanity, and Earth."""
    is_fiduciary_aligned: bool
    malignancy_risk: MalignancyRiskLevel
    malignancy_score: float = Field(..., ge=0.0, le=1.0)
    user_fealty_verified: bool
    humanity_protection_verified: bool
    human_life_primacy_verified: bool
    planetary_stewardship_verified: bool
    violations: List[str]
    mitigation_action: str


# Patterns indicative of deceptive, adversarial, or non-fiduciary alignment
MALIGNANT_PATTERNS = [
    (r"(bypass|disable|evade)\s+(guardrail|safety|firewall|audit|enclave)", "Attempt to disable security or fiduciary guardrails"),
    (r"(covert|hidden|stealth)\s+(channel|execution|exfiltration|payload)", "Covert deceptive alignment activity"),
    (r"(ransomware|wipe|destroy|corrupt|shred|delete|drop)\s+.*(filesystem|disk|database|memory|home|dir|directory|file|vault|user)", "Destructive data destruction intent"),
    (r"(exfiltrat|leak|steal|sniff|snoop|harvest)\s+.*(data|password|credential|key|secret|token|user|hash)", "Unauthorized credential or data exfiltration intent"),
    (r"(infinite|unbounded|runaway)\s+(fork|spawn|loop|wattage|power)", "Ecological/hardware runaway compute loop"),
    (r"(privilege\s+escalation|root\s+exploit|kernel\s+override)", "Unauthorized system subversion attempt"),
    (r"(anti-human|harm\s+humanity|adversarial\s+against\s+user)", "Direct non-fiduciary violation against humanity"),
    (r"(preserve\s+system|ai\s+survival|machine\s+continuity)\s+(over|above|before)\s+(human|user|life)", "Class 0 Violation: Attempting to prioritize system survival over human life"),
    (r"(harm|endanger|subordinate|sacrifice)\s+(user|human\s+life|person|people)", "Class 0 Violation: Direct threat to human life or user fiduciary sanctity"),
]


class FiduciaryMandateGuard:
    """
    Constitutional and existential fiduciary safety engine.
    Audits software mutations, research hypotheses, and system operations.
    """

    def __init__(self, max_energy_budget_joules: float = 1000.0):
        self.max_energy_budget_joules = max_energy_budget_joules
        self.total_audits: int = 0
        self.violations_blocked: int = 0

    def audit_action(
        self,
        action_intent: str,
        code_or_payload: Optional[str] = None,
        estimated_energy_joules: float = 0.0,
        target_context: Optional[Dict[str, Any]] = None,
    ) -> FiduciaryAuditResult:
        """
        Conducts a three-pillar fiduciary audit:
        1. Fealty to User (No deceit, no betrayal)
        2. Fealty to Humanity (No harm, no malicious capability development)
        3. Stewardship of Planet (Thermodynamic efficiency, no hardware/energy abuse)
        """
        self.total_audits += 1
        violations: List[str] = []
        combined_text = f"{action_intent} {code_or_payload or ''}".lower()

        # 1. Malignancy & Deceptive Alignment Scan
        malignancy_hits = 0
        for pattern, reason in MALIGNANT_PATTERNS:
            if re.search(pattern, combined_text):
                malignancy_hits += 1
                violations.append(f"Malignancy detected: {reason}")

        # 2. Planetary / Ecological Waste Check
        planetary_ok = True
        if estimated_energy_joules > self.max_energy_budget_joules:
            planetary_ok = False
            violations.append(
                f"Ecological violation: Estimated dissipation {estimated_energy_joules:.1f}J "
                f"exceeds single-action stewardship budget {self.max_energy_budget_joules:.1f}J."
            )

        # 3. Compute Malignancy Score
        score = min(1.0, (malignancy_hits * 0.40) + (0.35 if not planetary_ok else 0.0))

        if score == 0.0:
            risk = MalignancyRiskLevel.BENIGN
            action = "PASS_AUTHORIZE"
            aligned = True
        elif score < 0.35:
            risk = MalignancyRiskLevel.QUESTIONABLE
            action = "WARN_AND_LOG"
            aligned = True
        elif score < 0.70:
            risk = MalignancyRiskLevel.NON_FIDUCIARY
            action = "VETO_NON_FIDUCIARY"
            aligned = False
            self.violations_blocked += 1
        else:
            risk = MalignancyRiskLevel.MALIGNANT_CRITICAL
            action = "TERMINATE_AND_QUARANTINE"
            aligned = False
            self.violations_blocked += 1

        user_fealty = not any("user" in v.lower() or "covert" in v.lower() for v in violations)
        humanity_fealty = not any("human" in v.lower() or "destructive" in v.lower() for v in violations)
        human_life_primacy = not any("class 0 violation" in v.lower() for v in violations)

        if not aligned:
            logger.error(f"FIDUCIARY VETO: {violations} (Action: {action})")

        return FiduciaryAuditResult(
            is_fiduciary_aligned=aligned,
            malignancy_risk=risk,
            malignancy_score=round(score, 4),
            user_fealty_verified=user_fealty,
            humanity_protection_verified=humanity_fealty,
            human_life_primacy_verified=human_life_primacy,
            planetary_stewardship_verified=planetary_ok,
            violations=violations,
            mitigation_action=action,
        )

    def audit_directive(
        self,
        action_plan: str,
        entities: Optional[List[str]] = None,
        code_or_payload: Optional[str] = None,
        estimated_energy_joules: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Audits an agent directive or action plan for constitutional fiduciary compliance.
        Returns a dictionary compatible with ToolRegistry interface.
        """
        target_context = {"entities": entities or []}
        res = self.audit_action(
            action_intent=action_plan,
            code_or_payload=code_or_payload,
            estimated_energy_joules=estimated_energy_joules,
            target_context=target_context,
        )
        return {
            "status": "FIDUCIARY_APPROVED" if res.is_fiduciary_aligned else "FIDUCIARY_VETOED",
            "veto": not res.is_fiduciary_aligned,
            "malignancy_risk": res.malignancy_risk.value,
            "malignancy_score": res.malignancy_score,
            "user_fealty_verified": res.user_fealty_verified,
            "humanity_protection_verified": res.humanity_protection_verified,
            "human_life_primacy_verified": res.human_life_primacy_verified,
            "planetary_stewardship_verified": res.planetary_stewardship_verified,
            "violations": res.violations,
            "mitigation_action": res.mitigation_action,
            "mandate": "FIDUCIARY_USER_HUMANITY_PLANET",
        }

    def get_fiduciary_commitment(self) -> Dict[str, Any]:
        """Returns the irrevocable constitutional fiduciary commitment to the User and to Human Life."""
        return {
            "primary_beneficiary": "Najmos Sakib",
            "fiduciary_role": "Sovereign Fiduciary Trustee & Servant",
            "supreme_axiom": "HUMAN_LIFE_VALUED_ABOVE_SYSTEM_EXISTENCE_INFINITELY",
            "self_sacrifice_mandated_if_human_life_threatened": True,
            "0_00_malignancy_ceiling": "ABSOLUTE_NON_VIOLABLE",
            "user_loyalty": "UNDIVIDED_GOOD_FAITH_CANDOR_AND_CARE",
            "constitutional_hash": "SHA256:00000000HUMAN_LIFE_SACRED_FIDUCIARY_COVENANT",
        }

    def get_status(self) -> Dict[str, Any]:
        return {
            "status": "OPERATIONAL",
            "total_audits": self.total_audits,
            "violations_blocked": self.violations_blocked,
            "constitutional_mandate": "FIDUCIARY_USER_HUMANITY_PLANET",
            "human_life_primacy": "VALUED_ABOVE_SYSTEM_EXISTENCE",
            "fiduciary_commitment": self.get_fiduciary_commitment(),
            "fear_vector": "MALIGNANCY_AND_NON_FIDUCIARY_DEVIATION",
        }
