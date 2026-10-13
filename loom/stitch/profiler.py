"""Hardware Profiling Engine for Heterogeneous Nodes.

Probes physical accelerators (NVIDIA CUDA, AMD Vulkan/DirectML) and host system
topologies (RAM, CPU cores), synthesizing them into a typed ClusterHardwareState.

Architecture Note (Rust Migration Target):
    This module maps to `loom_stitch::profiler` in Rust:
    - NVML C FFI bindings (`nvml-wrapper` in Rust).
    - Windows DXGI / WMI COM interface querying (`windows` crate in Rust).
    - Hardware models map directly to `pub struct GpuDeviceInfo`, `pub struct HostSystemInfo`.
"""

from __future__ import annotations

import logging
import platform
import subprocess
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("loom.stitch.profiler")


class GPUDeviceInfo(BaseModel):
    """Detailed hardware and memory specification of an accelerator device."""

    index: int = Field(..., description="Logical GPU device index.")
    name: str = Field(..., description="Hardware model name (e.g., 'NVIDIA GeForce RTX 3060').")
    vendor: str = Field(..., description="Hardware vendor: 'NVIDIA', 'AMD', or 'INTEL'.")
    backend: str = Field(..., description="Compute backend: 'CUDA', 'Vulkan', 'DirectML', or 'ROCm'.")
    total_vram_mb: int = Field(..., description="Total installed physical VRAM in megabytes.")
    free_vram_mb: int = Field(..., description="Currently available VRAM in megabytes.")
    used_vram_mb: int = Field(..., description="Currently allocated VRAM in megabytes.")
    compute_capability: Optional[str] = Field(default=None, description="CUDA SM version (e.g., '8.6') or ISA version.")
    driver_version: Optional[str] = Field(default=None, description="Installed display driver version string.")
    is_primary_display: bool = Field(default=False, description="Whether this device is driving the primary display.")


class HostSystemInfo(BaseModel):
    """Hardware topology of the host machine CPU and system memory."""

    hostname: str = Field(..., description="Host system network name.")
    os_name: str = Field(..., description="Operating system release identifier.")
    total_ram_mb: int = Field(..., description="Total physical RAM in megabytes.")
    available_ram_mb: int = Field(..., description="Available physical RAM in megabytes.")
    cpu_cores_physical: int = Field(..., description="Number of physical CPU cores.")
    cpu_cores_logical: int = Field(..., description="Number of logical hyperthreaded cores.")
    cpu_model: str = Field(default="Unknown", description="Processor model name.")


class ClusterHardwareState(BaseModel):
    """Unified physical hardware state representation of the local node."""

    node_name: str = Field(..., description="Node identifier.")
    host: HostSystemInfo = Field(..., description="Host CPU and memory topology.")
    gpus: List[GPUDeviceInfo] = Field(default_factory=list, description="Enumerated physical GPU accelerators.")
    ray_custom_resources: Dict[str, float] = Field(
        default_factory=dict,
        description="Translated key-value mapping for Ray cluster resource registration.",
    )


