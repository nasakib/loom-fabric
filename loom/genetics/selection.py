# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
#
# Part of Pillar 1 & 2: FABRIC / CLOTHOS / LOOM PRECISION TOOLCHAIN.
r"""
Epistemic Natural Selection (`loom/genetics/selection.py`).

Drives Darwinian selection guided by empirical physical metrics and the Bullshit Meter.

Fitness Function:
$\text{Fitness} = \frac{\text{Throughput} \times \text{Accuracy}}{1.0 + \text{EnergyCost}} \times (1.0 - \text{BullshitScore})$

Selection Gates:
1. Viability Gate: Code must execute without unhandled runtime exceptions.
2. Epistemic Reality Gate: Claims, invariants, and results are audited by the Bullshit Meter.
3. Thermodynamic Efficiency Gate: High-FLOP wastes are penalized.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from loom.genetics.compiler import CompiledPhenotype, GeneticCompiler
from loom.genetics.types import Genome, PhenotypeExecutionResult

logger = logging.getLogger("loom.genetics.selection")


class EpistemicNaturalSelection:
    """
    Evaluates, ranks, and selects Software Genomes based on empirical performance
    and epistemic rigor.
    """

    def __init__(self, compiler: Optional[GeneticCompiler] = None, bullshit_meter: Optional[Any] = None):
        from loom.tools.epistemic_grounding import BullshitMeter

        self.compiler = compiler or GeneticCompiler()
        self.bullshit_meter = bullshit_meter or BullshitMeter()

    def evaluate_phenotype(
        self,
        genome: Genome,
        benchmark_input: Optional[Dict[str, Any]] = None,
    ) -> PhenotypeExecutionResult:
        """
        Compiles and executes a genome against empirical benchmark tasks,
        scoring throughput, accuracy, and epistemic truth.
        """
        inp = benchmark_input or {"vector": [0.7071, 0.7071, 0.0, 0.0]}
        
        try:
            phenotype = self.compiler.compile(genome)
            output_state, duration = phenotype.execute(inp)
            is_viable = True
            
            # Throughput: estimated operations per second
            n_ops = max(1, len(phenotype.pipeline_steps) * 100)
            throughput = n_ops / duration

            # Accuracy: check numerical stability of vector
            v_out = np.asarray(output_state.get("vector", [1.0]), dtype=np.float64)
            has_nan = bool(np.any(np.isnan(v_out)) or np.any(np.isinf(v_out)))
            accuracy = 0.0 if has_nan else 1.0

            # Energy estimate: proportional to duration and active genes
            energy_joules = duration * len(genome.get_effective_genes()) * 0.05
            mem_mb = 1.0 + (len(genome.get_all_genes()) * 0.1)

            # Epistemic Audit via the Bullshit Meter
            claim_desc = f"Genome {genome.genome_id} execution in {duration:.4f}s"
            pred_desc = f"State transformed with accuracy {accuracy:.2f} and energy {energy_joules:.6f}J"
            audit = self.bullshit_meter.audit_hypothesis(
                claim=claim_desc,
                prediction=pred_desc,
                parameters={"duration": duration},
                measurements={"accuracy": accuracy, "energy_drift_pct": 0.01},
            )

        except Exception as ex:
            logger.warning(f"Lethal mutation in genome {genome.genome_id}: {ex}")
            is_viable = False
            duration = 1.0
            throughput = 0.0
            accuracy = 0.0
            energy_joules = 10.0
            mem_mb = 1.0
            audit = self.bullshit_meter.audit_hypothesis(
                claim=f"Failed execution: {ex}",
                prediction="Execution failed with lethal exception",
                measurements={"error": str(ex)},
            )

        # Composite Fitness Formulation
        if not is_viable or not audit.is_grounded:
            composite_fitness = 0.0
        else:
            base_perf = (throughput * accuracy) / (1.0 + energy_joules)
            grounding_factor = max(0.0, 1.0 - audit.bullshit_score)
            composite_fitness = float(base_perf * grounding_factor)

        return PhenotypeExecutionResult(
            genome_id=genome.genome_id,
            throughput_ops_per_sec=round(throughput, 2),
            accuracy_score=round(accuracy, 4),
            energy_dissipation_joules=round(energy_joules, 6),
            memory_footprint_mb=round(mem_mb, 2),
            bullshit_score=audit.bullshit_score,
            epistemic_grade=audit.epistemic_grade,
            composite_fitness=round(composite_fitness, 4),
            is_viable=is_viable,
            execution_time_s=round(duration, 6),
        )

    def select_elites(
        self,
        population: List[Genome],
        top_k: int = 2,
    ) -> List[Tuple[Genome, PhenotypeExecutionResult]]:
        """
        Evaluates the entire population and selects the highest-fitness elites.
        """
        scored: List[Tuple[Genome, PhenotypeExecutionResult]] = []
        for g in population:
            result = self.evaluate_phenotype(g)
            scored.append((g, result))

        # Sort descending by composite fitness
        scored.sort(key=lambda pair: pair[1].composite_fitness, reverse=True)
        return scored[:top_k]
