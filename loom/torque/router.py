"""
Torque Complexity Router and Sovereign Arbitrage Engine.

Part of Pillar 1: TORQUE.
Analyzes prompt payload heuristics, structure, and tags:
- Forced [LOCAL] or [SOVEREIGN] tags enforce local cluster execution.
- Tier 1: Low-latency / conversational queries (<10s estimated) -> Local RTX 3060 (14B/7B).
- Tier 2: DAG / multi-step code generation / reasoning (10s-300s) -> Heterogeneous Ray Fabric.
- Tier 3: Ultra-heavy (>300s estimated) -> Scrubbed Zero-Trust Cloud Arbitrage with automatic stream rehydration.

Rust Migration Blueprint:
    In the native `loom-core` Rust crate:
    ```rust
    pub struct TorqueRouter {
        config: TorqueSecurityConfig,
        scrubber: Arc<TorqueScrubber>,
    }

    impl ComplexityRouter for TorqueRouter {
        fn route(&self, payload: &PromptPayload) -> RoutingDecision { ... }
    }
    ```
"""

from __future__ import annotations

import re
from typing import List
from loom.config import get_settings
from loom.types import ExecutionTier, PromptPayload, RouterProtocol, RoutingDecision


class TorqueRouter:
    """Evaluates query complexity and assigns execution to Tier 1, Tier 2, or Tier 3.

    Implements:
        `RouterProtocol`
    """

    def __init__(self) -> None:
        self.settings = get_settings()

    def estimate_compute_duration_seconds(self, payload: PromptPayload) -> float:
        """Calculates expected execution duration in seconds using structural heuristics.

        Formula:
            Tokens = Prompt Words * 1.33 + Max Output Tokens
            Complexity Multiplier based on presence of code blocks, formal proofs, or deep reasoning keywords.
        """
        full_text = " ".join([m.content for m in payload.messages])
        prompt_words = len(full_text.split())
        est_tokens = (prompt_words * 1.33) + payload.max_tokens

        # Baseline: ~25 tokens/second on local dual-GPU cluster
        baseline_seconds = est_tokens / 25.0

        # Complexity multipliers:
        multiplier = 1.0
        if "```" in full_text or "def " in full_text or "class " in full_text:
            multiplier += 0.5  # Code generation requires deeper reasoning
        if any(k in full_text.lower() for k in ["prove", "theorem", "smt", "formal verification", "fourier", "latex"]):
            multiplier += 1.2  # Mathematical verification tasks
        if any(k in full_text.lower() for k in ["analyze all", "step-by-step", "exhaustive", "benchmark", "simulate"]):
            multiplier += 0.8  # Large reasoning chain

        return round(baseline_seconds * multiplier, 2)

    def route(self, payload: PromptPayload) -> RoutingDecision:
        """Determines the optimal execution tier for the incoming prompt payload.

        Args:
            payload: Typed prompt DTO.

        Returns:
            RoutingDecision specifying the target execution tier, endpoint, and scrubbing requirement.
        """
        full_text = " ".join([m.content for m in payload.messages])
        upper_text = full_text.upper()

        # Rule 1: Forced Sovereign Local Override via [LOCAL] or [SOVEREIGN] or force_local flag
        if payload.force_local or "[LOCAL]" in upper_text or "[SOVEREIGN]" in upper_text:
            duration = self.estimate_compute_duration_seconds(payload)
            if duration <= 15.0:
                return RoutingDecision(
                    tier=ExecutionTier.TIER_1_LOCAL_RAPID,
                    estimated_duration_seconds=duration,
                    target_endpoint=self.settings.endpoints.worker_native_url,
                    is_scrubbed=False,
                    model_name="deepseek-r1:14b",
                    reasoning="Explicit [LOCAL] tag: routed to Tier 1 rapid RTX 3060 CUDA backend.",
                )
            else:
                return RoutingDecision(
                    tier=ExecutionTier.TIER_2_DISTRIBUTED_DAG,
                    estimated_duration_seconds=duration,
                    target_endpoint="http://192.168.99.2:6379",
                    is_scrubbed=False,
                    model_name="qwen2.5:32b",
                    reasoning="Explicit [LOCAL] tag on heavy prompt: routed to Tier 2 Ray heterogeneous mesh.",
                )

        # Rule 2: Compute Duration Heuristic
        duration = self.estimate_compute_duration_seconds(payload)
        threshold = self.settings.torque.cloud_fallback_threshold_seconds

        # Tier 3: Long-running compute (>300s) -> Scrubbed Zero-Trust Cloud Arbitrage
        if duration > threshold:
            return RoutingDecision(
                tier=ExecutionTier.TIER_3_SOVEREIGN_CLOUD,
                estimated_duration_seconds=duration,
                target_endpoint=self.settings.torque.cloud_api_url,
                is_scrubbed=True,
                model_name=self.settings.torque.cloud_model,
                reasoning=f"Estimated duration {duration:.1f}s exceeds {threshold:.1f}s limit: routed to Tier 3 Zero-Trust Cloud Arbitrage.",
            )

        # Tier 1: Fast conversational queries (estimated <= 12 seconds) -> Local RTX 3060
        if duration <= 12.0:
            return RoutingDecision(
                tier=ExecutionTier.TIER_1_LOCAL_RAPID,
                estimated_duration_seconds=duration,
                target_endpoint=self.settings.endpoints.worker_native_url,
                is_scrubbed=False,
                model_name="deepseek-r1:14b",
                reasoning=f"Rapid query ({duration:.1f}s): allocated to Tier 1 local RTX 3060.",
            )

        # Tier 2: Medium/heavy workloads (12s to 300s) -> Ray Heterogeneous Mesh
        return RoutingDecision(
            tier=ExecutionTier.TIER_2_DISTRIBUTED_DAG,
            estimated_duration_seconds=duration,
            target_endpoint="http://192.168.99.2:6379",
            is_scrubbed=False,
            model_name="qwen2.5:32b",
            reasoning=f"Complex DAG/reasoning workload ({duration:.1f}s): distributed across Tier 2 Ray Fabric.",
        )
