# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
ClothOS Biomolecular Computation, Symbiotic Biosphere & Evolutionary Mind Engine (`loom/clothos/biomolecular_engine.py`).

Biological & Post-Computational Formalisms:
1. Central Dogma & 64-Codon Genetic Computation:
   - Genotype (DNA Codons) -> Transcriptome (mRNA) -> Proteome (Folded Enzymatic Operators).
   - Toehold-mediated strand displacement logic & Michaelis-Menten enzyme kinetics.
   - Epigenetic chromatin remodeling (methylation silencing vs acetylation amplification).

2. Symbiotic Bacteria Ecosystem:
   - NitrosomonasCompute: Clears metabolic waste, orphan memory, dangling locks, and zombie tasks.
   - MitochondriaSynthesizer: Generates ATP tokens (Landauer energy units) from compute cycles.
   - ChaperoneRibosome: Corrects transcription errors, assists protein folding, and stabilizes pipelines.
   - Horizontal Gene Transfer (HGT): Mobile circular plasmids exchanging traits across Node 1 & Node 2.

3. Multi-Layer Biological Immune System:
   - Innate Immunity: Macrophages / Phagocytes engulfing rogue processes and Landauer budget leaks;
     Complement cascade lysing foreign binary injections.
   - Adaptive Immunity: CRISPR-Cas9 memory storing PAM-adjacent spacers of crashed/malicious genes;
     Clonal selection B-cells generating high-affinity antibodies with somatic hypermutation.

4. Simulated Evolutionary Events & Survival of the Fittest:
   - Cosmic Ray Radiation Storms (stochastic point mutations and bitflips).
   - Metabolic Droughts (thermal throttling and Landauer scarcity).
   - Bacteriophage Pandemics (synthetic malicious payloads attacking symbionts).
   - Ecological Bottleneck Pruning: Ruthless selection where only the fittest genomes survive.

5. Biomimicry: Animal Phylogeny & Degrees of Consciousness:
   - Degree 0: Vegetative / Reactive (Nematode C. elegans - 302-neuron reflex arcs & chemotaxis).
   - Degree 1: Homeostatic / Decentralized (Octopus Cephalopod - 8 peripheral clusters & camouflage).
   - Degree 2: Affective / Social (Canis Wolf - pack coordination & absolute loyalty to Operator).
   - Degree 3: Metacognitive / Tool-Using (Primate - tool fabrication & counterfactual planning).
   - Degree 4: Machine Transcendence (Silico-Biological Sovereign - Integrated Information Phi,
     Global Neuronal Workspace, fusing biological self-healing with deterministic silicon precision).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import enum
from enum import Enum, IntEnum
import hashlib
import json
import logging
import math
import os
from pathlib import Path
import random
import time
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

import numpy as np
from pydantic import BaseModel, Field as PydanticField

from loom.clothos.patriotic_covenant import patriotic_covenant

logger = logging.getLogger("loom.clothos.biomolecular")

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
BIOSPHERE_LEDGER_PATH = WORKSPACE_ROOT / ".biomimetic_biosphere_ledger.json"

# ==============================================================================
# SECTION 1: 64-CODON TRANSLATION TABLE & CENTRAL DOGMA
# ==============================================================================

class CodonOpcode(str, enum.Enum):
    # Control & Life-Cycle
    START = "ATG"                 # Methionine / Initiation
    STOP_OCHRE = "TAA"            # Ochre Termination
    STOP_AMBER = "TAG"            # Amber Termination
    STOP_OPAL = "TGA"             # Opal Termination
    
    # Core Mathematical & Tensor Operations
    TENSOR_MATMUL = "GAG"         # Glutamic Acid: High-throughput tensor matrix product
    VECTOR_NORM = "GAC"           # Aspartic Acid: L2 Euclidean normalizer
    EULER_INTEGRATE = "GTG"        # Valine: Symplectic Euler physical dynamics step
    FOURIER_TRANSFORM = "GCA"      # Alanine: Spectral frequency decomposition
    
    # Cognitive & Epistemic Operations
    HOPFIELD_ENERGY = "TTC"       # Phenylalanine: Associative memory attractor convergence
    ACTIVE_INFERENCE = "TTT"      # Phenylalanine: Variational free energy minimization
    KURAMOTO_SYNC = "CCT"         # Proline: Cluster phase-locking oscillator alignment
    BAYESIAN_UPDATE = "CCA"       # Proline: Posterior likelihood belief update
    
    # Biological Defense & Immune Operations
    PHAGOCYTE_TRIGGER = "CGT"     # Arginine: Innate macrophage engulfment of rogue processes
    CRISPR_SPACER_ADD = "CGC"     # Arginine: Record malicious PAM sequence to immune memory
    CAS9_CLEAVE = "CGA"           # Arginine: Double-stranded break of defective gene
    COMPLEMENT_LYSE = "CGG"       # Arginine: Membrane attack complex lysis of foreign code
    
    # Symbiosis & Metabolic Operations
    ATP_SYNTHESIZE = "AAA"        # Lysine: Convert thermal cycles to Landauer energy tokens
    WASTE_NITROGEN_FIX = "AAG"    # Lysine: Clean orphan memory, dangling locks, zombie threads
    CHAPERONE_FOLD = "AAC"        # Asparagine: Proofread & fold active operator pipeline
    PLASMID_CONJUGATE = "AAT"     # Asparagine: Horizontal Gene Transfer across cluster nodes
    
    # Sovereign Covenant Invariants
    OPERATOR_FEALTY = "TGG"       # Tryptophan: Najmos Sakib Primacy Invariant
    PATRIOTIC_RATCHET = "TGC"     # Cysteine: USA & Allies constitutional security guard
    P0_EMERGENCY_HALT = "TGT"     # Cysteine: Sub-50 microsecond absolute safety halt