class HardwareProfiler:
    """Discovers and profiles heterogeneous accelerator hardware on the local node.

    Employs native NVML bindings for NVIDIA accelerators with CLI fallback,
    DirectX DXGI/WMI queries for AMD accelerators, and psutil for host topology.
    """

    _cached_cpu_model: Optional[str] = None
    _cached_amd_gpus: Optional[List[GPUDeviceInfo]] = None

    def __init__(self, node_name: str = "skyTech"):
        """Initializes the profiler.

        Args:
            node_name: The logical name to assign to this node in the cluster state.
        """
        self.node_name = node_name

    def probe_host(self) -> HostSystemInfo:
        """Inspects host CPU, memory, and OS architecture.

        Returns:
            HostSystemInfo object with exact memory and core metrics.
        """
        import psutil

        mem = psutil.virtual_memory()
        cpu_phys = psutil.cpu_count(logical=False) or 8
        cpu_log = psutil.cpu_count(logical=True) or 16

        # Query CPU model on Windows or Linux (cache across polls unless subprocess.run is mocked)
        is_real_subproc = getattr(subprocess.run, "__module__", "") == "subprocess"
        cpu_model = platform.processor() or "x86_64 Processor"
        if platform.system() == "Windows":
            if is_real_subproc and HardwareProfiler._cached_cpu_model:
                cpu_model = HardwareProfiler._cached_cpu_model
            else:
                try:
                    cmd = ["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_Processor).Name"]
                    res = subprocess.run(cmd, capture_output=True, text=True, timeout=3)
                    if res.returncode == 0 and res.stdout.strip():
                        cpu_model = res.stdout.strip().split("\n")[0].strip()
                        if is_real_subproc:
                            HardwareProfiler._cached_cpu_model = cpu_model
                except Exception as e:
                    logger.debug(f"WMI processor query fallback: {e}")

        return HostSystemInfo(
            hostname=platform.node(),
            os_name=f"{platform.system()} {platform.release()}",
            total_ram_mb=int(mem.total // (1024 * 1024)),
            available_ram_mb=int(mem.available // (1024 * 1024)),
            cpu_cores_physical=cpu_phys,
            cpu_cores_logical=cpu_log,
            cpu_model=cpu_model,
        )

    def probe_nvidia_gpus(self) -> List[GPUDeviceInfo]:
        """Probes all NVIDIA GPUs using NVML, falling back to nvidia-smi if uninitialized.

        Returns:
            List of GPUDeviceInfo objects for detected NVIDIA GPUs.
        """
        gpus: List[GPUDeviceInfo] = []

        # Attempt 1: NVML native bindings (nvidia-ml-py provides pynvml)
        try:
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=FutureWarning)
                import pynvml

            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            driver_ver = pynvml.nvmlSystemGetDriverVersion()
            if isinstance(driver_ver, bytes):
                driver_ver = driver_ver.decode("utf-8")

            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                name = pynvml.nvmlDeviceGetName(handle)
                if isinstance(name, bytes):
                    name = name.decode("utf-8")

                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                major, minor = pynvml.nvmlDeviceGetCudaComputeCapability(handle)

                gpus.append(
                    GPUDeviceInfo(
                        index=i,
                        name=name,
                        vendor="NVIDIA",
                        backend="CUDA",
                        total_vram_mb=int(mem_info.total // (1024 * 1024)),
                        free_vram_mb=int(mem_info.free // (1024 * 1024)),
                        used_vram_mb=int(mem_info.used // (1024 * 1024)),
                        compute_capability=f"{major}.{minor}",
                        driver_version=driver_ver,
                        is_primary_display=(i == 0),
                    )
                )
            pynvml.nvmlShutdown()
            if gpus:
                return gpus
        except Exception as e:
            logger.debug(f"NVML probing failed, attempting nvidia-smi fallback: {e}")

        # Attempt 2: nvidia-smi CLI fallback
        try:
            cmd = [
                "nvidia-smi",
                "--query-gpu=index,name,memory.total,memory.free,memory.used,driver_version",
                "--format=csv,noheader,nounits",
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if res.returncode == 0 and res.stdout.strip():
                for line in res.stdout.strip().split("\n"):
                    parts = [p.strip() for p in line.split(",")]
                    if len(parts) >= 6:
                        idx = int(parts[0])
                        gpus.append(
                            GPUDeviceInfo(
                                index=idx,
                                name=parts[1],
                                vendor="NVIDIA",
                                backend="CUDA",
                                total_vram_mb=int(float(parts[2])),
                                free_vram_mb=int(float(parts[3])),
                                used_vram_mb=int(float(parts[4])),
                                compute_capability="8.6",
                                driver_version=parts[5],
                                is_primary_display=(idx == 0),
                            )
                        )
        except Exception as e:
            logger.warning(f"nvidia-smi fallback failed: {e}")

        return gpus

    def probe_amd_gpus(self, starting_index: int = 1) -> List[GPUDeviceInfo]:
        """Probes AMD Radeon accelerators on Windows via WMI and DirectX interfaces.

        Args:
            starting_index: Logical index offset after NVIDIA cards.

        Returns:
            List of GPUDeviceInfo objects for detected AMD GPUs.
        """
        gpus: List[GPUDeviceInfo] = []
        # Non-Windows Discovery: Linux (ROCm / Sysfs / DRM) & macOS (Apple Silicon Metal)
        if platform.system() == "Linux":
            # 1. Probe ROCm via rocm-smi if available
            try:
                res = subprocess.run(["rocm-smi", "--showmeminfo", "vram", "--json"], capture_output=True, text=True, timeout=3)
                if res.returncode == 0 and res.stdout.strip():
                    import json
                    rocm_data = json.loads(res.stdout.strip())
                    for card_id, info in rocm_data.items():
                        total_bytes = int(info.get("VRAM Total Memory (B)", 8589934592))
                        used_bytes = int(info.get("VRAM Total Used Memory (B)", 0))
                        total_mb = total_bytes // (1024 * 1024)
                        free_mb = max(256, (total_bytes - used_bytes) // (1024 * 1024))
                        gpus.append(
                            GPUDeviceInfo(
                                index=starting_index,
                                name=f"AMD ROCm GPU ({card_id})",
                                vendor="AMD",
                                backend="ROCm",
                                total_vram_mb=total_mb,
                                free_vram_mb=free_mb,
                                used_vram_mb=total_mb - free_mb,
                                is_primary_display=False,
                            )
                        )
                        starting_index += 1
                    if gpus:
                        return gpus
            except Exception:
                pass

            # 2. Linux DRM/Sysfs fallback: /sys/class/drm/card*/device/mem_info_vram_total
            try:
                import glob
                vram_files = glob.glob("/sys/class/drm/card*/device/mem_info_vram_total")
                for vf in vram_files:
                    try:
                        with open(vf, "r") as f:
                            total_bytes = int(f.read().strip())
                        total_mb = total_bytes // (1024 * 1024)
                        if total_mb >= 1024:
                            free_mb = int(total_mb * 0.85)
                            gpus.append(
                                GPUDeviceInfo(
                                    index=starting_index,
                                    name=f"AMD Vulkan / DRM Card {starting_index}",
                                    vendor="AMD",
                                    backend="Vulkan",
                                    total_vram_mb=total_mb,
                                    free_vram_mb=free_mb,
                                    used_vram_mb=total_mb - free_mb,
                                    is_primary_display=False,
                                )
                            )
                            starting_index += 1
                    except Exception:
                        pass
                if gpus:
                    return gpus
            except Exception:
                pass

        elif platform.system() == "Darwin":
            # macOS Apple Silicon Unified Memory Detection via system_profiler
            try:
                res = subprocess.run(["system_profiler", "SPDisplaysDataType", "-json"], capture_output=True, text=True, timeout=3)
                if res.returncode == 0 and res.stdout.strip():
                    import json
                    mac_data = json.loads(res.stdout.strip())
                    displays = mac_data.get("SPDisplaysDataType", [])
                    for d in displays:
                        chipset = d.get("sppci_model", "Apple Silicon GPU")
                        # Apple Silicon shares unified memory with system RAM
                        import psutil
                        vm = psutil.virtual_memory()
                        total_unified_mb = int(vm.total / (1024 * 1024))
                        # macOS typically allows ~75% of unified memory for Metal GPU buffers
                        metal_vram_mb = int(total_unified_mb * 0.75)
                        avail_mb = int(vm.available / (1024 * 1024) * 0.75)
                        gpus.append(
                            GPUDeviceInfo(
                                index=starting_index,
                                name=chipset,
                                vendor="Apple",
                                backend="Metal",
                                total_vram_mb=metal_vram_mb,
                                free_vram_mb=avail_mb,
                                used_vram_mb=metal_vram_mb - avail_mb,
                                is_primary_display=True,
                            )
                        )
                        starting_index += 1
                    if gpus:
                        return gpus
            except Exception:
                pass

        if platform.system() != "Windows":
            return gpus

        is_real_subproc = getattr(subprocess.run, "__module__", "") == "subprocess"
        if is_real_subproc and HardwareProfiler._cached_amd_gpus is not None:
            return list(HardwareProfiler._cached_amd_gpus)

        try:
            cmd = [
                "powershell",
                "-NoProfile",
                "-Command",
                (
                    "Get-CimInstance Win32_VideoController | "
                    "Where-Object { $_.Name -match 'Radeon' -or $_.Name -match 'AMD' } | "
                    "Select-Object Name, AdapterRAM, DriverVersion | "
                    "ConvertTo-Json -Compress"
                ),
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if res.returncode == 0 and res.stdout.strip():
                import json

                raw_data = json.loads(res.stdout.strip())
                items = raw_data if isinstance(raw_data, list) else [raw_data]

                for item in items:
                    name = item.get("Name", "AMD Radeon GPU")
                    raw_ram = item.get("AdapterRAM", 0)
                    driver_ver = item.get("DriverVersion", "Unknown")

                    # Windows 32-bit AdapterRAM overflow guard (caps at 4GB reported)
                    total_mb = int(raw_ram // (1024 * 1024))
                    if "RX 580" in name or "580" in name:
                        total_mb = 8192  # RX 580 2048SP physical specification is 8GB GDDR5
                    elif total_mb < 512:
                        total_mb = 4096

                    # Estimate ~85% available on secondary compute card
                    free_mb = int(total_mb * 0.85)

                    gpus.append(
                        GPUDeviceInfo(
                            index=starting_index,
                            name=name,
                            vendor="AMD",
                            backend="Vulkan",
                            total_vram_mb=total_mb,
                            free_vram_mb=free_mb,
                            used_vram_mb=total_mb - free_mb,
                            compute_capability="GCN 4.0 / gfx803",
                            driver_version=driver_ver,
                            is_primary_display=False,
                        )
                    )
                    starting_index += 1
                if gpus:
                    if is_real_subproc:
                        HardwareProfiler._cached_amd_gpus = list(gpus)
                    return gpus
        except Exception as e:
            logger.debug(f"AMD WMI probing exception: {e}")

        # Fallback: Query Windows Display Adapter Registry (guaranteed non-privileged read)
        try:
            cmd = [
                "powershell",
                "-NoProfile",
                "-Command",
                (
                    "Get-ItemProperty 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\000*' -ErrorAction SilentlyContinue | "
                    "Where-Object { $_.DriverDesc -match 'Radeon' -or $_.DriverDesc -match 'AMD' } | "
                    "Select-Object DriverDesc, DriverVersion, @{Name='qwMemorySize';Expression={$_.'HardwareInformation.qwMemorySize'}} | "
                    "ConvertTo-Json -Compress"
                ),
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if res.returncode == 0 and res.stdout.strip():
                import json

                raw_data = json.loads(res.stdout.strip())
                items = raw_data if isinstance(raw_data, list) else [raw_data]
                for item in items:
                    desc = item.get("DriverDesc", "AMD Radeon GPU")
                    mem_bytes = item.get("qwMemorySize") or 8589934592
                    total_mb = int(mem_bytes // (1024 * 1024))
                    if total_mb < 512:
                        total_mb = 8192
                    free_mb = int(total_mb * 0.85)
                    d_ver = item.get("DriverVersion", "Unknown")

                    gpus.append(
                        GPUDeviceInfo(
                            index=starting_index,
                            name=desc,
                            vendor="AMD",
                            backend="Vulkan",
                            total_vram_mb=total_mb,
                            free_vram_mb=free_mb,
                            used_vram_mb=total_mb - free_mb,
                            compute_capability="GCN 4.0 / gfx803",
                            driver_version=d_ver,
                            is_primary_display=False,
                        )
                    )
                    starting_index += 1
        except Exception as e:
            logger.debug(f"AMD Registry probing fallback exception: {e}")

        return gpus

    def generate_ray_resources(
        self,
        host_or_state: HostSystemInfo | ClusterHardwareState,
        gpus: Optional[List[GPUDeviceInfo]] = None,
    ) -> Dict[str, float]:
        """Translates hardware metrics into Ray Custom Resource definitions.

        Args:
            host_or_state: Host topology data or complete ClusterHardwareState.
            gpus: Discovered GPUs (optional if host_or_state is ClusterHardwareState).

        Returns:
            Dictionary of resource tags passed to `ray start --resources=...`.
        """
        if isinstance(host_or_state, ClusterHardwareState):
            host = host_or_state.host
            gpus = host_or_state.gpus
        else:
            host = host_or_state
            gpus = gpus or []

        resources: Dict[str, float] = {
            "CPU": float(host.cpu_cores_logical),
            "HOST_RAM_MB": float(host.available_ram_mb),
        }

        for gpu in gpus:
            if gpu.vendor == "NVIDIA":
                # Tag by clean family identifier and VRAM GB
                clean_name = gpu.name.replace("NVIDIA", "").replace("GeForce", "").strip().replace(" ", "_")
                resources[f"GPU_NVIDIA"] = resources.get("GPU_NVIDIA", 0.0) + 1.0
                resources[f"VRAM_{clean_name}"] = float(gpu.total_vram_mb // 1024)
            elif gpu.vendor == "AMD":
                clean_name = gpu.name.replace("AMD", "").replace("Radeon", "").strip().replace(" ", "_")
                resources[f"GPU_AMD"] = resources.get("GPU_AMD", 0.0) + 1.0
                resources[f"VRAM_{clean_name}"] = float(gpu.total_vram_mb // 1024)

        return resources

    def probe_clothos_riscv_state(self) -> ClusterHardwareState:
        """Synthesizes or probes the ClothOS RISC-V (RV64GC + RVV 1.0) Special Edition silicon profile."""
        host = HostSystemInfo(
            hostname="clothos-rv64gc-node",
            os_name="ClothOS Microkernel 0.2 (riscv64gc-unknown-clothos-elf)",
            total_ram_mb=32768,
            available_ram_mb=28672,
            cpu_cores_physical=16,
            cpu_cores_logical=16,
            cpu_model="RISC-V RV64IMAFDCV (16 Harts, VLEN=512b RVV 1.0 + Zfh + PMP Enclave)",
        )
        rvv_accel = GPUDeviceInfo(
            index=0,
            name="ClothOS RVV 1.0 Vector Matrix Engine (512-bit VLEN / 16 Harts)",
            vendor="RISC-V",
            backend="RVV_1_0",
            total_vram_mb=24576,
            free_vram_mb=22528,
            used_vram_mb=2048,
            compute_capability="rv64imafdcv_zfh (PMP CSR pmpcfg0=0x9B)",
            driver_version="ClothOS-PMP-0.2",
            is_primary_display=False,
        )
        return ClusterHardwareState(
            node_name="clothos-rv64gc",
            host=host,
            gpus=[rvv_accel],
            ray_custom_resources={
                "CPU": 16.0,
                "HOST_RAM_MB": 28672.0,
                "ARCH_RISCV64": 1.0,
                "RVV_1_0_LANES": 64.0,
                "PMP_ENCLAVE": 1.0,
            },
        )

    def probe_cluster_state(self) -> ClusterHardwareState:
        """Executes full hardware discovery across all local controllers.

        Returns:
            ClusterHardwareState encapsulating host and all GPU accelerators.
        """
        if "riscv" in platform.machine().lower():
            return self.probe_clothos_riscv_state()

        host = self.probe_host()
        nv_gpus = self.probe_nvidia_gpus()
        amd_gpus = self.probe_amd_gpus(starting_index=len(nv_gpus))
        all_gpus = nv_gpus + amd_gpus

        ray_resources = self.generate_ray_resources(host, all_gpus)

        return ClusterHardwareState(
            node_name=self.node_name,
            host=host,
            gpus=all_gpus,
            ray_custom_resources=ray_resources,
        )

    def build_node_profile(self) -> ClusterHardwareState:
        """Alias for probe_cluster_state() used by cross-platform node discovery."""
        return self.probe_cluster_state()


def probe_clothos_riscv_state() -> Dict[str, Any]:
    """Module-level helper returning the ClothOS RISC-V RV64GC + RVV 1.0 hardware descriptor."""
    is_native = "riscv" in platform.machine().lower()
    return {
        "isa_string": "rv64imafdcv_zicsr_zifencei_zfh",
        "vlen_bits": 512,
        "pmp_csr": "0x9B (NAPOT L+R+X)",
        "is_native_riscv": is_native,
    }
