"""
Test Suite: Zero-Trust Enclave, QCT Hybrid Router, and Protocol Abstractions.

Tests:
1. Pydantic v2 immutability on RoutingDecision, SanitizedPayload, and EnclaveToken.
2. Protocol compliance for ScrubberProtocol, VaultProtocol, and RouterProtocol.
3. Zero-Trust Enclave scrubbing, RehydrationVault, Rehydrator, and SecurityEgressViolation.
4. QCT Hybrid Router 3-tier routing: Deterministic, Thermodynamic, and Quantum/Cloud.
"""

import pytest
from pydantic import ValidationError

from loom.torque.enclave import (
    EgressFirewall,
    Enclave,
    RehydrationVault,
    Rehydrator,
    SecurityEgressViolation,
    TorqueEnclaveScrubber,
)
from loom.torque.scheduler import QCTHybridRouter, QCTRouter, SimulatedPBitSolver
from loom.types import (
    ChatMessageDTO,
    EnclaveToken,
    ExecutionTier,
    PromptPayload,
    RouterProtocol,
    RoutingDecision,
    SanitizedPayload,
    ScrubberProtocol,
    VaultProtocol,
)


def test_core_abstractions_immutability():
    """Verify that RoutingDecision, SanitizedPayload, and EnclaveToken are strictly immutable (frozen=True)."""
    # 1. EnclaveToken immutability
    token = EnclaveToken(
        token_tag="<<ENCLAVE_VAR_1>>",
        original_value="fouriersLibrary",
        category="IP",
        created_at=100.0,
    )
    assert token.token_tag == "<<ENCLAVE_VAR_1>>"
    with pytest.raises(ValidationError):
        token.token_tag = "<<MUTATED>>"

    # 2. SanitizedPayload immutability
    sanitized = SanitizedPayload(
        original_text="Raw text",
        sanitized_text="Clean text",
        replacements_count=1,
        vault_token_map={"<<ENCLAVE_VAR_1>>": "fouriersLibrary"},
        contains_protected_ip=True,
        is_scrubbed=True,
    )
    assert sanitized.scrubbed_text == "Clean text"
    with pytest.raises(ValidationError):
        sanitized.sanitized_text = "Mutated text"

    # 3. RoutingDecision immutability
    decision = RoutingDecision(
        tier=ExecutionTier.TIER_1_DETERMINISTIC,
        estimated_duration_seconds=5.2,
        target_endpoint="http://192.168.99.1:8080",
        is_scrubbed=False,
        model_name="qwen2.5:7b",
        reasoning="Test decision",
    )
    with pytest.raises(ValidationError):
        decision.estimated_duration_seconds = 10.0


def test_protocol_implementations():
    """Verify runtime protocol conformance for VaultProtocol, ScrubberProtocol, and RouterProtocol."""
    vault = RehydrationVault()
    scrubber = TorqueEnclaveScrubber(vault=vault)
    router = QCTRouter()

    assert isinstance(vault, VaultProtocol)
    assert isinstance(scrubber, ScrubberProtocol)
    assert isinstance(router, RouterProtocol)


def test_zero_trust_enclave_facade_and_rehydration():
    """Verify Enclave namespace, Scrubber, Rehydrator, and synthetic token resolution."""
    vault = Enclave.Vault()
    scrubber = Enclave.Scrubber(vault=vault)
    rehydrator = Enclave.Rehydrator(vault=vault)

    raw_text = "Analyzing ClothOS microkernel and VectorForge pipelines with key sk-abcdef1234567890abcdef1234567890."
    sanitized = scrubber.sanitize(raw_text)

    # Invariants: Protected IP must be scrubbed
    assert "ClothOS" not in sanitized.sanitized_text
    assert "VectorForge" not in sanitized.sanitized_text
    assert "sk-abcdef" not in sanitized.sanitized_text
    assert sanitized.contains_protected_ip is True
    assert sanitized.is_scrubbed is True
    assert len(sanitized.vault_token_map) >= 2

    # Rehydrate using Rehydrator
    restored = rehydrator.rehydrate(sanitized.sanitized_text, sanitized.vault_token_map)
    assert restored == raw_text


def test_egress_firewall_raises_security_egress_violation():
    """Verify EgressFirewall raises SecurityEgressViolation when unscrubbed IP is leaked to external endpoints."""
    firewall = Enclave.EgressFirewall()

    with pytest.raises(SecurityEgressViolation) as exc_info:
        firewall.inspect_outbound_payload(
            "https://api.external-cloud.com/v1/completions",
            "This prompt exposes fouriersLibrary source code to external servers.",
        )
    assert "fouriersLibrary" in str(exc_info.value)


def test_qct_router_tier1_deterministic():
    """Verify standard sequential inference routes to Tier 1 Deterministic on RTX 3060."""
    router = QCTHybridRouter()
    prompt = "Write a simple Python function to calculate the Fibonacci sequence."
    decision = router.route_task(raw_prompt=prompt, task_type="inference")

    assert decision.tier == ExecutionTier.TIER_1_DETERMINISTIC
    assert "192.168.99.1" in decision.target_endpoint or "8080" in decision.target_endpoint
    assert decision.is_scrubbed is False
    assert decision.circuit_breaker_triggered is False


def test_qct_router_tier2_thermodynamic():
    """Verify Z3 SMT constraints and QUBO mappings route to Tier 2 Thermodynamic on simulated p-bit solvers."""
    router = QCTHybridRouter()
    prompt = "Solve this QUBO mapping and verify Ising energy minimization with Z3 SMT constraints."
    decision = router.route_task(raw_prompt=prompt, task_type="qubo")

    assert decision.tier == ExecutionTier.TIER_2_THERMODYNAMIC
    assert "pbit" in decision.model_name or "p-bit" in decision.reasoning.lower()
    assert decision.is_scrubbed is False
    assert decision.circuit_breaker_triggered is False

    # Verify SimulatedPBitSolver mock
    qubo_res = SimulatedPBitSolver.solve_qubo([[1, -1], [-1, 2]])
    assert qubo_res["status"] == "CONVERGED"
    smt_res = SimulatedPBitSolver.solve_smt("(assert (> x 0))")
    assert smt_res["status"] == "SAT"


def test_qct_router_tier3_quantum_cloud_fallback():
    """Verify workloads exceeding 300s trigger Enclave.Scrubber and raise a routing alert."""
    router = QCTHybridRouter()
    massive_prompt = "Exhaustive simulation and theorem proving across the entire parameter space. " * 3000
    decision = router.route_task(raw_prompt=massive_prompt, task_type="inference")

    assert decision.tier == ExecutionTier.TIER_3_QUANTUM_CLOUD
    assert decision.is_scrubbed is True
    assert decision.circuit_breaker_triggered is True
    assert decision.requires_manual_approval is True
    assert decision.routing_alert is not None
    assert "ROUTING_ALERT_TIER3_CLOUD_FALLBACK" in decision.routing_alert