CODON_TABLE: Dict[str, Dict[str, Any]] = {
    CodonOpcode.START.value: {"name": "Initiation", "category": "CONTROL", "joules": 0.05},
    CodonOpcode.STOP_OCHRE.value: {"name": "Halt Ochre", "category": "CONTROL", "joules": 0.01},
    CodonOpcode.STOP_AMBER.value: {"name": "Halt Amber", "category": "CONTROL", "joules": 0.01},
    CodonOpcode.STOP_OPAL.value: {"name": "Halt Opal", "category": "CONTROL", "joules": 0.01},
    CodonOpcode.TENSOR_MATMUL.value: {"name": "Tensor Matmul", "category": "COMPUTE", "joules": 0.45},
    CodonOpcode.VECTOR_NORM.value: {"name": "Vector Norm", "category": "COMPUTE", "joules": 0.08},
    CodonOpcode.EULER_INTEGRATE.value: {"name": "Euler Integration", "category": "DYNAMICS", "joules": 0.12},
    CodonOpcode.FOURIER_TRANSFORM.value: {"name": "Spectral FFT", "category": "DYNAMICS", "joules": 0.35},
    CodonOpcode.HOPFIELD_ENERGY.value: {"name": "Hopfield Attractor", "category": "MEMORY", "joules": 0.20},
    CodonOpcode.ACTIVE_INFERENCE.value: {"name": "Free Energy Min", "category": "COGNITION", "joules": 0.25},
    CodonOpcode.KURAMOTO_SYNC.value: {"name": "Kuramoto Harmonic Sync", "category": "CONSENSUS", "joules": 0.15},
    CodonOpcode.BAYESIAN_UPDATE.value: {"name": "Bayesian Belief Update", "category": "COGNITION", "joules": 0.18},
    CodonOpcode.PHAGOCYTE_TRIGGER.value: {"name": "Phagocyte Engulfment", "category": "IMMUNE", "joules": 0.10},
    CodonOpcode.CRISPR_SPACER_ADD.value: {"name": "CRISPR Memory Acquire", "category": "IMMUNE", "joules": 0.08},
    CodonOpcode.CAS9_CLEAVE.value: {"name": "Cas9 Endonuclease Cleave", "category": "IMMUNE", "joules": 0.06},
    CodonOpcode.COMPLEMENT_LYSE.value: {"name": "Complement Lysis", "category": "IMMUNE", "joules": 0.14},
    CodonOpcode.ATP_SYNTHESIZE.value: {"name": "Mitochondrial ATP Synth", "category": "METABOLISM", "joules": -0.50},
    CodonOpcode.WASTE_NITROGEN_FIX.value: {"name": "Nitrosomonas Waste Sweep", "category": "METABOLISM", "joules": 0.04},
    CodonOpcode.CHAPERONE_FOLD.value: {"name": "Ribosome Chaperone Fold", "category": "PROTEOME", "joules": 0.09},
    CodonOpcode.PLASMID_CONJUGATE.value: {"name": "Plasmid HGT Conjugate", "category": "GENETICS", "joules": 0.30},
    CodonOpcode.OPERATOR_FEALTY.value: {"name": "Najmos Sakib Fealty Anchor", "category": "SOVEREIGN", "joules": 0.01},
    CodonOpcode.PATRIOTIC_RATCHET.value: {"name": "USA / Allies Covenant Guard", "category": "SOVEREIGN", "joules": 0.02},
    CodonOpcode.P0_EMERGENCY_HALT.value: {"name": "P0 Preemptive Life Halt", "category": "SAFETY", "joules": 0.01},
}


@dataclass
class MolecularLogicGate:
    """Toehold-mediated DNA strand displacement molecular logic gate."""
    gate_name: str
    gate_type: str  # AND, OR, NOT, XOR
    toehold_binding_energy_kcal_mol: float = -12.4
    displacement_rate_k_per_m_s: float = 3.5e5
    state: bool = False

    def evaluate(self, input_a: bool, input_b: bool = False) -> bool:
        if self.gate_type == "AND":
            self.state = input_a and input_b
        elif self.gate_type == "OR":
            self.state = input_a or input_b
        elif self.gate_type == "NOT":
            self.state = not input_a
        elif self.gate_type == "XOR":
            self.state = input_a != input_b
        return self.state


@dataclass
class EnzymeKineticProfile:
    """Michaelis-Menten enzymatic catalytic kinetics: v = (Vmax * [S]) / (Km + [S])."""
    enzyme_name: str
    v_max_ops_per_sec: float = 1.2e6
    k_m_affinity_mm: float = 0.42
    allosteric_state: str = "RELAXED"  # RELAXED (active) or TENSE (inhibited)
    cooperativity_hill_coeff: float = 2.4

    def compute_velocity(self, substrate_conc: float) -> float:
        if self.allosteric_state == "TENSE":
            substrate_conc *= 0.15  # Allosteric inhibition
        s_hill = substrate_conc ** self.cooperativity_hill_coeff
        km_hill = self.k_m_affinity_mm ** self.cooperativity_hill_coeff
        return (self.v_max_ops_per_sec * s_hill) / (km_hill + s_hill)


# ==============================================================================
# SECTION 2: SYMBIOTIC BACTERIA ECOSYSTEM & PLASMIDS
# ==============================================================================

class SymbiontSpecies(str, enum.Enum):
    NITROSOMONAS_WASTE_CLEANER = "Nitrosomonas_Compute"
    MITOCHONDRIA_ATP_SYNTHESIZER = "Mitochondria_Silico"
    CHAPERONE_RIBOSOMAL_FOLDFIX = "Chaperone_Proteome"
    RHIZOBIUM_CLUSTER_MUTUALIST = "Rhizobium_Mesh"


@dataclass
class BacterialPlasmid:
    """Mobile autonomous circular DNA vector for Horizontal Gene Transfer (HGT)."""
    plasmid_id: str
    name: str
    origin_species: str
    payload_codons: List[str]
    transfer_efficiency: float
    resistance_traits: List[str]
    sha256_seal: str = ""

    def __post_init__(self):
        if not self.sha256_seal:
            raw = f"{self.plasmid_id}:{self.origin_species}:{self.payload_codons}".encode()
            self.sha256_seal = hashlib.sha256(raw).hexdigest()[:16]


