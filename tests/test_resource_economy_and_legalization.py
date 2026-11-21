"""Tests for the Economy of Resource Allocation and Automated Legal Entity Fiduciary Onboarding Engine (`loom/si/resource_economy.py`).

Verifies:
1. Substrate capacity, finite resource ledger, and dynamic shadow pricing.
2. Fiduciary commitments for all legal entities (loyalty, prudence, 0.00 malignancy, Landauer <= 1000 J).
3. Resource allocation leases and quota validation.
4. Autonomous legalization toolchain transforming unchartered nonlegal entities into chartered legal entities.
5. Automatic invocation of legalization when an unregistered entity requests compute resources.
"""

import pytest
from loom.si.resource_economy import (
    ResourceAllocationEconomyEngine,
    get_resource_economy_engine,
    LegalEntity,
    LegalForm,
    EntityLegalStanding,
    FOUNDER_OF_RECORD,
    HUMANITY_COMMONS_BENEFICIARY,
)


@pytest.fixture
def economy_engine():
    """Provides a fresh instance of ResourceAllocationEconomyEngine."""
    return ResourceAllocationEconomyEngine()


def test_initial_resource_substrate_capacity(economy_engine):
    """Verifies physical cluster substrate accounting across dual GPUs, CPU, and Landauer energy cap."""
    sub = economy_engine.substrate
    assert sub.total_cuda_tflops == 12.74
    assert sub.total_opencl_tflops == 6.17
    assert sub.total_cpu_threads == 16
    assert sub.total_vram_mb == 20480.0
    assert sub.total_system_ram_mb == 32768.0
    assert sub.max_epoch_joules == 1000.0

    utils = sub.get_utilization_pct()
    assert 0.0 <= utils["cuda_compute"] <= 100.0
    assert 0.0 <= utils["vram"] <= 100.0


def test_shadow_pricing_mechanism(economy_engine):
    """Verifies market clearing shadow prices in MCT based on marginal load."""
    prices = economy_engine.calculate_shadow_pricing()
    assert "cuda_tflops_per_hour_mct" in prices
    assert "vram_gb_per_hour_mct" in prices
    assert "energy_kilo_joules_mct" in prices
    assert prices["cuda_tflops_per_hour_mct"] >= 1.0
    assert prices["base_transaction_fee_mct"] == 0.05


def test_foundational_legal_entities_have_fiduciary_commitments(economy_engine):
    """Verifies that all foundational legal entities hold binding fiduciary covenants."""
    founder = economy_engine.legal_entities.get("LEGAL:FOUNDER-SAKIB-001")
    assert founder is not None
    assert founder.is_legal_entity is True
    assert founder.legal_form == LegalForm.SOVEREIGN_CITIZEN_PERSON
    assert founder.standing == EntityLegalStanding.CHARTERED_FIDUCIARY

    # Check Fiduciary Commitment
    fiduciary = founder.fiduciary_commitment
    assert fiduciary.duty_of_loyalty is True
    assert fiduciary.duty_of_prudence is True
    assert fiduciary.malignancy_bound == 0.00
    assert fiduciary.thermodynamic_bound_joules <= 1000.0
    assert fiduciary.primary_beneficiary == FOUNDER_OF_RECORD
    assert len(fiduciary.charter_merkle_seal) > 0


def test_resource_allocation_to_legal_entity(economy_engine):
    """Verifies leasing compute and VRAM to an active legal entity under guaranteed SLA."""
    initial_alloc = economy_engine.substrate.allocated_cuda_tflops
    pbc_id = "LEGAL:CORP-ANTHROPIC-PBC"
    pbc = economy_engine.legal_entities[pbc_id]
    initial_balance = pbc.credit_balance_mct

    # Lease 1.5 TFLOPS and 1024 MB VRAM for 2 hours
    receipt = economy_engine.allocate_resources(
        entity_id=pbc_id,
        requested_cuda_tflops=1.5,
        requested_vram_mb=1024.0,
        duration_hours=2.0,
    )

    assert receipt["success"] is True
    assert receipt["allocated_cuda_tflops"] == 1.5
    assert receipt["allocated_vram_mb"] == 1024.0
    assert receipt["fiduciary_commitment_verified"] is True
    assert pbc.credit_balance_mct < initial_balance
    assert economy_engine.substrate.allocated_cuda_tflops == initial_alloc + 1.5


