# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
#
# Part of Pillar 1 & 2: FABRIC / CLOTHOS / LOOM PRECISION TOOLCHAIN.
"""
Chisel Ablator — Surgical AST Mutation, Context Compaction & Token Ablation.

Mechanics:
- Hardened wedge tool slicing away micro-slivers of redundant prompt/code material.
- Prunes conversational bloat while preserving mathematical theorems and vault tokens.
- Surgically targets and extracts AST nodes with single-statement precision.
"""

from __future__ import annotations

import ast
import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger("loom.tools.chisel")


class ChiselAblator:
    """Surgical token and AST ablation engine."""

    def __init__(self):
        self.cuts_executed: int = 0

    def ablate_context(
        self, text: str, max_chars: int = 4000, preserve_markers: Optional[List[str]] = None
    ) -> str:
        """
        Slices away fluff, repeated greeting phrases, and conversational filler,
        preserving code blocks, markdown tables, and Torque vault tokens (__SOV_*).
        """
        self.cuts_executed += 1
        if len(text) <= max_chars:
            return text

        markers = preserve_markers or ["__SOV_", "```", "|", "Cycle #", "Theorem", "def ", "class "]

        lines = text.splitlines()
        preserved_lines: List[str] = []
        discarded_count = 0

        for line in lines:
            s = line.strip()
            # If line contains critical marker, always preserve
            if any(m in line for m in markers) or not s:
                preserved_lines.append(line)
            elif len(s) > 10 and not s.startswith(("-", "*", "#")):
                # Check if it's generic conversational preamble
                lower = s.lower()
                if any(lower.startswith(p) for p in ["sure,", "i understand,", "as an ai,", "hello,", "certainly,"]):
                    discarded_count += 1
                    continue
                preserved_lines.append(line)
            else:
                preserved_lines.append(line)

        ablated = "\n".join(preserved_lines)
        if len(ablated) > max_chars:
            # Head-and-tail slice
            half = max_chars // 2
            ablated = ablated[:half] + "\n\n... [CHISELED INTERMEDIATE CONTEXT] ...\n\n" + ablated[-half:]

        logger.debug(f"🪓 [Chisel Slice]: Cut {len(text)} chars down to {len(ablated)} chars ({discarded_count} lines pruned).")
        return ablated

    def slice_ast_definition(self, source_code: str, target_name: str) -> Optional[str]:
        """
        Surgically extracts a specific function or class definition from source code
        using Python's AST parser without parsing or mutating surrounding code.
        """
        self.cuts_executed += 1
        try:
            tree = ast.parse(source_code)
            lines = source_code.splitlines()
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    if node.name == target_name:
                        start_line = node.lineno - 1
                        end_line = getattr(node, "end_lineno", len(lines))
                        extracted = "\n".join(lines[start_line:end_line])
                        logger.debug(f"🪓 [Chisel AST]: Successfully extracted node '{target_name}' (lines {start_line+1}-{end_line}).")
                        return extracted
        except Exception as e:
            logger.warning(f"Chisel AST parse warning: {e}")
        return None

    def get_status(self) -> Dict[str, Any]:
        return {"cuts_executed": self.cuts_executed}
