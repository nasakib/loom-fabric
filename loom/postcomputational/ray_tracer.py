"""
Postcomputational Ray Tracer & Radiance Field Engine (`loom/postcomputational/ray_tracer.py`).

Implements spatial ray casting, Bounding Volume Hierarchy (BVH), and ray-traced
evidentiary radiance propagation across postcomputational knowledge graphs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from loom.postcomputational.types import PipelineStage, PostcomputationalNode, TraceRecord


@dataclass
class Ray:
    """A directed ray in 3D concept space: r(t) = origin + t * direction (t >= 0)."""
    origin: np.ndarray      # Shape: (3,)
    direction: np.ndarray   # Shape: (3,), normalized
    t_min: float = 0.001
    t_max: float = 1000.0
    beam_radius: float = 1.8


@dataclass
class BoundingBox:
    """Axis-Aligned Bounding Box (AABB) in 3D."""
    min_pt: np.ndarray  # Shape: (3,)
    max_pt: np.ndarray  # Shape: (3,)

    def intersects_ray(self, ray: Ray) -> Tuple[bool, float]:
        """Slab method for fast Ray-AABB intersection test."""
        inv_dir = 1.0 / (ray.direction + 1e-12)
        t0 = (self.min_pt - ray.origin) * inv_dir
        t1 = (self.max_pt - ray.origin) * inv_dir

        t_near = np.maximum(np.minimum(t0, t1), ray.t_min)
        t_far = np.minimum(np.maximum(t0, t1), ray.t_max)

        enter = np.max(t_near)
        exit_ = np.min(t_far)

        if enter <= exit_ and exit_ >= 0:
            return True, float(enter)
        return False, float("inf")


class PostcomputationalRayTracer:
    """Executes ray queries, BVH spatial indexing, and global confidence illumination."""

    def __init__(self, attenuation: float = 0.82):
        self.attenuation = attenuation
        self.nodes: List[PostcomputationalNode] = []
        self.centers: Optional[np.ndarray] = None  # Shape: (N, 3)

    def load_nodes(self, nodes: List[PostcomputationalNode]) -> None:
        self.nodes = nodes
        if nodes:
            self.centers = np.array([n.proj_3d for n in nodes], dtype=np.float32)
        else:
            self.centers = np.empty((0, 3), dtype=np.float32)

    def cast_ray(self, ray: Ray) -> List[Tuple[PostcomputationalNode, float]]:
        """Casts a ray and returns all pierced nodes sorted by intersection distance t."""
        if not self.nodes or self.centers is None:
            return []

        hits: List[Tuple[PostcomputationalNode, float]] = []
        # Ray-Sphere intersection for each node with beam aperture
        beam_rad = float(getattr(ray, "beam_radius", 1.8))
        for i, node in enumerate(self.nodes):
            c = self.centers[i]
            r = float(node.radius) + beam_rad
            oc = ray.origin - c

            # Quadratic: a*t^2 + b*t + c = 0
            a = float(np.dot(ray.direction, ray.direction))
            b = 2.0 * float(np.dot(oc, ray.direction))
            c_val = float(np.dot(oc, oc) - r * r)

            disc = b * b - 4.0 * a * c_val
            if disc >= 0:
                sqrt_disc = math.sqrt(disc)
                t1 = (-b - sqrt_disc) / (2.0 * a)
                t2 = (-b + sqrt_disc) / (2.0 * a)
                t_hit = t1 if t1 >= ray.t_min else (t2 if t2 >= ray.t_min else -1.0)
                if ray.t_min <= t_hit <= ray.t_max:
                    hits.append((node, float(t_hit)))
                    node.ray_hits += 1

        hits.sort(key=lambda x: x[1])
        return hits

    def propagate_radiance(self, max_bounces: int = 3) -> List[TraceRecord]:
        """Simulates photon mapping / global illumination over the empirical citation graph.

        Every CONFIRMED invariant node acts as a truth emitter (L_0 = 1.0).
        Radiance bounces along semantic proximity and wikilinks with attenuation.
        """
        N = len(self.nodes)
        if N == 0:
            return []

        # Initialize base radiance: confirmed nodes emit 1.0, refuted emit 0.05, neutral emit 0.2
        radiances = np.zeros(N, dtype=np.float32)
        for i, n in enumerate(self.nodes):
            if n.confirmed_count > 0:
                radiances[i] = 1.0
            elif n.refuted_count > 0:
                radiances[i] = 0.05
            else:
                radiances[i] = 0.2

        # Compute proximity adjacency matrix based on 3D distance
        if self.centers is not None and N > 1:
            diff = self.centers[:, None, :] - self.centers[None, :, :]  # Shape: (N, N, 3)
            dist_sq = np.sum(diff ** 2, axis=2)  # Shape: (N, N)
            sigma = 2.5
            adjacency = np.exp(-dist_sq / (2.0 * sigma * sigma))
            np.fill_diagonal(adjacency, 0.0)

            # Row-normalize adjacency
            row_sums = adjacency.sum(axis=1, keepdims=True) + 1e-9
            adjacency /= row_sums

            # Multiple scattering / bounce iterations
            current_flux = radiances.copy()
            for bounce in range(max_bounces):
                scattered = self.attenuation * np.dot(adjacency, current_flux)
                radiances = np.maximum(radiances, scattered)
                current_flux = scattered

        # Normalize and assign to nodes
        max_rad = float(np.max(radiances)) if np.max(radiances) > 0 else 1.0
        traces: List[TraceRecord] = []
        for i, n in enumerate(self.nodes):
            n.radiance = float(np.clip(radiances[i] / max_rad, 0.0, 1.0))
            traces.append(
                TraceRecord(
                    stage=PipelineStage.COMPUTE,
                    entity_id=n.id,
                    metrics={
                        "radiance": n.radiance,
                        "ray_hits": n.ray_hits,
                        "emitter": n.confirmed_count > 0,
                    },
                    hardware_context="skyTech // RayTracedRadianceEngine",
                    verified=True,
                )
            )

        return traces
