"""
Spotlight-Local In-Network Settlement Client.

Implements real-dollar ($ USD) compute billing, 1.0% platform fee calculation,
99.0% host payout allocation, and cryptographic HMAC-SHA256 receipt generation
for the Spotlight-Local double-entry neobanking ledger.
"""

from __future__ import annotations

import hmac
import hashlib
import json
import time
import uuid
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from loom.csp.manifest import CspPricingModel
from loom.csp.streaming_meter import ComputeMeterReading


class SlComputeInvoice(BaseModel):
    """Verifiable invoice generated for an executed compute session."""
    invoice_id: str = Field(default_factory=lambda: f"sl-inv-{uuid.uuid4().hex[:12]}")
    meter_id: str = Field(..., description="Correlated meter reading ID")
    session_id: str = Field(..., description="Caller session ID")
    provider_node_id: str = Field(..., description="Serving CSP Node ID")
    sl_merchant_account_id: Optional[str] = Field(None, description="Host sL Neobank payout account")
    
    timestamp_epoch: float = Field(default_factory=time.time)
    currency: str = Field("USD", description="Fiat settlement currency")
    
    # Quantitative Volume
    prompt_tokens: int
    completion_tokens: int
    allocated_vram_gb: float
    duration_seconds: float
    
    # Financial Breakdown
    prompt_cost_usd: float
    completion_cost_usd: float
    vram_reservation_cost_usd: float
    gross_total_usd: float
    
    # sL 1.0% Arbitrage Split
    sl_platform_fee_usd: float = Field(..., description="1.0% Spotlight-Local in-network fee")
    csp_host_payout_usd: float = Field(..., description="99.0% net payout to the host's sL card/account")
    
    # Cryptographic Attestation
    hmac_receipt_signature: str = Field(..., description="HMAC-SHA256 signature validating the invoice")


class SlSettlementEngine:
    """
    Financial engine that prices meter readings and produces certified invoices.
    """
    def __init__(self, provider_node_id: str, hmac_secret_key: str = "spotlight_local_sovereignty_key"):
        self.provider_node_id = provider_node_id
        self.hmac_secret_key = hmac_secret_key.encode("utf-8")

    def create_invoice(
        self,
        reading: ComputeMeterReading,
        pricing: CspPricingModel,
        sl_merchant_account_id: Optional[str] = None
    ) -> SlComputeInvoice:
        """Calculates fee breakdown and signs the settlement record."""
        # Cost components
        prompt_cost = round((reading.prompt_tokens / 1000.0) * pricing.price_per_1k_prompt_tokens_usd, 6)
        comp_cost = round((reading.completion_tokens / 1000.0) * pricing.price_per_1k_completion_tokens_usd, 6)
        
        # VRAM reservation cost: (allocated_GB * (duration_sec / 3600)) * rate_per_gb_hr
        vram_cost = round(
            (reading.allocated_vram_gb * (reading.duration_seconds / 3600.0)) * pricing.price_per_vram_gb_hour_usd,
            6
        )
        
        gross_total = round(max(0.000001, prompt_cost + comp_cost + vram_cost), 6)
        
        # The Spotlight-Local 1.0% in-network split
        sl_fee = round(gross_total * pricing.platform_take_rate, 6)
        host_payout = round(gross_total - sl_fee, 6)
        
        # Build HMAC-SHA256 signature payload
        sig_payload = f"{reading.session_id}:{self.provider_node_id}:{gross_total}:{sl_fee}:{reading.start_time_epoch}"
        receipt_sig = hmac.new(self.hmac_secret_key, sig_payload.encode("utf-8"), hashlib.sha256).hexdigest()
        
        return SlComputeInvoice(
            meter_id=reading.meter_id,
            session_id=reading.session_id,
            provider_node_id=self.provider_node_id,
            sl_merchant_account_id=sl_merchant_account_id,
            prompt_tokens=reading.prompt_tokens,
            completion_tokens=reading.completion_tokens,
            allocated_vram_gb=reading.allocated_vram_gb,
            duration_seconds=round(reading.duration_seconds, 3),
            prompt_cost_usd=prompt_cost,
            completion_cost_usd=comp_cost,
            vram_reservation_cost_usd=vram_cost,
            gross_total_usd=gross_total,
            sl_platform_fee_usd=sl_fee,
            csp_host_payout_usd=host_payout,
            hmac_receipt_signature=receipt_sig
        )
