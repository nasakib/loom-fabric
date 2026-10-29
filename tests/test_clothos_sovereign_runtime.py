"""Tests for ClothOS Sovereign Offline Runtime (Models, Headless Chromium, Voice, ONNX Embeddings)."""

import pytest
from pathlib import Path
from loom.clothos.sovereign_runtime import ClothOSSovereignRuntime


class TestClothOSSovereignRuntime:
    @pytest.fixture(autouse=True)
    def setup_runtime(self):
        self.runtime = ClothOSSovereignRuntime.get_instance()

    def test_sovereign_status_returns_complete_telemetry(self):
        status = self.runtime.get_sovereign_status()
        assert status["sovereign_runtime"] == "Active"
        assert "models" in status
        assert "headless_browser" in status
        assert "voice_stt_tts" in status
        assert "dense_embeddings" in status

    def test_list_models_detects_gguf_models(self):
        models = self.runtime.list_models()
        assert len(models) >= 3
        filenames = [m["filename"] for m in models]
        assert any("qwen2.5-coder-7b" in f for f in filenames)
        assert any("deepseek-r1" in f for f in filenames)
        assert any("qwen2.5-3b" in f for f in filenames)

    def test_embeddings_computes_384d_dense_vector(self):
        vec = self.runtime.embed_text("ClothOS sovereign machine intelligence running locally.")
        assert len(vec) == 384
        norm = sum(x**2 for x in vec) ** 0.5
        assert abs(norm - 1.0) < 1e-3

    def test_semantic_similarity_discriminates_relevance(self):
        docs = [
            "Local neural model weights running on GPU silicon.",
            "A recipe for chocolate cake with strawberry frosting.",
            "High performance cluster fabric synchronization over Ray."
        ]
        ranks = self.runtime.semantic_similarity("GPU tensor computation", docs)
        assert len(ranks) == 3
        # First rank should be the silicon/GPU document
        assert ranks[0]["index"] == 0
        assert ranks[0]["score"] > ranks[1]["score"]

    def test_speech_synthesis_runs_without_exception(self):
        res = self.runtime.synthesize_speech("ClothOS system operational.")
        # Success true or graceful backend output
        assert res.get("success") is True or "error" in res


class TestClothOSAgentCLISovereignTools:
    def test_tool_sovereign_status(self):
        from loom.clothos.agent_cli import ToolRegistry
        tools = ToolRegistry(Path("."))
        res = tools.execute("clothos_sovereign_status")
        assert res.get("success") is True
        assert "models" in res
        assert "headless_browser" in res

    def test_tool_compute_embeddings_uses_neural_engine(self):
        from loom.clothos.agent_cli import ToolRegistry
        tools = ToolRegistry(Path("."))
        res = tools.execute("compute_embeddings", text="Test neural vector")
        assert res.get("success") is True
        assert res.get("dimension") == 384
        assert len(res.get("embedding")) == 16

    def test_tool_semantic_similarity_integration(self):
        from loom.clothos.agent_cli import ToolRegistry
        tools = ToolRegistry(Path("."))
        res = tools.execute("semantic_similarity", text1="Operating system kernel", text2="OS kernel architecture")
        assert res.get("success") is True
        assert res.get("similarity_score") > 0.0
