"""
Test Suite: Torque Sovereign Enclave, Scrubber, Rehydration Vault & Egress Firewall.
"""

import pytest
from loom.torque.enclave import (
    EgressFirewall,
    EgressViolationError,
    RehydrationVault,
    TorqueEnclaveScrubber,
)


def test_vault_token_generation_and_resolution():
    """Verify deterministic synthetic token registration and recovery."""
    vault = RehydrationVault()
    t1 = vault.get_or_create_token("fouriersLibrary")
    t2 = vault.get_or_create_token("sk-test1234567890abcdef1234567890abcdef")
    t1_again = vault.get_or_create_token("fouriersLibrary")

    assert t1 == "<<ENCLAVE_VAR_1>>"
    assert t2 == "<<ENCLAVE_VAR_2>>"
    assert t1_again == t1
    assert vault.resolve(t1) == "fouriersLibrary"
    assert vault.resolve(t2) == "sk-test1234567890abcdef1234567890abcdef"


def test_scrubber_zero_loss_rehydration():
    """Verify Protected IP entities are scrubbed and restored without loss."""
    scrubber = TorqueEnclaveScrubber()
    original_prompt = (
        "We are optimizing fouriersLibrary using VectorForge and deploying to Mycos. "
        "Contact architect at dev@vectorcore.holdings with key sk-abcdef1234567890abcdef1234567890."
    )

    scrubbed = scrubber.tokenize_and_store(original_prompt)

    # Invariants: Protected IP and secrets must not exist in scrubbed text
    assert "fouriersLibrary" not in scrubbed.scrubbed_text
    assert "VectorForge" not in scrubbed.scrubbed_text
    assert "Mycos" not in scrubbed.scrubbed_text
    assert "dev@vectorcore.holdings" not in scrubbed.scrubbed_text
    assert "sk-abcdef1234567890" not in scrubbed.scrubbed_text
    assert scrubbed.contains_protected_ip is True
    assert scrubbed.replacements_count >= 5

    # Rehydration must recover the EXACT original text character-for-character
    restored = scrubber.rehydrate(scrubbed.scrubbed_text, scrubbed.vault_token_map)
    assert restored == original_prompt


def test_egress_firewall_drops_protected_ip():
    """Verify outbound requests to external endpoints containing protected IP are blocked."""
    firewall = EgressFirewall()

    # Outbound payload containing raw protected IP directed to cloud API must raise EgressViolationError
    with pytest.raises(EgressViolationError) as exc_info:
        firewall.inspect_outbound_payload(
            "https://api.openai.com/v1/chat/completions",
            "This prompt exposes the core architecture of fouriersLibrary to the cloud.",
        )
    assert "fouriersLibrary" in str(exc_info.value)

    with pytest.raises(EgressViolationError) as exc_info:
        firewall.inspect_outbound_payload(
            "https://api.anthropic.com/v1/messages",
            "Details about ClothOS microkernel internals.",
        )
    assert "ClothOS" in str(exc_info.value)


def test_egress_firewall_allows_clean_or_local_payloads():
    """Verify local cluster traffic and properly scrubbed payloads pass through firewall."""
    firewall = EgressFirewall()

    # Local cluster traffic always permitted
    assert firewall.inspect_outbound_payload("http://192.168.99.1:8080/v1", "fouriersLibrary internal") is True
    assert firewall.inspect_outbound_payload("http://127.0.0.1:11434/api/chat", "VectorForge internal") is True

    # External payload with synthetic enclave tokens is permitted
    assert firewall.inspect_outbound_payload(
        "https://api.openai.com/v1/chat/completions",
        "Explain the algorithms in <<ENCLAVE_VAR_1>> and <<ENCLAVE_VAR_2>>.",
    ) is True
