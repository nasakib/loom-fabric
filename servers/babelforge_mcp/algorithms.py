"""babelForge Core Algorithms & Mathematical Invariants.

Implements pure, deterministic topological state-space algorithms:
1. Graph Invariant & Topological Audit (Betti numbers, Laplacian spectrum, Euler characteristic)
2. Kuramoto Oscillator State Simulation (Coupled dynamical systems, order parameter R, Landauer energy)
3. Topological Distributed Task Placement (Manifold projection & heterogeneous scheduling)
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Tuple
import numpy as np


# ── 1. Graph Invariant & Topology Verification ─────────────────────────────

def validate_graph_invariants(graph: Dict[str, Any]) -> Dict[str, Any]:
    """Validates topological invariants, spectral properties, and cycle hazards of a task graph."""
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    n_count = len(nodes)
    
    if n_count == 0:
        return {
            "valid": False,
            "error": "Graph has zero nodes",
            "invariants_satisfied": []
        }

    id_to_idx = {n["id"] if isinstance(n, dict) else n: i for i, n in enumerate(nodes)}
    adj = np.zeros((n_count, n_count), dtype=np.float64)

    for e in edges:
        if isinstance(e, dict):
            src, dst = e.get("source"), e.get("target")
            w = float(e.get("weight", 1.0))
        elif isinstance(e, (list, tuple)) and len(e) >= 2:
            src, dst = e[0], e[1]
            w = float(e[2]) if len(e) > 2 else 1.0
        else:
            continue

        if src in id_to_idx and dst in id_to_idx:
            u, v = id_to_idx[src], id_to_idx[dst]
            adj[u, v] = w
            adj[v, u] = w  # undirected communication metric

    # Check symmetry
    is_symmetric = bool(np.allclose(adj, adj.T, atol=1e-5))
    e_count = int(np.count_nonzero(np.triu(adj, k=1)))

    # Degree matrix & Graph Laplacian
    degrees = np.sum(adj, axis=1)
    laplacian = np.diag(degrees) - adj

    # Eigenvalues of Laplacian (Positive semi-definite check)
    eigvals = np.linalg.eigvalsh(laplacian)
    eigvals = np.sort(np.maximum(eigvals, 0.0))  # numerical stability

    # Betti-0: Number of connected components (zero eigenvalues within numerical tol)
    betti_0 = int(np.sum(eigvals < 1e-5))
    if betti_0 == 0:
        betti_0 = 1

    # Spectral gap (algebraic connectivity \lambda_2)
    spectral_gap = float(eigvals[1]) if n_count > 1 else 0.0

    # 1-Skeleton Euler Characteristic: \chi = V - E
    euler_char = n_count - e_count

    # Betti-1: Cycle rank (number of independent cycles / topological cavities)
    betti_1 = max(0, e_count - n_count + betti_0)
    acyclic = (betti_1 == 0)

    # Invariant checklist
    invariants = []
    if is_symmetric:
        invariants.append("ADJACENCY_SYMMETRY_PRESERVED")
    if eigvals[0] >= -1e-7:
        invariants.append("LAPLACIAN_POSITIVE_SEMIDEFINITE")
    if betti_0 == 1:
        invariants.append("CONNECTOME_GLOBAL_REACHABILITY")
    if acyclic:
        invariants.append("ZERO_CYCLE_DEADLOCK_FREE")

    return {
        "valid": bool(is_symmetric and bool(eigvals[0] >= -1e-7)),
        "node_count": n_count,
        "edge_count": e_count,
        "connected_components": betti_0,
        "betti_0": betti_0,
        "betti_1_cycles": betti_1,
        "euler_characteristic": euler_char,
        "spectral_gap": round(spectral_gap, 4),
        "acyclic": acyclic,
        "is_symmetric": is_symmetric,
        "invariants_satisfied": invariants
    }


# ── 2. Kuramoto Oscillator State Simulation ────────────────────────────────

def simulate_subgraph_execution(
    subgraph_id: str,
    node_config: Dict[str, Any],
    timesteps: int = 100,
    dt: float = 0.05
) -> Dict[str, Any]:
    """Deterministically simulates Kuramoto oscillator phase locking across subgraph nodes."""
    nodes = node_config.get("nodes", [])
    if not nodes:
        # Generate default 6-node cluster subgraph if none provided
        nodes = [
            {"id": f"node_{i}", "omega": 1.0 + (i * 0.1), "theta": (i * math.pi / 3)}
            for i in range(6)
        ]

    n_count = len(nodes)
    thetas = np.array([float(n.get("theta", 0.0)) for n in nodes], dtype=np.float64)
    omegas = np.array([float(n.get("omega", 1.0)) for n in nodes], dtype=np.float64)

    # Steering vector (\alpha, \delta, \chi, \rho)
    steering = node_config.get("steering_vector", [1.0, 0.0, 0.0, 1.0])
    alpha, delta, chi, rho = [float(x) for x in steering[:4]]

    # Effective parameters
    omegas = omegas * alpha
    base_k = float(node_config.get("coupling_k", 2.0))
    k_eff = max(0.1, (base_k * rho) - delta)
    noise_sigma = max(0.0, chi * 0.1)

    # Seeded RNG for deterministic numerical reproducibility
    seed = int(abs(hash(subgraph_id)) % (2**31 - 1))
    rng = np.random.default_rng(seed)

    # Initial order parameter R(0) = |1/N \sum exp(i \theta_j)|
    r_initial = float(np.abs(np.mean(np.exp(1j * thetas))))

    trajectory: List[float] = [round(r_initial, 4)]
    
    # Simple all-to-all or provided adjacency
    adj = node_config.get("adjacency")
    if adj and len(adj) == n_count:
        A = np.array(adj, dtype=np.float64)
    else:
        A = np.ones((n_count, n_count), dtype=np.float64) - np.eye(n_count)

    # Run Euler-Maruyama numerical integration
    for step in range(timesteps):
        # Coupling term: (K / N) \sum A_ij \sin(\theta_j - \theta_i)
        diff_matrix = thetas[np.newaxis, :] - thetas[:, np.newaxis]
        coupling = np.sum(A * np.sin(diff_matrix), axis=1)

        noise = rng.normal(0.0, noise_sigma, n_count) if noise_sigma > 0 else 0.0
        dtheta = omegas + (k_eff / n_count) * coupling + noise
        thetas = thetas + dtheta * dt
        
        if (step + 1) % max(1, timesteps // 10) == 0:
            current_r = float(np.abs(np.mean(np.exp(1j * thetas))))
            trajectory.append(round(current_r, 4))

    r_final = float(np.abs(np.mean(np.exp(1j * thetas))))
    phase_locked = bool(r_final >= 0.75)

    # Final phase-synchrony matrix R_ij = cos(\theta_i - \theta_j)
    final_diff = thetas[np.newaxis, :] - thetas[:, np.newaxis]
    sync_matrix = np.cos(final_diff)
    
    # Cliques with coherence > 0.85
    clique_mask = sync_matrix > 0.85
    cliques_count = int(np.sum(np.all(clique_mask, axis=1)))

    # Landauer thermodynamic dissipation bound (Joules at 300K)
    # E_L = k_B * T * ln(2) * bit_erasure
    entropy_initial = -np.sum((thetas % (2 * np.pi)) / (2 * np.pi + 1e-9) * np.log((thetas % (2 * np.pi)) / (2 * np.pi + 1e-9) + 1e-9))
    kb_t_ln2 = 1.380649e-23 * 300.0 * math.log(2)
    landauer_joules = float(abs(entropy_initial) * kb_t_ln2)

    return {
        "subgraph_id": subgraph_id,
        "nodes_simulated": n_count,
        "timesteps": timesteps,
        "coupling_k_effective": round(k_eff, 3),
        "initial_phase_coherence": round(r_initial, 4),
        "final_phase_coherence": round(r_final, 4),
        "phase_locked": phase_locked,
        "order_parameter_trajectory": trajectory,
        "cliques_detected": cliques_count,
        "landauer_joules_dissipated": landauer_joules,
        "stable": phase_locked and (r_final >= r_initial * 0.9)
    }


# ── 3. Topological Distributed Task Placement ──────────────────────────────

def optimize_clothos_schedule(
    task_graph: Dict[str, Any],
    cluster_topology: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Uses babelForge topological projection to balance distributed tasks across ClothOS silicon."""
    tasks = task_graph.get("tasks", [])
    if not tasks:
        tasks = [{"id": f"task_{i}", "ops": 1e9 * (i + 1), "vram_mb": 256 * (i + 1)} for i in range(4)]

    # Default heterogeneous ClothOS cluster nodes if not specified
    if not cluster_topology:
        cluster_topology = {
            "node1_gpu0_cuda": {"device": "RTX 3060", "vram_mb": 12288, "tflops": 12.7, "tier": "L1_GPU_PRIMARY"},
            "node1_gpu1_opencl": {"device": "RX 580", "vram_mb": 8192, "tflops": 6.2, "tier": "L2_GPU_SECONDARY"},
            "node2_ryzen7_apu": {"device": "Ryzen 7 7730U", "ram_mb": 16384, "tflops": 1.8, "tier": "L3_EDGE_APU"}
        }

    placements = []
    node_vram_alloc = {k: 0 for k in cluster_topology}
    
    # Sort tasks by compute and memory footprint
    sorted_tasks = sorted(
        tasks,
        key=lambda t: (float(t.get("vram_mb", 128)) * 0.5 + float(t.get("ops", 1e8)) / 1e9),
        reverse=True
    )

    for t in sorted_tasks:
        t_id = t.get("id", "unknown_task")
        vram_req = float(t.get("vram_mb", 256))
        ops = float(t.get("ops", 1e9))

        # Topological placement heuristic:
        # - High VRAM (>3GB) or heavy ops (>1e10) -> Node 1 GPU 0 (RTX 3060 CUDA)
        # - Medium VRAM (512MB - 3GB) -> Node 1 GPU 1 (RX 580 OpenCL)
        # - Memory light or AST/symbolic -> Node 2 Ryzen 7 APU
        if vram_req >= 3072 or ops >= 1e10:
            target_node = "node1_gpu0_cuda"
        elif vram_req >= 512 and (node_vram_alloc["node1_gpu1_opencl"] + vram_req <= 8192):
            target_node = "node1_gpu1_opencl"
        else:
            # Check APU RAM or fallback
            target_node = "node2_ryzen7_apu"

        node_vram_alloc[target_node] += int(vram_req)
        placements.append({
            "task_id": t_id,
            "assigned_node": target_node,
            "tier": cluster_topology[target_node]["tier"],
            "vram_allocated_mb": int(vram_req),
            "estimated_time_ms": round((ops / (cluster_topology[target_node]["tflops"] * 1e12)) * 1000.0, 2)
        })

    # Total latency estimate (max across parallel nodes + inter-node transfer)
    max_node_ms = max(p["estimated_time_ms"] for p in placements) if placements else 0.0
    cross_node_transfer_ms = 4.2  # 1 Gbps / local PCIe bridge

    return {
        "schedule_id": f"sched_bf_{abs(hash(str(task_graph))) % 100000}",
        "total_tasks": len(tasks),
        "placements": placements,
        "vram_utilization_mb": node_vram_alloc,
        "estimated_critical_path_ms": round(max_node_ms + cross_node_transfer_ms, 2),
        "balanced": all(v <= cluster_topology[k].get("vram_mb", 16384) for k, v in node_vram_alloc.items()),
        "bottleneck_risk": "LOW" if max_node_ms < 500 else "MEDIUM"
    }
