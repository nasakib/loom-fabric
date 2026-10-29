"""
Unit Test Suite for ClothOS Full Capability Integration:
- text_generation (Local/Sovereign LLM text generation)
- compute_embeddings & semantic_similarity
- variational_inference (Active Inference Free Energy)
- spectral_analysis (SVD & low-rank subspace projection)
- information_theory_metrics (Shannon entropy & KL divergence)
- software_genetics_evolve (Autonomous code evolution)
- truth_imagination (Fiction grounded in non-fiction)
- temporal_cognition (Prospective planning & foresight policies)
- biomolecular_analyze (Central dogma & genetic computation)
- image_generation & audio_synth (Visual & acoustic synthesis)
- launch_vulkan_dual_gpu (20GB Paired VRAM launcher)
- Slash commands and natural language query routing
"""

import math
import os
from pathlib import Path
import tempfile
import pytest

from loom.clothos.agent_cli import ClothOSAgentEngine, ClothOSAgentREPL, ExecutionMode


@pytest.fixture
def agent_engine():
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = ClothOSAgentEngine(workspace_root=Path(tmpdir), mode=ExecutionMode.FULL_ACCESS)
        yield engine


# ==============================================================================
# 1. Text Generation & Semantic Embedding Suite
# ==============================================================================

def test_text_generation_tool(agent_engine):
    res = agent_engine.tools.execute(
        "text_generation",
        prompt="Synthesize a principle of sovereign computing.",
        temperature=0.5,
        max_tokens=128,
    )
    assert res["success"] is True
    assert "generated_text" in res
    assert len(res["generated_text"]) > 0
    assert res["prompt_tokens"] > 0
    assert res["completion_tokens"] > 0
    assert res["total_tokens"] >= res["prompt_tokens"]
    assert res["latency_ms"] >= 0.0
    assert res["tokens_per_second"] >= 0.0
    assert "model" in res

    # Verify alias
    res_alias = agent_engine.tools.execute("generate_text", prompt="Hello world")
    assert res_alias["success"] is True


def test_compute_embeddings_and_similarity(agent_engine):
    # 1. Embeddings
    emb = agent_engine.tools.execute("compute_embeddings", text="Sovereign Heterogeneous Computing Fabric")
    assert emb["success"] is True
    assert emb["dimension"] == 384
    assert len(emb["embedding"]) == 16
    assert emb["embedding_norm"] == 1.0

    # 2. Semantic Similarity
    sim = agent_engine.tools.execute(
        "semantic_similarity",
        text1="Quantum harmonic oscillator in phase space",
        text2="Harmonic oscillator phase space trajectories",
    )
    assert sim["success"] is True
    assert 0.0 <= sim["similarity_score"] <= 1.0
    assert sim["lexical_overlap"] > 0.4


# ==============================================================================
# 2. Deep Probabilistic & Variational Inference Suite
# ==============================================================================

def test_variational_inference_tool(agent_engine):
    obs = [1.2, 0.8, 2.5]
    pred = [1.0, 1.0, 2.0]
    res = agent_engine.tools.execute(
        "variational_inference",
        observation=obs,
        predicted_obs=pred,
        mu_prior=[0.0, 0.0, 0.0],
    )
    assert res["success"] is True
    vfe = res["variational_free_energy"]
    assert "free_energy" in vfe
    assert "complexity_kl" in vfe
    assert "accuracy_inaccuracy" in vfe
    assert vfe["free_energy"] >= 0.0


def test_spectral_analysis_and_information_theory(agent_engine):
    # 1. Spectral Analysis
    matrix = [
        [3.0, 2.0],
        [2.0, 3.0],
    ]
    spec = agent_engine.tools.execute("spectral_analysis", matrix=matrix, rank=1)
    assert spec["success"] is True
    assert len(spec["singular_values"]) > 0
    assert spec["spectral_norm"] > 0.0

    # 2. Information Theory
    dist_p = [0.25, 0.25, 0.25, 0.25]
    dist_q = [0.5, 0.2, 0.2, 0.1]
    info = agent_engine.tools.execute("information_theory_metrics", distribution_p=dist_p, distribution_q=dist_q)
    assert info["success"] is True
    assert math.isclose(info["shannon_entropy_bits"], 2.0, rel_tol=1e-4)
    assert info["kl_divergence"] >= 0.0


