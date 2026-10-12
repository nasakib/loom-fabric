"""
Unit tests for Pillar 1: TORQUE Zero-Trust Scrubber and Complexity Router.
"""

import pytest
from loom.torque.scrubber import TorqueScrubber, RehydrationVault
from loom.torque.router import TorqueRouter
from loom.types import ExecutionTier, PromptPayload, ChatMessageDTO


def test_torque_scrubber_proprietary_terms():
    """Verifies that proprietary projects are detected, replaced with synthetic tokens, and rehydrated."""
    scrubber = TorqueScrubber()
    sample_text = "Analyzing formal proofs in fouriersLibrary using VectorForge and Mycos engine."

    scrub_result = scrubber.tokenize_and_store(sample_text)

    # Proprietary terms must not be present in scrubbed text
    assert "fouriersLibrary" not in scrub_result.scrubbed_text
    assert "VectorForge" not in scrub_result.scrubbed_text
    assert "Mycos" not in scrub_result.scrubbed_text

    # Synthetic tokens must be injected
    assert "<<IP_" in scrub_result.scrubbed_text
    assert scrub_result.replacements_count >= 3

    # Rehydration test
    rehydrated = scrubber.rehydrate(scrub_result.scrubbed_text, scrub_result.vault_token_map)
    assert rehydrated == sample_text


def test_torque_scrubber_pii_and_keys():
    """Verifies that API keys, emails, and IPs are scrubbed."""
    scrubber = TorqueScrubber()
    sample_text = "Connecting to 192.168.99.1 with key sk-1234567890abcdef1234567890abcdef and user test@domain.com"

    scrub_result = scrubber.tokenize_and_store(sample_text)

    assert "192.168.99.1" not in scrub_result.scrubbed_text
    assert "sk-1234567890abcdef" not in scrub_result.scrubbed_text
    assert "test@domain.com" not in scrub_result.scrubbed_text
    assert "<<SEC_" in scrub_result.scrubbed_text

    # Rehydrate
    rehydrated = scrubber.rehydrate(scrub_result.scrubbed_text, scrub_result.vault_token_map)
    assert rehydrated == sample_text


def test_torque_router_local_override():
    """Verifies that explicit [LOCAL] tag forces local execution tier."""
    router = TorqueRouter()
    payload = PromptPayload(
        model="qwen2.5:32b",
        messages=[ChatMessageDTO(role="user", content="[LOCAL] Run exhaustive full simulation benchmark for 1000 iterations.")],
    )

    decision = router.route(payload)
    assert decision.tier in [ExecutionTier.TIER_1_LOCAL_RAPID, ExecutionTier.TIER_2_DISTRIBUTED_DAG]
    assert decision.is_scrubbed is False


def test_torque_router_rapid_query():
    """Verifies short conversational prompt routes to Tier 1 local RTX 3060."""
    router = TorqueRouter()
    payload = PromptPayload(
        model="deepseek-r1:14b",
        messages=[ChatMessageDTO(role="user", content="Hello, what time is it?")],
        max_tokens=64,
    )

    decision = router.route(payload)
    assert decision.tier == ExecutionTier.TIER_1_LOCAL_RAPID
