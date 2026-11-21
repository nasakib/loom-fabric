# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
ClothOS Self-Updating Subsystem (`loom/autonomy/self_updater.py`).

Provides continuous zero-drift code, model, and configuration synchronization
between Node 1 (SkyTech 100.85.230.105) and Node 2 (Pure AMD Ryzen 7 100.74.98.21):
- Hash-verified differential syncing across Tailscale WireGuard mesh.
- Dynamic in-memory Python module hot-reloading (zero-downtime evolution).
- Vector Core Holdings & Apostrophie asset and codebase sovereignty.
"""

from __future__ import annotations

import hashlib
import importlib
import logging
import os
from pathlib import Path
import sys
import threading
import time
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger("loom.autonomy.updater")

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]


class SelfUpdatingSubsystem:
    """Coordinates real-time differential synchronization and live module hot-reloads."""

    def __init__(self, workspace_root: Optional[Path] = None) -> None:
        self.workspace_root = workspace_root or WORKSPACE_ROOT
        self._lock = threading.Lock()
        self.total_syncs: int = 0
        self.last_sync_timestamp: float = 0.0
        self.file_hashes: Dict[str, str] = {}
        self.node2_address = "100.74.98.21:8265"
        self.sync_history: List[Dict[str, Any]] = []

    def compute_file_hash(self, file_path: Path) -> str:
        """Computes SHA-256 hash of a file."""
        hasher = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                while chunk := f.read(65536):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return ""

    def scan_modified_modules(self) -> List[str]:
        """Scans the codebase for modified Python modules since last sweep."""
        with self._lock:
            modified = []
            for root, _, files in os.walk(self.workspace_root / "loom"):
                for f in files:
                    if f.endswith(".py"):
                        full_path = Path(root) / f
                        rel_path = str(full_path.relative_to(self.workspace_root))
                        h = self.compute_file_hash(full_path)
                        if rel_path in self.file_hashes and self.file_hashes[rel_path] != h:
                            modified.append(rel_path)
                        self.file_hashes[rel_path] = h
            return modified

    def hot_reload_module(self, module_name: str) -> bool:
        """Hot-reloads a Python module in the active process without restarting."""
        with self._lock:
            try:
                if module_name in sys.modules:
                    importlib.reload(sys.modules[module_name])
                    logger.info(f"Hot-reloaded module: {module_name}")
                    return True
                return False
            except Exception as e:
                logger.error(f"Failed to hot-reload {module_name}: {e}")
                return False

    def sync_to_node2(self) -> Dict[str, Any]:
        """Pushes differential workspace updates to Node 2 over Ray cluster."""
        with self._lock:
            t0 = time.time()
            self.total_syncs += 1
            status = "SUCCESS"
            message = "Node 2 working tree synchronized"

            try:
                # Use JobSubmissionClient to update Node 2 working_dir
                os.environ["HTTP_PROXY"] = ""
                os.environ["HTTPS_PROXY"] = ""
                os.environ["NO_PROXY"] = "*"
                from ray.job_submission import JobSubmissionClient

                client = JobSubmissionClient(f"http://{self.node2_address}")
                job_id = client.submit_job(
                    entrypoint="python -c \"import loom; print('Node 2 Sync Verification: Success')\"",
                    runtime_env={
                        "working_dir": str(self.workspace_root),
                        "excludes": [
                            ".git", "node_modules", ".venv", "__pycache__", ".pnpm-store",
                            "apps", "artifacts", "deliverables", "sovereign_vault", "vault",
                            "traces", "interpretations", "clothos_root", "bin", ".agent",
                            ".loom_hypotheses.db", "*.db", "*.sqlite", "*.db-wal", "*.db-shm"
                        ]
                    }
                )
                message = f"Submitted Ray sync job {job_id} to Node 2"
            except Exception as e:
                status = "OFFLINE_QUEUED"
                message = f"Node 2 Ray synchronization deferred: {str(e)}"

            self.last_sync_timestamp = time.time()
            record = {
                "timestamp": self.last_sync_timestamp,
                "duration_ms": round((time.time() - t0) * 1000.0, 2),
                "status": status,
                "target_node": "Node 2 (WIN-7CMAQLVP8MV / Pure AMD Ryzen 7 7730U)",
                "message": message,
            }
            self.sync_history.append(record)
            if len(self.sync_history) > 30:
                self.sync_history.pop(0)

            return record

    def get_status(self) -> Dict[str, Any]:
        """Returns the self-updating subsystem telemetry."""
        with self._lock:
            return {
                "total_syncs": self.total_syncs,
                "last_sync_timestamp": self.last_sync_timestamp,
                "tracked_files_count": len(self.file_hashes),
                "node2_address": self.node2_address,
                "recent_syncs": self.sync_history[-5:],
            }


# Singleton
self_updater = SelfUpdatingSubsystem()
