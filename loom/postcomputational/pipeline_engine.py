"""
Unified Postcomputational Pipeline Engine (`loom/postcomputational/pipeline_engine.py`).

Coordinates the complete 3-stage postcomputational lifecycle:
1. PREPROCESS: Tokenization & Semantic Parsing
2. COMPUTE: Linear Algebra (SVD, Gram Matrix), Vector Calculus (Gradient, Div, Curl), & Ray Tracing Radiance
3. POSTPROCESS: Obsidian Bidirectional Graph Generation & Cryptographic Traceability Logging
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from loom.postcomputational.obsidian_vault import ObsidianVaultGenerator
from loom.postcomputational.ray_tracer import PostcomputationalRayTracer, Ray
from loom.postcomputational.tokenizer import PostcomputationalTokenizer
from loom.postcomputational.traceability import TraceabilityLedger
from loom.postcomputational.types import PipelineStage, PostcomputationalNode, TraceRecord
from loom.postcomputational.vector_calculus import VectorCalculusEngine

logger = logging.getLogger("loom.postcomputational.pipeline")


class PostcomputationalPipeline:
    """Master orchestrator for postcomputational data transformation, vector calculus, and graph vaults."""

    def __init__(self, workspace_root: Optional[Path] = None):
        if workspace_root is None:
            workspace_root = Path(__file__).resolve().parents[2]
        self.workspace_root = workspace_root
        self.deliverables_dir = workspace_root / "deliverables"
        self.vault_dir = workspace_root / "vault"

        self.tokenizer = PostcomputationalTokenizer()
        self.vector_engine = VectorCalculusEngine(embedding_dim=64)
        self.ray_tracer = PostcomputationalRayTracer(attenuation=0.82)
        self.ledger = TraceabilityLedger(self.vault_dir / ".system" / "traceability_ledger.jsonl")
        self.vault_gen = ObsidianVaultGenerator(self.vault_dir)

        self.nodes: List[PostcomputationalNode] = []
        self._last_run_time: float = 0.0

    def run_full_pipeline(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """Runs all 3 stages over the deliverable collection."""
        t0 = time.time()
        logger.info(f"Starting Postcomputational Pipeline over {self.deliverables_dir}...")

        # -------------------------------------------------------------
        # STAGE 1: PREPROCESS (Tokenization & Parsing)
        # -------------------------------------------------------------
        files = sorted(self.deliverables_dir.glob("DELIVERABLE_*.md"), reverse=True)
        if limit:
            files = files[:limit]

        logger.info(f"Stage 1 [PREPROCESS]: Tokenizing {len(files)} deliverables...")
        parsed_nodes: List[PostcomputationalNode] = []
        preprocess_traces: List[TraceRecord] = []

        for f in files:
            try:
                node, trace = self.tokenizer.parse_deliverable_file(f)
                parsed_nodes.append(node)
                preprocess_traces.append(trace)
            except Exception as e:
                logger.debug(f"Failed to parse {f.name}: {e}")

        self.ledger.record_batch(preprocess_traces)
        logger.info(f"Stage 1 Complete: {len(parsed_nodes)} nodes tokenized.")

        if not parsed_nodes:
            return {"status": "EMPTY", "nodes_processed": 0, "elapsed_sec": time.time() - t0}

        # -------------------------------------------------------------
        # STAGE 2: COMPUTE (Linear Algebra, Vector Calculus, Ray Tracing)
        # -------------------------------------------------------------
        logger.info("Stage 2 [COMPUTE]: Computing Vector Embeddings & SVD Projections...")
        X = self.vector_engine.embed_nodes(parsed_nodes)
        coords_3d = self.vector_engine.compute_svd_3d_projection(X, parsed_nodes)

        logger.info("Stage 2 [COMPUTE]: Calculating Vector Calculus Fields (Gradient, Div, Curl)...")
        calculus_traces = self.vector_engine.compute_vector_calculus_fields(parsed_nodes, coords_3d)
        self.ledger.record_batch(calculus_traces)

        logger.info("Stage 2 [COMPUTE]: Integrating Manifold (Line, Flux, and Volume Integrals)...")
        integral_traces = self.vector_engine.compute_integral_calculus(parsed_nodes, coords_3d)
        self.ledger.record_batch(integral_traces)

        logger.info("Stage 2 [COMPUTE]: Executing Ray-Traced Radiance & Global Illumination...")
        self.ray_tracer.load_nodes(parsed_nodes)
        radiance_traces = self.ray_tracer.propagate_radiance(max_bounces=3)
        self.ledger.record_batch(radiance_traces)

        # -------------------------------------------------------------
        # STAGE 3: POSTPROCESS (Obsidian Vault & Bidirectional Wikilinks)
        # -------------------------------------------------------------
        logger.info("Stage 3 [POSTPROCESS]: Generating Obsidian Vault & Wikilinks Graph...")
        vault_traces = self.vault_gen.generate_vault(parsed_nodes)
        self.ledger.record_batch(vault_traces)

        self.nodes = parsed_nodes
        self._last_run_time = time.time()
        elapsed = round(time.time() - t0, 3)

        tot_confirmed = sum(n.confirmed_count for n in parsed_nodes)
        tot_refuted = sum(n.refuted_count for n in parsed_nodes)
        mean_radiance = float(np.mean([n.radiance for n in parsed_nodes])) if parsed_nodes else 0.0
        mean_line_int = float(np.mean([n.line_integral for n in parsed_nodes])) if parsed_nodes else 0.0
        tot_flux = float(np.sum([n.flux_integral for n in parsed_nodes])) if parsed_nodes else 0.0
        tot_vol_mass = float(np.sum([n.volume_integral for n in parsed_nodes])) if parsed_nodes else 0.0

        summary = {
            "status": "SUCCESS",
            "nodes_processed": len(parsed_nodes),
            "confirmed_invariants": tot_confirmed,
            "refuted_bounds": tot_refuted,
            "mean_radiance": round(mean_radiance, 4),
            "mean_line_integral": round(mean_line_int, 4),
            "total_flux_integral": round(tot_flux, 4),
            "integrated_volume_mass": round(tot_vol_mass, 4),
            "vault_path": str(self.vault_dir),
            "elapsed_sec": elapsed,
            "timestamp": self._last_run_time,
        }
        logger.info(f"Postcomputational Pipeline Completed in {elapsed}s: {summary}")
        return summary

    def query_ray(self, origin: Tuple[float, float, float], direction: Tuple[float, float, float], beam_radius: float = 1.8) -> List[Dict[str, Any]]:
        """Casts a ray and returns intersecting nodes sorted by distance."""
        if not self.nodes:
            self.run_full_pipeline(limit=150)
        if not self.ray_tracer.nodes and self.nodes:
            self.ray_tracer.load_nodes(self.nodes)

        orig_arr = np.array(origin, dtype=np.float32)
        dir_arr = np.array(direction, dtype=np.float32)
        norm = np.linalg.norm(dir_arr)
        if norm > 1e-9:
            dir_arr /= norm

        ray = Ray(origin=orig_arr, direction=dir_arr, beam_radius=beam_radius)
        hits = self.ray_tracer.cast_ray(ray)

        return [
            {
                "id": node.id,
                "title": node.title,
                "submolt": node.submolt,
                "hit_distance_t": round(dist, 4),
                "radiance": round(node.radiance, 4),
                "invariants": node.invariants,
                "proj_3d": [round(float(c), 3) for c in node.proj_3d],
            }
            for node, dist in hits
        ]

    def get_graph_data(self, limit: int = 250) -> Dict[str, Any]:
        """Returns structured JSON nodes and edges for 3D/2D interactive visualization."""
        if not self.nodes:
            # Auto-run if empty
            self.run_full_pipeline(limit=min(limit, 200))

        display_nodes = self.nodes[:limit]
        node_id_set = {n.id for n in display_nodes}

        nodes_json = []
        for n in display_nodes:
            nodes_json.append({
                "id": n.id,
                "title": n.title,
                "submolt": n.submolt,
                "x": round(float(n.proj_3d[0]), 3),
                "y": round(float(n.proj_3d[1]), 3),
                "z": round(float(n.proj_3d[2]), 3),
                "radiance": round(n.radiance, 3),
                "gradient_norm": round(n.gradient_norm, 3),
                "divergence": round(n.divergence, 3),
                "curl_norm": round(n.curl_norm, 3),
                "scalar_potential": round(n.scalar_potential, 3),
                "line_integral": round(n.line_integral, 3),
                "flux_integral": round(n.flux_integral, 3),
                "volume_integral": round(n.volume_integral, 3),
                "confirmed": n.confirmed_count,
                "refuted": n.refuted_count,
                "ray_hits": n.ray_hits,
            })

        edges_json = []
        for n in display_nodes:
            for target_id in n.wikilinks:
                if target_id in node_id_set and target_id != n.id:
                    edges_json.append({
                        "source": n.id,
                        "target": target_id,
                    })

        return {
            "total_nodes": len(nodes_json),
            "total_edges": len(edges_json),
            "nodes": nodes_json,
            "edges": edges_json,
        }

    def get_vault_stats(self) -> Dict[str, Any]:
        """Returns aggregate metrics of the postcomputational knowledge graph."""
        if not self.nodes:
            self.run_full_pipeline(limit=150)
        if not self.nodes:
            return {"status": "INITIALIZING", "total_nodes": 0}

        submolt_counts: Dict[str, int] = {}
        for n in self.nodes:
            submolt_counts[n.submolt] = submolt_counts.get(n.submolt, 0) + 1

        return {
            "total_nodes": len(self.nodes),
            "confirmed_invariants": sum(n.confirmed_count for n in self.nodes),
            "refuted_boundaries": sum(n.refuted_count for n in self.nodes),
            "mean_radiance": round(float(np.mean([n.radiance for n in self.nodes])), 4),
            "mean_gradient_norm": round(float(np.mean([n.gradient_norm for n in self.nodes])), 4),
            "mean_divergence": round(float(np.mean([n.divergence for n in self.nodes])), 4),
            "mean_line_integral": round(float(np.mean([n.line_integral for n in self.nodes])), 4),
            "total_flux_integral": round(float(np.sum([n.flux_integral for n in self.nodes])), 4),
            "total_volume_mass": round(float(np.sum([n.volume_integral for n in self.nodes])), 4),
            "submolt_breakdown": submolt_counts,
            "vault_path": str(self.vault_dir),
            "last_pipeline_run": self._last_run_time,
        }


# Singleton Instance
postcomputational_pipeline = PostcomputationalPipeline()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ClothOS Postcomputational Pipeline CLI")
    parser.add_argument("--limit", type=int, default=200, help="Number of deliverables to process")
    args = parser.parse_args()

    pipeline = PostcomputationalPipeline()
    res = pipeline.run_full_pipeline(limit=args.limit)
    print("\n=== PIPELINE RUN COMPLETE ===")
    for k, v in res.items():
        print(f"  {k}: {v}")
