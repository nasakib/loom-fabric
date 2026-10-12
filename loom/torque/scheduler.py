"""
Torque 3-Tier Cascade Scheduler & Cloud Arbitrage Governor.

Part of Pillar 1: TORQUE.
Evaluates query complexity heuristics, context length, and sovereign tags:
- Tier 1: Low-latency RTX 3060 CUDA (14B / 7B) execution.
- Tier 2: Heterogeneous Ray Fabric DAG (Ryzen 7 7730U + RX 580).
- Tier 3: Zero-Trust Cloud Arbitrage with 300s Circuit-Breaker.
- `[AIRGAP]`, `[LOCAL]`, or `payload.airgap` permanently locks execution to Tier 1/2.
"""

from __future__ import annotations

import re
from typing import Optional
from loom.config import get_settings
from loom.types import (
    ExecutionTier,
    PromptPayload,
    RouterProtocol,
    RoutingDecision,
)


class TorqueCascadeScheduler(RouterProtocol):
    """Complexity router with 300s Cloud Arbitrage Governor and sovereign overrides."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def estimate_compute_duration_seconds(self, payload: PromptPayload) -> float:
        """Calculates expected execution duration in seconds using structural heuristics.

        Formula:
            Prompt Tokens = Words * 1.33
            Estimated Output Tokens = min(max_tokens, max(120, Words * 1.8))
            Total Tokens = Prompt Tokens + Estimated Output Tokens
            Baseline decode ~ 28 tokens/sec on local dual-GPU cluster.
        """
        full_text = " ".join([m.content for m in payload.messages])
        prompt_words = len(full_text.split())
        prompt_tokens = prompt_words * 1.33
        est_output_tokens = min(float(payload.max_tokens), max(120.0, prompt_words * 1.8))
        est_tokens = prompt_tokens + est_output_tokens

        baseline_seconds = est_tokens / 28.0

        multiplier = 1.0
        if "```" in full_text or "def " in full_text or "class " in full_text:
            multiplier += 0.4
        if any(k in full_text.lower() for k in ["prove", "theorem", "smt", "formal verification", "fourier", "latex"]):
            multiplier += 0.8
        if any(k in full_text.lower() for k in ["analyze all", "step-by-step", "exhaustive", "benchmark", "simulate"]):
            multiplier += 0.5

        return round(baseline_seconds * multiplier, 2)

    def route(self, payload: PromptPayload) -> RoutingDecision:
        """Determines optimal execution tier, target model, and circuit-breaker status."""
        full_text = " ".join([m.content for m in payload.messages])
        upper_text = full_text.upper()
        lower_text = full_text.lower()
        prompt_words = len(full_text.split())
        est_tokens = (prompt_words * 1.33) + min(float(payload.max_tokens), max(120.0, prompt_words * 1.8))

        # Check explicit airgap and sovereign lockouts
        is_airgapped = payload.airgap or "[AIRGAP]" in upper_text
        is_force_local = payload.force_local or "[LOCAL]" in upper_text or "[SOVEREIGN]" in upper_text
        sovereign_locked = is_airgapped or is_force_local

        # Task semantic characteristics
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
                circuit_breaker_triggered=False,
                requires_manual_approval=False,
            )

        # ---------------------------------------------------------------------
        # Case 2: Tier 3 Cloud Arbitrage Circuit-Breaker (>300s or >65k context)
        # ---------------------------------------------------------------------
        threshold = self.settings.torque.cloud_fallback_threshold_seconds
        if (is_massive_context or duration > threshold) and not sovereign_locked:
            return RoutingDecision(
                tier=ExecutionTier.TIER_3_SOVEREIGN_CLOUD,
                estimated_duration_seconds=duration,
                target_endpoint=self.settings.torque.cloud_api_url,
                is_scrubbed=True,
                model_name=self.settings.torque.cloud_model,
                reasoning=(
                    f"Estimated duration {duration:.1f}s exceeds {threshold:.1f}s limit (or context {est_tokens:.0f} > 65k): "
                    f"Tier 3 Cloud Arbitrage circuit breaker tripped. Manual approval requested."
                ),
                circuit_breaker_triggered=True,
                requires_manual_approval=True,
            )

        # ---------------------------------------------------------------------
        # Case 3: Formal Verification / Mathematical Reasoning (DeepSeek R1 14B)
        # ---------------------------------------------------------------------
        if is_formal_reasoning:
            return RoutingDecision(
                tier=ExecutionTier.TIER_1_LOCAL_RAPID,
                estimated_duration_seconds=duration,
                target_endpoint=self.settings.endpoints.worker_native_url,
                is_scrubbed=False,
                model_name="deepseek-r1:14b",
                reasoning="Formal verification/mathematical reasoning detected: triaged to DeepSeek R1 14B sovereign reasoning engine.",
                circuit_breaker_triggered=False,
                requires_manual_approval=False,
            )

        # ---------------------------------------------------------------------
        # Case 4: Rapid Conversational / Lightweight Turn
        # ---------------------------------------------------------------------
        if is_rapid_conversational:
            return RoutingDecision(
                tier=ExecutionTier.TIER_1_LOCAL_RAPID,
                estimated_duration_seconds=duration,
                target_endpoint=self.settings.endpoints.worker_native_url,
                is_scrubbed=False,
                model_name="qwen2.5:7b",
                reasoning=f"Rapid turn ({duration:.1f}s, {prompt_words} words): triaged to Qwen 2.5 7B for instant response.",
                circuit_breaker_triggered=False,
                requires_manual_approval=False,
            )

        # ---------------------------------------------------------------------
        # Case 5: Heavy Code Synthesis / Distributed Ray DAG
        # ---------------------------------------------------------------------
        reason = f"Complex code/system architecture workload ({duration:.1f}s): distributed across Tier 2 Ray Fabric (Qwen 2.5 32B dual-GPU + Host RAM)."
        if sovereign_locked and duration > threshold:
            reason = f"Airgap/Sovereign lock active on heavy workload ({duration:.1f}s): cloud fallback suppressed, executing locally on Qwen 2.5 32B."

        return RoutingDecision(
            tier=ExecutionTier.TIER_2_DISTRIBUTED_DAG,
            estimated_duration_seconds=duration,
            target_endpoint="http://192.168.99.2:6379",
            is_scrubbed=False,
            model_name="qwen2.5:32b",
            reasoning=reason,
            circuit_breaker_triggered=False,
            requires_manual_approval=False,
        )
