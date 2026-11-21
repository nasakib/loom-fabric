# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
#
# Part of Pillar 1 & 2: FABRIC / CLOTHOS / LOOM PRECISION TOOLCHAIN.
r"""
Software Genetics Core Types (`loom/genetics/types.py`).

Biological & Computational Formalism:
1. Codon: Atomic instruction triplet representing an operator, operand type, and target register/variable.
2. Gene: A contiguous sequence of codons encoding a functional computational module (e.g. vector projection, numerical integration, attention routing).
3. Chromosome: Contiguous collection of genes governing a specific execution subsystem (e.g. Memory, Compute, Security, Communication).
4. EpigeneticProfile: Expression masks (methylation/silencing vs acetylation/activation) modulating gene activity in response to physical resource pressure.
5. Plasmid: Mobile autonomous genetic element enabling Horizontal Gene Transfer (HGT) across distributed cluster nodes without host downtime.
6. Phenotype: The compiled, executing software organism whose fitness is evaluated in the physical compute environment.
"""

from __future__ import annotations

import enum
import hashlib
import time
from typing import Any, Callable, Dict, List, Optional, Sequence, Union
import numpy as np
from pydantic import BaseModel, Field


class GeneFunctionType(str, enum.Enum):
    INFERENCE_OPERATOR = "inference_operator"
    MEMORY_RETRIEVAL = "memory_retrieval"
    VECTOR_TRANSFORM = "vector_transform"
    INTEGRAL_CALCULUS = "integral_calculus"
    CONSENSUS_SYNC = "consensus_sync"
    SECURITY_ENCLAVE = "security_enclave"


class Codon(BaseModel, frozen=True):
    """Atomic operational triplet in a software gene."""
    opcode: str               # e.g., 'DOT_PRODUCT', 'LSE_ATTENTION', 'EULER_STEP', 'FISHER_INV'
    input_type: str           # e.g., 'float_vector', 'matrix_2d', 'probability_simplex'
    output_type: str          # e.g., 'scalar', 'float_vector', 'matrix_2d'
    parameters: Dict[str, float] = Field(default_factory=dict)


class Gene(BaseModel):
    """Functional computational unit within a software chromosome."""
    gene_id: str
    name: str
    function_type: GeneFunctionType
    codons: List[Codon]
    is_essential: bool = False       # Essential "Hox genes" cannot be ablated or disabled
    homology_group: str = "general"  # Homologous locus for type-preserving crossover

    def compute_hash(self) -> str:
        raw = f"{self.gene_id}:{self.name}:{self.function_type.value}:{[c.model_dump() for c in self.codons]}".encode()
        return hashlib.sha256(raw).hexdigest()[:16]


class EpigeneticMarker(BaseModel):
    """Epigenetic expression modifier controlling gene transcription."""
    gene_id: str
    is_silenced: bool = False        # Methylation equivalent: completely turns off execution branch
    expression_weight: float = 1.0   # Acetylation equivalent: priority multiplier [0.0, 2.0]
    precision_mode: str = "fp32"     # 'fp64', 'fp32', 'fp16', 'int8' depending on compute stress


class Chromosome(BaseModel):
    """Subsystem chromosome containing an ordered sequence of genes."""
    chromosome_id: str
    subsystem: str
    genes: List[Gene]

    def get_gene(self, gene_id: str) -> Optional[Gene]:
        for g in self.genes:
            if g.gene_id == gene_id:
                return g
        return None


class Genome(BaseModel):
    """Complete genetic blueprint of a software organism."""
    genome_id: str
    generation: int
    chromosomes: List[Chromosome]
    epigenome: Dict[str, EpigeneticMarker] = Field(default_factory=dict)
    parent_ids: List[str] = Field(default_factory=list)
    created_at: float = Field(default_factory=time.time)

    def get_all_genes(self) -> List[Gene]:
        genes = []
        for c in self.chromosomes:
            genes.extend(c.genes)
        return genes

    def get_effective_genes(self) -> List[Gene]:
        """Returns only genes that are not epigenetically silenced."""
        active = []
        for g in self.get_all_genes():
            marker = self.epigenome.get(g.gene_id)
            if marker is None or not marker.is_silenced:
                active.append(g)
        return active

    def compute_genomic_fingerprint(self) -> str:
        gene_hashes = [g.compute_hash() for g in self.get_all_genes()]
        raw = f"{self.genome_id}:{self.generation}:{':'.join(sorted(gene_hashes))}".encode()
        return hashlib.sha256(raw).hexdigest()


class Plasmid(BaseModel, frozen=True):
    """
    Mobile genetic element for Horizontal Gene Transfer (HGT) across nodes.
    Transfers specialized capability (e.g. OpenCL kernel or mathematical operator)
    without rebooting the target system.
    """
    plasmid_id: str
    origin_node: str
    target_capability: str
    payload_genes: List[Gene]
    replication_origin_valid: bool = True
    sha256_seal: str


class PhenotypeExecutionResult(BaseModel):
    """Empirical fitness metrics of a compiled running genome."""
    genome_id: str
    throughput_ops_per_sec: float
    accuracy_score: float
    energy_dissipation_joules: float
    memory_footprint_mb: float
    bullshit_score: float
    epistemic_grade: str
    composite_fitness: float
    is_viable: bool
    execution_time_s: float
