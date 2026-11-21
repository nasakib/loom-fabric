# Copyright (c) 2026 Najmos Sakib / VectorCore Holdings, LLC.
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Verification Suite: Decentralized P2P Compute Swarm, Gas Tax & Low-Latency Streaming.
====================================================================================
Tests:
1. P2P Compute Swarm & Tit-for-Tat Choking/Unchoking Algorithm (BitTorrent-style).
2. Compute Task Sharding into Pieces & State Root Aggregation.
3. Gas Metering, Landauer Thermodynamic Pricing & Spotlight-Local 1% Gas Tax Split.
4. Proof of Verifiable Computation (PoVC) HMAC-SHA256 Receipts.
5. Low-Latency Gaming Streaming (Sub-16.6ms Deadlines, Base-16 DMA, Bidirectional Input).
6. Seamless Gateway Dual-Mode Execution (Hyper-Local Private vs. Public Mesh Rental).
7. CLI Subcommands Integration (`mode`, `swarm`, `gas`, `stream-game`, `exec`).
"""

import hashlib
import json
import pytest

from loom.csp.p2p_swarm import (
    P2PComputeSwarm,
    SwarmPeer,
    PeerRole,
    ConnectionMedium,
    TitForTatEngine,
    ComputePiece,
)
from loom.csp.gas_meter import (
    SpotlightLocalGasLedger,
    GasMeteringUnit,
    PoVCReceipt,
    PLATFORM_GAS_TAX_RATE,
    HOST_PROVIDER_SHARE,
    GAS_UNITS_PER_USD,
)
from loom.csp.stream_engine import (
    GamingStreamSession,
    GameStreamFrame,
    StreamResolution,
    StreamCodec,
    InputEventType,
)
from loom.hardware.seamless_gateway import SeamlessComputeGateway, ComputeMode
from loom.hardware.cli import main as cli_main


# =============================================================================
# 1. P2P Compute Swarm & Tit-for-Tat Choking/Unchoking
# =============================================================================

def test_p2p_swarm_initialization_and_peers():
    swarm = P2PComputeSwarm(local_node_id="skyTech-Worker", local_node_name="skyTech-Rig-01")
    stats = swarm.get_swarm_stats()
    assert stats["total_peers"] >= 4
    assert stats["active_seeders"] >= 2
    assert stats["pooled_capacity_tflops"] > 30.0
    assert stats["fiber_direct_peers"] >= 3

    # Check peer properties
    skytech = swarm.peers.get("LoomMesh-SkyTech")
    assert skytech is not None
    assert skytech.medium == ConnectionMedium.FIBER_DIRECT
    assert skytech.is_pure_amd is False

    ryzen = swarm.peers.get("LoomMesh-Ryzen7")
    assert ryzen is not None
    assert ryzen.is_pure_amd is True


def test_tit_for_tat_choking_and_optimistic_unchoking():
    engine = TitForTatEngine(top_k_unchoked=2, optimistic_interval_rounds=2)
    peers = {
        f"peer_{i}": SwarmPeer(
            peer_id=f"peer_{i}",
            node_name=f"node_{i}",
            address=f"192.168.1.{i}",
            role=PeerRole.HYBRID,
            medium=ConnectionMedium.FIBER_DIRECT,
            rtt_ms=1.0 + i,
            bandwidth_gbps=10.0,
            uploaded_compute_units=float(100 - i * 10),
            downloaded_compute_units=10.0,
        )
        for i in range(5)
    }

    # Run round 1
    choke_map = engine.evaluate_swarm(peers)
    unchoked = [pid for pid, is_choked in choke_map.items() if not is_choked]
    # Top 2 should definitely be unchoked
    assert "peer_0" in unchoked
    assert "peer_1" in unchoked
    assert len(unchoked) >= 2


def test_swarm_task_sharding_and_piece_aggregation():
    swarm = P2PComputeSwarm()
    task_id = "test_task_7788"
    payload = "Large dataset compute payload destined for tensor contraction across fiber mesh"

    pieces = swarm.shard_task_into_pieces(
        task_id=task_id,
        workload_type="tensor_contraction",
        payload=payload,
        num_pieces=4,
        expected_tflops_total=12.0,
    )
    assert len(pieces) == 4
    assert pieces[0].piece_index == 0
    assert pieces[3].piece_index == 3

    # Dispatch pieces to fiber provider
    provider = swarm.peers["LoomMesh-FiberNeighbor-01"]
    for piece in pieces:
        dispatch_res = swarm.dispatch_piece(piece, provider)
        assert dispatch_res["status"] == "SUCCESS"
        assert piece.is_completed is True
        assert piece.result_checksum is not None

    # Aggregate
    agg = swarm.aggregate_pieces(pieces)
    assert agg["total_pieces"] == 4
    assert agg["completed_pieces"] == 4
    assert len(agg["final_state_root"]) == 64
    assert agg["aggregate_execution_time_ms"] > 0.0


# =============================================================================
# 2. Gas Metering, Thermodynamic Landauer & Spotlight-Local 1% Tax
# =============================================================================

def test_gas_metering_unit_calculations():
    meter = GasMeteringUnit(landauer_rating_pj_per_mac=1.2)
    breakdown = meter.calculate_gas(
        tflops=10.0,
        vram_gb=12.0,
        duration_seconds=1.0,
        prompt_tokens=500,
        completion_tokens=200,
        streaming_megabytes=2.5,
    )

    assert breakdown["total_gas"] > 0.0
    assert breakdown["gross_cost_usd"] > 0.0
    assert breakdown["compute_gas"] == 500.0  # 10 * 1 * 50
    assert breakdown["landauer_microjoules"] > 0.0


def test_spotlight_local_gas_ledger_settlement():
    ledger = SpotlightLocalGasLedger(persistence_file=None)

    receipt = ledger.settle_compute_transaction(
        task_id="tsk_sl_001",
        consumer_id="p0_operator_wallet",
        provider_node_id="skytech_provider_wallet",
        workload_type="llm_inference",
        tflops=13.0,
        vram_gb=8.0,
        duration_seconds=0.75,
        prompt_tokens=1000,
        completion_tokens=100,
    )

    assert isinstance(receipt, PoVCReceipt)
    assert receipt.receipt_id.startswith("sl-gas-")
    assert receipt.gross_cost_usd > 0.0

    # Test the exact Spotlight-Local 1.0% in-network split
    expected_tax = round(receipt.gross_cost_usd * PLATFORM_GAS_TAX_RATE, 6)
    expected_payout = round(receipt.gross_cost_usd - expected_tax, 6)
    assert receipt.gas_tax_protocol_fee_usd == expected_tax
    assert receipt.net_provider_payout_usd == expected_payout

    # Verify HMAC-SHA256 signature
    assert receipt.verify(ledger.secret_key) is True

    # Check Treasury wallet received the 1% tax
    treasury = ledger.get_account_summary("sl_treasury_vectorcore_holdings")
    assert treasury["total_earned_usd"] > 0.0


def test_deposit_and_wallet_tracking():
    ledger = SpotlightLocalGasLedger(persistence_file=None)
    initial_bal = ledger.get_account_summary("p0_operator_wallet")["balance_usd"]
    new_bal = ledger.deposit_fiat_usd("p0_operator_wallet", 50.0)
    assert new_bal == pytest.approx(initial_bal + 50.0, rel=1e-4)


# =============================================================================
# 3. Low-Latency Gaming Streaming Engine
# =============================================================================

def test_gaming_stream_session_frame_deadlines():
    session = GamingStreamSession(
        session_id="game_test_01",
        consumer_id="consumer_gamer_01",
        provider_node_id="LoomMesh-FiberNeighbor-01",
        resolution=StreamResolution.FHD_1080P,
        target_fps=60,
        codec=StreamCodec.AV1,
        link_rtt_ms=0.85,
        link_bandwidth_gbps=25.0,
    )

    frame = session.render_and_send_frame()
    assert isinstance(frame, GameStreamFrame)
    assert frame.frame_id == 1
    assert frame.codec == StreamCodec.AV1
    # Check glass-to-glass latency is well under 16.6ms (60 FPS target)
    assert frame.total_latency_ms < 16.6
    assert frame.deadline_met is True
    assert len(frame.dma_base16_header_crc) == 8


def test_bidirectional_input_reception():
    session = GamingStreamSession(
        session_id="game_test_02",
        consumer_id="consumer_gamer_01",
        provider_node_id="LoomMesh-SkyTech",
        link_rtt_ms=0.5,
    )

    inp = session.receive_input(
        event_type=InputEventType.GAMEPAD_AXIS,
        payload={"left_stick_x": 0.85, "left_stick_y": -0.22, "button_a": True},
    )
    assert inp.sequence_id == 1
    assert inp.transit_latency_ms == 0.25  # RTT / 2

    telem = session.get_stream_telemetry()
    assert telem["inputs_processed"] == 1
    assert telem["frames_streamed"] == 0


# =============================================================================
# 4. Seamless Gateway Dual-Mode Execution (Private vs Public Mesh Rental)
# =============================================================================

def test_seamless_gateway_hyper_local_private_mode():
    gateway = SeamlessComputeGateway.get_instance()
    gateway.set_compute_mode(ComputeMode.HYPER_LOCAL_PRIVATE)
    assert gateway.get_compute_mode() == ComputeMode.HYPER_LOCAL_PRIVATE

    # Dispatch in Private Mode
    res = gateway.dispatch(
        prompt_or_payload="Private medical or financial query",
        workload_type="llm_inference",
        mode=ComputeMode.HYPER_LOCAL_PRIVATE,
    )

    assert res.status in ("SUCCESS", "OFFLINE_FALLBACK")
    assert res.mode == ComputeMode.HYPER_LOCAL_PRIVATE.value
    # Private mode must be 100% free of external gas fees
    assert res.gas_consumed == 0.0
    assert res.gross_cost_usd == 0.0
    assert res.gas_tax_protocol_fee_usd == 0.0
    assert res.povc_receipt_id is None
    assert "Hyper-Local Private" in res.execution_route


def test_seamless_gateway_public_mesh_rental_mode():
    gateway = SeamlessComputeGateway.get_instance()
    gateway.set_compute_mode(ComputeMode.PUBLIC_MESH_RENTAL)
    assert gateway.get_compute_mode() == ComputeMode.PUBLIC_MESH_RENTAL

    # Dispatch in Public Mesh Rental Mode
    res = gateway.dispatch(
        prompt_or_payload="Heavy compute rendering shard",
        workload_type="tensor_contraction",
        mode=ComputeMode.PUBLIC_MESH_RENTAL,
        required_vram_gb=6.0,
    )

    assert res.status == "SUCCESS"
    assert res.mode == ComputeMode.PUBLIC_MESH_RENTAL.value
    assert res.gas_consumed > 0.0
    assert res.gross_cost_usd > 0.0
    assert res.gas_tax_protocol_fee_usd > 0.0
    assert res.povc_receipt_id is not None
    assert "Public P2P Swarm Rental" in res.execution_route
    assert "state_root" in res.payload_metadata


def test_seamless_gateway_cloud_gaming_dispatch():
    gateway = SeamlessComputeGateway.get_instance()
    res = gateway.dispatch(
        prompt_or_payload={"fps": 60, "resolution": "1080p"},
        workload_type="cloud_gaming",
        mode="mesh",
    )

    assert res.status == "SUCCESS"
    assert "Gaming Stream initialized" in res.result_text
    assert "deadlines_met_percentage" in res.payload_metadata
    assert res.povc_receipt_id is not None


# =============================================================================
# 5. CLI Subcommands Integration
# =============================================================================

def test_cli_subcommands(capsys):
    # 1. status
    assert cli_main(["status"]) == 0
    captured = capsys.readouterr().out
    assert "FABRIC COMPUTE MESH" in captured

    # 2. mode switch
    assert cli_main(["mode", "--set", "mesh"]) == 0
    assert "PUBLIC_MESH_RENTAL" in capsys.readouterr().out

    # 3. swarm peers
    assert cli_main(["swarm", "peers"]) == 0
    captured = capsys.readouterr().out
    assert "LoomMesh-SkyTech" in captured
    assert "LoomMesh-FiberNeighbor-01" in captured

    # 4. gas balance
    assert cli_main(["gas", "balance"]) == 0
    captured = capsys.readouterr().out
    assert "Spotlight-Local Gas Account" in captured
    assert "Platform Take-Rate: 1.0%" in captured

    # 5. stream-game
    assert cli_main(["stream-game", "--fps", "60"]) == 0
    captured = capsys.readouterr().out
    assert "Initializing Low-Latency Interactive Gaming Stream" in captured

    # 6. exec in mesh mode
    assert cli_main(["exec", "Decentralized P2P Test", "--mode", "mesh"]) == 0
    captured = capsys.readouterr().out
    assert "PUBLIC_MESH_RENTAL" in captured

    # 7. Reset back to private mode
    assert cli_main(["mode", "--set", "private"]) == 0
    assert "HYPER_LOCAL_PRIVATE" in capsys.readouterr().out
