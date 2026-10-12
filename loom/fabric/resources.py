"""Custom Accelerator Resource Tagging and Registration for Ray Clusters.

Converts hardware specifications discovered by the Stitch profiler into
strongly-typed Ray Custom Resources used for scheduling actors onto specific GPUs.

Architecture Note (Rust Migration Target):
    This module maps to `loom_fabric::resources` in Rust:
    - Provides serializable resource dictionaries for Ray cluster node registration.
"""

from __future__ import annotations

import json
from typing import Dict
from pydantic import BaseModel, Field

from ..stitch.profiler import ClusterHardwareState
from ..config import settings


class RayNodeRegistrationPayload(BaseModel):
    """Specification of Ray launch arguments and custom resource mappings."""

    node_role: str = Field(..., description="'head' or 'worker'.")
    ray_start_command: str = Field(..., description="Exact CLI command to start the Ray node.")
    resources_json: str = Field(..., description="JSON representation of registered custom resources.")
    resource_map: Dict[str, float] = Field(default_factory=dict, description="Parsed resource mapping.")


class RayClusterResourceRegistry:
    """Generates Ray startup commands and registers custom hardware resources."""

    @staticmethod
    def build_worker_resources(state: ClusterHardwareState) -> RayNodeRegistrationPayload:
        """Constructs custom Ray resource tags for the SkyTech GPU worker node.

        Resources Generated:
            - `NODE_WORKER`: 1.0 (Actor placement constraint)
            - `GPU_NVIDIA`: Count of physical NVIDIA GPUs
            - `GPU_AMD`: Count of physical AMD GPUs
            - `RTX3060`: 1.0 (Specific hardware family tag)
            - `RX580`: 1.0 (Specific hardware family tag)
            - `VRAM_MB`: Total combined physical VRAM
            - `HOST_RAM_MB`: Available host system memory

        Args:
            state: Probed physical state of the local worker.

        Returns:
            RayNodeRegistrationPayload with exact ray start arguments.
        """
        res_map: Dict[str, float] = {
            "NODE_WORKER": 1.0,
            "HOST_RAM_MB": float(state.host.available_ram_mb),
        }

        total_vram = 0.0
        for gpu in state.gpus:
            total_vram += float(gpu.total_vram_mb)
            if gpu.vendor == "NVIDIA":
                res_map["GPU_NVIDIA"] = res_map.get("GPU_NVIDIA", 0.0) + 1.0
                if "3060" in gpu.name:
                    res_map["RTX3060"] = 1.0
            elif gpu.vendor == "AMD":
                res_map["GPU_AMD"] = res_map.get("GPU_AMD", 0.0) + 1.0
                if "580" in gpu.name:
                    res_map["RX580"] = 1.0

        res_map["TOTAL_VRAM_MB"] = total_vram

        res_json = json.dumps(res_map)
        head_addr = f"{settings.head_node.ip}:{settings.head_node.ray_port}"
        cmd = f"ray start --address={head_addr} --resources='{res_json}'"

        return RayNodeRegistrationPayload(
            node_role="worker",
            ray_start_command=cmd,
            resources_json=res_json,
            resource_map=res_map,
        )

    @staticmethod
    def build_head_resources() -> RayNodeRegistrationPayload:
        """Constructs custom Ray resource tags for the Ryzen Head node."""
        res_map: Dict[str, float] = {
            "NODE_HEAD": 1.0,
            "CPU_HEAD": 16.0,
            "HEAD_RAM_MB": 16384.0,
        }
        res_json = json.dumps(res_map)
        cmd = f"ray start --head --port={settings.head_node.ray_port} --dashboard-port={settings.head_node.dashboard_port} --resources='{res_json}'"

        return RayNodeRegistrationPayload(
            node_role="head",
            ray_start_command=cmd,
            resources_json=res_json,
            resource_map=res_map,
        )
