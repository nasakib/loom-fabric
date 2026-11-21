# Copyright (c) 2026 Najmos Sakib / VectorCore Holdings, LLC.
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Loom Fabric Modem & Seamless Compute CLI (`loom/hardware/cli.py`).
================================================================
Command-line interface to manage the Fabric Modem, P2P Compute Swarm,
Dual-Mode Routing (Hyper-Local Private vs. Public Mesh Rental), Spotlight-Local
1% Gas Tax Ledger, Low-Latency Gaming Streaming, and Base-12/16/ATGC accelerators.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from loom.hardware.fabric_modem import LoomFabricModem
from loom.hardware.seamless_gateway import SeamlessComputeGateway, ComputeMode
from loom.governance.ring_p0 import RingP0GovernanceController
from loom.csp.p2p_swarm import SwarmPeer, PeerRole, ConnectionMedium
from loom.csp.stream_engine import StreamResolution


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="ClothOS Fabric Mesh & Decentralized Compute Manager ('Wi-Fi & P2P for Compute')"
    )
    subparsers = parser.add_subparsers(dest="command", help="Fabric Commands")

    # Command: status
    subparsers.add_parser("status", help="Show current Fabric Modem link quality, P2P swarm, and gas status")

    # Command: mode
    mode_parser = subparsers.add_parser("mode", help="Inspect or switch compute mode (Hyper-Local Private vs. Public Mesh)")
    mode_parser.add_argument("--set", choices=["private", "mesh"], help="Switch mode: 'private' (air-gapped local) or 'mesh' (P2P rental)")

    # Command: swarm
    swarm_parser = subparsers.add_parser("swarm", help="Inspect decentralized P2P compute swarm (BitTorrent-style mesh)")
    swarm_parser.add_argument("action", nargs="?", default="status", choices=["status", "peers"], help="Action: 'status' or 'peers'")

    # Command: gas
    gas_parser = subparsers.add_parser("gas", help="Inspect Spotlight-Local Gas wallet, 1.0%% protocol tax, and PoVC receipts")
    gas_parser.add_argument("action", nargs="?", default="balance", choices=["balance", "statement", "receipts"], help="Action: 'balance', 'statement', 'receipts'")
    gas_parser.add_argument("--account", type=str, default="p0_operator_wallet", help="Account wallet ID")
    gas_parser.add_argument("--deposit", type=float, default=None, help="Top up account balance in USD")

    # Command: seed
    seed_parser = subparsers.add_parser("seed", help="Offer idle local hardware to the P2P swarm as a Compute Service Provider (CSP)")
    seed_parser.add_argument("--vram", type=float, default=8.0, help="VRAM to allocate for seeding in GB")
    seed_parser.add_argument("--rate", type=float, default=0.50, help="Advertised rate in USD/hour")

    # Command: rent
    rent_parser = subparsers.add_parser("rent", help="Lease high-performance compute from the decentralized P2P swarm (CSC)")
    rent_parser.add_argument("--type", type=str, default="llm_inference", choices=["llm_inference", "cloud_gaming", "3d_rendering"], help="Workload type")
    rent_parser.add_argument("--vram", type=float, default=16.0, help="Required VRAM in GB")
    rent_parser.add_argument("--max-rate", type=float, default=1.50, help="Maximum rate willing to pay in USD/hour")

    # Command: stream-game
    game_parser = subparsers.add_parser("stream-game", help="Benchmark or launch low-latency cloud gaming stream over fiber/wireless")
    game_parser.add_argument("--fps", type=int, default=60, choices=[60, 120], help="Target frame rate")
    game_parser.add_argument("--res", type=str, default="1080p", choices=["720p", "1080p", "1440p", "4k"], help="Stream resolution")
    game_parser.add_argument("--peer", type=str, default=None, help="Target CSP node ID")

    # Command: scan
    subparsers.add_parser("scan", help="Scan local RF and direct-wire airwaves for compute nodes")

    # Command: connect
    connect_parser = subparsers.add_parser("connect", help="Associate with a specific Fabric Mesh SSID")
    connect_parser.add_argument("ssid", type=str, help="SSID of the Fabric node to connect to")

    # Command: exec (seamless execution)
    exec_parser = subparsers.add_parser("exec", help="Seamlessly dispatch a compute task across the mesh")
    exec_parser.add_argument("prompt", type=str, help="Prompt or task to execute")
    exec_parser.add_argument("--model", type=str, default="auto", help="Target model tier (auto, 7b, 70b)")
    exec_parser.add_argument("--vram", type=float, default=4.0, help="Required VRAM in GB")
    exec_parser.add_argument(
        "--type",
        type=str,
        default="llm_inference",
        choices=["llm_inference", "base16", "base16_frame", "base12_convert", "atgc_analysis", "cloud_gaming"],
        help="Workload type (Base-16 is primary native substrate)"
    )
    exec_parser.add_argument("--mode", type=str, default=None, choices=["private", "mesh"], help="Override compute mode")
    exec_parser.add_argument("--nvidia", action="store_true", help="Explicitly require NVIDIA hardware (triggers Node 2 purity protection)")

    # Command: base16 (Dedicated Base-16 Native Inspector)
    b16_parser = subparsers.add_parser("base16", help="Convert number or frame buffer into canonical Base-16 hexadecimal")
    b16_parser.add_argument("input", type=str, help="Number or string payload to encode in Base-16")

    # Command: base12 (Harmonic RoPE Coprocessor)
    b12_parser = subparsers.add_parser("base12", help="Convert number into Base-12 duodecimal (harmonic attention RoPE)")
    b12_parser.add_argument("input", type=str, help="Number to encode in Base-12")

    # Command: atgc (2-Bit Genomic Accelerator)
    atgc_parser = subparsers.add_parser("atgc", help="Analyze DNA/RNA in 2-bit genomic format with exact tail-bits")
    atgc_parser.add_argument("sequence", type=str, help="Nucleotide string (A, C, G, T, U)")

    # Command: governance
    subparsers.add_parser("governance", help="Show Ring P0 Governance Root of Trust audit report")

    # Command: json
    subparsers.add_parser("json", help="Emit raw telemetry as JSON")

    args = parser.parse_args(argv)

    if not args.command or args.command == "status":
        gateway = SeamlessComputeGateway.get_instance()
        print(gateway.get_mesh_status_card())
        return 0

    elif args.command == "mode":
        gateway = SeamlessComputeGateway.get_instance()
        if args.set:
            new_mode = gateway.set_compute_mode(args.set)
            print(f"✅ Compute Mode successfully updated to: {new_mode.value}")
        else:
            print(f"Current Compute Mode: {gateway.get_compute_mode().value}")
        return 0

    elif args.command == "swarm":
        gateway = SeamlessComputeGateway.get_instance()
        stats = gateway.p2p_swarm.get_swarm_stats()
        if args.action == "peers":
            print(f"\n🌐 Decentralized P2P Compute Swarm ({stats['total_peers']} Active Peers):\n")
            print(f"{'PEER ID':<26} {'ROLE':<8} {'MEDIUM':<16} {'RTT':<8} {'BANDWIDTH':<11} {'VRAM':<9} {'CHOKED':<8} {'XI (RATIO)'}")
            print("-" * 105)
            for p in stats["peers"]:
                choked_str = "YES" if p["is_choked"] else "NO (FAST)"
                print(
                    f"{p['peer_id']:<26} {p['role']:<8} {p['medium']:<16} {str(p['rtt_ms']) + ' ms':<8} "
                    f"{str(p['bandwidth_gbps']) + ' Gbps':<11} {str(p['available_vram_gb']) + ' GB':<9} "
                    f"{choked_str:<8} {p['contribution_ratio']:.2f}"
                )
            print("\nTip: Peers with higher contribution ratio (Xi) receive unchoked high-priority compute routing.")
        else:
            print(json.dumps(stats, indent=2))
        return 0

    elif args.command == "gas":
        gateway = SeamlessComputeGateway.get_instance()
        ledger = gateway.gas_ledger
        if args.deposit is not None:
            new_bal = ledger.deposit_fiat_usd(args.account, args.deposit)
            print(f"✅ Deposited ${args.deposit:.2f} USD into {args.account}. New Balance: ${new_bal:.2f} USD")
            return 0

        summary = ledger.get_account_summary(args.account)
        if args.action == "receipts":
            print(f"\n🧾 Recent Proof of Verifiable Computation (PoVC) Receipts ({len(ledger.receipts)}):\n")
            for r in ledger.receipts[-5:]:
                print(f"Receipt ID: {r.receipt_id}")
                print(f"  Task: {r.task_id} | Provider: {r.provider_node_id} | Type: {r.workload_type}")
                print(f"  Gross: ${r.gross_cost_usd:.6f} USD | 1.0% Tax: ${r.gas_tax_protocol_fee_usd:.6f} | Net Host: ${r.net_provider_payout_usd:.6f}")
                print(f"  HMAC-SHA256 Sig: {r.hmac_signature[:24]}...")
                print("-" * 60)
        else:
            print(f"\n💳 Spotlight-Local Gas Account [{args.account}]:\n")
            print(f"  Owner:                    {summary['owner']}")
            print(f"  Gas Balance:              {summary['balance_gas_units']:.2f} Gas Units")
            print(f"  Fiat Value:               ${summary['balance_usd']:.4f} USD")
            print(f"  Total Spent:              ${summary['total_spent_usd']:.4f} USD")
            print(f"  Total Earned:             ${summary['total_earned_usd']:.4f} USD")
            print(f"  Protocol Tax Paid (1.0%): ${summary['total_protocol_tax_paid_usd']:.4f} USD")
            print("\n  Platform Take-Rate: 1.0% (VectorCore Holdings Treasury | Spotlight-Local)")
        return 0

    elif args.command == "seed":
        gateway = SeamlessComputeGateway.get_instance()
        # Register or update local node as a high-capacity seeder
        peer = SwarmPeer(
            peer_id="LoomMesh-LocalSeeder",
            node_name="Local-Rig-Seeder",
            address="127.0.0.1",
            role=PeerRole.SEEDER,
            medium=ConnectionMedium.FIBER_DIRECT,
            rtt_ms=0.2,
            bandwidth_gbps=10.0,
            total_vram_gb=args.vram,
            available_vram_gb=args.vram,
            capacity_tflops=13.0,
            hardware_desc=f"Local Seeder ({args.vram} GB VRAM)",
        )
        gateway.p2p_swarm.register_peer(peer)
        print(f"🚀 Local compute advertised to P2P Swarm as SEEDER:")
        print(f"   Allocated VRAM: {args.vram} GB | Advertised Rate: ${args.rate:.2f}/hr")
        print(f"   Host receives 99.0% net payout on all served compute via Spotlight-Local.")
        return 0

    elif args.command == "rent":
        gateway = SeamlessComputeGateway.get_instance()
        providers = gateway.p2p_swarm.find_optimal_providers(
            required_vram_gb=args.vram,
            count=1,
        )
        if not providers:
            print(f"❌ No proximate providers found with >= {args.vram} GB VRAM.")
            return 1
        p = providers[0]
        print(f"🎯 Matched with proximate P2P Provider for '{args.type}':")
        print(f"   Node: {p.node_name} ({p.peer_id}) via {p.medium.value}")
        print(f"   Latency: {p.rtt_ms} ms | Bandwidth: {p.bandwidth_gbps} Gbps | Available VRAM: {p.available_vram_gb} GB")
        print(f"   Estimated Compute Power: {p.capacity_tflops} TFLOPS [{ 'UNCHOKED' if not p.is_choked else 'CHOKED' }]")
        print(f"   Settlement: Spotlight-Local In-Network (1.0% Platform Gas Tax applied automatically)")
        return 0

    elif args.command == "stream-game":
        gateway = SeamlessComputeGateway.get_instance()
        print(f"🎮 Initializing Low-Latency Interactive Gaming Stream benchmark...")
        res = gateway.dispatch(
            prompt_or_payload={"target_fps": args.fps, "resolution": args.res},
            workload_type="cloud_gaming",
            mode="mesh",
        )
        print(f"\nStatus: {res.status}")
        print(f"Route: {res.execution_route}")
        print(f"Delivery: {res.result_text}")
        print(f"Gas Consumed: {res.gas_consumed:.4f} Gas | Protocol Tax: ${res.gas_tax_protocol_fee_usd:.6f} USD")
        print(f"PoVC Receipt: {res.povc_receipt_id}")
        if res.payload_metadata:
            print("\nStream Telemetry:")
            print(json.dumps(res.payload_metadata, indent=2))
        return 0

    elif args.command == "scan":
        modem = LoomFabricModem(auto_scan=False)
        print("🔍 Scanning RF airwaves and direct-wire interfaces for Fabric nodes...")
        networks = modem.scan_airwaves()
        print(f"\nDiscovered {len(networks)} Fabric compute nodes in range:\n")
        print(f"{'SSID':<22} {'SIGNAL':<10} {'RSSI':<10} {'BANDWIDTH':<12} {'VRAM':<10} {'PURE AMD':<10} {'HARDWARE'}")
        print("-" * 105)
        for net in networks:
            pure_amd_str = "YES (P0)" if net.get("pure_amd_open") else "NO"
            print(
                f"{net['ssid']:<22} {net['signal_bars']:<10} {str(net['rssi_dbm']) + ' dBm':<10} "
                f"{str(net['bandwidth_gbps']) + ' Gbps':<12} {str(net['available_vram_gb']) + ' GB':<10} "
                f"{pure_amd_str:<10} {net['hardware'][:25]}"
            )
        print("\nTo associate with a node, run: python -m loom.hardware.cli connect <SSID>")
        return 0

    elif args.command == "connect":
        gateway = SeamlessComputeGateway.get_instance()
        print(f"Connecting to Fabric Mesh '{args.ssid}'...")
        success = gateway.modem.associate(args.ssid)
        if success:
            print(f"✅ Successfully associated with {args.ssid}!")
            print(gateway.get_mesh_status_card())
            return 0
        else:
            print(f"❌ Failed to associate with {args.ssid}. Out of range or signal attenuated.")
            return 1

    elif args.command == "exec":
        gateway = SeamlessComputeGateway.get_instance()
        mode_str = f" [Mode: {args.mode.upper()}]" if args.mode else ""
        print(f"🌐 Dispatching seamlessly over Fabric Mesh{mode_str}: '{args.prompt}' (Type: {args.type})")
        res = gateway.dispatch(
            prompt_or_payload=args.prompt,
            target_model=args.model,
            required_vram_gb=args.vram,
            workload_type=args.type,
            requires_nvidia=args.nvidia,
            mode=args.mode,
        )
        print(f"\nRoute: {res.execution_route}")
        print(f"Mode: {res.mode}")
        print(f"Latency: {res.total_latency_ms} ms (DMA Transit: {res.dma_transit_time_ms} ms)")
        print(f"Dispatched Compute: {res.tflops_dispatched} TFLOPS [{res.carrier_link_bars}]")
        if res.gas_consumed > 0.0:
            print(f"Gas Consumed: {res.gas_consumed:.4f} Units | 1% Tax: ${res.gas_tax_protocol_fee_usd:.6f} USD | PoVC: {res.povc_receipt_id}")
        print(f"\nResponse:\n{res.result_text}\n")
        if res.payload_metadata:
            print("Payload Metadata:", json.dumps(res.payload_metadata, indent=2))
        return 0

    elif args.command == "base16":
        gateway = SeamlessComputeGateway.get_instance()
        inp = args.input
        try:
            inp_parsed = int(inp, 0) if (inp.startswith("0x") or inp.startswith("0b")) else (float(inp) if "." in inp else int(inp))
        except ValueError:
            inp_parsed = inp
        res = gateway.dispatch(prompt_or_payload=inp_parsed, workload_type="base16")
        print(f"Base-16 Output: {res.result_text}")
        if res.payload_metadata:
            print("Metadata:", json.dumps(res.payload_metadata, indent=2))
        return 0

    elif args.command == "base12":
        gateway = SeamlessComputeGateway.get_instance()
        res = gateway.dispatch(prompt_or_payload=float(args.input), workload_type="base12_convert")
        print(f"Base-12 Output: {res.result_text}")
        if res.payload_metadata:
            print("Metadata:", json.dumps(res.payload_metadata, indent=2))
        return 0

    elif args.command == "atgc":
        gateway = SeamlessComputeGateway.get_instance()
        res = gateway.dispatch(prompt_or_payload=args.sequence, workload_type="atgc_analysis")
        print(f"ATGC Analysis: {res.result_text}")
        if res.payload_metadata:
            print("Metadata:", json.dumps(res.payload_metadata, indent=2))
        return 0

    elif args.command == "governance":
        gov = RingP0GovernanceController.get_instance()
        print(json.dumps(gov.get_governance_report(), indent=2))
        return 0

    elif args.command == "json":
        gateway = SeamlessComputeGateway.get_instance()
        telem = gateway.modem.get_telemetry()
        telem["p2p_swarm"] = gateway.p2p_swarm.get_swarm_stats()
        telem["compute_mode"] = gateway.compute_mode.value
        print(json.dumps(telem, indent=2))
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
