# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
Comprehensive Test Suite for ClothOS Chat-Based Prompt Developer & Metaprompting Studio.
========================================================================================
Tests:
1. Quality metrics calculation across clarity, constraints, modularity, economy, robustness.
2. Production XML prompt synthesis (<identity>, <operating_principles>, <constraints>, etc.).
3. Optimization of raw prompts with radiance score improvements.
4. Prompt template persistence, loading, and library listing.
5. Interactive chat session turn handling and conversational refinement.
6. Tool registration in ClothOS Agent CLI (`prompt_developer`, `prompt_dev`, `metaprompt`).
7. Natural language routing in `agent.process_query()`.
"""

from pathlib import Path
import pytest

from loom.clothos.prompt_developer import (
    PromptDeveloperEngine,
    PromptDeveloperChatSession,
    PromptTemplate,
    PromptQualityMetrics,
    prompt_developer_engine,
)
from loom.clothos.agent_cli import ClothOSAgentEngine, ExecutionMode

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def engine():
    return PromptDeveloperEngine(workspace_root=WORKSPACE_ROOT)


@pytest.fixture(scope="module")
def agent():
    return ClothOSAgentEngine(workspace_root=WORKSPACE_ROOT, mode=ExecutionMode.FULL_ACCESS)


class TestPromptDeveloperEngine:
    """Tests the core prompt synthesis, quality evaluation, and persistence engine."""

    def test_evaluate_quality_on_basic_prompt(self, engine):
        raw_prompt = "You are a Python assistant. Write code."
        metrics = engine.evaluate_quality(raw_prompt)
        assert isinstance(metrics, PromptQualityMetrics)
        assert 0.0 <= metrics.overall_radiance <= 100.0
        assert metrics.clarity_score > 0
        assert len(metrics.recommendations) > 0

    def test_develop_prompt_synthesizes_xml_structure(self, engine):
        goal = "Build a high-performance RISC-V RVV 1.0 systolic matrix multiplication kernel."
        template = engine.develop_prompt(
            goal=goal,
            role="RISC-V Systems Architect",
            domain="HARDWARE_COMPUTE",
            output_format="Executable Assembly with Invariant Proof",
        )
        assert isinstance(template, PromptTemplate)
        assert "<identity>" in template.system_prompt
        assert "<operating_principles>" in template.system_prompt
        assert "<cognitive_workflow>" in template.system_prompt
        assert "<constraints>" in template.system_prompt
        assert "<output_contract>" in template.system_prompt
        assert template.quality_metrics is not None
        assert template.quality_metrics.overall_radiance >= 75.0

    def test_optimize_prompt_improves_radiance(self, engine):
        raw = "help me write rust code for a web server"
        res = engine.optimize_prompt(raw)
        assert res["original_prompt"] == raw
        assert res["optimized_radiance"] >= res["original_radiance"]
        assert "<identity>" in res["optimized_prompt"]
        assert len(res["improvements"]) >= 0

    def test_save_and_load_prompt_persistence(self, engine):
        template = engine.develop_prompt(
            goal="Test Autonomous Persistence Prompt",
            role="Test Verifier",
            domain="TESTING",
        )
        saved_path = engine.save_prompt(template, "test_autonomous_prompt")
        assert saved_path.exists()
        assert saved_path.suffix == ".md"

        loaded = engine.load_prompt("test_autonomous_prompt")
        assert loaded is not None
        assert loaded.name == "test_autonomous_prompt"
        assert "<identity>" in loaded.system_prompt

        # Clean up
        if saved_path.exists():
            saved_path.unlink()

    def test_list_prompts_returns_metadata(self, engine):
        prompts = engine.list_prompts()
        assert isinstance(prompts, list)


class TestPromptDeveloperChatSession:
    """Tests the conversational chat-based prompt developer REPL."""

    def test_session_develops_prompt_on_first_turn(self, engine):
        session = PromptDeveloperChatSession(engine=engine)
        reply = session.handle_user_input("I need a prompt for reviewing pull requests for security vulnerabilities")
        assert session.current_template is not None
        assert "Prompt Developed" in reply
        assert session.current_template.quality_metrics.overall_radiance >= 70.0

    def test_session_conversational_refinement(self, engine):
        session = PromptDeveloperChatSession(engine=engine)
        session.handle_user_input("Create an automated API documentation generator")
        orig_radiance = session.current_template.quality_metrics.overall_radiance

        # Refine
        refine_reply = session.handle_user_input("Add strict JSON output format and negative boundary constraints")
        assert "Prompt refined" in refine_reply
        assert session.current_template.output_contract == "Strict JSON"

    def test_session_commands_score_and_list(self, engine):
        session = PromptDeveloperChatSession(engine=engine)
        session.handle_user_input("Write a unit test generator for pytest")

        score_reply = session.handle_user_input("/score")
        assert "Overall Radiance is" in score_reply

        list_reply = session.handle_user_input("/list")
        assert "ClothOS" in list_reply or "prompt" in list_reply.lower()

    def test_session_exit_command(self, engine):
        session = PromptDeveloperChatSession(engine=engine)
        exit_reply = session.handle_user_input("/exit")
        assert exit_reply == "EXIT_SESSION"


class TestClothOSAgentCLIPromptIntegration:
    """Tests the agent tool registry and natural language routing for prompt developer."""

    def test_prompt_developer_tool_develop(self, agent):
        res = agent.tools.execute("prompt_developer", action="develop", goal="Create a fast database migration helper")
        assert res.get("success") is True
        assert res.get("action") == "develop"
        assert "<identity>" in res.get("system_prompt", "")
        assert res.get("radiance_score") >= 70.0

    def test_prompt_developer_tool_aliases(self, agent):
        res1 = agent.tools.execute("prompt_dev", action="score", prompt_text="You are a helper. Do stuff.")
        res2 = agent.tools.execute("metaprompt", action="list")
        assert res1.get("success") is True
        assert res2.get("success") is True

    def test_natural_language_prompt_routing(self, agent):
        response = agent.process_query("develop a prompt for an autonomous security audit agent")
        assert "ClothOS Prompt Developer Synthesis" in response
        assert "<identity>" in response
        assert "Radiance Score" in response
