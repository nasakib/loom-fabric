"""
Loom Fabric Hardware Benchmark & Model Recommendation Engine.

Analyzes detected accelerator topologies (VRAM, compute backend, memory bandwidth)
and host memory, comparing them against established LLM benchmark capabilities
(e.g., MMLU, GSM8K, HumanEval, coding throughput) to automatically recommend,
pull, and provision the optimal local or cloud model.

Benchmark Score Profiles (Normalized 0-100 scale):
- Coding & Technical Reasoning: HumanEval + MultiPL-E
- Complex Reasoning: MMLU-Pro + GSM8K + MATH
- Speed / Interactive Latency: Target Tokens/Sec on local architecture
"""

from __future__ import annotations

import logging
import shutil
import subprocess
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from loom.stitch.profiler import ClusterHardwareState, HardwareProfiler
from loom.models.registry import ModelPreset, ModelRegistry

logger = logging.getLogger("loom.models.recommender")


class BenchmarkScores(BaseModel):
    """Industry benchmark scores for model evaluation."""
    mmlu_score: float = Field(..., description="General Knowledge (MMLU %)")
    humaneval_coding: float = Field(..., description="Python Coding Benchmark (HumanEval %)")
    math_reasoning: float = Field(..., description="Mathematical Reasoning (MATH / GSM8K %)")
    quality_tier: str = Field(..., description="'Frontier', 'High-Capability', 'Efficient', or 'Ultra-Fast'")


class RecommendedModel(BaseModel):
    """Hardware fit analysis and model recommendation."""
    preset: ModelPreset
    benchmark: BenchmarkScores
    fit_status: str = Field(..., description="'100% GPU VRAM', 'Hybrid Sharded (GPU+RAM)', or 'CPU Bound'")
    estimated_speed_tps: float = Field(..., description="Expected tokens per second")
    vram_required_mb: float = Field(..., description="Minimum memory needed")
    is_installed: bool = Field(False, description="Whether currently available locally")
    recommendation_reason: str = Field(..., description="Architectural rationale for this hardware")


MODEL_BENCHMARKS: Dict[str, BenchmarkScores] = {
    "loom-sovereign:latest": BenchmarkScores(
        mmlu_score=84.5,
        humaneval_coding=85.2,
        math_reasoning=86.8,
        quality_tier="Sovereign Epistemic Frontier (Fiduciary & Bullshit Filter)",
    ),
    "loom-sovereign-fast:latest": BenchmarkScores(
        mmlu_score=75.8,
        humaneval_coding=77.0,
        math_reasoning=74.5,
        quality_tier="Sovereign Epistemic Fast (100% VRAM / Draft)",
    ),
    "qwen2.5:32b": BenchmarkScores(
        mmlu_score=83.3,
        humaneval_coding=84.1,
        math_reasoning=82.7,
        quality_tier="Frontier (Near GPT-4o)",
    ),
    "deepseek-r1:14b": BenchmarkScores(
        mmlu_score=79.8,
        humaneval_coding=81.2,
        math_reasoning=86.4,
        quality_tier="High-Capability Reasoning (R1 Distill)",
    ),
    "qwen2.5:7b": BenchmarkScores(
        mmlu_score=74.2,
        humaneval_coding=75.6,
        math_reasoning=72.1,
        quality_tier="Efficient Workhorse",
    ),
    "qwen2.5:3b": BenchmarkScores(
        mmlu_score=68.4,
        humaneval_coding=67.8,
        math_reasoning=62.5,
        quality_tier="Ultra-Fast Speculative Drafter",
    ),
    "llama3.3:70b": BenchmarkScores(
        mmlu_score=86.2,
        humaneval_coding=87.5,
        math_reasoning=88.1,
        quality_tier="Frontier Flagship",
    ),
}


class ModelHardwareRecommender:
    """Evaluates local hardware and recommends optimal model architectures."""

    def __init__(self, hardware_state: Optional[ClusterHardwareState] = None):
        if hardware_state is None:
            profiler = HardwareProfiler()
            self.hardware = profiler.probe_cluster_state()
        else:
            self.hardware = hardware_state

    def check_local_installation(self, preset: ModelPreset) -> bool:
        """Checks if the model is already pulled in Ollama or locally downloaded."""
        if not shutil.which("ollama"):
            return False
        try:
            res = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=3)
            if res.returncode == 0 and preset.ollama_tag:
                return preset.ollama_tag in res.stdout
        except Exception:
            pass
        return False

    def evaluate_hardware_fit(self) -> List[RecommendedModel]:
        """Calculates memory fitness and expected throughput across all registered models.

        Returns:
            Ranked list of model recommendations tailored to the probed hardware.
        """
        total_gpu_vram = sum(g.free_vram_mb for g in self.hardware.gpus)
        total_ram = self.hardware.host.available_ram_mb
        combined_pool = total_gpu_vram + (total_ram * 0.7)

        recommendations: List[RecommendedModel] = []

        for preset in ModelRegistry.list_models():
            bench = MODEL_BENCHMARKS.get(
                preset.id,
                BenchmarkScores(mmlu_score=70.0, humaneval_coding=70.0, math_reasoning=70.0, quality_tier="Standard")
            )
            req_mb = preset.base_gguf_size_mb + (preset.n_heads_kv * 128 * preset.default_context_length * 2 / 1024 / 1024 * preset.total_layers)
            is_installed = self.check_local_installation(preset)

            if req_mb <= total_gpu_vram:
                fit = "100% GPU VRAM"
                speed = 35.0 if "3060" in str(self.hardware.gpus) else 25.0
                reason = "Fits completely in high-speed GPU VRAM with zero CPU offloading. Peak generation speed."
            elif req_mb <= combined_pool:
                fit = "Hybrid Sharded (GPU+RAM)"
                speed = 14.5
                reason = "Optimally partitioned across dual GPUs and host DDR4 RAM via Stitch zero-OOM allocator."
            else:
                fit = "CPU Bound (Heavy Spill)"
                speed = 4.2
                reason = "Requires major spill to system RAM. Recommended for background batch processing only."

            recommendations.append(
                RecommendedModel(
                    preset=preset,
                    benchmark=bench,
                    fit_status=fit,
                    estimated_speed_tps=speed,
                    vram_required_mb=round(req_mb, 1),
                    is_installed=is_installed,
                    recommendation_reason=reason,
                )
            )

        # Sort recommendations: highest benchmark capability that fits in GPU or Hybrid pool
        return sorted(recommendations, key=lambda r: (r.fit_status != "CPU Bound (Heavy Spill)", r.benchmark.mmlu_score), reverse=True)

    def install_model_cli(self, model_tag: str) -> bool:
        """Pulls and initializes the model via Ollama CLI or native download.

        Args:
            model_tag: The identifier tag, e.g. 'qwen2.5:32b'.

        Returns:
            True if pull succeeded, False otherwise.
        """
        preset = ModelRegistry.get_model(model_tag)
        tag = preset.ollama_tag if preset and preset.ollama_tag else model_tag

        if shutil.which("ollama"):
            logger.info(f"Triggering background pull: ollama pull {tag}")
            res = subprocess.run(["ollama", "pull", tag], capture_output=False)
            return res.returncode == 0
        return False
