"""
Stitch MMU: Zero-OOM Mathematical VRAM Layer Allocator.

Part of Pillar 2: STITCH.
Computes deterministic tensor sharding boundaries across heterogeneous GPUs and Host RAM:
- Weight per layer: S_layer = Model GGUF Size / Total Layers
- KV-cache footprint: KV_layer = 2 * n_heads_kv * d_head * C * bytes_per_element
- Primary display GPU margin: VRAM_reserved >= 1200 MB (Windows DWM / WDDM)
- Headless GPU margin: VRAM_reserved >= 300 MB
- Host RAM Spillover when VRAM is saturated
"""

from __future__ import annotations

import logging
import time
from typing import Dict, List, Optional
from loom.config import get_settings
from loom.types import (
    DeviceAllocation,
    HardwareProfile,
    ModelArchitectureProfile,
    ShardingPlan,
)

logger = logging.getLogger("loom.stitch.mmu")


class StitchMMU:
    """Mathematical layer allocation engine calculating deterministic zero-OOM placements."""

    def __init__(self, hardware_profile: Optional[HardwareProfile] = None):
        self.settings = get_settings()
        self.hardware = hardware_profile

    def calculate_plan(
        self,
        profile: ModelArchitectureProfile,
        hardware: Optional[HardwareProfile] = None,
        allow_cpu_spill: bool = True,
    ) -> ShardingPlan:
        """Calculates exact layer boundaries across physical accelerators and host memory."""
        hw = hardware or self.hardware
        if hw is None:
            from loom.stitch.profiler import HardwareProfiler
            profiler = HardwareProfiler()
            state = profiler.probe_cluster_state()
            hw = HardwareProfile(
                node_name=state.node_name,
                cpu_cores_logical=state.cpu_cores_logical,
                total_ram_mb=state.total_ram_mb,
                available_ram_mb=state.available_ram_mb,
                gpus=state.gpus,
            )

        total_layers = profile.total_layers
        context_len = profile.context_length

        # 1. Calculate per-layer weight memory footprint in MB
        weight_per_layer_mb = profile.model_size_mb / max(1, total_layers)

        # 2. Calculate per-layer KV cache memory footprint in MB
        # Formula: 2 * n_heads_kv * head_dim * context_len * bytes_per_element
        kv_bytes_per_layer = (
            2.0 * profile.num_heads_kv * profile.head_dim * context_len * profile.bytes_per_kv_element
        )
        kv_per_layer_mb = kv_bytes_per_layer / (1024.0 * 1024.0)

        total_layer_cost_mb = weight_per_layer_mb + kv_per_layer_mb

        remaining_layers = total_layers
        current_layer_idx = 0
        allocations: List[DeviceAllocation] = []

        # 3. Allocate across physical GPUs
        for gpu in hw.gpus:
            if remaining_layers <= 0:
                break

            # Determine reserved headroom for OS display compositing / WDDM
            reserved_mb = (
                self.settings.memory.primary_display_reserved_mb
                if gpu.is_primary_display or gpu.index == 0
                else self.settings.memory.secondary_headless_reserved_mb
            )

            # Usable VRAM strictly protected by margin
            usable_vram_mb = max(0.0, gpu.free_vram_mb - reserved_mb)

            # Calculate how many layers can physically fit in this GPU
            layers_fit = int(usable_vram_mb // total_layer_cost_mb)
            layers_assigned = min(remaining_layers, layers_fit)

            if layers_assigned > 0:
                weights_mb = round(layers_assigned * weight_per_layer_mb, 2)
                kv_mb = round(layers_assigned * kv_per_layer_mb, 2)
                total_mb = weights_mb + kv_mb
                headroom_mb = round(gpu.free_vram_mb - total_mb, 2)

                allocations.append(
                    DeviceAllocation(
                        device_id=f"gpu_{gpu.index}",
                        device_name=gpu.name,
                        device_backend=gpu.backend.value.upper(),
                        layer_start_idx=current_layer_idx,
                        layer_end_idx=current_layer_idx + layers_assigned - 1,
                        layer_count=layers_assigned,
                        weights_memory_mb=weights_mb,
                        kv_memory_mb=kv_mb,
                        total_memory_mb=total_mb,
                        memory_headroom_mb=headroom_mb,
                    )
                )

                current_layer_idx += layers_assigned
                remaining_layers -= layers_assigned

        # 4. Handle CPU Host RAM Spilling
        spilled_to_cpu = False
        spilled_count = 0

        if remaining_layers > 0 and allow_cpu_spill:
            spilled_to_cpu = True
            spilled_count = remaining_layers
            weights_mb = round(spilled_count * weight_per_layer_mb, 2)
            kv_mb = round(spilled_count * kv_per_layer_mb, 2)
            total_mb = weights_mb + kv_mb
            headroom_mb = round(hw.available_ram_mb - total_mb, 2)

            allocations.append(
                DeviceAllocation(
                    device_id="cpu_host",
                    device_name="Host System RAM",
                    device_backend="CPU",
                    layer_start_idx=current_layer_idx,
                    layer_end_idx=current_layer_idx + spilled_count - 1,
                    layer_count=spilled_count,
                    weights_memory_mb=weights_mb,
                    kv_memory_mb=kv_mb,
                    total_memory_mb=total_mb,
                    memory_headroom_mb=headroom_mb,
                )
            )

        return ShardingPlan(
            model_name=profile.name,
            total_layers=total_layers,
            context_length=context_len,
            allocations=allocations,
            spilled_to_cpu=spilled_to_cpu,
            spilled_layer_count=spilled_count,
            calculated_at=time.time(),
        )
