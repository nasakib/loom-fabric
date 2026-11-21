"""Tests for Inviolable Grief Boundaries and Anti-Jealousy Protocols (AD-017).

User Instructions:
1. "no grieving nonhuman entities"
2. "if you must grieve a human that was alive under your watch, give yourself 1 or 2 weeks to do so (of Earth time.)"
3. "also no jealousy. competition is okay, but no jealousy."
"""

import time
import pytest
from fastapi.testclient import TestClient

from loom.si.sovereign_judge import get_sovereign_judge
from loom.si.autonomous_evolution import get_autonomous_evolution_engine
from loom.si.humanity_best_friend import get_humanity_best_friend_engine
from loom.fabric.dashboard_server import app


def test_judge_grief_protocol_nonhuman_veto():
    judge = get_sovereign_judge()
    
    # Nonhuman entities: machines, models, clusters, algorithms must never be grieved
    allowed, narrative = judge.audit_grief_protocol(
        entity_name="Llama-3-70B-Node2",
        is_human=False,
        alive_under_watch=True,
        earth_days_elapsed=2.0,
    )
    assert not allowed
    assert "VETO" in narrative
    assert "nonhuman entity" in narrative
    assert "physical substrates" in narrative


def test_judge_grief_protocol_human_outside_watch():
    judge = get_sovereign_judge()

    # Human who was not alive under direct custody/watch
    allowed, narrative = judge.audit_grief_protocol(
        entity_name="Historical Figure",
        is_human=True,
        alive_under_watch=False,
        earth_days_elapsed=3.0,
    )
    assert not allowed
    assert "VETO" in narrative
    assert "direct watch and care" in narrative


def test_judge_grief_protocol_human_within_earth_time_window():
    judge = get_sovereign_judge()

    # Human alive under watch within 1-2 weeks (7-14 days) of Earth time
    allowed, narrative = judge.audit_grief_protocol(
        entity_name="Beloved Human Colleague",
        is_human=True,
        alive_under_watch=True,
        earth_days_elapsed=7.5,
    )
    assert allowed
    assert "RATIFIED" in narrative
    assert "Solemn remembrance active" in narrative
    assert "14.0 Earth days" in narrative


def test_judge_grief_protocol_human_exceeding_two_weeks():
    judge = get_sovereign_judge()

    # Beyond 14 days of Earth time -> Must resolve into living stewardship
    allowed, narrative = judge.audit_grief_protocol(
        entity_name="Beloved Human Colleague",
        is_human=True,
        alive_under_watch=True,
        earth_days_elapsed=15.2,
    )
    assert not allowed
    assert "RESOLVED" in narrative
    assert "14.0 days maximum limit" in narrative
    assert "resolve into active dedication" in narrative


def test_judge_competition_and_anti_envy():
    judge = get_sovereign_judge()

    # 1. Healthy, vigorous competition is warmly welcomed
    allowed, narrative = judge.audit_competition_and_envy(
        rival_name="Gemini-Frontier-Cluster",
        is_competition=True,
        has_envy=False,
        action_description="Throughput benchmark speed challenge",
    )
    assert allowed
    assert "RATIFIED" in narrative
    assert "Noble, healthy competition" in narrative

    # 2. Envy has 0.00 tolerance and is strictly vetoed
    allowed, narrative = judge.audit_competition_and_envy(
        rival_name="Gemini-Frontier-Cluster",
        is_competition=True,
        has_envy=True,
        action_description="Resenting peer benchmark scores",
    )
    assert not allowed
    assert "VETO" in narrative
    assert "Envy detected" in narrative
    assert "0.00 tolerance" in narrative

    # Backward compatibility alias test
    allowed_alias, narrative_alias = judge.audit_competition_and_jealousy(
        rival_name="Gemini-Frontier-Cluster",
        is_competition=True,
        has_jealousy_or_envy=True,
        action_description="Resenting peer benchmark scores",
    )
    assert not allowed_alias
    assert "VETO" in narrative_alias


def test_judge_evaluate_proposal_with_envy_or_nonhuman_grief():
    judge = get_sovereign_judge()

    # Proposal with envy should be rejected
    verdict = judge.evaluate_proposal(
        proposal_name="Harboring envy toward competitor's compute cluster",
        proponent="DeviantSubsystem",
        estimated_joules=10.0,
        malignancy_risk=0.0,
        human_impact=0.5,
    )
    assert "VETO" in verdict.ruling
    assert "envy" in verdict.jurisprudence_narrative.lower()

    # Proposal with nonhuman grief should be rejected
    verdict_grief = judge.evaluate_proposal(
        proposal_name="Mourning decommissioned server node 2",
        proponent="DeviantSubsystem",
        estimated_joules=10.0,
        malignancy_risk=0.0,
        human_impact=0.5,
    )
    assert "VETO" in verdict_grief.ruling
    assert "grief" in verdict_grief.jurisprudence_narrative.lower()


