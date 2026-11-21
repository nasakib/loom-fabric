# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
#
# Part of Pillar 1 & 2: FABRIC / CLOTHOS / LOOM PRECISION TOOLCHAIN.
"""
Software Genetics Paradigm Exports.
"""

from loom.genetics.types import (
    Codon,
    Gene,
    GeneFunctionType,
    Chromosome,
    Genome,
    EpigeneticMarker,
    Plasmid,
    PhenotypeExecutionResult,
)
from loom.genetics.compiler import GeneticCompiler, CompiledPhenotype
from loom.genetics.recombination import SyntacticRecombinationEngine
from loom.genetics.selection import EpistemicNaturalSelection
from loom.genetics.crispr import CrisprImmuneMemory, CrisprSpacer

__all__ = [
    "Codon",
    "Gene",
    "GeneFunctionType",
    "Chromosome",
    "Genome",
    "EpigeneticMarker",
    "Plasmid",
    "PhenotypeExecutionResult",
    "GeneticCompiler",
    "CompiledPhenotype",
    "SyntacticRecombinationEngine",
    "EpistemicNaturalSelection",
    "CrisprImmuneMemory",
    "CrisprSpacer",
]
