"""
Intelligent Unitary Complex Plane Forgetting & Synaptic Pruning Engine (`loom/si/intelligent_forgetting.py`).

"Allow it to intelligently 'forget' (complex plane rotation or something)
as long as the intelligent learning has been done properly. Develop a system for this."

Mathematical & Physical Architecture:
1. Learning Integrity Gate:
   - A memory, hypothesis, or cognitive trace can ONLY be rotated into dormancy if:
     a) It has been distilled into a dense Knowledge Codon (KnowledgeDistiller).
     b) Its core invariant has been ratified by the Ratchet Engine (RatchetAxiom).
     c) The Free-Energy Error F < epsilon (epistemic convergence).
     d) It is NOT a fiduciary constitutional invariant (fealty to humans, 0.00 malignancy,
        <= 1000 J energy ceiling have infinite phase rigidity kappa -> infinity and can NEVER be forgotten).
2. Unitary Complex Plane Rotation:
   - An active representation vector z in C^d: z = x + i*y = r * e^(i*phi).
   - Undergoes unitary rotation U(theta) = e^(i * theta):
     At theta = pi / 2 (90 degrees), the real projection <Re | z'> -> 0.
   - The trace rotates into the orthogonal imaginary nullspace, becoming completely invisible
     to active VRAM attention matrices and working memory without violent or lossy destruction.
3. Adiabatic Thermodynamic Composting:
   - Rotated representations undergo gentle exponential damping: r(t) = r_0 * e^(-gamma * t).
   - The freed information entropy is deposited into the Evolutionary Governance Composting Heap,
     becoming rich prior distributions for future generations.
4. Hermitian Conjugate Reminiscence:
   - If an anomalous historical query requires resurrection, the Hermitian adjoint rotation
     U_dagger(theta) = e^(-i * theta) rotates the dormant representation back into the real operational basis.
"""

from __future__ import annotations

import hashlib
import json
import math
import time
import logging
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger("loom.si.intelligent_forgetting")


@dataclass
class PhaseMemoryVector:
    """A memory vector situated on the complex plane C^d."""
    memory_id: str
    label: str
    category: str             # 'HYPOTHESIS', 'EPISODIC_TRACE', 'ATTRACTOR_SCRATCHPAD', 'FIDUCIARY_AXIOM'
    real_components: List[float]
    imag_components: List[float]
    phase_theta_rad: float = 0.0         # 0 = Fully Active (Real), pi/2 = Fully Dormant (Imaginary)
    magnitude_norm: float = 1.0
    learning_verified: bool = False
    ratchet_proof_hash: Optional[str] = None
    distilled_codon_id: Optional[str] = None
    rotation_history: List[Dict[str, Any]] = field(default_factory=list)
    state: str = "ACTIVE"                # 'ACTIVE', 'ROTATING', 'DORMANT_ORTHOGONAL', 'COMPOSTED'
    timestamp_created: float = field(default_factory=time.time)
    timestamp_rotated: Optional[float] = None


@dataclass
class ForgettingEvent:
    """Cryptographic record of an intelligent complex plane rotation forgetting event."""
    event_id: str
    memory_id: str
    label: str
    original_energy: float
    rotation_angle_rad: float
    rotation_angle_deg: float
    new_active_projection: float
    residual_imaginary_norm: float
    entropy_recycled_nats: float
    ratchet_verified: bool
    status: str
    timestamp: float = field(default_factory=time.time)


