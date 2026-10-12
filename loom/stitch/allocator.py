"""Mathematical Layer Sharding and VRAM Allocation Engine.

Calculates zero-OOM layer distribution plans across heterogeneous accelerators
and host memory using exact transformer tensor dimensions and KV cache budgets.

Architecture Note (Rust Migration Target):
    This module maps to `loom_stitch::allocator` in Rust:
    - Pure, deterministic, zero-allocation mathematical functions.
    - `ModelArchitectureProfile` -> `pub struct ModelArchitectureProfile`
    - `LayerShardingPlan` -> `pub struct LayerShardingPlan`
    - Exported CLI flags generated via formatting traits (`impl Display for LayerShardingPlan`).
"""

from __future__ import annotations

import logging
import math
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from .profiler import GPUDeviceInfo, ClusterHardwareState
from ..config import settings

logger = logging.getLogger("loom.stitch.allocator")


class ModelArchitectureProfile(BaseModel):
    """Transformer structural dimensions required for analytical memory budgeting."""

    name: str = Field(..., description="Canonical model identifier.")
    total_layers: int = Field(..., ge=1, description="Total transformer decoder layer count.")
    hidden_dim: int = Field(..., ge=512, description="Hidden state dimension (d_model).")
    num_heads: int = Field(..., ge=1, description="Number of query attention heads.")
    num_heads_kv: int = Field(..., ge=1, description="Number of key/value attention heads (GQA/MQA).")
    head_dim: Optional[int] = Field(default=None, description="Head dimension (defaults to hidden_dim // num_heads).")
    vocab_size: int = Field(default=128256, description="Tokenizer vocabulary size.")
    model_size_mb: float = Field(..., ge=100.0, description="Total physical GGUF weight file size in megabytes.")
    quant_type: str = Field(default="Q4_K_M", description="Weight quantization descriptor.")
    context_length: int = Field(default=32768, ge=512, description="Target operational context window in tokens.")

    def get_head_dimension(self) -> int:
        """Returns the individual attention head dimension."""
        if self.head_dim is not None and self.head_dim > 0:
            return self.head_dim
        return self.hidden_dim // self.num_heads


class ShardAllocation(BaseModel):
    """Assigned layer slice and memory consumption for a specific compute device."""

    device_name: str = Field(..., description="Target device name (e.g., 'RTX 3060', 'RX 580', 'CPU').")
    device_backend: str = Field(..., description="Execution backend: 'CUDA', 'Vulkan', or 'CPU'.")
    layer_start_idx: int = Field(..., description="First layer index mapped to this device (inclusive).")
    layer_end_idx: int = Field(..., description="Last layer index mapped to this device (inclusive).")
    layer_count: int = Field(..., ge=0, description="Number of layers assigned to this slice.")
    weight_memory_mb: float = Field(..., description="VRAM/RAM allocated for weight tensors in MB.")
    kv_cache_memory_mb: float = Field(..., description="VRAM/RAM allocated for key-value cache in MB.")
    total_memory_mb: float = Field(..., description="Combined memory footprint in MB.")


class LayerShardingPlan(BaseModel):
    """Complete, verified cross-hardware sharding plan for model deployment."""

    model_name: str = Field(..., description="Model identifier.")
    total_model_layers: int = Field(..., description="Total layers in the architecture.")
    context_tokens: int = Field(..., description="Allocated context length.")
    allocations: List[ShardAllocation] = Field(default_factory=list, description="Per-device layer assignments.")
    spilled_to_cpu: bool = Field(default=False, description="Whether layers were forced to spill into host CPU RAM.")
    spilled_layer_count: int = Field(default=0, description="Number of layers executing on CPU.")
    throughput_warning: Optional[str] = Field(
        default=None,
        description="User-facing warning message detailing expected token/sec degradation if spilled.",
    )
    llama_server_flags: Dict[str, str] = Field(
        default_factory=dict,
        description="Exact CLI arguments to pass to the native llama-server binary.",
    )

    def render_cli_argument_string(self) -> str:
        """Constructs the CLI flag string for native llama-server launching."""
        return " ".join(f"{k} {v}" if v else k for k, v in self.llama_server_flags.items())


