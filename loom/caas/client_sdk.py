"""
VectorCore ClothOS CaaS Consumer Client SDK.

Client library enabling client applications (Spotlight-Local PWA, local games,
video editors, AI applications) to discover neighborhood CSPs, submit bids
into the P2P auction clearinghouse, preload consumer float, and stream
compute on demand.
"""

from __future__ import annotations

import hashlib
import time
import uuid
from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel, Field

from loom.caas.bank_vault import VectorCoreBankVault, BankAccount
from loom.caas.p2p_auction import P2PComputeAuction, BidOrder, AuctionMatchResult
from loom.csp.manifest import CspNodeManifest


class ComputeSession(BaseModel):
    """Active streaming compute session between a consumer and a CSP node."""
    session_id: str = Field(default_factory=lambda: f"sess-{uuid.uuid4().hex[:12]}")
    consumer_account_id: str
    provider_node_id: str
    provider_account_id: str
    match_id: str
    workload_type: str
    rate_usd_per_sec: float
    escrow_locked_usd: float
    start_time_epoch: float = Field(default_factory=time.time)
    end_time_epoch: Optional[float] = None
    accumulated_cost_usd: float = 0.0
    accumulated_tokens: int = 0
    accumulated_frames: int = 0
    status: str = Field("active", description="'active', 'completed', 'exhausted'")


class ClothosCaaSClient:
    """
    High-level Python SDK for consumers utilizing Spotlight-Local CaaS.
    """
    def __init__(
        self,
        consumer_id: str,
        bank_vault: Optional[VectorCoreBankVault] = None,
        auction: Optional[P2PComputeAuction] = None,
        gateway_url: str = "http://127.0.0.1:8087",
        consumer_geohash: str = "dn5bpq",
    ):
        self.consumer_id = consumer_id
        self.consumer_geohash = consumer_geohash
        self.gateway_url = gateway_url.rstrip("/")
        
        # In-memory engines (or fallback to remote HTTP calls)
        self.bank_vault = bank_vault or VectorCoreBankVault()
        self.auction = auction or P2PComputeAuction()
        
        # Ensure consumer bank account exists
        self.account = self.bank_vault.get_or_create_account(
            owner_id=self.consumer_id,
            account_type="consumer",
        )
        self.active_sessions: Dict[str, ComputeSession] = {}

    def preload_account_float(self, amount_usd: float) -> BankAccount:
        """Preloads fiat funds into the consumer's VectorCore Stored-Value balance."""
        self.account = self.bank_vault.deposit_fiat(self.account.account_id, amount_usd)
        return self.account

    def discover_local_csps(self, min_vram_gb: float = 8.0) -> List[Dict[str, Any]]:
        """Queries the neighborhood mesh for nearby compute providers."""
        try:
            with httpx.Client(timeout=3.0) as client:
                res = client.get(f"{self.gateway_url}/v1/csp/mesh/neighbors")
                if res.status_code == 200:
                    data = res.json()
                    neighbors = data.get("neighbors", [])
                    return [n for n in neighbors if n.get("aggregate_vram_gb", 0) >= min_vram_gb]
        except Exception:
            pass
        return []

    def request_compute_allocation(
        self,
        workload_type: str = "ai_inference",
        max_rate_usd_per_hr: float = 0.50,
        min_vram_gb: float = 8.0,
        max_latency_ms: float = 30.0,
    ) -> Optional[AuctionMatchResult]:
        """Submits a bid to the continuous double auction."""
        bid = BidOrder(
            consumer_id=self.consumer_id,
            workload_type=workload_type,
            max_rate_usd_per_hr=max_rate_usd_per_hr,
            min_vram_gb=min_vram_gb,
            max_acceptable_latency_ms=max_latency_ms,
            consumer_geohash=self.consumer_geohash,
        )
        _, match = self.auction.submit_bid(bid)
        return match

    def start_session(
        self,
        match: AuctionMatchResult,
        provider_account_id: str,
        escrow_budget_usd: float = 1.0,
    ) -> ComputeSession:
        """Locks consumer escrow and instantiates a streaming compute session."""
        success = self.bank_vault.lock_compute_escrow(self.account.account_id, escrow_budget_usd)
        if not success:
            raise ValueError(f"Insufficient funds: Balance ${self.account.balance_usd:.2f} < Escrow ${escrow_budget_usd:.2f}")

        session = ComputeSession(
            consumer_account_id=self.account.account_id,
            provider_node_id=match.provider_node_id,
            provider_account_id=provider_account_id,
            match_id=match.match_id,
            workload_type=match.workload_type,
            rate_usd_per_sec=match.clearing_rate_usd_per_sec,
            escrow_locked_usd=escrow_budget_usd,
        )
        self.active_sessions[session.session_id] = session
        return session

    def record_streaming_usage(
        self,
        session_id: str,
        duration_sec: float,
        tokens: int = 0,
        frames: int = 0,
    ) -> Dict[str, Any]:
        """Micro-meters incremental resource consumption."""
        if session_id not in self.active_sessions:
            raise KeyError(f"Session {session_id} not found.")

        session = self.active_sessions[session_id]
        cost_inc = round(duration_sec * session.rate_usd_per_sec, 6)
        session.accumulated_cost_usd = round(session.accumulated_cost_usd + cost_inc, 6)
        session.accumulated_tokens += tokens
        session.accumulated_frames += frames

        # Check if escrow exhausted
        remaining_escrow = round(session.escrow_locked_usd - session.accumulated_cost_usd, 4)
        if remaining_escrow <= 0:
            session.status = "exhausted"

        return {
            "session_id": session_id,
            "accumulated_cost_usd": session.accumulated_cost_usd,
            "remaining_escrow_usd": max(remaining_escrow, 0.0),
            "status": session.status,
        }

    def close_and_settle_session(self, session_id: str) -> Dict[str, Any]:
        """Terminates session and executes final settlement in the bank vault."""
        if session_id not in self.active_sessions:
            raise KeyError(f"Session {session_id} not found.")

        session = self.active_sessions[session_id]
        session.end_time_epoch = time.time()
        session.status = "completed"

        settlement = self.bank_vault.settle_compute_transaction(
            consumer_account_id=session.consumer_account_id,
            provider_account_id=session.provider_account_id,
            gross_cost_usd=session.accumulated_cost_usd,
            duration_seconds=session.end_time_epoch - session.start_time_epoch,
            workload_type=session.workload_type,
        )

        return {
            "session_id": session_id,
            "status": "settled",
            "settlement": settlement,
        }
