"""Tests for OSResearchHarvester and Continuous 24/7 Compute Orchestrator."""

import pytest
from pathlib import Path
from loom.clothos.research_harvester import OSResearchHarvester, research_harvester
from loom.clothos.continuous_24x7_orchestrator import ClothOSContinuousComputeManager


class TestOSResearchHarvester:
    @pytest.fixture(autouse=True)
    def setup_harvester(self):
        self.harvester = research_harvester

    def test_harvester_instantiation_and_paths(self):
        assert self.harvester is not None
        assert self.harvester.research_dir.exists()
        assert self.harvester.findings_file.parent.exists()

    def test_github_os_repos_harvest_and_schema(self):
        # Query 1 item to test GitHub REST integration
        repos = self.harvester.harvest_github_os_repos(query="microkernel in:name stars:>500", max_results=2)
        assert isinstance(repos, list)
        if repos:
            item = repos[0]
            assert "source" in item
            assert item["source"] == "GitHub Repository"
            assert "url" in item
            assert item["url"].startswith("http")
            assert "category" in item
            assert "date_cited" in item
            assert item["relevance_score"] > 0.0

    def test_hackernews_systems_harvest(self):
        stories = self.harvester.harvest_hackernews_systems(limit=2)
        assert isinstance(stories, list)
        if stories:
            story = stories[0]
            assert "source" in story
            assert "url" in story
            assert "date_cited" in story

    def test_synthesize_clothos_proposals_includes_citations(self):
        proposals = self.harvester.synthesize_clothos_proposals(limit=2)
        assert isinstance(proposals, list)
        assert len(proposals) > 0
        for p in proposals:
            assert "claim" in p
            assert "category" in p
            assert "provenance_url" in p
            assert "citation" in p
            assert len(p["citation"]) > 0

    def test_markdown_documentation_is_generated_and_cited(self):
        md_file = self.harvester.summary_md_file
        assert md_file.exists()
        content = md_file.read_text(encoding="utf-8")
        assert "# ClothOS Operating System Research & Citations Library" in content
        assert "Curated Research Citations" in content
        assert "Citation Link" in content


class TestClothOSContinuousComputeManager:
    def test_manager_instantiation_on_evolution_branch(self):
        mgr = ClothOSContinuousComputeManager(cycle_interval_s=0.1)
        assert mgr.unified_engine is not None
        assert mgr.research_harvester is not None
        assert mgr.self_evolution is not None

    def test_manager_single_cycle_executes_safely(self, monkeypatch):
        mgr = ClothOSContinuousComputeManager(cycle_interval_s=0.01)
        # Fast path test: mock heavy external network calls in test
        monkeypatch.setattr(mgr.research_harvester, "harvest_github_os_repos", lambda *a, **kw: [])
        monkeypatch.setattr(mgr.research_harvester, "harvest_hackernews_systems", lambda *a, **kw: [])
        monkeypatch.setattr(mgr.unified_engine, "step_phase1_drain_tasks", lambda max_tasks=1: 0)

        mgr.run_forever(max_cycles=1)
        assert mgr.total_cycles == 1
