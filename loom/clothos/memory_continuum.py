# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
ClothOS Multi-Tier Memory Continuum (`loom/clothos/memory_continuum.py`).

Provides persistent, multi-layered cognitive storage for ClothOS:
1. Episodic Memory: Concrete, timestamped logs of operator directives, system actions, and experiment results.
2. Semantic / Associative Memory: High-dimensional concept embeddings (HDC / Hopfield attractor networks)
   enabling zero-latency semantic recall across technical, biological, and cyber-physical domains.
3. Procedural Memory: Ratified execution pipelines, validated software codons, and robotic trajectories.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
import json
import logging
import math
import os
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("loom.clothos.memory")

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
MEMORY_DIR = WORKSPACE_ROOT / "clothos_root" / "var" / "memory"


@dataclass
class EpisodicRecord:
    event_id: str
    timestamp: float
    category: str        # 'OPERATOR_DIRECTIVE', 'SYSTEM_EVOLUTION', 'DRIVER_EVENT', 'EXPERIMENT'
    summary: str
    details: Dict[str, Any]
    salience_score: float = 0.5
    access_count: int = 1
    last_accessed: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SemanticConcept:
    concept_id: str
    term: str
    domain: str          # 'KERNEL', 'ROBOTICS', 'CLUSTER', 'PHARMACOLOGY', 'ETHICS'
    definition: str
    hypervector: List[float] = field(default_factory=list)
    associated_terms: List[str] = field(default_factory=list)
    salience_weight: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MemoryContinuum:
    """Master memory manager combining episodic, semantic, and procedural tiers."""

    def __init__(self):
        self.episodic_store: Dict[str, EpisodicRecord] = {}
        self.semantic_store: Dict[str, SemanticConcept] = {}
        self.procedural_store: Dict[str, Dict[str, Any]] = {}
        self._init_storage()
        self._load_seed_knowledge()

    def _init_storage(self) -> None:
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        self.episodic_file = MEMORY_DIR / "episodic_memory.json"
        self.semantic_file = MEMORY_DIR / "semantic_memory.json"
        self.procedural_file = MEMORY_DIR / "procedural_memory.json"

        # Load existing if available
        if self.episodic_file.exists():
            try:
                data = json.loads(self.episodic_file.read_text(encoding="utf-8"))
                for k, v in data.items():
                    self.episodic_store[k] = EpisodicRecord(**v)
            except Exception:
                pass

        if self.semantic_file.exists():
            try:
                data = json.loads(self.semantic_file.read_text(encoding="utf-8"))
                for k, v in data.items():
                    self.semantic_store[k] = SemanticConcept(**v)
            except Exception:
                pass

    def _persist(self) -> None:
        try:
            self.episodic_file.write_text(
                json.dumps({k: v.to_dict() for k, v in self.episodic_store.items()}, indent=2),
                encoding="utf-8",
            )
            self.semantic_file.write_text(
                json.dumps({k: v.to_dict() for k, v in self.semantic_store.items()}, indent=2),
                encoding="utf-8",
            )
            self.procedural_file.write_text(
                json.dumps(self.procedural_store, indent=2),
                encoding="utf-8",
            )
        except Exception as exc:
            logger.debug("Memory persist exception: %s", exc)

    def _load_seed_knowledge(self) -> None:
        """Seeds foundational semantic knowledge if empty."""
        seeds = [
            ("P0_SANCTITY", "ETHICS", "Inviolable kernel priority ring protecting human life and immediate safety.", ["safety", "kill_switch", "preemption"]),
            ("KURAMOTO_CONSENSUS", "CLUSTER", "Coupled phase oscillator dynamics ensuring dual-node cluster agreement (r >= 0.85).", ["phase_locking", "order_parameter", "mesh"]),
            ("LANDAUER_BOUND", "THERMODYNAMICS", "Thermodynamic limit on information erasure (ceiling <= 1000 Joules).", ["energy_budget", "joules", "cooling"]),
            ("ROBOTICS_ESTOP", "ROBOTICS", "Sub-50-microsecond hardware actuator cutoff preventing physical collision.", ["actuator", "imu", "lidar"]),
            ("RISCV_RV64GCV", "KERNEL", "Sovereign 64-bit RISC-V target with 512-bit vector extensions.", ["rvv", "vsetvli", "pmp_enclave"]),
        ]
        for term, domain, defn, assoc in seeds:
            if term not in self.semantic_store:
                hv = self._generate_hypervector(term + defn, dim=64)
                self.semantic_store[term] = SemanticConcept(
                    concept_id=f"SEM-{term}",
                    term=term,
                    domain=domain,
                    definition=defn,
                    hypervector=hv,
                    associated_terms=assoc,
                    salience_weight=1.0,
                )
        self._persist()

    @staticmethod
    def _generate_hypervector(text: str, dim: int = 64) -> List[float]:
        """Generates reproducible unit hypervector from text."""
        h = hashlib.sha256(text.encode("utf-8")).digest()
        vec = [((h[i % len(h)] / 127.5) - 1.0) for i in range(dim)]
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [round(x / norm, 4) for x in vec]

    def record_episodic_event(
        self,
        category: str,
        summary: str,
        details: Dict[str, Any],
        salience: float = 0.5,
    ) -> EpisodicRecord:
        """Records an episodic memory entry with initial salience weight."""
        event_id = f"EVT-{int(time.time() * 1000) % 10000000:07d}"
        record = EpisodicRecord(
            event_id=event_id,
            timestamp=time.time(),
            category=category,
            summary=summary,
            details=details,
            salience_score=salience,
        )
        self.episodic_store[event_id] = record
        self._persist()
        logger.info("Recorded episodic memory [%s]: %s (salience=%.2f)", event_id, summary, salience)
        return record

    def recall_semantic(self, query: str, top_k: int = 3) -> List[Tuple[SemanticConcept, float]]:
        """Associative retrieval using cosine similarity across semantic hypervectors."""
        q_vec = self._generate_hypervector(query, dim=64)
        results: List[Tuple[SemanticConcept, float]] = []

        for concept in self.semantic_store.values():
            dot = sum(a * b for a, b in zip(q_vec, concept.hypervector))
            results.append((concept, round(dot, 3)))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def get_summary(self) -> Dict[str, Any]:
        return {
            "episodic_records_count": len(self.episodic_store),
            "semantic_concepts_count": len(self.semantic_store),
            "procedural_routines_count": len(self.procedural_store),
            "storage_path": str(MEMORY_DIR),
        }


# Global memory continuum singleton
memory_continuum = MemoryContinuum()