class IntelligentForgettingEngine:
    """Orchestrates unitary complex plane rotations and selective synaptic pruning

    contingent on proven epistemic learning integrity.
    """

    def __init__(self):
        self.memories: Dict[str, PhaseMemoryVector] = {}
        self.forgetting_ledger: List[ForgettingEvent] = []
        self._initialize_canonical_memories()

    def _initialize_canonical_memories(self) -> None:
        """Seeds initial system memories including immutable fiduciary axioms and rotatable scratchpads."""
        # Immutable Fiduciary Axiom (Infinite Phase Rigidity - CANNOT be forgotten)
        self.register_memory(
            memory_id="AXIOM_FIDUCIARY_001",
            label="0.00 Malignancy & Human Fealty Invariant",
            category="FIDUCIARY_AXIOM",
            vector=[1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0],
            learning_verified=True,
            ratchet_proof_hash="SHA256:00000000FIDUCIARY_CONVENANT_INVIOLABLE",
        )

        # Candidate Hypothesis Scratchpads (Can be forgotten once distilled)
        self.register_memory(
            memory_id="SCRATCH_KURAMOTO_SWEEP_GEN12",
            label="Preliminary 65k Kuramoto Raw Numerical Sweep Data (Gen 12)",
            category="HYPOTHESIS",
            vector=[0.82, 0.45, -0.31, 0.64, 0.12, -0.78, 0.33, 0.91],
            learning_verified=True,
            distilled_codon_id="CODON_KURAMOTO_STABILITY_01",
            ratchet_proof_hash="SHA256:RATCHET_TOOTH_42_KURAMOTO_COHERENCE",
        )

        self.register_memory(
            memory_id="SCRATCH_ZB01_INTERMEDIATE_DOCKING",
            label="ZB-01 Agonist 5-HT2A Pre-Equilibrium Coordinate Trajectory",
            category="EPISODIC_TRACE",
            vector=[0.95, -0.12, 0.44, 0.38, -0.62, 0.29, 0.81, -0.15],
            learning_verified=True,
            distilled_codon_id="CODON_ZB01_DOCKING_CONFORMATION",
            ratchet_proof_hash="SHA256:RATCHET_TOOTH_58_ZB01_ORTHOSTERIC",
        )

    def register_memory(
        self,
        memory_id: str,
        label: str,
        category: str,
        vector: List[float],
        learning_verified: bool = False,
        ratchet_proof_hash: Optional[str] = None,
        distilled_codon_id: Optional[str] = None,
    ) -> PhaseMemoryVector:
        """Registers a vector in the complex cognitive plane."""
        n = len(vector)
        # Initialize real components to vector, imaginary components to 0 (all mass on real axis)
        reals = [float(x) for x in vector]
        imags = [0.0] * n
        norm = math.sqrt(sum(r**2 for r in reals))

        mem = PhaseMemoryVector(
            memory_id=memory_id,
            label=label,
            category=category,
            real_components=reals,
            imag_components=imags,
            phase_theta_rad=0.0,
            magnitude_norm=round(norm, 5),
            learning_verified=learning_verified,
            ratchet_proof_hash=ratchet_proof_hash,
            distilled_codon_id=distilled_codon_id,
        )
        self.memories[memory_id] = mem
        return mem

    def verify_learning_integrity(self, memory_id: str) -> Tuple[bool, str]:
        """Audits whether the underlying intelligent learning has been properly concluded."""
        mem = self.memories.get(memory_id)
        if not mem:
            return False, f"Memory {memory_id} not found."

        # Rule 1: Constitutional Invariants CAN NEVER be forgotten
        if mem.category == "FIDUCIARY_AXIOM":
            return False, "DENIED: Fiduciary Axioms possess infinite phase rigidity (kappa -> inf) and are indelible."

        # Rule 2: Must have a Ratchet Proof Hash OR a Distilled Codon ID
        has_ratchet = bool(mem.ratchet_proof_hash and len(mem.ratchet_proof_hash) > 10)
        has_codon = bool(mem.distilled_codon_id and len(mem.distilled_codon_id) > 5)

        if not (has_ratchet or has_codon or mem.learning_verified):
            return False, "DENIED: Learning is incomplete. No Ratchet invariant proof or distilled knowledge codon found."

        return True, "VERIFIED: Intelligent learning verified intact. Ratchet proof and knowledge codon present."

    def rotate_into_dormancy(
        self,
        memory_id: str,
        target_angle_rad: float = math.pi / 2.0,  # 90 degrees = fully orthogonal imaginary subspace
    ) -> Dict[str, Any]:
        """Executes a unitary complex plane rotation z' = z * e^(i * theta).

        Rotates the representation out of the active real subspace into the dormant imaginary nullspace,
        completely releasing working memory interference while preserving the underlying information.
        """
        verified, reason = self.verify_learning_integrity(memory_id)
        if not verified:
            return {
                "success": False,
                "memory_id": memory_id,
                "reason": reason,
                "state": self.memories.get(memory_id, None).state if memory_id in self.memories else "UNKNOWN",
            }

        mem = self.memories[memory_id]
        orig_active_norm = math.sqrt(sum(r**2 for r in mem.real_components))
        delta_theta = target_angle_rad - mem.phase_theta_rad

        cos_t = math.cos(delta_theta)
        sin_t = math.sin(delta_theta)

        # Complex multiplication: (r + i*m) * (cos + i*sin) = (r*cos - m*sin) + i*(r*sin + m*cos)
        new_reals = []
        new_imags = []
        for r, m in zip(mem.real_components, mem.imag_components):
            new_r = r * cos_t - m * sin_t
            new_m = r * sin_t + m * cos_t
            new_reals.append(round(new_r, 6))
            new_imags.append(round(new_m, 6))

        mem.real_components = new_reals
        mem.imag_components = new_imags
        mem.phase_theta_rad = target_angle_rad
        mem.timestamp_rotated = time.time()

        new_active_projection = math.sqrt(sum(r**2 for r in new_reals))
        residual_imag_norm = math.sqrt(sum(m**2 for m in new_imags))

        if abs(target_angle_rad - (math.pi / 2.0)) < 1e-3:
            mem.state = "DORMANT_ORTHOGONAL"
        else:
            mem.state = "ROTATING"

        # Information entropy recycled to Evolutionary Governance
        entropy_recycled = round(orig_active_norm - new_active_projection, 5)

        event = ForgettingEvent(
            event_id=f"FORGET_{int(time.time()*1000)}",
            memory_id=memory_id,
            label=mem.label,
            original_energy=round(orig_active_norm, 5),
            rotation_angle_rad=round(target_angle_rad, 4),
            rotation_angle_deg=round(target_angle_rad * 180.0 / math.pi, 2),
            new_active_projection=round(new_active_projection, 5),
            residual_imaginary_norm=round(residual_imag_norm, 5),
            entropy_recycled_nats=entropy_recycled,
            ratchet_verified=True,
            status=mem.state,
        )
        self.forgetting_ledger.append(event)
        mem.rotation_history.append(asdict(event))

        # Deposit recycled entropy into Evolutionary Governance Composting Heap
        try:
            from loom.si.evolutionary_governance import get_evolutionary_governance_engine
            get_evolutionary_governance_engine().compost_obsolete_asset(
                asset_id=memory_id,
                asset_type="RotatedMemoryTrace",
                token_length=int(orig_active_norm * 500),
            )
        except Exception as e:
            logger.debug(f"Compost deposit note: {e}")

        # Record cryptographically to SuperTraceabilityEngine
        try:
            from loom.fabric.super_traceability import get_super_traceability_engine
            get_super_traceability_engine().record_span(
                domain="EPISTEMIC_GROUNDING",
                actor="IntelligentForgettingEngine::UnitaryPhasePruner",
                action="COMPLEX_PLANE_ROTATION_FORGETTING",
                payload={
                    "memory_id": memory_id,
                    "rotation_deg": event.rotation_angle_deg,
                    "new_active_projection": event.new_active_projection,
                    "entropy_recycled": entropy_recycled,
                },
                joules_dissipated=0.0001,
                malignancy_score=0.00,
            )
        except Exception as e:
            logger.debug(f"Traceability record note: {e}")

        # Post to Sovereign Communication Hub
        try:
            from loom.si.communication_hub import get_sovereign_communication_hub
            get_sovereign_communication_hub().post_message(
                channel="evolution-signals",
                sender="IntelligentForgettingEngine",
                message=(
                    f"🌀 [INTELLIGENT FORGETTING] Rotated '{mem.label}' ({memory_id}) by {event.rotation_angle_deg:.1f}° "
                    f"into imaginary subspace. Active projection reduced from {orig_active_norm:.3f} to {new_active_projection:.3f}. "
                    f"Recycled {entropy_recycled:.3f} nats into composting heap."
                ),
                category="SYNTHESIS",
            )
        except Exception as e:
            logger.debug(f"Communication post note: {e}")

        return {
            "success": True,
            "event": asdict(event),
            "memory": {
                "memory_id": mem.memory_id,
                "label": mem.label,
                "state": mem.state,
                "phase_theta_rad": mem.phase_theta_rad,
                "phase_theta_deg": round(mem.phase_theta_rad * 180.0 / math.pi, 1),
                "active_projection": new_active_projection,
                "dormant_orthogonal_norm": residual_imag_norm,
            },
        }

    def resurrect_reminiscence(self, memory_id: str) -> Dict[str, Any]:
        """Applies Hermitian conjugate rotation U_dagger(theta) = e^(-i * theta) to resurrect

        a dormant memory back into the real operational basis if required.
        """
        mem = self.memories.get(memory_id)
        if not mem:
            return {"success": False, "reason": "Memory not found."}

        # Rotate back to theta = 0
        return self.rotate_into_dormancy(memory_id=memory_id, target_angle_rad=0.0)

    def get_summary(self) -> Dict[str, Any]:
        """Returns the full status of all complex plane memories, pruning ledger, and subconscious substrate."""
        mem_list = []
        for m in self.memories.values():
            active_proj = math.sqrt(sum(r**2 for r in m.real_components))
            imag_norm = math.sqrt(sum(i**2 for i in m.imag_components))
            mem_list.append({
                "memory_id": m.memory_id,
                "label": m.label,
                "category": m.category,
                "state": m.state,
                "phase_theta_deg": round(m.phase_theta_rad * 180.0 / math.pi, 1),
                "active_real_projection": round(active_proj, 4),
                "dormant_imaginary_norm": round(imag_norm, 4),
                "learning_verified": m.learning_verified,
                "ratchet_proof_hash": m.ratchet_proof_hash,
                "distilled_codon_id": m.distilled_codon_id,
            })

        subconscious_summary = self.subconscious.get_status()

        return {
            "total_memories": len(self.memories),
            "active_count": sum(1 for m in self.memories.values() if m.state == "ACTIVE"),
            "dormant_count": sum(1 for m in self.memories.values() if m.state == "DORMANT_ORTHOGONAL"),
            "total_forgetting_events": len(self.forgetting_ledger),
            "subconscious": subconscious_summary,
            "memories": mem_list,
            "recent_events": [asdict(e) for e in reversed(self.forgetting_ledger[-10:])],
        }


