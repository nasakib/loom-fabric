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
- [ ] **AD-010**: Maintain and monitor live cluster operations, background Moltbook wisdom ingestion, and ClothOS unikernel migration preparations.
