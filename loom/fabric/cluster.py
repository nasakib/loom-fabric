"""
Fabric Cluster Manager: Ray Bootstrap, Dual-Homed Network Resiliency & Wake-on-LAN.

Part of Pillar 3: FABRIC.
Coordinates distributed execution across Head Node (192.168.99.2) and Worker Node (192.168.99.1):
- Dual-homed network probing: Direct-wire Ethernet (192.168.99.1) -> Tailscale mesh -> Local Head fallback.
- Wake-on-LAN (WoL) magic packet dispatch to wake dormant worker nodes.
- Custom accelerator tags (`GPU_NVIDIA: 12`, `GPU_AMD: 8`, `CPU_HEAD: 16`).
"""

from __future__ import annotations

import logging
import socket
import time
from typing import Any, Dict, Optional, Tuple
from loom.config import get_settings

logger = logging.getLogger("loom.fabric.cluster")


class DualHomedNetworkManager:
    """Manages dual-homed connectivity with automatic failover."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def probe_socket(self, host: str, port: int, timeout: float = 1.0) -> bool:
        """Tests TCP socket connectivity with strict timeout."""
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            return False

    def send_wol(self, mac_address: Optional[str] = None) -> bool:
        """Dispatches Wake-on-LAN magic packet to awaken remote worker node."""
        mac = mac_address or self.settings.worker_nodes[0].wol_mac or "00:D8:61:A4:7B:12"
        clean_mac = mac.replace(":", "").replace("-", "").strip()
        if len(clean_mac) != 12:
            return False
        try:
            mac_bytes = bytes.fromhex(clean_mac)
            magic_payload = b"\xff" * 6 + mac_bytes * 16
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                sock.sendto(magic_payload, ("192.168.99.255", 9))
                sock.sendto(magic_payload, ("255.255.255.255", 9))
            logger.info(f"Dispatched WoL magic packet to MAC {mac}.")
            return True
        except Exception as e:
            logger.warning(f"Failed to dispatch WoL packet: {e}")
            return False

    def resolve_active_worker_endpoint(self, target_port: int = 8080) -> Tuple[str, str]:
        """Resolves active worker route: Direct LAN -> Tailscale Mesh -> Local Head Node Fallback.

        Returns:
            Tuple of (resolved_url, route_label)
        """
        worker = self.settings.worker_nodes[0]
        direct_ip = worker.ip
        tailscale_ip = worker.tailscale_ip or "100.100.99.1"

        # 1. Primary Route: Direct-wire 1 Gbps Ethernet
        if self.probe_socket(direct_ip, target_port, timeout=0.8):
            return f"http://{direct_ip}:{target_port}", "Direct-Ethernet"

        # Also check Stitch Bridge port (5555) on direct IP
        if self.probe_socket(direct_ip, 5555, timeout=0.8):
            return f"http://{direct_ip}:{target_port}", "Direct-Ethernet-Bridge-Active"

        # 2. Secondary Route: Tailscale Encrypted Overlay Mesh
        if self.probe_socket(tailscale_ip, target_port, timeout=1.2):
            logger.warning("Primary direct LAN unreachable. Failed over to Tailscale mesh.")
            return f"http://{tailscale_ip}:{target_port}", "Tailscale-Mesh"

        # 3. Attempt Wake-on-LAN dispatch if worker appears asleep
        logger.warning("Worker unreachable across both routes. Dispatching WoL packet...")
        self.send_wol(worker.wol_mac)

        # 4. Graceful Local Fallback: Head Node CPU inference
        head_ip = "127.0.0.1"
        logger.error("Cluster degraded to Head Node CPU fallback.")
        return f"http://{head_ip}:{target_port}", "Head-Node-CPU-Degraded"


class FabricClusterOrchestrator:
    """Manages Ray cluster connection, node discovery, and lifecycle."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.network = DualHomedNetworkManager()
        self._ray_connected = False

    @property
    def is_connected(self) -> bool:
        """Returns True if connected to an active Ray cluster."""
        return self._ray_connected

    def connect(self) -> bool:
        """Connects to the Ray cluster head node with custom resource descriptors."""
        try:
            import ray
            if not ray.is_initialized():
                ray.init(
                    address=f"{self.settings.head_node.ip}:{self.settings.head_node.ray_port}",
                    ignore_reinit_error=True,
                    logging_level=logging.WARNING,
                )
            self._ray_connected = True
            logger.info("Successfully connected to Ray cluster.")
            return True
        except Exception as e:
            logger.debug(f"Ray cluster connect attempt: {e}")
            self._ray_connected = False
            return False

    def get_cluster_status(self) -> Dict[str, Any]:
        """Returns physical cluster health, active nodes, and route status."""
        active_url, route = self.network.resolve_active_worker_endpoint(8080)
        return {
            "ray_connected": self._ray_connected,
            "active_worker_url": active_url,
            "active_route": route,
            "head_node": self.settings.head_node.model_dump(),
            "worker_node": self.settings.worker_nodes[0].model_dump() if self.settings.worker_nodes else None,
        }
