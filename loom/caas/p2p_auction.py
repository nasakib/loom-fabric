"""
VectorCore ClothOS P2P Compute Auction Clearinghouse.

Implements a Continuous Double Auction (CDA) matching engine for distributed
compute resources across the Spotlight-Local (sL) mesh network.

Consumers submit Bids (max rate, latency tolerance, required VRAM), and
Providers submit Asks (min rate, available VRAM, solar discount, geohash).
Matches are settled at an optimal clearing price, with 1.0% accruing to the
VectorCore Protocol Treasury and 99.0% routed to the local host.
"""

from __future__ import annotations

import heapq
import hashlib
import hmac
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


class BidOrder(BaseModel):
    """Consumer bid to acquire compute capacity."""
    bid_id: str = Field(default_factory=lambda: f"bid-{uuid.uuid4().hex[:8]}")
    consumer_id: str
    workload_type: str = Field(
        ...,
        description="'ai_inference', 'cloud_gaming_60fps', 'cloud_gaming_120fps', 'video_transcode', '3d_render'"
    )
    max_rate_usd_per_hr: float
    min_vram_gb: float = 8.0
    max_acceptable_latency_ms: float = 30.0
    consumer_geohash: str = "dn5bpq"
    created_at_epoch: float = Field(default_factory=time.time)
    status: str = Field("open", description="'open', 'matched', 'cancelled', 'expired'")


class AskOrder(BaseModel):
    """Provider ask offering compute capacity to the network."""
    ask_id: str = Field(default_factory=lambda: f"ask-{uuid.uuid4().hex[:8]}")
    provider_node_id: str
    supported_workloads: List[str]
    min_rate_usd_per_hr: float
    available_vram_gb: float
    reported_latency_ms: float = 1.0
    provider_geohash: str = "dn5bpq"
    is_solar_powered: bool = False
    solar_discount_pct: float = Field(0.0, description="e.g. 0.15 for 15% discount during peak solar generation")
    created_at_epoch: float = Field(default_factory=time.time)
    status: str = Field("open", description="'open', 'matched', 'cancelled', 'expired'")

    @property
    def effective_min_rate_usd_per_hr(self) -> float:
        return round(self.min_rate_usd_per_hr * (1.0 - self.solar_discount_pct), 4)


class AuctionMatchResult(BaseModel):
    """Executed match contract between consumer bid and provider ask."""
    match_id: str = Field(default_factory=lambda: f"match-{uuid.uuid4().hex[:10]}")
    bid_id: str
    ask_id: str
    consumer_id: str
    provider_node_id: str
    workload_type: str
    clearing_rate_usd_per_hr: float
    clearing_rate_usd_per_sec: float
    platform_fee_rate_usd_per_hr: float
    provider_net_rate_usd_per_hr: float
    matched_vram_gb: float
    matched_at_epoch: float = Field(default_factory=time.time)
    escrow_deposit_required_usd: float
    match_signature: str


