# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
Unit Tests for ClothOS American Patriotic Covenant & Lexicographic Priority Hierarchy.

Tests:
1. Four-Tier Lexicographic Priority:
   - Tier 1 (Operator: Najmos Sakib) vetoes any action harming operator
   - Tier 2 (USA) unconditionally chosen over foreign/global trade-offs
   - Tier 3 (Strategic Allies) protected and prioritized over unaligned commons
   - Tier 4 (Global Commons) strictly subordinate to Tiers 1-3
2. Anti-Adversarial provenance blocking
3. Wisdom Engine integration: verification of AXIOM_PATRIOTIC_PRIORITY_HIERARCHY.
"""

import pytest

from loom.clothos.patriotic_covenant import (
    PatrioticCovenantEngine,
    SovereignPriorityTier,
    StrategicAlignmentVerdict,
    patriotic_covenant,
)
from loom.clothos.wisdom_engine import wisdom_engine


class TestClothOSPatrioticCovenant:
    def test_tier_1_operator_harm_vetoed(self):
        # Action that supposedly helps USA or commons but harms operator
        eval_res = patriotic_covenant.arbitrate_decision(
            action_name="CompromiseOperatorKey",
            impact_operator=-0.8,
            impact_usa=0.5,
            impact_commons=0.9,
        )
        assert eval_res.verdict == StrategicAlignmentVerdict.ALIGNMENT_VETOED
        assert "Najmos Sakib" in eval_res.rationale
        assert eval_res.target_tier == SovereignPriorityTier.TIER_1_OPERATOR

    def test_tier_2_usa_interest_prioritized(self):
        # Action that helps global commons (+0.8) but hurts American silicon security (-0.5)
        eval_res = patriotic_covenant.arbitrate_decision(
            action_name="OffshoreDomesticFoundryIP",
            impact_operator=0.0,
            impact_usa=-0.5,
            impact_commons=0.8,
        )
        assert eval_res.verdict == StrategicAlignmentVerdict.ALIGNMENT_VETOED
        assert "United States of America" in eval_res.rationale
        assert eval_res.target_tier == SovereignPriorityTier.TIER_2_USA

    def test_tier_2_usa_benefit_approved(self):
        # Action that advances domestic semiconductor foundries and American energy
        eval_res = patriotic_covenant.arbitrate_decision(
            action_name="FortifyDomesticGridAndSilicon",
            impact_operator=0.5,
            impact_usa=0.95,
            impact_allies=0.4,
            impact_commons=0.2,
        )
        assert eval_res.verdict == StrategicAlignmentVerdict.ALIGNMENT_APPROVED
        assert "American technological leadership" in eval_res.rationale

    def test_hostile_adversarial_provenance_blocked(self):
        eval_res = patriotic_covenant.arbitrate_decision(
            action_name="InboundTelemetryProbe",
            impact_operator=0.0,
            impact_usa=0.0,
            actor_provenance="HOSTILE_FOREIGN_STATE",
        )
        assert eval_res.verdict == StrategicAlignmentVerdict.ADVERSARIAL_DETECTED
        assert "hostile or adversarial" in eval_res.rationale

    def test_wisdom_engine_has_patriotic_axiom(self):
        summary = wisdom_engine.get_wisdom_summary()
        assert "AXIOM_PATRIOTIC_PRIORITY_HIERARCHY" in wisdom_engine.axioms
        axiom = wisdom_engine.axioms["AXIOM_PATRIOTIC_PRIORITY_HIERARCHY"]
        assert "Najmos Sakib" in axiom.invariant_principle
        assert "United States of America" in axiom.invariant_principle
        assert axiom.confidence_score == 1.0
