"""
Spotlight-Local Compute Service Provider (sL-CSP) Node Manifest.

Defines the hardware attestation, geohash spatial coordinates, and dynamic
pricing models for local households, gamers, and small businesses acting
as compute nodes within the Spotlight-Local network under VectorCore Holdings.
"""

from __future__ import annotations

import hashlib
import time
import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class GpuDeviceManifest(BaseModel):
    """Specification of an active GPU or accelerator in the node."""
    name: str = Field(..., description="Device name (e.g. NVIDIA GeForce RTX 3060)")
    backend: str = Field(..., description="Compute backend (cuda, rocm, opencl, vulkan, metal)")
    vram_total_gb: float = Field(..., description="Total physical VRAM in gigabytes")
    vram_available_gb: float = Field(..., description="Currently free/allocatable VRAM in gigabytes")
    tflops_fp16: float = Field(..., description="Peak half-precision theoretical compute throughput")
    is_active_seeder: bool = Field(True, description="Whether this accelerator accepts external workloads")


class CspPricingModel(BaseModel):
    """Per-unit compute pricing in real USD ($) for Spotlight-Local consumers."""
    price_per_1k_prompt_tokens_usd: float = Field(
        0.0015,
        description="Cost per 1,000 input/prompt tokens ($0.0015 default)"
    )
    price_per_1k_completion_tokens_usd: float = Field(
        0.0030,
        description="Cost per 1,000 generated completion tokens ($0.0030 default)"
    )
    price_per_vram_gb_hour_usd: float = Field(
        0.015,
        description="Standby / KV cache reservation cost per GB-hour ($0.015 default)"
    )
    currency: str = Field("USD", description="Settlement currency on Spotlight-Local surface")
    platform_take_rate: float = Field(
        0.010,
        description="Spotlight-Local in-network platform fee (1.0% flat)"
    )


class CspNodeManifest(BaseModel):
    """
    Complete cryptographic attestation and service manifest for a local
    Spotlight-Local Compute Service Provider (sL-CSP).
    """
    node_id: str = Field(default_factory=lambda: f"sl-csp-{uuid.uuid4().hex[:12]}")
    node_name: str = Field(..., description="Friendly name (e.g. skyTech-Rig-01)")
    provider_address: str = Field(..., description="Host IP / Tailscale IP / hostname")
    port: int = Field(8002, description="Loom Fabric gateway port")
    
    # Spatial & Neighborhood Coordinates
    geohash: str = Field(..., description="Geohash coordinate (e.g. dn5bpq for Atlanta Downtown)")
    neighborhood_tag: str = Field("Inman Park / Old Fourth Ward", description="Human-readable neighborhood")
    city: str = Field("Atlanta", description="Primary metropolitan anchor")
    country: str = Field("USA", description="ISO country code")
    
    # Hardware Envelope
    vcpu_count: int = Field(..., description="Available physical CPU threads")
    host_ram_gb: float = Field(..., description="Total system RAM in gigabytes")
    gpus: List[GpuDeviceManifest] = Field(default_factory=list)
    aggregate_vram_gb: float = Field(..., description="Total poolable VRAM across all accelerators")
    
    # Energetics & Thermodynamics
    landauer_rating_pj_per_mac: float = Field(
        1.2,
        description="Thermodynamic efficiency rating in picojoules per Multiply-Accumulate"
    )
    is_solar_powered: bool = Field(False, description="Whether node operates on residential solar/battery")
    off_peak_tariff_active: bool = Field(False, description="Whether lower night-time electricity tariff applies")
    
    # Supported Local Models
    served_models: List[str] = Field(
        default_factory=lambda: [
            "auto",
            "loom-sovereign-fast:latest",
            "qwen2.5:32b",
            "deepseek-r1:14b",
            "qwen2.5:7b"
        ]
    )
    
    # Economics
    pricing: CspPricingModel = Field(default_factory=CspPricingModel)
    
    # Totem & Tactile Identity
    owner_avatar_totem_id: Optional[str] = Field(
        None,
        description="NFC UID of the owner's 3D Avatar Figurine / secure carryable element"
    )
    sl_merchant_account_id: Optional[str] = Field(
        None,
        description="Spotlight-Local merchant / Stripe Connect account ID for instant payout"
    )
    created_at_epoch: float = Field(default_factory=time.time)

    def compute_signature_hash(self, secret_salt: str = "vectorcore_sovereignty") -> str:
        """Generates a deterministic verification hash of the node's attestation."""
        payload = f"{self.node_id}:{self.geohash}:{self.aggregate_vram_gb}:{self.landauer_rating_pj_per_mac}:{secret_salt}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
