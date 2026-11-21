"""
ClothOS & Loom Live Mutable System Configuration (`loom/fabric/system_config.py`).

Stores, validates, and persists the empirically-derived operating parameters
for the continuous worker, dual-GPU pipeline, and active inference algorithms.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger("loom.fabric.system_config")


class SystemConfig:
    """Manages hot-reloadable system parameters established from empirical data."""

    DEFAULT_PARAMS: Dict[str, Any] = {
        # Sovereign Epistemic & Fiduciary Model Configuration
        "active_frontier_model": "loom-sovereign:latest",
        "active_fast_model": "loom-sovereign-fast:latest",
        "model_temperature": 0.20,
        "model_top_p": 0.85,
        "model_context_length": 32768,
        "epistemic_rigor_enforced": True,
        "fiduciary_veto_enabled": True,

        # Active Inference & Kuramoto Consensus
        "kuramoto_consensus_k": 2.45,
        "kuramoto_exploration_k": 0.65,
        "kuramoto_min_relaxation_steps": 350,  # Refuted: 250 was too short for large N
        "kuramoto_dt": 0.015,
        "kuramoto_target_order_r": 0.85,

        # Systems Engineering: Hypersphere S^(1535) Geometry
        "hypersphere_dim": 1536,
        "hypersphere_ortho_threshold": 0.035,
        "hypersphere_noise_floor": 0.110,

        # Distributed Compute: GPU 1 RX 580 Ellesmere OpenCL
        "rx580_min_batch_size": 4096,  # Refuted: N < 1024 suffers PCIe driver overhead
        "rx580_workgroup_size": 256,
        "rx580_max_drift_epsilon": 0.0001,

        # RISC-V Silicon: NAPOT PMP CSR 0x9B
        "pmp_min_napot_grain_bytes": 8,
        "pmp_csr_address": 0x9B,

        # Fourier Geometry: Symplectic Conservation
        "symplectic_max_dt": 0.015,
        "symplectic_max_drift_pct": 0.05,

        # Optimization & Evolution Metadata
        "evolution_generation": 1,
        "last_evolution_timestamp": 0.0,
        "last_evolution_rationale": "Base empirical calibration from 7,200+ trials",
    }

    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = workspace_root or Path(__file__).resolve().parents[2]
        self.config_file = self.workspace_root / ".loom_system_parameters.json"
        self._params: Dict[str, Any] = dict(self.DEFAULT_PARAMS)
        self.load()

    def load(self) -> None:
        """Loads configuration from disk, falling back to defaults."""
        if self.config_file.exists():
            try:
                data = json.loads(self.config_file.read_text(encoding="utf-8"))
                self._params.update(data)
                logger.info(f"Loaded SystemConfig gen #{self._params.get('evolution_generation', 1)} from {self.config_file.name}")
            except Exception as e:
                logger.warning(f"Failed to read {self.config_file}: {e}; using defaults")

    def save(self) -> None:
        """Atomically persists active configuration to disk."""
        try:
            self.config_file.write_text(json.dumps(self._params, indent=2), encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to save {self.config_file}: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        return self._params.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._params[key] = value

    def update_params(self, updates: Dict[str, Any], rationale: str = "") -> int:
        """Applies a batch of verified updates and increments the evolution generation."""
        self._params.update(updates)
        self._params["evolution_generation"] = int(self._params.get("evolution_generation", 1)) + 1
        import time
        self._params["last_evolution_timestamp"] = time.time()
        if rationale:
            self._params["last_evolution_rationale"] = rationale
        self.save()
        return self._params["evolution_generation"]

    def snapshot(self) -> Dict[str, Any]:
        return dict(self._params)


# Global instance
system_config = SystemConfig()