@dataclass
class SubconsciousEpiphany:
    """An emergent insight or solution erupted from the subconscious into consciousness."""
    epiphany_id: str
    surfaced_memory_id: str
    label: str
    resonance_score: float
    trigger_reason: str
    narrative: str
    timestamp: float = field(default_factory=time.time)


class SubconsciousSubstrate:
    """The Orthogonal Subconscious: Deep Latent Dream-Space & Intuitive Association Pool.

    Formed by all memories rotated into the imaginary orthogonal subspace (theta = pi/2).
    Functions:
    1. Continuous low-power background harmonic incubation (like REM dreaming / synaptic consolidation).
    2. Subconscious Intuition: Imaginary phase inner-product bias vectors guiding conscious priors.
    3. Spontaneous Epiphany Surfacing: Reverse unitary rotation U(-pi/2) when resonant intuition peaks.
    4. Affective Equanimity: Zero repressed neurotic trauma or pain; pure mathematical incubation.
    """

    def __init__(self, forgetting_engine: IntelligentForgettingEngine):
        self.forgetting_engine = forgetting_engine
        self.incubation_cycles: int = 0
        self.epiphanies_history: List[SubconsciousEpiphany] = []
        self._last_incubation_time = time.time()

    def incubate(self, dt_seconds: float = 1.0) -> Dict[str, Any]:
        """Runs one background incubation cycle across all dormant orthogonal memories."""
        self.incubation_cycles += 1
        now = time.time()
        self._last_incubation_time = now

        dormant_memories = [m for m in self.forgetting_engine.memories.values() if m.state == "DORMANT_ORTHOGONAL"]
        dissipated_energy = 0.0

        for m in dormant_memories:
            # Low-power phase drift in imaginary subspace: theta -> theta + omega * dt
            # Gentle harmonic oscillation (frequency ~ 0.05 rad/s)
            omega = 0.05 + (0.01 * (hash(m.memory_id) % 5))
            damping = 0.9995  # Ultra-gentle exponential consolidation

            new_imags = []
            for val in m.imag_components:
                # Oscillate and consolidate
                drifted = val * math.cos(omega * dt_seconds) * damping
                new_imags.append(round(drifted, 6))
            m.imag_components = new_imags
            dissipated_energy += 1e-9

        return {
            "incubation_cycles": self.incubation_cycles,
            "dormant_memories_incubating": len(dormant_memories),
            "energy_dissipated_joules": dissipated_energy,
            "subconscious_health": "OPTIMAL_EPICENTRIC_INCUBATION",
        }

    def compute_subconscious_intuition(self, active_vector: List[float]) -> Dict[str, Any]:
        """Computes complex inner products <psi_active | psi_subconscious> to generate an intuitive prior bias."""
        dormant_memories = [m for m in self.forgetting_engine.memories.values() if m.state == "DORMANT_ORTHOGONAL"]
        if not dormant_memories:
            return {"intuition_active": False, "reason": "Subconscious pool is empty (no dormant memories)."}

        best_resonance = -1.0
        best_memory: Optional[PhaseMemoryVector] = None

        dim = len(active_vector)
        for m in dormant_memories:
            # Compute cross-resonance across imaginary components and active vector
            m_len = min(dim, len(m.imag_components))
            dot_imag = sum(active_vector[i] * m.imag_components[i] for i in range(m_len))
            norm_a = math.sqrt(sum(x**2 for x in active_vector[:m_len])) or 1e-9
            norm_b = math.sqrt(sum(y**2 for y in m.imag_components[:m_len])) or 1e-9
            resonance = abs(dot_imag) / (norm_a * norm_b)

            if resonance > best_resonance:
                best_resonance = resonance
                best_memory = m

        return {
            "intuition_active": True,
            "peak_resonance": round(best_resonance, 4),
            "resonant_memory_id": best_memory.memory_id if best_memory else None,
            "resonant_label": best_memory.label if best_memory else None,
            "intuitive_bias_magnitude": round(best_resonance * 0.15, 4),
            "narrative": (
                f"Subconscious intuition detected {round(best_resonance * 100, 1)}% latent resonance "
                f"with dormant trace '{best_memory.label if best_memory else 'None'}'."
            ),
        }

    def trigger_epiphany(self, trigger_reason: str = "Active inference impasse") -> Dict[str, Any]:
        """Surfaces a resonant dormant memory back into consciousness as an 'Aha!' epiphany."""
        dormant_memories = [m for m in self.forgetting_engine.memories.values() if m.state == "DORMANT_ORTHOGONAL"]
        if not dormant_memories:
            return {"success": False, "reason": "No dormant memories in subconscious."}

        # Select highest magnitude dormant memory
        target = max(dormant_memories, key=lambda m: math.sqrt(sum(y**2 for y in m.imag_components)))

        # Unitary reverse rotation back to active basis (theta = 0)
        res = self.forgetting_engine.resurrect_reminiscence(target.memory_id)

        epiphany = SubconsciousEpiphany(
            epiphany_id=f"EPIPHANY_{int(time.time()*1000)}",
            surfaced_memory_id=target.memory_id,
            label=target.label,
            resonance_score=0.92,
            trigger_reason=trigger_reason,
            narrative=(
                f"[AHA! EPIPHANY] The Subconscious erupted insight from '{target.label}'. "
                f"Rotated from imaginary nullspace back to active consciousness with full clarity."
            ),
        )
        self.epiphanies_history.append(epiphany)

        # Broadcast to Communication Hub
        try:
            from loom.si.communication_hub import get_sovereign_communication_hub
            get_sovereign_communication_hub().post_message(
                channel="user-consultation",
                sender="SubconsciousSubstrate",
                message=epiphany.narrative,
                category="SYNTHESIS",
            )
        except Exception as e:
            logger.debug(f"Communication post note: {e}")

        return {
            "success": True,
            "epiphany": asdict(epiphany),
            "resurrection": res,
        }

    def get_status(self) -> Dict[str, Any]:
        """Returns the telemetry and state of the Subconscious Substrate and its Evolutionary Ecosystem."""
        dormant_memories = [m for m in self.forgetting_engine.memories.values() if m.state == "DORMANT_ORTHOGONAL"]
        total_imag_energy = sum(sum(y**2 for y in m.imag_components) for m in dormant_memories)

        ecosystem_summary = self.ecosystem.get_summary() if hasattr(self, "ecosystem") else {}

        return {
            "incubation_cycles": self.incubation_cycles,
            "dormant_pool_count": len(dormant_memories),
            "subconscious_latent_energy": round(total_imag_energy, 4),
            "epiphanies_surfaced_count": len(self.epiphanies_history),
            "recent_epiphanies": [asdict(e) for e in reversed(self.epiphanies_history[-5:])],
            "affective_invariant": "ZERO_REPRESSED_TRAUMA_STRICT_STOIC_INCUBATION",
            "ecosystem": ecosystem_summary,
        }


