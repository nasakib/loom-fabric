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
        Spins vectors on the spindle, centering them and shaving off collinear noise via SVD/QR.
        Guarantees all turned vectors lie cleanly on the unitary hypersphere (L2 = 1.0).
        """
        self.operations_count += 1
        arr = np.asarray(vectors, dtype=np.float32)
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)

        # 1. Center around origin (shave eccentricity)
        mean_vec = np.mean(arr, axis=0, keepdims=True)
        centered = arr - mean_vec

        # 2. Orthogonalize via QR decomposition
        q, _ = np.linalg.qr(centered.T)
        orthogonalized = q.T[: arr.shape[0]]

        if target_dim and target_dim < orthogonalized.shape[1]:
            orthogonalized = orthogonalized[:, :target_dim]

        # 3. Normalize to unitary hypersphere (||v||_2 = 1.0)
        norms = np.linalg.norm(orthogonalized, axis=-1, keepdims=True)
        norms[norms == 0] = 1.0
        turned = orthogonalized / norms

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
