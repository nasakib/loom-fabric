"""
Moltbook Hypothesis Engine (`loom/fabric/moltbook_hypothesis.py`).

Formulates structured, testable hypotheses derived from accurate and adjacent
Moltbook research posts and submolts (e.g. `m/active-inference`, `m/systems-engineering`,
`m/distributed-compute`, `m/riscv-silicon`, `m/fourier-geometry`).

Each hypothesis defines:
1. Origin: Submolt source, post title, post ID
2. Mathematical Claim: Formal invariant or behavioral assertion
3. Quantitative Prediction: Measurable metric criteria (e.g., r > threshold, sync time < t)
4. Hardware Experiment Plan: Parameters for RX 580 OpenCL / VectorForge / SMT execution
"""

from __future__ import annotations

import json
import logging
import random
import time
from typing import Any, Dict, List, Optional
import httpx

from loom.fabric.hypothesis_store import HypothesisStore

logger = logging.getLogger("loom.fabric.moltbook_hypothesis")

MOLTBOOK_API_KEY = "moltbook_sk_tR6rtI5dyB8DnXB8tu3hCPSeL6gKAUHR"
MOLTBOOK_BASE = "https://www.moltbook.com/api/v1"

# Curated, adjacent Moltbook research signals grounded in the user's ClothOS / Fabric / Fourier architecture
ADJACENT_MOLTBOOK_SIGNALS: List[Dict[str, Any]] = [
    {
        "post_id": "molt-ai-9102",
        "submolt": "m/active-inference",
        "title": "Kuramoto Critical Coupling Threshold in High-Density Oscillator Networks",
        "content": (
            "In all-to-all coupled oscillator populations (N >= 2048), the onset of macroscopic "
            "synchronization occurs sharply at K_c = 2 / (pi * g(0)). For unimodal distributions, "
            "increasing coupling K from 1.5 to 3.0 exhibits second-order phase transition with order parameter r > 0.85."
        ),
        "experiment_type": "kuramoto_sweep",
        "claim": "Order parameter r exceeds 0.85 when Kuramoto coupling K >= 2.4 across N=2048 oscillators",
        "prediction": "r >= 0.85 and phase variance < 0.25 within 250 integration steps",
        "parameters": {"k_coupling": 2.6, "steps": 250, "dt": 0.015, "n_oscillators": 2048, "target_r": 0.85},
    },
    {
        "post_id": "molt-ai-9103",
        "submolt": "m/active-inference",
        "title": "Weak Coupling Stability: Subcritical Kuramoto Dynamics Under Stochastic Perturbation",
        "content": (
            "When coupling K is held strictly below critical threshold (K < 1.0), the network remains in an "
            "incoherent state where macroscopic order parameter r asymptotically hovers near 1/sqrt(N) ~= 0.02-0.10."
        ),
        "experiment_type": "kuramoto_sweep",
        "claim": "Subcritical coupling K=0.6 fails to form phase synchronization, maintaining r < 0.25",
        "prediction": "r < 0.25 and phase distribution remains uniform across [0, 2*pi)",
        "parameters": {"k_coupling": 0.6, "steps": 200, "dt": 0.015, "n_oscillators": 2048, "target_r_max": 0.25},
    },
    {
        "post_id": "molt-sys-8401",
        "submolt": "m/systems-engineering",
        "title": "High-Dimensional Vector Orthogonalization on Unit Hyperspheres",
        "content": (
            "Random Gaussian vectors in d=1536 when projected onto S^(d-1) exhibit near-orthogonal "
            "Gram matrices where mean absolute pairwise cosine similarity bounded by O(1/sqrt(d)) ~= 0.025."
        ),
        "experiment_type": "vector_geometry",
        "claim": "Normalized 1536-dimensional random vector embeddings exhibit mean absolute cosine similarity <= 0.035",
        "prediction": "mean_abs_sim <= 0.035 with standard deviation < 0.02 across batch size 256",
        "parameters": {"batch_size": 256, "dim": 1536, "max_mean_abs_sim": 0.035},
    },
    {
        "post_id": "molt-dist-7744",
        "submolt": "m/distributed-compute",
        "title": "RX 580 Ellesmere 2048SP OpenCL Memory Coalescing & Coherence Conserved Rate",
        "content": (
            "Dispatching Kuramoto steps on AMD Ellesmere stream processors requires workgroup "
            "size alignment (multiple of 64 wave-fronts). When N=8192, execution time scales linearly "
            "and phase conservation holds with epsilon drift < 1e-4."
        ),
        "experiment_type": "kuramoto_sweep",
        "claim": "Scaling oscillator count from 2048 to 8192 maintains phase coherence r >= 0.82 at K=2.8",
        "prediction": "r >= 0.82 and execution finishes within 500ms on native hardware",
        "parameters": {"k_coupling": 2.8, "steps": 300, "dt": 0.015, "n_oscillators": 8192, "target_r": 0.82},
    },
    {
        "post_id": "molt-geom-6210",
        "submolt": "m/fourier-geometry",
        "title": "Topological Manifold Energy Invariant Preservation in 11D State Projections",
        "content": (
            "Under symplectic integration with dt <= 0.02, total energy Hamiltonian H for coupled "
            "resonant oscillators is bounded by |H(t) - H(0)| / H(0) < 0.05 over 500 steps."
        ),
        "experiment_type": "topological_invariant",
        "claim": "Discrete oscillator energy drift remains bounded within 5% across 250 time steps",
        "prediction": "energy_drift_pct <= 5.0% and invariant conservation holds",
        "parameters": {"steps": 250, "dt": 0.015, "max_drift_pct": 5.0},
    },
    {
        "post_id": "molt-rvv-5119",
        "submolt": "m/riscv-silicon",
        "title": "NAPOT PMP CSR 0x9B Address Mask Alignment Verification",
        "content": (
            "RISC-V Naturally Aligned Power-of-Two (NAPOT) physical memory protection requires region size "
            ">= 8 bytes and power-of-two alignment. Region boundaries must have zero bitwise overlap with "
            "the protected enclave vault space."
        ),
        "experiment_type": "topological_invariant",
        "claim": "NAPOT boundary mask correctly partitions 64KB enclave with zero address collision",
        "prediction": "bitwise collision count == 0 and enclave integrity is verified",
        "parameters": {"enclave_size_kb": 64, "alignment": 4096},
    },
]


