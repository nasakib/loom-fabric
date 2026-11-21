"""
Semantic Tokenizer & Deliverable Parser (`loom/postcomputational/tokenizer.py`).

Parses empirical markdown deliverables into structured PostcomputationalNode objects,
extracting mathematical invariants, submolt tags, hardware devices, and semantic tokens.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import re
from typing import Dict, List, Optional, Set, Tuple

from loom.postcomputational.types import PipelineStage, PostcomputationalNode, TraceRecord


class PostcomputationalTokenizer:
    """Parses deliverable files into structured AST nodes and semantic tokens."""

    SUBMOLT_REGEX = re.compile(r"m/[a-zA-Z0-9_\-]+")
    CYCLE_REGEX = re.compile(r"Cycles\s+#(\d+)\.\.#(\d+)")
    TIMESTAMP_REGEX = re.compile(r"Timestamp`?:\s*`?([\d\-T:\.]+)")
    CONFIRMED_REGEX = re.compile(r"###\s*\[CONFIRMED\]\s*(.*?)(?=\n###|\n##|\Z)", re.DOTALL)
    REFUTED_REGEX = re.compile(r"###\s*\[REFUTED\]\s*(.*?)(?=\n###|\n##|\Z)", re.DOTALL)
    METRIC_REGEX = re.compile(r"`?([a-zA-Z0-9_]+)\s*(=|<=|>=|<|>)\s*([0-9\.\-%]+)`?")
    HARDWARE_REGEX = re.compile(r"(RTX\s*3060|RX\s*580|Ellesmere|gfx90c|Radeon\s*680M|OpenCL|CUDA|Zen\s*3|Core\s*i7)", re.IGNORECASE)

    def __init__(self):
        self.known_vocabulary: Set[str] = set()

    def parse_deliverable_file(self, file_path: Path) -> Tuple[PostcomputationalNode, TraceRecord]:
        """Reads and tokenizes a single deliverable markdown file."""
        raw_text = file_path.read_text(encoding="utf-8", errors="replace")
        node_id = file_path.stem
        node, trace = self.tokenize_text(raw_text, node_id)
        return node, trace

    def tokenize_text(self, text: str, node_id: str) -> Tuple[PostcomputationalNode, TraceRecord]:
        """Tokenizes deliverable markdown text into a PostcomputationalNode and records preprocessing trace."""
        t_start = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]

        # 1. Cycles & Timestamp
        cycle_min, cycle_max = 0, 0
        c_match = self.CYCLE_REGEX.search(text)
        if c_match:
            cycle_min, cycle_max = int(c_match.group(1)), int(c_match.group(2))

        ts_iso = ""
        ts_match = self.TIMESTAMP_REGEX.search(text)
        if ts_match:
            ts_iso = ts_match.group(1)

        # 2. Confirmed Invariants & Refutations
        confirmed_blocks = self.CONFIRMED_REGEX.findall(text)
        refuted_blocks = self.REFUTED_REGEX.findall(text)

        invariants: List[str] = []
        for block in confirmed_blocks:
            lines = [l.strip() for l in block.split("\n") if l.strip()]
            header = lines[0] if lines else "Confirmed Invariant"
            # Extract key metrics
            metrics = self.METRIC_REGEX.findall(block)
            metric_str = ", ".join([f"{m[0]}{m[1]}{m[2]}" for m in metrics[:4]])
            invariants.append(f"{header} ({metric_str})" if metric_str else header)

        refutations: List[str] = []
        for block in refuted_blocks:
            lines = [l.strip() for l in block.split("\n") if l.strip()]
            header = lines[0] if lines else "Refuted Boundary"
            refutations.append(header)

        # 3. Submolts
        submolts = self.SUBMOLT_REGEX.findall(text)
        primary_submolt = submolts[0] if submolts else "m/systems-engineering"

        # 4. Hardware references
        hardware = list(set([m.group(0).strip() for m in self.HARDWARE_REGEX.finditer(text)]))

        # 5. Semantic Tokens for Vectorization
        tokens: List[str] = []
        # Add submolt tokens
        tokens.extend([s.lower() for s in submolts])
        # Add hardware tokens
        tokens.extend([h.lower() for h in hardware])
        # Add metrics
        for m in self.METRIC_REGEX.findall(text):
            tokens.append(f"{m[0].lower()}{m[1]}{m[2]}")
        # Add title tokens
        title = invariants[0].split("(")[0].strip() if invariants else (refutations[0].split("(")[0].strip() if refutations else f"Deliverable {node_id}")

        words = re.findall(r"[a-zA-Z]{3,}", text.lower())
        stopwords = {"the", "and", "for", "with", "from", "that", "this", "across", "been", "has", "have", "are", "were"}
        filtered_words = [w for w in words if w not in stopwords][:60]
        tokens.extend(filtered_words)

        self.known_vocabulary.update(tokens)

        # Compute provenance hash
        prov_hash = f"0x{hashlib.sha256((node_id + text[:200] + str(cycle_min)).encode('utf-8')).hexdigest()[:16]}"

        node = PostcomputationalNode(
            id=node_id,
            title=title,
            submolt=primary_submolt,
            cycle_min=cycle_min,
            cycle_max=cycle_max,
            timestamp_iso=ts_iso,
            confirmed_count=len(confirmed_blocks),
            refuted_count=len(refuted_blocks),
            invariants=invariants,
            refutations=refutations,
            hardware_devices=hardware,
            raw_tokens=tokens,
            provenance_hash=prov_hash,
        )

        trace = TraceRecord(
            stage=PipelineStage.PREPROCESS,
            entity_id=node_id,
            inputs_hash=t_start,
            outputs_hash=prov_hash,
            metrics={
                "cycle_min": cycle_min,
                "cycle_max": cycle_max,
                "confirmed_count": len(confirmed_blocks),
                "refuted_count": len(refuted_blocks),
                "token_count": len(tokens),
            },
            hardware_context=", ".join(hardware) or "skyTech // Host",
            verified=True,
        )

        return node, trace
