# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
#
# Part of Pillar 1 & 2: FABRIC / CLOTHOS / LOOM PRECISION TOOLCHAIN.
r"""
CRISPR Immune Memory & Invariant Lock (`loom/genetics/crispr.py`).

Biological & Computational Mechanism:
1. Spacers: Cryptographic signatures of refuted mutations, ungrounded claims, and lethal exceptions.
2. Cas Cleavage: Scans incoming genomes and candidate plasmids; cuts and ablates any gene matching
   a known defective/bullshit spacer.
3. Invariant Ratcheting: Permanently cements verified theorems and high-fitness operational blocks
   into the genome as non-mutable "Hox genes".
"""

from __future__ import annotations

import copy
import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, Field

from loom.genetics.types import Gene, Genome

logger = logging.getLogger("loom.genetics.crispr")


class CrisprSpacer(BaseModel, frozen=True):
    """Immune spacer recording a lethal or ungrounded genetic sequence."""
    spacer_hash: str
    gene_name: str
    rejection_reason: str
    timestamp: float


class CrisprImmuneMemory:
    """
    CRISPR-Cas Immune Defense for Software Genomes.
    Maintains non-volatile memory of flawed mutations and protects genomic integrity.
    """

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path(__file__).resolve().parents[2] / "vault" / "crispr_spacers.json"
        self.spacers: Dict[str, CrisprSpacer] = {}
        self._load()

    def _load(self) -> None:
        if self.storage_path.exists():
            try:
                data = json.loads(self.storage_path.read_text(encoding="utf-8"))
                for s in data:
                    spacer = CrisprSpacer(**s)
                    self.spacers[spacer.spacer_hash] = spacer
            except Exception as ex:
                logger.warning(f"Failed to load CRISPR spacers: {ex}")

    def _save(self) -> None:
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            serializable = [s.model_dump() for s in self.spacers.values()]
            self.storage_path.write_text(json.dumps(serializable, indent=2), encoding="utf-8")
        except Exception as ex:
            logger.warning(f"Failed to save CRISPR spacers: {ex}")

    def record_immune_spacer(self, gene: Gene, reason: str) -> CrisprSpacer:
        """Acquires a new spacer sequence from a refuted or lethal gene."""
        h = gene.compute_hash()
        import time
        spacer = CrisprSpacer(
            spacer_hash=h,
            gene_name=gene.name,
            rejection_reason=reason,
            timestamp=time.time(),
        )
        self.spacers[h] = spacer
        self._save()
        logger.info(f"Acquired CRISPR spacer for defective gene '{gene.name}' [{h}]")
        return spacer

    def is_defective(self, gene: Gene) -> bool:
        """Checks if a gene matches any known defective spacer in immune memory."""
        return gene.compute_hash() in self.spacers

    def cas_cleave_defects(self, genome: Genome) -> Tuple[Genome, int]:
        """
        Scans a candidate genome and cleaves (removes) any non-essential genes
        matching known defective spacers.
        """
        cleaved_genome = copy.deepcopy(genome)
        cleaved_count = 0

        for chrom in cleaved_genome.chromosomes:
            clean_genes: List[Gene] = []
            for gene in chrom.genes:
                if self.is_defective(gene) and not gene.is_essential:
                    logger.warning(f"CRISPR Cas cleavage: Gene '{gene.name}' ablated (known defect).")
                    cleaved_count += 1
                else:
                    clean_genes.append(gene)
            chrom.genes = clean_genes

        return cleaved_genome, cleaved_count

    def lock_as_essential_hox_gene(self, genome: Genome, gene_id: str) -> bool:
        """
        Ratchets a verified invariant gene into an immutable 'Hox gene'.
        It can no longer be mutated, cleaved, or silenced.
        """
        for g in genome.get_all_genes():
            if g.gene_id == gene_id:
                g.is_essential = True
                logger.info(f"Ratcheted gene '{g.name}' [{gene_id}] into immutable Hox gene.")
                return True
        return False
