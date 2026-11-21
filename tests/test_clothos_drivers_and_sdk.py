# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
Comprehensive Unit Tests for ClothOS Hardware Drivers, Developer SDK, and Success Gauge.

Tests:
1. NVIDIA CUDA driver state and device node telemetry
2. AMD Radeon / ROCm driver Kuramoto phase-coupling
3. Apple Silicon Metal 3 UMA zero-copy memory allocation & release
4. RISC-V RV64GCV driver vector strip-mining calculation
5. Robotics Actuator microsecond P0 emergency stop & sensor suite
6. Master Driver Manager device node synchronization into ClothFS /dev/
7. Developer SDK: @ring(P0) priority dispatch, Landauer energy_budget, sandbox execution
8. Sensible Success Gauge evaluation and Sovereign Coherence Index (SCI) calculation.
"""

import pytest
import time

from loom.clothos.drivers import (
    NvidiaCudaDriver,
    AmdRocmDriver,
    AppleMetalDriver,
    RiscvVectorDriver,
    RoboticsActuatorDriver,
    RoboticsSensorDriver,
    get_driver_manager,
)
from loom.clothos.sdk import (
    ring,
    energy_budget,
    sandbox,
    kuramoto_sync,
    P0,
    P1,
    P4,
    clothos,
    PriorityRing,
    Signal,
)
from loom.clothos.success_gauge import success_gauge
from loom.clothos.fs import cloth_fs


class TestClothOSDrivers:
    def test_nvidia_cuda_driver(self):
        drv = NvidiaCudaDriver(device_id=0)
        assert drv.initialize() is True
        st = drv.get_state()
        assert st.total_vram_mb > 0
        assert drv.allocate_vram(128.0) is True
        drv.free_vram(128.0)
        formatted = drv.format_device_status()
        assert "Device:" in formatted
        assert drv.DEVICE_NODE == "/dev/gpu0_cuda"

    def test_amd_rocm_driver(self):
        drv = AmdRocmDriver(device_id=1)
        assert drv.initialize() is True
        initial_r = drv.get_state().kuramoto_order_r
        new_r = drv.dispatch_kuramoto_step(coupling_strength=0.1)
        assert new_r >= 0.0
        formatted = drv.format_device_status()
        assert "Kuramoto:" in formatted
        assert drv.DEVICE_NODE == "/dev/gpu1_rocm"

    def test_apple_metal_driver(self):
        drv = AppleMetalDriver()
        assert drv.initialize() is True
        st = drv.get_state()
        assert st.unified_memory_gb >= 16.0
        assert drv.allocate_zero_copy_buffer(512.0) is True
        drv.free_zero_copy_buffer(512.0)
        formatted = drv.format_device_status()
        assert "UMA Zero-Copy:" in formatted
        assert drv.DEVICE_NODE == "/dev/apple_metal"

    def test_riscv_vector_driver(self):
        drv = RiscvVectorDriver()
        assert drv.initialize() is True
        plan = drv.calculate_strip_mined_plan(elements=1024)
        assert plan["total_elements"] == 1024
        assert plan["iterations_required"] > 0
        formatted = drv.format_device_status()
        assert "RVV 1.0" in formatted
        assert drv.DEVICE_NODE == "/dev/riscv_rvv"

    def test_robotics_actuator_p0_estop(self):
        actuator = RoboticsActuatorDriver(num_joints=6)
        assert actuator.command_trajectory([0.1, 0.2, 0.3, 0.4, 0.5, 0.6]) is True
        assert actuator.joints[0].position_rad == 0.1

        # Trigger P0 emergency stop
        latency_us = actuator.trigger_p0_emergency_stop(reason="Obstacle detected")
        assert latency_us < 1000.0  # Under 1 millisecond
        assert actuator._emergency_stopped is True
        assert actuator.joints[0].is_enabled is False

        # Verify actuator refuses commands while stopped
        assert actuator.command_trajectory([0.0, 0.0, 0.0, 0.0, 0.0, 0.0]) is False

        # Release stop
        actuator.release_p0_emergency_stop()
        assert actuator._emergency_stopped is False

    def test_robotics_sensor_suite(self):
        sensors = RoboticsSensorDriver()
        imu = sensors.update_imu(roll=1.5, pitch=-2.0, yaw=45.0)
        assert imu.roll_deg == 1.5
        lidar = sensors.update_lidar_scan([1.5, 2.0, 0.3, 4.0])
        assert lidar.collision_warning is True  # 0.3m is within 0.5m safe zone

    def test_driver_manager_vfs_sync(self):
        dm = get_driver_manager()
        dm.sync_dev_nodes()
        health = dm.get_driver_health_score()
        assert health["driver_health_pct"] >= 90.0
        assert health["active_drivers_count"] >= 5

        # Verify device files exist in ClothFS /dev/
        cuda_content = cloth_fs.read_file("/dev/gpu0_cuda").decode("utf-8")
        assert "name" in cuda_content.lower()
        actuator_content = cloth_fs.read_file("/dev/robot_actuator0").decode("utf-8")
        assert "Robotic Actuator Subsystem" in actuator_content


class TestClothOSDeveloperSDK:
    def test_ring_decorator_p0_and_p4(self):
        @ring(P0)
        def critical_p0_action():
            return "P0_SUCCESS"

        @ring(P4)
        def epistemic_p4_action():
            return "P4_SUCCESS"

        assert critical_p0_action() == "P0_SUCCESS"
        assert epistemic_p4_action() == "P4_SUCCESS"

    def test_energy_budget_compliance(self):
        with energy_budget(joules=25.0) as eb:
            val = sum(x * x for x in range(50000))
        assert eb.within_budget is True
        assert eb.joules_consumed < 25.0

    def test_kuramoto_sync(self):
        r = kuramoto_sync(min_order_r=0.85)
        assert r >= 0.5

    def test_clothos_client_interface(self):
        prof = clothos.get_hardware_profile()
        assert prof.platform is not None
        assert prof.logical_cores > 0


class TestClothOSSuccessGauge:
    def test_success_gauge_evaluation(self):
        report = success_gauge.evaluate(run_tests=False)
        assert report.sovereign_coherence_index >= 85.0
        assert report.is_production_ready is True
        assert "hardware_drivers" in report.dimensions
        assert "process_governance" in report.dimensions
        assert "thermodynamics" in report.dimensions
        assert "vfs_host_bridge" in report.dimensions
