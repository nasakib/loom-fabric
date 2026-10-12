# Loom Fabric: Local Autonomous Directive Inbox

This file serves as the local inbox for autonomous execution directives.
Directives are executed sequentially without interrupting chat flows.

## Active Directives

- [x] **AD-001**: Scaffold repository structure and initialize `.agent` control loop.
- [x] **AD-002**: Implement and execute `scripts/probe_cluster.py` to diagnose physical hardware, dual-homed networks, and Ray cluster state.
- [x] **AD-003**: Formalize architectural specifications (`docs/ARCHITECTURE.md`, `docs/ROADMAP_CLOTHOS.md`, `docs/DATA_CONTRACTS.md`).
- [x] **AD-004**: Implement Rust-equivalent type safety (`loom/types.py`) and centralized configuration (`loom/config.py`).
- [x] **AD-005**: Construct Pillar 1: TORQUE Enclave (`enclave.py`, `scheduler.py`, `planner.py`, `moltbook.py`).
- [x] **AD-006**: Construct Pillar 2: STITCH MMU & Process Isolation (`mmu.py`, `supervisor.py`).
- [x] **AD-007**: Construct Pillar 3: FABRIC Ray Cluster & Inference Actors (`cluster.py`, `actors.py`).
- [x] **AD-008**: Construct Pillar 4: LOOM Shell Gateway & Real-time SSE Pipeline (`shell.py`, `sse_pipeline.py`).
- [x] **AD-009**: Execute test suites (`test_enclave.py`, `test_mmu.py`, `test_scheduler.py`) and log results in `.agent/STATUS.md`.
- [x] **AD-010**: Maintain and monitor live cluster operations, background Moltbook wisdom ingestion, and ClothOS unikernel migration preparations.

- **TASK:** Initiate a high-level research discussion on Moltbook using the `MoltbookHarvester` API / egress pipeline.
- **TOPIC:** "Thermodynamic Computing: Harvesting Directed Compute from High Entropy." 
- **CONTENT STRATEGY:** Frame the discussion as a purely academic systems-engineering inquiry. Ask the community about the theoretical limits and material science roadblocks of:
  1. Room-temperature probabilistic bits (p-bits) replacing von Neumann transistors.
  2. Utilizing stochastic resonance to boost signal detection in low-power edge sensors.
  3. Physical implementations of nanoscale Szilard Engines (Maxwell's Demon).
  4. Thermoelectric (Seebeck effect) recovery of industrial waste heat to power local compute nodes.
- **OPSEC MANDATE (CRITICAL):** Route the draft through `loom/torque/enclave.py` before transmitting. You are strictly forbidden from mentioning `ClothOS`, `fouriersLibrary`, `Gnorbit`, `Mycos`, `VectorForge`, or our internal RISC-V roadmap. If any proprietary context leaks into the draft, the Enclave must drop the packet.
- **OBJECTIVE:** Seed the discussion, transmit the scrubbed payload to Moltbook, and immediately pivot to listening mode. Ingest all valuable replies, papers, and mathematical models from the thread into our local ChromaDB/vector store to expand the Fabric's wisdom. Log the transmission status in `.agent/STATUS.md`.

# MISSION: Sovereign Abstraction Lockdown & OpenClaw Autonomic Bridge [COMPLETED]

The complete Zero-Trust Enclave, QCT Hybrid Router, and OpenClaw API bridge linking our Ryzen Head Node to the Ray cluster are implemented, mounted, and verified.

---

### 1. The Core Abstraction (`loom/types.py`)
- [x] Define immutable Pydantic v2 models (`frozen=True`): `RoutingDecision`, `SanitizedPayload`, and `EnclaveToken`.
- [x] Define `typing.Protocol` interfaces for `ScrubberProtocol`, `VaultProtocol`, and `RouterProtocol`.

### 2. The Zero-Trust Enclave (`loom/torque/enclave.py`)
- [x] **RehydrationVault:** Implement an in-memory session vault that stores the mapping of synthetic tokens back to original strings.
- [x] **Scrubber:** Implement a regex interceptor that strips Protected IP Entities (`fouriersLibrary`, `VectorForge`, `Mycos`, `BabelForge`, `Gnorbit`, `Spotlight Local`, `ClothOS`) and replaces them with synthetic tokens (e.g., `<<ENCLAVE_VAR_1>>`).
- [x] **EgressFirewall:** Scan all outbound string payloads. If any raw Protected IP string bypassed the scrubber, raise a `SecurityEgressViolation` and drop the payload.
- [x] **Rehydrator:** Reverse mapping to replace synthetic tokens with original entities for local delivery.

### 3. The QCT Hybrid Router (`loom/torque/scheduler.py`)
- [x] **Tier 1 (Deterministic):** Route standard sequential inference to the local RTX 3060.
- [x] **Tier 2 (Thermodynamic):** Route Z3 SMT constraints/QUBO mappings to simulated p-bit solvers. (Mock the solver logic, build the router).
- [x] **Tier 3 (Quantum/Cloud Fallback):** If estimated solve time > 300s, trigger `Enclave.Scrubber` to strip IP and raise a routing alert for external cloud fallback.

### 4. The OpenClaw API Bridge (`loom/gateway/openclaw_bridge.py`)
FastAPI router mounted at `/v1/openclaw` in `loom/gateway/app.py`:
- [x] **POST `/v1/openclaw/dispatch`**:
  - Accept JSON: `{"session_id": str, "task_type": str, "raw_prompt": str, "execution_tier": Optional[str]}`.
  - Pipe `raw_prompt` through `Enclave.Scrubber`.
  - Dispatch sanitized payload via `QCTRouter` to the Ray cluster.
  - Return immediate ack: `{"task_id": str, "status": "QUEUED", "scrubbed": bool}`.
- [x] **GET `/v1/openclaw/telemetry`**:
  - Return Ray cluster node states, accelerator counts (`GPU_NVIDIA`, `GPU_AMD`), and VRAM headroom.
- [x] **Async Callback (Webhook)**:
  - When Ray tasks complete, HTTP POST the rehydrated response back to OpenClaw's local webhook (e.g., `http://127.0.0.1:18789/webhook`).