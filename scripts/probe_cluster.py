"""
Loom Fabric: Cluster Hardware, Network Dual-Homing & Socket Diagnostics.

Probes physical accelerators, system RAM, network dual-homing between Head Node
(192.168.99.2) and Worker Node (192.168.99.1), tests Ray cluster connectivity,
and provides Wake-on-LAN (WoL) dispatch capabilities.
"""

from __future__ import annotations

import json
import os
import platform
import socket
import struct
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Tuple


def probe_socket(host: str, port: int, timeout: float = 1.0) -> bool:
    """Test TCP socket reachability with strict timeout."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def send_wol_magic_packet(mac_address: str, broadcast_ip: str = "192.168.99.255", port: int = 9) -> bool:
    """Dispatches a Wake-on-LAN (WoL) magic packet to awaken the remote node."""
    clean_mac = mac_address.replace(":", "").replace("-", "").strip()
    if len(clean_mac) != 12:
        return False

    try:
        mac_bytes = bytes.fromhex(clean_mac)
        magic_payload = b"\xff" * 6 + mac_bytes * 16
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(magic_payload, (broadcast_ip, port))
        return True
    except Exception:
        return False


def get_local_hardware_profile() -> Dict[str, Any]:
    """Inspects physical CPU, memory, and accelerator topologies."""
    profile: Dict[str, Any] = {
        "hostname": platform.node(),
        "os": f"{platform.system()} {platform.release()} ({platform.architecture()[0]})",
        "python": sys.version.split()[0],
        "cpu_cores_logical": os.cpu_count() or 1,
        "gpus": [],
        "total_ram_mb": 0,
        "available_ram_mb": 0,
    }

    # RAM via psutil if available or Windows/Linux APIs
    try:
        import psutil
        mem = psutil.virtual_memory()
        profile["total_ram_mb"] = round(mem.total / (1024 * 1024), 2)
        profile["available_ram_mb"] = round(mem.available / (1024 * 1024), 2)
    except ImportError:
        pass

    # Inspect NVIDIA GPUs via nvidia-smi if available (never on Node 2 / Ryzen)
    import shutil
    extra_flags = 0x08000000 if sys.platform == "win32" else 0
    node_name = platform.node().lower()
    if "ryzen" not in node_name and "head" not in node_name and shutil.which("nvidia-smi"):
        try:
            res = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total,memory.free,driver_version", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=2,
                creationflags=extra_flags,
            )
            if res.returncode == 0:
                for line in res.stdout.strip().splitlines():
                    parts = [p.strip() for p in line.split(",")]
                    if len(parts) >= 4:
                        profile["gpus"].append({
                            "name": parts[0],
                            "vendor": "NVIDIA",
                            "total_vram_mb": float(parts[1]),
                            "free_vram_mb": float(parts[2]),
                            "driver_version": parts[3],
                            "backend": "CUDA",
                        })
        except Exception:
            pass

    # Inspect AMD/Intel GPUs via Windows PowerShell / WMI if on Windows
    if sys.platform == "win32":
        try:
            cmd = "Get-CimInstance Win32_VideoController | Select-Object -Property Name, AdapterRAM, DriverVersion | ConvertTo-Json"
            ps_res = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, text=True, timeout=3, creationflags=extra_flags)
            if ps_res.returncode == 0 and ps_res.stdout.strip():
                try:
                    data = json.loads(ps_res.stdout)
                    if isinstance(data, dict):
                        data = [data]
                    for d in data:
                        gpu_name = d.get("Name", "Unknown GPU")
                        # Skip Microsoft Basic Render or already listed NVIDIA
                        if "Basic Render" in gpu_name:
                            continue
                        if any(g["name"] == gpu_name for g in profile["gpus"]):
                            continue
                        adapter_ram = d.get("AdapterRAM") or 0
                        vram_mb = round(adapter_ram / (1024 * 1024), 2) if adapter_ram > 0 else 8192.0
                        vendor = "AMD" if "Radeon" in gpu_name or "AMD" in gpu_name else ("Intel" if "Intel" in gpu_name else "Unknown")
                        backend = "Vulkan" if vendor == "AMD" else "OpenCL/D3D"
                        profile["gpus"].append({
                            "name": gpu_name,
                            "vendor": vendor,
                            "total_vram_mb": vram_mb,
                            "free_vram_mb": max(512.0, vram_mb - 512.0),
                            "driver_version": d.get("DriverVersion", "N/A"),
                            "backend": backend,
                        })
                except Exception:
                    pass
        except Exception:
            pass

    return profile


def run_diagnostics() -> Dict[str, Any]:
    """Executes complete diagnostic matrix across physical cluster."""
    hardware = get_local_hardware_profile()

    worker_ip = "192.168.99.1"
    head_ip = "192.168.99.2"

    network_probes = {
        "worker_direct_ip": worker_ip,
        "worker_stitch_native_8080": probe_socket(worker_ip, 8080, timeout=1.0),
        "worker_bridge_5555": probe_socket(worker_ip, 5555, timeout=1.0),
        "worker_ollama_11434": probe_socket(worker_ip, 11434, timeout=1.0),
        "head_ray_gcs_6379": probe_socket(head_ip, 6379, timeout=0.8) or probe_socket("127.0.0.1", 6379, timeout=0.8),
        "head_gateway_8002": probe_socket(head_ip, 8002, timeout=0.8) or probe_socket("127.0.0.1", 8002, timeout=0.8),
        "head_gateway_8000": probe_socket(head_ip, 8000, timeout=0.8) or probe_socket("127.0.0.1", 8000, timeout=0.8),
        "head_claw_18789": probe_socket(head_ip, 18789, timeout=0.8) or probe_socket("127.0.0.1", 18789, timeout=0.8),
    }

    report = {
        "timestamp": time.time(),
        "local_node": hardware,
        "network_matrix": network_probes,
    }
    return report


if __name__ == "__main__":
    report = run_diagnostics()
    print(json.dumps(report, indent=2))
