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
            Prompt Tokens = Prompt Words * 1.33
            Estimated Output Tokens = min(max_tokens, max(120, prompt_words * 1.8))
            Total Tokens = Prompt Tokens + Estimated Output Tokens
            Baseline decode ~ 28 tokens/sec on local dual-GPU cluster.
        """
        full_text = " ".join([m.content for m in payload.messages])
        prompt_words = len(full_text.split())
        prompt_tokens = prompt_words * 1.33
        est_output_tokens = min(float(payload.max_tokens), max(120.0, prompt_words * 1.8))
        est_tokens = prompt_tokens + est_output_tokens

        # Baseline: ~28 tokens/second on local dual-GPU cluster
        baseline_seconds = est_tokens / 28.0

        # Complexity multipliers:
        multiplier = 1.0
        if "```" in full_text or "def " in full_text or "class " in full_text:
            multiplier += 0.4  # Code generation requires deeper reasoning
        if any(k in full_text.lower() for k in ["prove", "theorem", "smt", "formal verification", "fourier", "latex"]):
            multiplier += 0.8  # Mathematical verification tasks
        if any(k in full_text.lower() for k in ["analyze all", "step-by-step", "exhaustive", "benchmark", "simulate"]):
            multiplier += 0.5  # Large reasoning chain

        return round(baseline_seconds * multiplier, 2)

    def route(self, payload: PromptPayload) -> RoutingDecision:
        """Determines the optimal execution tier and model for the incoming prompt payload.

        Args:
            payload: Typed prompt DTO.

        Returns:
            RoutingDecision specifying the target execution tier, endpoint, model, and scrubbing requirement.
        """
        full_text = " ".join([m.content for m in payload.messages])
        upper_text = full_text.upper()
        lower_text = full_text.lower()
        prompt_words = len(full_text.split())
        est_tokens = (prompt_words * 1.33) + min(float(payload.max_tokens), max(120.0, prompt_words * 1.8))

        # Check intent characteristics
        is_compaction = any(
            k in lower_text
            for k in [
                "summarize the conversation",
                "compaction",
                "cut-point",
                "historical context summary",
                "condense previous messages",
                "condense the conversation",
            ]
        )
        is_formal_reasoning = any(
            k in lower_text
            for k in [
                "prove",
                "theorem",
                "smt",
                "formal verification",
                "fourier's library",
                "fourierslibrary",
                "z3",
                "axiom",
                "lean",
                "coq",
                "formal logic",
                "logic puzzle",
                "deduction",
            ]
        )
        is_code_synthesis = (
            "```" in full_text
            or "def " in full_text
            or "class " in full_text
            or any(k in lower_text for k in ["refactor", "architecture", "microkernel", "riscv", "rust crate", "component"])
        )
        is_rapid_conversational = prompt_words < 120 and not is_code_synthesis and not is_formal_reasoning
        is_massive_context = est_tokens > 65536

        # Check explicit sovereign flags
        force_sovereign = payload.force_local or "[LOCAL]" in upper_text or "[SOVEREIGN]" in upper_text
        duration = self.estimate_compute_duration_seconds(payload)

        # ---------------------------------------------------------------------
        # Case 1: Compaction Triage (Always Tier 1 Rapid to prevent timeouts)
        # ---------------------------------------------------------------------
        if is_compaction:
            return RoutingDecision(
                tier=ExecutionTier.TIER_1_LOCAL_RAPID,
                estimated_duration_seconds=min(duration, 3.5),
                target_endpoint=self.settings.endpoints.worker_native_url,
                is_scrubbed=False,
                model_name="qwen2.5:7b",
                reasoning="Compaction turn detected: triaged to Tier 1 Qwen 2.5 7B (pure CUDA) for zero-timeout execution.",
            )

        # ---------------------------------------------------------------------
        # Case 2: Extreme Context (>65k tokens) or Multimodal (Cloud Arbitrage)
        # ---------------------------------------------------------------------
        threshold = self.settings.torque.cloud_fallback_threshold_seconds
        if (is_massive_context or duration > threshold) and not force_sovereign:
            return RoutingDecision(
                tier=ExecutionTier.TIER_3_SOVEREIGN_CLOUD,
                estimated_duration_seconds=duration,
                target_endpoint=self.settings.torque.cloud_api_url,
                is_scrubbed=True,
                model_name=self.settings.torque.cloud_model,
                reasoning=f"Compute requirements (tokens: {est_tokens:.0f}, est: {duration:.1f}s) exceed local budget: routed to Tier 3 Zero-Trust Cloud Arbitrage with sovereign entity scrubbing.",
            )

        # ---------------------------------------------------------------------
        # Case 3: Formal Verification / Math / Proofs (Sovereign DeepSeek R1 14B)
        # ---------------------------------------------------------------------
        if is_formal_reasoning:
            return RoutingDecision(
                tier=ExecutionTier.TIER_1_LOCAL_RAPID,
                estimated_duration_seconds=duration,
                target_endpoint=self.settings.endpoints.worker_native_url,
                is_scrubbed=False,
                model_name="deepseek-r1:14b",
                reasoning="Formal verification/mathematical reasoning detected: triaged to DeepSeek R1 14B sovereign reasoning engine.",
            )

        # ---------------------------------------------------------------------
        # Case 4: Rapid Conversational / Heartbeat / Quick Turn
        # ---------------------------------------------------------------------
        if is_rapid_conversational:
            return RoutingDecision(
                tier=ExecutionTier.TIER_1_LOCAL_RAPID,
                estimated_duration_seconds=duration,
                target_endpoint=self.settings.endpoints.worker_native_url,
                is_scrubbed=False,
                model_name="qwen2.5:7b",
                reasoning=f"Rapid turn ({duration:.1f}s, {prompt_words} words): triaged to Qwen 2.5 7B for instant sub-second response.",
            )

        # ---------------------------------------------------------------------
        # Case 5: Heavy Code Synthesis / Multi-File / Architecture / Sovereign DAG
        # ---------------------------------------------------------------------
        target_model = "qwen2.5:32b"
        reason = f"Complex code/system architecture workload ({duration:.1f}s): distributed across Tier 2 Ray Fabric (Qwen 2.5 32B dual-GPU + Host RAM)."
        if force_sovereign and duration > threshold:
            reason = f"Forced [SOVEREIGN] override active on heavy workload ({duration:.1f}s): executed locally on Qwen 2.5 32B."

        return RoutingDecision(
            tier=ExecutionTier.TIER_2_DISTRIBUTED_DAG,
            estimated_duration_seconds=duration,
            target_endpoint="http://192.168.99.2:6379",
            is_scrubbed=False,
            model_name=target_model,
            reasoning=reason,
        )
