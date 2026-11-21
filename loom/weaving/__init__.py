# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
ClothOS Weaving Ontology & Architecture (`loom/weaving`).

The full, fleshed-out implementation of:
1. Thread (Warp invariants & Weft dynamic inputs)
2. Shuttle (High-velocity cross-node transport & IPC)
3. Stitch (Atomic Zero-OOM memory binding, systolic TPU MAC, & Fourier truth locks)
4. Loom (Master apparatus, 5-stage planner, test-time reasoning, torque security)
5. Fabric (Distributed physical silicon mesh, Kuramoto phase lock r = 0.965)
6. Cloth / ClothOS (Living sovereign operating system garment)
"""

from .threads import (
    WarpType,
    WeftPriority,
    WarpThread,
    WeftThread,
    InterlacedPoint,
    ThreadRegistry,
)
from .shuttle import (
    ShuttleState,
    ShuttleFlightTelemetry,
    WeavingShuttle,
    get_shuttle,
    shuttle,
)
from .stitch import (
    StitchType,
    StitchRecord,
    StitchEngine,
    get_stitch_engine,
    stitch_engine,
)
from .loom import (
    LoomHarnessState,
    WovenTapestry,
    LoomMasterApparatus,
    get_loom_apparatus,
    loom_apparatus,
)
from .fabric import (
    FabricNodeProfile,
    FabricElasticityMetrics,
    FabricSubstrate,
    get_fabric_substrate,
    fabric_substrate,
)
from .cloth import (
    ClothOSGarment,
    get_clothos_garment,
    clothos_garment,
)

__all__ = [
    # Threads
    "WarpType",
    "WeftPriority",
    "WarpThread",
    "WeftThread",
    "InterlacedPoint",
    "ThreadRegistry",
    # Shuttle
    "ShuttleState",
    "ShuttleFlightTelemetry",
    "WeavingShuttle",
    "get_shuttle",
    "shuttle",
    # Stitch
    "StitchType",
    "StitchRecord",
    "StitchEngine",
    "get_stitch_engine",
    "stitch_engine",
    # Loom
    "LoomHarnessState",
    "WovenTapestry",
    "LoomMasterApparatus",
    "get_loom_apparatus",
    "loom_apparatus",
    # Fabric
    "FabricNodeProfile",
    "FabricElasticityMetrics",
    "FabricSubstrate",
    "get_fabric_substrate",
    "fabric_substrate",
    # Cloth
    "ClothOSGarment",
    "get_clothos_garment",
    "clothos_garment",
]
