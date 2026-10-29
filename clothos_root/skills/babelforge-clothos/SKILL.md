---
name: babelforge-clothos
description: Guides the design, scheduling, compilation, and validation of distributed ClothOS workloads utilizing babelForge algorithms and topological state-space simulations.
---

# babelForge-ClothOS Orchestration Skill

This skill guides the design, topological decomposition, distributed scheduling, and programmatic verification of ClothOS workloads using babelForge dynamical systems and algebraic topology.

## When to Use

Trigger this skill whenever:
- Designing or routing a multi-node distributed task graph across Node 1 (RTX 3060 CUDA + RX 580 OpenCL) and Node 2 (Ryzen 7 APU).
- Simulating oscillator synchronization, clock phase locking, or worker consensus using the Kuramoto model.
- Validating acyclic guarantees, clique densities, or cavity hazards in ClothOS execution DAGs.
- Tuning task execution cadence with 4D steering vectors $(\alpha, \delta, \chi, \rho)$.

---

## Operational Workflow

```mermaid
flowchart LR
    A["Stage 1: Pre-check"] --> B["Stage 2: Mapping & Lowering"] --> C["Stage 3: Verification"]
```

### Stage 1: Pre-check (Topological Invariants & Hardware Constraints)
Before scheduling or compiling:
1. **Node Topology Verification**:
   - Inspect cluster VRAM and compute tiers: Node 1 (12GB CUDA + 8GB OpenCL = 20GB VRAM), Node 2 (16 vCPU threads + 16GB RAM).
   - Verify that communication latency between nodes does not exceed the critical phase-locking threshold ($K_{\text{crit}} \ge \frac{2}{\pi g(0)}$).
2. **Graph Invariant Audit**:
   - Call `validate_graph_invariants` to ensure the task graph is well-formed, connected, and contains no non-contractible topological cavities (Betti-1 cycle hazards).

### Stage 2: Mapping & Lowering (babelForge Projection)
1. **State-Space Embedding**:
   - Map each ClothOS subtask into a coordinate manifold $\mathcal{M}$ where distance reflects tensor transfer overhead.
   - Set intrinsic frequencies $\omega_i$ based on FLOP/s capacity of target accelerators.
2. **Topological Partitioning**:
   - Lower the high-level DAG into distributed subgraphs via Vietoris-Rips clique extraction ($\tau = 0.75$).
   - High-coherence cliques are assigned to shared memory/PCIe on Node 1; decoupled subgraphs are hoisted to Node 2 over Ray/ZeroMQ.
3. **Schedule Optimization**:
   - Call `optimize_clothos_schedule(task_graph, cluster_topology)` to balance memory footprint and minimize communication delay.

### Stage 3: Verification & Execution
1. **Simulation Sweep**:
   - Call `simulate_subgraph_execution(subgraph_id, node_config, timesteps=100)` to deterministically verify numerical convergence, Landauer dissipation, and phase synchrony ($R > 0.80$).
2. **Zero-Regression Ratification**:
   - If simulation passes, commit the verified plan to ClothOS ProcessManager and dispatch execution.
   - Store the ratified invariant into `CrystallizedMemoryVault`.

---

## Tool Reference

| MCP Tool | Purpose | Primary Argument |
| :--- | :--- | :--- |
| `validate_graph_invariants` | Checks graph symmetry, positive semi-definiteness, and Betti numbers. | `graph_json` |
| `simulate_subgraph_execution` | Deterministic Kuramoto phase simulation of execution stability. | `subgraph_id`, `node_config`, `timesteps` |
| `optimize_clothos_schedule` | Topological routing and balanced hardware node assignment. | `task_graph`, `cluster_topology` |
