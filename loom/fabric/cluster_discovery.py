"""
Cluster Compute Auto-Discovery (`loom/fabric/cluster_discovery.py`).

Self-discovers local and remote GPUs, accelerators, and CPU compute units across
the dual-machine sovereign mesh (Node 1 Desktop + Node 2 Laptop).
"""

from __future__ import annotations

import ctypes
from dataclasses import dataclass, field
import json
import logging
from pathlib import Path
import platform
import time
from typing import Any, Dict, List, Optional
import httpx

logger = logging.getLogger("loom.fabric.cluster_discovery")

PEER_IP = "192.168.99.2"
SHUTTLE_URL = f"http://{PEER_IP}:5555"
MASTER_TOKEN = "G-GzcZEzqteW241i720XeH5UNT73T6qk"


@dataclass
class DiscoveredComputeUnit:
    node_id: str
    device_id: str
    device_name: str
    device_type: str  # 'NVIDIA_CUDA_OPENCL', 'AMD_OPENCL', 'REMOTE_AMD_OPENCL', 'CPU'
    vram_bytes: int
    vram_gb: float
    platform_index: int
    device_index: int
    is_remote: bool
    status: str = "ONLINE"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "device_id": self.device_id,
            "device_name": self.device_name,
            "device_type": self.device_type,
            "vram_gb": round(self.vram_gb, 2),
            "is_remote": self.is_remote,
            "status": self.status,
            "metadata": self.metadata,
        }


