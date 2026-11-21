"""
ClothOS Sovereign Compute Broker.

Acts as the decentralized middleman connecting Compute Service Providers (CSPs)
with Compute Service Consumers (CSCs) across AI inference, real-time gaming,
video editing, and 3D rendering under VectorCore Holdings and Spotlight-Local.
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from loom.csp.manifest import CspNodeManifest, CspPricingModel
from loom.csp.streaming_meter import StreamingComputeMeter, ComputeMeterReading
from loom.csp.sl_settlement import SlSettlementEngine, SlComputeInvoice
from loom.csp.neighborhood_mesh import NeighborhoodMeshRouter, PeerNodeScore


class ConsumerWorkloadRequest(BaseModel):
    """Incoming demand request from a Compute Service Consumer (CSC)."""
    consumer_id: str = Field(..., description="Unique caller identifier")
    consumer_geohash: str = Field(..., description="Consumer spatial coordinate")
    workload_type: str = Field(
        "ai_inference",
        description="Workload type: 'ai_inference', 'cloud_gaming', 'video_editing', '3d_rendering'"
    )
    target_spec: Dict[str, Any] = Field(
        default_factory=dict,
        description="Detailed requirements: model_id, target_resolution, max_rtt_ms, required_vram_gb"
    )
    max_acceptable_rate_usd_hr: float = Field(
        1.50,
        description="Maximum rate in USD the consumer is willing to pay per hour"
    )
    caller_avatar_totem_id: Optional[str] = Field(
        None,
        description="Consumer's NFC/UWB 3D Avatar Figurine token ID for authentication"
    )


class BrokerMatchResult(BaseModel):
    """Matched allocation produced by the ClothOS Middleman."""
    match_id: str = Field(default_factory=lambda: f"mch-{uuid.uuid4().hex[:12]}")
    matched_provider_node_id: str
    matched_provider_node_name: str
    workload_type: str
    geohash_distance_km: float
    ping_rtt_ms: float
    is_solar_powered: bool
    pricing: CspPricingModel
    session_stream_endpoint: str
    created_at_epoch: float = Field(default_factory=time.time)


class ClothosComputeBroker:
    """
    The Core ClothOS Broker Engine orchestrating supply and demand across
    the Spotlight-Local spatial mesh under VectorCore Holdings.
    """
    def __init__(self, local_geohash: str = "dn5bpq"):
        self.local_geohash = local_geohash
        self.mesh_router = NeighborhoodMeshRouter(local_geohash=local_geohash)
        self.meters_by_node: Dict[str, StreamingComputeMeter] = {}
        self.settlement_engines_by_node: Dict[str, SlSettlementEngine] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}

    def register_provider_node(self, manifest: CspNodeManifest, ping_rtt_ms: float = 1.0) -> None:
        """Onboards an individual, household, or business as a Compute Service Provider."""
        self.mesh_router.register_peer(manifest, ping_rtt_ms=ping_rtt_ms)
        self.meters_by_node[manifest.node_id] = StreamingComputeMeter(
            node_id=manifest.node_id,
            landauer_rating_pj_per_mac=manifest.landauer_rating_pj_per_mac
        )
        self.settlement_engines_by_node[manifest.node_id] = SlSettlementEngine(
            provider_node_id=manifest.node_id
        )

    def unregister_provider_node(self, node_id: str) -> None:
        self.mesh_router.unregister_peer(node_id)
        self.meters_by_node.pop(node_id, None)
        self.settlement_engines_by_node.pop(node_id, None)

    def match_workload(self, req: ConsumerWorkloadRequest) -> BrokerMatchResult:
        """
        The Middleman Matching Algorithm:
        Evaluates physical distance, RTT latency, available VRAM, and pricing
        to select the optimal nearby provider for the requested workload.
        """
        required_vram = float(req.target_spec.get("required_vram_gb", 8.0))
        target_model = req.target_spec.get("model_id", "auto")

        best = self.mesh_router.select_optimal_csp(
            required_vram_gb=required_vram,
            target_model=target_model if req.workload_type == "ai_inference" else None,
            caller_geohash=req.consumer_geohash
        )

        if not best:
            raise RuntimeError(
                f"ClothOS Broker: No proximate CSP available matching requirements for '{req.workload_type}' near {req.consumer_geohash}."
            )

        provider, score = best
        dist_km = self.mesh_router._approximate_geohash_distance_km(req.consumer_geohash, provider.geohash)

        # Construct ephemeral stream endpoint based on workload
        if req.workload_type == "cloud_gaming":
            stream_url = f"rtp://{provider.provider_address}:47998/game_stream"
        elif req.workload_type == "video_editing":
            stream_url = f"webrtc://{provider.provider_address}:8002/video_proxy"
        else: # ai_inference / 3d_rendering
            stream_url = f"http://{provider.provider_address}:{provider.port}/v1/chat/completions"

        return BrokerMatchResult(
            matched_provider_node_id=provider.node_id,
            matched_provider_node_name=provider.node_name,
            workload_type=req.workload_type,
            geohash_distance_km=dist_km,
            ping_rtt_ms=score.rtt_ms,
            is_solar_powered=provider.is_solar_powered,
            pricing=provider.pricing,
            session_stream_endpoint=stream_url
        )

    def initiate_consumer_session(
        self,
        match: BrokerMatchResult,
        consumer_id: str,
        allocated_vram_gb: float = 12.0
    ) -> str:
        """Starts real-time compute tracking for the consumer-provider pair."""
        session_id = f"sess-{uuid.uuid4().hex[:12]}"
        meter = self.meters_by_node.get(match.matched_provider_node_id)
        if not meter:
            raise KeyError(f"Meter not found for node {match.matched_provider_node_id}")

        meter.start_session(
            session_id=session_id,
            model_id=match.workload_type,
            allocated_vram_gb=allocated_vram_gb
        )

        self.active_sessions[session_id] = {
            "consumer_id": consumer_id,
            "provider_node_id": match.matched_provider_node_id,
            "pricing": match.pricing,
            "workload_type": match.workload_type,
            "started_at": time.time()
        }
        return session_id

    def reconcile_and_settle(
        self,
        session_id: str,
        final_prompt_tokens: int = 0,
        final_completion_tokens: int = 0,
        host_merchant_account: Optional[str] = None
    ) -> SlComputeInvoice:
        """
        Finalizes compute session, applies Spotlight-Local's 1.0% fee,
        and generates an immutable HMAC-SHA256 double-entry settlement receipt.
        """
        if session_id not in self.active_sessions:
            raise KeyError(f"Session {session_id} not found in active broker registry.")

        session_meta = self.active_sessions.pop(session_id)
        node_id = session_meta["provider_node_id"]
        meter = self.meters_by_node[node_id]
        settlement = self.settlement_engines_by_node[node_id]

        reading = meter.finalize_session(
            session_id=session_id,
            final_prompt_tokens=final_prompt_tokens,
            final_completion_tokens=final_completion_tokens
        )

        invoice = settlement.create_invoice(
            reading=reading,
            pricing=session_meta["pricing"],
            sl_merchant_account_id=host_merchant_account
        )
        return invoice
