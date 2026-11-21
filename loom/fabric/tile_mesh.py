# Copyright (c) 2026 Najmos Sakib / VectorCore Holdings, LLC.
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Heterogeneous 2D Compute & Memory Tile Mesh Architecture (`loom/fabric/tile_mesh.py`).
=====================================================================================
Models a 2D Network-on-Chip (NoC) and inter-node tile topology with dimension-order
XY routing, link backpressure, fault isolation, and full tile classes:
1. RISCV_CPU (Scalar & RVV Vector)
2. X86_CPU (Host General Purpose)
3. GPU_SIMT (NVIDIA CUDA on Node 1 / Pure AMD ROCm & Vulkan on Node 2)
4. NPU_TENSOR (Systolic Array / MXU)
5. FPGA (Reconfigurable Logic)
6. DPU_SMARTNIC (Fabric Modem DMA Engine)
7. MEMORY_TILE (Unified Memory Pool, HBM3, Near-Memory, Scratchpad)
"""

from __future__ import annotations

import logging
import math
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("loom.fabric.tile_mesh")


class TileClass(str, Enum):
    RISCV_CPU = "RISCV_CPU"       # RV64GCVB Core
    X86_CPU = "X86_CPU"           # Host AMD/Intel Core
    GPU_SIMT = "GPU_SIMT"         # Discrete/Integrated GPU
    NPU_TENSOR = "NPU_TENSOR"     # Matrix Multiply Accelerator
    FPGA = "FPGA"                 # Reconfigurable Logic Tile
    DPU_SMARTNIC = "DPU_SMARTNIC" # Fabric Modem DMA Transceiver
    MEMORY_TILE = "MEMORY_TILE"   # HBM / Unified / Scratchpad


class TileStatus(str, Enum):
    IDLE = "IDLE"
    BUSY = "BUSY"
    CONGESTED = "CONGESTED"
    OFFLINE = "OFFLINE"
    FALLBACK = "FALLBACK"


@dataclass
class ComputeTile:
    tile_id: str
    x: int
    y: int
    tile_class: TileClass
    clock_ghz: float
    capacity_tflops: float
    memory_gb: float
    backend_driver: str           # "CUDA", "ROCm", "Vulkan", "RISCV_HAL", "HOST_NATIVE"
    node_id: str                  # "skyTech-Worker" (Node 1) or "Ryzen7-Head" (Node 2)
    status: TileStatus = TileStatus.IDLE
    is_pure_amd: bool = False     # Enforces Node 2 Purity

    def accepts_workload(self, requires_nvidia: bool) -> bool:
        if self.status in (TileStatus.OFFLINE, TileStatus.CONGESTED):
            return False
        # Node 2 Purity Check: Reject NVIDIA if marked pure AMD
        if requires_nvidia and self.is_pure_amd:
            return False
        if requires_nvidia and "CUDA" not in self.backend_driver:
            return False
        return True


@dataclass
class MeshRouteHop:
    from_x: int
    from_y: int
    to_x: int
    to_y: int
    latency_ns: float
    congested: bool


class HeterogeneousTileMesh:
    """2D Dimension-Order (XY) Grid Mesh interconnecting heterogeneous compute tiles."""

    def __init__(self, width: int = 4, height: int = 4):
        self.width = width
        self.height = height
        self.grid: Dict[Tuple[int, int], ComputeTile] = {}
        self.link_bandwidth_gbps = 256.0 # Inter-tile crossbar
        self.hop_latency_ns = 2.5        # 2.5 ns per tile hop
        self._init_default_cluster_mesh()

    def _init_default_cluster_mesh(self) -> None:
        """Initializes the heterogeneous cluster topology incorporating live cluster hardware."""
        # Tile (0, 0): DPU / Fabric Modem SmartNIC (skyTech)
        self.add_tile(ComputeTile("tile_dpu0", 0, 0, TileClass.DPU_SMARTNIC, 2.0, 4.0, 2.0, "FABRIC_DMA", "skyTech-Worker"))
        
        # Tile (0, 1): GPU SIMT (NVIDIA RTX 3060 12GB CUDA - Node 1)
        self.add_tile(ComputeTile("tile_gpu0", 0, 1, TileClass.GPU_SIMT, 1.78, 12.7, 12.0, "CUDA", "skyTech-Worker", is_pure_amd=False))

        # Tile (0, 2): GPU SIMT (AMD Radeon RX 580 8GB Vulkan/OpenCL - Node 1)
        self.add_tile(ComputeTile("tile_gpu1", 0, 2, TileClass.GPU_SIMT, 1.28, 6.2, 8.0, "Vulkan/OpenCL", "skyTech-Worker", is_pure_amd=True))

        # Tile (1, 0): x86 CPU (Host Core Array)
        self.add_tile(ComputeTile("tile_x86", 1, 0, TileClass.X86_CPU, 3.8, 2.4, 32.0, "HOST_NATIVE", "skyTech-Worker"))

        # Tile (1, 1): RISC-V Scalar + Vector Tile (RV64GCVB Core)
        self.add_tile(ComputeTile("tile_rv64v", 1, 1, TileClass.RISCV_CPU, 2.5, 3.2, 8.0, "RISCV_HAL", "skyTech-Worker"))

        # Tile (1, 2): NPU Tensor Unit (Systolic MXU Array)
        self.add_tile(ComputeTile("tile_npu0", 1, 2, TileClass.NPU_TENSOR, 2.0, 18.0, 16.0, "SYSTOLIC_MXU", "skyTech-Worker"))

        # Tile (2, 0): Node 2 DPU / Interconnect Bridge (Ryzen Head)
        self.add_tile(ComputeTile("tile_dpu1", 2, 0, TileClass.DPU_SMARTNIC, 2.0, 2.0, 2.0, "FABRIC_DMA", "Ryzen7-Head", is_pure_amd=True))

        # Tile (2, 1): Node 2 CPU (AMD Ryzen 7 7730U 16-vCPU Zen 3 - Node 2 Purity)
        self.add_tile(ComputeTile("tile_ryzen_cpu", 2, 1, TileClass.X86_CPU, 4.5, 4.8, 32.0, "ROCm/OpenRoad", "Ryzen7-Head", is_pure_amd=True))

        # Tile (2, 2): Node 2 GPU (AMD Radeon Vega 8 - Node 2 Purity Guaranteed)
        self.add_tile(ComputeTile("tile_ryzen_gpu", 2, 2, TileClass.GPU_SIMT, 2.0, 3.6, 14.4, "Vulkan/ROCm", "Ryzen7-Head", is_pure_amd=True))

        # Tile (3, 3): Unified High-Bandwidth Memory (HBM3 Pool)
        self.add_tile(ComputeTile("tile_mem0", 3, 3, TileClass.MEMORY_TILE, 3.2, 0.0, 64.0, "UNIFIED_POOL", "skyTech-Worker"))

    def add_tile(self, tile: ComputeTile) -> None:
        self.grid[(tile.x, tile.y)] = tile

    def get_tile(self, x: int, y: int) -> Optional[ComputeTile]:
        return self.grid.get((x, y))

    def compute_xy_route(self, src: Tuple[int, int], dst: Tuple[int, int]) -> List[MeshRouteHop]:
        """Dimension-Order (X-first, then Y) deadlock-free routing."""
        hops: List[MeshRouteHop] = []
        curr_x, curr_y = src
        dst_x, dst_y = dst

        # X-dimension routing
        while curr_x != dst_x:
            next_x = curr_x + (1 if dst_x > curr_x else -1)
            target_tile = self.grid.get((next_x, curr_y))
            congested = target_tile.status == TileStatus.CONGESTED if target_tile else False
            lat = self.hop_latency_ns * (3.5 if congested else 1.0)
            hops.append(MeshRouteHop(curr_x, curr_y, next_x, curr_y, lat, congested))
            curr_x = next_x

        # Y-dimension routing
        while curr_y != dst_y:
            next_y = curr_y + (1 if dst_y > curr_y else -1)
            target_tile = self.grid.get((curr_x, next_y))
            congested = target_tile.status == TileStatus.CONGESTED if target_tile else False
            lat = self.hop_latency_ns * (3.5 if congested else 1.0)
            hops.append(MeshRouteHop(curr_x, curr_y, curr_x, next_y, lat, congested))
            curr_y = next_y

        return hops

    def dispatch_workload(
        self,
        tile_class_preference: TileClass,
        requires_nvidia: bool = False,
        target_node: Optional[str] = None,
    ) -> Tuple[ComputeTile, float, str]:
        """Selects the optimal tile, enforcing Node 2 purity and fallback if busy."""
        candidates = [
            t for t in self.grid.values()
            if t.tile_class == tile_class_preference and t.accepts_workload(requires_nvidia)
        ]

        # Filter by target node if specified
        if target_node:
            filtered = [t for t in candidates if t.node_id == target_node]
            if filtered:
                candidates = filtered

        # If Node 2 is targeted with an NVIDIA workload, strictly deny/divert to Node 1
        if target_node == "Ryzen7-Head" and requires_nvidia:
            logger.warning("Node 2 Purity Alert: NVIDIA workload redirected to Node 1 (skyTech-Worker).")
            candidates = [t for t in self.grid.values() if t.tile_class == tile_class_preference and t.node_id == "skyTech-Worker"]

        # If preferred tile is offline or busy, fallback to CPU or general tile
        if not candidates:
            # Fallback to general CPU
            fallback_candidates = [
                t for t in self.grid.values()
                if t.tile_class in (TileClass.X86_CPU, TileClass.RISCV_CPU) and t.status != TileStatus.OFFLINE
            ]
            if not fallback_candidates:
                raise RuntimeError("No viable compute tiles available across the mesh.")
            selected = fallback_candidates[0]
            route_info = f"FALLBACK -> {selected.tile_id} ({selected.tile_class.value} on {selected.node_id})"
            return selected, 45.0, route_info

        # Select highest capacity idle candidate
        selected = max(candidates, key=lambda t: t.capacity_tflops)
        route_hops = self.compute_xy_route((0, 0), (selected.x, selected.y))
        total_hops_latency_ns = sum(h.latency_ns for h in route_hops)
        route_info = f"DIRECT_XY -> {selected.tile_id} ({selected.tile_class.value} on {selected.node_id}, Pure AMD: {selected.is_pure_amd})"
        return selected, total_hops_latency_ns, route_info
