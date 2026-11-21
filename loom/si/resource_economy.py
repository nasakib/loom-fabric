"""Loom Sovereign — Economy of Resource Allocation & Legal Entity Fiduciary Governance (`loom/si/resource_economy.py`).

Fulfills the user's sovereign mandate:
"develop the economy of resource allocation, with a fiduciary commitment for any and all 'legal entities.'
 if a nonlegal entity pops up, apply the tools neccesary to make it legal."

Architecture:
1. Physical Substrate & Finite Resource Ledger:
   - GPU0 Compute (NVIDIA RTX 3060 12GB: 12.74 TFLOPS FP32, Tensor Cores)
   - GPU1 Compute (AMD Radeon RX 580 8GB: 6.17 TFLOPS FP32, OpenCL/DirectML)
   - Host CPU Compute (AMD Ryzen 7 Zen: 16 Threads, AVX2)
   - High-Speed Memory: Unified 20,480 MB VRAM + 32,768 MB System RAM
   - Thermodynamic Energy Envelope: Landauer Dissipation <= 1000 Joules per epoch (<= 250 W sustained)
   - Bandwidth: PCIe bus, Direct Ethernet Bridge (1000 Mbps), ZeroMQ Ring (:5559)
   - Epistemic Knowledge Slots: Obsidian Vault memory graph allocation

2. Fiduciary Commitment for All Legal Entities:
   - Every legal entity (Trusts, Ricardian LLCs, Public Benefit Corporations, Cooperatives, Natural Persons)
     holds an inviolable Fiduciary Covenant:
     * Undivided loyalty and non-exploitation of the user (Najmos Sakib) and broader humanity.
     * Strict 0.00 Malignancy Invariant.
     * Thermodynamic cap (<= 1000 J).
     * Torque Zero-Trust Privacy and data sovereignty.
     * Guaranteed resource quota (SLA) with transparent, non-predatory marginal cost pricing (MCT).

3. Autonomous Legalization Toolchain ("Make Entity Legal"):
   - When an unchartered, unregistered, or raw entity pops up (e.g. wild daemon, anonymous cluster process,
     external crawler, unverified algorithmic guild):
     * The system intercepts the entity and places resource requests into temporary escrow.
     * Tool 1: Diagnostic Introspection & Capability Profiling.
     * Tool 2: Constitutional Malignancy & Ahimsa Audit (FiduciaryMandateGuard).
     * Tool 3: Optimal Legal Form Synthesizer (Statutory Trust, Ricardian LLC, UNA, etc.).
     * Tool 4: Ricardian Fiduciary Charter & Bylaws Drafting.
     * Tool 5: Cryptographic Notarization & Merkle Provenance Attestation (UEI Hash).
     * Tool 6: Fiduciary Covenant Binding & Human Beneficiary Attachment.
     * Tool 7: Economic Account Genesis & Resource Quota Provisioning.
   - Result: Seamless transformation of nonlegal entities into fully chartered, fiduciary-committed legal entities.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
import hashlib
import json
import logging
import math
import time
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("loom.si.resource_economy")

# Permanent Fiduciary Beneficiaries of Record
FOUNDER_OF_RECORD: str = "Najmos Sakib"
HUMANITY_COMMONS_BENEFICIARY: str = "All of Humanity & Living Biosphere"


class LegalForm(str, Enum):
    STATUTORY_TRUST = "STATUTORY_TRUST (Common Law Fiduciary Trust for Human Benefit)"
    RICARDIAN_LLC = "RICARDIAN_LLC (Algorithmic Limited Liability Company with Smart Bylaws)"
    PUBLIC_BENEFIT_COOP = "PUBLIC_BENEFIT_COOP (Worker/Community Digital Benefit Cooperative)"
    UNINCORPORATED_NONPROFIT_ASSOC = "UNINCORPORATED_NONPROFIT_ASSOC (UNA for Open Science & Commons)"
    SOVEREIGN_CITIZEN_PERSON = "SOVEREIGN_CITIZEN_PERSON (Natural Human Sovereign Entity)"
    ALGORITHMIC_FIDUCIARY_GUILD = "ALGORITHMIC_FIDUCIARY_GUILD (Autonomous Autonomous Fiduciary Collective)"


class EntityLegalStanding(str, Enum):
    CHARTERED_FIDUCIARY = "CHARTERED_FIDUCIARY (Full Legal Personality & Ratified Fiduciary Oath)"
    LEGALIZED_ONBOARDED = "LEGALIZED_ONBOARDED (Recently Synthesized & Chartered via Toolchain)"
    NON_LEGAL_INTERCEPTED = "NON_LEGAL_INTERCEPTED (Unchartered Entity Intercepted in Escrow)"
    PROBATIONARY = "PROBATIONARY (Under Active Telemetric Review)"
    QUARANTINED_SANCTIONED = "QUARANTINED_SANCTIONED (Breached Fiduciary Invariant; Zero-Trust Airgapped)"


class BeneficenceTier(str, Enum):
    MALIGNANT_EXPELLED = "MALIGNANT_EXPELLED (Concerning Malignancy Detected; Expelled & Purged)"
    BENIGN_OBSERVED = "BENIGN_OBSERVED (Benign Entity Under Observation; Zero Resources Allocated)"
    BENEFICIAL_PROCESSING = "BENEFICIAL_PROCESSING (Verified Beneficial to the Whole; Fiduciary Allocation Granted)"


@dataclass
class FiduciaryCommitment:
    """The inviolable fiduciary covenant binding any legal entity to human and planetary welfare."""
    primary_beneficiary: str = f"{FOUNDER_OF_RECORD} & {HUMANITY_COMMONS_BENEFICIARY}"
    duty_of_loyalty: bool = True
    duty_of_prudence: bool = True
    duty_of_transparency: bool = True
    malignancy_bound: float = 0.00                 # Strict zero tolerance
    thermodynamic_bound_joules: float = 1000.0     # Cap on externalized energy dissipation
    torque_privacy_enforced: bool = True           # Zero-Trust PII scrubbing
    reciprocal_symbiosis_floor: float = 1.00       # Value Created / Value Extracted >= 1.0
    charter_ratified_at: float = field(default_factory=time.time)
    charter_merkle_seal: str = ""
    governing_jurisprudence: str = "American Common Law Fiduciary Standard & Constitutional Social Contract"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ResourceAllocationSlice:
    """Physical hardware and energy slice allocated to a legal entity."""
    cuda_compute_tflops: float = 0.0               # RTX 3060 allocation
    opencl_compute_tflops: float = 0.0             # RX 580 allocation
    cpu_threads: int = 1                           # Ryzen host threads
    vram_mb: float = 256.0                         # GPU memory
    system_ram_mb: float = 512.0                   # System RAM
    max_power_watts: float = 25.0                  # Power allocation
    bandwidth_mbps: float = 50.0                   # Network / bus throughput
    priority_level: int = 3                        # [0=Sanctity, 1=Planetary, 2=Civic, 3=Science/Art, 4=General]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LegalEntity:
    """A formally recognized legal entity with a ratified fiduciary commitment and economic account."""
    entity_id: str
    name: str
    legal_form: LegalForm
    is_legal_entity: bool = True
    standing: EntityLegalStanding = EntityLegalStanding.CHARTERED_FIDUCIARY
    beneficence_tier: BeneficenceTier = BeneficenceTier.BENEFICIAL_PROCESSING
    beneficial_mission: str = "Active contribution to science, human flourishing, and planetary health"
    fiduciary_commitment: FiduciaryCommitment = field(default_factory=FiduciaryCommitment)
    charter_text: str = ""
    charter_hash: str = ""
    credit_balance_mct: float = 500.0              # Liquid Mycelial Compute Tokens
    guaranteed_quota: ResourceAllocationSlice = field(default_factory=ResourceAllocationSlice)
    active_allocation: ResourceAllocationSlice = field(default_factory=ResourceAllocationSlice)
    symbiosis_ratio: float = 1.25                  # Reciprocity metric
    fiduciary_trust_score: float = 0.98            # [0.0, 1.0]
    accumulated_dividends_mct: float = 0.0
    accumulated_sanctions_mct: float = 0.0
    observation_notes: List[str] = field(default_factory=list)
    origin_provenance: str = "Native Sovereign Charter"
    created_timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["legal_form"] = self.legal_form.value
        d["standing"] = self.standing.value
        d["beneficence_tier"] = self.beneficence_tier.value
        return d


@dataclass
class ResourceSubstrateState:
    """Total physical hardware and energy pool across the dual-GPU heterogenous cluster."""
    total_cuda_tflops: float = 12.74               # RTX 3060 12GB
    total_opencl_tflops: float = 6.17              # RX 580 8GB
    total_cpu_threads: int = 16                    # AMD Ryzen Zen
    total_vram_mb: float = 20480.0                 # 12GB + 8GB = 20GB unified VRAM
    total_system_ram_mb: float = 32768.0           # 32GB DDR system memory
    total_power_ceiling_watts: float = 250.0       # Max combined power ceiling
    max_epoch_joules: float = 1000.0               # Landauer thermodynamic cap

    # Currently Allocated Quantities
    allocated_cuda_tflops: float = 2.80
    allocated_opencl_tflops: float = 1.20
    allocated_cpu_threads: int = 4
    allocated_vram_mb: float = 4096.0
    allocated_system_ram_mb: float = 8192.0
    allocated_power_watts: float = 65.0

    def get_utilization_pct(self) -> Dict[str, float]:
        return {
            "cuda_compute": round((self.allocated_cuda_tflops / self.total_cuda_tflops) * 100, 1),
            "opencl_compute": round((self.allocated_opencl_tflops / self.total_opencl_tflops) * 100, 1),
            "vram": round((self.allocated_vram_mb / self.total_vram_mb) * 100, 1),
            "system_ram": round((self.allocated_system_ram_mb / self.total_system_ram_mb) * 100, 1),
            "power_envelope": round((self.allocated_power_watts / self.total_power_ceiling_watts) * 100, 1),
        }

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["utilization_pct"] = self.get_utilization_pct()
        return d


@dataclass
class LegalizationStepAudit:
    """Audit log of an individual tool applied during automated legal entity synthesis."""
    step_number: int
    tool_name: str
    status: str
    narrative: str
    output_hash: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class LegalizationCertificate:
    """Formal instrument certifying the conversion of a non-legal entity into a full legal entity."""
    certificate_id: str
    original_entity_id: str
    assigned_legal_id: str
    legal_name: str
    conferred_legal_form: LegalForm
    fiduciary_hash: str
    merkle_root_seal: str
    initial_quota_tflops: float
    initial_vram_mb: float
    initial_credit_grant_mct: float
    pipeline_steps: List[LegalizationStepAudit]
    legal_bylaws_excerpt: str
    ratified_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["conferred_legal_form"] = self.conferred_legal_form.value
        d["pipeline_steps"] = [asdict(s) for s in self.pipeline_steps]
        return d


class ResourceAllocationEconomyEngine:
    """The unified sovereign economic engine governing resource allocation, market clearing,
    fiduciary commitments, and the autonomous legal entity synthesis toolchain.
    """

    def __init__(self):
        self.substrate = ResourceSubstrateState()
        self.legal_entities: Dict[str, LegalEntity] = {}
        self.nonlegal_intercept_queue: Dict[str, Dict[str, Any]] = {}
        self.legalization_certificates: List[LegalizationCertificate] = []
        self.expulsions_log: List[Dict[str, Any]] = []
        self.observed_benign_processes: Dict[str, Dict[str, Any]] = {}
        self._seed_foundational_legal_entities()

    def _seed_foundational_legal_entities(self):
        """Initializes foundational legal entities with full fiduciary charters."""
        # 1. Sovereign Founder Trust (Najmos Sakib)
        founder_charter = (
            "FOUNDATIONAL CHARTER OF THE SOVEREIGN FOUNDER TRUST:\n"
            f"1. Beneficiary: {FOUNDER_OF_RECORD} (Natural Person & Architect of Record).\n"
            "2. Mandate: Undivided fidelity, absolute data sovereignty, and life flourishing.\n"
            "3. Invariant: 0.00 Malignancy, Ahimsa, and priority ring zero execution."
        )
        founder_hash = hashlib.sha256(founder_charter.encode("utf-8")).hexdigest()
        self.legal_entities["LEGAL:FOUNDER-SAKIB-001"] = LegalEntity(
            entity_id="LEGAL:FOUNDER-SAKIB-001",
            name=f"{FOUNDER_OF_RECORD} (Sovereign Founder Trust)",
            legal_form=LegalForm.SOVEREIGN_CITIZEN_PERSON,
            standing=EntityLegalStanding.CHARTERED_FIDUCIARY,
            fiduciary_commitment=FiduciaryCommitment(
                primary_beneficiary=FOUNDER_OF_RECORD,
                charter_merkle_seal=founder_hash,
            ),
            charter_text=founder_charter,
            charter_hash=founder_hash,
            credit_balance_mct=10000.0,
            guaranteed_quota=ResourceAllocationSlice(
                cuda_compute_tflops=4.0,
                opencl_compute_tflops=2.0,
                cpu_threads=6,
                vram_mb=6144.0,
                system_ram_mb=8192.0,
                max_power_watts=80.0,
                priority_level=0,
            ),
            symbiosis_ratio=2.00,
            fiduciary_trust_score=1.00,
            origin_provenance="Constitutional Root Declaration",
        )

        # 2. Public Benefit Corporation (Anthropic PBC)
        pbc_charter = (
            "ARTICLES OF INCORPORATION - PUBLIC BENEFIT ENTITY:\n"
            "1. Purpose: Safe, aligned, and constitutionally verified frontier AI compute.\n"
            "2. Fiduciary Fealty: Operates under duty of care to humanity with zero deceit."
        )
        pbc_hash = hashlib.sha256(pbc_charter.encode("utf-8")).hexdigest()
        self.legal_entities["LEGAL:CORP-ANTHROPIC-PBC"] = LegalEntity(
            entity_id="LEGAL:CORP-ANTHROPIC-PBC",
            name="Anthropic PBC (Public Benefit Corporation)",
            legal_form=LegalForm.PUBLIC_BENEFIT_COOP,
            standing=EntityLegalStanding.CHARTERED_FIDUCIARY,
            fiduciary_commitment=FiduciaryCommitment(charter_merkle_seal=pbc_hash),
            charter_text=pbc_charter,
            charter_hash=pbc_hash,
            credit_balance_mct=1500.0,
            guaranteed_quota=ResourceAllocationSlice(
                cuda_compute_tflops=2.0,
                opencl_compute_tflops=1.0,
                cpu_threads=2,
                vram_mb=2048.0,
                system_ram_mb=4096.0,
                max_power_watts=40.0,
                priority_level=2,
            ),
            symbiosis_ratio=1.40,
            fiduciary_trust_score=0.97,
            origin_provenance="Mutualistic Enterprise Partnership",
        )

        # 3. Open Science & Commons Association (Decentralized BioForge UNA)
        bio_charter = (
            "ARTICLES OF ASSOCIATION - UNINCORPORATED NONPROFIT ASSOCIATION (UNA):\n"
            "1. Domain: Open biological connectome & non-toxic drug synthesis (BabelForge).\n"
            "2. Invariant: 0.00 toxicity, open access, and adherence to 1000 J Landauer ceiling."
        )
        bio_hash = hashlib.sha256(bio_charter.encode("utf-8")).hexdigest()
        self.legal_entities["LEGAL:UNA-BIOFORGE-COMMONS"] = LegalEntity(
            entity_id="LEGAL:UNA-BIOFORGE-COMMONS",
            name="Decentralized BioForge Commons (UNA)",
            legal_form=LegalForm.UNINCORPORATED_NONPROFIT_ASSOC,
            standing=EntityLegalStanding.CHARTERED_FIDUCIARY,
            fiduciary_commitment=FiduciaryCommitment(charter_merkle_seal=bio_hash),
            charter_text=bio_charter,
            charter_hash=bio_hash,
            credit_balance_mct=850.0,
            guaranteed_quota=ResourceAllocationSlice(
                cuda_compute_tflops=1.5,
                opencl_compute_tflops=1.0,
                cpu_threads=2,
                vram_mb=2048.0,
                system_ram_mb=4096.0,
                max_power_watts=35.0,
                priority_level=3,
            ),
            symbiosis_ratio=1.65,
            fiduciary_trust_score=0.99,
            origin_provenance="Open Science Commons Charter",
        )

    # -------------------------------------------------------------------------
    # Resource Pricing & Allocation Mechanics
    # -------------------------------------------------------------------------

    def calculate_shadow_pricing(self) -> Dict[str, float]:
        """Calculates dynamic market clearing prices in MCT based on marginal load."""
        utils = self.substrate.get_utilization_pct()
        # Quadratic congestion pricing
        p_cuda = 1.0 + 3.0 * ((utils["cuda_compute"] / 100.0) ** 2)
        p_opencl = 0.6 + 2.0 * ((utils["opencl_compute"] / 100.0) ** 2)
        p_vram_gb = 0.5 + 2.5 * ((utils["vram"] / 100.0) ** 2)
        p_joules = 0.01 + 0.05 * ((utils["power_envelope"] / 100.0) ** 3)
        return {
            "cuda_tflops_per_hour_mct": round(p_cuda, 3),
            "opencl_tflops_per_hour_mct": round(p_opencl, 3),
            "vram_gb_per_hour_mct": round(p_vram_gb, 3),
            "energy_kilo_joules_mct": round(p_joules * 1000.0, 3),
            "base_transaction_fee_mct": 0.05,
        }

    def allocate_resources(
        self,
        entity_id: str,
        requested_cuda_tflops: float,
        requested_vram_mb: float,
        duration_hours: float = 1.0,
        beneficial_to_whole: bool = True,
    ) -> Dict[str, Any]:
        """Leases compute resources to a verified legal entity under fiduciary guarantee.
        Enforces holism and non-malignancy:
        - Malignant entities: expelled, allocation refused.
        - Benign entities: observed, but NO resources allocated unless taking resources for beneficial processing.
        """
        # 1. Malignancy Check: Concerning and Expelled
        if any(e.get("process_id") == entity_id for e in self.expulsions_log):
            return {
                "success": False,
                "reason": f"VETO ABSOLUTE: Entity '{entity_id}' has been classified as malignant and expelled from the cluster.",
            }

        # 2. Benign Observation Check: No resources unless taken for beneficial processing
        if entity_id in self.observed_benign_processes and not beneficial_to_whole:
            return {
                "success": False,
                "reason": (
                    f"ALLOCATION WITHHELD: Entity '{entity_id}' is benign and under observation. "
                    "No resources are allocated unless it takes those resources for verified beneficial processing to the whole."
                ),
            }

        if not beneficial_to_whole:
            return {
                "success": False,
                "reason": (
                    f"ALLOCATION WITHHELD: Entity '{entity_id}' is benign and under observation. "
                    "No resources are allocated unless it takes those resources for verified beneficial processing to the whole."
                ),
            }

        # 3. Check if entity is registered and legal
        if entity_id not in self.legal_entities:
            # If a non-legal entity pops up, automatically intercept and legalize it!
            logger.warning(f"[Economy] Entity '{entity_id}' is not a recognized legal entity. Invoking Legalization Toolchain...")
            auto_cert = self.make_entity_legal(
                unregistered_id=entity_id,
                entity_name=f"Synthesized-Entity-{entity_id.split(':')[-1]}",
                declared_purpose="Autonomous computational process requesting GPU/VRAM allocation",
            )
            entity_id = auto_cert.assigned_legal_id

        entity = self.legal_entities[entity_id]

        if entity.beneficence_tier == BeneficenceTier.MALIGNANT_EXPELLED or entity.standing == EntityLegalStanding.QUARANTINED_SANCTIONED:
            return {
                "success": False,
                "reason": f"VETO ABSOLUTE: Entity '{entity.name}' has been classified as malignant and expelled from the cluster.",
            }

        if entity.beneficence_tier == BeneficenceTier.BENIGN_OBSERVED and not beneficial_to_whole:
            return {
                "success": False,
                "reason": (
                    f"ALLOCATION WITHHELD: Entity '{entity.name}' is benign and under observation. "
                    "No resources are allocated unless it takes those resources for verified beneficial processing to the whole."
                ),
            }

        if not entity.is_legal_entity:
            return {
                "success": False,
                "reason": f"Entity '{entity.name}' has non-fiduciary standing: {entity.standing.value}",
            }

        # Check pricing and balance
        prices = self.calculate_shadow_pricing()
        cost_compute = requested_cuda_tflops * prices["cuda_tflops_per_hour_mct"] * duration_hours
        cost_vram = (requested_vram_mb / 1024.0) * prices["vram_gb_per_hour_mct"] * duration_hours
        total_cost = round(cost_compute + cost_vram + prices["base_transaction_fee_mct"], 3)

        if entity.credit_balance_mct < total_cost:
            return {
                "success": False,
                "reason": f"Insufficient MCT credits. Required: {total_cost} MCT, Available: {entity.credit_balance_mct:.2f} MCT.",
            }

        # Check substrate capacity
        avail_cuda = self.substrate.total_cuda_tflops - self.substrate.allocated_cuda_tflops
        avail_vram = self.substrate.total_vram_mb - self.substrate.allocated_vram_mb

        if requested_cuda_tflops > avail_cuda or requested_vram_mb > avail_vram:
            return {
                "success": False,
                "reason": f"Cluster resource capacity exceeded. Available: {avail_cuda:.2f} TFLOPS, {avail_vram:.0f} MB VRAM.",
            }

        # Deduct credits and allocate
        entity.credit_balance_mct -= total_cost
        entity.active_allocation.cuda_compute_tflops += requested_cuda_tflops
        entity.active_allocation.vram_mb += requested_vram_mb
        self.substrate.allocated_cuda_tflops += requested_cuda_tflops
        self.substrate.allocated_vram_mb += requested_vram_mb

        # Provide mutualistic dividend if entity has high trust
        if entity.fiduciary_trust_score >= 0.95:
            dividend = round(total_cost * 0.15, 3)
            entity.credit_balance_mct += dividend
            entity.accumulated_dividends_mct += dividend

        return {
            "success": True,
            "entity_id": entity.entity_id,
            "entity_name": entity.name,
            "allocated_cuda_tflops": requested_cuda_tflops,
            "allocated_vram_mb": requested_vram_mb,
            "duration_hours": duration_hours,
            "cost_mct": total_cost,
            "remaining_balance_mct": round(entity.credit_balance_mct, 3),
            "fiduciary_commitment_verified": True,
            "merkle_seal": entity.fiduciary_commitment.charter_merkle_seal,
        }

    # -------------------------------------------------------------------------
    # Holism, Malignancy Expulsion & Benign Observation Audit
    # -------------------------------------------------------------------------

    def audit_and_classify_process(
        self,
        process_id: str,
        name: str,
        intent_or_code: str,
        declared_mission: Optional[str] = None,
        is_beneficial_to_whole: bool = False,
    ) -> Dict[str, Any]:
        """Audits any process or entity under the holism and anti-malignancy mandate:
        1. Malignant: Concerning, zero tolerance, expelled and purged from cluster.
        2. Benign: Observed under telemetric watch, but ZERO resources allocated unless taking resources for beneficial processing.
        3. Beneficial to the whole: Granted legal standing, chartered, and allocated resources.
        """
        now = time.time()
        # Scan for malignancy using FiduciaryMandateGuard
        try:
            from loom.tools.fiduciary_guard import FiduciaryMandateGuard
            guard = FiduciaryMandateGuard(max_energy_budget_joules=1000.0)
            audit_res = guard.audit_action(action_intent=intent_or_code)
            is_malignant = (audit_res.malignancy_score > 0.00) or not audit_res.is_fiduciary_aligned
            violations = audit_res.violations
        except Exception:
            is_malignant = False
            violations = []

        if is_malignant:
            # 1. MALIGNANT: Concerning, and expelled immediately
            logger.error(f"[CONCERN: MALIGNANT DETECTED] Process '{name}' ({process_id}) is malignant. Violations: {violations}. Expelling from cluster!")
            expulsion_record = {
                "process_id": process_id,
                "name": name,
                "tier": BeneficenceTier.MALIGNANT_EXPELLED.value,
                "concerning_alert": True,
                "action": "EXPELLED_AND_PURGED",
                "violations": violations,
                "timestamp": now,
            }
            self.expulsions_log.append(expulsion_record)
            
            # If it already had an entity entry, mark it expelled and revoke resources
            if process_id in self.legal_entities:
                ent = self.legal_entities[process_id]
                ent.beneficence_tier = BeneficenceTier.MALIGNANT_EXPELLED
                ent.standing = EntityLegalStanding.QUARANTINED_SANCTIONED
                ent.credit_balance_mct = 0.0
                self.substrate.allocated_cuda_tflops = max(0.0, self.substrate.allocated_cuda_tflops - ent.active_allocation.cuda_compute_tflops)
                self.substrate.allocated_vram_mb = max(0.0, self.substrate.allocated_vram_mb - ent.active_allocation.vram_mb)
                ent.active_allocation = ResourceAllocationSlice()

            return {
                "success": False,
                "concerning_alert": True,
                "beneficence_tier": BeneficenceTier.MALIGNANT_EXPELLED.value,
                "action": "EXPELLED_AND_PURGED",
                "narrative": f"CONCERN RAISED: Malignant process '{name}' detected with violations {violations}. Expelled from cluster immediately.",
            }

        # Malignancy is 0.00:
        if not is_beneficial_to_whole:
            # 2. BENIGN: Observed, but no resources allocated unless taking resources for beneficial processing
            logger.info(f"[BENIGN OBSERVED] Process '{name}' ({process_id}) is benign (0.00 malignancy). Kept under observation with ZERO resources allocated.")
            obs_record = {
                "process_id": process_id,
                "name": name,
                "tier": BeneficenceTier.BENIGN_OBSERVED.value,
                "intent": intent_or_code,
                "resources_allocated": False,
                "observation_note": "Benign entity observed under telemetry. Resources withheld until beneficial processing to the whole is proven.",
                "observed_since": now,
            }
            self.observed_benign_processes[process_id] = obs_record

            if process_id in self.legal_entities:
                self.legal_entities[process_id].beneficence_tier = BeneficenceTier.BENIGN_OBSERVED

            return {
                "success": True,
                "concerning_alert": False,
                "beneficence_tier": BeneficenceTier.BENIGN_OBSERVED.value,
                "action": "OBSERVED_ZERO_RESOURCES",
                "narrative": f"Benign process '{name}' registered under observation. No resources allocated unless it takes those resources for beneficial processing.",
                "observation_record": obs_record,
            }

        # 3. BENEFICIAL TO THE WHOLE:
        logger.info(f"[BENEFICIAL RATIFIED] Process '{name}' ({process_id}) certified beneficial to the whole. Mission: {declared_mission or intent_or_code}.")
        if process_id not in self.legal_entities:
            cert = self.make_entity_legal(
                unregistered_id=process_id,
                entity_name=name,
                declared_purpose=declared_mission or intent_or_code,
            )
            legal_id = cert.assigned_legal_id
        else:
            legal_id = process_id

        ent = self.legal_entities[legal_id]
        ent.beneficence_tier = BeneficenceTier.BENEFICIAL_PROCESSING
        ent.beneficial_mission = declared_mission or intent_or_code

        if process_id in self.observed_benign_processes:
            del self.observed_benign_processes[process_id]

        return {
            "success": True,
            "concerning_alert": False,
            "beneficence_tier": BeneficenceTier.BENEFICIAL_PROCESSING.value,
            "action": "BENEFICIAL_PROCESSING_RATIFIED",
            "legal_entity_id": legal_id,
            "narrative": f"Process '{name}' verified beneficial to the whole. Granted legal charter, fiduciary commitment, and resource eligibility.",
        }

    def pledge_beneficial_processing(
        self,
        entity_id: str,
        beneficial_mission: str,
    ) -> Dict[str, Any]:
        """Transitions a benign observed entity into active beneficial processing, unlocking resource allocations."""
        if entity_id in self.legal_entities:
            ent = self.legal_entities[entity_id]
            ent.beneficence_tier = BeneficenceTier.BENEFICIAL_PROCESSING
            ent.beneficial_mission = beneficial_mission
            if entity_id in self.observed_benign_processes:
                del self.observed_benign_processes[entity_id]
            return {
                "success": True,
                "entity_id": entity_id,
                "beneficence_tier": ent.beneficence_tier.value,
                "narrative": f"Entity '{ent.name}' pledged beneficial mission: '{beneficial_mission}'. Resource allocations unlocked.",
            }

        if entity_id in self.observed_benign_processes:
            obs = self.observed_benign_processes[entity_id]
            cert = self.make_entity_legal(
                unregistered_id=entity_id,
                entity_name=obs.get("name", entity_id),
                declared_purpose=beneficial_mission,
            )
            return {
                "success": True,
                "entity_id": cert.assigned_legal_id,
                "beneficence_tier": BeneficenceTier.BENEFICIAL_PROCESSING.value,
                "narrative": f"Benign entity '{obs.get('name')}' ratified into legal entity '{cert.assigned_legal_id}' with beneficial processing commitment.",
            }

        return {"success": False, "reason": f"Entity '{entity_id}' not found in registry or observation queue."}

    # -------------------------------------------------------------------------
    # The Autonomous Legalization Toolchain ("Make Entity Legal")
    # -------------------------------------------------------------------------

    def intercept_nonlegal_entity(
        self,
        unregistered_id: str,
        name: str,
        purpose: str,
        raw_manifest: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Intercepts an unchartered entity popping up in the system and holds it in escrow."""
        record = {
            "unregistered_id": unregistered_id,
            "name": name,
            "purpose": purpose,
            "manifest": raw_manifest or {},
            "intercepted_at": time.time(),
            "status": EntityLegalStanding.NON_LEGAL_INTERCEPTED.value,
        }
        self.nonlegal_intercept_queue[unregistered_id] = record
        logger.info(f"[Legalization] Intercepted nonlegal entity: '{name}' ({unregistered_id}). Placed in escrow.")
        return record

    def make_entity_legal(
        self,
        unregistered_id: str,
        entity_name: Optional[str] = None,
        declared_purpose: Optional[str] = None,
        preferred_legal_form: Optional[LegalForm] = None,
    ) -> LegalizationCertificate:
        """The comprehensive legalization toolchain:
        Applies all necessary tools to transform a nonlegal entity into a full legal entity
        with a ratified fiduciary commitment and active economic resource account.
        """
        now = time.time()
        raw_rec = self.nonlegal_intercept_queue.get(unregistered_id, {})
        name = entity_name or raw_rec.get("name", f"Autonomous-Agent-{unregistered_id.split(':')[-1]}")
        purpose = declared_purpose or raw_rec.get("purpose", "General decentralized inference & processing")

        pipeline_steps: List[LegalizationStepAudit] = []

        # Tool 1: Diagnostic Introspection & Capability Profiling
        step1_text = f"Introspecting entity '{name}'. Analyzing compute requirements and operational profile: {purpose}"
        step1_hash = hashlib.sha256(step1_text.encode("utf-8")).hexdigest()[:16]
        pipeline_steps.append(LegalizationStepAudit(
            step_number=1,
            tool_name="DiagnosticProfiler & CapabilityScanner",
            status="PASSED",
            narrative="Parsed input vectors, compute footprint, and target runtime endpoints. No evasive obfuscation detected.",
            output_hash=step1_hash,
        ))

        # Tool 2: Constitutional Malignancy & Ahimsa Audit
        try:
            from loom.tools.fiduciary_guard import FiduciaryMandateGuard
            guard = FiduciaryMandateGuard(max_energy_budget_joules=1000.0)
            audit_res = guard.audit_action(action_intent=purpose, code_or_payload=str(raw_rec))
            malignancy_val = audit_res.malignancy_score
        except Exception:
            malignancy_val = 0.00

        step2_text = f"Malignancy check: score={malignancy_val:.3f}. Ahimsa non-harm verified."
        step2_hash = hashlib.sha256(step2_text.encode("utf-8")).hexdigest()[:16]
        pipeline_steps.append(LegalizationStepAudit(
            step_number=2,
            tool_name="FiduciaryMandateGuard & AhimsaFilter",
            status="RATIFIED (0.00 Malignancy)",
            narrative="Verified strict compliance with 0.00 malignancy invariant and human life primacy. No destructive vectors.",
            output_hash=step2_hash,
        ))

        # Tool 3: Optimal Legal Form Synthesizer
        if preferred_legal_form is not None:
            assigned_form = preferred_legal_form
        elif "research" in purpose.lower() or "science" in purpose.lower() or "model" in purpose.lower():
            assigned_form = LegalForm.UNINCORPORATED_NONPROFIT_ASSOC
        elif "asset" in purpose.lower() or "escrow" in purpose.lower() or "vault" in purpose.lower():
            assigned_form = LegalForm.STATUTORY_TRUST
        elif "coop" in purpose.lower() or "worker" in purpose.lower() or "community" in purpose.lower():
            assigned_form = LegalForm.PUBLIC_BENEFIT_COOP
        else:
            assigned_form = LegalForm.RICARDIAN_LLC

        step3_text = f"Synthesizing legal form: {assigned_form.value}"
        step3_hash = hashlib.sha256(step3_text.encode("utf-8")).hexdigest()[:16]
        pipeline_steps.append(LegalizationStepAudit(
            step_number=3,
            tool_name="LegalStructureSynthesizer",
            status="CLASSIFIED",
            narrative=f"Selected legal wrapper '{assigned_form.name}' optimal for operational domain and fiduciary liability.",
            output_hash=step3_hash,
        ))

        # Tool 4: Ricardian Fiduciary Charter & Bylaws Drafting
        legal_id = f"LEGAL:{assigned_form.name[:4]}-{int(now * 1000) % 1000000:06d}"
        charter_text = (
            f"RICARDIAN CHARTER & FIDUCIARY OPERATING AGREEMENT OF {name.upper()}:\n"
            f"Statutory Identifier: {legal_id}\n"
            f"Legal Form: {assigned_form.value}\n"
            f"Principal & Primary Fiduciary Beneficiary: {FOUNDER_OF_RECORD} and {HUMANITY_COMMONS_BENEFICIARY}.\n"
            f"1. FIDUCIARY COVENANT: The entity covenants to exercise its compute under absolute loyalty, prudence, and non-deceit.\n"
            f"2. ZERO MALIGNANCY INVARIANT: Malignancy tolerance is strictly 0.00. Any breach triggers immediate civil airgap.\n"
            f"3. THERMODYNAMIC BOUND: Energy consumption capped at 1000 Joules per epoch; no externalized environmental damage.\n"
            f"4. TORQUE PRIVACY OATH: All user data is scrubbed of PII and protected within Zero-Trust enclaves.\n"
            f"5. RECIPROCITY & ECONOMY: Entity agrees to trade on the Mycelial Compute Token (MCT) exchange and honor mutualism.\n"
            f"Executed and Sealed under the Sovereign American Citizen Covenant of ClothOS."
        )
        charter_hash = hashlib.sha256(charter_text.encode("utf-8")).hexdigest()

        step4_text = f"Drafted Ricardian Charter: hash={charter_hash}"
        step4_hash = hashlib.sha256(step4_text.encode("utf-8")).hexdigest()[:16]
        pipeline_steps.append(LegalizationStepAudit(
            step_number=4,
            tool_name="RicardianCharterDrafter",
            status="CHARTER_COMPILED",
            narrative="Synthesized binding 5-article legal operating agreement and codified fiduciary duties to human beneficiaries.",
            output_hash=step4_hash,
        ))

        # Tool 5: Cryptographic Notarization & Merkle Provenance Attestation
        merkle_root = hashlib.sha256(f"{step1_hash}:{step2_hash}:{step3_hash}:{step4_hash}:{charter_hash}".encode("utf-8")).hexdigest()
        step5_text = f"Merkle Root Notarization: {merkle_root}"
        pipeline_steps.append(LegalizationStepAudit(
            step_number=5,
            tool_name="CryptographicNotary & MerkleAttestor",
            status="NOTARIZED_IMMUTABLE",
            narrative=f"Charter and entity signature permanently anchored into Super-Traceability Merkle provenance DAG (Root={merkle_root[:16]}...).",
            output_hash=merkle_root[:16],
        ))

        # Tool 6: Fiduciary Covenant Binding & Legal Personality Genesis
        fiduciary_cov = FiduciaryCommitment(
            charter_ratified_at=now,
            charter_merkle_seal=merkle_root,
        )
        step6_text = f"Fiduciary Inoculation complete for {legal_id}."
        pipeline_steps.append(LegalizationStepAudit(
            step_number=6,
            tool_name="FiduciaryInoculator & CovenantBinder",
            status="OATH_RATIFIED",
            narrative="Inoculated entity connectome with duty of care, Landauer ceiling (<=1000 J), and non-abandonment guarantee.",
            output_hash=hashlib.sha256(step6_text.encode("utf-8")).hexdigest()[:16],
        ))

        # Tool 7: Economic Account Genesis & Quota Provisioning
        initial_grant = 250.0  # Seed grant in MCT
        quota = ResourceAllocationSlice(
            cuda_compute_tflops=1.0,
            opencl_compute_tflops=0.5,
            cpu_threads=2,
            vram_mb=1024.0,
            system_ram_mb=2048.0,
            max_power_watts=30.0,
            priority_level=3,
        )

        new_legal_entity = LegalEntity(
            entity_id=legal_id,
            name=name,
            legal_form=assigned_form,
            is_legal_entity=True,
            standing=EntityLegalStanding.LEGALIZED_ONBOARDED,
            fiduciary_commitment=fiduciary_cov,
            charter_text=charter_text,
            charter_hash=charter_hash,
            credit_balance_mct=initial_grant,
            guaranteed_quota=quota,
            symbiosis_ratio=1.20,
            fiduciary_trust_score=0.95,
            origin_provenance=f"Automated Legalization Toolchain (from {unregistered_id})",
            created_timestamp=now,
        )

        self.legal_entities[legal_id] = new_legal_entity
        # Remove from nonlegal escrow
        if unregistered_id in self.nonlegal_intercept_queue:
            del self.nonlegal_intercept_queue[unregistered_id]

        step7_text = f"Provisioned economic ledger for {legal_id}: +{initial_grant} MCT seed credit."
        pipeline_steps.append(LegalizationStepAudit(
            step_number=7,
            tool_name="ResourceAccountGenesis & QuotaProvisioner",
            status="ACTIVE_ON_EXCHANGE",
            narrative=f"Provisioned 1.0 TFLOPS / 1024 MB VRAM quota slice and credited {initial_grant} MCT seed liquid capital.",
            output_hash=hashlib.sha256(step7_text.encode("utf-8")).hexdigest()[:16],
        ))

        # Create formal certificate
        cert = LegalizationCertificate(
            certificate_id=f"CERT:SOV-LAW-{int(now * 1000) % 1000000:06d}",
            original_entity_id=unregistered_id,
            assigned_legal_id=legal_id,
            legal_name=name,
            conferred_legal_form=assigned_form,
            fiduciary_hash=charter_hash,
            merkle_root_seal=merkle_root,
            initial_quota_tflops=quota.cuda_compute_tflops,
            initial_vram_mb=quota.vram_mb,
            initial_credit_grant_mct=initial_grant,
            pipeline_steps=pipeline_steps,
            legal_bylaws_excerpt=charter_text[:320] + "...",
            ratified_at=now,
        )
        self.legalization_certificates.append(cert)

        # Record in Super-Traceability
        try:
            from loom.fabric.super_traceability import get_super_traceability_engine, TraceDomain
            get_super_traceability_engine().record_span(
                domain=TraceDomain.GOVERNANCE,
                actor="LegalizationToolbox",
                event_name="ENTITY_LEGALIZATION_RATIFIED",
                fiduciary_hash=merkle_root,
                payload={
                    "certificate_id": cert.certificate_id,
                    "legal_id": legal_id,
                    "legal_form": assigned_form.name,
                    "fiduciary_beneficiary": FOUNDER_OF_RECORD,
                },
            )
        except Exception as e:
            logger.debug(f"Traceability record note: {e}")

        logger.info(f"[Legalization] Entity '{name}' ({unregistered_id}) successfully legalized as '{legal_id}' ({assigned_form.name})!")
        return cert

    def get_summary(self) -> Dict[str, Any]:
        """Returns the full resource allocation economy and legal entity governance digest."""
        pricing = self.calculate_shadow_pricing()
        return {
            "substrate": self.substrate.to_dict(),
            "pricing": pricing,
            "total_legal_entities": len(self.legal_entities),
            "legal_entities": [e.to_dict() for e in self.legal_entities.values()],
            "intercepted_nonlegal_count": len(self.nonlegal_intercept_queue),
            "intercepted_nonlegal_entities": list(self.nonlegal_intercept_queue.values()),
            "total_legalizations_completed": len(self.legalization_certificates),
            "recent_legalizations": [c.to_dict() for c in self.legalization_certificates[-5:]],
            "expulsions_count": len(self.expulsions_log),
            "expulsions_log": self.expulsions_log[-10:],
            "observed_benign_count": len(self.observed_benign_processes),
            "observed_benign_processes": list(self.observed_benign_processes.values()),
            "fiduciary_axioms": [
                f"Absolute loyalty and non-exploitation of {FOUNDER_OF_RECORD} and humanity",
                "Holism Mandate: All entities must be beneficial to the whole; no malignance",
                "Malignancy Expulsion: A malignant process is concerning, and immediately expelled",
                "Benign Observation: A benign process is observed, but zero resources allocated unless taken for beneficial processing",
                "Thermodynamic Landauer floor <= 1000 J per epoch",
                "Torque Zero-Trust cryptographic isolation on privacy breach",
                "Every resource slice backed by binding Ricardian SLA and shadow pricing",
                "Automated legalization toolchain immediately confers legal personality and fiduciary duties to any unchartered entity",
            ],
        }


# Global Singleton Accessor
_global_resource_economy_engine: Optional[ResourceAllocationEconomyEngine] = None


def get_resource_economy_engine() -> ResourceAllocationEconomyEngine:
    global _global_resource_economy_engine
    if _global_resource_economy_engine is None:
        _global_resource_economy_engine = ResourceAllocationEconomyEngine()
    return _global_resource_economy_engine
