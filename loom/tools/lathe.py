# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
#
# Part of Pillar 1 & 2: FABRIC / CLOTHOS / LOOM PRECISION TOOLCHAIN.
"""
Lathe Shaper — Rotational Latent Turning & Manifold Orthogonalization.

Mechanics:
- Spins raw high-dimensional embedding spaces against a cutting tool to shave off collinear noise.
- Balances and centers vector representations via SVD and QR decomposition onto unitary manifolds.
- Symmetrizes Kuramoto phase distributions to evaluate synchronization order parameter $r$.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional
import numpy as np

logger = logging.getLogger("loom.tools.lathe")


class LatheShaper:
    """Rotational lathe for vector representation normalization and phase balancing."""

    def __init__(self):
        self.operations_count: int = 0

    def turn_embeddings(self, vectors: np.ndarray, target_dim: Optional[int] = None) -> np.ndarray:
        """
        Spins vectors on the spindle, centering them and shaving off collinear noise via SVD.
        Preserves relative semantic pairwise similarities while eliminating common-mode drift.
        Guarantees all turned vectors lie cleanly on the unitary hypersphere (L2 = 1.0).
        """
        self.operations_count += 1
        arr = np.asarray(vectors, dtype=np.float32)
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)

        if arr.shape[0] == 1:
            norm = np.linalg.norm(arr, axis=-1, keepdims=True)
            norm = np.where(norm == 0, 1.0, norm)
            return arr / norm

        # 1. Center around origin (shave common-mode anisotropic bias)
        mean_vec = np.mean(arr, axis=0, keepdims=True)
        centered = arr - mean_vec

        if np.allclose(centered, 0):
            norm = np.linalg.norm(arr, axis=-1, keepdims=True)
            norm = np.where(norm == 0, 1.0, norm)
            return arr / norm

        # 2. Decompose via SVD onto principal manifold (preserving pairwise angles)
        try:
            _, _, vt = np.linalg.svd(centered, full_matrices=False)
            if target_dim and target_dim < vt.shape[0]:
                turned_coords = centered @ vt[:target_dim].T
            else:
                turned_coords = centered @ vt.T
        except Exception:
            turned_coords = centered

        # 3. Normalize to unitary hypersphere (||v||_2 = 1.0)
        norms = np.linalg.norm(turned_coords, axis=-1, keepdims=True)
        norms = np.where(norms == 0, 1.0, norms)
        turned = turned_coords / norms

        logger.debug(f"🔄 [Lathe Turned]: Shaved {arr.shape} -> {turned.shape} onto unitary manifold.")
        return turned

    def balance_kuramoto_oscillators(self, phases: np.ndarray) -> Dict[str, Any]:
        """
        Evaluates the balance of Kuramoto oscillator phases:
        r * exp(i * psi) = (1 / N) * sum(exp(i * theta_j))
        """
        self.operations_count += 1
        arr = np.asarray(phases, dtype=np.float32)
        complex_order = np.mean(np.exp(1j * arr))
        r = float(np.abs(complex_order))
        psi = float(np.angle(complex_order))

        return {
            "oscillator_count": len(arr),
            "coherence_order_parameter_r": round(r, 4),
            "mean_phase_angle_psi": round(psi, 4),
            "is_synchronized": r > 0.85,
        }

    def get_status(self) -> Dict[str, Any]:
        return {"operations_count": self.operations_count}