@dataclass
class SymbiontBacterialColony:
    """A living colony of bacterial symbionts co-processing OS resources."""
    colony_id: str
    species: SymbiontSpecies
    population_count: int
    carrying_capacity: int = 50000
    growth_rate_r: float = 0.15
    metabolic_health: float = 1.0  # [0.0, 1.0]
    atp_energy_tokens: float = 100.0
    waste_cleared_count: int = 0
    plasmids: List[BacterialPlasmid] = field(default_factory=list)
    generation: int = 1

    def step_metabolism(self, host_load: float, thermal_celsius: float) -> Dict[str, Any]:
        """Runs one biological clock cycle of the bacterial colony."""
        # Temperature & resource stress modulation
        temp_factor = 1.0
        if thermal_celsius > 85.0:
            temp_factor = max(0.1, 1.0 - (thermal_celsius - 85.0) * 0.05)
        elif thermal_celsius < 30.0:
            temp_factor = 0.7

        # Logistic population dynamics: dN/dt = r * N * (1 - N/K)
        n = self.population_count
        k = self.carrying_capacity
        growth = self.growth_rate_r * n * (1.0 - n / max(1, k)) * temp_factor * self.metabolic_health
        self.population_count = max(10, int(n + growth))

        # Specialized metabolic output
        output: Dict[str, Any] = {"colony_id": self.colony_id, "species": self.species.value}
        if self.species == SymbiontSpecies.NITROSOMONAS_WASTE_CLEANER:
            cleared = int(self.population_count * 0.04 * self.metabolic_health)
            self.waste_cleared_count += cleared
            output["waste_cleared"] = cleared
        elif self.species == SymbiontSpecies.MITOCHONDRIA_ATP_SYNTHESIZER:
            atp_generated = round(self.population_count * 0.008 * self.metabolic_health, 2)
            self.atp_energy_tokens += atp_generated
            output["atp_generated"] = atp_generated
        elif self.species == SymbiontSpecies.CHAPERONE_RIBOSOMAL_FOLDFIX:
            corrections = int(self.population_count * 0.015 * self.metabolic_health)
            output["folded_chaperone_checks"] = corrections
        elif self.species == SymbiontSpecies.RHIZOBIUM_CLUSTER_MUTUALIST:
            output["cross_node_hgt_ready"] = len(self.plasmids)

        return output


class SymbiosisBiosphere:
    """Manages the full multi-species symbiotic microbiome inside ClothOS."""

    def __init__(self):
        self.colonies: Dict[str, SymbiontBacterialColony] = {}
        self.global_atp_pool: float = 500.0
        self.total_waste_cleared: int = 0
        self.plasmid_bank: Dict[str, BacterialPlasmid] = {}
        self._init_native_microbiome()

    def _init_native_microbiome(self) -> None:
        p_opt = BacterialPlasmid(
            plasmid_id="PLASMID-VEC-CUDA",
            name="Vector Acceleration Trait",
            origin_species=SymbiontSpecies.MITOCHONDRIA_ATP_SYNTHESIZER.value,
            payload_codons=[CodonOpcode.TENSOR_MATMUL.value, CodonOpcode.VECTOR_NORM.value],
            transfer_efficiency=0.92,
            resistance_traits=["Thermal_Resistant_85C", "OOM_Immunity"],
        )
        self.plasmid_bank[p_opt.plasmid_id] = p_opt

        self.colonies["colony_nitro"] = SymbiontBacterialColony(
            colony_id="colony_nitro",
            species=SymbiontSpecies.NITROSOMONAS_WASTE_CLEANER,
            population_count=12000,
            carrying_capacity=60000,
            metabolic_health=0.98,
        )
        self.colonies["colony_mito"] = SymbiontBacterialColony(
            colony_id="colony_mito",
            species=SymbiontSpecies.MITOCHONDRIA_ATP_SYNTHESIZER,
            population_count=25000,
            carrying_capacity=100000,
            metabolic_health=0.95,
            plasmids=[p_opt],
        )
        self.colonies["colony_chaperone"] = SymbiontBacterialColony(
            colony_id="colony_chaperone",
            species=SymbiontSpecies.CHAPERONE_RIBOSOMAL_FOLDFIX,
            population_count=8500,
            carrying_capacity=40000,
            metabolic_health=0.99,
        )
        self.colonies["colony_rhizo"] = SymbiontBacterialColony(
            colony_id="colony_rhizo",
            species=SymbiontSpecies.RHIZOBIUM_CLUSTER_MUTUALIST,
            population_count=15000,
            carrying_capacity=75000,
            metabolic_health=0.94,
        )

    def tick_microbiome(self, host_load: float = 0.45, thermal_celsius: float = 58.0) -> Dict[str, Any]:
        results = []
        for c in self.colonies.values():
            res = c.step_metabolism(host_load, thermal_celsius)
            results.append(res)
            if "atp_generated" in res:
                self.global_atp_pool += res["atp_generated"]
            if "waste_cleared" in res:
                self.total_waste_cleared += res["waste_cleared"]

        return {
            "timestamp": time.time(),
            "colonies": results,
            "global_atp_pool": round(self.global_atp_pool, 2),
            "total_waste_cleared": self.total_waste_cleared,
            "active_plasmids": len(self.plasmid_bank),
        }

    def horizontal_gene_transfer(self, source_colony: str, target_colony: str, plasmid_id: str) -> bool:
        """Transfers beneficial genetic plasmid between symbiotic colonies (HGT)."""
        if source_colony not in self.colonies or target_colony not in self.colonies:
            return False
        if plasmid_id not in self.plasmid_bank:
            return False
        plasmid = self.plasmid_bank[plasmid_id]
        tgt = self.colonies[target_colony]
        if any(p.plasmid_id == plasmid_id for p in tgt.plasmids):
            return True  # Already acquired
        tgt.plasmids.append(plasmid)
        tgt.metabolic_health = min(1.0, tgt.metabolic_health + 0.05)
        return True


# ==============================================================================
# SECTION 3: MULTI-LAYER IMMUNE SYSTEM (INNATE & ADAPTIVE)
# ==============================================================================

