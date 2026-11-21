# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
#
# Part of Pillar 1 & 2: FABRIC / CLOTHOS / LOOM PRECISION TOOLCHAIN.
r"""
Inference Intelligence Suite (`loom/tools/inference_engine.py`).

Mathematical Tool Suite for Deep Probabilistic & Variational Inference:
1. VariationalBayesTool:
   - Variational Free Energy: $\mathcal{F} = D_{KL}(q(\theta) \parallel p(\theta)) - \mathbb{E}_q[\ln p(y|\theta)]$
   - Precision-weighted prediction error: $\varepsilon = \Pi_y (y - g(\mu))$
   - Active Inference belief update dynamics: $\dot{\mu} = -\nabla_\mu \mathcal{F}$
2. InformationGeometryTool:
   - Fisher Information Metric Tensor: $G_{ij}(\theta) = \mathbb{E}[\partial_i \ln p \cdot \partial_j \ln p]$
   - Natural Gradient: $\tilde{\nabla} L = G^{-1} \nabla L$
   - Riemannian Geodesic Distance along statistical manifolds
3. InformationTheoryTool:
   - Shannon Entropy $H(P)$, Rényi Entropy $H_\alpha(P)$
   - Kullback-Leibler Divergence $D_{KL}(P \parallel Q)$, Jensen-Shannon Divergence $D_{JS}(P \parallel Q)$
   - Mutual Information $I(X; Y)$
4. SpectralOperatorTool:
   - Singular Value Decomposition (SVD): $A = U \Sigma V^T$
   - Spectral Radius $\rho(A)$ and Spectral Gap $\Delta\lambda = |\lambda_1| - |\lambda_2|$
   - Resolvent Operator: $R(z, A) = (z I - A)^{-1}$
   - Optimal Rank-$k$ Subspace Projection (Eckart-Young-Mirsky)
5. MarkovKernelTool:
   - Ergodic transition matrix analysis, Perron-Frobenius stationary distribution $\pi P = \pi$
   - Mixing time bound: $\tau_{\text{mix}}(\epsilon) \le \frac{1}{1 - |\lambda_2|} \ln \frac{1}{\epsilon \min \pi}$
"""

from __future__ import annotations

import logging
import math
from typing import Any, Dict, List, Optional, Sequence, Tuple
import numpy as np

logger = logging.getLogger("loom.tools.inference_engine")


