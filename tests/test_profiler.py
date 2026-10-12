"""
Unit tests for Loom Fabric Hardware Profiling Engine.
"""

from loom.stitch.profiler import HardwareProfiler, ClusterHardwareState


def test_hardware_profiler_probing():
    """Verifies that HardwareProfiler probes CPU, RAM, and GPUs without throwing exceptions."""
    profiler = HardwareProfiler(node_name="testNode")
    state = profiler.probe_cluster_state()

    assert isinstance(state, ClusterHardwareState)
    assert state.host.total_ram_mb > 1024
    assert state.host.cpu_cores_logical >= 1
    assert isinstance(state.gpus, list)

    # Export Ray resources dictionary
    ray_resources = profiler.generate_ray_resources(state)
    assert isinstance(ray_resources, dict)
    assert "CPU" in ray_resources
    assert "HOST_RAM_MB" in ray_resources
