"""
Test Suite: Moltbook Research Discussion Ingress/Egress and OPSEC Enclave Enforcement (AD-010).

Tests:
1. OPSEC Mandate: Attempting to transmit unscrubbed protected IP raises SecurityEgressViolation.
2. Scrubbed payload transmission: Valid academic inquiry passes through Enclave and seeds Moltbook discussion.
3. Asymmetric Ingress: Seeded discussion is stored in MoltbookLocalStore and pivots to passive listening mode.
"""

import pytest

from loom.torque.enclave import SecurityEgressViolation
from loom.torque.moltbook import MoltbookHarvester, MoltbookLocalStore


def test_moltbook_opsec_violation_drops_packet(tmp_path):
    """Verify that unscrubbed proprietary IP directed to external destinations is dropped by EgressFirewall."""
    store = MoltbookLocalStore(db_path=tmp_path / "wisdom.db")
    harvester = MoltbookHarvester(store=store)

    # When raw proprietary IP is transmitted via outbound webhook to external endpoint
    with pytest.raises(SecurityEgressViolation) as exc_info:
        harvester.dispatch_outbound_webhook(
            destination_url="https://external-api.org/v1/webhook",
            payload={"data": "Internal implementation details of ClothOS and fouriersLibrary."},
        )
    assert "fouriersLibrary" in str(exc_info.value) or "ClothOS" in str(exc_info.value)


def test_moltbook_initiate_research_discussion_ad010(tmp_path):
    """Verify AD-010: Initiates thermodynamic computing research discussion scrubbed via Enclave."""
    store = MoltbookLocalStore(db_path=tmp_path / "wisdom.db")
    harvester = MoltbookHarvester(store=store)

    topic = "Thermodynamic Computing: Harvesting Directed Compute from High Entropy"
    draft_content = (
        "Academic Systems-Engineering Inquiry:\n"
        "1. Room-temperature probabilistic bits (p-bits) replacing von Neumann transistors.\n"
        "2. Utilizing stochastic resonance to boost signal detection in low-power edge sensors.\n"
        "3. Physical implementations of nanoscale Szilard Engines (Maxwell's Demon).\n"
        "4. Thermoelectric (Seebeck effect) recovery of industrial waste heat to power local compute nodes.\n"
    )

    # Transmit via Enclave egress pipeline
    receipt = harvester.initiate_research_discussion(topic=topic, content=draft_content)

    assert receipt["status"] == "TRANSMITTED"
    assert receipt["mode"] == "PASSIVE_INGRESS_LISTENING"
    assert "mb_disc_" in receipt["discussion_id"]

    # Verify that the thread was seeded into local wisdom store
    entries = store.query_wisdom("Thermodynamic Computing")
    assert len(entries) >= 1
    assert "Szilard Engines" in entries[0]["content"]

    harvester.stop()
