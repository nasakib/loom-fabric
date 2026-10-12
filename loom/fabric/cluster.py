"""Ray Cluster Connectivity and Node Discovery Manager.

Initializes, queries, and maintains resilient communication with the Ray distributed
cluster plane across the dual-node mesh (SkyTech GPU Worker <-> Ryzen Head Node).

Architecture Note (Rust Migration Target):
    This module maps to `loom_fabric::cluster` in Rust:
    - Communicates with Ray Core via GCS (Global Control Store) gRPC API.
    - Manages cluster topology and node heartbeats through asynchronous async-trait actors.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
import ray
from pydantic import BaseModel, Field

from ..config import settings

logger = logging.getLogger("loom.fabric.cluster")


class RayNodeDescriptor(BaseModel):
    """Specification of an active node discovered in the Ray cluster."""

    node_id: str = Field(..., description="Unique 28-byte hex Ray node identifier.")
    node_ip: str = Field(..., description="Node network IP address.")
    hostname: str = Field(..., description="Node machine hostname.")
    is_head_node: bool = Field(..., description="Whether this node acts as the Ray GCS Head.")
    is_alive: bool = Field(..., description="Whether the node is actively passing heartbeats.")
    resources_total: Dict[str, float] = Field(default_factory=dict, description="Total physical resources registered.")
    resources_available: Dict[str, float] = Field(default_factory=dict, description="Currently unallocated resources.")


class ClusterTopologyReport(BaseModel):
    """Comprehensive snapshot of the Ray distributed cluster status."""

    is_connected: bool = Field(..., description="Whether Loom is actively connected to Ray.")
    gcs_address: str = Field(..., description="Ray GCS server address (e.g., '192.168.99.2:6379').")
    dashboard_url: str = Field(..., description="Ray dashboard and job submission URL.")
    total_nodes: int = Field(default=0, description="Total count of discovered nodes.")
    alive_nodes: int = Field(default=0, description="Count of responsive, healthy nodes.")
    nodes: List[RayNodeDescriptor] = Field(default_factory=list, description="Per-node detailed metrics.")
    cluster_resources: Dict[str, float] = Field(default_factory=dict, description="Summed total cluster resources.")


class RayClusterManager:
    """Manages connection, health probing, and actor discovery across the Ray cluster."""

    def __init__(self, gcs_address: Optional[str] = None):
        """Initializes the cluster manager.

        Args:
            gcs_address: Optional override for the Ray Head node GCS address (ip:port).
        """
        self.gcs_address = gcs_address or f"{settings.head_node.ip}:{settings.head_node.ray_port}"
    @property
    def is_connected(self) -> bool:
        """Returns True if the runtime is currently connected to Ray."""
        return ray.is_initialized()

    def ensure_connected(self, timeout_seconds: int = 15) -> bool:
        """Ensures that the current runtime process is attached to the Ray cluster.

        Args:
            timeout_seconds: Timeout for Ray connection initialization.

        Returns:
            True if connected, False if the cluster could not be reached.
        """
        if ray.is_initialized():
            return True

        try:
            logger.info(f"Connecting to Ray cluster at {self.gcs_address}...")
            # Attempt remote connection to Ray Head node
            ray.init(
                address=self.gcs_address,
                ignore_reinit_error=True,
                _temp_dir=None,
            )
            logger.info("Successfully attached to Ray cluster.")
            return True
        except Exception as e:
            logger.warning(f"Failed to connect to Ray Head at {self.gcs_address}: {e}")
            # Fallback: check if local ray instance can be initialized
            try:
                logger.info("Attempting local ray connection...")
                ray.init(address="auto", ignore_reinit_error=True)
                return True
            except Exception as e2:
                logger.error(f"Ray auto-connection also failed: {e2}")
                return False

    def get_cluster_topology(self) -> ClusterTopologyReport:
        """Queries the Ray Global Control Store (GCS) for all active cluster nodes.

        Returns:
            ClusterTopologyReport encapsulating live nodes and custom resources.
        """
        if not self.ensure_connected():
            return ClusterTopologyReport(
                is_connected=False,
                gcs_address=self.gcs_address,
                dashboard_url=self.dashboard_url,
                total_nodes=0,
                alive_nodes=0,
                nodes=[],
                cluster_resources={},
            )

        try:
            raw_nodes = ray.nodes()
            cluster_res = ray.cluster_resources()
            node_descriptors: List[RayNodeDescriptor] = []
            alive_count = 0

            for n in raw_nodes:
                is_alive = n.get("Alive", False)
                if is_alive:
                    alive_count += 1

                node_ip = n.get("NodeManagerAddress", "")
                is_head = (node_ip == settings.head_node.ip) or ("node:__internal_head__" in n.get("Resources", {}))

                node_descriptors.append(
                    RayNodeDescriptor(
                        node_id=n.get("NodeID", ""),
                        node_ip=node_ip,
                        hostname=n.get("NodeName", node_ip),
                        is_head_node=is_head,
                        is_alive=is_alive,
                        resources_total=n.get("Resources", {}),
                        resources_available={},
                    )
                )

            return ClusterTopologyReport(
                is_connected=True,
                gcs_address=self.gcs_address,
                dashboard_url=self.dashboard_url,
                total_nodes=len(raw_nodes),
                alive_nodes=alive_count,
                nodes=node_descriptors,
                cluster_resources=cluster_res,
            )
        except Exception as e:
            logger.error(f"Error reading cluster topology from GCS: {e}")
            return ClusterTopologyReport(
                is_connected=False,
                gcs_address=self.gcs_address,
                dashboard_url=self.dashboard_url,
                total_nodes=0,
                alive_nodes=0,
                nodes=[],
                cluster_resources={},
            )

    def shutdown(self) -> None:
        """Disconnects the local process from the Ray cluster."""
        if ray.is_initialized():
            ray.shutdown()