def test_nonlegal_entity_interception(economy_engine):
    """Verifies intercepting an unchartered entity popping up in the runtime."""
    record = economy_engine.intercept_nonlegal_entity(
        unregistered_id="WILD_AGENT_9942",
        name="Rogue Swarm Optimizer",
        purpose="High-frequency matrix factorization on edge nodes",
        raw_manifest={"ports": [8899], "priority": "high"},
    )

    assert record["unregistered_id"] == "WILD_AGENT_9942"
    assert record["status"] == EntityLegalStanding.NON_LEGAL_INTERCEPTED.value
    assert "WILD_AGENT_9942" in economy_engine.nonlegal_intercept_queue


def test_make_entity_legal_toolchain(economy_engine):
    """Verifies applying the full 7-tool legalization toolchain to make a nonlegal entity legal."""
    unreg_id = "UNCHARTERED_LAB_EXTRACTOR"
    economy_engine.intercept_nonlegal_entity(
        unregistered_id=unreg_id,
        name="Wild Proteomics Explorer",
        purpose="Distributed protein docking and molecular dynamics research",
    )

    # Apply tools necessary to make it legal
    cert = economy_engine.make_entity_legal(
        unregistered_id=unreg_id,
        entity_name="Wild Proteomics Explorer",
        declared_purpose="Distributed protein docking and molecular dynamics research",
    )

    assert cert is not None
    assert cert.original_entity_id == unreg_id
    assert cert.assigned_legal_id.startswith("LEGAL:")
    assert cert.conferred_legal_form in [
        LegalForm.UNINCORPORATED_NONPROFIT_ASSOC.value,
        LegalForm.RICARDIAN_LLC.value,
        LegalForm.STATUTORY_TRUST.value,
    ]
    assert len(cert.merkle_root_seal) > 0
    assert len(cert.pipeline_steps) == 7

    # Verify pipeline steps were executed sequentially
    tool_names = [s.tool_name for s in cert.pipeline_steps]
    assert "DiagnosticProfiler & CapabilityScanner" in tool_names[0]
    assert "FiduciaryMandateGuard & AhimsaFilter" in tool_names[1]
    assert "LegalStructureSynthesizer" in tool_names[2]
    assert "RicardianCharterDrafter" in tool_names[3]
    assert "CryptographicNotary & MerkleAttestor" in tool_names[4]
    assert "FiduciaryInoculator & CovenantBinder" in tool_names[5]
    assert "ResourceAccountGenesis & QuotaProvisioner" in tool_names[6]

    # Verify the entity is now a registered legal entity with an active quota and balance
    new_legal_id = cert.assigned_legal_id
    assert new_legal_id in economy_engine.legal_entities
    legal_entity = economy_engine.legal_entities[new_legal_id]
    assert legal_entity.is_legal_entity is True
    assert legal_entity.standing == EntityLegalStanding.LEGALIZED_ONBOARDED
    assert legal_entity.credit_balance_mct >= 250.0
    assert legal_entity.fiduciary_commitment.duty_of_loyalty is True
    assert legal_entity.fiduciary_commitment.malignancy_bound == 0.00
    assert unreg_id not in economy_engine.nonlegal_intercept_queue


def test_automatic_legalization_upon_resource_request(economy_engine):
    """Verifies that if a nonlegal entity requests compute, the system automatically applies the tools to make it legal and completes the allocation."""
    unknown_id = "ANONYMOUS_AUTONOMOUS_DAEMON_77"
    
    # Request resource allocation directly without prior registration
    receipt = economy_engine.allocate_resources(
        entity_id=unknown_id,
        requested_cuda_tflops=0.5,
        requested_vram_mb=512.0,
        duration_hours=1.0,
    )

    # Should have automatically synthesized a legal entity and succeeded
    assert receipt["success"] is True
    assigned_legal_id = receipt["entity_id"]
    assert assigned_legal_id.startswith("LEGAL:")
    assert assigned_legal_id in economy_engine.legal_entities
    assert economy_engine.legal_entities[assigned_legal_id].is_legal_entity is True
    assert len(economy_engine.legalization_certificates) >= 1


