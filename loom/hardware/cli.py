# Copyright (c) 2026 Najmos Sakib / VectorCore Holdings, LLC.
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Loom Fabric Modem & Seamless Compute CLI (`loom/hardware/cli.py`).
================================================================
Command-line interface to manage the Fabric Modem, scan for in-range
compute networks, inspect signal bars, and dispatch compute seamlessly.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from loom.hardware.fabric_modem import LoomFabricModem
from loom.hardware.seamless_gateway import SeamlessComputeGateway


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Loom Fabric Modem & Seamless Mesh Manager ('Wi-Fi for Compute')"
    )
    subparsers = parser.add_subparsers(dest="command", help="Fabric Modem Subcommands")

    # Command: status
    subparsers.add_parser("status", help="Show current Fabric Modem link quality and signal bars")

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

    # Command: json
    subparsers.add_parser("json", help="Emit raw telemetry as JSON")

    args = parser.parse_args(argv)

    if not args.command or args.command == "status":
        gateway = SeamlessComputeGateway.get_instance()
        print(gateway.get_mesh_status_card())
        return 0

    elif args.command == "scan":
        modem = LoomFabricModem(auto_scan=False)
        print("🔍 Scanning RF airwaves and direct-wire interfaces for Fabric nodes...")
        networks = modem.scan_airwaves()
        print(f"\nDiscovered {len(networks)} Fabric compute nodes in range:\n")
        print(f"{'SSID':<22} {'SIGNAL':<10} {'RSSI':<10} {'BANDWIDTH':<12} {'VRAM':<10} {'HARDWARE'}")
        print("-" * 90)
        for net in networks:
            print(
                f"{net['ssid']:<22} {net['signal_bars']:<10} {str(net['rssi_dbm']) + ' dBm':<10} "
                f"{str(net['bandwidth_gbps']) + ' Gbps':<12} {str(net['available_vram_gb']) + ' GB':<10} "
                f"{net['hardware'][:30]}"
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
        print(f"🌐 Dispatching seamlessly over Fabric Mesh: '{args.prompt}'")
        res = gateway.dispatch(
            prompt_or_payload=args.prompt,
            target_model=args.model,
            required_vram_gb=args.vram,
        )
        print(f"\n{res.execution_route}")
        print(f"Latency: {res.total_latency_ms} ms (DMA Transit: {res.dma_transit_time_ms} ms)")
        print(f"Dispatched Compute: {res.tflops_dispatched} TFLOPS [{res.carrier_link_bars}]")
        print(f"\nResponse:\n{res.result_text}\n")
        return 0

    elif args.command == "json":
        gateway = SeamlessComputeGateway.get_instance()
        print(json.dumps(gateway.modem.get_telemetry(), indent=2))
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
