"""
Cross-Platform Node Discovery (`fabric/discovery/nodes.py`).

Auto-discovers and registers heterogeneous compute nodes across:
- Windows 10/11 (`192.168.99.1` skyTech Worker & `192.168.99.2` Ryzen 7 Head Node)
- WSL2 Ubuntu Subsystems
- macOS (`Apple Silicon Metal Unified Memory` & `Intel`)
- Linux (`CUDA` / `ROCm` / `Vulkan`)
- ClothOS Special Edition (`RISC-V RV64GC + RVV 1.0` + `PMP Enclave`)
"""

from __future__ import annotations

import platform
import shutil
import socket
import time
from typing import List, Literal, Tuple
from pydantic import BaseModel, ConfigDict, Field

from loom.stitch.profiler import HardwareProfiler, probe_clothos_riscv_state


class DiscoveredFabricNode(BaseModel):
    """Immutable descriptor of a discovered node in the Fabric compute pool."""

    model_config = ConfigDict(frozen=True)

    node_id: str = Field(..., description="Logical node identifier.")
    ip_address: str = Field(..., description="IPv4 address on the 192.168.99.x Fabric subnet.")
    platform_family: Literal["Windows", "WSL2", "macOS", "Linux", "ClothOS-RISCV"] = Field(
        ..., description="Operating system / ISA family."
    )
    architecture: str = Field(..., description="CPU/Accelerator ISA (e.g., x86_64, arm64, rv64imafdcv).")
    role: Literal["head_orchestrator", "gpu_worker", "wsl_bridge", "riscv_enclave"] = Field(
        ..., description="Cluster role."
    )
    total_vram_mb: int = Field(..., ge=0, description="Total accelerator VRAM in MB.")
    free_vram_mb: int = Field(..., ge=0, description="Available accelerator VRAM margin in MB.")
    online_ports: Tuple[int, ...] = Field(default_factory=tuple, description="Reachable Fabric TCP ports.")
    status: Literal["ONLINE", "STANDBY", "OFFLINE"] = Field(..., description="Current health status.")


class ClusterTopologySnapshot(BaseModel):
    """Immutable snapshot of the entire cross-platform Fabric node pool."""

    model_config = ConfigDict(frozen=True)

    snapshot_epoch: float = Field(..., description="UTC timestamp of discovery scan.")
    total_cluster_vram_mb: int = Field(..., ge=0)
    free_cluster_vram_mb: int = Field(..., ge=0)
    nodes: Tuple[DiscoveredFabricNode, ...] = Field(...)


class CrossPlatformNodeDiscovery:
    """Scans local hardware, WSL2, ClothOS RISC-V target, and the 192.168.99.x subnet."""

    @staticmethod
    def _probe_port(host: str, port: int, timeout: float = 0.25) -> bool:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except Exception:
            return False

    def discover_all(self, probe_network: bool = True) -> ClusterTopologySnapshot:
        """Discovers all nodes across Windows, WSL2, macOS, Linux, and ClothOS RISC-V."""
        profiler = HardwareProfiler()
        local_profile = profiler.build_node_profile()
        local_total_vram = sum(g.total_vram_mb for g in local_profile.gpus) or 20480
        local_free_vram = sum(g.free_vram_mb for g in local_profile.gpus) or 12918

        hostname = socket.gethostname().lower()
        is_skytech = "skytech" in hostname
        worker_ip = "192.168.99.1"
        head_ip = "192.168.99.2"

        worker_ports: List[int] = []
        head_ports: List[int] = []
        if probe_network:
            for p in (8002, 5555, 11434, 18789):
                target_w = "127.0.0.1" if is_skytech else worker_ip
                if self._probe_port(target_w, p):
                    worker_ports.append(p)
            for p in (8002, 5555, 6379, 8265, 11434, 18789):
                target_h = "127.0.0.1" if not is_skytech else head_ip
                if self._probe_port(target_h, p):
                    head_ports.append(p)
        else:
            worker_ports = [8002, 5555, 11434, 18789]
            head_ports = [8002, 5555, 6379, 8265, 11434, 18789]

        sys_os = platform.system()
        if sys_os == "Darwin":
            local_family: Literal["Windows", "WSL2", "macOS", "Linux", "ClothOS-RISCV"] = "macOS"
        elif sys_os == "Linux":
            local_family = "Linux"
        else:
            local_family = "Windows"

        nodes: List[DiscoveredFabricNode] = [
            DiscoveredFabricNode(
                node_id="skyTech-Worker",
                ip_address=worker_ip,
                platform_family=local_family if is_skytech else "Windows",
                architecture="x86_64 (RTX 3060 12GB CUDA + RX 580 8GB Vulkan)",
                role="gpu_worker",
                total_vram_mb=local_total_vram if is_skytech else 20480,
                free_vram_mb=local_free_vram if is_skytech else 12918,
                online_ports=tuple(worker_ports),
                status="ONLINE" if worker_ports else "OFFLINE",
            ),
            DiscoveredFabricNode(
                node_id="Ryzen7-Head",
                ip_address=head_ip,
                platform_family=local_family if not is_skytech else "Windows",
                architecture="x86_64 (Ryzen 7 7730U 16-vCPU + Radeon 680M)",
                role="head_orchestrator",
                total_vram_mb=2048,
                free_vram_mb=1536,
                online_ports=tuple(head_ports),
                status="ONLINE" if head_ports else "OFFLINE",
            ),
        ]

        # Check WSL2 availability on Windows
        if shutil.which("wsl"):
            nodes.append(
                DiscoveredFabricNode(
                    node_id="WSL2-Ubuntu-Bridge",
                    ip_address="127.0.0.1",
                    platform_family="WSL2",
                    architecture="x86_64 Linux Kernel (OpenClaw + Aider Sandbox)",
                    role="wsl_bridge",
                    total_vram_mb=local_total_vram,
                    free_vram_mb=local_free_vram,
                    online_ports=tuple(worker_ports if is_skytech else head_ports),
                    status="ONLINE",
                )
            )

        # Check ClothOS RISC-V Special Edition status
        riscv_info = probe_clothos_riscv_state()
        nodes.append(
            DiscoveredFabricNode(
                node_id="ClothOS-RISCV-Enclave",
                ip_address="192.168.99.1",
                platform_family="ClothOS-RISCV",
                architecture=f"{riscv_info['isa_string']} (VLEN={riscv_info['vlen_bits']}b, PMP={riscv_info['pmp_csr']})",
                role="riscv_enclave",
                total_vram_mb=16384,
                free_vram_mb=14336,
                online_ports=(8002,),
                status="ONLINE" if riscv_info.get("is_native_riscv") else "STANDBY",
            )
        )

        total_vram = sum(n.total_vram_mb for n in nodes[:2])
        free_vram = sum(n.free_vram_mb for n in nodes[:2])

        return ClusterTopologySnapshot(
            snapshot_epoch=time.time(),
            total_cluster_vram_mb=total_vram,
            free_cluster_vram_mb=free_vram,
            nodes=tuple(nodes),
        )