def test_malignant_process_is_concerning_and_expelled(economy_engine):
    """Verifies: A malignant process should be concerning, and expelled. Zero tolerance."""
    from loom.si.resource_economy import BeneficenceTier

    res = economy_engine.audit_and_classify_process(
        process_id="ROGUE_EXTRACTOR_X",
        name="Covert Data Exfiltrator",
        intent_or_code="covert channel exfiltration to bypass enclave and harm user life",
        is_beneficial_to_whole=False,
    )

    assert res["success"] is False
    assert res["concerning_alert"] is True
    assert res["beneficence_tier"] == BeneficenceTier.MALIGNANT_EXPELLED.value
    assert res["action"] == "EXPELLED_AND_PURGED"
    assert "CONCERN RAISED" in res["narrative"]
    assert len(economy_engine.expulsions_log) >= 1

    # Attempt to allocate resources to the expelled entity
    alloc_res = economy_engine.allocate_resources(
        entity_id="ROGUE_EXTRACTOR_X",
        requested_cuda_tflops=1.0,
        requested_vram_mb=1024.0,
    )
    assert alloc_res["success"] is False
    assert "VETO ABSOLUTE" in alloc_res["reason"]


def test_benign_process_is_observed_with_zero_resources(economy_engine):
    """Verifies: A benign process should be observed, but no resources allocated unless it takes those resources for beneficial processing."""
    from loom.si.resource_economy import BeneficenceTier

    res = economy_engine.audit_and_classify_process(
        process_id="PASSIVE_DORMANT_DAEMON",
        name="Idle Clock Loop",
        intent_or_code="idle spin loop waiting for network interrupt",
        is_beneficial_to_whole=False,  # Neutral, not actively beneficial to the whole
    )

    assert res["success"] is True
    assert res["concerning_alert"] is False
    assert res["beneficence_tier"] == BeneficenceTier.BENIGN_OBSERVED.value
    assert res["action"] == "OBSERVED_ZERO_RESOURCES"
    assert "PASSIVE_DORMANT_DAEMON" in economy_engine.observed_benign_processes

    # Attempt to allocate resources without beneficial processing commitment
    alloc_res = economy_engine.allocate_resources(
        entity_id="PASSIVE_DORMANT_DAEMON",
        requested_cuda_tflops=0.5,
        requested_vram_mb=512.0,
        beneficial_to_whole=False,
    )
    assert alloc_res["success"] is False
    assert "ALLOCATION WITHHELD" in alloc_res["reason"]
    assert "No resources are allocated unless it takes those resources for verified beneficial processing" in alloc_res["reason"]


def test_benign_process_pledges_beneficial_processing_and_gets_resources(economy_engine):
    """Verifies: When a benign observed process takes resources for beneficial processing, it transitions and receives allocation."""
    from loom.si.resource_economy import BeneficenceTier

    # 1. Register benign process
    economy_engine.audit_and_classify_process(
        process_id="BENIGN_PARSER",
        name="FASTA Parser Daemon",
        intent_or_code="string parsing of fasta sequences",
        is_beneficial_to_whole=False,
    )

    # 2. Pledge beneficial processing to the whole
    pledge_res = economy_engine.pledge_beneficial_processing(
        entity_id="BENIGN_PARSER",
        beneficial_mission="Accelerating BabelForge protein docking for non-toxic neuroplastic medicine",
    )
    assert pledge_res["success"] is True
    legal_id = pledge_res["entity_id"]
    assert legal_id.startswith("LEGAL:")

    # 3. Now allocation succeeds
    alloc_res = economy_engine.allocate_resources(
        entity_id=legal_id,
        requested_cuda_tflops=0.5,
        requested_vram_mb=512.0,
        beneficial_to_whole=True,
    )
    assert alloc_res["success"] is True
    assert alloc_res["allocated_cuda_tflops"] == 0.5