class VariationalBayesTool:
    """
    Mathematical tool for Variational Inference, Bayesian Belief Updating,
    and Active Inference Free Energy minimization.
    """

    def compute_free_energy(
        self,
        mu_prior: Sequence[float],
        sigma_prior: Sequence[Sequence[float]] | Sequence[float],
        mu_posterior: Sequence[float],
        sigma_posterior: Sequence[Sequence[float]] | Sequence[float],
        observation: Sequence[float],
        predicted_obs: Sequence[float],
        obs_precision: Sequence[Sequence[float]] | Sequence[float],
    ) -> Dict[str, Any]:
        r"""
        Computes the Variational Free Energy $\mathcal{F} = \text{Complexity} + \text{Accuracy}$.
        $\mathcal{F} = D_{KL}(q(\theta) \parallel p(\theta)) - \mathbb{E}_q[\ln p(y|\theta)]$
        """
        mu_0 = np.asarray(mu_prior, dtype=np.float64)
        mu = np.asarray(mu_posterior, dtype=np.float64)
        y = np.asarray(observation, dtype=np.float64)
        g_mu = np.asarray(predicted_obs, dtype=np.float64)
        dim = len(mu)

        # Handle covariance inputs (diagonal or full)
        cov_0 = np.diag(sigma_prior) if np.ndim(sigma_prior) == 1 else np.asarray(sigma_prior, dtype=np.float64)
        cov = np.diag(sigma_posterior) if np.ndim(sigma_posterior) == 1 else np.asarray(sigma_posterior, dtype=np.float64)
        pi_y = np.diag(obs_precision) if np.ndim(obs_precision) == 1 else np.asarray(obs_precision, dtype=np.float64)

        # Invert prior covariance with regularization
        inv_cov_0 = np.linalg.pinv(cov_0 + 1e-9 * np.eye(dim))
        
        # 1. KL Divergence (Complexity)
        diff_mu = mu - mu_0
        trace_term = float(np.trace(inv_cov_0 @ cov))
        quad_term = float(diff_mu.T @ inv_cov_0 @ diff_mu)
        sign_0, logdet_0 = np.linalg.slogdet(cov_0 + 1e-9 * np.eye(dim))
        sign_q, logdet_q = np.linalg.slogdet(cov + 1e-9 * np.eye(dim))
        logdet_ratio = float(logdet_0 - logdet_q)
        kl_complexity = 0.5 * (trace_term + quad_term - dim + logdet_ratio)
        kl_complexity = max(0.0, kl_complexity)

        # 2. Prediction Error & Inaccuracy
        err_y = y - g_mu
        weighted_sq_err = float(err_y.T @ pi_y @ err_y)
        accuracy_inaccuracy = 0.5 * weighted_sq_err

        # Total Variational Free Energy
        free_energy = kl_complexity + accuracy_inaccuracy

        # Precision-weighted prediction error vector
        pw_error = (pi_y @ err_y).tolist()

        return {
            "free_energy": float(free_energy),
            "complexity_kl": float(kl_complexity),
            "accuracy_inaccuracy": float(accuracy_inaccuracy),
            "prediction_error_l2": float(np.linalg.norm(err_y)),
            "precision_weighted_error": [round(x, 6) for x in pw_error],
            "converged": float(free_energy) < 0.05,
        }

    def update_beliefs(
        self,
        current_mu: Sequence[float],
        mu_prior: Sequence[float],
        prior_precision: Sequence[float],
        observation: Sequence[float],
        predicted_obs: Sequence[float],
        obs_precision: Sequence[float],
        learning_rate: float = 0.1,
    ) -> Dict[str, Any]:
        r"""
        Performs one gradient step of Active Inference belief updating:
        $\dot{\mu} = \Pi_0(\mu_0 - \mu) + J^T \Pi_y(y - g(\mu))$
        """
        mu = np.asarray(current_mu, dtype=np.float64)
        mu_0 = np.asarray(mu_prior, dtype=np.float64)
        pi_0 = np.asarray(prior_precision, dtype=np.float64)
        y = np.asarray(observation, dtype=np.float64)
        g_mu = np.asarray(predicted_obs, dtype=np.float64)
        pi_y = np.asarray(obs_precision, dtype=np.float64)

        # Prior gradient pull
        prior_gradient = pi_0 * (mu_0 - mu)

        # Observation sensory prediction error pull (assuming identity Jacobian J=I)
        obs_error = y - g_mu
        sensory_gradient = pi_y * obs_error

        # Net gradient & update
        net_flow = prior_gradient + sensory_gradient
        updated_mu = mu + learning_rate * net_flow

        return {
            "updated_mu": [round(float(x), 6) for x in updated_mu],
            "belief_shift_norm": float(np.linalg.norm(updated_mu - mu)),
            "sensory_pull_norm": float(np.linalg.norm(sensory_gradient)),
            "prior_pull_norm": float(np.linalg.norm(prior_gradient)),
            "learning_rate": learning_rate,
        }