class ClusterComputeDiscovery:
    """Discovers and catalogs all local and network compute accelerators."""

    def __init__(self, peer_ip: str = PEER_IP):
        self.peer_ip = peer_ip
        self.shuttle_url = f"http://{peer_ip}:5555"

    def discover_local_opencl_devices(self) -> List[DiscoveredComputeUnit]:
        """Discovers all local OpenCL devices (RTX 3060 12GB + RX 580 8GB)."""
        units: List[DiscoveredComputeUnit] = []
        try:
            cl = ctypes.cdll.LoadLibrary("OpenCL.dll")
            cl.clGetPlatformIDs.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_uint32)]
            cl.clGetPlatformInfo.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_size_t, ctypes.c_void_p, ctypes.POINTER(ctypes.c_size_t)]
            cl.clGetDeviceIDs.argtypes = [ctypes.c_void_p, ctypes.c_ulonglong, ctypes.c_uint32, ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_uint32)]
            cl.clGetDeviceInfo.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_size_t, ctypes.c_void_p, ctypes.POINTER(ctypes.c_size_t)]

            num_plat = ctypes.c_uint32()
            cl.clGetPlatformIDs(0, None, ctypes.byref(num_plat))
            plat_arr = (ctypes.c_void_p * num_plat.value)()
            cl.clGetPlatformIDs(num_plat.value, plat_arr, None)

            CL_PLATFORM_NAME = 0x0902
            CL_DEVICE_NAME = 0x102B
            CL_DEVICE_GLOBAL_MEM_SIZE = 0x101F
            CL_DEVICE_TYPE_ALL = 0xFFFFFFFF

            for p_idx in range(num_plat.value):
                pname = ctypes.create_string_buffer(256)
                cl.clGetPlatformInfo(plat_arr[p_idx], CL_PLATFORM_NAME, 256, pname, None)
                plat_name = pname.value.decode("utf-8", errors="ignore")

                num_dev = ctypes.c_uint32()
                cl.clGetDeviceIDs(plat_arr[p_idx], CL_DEVICE_TYPE_ALL, 0, None, ctypes.byref(num_dev))
                dev_arr = (ctypes.c_void_p * num_dev.value)()
                cl.clGetDeviceIDs(plat_arr[p_idx], CL_DEVICE_TYPE_ALL, num_dev.value, dev_arr, None)

                for d_idx in range(num_dev.value):
                    dname = ctypes.create_string_buffer(256)
                    cl.clGetDeviceInfo(dev_arr[d_idx], CL_DEVICE_NAME, 256, dname, None)
                    dev_name = dname.value.decode("utf-8", errors="ignore")

                    dmem = ctypes.c_ulonglong()
                    cl.clGetDeviceInfo(dev_arr[d_idx], CL_DEVICE_GLOBAL_MEM_SIZE, ctypes.sizeof(dmem), ctypes.byref(dmem), None)
                    vram_bytes = dmem.value
                    vram_gb = vram_bytes / (1024**3)

                    if "NVIDIA" in plat_name or "GeForce" in dev_name:
                        dev_type = "NVIDIA_CUDA_OPENCL"
                        dev_id = "node1_gpu0_rtx3060"
                    elif "Ellesmere" in dev_name or "AMD" in plat_name:
                        dev_type = "AMD_OPENCL"
                        dev_id = "node1_gpu1_rx580"
                    else:
                        dev_type = "GENERIC_OPENCL"
                        dev_id = f"node1_gpu_{p_idx}_{d_idx}"

                    units.append(
                        DiscoveredComputeUnit(
                            node_id="Node1-skyTech",
                            device_id=dev_id,
                            device_name=dev_name,
                            device_type=dev_type,
                            vram_bytes=vram_bytes,
                            vram_gb=vram_gb,
                            platform_index=p_idx,
                            device_index=d_idx,
                            is_remote=False,
                            metadata={"platform_name": plat_name},
                        )
                    )
        except Exception as e:
            logger.warning(f"Local OpenCL discovery error: {e}")

        return units

    def discover_remote_node2_devices(self) -> List[DiscoveredComputeUnit]:
        """Queries Node 2 (Ryzen 7 laptop @ 192.168.99.2) to discover its GPU 0 and CPUs."""
        units: List[DiscoveredComputeUnit] = []
        code = """
import ctypes, json
try:
    cl = ctypes.cdll.LoadLibrary('OpenCL.dll')
    cl.clGetPlatformIDs.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_uint32)]
    cl.clGetPlatformInfo.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_size_t, ctypes.c_void_p, ctypes.POINTER(ctypes.c_size_t)]
    cl.clGetDeviceIDs.argtypes = [ctypes.c_void_p, ctypes.c_ulonglong, ctypes.c_uint32, ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_uint32)]
    cl.clGetDeviceInfo.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_size_t, ctypes.c_void_p, ctypes.POINTER(ctypes.c_size_t)]
    num_plat = ctypes.c_uint32()
    cl.clGetPlatformIDs(0, None, ctypes.byref(num_plat))
    plat_arr = (ctypes.c_void_p * num_plat.value)()
    cl.clGetPlatformIDs(num_plat.value, plat_arr, None)
    devices = []
    for p in range(num_plat.value):
        num_dev = ctypes.c_uint32()
        cl.clGetDeviceIDs(plat_arr[p], 0xFFFFFFFF, 0, None, ctypes.byref(num_dev))
        dev_arr = (ctypes.c_void_p * num_dev.value)()
        cl.clGetDeviceIDs(plat_arr[p], 0xFFFFFFFF, num_dev.value, dev_arr, None)
        for d in range(num_dev.value):
            dname = ctypes.create_string_buffer(256)
            cl.clGetDeviceInfo(dev_arr[d], 0x102B, 256, dname, None)
            dmem = ctypes.c_ulonglong()
            cl.clGetDeviceInfo(dev_arr[d], 0x101F, ctypes.sizeof(dmem), ctypes.byref(dmem), None)
            devices.append({"name": dname.value.decode('utf-8', errors='ignore'), "vram_bytes": dmem.value, "p": p, "d": d})
    print(json.dumps(devices))
except Exception as e:
    print(json.dumps([]))
"""
        try:
            with httpx.Client(timeout=4.0) as client:
                r = client.post(
                    f"{self.shuttle_url}/api/science/run_python",
                    json={"code": code},
                    headers={"X-Fabric-Token": MASTER_TOKEN},
                )
                if r.status_code == 200:
                    raw_out = r.json().get("stdout", "[]").strip()
                    parsed = json.loads(raw_out)
                    for item in parsed:
                        dev_name = item.get("name", "AMD Radeon Graphics (Node 2)")
                        vram_bytes = item.get("vram_bytes", 0)
                        vram_gb = vram_bytes / (1024**3)
                        units.append(
                            DiscoveredComputeUnit(
                                node_id="Node2-Laptop-Ryzen7",
                                device_id="node2_gpu0_radeon",
                                device_name=f"Node2 Remote GPU ({dev_name})",
                                device_type="REMOTE_AMD_OPENCL",
                                vram_bytes=vram_bytes,
                                vram_gb=vram_gb,
                                platform_index=item.get("p", 0),
                                device_index=item.get("d", 0),
                                is_remote=True,
                                metadata={"ip": self.peer_ip, "port": 5555},
                            )
                        )
        except Exception as e:
            logger.debug(f"Node 2 remote accelerator discovery notice: {e}")

        return units

    def discover_all_compute_units(self) -> Dict[str, Any]:
        """Discovers all cluster resources and computes pooled capacity."""
        local_units = self.discover_local_opencl_devices()
        remote_units = self.discover_remote_node2_devices()
        all_units = local_units + remote_units

        total_vram_gb = sum(u.vram_gb for u in all_units)

        catalog = {
            "timestamp": time.time(),
            "total_accelerators": len(all_units),
            "total_vram_gb": round(total_vram_gb, 2),
            "units": [u.to_dict() for u in all_units],
            "node1_gpu0": next((u.to_dict() for u in all_units if u.device_id == "node1_gpu0_rtx3060"), None),
            "node1_gpu1": next((u.to_dict() for u in all_units if u.device_id == "node1_gpu1_rx580"), None),
            "node2_gpu0": next((u.to_dict() for u in all_units if u.device_id == "node2_gpu0_radeon"), None),
        }
        return catalog


# Global discovery instance
cluster_discovery = ClusterComputeDiscovery()