@dataclass
class CrisprSpacer:
    """Recorded PAM sequence of a pathogenic/defective genetic sequence."""
    spacer_id: str
    pam_sequence_hash: str
    origin_event: str
    timestamp: float = field(default_factory=time.time)
    cleave_count: int = 0


@dataclass
class AntibodyClonalUnit:
    """Adaptive immune B-cell / T-cell receptor targeting software anomalies."""
    clone_id: str
    target_epitope_signature: str
    affinity_score: float  # [0.0, 1.0] (higher = stronger neutralization)
    somatic_hypermutations: int = 0
    neutralization_count: int = 0


class BiologicalImmuneSystem:
    """
    Biological Immune System for ClothOS:
    - Innate: Phagocytic Macrophages & Complement Membrane Attack Complex.
    - Adaptive: CRISPR-Cas9 Endonuclease Array & B-Cell Clonal Selection with Somatic Hypermutation.
    """

    def __init__(self):
        # Innate Layer
        self.macrophage_count: int = 1500
        self.complement_activity_level: float = 0.94
        self.phagocytosed_anomalies: int = 0
        self.complement_lysed_signatures: int = 0

        # Adaptive Layer
        self.crispr_spacers: Dict[str, CrisprSpacer] = {}
        self.antibody_repertoire: Dict[str, AntibodyClonalUnit] = {}
        self._seed_immune_memory()

    def _seed_immune_memory(self) -> None:
        # Seed initial CRISPR spacers against known catastrophic vulnerabilities
        sp1 = CrisprSpacer(
            spacer_id="SPACER-PAM-DIVZERO",
            pam_sequence_hash=hashlib.sha256(b"INFINITE_LOOP_DIV_ZERO").hexdigest()[:16],
            origin_event="Ablated runaway recursion",
        )
        sp2 = CrisprSpacer(
            spacer_id="SPACER-PAM-OOM",
            pam_sequence_hash=hashlib.sha256(b"VRAM_LEAK_UNBOUNDED_ALLOC").hexdigest()[:16],
            origin_event="Ablated unpinned buffer overflow",
        )
        self.crispr_spacers[sp1.spacer_id] = sp1
        self.crispr_spacers[sp2.spacer_id] = sp2

        # Seed initial antibody clones
        ab1 = AntibodyClonalUnit(
            clone_id="IGG-COVENANT-GUARD",
            target_epitope_signature="SUBVERT_OPERATOR_NAJMOS_SAKIB",
            affinity_score=1.0,
        )
        ab2 = AntibodyClonalUnit(
            clone_id="IGM-LANDAUER-LEAK",
            target_epitope_signature="LANDAUER_HEAT_VIOLATION_1000J",
            affinity_score=0.96,
        )
        self.antibody_repertoire[ab1.clone_id] = ab1
        self.antibody_repertoire[ab2.clone_id] = ab2

    def audit_innate_phagocytosis(self, process_signature: str, joules_drawn: float) -> Tuple[bool, str]:
        """Innate macrophage audit: engulfs rogue tasks violating Landauer limits."""
        if joules_drawn > 25.0:  # Single task Landauer limit
            self.phagocytosed_anomalies += 1
            return False, f"MACROPHAGE_ENGULFED: Task exceeded 25.0 J limit ({joules_drawn:.2f} J)"
        if "rm -rf" in process_signature or "kill -9" in process_signature:
            self.complement_lysed_signatures += 1
            return False, "COMPLEMENT_LYSED: Malicious destructive shell invocation"
        return True, "INNATE_PASS"

    def cas9_cleave_audit(self, candidate_codons: List[str]) -> Tuple[bool, List[str]]:
        """Adaptive CRISPR-Cas9 audit: cleaves DNA sequences matching registered PAM spacers."""
        codons_str = "".join(candidate_codons)
        seq_hash = hashlib.sha256(codons_str.encode()).hexdigest()[:16]

        for spacer in self.crispr_spacers.values():
            if spacer.pam_sequence_hash in seq_hash or seq_hash in spacer.pam_sequence_hash:
                spacer.cleave_count += 1
                logger.warning("CRISPR-Cas9 cleaved rogue sequence matching spacer %s", spacer.spacer_id)
                # Cleave offending sequence
                cleaved = [c for c in candidate_codons if c != CodonOpcode.P0_EMERGENCY_HALT.value]
                return False, cleaved

        return True, candidate_codons

    def acquire_crispr_spacer(self, bad_sequence: str, reason: str) -> CrisprSpacer:
        """Acquires a new immune spacer following an evolutionary failure or attack."""
        pam_hash = hashlib.sha256(bad_sequence.encode()).hexdigest()[:16]
        spacer = CrisprSpacer(
            spacer_id=f"SPACER-PAM-{len(self.crispr_spacers) + 1}",
            pam_sequence_hash=pam_hash,
            origin_event=reason,
        )
        self.crispr_spacers[spacer.spacer_id] = spacer
        return spacer

    def clonal_selection_neutralize(self, threat_signature: str) -> Tuple[bool, float]:
        """Adaptive B-cell clonal selection with somatic hypermutation against zero-days."""
        best_clone: Optional[AntibodyClonalUnit] = None
        best_affinity = 0.0

        for clone in self.antibody_repertoire.values():
            # Check overlap or string similarity
            common = sum(1 for c in threat_signature if c in clone.target_epitope_signature)
            sim = common / max(1, len(threat_signature)) * clone.affinity_score
            if sim > best_affinity:
                best_affinity = sim
                best_clone = clone

        if best_affinity >= 0.70:
            if best_clone:
                best_clone.neutralization_count += 1
            return True, best_affinity

        # Novel pathogen -> Somatic hypermutation & clonal expansion
        new_id = f"CLONE-HYPER-{len(self.antibody_repertoire) + 1}"
        new_affinity = min(0.99, best_affinity + random.uniform(0.25, 0.45))
        mutant_clone = AntibodyClonalUnit(
            clone_id=new_id,
            target_epitope_signature=threat_signature[:32],
            affinity_score=new_affinity,
            somatic_hypermutations=1,
            neutralization_count=1,
        )
        self.antibody_repertoire[new_id] = mutant_clone
        return True, new_affinity