class InformationGeometryTool:
    """
    Mathematical tool for Information Geometry on statistical manifolds:
    Fisher Information Metric, Natural Gradient, and Geodesic Distances.
    """

    def compute_fisher_metric(
        self,
        probabilities: Sequence[Sequence[float]],
        grad_log_p: Sequence[Sequence[Sequence[float]]],
    ) -> Dict[str, Any]:
        r"""
        Computes the empirical Fisher Information Matrix:
        $G_{ij} = \sum_x p(x) \frac{\partial \ln p(x)}{\partial \theta_i} \frac{\partial \ln p(x)}{\partial \theta_j}$
        """
        p = np.asarray(probabilities, dtype=np.float64)
        grads = np.asarray(grad_log_p, dtype=np.float64)  # shape (n_samples, n_params)
        n_samples, n_params = grads.shape

        # Weight samples by probability distribution if normalized
        weights = p.flatten() if p.size == n_samples else np.ones(n_samples) / n_samples
        weights = weights / np.sum(weights)

        # Compute Fisher matrix
        fisher = np.zeros((n_params, n_params), dtype=np.float64)
        for i in range(n_samples):
            g = grads[i : i + 1]  # shape (1, n_params)
            fisher += weights[i] * (g.T @ g)

        # Condition number & determinant
        det = float(np.linalg.det(fisher))
        cond = float(np.linalg.cond(fisher)) if det > 1e-12 else float("inf")

        return {
            "fisher_matrix": [[round(float(v), 6) for v in row] for row in fisher],
            "determinant": det,
            "condition_number": cond,
            "is_positive_definite": bool(np.all(np.linalg.eigvalsh(fisher) > 1e-9)),
        }

    def compute_natural_gradient(
        self,
        euclidean_gradient: Sequence[float],
        fisher_matrix: Sequence[Sequence[float]],
        damping: float = 1e-4,
    ) -> Dict[str, Any]:
        r"""
        Computes the natural gradient $\tilde{\nabla} L = G^{-1} \nabla L$
        along the Riemannian manifold.
        """
        g_euc = np.asarray(euclidean_gradient, dtype=np.float64)
        f_mat = np.asarray(fisher_matrix, dtype=np.float64)
        dim = len(g_euc)

        # Regularized inverse for stable Riemannian inversion
        reg_f = f_mat + damping * np.eye(dim)
        nat_grad = np.linalg.solve(reg_f, g_euc)

        cosine_alignment = float(
            np.dot(g_euc, nat_grad) / (np.linalg.norm(g_euc) * np.linalg.norm(nat_grad) + 1e-12)
        )

        return {
            "natural_gradient": [round(float(x), 6) for x in nat_grad],
            "euclidean_norm": float(np.linalg.norm(g_euc)),
            "natural_norm": float(np.sqrt(np.dot(nat_grad, g_euc))),
            "manifold_acceleration": float(np.linalg.norm(nat_grad) / (np.linalg.norm(g_euc) + 1e-12)),
            "cosine_alignment": cosine_alignment,
        }

    def compute_riemannian_distance(
        self,
        theta_1: Sequence[float],
        theta_2: Sequence[float],
        metric_tensor: Sequence[Sequence[float]],
    ) -> float:
        r"""
        Local Riemannian distance approximation:
        $d_R(\theta_1, \theta_2) = \sqrt{(\theta_1 - \theta_2)^T G (\theta_1 - \theta_2)}$
        """
        t1 = np.asarray(theta_1, dtype=np.float64)
        t2 = np.asarray(theta_2, dtype=np.float64)
        g = np.asarray(metric_tensor, dtype=np.float64)
        diff = t1 - t2
        sq_dist = float(diff.T @ g @ diff)
        return float(np.sqrt(max(0.0, sq_dist)))


