"""
Test Suite: Stitch MMU Mathematical Layer & KV-Cache Allocator.
"""

from loom.stitch.mmu import StitchMMU
from loom.types import (
    AcceleratorVendor,
    ComputeBackend,
    GPUSpec,
    HardwareProfile,
    ModelArchitectureProfile,
)


def test_mmu_layer_allocation_rtx3060_envelope():
    """Verify deterministic layer allocation on RTX 3060 12GB envelope with 1200MB WDDM reserve."""
    # Synthetic RTX 3060 hardware profile
    rtx_3060 = GPUSpec(
        index=0,
        name="NVIDIA GeForce RTX 3060",
        vendor=AcceleratorVendor.NVIDIA,
        backend=ComputeBackend.CUDA,
        total_vram_mb=12288.0,
        free_vram_mb=11500.0,
        is_primary_display=True,
    )
    hw = HardwareProfile(
        node_name="test-worker",
        cpu_cores_logical=16,
        total_ram_mb=40960.0,
        available_ram_mb=25000.0,
        gpus=[rtx_3060],
    )

    mmu = StitchMMU(hardware_profile=hw)

    # 14B model: ~9000 MB weights, 48 layers, context 8192
    profile_14b = ModelArchitectureProfile(
        name="deepseek-r1:14b",
        total_layers=48,
        hidden_dim=5120,
        num_heads=40,
        num_heads_kv=8,
        head_dim=128,
        model_size_mb=9000.0,
        quant_type="Q4_K_M",
        context_length=8192,
        bytes_per_kv_element=2.0,
    )

    plan = mmu.calculate_plan(profile_14b, hardware=hw, allow_cpu_spill=True)

    # Invariants:
    # 1. Total layers must equal 48
    assert sum(a.layer_count for a in plan.allocations) == 48

    # 2. Total allocated memory on GPU 0 must NOT exceed usable VRAM (11500 - 1200 = 10300 MB)
    gpu_alloc = next(a for a in plan.allocations if a.device_id == "gpu_0")
    assert gpu_alloc.total_memory_mb <= (11500.0 - 1200.0)
    assert gpu_alloc.memory_headroom_mb >= 1200.0

    # 3. CLI arguments string must be formatted correctly
    cli_str = plan.render_cli_argument_string()
    assert cli_str.startswith("-ngl ")


def test_mmu_spillover_to_cpu_when_vram_exceeded():
    """Verify that when a model exceeds usable GPU VRAM, remainder spills to CPU."""
    # Constrained GPU: only 4000 MB free, 1200 MB reserved -> 2800 MB usable
    small_gpu = GPUSpec(
        index=0,
        name="Constrained GPU",
        vendor=AcceleratorVendor.NVIDIA,
        backend=ComputeBackend.CUDA,
        total_vram_mb=4096.0,
        free_vram_mb=4000.0,
        is_primary_display=True,
    )
    hw = HardwareProfile(
        node_name="test-worker",
        cpu_cores_logical=16,
        total_ram_mb=40960.0,
        available_ram_mb=25000.0,
        gpus=[small_gpu],
    )

    mmu = StitchMMU(hardware_profile=hw)

    # 32B model: ~19800 MB weights, 64 layers
    profile_32b = ModelArchitectureProfile(
        name="qwen2.5:32b",
        total_layers=64,
        hidden_dim=5120,
        num_heads=40,
        num_heads_kv=8,
        head_dim=128,
        model_size_mb=19800.0,
        quant_type="Q4_K_M",
        context_length=8192,
        bytes_per_kv_element=2.0,
    )

    plan = mmu.calculate_plan(profile_32b, hardware=hw, allow_cpu_spill=True)

    # Must spill to CPU
    assert plan.spilled_to_cpu is True
    assert plan.spilled_layer_count > 0

    # Total layers across GPU and CPU must equal 64
    total_assigned = sum(a.layer_count for a in plan.allocations)
    assert total_assigned == 64
