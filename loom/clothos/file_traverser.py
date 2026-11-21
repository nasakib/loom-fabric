# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
ClothOS Recursive File Traverser & Filesystem Profiler (`loom/clothos/file_traverser.py`).
Recursively scans, indexes, categorizes, and profiles files across any directory tree.
Identifies programming languages, configuration formats, tabular datasets, and assembly/hardware files (especially RISC-V .s / .asm / .riscv).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


DEFAULT_EXCLUDES: Set[str] = {
    ".git",
    ".github",
    ".pytest_cache",
    "node_modules",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pnpm-store",
    ".clothos_sandbox",
    "dist",
    "build",
    "target",
    ".turbo",
    ".next",
    ".cache",
    ".gemini",
    ".agent",
    "bin",
    "traces",
    "artifacts",
    "data",
    "deliverables",
    "scratch",
}

RISCV_EXTENSIONS: Set[str] = {".s", ".asm", ".riscv"}


def is_riscv_file(file_path: Path) -> bool:
    """Checks if a file is a RISC-V assembly or object file by extension or content."""
    ext = file_path.suffix.lower()
    if ext in RISCV_EXTENSIONS:
        return True
    if file_path.name.lower().startswith("riscv_") or "_riscv" in file_path.name.lower():
        return True
    return False


def traverse_directory(
    root_path: Path | str,
    max_depth: int = 4,
    extension_filter: Optional[str] = None,
    exclude_dirs: Optional[Set[str]] = None,
    max_files: int = 500
) -> Dict[str, Any]:
    """
    Recursively scans and profiles a directory tree.
    Returns file counts, size summaries, extension breakdowns, and flagged RISC-V files.
    """
    base = Path(root_path).resolve()
    if not base.exists():
        return {"error": f"Path not found: {base}", "files": []}

    excludes = exclude_dirs or DEFAULT_EXCLUDES
    ext_filter = extension_filter.lower().strip() if extension_filter else None
    if ext_filter and not ext_filter.startswith("."):
        ext_filter = f".{ext_filter}"

    total_files = 0
    total_dirs = 0
    total_bytes = 0
    total_lines = 0

    extension_stats: Dict[str, Dict[str, int]] = {}
    file_records: List[Dict[str, Any]] = []
    riscv_records: List[Dict[str, Any]] = []

    def _walk(current_dir: Path, current_depth: int):
        nonlocal total_files, total_dirs, total_bytes, total_lines
        if current_depth > max_depth or total_files >= max_files:
            return

        try:
            entries = sorted(list(current_dir.iterdir()), key=lambda x: (not x.is_dir(), x.name.lower()))
        except PermissionError:
            return

        for entry in entries:
            name = entry.name
            if name in excludes or name.startswith(".git"):
                continue

            if entry.is_dir():
                total_dirs += 1
                _walk(entry, current_depth + 1)
            elif entry.is_file():
                ext = entry.suffix.lower() or "[no_ext]"
                if ext_filter and ext != ext_filter:
                    continue

                total_files += 1
                try:
                    size = entry.stat().st_size
                except Exception:
                    size = 0
                total_bytes += size

                lines = 0
                # Fast newline count only for text/code files < 64KB
                text_exts = {".py", ".s", ".asm", ".riscv", ".rs", ".ts", ".js", ".json", ".md", ".txt"}
                if ext in text_exts and size < 64 * 1024:
                    try:
                        with open(entry, "rb") as f:
                            lines = f.read().count(b"\n")
                    except Exception:
                        lines = 0
                total_lines += lines

                if ext not in extension_stats:
                    extension_stats[ext] = {"count": 0, "bytes": 0, "lines": 0}
                extension_stats[ext]["count"] += 1
                extension_stats[ext]["bytes"] += size
                extension_stats[ext]["lines"] += lines

                is_rv = is_riscv_file(entry)

                rec = {
                    "rel_path": str(entry.relative_to(base)).replace("\\", "/"),
                    "name": name,
                    "extension": ext,
                    "size_bytes": size,
                    "lines": lines,
                    "is_riscv": is_rv,
                }

                if len(file_records) < max_files:
                    file_records.append(rec)

                if is_rv:
                    riscv_records.append(rec)

    _walk(base, current_depth=0)

    # Sort extension stats by file count descending
    sorted_exts = dict(sorted(extension_stats.items(), key=lambda kv: kv[1]["count"], reverse=True))

    return {
        "root": str(base).replace("\\", "/"),
        "max_depth": max_depth,
        "total_files": total_files,
        "total_dirs": total_dirs,
        "total_bytes": total_bytes,
        "total_lines": total_lines,
        "extension_breakdown": sorted_exts,
        "riscv_files_count": len(riscv_records),
        "riscv_files": riscv_records,
        "files_sample": file_records[:100],
    }
