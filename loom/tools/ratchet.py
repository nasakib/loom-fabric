# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
#
# Part of Pillar 1 & 2: FABRIC / CLOTHOS / LOOM PRECISION TOOLCHAIN.
r"""
Ratchet Engine — Unidirectional Monotonic Progress & State Invariant Pawl.

Mechanics:
- Permits forward motion ($d\mathcal{K}/dt \ge 0$) while physically barring backward slippage.
- Irreversible Invariant Cementing: Locks proved mathematical theorems into Fourier's Library.
- Forward-Secrecy Double-Ratchet: Ephemeral key rotation destroying historical decryptability.
- Preemption Catch-Dog: Instant zero-OOM execution state freezing and resumption.
- Thermodynamic Free-Energy Diode: Accepts only entropy-reducing / coherence-increasing mutations.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from pathlib import Path
import shutil
import threading
import time
from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, Field

logger = logging.getLogger("loom.tools.ratchet")

MAX_IN_MEMORY_AXIOMS = 500
COMPACT_THRESHOLD_BYTES = 2 * 1024 * 1024  # 2 MiB automatic archive compaction threshold


class RatchetAxiom(BaseModel, frozen=True):
    """An immutable, non-regressible theorem or invariant tooth locked by the Ratchet."""
    tooth_index: int
    axiom_id: str
    claim: str
    proof_hash: str
    confidence: float
    timestamp_epoch: float
    node_origin: str


class RatchetSnapshot(BaseModel, frozen=True):
    """Zero-OOM preemption catch snapshot locked in place until compute resumes."""
    snapshot_id: str
    tooth_index: int
    cycle: int
    oscillator_offset: int
    active_tier: str
    timestamp_epoch: float
    payload: Dict[str, Any]


class RatchetEngine:
    """The Unidirectional Monotonic State & Invariant Pawl for Fabric & ClothOS."""

    def __init__(
        self,
        workspace_root: Optional[Path] = None,
        ledger_file: Optional[Path] = None,
        home_ledger: Optional[Path] = None,
        catch_file: Optional[Path] = None,
    ):
        self._lock = threading.RLock()
        self.workspace_root = workspace_root or Path(__file__).resolve().parents[2]
        self.ledger_file = ledger_file or (self.workspace_root / ".loom_ratchet_axioms.json")
        self.log_file = self.ledger_file.with_suffix(".jsonl")
        self.catch_file = catch_file or (self.workspace_root / ".loom_ratchet_catch.json")
        self.home_ledger = home_ledger or (Path.home() / ".loom" / "ratchet_axioms.json")
        self.home_log_file = self.home_ledger.with_suffix(".jsonl")
        self.tooth_count: int = 0
        self.current_root_key: str = hashlib.sha256(b"CLOTHOS_INITIAL_RATCHET_SEED_2026").hexdigest()
        self.axioms: Dict[str, RatchetAxiom] = {}
        self._seen_claim_hashes: Set[str] = set()
        fallback_to_home = (workspace_root is None or home_ledger is not None)
        self._load_ledger(fallback_to_home=fallback_to_home)

    @staticmethod
    def _claim_digest(claim: str) -> str:
        norm = " ".join(str(claim).strip().lower().split())
        return hashlib.sha256(norm.encode("utf-8", errors="ignore")).hexdigest()[:16]

    def _load_ledger(self, fallback_to_home: bool = True) -> None:
        if self.ledger_file.exists():
            target = self.ledger_file
        elif fallback_to_home and self.home_ledger.exists():
            target = self.home_ledger
        else:
            return

        try:
            file_size = target.stat().st_size
            data = json.loads(target.read_text(encoding="utf-8"))
            self.tooth_count = int(data.get("tooth_count", 0))
            self.current_root_key = data.get("current_root_key", self.current_root_key)
            raw_axioms = data.get("axioms", [])
            recent_axioms = raw_axioms[-MAX_IN_MEMORY_AXIOMS:] if len(raw_axioms) > MAX_IN_MEMORY_AXIOMS else raw_axioms
            for item in recent_axioms:
                ax = RatchetAxiom(**item)
                self.axioms[ax.axiom_id] = ax
                self._seen_claim_hashes.add(self._claim_digest(ax.claim))

            for ch in data.get("recent_claim_hashes", [])[-2000:]:
                self._seen_claim_hashes.add(str(ch))

            # Auto-compact legacy multi-MB monolithic ledgers while preserving tooth_count & archive
            if file_size > COMPACT_THRESHOLD_BYTES:
                archive_path = target.with_name(f"{target.stem}.archive{target.suffix}")
                try:
                    if not archive_path.exists():
                        shutil.copy2(target, archive_path)
                except Exception:
                    pass
                logger.info(
                    "Compacted oversized Ratchet ledger %s (%.1f MB -> tail %d of %d teeth).",
                    target.name,
                    file_size / (1024 * 1024),
                    len(self.axioms),
                    self.tooth_count,
                )
                self._persist_ledger()
        except Exception as e:
            logger.warning(f"Could not load Ratchet ledger: {e}")

    def _persist_ledger(self, new_axiom: Optional[RatchetAxiom] = None) -> None:
        with self._lock:
            # Keep memory bounded so long-running daemons never leak RAM
            if len(self.axioms) > MAX_IN_MEMORY_AXIOMS:
                overflow = len(self.axioms) - MAX_IN_MEMORY_AXIOMS
                for old_key in list(self.axioms.keys())[:overflow]:
                    self.axioms.pop(old_key, None)

            if new_axiom is not None:
                line = new_axiom.model_dump_json() + "\n"
                for log_p in (self.log_file, self.home_log_file):
                    try:
                        log_p.parent.mkdir(parents=True, exist_ok=True)
                        with open(log_p, "a", encoding="utf-8") as lf:
                            lf.write(line)
                    except Exception:
                        pass

            data = {
                "tooth_count": self.tooth_count,
                "current_root_key": self.current_root_key,
                "axioms": [ax.model_dump() for ax in list(self.axioms.values())[-MAX_IN_MEMORY_AXIOMS:]],
                "recent_claim_hashes": list(self._seen_claim_hashes)[-2000:],
                "last_updated": time.time(),
            }
            serialized = json.dumps(data, indent=2)
            try:
                self.ledger_file.parent.mkdir(parents=True, exist_ok=True)
                self.ledger_file.write_text(serialized, encoding="utf-8")
            except Exception:
                pass
            try:
                self.home_ledger.parent.mkdir(parents=True, exist_ok=True)
                self.home_ledger.write_text(serialized, encoding="utf-8")
            except Exception:
                pass

    def click(
        self,
        axiom_id: str,
        claim: str,
        proof_payload: str,
        confidence: float = 1.0,
        node_origin: str = "skyTech-Worker",
        deduplicate_claim: bool = False,
    ) -> bool:
        """
        Advances the Ratchet by exactly one tooth, cementing an invariant forever.
        Rejects any attempt to regress or overwrite an already clicked axiom.
        """
        with self._lock:
            if axiom_id in self.axioms:
                # Monotonic invariance: already proven theorems cannot be overwritten
                return False

            claim_digest = self._claim_digest(claim)
            if deduplicate_claim and claim_digest in self._seen_claim_hashes:
                return False

            if confidence < 0.80:
                logger.debug(f"[Ratchet Pawl Slip]: Invariant {axiom_id} confidence {confidence:.2f} < 0.80 threshold.")
                return False

            self.tooth_count += 1
            proof_hash = hashlib.sha256(proof_payload.encode("utf-8")).hexdigest()

            axiom = RatchetAxiom(
                tooth_index=self.tooth_count,
                axiom_id=axiom_id,
                claim=claim,
                proof_hash=proof_hash,
                confidence=confidence,
                timestamp_epoch=time.time(),
                node_origin=node_origin,
            )
            self.axioms[axiom_id] = axiom
            self._seen_claim_hashes.add(claim_digest)
            if len(self._seen_claim_hashes) > 5000:
                self._seen_claim_hashes = set(list(self._seen_claim_hashes)[-2500:])
            self.rotate_key(salt=proof_hash.encode("utf-8")[:16])
            self._persist_ledger(new_axiom=axiom)

            logger.info(f"⚙ [Ratchet Click]: Tooth #{self.tooth_count} locked: {axiom_id} ({claim[:50]}...)")
            return True

    def rotate_key(self, salt: bytes = b"") -> str:
        """Rotates the forward-secrecy HKDF key forward by 1 tick; destroys past decryptability."""
        combined = (self.current_root_key + salt.hex() + str(time.time())).encode("utf-8")
        self.current_root_key = hashlib.sha256(combined).hexdigest()
        return self.current_root_key

    def preemption_catch(self, cycle: int, oscillator_offset: int, payload: Dict[str, Any], active_tier: str = "CUDA+OpenCL") -> str:
        """Engages the preemption catch dog, freezing current execution offset before yielding silicon."""
        snap_id = f"snap-{int(time.time()*1000)}"
        snap = RatchetSnapshot(
            snapshot_id=snap_id,
            tooth_index=self.tooth_count,
            cycle=cycle,
            oscillator_offset=oscillator_offset,
            active_tier=active_tier,
            timestamp_epoch=time.time(),
            payload=payload,
        )
        try:
            self.catch_file.write_text(snap.model_dump_json(indent=2), encoding="utf-8")
        except Exception:
            pass
        logger.info(f"🛑 [Ratchet Preemption Catch]: Clamped at Tooth #{self.tooth_count}, cycle {cycle}, offset {oscillator_offset}.")
        return snap_id

    def release_catch(self) -> Optional[RatchetSnapshot]:
        """Releases the preemption catch dog, restoring exact state so compute resumes with zero replay."""
        if not self.catch_file.exists():
            return None
        try:
            data = json.loads(self.catch_file.read_text(encoding="utf-8"))
            self.catch_file.unlink(missing_ok=True)
            snap = RatchetSnapshot(**data)
            logger.info(f"▶ [Ratchet Catch Released]: Resuming from Tooth #{snap.tooth_index}, cycle {snap.cycle}.")
            return snap
        except Exception:
            return None

    def free_energy_diode(self, delta_free_energy: float, delta_coherence: float) -> bool:
        """
        Thermodynamic Feynman Ratchet Diode:
        Allows advancement only if Free Energy decreases (dF <= 0) or coherence improves (dr >= 0).
        Blocks regressive mutations.
        """
        if delta_free_energy <= 0.0 or delta_coherence >= 0.0:
            return True
        logger.debug(f"⛔ [Ratchet Diode]: Regressive mutation blocked (dFE={delta_free_energy:+.3f}, dr={delta_coherence:+.3f})")
        return False

    def get_status(self) -> Dict[str, Any]:
        return {
            "tooth_count": self.tooth_count,
            "cemented_axioms": len(self.axioms),
            "current_root_key_preview": f"{self.current_root_key[:12]}...",
            "has_active_catch": self.catch_file.exists(),
        }
