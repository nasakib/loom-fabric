"""
Data types and models for the Postcomputational Engine (`loom/postcomputational/types.py`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import time
from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np


class PipelineStage(str, Enum):
    PREPROCESS = "PREPROCESS"
    COMPUTE = "COMPUTE"
    POSTPROCESS = "POSTPROCESS"


@dataclass
class TraceRecord:
    """Immutable record tracking one stage of postcomputational transformation."""
    stage: PipelineStage
    entity_id: str
    timestamp: float = field(default_factory=time.time)
    inputs_hash: str = ""
    outputs_hash: str = ""
    metrics: Dict[str, Any] = field(default_factory=dict)
    hardware_context: str = "skyTech // RTX 3060 + RX 580"
    verified: bool = True

    def compute_hash(self) -> str:
        content = f"{self.stage.value}:{self.entity_id}:{self.timestamp}:{self.inputs_hash}:{self.outputs_hash}:{sorted(self.metrics.items())}"
        return f"0x{hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]}"


@dataclass
class PostcomputationalNode:
    """Represents a tokenized, vectorized, and ray-traced empirical node."""
    id: str
    title: str
    submolt: str = "m/systems-engineering"
    cycle_min: int = 0
    cycle_max: int = 0
    timestamp_iso: str = ""
    confirmed_count: int = 0
    refuted_count: int = 0
    invariants: List[str] = field(default_factory=list)
    refutations: List[str] = field(default_factory=list)
    hardware_devices: List[str] = field(default_factory=list)
    raw_tokens: List[str] = field(default_factory=list)
    
    # Linear Algebra Vector Space
    embedding: Optional[np.ndarray] = None  # Vector in R^d (d=64)
    proj_3d: Tuple[float, float, float] = (0.0, 0.0, 0.0)  # Top 3 SVD coordinates
    
    # Vector Calculus Differential Operators
    gradient_vector: Optional[np.ndarray] = None  # Grad Phi
    gradient_norm: float = 0.0
    divergence: float = 0.0  # Div F (source/sink)
    curl_norm: float = 0.0   # ||Curl F|| (vorticity/cyclic feedback)

    # Vector Calculus Integral Operators
    scalar_potential: float = 0.0   # Phi(x): local scalar potential value
    line_integral: float = 0.0      # \int_C F . dr (path accumulation along citations)
    flux_integral: float = 0.0      # \iint_S F . dA (net outward flux via Divergence Theorem)
    volume_integral: float = 0.0    # \iiint_V Phi dV (integrated confidence mass)

    # Ray Tracing & Radiance Illumination
    radiance: float = 0.0  # [0.0, 1.0] Ray-traced confidence illumination
    ray_hits: int = 0      # Number of ray intersections
    radius: float = 0.5    # Bounding sphere radius in 3D projection

    # Obsidian-Style Bidirectional Graph
    wikilinks: List[str] = field(default_factory=list)
    backlinks: List[str] = field(default_factory=list)
    provenance_hash: str = ""

    def summary_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "submolt": self.submolt,
            "cycles": f"#{self.cycle_min}..#{self.cycle_max}",
            "confirmed_count": self.confirmed_count,
            "refuted_count": self.refuted_count,
            "invariants_count": len(self.invariants),
            "proj_3d": [round(float(x), 4) for x in self.proj_3d],
            "radiance": round(self.radiance, 4),
            "gradient_norm": round(self.gradient_norm, 4),
            "divergence": round(self.divergence, 4),
            "curl_norm": round(self.curl_norm, 4),
            "scalar_potential": round(self.scalar_potential, 4),
            "line_integral": round(self.line_integral, 4),
            "flux_integral": round(self.flux_integral, 4),
            "volume_integral": round(self.volume_integral, 4),
            "ray_hits": self.ray_hits,
            "wikilinks_count": len(self.wikilinks),
            "backlinks_count": len(self.backlinks),
            "provenance_hash": self.provenance_hash,
        }
