# Fabric // ClothOS Agentic Operating System

**CONFIDENTIAL & PROPRIETARY — Copyright (c) 2026 Najmos Sakib. All Rights Reserved.**  
*Operated by **BRAND** under the sovereign umbrella of **VectorCore Holdings, LLC (Georgia LLC)**.*  
*Governed strictly by the [Proprietary and Commercial Source Code License](LICENSE). Unauthorized copying, distribution, SaaS hosting, or reverse engineering is strictly prohibited.*

---

## 1. Overview & Sovereign Identity

**ClothOS** is the **wearable operating system for AGI**, developed and commercialized by **BRAND** under **VectorCore Holdings, LLC**. Rather than treating artificial intelligence as a disembodied software script querying an API in the cloud, ClothOS provides the somatic nervous system that connects cognition to physical and future silicon substrates:

1. **Heterogeneous Silicon Proprioception (`DualGPURunner`, `HardwareProfiler`)**: Automatically discovers and pools discrete GPUs across vendors (Node 1 NVIDIA RTX 3060 12GB CUDA + AMD RX 580 8GB OpenCL/Vulkan), dynamically computing model layer partitions based on live empirical bandwidth.
2. **Polymorphic Radix Engine (`loom/clothos/polymorphic_radix.py`)**: Substrate-independent arithmetic engine enabling **Base-12 (Dozenal / Duodecimal)** computing. Eliminates recurring decimal truncation ($1/3 = 0.4_{12}$, $1/4 = 0.3_{12}$, $1/6 = 0.2_{12}$), achieving over **41.5% entropy reduction** in rotary embeddings and attention head slicing.
3. **Progenetic Evolutionary Agent (`loom/clothos/progenetic_agent.py`)**: Software genetics paradigm that compiles execution DAGs into chromosomes (`Codon`, `Gene`, `Chromosome`, `Genome`) and leverages **CRISPR-Cas immune memory** to record, cleave, and prevent fatal execution failures without downtime.
4. **Forward-Compatible Silicon Emulation (`riscv_tpu_emulator.py`)**: Cycle-accurate emulation of RISC-V 64-bit (`RV64GCV`) tightly coupled with Google TPU v5e systolic matrix multiply units (MXU), bounded by Landauer thermodynamic dissipation ($1.2\text{ pJ}/\text{MAC}$).
5. **OpenClaw Tier-1 Autonomous Bridge (`loom/gateway/openclaw_bridge.py`)**: Native buttonary API on port `8002` connecting OpenClaw (acting as the front-end surrogate pilot) directly to ClothOS without requiring manual batch launchers.

---

## 2. Dual-Machine Sovereign Topology

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

## 3. Launching & Interfacing with ClothOS

* **Background Daemon (Auto-Managed):** Runs windowless on port `8002` via `.venv/Scripts/python -m uvicorn loom.gateway.app:app --host 0.0.0.0 --port 8002`.
* **OpenClaw Buttonary Integration:** OpenClaw executes native skills in `~/.openclaw/skills/`:
  - `clothos-agi-status.sh` (Inspects cluster VRAM, GFLOPS, active radix, and TPU status)
  - `clothos-agi-contemplate.sh` (Triggers autonomous Muse/BRAND philosophical contemplation)
  - `clothos-radix-evaluate.sh` (Evaluates Base-12 vs Base-2 entropy for target tensor shapes)
  - `clothos-tpu-simulate.sh` (Executes a systolic wavefront pass on RISC-V TPU)
* **Single-Prompt CLI**: `fabric -p "Your prompt here"`
* **Cluster Health Matrix**: `fabric status`

---

## 4. Role in VectorCore Holdings

**ClothOS** and **Spotlight-Local (sL)** operate harmoniously under the sovereign parent company **VectorCore Holdings, LLC**:
* **ClothOS (BRAND):** Acts as the **decentralized middleman broker** connecting **Compute Service Providers (CSPs)** (gamers, home labs, Mac Pros, solar households) to **Compute Service Consumers (CSCs)** (gamers on budget laptops, 4K/8K video editors, AI agents).
* **Spotlight-Local, Inc. (sL):** Supplies the spatial geohash discovery (`studio`, `uc`, `mycos`), physical NFC avatar proof-of-presence, and in-network double-entry neobanking rails (1.0% platform fee, 99.0% direct host payout in real $ USD).
* Processes the spatial and biometric telemetry streamed by **mycos**.
* Executes the mathematical verification tasks required by **Fourier's Library**.

---

## 5. The Sovereign Compute Brokerage Engine (`loom.csp`)

The `loom.csp` subsystem implements ClothOS's mandate as the sovereign middleman:
* **Heterogeneous Ingestion:** Virtualizes raw silicon across Apple Silicon Metal 3 (macOS), NVIDIA CUDA, AMD ROCm/AMF, Intel QuickSync, and x86/ARM CPUs.
* **Neighborhood Proximity Routing (`/v1/csp/broker/match`):** Matches consumers to nearby nodes by geohash distance with sub-2ms network latency over Wi-Fi 6 Direct or Tailscale point-to-point tunnels.
* **Universal Workloads:** 
  - **AI Inference:** 7B–70B model sharding with Dozenal Base-12 batching and Balanced Ternary triage.
  - **Low-Latency Cloud Gaming:** Translating DirectX 12 calls via D3DMetal/MoltenVK and streaming 4K 120 FPS video from host GPUs to budget integrated graphics laptops.
  - **Remote Video Editing:** Real-time 4:4:4 10-bit HDR scrubbing for DaVinci Resolve and Premiere Pro.
  - **Distributed 3D Render Farms:** Batch frame rendering across neighborhood gaming rigs in Blender and Unreal Engine.
* **Real-Time Streaming Metering (`/v1/csp/meter/summary`):** Microsecond tracking of prompt tokens, completion tokens, TTFT, VRAM allocation, and Landauer energy expenditure ($1.2\text{ pJ}/\text{MAC}$).
* **Spotlight-Local In-Network Settlement (`/v1/csp/broker/settle`):** Reconciles gross compute fees in real dollars ($ USD), applies Spotlight-Local's 1.0% in-network fee, and instantly routes 99.0% net payouts directly to the host's sL debit card/account.

---

## 6. Next Steps & Tactical Roadmap

- [x] **CSP Broker & Streaming Meter Live:** Implemented in `loom.csp` with full REST/SSE endpoints on port 8002.
- [ ] **Physical RISC-V Hardware Target:** Flash ClothOS microkernel to physical RISC-V development boards (e.g. SiFive HiFive, Milk-V Pioneer).
- [ ] **Base-12 Hardware Fixed-Point ALU:** Implement fixed-point duodecimal arithmetic in hardware simulation (Verilog / Chisel).
- [ ] **B2B OEM Licensing Package:** Finalize enterprise documentation for licensing ClothOS to edge device and robotics manufacturers.

---

## License

Copyright (c) 2026 **Najmos Sakib**. All Rights Reserved.  
See [LICENSE](LICENSE) for full commercial and proprietary terms.
