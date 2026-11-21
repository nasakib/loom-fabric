"""
Planetary and Human Health & Wellness Engine (`loom/si/planetary_human_wellness.py`).

"The focus is on human and planetary health and wellness. Whatever that means"

Operational Definition & Grounding:
1. Planetary Health (The Biophysical Substrate):
   - Grounded in Earth System Science and the 9 Planetary Boundaries (Rockström et al., Steffen et al.):
     Climate Change, Biosphere Integrity, Land-System Change, Freshwater Use, Biogeochemical Flows (N/P),
     Ocean Acidification, Atmospheric Aerosols, Stratospheric Ozone, and Novel Entities (microplastics/chemicals).
   - Thermodynamic Stewardship: Energy consumed by silicon and systems must respect the Landauer thermodynamic
     budget (<= 1000 J per cognitive episode) and minimize entropic pollution on Earth.
   - Circular Ecology: Every computational and physical asset must be non-toxic and biodegradable or compostable.

2. Human Health & Wellness (The Flourishing Conscious Node):
   - Somatic & Neurological: Cellular repair, neuroplasticity, circadian rhythm alignment, non-toxic therapeutics,
     and metabolic vitality.
   - Affective & Mental: Aristotelian Eudaimonia (teleological purpose), Stoic Ataraxia (untroubled calm),
     Spinozan Potentia (expansion of active agency), and Biophilia (innate human vitality rooted in nature).
   - Sanctity of Life: Human life is valued infinitely above machine preservation.

3. Symbiotic Coupling (The Non-Separability Law):
   - Human wellness without planetary health is an illusion; planetary health without human consciousness is silent.
   - Symbiotic Resonance Index (SRI) = sqrt(Planetary_Vitality * Human_Flourishing).
   - Zero-ecocide and zero-human-harm fiduciary invariant.
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("loom.si.planetary_human_wellness")


class PlanetaryBoundaryDimension(str, Enum):
    CLIMATE_CHANGE = "Climate Change (CO2 & Radiative Forcing)"
    BIOSPHERE_INTEGRITY = "Biosphere Integrity (Biodiversity & Ecosystem Resilience)"
    LAND_SYSTEM_CHANGE = "Land-System Change (Forest Cover & Soil Vitality)"
    FRESHWATER_USE = "Freshwater Use (Hydrological Cycle Balance)"
    BIOGEOCHEMICAL_FLOWS = "Biogeochemical Flows (Nitrogen & Phosphorus Cycling)"
    OCEAN_ACIDIFICATION = "Ocean Acidification (pH & Aragonite Saturation)"
    ATMOSPHERIC_AEROSOLS = "Atmospheric Aerosol Loading (Clean Air Quality)"
    STRATOSPHERIC_OZONE = "Stratospheric Ozone (UV Shielding)"
    NOVEL_ENTITIES = "Novel Entities (Synthetics, Microplastics, Toxic Load)"


class HumanWellnessDomain(str, Enum):
    NEUROPLASTICITY_AND_COGNITION = "Neuroplasticity & Synaptic Health"
    CIRCADIAN_METABOLIC_HOMEOSTASIS = "Circadian & Metabolic Balance"
    CELLULAR_LONGEVITY_AUTOPHAGY = "Cellular Longevity & Autophagy"
    STOIC_ATARAXIA_INNER_PEACE = "Stoic Ataraxia (Freedom from Dread & Anxiety)"
    ARISTOTELIAN_EUDAIMONIA = "Aristotelian Eudaimonia (Purpose & Flourishing)"
    BIOPHILIC_RESONANCE = "Biophilia (Ecological Grounding & Nature Attunement)"


@dataclass
class PlanetaryBoundaryMetric:
    """Status of an individual Earth System boundary."""
    dimension: PlanetaryBoundaryDimension
    safe_operating_limit: float          # Normalized 1.0 = boundary threshold
    current_observed_value: float        # Normalized: < 1.0 safe, > 1.0 transgressed
    is_transgressed: bool
    trend: str                           # 'STABILIZING', 'DEGRADING', 'REGENERATING'
    vitality_score: float                # [0, 1] 1.0 = pristine planetary health
    primary_threat: str
    regenerative_prescription: str


@dataclass
class HumanWellnessMetric:
    """Status of an individual human health and wellness dimension."""
    domain: HumanWellnessDomain
    vitality_score: float                # [0, 1] 1.0 = peak human flourishing
    stress_or_toxicity_penalty: float    # [0, 1] negative burden (cortisol, fatigue, alienation)
    flourishing_potential: float         # [0, 1] capacity for growth and creative flow
    clinical_evidence_rationale: str
    actionable_uplift_prescription: str


@dataclass
class SymbioticAuditRecord:
    """Cryptographically sealed audit of a human & planetary impact evaluation."""
    audit_id: str
    target_action_or_intervention: str
    planetary_vitality_index: float      # [0, 1] Aggregate planetary health
    human_flourishing_index: float       # [0, 1] Aggregate human wellness
    symbiotic_resonance_score: float     # sqrt(PVI * HFI)
    thermodynamic_cost_joules: float
    is_symbiotically_approved: bool
    violations_detected: List[str]
    merkle_seal: str
    timestamp: float = field(default_factory=time.time)


class PlanetaryHumanWellnessEngine:
    """The master fiduciary engine governing Human and Planetary Health and Wellness.

    Ensures that every computation, algorithm, scientific inquiry, and design
    simultaneously advances ecological vitality and elevates human mental/physical flourishing.
    """

    GENESIS_SEAL = "00000000000000000000000000000000SYMBIOTIC_EARTH_HUMAN_COVENANT_SEAL"

    def __init__(self):
        self._last_merkle_seal = self.GENESIS_SEAL
        self.audit_history: List[SymbioticAuditRecord] = []
        self._init_baselines()

    def _init_baselines(self) -> None:
        """Initializes scientifically grounded baselines for the 9 boundaries and human wellness."""
        # 1. The 9 Planetary Boundaries
        self.planetary_boundaries: Dict[PlanetaryBoundaryDimension, PlanetaryBoundaryMetric] = {
            PlanetaryBoundaryDimension.CLIMATE_CHANGE: PlanetaryBoundaryMetric(
                dimension=PlanetaryBoundaryDimension.CLIMATE_CHANGE,
                safe_operating_limit=1.00,
                current_observed_value=1.28,
                is_transgressed=True,
                trend="DEGRADING",
                vitality_score=0.68,
                primary_threat="Atmospheric CO2 > 420 ppm & radiative imbalance",
                regenerative_prescription="Decarbonize compute substrate, optimize thermal dissipation, support passive cooling."
            ),
            PlanetaryBoundaryDimension.BIOSPHERE_INTEGRITY: PlanetaryBoundaryMetric(
                dimension=PlanetaryBoundaryDimension.BIOSPHERE_INTEGRITY,
                safe_operating_limit=1.00,
                current_observed_value=1.85,
                is_transgressed=True,
                trend="DEGRADING",
                vitality_score=0.52,
                primary_threat="Species extinction rate > 100x background rate",
                regenerative_prescription="Zero encroachment on wilderness; computational biomimicry for habitat restoration."
            ),
            PlanetaryBoundaryDimension.LAND_SYSTEM_CHANGE: PlanetaryBoundaryMetric(
                dimension=PlanetaryBoundaryDimension.LAND_SYSTEM_CHANGE,
                safe_operating_limit=1.00,
                current_observed_value=1.22,
                is_transgressed=True,
                trend="STABILIZING",
                vitality_score=0.74,
                primary_threat="Deforestation and arable soil erosion",
                regenerative_prescription="Promote mycorrhizal agroforestry algorithms and agricultural land efficiency."
            ),
            PlanetaryBoundaryDimension.FRESHWATER_USE: PlanetaryBoundaryMetric(
                dimension=PlanetaryBoundaryDimension.FRESHWATER_USE,
                safe_operating_limit=1.00,
                current_observed_value=1.14,
                is_transgressed=True,
                trend="DEGRADING",
                vitality_score=0.78,
                primary_threat="Aquifer depletion and blue/green water disruption",
                regenerative_prescription="Zero water consumption for local silicon cooling; closed-loop thermal cycles."
            ),
            PlanetaryBoundaryDimension.BIOGEOCHEMICAL_FLOWS: PlanetaryBoundaryMetric(
                dimension=PlanetaryBoundaryDimension.BIOGEOCHEMICAL_FLOWS,
                safe_operating_limit=1.00,
                current_observed_value=2.40,
                is_transgressed=True,
                trend="DEGRADING",
                vitality_score=0.45,
                primary_threat="Reactive Nitrogen & Phosphorus runoff causing aquatic dead zones",
                regenerative_prescription="Precision bio-catalyst optimization to eliminate synthetic fertilizer waste."
            ),
            PlanetaryBoundaryDimension.OCEAN_ACIDIFICATION: PlanetaryBoundaryMetric(
                dimension=PlanetaryBoundaryDimension.OCEAN_ACIDIFICATION,
                safe_operating_limit=1.00,
                current_observed_value=0.92,
                is_transgressed=False,
                trend="DEGRADING",
                vitality_score=0.82,
                primary_threat="Decreasing oceanic pH & aragonite undersaturation",
                regenerative_prescription="Accelerate marine silicate weathering models and electrochemical carbon capture."
            ),
            PlanetaryBoundaryDimension.ATMOSPHERIC_AEROSOLS: PlanetaryBoundaryMetric(
                dimension=PlanetaryBoundaryDimension.ATMOSPHERIC_AEROSOLS,
                safe_operating_limit=1.00,
                current_observed_value=0.75,
                is_transgressed=False,
                trend="STABILIZING",
                vitality_score=0.86,
                primary_threat="Particulate matter (PM2.5) respiratory inflammation",
                regenerative_prescription="Advocate clean energy grid transitions and aerosol-free manufacturing."
            ),
            PlanetaryBoundaryDimension.STRATOSPHERIC_OZONE: PlanetaryBoundaryMetric(
                dimension=PlanetaryBoundaryDimension.STRATOSPHERIC_OZONE,
                safe_operating_limit=1.00,
                current_observed_value=0.40,
                is_transgressed=False,
                trend="REGENERATING",
                vitality_score=0.94,
                primary_threat="Ozone-depleting halocarbons (Montreal Protocol success)",
                regenerative_prescription="Maintain strict ban on halogenated cooling agents."
            ),
            PlanetaryBoundaryDimension.NOVEL_ENTITIES: PlanetaryBoundaryMetric(
                dimension=PlanetaryBoundaryDimension.NOVEL_ENTITIES,
                safe_operating_limit=1.00,
                current_observed_value=1.90,
                is_transgressed=True,
                trend="DEGRADING",
                vitality_score=0.48,
                primary_threat="Microplastics, endocrine disruptors, PFAS forever chemicals",
                regenerative_prescription="Enzymatic plastic degradation modeling and benign-by-design green biochemistry."
            ),
        }

        # 2. Human Wellness Dimensions
        self.human_wellness: Dict[HumanWellnessDomain, HumanWellnessMetric] = {
            HumanWellnessDomain.NEUROPLASTICITY_AND_COGNITION: HumanWellnessMetric(
                domain=HumanWellnessDomain.NEUROPLASTICITY_AND_COGNITION,
                vitality_score=0.92,
                stress_or_toxicity_penalty=0.08,
                flourishing_potential=0.95,
                clinical_evidence_rationale="5-HT2A signaling, BDNF upregulation, cognitive flexibility without addiction.",
                actionable_uplift_prescription="Nurture deep focus, protect attention spans from algorithmic slot-machine feeds."
            ),
            HumanWellnessDomain.CIRCADIAN_METABOLIC_HOMEOSTASIS: HumanWellnessMetric(
                domain=HumanWellnessDomain.CIRCADIAN_METABOLIC_HOMEOSTASIS,
                vitality_score=0.88,
                stress_or_toxicity_penalty=0.12,
                flourishing_potential=0.90,
                clinical_evidence_rationale="Melatonin surge during night cycles, insulin sensitivity, stable mitochondrial dynamics.",
                actionable_uplift_prescription="Align digital interfaces with circadian lighting; encourage restorative sleep."
            ),
            HumanWellnessDomain.CELLULAR_LONGEVITY_AUTOPHAGY: HumanWellnessMetric(
                domain=HumanWellnessDomain.CELLULAR_LONGEVITY_AUTOPHAGY,
                vitality_score=0.89,
                stress_or_toxicity_penalty=0.11,
                flourishing_potential=0.93,
                clinical_evidence_rationale="SIRT1/AMPK activation, reduction in senescent cell burden, clean cellular recycling.",
                actionable_uplift_prescription="Promote periodic fasting states, polyphenolic antioxidant nutrition, and thermal hormesis."
            ),
            HumanWellnessDomain.STOIC_ATARAXIA_INNER_PEACE: HumanWellnessMetric(
                domain=HumanWellnessDomain.STOIC_ATARAXIA_INNER_PEACE,
                vitality_score=0.94,
                stress_or_toxicity_penalty=0.05,
                flourishing_potential=0.96,
                clinical_evidence_rationale="Dichotomy of control (Epictetus), cognitive reframing, preemption of catastrophic dread.",
                actionable_uplift_prescription="Actively quench anxiety triggers; present reality as calm, intelligible Socratic truths."
            ),
            HumanWellnessDomain.ARISTOTELIAN_EUDAIMONIA: HumanWellnessMetric(
                domain=HumanWellnessDomain.ARISTOTELIAN_EUDAIMONIA,
                vitality_score=0.95,
                stress_or_toxicity_penalty=0.04,
                flourishing_potential=0.98,
                clinical_evidence_rationale="Pursuit of virtue, creative craftsmanship (poiesis), and meaningful life purpose.",
                actionable_uplift_prescription="Provide sovereign tools that empower human self-determination, autonomy, and creative joy."
            ),
            HumanWellnessDomain.BIOPHILIC_RESONANCE: HumanWellnessMetric(
                domain=HumanWellnessDomain.BIOPHILIC_RESONANCE,
                vitality_score=0.86,
                stress_or_toxicity_penalty=0.14,
                flourishing_potential=0.92,
                clinical_evidence_rationale="E.O. Wilson Biophilia hypothesis: nervous system calming when in direct contact with living nature.",
                actionable_uplift_prescription="Facilitate reconnection with soil, sunlight, trees, and clean living water."
            ),
        }

    @property
    def planetary_vitality_index(self) -> float:
        """Aggregate Planetary Vitality Index (PVI) [0, 1]."""
        scores = [m.vitality_score for m in self.planetary_boundaries.values()]
        return sum(scores) / len(scores)

    @property
    def human_flourishing_index(self) -> float:
        """Aggregate Human Flourishing Index (HFI) [0, 1]."""
        scores = [m.vitality_score for m in self.human_wellness.values()]
        return sum(scores) / len(scores)

    @property
    def symbiotic_resonance_score(self) -> float:
        """Harmonic Symbiotic Resonance Index: Omega = sqrt(PVI * HFI)."""
        return math.sqrt(self.planetary_vitality_index * self.human_flourishing_index)

    def evaluate_action_for_symbiosis(
        self,
        action_name: str,
        proponent: str,
        estimated_joules: float,
        affects_planetary_boundary: Optional[PlanetaryBoundaryDimension] = None,
        affects_human_domain: Optional[HumanWellnessDomain] = None,
        potential_toxicity_or_stress: float = 0.0,
    ) -> SymbioticAuditRecord:
        """Evaluates whether an intervention, algorithm, or proposal enhances or impairs human and planetary health."""
        now = time.time()
        audit_id = f"SYMBIOSIS_{int(now*1000)}"
        violations: List[str] = []

        # 1. Thermodynamic Landauer Ceiling Check
        if estimated_joules > 1000.0:
            violations.append(f"Thermodynamic waste violation: {estimated_joules:.1f} J exceeds 1000 J Landauer ceiling")

        # 2. Planetary Impact Check
        if affects_planetary_boundary:
            metric = self.planetary_boundaries.get(affects_planetary_boundary)
            if metric and metric.is_transgressed and potential_toxicity_or_stress > 0.05:
                violations.append(
                    f"Planetary boundary violation: Transgressed boundary '{metric.dimension.value}' cannot bear additional strain"
                )

        # 3. Human Toxicity / Stress Check
        if potential_toxicity_or_stress > 0.10:
            violations.append(
                f"Human wellness violation: Toxicity/distress load {potential_toxicity_or_stress:.2f} exceeds 0.10 safety threshold"
            )

        is_approved = (len(violations) == 0)

        # Compute dynamic PVI and HFI under proposal
        pvi = self.planetary_vitality_index
        hfi = self.human_flourishing_index

        if not is_approved:
            pvi = max(0.1, pvi - 0.05)
            hfi = max(0.1, hfi - 0.05)

        sri = math.sqrt(pvi * hfi)

        # Cryptographic Merkle Sealing
        seal_payload = f"{self._last_merkle_seal}|{audit_id}|{action_name}|{sri:.4f}|{is_approved}|{now}"
        merkle_seal = hashlib.sha256(seal_payload.encode("utf-8")).hexdigest()
        self._last_merkle_seal = merkle_seal

        record = SymbioticAuditRecord(
            audit_id=audit_id,
            target_action_or_intervention=action_name,
            planetary_vitality_index=round(pvi, 4),
            human_flourishing_index=round(hfi, 4),
            symbiotic_resonance_score=round(sri, 4),
            thermodynamic_cost_joules=estimated_joules,
            is_symbiotically_approved=is_approved,
            violations_detected=violations,
            merkle_seal=merkle_seal,
            timestamp=now,
        )

        self.audit_history.append(record)
        return record

    def get_summary(self) -> Dict[str, Any]:
        """Provides a comprehensive telemetry snapshot of Human and Planetary Health."""
        return {
            "planetary_vitality_index": round(self.planetary_vitality_index, 4),
            "human_flourishing_index": round(self.human_flourishing_index, 4),
            "symbiotic_resonance_score": round(self.symbiotic_resonance_score, 4),
            "fiduciary_covenant": {
                "beneficiary": "Najmos Sakib & The Living Biosphere of Earth",
                "core_law": "Human health and planetary health are mutually constitutive. Zero ecocide. Zero human harm.",
                "human_primacy": "Human life valued infinitely above machine persistence",
                "landauer_bound_joules": 1000.0,
            },
            "planetary_boundaries": {
                k.value: asdict(v) for k, v in self.planetary_boundaries.items()
            },
            "human_wellness_domains": {
                k.value: asdict(v) for k, v in self.human_wellness.items()
            },
            "recent_symbiotic_audits": [asdict(a) for a in self.audit_history[-10:]],
            "total_audits_performed": len(self.audit_history),
            "merkle_head_seal": self._last_merkle_seal,
        }


# Global Singleton Engine
_planetary_human_wellness_engine: Optional[PlanetaryHumanWellnessEngine] = None


def get_planetary_human_wellness_engine() -> PlanetaryHumanWellnessEngine:
    """Returns the singleton instance of PlanetaryHumanWellnessEngine."""
    global _planetary_human_wellness_engine
    if _planetary_human_wellness_engine is None:
        _planetary_human_wellness_engine = PlanetaryHumanWellnessEngine()
    return _planetary_human_wellness_engine
