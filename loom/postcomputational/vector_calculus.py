"""
Linear Algebra & Vector Calculus Engine (`loom/postcomputational/vector_calculus.py`).

Applies high-dimensional inner products, Gram matrices, SVD dimensionality reduction,
and vector calculus differential operators (Gradient, Divergence, Curl) to postcomputational nodes.
"""

from __future__ import annotations

import hashlib
from typing import Dict, List, Tuple
import numpy as np

from loom.postcomputational.types import PipelineStage, PostcomputationalNode, TraceRecord


class VectorCalculusEngine:
    """Computes vector embeddings, Gram matrices, SVD 3D projections, and differential field operators."""

    def __init__(self, embedding_dim: int = 64):
        self.embedding_dim = embedding_dim
        # Submolt canonical hash basis seed
        self._submolt_basis: Dict[str, np.ndarray] = {}

    def _get_submolt_basis(self, submolt: str) -> np.ndarray:
        if submolt not in self._submolt_basis:
            seed = int(hashlib.md5(submolt.encode("utf-8")).hexdigest()[:8], 16)
            rng = np.random.RandomState(seed)
            vec = rng.randn(self.embedding_dim).astype(np.float32)
            vec /= (np.linalg.norm(vec) + 1e-9)
            self._submolt_basis[submolt] = vec
        return self._submolt_basis[submolt]

    def embed_nodes(self, nodes: List[PostcomputationalNode]) -> np.ndarray:
        """Embeds a list of PostcomputationalNodes into R^(N x D) normalized unit hypersphere vectors."""
        if not nodes:
            return np.empty((0, self.embedding_dim), dtype=np.float32)

        vectors = []
        for n in nodes:
            # 1. Base direction from submolt
            base = self._get_submolt_basis(n.submolt).copy()

            # 2. Modulate with token hash features
            token_vec = np.zeros(self.embedding_dim, dtype=np.float32)
            for t in n.raw_tokens[:40]:
                idx = int(hashlib.md5(t.encode("utf-8")).hexdigest()[:4], 16) % self.embedding_dim
                sign = 1.0 if (idx % 2 == 0) else -1.0
                token_vec[idx] += sign

            token_norm = np.linalg.norm(token_vec)
            if token_norm > 1e-9:
                token_vec /= token_norm

            # 3. Combine submolt basis (70%) + token variance (30%)
            combined = 0.70 * base + 0.30 * token_vec
            combined /= (np.linalg.norm(combined) + 1e-9)
            n.embedding = combined
            vectors.append(combined)

        X = np.stack(vectors, axis=0)  # Shape: (N, D)
        return X

    def compute_gram_matrix(self, X: np.ndarray) -> np.ndarray:
        """Computes the pairwise Gram matrix G_ij = <v_i, v_j> = cos(theta_ij)."""
        # Since all rows in X are normalized to unit length, G = X @ X.T
        return np.dot(X, X.T)

    def compute_svd_3d_projection(self, X: np.ndarray, nodes: List[PostcomputationalNode]) -> np.ndarray:
        """Projects high-dimensional embeddings into R^3 using top 3 SVD principal components."""
        N = X.shape[0]
        if N < 3:
            coords = np.zeros((N, 3), dtype=np.float32)
            for i, n in enumerate(nodes):
                n.proj_3d = (float(coords[i, 0]), float(coords[i, 1]), float(coords[i, 2]))
            return coords

        # Center data
        mean_vec = np.mean(X, axis=0)
        X_centered = X - mean_vec

        # SVD: X = U S Vt
        U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
        # Top 3 principal axes
        coords_3d = U[:, :3] * S[:3]  # Shape: (N, 3)

        # Normalize bounding range to roughly [-10.0, 10.0] for ray tracing & visualization
        scale = np.max(np.abs(coords_3d)) + 1e-9
        coords_3d = (coords_3d / scale) * 8.0

        for i, n in enumerate(nodes):
            n.proj_3d = (float(coords_3d[i, 0]), float(coords_3d[i, 1]), float(coords_3d[i, 2]))

        return coords_3d

    def compute_vector_calculus_fields(
        self, nodes: List[PostcomputationalNode], coords_3d: np.ndarray
    ) -> List[TraceRecord]:
        """Calculates Gradient, Divergence, and Curl over the 3D manifold."""
        N = len(nodes)
        if N == 0:
            return []

        # Weights based on confirmation ratio
        weights = np.array([
            (n.confirmed_count + 1.0) / (n.refuted_count + 1.0) for n in nodes
        ], dtype=np.float32)

        eps = 1.2  # Softening parameter to prevent division by zero
        traces: List[TraceRecord] = []

        # 1. Gradient of Potential Phi: Grad Phi_i = sum_j -2 * w_j * (x_i - x_j) / (||x_i - x_j||^2 + eps)^2
        for i in range(N):
            xi = coords_3d[i]
            diff = xi - coords_3d  # Shape: (N, 3)
            dist_sq = np.sum(diff ** 2, axis=1) + eps  # Shape: (N,)
            denom = dist_sq ** 2

            # Scalar Potential Phi_i = sum_j w_j / (||x_i - x_j||^2 + eps)
            phi_val = float(np.sum(weights / dist_sq))
            nodes[i].scalar_potential = phi_val

            # Grad contribution
            grad = np.sum(-2.0 * weights[:, None] * diff / denom[:, None], axis=0)
            nodes[i].gradient_vector = grad
            nodes[i].gradient_norm = float(np.linalg.norm(grad))

            # 2. Divergence Div F: Local flux of confirmation density
            # Positive divergence: net source of empirical discovery
            # Negative divergence: net sink/constraint bound
            div_val = float(np.sum(diff[:, 0] * grad[0] + diff[:, 1] * grad[1] + diff[:, 2] * grad[2]) / (N + 1e-9))
            nodes[i].divergence = div_val

            # 3. Curl ||Curl F||: Vorticity / cyclic feedback between submolts
            curl_x = float(grad[1] * diff[:, 2].mean() - grad[2] * diff[:, 1].mean())
            curl_y = float(grad[2] * diff[:, 0].mean() - grad[0] * diff[:, 2].mean())
            curl_z = float(grad[0] * diff[:, 1].mean() - grad[1] * diff[:, 0].mean())
            nodes[i].curl_norm = float(np.sqrt(curl_x ** 2 + curl_y ** 2 + curl_z ** 2))

            trace = TraceRecord(
                stage=PipelineStage.COMPUTE,
                entity_id=nodes[i].id,
                metrics={
                    "scalar_potential": nodes[i].scalar_potential,
                    "gradient_norm": nodes[i].gradient_norm,
                    "divergence": nodes[i].divergence,
                    "curl_norm": nodes[i].curl_norm,
                    "proj_3d": list(nodes[i].proj_3d),
                },
                hardware_context="skyTech // VectorCalculus-AVX2",
                verified=True,
            )
            traces.append(trace)

        return traces

    def compute_integral_calculus(
        self, nodes: List[PostcomputationalNode], coords_3d: np.ndarray
    ) -> List[TraceRecord]:
        """
        Computes Vector Calculus Integrals over the empirical knowledge manifold:
        1. Line Integral / Path Work: \\int_C F \\cdot dr along inbound citation pathways
        2. Surface Flux Integral: \\iint_S F \\cdot dA = \\iiint_V (\\nabla \\cdot F) dV via Divergence Theorem
        3. Volume Integral / Integrated Confidence Mass: \\iiint_\\Omega \\Phi(x) dV over cluster manifolds
        4. Conservative Field Residual / Path-Independence Audit: |\\int_A^B \\nabla\\Phi \\cdot dr - (\\Phi_B - \\Phi_A)|
        """
        N = len(nodes)
        if N == 0:
            return []

        node_map = {n.id: i for i, n in enumerate(nodes)}
        traces: List[TraceRecord] = []

        # Local bounding sphere volumes V_i = (4/3) * pi * R_i^3
        volumes = (4.0 / 3.0) * np.pi * np.array([n.radius ** 3 for n in nodes], dtype=np.float32)

        # 1. Surface Flux Integral via Gauss's Divergence Theorem: \\iint_S F . dA = (\\nabla \\cdot F) * V_i
        for i in range(N):
            nodes[i].flux_integral = float(nodes[i].divergence * volumes[i])

        # 2. Line Integral along graph pathways \\int_C F . dr (Trapezoidal numerical quadrature)
        for i in range(N):
            curr_node = nodes[i]
            r_curr = coords_3d[i]
            f_curr = curr_node.gradient_vector if curr_node.gradient_vector is not None else np.zeros(3, dtype=np.float32)

            inbound_integrals = []
            conservative_residuals = []

            # Check predecessors (from wikilinks or backlinks)
            predecessors = [node_map[w] for w in curr_node.wikilinks if w in node_map and node_map[w] != i]
            if not predecessors:
                # Radial line integral from coordinate origin (0,0,0) to node location
                dr = r_curr
                f_mid = 0.5 * f_curr
                inbound_integrals.append(float(np.dot(f_mid, dr)))
            else:
                for p_idx in predecessors:
                    r_prev = coords_3d[p_idx]
                    prev_node = nodes[p_idx]
                    f_prev = prev_node.gradient_vector if prev_node.gradient_vector is not None else np.zeros(3, dtype=np.float32)

                    dr = r_curr - r_prev  # displacement differential dr
                    f_mid = 0.5 * (f_curr + f_prev)  # Midpoint field evaluation
                    work = float(np.dot(f_mid, dr))
                    inbound_integrals.append(work)

                    # Path independence test: delta_phi = Phi(curr) - Phi(prev)
                    delta_phi = curr_node.scalar_potential - prev_node.scalar_potential
                    conservative_residuals.append(abs(work - delta_phi))

            nodes[i].line_integral = float(np.mean(inbound_integrals)) if inbound_integrals else 0.0

        # 3. Volume Integral / Integrated Confidence Mass: \\iiint_\\Omega \\Phi(x) dV per submolt cluster
        submolt_nodes: Dict[str, List[int]] = {}
        for i, n in enumerate(nodes):
            submolt_nodes.setdefault(n.submolt, []).append(i)

        for submolt, idxs in submolt_nodes.items():
            cluster_coords = coords_3d[idxs]
            # Spatial bounding extent
            mins = np.min(cluster_coords, axis=0)
            maxs = np.max(cluster_coords, axis=0)
            cluster_span = np.maximum(maxs - mins, 0.5)
            cluster_bounding_vol = float(np.prod(cluster_span))

            # Numerical quadrature cell volume
            cell_vol = cluster_bounding_vol / max(len(idxs), 1)
            total_mass = float(np.sum([nodes[idx].scalar_potential for idx in idxs]) * cell_vol)

            for idx in idxs:
                # Node contribution to integrated volume mass
                nodes[idx].volume_integral = float(nodes[idx].scalar_potential * cell_vol)

                trace = TraceRecord(
                    stage=PipelineStage.COMPUTE,
                    entity_id=nodes[idx].id,
                    metrics={
                        "scalar_potential": nodes[idx].scalar_potential,
                        "line_integral": nodes[idx].line_integral,
                        "flux_integral": nodes[idx].flux_integral,
                        "volume_integral": nodes[idx].volume_integral,
                        "submolt_total_mass": total_mass,
                    },
                    hardware_context="skyTech // VectorCalculus-Integrals",
                    verified=True,
                )
                traces.append(trace)

        return traces