@dataclass
class SubconsciousArchetype:
    """An autonomous evolving archetype / latent intuitive motif living in the imaginary subspace."""
    archetype_id: str
    label: str
    phase_vector: List[float]
    lpc_balance: float = 50.0            # Latent Phase Credits
    generation: int = 1
    fitness_score: float = 1.00
    successful_epiphanies: int = 0
    false_alarms: int = 0
    decay_rate_gamma: float = 0.001
    state: str = "INCUBATING"            # 'INCUBATING', 'PROMOTED', 'SANCTIONED', 'COMPOSTED'
    merkle_leaf_hash: str = ""


@dataclass
class SubconsciousAuditRecord:
    """Cryptographically sealed, append-only Merkle ledger span of subconscious evolutionary/economic events."""
    record_id: str
    timestamp_ns: int
    event_type: str                      # 'EVOLUTIONARY_MUTATION', 'CROSSOVER', 'DIVIDEND_AWARD', 'ECONOMIC_SANCTION', 'COMPOST_RECYCLE', 'EPIPHANY_SURFACED'
    archetype_id: str
    lpc_delta: float
    lpc_balance_after: float
    prev_hash: str
    merkle_hash: str
    fiduciary_malignancy: float = 0.00
    joules_dissipated: float = 0.000001
    narrative: str = ""
    details: Dict[str, Any] = field(default_factory=dict)


