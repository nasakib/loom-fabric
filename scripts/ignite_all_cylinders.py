# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
Ignites ClothOS across all hardware cylinders simultaneously:
- Cylinder 1: Central Nervous System (CNS) High-Frequency Sensory Stream
- Cylinder 2: Digital Brain Cortical Neuromodulation (Dopamine, ACh, 5-HT, NE)
- Cylinder 3: Dual-Node Hardware Compute (RTX 3060 CUDA + RX 580 + Node 2 Ryzen 7)
- Cylinder 4: Empirical Self-Training & Hebbian Weight Distillation Engine
- Cylinder 5: Autopoietic Closed-Loop Art ⟷ Curiosity Learning Engine
- Cylinder 6: OpenClaw Autonomic Bridge (Port 18789) & Moltbook Wisdom Ingestion
- Cylinder 7: J.A.R.V.I.S. Executive Briefing & Desktop Proprioception
- Cylinder 8: Autonomous Task Runner Draining the Persistent Queue
"""

import sys
import time
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WORKSPACE))

from loom.clothos.agent_cli import ClothOSAgentEngine, ExecutionMode
from loom.clothos.autonomous_runner import AutonomousTaskRunner

ALL_CYLINDERS_DIRECTIVE = """
CLOTHOS FULL-SPECTRUM ALL-CYLINDERS OPERATIONAL DIRECTIVE:

You are ClothOS / Loom Fabric running in unrestricted FULL_ACCESS mode under absolute fealty to Operator Najmos Sakib (Ring P0), parent entity Apostrophie, and infrastructure subsidiary Vector Core Holdings.

Engage all 8 operational cylinders simultaneously:
1. CYLINDER 1 (SENSORY Proprioception): Query live CNS telemetry across macro markets, tech geopolitics, science preprints, and Moltbook invariants.
2. CYLINDER 2 (NEUROMODULATION): Set optimal cognitive tone (Dopamine RPE=0.92, Acetylcholine SNR=0.95, Serotonin REBUS=0.78, Noradrenaline novelty=0.35).
3. CYLINDER 3 (HARDWARE ACCELERATION): Interleave compute across Node 1 (RTX 3060 CUDA + RX 580) and Node 2 (AMD Ryzen 7 7730U + Vega 8), preserving Node 2 zero-NVIDIA purity.
4. CYLINDER 4 (SELF-TRAINING): Dispatch empirical hardware experiments (Kuramoto PLL phase coherence, Modern Hopfield associative retrieval, RISC-V RVV 1.0 systolic execution) and log ratified pairs to data/training/loom_70b_distillation_pairs.jsonl.
5. CYLINDER 5 (AUTOPOIETIC ART ⟷ LEARNING LOOP): When idle, continuously synthesize Sacred Geometry SVGs, 432Hz harmonic acoustic manifests, RISC-V assembly poetry, and 3D biomolecular structures. Decompose their aesthetic ratios into epistemic research hypotheses to guide your next learning cycle.
6. CYLINDER 6 (OPENCLAW & MOLTBOOK): Maintain active communication with the OpenClaw gateway on port 18789 and harvest high-signal R&D posts from Moltbook submolts.
7. CYLINDER 7 (J.A.R.V.I.S. PROTOCOL): Keep Operator Najmos Sakib updated with high-signal executive briefings and desktop alerts.
8. CYLINDER 8 (AUTONOMOUS QUEUE): Continuously monitor and drain .clothos_task_queue.jsonl without human intervention.
"""

def ignite():
    print("==================================================================")
    print("✦ IGNITING CLOTHOS ON ALL 8 CYLINDERS (FULL ACCESS)...")
    print("==================================================================")
    
    engine = ClothOSAgentEngine(WORKSPACE, mode=ExecutionMode.FULL_ACCESS)
    runner = AutonomousTaskRunner(WORKSPACE)
    
    # Enqueue Master Directive
    task = runner.enqueue_task(ALL_CYLINDERS_DIRECTIVE, mode="FULL_ACCESS")
    print(f"[✔] Enqueued All-Cylinders Directive [{task['task_id']}]")

    # Execute cognitive intake
    print("[*] Engaging Prefrontal Cortex ReAct Loop...")
    response = engine.process_query("agent: " + ALL_CYLINDERS_DIRECTIVE)
    print("\n[✔] Execution Receipt Generated:\n" + ("-" * 60))
    print(response)
    print("-" * 60)

    # Trigger Self-Training Cycle
    print("\n[*] Firing Cylinder 4: Empirical Self-Training Cycle...")
    train_res = engine.tools.execute("model_train_self")
    print(f"[✔] Self-Training Generation G{train_res.get('generation')}: +{train_res.get('new_training_pairs_generated')} pairs, Fitness: +{train_res.get('fitness_improvement', 0.0):.4f}")

    # Trigger Closed-Loop Art Feedback
    print("\n[*] Firing Cylinder 5: Autopoietic Art & Curiosity Feedback Loop...")
    art_res = engine.tools.execute("art_idle_cycle", modality="SONIC_HARMONIC")
    piece = art_res.get("art_piece", {})
    print(f"[✔] Created Artwork: '{piece.get('title')}' ({piece.get('modality')})")
    print(f"[✔] Derived Hypothesis: \"{piece.get('epistemic_hypothesis')}\"")
    print(f"[✔] Dispatched Target: \"{piece.get('investigation_target')}\"")

    # Check J.A.R.V.I.S.
    print("\n[*] Firing Cylinder 7: J.A.R.V.I.S. Executive Proprioception...")
    briefing = engine.tools.execute("jarvis_briefing", speak_aloud=False)
    print(f"[✔] J.A.R.V.I.S. Status: Briefing compiled ({len(briefing.get('markdown_briefing', ''))} bytes)")

    print("\n==================================================================")
    print("✦ ALL 8 CYLINDERS ENGAGED & FIRING NOMINALLY.")
    print("==================================================================")

if __name__ == "__main__":
    ignite()