class P2PComputeAuction:
    """
    Continuous Double Auction (CDA) order book and execution engine.
    """
    def __init__(self, treasury_secret: str = "vectorcore_auction_secret"):
        self.secret = treasury_secret.encode("utf-8")
        self.bids: Dict[str, BidOrder] = {}
        self.asks: Dict[str, AskOrder] = {}
        self.matched_contracts: Dict[str, AuctionMatchResult] = {}

    def submit_bid(self, bid: BidOrder) -> Tuple[BidOrder, Optional[AuctionMatchResult]]:
        """Registers a consumer bid and attempts immediate clearing against existing asks."""
        self.bids[bid.bid_id] = bid
        match = self._attempt_match_bid(bid)
        return bid, match

    def submit_ask(self, ask: AskOrder) -> Tuple[AskOrder, Optional[AuctionMatchResult]]:
        """Registers a provider ask and attempts immediate clearing against existing bids."""
        self.asks[ask.ask_id] = ask
        match = self._attempt_match_ask(ask)
        return ask, match

    def cancel_bid(self, bid_id: str) -> bool:
        if bid_id in self.bids and self.bids[bid_id].status == "open":
            self.bids[bid_id].status = "cancelled"
            return True
        return False

    def cancel_ask(self, ask_id: str) -> bool:
        if ask_id in self.asks and self.asks[ask_id].status == "open":
            self.asks[ask_id].status = "cancelled"
            return True
        return False

    def _attempt_match_bid(self, bid: BidOrder) -> Optional[AuctionMatchResult]:
        eligible_asks: List[Tuple[float, AskOrder]] = []
        for ask in self.asks.values():
            if ask.status != "open":
                continue
            if bid.workload_type not in ask.supported_workloads:
                continue
            if ask.available_vram_gb < bid.min_vram_gb:
                continue
            if ask.reported_latency_ms > bid.max_acceptable_latency_ms:
                continue
            eff_rate = ask.effective_min_rate_usd_per_hr
            if eff_rate <= bid.max_rate_usd_per_hr:
                # Priority score: lower price + geohash affinity + low latency
                geo_bonus = 0.5 if ask.provider_geohash[:4] == bid.consumer_geohash[:4] else 0.0
                score = eff_rate - geo_bonus + (ask.reported_latency_ms / 100.0)
                eligible_asks.append((score, ask))

        if not eligible_asks:
            return None

        # Sort by score ascending (best match first)
        eligible_asks.sort(key=lambda x: x[0])
        _, best_ask = eligible_asks[0]
        return self._execute_contract(bid, best_ask)

    def _attempt_match_ask(self, ask: AskOrder) -> Optional[AuctionMatchResult]:
        eligible_bids: List[Tuple[float, BidOrder]] = []
        eff_ask_rate = ask.effective_min_rate_usd_per_hr
        for bid in self.bids.values():
            if bid.status != "open":
                continue
            if bid.workload_type not in ask.supported_workloads:
                continue
            if ask.available_vram_gb < bid.min_vram_gb:
                continue
            if ask.reported_latency_ms > bid.max_acceptable_latency_ms:
                continue
            if bid.max_rate_usd_per_hr >= eff_ask_rate:
                # High max rate bid wins, geo proximity preference
                geo_bonus = 0.5 if ask.provider_geohash[:4] == bid.consumer_geohash[:4] else 0.0
                score = -bid.max_rate_usd_per_hr - geo_bonus
                eligible_bids.append((score, bid))

        if not eligible_bids:
            return None

        eligible_bids.sort(key=lambda x: x[0])
        _, best_bid = eligible_bids[0]
        return self._execute_contract(best_bid, ask)

    def _execute_contract(self, bid: BidOrder, ask: AskOrder) -> AuctionMatchResult:
        # Midpoint clearing price
        eff_ask_rate = ask.effective_min_rate_usd_per_hr
        clearing_rate = round((bid.max_rate_usd_per_hr + eff_ask_rate) / 2.0, 4)
        rate_per_sec = round(clearing_rate / 3600.0, 6)
        
        # 1.0% protocol fee, 99.0% host revenue
        platform_fee = round(clearing_rate * 0.01, 4)
        provider_net = round(clearing_rate * 0.99, 4)

        # Deposit escrow = 30 minutes of estimated consumption
        escrow_deposit = round(clearing_rate * 0.5, 4)

        sig_data = f"{bid.bid_id}:{ask.ask_id}:{clearing_rate}:{bid.consumer_id}:{ask.provider_node_id}"
        sig = hmac.new(self.secret, sig_data.encode("utf-8"), hashlib.sha256).hexdigest()

        match = AuctionMatchResult(
            bid_id=bid.bid_id,
            ask_id=ask.ask_id,
            consumer_id=bid.consumer_id,
            provider_node_id=ask.provider_node_id,
            workload_type=bid.workload_type,
            clearing_rate_usd_per_hr=clearing_rate,
            clearing_rate_usd_per_sec=rate_per_sec,
            platform_fee_rate_usd_per_hr=platform_fee,
            provider_net_rate_usd_per_hr=provider_net,
            matched_vram_gb=ask.available_vram_gb,
            escrow_deposit_required_usd=escrow_deposit,
            match_signature=sig,
        )

        bid.status = "matched"
        ask.status = "matched"
        self.matched_contracts[match.match_id] = match
        return match

    def get_order_book_depth(self) -> Dict[str, Any]:
        """Provides transparency on spot liquidity, spread, and active orders."""
        open_bids = [b for b in self.bids.values() if b.status == "open"]
        open_asks = [a for a in self.asks.values() if a.status == "open"]
        
        highest_bid = max([b.max_rate_usd_per_hr for b in open_bids], default=0.0)
        lowest_ask = min([a.effective_min_rate_usd_per_hr for a in open_asks], default=0.0)
        
        return {
            "total_open_bids": len(open_bids),
            "total_open_asks": len(open_asks),
            "highest_bid_usd_per_hr": highest_bid,
            "lowest_ask_usd_per_hr": lowest_ask,
            "bid_ask_spread_usd": round(lowest_ask - highest_bid, 4) if lowest_ask > 0 and highest_bid > 0 else 0.0,
            "open_bids": [b.dict() for b in open_bids[-10:]],
            "open_asks": [a.dict() for a in open_asks[-10:]],
            "recent_contracts": [c.dict() for c in list(self.matched_contracts.values())[-5:]],
        }
