# Fabric // ClothOS Agentic Operating System

**CONFIDENTIAL & PROPRIETARY — Copyright (c) 2026 Najmos Sakib. All Rights Reserved.**  
*Governed strictly by the [Proprietary and Commercial Source Code License](LICENSE). Unauthorized copying, distribution, SaaS hosting, or reverse engineering is strictly prohibited.*

---

**Fabric** unifies five mechanistic pillars into a zero-terminal, cross-platform Sovereign AI Operating System across **Windows**, **macOS**, **Linux**, **WSL2**, **iOS/Android (React Native & PWA)**, and **ClothOS on RISC-V (`RV64GC` + `RVV 1.0`)**:

1. **Fabric (`fabric.discovery`, `loom.fabric`)**: Distributed Ray 2.59+ compute mesh & cross-platform node auto-discovery binding heterogeneous nodes into a unified silicon pool.
2. **Loom (`fabric.routing`, `loom.gateway`)**: FastAPI SSE Gateway (`:8002`), Quantum-Classical-Tensor (`QCTHybridRouter`) complexity scorer, and live 5-stage Directed Acyclic Graph (`DAGExecutionPlan`) planner.
3. **Stitch (`fabric.ipc`, `loom.stitch`)**: High-throughput ZeroMQ IPC telemetry bus (`StitchZMQTelemetryBus`) and 3-tier Zero-OOM Memory Management Unit (Tier-1 VRAM $\rightarrow$ Tier-2 DDR4 RAM $\rightarrow$ Tier-3 NVMe).
4. **Torque (`loom.torque`)**: Zero-Trust security enclave enforcing strict `ConfigDict(frozen=True)` Pydantic v2 immutability, synthetic `<<ENCLAVE_VAR_N>>` vault tokenization, and the `EgressFirewall` air-gap.
5. **ClothOS & Moltbook Bridge (`loom.clothos`, `platforms/clothos-riscv`)**: Agentic OS kernel with persistent state, air-gapped Moltbook R&D submolt ingestion, `.agent/STATUS.md` synchronization, OpenClaw $\rightarrow$ Aider self-evolution, and native RISC-V `RV64GC + RVV 1.0 + PMP CSR 0x9B` support.

---

## Dual-Machine Sovereign Topology

```text
[ Head Node: Ryzen 7 7730U ] (IP: 192.168.99.2)
  ├── OS: Windows 11 / WSL2 Ubuntu
  ├── Compute: 16 vCPUs (Zen 3), 32 GB RAM + Radeon 680M
  └── Services (Windowless Background):
       ├── Ray Cluster Head (GCS: 6379, Dashboard: 8265)
       ├── Fabric Gateway & Web UI (Port 8002)
       ├── The Shuttle PWA & Bridge (Port 5555)
       └── OpenClaw Autonomous Orchestrator (Port 18789)
           │
           ▼ [ 192.168.99.x Direct-Wire Ethernet Fabric ]
           │
[ Worker Node: skyTech Dual-GPU Desktop ] (IP: 192.168.99.1)
  ├── OS: Windows 11 / WSL2 Ubuntu
  ├── Host Memory: 64 GB DDR4
  ├── GPU 0: NVIDIA GeForce RTX 3060 12GB GDDR6 (CUDA)
  ├── GPU 1: AMD Radeon RX 580 2048SP 8GB GDDR5 (Vulkan)
  └── Services (Windowless Background):
       ├── Fabric Gateway & Web UI (Port 8002)
       ├── The Shuttle PWA & Bridge (Port 5555)
       ├── Ollama Multi-GPU Tensor Engine (Port 11434)
       └── OpenClaw Worker Daemon (Port 18789)
```

---

## Launching Fabric

- **Desktop App (Windows / macOS / Linux)**: Double-click **`Start-Fabric.bat`** on the Desktop (or run `fabric gui`).
- **Single-Prompt CLI**: `fabric -p "Your prompt here"`
- **Cluster Health & Port Matrix**: `fabric status`
- **ClothOS DAG & Moltbook R&D Synergy**: `fabric synergy`

---

## License

Copyright (c) 2026 **Najmos Sakib**. All Rights Reserved.  
See [LICENSE](LICENSE) for full commercial and proprietary terms.