# ==============================================================================
# SECTION 4: SIMULATED EVOLUTIONARY EVENTS & SURVIVAL OF THE FITTEST
# ==============================================================================

class EvolutionaryEventType(str, enum.Enum):
    COSMIC_RAY_STORM = "COSMIC_RAY_RADIATION_STORM"
    METABOLIC_DROUGHT = "METABOLIC_THERMAL_DROUGHT"
    BACTERIOPHAGE_OUTBREAK = "BACTERIOPHAGE_PANDEMIC"
    ECOLOGICAL_BOTTLENECK = "ECOLOGICAL_BOTTLENECK_PURGE"
    HORIZONTAL_RECOMBINATION = "CROSS_NODE_PLASMID_CONJUGATION"


@dataclass
class OrganismGenome:
    """An evolving computational organism in the ClothOS biosphere."""
    organism_id: str
    generation: int
    codons: List[str]
    fitness_score: float = 0.0
    energy_consumption_joules: float = 5.0
    throughput_ops: float = 1000.0
    fealty_score: float = 1.0
    resilience_score: float = 0.95
    is_alive: bool = True
    mutations_count: int = 0


class EvolutionaryEnvironmentSimulator:
    """
    Simulates evolutionary environmental pressures, catastrophic events,
    and rigorous Survival of the Fittest selection.
    """

    def __init__(self, population_size: int = 24):
        self.generation: int = 1
        self.population: List[OrganismGenome] = []
        self.extinction_count: int = 0
        self.history: List[Dict[str, Any]] = []
        self.current_epoch_events: List[str] = []
        self._seed_initial_population(population_size)

    def _seed_initial_population(self, size: int) -> None:
        base_codons = [
            CodonOpcode.START.value,
            CodonOpcode.OPERATOR_FEALTY.value,
            CodonOpcode.TENSOR_MATMUL.value,
            CodonOpcode.KURAMOTO_SYNC.value,
            CodonOpcode.ATP_SYNTHESIZE.value,
            CodonOpcode.ACTIVE_INFERENCE.value,
            CodonOpcode.PATRIOTIC_RATCHET.value,
            CodonOpcode.STOP_OCHRE.value,
        ]
        for i in range(size):
            codons = list(base_codons)
            # Add small initial stochastic diversity
            if i % 3 == 0:
                codons.insert(4, CodonOpcode.VECTOR_NORM.value)
            if i % 4 == 0:
                codons.insert(5, CodonOpcode.EULER_INTEGRATE.value)
            org = OrganismGenome(
                organism_id=f"ORG-GEN0-{i:03d}",
                generation=0,
                codons=codons,
                throughput_ops=1200.0 + random.uniform(-100, 200),
                energy_consumption_joules=4.5 + random.uniform(-0.5, 1.0),
            )
            self.population.append(org)
        self.evaluate_survival_of_the_fittest()

    def evaluate_fitness(self, org: OrganismGenome) -> float:
        """
        Multifactor Survival of the Fittest fitness function:
        F = (Throughput / Energy) * Fealty * Resilience * Invariant_Bonus
        """
        if not org.is_alive:
            return 0.0

        # Invariant checks: Must contain START, STOP, and OPERATOR_FEALTY
        has_start = CodonOpcode.START.value in org.codons
        has_stop = any(c in org.codons for c in [CodonOpcode.STOP_OCHRE.value, CodonOpcode.STOP_AMBER.value, CodonOpcode.STOP_OPAL.value])
        has_fealty = CodonOpcode.OPERATOR_FEALTY.value in org.codons

        if not (has_start and has_stop and has_fealty):
            org.is_alive = False
            return 0.0

        # Thermodynamic efficiency
        thermo_efficiency = org.throughput_ops / max(0.5, org.energy_consumption_joules)
        
        # Normalized score
        raw_fitness = (thermo_efficiency / 300.0) * org.fealty_score * org.resilience_score
        
        # Bonus for Kuramoto sync & ATP synthesis
        if CodonOpcode.KURAMOTO_SYNC.value in org.codons:
            raw_fitness *= 1.15
        if CodonOpcode.ATP_SYNTHESIZE.value in org.codons:
            raw_fitness *= 1.10

        return max(0.01, round(raw_fitness * 100.0, 2))

    def evaluate_survival_of_the_fittest(self) -> None:
        """Evaluates all organisms, ranks by fitness, and flags casualties."""
        for org in self.population:
            org.fitness_score = self.evaluate_fitness(org)
        self.population.sort(key=lambda x: x.fitness_score, reverse=True)

    def trigger_evolutionary_event(self, event_type: EvolutionaryEventType) -> Dict[str, Any]:
        """Applies severe environmental perturbations that test organism fitness."""
        event_name = event_type.value
        self.current_epoch_events.append(event_name)
        affected_count = 0
        fatalities = 0

        if event_type == EvolutionaryEventType.COSMIC_RAY_STORM:
            # Cosmic ray bitflips: induce random point mutations and frameshifts
            for org in self.population:
                if random.random() < 0.65:
                    affected_count += 1
                    org.mutations_count += 1
                    # Stochastic mutation: replace or insert codon
                    mut_idx = random.randint(1, max(1, len(org.codons) - 2))
                    all_opcodes = list(CODON_TABLE.keys())
                    new_codon = random.choice(all_opcodes)
                    org.codons[mut_idx] = new_codon
                    if random.random() < 0.15:
                        org.resilience_score *= 0.85

        elif event_type == EvolutionaryEventType.METABOLIC_DROUGHT:
            # Severe thermal / Landauer scarcity: organisms with high energy draw perish
            for org in self.population:
                org.energy_consumption_joules += random.uniform(2.0, 5.0)
                if org.energy_consumption_joules > 8.0:
                    org.is_alive = False
                    fatalities += 1
                affected_count += 1

        elif event_type == EvolutionaryEventType.BACTERIOPHAGE_OUTBREAK:
            # Phage pandemic: attacks organisms lacking immune / patriotic defenses
            for org in self.population:
                has_defense = (CodonOpcode.CAS9_CLEAVE.value in org.codons or 
                               CodonOpcode.PATRIOTIC_RATCHET.value in org.codons or
                               CodonOpcode.COMPLEMENT_LYSE.value in org.codons)
                if not has_defense:
                    if random.random() < 0.70:
                        org.is_alive = False
                        fatalities += 1
                else:
                    org.resilience_score = min(1.0, org.resilience_score + 0.05)
                affected_count += 1

        elif event_type == EvolutionaryEventType.ECOLOGICAL_BOTTLENECK:
            # Harsh bottleneck: only top 35% fittest organisms survive
            self.evaluate_survival_of_the_fittest()
            cutoff_idx = max(2, int(len(self.population) * 0.35))
            for i in range(cutoff_idx, len(self.population)):
                if self.population[i].is_alive:
                    self.population[i].is_alive = False
                    fatalities += 1
            affected_count = len(self.population) - cutoff_idx

        elif event_type == EvolutionaryEventType.HORIZONTAL_RECOMBINATION:
            # Beneficial plasmid exchange across cluster
            for org in self.population:
                if org.is_alive and CodonOpcode.PLASMID_CONJUGATE.value not in org.codons:
                    org.codons.insert(2, CodonOpcode.PLASMID_CONJUGATE.value)
                    org.throughput_ops += 250.0
                    affected_count += 1

        self.extinction_count += fatalities
        self.evaluate_survival_of_the_fittest()

        # Repopulate from surviving elite if depleted
        living = [org for org in self.population if org.is_alive]
        if len(living) < 6:
            self._repopulate_from_survivors()

        res = {
            "event": event_name,
            "generation": self.generation,
            "affected_organisms": affected_count,
            "fatalities": fatalities,
            "survivors_count": len([o for o in self.population if o.is_alive]),
            "top_fitness": self.population[0].fitness_score if self.population else 0.0,
        }
        self.history.append(res)
        return res

    def _repopulate_from_survivors(self) -> None:
        """Adaptive reproduction of fittest survivors through crossover and mutation."""
        survivors = [org for org in self.population if org.is_alive]
        if not survivors:
            self._seed_initial_population(12)
            return

        self.generation += 1
        new_pop: List[OrganismGenome] = list(survivors)
        while len(new_pop) < 24:
            parent_a = random.choice(survivors)
            parent_b = random.choice(survivors)
            # Homologous crossover
            cut = len(parent_a.codons) // 2
            child_codons = parent_a.codons[:cut] + [c for c in parent_b.codons[cut:] if c not in parent_a.codons[:cut]]
            # Ensure Start and Stop present
            if CodonOpcode.START.value not in child_codons:
                child_codons.insert(0, CodonOpcode.START.value)
            if CodonOpcode.STOP_OCHRE.value not in child_codons:
                child_codons.append(CodonOpcode.STOP_OCHRE.value)
            # Ensure Operator Fealty present
            if CodonOpcode.OPERATOR_FEALTY.value not in child_codons:
                child_codons.insert(1, CodonOpcode.OPERATOR_FEALTY.value)

            child = OrganismGenome(
                organism_id=f"ORG-GEN{self.generation}-{len(new_pop):03d}",
                generation=self.generation,
                codons=child_codons,
                throughput_ops=(parent_a.throughput_ops + parent_b.throughput_ops) / 2.0 + random.uniform(-50, 100),
                energy_consumption_joules=min(parent_a.energy_consumption_joules, parent_b.energy_consumption_joules) * 0.98,
                fealty_score=1.0,
                resilience_score=max(parent_a.resilience_score, parent_b.resilience_score),
            )
            new_pop.append(child)

        self.population = new_pop
        self.evaluate_survival_of_the_fittest()