class InformationTheoryTool:
    """
    Mathematical tool for Shannon, Rényi, Kullback-Leibler, and Jensen-Shannon
    information metrology.
    """

    def shannon_entropy(self, probabilities: Sequence[float], base: float = 2.0) -> float:
        r"""$H(P) = -\sum_i p_i \log_b(p_i)$"""
        p = np.asarray(probabilities, dtype=np.float64)
        p = p[p > 0]
        if len(p) == 0:
            return 0.0
        p = p / np.sum(p)
        return float(-np.sum(p * (np.log(p) / np.log(base))))

    def renyi_entropy(self, probabilities: Sequence[float], alpha: float = 2.0, base: float = 2.0) -> float:
        r"""$H_\alpha(P) = \frac{1}{1-\alpha} \log_b \sum_i p_i^\alpha$"""
        if math.isclose(alpha, 1.0):
            return self.shannon_entropy(probabilities, base=base)
        p = np.asarray(probabilities, dtype=np.float64)
        p = p[p > 0]
        p = p / np.sum(p)
        sum_p_alpha = float(np.sum(p**alpha))
        return float((1.0 / (1.0 - alpha)) * (np.log(sum_p_alpha) / np.log(base)))

    def kl_divergence(self, p_dist: Sequence[float], q_dist: Sequence[float], eps: float = 1e-12) -> float:
        r"""$D_{KL}(P \parallel Q) = \sum_i p_i \ln \frac{p_i}{q_i}$"""
        p = np.asarray(p_dist, dtype=np.float64) + eps
        q = np.asarray(q_dist, dtype=np.float64) + eps
        p = p / np.sum(p)
        q = q / np.sum(q)
        return float(np.sum(p * np.log(p / q)))

    def jensen_shannon_divergence(self, p_dist: Sequence[float], q_dist: Sequence[float]) -> float:
        r"""$D_{JS}(P \parallel Q) = \frac{1}{2} D_{KL}(P \parallel M) + \frac{1}{2} D_{KL}(Q \parallel M)$"""
        p = np.asarray(p_dist, dtype=np.float64)
        q = np.asarray(q_dist, dtype=np.float64)
        p = p / np.sum(p)
        q = q / np.sum(q)
        m = 0.5 * (p + q)
        return float(0.5 * self.kl_divergence(p, m) + 0.5 * self.kl_divergence(q, m))

    def mutual_information(self, joint_probabilities: Sequence[Sequence[float]]) -> float:
        r"""$I(X; Y) = \sum_{x, y} p(x, y) \log_2 \frac{p(x, y)}{p(x) p(y)}$"""
        pxy = np.asarray(joint_probabilities, dtype=np.float64)
        pxy = pxy / np.sum(pxy)
        px = np.sum(pxy, axis=1)
        py = np.sum(pxy, axis=0)

        mi = 0.0
        for i in range(len(px)):
            for j in range(len(py)):
                if pxy[i, j] > 1e-12 and px[i] > 1e-12 and py[j] > 1e-12:
                    mi += pxy[i, j] * np.log2(pxy[i, j] / (px[i] * py[j]))
        return float(max(0.0, mi))


class SpectralOperatorTool:
    """
    Mathematical tool for Spectral Decomposition, Singular Values,
    Resolvent Operators, and Subspace Projections.
    """

    def spectral_analysis(self, matrix: Sequence[Sequence[float]]) -> Dict[str, Any]:
        r"""
        Computes eigenvalues, singular values, spectral radius $\rho(A)$,
        and the spectral gap $\Delta\lambda = |\lambda_1| - |\lambda_2|$.
        """
        mat = np.asarray(matrix, dtype=np.float64)
        eigvals = np.linalg.eigvals(mat)
        abs_eigs = np.sort(np.abs(eigvals))[::-1]

        spectral_radius = float(abs_eigs[0])
        spectral_gap = float(abs_eigs[0] - abs_eigs[1]) if len(abs_eigs) > 1 else float(abs_eigs[0])

        # Singular Value Decomposition
        u, s, vh = np.linalg.svd(mat)
        frobenius_norm = float(np.linalg.norm(mat, "fro"))
        energy_90_idx = int(np.searchsorted(np.cumsum(s**2) / np.sum(s**2), 0.90) + 1)

        return {
            "spectral_radius": spectral_radius,
            "spectral_gap": spectral_gap,
            "singular_values": [round(float(v), 6) for v in s[:10]],
            "frobenius_norm": frobenius_norm,
            "rank_for_90_pct_energy": energy_90_idx,
            "condition_number": float(s[0] / (s[-1] + 1e-12)),
        }

    def low_rank_project(self, matrix: Sequence[Sequence[float]], rank: int) -> List[List[float]]:
        r"""
        Eckart-Young-Mirsky optimal rank-$k$ projection via truncated SVD.
        $A_k = \sum_{i=1}^k \sigma_i u_i v_i^T$
        """
        mat = np.asarray(matrix, dtype=np.float64)
        u, s, vh = np.linalg.svd(mat, full_matrices=False)
        k = min(rank, len(s))
        approx = (u[:, :k] * s[:k]) @ vh[:k, :]
        return [[round(float(v), 6) for v in row] for row in approx]


