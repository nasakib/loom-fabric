"""
VectorCore ClothOS P2P CaaS Inference Dispatcher.

Enables instant peer-to-peer AI inference across the Spotlight-Local network:
- Checks consumer preloaded float in VectorCoreBankVault
- Routes to the optimal neighborhood CSP provider (or local silicon rig)
- Meters token throughput, TTFT, and Landauer energy expenditure
- Executes atomic settlement: 1.0% protocol treasury, 50% loan split (if active), 49% host payout
- Returns OpenAI-compatible completions with certified SlComputeInvoice
"""

from __future__ import annotations

import asyncio
import time
import uuid
from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel, Field

from loom.caas.bank_vault import VectorCoreBankVault, BankAccount
from loom.csp.manifest import CspNodeManifest, CspPricingModel
from loom.csp.streaming_meter import StreamingComputeMeter, ComputeMeterReading
from loom.csp.sl_settlement import SlSettlementEngine, SlComputeInvoice


class P2PInferenceRequest(BaseModel):
    """Consumer request to purchase a P2P compute slice for inference."""
    consumer_account_id: str
    model: str = "auto"
    messages: List[Dict[str, Any]]
    max_tokens: int = 1024
    temperature: float = 0.7
    consumer_geohash: str = "dn5bpq"
    provider_node_id: Optional[str] = None


class P2PInferenceResponse(BaseModel):
    """Result of an executed P2P inference session with cryptographic settlement."""
    session_id: str
    model_served: str
    provider_node_id: str
    content: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    duration_seconds: float
    tokens_per_second: float
    landauer_energy_microjoules: float
    invoice: Dict[str, Any]
    consumer_remaining_balance_usd: float
    host_payout_usd: float
    platform_fee_usd: float
    loan_repayment_usd: float


class P2PInferenceDispatcher:
    """
    Coordinates P2P inference dispatching, metering, and settlement.
    """
    def __init__(
        self,
        bank_vault: VectorCoreBankVault,
        local_gateway_url: str = "http://127.0.0.1:8002",
        local_node_id: str = "sl-csp-skytech-01",
    ):
        self.bank_vault = bank_vault
        self.gateway_url = local_gateway_url.rstrip("/")
        self.local_node_id = local_node_id
        self.meter = StreamingComputeMeter(node_id=local_node_id)
        self.settlement_engine = SlSettlementEngine(provider_node_id=local_node_id)

    async def execute_p2p_inference(
        self,
        req: P2PInferenceRequest,
        provider_account_id: str,
    ) -> P2PInferenceResponse:
        session_id = f"p2p-inf-{uuid.uuid4().hex[:10]}"

        # 1. Verify consumer balance (require minimum $0.05 float for inference)
        consumer_acc = self.bank_vault.accounts.get(req.consumer_account_id)
        if not consumer_acc:
            raise KeyError(f"Consumer account '{req.consumer_account_id}' not found in VectorCore Bank.")
        if consumer_acc.balance_usd < 0.05:
            raise ValueError(f"Insufficient funds: Balance ${consumer_acc.balance_usd:.4f} < Required $0.05 min float.")

        # 2. Lock escrow ($0.05 upfront max estimate)
        escrow_held = 0.05
        self.bank_vault.lock_compute_escrow(req.consumer_account_id, escrow_held)

        # 3. Start meter reading
        meter_reading = self.meter.start_session(
            session_id=session_id,
            model_id=req.model,
            caller_geohash=req.consumer_geohash,
            allocated_vram_gb=12.0,
        )

        # 4. Dispatch inference to local engine or gateway
        start_time = time.time()
        completion_text = ""
        prompt_tokens = sum(len(str(m.get("content", ""))) // 4 for m in req.messages)
        completion_tokens = 0

        async with httpx.AsyncClient(timeout=120.0) as client:
            res = await client.post(
                f"{self.gateway_url}/v1/chat/completions",
                json={
                    "model": req.model,
                    "messages": req.messages,
                    "max_tokens": req.max_tokens,
                    "temperature": req.temperature,
                },
            )
            if res.status_code != 200:
                # Release escrow on error
                consumer_acc.escrow_locked_usd = round(consumer_acc.escrow_locked_usd - escrow_held, 4)
                consumer_acc.balance_usd = round(consumer_acc.balance_usd + escrow_held, 4)
                raise RuntimeError(f"Upstream inference failed: {res.status_code} - {res.text}")

            res_json = res.json()
            completion_text = res_json["choices"][0]["message"]["content"]
            usage = res_json.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens") or prompt_tokens
            completion_tokens = usage.get("completion_tokens") or max(len(completion_text) // 4, 1)

        # 5. Finalize meter
        self.meter.record_first_token(session_id)
        final_reading = self.meter.finalize_session(
            session_id=session_id,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )

        # 6. Settle invoice
        pricing = CspPricingModel(
            price_per_1k_prompt_tokens_usd=0.0015,
            price_per_1k_completion_tokens_usd=0.0030,
            price_per_vram_gb_hour_usd=0.015,
            platform_take_rate=0.010,
        )
        invoice = self.settlement_engine.generate_invoice(final_reading, pricing)

        # Release the locked escrow before settling actual cost
        consumer_acc.escrow_locked_usd = round(consumer_acc.escrow_locked_usd - escrow_held, 4)
        consumer_acc.balance_usd = round(consumer_acc.balance_usd + escrow_held, 4)

        # Execute final settlement in VectorCore Bank Vault
        settlement_record = self.bank_vault.settle_compute_transaction(
            consumer_account_id=req.consumer_account_id,
            provider_account_id=provider_account_id,
            gross_cost_usd=invoice.gross_total_usd,
            duration_seconds=final_reading.duration_seconds,
            workload_type="ai_inference",
        )

        return P2PInferenceResponse(
            session_id=session_id,
            model_served=final_reading.model_id,
            provider_node_id=self.local_node_id,
            content=completion_text,
            prompt_tokens=final_reading.prompt_tokens,
            completion_tokens=final_reading.completion_tokens,
            total_tokens=final_reading.prompt_tokens + final_reading.completion_tokens,
            duration_seconds=round(final_reading.duration_seconds, 3),
            tokens_per_second=final_reading.tokens_per_second,
            landauer_energy_microjoules=final_reading.landauer_energy_microjoules,
            invoice=invoice.dict(),
            consumer_remaining_balance_usd=settlement_record["consumer_remaining_balance"],
            host_payout_usd=settlement_record["net_provider_payout_usd"],
            platform_fee_usd=settlement_record["sl_platform_fee_usd"],
            loan_repayment_usd=settlement_record["loan_repayment_usd"],
        )
