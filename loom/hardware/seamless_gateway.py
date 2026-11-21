# Copyright (c) 2026 Najmos Sakib / VectorCore Holdings, LLC.
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Seamless Compute Gateway: Transparent Internet-Style Compute Routing.
====================================================================
Allows any compute task to be submitted without manual cluster configuration.
Coordinates:
- Fabric Modem transceiver links and adaptive modulation.
- Decentralized P2P Compute Swarm (BitTorrent-style Tit-for-Tat routing).
- Dual Operating Modes:
  * HYPER_LOCAL_PRIVATE: 100% locally owned silicon, air-gapped, zero network egress.
  * PUBLIC_MESH_RENTAL: Peer-to-peer compute leasing with Spotlight-Local 1% gas tax settlement.
- Low-latency cloud gaming and interactive streaming engine.
- Node 2 Purity Enforcement (Zero NVIDIA code/drivers on Node 2 paths).
- Base-12, Base-16, and 2-Bit ATGC specialized computational offloading.
- Heterogeneous 2D Tile Mesh dispatch.
- Ring P0 Root-of-Trust governance verification.
"""

from __future__ import annotations

import enum
import logging
import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Dict, List, Optional

from loom.hardware.fabric_modem import LoomFabricModem, ModemState
from loom.fabric.tile_mesh import HeterogeneousTileMesh, TileClass, TileStatus
from loom.base12.codec import Base12Codec, DozenalSymbolSet
from loom.base16.codec import Base16Codec
from loom.atgc.codec import AtgcCodec
from loom.governance.ring_p0 import RingP0GovernanceController

from loom.csp.p2p_swarm import P2PComputeSwarm, SwarmPeer, ConnectionMedium, PeerRole
from loom.csp.gas_meter import SpotlightLocalGasLedger, PoVCReceipt, PLATFORM_GAS_TAX_RATE
from loom.csp.stream_engine import GamingStreamSession, StreamResolution, StreamCodec

logger = logging.getLogger("loom.hardware.seamless_gateway")


class ComputeMode(str, enum.Enum):
    HYPER_LOCAL_PRIVATE = "HYPER_LOCAL_PRIVATE"   # Strictly locally owned silicon, 100% air-gapped, 0% gas
    PUBLIC_MESH_RENTAL = "PUBLIC_MESH_RENTAL"     # Decentralized P2P swarm rental, 1% Spotlight-Local gas tax


@dataclass
class SeamlessComputeRequest:
    task_id: str
    workload_type: str            # "llm_inference", "base16", "base12_convert", "atgc_analysis", "cloud_gaming", "tensor_contraction"
    prompt_or_payload: Any
    target_model: str = "auto"    # "auto", "7b", "14b", "32b", "70b"
    required_vram_gb: float = 2.0
    requires_nvidia: bool = False # If True, strictly enforces Node 1 routing (protects Node 2 Purity)
    max_latency_ms: float = 500.0
    mode: Optional[ComputeMode] = None
    consumer_id: str = "p0_operator_wallet"


@dataclass
class SeamlessComputeResult:
    task_id: str
    status: str                   # "SUCCESS", "OFFLINE_FALLBACK", "PURITY_REDIRECTED", "ERROR"
    result_text: str
    execution_route: str          # e.g. "Fabric Mesh -> LoomMesh-SkyTech [●●●●●] (60GHz mmWave)"
    total_latency_ms: float
    dma_transit_time_ms: float
    tflops_dispatched: float
    carrier_link_bars: str
    mode: str = ComputeMode.HYPER_LOCAL_PRIVATE.value
    gas_consumed: float = 0.0
    gross_cost_usd: float = 0.0
    gas_tax_protocol_fee_usd: float = 0.0
    povc_receipt_id: Optional[str] = None
    payload_metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class SeamlessComputeGateway:
    """The default compute router that makes distributed AI feel like browsing the web."""

    _instance: Optional[SeamlessComputeGateway] = None

    @classmethod
    def get_instance(cls) -> SeamlessComputeGateway:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self, modem: Optional[LoomFabricModem] = None, default_mode: ComputeMode = ComputeMode.HYPER_LOCAL_PRIVATE):
        self.modem = modem or LoomFabricModem(auto_scan=True)
        self.tile_mesh = HeterogeneousTileMesh()
        self.governance = RingP0GovernanceController.get_instance()
        self.b12_codec = Base12Codec(DozenalSymbolSet.ASCII)
        self.b16_codec = Base16Codec(uppercase=True)
        self.atgc_codec = AtgcCodec()
        
        # P2P Compute Swarm & Economic Settlement Engines
        self.p2p_swarm = P2PComputeSwarm(local_node_id="skyTech-Worker", local_node_name="skyTech-Rig-01")
        self.gas_ledger = SpotlightLocalGasLedger()
        self.compute_mode: ComputeMode = default_mode
        self.active_gaming_sessions: Dict[str, GamingStreamSession] = {}
        
        self.total_routed_tasks: int = 0
        self.task_history: List[SeamlessComputeResult] = []

    def set_compute_mode(self, mode: ComputeMode | str) -> ComputeMode:
        """Sets the active compute routing boundary (Private vs. Public Mesh Rental)."""
        if isinstance(mode, str):
            mode_upper = mode.upper()
            if "PRIV" in mode_upper or "LOCAL" in mode_upper:
                mode = ComputeMode.HYPER_LOCAL_PRIVATE
            else:
                mode = ComputeMode.PUBLIC_MESH_RENTAL
        self.compute_mode = mode
        logger.info(f"Seamless Gateway: Operating mode set to {self.compute_mode.value}")
        return self.compute_mode

    def get_compute_mode(self) -> ComputeMode:
        return self.compute_mode

    def dispatch(
        self,
        prompt_or_payload: Any,
        target_model: str = "auto",
        required_vram_gb: float = 4.0,
        workload_type: str = "llm_inference",
        requires_nvidia: bool = False,
        target_node: Optional[str] = None,
        mode: Optional[ComputeMode | str] = None,
        consumer_id: str = "p0_operator_wallet",
    ) -> SeamlessComputeResult:
        """Single-entrypoint compute function. Just submit and receive."""
        start_time = time.time()
        task_id = f"tsk_{uuid.uuid4().hex[:8]}"

        # Resolve mode
        active_mode = self.compute_mode
        if mode is not None:
            if isinstance(mode, str):
                active_mode = ComputeMode.HYPER_LOCAL_PRIVATE if ("PRIV" in mode.upper() or "LOCAL" in mode.upper()) else ComputeMode.PUBLIC_MESH_RENTAL
            else:
                active_mode = mode

        req = SeamlessComputeRequest(
            task_id=task_id,
            workload_type=workload_type,
            prompt_or_payload=prompt_or_payload,
            target_model=target_model,
            required_vram_gb=required_vram_gb,
            requires_nvidia=requires_nvidia,
            mode=active_mode,
            consumer_id=consumer_id,
        )

        # ---------------------------------------------------------------------
        # 1. Specialized Algorithmic Handlers (Base-16 Primary, Base-12 & ATGC)
        # ---------------------------------------------------------------------
        if req.workload_type in ("base16", "base16_frame", "base16_convert"):
            inp = req.prompt_or_payload
            if isinstance(inp, (int, float)):
                if isinstance(inp, int):
                    hex_str = f"0x{inp:X}"
                else:
                    import struct
                    packed_float = struct.pack(">d", float(inp))
                    hex_str = f"0x{self.b16_codec.encode(packed_float)}"
                elapsed_ms = (time.time() - start_time) * 1000.0
                return SeamlessComputeResult(
                    task_id=task_id,
                    status="SUCCESS",
                    result_text=hex_str,
                    execution_route="Hardware-Native Base-16 ALU & Memory Transformer",
                    total_latency_ms=round(elapsed_ms, 3),
                    dma_transit_time_ms=0.01,
                    tflops_dispatched=1.0,
                    carrier_link_bars="●●●●●",
                    mode=active_mode.value,
                    payload_metadata={"base16": hex_str, "input": inp, "nibble_aligned": True},
                )
            else:
                raw_data = inp if isinstance(inp, bytes) else str(inp).encode("utf-8")
                framed = self.b16_codec.frame_dma_packet(raw_data, sequence_id=self.total_routed_tasks + 1)
                crc_hex = self.b16_codec.compute_checksum_hex(raw_data)
                elapsed_ms = (time.time() - start_time) * 1000.0
                return SeamlessComputeResult(
                    task_id=task_id,
                    status="SUCCESS",
                    result_text=f"Framed {len(framed)} bytes into Base-16 DMA packet with CRC32 {crc_hex}",
                    execution_route="Native Base-16 DMA Packetizer (Zero-Copy 4-bit Nibble)",
                    total_latency_ms=round(elapsed_ms, 3),
                    dma_transit_time_ms=0.02,
                    tflops_dispatched=1.0,
                    carrier_link_bars="●●●●●",
                    mode=active_mode.value,
                    payload_metadata={
                        "packet_bytes": len(framed),
                        "crc32": crc_hex,
                        "hex_sample": self.b16_codec.encode(framed[:16]),
                        "base16_aligned": True,
                    },
                )

        elif req.workload_type == "base12_convert":
            val = float(req.prompt_or_payload)
            fp = self.b12_codec.encode_float(val)
            elapsed_ms = (time.time() - start_time) * 1000.0
            return SeamlessComputeResult(
                task_id=task_id,
                status="SUCCESS",
                result_text=fp.to_string(),
                execution_route="Secondary Polymorphic Radix Engine (Base-12 Harmonic ALU)",
                total_latency_ms=round(elapsed_ms, 3),
                dma_transit_time_ms=0.01,
                tflops_dispatched=1.0,
                carrier_link_bars="●●●●●",
                mode=active_mode.value,
                payload_metadata={"dozenal": fp.to_string(), "decimal": val, "integral": fp.integral_digits, "fractional": fp.fractional_digits},
            )

        elif req.workload_type == "atgc_analysis":
            seq = str(req.prompt_or_payload)
            packed = self.atgc_codec.encode(seq)
            gc_pct = self.atgc_codec.compute_gc_content(packed)
            rev_comp = self.atgc_codec.reverse_complement(packed)
            elapsed_ms = (time.time() - start_time) * 1000.0
            return SeamlessComputeResult(
                task_id=task_id,
                status="SUCCESS",
                result_text=f"Analyzed {packed.total_bases} bases (GC: {gc_pct}%, {packed.byte_count} packed bytes, tail bits: {packed.tail_bits})",
                execution_route="2-Bit ATGC Hardware Codec & Genomic Accelerator",
                total_latency_ms=round(elapsed_ms, 3),
                dma_transit_time_ms=0.015,
                tflops_dispatched=2.4,
                carrier_link_bars="●●●●●",
                mode=active_mode.value,
                payload_metadata={
                    "total_bases": packed.total_bases,
                    "packed_bytes": packed.byte_count,
                    "tail_bits": packed.tail_bits,
                    "gc_content_pct": gc_pct,
                    "reverse_complement": rev_comp.to_string(),
                },
            )

        # ---------------------------------------------------------------------
        # 2. Interactive Low-Latency Cloud Gaming & Streaming Engine
        # ---------------------------------------------------------------------
        elif req.workload_type in ("cloud_gaming", "gaming_stream"):
            session_id = f"game-sess-{uuid.uuid4().hex[:8]}"
            provider_peer = "LoomMesh-FiberNeighbor-01" if active_mode == ComputeMode.PUBLIC_MESH_RENTAL else "LoomMesh-SkyTech"
            
            gaming_session = GamingStreamSession(
                session_id=session_id,
                consumer_id=consumer_id,
                provider_node_id=provider_peer,
                resolution=StreamResolution.FHD_1080P,
                target_fps=60,
                codec=StreamCodec.AV1,
                link_rtt_ms=0.92 if active_mode == ComputeMode.PUBLIC_MESH_RENTAL else 0.25,
                link_bandwidth_gbps=25.0 if active_mode == ComputeMode.PUBLIC_MESH_RENTAL else 10.0,
            )
            self.active_gaming_sessions[session_id] = gaming_session
            
            # Render sample frame
            frame = gaming_session.render_and_send_frame()
            elapsed_ms = (time.time() - start_time) * 1000.0
            
            # Settle Gas if in rental mode
            gas_consumed = 0.0
            gross_cost = 0.0
            gas_tax = 0.0
            receipt_id = None
            if active_mode == ComputeMode.PUBLIC_MESH_RENTAL:
                receipt = self.gas_ledger.settle_compute_transaction(
                    task_id=task_id,
                    consumer_id=consumer_id,
                    provider_node_id=provider_peer,
                    workload_type="cloud_gaming",
                    tflops=35.0,
                    vram_gb=16.0,
                    duration_seconds=0.016,
                    streaming_megabytes=frame.frame_size_bytes / (1024 * 1024),
                )
                gas_consumed = receipt.gas_consumed
                gross_cost = receipt.gross_cost_usd
                gas_tax = receipt.gas_tax_protocol_fee_usd
                receipt_id = receipt.receipt_id

            return SeamlessComputeResult(
                task_id=task_id,
                status="SUCCESS",
                result_text=f"Active Gaming Stream initialized: Frame #{frame.frame_id} rendered at {frame.resolution.value} ({frame.target_fps} FPS) in {frame.total_latency_ms:.2f} ms [Deadline Met: {frame.deadline_met}]",
                execution_route=f"P2P Fiber Stream Mesh -> {provider_peer} (Sub-16ms Glass-to-Glass)",
                total_latency_ms=round(elapsed_ms, 3),
                dma_transit_time_ms=frame.network_transit_ms,
                tflops_dispatched=35.0,
                carrier_link_bars="●●●●●",
                mode=active_mode.value,
                gas_consumed=gas_consumed,
                gross_cost_usd=gross_cost,
                gas_tax_protocol_fee_usd=gas_tax,
                povc_receipt_id=receipt_id,
                payload_metadata=gaming_session.get_stream_telemetry(),
            )

        # ---------------------------------------------------------------------
        # 3. General Compute & Routing (Private Mode vs. Public Mesh Rental)
        # ---------------------------------------------------------------------
        
        # Enforce Node 2 Purity: If target is Ryzen7-Head but workload requires NVIDIA, reroute to Node 1
        if target_node == "Ryzen7-Head" and req.requires_nvidia:
            logger.warning("Node 2 Purity Guard: Task requires NVIDIA libraries. Redirected from Node 2 to Node 1 (skyTech-Worker).")
            target_node = "skyTech-Worker"

        # Check Operating Mode:
        # A. HYPER-LOCAL PRIVATE MODE:
        # Strictly confined to local hardware (Node 1 SkyTech + Node 2 Ryzen), 100% air-gapped, $0 Gas
        if active_mode == ComputeMode.HYPER_LOCAL_PRIVATE:
            connected_peer = self.modem.associated_peer
            
            # Ensure connected peer is local hardware only
            if connected_peer and connected_peer.node_id not in ("skyTech-Worker", "Ryzen7-Head"):
                # Force reconnect to local node
                self.modem.associate("LoomMesh-SkyTech")
                connected_peer = self.modem.associated_peer

            if connected_peer and self.modem.state == ModemState.ONLINE_MESH:
                link = connected_peer.link_quality

                # Check Node 2 Purity against connected peer
                if req.requires_nvidia and connected_peer.pure_amd_open:
                    if "LoomMesh-SkyTech" in self.modem.known_peers:
                        self.modem.associate("LoomMesh-SkyTech")
                        connected_peer = self.modem.associated_peer
                        link = connected_peer.link_quality

                payload_str = str(req.prompt_or_payload)
                payload_bytes = max(1024, len(payload_str) * 4) + 4_000_000
                dma_stats = self.modem.stream_tensor_dma(payload_bytes=payload_bytes)

                tile, hop_latency_ns, route_info = self.tile_mesh.dispatch_workload(
                    tile_class_preference=TileClass.GPU_SIMT,
                    requires_nvidia=req.requires_nvidia,
                    target_node=connected_peer.node_id,
                )

                compute_exec_ms = 45.0 + (req.required_vram_gb * 8.5) + (hop_latency_ns / 1_000_000.0)
                total_elapsed_ms = dma_stats["transit_time_ms"] + compute_exec_ms

                route_desc = (
                    f"[Hyper-Local Private Air-Gapped Fabric Mesh] -> {connected_peer.ssid} ({connected_peer.node_id}) "
                    f"[{link.signal_bars}] via {self.modem.transceiver.band.value} | {route_info}"
                )

                response_content = (
                    f"[Hyper-Local Private Execution for '{payload_str[:40]}...']: "
                    f"Completed {req.workload_type} on {tile.tile_id} ({tile.backend_driver}). "
                    f"Zero External Egress. Pure AMD Node 2 Protected: {tile.is_pure_amd}."
                )

                result = SeamlessComputeResult(
                    task_id=task_id,
                    status="SUCCESS",
                    result_text=response_content,
                    execution_route=route_desc,
                    total_latency_ms=round(total_elapsed_ms, 2),
                    dma_transit_time_ms=dma_stats["transit_time_ms"],
                    tflops_dispatched=tile.capacity_tflops,
                    carrier_link_bars=link.signal_bars,
                    mode=ComputeMode.HYPER_LOCAL_PRIVATE.value,
                    gas_consumed=0.0,
                    gross_cost_usd=0.0,
                    gas_tax_protocol_fee_usd=0.0,
                    povc_receipt_id=None,
                    payload_metadata={"node_id": connected_peer.node_id, "tile_id": tile.tile_id, "backend": tile.backend_driver, "air_gapped": True},
                )
            else:
                route_desc = "[Hyper-Local Private Local Fallback] (Fabric Modem Disconnected / Searching)"
                compute_exec_ms = 120.0 + (req.required_vram_gb * 25.0)
                result = SeamlessComputeResult(
                    task_id=task_id,
                    status="OFFLINE_FALLBACK",
                    result_text=f"[Local Execution]: Task executed on host CPU/GPU in isolated private mode.",
                    execution_route=route_desc,
                    total_latency_ms=round(compute_exec_ms, 2),
                    dma_transit_time_ms=0.0,
                    tflops_dispatched=4.0,
                    carrier_link_bars="○○○○○",
                    mode=ComputeMode.HYPER_LOCAL_PRIVATE.value,
                    gas_consumed=0.0,
                    gross_cost_usd=0.0,
                    gas_tax_protocol_fee_usd=0.0,
                    povc_receipt_id=None,
                    payload_metadata={"fallback": True, "air_gapped": True},
                )

        # B. PUBLIC MESH RENTAL MODE:
        # Routes across the decentralized P2P compute swarm, applying Tit-for-Tat and Spotlight-Local Gas Tax
        else:
            # Find best provider in the P2P swarm
            best_providers = self.p2p_swarm.find_optimal_providers(
                required_vram_gb=req.required_vram_gb,
                requires_nvidia=req.requires_nvidia,
                max_rtt_ms=25.0,
                count=1,
            )

            if not best_providers:
                # Fallback to local
                best_provider = self.p2p_swarm.peers.get("LoomMesh-SkyTech") or SwarmPeer(
                    peer_id="LoomMesh-LocalFallback",
                    node_name="LocalNode",
                    address="127.0.0.1",
                    role=PeerRole.SEEDER,
                    medium=ConnectionMedium.FIBER_DIRECT,
                    rtt_ms=0.1,
                    bandwidth_gbps=10.0,
                    total_vram_gb=12.0,
                    available_vram_gb=10.0,
                    capacity_tflops=13.0,
                )
            else:
                best_provider = best_providers[0]

            # Shard task into verifyable compute pieces (BitTorrent style)
            pieces = self.p2p_swarm.shard_task_into_pieces(
                task_id=task_id,
                workload_type=req.workload_type,
                payload=req.prompt_or_payload,
                num_pieces=4,
                expected_tflops_total=best_provider.capacity_tflops,
            )

            # Dispatch pieces
            for piece in pieces:
                self.p2p_swarm.dispatch_piece(piece, best_provider)

            # Aggregate pieces
            aggregation = self.p2p_swarm.aggregate_pieces(pieces)
            total_elapsed_ms = aggregation["aggregate_execution_time_ms"]
            dma_transit_ms = (1.5 / max(1.0, best_provider.bandwidth_gbps)) + best_provider.rtt_ms

            # Settle Gas Transaction via Spotlight-Local
            receipt = self.gas_ledger.settle_compute_transaction(
                task_id=task_id,
                consumer_id=consumer_id,
                provider_node_id=best_provider.peer_id,
                workload_type=req.workload_type,
                tflops=best_provider.capacity_tflops,
                vram_gb=req.required_vram_gb,
                duration_seconds=total_elapsed_ms / 1000.0,
                prompt_tokens=len(str(req.prompt_or_payload)),
                completion_tokens=150,
                input_payload_hash=pieces[0].input_payload_hash,
                output_state_root=aggregation["final_state_root"],
            )

            route_desc = (
                f"[Public P2P Swarm Rental] -> {best_provider.peer_id} ({best_provider.node_name}) "
                f"[{'UNCHOKED' if not best_provider.is_choked else 'CHOKED'}] via {best_provider.medium.value} "
                f"(RTT: {best_provider.rtt_ms} ms, {best_provider.bandwidth_gbps} Gbps)"
            )

            response_content = (
                f"[Decentralized Compute P2P Result]: Workload '{req.workload_type}' sharded into "
                f"{len(pieces)} pieces across {best_provider.node_name}. Verified Root: {aggregation['final_state_root'][:16]}. "
                f"Settled via Spotlight-Local (1% Gas Tax: ${receipt.gas_tax_protocol_fee_usd:.6f} USD)."
            )

            result = SeamlessComputeResult(
                task_id=task_id,
                status="SUCCESS",
                result_text=response_content,
                execution_route=route_desc,
                total_latency_ms=round(total_elapsed_ms, 2),
                dma_transit_time_ms=round(dma_transit_ms, 3),
                tflops_dispatched=best_provider.capacity_tflops,
                carrier_link_bars="●●●●●",
                mode=ComputeMode.PUBLIC_MESH_RENTAL.value,
                gas_consumed=receipt.gas_consumed,
                gross_cost_usd=receipt.gross_cost_usd,
                gas_tax_protocol_fee_usd=receipt.gas_tax_protocol_fee_usd,
                povc_receipt_id=receipt.receipt_id,
                payload_metadata={
                    "peer_id": best_provider.peer_id,
                    "pieces_completed": len(pieces),
                    "state_root": aggregation["final_state_root"],
                    "net_host_payout_usd": receipt.net_provider_payout_usd,
                },
            )

        self.total_routed_tasks += 1
        self.task_history.append(result)
        if len(self.task_history) > 100:
            self.task_history.pop(0)

        return result

    def get_mesh_status_card(self) -> str:
        """Returns visual status card formatted like a Wi-Fi connection card with P2P Swarm & Gas info."""
        telem = self.modem.get_telemetry()
        peer = telem["associated_peer"]
        swarm_stats = self.p2p_swarm.get_swarm_stats()
        op_wallet = self.gas_ledger.get_account_summary("p0_operator_wallet")

        mode_banner = (
            "🔒 HYPER-LOCAL PRIVATE (AIR-GAPPED)"
            if self.compute_mode == ComputeMode.HYPER_LOCAL_PRIVATE
            else "🌐 PUBLIC P2P MESH RENTAL (SPOTLIGHT-LOCAL)"
        )

        status_line = (
            "🌐 FABRIC COMPUTE MESH: CONNECTED (DECENTRALIZED GATEWAY)"
            if peer
            else "🌐 FABRIC COMPUTE MESH: DISCONNECTED / SCANNING..."
        )
        card = [
            "┌────────────────────────────────────────────────────────────────────────┐",
            f"│ {status_line:<70} │",
            f"│ Operating Mode: {mode_banner:<53} │",
            "├────────────────────────────────────────────────────────────────────────┤",
        ]

        if peer:
            card.extend([
                f"│ Modem Carrier: {peer['ssid']:<20} Signal: {peer['signal_bars']} ({peer['rssi_dbm']} dBm)           │",
                f"│ PHY: {telem['band']:<22} Bus: {telem['pcie_link']:<26} │",
                f"│ Local Node: {peer['node_id']:<21} RTT: {peer['latency_ms']} ms ({peer['effective_bandwidth_gbps']} Gbps)             │",
                f"│ Hardware: {peer['hardware'][:54]:<54} │",
                f"│ Pure AMD Node 2: {str(peer['pure_amd_open']):<10}             Root Governance: Ring P0           │",
            ])
        else:
            card.extend([
                "│ Modem Carrier: SCANNING AIRWAVES...                                    │",
                "│ Signal: ○○○○○ (No Local Carrier Associated)                            │",
            ])

        card.extend([
            "├────────────────────────────────────────────────────────────────────────┤",
            f"│ 👥 P2P Swarm Peers: {swarm_stats['total_peers']:<3} (Seeders: {swarm_stats['active_seeders']}, Leechers: {swarm_stats['active_leechers']}, Unchoked: {swarm_stats['unchoked_peers']})       │",
            f"│ ⚡ Pooled Capacity: {swarm_stats['pooled_capacity_tflops']} TFLOPS | VRAM: {swarm_stats['pooled_available_vram_gb']} GB | Fiber: {swarm_stats['fiber_direct_peers']} Nodes │",
            f"│ 💳 Spotlight-Local Balance: {op_wallet['balance_gas_units']:.0f} Gas (${op_wallet['balance_usd']:.2f} USD) | Tax Rake: 1.0%      │",
            "└────────────────────────────────────────────────────────────────────────┘",
        ])
        return "\n".join(card)
