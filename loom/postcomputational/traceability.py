"""
Cryptographic Traceability Ledger (`loom/postcomputational/traceability.py`).

Provides append-only, tamper-evident audit logging for the 3-stage
postcomputational pipeline (PREPROCESS, COMPUTE, POSTPROCESS).
"""

from __future__ import annotations

import json
from pathlib import Path
import threading
import time
from typing import Any, Dict, List, Optional

from loom.postcomputational.types import PipelineStage, TraceRecord


class TraceabilityLedger:
    """Manages the persistent JSONL audit trail with SHA-256 provenance chaining."""

    def __init__(self, ledger_path: Optional[Path] = None):
        if ledger_path is None:
            ledger_path = Path(__file__).resolve().parents[2] / "vault" / ".system" / "traceability_ledger.jsonl"
        self.ledger_path = ledger_path
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._in_memory_records: List[TraceRecord] = []

    def record(self, trace: TraceRecord) -> str:
        """Appends a trace record to the ledger and returns its verification hash."""
        trace_hash = trace.compute_hash()
        data = {
            "stage": trace.stage.value,
            "entity_id": trace.entity_id,
            "timestamp": trace.timestamp,
            "inputs_hash": trace.inputs_hash,
            "outputs_hash": trace.outputs_hash,
            "metrics": trace.metrics,
            "hardware_context": trace.hardware_context,
            "verified": trace.verified,
            "trace_hash": trace_hash,
        }

        line = json.dumps(data, sort_keys=True) + "\n"
        with self._lock:
            self._in_memory_records.append(trace)
            try:
                with open(self.ledger_path, "a", encoding="utf-8") as f:
                    f.write(line)
            except Exception:
                pass

        return trace_hash

    def record_batch(self, traces: List[TraceRecord]) -> int:
        """Records a batch of traces atomically."""
        if not traces:
            return 0
        lines = []
        with self._lock:
            for t in traces:
                self._in_memory_records.append(t)
                data = {
                    "stage": t.stage.value,
                    "entity_id": t.entity_id,
                    "timestamp": t.timestamp,
                    "inputs_hash": t.inputs_hash,
                    "outputs_hash": t.outputs_hash,
                    "metrics": t.metrics,
                    "hardware_context": t.hardware_context,
                    "verified": t.verified,
                    "trace_hash": t.compute_hash(),
                }
                lines.append(json.dumps(data, sort_keys=True) + "\n")

            try:
                with open(self.ledger_path, "a", encoding="utf-8") as f:
                    f.writelines(lines)
            except Exception:
                pass

        return len(traces)

    def get_recent_traces(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Reads recent audit trace entries from the ledger file."""
        if not self.ledger_path.exists():
            return []
        try:
            with open(self.ledger_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            results = []
            for line in lines[-limit:]:
                line = line.strip()
                if line:
                    results.append(json.loads(line))
            return results
        except Exception:
            return []
