# Loom Fabric: System Architecture & Subsystem Lifecycle

> **Kernel State**: Precursor to ClothOS (RISC-V Unikernel)  
> **Topology**: Dual-Homed Heterogeneous Connectome (`skyTech` @ 192.168.99.1 & `WIN-7CMAQLVP8MV` @ 192.168.99.2)

---

## 1. Physical Topology & Network Dual-Homing

```
+-----------------------------------------------------------------------------------+
|                              HEAD NODE: 192.168.99.2                              |
|                    AMD Ryzen 7 7730U (16 vCPUs, 32 GB DDR4)                       |
|                                                                                   |
|  [Ray Head: 6379]   [Ray Web: 8265]   [Loom API: 8000/8002]   [Streamlit UI: 8501] |
|  [MoltbookHarvester] [Torque Cascade Router] [Speculative Draft Worker (CPU/Vulkan)]|
+-----------------------------------------------------------------------------------+
                                         |  |
             Direct-Wire 1 Gbps Ethernet |  | Tailscale Encrypted Mesh
             (Primary LAN: 192.168.99.x) |  | (Secondary Fallback)
                                         |  |
+-----------------------------------------------------------------------------------+
|                             WORKER NODE: 192.168.99.1                             |
|               Bare-Metal Windows 11 (Win32 Job Object Process Guard)              |
|                                                                                   |
|  [NVIDIA RTX 3060 12GB (CUDA 12.x)]      [AMD Radeon RX 580 8GB (Vulkan 1.3)]    |
|  40 GB Host DDR4 System RAM               [Stitch Native Execution Server: 5555]  |
|  [Ray Worker Daemon]                      [llama-server Subprocess Sandboxes]     |
+-----------------------------------------------------------------------------------+
```

### Network Dual-Homing & Resiliency Protocol
1. **Primary Route**: Low-latency, direct gigabit socket to `192.168.99.1`.
2. **Failover Route**: If Ethernet cable is disconnected or socket timeout $>1.0\text{s}$, the connection manager transparently fails over to the Tailscale overlay mesh IP.
3. **Graceful Local Fallback**: If both paths are unreachable, the scheduler degrades to local Head Node CPU/APU inference, logs an alert, and attempts a Wake-on-LAN (WoL) broadcast.

---

## 2. The Five Kernel Subsystems

### A. TORQUE: Sovereign Ingress & Cognitive Router
1. **Zero-Trust Enclave**:
   - Cryptographic and pattern-based scrubber detects all PII, keys, and **Protected IP Entities**:
     `fouriersLibrary`, `VectorForge`, `Mycos`, `BabelForge`, `Gnorbit`, `Spotlight Local`, `ClothOS`.
   - Synthetic token mapping: Replaces sensitive tokens with `<<ENCLAVE_VAR_N>>` linked to an ephemeral, in-memory `RehydrationVault`.
   - On-the-fly SSE rehydration transforms outgoing streaming chunks before returning them to client applications.
2. **Cascade Routing & Arbitrage Engine**:
   - **Tier 1 (Instant/Local)**: Single-shot coding and fast reasoning ($\le 12\text{s}$) dispatches to RTX 3060 CUDA (`qwen2.5:7b` / `deepseek-r1:14b`).
   - **Tier 2 (Distributed DAG)**: Multi-step workflows split across Ray Actors on the Head Node and Worker Node (`qwen2.5:32b`).
   - **Tier 3 (Cloud Arbitrage Governor)**: If estimated local execution exceeds **300 seconds** (or requires 70B+ weights), Torque halts execution and requests manual confirmation via the Mission Control UI or webhook. Prompts with `[AIRGAP]` or `[LOCAL]` permanently lock execution to Tier 1/2.

### B. THE MOLTBOOK PROTOCOL: Passive Wisdom Ingress & Zero Egress
- **Passive Wisdom**: `MoltbookHarvester` runs as a non-blocking background Ray Actor crawling and embedding external wisdom into a local vector store.
- **Strict Egress Firewall**: Network filters drop any outbound HTTP/WebSocket frame directed to Moltbook or third-party webhooks if the payload contains Protected IP Entities or unscrubbed secrets. Read-only permitted; write-back prohibited.

### C. STITCH: MMU & Native Process Sandbox
- **Zero-OOM Layer Allocation Formula**:
  $$S_{\text{layer}} = \frac{\text{Model GGUF Size (MB)}}{\text{Total Layers}}$$
  $$KV_{\text{layer}} = 2 \times n_{\text{heads\_kv}} \times d_{\text{head}} \times C \times \text{bytes\_per\_element}$$
  $$\text{Allocated Layers} \le \frac{VRAM_{\text{free}} - VRAM_{\text{reserved}}}{S_{\text{layer}} + KV_{\text{layer}}}$$
  where $VRAM_{\text{reserved}} \ge 1200\text{ MB}$ to account for Windows WDDM and desktop compositing.
- **Subprocess Isolation**:
  - `llama-server` instances are launched inside Win32 Job Objects configured with `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`. When Python terminates or crashes, the OS kernel forcefully reclaims all VRAM within $<50\text{ms}$.

### D. FABRIC: Distributed Ray Mesh
- Heterogeneous accelerator registration:
  - `GPU_NVIDIA`: 12
  - `GPU_AMD`: 8
  - `CPU_HEAD`: 16
- Speculative decoding: Head Node CPU drafts tokens at high throughput, while RTX 3060 verifies candidate tokens in parallel batches.

### E. LOOM: Shell, Gateway & Mission Control
- FastAPI gateway exposing standard `/v1/chat/completions` and `/v1/models` endpoints.
- Injects observability headers: `X-Fabric-Route`, `X-Fabric-TTFT-Ms`, `X-Fabric-Tokens-Per-Sec`, `X-Enclave-Scrubbed`.
- Live SSE pipeline handles streaming token delivery and synchronous rehydration.
