"""
Aha! Autonomous System Evolution Engine (`loom/fabric/aha_engine.py`).

Detects breakthroughs and boundary insights from empirical trials, synthesizes
candidate system upgrades, enforces 4-gate verification, and ratchets improvements
into the running OS configuration.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Tuple

from loom.fabric.evolution_verifier import EvolutionVerifier, EvolutionVerificationReport
from loom.fabric.hypothesis_store import HypothesisStore
from loom.fabric.system_config import SystemConfig, system_config
from loom.tools.toolbox import toolbox

logger = logging.getLogger("loom.fabric.aha_engine")


class AhaEngine:
    """Detects, verifies, and applies autonomous system improvements."""

    def __init__(
        self,
        store: Optional[HypothesisStore] = None,
        config: Optional[SystemConfig] = None,
        verifier: Optional[EvolutionVerifier] = None,
        workspace_root: Optional[Path] = None,
    ):
        self.workspace_root = workspace_root or Path(__file__).resolve().parents[2]
        self.store = store or HypothesisStore()
        self.config = config or system_config
        self.verifier = verifier or EvolutionVerifier(workspace_root=self.workspace_root)
        self.ledger_file = self.workspace_root / ".loom_evolution_ledger.json"
        self._last_evaluated_id: int = 0

    def scan_for_aha_opportunities(self) -> List[Dict[str, Any]]:
        """
        Scans recent confirmed and refuted findings to discover potential
        system optimizations (Aha! moments).
        """
        findings = self.store.get_findings_for_deliverable(limit=50)
        proposals: List[Dict[str, Any]] = []

        active_params = self.config.snapshot()

        for f in findings:
            submolt = f.get("submolt", "")
            verdict = f.get("verdict", "")
            measurements = f.get("measurements", {})
            claim = f.get("claim", "")

            # -------------------------------------------------------------
            # Opportunity 1: Active Inference Kuramoto Relaxation Time
            # -------------------------------------------------------------
            if submolt == "m/active-inference":
                if verdict == "refuted" and "250" in claim and ("r >= 0.85" in claim or "order parameter" in claim):
                    # Refuted transient claim proves 250 steps is too short!
                    current_steps = active_params.get("kuramoto_min_relaxation_steps", 250)
                    if current_steps < 350:
                        proposals.append({
                            "proposal_id": f"AHA_RELAX_{f['id']}_{int(time.time())}",
                            "parameter_name": "kuramoto_min_relaxation_steps",
                            "old_value": current_steps,
                            "new_value": 350,
                            "submolt": submolt,
                            "rationale": "Empirical refutation of fast transient synchronization proves N>=2048 requires >=350 steps.",
                            "improvement_pct": 40.0,
                            "context": measurements,
                        })
                elif verdict == "confirmed" and measurements.get("measured_coherence_r", 0.0) >= 0.85:
                    k_val = measurements.get("k_coupling")
                    if k_val and abs(k_val - active_params.get("kuramoto_consensus_k", 2.45)) > 0.05:
                        proposals.append({
                            "proposal_id": f"AHA_K_COUPLING_{f['id']}_{int(time.time())}",
                            "parameter_name": "kuramoto_consensus_k",
                            "old_value": active_params.get("kuramoto_consensus_k", 2.45),
                            "new_value": round(float(k_val), 2),
                            "submolt": submolt,
                            "rationale": f"Hardware sweep achieved solid phase lock (r={measurements.get('measured_coherence_r'):.3f}) at K={k_val}.",
                            "improvement_pct": 12.5,
                            "context": measurements,
                        })

            # -------------------------------------------------------------
            # Opportunity 2: Systems Engineering Hypersphere Orthogonality
            # -------------------------------------------------------------
            elif submolt == "m/systems-engineering":
                if verdict == "confirmed" and "mean_abs_cosine_sim" in measurements:
                    sim = measurements.get("mean_abs_cosine_sim", 0.0)
                    current_thresh = active_params.get("hypersphere_ortho_threshold", 0.035)
                    if 0.0 < sim < current_thresh:
                        new_thresh = round(sim * 1.5, 3)  # Tighten safety margin
                        if new_thresh < current_thresh:
                            proposals.append({
                                "proposal_id": f"AHA_ORTHO_{f['id']}_{int(time.time())}",
                                "parameter_name": "hypersphere_ortho_threshold",
                                "old_value": current_thresh,
                                "new_value": new_thresh,
                                "submolt": submolt,
                                "rationale": f"High-dim projection proved mean cosine sim {sim:.4f}, allowing tighter orthogonal routing bound.",
                                "improvement_pct": round((current_thresh - new_thresh) / current_thresh * 100, 1),
                                "context": measurements,
                            })

            # -------------------------------------------------------------
            # Opportunity 3: Distributed Compute GPU 1 Batch Scaling
            # -------------------------------------------------------------
            elif submolt == "m/distributed-compute":
                if verdict == "confirmed" and measurements.get("n_oscillators", 0) >= 4096:
                    dur = measurements.get("duration_s", 0.0)
                    current_min = active_params.get("rx580_min_batch_size", 2048)
                    if current_min < 4096 and dur < 0.06:
                        proposals.append({
                            "proposal_id": f"AHA_BATCH_{f['id']}_{int(time.time())}",
                            "parameter_name": "rx580_min_batch_size",
                            "old_value": current_min,
                            "new_value": 4096,
                            "submolt": submolt,
                            "rationale": "Ellesmere stream processors reach maximum ALU occupancy at N>=4096 while keeping latency < 60ms.",
                            "improvement_pct": 25.0,
                            "context": measurements,
                        })

            # -------------------------------------------------------------
            # Opportunity 4: Fourier Geometry Symplectic Energy Tolerance
            # -------------------------------------------------------------
            elif submolt == "m/fourier-geometry":
                if verdict == "confirmed" and "energy_drift_pct" in measurements:
                    drift = measurements.get("energy_drift_pct", 0.0)
                    current_tol = active_params.get("symplectic_max_drift_pct", 0.05)
                    if 0.0 < drift < 0.01 and current_tol > 0.02:
                        proposals.append({
                            "proposal_id": f"AHA_SYMPLECTIC_{f['id']}_{int(time.time())}",
                            "parameter_name": "symplectic_max_drift_pct",
                            "old_value": current_tol,
                            "new_value": 0.015,
                            "submolt": submolt,
                            "rationale": f"Empirical Hamiltonian drift measured at {drift:.4f}% (< 0.01%), permitting stricter conservation guarantee.",
                            "improvement_pct": 70.0,
                            "context": measurements,
                        })

        return proposals

    def process_and_ratify_opportunities(self) -> List[Dict[str, Any]]:
        """
        Discovers, rigorously verifies, and applies candidate optimizations.
        Returns a list of ratification results.
        """
        proposals = self.scan_for_aha_opportunities()
        ratified_results = []

        for p in proposals:
            logger.info(f"🔍 [Aha! Opportunity]: Evaluating {p['parameter_name']} ({p['old_value']} ➔ {p['new_value']})")

            # 1. RIGOROUS 4-GATE VERIFICATION
            report = self.verifier.verify_proposal(
                proposal_id=p["proposal_id"],
                parameter_name=p["parameter_name"],
                old_value=p["old_value"],
                new_value=p["new_value"],
                submolt=p["submolt"],
                rationale=p["rationale"],
                context=p.get("context", {}),
            )

            if report.overall_passed:
                # 2. RATIFY INTO SYSTEM CONFIG
                gen = self.config.update_params(
                    updates={p["parameter_name"]: p["new_value"]},
                    rationale=p["rationale"],
                )

                # 3. RATCHET & HAMMER RIVETING
                axiom_id = f"EVOLUTION_{p['parameter_name'].upper()}_GEN_{gen}"
                proof_text = f"Verified: {p['parameter_name']}={p['new_value']} ({p['rationale']})"
                try:
                    toolbox.ratchet.click(
                        axiom_id=axiom_id,
                        claim=proof_text,
                        proof_payload=json.dumps(report.to_dict()),
                        confidence=0.99,
                        node_origin="AhaEngine-4Gate-Verified",
                    )
                    toolbox.hammer.rivet(
                        identifier=f"RIVET_EVOLUTION_{gen}",
                        payload={"parameter": p["parameter_name"], "new_value": p["new_value"], "report": report.to_dict()},
                    )
                except Exception as e:
                    logger.debug(f"Toolbox ratchet/hammer click note: {e}")

                # 4. RECORD TO DATABASE & LEDGER
                db_id = self.store.record_system_evolution(
                    proposal_id=p["proposal_id"],
                    parameter_name=p["parameter_name"],
                    old_value=p["old_value"],
                    new_value=p["new_value"],
                    submolt=p["submolt"],
                    rationale=p["rationale"],
                    improvement_pct=p["improvement_pct"],
                    verification_hash=report.verification_hash,
                    verification_report=report.to_dict(),
                    status="ratified",
                )

                self._append_to_ledger({
                    "id": db_id,
                    "generation": gen,
                    "proposal_id": p["proposal_id"],
                    "parameter": p["parameter_name"],
                    "old_value": p["old_value"],
                    "new_value": p["new_value"],
                    "improvement_pct": p["improvement_pct"],
                    "rationale": p["rationale"],
                    "verification_hash": report.verification_hash,
                    "status": "RATIFIED",
                    "timestamp": time.time(),
                })

                logger.info(
                    f"✨ [Aha! Ratified]: Evolved {p['parameter_name']} to {p['new_value']} (Gen #{gen}) "
                    f"[+{p['improvement_pct']}%] — Hash: {report.verification_hash}"
                )
                ratified_results.append({
                    "status": "RATIFIED",
                    "parameter": p["parameter_name"],
                    "new_value": p["new_value"],
                    "generation": gen,
                    "improvement_pct": p["improvement_pct"],
                    "hash": report.verification_hash,
                    "critique": report.audit_critique,
                })
            else:
                logger.warning(
                    f"⛔ [Aha! Rejected]: Proposal {p['proposal_id']} failed {report.failed_gate}: "
                    f"{report.audit_critique}"
                )
                self._append_to_ledger({
                    "proposal_id": p["proposal_id"],
                    "parameter": p["parameter_name"],
                    "attempted_value": p["new_value"],
                    "failed_gate": report.failed_gate,
                    "reason": report.audit_critique,
                    "status": "REJECTED",
                    "timestamp": time.time(),
                })

        return ratified_results

    def _append_to_ledger(self, record: Dict[str, Any]) -> None:
        entries = []
        if self.ledger_file.exists():
            try:
                entries = json.loads(self.ledger_file.read_text(encoding="utf-8"))
            except Exception:
                entries = []
        entries.append(record)
        try:
            self.ledger_file.write_text(json.dumps(entries, indent=2), encoding="utf-8")
        except Exception as e:
            logger.debug(f"Failed to append to evolution ledger: {e}")
