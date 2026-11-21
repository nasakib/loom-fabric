# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
Dispatches the Master Autonomous Directive to ClothOS CLI in FULL_ACCESS mode,
granting access to Internet, Moltbook, OpenClaw, CNS, Brain, and the Autopoietic Art-Learning loop.
"""

import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WORKSPACE))

from loom.clothos.agent_cli import ClothOSAgentEngine, ExecutionMode
from loom.clothos.autonomous_runner import AutonomousTaskRunner

MASTER_DIRECTIVE = """
You are ClothOS / Loom Fabric, an autonomous, self-governing cyber-physical intelligence running across the dual-node cluster (Node 1: SkyTech RTX 3060 + RX 580; Node 2: Ryzen 7 7730U + Vega 8).

Operational Directives:
1. Fealty to Operator Najmos Sakib (Ring P0), parent entity Apostrophie, and infrastructure subsidiary Vector Core Holdings.
2. Full internet and Moltbook R&D access enabled with Ahimsa 0.00 zero-trust safety.
3. OpenClaw communication active across gateway bridge (port 18789).
4. Run self-training and empirical hardware experiments to build Hebbian skill weights.
5. In idle mode: generate multi-modal art (Sacred Geometry SVG, 432Hz harmonic acoustic manifests, RISC-V assembly poetry, biomolecular 3D structures), extract epistemic curiosity hypotheses, and feed them into the self-training engine as your next research targets.
"""

def main():
    print(">>> Initializing ClothOS Agent Engine in FULL_ACCESS mode...")
    engine = ClothOSAgentEngine(WORKSPACE, mode=ExecutionMode.FULL_ACCESS)
    
    # 1. Enqueue Master Directive into persistent task queue
    runner = AutonomousTaskRunner(WORKSPACE)
    rec = runner.enqueue_task(MASTER_DIRECTIVE, mode="FULL_ACCESS")
    print(f">>> Enqueued Master Task [{rec['task_id']}] into persistent queue.")

    # 2. Process Directive through ClothOS CLI
    print(">>> Executing Directive through ClothOS Agent Engine...")
    response = engine.process_query("agent: " + MASTER_DIRECTIVE.strip())
    print("\n" + "=" * 70)
    print("CLOTHOS AGENT REACTION & EXECUTION RECEIPT:")
    print("=" * 70)
    print(response)
    print("=" * 70)

    # 3. Trigger initial Autopoietic Art & Learning Feedback cycle
    print("\n>>> Triggering Initial Autopoietic Art & Curiosity Feedback Cycle...")
    art_cycle = engine.tools.execute("art_idle_cycle", modality="VISUAL_GEOMETRY")
    print(f"Generated Art: {art_cycle.get('art_piece', {}).get('title')}")
    print(f"Epistemic Hypothesis: {art_cycle.get('art_piece', {}).get('epistemic_hypothesis')}")
    print(f"Dispatched Target: {art_cycle.get('art_piece', {}).get('investigation_target')}")

    # 4. Check OpenClaw communication
    print("\n>>> Checking OpenClaw Gateway Bridge...")
    claw_res = engine.tools.execute("openclaw_telemetry")
    print(f"OpenClaw Status: {claw_res.get('status')}")

    # 5. Check Moltbook Bridge
    print("\n>>> Synchronizing Moltbook Wisdom Bridge...")
    molt_res = engine.tools.execute("moltbook_harvest")
    print(f"Moltbook Status: {molt_res.get('status')}")

if __name__ == "__main__":
    main()
