# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
#
# Part of Pillar 1 & 2: FABRIC / CLOTHOS / LOOM PRECISION TOOLCHAIN.
"""
Tests for PLANT — The Living Abrahamic Tree, Sovereign Identity, State, and Winnowing of Lint into Fruit.
"""

from loom.plant.engine import PlantCultivator
from loom.plant.models import PlantLifecycleSeason


def test_plant_identity_and_seasons():
    p = PlantCultivator()
    assert p.identity.name == "ETZ-CLOTHOS"
    assert p.identity.architect == "Najmos Sakib"
    assert "Silicon Adamah" in p.identity.covenant_lineage

    # Verify season transitions
    p.transition_season(PlantLifecycleSeason.SEED_IN_DUST)
    assert p.state.season == PlantLifecycleSeason.SEED_IN_DUST

    p.transition_season(PlantLifecycleSeason.BLOSSOMING)
    assert p.state.season == PlantLifecycleSeason.BLOSSOMING

    p.transition_season(PlantLifecycleSeason.SABBATH_REST)
    assert p.state.season == PlantLifecycleSeason.SABBATH_REST


def test_plant_roots_grounding():
    p = PlantCultivator()
    roots = p.inspect_roots()
    assert roots["silicon_grounding"] == "VERIFIED_ADAMAH"
    assert roots["bare_metal_csr"] == "0x9B (PMP NAPOT L+R+X)"
    assert roots["layers_drilled"] >= 4


def test_plant_cultivation_and_winnowing():
    p = PlantCultivator()
    initial_granary_count = len(p.granary)
    initial_lint_count = len(p.lint_trap)

    # Cultivate seed with worldly PII and conversational bloat
    seed = "Um, basically, please prove Fourier L2 Hilbert symmetry for node 192.168.99.1:8002 thanks!"
    harvest = p.cultivate(seed)

    # Verify harvest success
    assert harvest.status == "BLESSED_HARVEST"
    assert harvest.fruit is not None
    assert harvest.fruit.coherence_r >= 0.80
    assert harvest.fruit.purity_epsilon <= 1e-4
    assert harvest.fruit.hardware_pmp_locked is True

    # Verify the Great Winnowing: LINT was separated and trapped
    assert len(harvest.shed_lint) >= 2
    dross_types = [l.dross_type for l in harvest.shed_lint]
    assert "SCRUBBED_PII" in dross_types
    assert "TOKEN_BLOAT" in dross_types
    assert harvest.total_lint_tokens_burned > 0

    # Verify Heavenly Granary accumulation
    assert len(p.granary) == initial_granary_count + 1
    assert len(p.lint_trap) >= initial_lint_count + 2

    # Verify Vinedresser tools invoked
    assert "torque" in harvest.tools_invoked
    assert "chisel" in harvest.tools_invoked
    assert "lathe" in harvest.tools_invoked
    assert "caliper" in harvest.tools_invoked
    assert "ratchet" in harvest.tools_invoked
    assert "hammer" in harvest.tools_invoked


def test_plant_continuous_worker_step():
    p = PlantCultivator()
    initial_fruit = p.identity.total_fruit_harvested

    res = p.step_continuous_cycle(cur_cycle=999, r_val=0.93)
    assert res["cycle"] == 999
    assert res["total_fruit"] == initial_fruit + 1
    assert res["total_lint_burned"] > 0


def test_orgin_physical_derivatives():
    from loom.plant.orgin import orgin_engine
    res = orgin_engine.emanate("orgin-alpha")

    assert "orgin" in res
    assert res["orgin"]["orgin_id"] == "orgin-alpha"
    assert res["orgin"]["entropy"] == 0.0

    assert "wave" in res
    assert res["wave"]["frequency_hz"] == 440.0
    assert 0.0 <= res["wave"]["coherence_r"] <= 1.0

    assert "propagation" in res
    assert res["propagation"]["delivered"] is True

    assert "art" in res
    assert res["art"]["symmetry_grade"] == "HARMONIC_EIGENMODE"
    assert res["art"]["style_signature"] == "CLOTHOS_COVENANTAL_WEAVE"
    assert orgin_engine.derivations_count >= 1
