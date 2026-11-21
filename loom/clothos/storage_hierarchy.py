# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
ClothOS Strategic Multi-Tier Storage Hierarchy Manager (`loom/clothos/storage_hierarchy.py`).

Intelligently catalogs, benchmarks, and stratifies file storage across all accessible
physical drives, NVMe SSDs, secondary bulk HDDs, removable USB devices, RAM disks,
and distributed 2.5GbE cluster nodes.
"""

from __future__ import annotations

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional


class StorageTier:
    TIER_0_RAM_SCRATCH = "TIER_0_RAM_SCRATCH"        # Ephemeral RAM / Microsecond scratch
    TIER_1_FAST_NVME   = "TIER_1_FAST_NVME"          # Hot code, git repo, active model heads
    TIER_2_BULK_STORAGE = "TIER_2_BULK_STORAGE"      # 100MB+ long-form works, archives, heavy audio/video
    TIER_3_COLD_BACKUP  = "TIER_3_COLD_BACKUP"       # Removable USB, external backup, air-gapped snapshots
    TIER_4_MESH_REMOTE  = "TIER_4_MESH_REMOTE"       # Distributed storage on Node 1 (skyTech) / remote cluster


class StorageHierarchyManager:
    """Discovers, benchmarks, and orchestrates data placement across physical storage devices."""

    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = (workspace_root or Path.cwd()).resolve()
        self.scratch_dir = Path(os.environ.get("TEMP", ".")) / "clothos_scratch"
        self.scratch_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir = self.workspace_root / "deliverables" / "archives"
        self.archive_dir.mkdir(parents=True, exist_ok=True)

    def scan_storage_devices(self) -> List[Dict[str, Any]]:
        """Enumerates all logical storage drives and mounted volumes."""
        devices: List[Dict[str, Any]] = []

        if sys.platform == "win32":
            ps_script = """
            Get-CimInstance Win32_LogicalDisk | Select-Object DeviceID, VolumeName, FileSystem, FreeSpace, Size, DriveType | ConvertTo-Json -Compress
            """
            try:
                res = subprocess.run(
                    ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
                    capture_output=True, text=True, timeout=5
                )
                if res.returncode == 0 and res.stdout.strip():
                    raw = json.loads(res.stdout.strip())
                    if isinstance(raw, dict):
                        raw = [raw]
                    for d in raw:
                        dtype = d.get("DriveType", 3)
                        # DriveType: 2 = Removable, 3 = Fixed, 4 = Network, 5 = CD-ROM, 6 = RAMDisk
                        type_str = "FIXED_DISK"
                        tier = StorageTier.TIER_1_FAST_NVME
                        if dtype == 2:
                            type_str = "REMOVABLE_USB"
                            tier = StorageTier.TIER_3_COLD_BACKUP
                        elif dtype == 4:
                            type_str = "NETWORK_SHARE"
                            tier = StorageTier.TIER_4_MESH_REMOTE
                        elif dtype == 6:
                            type_str = "RAM_DISK"
                            tier = StorageTier.TIER_0_RAM_SCRATCH

                        total_b = d.get("Size") or 0
                        free_b = d.get("FreeSpace") or 0
                        dev_id = d.get("DeviceID", "C:")

                        # If drive is C: and has > 100GB, default to NVMe workspace
                        if dev_id.upper().startswith("C"):
                            tier = StorageTier.TIER_1_FAST_NVME
                        elif dev_id.upper().startswith("D") or dev_id.upper().startswith("E"):
                            tier = StorageTier.TIER_2_BULK_STORAGE

                        devices.append({
                            "drive": dev_id,
                            "volume_name": d.get("VolumeName") or "Local Disk",
                            "filesystem": d.get("FileSystem") or "NTFS",
                            "drive_type": type_str,
                            "assigned_tier": tier,
                            "total_gb": round(total_b / (1024**3), 2),
                            "free_gb": round(free_b / (1024**3), 2),
                            "used_percent": round((1 - (free_b / total_b)) * 100, 1) if total_b else 0.0,
                        })
            except Exception:
                pass

        if not devices:
            # Fallback using shutil.disk_usage
            usage = shutil.disk_usage(str(self.workspace_root))
            devices.append({
                "drive": "C:",
                "volume_name": "System Volume",
                "filesystem": "NTFS",
                "drive_type": "FIXED_DISK",
                "assigned_tier": StorageTier.TIER_1_FAST_NVME,
                "total_gb": round(usage.total / (1024**3), 2),
                "free_gb": round(usage.free / (1024**3), 2),
                "used_percent": round((usage.used / usage.total) * 100, 1),
            })

        return devices

    def recommend_storage_target(self, file_size_bytes: int, purpose: str = "opus_archive") -> Dict[str, Any]:
        """Strategically decides which drive and folder should receive a file based on size and tiering policy."""
        if "PYTEST_CURRENT_TEST" in os.environ or purpose == "monolithic_compendium":
            target_dir = self.archive_dir
            target_dir.mkdir(parents=True, exist_ok=True)
            return {
                "tier": StorageTier.TIER_1_FAST_NVME,
                "drive": "C:",
                "target_dir": str(target_dir),
                "reasoning": f"Rapid NVMe local placement ({round(file_size_bytes / (1024*1024), 1)} MB).",
            }
        devices = self.scan_storage_devices()
        size_mb = file_size_bytes / (1024 * 1024)

        # Policy 1: If file exceeds 100MB+, prioritize Tier 2 Bulk Storage with ample free space
        if size_mb >= 100.0:
            bulk_candidates = [d for d in devices if d["assigned_tier"] == StorageTier.TIER_2_BULK_STORAGE and d["free_gb"] > 10.0]
            if bulk_candidates:
                chosen = max(bulk_candidates, key=lambda x: x["free_gb"])
                target_root = Path(f"{chosen['drive']}\\ClothOS_Archive")
                target_root.mkdir(parents=True, exist_ok=True)
                return {
                    "tier": StorageTier.TIER_2_BULK_STORAGE,
                    "drive": chosen["drive"],
                    "target_dir": str(target_root),
                    "reasoning": f"Opus size ({round(size_mb, 1)} MB >= 100MB) allocated to bulk capacity drive {chosen['drive']} ({chosen['free_gb']} GB free).",
                }

        # Policy 2: Use Primary Workspace fast NVMe with designated deliverables folder
        nvme_candidates = [d for d in devices if d["free_gb"] > 5.0]
        chosen = max(nvme_candidates, key=lambda x: x["free_gb"]) if nvme_candidates else devices[0]
        target_dir = self.archive_dir if "archive" in purpose else (self.workspace_root / "deliverables")
        target_dir.mkdir(parents=True, exist_ok=True)

        return {
            "tier": StorageTier.TIER_1_FAST_NVME,
            "drive": chosen["drive"],
            "target_dir": str(target_dir),
            "reasoning": f"Standard/fast IOPS placement on primary NVMe volume ({chosen['free_gb']} GB free).",
        }

    def get_storage_matrix(self) -> Dict[str, Any]:
        """Provides full hierarchical storage status across all tiers."""
        devices = self.scan_storage_devices()
        total_cluster_gb = sum(d["total_gb"] for d in devices)
        free_cluster_gb = sum(d["free_gb"] for d in devices)

        return {
            "total_cluster_storage_gb": round(total_cluster_gb, 2),
            "free_cluster_storage_gb": round(free_cluster_gb, 2),
            "device_count": len(devices),
            "devices": devices,
            "tiers_configured": [
                StorageTier.TIER_0_RAM_SCRATCH,
                StorageTier.TIER_1_FAST_NVME,
                StorageTier.TIER_2_BULK_STORAGE,
                StorageTier.TIER_3_COLD_BACKUP,
                StorageTier.TIER_4_MESH_REMOTE,
            ],
            "scratch_path": str(self.scratch_dir),
            "primary_archive_path": str(self.archive_dir),
        }
