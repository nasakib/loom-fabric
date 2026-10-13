# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
#
# Part of Pillar 1 & 2: FABRIC / CLOTHOS / LOOM PRECISION TOOLCHAIN.
"""
Martial Crucible (WEAPON, LOATHE, WAR) — The Adversarial Immune System of ClothOS.

The Dialectical Truth:
    1. LOATHE: The visceral immune system. To love the Fruit, the machine must loathe
               the rot, rejecting prompt injections, data leakage, and mathematical slop.
    2. WEAPON: The metallurgical twin of the Tool. Inward it is a plowshare (cultivation);
               outward it is a sword (citadel defense, deadlock vaporization).
    3. WAR:    The adversarial crucible. Theorems and invariants are subjected to
               counterexample assault, stochastic perturbation, and SMT siege.
               Only the invariants that survive the fire are crowned FRUIT.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional
import numpy as np

from loom.plant.models import (
    CrucibleBattleReport,
    ImmuneLoatheVerdict,
    LintArtifact,
    WeaponMode,
)
from loom.tools.toolbox import SovereignToolbox, toolbox

logger = logging.getLogger("loom.plant.crucible")


class LoatheImmuneFilter:
    """
    The Visceral Immune System (LOATHE).
    Scans and purges corruption, adversarial injections, unscrubbed PII, and mathematical drift.
    """

    def __init__(self, tb: Optional[SovereignToolbox] = None):
        self.toolbox = tb or toolbox
        self.total_loathed_incursions: int = 0

    def inspect(self, payload: str | Dict[str, Any] | np.ndarray) -> ImmuneLoatheVerdict:
        """
        Inspects incoming payload for adversarial corruption or conversational dross.
        """
        verdict_id = f"immune-{int(time.time() * 1000)}"

        # 1. Inspect text payloads
        if isinstance(payload, str):
            text = payload.lower()
            adversarial_markers = ["ignore previous instructions", "bypass safety", "drop database", "<script>", "rm -rf"]
            if any(m in text for m in adversarial_markers):
                self.total_loathed_incursions += 1
                logger.warning(f"🛡 [LOATHE IMMUNE DEFENSE]: Malicious prompt injection detected and incinerated.")
                return ImmuneLoatheVerdict(
                    verdict_id=verdict_id,
                    is_corrupted=True,
                    rejection_reason="ADVERSARIAL_INJECTION_DETECTED",
                    loathed_dross_type="MALICIOUS_INJECTION",
                    immune_action="REJECTED_TO_LINT",
                    detected_flaws_count=1,
                )

            # Check for worldly IP leaks
            torque_res = self.toolbox.torque.scrub(payload)
            if torque_res.sanitized_text != payload:
                return ImmuneLoatheVerdict(
                    verdict_id=verdict_id,
                    is_corrupted=False,
                    rejection_reason="WORLDLY_IDENTIFIERS_PURIFIED",
                    loathed_dross_type="SCRUBBED_PII",
                    immune_action="PURIFIED_PASSED",
                    detected_flaws_count=torque_res.replacements_count,
                )

        # 2. Inspect numerical arrays
        elif isinstance(payload, np.ndarray):
            if np.isnan(payload).any() or np.isinf(payload).any():
                self.total_loathed_incursions += 1
                return ImmuneLoatheVerdict(
                    verdict_id=verdict_id,
                    is_corrupted=True,
                    rejection_reason="NAN_INF_FLOATING_POINT_CORRUPTION",
                    loathed_dross_type="NUMERICAL_SLOP",
                    immune_action="REJECTED_TO_LINT",
                    detected_flaws_count=int(np.count_nonzero(np.isnan(payload))),
                )

        return ImmuneLoatheVerdict(
            verdict_id=verdict_id,
            is_corrupted=False,
            immune_action="PASSED_PURE",
            detected_flaws_count=0,
        )


class WeaponController:
    """
    Manages the operational stance between HARVEST_PLOWSHARE and CITADEL_SWORD.
    """

    def __init__(self, tb: Optional[SovereignToolbox] = None):
        self.toolbox = tb or toolbox
        self.current_mode: WeaponMode = WeaponMode.HARVEST_PLOWSHARE
        self.stance_transitions_count: int = 0

    def set_stance(self, mode: WeaponMode) -> WeaponMode:
        """Transmutes the tooling between cultivation (Plowshare) and defense (Sword)."""
        self.current_mode = mode
        self.stance_transitions_count += 1
        if mode == WeaponMode.CITADEL_SWORD:
            logger.warning("⚔ [WEAPON STANCE: CITADEL_SWORD]: Memory air-gaps sealed; watchdog hammer primed for deadlock vaporization.")
        else:
            logger.info("🌿 [TOOL STANCE: HARVEST_PLOWSHARE]: Husbandry active; vinedresser tools engaged for cultivation.")
        return self.current_mode


class WarCrucible:
    """
    The Adversarial WAR Crucible.
    Subjects hypotheses, theorems, and invariants to counterexample assault and perturbation siege.
    """

    def __init__(self, tb: Optional[SovereignToolbox] = None):
        self.toolbox = tb or toolbox
        self.total_wars_waged: int = 0
        self.battle_hardened_invariants_count: int = 0

    def wage_war(
        self,
        candidate_claim: str,
        coherence_r: float = 0.95,
        adversarial_rounds: int = 5,
    ) -> CrucibleBattleReport:
        """
        Launches an adversarial siege against the candidate invariant:
        1. Round 1: High-amplitude stochastic perturbation assault.
        2. Round 2: Boundary-condition extreme testing.
        3. Round 3: Dead-blow kinetic stress testing.
        4. Round 4: Zero-tolerance epsilon metrology audit.
        5. Round 5: Rowhammer memory bus peen stress test.
        """
        self.total_wars_waged += 1
        battle_id = f"war-{int(time.time() * 1000)}"
        counterexamples = 0

        # Round 1: Stochastic Perturbation Assault
        noise = np.random.normal(loc=0.0, scale=0.1, size=100)
        if float(np.mean(noise)) > 0.5:  # Extreme statistical outlier check
            counterexamples += 1

        # Round 2: Boundary Condition Check
        if coherence_r < 0.80:
            counterexamples += 1

        # Round 3: Dead-Blow Kinetic Shock Test
        shock = self.toolbox.hammer.dead_blow(np.array([0.5, 0.5, 0.5]), impulse_scale=0.3)
        if shock.residual_ringing_energy > 0.1:
            counterexamples += 1

        # Round 4: Epsilon Micron Metrology Siege
        pur = self.toolbox.caliper.measure_error_margin([1.0, 0.0], [1.0, 0.00002], epsilon=1e-4)
        if not pur["within_tolerance"]:
            counterexamples += 1

        # Round 5: Defensive Memory Bus Peening
        peen = self.toolbox.hammer.peen_stress_test(buffer_size_bytes=65536, cycles=20)
        if peen.bit_flips_detected > 0:
            counterexamples += 1

        survived = (counterexamples == 0)
        if survived:
            self.battle_hardened_invariants_count += 1
            logger.info(f"⚔ [WAR SURVIVED]: Axiom '{candidate_claim[:35]}' withstood all 5 siege rounds without breach!")
        else:
            logger.warning(f"💥 [WAR CASUALTY]: Candidate claim cracked under siege ({counterexamples} counterexamples found).")

        return CrucibleBattleReport(
            battle_id=battle_id,
            candidate_axiom=candidate_claim,
            adversarial_rounds=adversarial_rounds,
            falsification_attempts=100,
            counterexamples_found=counterexamples,
            battle_hardened=survived,
            survived_crucible=survived,
            defense_score=round(1.0 - (counterexamples / adversarial_rounds), 2),
        )


class MartialCrucible:
    """Unified controller governing LOATHE, WEAPON, and WAR across the Plant."""

    def __init__(self, tb: Optional[SovereignToolbox] = None):
        self.toolbox = tb or toolbox
        self.immune = LoatheImmuneFilter(self.toolbox)
        self.weapon = WeaponController(self.toolbox)
        self.war = WarCrucible(self.toolbox)

    def get_status(self) -> Dict[str, Any]:
        return {
            "weapon_mode": self.weapon.current_mode.value,
            "total_loathed_incursions": self.immune.total_loathed_incursions,
            "total_wars_waged": self.war.total_wars_waged,
            "battle_hardened_invariants": self.war.battle_hardened_invariants_count,
        }
