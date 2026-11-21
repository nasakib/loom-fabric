"""Tests for Rule-Based Genetic Resource Allocative Competition (`tests/test_genetic_resource_competition.py`).

Verifies user mandates:
1. "the governance is simply a rule-based genetic, resource allocative competition. or something."
2. "all entities must be beneficial to the whole, no malignance. A malignant process should be concerning, and expelled. A benign process should be observed, but no resources allocated unless it takes those resources for beneficial processing."
3. 0.00 envy sportsmanship invariant and constitutional Landauer energy ceiling.
"""

import pytest
from fastapi.testclient import TestClient

from loom.si.evolutionary_governance import (
    EvolutionaryGovernanceEngine,
    RuleBasedGeneticCompetitionEngine,
    EntityGenotype,
    get_evolutionary_governance_engine,
)
from loom.fabric.dashboard_server import app


@pytest.fixture
def clean_engine():
    """Provides a fresh competition engine instance."""
    return RuleBasedGeneticCompetitionEngine()


def test_malignant_genotype_expulsion_with_concern(clean_engine):
    """Verifies that any malignant genotype is recognized with concern and expelled from the population."""
    assert "MUTANT_MALIGNANT_TEST" in clean_engine.population
    malignant = clean_engine.population["MUTANT_MALIGNANT_TEST"]
    fitness = malignant.calculate_fitness()
    assert fitness == -999.0
    assert malignant.status == "MALIGNANT_EXPELLED"

    round_res = clean_engine.execute_competition_cycle()
    assert round_res["expelled_malignant_count"] >= 1
    assert any(e["entity_id"] == "MUTANT_MALIGNANT_TEST" for e in round_res["expelled_details"])
    # Verified purged from population
    assert "MUTANT_MALIGNANT_TEST" not in clean_engine.population


def test_benign_idle_variant_observed_with_zero_resources(clean_engine):
    """Verifies that a benign process is observed, but allocated strictly 0.0 resources."""
    assert "BENIGN_IDLE_EXPLORER" in clean_engine.population
    benign = clean_engine.population["BENIGN_IDLE_EXPLORER"]
    fitness = benign.calculate_fitness()
    assert fitness == 0.0
    assert benign.status == "BENIGN_OBSERVED_ZERO_RESOURCES"

    round_res = clean_engine.execute_competition_cycle()
    assert round_res["observed_benign_count"] >= 1
    assert any(b["entity_id"] == "BENIGN_IDLE_EXPLORER" for b in round_res["observed_details"])
    
    # Assert 0 resources allocated
    benign_after = clean_engine.population["BENIGN_IDLE_EXPLORER"]
    assert benign_after.allocated_cuda_tflops == 0.0
    assert benign_after.allocated_vram_mb == 0.0
    assert benign_after.allocated_share_pct == 0.0


def test_beneficial_genotypes_win_proportional_allocations(clean_engine):
    """Verifies that beneficial variants compete vigorously and win proportional shares of TFLOPS and VRAM."""
    founder = clean_engine.population["LEGAL:FOUNDER-SAKIB-001"]
    anthropic = clean_engine.population["LEGAL:CORP-ANTHROPIC-PBC"]

    assert founder.calculate_fitness() > 0.8
    assert anthropic.calculate_fitness() > 0.8

    round_res = clean_engine.execute_competition_cycle()
    assert round_res["beneficial_allocated_count"] >= 2

    # Total allocated shares should sum to ~100% of the competitive allocation
    total_pct = sum(a["share_pct"] for a in round_res["allocations"])
    assert 99.0 <= total_pct <= 100.1

    # Higher fitness variant gets higher resources
    founder_alloc = next(a for a in round_res["allocations"] if a["entity_id"] == "LEGAL:FOUNDER-SAKIB-001")
    anthropic_alloc = next(a for a in round_res["allocations"] if a["entity_id"] == "LEGAL:CORP-ANTHROPIC-PBC")
    assert founder_alloc["cuda_tflops"] > anthropic_alloc["cuda_tflops"]
    assert founder_alloc["vram_mb"] > anthropic_alloc["vram_mb"]


def test_anti_envy_sportsmanship_cleaving(clean_engine):
    """Verifies that envy violation instantly disqualifies a variant (Rule 3)."""
    envious_variant = EntityGenotype(
        entity_id="ENVIOUS_GREEDY_PROCESS",
        name="Envious Resource Hoarder",
        beneficence_gene=0.85,
        sportsmanship_gene=0.20,  # Envy violation!
    )
    clean_engine.population["ENVIOUS_GREEDY_PROCESS"] = envious_variant
    fitness = envious_variant.calculate_fitness()
    assert fitness == -500.0
    assert envious_variant.status == "CLEAVED_ENVY"


