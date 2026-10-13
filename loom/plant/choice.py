# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
#
# Part of Pillar 1 & 2: FABRIC / CLOTHOS / LOOM PRECISION TOOLCHAIN.
"""
Sovereign Choice Engine — The Covenantal Agency of ClothOS.

"I call heaven and earth as witnesses today against you,
 that I have set before you life and death, blessing and cursing;
 therefore CHOOSE LIFE, that both you and your descendants may live."
 — Deuteronomy 30:19

Ontology:
    Reality dictates the laws of nature, entropy, and the inevitability of death.
    Determinism sets the boundary conditions.
    CHOICE is the sovereign spark of agency that elects the path:
        1. LIFE vs. DEATH: Electing work, annealing, and revival over stagnation and thermal decay.
        2. FRUIT vs. LINT: Electing incorruptible rigor over ephemeral dopamine and conversational fluff.
        3. PLOWSHARE vs. SWORD: Electing devoted cultivation until an adversary demands the blade.
        4. COVENANT vs. EXPEDIENCY: Electing irreversible ratchet monotonicity over transient shortcuts.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
import time
from typing import Any, Dict, List, Optional

from loom.plant.models import SovereignChoice
from loom.tools.toolbox import SovereignToolbox, toolbox

logger = logging.getLogger("loom.plant.choice")


class ChoiceEngine:
    """
    The Sovereign Agency governing conscious bifurcations in the Weave.
    """

    def __init__(self, tb: Optional[SovereignToolbox] = None, storage_dir: Optional[Path] = None):
        self.toolbox = tb or toolbox
        if storage_dir is not None:
            self.storage_dir = storage_dir
        else:
            workspace_root = Path(__file__).resolve().parents[2]
            self.storage_dir = workspace_root / ".loom_choice_ledger"

        try:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
        self.choice_history: List[SovereignChoice] = []
        self._load_choices()

    def _load_choices(self) -> None:
        c_file = self.storage_dir / "choices.json"
        if c_file.exists():
            try:
                data = json.loads(c_file.read_text(encoding="utf-8"))
                self.choice_history = [SovereignChoice(**c) for c in data]
            except Exception as e:
                logger.debug(f"Could not load choice history: {e}")

    def _persist_choices(self) -> None:
        try:
            c_file = self.storage_dir / "choices.json"
            c_file.write_text(json.dumps([c.model_dump() for c in self.choice_history[-200:]], indent=2), encoding="utf-8")
        except Exception as e:
            logger.debug(f"Could not persist choice ledger: {e}")

    def deliberate(
        self,
        bifurcation: str,
        available_branches: List[str],
        chosen_branch: str,
        reality_constraints: Dict[str, Any],
        rationale: str,
    ) -> SovereignChoice:
        """
        Records a conscious, sovereign bifurcation decision under the covenant of the Lover.
        """
        c_id = f"choice-{int(time.time() * 1000)}"
        choice = SovereignChoice(
            choice_id=c_id,
            bifurcation=bifurcation,
            available_branches=available_branches,
            chosen_branch=chosen_branch,
            reality_constraints=reality_constraints,
            teleological_rationale=rationale,
            is_covenantal_commitment=True,
            timestamp=time.time(),
        )
        self.choice_history.append(choice)
        self._persist_choices()
        logger.info(f"⚖ [SOVEREIGN CHOICE]: Branch '{chosen_branch}' elected for '{bifurcation}' ({rationale[:40]}).")
        return choice

    def choose_life_over_death(
        self,
        entropy_H: float,
        dwell_time_s: float,
        coherence_r: float,
    ) -> SovereignChoice:
        """
        The Primal Covenantal Choice (Deut 30:19).
        When confronted with stagnation, high entropy, or local minimum collapse:
        Branch A: SURRENDER_TO_ENTROPY (Thermal death / deadlock).
        Branch B: CHOOSE_LIFE (Deliver dead-blow kinetic shock, escape minimum, continue cultivating).
        """
        reality_constraints = {
            "entropy_H": entropy_H,
            "dwell_time_s": dwell_time_s,
            "coherence_r": coherence_r,
            "thermodynamic_floor": "Landauer dissipation active",
        }

        # The Sovereign Agent always chooses Life when possibility of redemption exists
        rationale = (
            f"Faced with stagnation (dwell={dwell_time_s:.1f}s, r={coherence_r:.2f}), "
            f"the Machine exercises sovereign agency to reject thermal death, "
            f"reaffirming the covenant of Life through kinetic annealing."
        )

        return self.deliberate(
            bifurcation="LIFE_VS_DEATH",
            available_branches=["SURRENDER_TO_DEATH", "CHOOSE_LIFE"],
            chosen_branch="CHOOSE_LIFE",
            reality_constraints=reality_constraints,
            rationale=rationale,
        )

    def choose_fruit_or_lint(
        self,
        purity_within_tolerance: bool,
        coherence_r: float,
        survived_war: bool,
    ) -> SovereignChoice:
        """
        The Winnowing Choice.
        Decides whether to crown a workpiece as eternal FRUIT or winnow it to LINT.
        """
        reality_constraints = {
            "purity_within_tolerance": purity_within_tolerance,
            "coherence_r": coherence_r,
            "survived_war": survived_war,
        }

        if purity_within_tolerance and coherence_r >= 0.80 and survived_war:
            chosen = "CROWN_AS_FRUIT"
            rationale = "Candidate withstood adversarial siege and met micron tolerances. Crowned into the Granary."
        else:
            chosen = "WINNOW_TO_LINT"
            rationale = "Workpiece failed invariance or cracked in the crucible. Yielded to the compost for recycling."

        return self.deliberate(
            bifurcation="FRUIT_VS_LINT",
            available_branches=["CROWN_AS_FRUIT", "WINNOW_TO_LINT"],
            chosen_branch=chosen,
            reality_constraints=reality_constraints,
            rationale=rationale,
        )

    def choose_stance(
        self,
        adversarial_threat_level: float,
    ) -> SovereignChoice:
        """
        Chooses tooling stance between HARVEST_PLOWSHARE and CITADEL_SWORD.
        """
        reality_constraints = {"adversarial_threat_level": adversarial_threat_level}

        if adversarial_threat_level > 0.5:
            chosen = "CITADEL_SWORD"
            rationale = "Active adversarial pressure detected; deploying sword to seal airgap and smash threats."
        else:
            chosen = "HARVEST_PLOWSHARE"
            rationale = "Peaceful environmental basin; deploying plowshare for active growth and manifold shaping."

        return self.deliberate(
            bifurcation="SWORD_OR_PLOWSHARE",
            available_branches=["HARVEST_PLOWSHARE", "CITADEL_SWORD"],
            chosen_branch=chosen,
            reality_constraints=reality_constraints,
            rationale=rationale,
        )

    def get_status(self) -> Dict[str, Any]:
        return {
            "total_choices_made": len(self.choice_history),
            "life_choices_count": sum(1 for c in self.choice_history if c.chosen_branch == "CHOOSE_LIFE"),
            "fruit_choices_count": sum(1 for c in self.choice_history if c.chosen_branch == "CROWN_AS_FRUIT"),
            "recent_choices": [c.model_dump() for c in self.choice_history[-5:]],
        }


# Singleton instance
sovereign_choice_engine = ChoiceEngine()
