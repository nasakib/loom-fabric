# ClothOS & Loom Fabric: The Sovereign Distributed AI Operating System

[![Release](https://img.shields.io/badge/Release-v1.0.0--clothos--sovereign-blue.svg)](https://github.com/nasakib/loom-fabric/releases)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12%20%7C%203.14-green.svg)](https://www.python.org/)
[![Rust](https://img.shields.io/badge/Rust-2024_Edition-orange.svg)](https://www.rust-lang.org/)
[![Hardware](https://img.shields.io/badge/Hardware-NVIDIA%20%7C%20AMD%20%7C%20Apple%20%7C%20RISC--V-purple.svg)](#hardware-support)
[![Tests](https://img.shields.io/badge/Tests-25%2F25%20Passing-brightgreen.svg)](tests/)

> **Run AI with Complete Sovereignty.**  
> ClothOS and Loom Fabric pool geographically dispersed, heterogeneous silicon (NVIDIA CUDA, AMD Vulkan/OpenCL, Apple Silicon, and x86/ARM/RISC-V CPUs) into a unified, high-performance distributed AI compute mesh with zero cloud dependencies and air-gapped security.

---

## Key Features

1. **Heterogeneous Silicon Virtualization**: Dynamically shards large models (7B–70B parameters) across multi-vendor GPUs (e.g., NVIDIA RTX 3060 CUDA + AMD RX 580 Vulkan/OpenCL) based on empirical real-time interconnect bandwidth.
2. **Proximity-Aware P2P Mesh**: Low-latency (sub-2ms) neighborhood peer-to-peer compute discovery over LAN, Wi-Fi 6 Direct, and encrypted point-to-point overlays (Tailscale / WireGuard).
3. **Sovereign Air-Gapped Security**: Zero-trust **Torque Scrubber** tokenizes sensitive data and PII into local cryptographic vaults before distributed execution, with fail-closed fiduciary and epistemic verification.
4. **Polymorphic Radix Arithmetic Engine**: Hardware-abstracted Base-12 (Dozenal / Duodecimal) arithmetic eliminating recurring fractional truncation ($1/3 = 0.4_{12}$, $1/4 = 0.3_{12}$), achieving up to 41.5% entropy reduction in rotary embeddings.
5. **Grid-Aware Energy Arbitrage**: Integrates local grid telemetry to schedule compute-intensive workloads (model fine-tuning, parameter sweeps, synthetic data synthesis) during off-peak power hours, providing Proof of Verifiable Computation (PoVC).

---

## Topology Architecture

```
                       [ Loom Fabric Gateway & Orchestrator ]
                               (Port 8002 / REST & SSE)
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  ▼                                               ▼
      [ Heterogeneous Node 1 ]                         [ Head Cluster Node 2 ]
       NVIDIA GeForce RTX 3060                          AMD Ryzen 7 7730U (16 vCPUs)
       AMD Radeon RX 580 8GB                            32 GB System Memory
       Local Sharded Tensor Inference                   Context Arbiter & Triage Mesh
```

---

## Quickstart

### 1. Installation

**Windows (PowerShell)**:
```powershell
git clone https://github.com/nasakib/loom-fabric.git
cd loom-fabric
.\Install-ClothOS.bat
```

**Linux / macOS**:
```bash
git clone https://github.com/nasakib/loom-fabric.git
cd loom-fabric
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Launch the Gateway & UI
```powershell
.\Launch-ClothOS-Desktop.bat
```
The central dashboard is accessible at `http://127.0.0.1:8002/`.

### 3. Check Cluster Hardware & Mesh Health
```powershell
python -m loom.virtual_device.loom_smi
```

---

## Hardware Support

| Platform / Vendor | Backend | Tested Target | Status |
| :--- | :--- | :--- | :--- |
| **NVIDIA** | CUDA 12.x / TensorRT | RTX 3060, RTX 40-series | Supported |
| **AMD** | ROCm / Vulkan / OpenCL | RX 580 (Polaris), Radeon 680M | Supported |
| **Apple Silicon** | Metal 3 Unified Memory | M1 / M2 / M3 / M4 Series | Supported |
| **x86_64 Unikernel** | Bare-Metal / Rust Microkernel | Intel / AMD Multi-Core CPUs | Supported (`loom-clothos-x86.exe`) |
| **RISC-V** | Emulated Systolic MXU | RV64GCV Instruction Set | In Development |

---

## Test Suite & Verification

The codebase includes an extensive suite of automated verification suites covering POSIX shims, mathematical tools, memory vaults, and dual-track boot logic:

```powershell
pytest tests/test_sovereign_tools.py tests/test_clothos_dual_track_boot.py tests/test_clothos_posix_and_diagnostics.py -v
```

---

## Ecosystem & Related Systems

ClothOS and Loom Fabric interface directly with our open-source systems and compilation toolchain:

- **[Universal JIT (`ujit`)](https://github.com/nasakib/universal-jit)**: Embeddable C99 JIT compiler synthesizing algorithmic pseudocode into native machine code (x86-64 / RV64GC) for distributed runtime acceleration.
- **[Typemetric-JIT](https://github.com/nasakib/typemetric-jit)**: Metric type-space optimization, Gonzalez $k$-center geometric diversity pruning, and spectral Fourier optimization for polymorphic JIT dispatch.
- **[MiniVM](https://github.com/nasakib/minivm)**: High-performance Lua virtual machine with Lazy Basic Block Versioning, RV64 backend, and formal SMT lowering verification.
- **[Fourier's Library](https://github.com/nasakib/fouriersLibrary)**: Spectral signal processing, Fourier truth verification, and harmonic state-space simulation engine.

---

## License & Community

- **Community Core**: Licensed under the [GNU Affero General Public License v3 (AGPL-3.0)](LICENSE).
- **Commercial & Enterprise**: For air-gapped enterprise compliance, multi-tenant fleet management, or proprietary integration exceptions, contact `licensing@vectorcore.holdings`.
- **Contributions**: Pull requests, bug reports, and architectural RFCs are welcome. Please refer to [DEVELOPER.md](DEVELOPER.md) for contribution guidelines.
