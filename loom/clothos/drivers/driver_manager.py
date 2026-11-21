# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
ClothOS Master Hardware Driver Manager (`loom/clothos/drivers/driver_manager.py`).

Coordinates all physical and virtual hardware drivers across the sovereign substrate:
- NVIDIA CUDA & Tensor Cores (`/dev/gpu0_cuda`)
- AMD Radeon & ROCm / DirectML (`/dev/gpu1_rocm`)
- Apple Silicon Metal 3 & UMA (`/dev/apple_metal`)
- RISC-V RV64GCV Vector & PMP Enclaves (`/dev/riscv_rvv`)
- Robotics Cyber-Physical Actuators & Sensors (`/dev/robot_actuator0`, `/dev/robot_imu0`, `/dev/robot_lidar0`)

Registers character device hooks into ClothFS `/dev/` and provides unified driver health scoring.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

from loom.clothos.drivers.amd_rocm_driver import AmdRocmDriver
from loom.clothos.drivers.apple_metal_driver import AppleMetalDriver
from loom.clothos.drivers.nvidia_cuda_driver import NvidiaCudaDriver
from loom.clothos.drivers.riscv_driver import RiscvVectorDriver
from loom.clothos.drivers.robotics_driver import RoboticsActuatorDriver, RoboticsSensorDriver
from loom.clothos.fs import ClothFS, cloth_fs

logger = logging.getLogger("loom.clothos.drivers.manager")


class ClothOSDriverManager:
    """Master hardware abstraction and driver orchestrator for ClothOS."""

    def __init__(self, fs: Optional[ClothFS] = None):
        self.fs = fs or cloth_fs
        self.nvidia = NvidiaCudaDriver(device_id=0)
        self.amd = AmdRocmDriver(device_id=1)
        self.apple = AppleMetalDriver()
        self.riscv = RiscvVectorDriver()
        self.robot_actuator = RoboticsActuatorDriver(num_joints=6)
        self.robot_sensor = RoboticsSensorDriver()
        self._register_dev_nodes()

    def _register_dev_nodes(self) -> None:
        """Exposes dynamic character device nodes into ClothFS /dev/."""
        try:
            self.fs.mkdir("/dev")
        except Exception:
            pass

        # Write initial device status descriptors into VFS
        self.sync_dev_nodes()

    def sync_dev_nodes(self) -> None:
        """Refreshes all /dev/ character device nodes with live driver telemetry."""
        devices = {
            self.nvidia.DEVICE_NODE: self.nvidia.format_device_status(),
            self.amd.DEVICE_NODE: self.amd.format_device_status(),
            self.apple.DEVICE_NODE: self.apple.format_device_status(),
            self.riscv.DEVICE_NODE: self.riscv.format_device_status(),
            self.robot_actuator.DEVICE_NODE: self.robot_actuator.format_device_status(),
            self.robot_sensor.IMU_NODE: self.robot_sensor.format_device_status(),
        }

        for path, content in devices.items():
            try:
                self.fs.write_file(path, content.encode("utf-8"))
            except Exception as exc:
                logger.debug("Failed to sync /dev node %s: %s", path, exc)

    def get_driver_health_score(self) -> Dict[str, Any]:
        """Calculates quantitative driver health and availability score (0 - 100%)."""
        drivers = [
            ("nvidia_cuda", self.nvidia.get_state().is_online, 1.0),
            ("amd_rocm", self.amd.get_state().is_online, 1.0),
            ("apple_metal", self.apple.get_state().is_online, 1.0),
            ("riscv_rvv", self.riscv.get_state().is_online, 1.0),
            ("robot_actuator", not self.robot_actuator._emergency_stopped, 1.0),
            ("robot_sensor", self.robot_sensor.imu.is_calibrated, 1.0),
        ]

        total_weight = sum(w for _, _, w in drivers)
        active_weight = sum(w for _, online, w in drivers if online)
        score_pct = round((active_weight / total_weight) * 100.0, 1)

        return {
            "driver_health_pct": score_pct,
            "drivers_count": len(drivers),
            "active_drivers_count": sum(1 for _, online, _ in drivers if online),
            "details": {name: "ONLINE" if online else "OFFLINE" for name, online, _ in drivers},
        }


# Global singleton instance
_DRIVER_MANAGER: Optional[ClothOSDriverManager] = None


def get_driver_manager() -> ClothOSDriverManager:
    global _DRIVER_MANAGER
    if _DRIVER_MANAGER is None:
        _DRIVER_MANAGER = ClothOSDriverManager()
    return _DRIVER_MANAGER