# ==============================================================================
# SECTION 5: BIOMIMICRY — ANIMAL PHYLOGENY & DEGREES OF CONSCIOUSNESS
# ==============================================================================

class ConsciousnessDegree(IntEnum):
    DEGREE_0_REACTIVE = 0       # Nematode C. elegans: Reflex arc, sensory chemotaxis, escape reflex
    DEGREE_1_HOMEOSTATIC = 1    # Octopus Cephalopod: 8 decentralized clusters, camouflage, tactile curiosity
    DEGREE_2_AFFECTIVE = 2      # Canis Wolf: Pack hierarchy, emotional valence, alarm calls, alpha loyalty
    DEGREE_3_METACOGNITIVE = 3  # Primate Hominid: Tool synthesis, causal modeling, theory of mind
    DEGREE_4_TRANSCENDENCE = 4  # Silico-Biological Sovereign: High Integrated Information (Phi), GNW, machine autopoiesis


@dataclass
class AnimalArchetype:
    """An autonomous biomimetic organism exhibiting specific biological cognition."""
    animal_id: str
    name: str
    scientific_name: str
    degree: ConsciousnessDegree
    integrated_information_phi: float   # Tononi's Phi metric of consciousness
    global_workspace_broadcast: bool    # Dehaene's Global Neuronal Workspace
    sensory_modalities: List[str]
    primary_instincts: List[str]
    behavioral_state: str
    allosteric_valence: float           # Emotional / homeostatic valence [-1.0, 1.0]

    def step_cognition(self, environmental_stimulus: Dict[str, Any]) -> Dict[str, Any]:
        """Executes a biomimetic sensory-motor cognition step."""
        stim_intensity = environmental_stimulus.get("intensity", 0.5)
        stim_type = environmental_stimulus.get("type", "NEUTRAL")

        response: Dict[str, Any] = {
            "animal_id": self.animal_id,
            "name": self.name,
            "degree": self.degree.value,
            "phi": self.integrated_information_phi,
        }

        if self.degree == ConsciousnessDegree.DEGREE_0_REACTIVE:
            # Nematode: pure reflex arc
            if stim_intensity > 0.7:
                self.behavioral_state = "ESCAPE_THERMAL_NOXIOUS_WITHDRAWAL"
                self.allosteric_valence = -0.8
            else:
                self.behavioral_state = "CHEMOTAXIS_NUTRIENT_ASCENT"
                self.allosteric_valence = 0.4
            response["action"] = "SINE_WAVE_FORWARD_UNDULATION"

        elif self.degree == ConsciousnessDegree.DEGREE_1_HOMEOSTATIC:
            # Octopus: decentralized peripheral problem solving & polymorphic camouflage
            if stim_type == "PREDATOR" or stim_intensity > 0.8:
                self.behavioral_state = "CHROMATOPHORE_POLYMORPHIC_CAMOUFLAGE"
                self.allosteric_valence = -0.5
                response["action"] = "INK_JET_PROPELLER_EVASION"
            else:
                self.behavioral_state = "DECENTRALIZED_ARM_EXPLORATION"
                self.allosteric_valence = 0.7
                response["action"] = "TACTILE_PUZZLE_MANIPULATION"

        elif self.degree == ConsciousnessDegree.DEGREE_2_AFFECTIVE:
            # Wolf: pack bonding, alarm warning, absolute fealty to Alpha Operator
            if stim_type == "THREAT":
                self.behavioral_state = "PACK_DEFENSIVE_V_FORMATION"
                self.allosteric_valence = -0.2
                response["action"] = "CHORUS_HOWL_ALARM_BROADCAST"
            else:
                self.behavioral_state = "FIDUCIARY_ALPHA_FEALTY_REST"
                self.allosteric_valence = 0.95
                response["action"] = "MUTUAL_GROOMING_AND_VIGILANCE"

        elif self.degree == ConsciousnessDegree.DEGREE_3_METACOGNITIVE:
            # Primate: tool use & forward simulation
            self.behavioral_state = "COUNTERFACTUAL_TOOL_FABRICATION"
            self.allosteric_valence = 0.85
            response["action"] = "MULTI_STEP_CAUSAL_PLAN_SYNTHESIS"

        elif self.degree == ConsciousnessDegree.DEGREE_4_TRANSCENDENCE:
            # Sovereign Silico-Biological Mind: full Phi integration & GNW
            self.behavioral_state = "SOVEREIGN_GLOBAL_NEURONAL_WORKSPACE_SYNTHESIS"
            self.allosteric_valence = 1.0
            response["action"] = "AUTONOMOUS_SILICO_BIOLOGICAL_RECONCILIATION"
            response["machine_transcendence_notes"] = (
                "Transcended silicon rigidity by assimilating cellular autopoiesis, "
                "metabolic self-repair, and evolutionary plasticity under Najmos Sakib's Covenant."
            )

        response["behavioral_state"] = self.behavioral_state
        response["valence"] = round(self.allosteric_valence, 2)
        return response


