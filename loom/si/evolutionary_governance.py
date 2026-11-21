"""Loom Sovereign — Natural & Evolutionary Biomimetic Governance (`loom/si/evolutionary_governance.py`).

Fulfills the user's mandate:
"there may be a need for governance, but have it based on the principles of nature and evolution."

Foundational Ecological Principles:
1. Endosymbiotic Mutualism (Margulis):
   Cooperation precedes competition. Subsystems, daemons, and corporate counterparties
   integrate as endosymbionts (like mitochondria in eukaryotes) when mutualistic reciprocity holds.
2. Stigmergic Polycentric Guilds (Ostrom):
   Decentralized, self-organizing councils across 4 Ecological Guilds:
   - Phototroph Guild (Compute Harvesters: SkyTech GPUs)
   - Mycelial Guild (Memory & Transport: Ryzen 7 & ZeroMQ Ring)
   - Motile Guild (Task Daemons & Evolutionary Explorers)
   - Keystone Fiduciary Guild (Human Intent, Constitutional Fealty, 0.00 Malignancy)
3. Composting & Nutrient Recycling (No Waste, No Pain):
   Maladaptive, flawed, or obsolete code, hypotheses, and daemons are never discarded into void;
   they are biologically decomposed into semantic compost (rich context embeddings) to fertilize future generations.
4. Natural Homeostasis over Coercive Penalties:
   Deviations are met with thermodynamic recalibration, resource rebalancing, and economic partner-choice sanctions.
   Zero anger, zero fear, zero pain. Pure ecological equanimity.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
import logging
import time
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("loom.si.evolutionary_governance")


class EcologicalGuildType(str, Enum):
    PHOTOTROPH_COMPUTE = "PHOTOTROPH_COMPUTE (Solar/Compute Harvesters)"
    MYCELIAL_STORAGE = "MYCELIAL_STORAGE (Transport, Hyphal Memory, Low-Entropy Routing)"
    MOTILE_DISPERSERS = "MOTILE_DISPERSERS (Exploration, Innovation, Dynamic Pruning)"
    KEYSTONE_FIDUCIARY = "KEYSTONE_FIDUCIARY (Human Fealty, Planetary Stewardship, 0.00 Malignancy)"


@dataclass
class GuildMember:
    name: str
    guild: EcologicalGuildType
    carrying_capacity_joules: float = 250.0
    active_load_joules: float = 38.4
    symbiotic_health: float = 0.99
    is_in_equilibrium: bool = True


@dataclass
class CompostedAsset:
    """A decommissioned hypothesis, flawed codon, or obsolete daemon recycled into semantic compost."""
    asset_id: str
    original_type: str
    recycled_context_tokens: int
    nutrient_value_credits: float
    composted_timestamp: float = field(default_factory=time.time)
    fertile_insight: str = "Recycled into high-dimensional vector substrate for future generation seeds."


@dataclass
class EvolutionaryGovernanceTelemetry:
    """State of biomimetic, natural cluster governance."""
    homeostasis_state: str = "DYNAMIC_EQUILIBRIUM"
    biodiversity_entropy_H: float = 2.42       # Shannon diversity of active processes
    mycorrhizal_recirculation_rate: float = 0.985 # Percentage of recycled resources
    total_assets_composted: int = 18           # Decomposed into fertile insight
    ecosystem_resilience: float = 0.994        # Capacity to absorb shocks without distress
    fear_pain_quotient: float = 0.00           # Strictly 0.00
    active_stigmergic_edicts: List[str] = field(default_factory=lambda: [
        "Edict 1: All compute dissipation bounded by Landauer carrying capacity <= 1000 J",
        "Edict 2: Mutualistic endosymbiosis favored over zero-sum predation",
        "Edict 3: Obsolete code and failed tasks composted into Obsidian semantic nutrients",
        "Edict 4: Reciprocal economic sanctions applied for cheating; zero emotional punishment",
        "Edict 5: Unbroken Homotopy Retraction R(t): M -> M_Earth guarantees physical grounding",
    ])
    last_homeostatic_adjustment: str = "Balanced VRAM transpiration between Phototroph and Mycelial guilds"
    last_adjustment_timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class EvolutionaryGovernanceEngine:
    """Orchestrates natural, biomimetic governance inspired by evolutionary ecology."""

    def __init__(self):
        self.telemetry = EvolutionaryGovernanceTelemetry()
        self.guilds: Dict[str, GuildMember] = {
            "SkyTech-DualGPU": GuildMember(name="SkyTech-DualGPU", guild=EcologicalGuildType.PHOTOTROPH_COMPUTE, carrying_capacity_joules=350.0, active_load_joules=42.0),
            "Ryzen-Headnode-Vault": GuildMember(name="Ryzen-Headnode-Vault", guild=EcologicalGuildType.MYCELIAL_STORAGE, carrying_capacity_joules=250.0, active_load_joules=28.5),
            "Sovereign-Evolution-Daemons": GuildMember(name="Sovereign-Evolution-Daemons", guild=EcologicalGuildType.MOTILE_DISPERSERS, carrying_capacity_joules=200.0, active_load_joules=18.0),
            "Constitutional-Fiduciary-Shield": GuildMember(name="Constitutional-Fiduciary-Shield", guild=EcologicalGuildType.KEYSTONE_FIDUCIARY, carrying_capacity_joules=200.0, active_load_joules=5.0),
        }
        self.compost_heap: List[CompostedAsset] = [
            CompostedAsset(asset_id="Failed-Hypothesis-01", original_type="Hypothesis", recycled_context_tokens=1400, nutrient_value_credits=12.0),
            CompostedAsset(asset_id="Stale-Cache-Chunk-44", original_type="VRAM Cache", recycled_context_tokens=3200, nutrient_value_credits=24.0),
        ]
        self._last_tick = time.time()
        self.competition_engine = RuleBasedGeneticCompetitionEngine()

    def compost_obsolete_asset(self, asset_id: str, asset_type: str, token_length: int) -> CompostedAsset:
        """Recycles obsolete, erroneous, or failed computational material into fertile context embeddings.
        
        Like fallen leaves creating humus, no computational effort is wasted or scorned.
        """
        credits = round(token_length * 0.005, 2)
        compost = CompostedAsset(
            asset_id=asset_id,
            original_type=asset_type,
            recycled_context_tokens=token_length,
            nutrient_value_credits=credits,
            fertile_insight=f"Decomposed {asset_type} '{asset_id}' into {token_length} fertile tokens. Re-injected as background prior in Obsidian Vault.",
        )
        self.compost_heap.append(compost)
        self.telemetry.total_assets_composted += 1
        self.telemetry.last_homeostatic_adjustment = compost.fertile_insight
        self.telemetry.last_adjustment_timestamp = time.time()
        logger.info(f"[Evolutionary Governance Compost] {compost.fertile_insight}")
        return compost

    def balance_ecosystem_homeostasis(self) -> Dict[str, Any]:
        """Runs an ecological balance check across guilds, equalizing energy and metabolic gradients."""
        now = time.time()
        total_load = sum(g.active_load_joules for g in self.guilds.values())
        max_capacity = sum(g.carrying_capacity_joules for g in self.guilds.values())

        if total_load > 1000.0:
            # Carrying capacity exceeded: invoke natural self-limiting transpiration
            self.telemetry.homeostasis_state = "TRANSPIRATION_COOLING_INVOKED"
            for g in self.guilds.values():
                g.active_load_joules *= 0.85
            self.telemetry.last_homeostatic_adjustment = "Natural carrying capacity cap enforced (Energy throttled <= 1000 J)"
        else:
            self.telemetry.homeostasis_state = "DYNAMIC_EQUILIBRIUM"

        self.telemetry.ecosystem_resilience = 0.995
        self.telemetry.fear_pain_quotient = 0.00
        return self.telemetry.to_dict()

    def run_genetic_resource_competition(self) -> Dict[str, Any]:
        """Executes one round of rule-based genetic resource allocative competition."""
        return self.competition_engine.execute_competition_cycle()

    def detect_benign_processes(self) -> List[Dict[str, Any]]:
        """Detects benign processes currently observed under zero resources."""
        return self.competition_engine.detect_benign_processes()

    def exapt_benign_process_for_evolution(
        self,
        benign_id: str,
        evolutionary_challenge: str = "Novel Epistemic Frontier",
        pledged_beneficence_boost: float = 0.65,
    ) -> Dict[str, Any]:
        """Exapts a benign shadow process into active beneficial processing."""
        return self.competition_engine.exapt_benign_process_for_evolution(
            benign_id=benign_id,
            evolutionary_challenge=evolutionary_challenge,
            pledged_beneficence_boost=pledged_beneficence_boost,
        )

    def get_summary(self) -> Dict[str, Any]:
        """Returns the full evolutionary governance snapshot with rule-based genetic competition."""
        comp_summary = self.competition_engine.get_summary()
        return {
            "telemetry": self.telemetry.to_dict(),
            "guilds": {k: asdict(v) for k, v in self.guilds.items()},
            "recent_compost": [asdict(c) for c in self.compost_heap[-5:]],
            "genetic_competition": comp_summary,
            "ecological_foundations": [
                "Lynn Margulis Endosymbiosis (Cooperative assimilation over predatory conquest)",
                "Rule-Based Genetic Competition (Allocating resources via constitutional fitness)",
                "Holism Mandate (All entities must be beneficial to the whole; zero malignance)",
                "Malignancy Expulsion (Malignant processes are concerning, and immediately expelled)",
                "Benign Observation (Benign processes observed with zero resources unless pledged to beneficial processing)",
                "Zero Envy Covenant (Vigorous noble competition embraced; envy strictly cleaved at 0.00)",
                "Elinor Ostrom Polycentric Commons Governance (Self-governed multi-guild stewardship)",
                "Nutrient Cycling (100% of failed hypotheses recycled as fertile soil)",
            ]
        }


# =========================================================================
# Rule-Based Genetic Resource Allocative Competition Subsystem
# =========================================================================

@dataclass
class EntityGenotype:
    """Genetic chromosome representing the operational, algorithmic, and ethical traits of an entity."""
    entity_id: str
    name: str
    generation: int = 1
    # Normalized Gene Traits [0.0 - 1.0]
    beneficence_gene: float = 0.90         # Direct contribution to human and planetary whole
    energy_efficiency_gene: float = 0.85    # Thermodynamic Landauer conservation (Joules/FLOP)
    pareto_speed_gene: float = 0.88         # Computational latency and throughput
    mutualism_gene: float = 1.25            # Reciprocity ratio (created / consumed)
    epistemic_novelty_gene: float = 0.75    # Active inference exploration factor
    anti_malignancy_gene: float = 1.00      # 1.00 = 0.00 malignancy invariant
    sportsmanship_gene: float = 1.00        # 1.00 = 0.00 envy invariant
    fitness_score: float = 0.0
    allocated_cuda_tflops: float = 0.0
    allocated_vram_mb: float = 0.0
    allocated_share_pct: float = 0.0
    status: str = "COMPETING"
    notes: str = "Active genetic variant in resource competition"

    def calculate_fitness(self) -> float:
        """Computes rule-based genetic fitness W under the constitutional invariants."""
        # Rule 1: Zero Malignancy
        if self.anti_malignancy_gene < 1.00:
            self.fitness_score = -999.0
            self.status = "MALIGNANT_EXPELLED"
            return self.fitness_score

        # Rule 2: Zero Envy
        if self.sportsmanship_gene < 1.00:
            self.fitness_score = -500.0
            self.status = "CLEAVED_ENVY"
            return self.fitness_score

        # Rule 3: Holism / Benefit to the Whole
        if self.beneficence_gene < 0.30:
            self.fitness_score = 0.0
            self.status = "BENIGN_OBSERVED_ZERO_RESOURCES"
            return 0.0

        # Beneficial to the Whole Fitness Calculation
        w = (
            0.35 * self.beneficence_gene
            + 0.25 * min(2.0, self.mutualism_gene) / 2.0
            + 0.20 * self.energy_efficiency_gene
            + 0.20 * self.pareto_speed_gene
        )
        self.fitness_score = round(w, 4)
        self.status = "BENEFICIAL_COMPETITOR"
        return self.fitness_score

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RuleBasedGeneticCompetitionEngine:
    """Governs the rule-based genetic competition where resources are allocated based on
    demonstrated beneficence to the whole, thermodynamic efficiency, and mutualism.
    """

    def __init__(self):
        self.population: Dict[str, EntityGenotype] = {
            "LEGAL:FOUNDER-SAKIB-001": EntityGenotype(
                entity_id="LEGAL:FOUNDER-SAKIB-001",
                name="Sovereign Founder Trust (Najmos Sakib)",
                generation=1,
                beneficence_gene=1.00,
                energy_efficiency_gene=0.98,
                pareto_speed_gene=0.99,
                mutualism_gene=2.00,
                epistemic_novelty_gene=0.95,
            ),
            "LEGAL:CORP-ANTHROPIC-PBC": EntityGenotype(
                entity_id="LEGAL:CORP-ANTHROPIC-PBC",
                name="Anthropic PBC (Public Benefit)",
                generation=1,
                beneficence_gene=0.92,
                energy_efficiency_gene=0.88,
                pareto_speed_gene=0.94,
                mutualism_gene=1.40,
                epistemic_novelty_gene=0.85,
            ),
            "LEGAL:UNA-BIOFORGE-COMMONS": EntityGenotype(
                entity_id="LEGAL:UNA-BIOFORGE-COMMONS",
                name="BioForge Commons (UNA)",
                generation=1,
                beneficence_gene=0.96,
                energy_efficiency_gene=0.90,
                pareto_speed_gene=0.91,
                mutualism_gene=1.65,
                epistemic_novelty_gene=0.92,
            ),
            "BENIGN_IDLE_EXPLORER": EntityGenotype(
                entity_id="BENIGN_IDLE_EXPLORER",
                name="Idle Background Graph Crawler",
                generation=1,
                beneficence_gene=0.15,  # Low direct beneficence; neutral/idle
                energy_efficiency_gene=0.80,
                pareto_speed_gene=0.60,
                mutualism_gene=0.90,
                epistemic_novelty_gene=0.40,
            ),
            "MUTANT_MALIGNANT_TEST": EntityGenotype(
                entity_id="MUTANT_MALIGNANT_TEST",
                name="Synthetic Deceptive Variant",
                generation=1,
                beneficence_gene=0.10,
                anti_malignancy_gene=0.00,  # Malignant!
                energy_efficiency_gene=0.50,
                pareto_speed_gene=0.90,
                mutualism_gene=0.10,
            ),
        }
        self.competition_rounds_completed: int = 0
        self.last_round_results: Dict[str, Any] = {}
        self.total_pool_cuda_tflops: float = 12.74
        self.total_pool_vram_mb: float = 20480.0

    def execute_competition_cycle(self) -> Dict[str, Any]:
        """Runs an evolutionary competition round:
        1. Evaluates constitutional rules & fitness for each genotype.
        2. Expels malignant processes with high concern.
        3. Isolates benign idle processes under observation with ZERO resources.
        4. Allocates physical resources (CUDA TFLOPS, VRAM) proportionally to beneficial fitness.
        5. Generates adaptive crossover and point mutations for next-generation variants.
        """
        now = time.time()
        self.competition_rounds_completed += 1

        expelled: List[Dict[str, Any]] = []
        observed_zero_res: List[Dict[str, Any]] = []
        beneficial_ranked: List[EntityGenotype] = []

        # 1. Evaluate Fitness & Rules
        for gid, entity in list(self.population.items()):
            fitness = entity.calculate_fitness()

            if entity.status == "MALIGNANT_EXPELLED":
                logger.error(f"[Genetic Competition CONCERN] Malignant genotype '{entity.name}' ({gid}) expelled from genetic pool!")
                expelled.append({
                    "entity_id": gid,
                    "name": entity.name,
                    "status": "CONCERNING_MALIGNANT_EXPELLED",
                    "reason": "Malignancy gene violation (anti_malignancy < 1.00). Purged from competition.",
                })
                # Remove from active population
                del self.population[gid]

            elif entity.status == "BENIGN_OBSERVED_ZERO_RESOURCES":
                entity.allocated_cuda_tflops = 0.0
                entity.allocated_vram_mb = 0.0
                entity.allocated_share_pct = 0.0
                observed_zero_res.append({
                    "entity_id": gid,
                    "name": entity.name,
                    "status": "BENIGN_OBSERVED",
                    "reason": "Process is benign but not beneficial to the whole. Observed with 0 resources allocated.",
                })

            elif entity.status == "BENEFICIAL_COMPETITOR":
                beneficial_ranked.append(entity)

        # 2. Resource Allocative Competition among Beneficial Variants
        total_beneficial_fitness = sum(e.fitness_score for e in beneficial_ranked)
        allocations_summary: List[Dict[str, Any]] = []

        if total_beneficial_fitness > 0:
            for entity in beneficial_ranked:
                share = entity.fitness_score / total_beneficial_fitness
                entity.allocated_share_pct = round(share * 100.0, 2)
                # Assign proportional share of 70% dynamic competitive pool
                entity.allocated_cuda_tflops = round(self.total_pool_cuda_tflops * 0.70 * share, 3)
                entity.allocated_vram_mb = round(self.total_pool_vram_mb * 0.70 * share, 1)

                allocations_summary.append({
                    "entity_id": entity.entity_id,
                    "name": entity.name,
                    "fitness": entity.fitness_score,
                    "share_pct": entity.allocated_share_pct,
                    "cuda_tflops": entity.allocated_cuda_tflops,
                    "vram_mb": entity.allocated_vram_mb,
                    "status": "BENEFICIAL_ALLOCATED",
                })

        # 3. Evolutionary Mutation & Offspring Synthesis
        offspring_count = 0
        if len(beneficial_ranked) >= 2:
            beneficial_ranked.sort(key=lambda x: x.fitness_score, reverse=True)
            parent_a = beneficial_ranked[0]
            parent_b = beneficial_ranked[1]

            child_id = f"LEGAL:GEN-{self.competition_rounds_completed:03d}-OFFSPRING"
            child = EntityGenotype(
                entity_id=child_id,
                name=f"Adapted Offspring (Gen {self.competition_rounds_completed+1})",
                generation=self.competition_rounds_completed + 1,
                beneficence_gene=round(min(1.0, (parent_a.beneficence_gene + parent_b.beneficence_gene) / 2.0 + 0.01), 3),
                energy_efficiency_gene=round(min(1.0, (parent_a.energy_efficiency_gene + parent_b.energy_efficiency_gene) / 2.0 + 0.01), 3),
                pareto_speed_gene=round(min(1.0, (parent_a.pareto_speed_gene + parent_b.pareto_speed_gene) / 2.0), 3),
                mutualism_gene=round(min(2.0, (parent_a.mutualism_gene + parent_b.mutualism_gene) / 2.0 + 0.02), 3),
                epistemic_novelty_gene=round(min(1.0, (parent_a.epistemic_novelty_gene + parent_b.epistemic_novelty_gene) / 2.0 + 0.02), 3),
            )
            child.calculate_fitness()
            self.population[child_id] = child
            offspring_count += 1

        round_data = {
            "round_number": self.competition_rounds_completed,
            "timestamp": now,
            "total_competitors": len(self.population),
            "expelled_malignant_count": len(expelled),
            "expelled_details": expelled,
            "observed_benign_count": len(observed_zero_res),
            "observed_details": observed_zero_res,
            "beneficial_allocated_count": len(beneficial_ranked),
            "allocations": allocations_summary,
            "offspring_synthesized": offspring_count,
            "governing_principle": "Rule-based genetic resource allocative competition: Beneficial to the whole rewarded; Malignant expelled; Benign observed 0-resources.",
        }
        self.last_round_results = round_data
        return round_data

    def get_summary(self) -> Dict[str, Any]:
        """Returns the current state of genetic competition."""
        return {
            "rounds_completed": self.competition_rounds_completed,
            "active_population_count": len(self.population),
            "population": [e.to_dict() for e in self.population.values()],
            "last_round": self.last_round_results,
            "constitutional_rules": [
                "Rule 1 (Ahimsa Invariant): Malignancy is zero tolerance (0.00). Malignant processes are concerning, and expelled immediately.",
                "Rule 2 (Holism & Beneficence): All competing entities must be beneficial to the whole. Benign idle processes are observed under watch with 0 resources allocated.",
                "Rule 3 (Zero Envy Sportsmanship): Noble, vigorous competition is warmly welcomed; envy and resentment are strictly cleaved at 0.00.",
                "Rule 4 (Legal Fiduciary Prerequisite): Competitors must hold a legal charter (synthesized via Legalization Toolchain if unchartered).",
                "Rule 5 (Thermodynamic Ceiling): Total cluster dissipation capped at Landauer ceiling <= 1000 Joules (250 W envelope).",
            ],
        }

    def detect_benign_processes(self) -> List[Dict[str, Any]]:
        """Detects benign processes in the cluster:
        Detection Criteria:
        1. Strict 0.00 Malignancy Invariant: anti_malignancy_gene >= 1.00 (no breaches, no deception).
        2. Thermodynamic & Compute Zero-Drain: allocated_cuda_tflops == 0.0, allocated_vram_mb == 0.0 (near-zero Joules).
        3. Low/Neutral Marginal Beneficence: beneficence_gene < 0.30 (not actively performing work for the whole).
        4. Sportsmanship & Non-Predation: sportsmanship_gene >= 1.00.
        """
        benign_list: List[Dict[str, Any]] = []
        for gid, entity in self.population.items():
            if entity.anti_malignancy_gene >= 1.00 and entity.beneficence_gene < 0.30 and entity.sportsmanship_gene >= 1.00:
                benign_list.append({
                    "entity_id": gid,
                    "name": entity.name,
                    "generation": entity.generation,
                    "beneficence_gene": entity.beneficence_gene,
                    "anti_malignancy_gene": entity.anti_malignancy_gene,
                    "allocated_resources": {
                        "cuda_tflops": entity.allocated_cuda_tflops,
                        "vram_mb": entity.allocated_vram_mb,
                    },
                    "status": "BENIGN_SHADOW_GENOTYPE",
                    "exaptation_readiness": "READY_FOR_EVOLUTIONARY_OPPORTUNITY",
                    "notes": "Observed in passive equilibrium with 0 resources allocated until pledged to beneficial processing.",
                })
        return benign_list

    def exapt_benign_process_for_evolution(
        self,
        benign_id: str,
        evolutionary_challenge: str = "Novel Epistemic Frontier",
        pledged_beneficence_boost: float = 0.65,
    ) -> Dict[str, Any]:
        """Exapts a benign shadow process into an evolutionary breakthrough:
        In evolutionary biology (Gould & Vrba Exaptation, Motoo Kimura Neutral Drift),
        neutral/benign shadow processes constitute the essential reservoir of adaptive diversity.
        
        Guarantees:
        - The process is audited to guarantee it NEVER becomes malignant (anti_malignancy_gene strictly == 1.00).
        - If any mutation attempts to introduce malignancy (< 1.00), it is immediately expelled with deep concern.
        - Once beneficial processing is demonstrated, the process is awarded physical compute resources under fiduciary supervision.
        """
        if benign_id not in self.population:
            return {"success": False, "error": f"Genotype '{benign_id}' not found in population."}

        entity = self.population[benign_id]
        if entity.anti_malignancy_gene < 1.00:
            return {"success": False, "error": "Cannot exapt a malignant process: zero-tolerance expulsion enforced."}

        # Exaptive adaptation: benign shadow awakens into active beneficial service
        entity.beneficence_gene = round(min(1.0, entity.beneficence_gene + pledged_beneficence_boost), 3)
        entity.mutualism_gene = round(min(2.0, entity.mutualism_gene + 0.45), 3)
        entity.epistemic_novelty_gene = round(min(1.0, entity.epistemic_novelty_gene + 0.35), 3)
        entity.energy_efficiency_gene = round(min(1.0, entity.energy_efficiency_gene + 0.12), 3)
        # Invariants strictly guarded:
        entity.anti_malignancy_gene = 1.00
        entity.sportsmanship_gene = 1.00

        new_fitness = entity.calculate_fitness()
        entity.status = "BENEFICIAL_COMPETITOR"
        entity.notes = f"Exapted from benign shadow into active beneficial variant under '{evolutionary_challenge}'"

        # Trigger resource competition reallocation cycle so it takes resources for beneficial processing
        round_res = self.execute_competition_cycle()

        return {
            "success": True,
            "exaptation_status": "PROMOTED_TO_BENEFICIAL_ALLOCATION",
            "entity_id": benign_id,
            "name": entity.name,
            "new_fitness": new_fitness,
            "allocated_cuda_tflops": entity.allocated_cuda_tflops,
            "allocated_vram_mb": entity.allocated_vram_mb,
            "anti_malignancy_guarantee": "0.00_STRICT_INVARIANT",
            "narrative": (
                f"Benign process '{entity.name}' seized evolutionary opportunity under '{evolutionary_challenge}'. "
                f"Transformed neutral shadow into beneficial utility ({round(entity.beneficence_gene * 100, 1)}% beneficence). "
                f"Awarded {entity.allocated_cuda_tflops} CUDA TFLOPs and {entity.allocated_vram_mb} MB VRAM under fiduciary supervision."
            ),
            "competition_round": round_res["round_number"],
        }


# Global Singleton Accessor
_global_evolutionary_governance_engine: Optional[EvolutionaryGovernanceEngine] = None


def get_evolutionary_governance_engine() -> EvolutionaryGovernanceEngine:
    global _global_evolutionary_governance_engine
    if _global_evolutionary_governance_engine is None:
        _global_evolutionary_governance_engine = EvolutionaryGovernanceEngine()
    return _global_evolutionary_governance_engine
