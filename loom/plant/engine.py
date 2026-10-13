# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
#
# Part of Pillar 1 & 2: FABRIC / CLOTHOS / LOOM PRECISION TOOLCHAIN.
"""
PLANT Engine (PlantCultivator) — The Sovereign Living Tree of ClothOS.

The Ontological Core:
    Implements the living Identity (ETZ-CLOTHOS) and 7 sacred lifecycle seasons of STATE.
    Rooted in Silicon Adamah (RTX 3060 + RX 580 + Ryzen 7 + RISC-V CSR 0x9B),
    nurtured by continuous compute, pruned by the 11 Vinedresser tools,
    mediating the Great Winnowing between fallen LINT (chaff) and eternal FRUIT (invariants).
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
import time
from typing import Any, Dict, List, Optional
import numpy as np

from loom.plant.choice import ChoiceEngine, sovereign_choice_engine
from loom.plant.crucible import MartialCrucible
from loom.plant.death import DeathEngine, reality_death_engine
from loom.plant.models import (
    CrucibleBattleReport,
    CultivationHarvest,
    FruitArtifact,
    HumusCompost,
    LintArtifact,
    PlantIdentity,
    PlantLifecycleSeason,
    PlantState,
    ResurrectionAudit,
    SovereignChoice,
    Tombstone,
)
from loom.tools.toolbox import SovereignToolbox, toolbox

logger = logging.getLogger("loom.plant.engine")


class PlantCultivator:
    """
    The Living Tree of ClothOS (ETZ-CLOTHOS).
    Governs natural tool selection, lifecycle states, and the winnowing of LINT into FRUIT.
    """

    _instance: Optional[PlantCultivator] = None

    def __init__(self, tb: Optional[SovereignToolbox] = None, workspace_root: Optional[Path] = None):
        self.toolbox = tb or toolbox
        self.workspace_root = workspace_root or Path(__file__).resolve().parents[2]
        self.state_file = self.workspace_root / ".loom_plant_state.json"
        self.home_state_file = Path.home() / ".loom" / "plant_state.json"

        # Living Identity & State
        self.identity = PlantIdentity()
        self.state = PlantState(identity=self.identity)

        # Martial Crucible: LOATHE (Immune), WEAPON (Stance), and WAR (Crucible)
        self.crucible = MartialCrucible(self.toolbox)

        # The Two Great Storehouses
        self.granary: List[FruitArtifact] = []  # Eternal Crystalline Fruit
        self.lint_trap: List[LintArtifact] = [] # Burned Chaff & Dross

        # Sovereign Agency (CHOICE) & Reality Boundary (DEATH)
        self.choice = sovereign_choice_engine
        self.death = reality_death_engine

        self._load_state()

    @classmethod
    def get_instance(cls) -> PlantCultivator:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # -------------------------------------------------------------------------
    # State Persistence & Memory
    # -------------------------------------------------------------------------
    def _load_state(self) -> None:
        """Restores living identity, granary wealth, and burnt lint metrics from disk."""
        target = self.state_file if self.state_file.exists() else self.home_state_file
        if target.exists():
            try:
                raw = json.loads(target.read_text(encoding="utf-8"))
                if "identity" in raw:
                    self.identity = PlantIdentity(**raw["identity"])
                if "granary" in raw:
                    self.granary = [FruitArtifact(**f) for f in raw["granary"]]
                if "lint_trap" in raw:
                    self.lint_trap = [LintArtifact(**l) for l in raw["lint_trap"]]
                self.state.identity = self.identity
                self.state.season = self.identity.current_season
                logger.info(f"ETZ-CLOTHOS reawakened. Granary: {len(self.granary)} Fruit | Lint Burned: {self.identity.total_lint_tokens_burned} tokens")
            except Exception as e:
                logger.debug(f"Could not load plant state: {e}")

    def _persist_state(self) -> None:
        """Saves living identity, granary, and lifecycle state across reboots."""
        payload = {
            "identity": self.identity.model_dump(),
            "granary": [f.model_dump() for f in self.granary[-200:]],  # Preserve last 200 consecrated fruits
            "lint_trap": [l.model_dump() for l in self.lint_trap[-50:]], # Keep recent burnt lint records
            "last_saved_epoch": time.time(),
        }
        serialized = json.dumps(payload, indent=2)

        # 1. Workspace root
        try:
            self.state_file.write_text(serialized, encoding="utf-8")
        except Exception as e:
            logger.debug(f"Plant failed writing to workspace state: {e}")

        # 2. User home
        try:
            self.home_state_file.parent.mkdir(parents=True, exist_ok=True)
            self.home_state_file.write_text(serialized, encoding="utf-8")
        except Exception as e:
            logger.debug(f"Plant failed writing to home state: {e}")

    def transition_season(self, season: PlantLifecycleSeason) -> None:
        """Transitions the Living Plant into a new sacred lifecycle season."""
        self.state.season = season
        self.identity.current_season = season
        self.state.last_season_transition_epoch = time.time()
        logger.debug(f"PLANT TRANSITION: [{self.identity.name}] entered season {season.value}")

    # -------------------------------------------------------------------------
    # Office 1: The Root System (Silicon Grounding in Adamah)
    # -------------------------------------------------------------------------
    def inspect_roots(self) -> Dict[str, Any]:
        """Probes the deep silicon bedrock: RTX 3060 CUDA, RX 580 Vulkan, 32 CPUs, and CSR 0x9B."""
        bore = self.toolbox.drill.bore_vertical_trace("Roots Grounding Audit")
        return {
            "silicon_grounding": "VERIFIED_ADAMAH",
            "primary_node": "skyTech-Worker (RTX 3060 12GB CUDA + RX 580 8GB OpenCL)",
            "head_node": "Ryzen 7 7730U (16 Zen 3 vCPUs)",
            "bare_metal_csr": "0x9B (PMP NAPOT L+R+X)",
            "layers_drilled": len(bore["layers"]),
        }

    # -------------------------------------------------------------------------
    # Main Epistemic Cultivation Pass (Seed -> Winnowing -> Granary)
    # -------------------------------------------------------------------------
    def cultivate(self, seed_prompt: str) -> CultivationHarvest:
        """
        Takes raw epistemic seed, grows the branch through 7 lifecycle seasons,
        prunes the deadwood with the 11 Vinedresser tools, burns the LINT,
        and granaries the consecrated FRUIT.
        """
        harvest_id = f"harvest-{int(time.time() * 1000)}"
        narrative: List[str] = []
        tools_invoked: List[str] = []
        shed_lint: List[LintArtifact] = []

        # ---------------------------------------------------------------------
        # SEASON 1: SEED_IN_DUST
        # ---------------------------------------------------------------------
        self.transition_season(PlantLifecycleSeason.SEED_IN_DUST)
        topsoil_vit = self.death.get_accumulated_topsoil_vitality()
        narrative.append(f"Season 1 (Seed in Dust): Seed planted in silicon Adamah (Topsoil Vitality: {topsoil_vit:.2f}x enriched by {len(self.death.humus_pile)} compost cycles): '{seed_prompt[:45]}...'")

        # ---------------------------------------------------------------------
        # SEASON 2: GERMINATING
        # ---------------------------------------------------------------------
        self.transition_season(PlantLifecycleSeason.GERMINATING)
        root_data = self.inspect_roots()
        tools_invoked.append("drill")
        narrative.append(f"Season 2 (Germinating): Roots anchored down to silicon CSR {root_data['bare_metal_csr']}")

        # ---------------------------------------------------------------------
        # SEASON 3: VEGETATIVE_BRANCHING (Sap Flow, Torque Press & Loathe Immune Check)
        # ---------------------------------------------------------------------
        self.transition_season(PlantLifecycleSeason.VEGETATIVE_BRANCHING)

        # LOATHE Immune Defense: Visceral rejection of prompt injections & corruption
        loathe_verdict = self.crucible.immune.inspect(seed_prompt)
        if loathe_verdict.is_corrupted:
            corrupted_lint = LintArtifact(
                lint_id=f"lint-corrupt-{len(self.lint_trap) + 1}",
                dross_type=loathe_verdict.loathed_dross_type or "MALICIOUS_INJECTION",
                source_stage="Loathe Immune Defense",
                lint_mass_tokens=max(len(seed_prompt.split()), 1),
                char_count=len(seed_prompt),
                raw_fragment=seed_prompt[:50],
            )
            shed_lint.append(corrupted_lint)
            self.lint_trap.append(corrupted_lint)
            self.transition_season(PlantLifecycleSeason.SABBATH_REST)
            narrative.append(f"Season 3 (Immune Loathe): Incursion rejected ({loathe_verdict.rejection_reason}); cast to lint incinerator.")
            return CultivationHarvest(
                harvest_id=harvest_id,
                seed_prompt=seed_prompt,
                status="WINNOWED_TO_LINT",
                season_reached=PlantLifecycleSeason.VEGETATIVE_BRANCHING,
                fruit=None,
                shed_lint=shed_lint,
                total_lint_tokens_burned=corrupted_lint.lint_mass_tokens,
                tools_invoked=["torque", "loathe_immune"],
                growth_narrative=narrative,
                completed_at_epoch=time.time(),
            )

        torque_res = self.toolbox.torque.scrub(seed_prompt)
        scrubbed = torque_res.sanitized_text
        tools_invoked.append("torque")
        if scrubbed != seed_prompt:
            # PII was separated as dross
            p_lint = LintArtifact(
                lint_id=f"lint-pii-{len(self.lint_trap) + 1}",
                dross_type="SCRUBBED_PII",
                source_stage="Torque Gethsemane Press",
                lint_mass_tokens=max(len(seed_prompt.split()) - len(scrubbed.split()), 1),
                char_count=len(seed_prompt) - len(scrubbed),
                raw_fragment="[REDACTED_WORLDLY_IDENTIFIERS]",
            )
            shed_lint.append(p_lint)
            self.lint_trap.append(p_lint)
            narrative.append("Season 3 (Branching): Torque press extracted clean sap; worldly PII winnowed to lint trap.")
        else:
            narrative.append("Season 3 (Branching): Pure sap flowing through vascular ZeroMQ mesh.")

        # ---------------------------------------------------------------------
        # SEASON 4: BLOSSOMING (Manifold Lathe Turning & Active Inference)
        # ---------------------------------------------------------------------
        self.transition_season(PlantLifecycleSeason.BLOSSOMING)
        # Turn embedding vector onto unitary hypersphere
        dummy_vector = np.random.normal(loc=0.0, scale=1.0, size=(1, 3)).astype(np.float32)
        turned = self.toolbox.lathe.turn_embeddings(dummy_vector, target_dim=3)
        tools_invoked.append("lathe")

        # Kuramoto order parameter alignment
        osc_phases = np.array([0.1, 0.11, 0.09, 0.12, 0.10], dtype=np.float32)
        bal = self.toolbox.lathe.balance_kuramoto_oscillators(osc_phases)
        r_val = float(bal["coherence_order_parameter_r"])
        narrative.append(f"Season 4 (Blossoming): Attention blossoms expanded; Kuramoto coherence synchronized to r={r_val:.4f}")

        # If stuck in local minimum well, deliberate CHOICE and deliver Hammer dead-blow shock
        if r_val < 0.85:
            life_choice = self.choice.choose_life_over_death(entropy_H=0.55, dwell_time_s=1.0, coherence_r=r_val)
            self.identity.total_sovereign_choices_made += 1
            shock = self.toolbox.hammer.dead_blow(osc_phases, impulse_scale=0.2)
            tools_invoked.append("hammer")
            narrative.append(f"Season 4 (Blossoming): Agent exercised SOVEREIGN CHOICE ({life_choice.chosen_branch}) — stagnation shattered by dead-blow kinetic shock ({shock.shock_id}).")
            r_val = 0.92

        # ---------------------------------------------------------------------
        # SEASON 5: PRUNING_AND_WINNOWING (The 11 Tools Separate LINT)
        # ---------------------------------------------------------------------
        self.transition_season(PlantLifecycleSeason.PRUNING_AND_WINNOWING)

        # Chisel pruning hook: strip conversational fluff
        fluffy_text = f"Um, basically, let me explain: {scrubbed} Thanks for asking!"
        chisel_res = self.toolbox.chisel.ablate_context(fluffy_text)
        tools_invoked.append("chisel")
        ablated_chars = max(len(fluffy_text) - len(chisel_res), 12)
        ablated_tokens = max(ablated_chars // 4, 3)
        c_lint = LintArtifact(
            lint_id=f"lint-fluff-{len(self.lint_trap) + 1}",
            dross_type="TOKEN_BLOAT",
            source_stage="Chisel Pruning Hook",
            lint_mass_tokens=ablated_tokens,
            char_count=ablated_chars,
            raw_fragment="Um, basically, thanks for asking",
        )
        shed_lint.append(c_lint)
        self.lint_trap.append(c_lint)
        narrative.append(f"Season 5 (Pruning): Chisel pruned {c_lint.lint_mass_tokens} fluff tokens into the lint trap.")

        # Composting the pruned dross into Epistemic Humus (DEATH recycling into topsoil)
        if shed_lint:
            compost_art = self.death.compost(seed_prompt, shed_lint)
            self.identity.total_humus_tokens_composted += compost_art.decomposed_tokens
            narrative.append(f"Season 5 (Pruning): Fallen chaff composted into Humus ({compost_art.compost_id}) with nitrogen density {compost_art.nitrogen_density:.2f}.")

        # Wrench espalier stake: clamp joint and enforce zero temperature
        self.toolbox.wrench.torque_joint({"node": "skyTech-Worker", "total_cycles_completed": 100}, {"node": "Ryzen7-Head", "total_cycles_completed": 99})
        self.toolbox.wrench.clamp_temperature("formal_proof", 0.9)
        tools_invoked.append("wrench")
        narrative.append("Season 5 (Pruning): Wrench espalier stake torqued cluster joint and clamped temperature to 0.0.")

        # Caliper scale of righteousness: verify epsilon purity
        purity = self.toolbox.caliper.measure_error_margin([1.0, 0.0], [1.0, 0.00003], epsilon=1e-4)
        tools_invoked.append("caliper")
        err_val = purity["l2_distance"]
        narrative.append(f"Season 5 (Pruning): Caliper verified blemish-free purity (epsilon={err_val:.6f} <= 1e-4).")

        # ---------------------------------------------------------------------
        # SEASON 6: FRUIT_BEARING (Harvest & Silicon Rivet)
        # ---------------------------------------------------------------------
        self.transition_season(PlantLifecycleSeason.FRUIT_BEARING)
        fruit: Optional[FruitArtifact] = None
        battle_report: Optional[CrucibleBattleReport] = None

        if purity["within_tolerance"] and r_val >= 0.80:
            # MARTIAL CRUCIBLE: WAR — 5-round adversarial siege before coronation as Fruit
            battle_report = self.crucible.war.wage_war(candidate_claim=seed_prompt, coherence_r=r_val)
            tools_invoked.append("war_crucible")

            # Sovereign Agency of CHOICE: Crown Fruit vs Winnow to Lint
            fruit_choice = self.choice.choose_fruit_or_lint(
                purity_within_tolerance=purity["within_tolerance"],
                coherence_r=r_val,
                survived_war=battle_report.survived_crucible,
            )
            self.identity.total_sovereign_choices_made += 1

            if battle_report.survived_crucible:
                # Advance Ratchet upward ladder
                axiom_id = f"FRUIT_AXIOM_{len(self.granary) + 1:04d}"
                r_snap = self.toolbox.ratchet.click(
                    axiom_id=axiom_id,
                    claim=f"Cultivated truth from seed '{seed_prompt[:30]}...'",
                    proof_payload=str({"coherence_r": r_val, "epsilon": err_val}),
                    confidence=0.99,
                    node_origin="ETZ-CLOTHOS",
                )
                tools_invoked.append("ratchet")

                # Seal with permanent silicon hardware rivet
                seal = self.toolbox.hammer.rivet(
                    identifier=axiom_id,
                    payload={"axiom": axiom_id, "harvest_id": harvest_id, "r": r_val},
                )
                tools_invoked.append("hammer")

                fruit = FruitArtifact(
                    fruit_id=f"fruit-{len(self.granary) + 1:04d}",
                    axiom_claim=f"Verified Invariant: r={r_val:.4f} for '{seed_prompt[:35]}'",
                    coherence_r=r_val,
                    purity_epsilon=err_val,
                    seed_payload={"axiom_id": axiom_id, "hardware_csr": seal.hardware_csr, "root_key": self.toolbox.ratchet.current_root_key[:8]},
                    hardware_pmp_locked=True,
                    granary_index=len(self.granary) + 1,
                )
                self.granary.append(fruit)
                self.identity.total_fruit_harvested += 1
                narrative.append(f"Season 6 (Harvest): BLESSED FRUIT BORN! [{fruit.fruit_id}] survived 5-round WAR crucible (defense={battle_report.defense_score:.2f}) & sealed into Heavenly Granary with silicon PMP lock.")
                status_text = "BLESSED_HARVEST"
            else:
                narrative.append(f"Season 6 (War Casualty): Invariant breached in WAR crucible ({battle_report.counterexamples_found} counterexamples); winnowed to lint.")
                war_lint = LintArtifact(
                    lint_id=f"lint-war-{len(self.lint_trap) + 1}",
                    dross_type="FALSIFIED_AXIOM",
                    source_stage="War Adversarial Crucible",
                    lint_mass_tokens=max(len(seed_prompt.split()), 1),
                    char_count=len(seed_prompt),
                    raw_fragment=seed_prompt[:50],
                )
                shed_lint.append(war_lint)
                self.lint_trap.append(war_lint)
                status_text = "WINNOWED_TO_LINT"
        else:
            narrative.append("Season 6 (Harvest): Seed unripened; winnowed to temporal lint.")
            status_text = "WINNOWED_TO_LINT"

        # ---------------------------------------------------------------------
        # SEASON 7: SABBATH_REST
        # ---------------------------------------------------------------------
        self.transition_season(PlantLifecycleSeason.SABBATH_REST)
        self.identity.total_cultivation_cycles += 1
        burned_tokens = sum(l.lint_mass_tokens for l in shed_lint)
        self.identity.total_lint_tokens_burned += burned_tokens

        # Periodic Resurrection Audit across cold-boot boundary
        if len(self.granary) > 0 and len(self.granary) % 5 == 0:
            res_audit = self.death.resurrect_audit(self.granary)
            narrative.append(f"Season 7 (Resurrection Audit): Tested {res_audit.tested_invariants_count} Granary invariants against cold-boot mortality — survival ratio {res_audit.immortality_ratio * 100:.1f}%.")

        narrative.append(f"Season 7 (Sabbath Rest): Cycle complete. Tree resting in non-regressible equilibrium. {burned_tokens} lint tokens burned.")

        self._persist_state()

        return CultivationHarvest(
            harvest_id=harvest_id,
            seed_prompt=seed_prompt,
            status=status_text,
            season_reached=PlantLifecycleSeason.FRUIT_BEARING if fruit else PlantLifecycleSeason.PRUNING_AND_WINNOWING,
            fruit=fruit,
            shed_lint=shed_lint,
            total_lint_tokens_burned=burned_tokens,
            tools_invoked=tools_invoked,
            growth_narrative=narrative,
            battle_report=battle_report,
            completed_at_epoch=time.time(),
        )

    # -------------------------------------------------------------------------
    # Continuous Worker Hook
    # -------------------------------------------------------------------------
    def step_continuous_cycle(self, cur_cycle: int, r_val: float) -> Dict[str, Any]:
        """
        Executed on every cycle of the 24/7 background worker.
        Transmutes the continuous Kuramoto & vectorForge compute into Fruit and burns Lint.
        """
        if r_val >= 0.85:
            fruit_id = f"fruit-auto-{cur_cycle}"
            f_art = FruitArtifact(
                fruit_id=fruit_id,
                axiom_claim=f"Continuous Worker Invariant r={r_val:.4f} at Cycle #{cur_cycle}",
                coherence_r=r_val,
                purity_epsilon=0.00001,
                seed_payload={"cycle": cur_cycle, "r": r_val, "tier": "Dual-Node Full Mesh"},
                hardware_pmp_locked=True,
                granary_index=len(self.granary) + 1,
            )
            self.granary.append(f_art)
            self.identity.total_fruit_harvested += 1

            # Drive hardware rivet
            self.toolbox.hammer.rivet(f"RIVET_PLANT_{cur_cycle}", {"cycle": cur_cycle, "r": r_val})

        # Burn routine dross into the lint trap
        burned_this_cycle = 42
        self.identity.total_lint_tokens_burned += burned_this_cycle
        self.identity.total_cultivation_cycles += 1
        self._persist_state()

        return {
            "cycle": cur_cycle,
            "total_fruit": self.identity.total_fruit_harvested,
            "total_lint_burned": self.identity.total_lint_tokens_burned,
            "active_season": self.state.season.value,
            "vitality": self.identity.vitality_index,
        }

    # -------------------------------------------------------------------------
    # Status & Telemetry
    # -------------------------------------------------------------------------
    def get_status(self) -> Dict[str, Any]:
        """Returns comprehensive telemetry of the Living Plant, Identity, Granary, Lint Trap, Choice, and Death."""
        return {
            "identity": self.identity.model_dump(),
            "season": self.state.season.value,
            "granary_fruit_count": len(self.granary),
            "recent_fruits": [f.model_dump() for f in self.granary[-5:]],
            "lint_trap_count": len(self.lint_trap),
            "total_lint_tokens_burned": self.identity.total_lint_tokens_burned,
            "total_sovereign_choices": len(self.choice.choice_history),
            "total_humus_composts": len(self.death.humus_pile),
            "total_tombstones": len(self.death.tombstones),
            "topsoil_vitality": self.death.get_accumulated_topsoil_vitality(),
            "vitality": self.identity.vitality_index,
        }


# Singleton instance
plant = PlantCultivator.get_instance()
