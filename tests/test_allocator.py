"""
Unit tests for Loom Fabric Zero-OOM Layer Allocator.
"""

import pytest
from loom.stitch.allocator import LayerAllocator, ModelArchitectureProfile, LayerShardingPlan
from loom.stitch.profiler import ClusterHardwareState, GPUDeviceInfo, HostSystemInfo
from loom.models.registry import ModelRegistry


@pytest.fixture
def mock_hardware_state() -> ClusterHardwareState:
    """Fixture mimicking SkyTech dual-GPU workstation."""
    return ClusterHardwareState(
        node_name="skyTech",
        host=HostSystemInfo(
            hostname="skyTech",
            os_name="Windows 11",
            total_ram_mb=40960,
            available_ram_mb=28000,
            cpu_cores_physical=8,
            cpu_cores_logical=16,
            cpu_model="AMD Ryzen 7",
        ),
        gpus=[
            GPUDeviceInfo(
                index=0,
                name="NVIDIA GeForce RTX 3060",
                vendor="NVIDIA",
                backend="CUDA",
                total_vram_mb=12288,
                free_vram_mb=10500,
                used_vram_mb=1788,
                compute_capability="8.6",
                driver_version="551.86",
                is_primary_display=True,
            ),
            GPUDeviceInfo(
                index=1,
                name="Radeon RX 580 2048SP",
                vendor="AMD",
                backend="Vulkan",
                total_vram_mb=8192,
                free_vram_mb=7200,
                used_vram_mb=992,
                compute_capability=None,
                driver_version="31.0.21912.14",
                is_primary_display=False,
            ),
        ],
    )


def test_qwen_32b_sharding(mock_hardware_state):
    """Verifies that 32B model allocates layers across RTX 3060, RX 580, and spills to RAM safely."""
    allocator = LayerAllocator(mock_hardware_state)
    preset = ModelRegistry.get_model("qwen2.5:32b")
    assert preset is not None

    profile = preset.to_architecture_profile(context_length=8192)
    plan = allocator.calculate_plan(profile, allow_cpu_spill=True)

    assert plan.total_model_layers == 64
    assert len(plan.allocations) == 3  # RTX 3060, RX 580, Host CPU

    # First tier must be RTX 3060
    assert "RTX 3060" in plan.allocations[0].device_name
    assert plan.allocations[0].layer_count > 20

    # Second tier must be RX 580
    assert "RX 580" in plan.allocations[1].device_name
    assert plan.allocations[1].layer_count > 15

    # Check llama-server flags generated
    cli_flags = plan.render_cli_argument_string()
    assert "-ngl" in cli_flags
    assert "--tensor-split" in cli_flags


def test_deepseek_14b_sharding(mock_hardware_state):
    """Verifies that 14B model fits 100% in dual-GPU VRAM without CPU spill."""
    allocator = LayerAllocator(mock_hardware_state)
    preset = ModelRegistry.get_model("deepseek-r1:14b")
    assert preset is not None

    profile = preset.to_architecture_profile(context_length=8192)
    plan = allocator.calculate_plan(profile, allow_cpu_spill=False)

    assert plan.total_model_layers == 48
    assert plan.spilled_to_cpu is False
    assert len(plan.allocations) == 2  # Handled entirely by RTX 3060 + RX 580
