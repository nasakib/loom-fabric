"""
Comprehensive Unit Tests for Software Genetics Paradigm.

Tests:
1. Codon, Gene, Chromosome, and Genome instantiation & hashing
2. GeneticCompiler transcription and phenotype execution
3. SyntacticRecombinationEngine homologous crossover & mutation
4. Epigenetic adaptation under resource pressure (VRAM/thermal stress)
5. CRISPR immune memory: spacer acquisition and Cas cleavage of defective genes
6. SoftwareGeneticsSuite generational evolutionary cycle
"""

import numpy as np
import pytest

from loom.genetics.types import (
    Chromosome,
    Codon,
    EpigeneticMarker,
    Gene,
    GeneFunctionType,
    Genome,
    Plasmid,
)
from loom.genetics.compiler import GeneticCompiler
from loom.genetics.recombination import SyntacticRecombinationEngine
from loom.genetics.selection import EpistemicNaturalSelection
from loom.genetics.crispr import CrisprImmuneMemory
from loom.tools.genetics_tool import SoftwareGeneticsSuite


class TestSoftwareGenetics:
    def test_genome_creation_and_hashing(self):
        gene = Gene(
            gene_id="GENE_01",
            name="VectorScaling",
            function_type=GeneFunctionType.VECTOR_TRANSFORM,
            codons=[Codon(opcode="VECTOR_SCALE_NORM", input_type="float_vector", output_type="float_vector")],
            is_essential=True,
            homology_group="transform",
        )
        chrom = Chromosome(chromosome_id="CHROM_01", subsystem="core", genes=[gene])
        genome = Genome(genome_id="GENOME_TEST_01", generation=0, chromosomes=[chrom])

        fingerprint = genome.compute_genomic_fingerprint()
        assert len(fingerprint) == 64
        assert len(genome.get_all_genes()) == 1
        assert len(genome.get_effective_genes()) == 1

    def test_genetic_compiler_phenotype_execution(self):
        suite = SoftwareGeneticsSuite()
        seed = suite.create_seed_genome("GENOME_SEED_TEST")

        compiler = GeneticCompiler()
        phenotype = compiler.compile(seed)
        assert len(phenotype.pipeline_steps) == 3

        initial_state = {"vector": [1.0, 0.0, 0.0, 0.0]}
        output_state, duration = phenotype.execute(initial_state)

        assert "free_energy" in output_state
        assert "hopfield_energy" in output_state
        assert duration > 0.0

    def test_homologous_crossover_and_mutation(self):
        suite = SoftwareGeneticsSuite()
        g1 = suite.create_seed_genome("GENOME_P1")
        g2 = suite.create_seed_genome("GENOME_P2")

        recomb = SyntacticRecombinationEngine(mutation_rate=0.5, rng_seed=42)
        child = recomb.crossover(g1, g2)
        assert child.generation == 1
        assert len(child.chromosomes) == 1

        mutant = recomb.mutate(child)
        assert mutant.genome_id == child.genome_id

    def test_epigenetic_adaptation(self):
        suite = SoftwareGeneticsSuite()
        genome = suite.create_seed_genome("GENOME_EPI_TEST")
        recomb = SyntacticRecombinationEngine()

        # Under severe VRAM and thermal stress
        stress = {"vram_pressure": 0.96, "thermal_throttling": 0.90}
        adapted = recomb.adapt_epigenetics(genome, stress)

        # Essential genes should remain unsilenced
        for g in adapted.get_all_genes():
            marker = adapted.epigenome.get(g.gene_id)
            assert marker is not None
            if g.is_essential:
                assert marker.is_silenced is False
            else:
                assert marker.is_silenced is True

    def test_crispr_immune_defense(self, tmp_path):
        crispr = CrisprImmuneMemory(storage_path=tmp_path / "crispr_test.json")

        bad_gene = Gene(
            gene_id="GENE_LETHAL_01",
            name="InfiniteLoopBug",
            function_type=GeneFunctionType.VECTOR_TRANSFORM,
            codons=[],
            is_essential=False,
        )

        # Acquire immune spacer
        spacer = crispr.record_immune_spacer(bad_gene, "Causes zero-division and stall")
        assert crispr.is_defective(bad_gene) is True

        # Test Cas cleavage
        chrom = Chromosome(chromosome_id="CHROM_DIRTY", subsystem="test", genes=[bad_gene])
        dirty_genome = Genome(genome_id="GENOME_DIRTY", generation=1, chromosomes=[chrom])

        clean_genome, cleaved_count = crispr.cas_cleave_defects(dirty_genome)
        assert cleaved_count == 1
        assert len(clean_genome.get_all_genes()) == 0

    def test_software_genetics_evolutionary_cycle(self):
        suite = SoftwareGeneticsSuite()
        suite.create_seed_genome()

        cycle_result = suite.evolve_cycle(population_size=3)
        assert cycle_result["generation"] == 1
        assert cycle_result["population_size"] == 3
        assert cycle_result["best_fitness"] > 0.0
        assert cycle_result["epistemic_grade"] in ["GROUNDED_FACT", "VALID_CONJECTURE"]
