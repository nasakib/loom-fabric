# Copyright (c) 2026 Najmos Sakib / VectorCore Holdings, LLC.
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Decentralized P2P Compute Swarm Engine (`loom/csp/p2p_swarm.py`).
================================================================
Implements a BitTorrent-inspired peer-to-peer compute sharing architecture
connecting Compute Service Providers (CSPs / Seeders) and Compute Service
Consumers (CSCs / Leechers) over ultra-low-latency fiber and wireless meshes.

Features:
- BitTorrent-style Tit-for-Tat incentives and dynamic choking/unchoking.
- Optimistic unchoking for peer discovery and anti-starvation.
- Chunked compute unit distribution (tensor pieces, render tiles, frame buffers).
- Support for heterogeneous transport (Fiber Direct, 60GHz mmWave, Wi-Fi 7).
- Node 2 Purity and Ring P0 root-of-trust adherence.
"""

from __future__ import annotations

import enum
import hashlib
import json
import logging
import random
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("loom.csp.p2p_swarm")


class PeerRole(str, enum.Enum):
    SEEDER = "SEEDER"       # Provides compute cycles, VRAM, and streaming capacity
    LEECHER = "LEECHER"     # Consumes external compute cycles
    HYBRID = "HYBRID"       # Simultaneously seeds idle capacity and leases external bursts


class ConnectionMedium(str, enum.Enum):
    FIBER_DIRECT = "FIBER_DIRECT"         # Fiber optic dedicated link (<1ms latency, 10-100 Gbps)
    MMWAVE_60GHZ = "MMWAVE_60GHZ"         # 60GHz IEEE 802.11ay wireless line-of-sight (1-2ms, 20-40 Gbps)
    WIFI_7 = "WIFI_7"                     # Wi-Fi 7 / 802.11be MLO (2-4ms, 5-10 Gbps)
    OVERLAY_WIREGUARD = "OVERLAY_WIREGUARD" # WireGuard/Tailscale encrypted P2P overlay (5-20ms)


@dataclass
class SwarmPeer:
    """Represents a peer node in the decentralized P2P compute swarm."""
    peer_id: str
    node_name: str
    address: str
    port: int = 8002
    role: PeerRole = PeerRole.SEEDER
    medium: ConnectionMedium = ConnectionMedium.FIBER_DIRECT
    rtt_ms: float = 0.85
    bandwidth_gbps: float = 10.0
    total_vram_gb: float = 12.0
    available_vram_gb: float = 10.0
    capacity_tflops: float = 13.0
    hardware_desc: str = "NVIDIA RTX 3060 12GB"
    is_pure_amd: bool = False             # True if node strictly runs pure AMD/open stack (Node 2)
    is_solar_powered: bool = False
    
    # Tit-for-Tat state
    is_choked: bool = True                 # If True, peer is temporarily choked (throttled)
    is_interested: bool = False           # If True, peer wants compute from this node
    optimistically_unchoked: bool = False  # Selected in current exploration round
    
    # Cumulative compute ledger (for Tit-for-Tat contribution ratio)
    uploaded_compute_units: float = 0.0   # Total compute units provided to the swarm
    downloaded_compute_units: float = 0.0 # Total compute units consumed from the swarm
    reputation_score: float = 1.0         # 0.0 to 1.0 based on reliability and uptime
    last_seen_epoch: float = field(default_factory=time.time)

    @property
    def contribution_ratio(self) -> float:
        """BitTorrent tit-for-tat ratio: seeded / leased (Xi factor)."""
        eps = 1e-4
        return (self.uploaded_compute_units + eps) / (self.downloaded_compute_units + eps)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "peer_id": self.peer_id,
            "node_name": self.node_name,
            "address": f"{self.address}:{self.port}",
            "role": self.role.value,
            "medium": self.medium.value,
            "rtt_ms": round(self.rtt_ms, 2),
            "bandwidth_gbps": round(self.bandwidth_gbps, 1),
            "available_vram_gb": round(self.available_vram_gb, 1),
            "capacity_tflops": round(self.capacity_tflops, 1),
            "hardware": self.hardware_desc,
            "pure_amd": self.is_pure_amd,
            "is_choked": self.is_choked,
            "optimistically_unchoked": self.optimistically_unchoked,
            "contribution_ratio": round(self.contribution_ratio, 3),
            "reputation": round(self.reputation_score, 2),
        }


@dataclass
class ComputePiece:
    """
    A chunked unit of work distributed across the swarm, analogous to a BitTorrent piece.
    """
    piece_index: int
    task_id: str
    workload_type: str                   # "tensor_shard", "inference_layer", "render_tile", "gaming_frame"
    payload: Any
    input_payload_hash: str
    expected_tflops: float = 1.0
    assigned_peer_id: Optional[str] = None
    is_completed: bool = False
    result_data: Optional[Any] = None
    result_checksum: Optional[str] = None
    execution_time_ms: float = 0.0

    @classmethod
    def create(cls, piece_index: int, task_id: str, workload_type: str, payload: Any, expected_tflops: float = 1.0) -> ComputePiece:
        payload_bytes = json.dumps(payload, default=str).encode("utf-8") if not isinstance(payload, bytes) else payload
        h = hashlib.sha256(payload_bytes).hexdigest()[:16]
        return cls(
            piece_index=piece_index,
            task_id=task_id,
            workload_type=workload_type,
            payload=payload,
            input_payload_hash=h,
            expected_tflops=expected_tflops,
        )


class TitForTatEngine:
    """
    Implements dynamic BitTorrent-style choking and unchoking for compute peers.
    Rewards peers who seed high throughput/low latency compute, while continuously
    exploring the mesh via optimistic unchoking.
    """

    def __init__(self, top_k_unchoked: int = 4, optimistic_interval_rounds: int = 3):
        self.top_k_unchoked = top_k_unchoked
        self.optimistic_interval_rounds = optimistic_interval_rounds
        self.round_counter: int = 0
        self.currently_optimistic_peer_id: Optional[str] = None

    def evaluate_swarm(self, peers: Dict[str, SwarmPeer]) -> Dict[str, bool]:
        """
        Executes a Tit-for-Tat evaluation round across all peers.
        Returns mapping: peer_id -> is_choked.
        """
        self.round_counter += 1
        active_peers = [p for p in peers.values() if time.time() - p.last_seen_epoch < 60.0]
        if not active_peers:
            return {}

        # Reset optimistic states
        for p in active_peers:
            p.optimistically_unchoked = False

        # Rank peers by combination of contribution ratio, available bandwidth, and low RTT
        # Score = (contribution_ratio * 0.4) + (bandwidth_gbps / max(0.1, rtt_ms) * 0.4) + (reputation * 0.2)
        def peer_score(p: SwarmPeer) -> float:
            latency_factor = max(0.1, p.rtt_ms)
            bw_ratio = p.bandwidth_gbps / latency_factor
            return (p.contribution_ratio * 0.4) + (bw_ratio * 0.4) + (p.reputation_score * 0.2)

        sorted_peers = sorted(active_peers, key=peer_score, reverse=True)

        # Unchoke top-K peers
        unchoked_ids = set()
        for p in sorted_peers[: self.top_k_unchoked]:
            p.is_choked = False
            unchoked_ids.add(p.peer_id)

        # Optimistic unchoking: Pick one choked peer at random every N rounds
        candidates_for_optimistic = [p for p in sorted_peers[self.top_k_unchoked :] if p.peer_id not in unchoked_ids]
        if candidates_for_optimistic:
            if self.round_counter % self.optimistic_interval_rounds == 0 or not self.currently_optimistic_peer_id:
                chosen = random.choice(candidates_for_optimistic)
                self.currently_optimistic_peer_id = chosen.peer_id
            
            # Apply optimistic unchoke if chosen candidate is still present
            for p in candidates_for_optimistic:
                if p.peer_id == self.currently_optimistic_peer_id:
                    p.is_choked = False
                    p.optimistically_unchoked = True
                    unchoked_ids.add(p.peer_id)
                    break

        # Choke all others
        for p in active_peers:
            if p.peer_id not in unchoked_ids:
                p.is_choked = True

        return {p.peer_id: p.is_choked for p in active_peers}


class P2PComputeSwarm:
    """
    Decentralized P2P Compute Swarm Coordinator.
    Manages peers, DHT-based proximity matching, task piece sharding, and Tit-for-Tat routing.
    """

    def __init__(self, local_node_id: str = "skyTech-Worker", local_node_name: str = "skyTech-Rig-01"):
        self.local_node_id = local_node_id
        self.local_node_name = local_node_name
        self.peers: Dict[str, SwarmPeer] = {}
        self.tit_for_tat = TitForTatEngine()
        self._initialize_default_mesh()

    def _initialize_default_mesh(self) -> None:
        """Seeds the local neighborhood fabric mesh (Fiber, 60GHz, and local nodes)."""
        # Node 1 (Local Worker / Seeder): RTX 3060 12GB + RX 580 8GB
        self.register_peer(
            SwarmPeer(
                peer_id="LoomMesh-SkyTech",
                node_name="skyTech-Worker",
                address="192.168.99.1",
                port=8002,
                role=PeerRole.SEEDER,
                medium=ConnectionMedium.FIBER_DIRECT,
                rtt_ms=0.25,
                bandwidth_gbps=10.0,
                total_vram_gb=12.0,
                available_vram_gb=10.5,
                capacity_tflops=13.0,
                hardware_desc="NVIDIA RTX 3060 12GB CUDA (GA106)",
                is_pure_amd=False,
                uploaded_compute_units=150.0,
                downloaded_compute_units=40.0,
            )
        )
        # Node 2 (Remote Head Node): AMD Ryzen 7 7730U + Vega 8 (Pure AMD / Node 2 Purity)
        self.register_peer(
            SwarmPeer(
                peer_id="LoomMesh-Ryzen7",
                node_name="Ryzen7-Head",
                address="192.168.99.2",
                port=8002,
                role=PeerRole.HYBRID,
                medium=ConnectionMedium.FIBER_DIRECT,
                rtt_ms=0.45,
                bandwidth_gbps=10.0,
                total_vram_gb=16.0,
                available_vram_gb=14.0,
                capacity_tflops=6.5,
                hardware_desc="AMD Ryzen 7 7730U 16-Th + Radeon Vega 8 (ROCm/Vulkan)",
                is_pure_amd=True,
                uploaded_compute_units=110.0,
                downloaded_compute_units=85.0,
            )
        )
        # Proximity Neighborhood High-Bandwidth Fiber Seeder (e.g. Neighboring Creator / Gamer Rig)
        self.register_peer(
            SwarmPeer(
                peer_id="LoomMesh-FiberNeighbor-01",
                node_name="inman-park-fiber-rig",
                address="192.168.99.15",
                port=8002,
                role=PeerRole.SEEDER,
                medium=ConnectionMedium.FIBER_DIRECT,
                rtt_ms=0.92,
                bandwidth_gbps=25.0,
                total_vram_gb=24.0,
                available_vram_gb=22.0,
                capacity_tflops=35.0,
                hardware_desc="NVIDIA RTX 4090 24GB (Fiber Low-Latency)",
                is_pure_amd=False,
                uploaded_compute_units=320.0,
                downloaded_compute_units=15.0,
            )
        )
        # Neighborhood 60GHz mmWave Seeder (Wireless Line of Sight)
        self.register_peer(
            SwarmPeer(
                peer_id="LoomMesh-mmWave-Rooftop",
                node_name="rooftop-60ghz-station",
                address="192.168.99.40",
                port=8002,
                role=PeerRole.HYBRID,
                medium=ConnectionMedium.MMWAVE_60GHZ,
                rtt_ms=1.15,
                bandwidth_gbps=20.0,
                total_vram_gb=16.0,
                available_vram_gb=12.0,
                capacity_tflops=18.0,
                hardware_desc="AMD Radeon RX 7900 XTX 24GB (Vulkan/ROCm)",
                is_pure_amd=True,
                is_solar_powered=True,
                uploaded_compute_units=80.0,
                downloaded_compute_units=70.0,
            )
        )
        # Initial Tit-for-Tat evaluation round
        self.tit_for_tat.evaluate_swarm(self.peers)

    def register_peer(self, peer: SwarmPeer) -> None:
        """Adds or updates a peer in the swarm DHT table."""
        self.peers[peer.peer_id] = peer
        logger.info(f"P2P Swarm: Registered peer {peer.peer_id} ({peer.node_name}) via {peer.medium.value}")

    def unregister_peer(self, peer_id: str) -> Optional[SwarmPeer]:
        """Removes a peer from the swarm."""
        return self.peers.pop(peer_id, None)

    def heartbeat(self) -> Dict[str, bool]:
        """Runs periodic health-check and Tit-for-Tat unchoke cycle."""
        return self.tit_for_tat.evaluate_swarm(self.peers)

    def find_optimal_providers(
        self,
        required_vram_gb: float = 4.0,
        requires_nvidia: bool = False,
        requires_pure_amd: bool = False,
        max_rtt_ms: float = 15.0,
        preferred_medium: Optional[ConnectionMedium] = None,
        count: int = 1,
    ) -> List[SwarmPeer]:
        """
        Discovers and ranks candidate providers based on:
        1. Hardware constraints (VRAM, Node 2 Purity / Pure AMD vs. NVIDIA).
        2. Network constraints (RTT threshold, Medium).
        3. Tit-for-Tat status (unchoked peers prioritized).
        """
        candidates: List[Tuple[float, SwarmPeer]] = []

        for peer in self.peers.values():
            # Check availability & capacity
            if peer.available_vram_gb < required_vram_gb:
                continue
            if peer.rtt_ms > max_rtt_ms:
                continue

            # Node 2 Purity / Architecture enforcement
            if requires_nvidia and peer.is_pure_amd:
                continue  # Never send NVIDIA tasks to Pure AMD nodes
            if requires_pure_amd and not peer.is_pure_amd:
                continue

            # Prefer unchoked peers (choked peers penalized in ranking)
            choke_penalty = 0.3 if peer.is_choked else 1.0

            # Medium weighting
            medium_bonus = 1.2 if (preferred_medium and peer.medium == preferred_medium) else 1.0
            if peer.medium == ConnectionMedium.FIBER_DIRECT:
                medium_bonus *= 1.3

            # Composite ranking score: higher = better
            score = (
                (peer.capacity_tflops / 10.0)
                * (peer.bandwidth_gbps / max(0.1, peer.rtt_ms))
                * peer.contribution_ratio
                * choke_penalty
                * medium_bonus
                * peer.reputation_score
            )
            candidates.append((score, peer))

        # Sort descending by score
        candidates.sort(key=lambda x: x[0], reverse=True)
        return [peer for _, peer in candidates[:count]]

    def shard_task_into_pieces(
        self,
        task_id: str,
        workload_type: str,
        payload: Any,
        num_pieces: int = 4,
        expected_tflops_total: float = 4.0,
    ) -> List[ComputePiece]:
        """
        Splits a large compute task into verifyable pieces, analogous to BitTorrent file pieces.
        """
        pieces: List[ComputePiece] = []
        piece_tflops = expected_tflops_total / max(1, num_pieces)

        if isinstance(payload, list):
            # Split list chunks
            chunk_size = max(1, len(payload) // num_pieces)
            for i in range(num_pieces):
                start = i * chunk_size
                end = None if i == num_pieces - 1 else (i + 1) * chunk_size
                piece_payload = payload[start:end]
                pieces.append(ComputePiece.create(i, task_id, workload_type, piece_payload, piece_tflops))
        elif isinstance(payload, str) and len(payload) > 100:
            # Split text blocks
            chunk_len = len(payload) // num_pieces
            for i in range(num_pieces):
                start = i * chunk_len
                end = len(payload) if i == num_pieces - 1 else (i + 1) * chunk_len
                pieces.append(ComputePiece.create(i, task_id, workload_type, payload[start:end], piece_tflops))
        else:
            # Single or replicated workload piece
            for i in range(num_pieces):
                piece_data = {"sub_index": i, "total_sub_tasks": num_pieces, "base_payload": payload}
                pieces.append(ComputePiece.create(i, task_id, workload_type, piece_data, piece_tflops))

        return pieces

    def dispatch_piece(self, piece: ComputePiece, peer: SwarmPeer) -> Dict[str, Any]:
        """
        Dispatches a compute piece to a selected peer and records execution metadata.
        """
        start = time.time()
        piece.assigned_peer_id = peer.peer_id

        # Simulate DMA transfer over the link medium
        dma_latency_ms = (1.5 / max(1.0, peer.bandwidth_gbps)) + peer.rtt_ms
        compute_ms = (piece.expected_tflops / max(1.0, peer.capacity_tflops)) * 12.0
        total_exec_ms = dma_latency_ms + compute_ms

        # Compute deterministic result checksum
        result_str = f"COMPUTE_RESULT_{piece.task_id}_{piece.piece_index}_{peer.peer_id}"
        result_checksum = hashlib.sha256(result_str.encode("utf-8")).hexdigest()[:16]

        piece.is_completed = True
        piece.result_data = result_str
        piece.result_checksum = result_checksum
        piece.execution_time_ms = round(total_exec_ms, 3)

        # Update peer's uploaded ledger (peer served compute)
        peer.uploaded_compute_units += piece.expected_tflops
        peer.last_seen_epoch = time.time()

        return {
            "piece_index": piece.piece_index,
            "peer_id": peer.peer_id,
            "status": "SUCCESS",
            "execution_time_ms": piece.execution_time_ms,
            "result_checksum": result_checksum,
        }

    def aggregate_pieces(self, pieces: List[ComputePiece]) -> Dict[str, Any]:
        """
        Assembles completed compute pieces into a verified final task artifact.
        """
        completed = [p for p in pieces if p.is_completed]
        if len(completed) != len(pieces):
            raise RuntimeError(f"Swarm aggregation failure: {len(completed)}/{len(pieces)} pieces completed.")

        total_exec_ms = sum(p.execution_time_ms for p in pieces)
        combined_checksums = "".join(str(p.result_checksum) for p in pieces)
        final_state_root = hashlib.sha256(combined_checksums.encode("utf-8")).hexdigest()

        return {
            "total_pieces": len(pieces),
            "completed_pieces": len(completed),
            "aggregate_execution_time_ms": round(total_exec_ms, 3),
            "final_state_root": final_state_root,
            "pieces_breakdown": [
                {
                    "index": p.piece_index,
                    "peer_id": p.assigned_peer_id,
                    "tflops": p.expected_tflops,
                    "checksum": p.result_checksum,
                    "time_ms": p.execution_time_ms,
                }
                for p in pieces
            ],
        }

    def get_swarm_stats(self) -> Dict[str, Any]:
        """Emits comprehensive P2P compute swarm statistics."""
        active_peers = [p for p in self.peers.values() if time.time() - p.last_seen_epoch < 120.0]
        seeders = [p for p in active_peers if p.role in (PeerRole.SEEDER, PeerRole.HYBRID)]
        leechers = [p for p in active_peers if p.role in (PeerRole.LEECHER, PeerRole.HYBRID)]
        unchoked = [p for p in active_peers if not p.is_choked]
        fiber_peers = [p for p in active_peers if p.medium == ConnectionMedium.FIBER_DIRECT]

        total_vram = sum(p.available_vram_gb for p in active_peers)
        total_tflops = sum(p.capacity_tflops for p in active_peers)
        avg_rtt = sum(p.rtt_ms for p in active_peers) / max(1, len(active_peers))

        return {
            "total_peers": len(active_peers),
            "active_seeders": len(seeders),
            "active_leechers": len(leechers),
            "unchoked_peers": len(unchoked),
            "fiber_direct_peers": len(fiber_peers),
            "pooled_available_vram_gb": round(total_vram, 2),
            "pooled_capacity_tflops": round(total_tflops, 2),
            "average_rtt_ms": round(avg_rtt, 2),
            "peers": [p.to_dict() for p in active_peers],
        }
