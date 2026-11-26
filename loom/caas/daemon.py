"""
VectorCore ClothOS CaaS (Compute-as-a-Service) Host Daemon.

Autonomous agent running on provider machines (Windows, macOS Apple Silicon, Linux).
Discovers local accelerators (NVIDIA CUDA, AMD ROCm/OpenCL, Apple Silicon Metal),
generates signed hardware manifests, publishes capacity to the Spotlight-Local mesh,
and fulfills compute workloads (AI inference, cloud gaming, video encoding).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import platform
import subprocess
import sys
import time
import uuid
from typing import Any, Dict, List, Optional

from loom.csp.manifest import CspNodeManifest, GpuDeviceManifest, CspPricingModel
from loom.csp.streaming_meter import StreamingComputeMeter
from loom.caas.p2p_auction import AskOrder

logger = logging.getLogger("loom.caas.daemon")


class SiliconDetector:
    """Probes local platform silicon across NVIDIA, Apple Silicon, AMD, and Intel."""

    @classmethod
    def probe_hardware(cls) -> Dict[str, Any]:
        os_type = platform.system()
        gpus: List[GpuDeviceManifest] = []
        host_ram_gb = 16.0
        vcpu_count = 8
        chip_brand = platform.processor() or "Generic Processor"

        # Host RAM & CPU
        try:
            import psutil
            host_ram_gb = round(psutil.virtual_memory().total / (1024**3), 2)
            vcpu_count = psutil.cpu_count(logical=True) or 8
        except Exception:
            pass

        # 1. macOS Apple Silicon Detection
        if os_type == "Darwin":
            try:
                chip_brand = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"]).decode().strip()
            except Exception:
                chip_brand = "Apple Silicon"

            # Check for Apple Silicon GPU via system_profiler or unified memory
            if "Apple" in chip_brand or platform.machine() == "arm64":
                # Apple unified memory allows full system RAM to be used as VRAM
                allocatable_vram = round(host_ram_gb * 0.75, 1)  # standard macOS Metal limit ~75%
                gpus.append(
                    GpuDeviceManifest(
                        name=f"{chip_brand} Metal Core",
                        backend="metal",
                        vram_total_gb=host_ram_gb,
                        vram_available_gb=allocatable_vram,
                        tflops_fp16=26.0 if "Max" in chip_brand or "Ultra" in chip_brand else 13.0,
                        is_active_seeder=True,
                    )
                )

        # 2. NVIDIA GPU Detection (nvidia-smi)
        nvidia_found = False
        try:
            res = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total,memory.free", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=3,
            )
            if res.returncode == 0 and res.stdout.strip():
                for line in res.stdout.strip().split("\n"):
                    parts = [p.strip() for p in line.split(",")]
                    if len(parts) >= 3:
                        name = parts[0]
                        tot_mb = float(parts[1])
                        free_mb = float(parts[2])
                        gpus.append(
                            GpuDeviceManifest(
                                name=name,
                                backend="cuda",
                                vram_total_gb=round(tot_mb / 1024.0, 1),
                                vram_available_gb=round(free_mb / 1024.0, 1),
                                tflops_fp16=12.74,  # baseline estimation
                                is_active_seeder=True,
                            )
                        )
                        nvidia_found = True
        except Exception:
            pass

        # 3. AMD / Fallback GPU Detection on Windows / Linux
        if not gpus and os_type == "Windows":
            # Direct probe for AMD / Intel via PowerShell Get-CimInstance
            try:
                cmd = ["powershell", "-NoProfile", "-Command", "Get-CimInstance Win32_VideoController | Select-Object -Property Name, AdapterRAM | ConvertTo-Json"]
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                if res.returncode == 0 and res.stdout.strip():
                    data = json.loads(res.stdout)
                    if isinstance(data, dict):
                        data = [data]
                    for item in data:
                        gpu_name = item.get("Name", "Unknown GPU")
                        ram_bytes = item.get("AdapterRAM", 0) or 0
                        ram_gb = round(ram_bytes / (1024**3), 1) if ram_bytes else 4.0
                        backend = "opencl" if "AMD" in gpu_name or "Radeon" in gpu_name else "directml"
                        gpus.append(
                            GpuDeviceManifest(
                                name=gpu_name,
                                backend=backend,
                                vram_total_gb=max(ram_gb, 4.0),
                                vram_available_gb=max(ram_gb * 0.9, 3.6),
                                tflops_fp16=6.17,
                                is_active_seeder=True,
                            )
                        )
            except Exception:
                pass

        # Fallback if no dedicated accelerator was detected: CPU Compute Node
        if not gpus:
            gpus.append(
                GpuDeviceManifest(
                    name=f"{chip_brand} (AVX2/AVX-512 CPU Compute)",
                    backend="cpu",
                    vram_total_gb=round(host_ram_gb * 0.5, 1),
                    vram_available_gb=round(host_ram_gb * 0.4, 1),
                    tflops_fp16=2.5,
                    is_active_seeder=True,
                )
            )

        total_vram = round(sum(g.vram_total_gb for g in gpus), 1)
        return {
            "gpus": gpus,
            "aggregate_vram_gb": total_vram,
            "host_ram_gb": host_ram_gb,
            "vcpu_count": vcpu_count,
            "chip_brand": chip_brand,
            "os_name": f"{os_type} {platform.release()}",
        }


class CaaSHostDaemon:
    """
    Autonomous node daemon connecting a provider's rig to the VectorCore Compute Mesh.
    """
    def __init__(
        self,
        node_name: str,
        geohash: str = "dn5bpq",
        neighborhood_tag: str = "Inman Park / O4W",
        city: str = "Atlanta",
        is_solar_powered: bool = False,
        solar_discount_pct: float = 0.0,
        owner_avatar_totem_id: str = "NFC-TOTEM-DEFAULT",
        sl_merchant_account_id: str = "acct_sl_default",
        gateway_url: str = "http://127.0.0.1:8087",
    ):
        self.node_name = node_name
        self.geohash = geohash
        self.neighborhood_tag = neighborhood_tag
        self.city = city
        self.is_solar_powered = is_solar_powered
        self.solar_discount_pct = solar_discount_pct
        self.owner_avatar_totem_id = owner_avatar_totem_id
        self.sl_merchant_account_id = sl_merchant_account_id
        self.gateway_url = gateway_url

        # Hardware profiling
        hw = SiliconDetector.probe_hardware()
        self.manifest = CspNodeManifest(
            node_name=self.node_name,
            provider_address=platform.node(),
            geohash=self.geohash,
            neighborhood_tag=self.neighborhood_tag,
            city=self.city,
            vcpu_count=hw["vcpu_count"],
            host_ram_gb=hw["host_ram_gb"],
            gpus=hw["gpus"],
            aggregate_vram_gb=hw["aggregate_vram_gb"],
            landauer_rating_pj_per_mac=1.2,
            is_solar_powered=self.is_solar_powered,
            owner_avatar_totem_id=self.owner_avatar_totem_id,
            sl_merchant_account_id=self.sl_merchant_account_id,
            pricing=CspPricingModel(
                price_per_1k_prompt_tokens_usd=0.0015,
                price_per_1k_completion_tokens_usd=0.0030,
                price_per_vram_gb_hour_usd=0.015,
                platform_take_rate=0.010,
            ),
        )

        self.meter = StreamingComputeMeter(node_id=self.manifest.node_id)
        self.is_running = False

    def generate_ask_order(self) -> AskOrder:
        """Publishes active capacity to the Continuous Double Auction."""
        supported = ["ai_inference", "video_transcode"]
        if self.manifest.aggregate_vram_gb >= 8.0:
            supported.append("cloud_gaming_60fps")
        if self.manifest.aggregate_vram_gb >= 16.0:
            supported.append("cloud_gaming_120fps")
            supported.append("3d_render")

        hourly_rate = round(self.manifest.aggregate_vram_gb * self.manifest.pricing.price_per_vram_gb_hour_usd * 2.0, 4)

        return AskOrder(
            provider_node_id=self.manifest.node_id,
            supported_workloads=supported,
            min_rate_usd_per_hr=max(hourly_rate, 0.25),
            available_vram_gb=self.manifest.aggregate_vram_gb,
            reported_latency_ms=0.5,
            provider_geohash=self.manifest.geohash,
            is_solar_powered=self.is_solar_powered,
            solar_discount_pct=self.solar_discount_pct,
        )

    def start_heartbeat_loop(self, interval_seconds: int = 15):
        """Asynchronously advertises node presence to mesh."""
        self.is_running = True
        logger.info(
            f"Host Daemon [{self.node_name}] active. Geohash: {self.geohash}. "
            f"Silicon: {len(self.manifest.gpus)} accelerators, {self.manifest.aggregate_vram_gb} GB VRAM."
        )


def main():
    parser = argparse.ArgumentParser(description="ClothOS CaaS Host Daemon")
    parser.add_argument("--name", default=f"Host-{platform.node()}", help="Host display name")
    parser.add_argument("--geohash", default="dn5bpq", help="6-char geohash location anchor")
    parser.add_argument("--neighborhood", default="Inman Park / O4W", help="Neighborhood tag")
    parser.add_argument("--solar", action="store_true", help="Flag if running on solar battery power")
    parser.add_argument("--solar-discount", type=float, default=0.15, help="Solar discount percentage")
    args = parser.parse_args()

    daemon = CaaSHostDaemon(
        node_name=args.name,
        geohash=args.geohash,
        neighborhood_tag=args.neighborhood,
        is_solar_powered=args.solar,
        solar_discount_pct=args.solar_discount if args.solar else 0.0,
    )

    print("=" * 68)
    print("  VectorCore ClothOS Compute Service Provider (sL-CSP) Daemon")
    print("=" * 68)
    print(f"Node ID:          {daemon.manifest.node_id}")
    print(f"Node Name:        {daemon.manifest.node_name}")
    print(f"Geohash Anchor:   {daemon.manifest.geohash} ({daemon.manifest.neighborhood_tag})")
    print(f"Pooled VRAM:      {daemon.manifest.aggregate_vram_gb} GB")
    print(f"Accelerators:     {', '.join(g.name + ' (' + g.backend + ')' for g in daemon.manifest.gpus)}")
    print(f"Solar Powered:    {daemon.manifest.is_solar_powered} (Discount: {daemon.solar_discount_pct * 100:.0f}%)")
    print(f"Hardware Hash:    {daemon.manifest.compute_signature_hash()[:20]}...")
    print("=" * 68)
    ask = daemon.generate_ask_order()
    print(f"Active Ask Order: {ask.ask_id} -> Min Rate: ${ask.effective_min_rate_usd_per_hr:.4f}/hr for {ask.supported_workloads}")
    print("Ready to serve compute sessions.")


if __name__ == "__main__":
    main()
