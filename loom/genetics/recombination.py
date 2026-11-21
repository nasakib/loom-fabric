# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
#
# Part of Pillar 1 & 2: FABRIC / CLOTHOS / LOOM PRECISION TOOLCHAIN.
r"""
Syntactic Recombination & Horizontal Gene Transfer Engine (`loom/genetics/recombination.py`).

Biological & Computational Mechanics:
1. Homologous Crossover: Exchanges compatible gene cassettes across matching homology groups
   without breaking typing contracts or syntax.
2. Manifold-Bounded Point Mutation: Mutates hyperparameters within stable mathematical attractors.
3. Horizontal Gene Transfer (HGT): Injects mobile Plasmids into target genomes across distributed nodes.
4. Epigenetic Plasticity: Toggles methylation/silencing masks to adapt to physical hardware stress.
"""

from __future__ import annotations

import copy
import hashlib
import logging
import random
import time
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from loom.genetics.types import (
    Chromosome,
    Codon,
    EpigeneticMarker,
    Gene,
    Genome,
    Plasmid,
)

logger = logging.getLogger("loom.genetics.recombination")


class SyntacticRecombinationEngine:
    """
    Drives genetic variation through type-preserving homologous crossover,
    bounded mutations, and distributed plasmid transfer.
    """

    def __init__(self, mutation_rate: float = 0.05, rng_seed: Optional[int] = None):
        self.mutation_rate = mutation_rate
        self.rng = random.Random(rng_seed)

    def crossover(self, parent_a: Genome, parent_b: Genome) -> Genome:
        """
        Performs homologous crossover between two parent genomes.
        Swaps compatible genes belonging to the same homology group.
        """
        child_generation = max(parent_a.generation, parent_b.generation) + 1
        child_chromosomes: List[Chromosome] = []

        # Map genes from parent_b by homology group
        b_homology_map: Dict[str, List[Gene]] = {}
        for gene in parent_b.get_all_genes():
            b_homology_map.setdefault(gene.homology_group, []).append(gene)

        for chrom_a in parent_a.chromosomes:
            child_genes: List[Gene] = []
            for gene_a in chrom_a.genes:
                # Essential genes are conserved without blind replacement
                if gene_a.is_essential or self.rng.random() > 0.5:
                    child_genes.append(copy.deepcopy(gene_a))
                else:
                    # Look for homologous partner in parent_b
                    candidates = b_homology_map.get(gene_a.homology_group, [])
                    if candidates:
                        chosen = copy.deepcopy(self.rng.choice(candidates))
                        child_genes.append(chosen)
                    else:
                        child_genes.append(copy.deepcopy(gene_a))

            child_chromosomes.append(Chromosome(
                chromosome_id=f"CHROM_{chrom_a.subsystem}_G{child_generation}",
                subsystem=chrom_a.subsystem,
                genes=child_genes,
            ))

        # Recombine epigenetic profiles
        merged_epigenome: Dict[str, EpigeneticMarker] = {}
        for gid, marker in parent_a.epigenome.items():
            merged_epigenome[gid] = copy.deepcopy(marker)
        for gid, marker in parent_b.epigenome.items():
            if gid not in merged_epigenome or self.rng.random() < 0.5:
                merged_epigenome[gid] = copy.deepcopy(marker)

        cid = f"GENOME_REC_{child_generation}_{self.rng.randint(1000, 9999)}"
        return Genome(
            genome_id=cid,
            generation=child_generation,
            chromosomes=child_chromosomes,
            epigenome=merged_epigenome,
            parent_ids=[parent_a.genome_id, parent_b.genome_id],
        )

    def mutate(self, genome: Genome) -> Genome:
        r"""
        Applies conservative, manifold-bounded point mutations to non-essential genes.
        Mutates parameter continuous values by $\pm 10\%$ to explore adjacent state spaces.
        """
        mutant = copy.deepcopy(genome)
        for gene in mutant.get_all_genes():
            if gene.is_essential:
                continue
            for codon in gene.codons:
                if self.rng.random() < self.mutation_rate:
                    # Mutate continuous hyperparameters within bounded manifold
                    new_params = dict(codon.parameters)
                    for k, v in new_params.items():
                        delta = (self.rng.random() - 0.5) * 0.20 * v # +/- 10%
                        new_params[k] = round(v + delta, 6)
                    # Replace codon with mutated parameters
                    # (Codon is frozen, so replace in list)
                    idx = gene.codons.index(codon)
                    gene.codons[idx] = Codon(
                        opcode=codon.opcode,
                        input_type=codon.input_type,
                        output_type=codon.output_type,
                        parameters=new_params,
                    )

        return mutant

    def inject_plasmid(self, genome: Genome, plasmid: Plasmid) -> Genome:
        """
        Horizontal Gene Transfer (HGT): Injects mobile plasmid genes
        into the appropriate chromosome of the host genome.
        """
        host = copy.deepcopy(genome)
        if not plasmid.replication_origin_valid:
            logger.warning(f"Plasmid {plasmid.plasmid_id} rejected: Invalid replication origin.")
            return host

        # Find or create chromosome for injected payload
        target_chrom = host.chromosomes[0] if host.chromosomes else Chromosome(
            chromosome_id="CHROM_PLASMID_ACQUIRED",
            subsystem="horizontal_transfer",
            genes=[],
        )
        if not host.chromosomes:
            host.chromosomes.append(target_chrom)

        for p_gene in plasmid.payload_genes:
            # Check for existing duplicate
            existing = [g.gene_id for g in target_chrom.genes]
            if p_gene.gene_id not in existing:
                target_chrom.genes.append(copy.deepcopy(p_gene))
                # Set active expression by default
                host.epigenome[p_gene.gene_id] = EpigeneticMarker(
                    gene_id=p_gene.gene_id,
                    is_silenced=False,
                    expression_weight=1.0,
                    precision_mode="fp32",
                )

        return host

    def adapt_epigenetics(self, genome: Genome, resource_stress: Dict[str, float]) -> Genome:
        """
        Modulates gene expression in response to environmental/hardware pressure.
        If VRAM or thermal stress is high, silences expensive operators and downscales precision.
        """
        adapted = copy.deepcopy(genome)
        vram_stress = resource_stress.get("vram_pressure", 0.0) # [0.0, 1.0]
        thermal_stress = resource_stress.get("thermal_throttling", 0.0) # [0.0, 1.0]

        for gene in adapted.get_all_genes():
            marker = adapted.epigenome.get(gene.gene_id)
            if marker is None:
                marker = EpigeneticMarker(gene_id=gene.gene_id)
                adapted.epigenome[gene.gene_id] = marker

            if (vram_stress > 0.95 or thermal_stress > 0.95) and not gene.is_essential:
                # Extreme stress: Methylate / Silence non-critical gene
                marker.is_silenced = True
            elif (vram_stress > 0.8 or thermal_stress > 0.8) and not gene.is_essential:
                # Moderate stress: Downscale precision and throttle weight
                marker.precision_mode = "fp16"
                marker.expression_weight = 0.5
                marker.is_silenced = False
            else:
                # Optimal conditions: Unsilence and restore full precision
                marker.is_silenced = False
                marker.precision_mode = "fp32"
                marker.expression_weight = 1.0

        return adapted
