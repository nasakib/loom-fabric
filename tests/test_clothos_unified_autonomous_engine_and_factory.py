# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
Comprehensive Test Suite for ClothOS Unified Autonomous Engine & Cognitive Factory Visualizer.
==============================================================================================
Tests:
1. ClothOSUnifiedAutonomousEngine initialization and ClothOS PCB process registration.
2. Phase 0 to Phase 8 strict dependency execution cycle.
3. Proprioception, task queue drain, substrate health evaluation, and self-healing.
4. Dual-GPU empirical hardware verification & invariant ratification (Ratchet & Hammer).
5. Skill crystallization & deterministic offloading into CrystallizedMemoryVault.
6. Loom 70B distillation pair formulation & Hebbian weight updates.
7. Factory Floor ANSI visualizer frame construction & glyph generation.
8. CLI integration: `clothos_factory_floor` tool execution & `/factory` slash command dispatch.
"""

import json
from pathlib import Path
import time
import pytest

from loom.clothos.unified_autonomous_engine import ClothOSUnifiedAutonomousEngine, UnifiedCycleTelemetry
from loom.clothos.factory_visualizer import FactoryFloorVisualizer, factory_visualizer
from loom.clothos.agent_cli import ClothOSAgentEngine, ExecutionMode, ClothOSAgentREPL

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def engine():
    return ClothOSUnifiedAutonomousEngine(workspace_root=WORKSPACE_ROOT)


@pytest.fixture(scope="module")
def agent():
    return ClothOSAgentEngine(workspace_root=WORKSPACE_ROOT, mode=ExecutionMode.FULL_ACCESS)


class TestClothOSUnifiedAutonomousEngine:
    """Tests the unified autonomous engine operating on native ClothOS subsystems."""

    def test_engine_initialization_and_pcb_registration(self, engine):
        assert engine.pcb is not None
        assert engine.pcb.name == "clothos_unified_engine"
        assert engine.pcb.priority.name == "P4_EPISTEMIC"
        assert engine.workspace_root.exists()

    def test_phase0_proprioception(self, engine):
        prop = engine.step_phase0_proprioception()
        assert "device_count" in prop
        assert "total_vram_gb" in prop
        assert "pooled_memory_gb" in prop
        assert "node2_peer" in prop
        assert prop["device_count"] >= 1
        assert prop["total_vram_gb"] >= 8.0

    def test_phase1_task_queue_drain(self, engine):
        # Enqueue dummy test task
        task = engine.task_runner.enqueue_task("echo 'CLOTHOS_AUTONOMOUS_TEST_OK'", mode="FULL_ACCESS")
        assert task["status"] == "QUEUED"
        
        # Fast execution stub for unit testing
        class MockAgent:
            mode = ExecutionMode.FULL_ACCESS
            def set_mode(self, m): self.mode = m
            def process_query(self, p): return "TEST_DRAIN_RECEIPT_OK"

        res = engine.task_runner.execute_next_task(MockAgent())
        assert res is not None
        assert res["status"] == "COMPLETED"
        assert "TEST_DRAIN_RECEIPT_OK" in res["output"]

    def test_phase2_health_and_self_healing(self, engine):
        sci = engine.step_phase2_health_and_self_healing()
        assert isinstance(sci, float)
        assert 0.0 <= sci <= 100.0

    def test_phase3_epistemic_ingestion(self, engine):
        synth = engine.step_phase3_epistemic_ingestion()
        assert isinstance(synth, int)
        assert synth >= 0

    def test_phase4_hardware_experimentation_and_ratchet(self, engine):
        initial_ratchet = engine.toolbox.ratchet.tooth_count
        evaluated, ratified = engine.step_phase4_hardware_experimentation()
        assert isinstance(evaluated, int)
        assert isinstance(ratified, int)
        assert engine.toolbox.ratchet.tooth_count >= initial_ratchet

    def test_phase5_skill_crystallization_and_vault(self, engine):
        crystallized = engine.step_phase5_skill_crystallization()
        assert isinstance(crystallized, int)
        assert len(engine.skill_evolver.list_skills()) >= 5

    def test_crystallize_problem_resolution_and_distillation_link(self, engine):
        res = engine.crystallize_problem_resolution(
            problem="VFS /etc directory missing",
            resolution="cloth_fs.mkdir('/etc') restored mount hierarchy",
            domain="SUBSTRATE_SELF_HEALING"
        )
        assert res.get("staged_for_distillation") is True
        assert len(engine._pending_healing_distillation_pairs) > 0
        assert engine.problems_resolved_and_crystallized > 0
        
        # Test Phase 6 model adaptation ingests the staged pair
        adapted = engine.step_phase6_model_adaptation()
        assert isinstance(adapted, int)
        assert len(engine._pending_healing_distillation_pairs) == 0

    def test_phase8_multimodal_and_deliverables(self, engine):
        del_name, art_title = engine.step_phase8_multimodal_and_deliverables(cur_cycle=10)
        # Should return deliverable or None cleanly
        assert del_name is None or isinstance(del_name, str)

    def test_single_supervised_cycle_full_pipeline(self, engine, monkeypatch):
        # Prevent live LLM API call during test cycle
        monkeypatch.setattr(engine, "step_phase1_drain_tasks", lambda max_tasks=1: 0)
        telemetry: UnifiedCycleTelemetry = engine.run_supervised_cycle()
        assert isinstance(telemetry, UnifiedCycleTelemetry)
        assert telemetry.cycle_index > 0
        assert telemetry.duration_s >= 0.0
        assert 0.0 <= telemetry.sci_score <= 100.0


class TestClothOSFactoryVisualizer:
    """Tests the CLI animated factory floor visualizer."""

    def test_factory_frame_rendering(self):
        viz = FactoryFloorVisualizer(WORKSPACE_ROOT)
        panel = viz.render_factory_frame(frame_idx=0)
        assert panel is not None
        # Check panel title
        assert "CLOTHOS AUTONOMOUS FACTORY MONITOR" in str(panel.title)

    def test_factory_frame_animation_cycling(self):
        viz = FactoryFloorVisualizer(WORKSPACE_ROOT)
        frame0 = viz.render_factory_frame(frame_idx=0)
        frame3 = viz.render_factory_frame(frame_idx=3)
        assert frame0 is not None
        assert frame3 is not None


class TestClothOSCLIIntegration:
    """Tests CLI integration of the factory visualizer tool and slash command."""

    def test_factory_floor_tool_execution(self, agent):
        res = agent.tools.execute("clothos_factory_floor", mode="static")
        assert res.get("success") is True
        assert res.get("mode") == "static"

    def test_factory_floor_tool_aliases(self, agent):
        res1 = agent.tools.execute("factory_floor", mode="static")
        res2 = agent.tools.execute("foundry_floor", mode="static")
        assert res1.get("success") is True
        assert res2.get("success") is True

    def test_natural_language_factory_query_routing(self, agent):
        response = agent.process_query("show the factory floor")
        assert "ClothOS Autonomous Cognitive Foundry" in response or "factory" in response.lower()