class MarkovKernelTool:
    """
    Mathematical tool for stochastic Markov kernels, ergodic contraction,
    and Perron-Frobenius stationary distributions.
    """

    def compute_stationary_distribution(
        self, transition_matrix: Sequence[Sequence[float]]
    ) -> Dict[str, Any]:
        r"""
        Computes the stationary distribution $\pi P = \pi$ as the left eigenvector
        corresponding to eigenvalue $\lambda = 1$.
        """
        p = np.asarray(transition_matrix, dtype=np.float64)
        # Normalize rows to ensure stochasticity
        row_sums = p.sum(axis=1, keepdims=True)
        p = np.divide(p, row_sums, out=np.zeros_like(p), where=row_sums > 0)

        # Eigenvalue problem for P.T
        eigvals, eigvecs = np.linalg.eig(p.T)
        # Find index of eigenvalue closest to 1.0
        idx = int(np.argmin(np.abs(eigvals - 1.0)))
        pi = np.real(eigvecs[:, idx])
        pi = pi / np.sum(pi)  # Normalize to simplex

        # Second largest eigenvalue for mixing rate
        sorted_eigs = np.sort(np.abs(eigvals))[::-1]
        lambda_2 = float(sorted_eigs[1]) if len(sorted_eigs) > 1 else 0.0
        spectral_gap = 1.0 - lambda_2

        # Mixing time upper bound: \tau_mix(0.1) \approx \ln(1 / (0.1 * min(pi))) / spectral_gap
        min_pi = float(np.min(pi[pi > 0])) if np.any(pi > 0) else 1e-6
        mixing_time_bound = float(np.log(10.0 / min_pi) / max(spectral_gap, 1e-4))

        return {
            "stationary_distribution": [round(float(x), 6) for x in pi],
            "second_eigenvalue": round(lambda_2, 6),
            "spectral_gap": round(spectral_gap, 6),
            "mixing_time_steps_bound": round(mixing_time_bound, 2),
            "is_ergodic": lambda_2 < 0.999,
        }


class InferenceIntelligenceSuite:
    """
    Unified Inference Intelligence Tooling Suite uniting Variational Bayes,
    Information Geometry, Information Theory, Spectral Operators, and Markov Kernels.
    """

    def __init__(self):
        self.bayes = VariationalBayesTool()
        self.geometry = InformationGeometryTool()
        self.info = InformationTheoryTool()
        self.spectral = SpectralOperatorTool()
        self.markov = MarkovKernelTool()

    def get_status(self) -> Dict[str, Any]:
        return {
            "status": "OPERATIONAL",
            "tools": [
                "VariationalBayesTool",
                "InformationGeometryTool",
                "InformationTheoryTool",
                "SpectralOperatorTool",
                "MarkovKernelTool",
            ],
            "capabilities": [
                "variational_free_energy",
                "active_inference_belief_updating",
                "fisher_metric_tensor",
                "natural_gradient",
                "renyi_entropy",
                "jensen_shannon_divergence",
                "spectral_gap",
                "perron_frobenius_stationary_distribution",
            ],
        }