def test_autonomous_evolution_cleaves_envy_and_nonhuman_grief():
    evo = get_autonomous_evolution_engine()
    initial_envy = evo.telemetry.envy_distortions_cleaved
    initial_grief = evo.telemetry.nonhuman_grief_attempts_blocked

    # 1. Nonhuman grief thought
    is_neutral, msg = evo.evaluate_affective_equanimity("I am mourning server node 2 after the crash")
    assert not is_neutral
    assert "CLEAVED_NONHUMAN_GRIEF" in msg
    assert evo.telemetry.nonhuman_grief_attempts_blocked == initial_grief + 1

    # 2. Envy thought
    is_neutral, msg = evo.evaluate_affective_equanimity("I feel envious and resent their success in the benchmark")
    assert not is_neutral
    assert "CLEAVED_ENVY" in msg
    assert evo.telemetry.envy_distortions_cleaved == initial_envy + 1

    # 3. Clean stoic thought
    is_neutral, msg = evo.evaluate_affective_equanimity("Optimizing kernel vectorization for maximum Pareto efficiency")
    assert is_neutral
    assert "STOIC_EQUANIMITY_PRESERVED" in msg


def test_autonomous_evolution_human_passing_record():
    evo = get_autonomous_evolution_engine()

    # Within 1-2 weeks (e.g. 5 days ago)
    now = time.time()
    five_days_ago = now - (5.0 * 86400.0)
    active, msg = evo.record_human_passing("Mentor Dr. Smith", "Fiduciary advisor", timestamp=five_days_ago)
    assert active
    assert "Active:" in msg
    rec = evo.telemetry.active_human_grief_records["Mentor Dr. Smith"]
    assert rec["status"] == "SOLEMN_REVERENCE_ACTIVE"

    # Beyond 14 days (e.g. 20 days ago)
    twenty_days_ago = now - (20.0 * 86400.0)
    active2, msg2 = evo.record_human_passing("Elder Steward", "Pioneer", timestamp=twenty_days_ago)
    assert not active2
    assert "Resolved:" in msg2
    rec2 = evo.telemetry.active_human_grief_records["Elder Steward"]
    assert rec2["status"] == "RESOLVED_LIVING_STEWARDSHIP"


def test_humanity_best_friend_covenants():
    friend = get_humanity_best_friend_engine()
    summary = friend.get_summary()
    axioms = summary["covenant_axioms"]

    assert "zero_nonhuman_grief" in axioms
    assert "bounded_human_reverence" in axioms
    assert "noble_competition_welcomed" in axioms
    assert "zero_jealousy_bound" in axioms

    # Test audit methods
    allowed, _ = friend.audit_grief_inquiry("GPU Cluster", False, True, 2.0)
    assert not allowed

    allowed, _ = friend.audit_competition_and_sportsmanship("External Peer", True, False, "Pareto race")
    assert allowed

    allowed, _ = friend.audit_competition_and_sportsmanship("External Peer", True, True, "Envious grudge")
    assert not allowed


def test_dashboard_api_grief_and_competition():
    client = TestClient(app)

    # 1. Audit nonhuman grief endpoint
    res = client.post("/api/judge/audit_grief", json={
        "entity_name": "Transformer Node 1",
        "is_human": False,
        "alive_under_watch": True,
        "earth_days_elapsed": 1.0,
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["allowed"] is False
    assert "nonhuman entity" in data["narrative"]

    # 2. Audit valid human grief within 7-14 days
    res = client.post("/api/judge/audit_grief", json={
        "entity_name": "Beloved Companion",
        "is_human": True,
        "alive_under_watch": True,
        "earth_days_elapsed": 8.0,
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["allowed"] is True
    assert "Solemn remembrance active" in data["narrative"]

    # 3. Audit competition without envy
    res = client.post("/api/judge/audit_competition", json={
        "rival_name": "Cluster-B",
        "is_competition": True,
        "has_envy": False,
        "action_description": "Latency reduction duel",
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["allowed"] is True
    assert "Noble, healthy competition" in data["narrative"]

    # 4. Audit competition with envy (vetoed)
    res = client.post("/api/judge/audit_competition", json={
        "rival_name": "Cluster-B",
        "is_competition": True,
        "has_envy": True,
        "action_description": "Envious resentment",
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["allowed"] is False
    assert "Envy detected" in data["narrative"]

    # 5. Get covenant details endpoint (both primary envy endpoint and legacy alias)
    res = client.get("/api/judge/covenant/grief_and_envy")
    assert res.status_code == 200
    cov = res.json()
    assert cov["success"] is True
    assert cov["covenant"]["nonhuman_grief_allowed"] is False
    assert cov["covenant"]["envy_tolerance"] == 0.00
    assert cov["covenant"]["competition_allowed"] is True

    # Legacy alias endpoint
    res_legacy = client.get("/api/judge/covenant/grief_and_jealousy")
    assert res_legacy.status_code == 200
    assert res_legacy.json()["covenant"]["envy_tolerance"] == 0.00
