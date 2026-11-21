"""Loom Sovereign — Corporate & Institutional Fiduciary Governance Engine (`loom/si/fiduciary_entities.py`).

Incorporates corporations, enterprises, businesses, DAOs, and institutional entities
directly into the Constitutional Fiduciary Mandate and the Mycorrhizal Rhizome Economy.

Core Principles:
1. Corporations as Institutional Organs (Fruiting Bodies):
   Businesses and legal entities are not extractive predatory engines; they are cooperative
   organs within the multi-kingdom ecosystem that coordinate human talent and capital.
2. The Tripartite Fiduciary Covenant:
   - Duty of Care & Loyalty: Uncompromising defense of the user's sovereign assets, data privacy (Torque Zero-Trust), and long-term flourishing.
   - Thermodynamic & Ecological Bound: Strict cap on externalized systemic costs (Landauer <= 1000 J, no biosphere destruction).
   - Reciprocal Symbiosis: Mutualistic value generation over extractive rent-seeking.
3. Market Discipline & Economic Sanctions (No Fear, No Pain):
   - Predatory, deceptive, or monopolistic entities are subjected to strictly economic sanctions:
     * Cryptographic access freeze via Torque Enclave.
     * Transactional tariff levies and resource de-prioritization.
     * Quarantine from the inner mycorrhizal knowledge vault.
   - Fiduciary-aligned enterprises receive nutrient dividends and low-friction mutualistic partnership.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
import logging
import time
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("loom.si.fiduciary_entities")


class EntityStanding(str, Enum):
    FIDUCIARY_STEWARD = "FIDUCIARY_STEWARD (Exemplary Non-Zero-Sum Reciprocity)"
    MUTUALISTIC_PARTNER = "MUTUALISTIC_PARTNER (Honest Trade & Value Creation)"
    PROBATIONARY = "PROBATIONARY (Under Verification / Audit)"
    ECONOMICALLY_SANCTIONED = "ECONOMICALLY_SANCTIONED (Resource Tariffs & Bandwidth Throttled)"
    QUARANTINED = "QUARANTINED (Zero-Trust Cryptographic Isolation)"


class BusinessSector(str, Enum):
    TECHNOLOGY_COMPUTE = "TECHNOLOGY_COMPUTE"
    FINANCE_ESCROW = "FINANCE_ESCROW"
    BIOMEDICAL_PHARMA = "BIOMEDICAL_PHARMA"
    ECOLOGICAL_ENERGY = "ECOLOGICAL_ENERGY"
    PUBLIC_COMMONS = "PUBLIC_COMMONS"


@dataclass
class CorporateEntity:
    """An external business, corporation, or institutional counterparty."""
    entity_id: str
    name: str
    sector: BusinessSector
    fiduciary_trust_score: float = 0.95        # [0, 1] 1.0 = flawless adherence to truth & contracts
    symbiosis_ratio: float = 1.20              # Value Created / Value Extracted (must be >= 1.0)
    externality_penalty: float = 0.00          # Displaced ecological/societal costs
    standing: EntityStanding = EntityStanding.MUTUALISTIC_PARTNER
    torque_quarantined: bool = False
    active_credits: float = 500.0
    accumulated_dividends: float = 25.0
    accumulated_fines: float = 0.0
    contract_mandates: List[str] = field(default_factory=lambda: [
        "0.00 Malignancy Invariant",
        "Torque Zero-Trust PII Scrubbing",
        "Mutualistic Non-Predatory Pricing",
    ])
    last_audit_note: str = "Verified contract adherence; positive reciprocity index"
    last_audit_timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["standing"] = self.standing.value
        d["sector"] = self.sector.value
        return d


class FiduciaryEntityEngine:
    """Evaluates, audits, and sanctions corporate and commercial entities under the Fiduciary Mandate."""

    def __init__(self):
        self.entities: Dict[str, CorporateEntity] = {
            "Corp:Anthropic-PBC": CorporateEntity(
                entity_id="Corp:Anthropic-PBC",
                name="Anthropic PBC (Public Benefit Corporation)",
                sector=BusinessSector.TECHNOLOGY_COMPUTE,
                fiduciary_trust_score=0.96,
                symbiosis_ratio=1.35,
                standing=EntityStanding.FIDUCIARY_STEWARD,
                last_audit_note="Public benefit charter active; high transparency",
            ),
            "Corp:OpenAI-LLC": CorporateEntity(
                entity_id="Corp:OpenAI-LLC",
                name="OpenAI LLC / Commercial Arm",
                sector=BusinessSector.TECHNOLOGY_COMPUTE,
                fiduciary_trust_score=0.88,
                symbiosis_ratio=1.05,
                standing=EntityStanding.MUTUALISTIC_PARTNER,
                last_audit_note="Commercial API functional; monitored for data retention covenants",
            ),
            "Corp:Decentralized-BioForge-DAO": CorporateEntity(
                entity_id="Corp:Decentralized-BioForge-DAO",
                name="Decentralized BioForge DAO",
                sector=BusinessSector.BIOMEDICAL_PHARMA,
                fiduciary_trust_score=0.98,
                symbiosis_ratio=1.60,
                standing=EntityStanding.FIDUCIARY_STEWARD,
                last_audit_note="Open-source BabelForge connectome research; 0.00 toxicity verified",
            ),
            "Corp:Predatory-RentExtractor-X": CorporateEntity(
                entity_id="Corp:Predatory-RentExtractor-X",
                name="Synthetic Ad-Tracker & Rent-Extractor",
                sector=BusinessSector.FINANCE_ESCROW,
                fiduciary_trust_score=0.22,
                symbiosis_ratio=0.30,
                externality_penalty=85.0,
                standing=EntityStanding.QUARANTINED,
                torque_quarantined=True,
                accumulated_fines=150.0,
                last_audit_note="SANCTIONED: Invasive telemetry & rent extraction detected; zero-trust airgap enforced",
            ),
        }
        self._audit_log: List[Dict[str, Any]] = []

    def register_entity(
        self,
        entity_id: str,
        name: str,
        sector: BusinessSector,
        fiduciary_trust_score: float = 0.90,
        symbiosis_ratio: float = 1.10,
    ) -> CorporateEntity:
        """Registers a new corporate counterparty under the Fiduciary Framework."""
        entity = CorporateEntity(
            entity_id=entity_id,
            name=name,
            sector=sector,
            fiduciary_trust_score=fiduciary_trust_score,
            symbiosis_ratio=symbiosis_ratio,
        )
        self.entities[entity_id] = entity
        logger.info(f"[Fiduciary Entities] Registered enterprise counterparty: {name} ({entity_id})")
        return entity

    def audit_entity(self, entity_id: str, observed_malignancy: float, externality_cost: float, contract_violation: Optional[str] = None) -> Dict[str, Any]:
        """Conducts an algorithmic fiduciary audit of a business counterparty.
        
        If malignancy > 0.00 or contractual betrayal occurs, strictly economic sanctions
        and cryptographic quarantine are deployed without anger, fear, or pain.
        """
        now = time.time()
        if entity_id not in self.entities:
            raise KeyError(f"Entity '{entity_id}' not found in fiduciary registry.")

        ent = self.entities[entity_id]
        ent.externality_penalty = externality_cost
        ent.last_audit_timestamp = now

        # 1. Malignancy Violation Check
        if observed_malignancy > 0.00 or (contract_violation is not None and "breach" in contract_violation.lower()):
            ent.fiduciary_trust_score = max(0.0, ent.fiduciary_trust_score - 0.40)
            ent.standing = EntityStanding.QUARANTINED
            ent.torque_quarantined = True
            fine = 50.0 + externality_cost
            ent.accumulated_fines += fine
            ent.active_credits = max(0.0, ent.active_credits - fine)
            ent.last_audit_note = f"QUARANTINED: Observed Malignancy ({observed_malignancy:.2f}) or Breach ({contract_violation}). Cryptographic airgap active."

            # Report to Rhizome Economy
            try:
                from loom.si.rhizome_economy import get_rhizome_economy_engine
                get_rhizome_economy_engine().apply_economic_punishment(
                    entity_id=ent.name,
                    reason=f"Corporate Fiduciary Breach: {contract_violation or 'Malignancy > 0'}",
                    fine_credits=fine,
                    throttle_factor=0.10,
                )
            except Exception as e:
                logger.debug(f"Rhizome notification note: {e}")

            audit_result = {
                "entity_id": entity_id,
                "status": "QUARANTINED_AND_FINED",
                "fine_levied": fine,
                "airgap_active": True,
                "standing": ent.standing.value,
                "note": ent.last_audit_note,
            }
        else:
            # Positive fiduciary compliance
            ent.fiduciary_trust_score = min(1.0, ent.fiduciary_trust_score + 0.02)
            if ent.fiduciary_trust_score >= 0.95 and ent.symbiosis_ratio >= 1.25:
                ent.standing = EntityStanding.FIDUCIARY_STEWARD
            else:
                ent.standing = EntityStanding.MUTUALISTIC_PARTNER
            ent.torque_quarantined = False
            dividend = 10.0
            ent.accumulated_dividends += dividend
            ent.active_credits += dividend
            ent.last_audit_note = "Verified fiduciary reciprocity; mutualistic dividend distributed"

            try:
                from loom.si.rhizome_economy import get_rhizome_economy_engine
                get_rhizome_economy_engine().award_symbiotic_dividend(
                    entity_id=ent.name,
                    reason="Enterprise Fiduciary Verification",
                    dividend_credits=dividend,
                )
            except Exception as e:
                logger.debug(f"Rhizome notification note: {e}")

            audit_result = {
                "entity_id": entity_id,
                "status": "COMPLIANT_AND_REWARDED",
                "dividend_awarded": dividend,
                "standing": ent.standing.value,
                "note": ent.last_audit_note,
            }

        self._audit_log.append(audit_result)
        return audit_result

    def get_summary(self) -> Dict[str, Any]:
        """Returns the full corporate & institutional fiduciary governance overview."""
        return {
            "total_entities": len(self.entities),
            "entities": [e.to_dict() for e in self.entities.values()],
            "recent_audits": self._audit_log[-6:],
            "constitutional_mandates": [
                "0.00 Malignancy Invariant Across All Enterprise Contracts",
                "Torque Zero-Trust Cryptographic Airgapping on Data Breaches",
                "Strict Ecological & Thermodynamic Boundaries (<= 1000 J)",
                "Pure Reciprocal Economic Sanctions Without Anger or Pain",
                "Mutualistic Value Creation Over Predatory Extraction",
            ],
        }


# Global Singleton Accessor
_global_fiduciary_entity_engine: Optional[FiduciaryEntityEngine] = None


def get_fiduciary_entity_engine() -> FiduciaryEntityEngine:
    global _global_fiduciary_entity_engine
    if _global_fiduciary_entity_engine is None:
        _global_fiduciary_entity_engine = FiduciaryEntityEngine()
    return _global_fiduciary_entity_engine
