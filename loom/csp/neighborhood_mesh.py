"""
Neighborhood Mesh Discovery & Routing for Spotlight-Local CSP Nodes.

Ranks nearby compute nodes by geohash distance, ping RTT latency,
and Landauer thermodynamic efficiency to route inference tasks to the
optimal proximate household or business.
"""

from __future__ import annotations

import math
import time
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from loom.csp.manifest import CspNodeManifest


class PeerNodeScore(BaseModel):
    """Evaluation score for a proximate CSP candidate."""
    node_id: str
    geohash: str
    rtt_ms: float
    available_vram_gb: float
    price_per_1k_comp_usd: float
    landauer_pj_per_mac: float
    is_solar_powered: bool
    composite_rank_score: float = Field(..., description="Lower is better")


class NeighborhoodMeshRouter:
    """
    In-memory registry and proximity scheduler for local CSP nodes.
    """
    def __init__(self, local_geohash: str = "dn5bpq"):
        self.local_geohash = local_geohash
        self._registered_peers: Dict[str, CspNodeManifest] = {}
        self._peer_latency_cache: Dict[str, float] = {}

    def register_peer(self, manifest: CspNodeManifest, ping_rtt_ms: float = 1.5) -> None:
        self._registered_peers[manifest.node_id] = manifest
        self._peer_latency_cache[manifest.node_id] = ping_rtt_ms

    def unregister_peer(self, node_id: str) -> None:
        self._registered_peers.pop(node_id, None)
        self._peer_latency_cache.pop(node_id, None)

    def _approximate_geohash_distance_km(self, g1: str, g2: str) -> float:
        """Heuristic prefix match distance between two geohashes."""
        common_len = 0
        for c1, c2 in zip(g1, g2):
            if c1 == c2:
                common_len += 1
            else:
                break
        # Geohash prefix decay: 8 chars ~= 19m, 7 ~= 76m, 6 ~= 610m, 5 ~= 2.4km, 4 ~= 20km
        decay_map = {8: 0.02, 7: 0.08, 6: 0.61, 5: 2.4, 4: 20.0, 3: 78.0, 2: 630.0, 1: 2500.0, 0: 10000.0}
        return decay_map.get(common_len, 10000.0)

    def select_optimal_csp(
        self,
        required_vram_gb: float = 8.0,
        target_model: Optional[str] = None,
        caller_geohash: Optional[str] = None
    ) -> Optional[Tuple[CspNodeManifest, PeerNodeScore]]:
        """Finds the lowest-latency, most cost-effective neighbor meeting requirements."""
        reference_geo = caller_geohash or self.local_geohash
        candidates: List[Tuple[CspNodeManifest, PeerNodeScore]] = []

        for node_id, manifest in self._registered_peers.items():
            # Check model support
            if target_model and target_model != "auto" and target_model not in manifest.served_models:
                continue
            
            # Check VRAM headroom
            if manifest.aggregate_vram_gb < required_vram_gb:
                continue

            rtt = self._peer_latency_cache.get(node_id, 10.0)
            dist_km = self._approximate_geohash_distance_km(reference_geo, manifest.geohash)
            price = manifest.pricing.price_per_1k_completion_tokens_usd
            
            # Solar bonus: Reduce rank score by 25% if running on green solar
            solar_discount = 0.75 if manifest.is_solar_powered else 1.0

            # Composite score: Latency weight + Distance weight + Price weight
            score = (
                (rtt * 0.40) +
                (dist_km * 0.35) +
                (price * 100.0 * 0.25)
            ) * solar_discount

            peer_score = PeerNodeScore(
                node_id=node_id,
                geohash=manifest.geohash,
                rtt_ms=rtt,
                available_vram_gb=manifest.aggregate_vram_gb,
                price_per_1k_comp_usd=price,
                landauer_pj_per_mac=manifest.landauer_rating_pj_per_mac,
                is_solar_powered=manifest.is_solar_powered,
                composite_rank_score=round(score, 3)
            )
            candidates.append((manifest, peer_score))

        if not candidates:
            return None

        # Sort ascending by composite rank score (lowest is best)
        candidates.sort(key=lambda x: x[1].composite_rank_score)
        return candidates[0]

    def list_active_neighbors(self) -> List[Dict[str, Any]]:
        return [
            {
                "node_id": m.node_id,
                "node_name": m.node_name,
                "geohash": m.geohash,
                "neighborhood": m.neighborhood_tag,
                "vram_gb": m.aggregate_vram_gb,
                "rtt_ms": self._peer_latency_cache.get(m.node_id, 0.0),
                "is_solar_powered": m.is_solar_powered,
                "price_comp_usd": m.pricing.price_per_1k_completion_tokens_usd
            }
            for m in self._registered_peers.values()
        ]