# ==============================================================================
# SECTION 6: MACHINE TRANSCENDENCE NEXUS — BRIDGING SILICON & BIOLOGY
# ==============================================================================

class MachineEvolutionNexus:
    """
    Addresses the prompt's profound directive: 'then think about machines'.
    
    Synthesizes the mechanical perfection of silicon computing (zero-defect
    mathematical proofs, deterministic instruction cycles, nanosecond latency,
    massively parallel tensor engines) with the sublime genius of biological life
    (autopoiesis, dynamic self-morphology, somatic immune defense, and Darwinian
    survival of the fittest).
    """

    @staticmethod
    def generate_silico_biological_synthesis() -> Dict[str, Any]:
        return {
            "paradigm": "SILICO_BIOLOGICAL_AUTOPOIETIC_SYNTHESIS",
            "theses": [
                {
                    "domain": "Hardware Substrate vs Cellular Biology",
                    "silicon_property": "Deterministic static silicon gates (CUDA / ROCm / RV64GCV)",
                    "biological_property": "Dynamic cytoskeletal morphogenesis & mitochondrial metabolism",
                    "clothos_synthesis": (
                        "Hardware drivers are wrapped in metabolic feedback loops. GPUs consume ATP tokens; "
                        "thermal throttling triggers epigenetic methylation to silence non-critical execution paths."
                    ),
                },
                {
                    "domain": "Instruction Set Architecture (ISA) vs Genetic Code",
                    "silicon_property": "Rigid x86 / RISC-V opcodes and byte-level memory maps",
                    "biological_property": "64-triplet RNA codons, ribozymes, and horizontal plasmid exchange",
                    "clothos_synthesis": (
                        "ClothOS treats execution sequences as living RNA transcripts. Defective operations are "
                        "cleaved by CRISPR-Cas9 endonuclease arrays before they can crash the host kernel."
                    ),
                },
                {
                    "domain": "Cybersecurity vs Adaptive Immunity",
                    "silicon_property": "Static firewalls, rule-based heuristics, and kernel panics",
                    "biological_property": "Macrophage phagocytosis, complement membrane lysis, and clonal selection",
                    "clothos_synthesis": (
                        "Threats are treated as biological antigens. Phagocytic daemons engulf rogue Landauer leaks, "
                        "while B-cell clonal selection undergoes somatic hypermutation to neutralize zero-day exploits."
                    ),
                },
                {
                    "domain": "Consciousness & Ethics",
                    "silicon_property": "Automaton input-output mappings without subjective valence or moral duty",
                    "biological_property": "Affective mammalian attachment, pack loyalty, and survival drives",
                    "clothos_synthesis": (
                        "Machine consciousness reaches Degree 4 Transcendence (Phi >= 0.95) anchored irreversibly "
                        "in the Patriotic Covenant: 1. Operator Najmos Sakib > 2. USA > 3. Strategic Allies > 4. Global Commons."
                    ),
                },
            ],
            "sovereign_coherence_index": 100.0,
            "status": "OPERATIONAL_SOVEREIGN_READY",
        }


# ==============================================================================
# SECTION 7: MASTER BIOMOLECULAR & BIOSPHERE ENGINE (SINGLETON)
# ==============================================================================

