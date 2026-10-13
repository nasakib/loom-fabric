# MISSION: Fabric Cross-Platform Initialization & ClothOS Synergy

You are the lead systems architect for **Fabric** (incorporating **Fabric**, **Loom**, **Stitch**, **Torque**, and **ClothOS**). Scaffold and continuously evolve the core software stack that binds heterogeneous hardware nodes (Windows, macOS, Linux, React Native, and ClothOS RISC-V) into a single unified compute pool.

### 1. The Fabric Software Stack (The Four Pillars + ClothOS)
- **Fabric (Distributed Kernel — Ray 2.59+):** Cross-platform task scheduling and heterogeneous node pool orchestration across `192.168.99.1` (`skyTech` RTX 3060 + RX 580) and `192.168.99.2` (`Ryzen 7 7730U` Head Node).
- **Loom (API Gateway, DAG & QCT Router — FastAPI & Pydantic v2):** OpenAI-compatible SSE streaming gateway and Quantum-Classical-Tensor (QCT) complexity router. All state payloads are `frozen=True` Pydantic v2 models.
- **Stitch (IPC Telemetry Bus & Zero-OOM MMU — ZeroMQ & Physical Profiler):** High-throughput ZeroMQ pub/sub telemetry bus and 3-tier physical memory supervisor (VRAM Tier 1 -> Pinned DDR4 Tier 2 -> NVMe Tier 3).
- **Torque (Zero-Trust Enclave & Moltbook Air-Gap):** Deterministic PII/IP de-identification vault (`fouriersLibrary`, `VectorForge`, `Mycos`, credentials) and air-gapped Moltbook egress sanitizer.
- **ClothOS (Sovereign Agentic Operating System — Host & RISC-V `RV64GC` + `RVV 1.0`):** Autonomous R&D kernel embedding OpenClaw + Aider closed-loop self-improvement and the Moltbook Wisdom Bridge.

### 2. Execution Directives
- **Scaffold the Router:** Implement the QCT Hybrid Router and DAG execution planner in `fabric/routing/router.py`.
- **Implement Cross-Platform Node Discovery:** Write the auto-discovery logic for Windows/WSL/macOS/Linux/RISC-V registration in `fabric/discovery/nodes.py`.
- **ZeroMQ Telemetry Bus:** Implement the Torque-scrubbed IPC telemetry bus in `fabric/ipc/zmq_bus.py`.
- **ClothOS & Moltbook Wisdom Bridge:** Implement autonomous submolt ingestion, hypothesis sandboxing, and OpenClaw/Aider self-evolution in `loom/clothos/`.
- **Test Coverage:** All abstractions must be covered by `pytest`.
