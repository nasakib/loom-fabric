# Loom Fabric

**Heterogeneous Distributed AI Compute Fabric with Ray & Native Model Sharding**

Loom Fabric unifies **Loom** (control plane & developer gateway), **Stitch** (heterogeneous VRAM layer allocator & native process supervisor), and **Fabric** (Ray distributed actor orchestrator) into an asymmetric local AI compute cloud.

---

## Architecture Overview

```text
[ Head Node: Ryzen 7 7730U ] (IP: 192.168.99.2)
  ├── OS: Windows 11 / WSL2
  ├── Compute: 16 vCPUs (Zen 3), 32 GB RAM
  └── Roles: 
       ├── Ray Cluster Head (GCS, Redis, Dashboard: 8265)
       ├── Loom Gateway / Reverse Proxy (Port 8000)
       └── Speculative Draft Worker / Embedding Actor (CPU/Vulkan)
           │
           ▼ [ Direct-Wire 1 Gbps / Tailscale P2P Link ]
           │
[ Worker Node: SkyTech GPU Desktop ] (IP: 192.168.99.1)
  ├── OS: Windows 11 Bare-Metal (WDDM 3.x)
  ├── Host Memory: 40 GB DDR4
  ├── GPU 0 (Primary): NVIDIA GeForce RTX 3060 12GB GDDR6 (CUDA 12.x, SM 8.6)
  ├── GPU 1 (Secondary): AMD Radeon RX 580 2048SP 8GB GDDR5 (Vulkan 1.3 / GCN 4.0)
  └── Roles:
       ├── Ray Worker Node (Resources: {"RTX3060": 1, "RX580": 1, "CPU": 8})
       ├── Stitch Shard Executor (llama-server CUDA/Vulkan backend)
       └── Subprocess Process Supervisor (Windows Job Object sandbox)
```

---

## Key Modules

- **`loom.stitch.profiler`**: Hardware detection engine probing NVIDIA (NVML), AMD (WMI/DirectX DXGI), and Host topology (psutil).
- **`loom.stitch.allocator`**: Zero-OOM mathematical layer sharding engine calculating exact VRAM, weight footprint, KV cache budgets, and `llama-server` runtime flags.
- **`loom.stitch.supervisor`**: Native process manager backed by Windows Job Objects for leak-free, clean process tree termination on Windows.
- **`loom.fabric`**: Stateful Ray Actors (`InferenceDirector`, `ShardSupervisor`, `HealthMonitor`) managing distributed cluster execution.
- **`loom.gateway`**: FastAPI OpenAI-compatible proxy (`/v1/chat/completions`) emitting real-time telemetry headers (`X-Loom-Tokens-Per-Sec`, `X-Loom-TTFT-Ms`, `X-Loom-Sharding`).
- **`loom.cli`**: Rich, high-throughput Typer CLI for probing, running, and serving models.
