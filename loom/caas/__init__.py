"""
VectorCore ClothOS Compute-as-a-Service (CaaS) Package.

Components:
- `VectorCoreBankVault`: Stored-value float, escrow locking, 1.0% treasury accumulation, and hardware lending.
- `P2PComputeAuction`: Continuous double-auction order book for spot compute capacity.
- `CaaSHostDaemon`: Autonomous node agent for CSP providers.
- `ClothosCaaSClient`: Client SDK for consumers, games, and creative workflows.
"""

from loom.caas.bank_vault import VectorCoreBankVault, BankAccount, SiliconHardwareLoan
from loom.caas.p2p_auction import P2PComputeAuction, BidOrder, AskOrder, AuctionMatchResult
from loom.caas.daemon import CaaSHostDaemon, SiliconDetector
from loom.caas.client_sdk import ClothosCaaSClient, ComputeSession

__all__ = [
    "VectorCoreBankVault",
    "BankAccount",
    "SiliconHardwareLoan",
    "P2PComputeAuction",
    "BidOrder",
    "AskOrder",
    "AuctionMatchResult",
    "CaaSHostDaemon",
    "SiliconDetector",
    "ClothosCaaSClient",
    "ComputeSession",
]