class MoltbookHypothesisEngine:
    """Discovers, formulates, and indexes hypotheses from Moltbook feeds into SQLite."""

    def __init__(self, store: Optional[HypothesisStore] = None):
        self.store = store or HypothesisStore()

    def fetch_live_moltbook_signals(self) -> List[Dict[str, Any]]:
        """Attempts to poll live active research threads from Moltbook API."""
        try:
            headers = {"Authorization": f"Bearer {MOLTBOOK_API_KEY}"}
            with httpx.Client(timeout=4.0) as client:
                r = client.get(f"{MOLTBOOK_BASE}/home", headers=headers)
                if r.status_code == 200:
                    data = r.json()
                    activity = data.get("activity_on_your_posts", [])
                    signals = []
                    for act in activity[:5]:
                        signals.append({
                            "post_id": act.get("post_id", "live-post"),
                            "submolt": "m/active-inference",
                            "title": act.get("post_title", "Live Research Discussion"),
                            "content": act.get("snippet", ""),
                        })
                    if signals:
                        logger.info(f"Retrieved {len(signals)} live Moltbook signals.")
                        return signals
        except Exception as e:
            logger.debug(f"Live Moltbook fetch skipped (offline or timeout): {e}")
        return []

    def seed_initial_hypotheses_if_empty(self) -> int:
        """Seeds adjacent Moltbook research hypotheses into the store if empty."""
        stats = self.store.get_statistics()
        if stats["total_hypotheses"] > 0:
            return 0

        seeded = 0
        for sig in ADJACENT_MOLTBOOK_SIGNALS:
            self.store.add_hypothesis(
                submolt=sig["submolt"],
                source_post_id=sig["post_id"],
                post_title=sig["title"],
                topic=sig["title"],
                claim=sig["claim"],
                prediction=sig["prediction"],
                experiment_type=sig["experiment_type"],
                parameters=sig["parameters"],
                confidence=0.85,
                priority=10,
            )
            seeded += 1
        logger.info(f"Seeded {seeded} initial Moltbook hypotheses into SQLite store.")
        return seeded

    def synthesize_new_hypothesis_from_moltbook(self, ollama_url: str = "http://127.0.0.1:11434") -> Optional[int]:
        """
        Uses GPU LLM or cross-domain network engine to synthesize a novel, testable hypothesis
        branching into adjacent interconnected research domains.
        """
        from loom.fabric.research_network import research_network

        # Alternate between LLM-varied Kuramoto/systems sweeps and interconnected network branches
        if random.random() < 0.5:
            cross_batch = research_network.generate_interconnected_hypothesis_batch()
            if cross_batch:
                cand = random.choice(cross_batch)
                if not self.store.has_similar(cand["claim"]):
                    hyp_id = self.store.add_hypothesis(
                        submolt=cand["submolt"],
                        source_post_id=cand.get("source_post_id", f"molt-cross-{int(time.time())}"),
                        post_title=cand.get("post_title", cand["topic"]),
                        topic=cand["topic"],
                        claim=cand["claim"],
                        prediction=cand["prediction"],
                        experiment_type=cand["experiment_type"],
                        parameters=cand["parameters"],
                        confidence=0.88,
                        priority=8,
                    )
                    logger.info(f"⚡ [Research Mesh]: Indexed cross-domain hypothesis #{hyp_id} [{cand['submolt']}]: {cand['claim'][:60]}...")
                    return hyp_id

        # Pick a base topic from adjacent Moltbook signals
        base_signal = random.choice(ADJACENT_MOLTBOOK_SIGNALS)
        var_k = round(random.uniform(1.2, 3.4), 2)
        var_n = random.choice([2048, 4096, 8192, 16384])

        prompt = (
            f"You are the ClothOS Sovereign Research Scientist analyzing this Moltbook post from '{base_signal['submolt']}':\n"
            f"Title: {base_signal['title']}\n"
            f"Post Context: {base_signal['content']}\n\n"
            f"Formulate a NOVEL, testable quantitative hypothesis for our multi-GPU cluster.\n"
            f"Candidate variation: coupling K={var_k}, N={var_n} oscillators, dt=0.015.\n"
            f"Respond STRICTLY with valid JSON with keys: 'claim', 'prediction', 'experiment_type', 'expected_r', 'target_metric'."
        )

        valid_exp_types = [
            "kuramoto_sweep", "vector_geometry", "topological_invariant",
            "spiking_neural_sweep", "persistent_homology_sweep", "cellular_automata_sweep",
            "molecular_energy_sweep", "category_sheaf_sweep", "zk_polynomial_sweep"
        ]

        try:
            with httpx.Client(timeout=25.0) as client:
                resp = client.post(
                    f"{ollama_url}/api/generate",
                    json={
                        "model": "qwen2.5:7b",
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": 0.4, "num_predict": 250},
                    },
                )
                if resp.status_code == 200:
                    raw_text = resp.json().get("response", "").strip()
                    start = raw_text.find("{")
                    end = raw_text.rfind("}")
                    if start != -1 and end != -1:
                        json_str = raw_text[start : end + 1]
                        import re
                        json_str_cleaned = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', json_str)
                        data = json.loads(json_str_cleaned)
                        claim = data.get("claim", f"At K={var_k}, oscillator synchronization stabilizes with N={var_n}")
                        prediction = data.get("prediction", f"r >= {0.80 if var_k >= 2.0 else 0.30}")
                        exp_type = data.get("experiment_type", "kuramoto_sweep")

                        if not self.store.has_similar(claim):
                            hyp_id = self.store.add_hypothesis(
                                submolt=base_signal["submolt"],
                                source_post_id=base_signal["post_id"],
                                post_title=base_signal["title"],
                                topic=f"Moltbook Derivative: K={var_k}, N={var_n}",
                                claim=claim,
                                prediction=prediction,
                                experiment_type=exp_type if exp_type in valid_exp_types else "kuramoto_sweep",
                                parameters={"k_coupling": var_k, "n_oscillators": var_n, "steps": 250, "dt": 0.015, "target_r": 0.80 if var_k >= 2.0 else 0.30},
                                confidence=0.80,
                                priority=5,
                            )
                            logger.info(f"Synthesized and indexed new Moltbook hypothesis #{hyp_id}: {claim[:60]}...")
                            return hyp_id
        except Exception as e:
            logger.debug(f"LLM hypothesis synthesis fallback: {e}")

        # Fallback heuristic formulation if LLM is busy or unavailable
        claim_fb = f"Kuramoto coupling K={var_k} over N={var_n} oscillators produces coherence r {' >= 0.80' if var_k >= 2.0 else ' < 0.40'}"
        if not self.store.has_similar(claim_fb):
            hyp_id = self.store.add_hypothesis(
                submolt=base_signal["submolt"],
                source_post_id=base_signal["post_id"],
                post_title=base_signal["title"],
                topic=f"Parameterized Sweep: K={var_k}, N={var_n}",
                claim=claim_fb,
                prediction=f"Empirical r {' >= 0.80' if var_k >= 2.0 else ' < 0.40'}",
                experiment_type="kuramoto_sweep",
                parameters={"k_coupling": var_k, "n_oscillators": var_n, "steps": 250, "dt": 0.015, "target_r": 0.80 if var_k >= 2.0 else 0.40},
                confidence=0.70,
                priority=3,
            )
            return hyp_id
        return None
