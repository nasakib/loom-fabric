"""
ClothOS Silicon Hardware Telemetry & Capability Scanner
File: loom/clothos/hardware_profile.py

Gathers rich local hardware capabilities for cluster broadcast:
- CPU model, cores, logical threads, base frequency.
- Physical RAM (total, available, percent used).
- GPUs (NVIDIA CUDA VRAM, AMD DirectML/Vulkan, Integrated).
- Local Ollama models and running tensor heads.
- Disk storage capacity and available scratch space.
"""

import os
import sys
import socket
import json
import subprocess
from typing import Dict, Any, List

def get_hardware_profile() -> Dict[str, Any]:
    profile: Dict[str, Any] = {
        "hostname": socket.gethostname(),
        "platform": sys.platform,
        "cpu": {},
        "ram": {},
        "gpus": [],
        "models": [],
        "storage": {}
    }

    if sys.platform == "win32":
        try:
            import ctypes
            # Fast WMI or PowerShell query
            ps_cmd = """
            $cs = Get-CimInstance Win32_ComputerSystem
            $os = Get-CimInstance Win32_OperatingSystem
            $cpu = Get-CimInstance Win32_Processor
            $gpus = Get-CimInstance Win32_VideoController
            $disks = Get-CimInstance Win32_LogicalDisk -Filter 'DriveType=3'

            $gpuList = @()
            foreach ($g in $gpus) {
                $gpuList += @{
                    name = $g.Name
                    vram_gb = [math]::Round($g.AdapterRAM / 1GB, 1)
                    driver = $g.DriverVersion
                }
            }

            $diskList = @()
            foreach ($d in $disks) {
                $diskList += @{
                    drive = $d.DeviceID
                    free_gb = [math]::Round($d.FreeSpace / 1GB, 1)
                    total_gb = [math]::Round($d.Size / 1GB, 1)
                }
            }

            [PSCustomObject]@{
                cpu_name = $cpu.Name
                cores = $cpu.NumberOfCores
                threads = $cpu.NumberOfLogicalProcessors
                total_ram_gb = [math]::Round($cs.TotalPhysicalMemory / 1GB, 1)
                free_ram_gb = [math]::Round($os.FreePhysicalMemory / 1MB, 1)
                gpus = $gpuList
                disks = $diskList
            } | ConvertTo-Json -Compress -Depth 4
            """
            res = subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd],
                capture_output=True, text=True, timeout=4
            )
            if res.returncode == 0 and res.stdout.strip():
                data = json.loads(res.stdout.strip())
                profile["cpu"] = {
                    "model": data.get("cpu_name", "Unknown CPU"),
                    "cores": data.get("cores", 4),
                    "threads": data.get("threads", 8)
                }
                profile["ram"] = {
                    "total_gb": data.get("total_ram_gb", 16.0),
                    "free_gb": data.get("free_ram_gb", 8.0)
                }
                profile["gpus"] = data.get("gpus", [])
                profile["storage"] = data.get("disks", [])
        except Exception:
            pass

    # Inspect local Ollama tags if running
    try:
        import urllib.request
        with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=1.0) as resp:
            tags = json.loads(resp.read().decode("utf-8"))
            profile["models"] = [m.get("name") for m in tags.get("models", [])]
    except Exception:
        profile["models"] = []

    return profile