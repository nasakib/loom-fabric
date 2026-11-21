# Copyright (c) 2026 Najmos Sakib / VectorCore Holdings, LLC.
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Loom Fabric Hardware Acceleration & Modem Subsystem.
===================================================
Provides software emulation and driver HALs for the Loom Fabric Modem,
virtual transceivers, zero-copy PCIe DMA engines, and seamless mesh routing.
"""

from loom.hardware.transceiver import (
    FabricTransceiver,
    LinkQuality,
    ModulationScheme,
    TransceiverBand,
)
from loom.hardware.fabric_modem import (
    FabricPeerNode,
    LoomFabricModem,
    ModemState,
)
from loom.hardware.seamless_gateway import (
    SeamlessComputeGateway,
    SeamlessComputeRequest,
    SeamlessComputeResult,
)

__all__ = [
    "FabricTransceiver",
    "LinkQuality",
    "ModulationScheme",
    "TransceiverBand",
    "FabricPeerNode",
    "LoomFabricModem",
    "ModemState",
    "SeamlessComputeGateway",
    "SeamlessComputeRequest",
    "SeamlessComputeResult",
]