class LayerAllocator:
    """Calculates zero-OOM layer partitions across asymmetric physical accelerators."""

    def __init__(self, hardware_state: ClusterHardwareState):
        """Initializes the allocator with a probed hardware topology.

        Args:
            hardware_state: The physical topology of the local worker node.
        """
        self.hardware = hardware_state

    def compute_layer_memory_costs(self, model: ModelArchitectureProfile) -> tuple[float, float]:
        """Calculates per-layer weight and KV cache footprint in megabytes.

        Mathematical Formulation:
            S_layer = Model GGUF Size (MB) / Total Model Layers
            KV_layer = (2 * n_heads_kv * d_head * Context * bytes_per_elem) / (1024 * 1024)

        Args:
            model: Transformer structural dimensions.

        Returns:
            Tuple of (weight_mb_per_layer, kv_mb_per_layer).
        """
        weight_mb_per_layer = model.model_size_mb / float(model.total_layers)

        d_head = model.get_head_dimension()
        bytes_per_elem = settings.memory.kv_cache_quantization_bytes  # FP16 = 2 bytes

        # KV cache per layer in bytes = 2 (keys + values) * n_heads_kv * d_head * C * bytes_per_elem
        kv_bytes_per_layer = 2.0 * float(model.num_heads_kv) * float(d_head) * float(model.context_length) * float(bytes_per_elem)
        kv_mb_per_layer = kv_bytes_per_layer / (1024.0 * 1024.0)

        return weight_mb_per_layer, kv_mb_per_layer

    def calculate_plan(
        self,
        model: ModelArchitectureProfile,
        allow_cpu_spill: bool = True,
    ) -> LayerShardingPlan:
        """Computes a multi-tier sharding plan prioritizing pure GPU execution.

        Allocation Priority Hierarchy:
            Tier 1: Primary NVIDIA GPU (RTX 3060 CUDA)
            Tier 2: Secondary AMD GPU (RX 580 Vulkan / DirectML)
            Tier 3: Host CPU RAM (only if allow_cpu_spill=True)

        Args:
            model: Target model architecture parameters.
            allow_cpu_spill: Whether to allow unassigned layers to execute on host CPU.

        Returns:
            Complete LayerShardingPlan with exact bounds and llama-server flags.

        Raises:
            MemoryError: If VRAM is insufficient and allow_cpu_spill is False.
        """
        weight_cost, kv_cost = self.compute_layer_memory_costs(model)
        total_layer_cost_mb = weight_cost + kv_cost

        remaining_layers = model.total_layers
        current_layer_idx = 0
        allocations: List[ShardAllocation] = []

        # Sort GPUs: prioritize NVIDIA CUDA primary display first, then AMD secondary
        sorted_gpus = sorted(self.hardware.gpus, key=lambda g: 0 if g.vendor == "NVIDIA" else 1)

        total_gpu_layers_assigned = 0

        for gpu in sorted_gpus:
            if remaining_layers <= 0:
                break

            # Deduct OS and driver reservation margins
            reserved_mb = (
                settings.memory.primary_display_reserved_mb
                if gpu.is_primary_display
                else settings.memory.secondary_headless_reserved_mb
            )

            usable_vram_mb = max(0.0, float(gpu.free_vram_mb - reserved_mb))

            # How many layers can fit strictly within usable VRAM:
            # N = floor( Usable_VRAM / (S_layer + KV_layer) )
            max_layers_fit = int(math.floor(usable_vram_mb / total_layer_cost_mb))
            layers_to_assign = min(remaining_layers, max(0, max_layers_fit))

            if layers_to_assign > 0:
                layer_start = current_layer_idx
                layer_end = current_layer_idx + layers_to_assign - 1
                alloc_weight = float(layers_to_assign) * weight_cost
                alloc_kv = float(layers_to_assign) * kv_cost

                allocations.append(
                    ShardAllocation(
                        device_name=gpu.name,
                        device_backend=gpu.backend,
                        layer_start_idx=layer_start,
                        layer_end_idx=layer_end,
                        layer_count=layers_to_assign,
                        weight_memory_mb=round(alloc_weight, 2),
                        kv_cache_memory_mb=round(alloc_kv, 2),
                        total_memory_mb=round(alloc_weight + alloc_kv, 2),
                    )
                )

                remaining_layers -= layers_to_assign
                current_layer_idx += layers_to_assign
                total_gpu_layers_assigned += layers_to_assign

        spilled = False
        spilled_count = 0
        warning = None

        if remaining_layers > 0:
            if not allow_cpu_spill:
                raise MemoryError(
                    f"Model '{model.name}' requires {model.total_layers} layers ({round(model.model_size_mb, 1)} MB), "
                    f"but physical GPU VRAM could only accommodate {total_gpu_layers_assigned} layers. "
                    f"CPU spilling is disabled."
                )

            # Check if host system RAM can hold the remaining layers
            usable_host_ram_mb = max(0.0, float(self.hardware.host.available_ram_mb - settings.memory.system_ram_reserve_mb))
            required_host_mb = float(remaining_layers) * total_layer_cost_mb

            if required_host_mb > usable_host_ram_mb:
                raise MemoryError(
                    f"Out of System RAM: {remaining_layers} remaining layers require {round(required_host_mb, 1)} MB, "
                    f"but only {round(usable_host_ram_mb, 1)} MB of usable host RAM remains."
                )

            spilled = True
            spilled_count = remaining_layers
            layer_start = current_layer_idx
            layer_end = current_layer_idx + remaining_layers - 1
            alloc_weight = float(remaining_layers) * weight_cost
            alloc_kv = float(remaining_layers) * kv_cost

            allocations.append(
                ShardAllocation(
                    device_name="Host System Memory (CPU)",
                    device_backend="CPU",
                    layer_start_idx=layer_start,
                    layer_end_idx=layer_end,
                    layer_count=remaining_layers,
                    weight_memory_mb=round(alloc_weight, 2),
                    kv_cache_memory_mb=round(alloc_kv, 2),
                    total_memory_mb=round(alloc_weight + alloc_kv, 2),
                )
            )

            warning = (
                f"⚠️ VRAM Capacity Exceeded: {spilled_count}/{model.total_layers} layers spilled to CPU RAM. "
                f"Generation throughput will drop from ~45 tok/s to ~8-15 tok/s due to host memory bus latency."
            )

        # Generate exact llama-server execution flags
        # -ngl specifies the total number of offloaded GPU layers
        flags: Dict[str, str] = {
            "-ngl": str(total_gpu_layers_assigned),
            "-c": str(model.context_length),
            "--host": "0.0.0.0",
        }

        # Multi-GPU tensor-split string if multiple GPUs were allocated
        gpu_allocs = [a for a in allocations if a.device_backend != "CPU"]
        if len(gpu_allocs) > 1:
            total_gpu_mb = sum(a.total_memory_mb for a in gpu_allocs)
            split_ratios = [f"{round(a.total_memory_mb / total_gpu_mb, 2):.2f}" for a in gpu_allocs]
            flags["--tensor-split"] = ",".join(split_ratios)

        return LayerShardingPlan(
            model_name=model.name,
            total_model_layers=model.total_layers,
            context_tokens=model.context_length,
            allocations=allocations,
            spilled_to_cpu=spilled,
            spilled_layer_count=spilled_count,
            throughput_warning=warning,
            llama_server_flags=flags,
        )