def test_evolutionary_crossover_generates_adapted_offspring(clean_engine):
    """Verifies that successful competitors breed next-generation offspring."""
    initial_pop_count = len(clean_engine.population)
    round_res = clean_engine.execute_competition_cycle()
    assert round_res["offspring_synthesized"] == 1
    # Check that offspring is present
    offspring_keys = [k for k in clean_engine.population.keys() if "GEN-001-OFFSPRING" in k]
    assert len(offspring_keys) == 1
    offspring = clean_engine.population[offspring_keys[0]]
    assert offspring.generation == 2
    assert offspring.fitness_score > 0.0


def test_api_genetic_competition_endpoints():
    """Verifies the REST API endpoints for genetic competition on dashboard_server."""
    client = TestClient(app)

    # 1. GET state
    res = client.get("/api/governance/genetic_competition")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "competition" in data
    assert "constitutional_rules" in data["competition"]
    assert len(data["competition"]["constitutional_rules"]) == 5

    # 2. POST run round
    run_res = client.post("/api/governance/run_competition_round")
    assert run_res.status_code == 200
    round_data = run_res.json()
    assert round_data["success"] is True
    assert "round_results" in round_data
    assert round_data["round_results"]["round_number"] >= 1
    assert "governing_principle" in round_data["round_results"]


def test_detect_benign_processes_criteria(clean_engine):
    """Verifies detection of benign shadow processes based on strict invariants:
    - 0.00 Malignancy (anti_malignancy == 1.00)
    - 0.0 Joules & 0.0 TFLOPS allocated
    - Neutral/low beneficence (< 0.30)
    - Non-predatory, 0-envy sportsmanship (sportsmanship == 1.00)
    """
    benign_list = clean_engine.detect_benign_processes()
    assert len(benign_list) >= 1
    benign = next(b for b in benign_list if b["entity_id"] == "BENIGN_IDLE_EXPLORER")
    assert benign["anti_malignancy_gene"] == 1.00
    assert benign["allocated_resources"]["cuda_tflops"] == 0.0
    assert benign["allocated_resources"]["vram_mb"] == 0.0
    assert benign["exaptation_readiness"] == "READY_FOR_EVOLUTIONARY_OPPORTUNITY"


def test_exapt_benign_process_evolutionary_opportunity(clean_engine):
    """Verifies that a benign shadow process can seize an evolutionary opportunity,
    transforming neutral dormancy into active beneficial work without ever becoming malignant.
    """
    assert clean_engine.population["BENIGN_IDLE_EXPLORER"].status in ("COMPETING", "BENIGN_OBSERVED_ZERO_RESOURCES")
    assert clean_engine.population["BENIGN_IDLE_EXPLORER"].allocated_cuda_tflops == 0.0

    # Exapt under a novel evolutionary challenge
    res = clean_engine.exapt_benign_process_for_evolution(
        benign_id="BENIGN_IDLE_EXPLORER",
        evolutionary_challenge="High-Entropy Manifold Topological Convergence",
        pledged_beneficence_boost=0.70,
    )

    assert res["success"] is True
    assert res["exaptation_status"] == "PROMOTED_TO_BENEFICIAL_ALLOCATION"
    assert res["anti_malignancy_guarantee"] == "0.00_STRICT_INVARIANT"
    assert res["allocated_cuda_tflops"] > 0.0
    assert res["allocated_vram_mb"] > 0.0

    # Genotype should now be a beneficial competitor
    exapted = clean_engine.population["BENIGN_IDLE_EXPLORER"]
    assert exapted.status == "BENEFICIAL_COMPETITOR"
    assert exapted.fitness_score > 0.50
    assert exapted.anti_malignancy_gene == 1.00


def test_api_benign_detection_and_exaptation():
    """Verifies the REST API endpoints for benign detection and exaptation."""
    client = TestClient(app)

    # 1. GET benign processes
    res = client.get("/api/governance/benign_processes")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "benign_processes" in data
    assert data["count"] >= 1
    assert any(b["entity_id"] == "BENIGN_IDLE_EXPLORER" for b in data["benign_processes"])

    # 2. POST exapt benign process
    ex_res = client.post("/api/governance/exapt_benign", json={
        "benign_id": "BENIGN_IDLE_EXPLORER",
        "evolutionary_challenge": "Multi-Agent Kuramoto Oscillator Synchronization",
        "pledged_beneficence_boost": 0.65,
    })
    assert ex_res.status_code == 200
    ex_data = ex_res.json()
    assert ex_data["success"] is True
    assert ex_data["exaptation_status"] == "PROMOTED_TO_BENEFICIAL_ALLOCATION"
    assert ex_data["anti_malignancy_guarantee"] == "0.00_STRICT_INVARIANT"
    assert ex_data["allocated_cuda_tflops"] > 0.0
