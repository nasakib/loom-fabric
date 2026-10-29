"""Tests for babelForge and ClothOS Co-Reasoning & MCP Integration."""

import pytest
from pathlib import Path
from servers.babelforge_mcp.algorithms import (
    validate_graph_invariants,
    simulate_subgraph_execution,
    optimize_clothos_schedule,
)


class TestBabelForgeAlgorithms:
    def test_validate_graph_invariants_on_connected_dag(self):
        graph = {
            "nodes": [{"id": "n1"}, {"id": "n2"}, {"id": "n3"}, {"id": "n4"}],
            "edges": [
                {"source": "n1", "target": "n2", "weight": 1.0},
                {"source": "n2", "target": "n3", "weight": 1.0},
                {"source": "n3", "target": "n4", "weight": 1.0},
            ]
        }
        res = validate_graph_invariants(graph)
        assert res["valid"] is True
        assert res["node_count"] == 4
        assert res["edge_count"] == 3
        assert res["connected_components"] == 1
        assert res["betti_1_cycles"] == 0
        assert res["acyclic"] is True
        assert "ADJACENCY_SYMMETRY_PRESERVED" in res["invariants_satisfied"]

    def test_validate_graph_invariants_detects_cycles(self):
        # 3-node cycle
        graph = {
            "nodes": [{"id": "a"}, {"id": "b"}, {"id": "c"}],
            "edges": [
                {"source": "a", "target": "b", "weight": 1.0},
                {"source": "b", "target": "c", "weight": 1.0},
                {"source": "c", "target": "a", "weight": 1.0},
            ]
        }
        res = validate_graph_invariants(graph)
        assert res["valid"] is True
        assert res["betti_1_cycles"] == 1
        assert res["acyclic"] is False

    def test_simulate_subgraph_execution_kuramoto_phase_locking(self):
        node_cfg = {
            "nodes": [
                {"id": "w1", "omega": 1.0, "theta": 0.0},
                {"id": "w2", "omega": 1.05, "theta": 0.2},
                {"id": "w3", "omega": 0.95, "theta": 0.1},
                {"id": "w4", "omega": 1.0, "theta": 0.15},
            ],
            "coupling_k": 3.5,
            "steering_vector": [1.0, 0.0, 0.0, 1.0],  # normal operation + repair
        }
        sim = simulate_subgraph_execution("subgraph_test_1", node_cfg, timesteps=150)
        assert sim["subgraph_id"] == "subgraph_test_1"
        assert sim["nodes_simulated"] == 4
        assert len(sim["order_parameter_trajectory"]) > 0
        assert sim["final_phase_coherence"] >= 0.70
        assert sim["phase_locked"] is True
        assert sim["stable"] is True
        assert sim["landauer_joules_dissipated"] > 0.0

    def test_optimize_clothos_schedule_heterogeneous_balancing(self):
        task_graph = {
            "tasks": [
                {"id": "heavy_llm_inference", "vram_mb": 4096, "ops": 5e10},
                {"id": "opencl_stream_sweep", "vram_mb": 1500, "ops": 2e9},
                {"id": "ast_code_parsing", "vram_mb": 256, "ops": 5e7},
                {"id": "memory_compaction", "vram_mb": 128, "ops": 1e7},
            ]
        }
        sched = optimize_clothos_schedule(task_graph)
        assert sched["total_tasks"] == 4
        assert len(sched["placements"]) == 4
        assert sched["balanced"] is True
        
        # Verify node placement affinity
        node_map = {p["task_id"]: p["assigned_node"] for p in sched["placements"]}
        assert node_map["heavy_llm_inference"] == "node1_gpu0_cuda"
        assert node_map["opencl_stream_sweep"] == "node1_gpu1_opencl"
        assert node_map["ast_code_parsing"] == "node2_ryzen7_apu"


class TestBabelForgeSkillAndDocs:
    def test_skill_markdown_exists_and_has_valid_frontmatter(self):
        skill_path = Path(".agents/skills/babelforge-clothos/SKILL.md")
        assert skill_path.exists(), "Skill markdown does not exist"
        content = skill_path.read_text(encoding="utf-8")
        assert "name: babelforge-clothos" in content
        assert "description:" in content
        assert "Stage 1: Pre-check" in content
        assert "Stage 2: Mapping & Lowering" in content
        assert "Stage 3: Verification" in content

    def test_agents_markdown_exists_in_root(self):
        agents_path = Path("AGENTS.md")
        assert agents_path.exists(), "AGENTS.md missing in root"
        content = agents_path.read_text(encoding="utf-8")
        assert "Domain Ontology & System Mapping" in content
        assert "Mathematical Axioms & Strict Invariants" in content
        assert "Kuramoto Phase Dynamics" in content
