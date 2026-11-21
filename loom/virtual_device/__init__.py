"""
VectorCore ClothOS Virtual Device Subsystem.

Provides virtual hardware device drivers and runtime bridges so local operating
systems, frameworks, and applications perceive the Loom Fabric mesh as
additional local PCIe GPU/CPU accelerators.
"""

from loom.virtual_device.virtual_accelerator import (
    VirtualComputeDevice,
    VirtualAcceleratorManager,
    virtual_accelerator_manager,
)
from loom.virtual_device.torch_shim import torch_mesh

__all__ = [
    "VirtualComputeDevice",
    "VirtualAcceleratorManager",
    "virtual_accelerator_manager",
    "torch_mesh",
]