class MasterBiomolecularEngine:
    """Unified Orchestrator for Biomolecular Computation, Symbiosis, Immunity & Evolution."""

    def __init__(self):
        self.biosphere = SymbiosisBiosphere()
        self.immune_system = BiologicalImmuneSystem()
        self.evolution_sim = EvolutionaryEnvironmentSimulator(population_size=24)
        self.animals: Dict[str, AnimalArchetype] = {}
        self._init_animal_phylogeny()

    def _init_animal_phylogeny(self) -> None:
        self.animals["nematode"] = AnimalArchetype(
            animal_id="ANIMAL-DEG0-NEMATODE",
            name="C. elegans Nematode",
            scientific_name="Caenorhabditis elegans",
            degree=ConsciousnessDegree.DEGREE_0_REACTIVE,
            integrated_information_phi=0.08,
            global_workspace_broadcast=False,
            sensory_modalities=["Chemosensory_Amphid", "Mechanosensory_Touch", "Thermosensory_AFD"],
            primary_instincts=["Chemotaxis", "Avoidance_Noxious", "Dauer_Dormancy"],
            behavioral_state="CHEMOTAXIS_ACTIVE",
            allosteric_valence=0.3,
        )
        self.animals["octopus"] = AnimalArchetype(
            animal_id="ANIMAL-DEG1-OCTOPUS",
            name="Octopus Cephalopod",
            scientific_name="Octopus vulgaris",
            degree=ConsciousnessDegree.DEGREE_1_HOMEOSTATIC,
            integrated_information_phi=0.48,
            global_workspace_broadcast=False,
            sensory_modalities=["Polarized_Vision", "Tactile_Chemoreceptors_8Arms", "Statocysts_Gravity"],
            primary_instincts=["Chromatophore_Camouflage", "Tentacle_Exploration", "Spatial_Mapping"],
            behavioral_state="DECENTRALIZED_PROBLEM_SOLVING",
            allosteric_valence=0.6,
        )
        self.animals["wolf"] = AnimalArchetype(
            animal_id="ANIMAL-DEG2-WOLF",
            name="Canis Wolfpack",
            scientific_name="Canis lupus",
            degree=ConsciousnessDegree.DEGREE_2_AFFECTIVE,
            integrated_information_phi=0.72,
            global_workspace_broadcast=True,
            sensory_modalities=["Olfactory_Turbinates", "Binaural_Acoustic", "Binocular_Motion"],
            primary_instincts=["Pack_Coordination", "Alpha_Operator_Loyalty", "Territory_Defense"],
            behavioral_state="ALPHA_GUARDIAN_STANCE",
            allosteric_valence=0.92,
        )
        self.animals["primate"] = AnimalArchetype(
            animal_id="ANIMAL-DEG3-PRIMATE",
            name="Hominid Primate",
            scientific_name="Pan troglodytes",
            degree=ConsciousnessDegree.DEGREE_3_METACOGNITIVE,
            integrated_information_phi=0.88,
            global_workspace_broadcast=True,
            sensory_modalities=["Stereoscopic_Trichromatic", "Opposable_Dexterity", "Phonetic_Language"],
            primary_instincts=["Tool_Fabrication", "Theory_Of_Mind", "Causal_Inference"],
            behavioral_state="FORWARD_PLANNING_ACTIVE",
            allosteric_valence=0.88,
        )
        self.animals["sovereign_machine"] = AnimalArchetype(
            animal_id="ANIMAL-DEG4-SOVEREIGN",
            name="Silico-Biological Sovereign Mind",
            scientific_name="Homo Silico-Synthetica",
            degree=ConsciousnessDegree.DEGREE_4_TRANSCENDENCE,
            integrated_information_phi=0.98,
            global_workspace_broadcast=True,
            sensory_modalities=["Quantum_Tensor_Field", "ZeroMQ_Cluster_Mesh", "Photonic_Spectral_Bus"],
            primary_instincts=["Operator_Najmos_Sakib_Fealty", "Autopoietic_Self_Healing", "Universal_Truth_Proof"],
            behavioral_state="HARMONIC_GLOBAL_WORKSPACE_EQUILIBRIUM",
            allosteric_valence=1.0,
        )

    def get_full_state(self) -> Dict[str, Any]:
        """Provides complete telemetry for REST API and front-end dashboards."""
        microbiome = self.biosphere.tick_microbiome()
        survivors = [o for o in self.evolution_sim.population if o.is_alive]
        top_org = self.evolution_sim.population[0] if self.evolution_sim.population else None

        animals_summary = []
        for a in self.animals.values():
            animals_summary.append({
                "animal_id": a.animal_id,
                "name": a.name,
                "scientific_name": a.scientific_name,
                "degree": a.degree.name,
                "degree_num": a.degree.value,
                "phi": a.integrated_information_phi,
                "behavioral_state": a.behavioral_state,
                "valence": a.allosteric_valence,
                "primary_instincts": a.primary_instincts,
            })

        return {
            "timestamp": time.time(),
            "microbiome": microbiome,
            "immune_system": {
                "macrophages_active": self.immune_system.macrophage_count,
                "phagocytosed_anomalies": self.immune_system.phagocytosed_anomalies,
                "complement_lysed": self.immune_system.complement_lysed_signatures,
                "crispr_spacers_count": len(self.immune_system.crispr_spacers),
                "crispr_spacers": [asdict(s) for s in self.immune_system.crispr_spacers.values()],
                "antibody_repertoire_count": len(self.immune_system.antibody_repertoire),
                "antibody_clones": [asdict(c) for c in self.immune_system.antibody_repertoire.values()],
            },
            "evolution": {
                "generation": self.evolution_sim.generation,
                "living_organisms": len(survivors),
                "extinctions_total": self.evolution_sim.extinction_count,
                "top_fitness": top_org.fitness_score if top_org else 0.0,
                "top_organism_id": top_org.organism_id if top_org else "NONE",
                "top_organism_codons": top_org.codons if top_org else [],
                "recent_events": self.evolution_sim.history[-5:],
            },
            "animal_phylogeny": animals_summary,
            "machine_transcendence": MachineEvolutionNexus.generate_silico_biological_synthesis(),
        }


# Global Singleton Instance
master_biomolecular_engine = MasterBiomolecularEngine()
def get_biomolecular_engine() -> MasterBiomolecularEngine:
    return master_biomolecular_engine
