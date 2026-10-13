"""
Fabric: Unified Cross-Platform Distributed Compute Stack (Fabric + Loom + Stitch + Torque + ClothOS).
"""

import loom  # Enforces Windows CREATE_NO_WINDOW subprocess guard globally

from fabric.routing.router import (
    DAGNode,
    DAGExecutionPlan,
    QCTRouteDecision,
    QCTHybridRouter,
)
from fabric.ipc.zmq_bus import (
    TelemetryEnvelope,
    StitchZMQTelemetryBus,
)
from fabric.discovery.nodes import (
    DiscoveredFabricNode,
    ClusterTopologySnapshot,
    CrossPlatformNodeDiscovery,
)

__version__ = "0.2.0"
__all__ = [
    "DAGNode",
    "DAGExecutionPlan",
    "QCTRouteDecision",
    "QCTHybridRouter",
    "TelemetryEnvelope",
    "StitchZMQTelemetryBus",
    "DiscoveredFabricNode",
    "ClusterTopologySnapshot",
    "CrossPlatformNodeDiscovery",
]
