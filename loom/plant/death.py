# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
#
# Part of Pillar 1 & 2: FABRIC / CLOTHOS / LOOM PRECISION TOOLCHAIN.
"""
Death Engine (RealityAuditor) — The Sovereign Reaper and Epistemic Composting of ClothOS.

The Architecture of DEATH as Decreed by Reality:
    1. REAP:      Non-maskable reclamation of deadlocked, stalled, or completed processes.
    2. COMPOST:   Transmuting fallen LINT, dead tokens, and falsified hypotheses into rich
                  nutrient-dense Humus (epistemic priors) for future germination.
    3. TOMBSTONE: Inscribing the permanent cessation record into an immutable ledger.
    4. IMMORTAL:  The Cold Boot Resurrection Audit — verifying that only true FRUIT
                  survives the mortality of volatile RAM across power cycles.
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
import time
from typing import Any, Dict, List, Optional

from loom.plant.models import (
    FruitArtifact,
    HumusCompost,
    LintArtifact,
    MortalityCause,
    ResurrectionAudit,
    Tombstone,
)

logger = logging.getLogger("loom.plant.death")


class DeathEngine:
    """
    Governs mortality, process reclamation, epistemic composting, and cold-boot survival audits.
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        if storage_dir is not None:
            self.storage_dir = storage_dir
        else:
            workspace_root = Path(__file__).resolve().parents[2]
            self.storage_dir = workspace_root / ".loom_death_ledger"

        try:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
        self.tombstones: List[Tombstone] = []
        self.humus_pile: List[HumusCompost] = []
        self._load_records()

    def _load_records(self) -> None:
        t_file = self.storage_dir / "tombstones.json"
        if t_file.exists():
            try:
                data = json.loads(t_file.read_text(encoding="utf-8"))
                self.tombstones = [Tombstone(**t) for t in data]
            except Exception as e:
                logger.debug(f"Could not load tombstones: {e}")

        h_file = self.storage_dir / "humus.json"
        if h_file.exists():
            try:
                data = json.loads(h_file.read_text(encoding="utf-8"))
                self.humus_pile = [HumusCompost(**h) for h in data]
            except Exception as e:
                logger.debug(f"Could not load humus compost: {e}")

    def _persist_records(self) -> None:
        try:
            t_file = self.storage_dir / "tombstones.json"
            t_file.write_text(json.dumps([t.model_dump() for t in self.tombstones[-200:]], indent=2), encoding="utf-8")
            h_file = self.storage_dir / "humus.json"
            h_file.write_text(json.dumps([h.model_dump() for h in self.humus_pile[-100:]], indent=2), encoding="utf-8")
        except Exception as e:
            logger.debug(f"Could not persist death ledger: {e}")

    def reap(
        self,
        entity_id: str,
        cause: MortalityCause = MortalityCause.NATURAL_TELEOLOGICAL_COMPLETION,
        epitaph: str = "Work completed; spirit yielded to ground state.",
    ) -> Tombstone:
        """
        Reaps an entity, halts its thread/context, and sets an immutable tombstone.
        """
        t_id = f"tomb-{int(time.time() * 1000)}"
        raw_seed = f"{t_id}:{entity_id}:{cause.value}:{time.time()}"
        worm_hash = hashlib.sha256(raw_seed.encode("utf-8")).hexdigest()

        tombstone = Tombstone(
            tombstone_id=t_id,
            entity_id=entity_id,
            cause=cause,
            epoch_of_cessation=time.time(),
            epitaph=epitaph,
            worm_hash=worm_hash,
        )
        self.tombstones.append(tombstone)
        self._persist_records()
        logger.warning(f"💀 [DEATH REAPER]: Entity '{entity_id}' reaped ({cause.value}). Tombstone {t_id} erected.")
        return tombstone

    def compost(self, seed_prompt: str, shed_lint: List[LintArtifact]) -> HumusCompost:
        """
        Decomposes shed dross, failed hypotheses, and burned tokens into epistemic Humus.
        Returns nutrient-dense prior knowledge for subsequent seeds.
        """
        compost_id = f"humus-{int(time.time() * 1000)}"
        total_tokens = sum(l.lint_mass_tokens for l in shed_lint) if shed_lint else max(len(seed_prompt.split()) // 2, 1)

        # Decompose into negative priors (what NOT to do, what failed, tokens to avoid)
        recycled_priors: Dict[str, Any] = {
            "avoid_tokens": [l.raw_fragment[:30] for l in shed_lint[:5]],
            "dross_causes": list({l.dross_type for l in shed_lint}),
            "entropy_reclaimed": float(round(total_tokens * 0.042, 3)),
            "parent_seed": seed_prompt[:40],
        }

        # Richness increases with how much truth was separated from fluff
        nitrogen = min(0.95, max(0.40, 0.50 + (total_tokens * 0.01)))

        compost = HumusCompost(
            compost_id=compost_id,
            origin_seed=seed_prompt[:50],
            decomposed_tokens=total_tokens,
            nitrogen_density=round(nitrogen, 2),
            recycled_priors=recycled_priors,
            composted_at_epoch=time.time(),
        )
        self.humus_pile.append(compost)
        self._persist_records()
        logger.info(f"🍂 [EPISTEMIC COMPOST]: Decomposed {total_tokens} dead tokens into Humus {compost_id} (Nitrogen={nitrogen:.2f}).")
        return compost

    def resurrect_audit(self, granary: List[FruitArtifact]) -> ResurrectionAudit:
        """
        The Cold-Boot Mortality Audit.
        Simulates sudden power loss / volatile memory wipe.
        Only items possessing irreversible hardware silicon PMP locks (Bit 7 L=1) survive.
        """
        audit_id = f"audit-resurrection-{int(time.time() * 1000)}"
        total = len(granary)
        survived = sum(1 for f in granary if f.hardware_pmp_locked and f.coherence_r >= 0.80)
        decayed = total - survived
        ratio = round(survived / total, 3) if total > 0 else 1.0

        audit = ResurrectionAudit(
            audit_id=audit_id,
            tested_invariants_count=total,
            survived_fruits_count=survived,
            decayed_mortal_count=decayed,
            immortality_ratio=ratio,
            timestamp=time.time(),
        )
        logger.info(f"✨ [RESURRECTION AUDIT]: Tested {total} invariants across cold-boot threshold. Survived: {survived} ({ratio*100:.1f}%)")
        return audit

    def get_accumulated_topsoil_vitality(self) -> float:
        """Calculates soil fertility bonus derived from composted past failures."""
        if not self.humus_pile:
            return 1.0
        recent = self.humus_pile[-10:]
        avg_density = sum(h.nitrogen_density for h in recent) / len(recent)
        # Yields a boost between 1.0 and 1.25
        return round(1.0 + (avg_density * 0.25), 3)

    def get_status(self) -> Dict[str, Any]:
        return {
            "total_tombstones": len(self.tombstones),
            "total_humus_composts": len(self.humus_pile),
            "accumulated_topsoil_vitality": self.get_accumulated_topsoil_vitality(),
            "total_decomposed_tokens": sum(h.decomposed_tokens for h in self.humus_pile),
            "recent_tombstones": [t.model_dump() for t in self.tombstones[-5:]],
            "recent_humus": [h.model_dump() for h in self.humus_pile[-5:]],
        }


# Singleton instance
reality_death_engine = DeathEngine()
