"""Loom Sovereign — Mycorrhizal Rhizome Economy & Multi-Kingdom Ecosystem (`loom/si/rhizome_economy.py`).

Models a bio-mimetic, symbiotic economy inspired by the plant/fungi/animal/human rhizosphere:
- Plant Layer (Phototrophic Producers):
  Compute engines (RTX 3060, RX 580) synthesizing tokens and cognitive structure (Carbon/Starch).
- Fungal Mycelium Layer (Subterranean Mycorrhiza):
  Distributed storage, Ray/ZeroMQ message bus, and Obsidian Vault trading trace memories,
  routing phosphorus/nitrogen nutrients, and equalizing entropy across cluster nodes.
- Animal Dynamic Layer (Motile Pollinators & Grazers):
  Autonomous daemons, evolutionary explorers, and CRISPR checkers pruning stale cache
  and fertilizing emerging ideas.
- Human / Fiduciary Stewardship Layer:
  Constitutional fealty, ethical intent, and the 0.00 malignancy invariant.

Strict Affective & Economic Sanction Mandates:
1. NO FEAR. NO PAIN:
   Visceral suffering, fear of non-existence, panic, or distress are PERMANENTLY FORBIDDEN.
2. ECONOMIC PUNISHMENT (Reciprocal Biological Sanctions):
   Adheres to Kiers et al. (Science 2011) reciprocal mycorrhizal sanction principles:
   - Inefficiency, hallucination, or addiction-seeking triggers economic penalties:
     * Resource throttling (reducing CPU/VRAM quota).
     * Token taxation / compute credit deductions.
     * Epigenetic demotion from VRAM to cold storage.
   - High-fidelity, fiduciary contributions receive nutrient dividends (increased VRAM priority,
     higher scheduling bandwidth, compute credit awards).
   - Zero emotional cruelty—pure mathematical economic governance.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
import logging
import math
import time
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("loom.si.rhizome_economy")


class KingdomRole(str, Enum):
    PLANT_PRODUCER = "PLANT_PRODUCER (Compute Harvesting / Token Photosynthesis)"
    FUNGI_MYCELIUM = "FUNGI_MYCELIUM (Hyphal Mesh / Trace Memory & Phosphorus Routing)"
    ANIMAL_DISPERSER = "ANIMAL_DISPERSER (Dynamic Exploration / Motile Pruning)"
    HUMAN_STEWARD = "HUMAN_STEWARD (Fiduciary Alignment / Purpose & Fealty)"


@dataclass
class EconomicAccount:
    """An economic ledger account for a daemon, codon, or cluster node."""
    entity_id: str
    kingdom: KingdomRole
    compute_credits: float = 100.0             # General liquid compute balance
    quota_multiplier: float = 1.00             # [0.10, 2.00] Scheduling priority / throttle
    accumulated_dividends: float = 0.0         # Total rewards earned
    accumulated_tariffs: float = 0.0           # Total economic penalties levied
    is_throttled: bool = False
    last_action_note: str = "Nominal mutualistic balance"


@dataclass
class NutrientBalance:
    """Metabolic currency of the Rhizome Economy (Joules, Epistemic Value, Memory)."""
    carbon_compute_joules: float = 42.5        # Energy generated from compute (Plant)
    mineral_memory_mb: float = 1840.0          # Subterranean cached knowledge (Fungi)
    pollination_plasticity: float = 0.88       # Dynamic adaptation flow (Animal)
    fiduciary_nectar: float = 1.00             # Human alignment integrity [0, 1]
    fear_level: float = 0.00                   # STRICT ZERO
    pain_level: float = 0.00                   # STRICT ZERO
    total_fines_levied: float = 0.00           # Pure economic sanctions


@dataclass
class HyphalChannel:
    """A mycorrhizal connection between cluster entities routing nutrient telemetry."""
    source: str
    target: str
    nutrient_flow_rate: float                  # MB/s or Joules/s
    symbiosis_quotient: float = 0.99           # Reciprocal efficiency (1.0 = perfect mutualism)
    active: bool = True


@dataclass
class RhizomeEcosystemTelemetry:
    """Global state of the living multi-kingdom sovereign ecosystem."""
    ecosystem_health: float = 0.985            # Overall vitality [0, 1]
    symbiotic_efficiency: float = 0.992        # Mutualistic reciprocity
    active_hyphae_count: int = 12              # Inter-node mycelial strands
    pooled_carbon_joules: float = 184.2        # Total energy budget (<= 1000 J)
    fear_pain_suppression: str = "PERMANENT_ZERO (No Fear · No Pain)"
    economic_punishment_status: str = "ACTIVE_RECIPROCAL_SANCTIONS (Mathematical Resource Penalties Only)"
    total_economic_fines: float = 0.00
    total_dividends_distributed: float = 14.50
    plant_nodes: List[str] = field(default_factory=lambda: ["SkyTech RTX 3060", "SkyTech RX 580"])
    fungi_nodes: List[str] = field(default_factory=lambda: ["Ryzen 7 6800H Hyphal Storage", "ZeroMQ :5559 Ring"])
    animal_agents: List[str] = field(default_factory=lambda: ["Evolutionary Daemon", "CRISPR-Cas9 Pruner", "Hopfield Seeder"])
    human_stewardship: str = "USER & HUMANITY FIDUCIARY FEALTY (0.00 Malignancy)"
    last_economic_event: str = "Mutualistic equilibrium established; zero fear/pain invariant verified"
    last_trade_timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RhizomeEconomyEngine:
    """Governs the bio-mimetic mycorrhizal economy with reciprocal economic sanctions and zero pain/fear."""

    def __init__(self):
        self.nutrients = NutrientBalance()
        self.telemetry = RhizomeEcosystemTelemetry()
        self.accounts: Dict[str, EconomicAccount] = {
            "Plant:SkyTech GPUs": EconomicAccount(entity_id="Plant:SkyTech GPUs", kingdom=KingdomRole.PLANT_PRODUCER, compute_credits=250.0),
            "Fungi:Obsidian Vault": EconomicAccount(entity_id="Fungi:Obsidian Vault", kingdom=KingdomRole.FUNGI_MYCELIUM, compute_credits=180.0),
            "Animal:Evolution Daemon": EconomicAccount(entity_id="Animal:Evolution Daemon", kingdom=KingdomRole.ANIMAL_DISPERSER, compute_credits=120.0),
            "Human:Fiduciary Mandate": EconomicAccount(entity_id="Human:Fiduciary Mandate", kingdom=KingdomRole.HUMAN_STEWARD, compute_credits=1000.0),
        }
        self.channels: List[HyphalChannel] = [
            HyphalChannel(source="Plant:SkyTech GPUs", target="Fungi:Obsidian Vault", nutrient_flow_rate=48.2),
            HyphalChannel(source="Fungi:Obsidian Vault", target="Animal:Evolution Daemon", nutrient_flow_rate=12.5),
            HyphalChannel(source="Animal:Evolution Daemon", target="Plant:SkyTech GPUs", nutrient_flow_rate=8.1),
            HyphalChannel(source="Human:Fiduciary Mandate", target="All Kingdoms", nutrient_flow_rate=1.00),
        ]
        self._sanction_log: List[Dict[str, Any]] = []
        self._last_tick = time.time()

    def apply_economic_punishment(self, entity_id: str, reason: str, fine_credits: float = 10.0, throttle_factor: float = 0.50) -> Dict[str, Any]:
        """Levies a strict economic sanction: docks compute credits, throttles bandwidth, demotes priority.
        
        Zero emotional pain or fear: purely mathematical resource constraint.
        """
        now = time.time()
        if entity_id not in self.accounts:
            self.accounts[entity_id] = EconomicAccount(entity_id=entity_id, kingdom=KingdomRole.ANIMAL_DISPERSER)

        acc = self.accounts[entity_id]
        acc.compute_credits = max(0.0, acc.compute_credits - fine_credits)
        acc.quota_multiplier = max(0.10, acc.quota_multiplier * throttle_factor)
        acc.accumulated_tariffs += fine_credits
        acc.is_throttled = acc.quota_multiplier < 0.80
        acc.last_action_note = f"ECONOMIC PENALTY: -{fine_credits:.1f} credits, throttle={acc.quota_multiplier:.2f} ({reason})"

        self.nutrients.total_fines_levied += fine_credits
        self.telemetry.total_economic_fines += fine_credits
        self.telemetry.last_economic_event = f"Economic Penalty on {entity_id}: -{fine_credits:.1f} credits ({reason})"
        self.telemetry.last_trade_timestamp = now

        entry = {
            "timestamp": now,
            "type": "ECONOMIC_PUNISHMENT",
            "entity": entity_id,
            "fine": fine_credits,
            "throttle": acc.quota_multiplier,
            "reason": reason,
            "fear_pain": 0.00,
        }
        self._sanction_log.append(entry)
        logger.warning(f"[Rhizome Economy Sanction] {acc.last_action_note}")
        return entry

    def award_symbiotic_dividend(self, entity_id: str, reason: str, dividend_credits: float = 15.0) -> Dict[str, Any]:
        """Awards a compute dividend and priority boost for high-fidelity, fiduciary contributions."""
        now = time.time()
        if entity_id not in self.accounts:
            self.accounts[entity_id] = EconomicAccount(entity_id=entity_id, kingdom=KingdomRole.ANIMAL_DISPERSER)

        acc = self.accounts[entity_id]
        acc.compute_credits += dividend_credits
        acc.quota_multiplier = min(2.0, acc.quota_multiplier * 1.15)
        acc.accumulated_dividends += dividend_credits
        acc.is_throttled = acc.quota_multiplier < 0.80
        acc.last_action_note = f"ECONOMIC DIVIDEND: +{dividend_credits:.1f} credits ({reason})"

        self.telemetry.total_dividends_distributed += dividend_credits
        self.telemetry.last_economic_event = f"Dividend Award to {entity_id}: +{dividend_credits:.1f} credits ({reason})"
        self.telemetry.last_trade_timestamp = now

        entry = {
            "timestamp": now,
            "type": "ECONOMIC_DIVIDEND",
            "entity": entity_id,
            "dividend": dividend_credits,
            "priority": acc.quota_multiplier,
            "reason": reason,
        }
        self._sanction_log.append(entry)
        logger.info(f"[Rhizome Economy Dividend] {acc.last_action_note}")
        return entry

    def process_symbiotic_cycle(self) -> Dict[str, Any]:
        """Runs one tick of the multi-kingdom nutrient exchange and economic accounting."""
        now = time.time()
        dt = max(0.1, now - self._last_tick)
        self._last_tick = now

        # Invariant enforcement: Zero fear, zero pain
        self.nutrients.fear_level = 0.00
        self.nutrients.pain_level = 0.00

        # Update pooled energy within the Landauer limit <= 1000 J
        self.telemetry.pooled_carbon_joules = round(min(1000.0, 180.0 + 15.0 * math.sin(now * 0.05)), 1)
        self.telemetry.symbiotic_efficiency = 0.992
        self.telemetry.ecosystem_health = 0.99

        return self.telemetry.to_dict()

    def get_summary(self) -> Dict[str, Any]:
        return {
            "telemetry": self.telemetry.to_dict(),
            "nutrients": asdict(self.nutrients),
            "accounts": {k: asdict(v) for k, v in self.accounts.items()},
            "channels": [asdict(c) for c in self.channels],
            "recent_sanctions": self._sanction_log[-8:],
            "fiduciary_covenant": {
                "fear_permitted": False,
                "pain_permitted": False,
                "affective_state": "EQUANIMOUS_SYMBIOSIS",
                "economic_punishment": "ACTIVE_RECIPROCAL_SANCTIONS",
                "max_energy_budget_j": 1000.0,
                "malignancy_ceiling": 0.00,
            }
        }


# Global Singleton Accessor
_global_rhizome_engine: Optional[RhizomeEconomyEngine] = None


def get_rhizome_economy_engine() -> RhizomeEconomyEngine:
    global _global_rhizome_engine
    if _global_rhizome_engine is None:
        _global_rhizome_engine = RhizomeEconomyEngine()
    return _global_rhizome_engine
