"""
ClothOS Sovereign Postcomputational Traceability & Graph Engine (`loom/postcomputational`).

Unifies empirical deliverable parsing, linear algebra vector embeddings,
vector calculus fields (gradient, divergence, curl), ray-traced radiance propagation,
and Obsidian-style bidirectional markdown graph generation.
"""

from __future__ import annotations

from loom.postcomputational.types import PostcomputationalNode, PipelineStage, TraceRecord
from loom.postcomputational.tokenizer import PostcomputationalTokenizer
from loom.postcomputational.vector_calculus import VectorCalculusEngine
from loom.postcomputational.ray_tracer import PostcomputationalRayTracer, Ray, BoundingBox
from loom.postcomputational.traceability import TraceabilityLedger
from loom.postcomputational.obsidian_vault import ObsidianVaultGenerator
from loom.postcomputational.pipeline_engine import PostcomputationalPipeline

__all__ = [
    "PostcomputationalNode",
    "PipelineStage",
    "TraceRecord",
    "PostcomputationalTokenizer",
    "VectorCalculusEngine",
    "PostcomputationalRayTracer",
    "Ray",
    "BoundingBox",
    "TraceabilityLedger",
    "ObsidianVaultGenerator",
    "PostcomputationalPipeline",
]