# ==============================================================================
# 3. Software Genetics & Grounded Cognitive Imagination
# ==============================================================================

def test_software_genetics_evolve_tool(agent_engine):
    source = "def quick_add(a, b):\n    return a + b\n"
    res = agent_engine.tools.execute("software_genetics_evolve", source_code=source, generations=3)
    assert res["success"] is True
    assert "seed_genome_id" in res
    assert res["generation"] >= 1
    assert res["fitness_score"] > 0.0


def test_truth_imagination_and_temporal_cognition(agent_engine):
    # 1. Truth Imagination
    premise = "What if silicon computing operated as a biological mycorrhizal network?"
    imag = agent_engine.tools.execute(
        "truth_imagination",
        premise=premise,
        non_fiction_anchors=["Landauer Limit", "Shannon Information Capacity"],
    )
    assert imag["success"] is True
    assert "experiment_id" in imag
    assert len(imag["narrative_scenario"]) > 0
    assert imag["is_fiduciary_safe"] is True

    # 2. Temporal Cognition
    cog = agent_engine.tools.execute(
        "temporal_cognition",
        goal="Shard 32B model across dual-GPU VRAM with zero latency jitter",
        horizon_steps=3,
    )
    assert cog["success"] is True
    assert "plan_id" in cog
    assert len(cog["steps"]) >= 1


# ==============================================================================
# 4. Biomolecular & Multimodal Synthesis
# ==============================================================================

def test_biomolecular_analyze_tool(agent_engine):
    dna = "ATGCGATCGATCGATCGATCGATCGATC"
    res = agent_engine.tools.execute("biomolecular_analyze", sequence_or_query=dna)
    assert res["success"] is True
    assert res["status"] == "BIOMOL_ANALYZED"
    assert res["length"] == len(dna)
    assert 0.0 <= res["gc_content"] <= 1.0


def test_image_and_audio_synthesis_tools(agent_engine):
    # 1. Image / Vector SVG
    img = agent_engine.tools.execute(
        "image_generation",
        prompt="Sovereign Heterogeneous Computing Topology",
        output_path="deliverables/test_topology.svg",
    )
    assert img["success"] is True

    # 2. Audio Synthesis
    snd = agent_engine.tools.execute(
        "audio_synth",
        frequency_hz=432.0,
        duration_sec=0.2,
        waveform="sine",
        output_path="deliverables/test_432hz.wav",
    )
    assert snd["success"] is True
    assert snd["frequency_hz"] == 432.0
    assert snd["bytes_written"] > 0
    assert Path(snd["output_path"]).exists()


# ==============================================================================
# 5. Vulkan Dual-GPU Launcher & Slash Commands
# ==============================================================================

def test_launch_vulkan_dual_gpu_tool(agent_engine):
    vulkan = agent_engine.tools.execute("launch_vulkan_dual_gpu", model_key="loom-sovereign", port=8002)
    assert vulkan["success"] is True
    assert vulkan["port"] == 8002
    assert "--split-mode layer" in vulkan["command"]
    assert "--tensor-split 60,40" in vulkan["command"]


def test_slash_commands_and_nl_routing(agent_engine):
    repl = ClothOSAgentREPL(agent_engine.workspace_root)
    repl.engine = agent_engine

    # 1. Slash command /generate
    res_slash = repl.handle_slash_command("/generate Explain Kuramoto phase synchronization in 1 line.")
    assert res_slash is False  # Successfully handled without exiting

    # 2. Slash command /vulkan
    res_vulkan = repl.handle_slash_command("/vulkan loom-sovereign 8002")
    assert res_vulkan is False

    # 3. Slash command /synth
    res_synth = repl.handle_slash_command("/synth 528.0 0.1")
    assert res_synth is False

    # 4. Natural language routing in process_query
    nl_gen = agent_engine.process_query("generate text about the speed of light")
    assert "ClothOS Sovereign Text Generation" in nl_gen

    nl_sim = agent_engine.process_query('semantic similarity between "alpha" and "omega"')
    assert "Semantic Similarity Evaluation" in nl_sim

    nl_bio = agent_engine.process_query("biomolecular analysis of sequence ATGCCCAGATAG")
    assert "Biomolecular Analysis Receipt" in nl_bio