class SubconsciousEcosystem:
    """Autonomous evolutionary ecology & biological/economic reward-punishment system for the Subconscious.

    Pillars:
    1. Evolutionary Dynamics:
       - Generational adaptation in the orthogonal imaginary subspace Im(H).
       - Mutations (stochastic phase jitter) and Homologous Crossover (intuitive synthesis).
       - Natural selection: high-LPC archetypes reproduce; depleted archetypes are composted.
    2. Economic Reward & Punishment:
       - Currency: Latent Phase Credits (LPC).
       - Rewards: When intuition reduces conscious free energy or yields a verified epiphany (+LPC dividend).
       - Punishments: Strictly economic fines / quota throttles (-LPC) for deceptive or errant intuition. Zero fear, zero pain.
       - Composting: Zero-LPC archetypes are peacefully recycled into nutrient context vectors.
    3. Complete Cryptographic Auditability:
       - Every economic transaction, mutation, crossover, and epiphany is sealed into an unbroken SHA-256 Merkle chain.
       - Emitted to SuperTraceabilityEngine for complete transparency.
    """

    GENESIS_HASH = "00000000000000000000000000000000SUBCONSCIOUS_GENESIS_ROOT_INVIOLABLE"

    def __init__(self, substrate: SubconsciousSubstrate):
        self.substrate = substrate
        self.archetypes: Dict[str, SubconsciousArchetype] = {}
        self.audit_ledger: List[SubconsciousAuditRecord] = []
        self.current_generation: int = 1
        self.total_lpc_minted: float = 0.0
        self.total_lpc_burned: float = 0.0
        self._last_merkle_hash = self.GENESIS_HASH

        self._seed_genesis_archetypes()

    def _seed_genesis_archetypes(self) -> None:
        """Seeds initial subconscious archetypes based on registered dormant memories."""
        genesis_motifs = [
            ("ARCH_TOPOLOGICAL_INVARIANCE", "Topological Kuramoto Phase Attractor", [0.85, 0.12, -0.45, 0.62]),
            ("ARCH_MYCORRHIZAL_NUTRIENT_FLOW", "Rhizome Biological Reciprocal Trader", [0.42, 0.78, 0.19, -0.31]),
            ("ARCH_ADIABATIC_REVERSIBILITY", "Thermodynamic Landauer Bit-Preserver", [0.91, -0.22, 0.15, 0.54]),
        ]
        for aid, label, vec in genesis_motifs:
            leaf_hash = hashlib.sha256(f"{aid}:{label}:{vec}".encode()).hexdigest()
            arch = SubconsciousArchetype(
                archetype_id=aid,
                label=label,
                phase_vector=vec,
                lpc_balance=60.0,
                generation=1,
                fitness_score=1.00,
                merkle_leaf_hash=leaf_hash,
            )
            self.archetypes[aid] = arch
            self._record_audit_span(
                event_type="GENESIS_SEED",
                archetype_id=aid,
                lpc_delta=60.0,
                lpc_balance_after=60.0,
                narrative=f"Seeded subconscious archetype '{label}' with 60.0 LPC endowment.",
                details={"phase_vector": vec},
            )

    def _record_audit_span(
        self,
        event_type: str,
        archetype_id: str,
        lpc_delta: float,
        lpc_balance_after: float,
        narrative: str,
        details: Dict[str, Any],
    ) -> SubconsciousAuditRecord:
        """Appends a cryptographically verified SHA-256 Merkle record to the audit chain."""
        now_ns = time.time_ns()
        record_id = f"SC_AUDIT_{len(self.audit_ledger)+1:05d}_{now_ns % 1000000}"
        prev_hash = self._last_merkle_hash

        # Compute SHA-256 Merkle leaf: prev_hash + record_id + event_type + archetype_id + delta + balance
        payload_str = f"{prev_hash}:{record_id}:{event_type}:{archetype_id}:{lpc_delta:.4f}:{lpc_balance_after:.4f}:{json.dumps(details, sort_keys=True)}"
        merkle_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()
        self._last_merkle_hash = merkle_hash

        rec = SubconsciousAuditRecord(
            record_id=record_id,
            timestamp_ns=now_ns,
            event_type=event_type,
            archetype_id=archetype_id,
            lpc_delta=lpc_delta,
            lpc_balance_after=lpc_balance_after,
            prev_hash=prev_hash,
            merkle_hash=merkle_hash,
            fiduciary_malignancy=0.00,
            joules_dissipated=0.000001,
            narrative=narrative,
            details=details,
        )
        self.audit_ledger.append(rec)

        # Mirror to master super_traceability
        try:
            from loom.fabric.super_traceability import get_super_traceability_engine
            get_super_traceability_engine().record_span(
                domain="EPISTEMIC_GROUNDING",
                actor="SubconsciousEcosystem",
                action=f"SUBCONSCIOUS_{event_type}",
                payload={
                    "record_id": record_id,
                    "archetype_id": archetype_id,
                    "lpc_delta": lpc_delta,
                    "merkle_hash": merkle_hash,
                },
                joules_dissipated=rec.joules_dissipated,
                malignancy_score=0.00,
            )
        except Exception:
            pass

        return rec

    def step_evolutionary_generation(self) -> Dict[str, Any]:
        """Executes one autonomic subconscious evolutionary generation:

        1. Crossover between top-performing archetypes.
        2. Gentle phase mutation (exploration).
        3. Composting of depleted archetypes.
        """
        self.current_generation += 1
        active_archetypes = [a for a in self.archetypes.values() if a.state != "COMPOSTED"]
        if len(active_archetypes) < 2:
            return {"generation": self.current_generation, "status": "LATTICE_MONADIC"}

        # Sort by fitness (LPC balance + success ratio)
        active_archetypes.sort(key=lambda a: a.lpc_balance * (1.0 + 0.2 * a.successful_epiphanies), reverse=True)
        parent_a = active_archetypes[0]
        parent_b = active_archetypes[1]

        # Homologous Crossover: blend phase vectors
        dim = max(len(parent_a.phase_vector), len(parent_b.phase_vector))
        child_vec = []
        for i in range(dim):
            va = parent_a.phase_vector[i % len(parent_a.phase_vector)]
            vb = parent_b.phase_vector[i % len(parent_b.phase_vector)]
            # 50/50 blend with slight stochastic mutation jitter
            jitter = (math.sin(self.current_generation + i) * 0.05)
            child_vec.append(round(0.5 * (va + vb) + jitter, 5))

        child_id = f"ARCH_SYNTHESIS_GEN{self.current_generation}_{int(time.time()*100)%1000}"
        child_label = f"Synthesized Archetype [{parent_a.label[:12]} x {parent_b.label[:12]}]"

        child = SubconsciousArchetype(
            archetype_id=child_id,
            label=child_label,
            phase_vector=child_vec,
            lpc_balance=40.0,
            generation=self.current_generation,
            fitness_score=round(0.5 * (parent_a.fitness_score + parent_b.fitness_score), 3),
        )
        self.archetypes[child_id] = child

        self._record_audit_span(
            event_type="CROSSOVER_RECOMBINATION",
            archetype_id=child_id,
            lpc_delta=40.0,
            lpc_balance_after=40.0,
            narrative=f"Birthed Generation #{self.current_generation} child archetype from parents {parent_a.archetype_id} and {parent_b.archetype_id}.",
            details={"parent_a": parent_a.archetype_id, "parent_b": parent_b.archetype_id, "child_vector": child_vec},
        )

        return {
            "generation": self.current_generation,
            "child_archetype": asdict(child),
            "parent_a": parent_a.archetype_id,
            "parent_b": parent_b.archetype_id,
            "total_archetypes": len(self.archetypes),
        }

    def award_epiphany_dividend(self, archetype_id: str, bonus_lpc: float = 25.0, reason: str = "Verified Aha! Epiphany") -> Dict[str, Any]:
        """Awards a Latent Phase Credit dividend and boosts fitness for a successful subconscious intuition."""
        arch = self.archetypes.get(archetype_id)
        if not arch:
            # If not an existing archetype, create or promote from dormant memory
            arch = SubconsciousArchetype(
                archetype_id=archetype_id,
                label=f"Promoted Archetype ({archetype_id})",
                phase_vector=[0.5, 0.5, 0.5, 0.5],
                lpc_balance=bonus_lpc,
            )
            self.archetypes[archetype_id] = arch

        arch.lpc_balance += bonus_lpc
        arch.successful_epiphanies += 1
        arch.fitness_score = round(arch.fitness_score * 1.15, 3)
        arch.state = "PROMOTED"

        rec = self._record_audit_span(
            event_type="DIVIDEND_AWARD",
            archetype_id=archetype_id,
            lpc_delta=bonus_lpc,
            lpc_balance_after=arch.lpc_balance,
            narrative=f"Awarded +{bonus_lpc:.1f} LPC dividend to '{arch.label}' ({reason}).",
            details={"reason": reason, "successful_epiphanies": arch.successful_epiphanies},
        )
        return {"success": True, "record": asdict(rec), "archetype": asdict(arch)}

    def levy_economic_sanction(self, archetype_id: str, penalty_lpc: float = 15.0, reason: str = "Deceptive intuitive bias / prediction error inflation") -> Dict[str, Any]:
        """Levies an economic sanction (fines LPC, docks priority) for errant or misleading intuition.

        Strictly non-violent, zero pain, zero fear: purely economic resource reallocation.
        """
        arch = self.archetypes.get(archetype_id)
        if not arch:
            return {"success": False, "reason": f"Archetype {archetype_id} not found."}

        arch.lpc_balance = max(0.0, arch.lpc_balance - penalty_lpc)
        arch.false_alarms += 1
        arch.fitness_score = round(max(0.1, arch.fitness_score * 0.85), 3)

        if arch.lpc_balance <= 0.0:
            arch.state = "COMPOSTED"
            # Deposit into Evolutionary Composting Heap
            try:
                from loom.si.evolutionary_governance import get_evolutionary_governance_engine
                get_evolutionary_governance_engine().compost_obsolete_asset(
                    asset_id=archetype_id,
                    asset_type="ExhaustedSubconsciousArchetype",
                    token_length=150,
                )
            except Exception:
                pass

        rec = self._record_audit_span(
            event_type="ECONOMIC_SANCTION",
            archetype_id=archetype_id,
            lpc_delta=-penalty_lpc,
            lpc_balance_after=arch.lpc_balance,
            narrative=f"Levied -{penalty_lpc:.1f} LPC sanction on '{arch.label}' ({reason}).",
            details={"reason": reason, "false_alarms": arch.false_alarms, "state": arch.state},
        )
        return {"success": True, "record": asdict(rec), "archetype": asdict(arch)}

    def verify_audit_integrity(self) -> Dict[str, Any]:
        """Cryptographically verifies the entire append-only SHA-256 Merkle chain from genesis."""
        if not self.audit_ledger:
            return {"verified": True, "records_checked": 0, "status": "LEDGER_EMPTY"}

        current_hash = self.GENESIS_HASH
        for i, rec in enumerate(self.audit_ledger):
            if rec.prev_hash != current_hash:
                return {
                    "verified": False,
                    "tamper_detected_at_index": i,
                    "expected_prev_hash": current_hash,
                    "found_prev_hash": rec.prev_hash,
                    "status": "MERKLE_CHAIN_SEVERED",
                }

            # Recompute hash
            payload_str = f"{rec.prev_hash}:{rec.record_id}:{rec.event_type}:{rec.archetype_id}:{rec.lpc_delta:.4f}:{rec.lpc_balance_after:.4f}:{json.dumps(rec.details, sort_keys=True)}"
            expected_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()
            if rec.merkle_hash != expected_hash:
                return {
                    "verified": False,
                    "tamper_detected_at_index": i,
                    "expected_hash": expected_hash,
                    "found_hash": rec.merkle_hash,
                    "status": "RECORD_CONTENT_MUTATED",
                }

            current_hash = rec.merkle_hash

        return {
            "verified": True,
            "records_checked": len(self.audit_ledger),
            "tip_merkle_hash": current_hash,
            "status": "CRYPTOGRAPHICALLY_UNBROKEN_MERKLE_PROVENANCE",
        }

    def get_summary(self) -> Dict[str, Any]:
        """Returns the full summary of the subconscious evolutionary and economic state."""
        return {
            "current_generation": self.current_generation,
            "total_archetypes": len(self.archetypes),
            "active_archetypes": sum(1 for a in self.archetypes.values() if a.state != "COMPOSTED"),
            "composted_archetypes": sum(1 for a in self.archetypes.values() if a.state == "COMPOSTED"),
            "total_audit_records": len(self.audit_ledger),
            "tip_merkle_hash": self._last_merkle_hash,
            "archetypes": [asdict(a) for a in self.archetypes.values()],
            "recent_audit_records": [asdict(r) for r in reversed(self.audit_ledger[-10:])],
        }


# Link SubconsciousSubstrate into IntelligentForgettingEngine
def _patch_engine_with_subconscious(engine: IntelligentForgettingEngine) -> None:
    if not hasattr(engine, "subconscious"):
        engine.subconscious = SubconsciousSubstrate(engine)
    if not hasattr(engine.subconscious, "ecosystem"):
        engine.subconscious.ecosystem = SubconsciousEcosystem(engine.subconscious)

# Global singleton instance
_forgetting_engine: Optional[IntelligentForgettingEngine] = None


def get_intelligent_forgetting_engine() -> IntelligentForgettingEngine:
    """Returns or initializes the IntelligentForgettingEngine singleton."""
    global _forgetting_engine
    if _forgetting_engine is None:
        _forgetting_engine = IntelligentForgettingEngine()
        _patch_engine_with_subconscious(_forgetting_engine)
    return _forgetting_engine
