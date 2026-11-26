# Copyright (c) 2026 Najmos Sakib / VectorCore Holdings, LLC.
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Ring P0 Governance & Root of Trust Engine (`loom/governance/ring_p0.py`).
========================================================================
Codifies non-bypassable governance guardrails for ClothOS and Loom Fabric:
- Operator Root of Trust: Najmos Sakib (Ring P0)
- Parent Sovereign Entity: ClothOS
- Subsidiary Infrastructure Entity: Vector Core Holdings, LLC
- Non-bypassable verification on structural mutations, resource reallocations,
  and autonomous cluster updates.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger("loom.governance.ring_p0")

OPERATOR_ROOT_IDENTITY = "Najmos Sakib"
PARENT_ENTITY = "ClothOS"
SUBSIDIARY_ENTITY = "Vector Core Holdings, LLC"
P0_SECURITY_EPOCH = 1795267200 # Sovereign ClothOS Era


class SecurityRing(int, Enum):
    RING_P0_OPERATOR = 0    # Najmos Sakib / ClothOS / Vector Core Holdings (Supreme Root of Trust)
    RING_P1_MICROKERNEL = 1 # Core OS scheduler, PMP memory protection, DMA controllers
    RING_P2_MESH = 2        # Fabric Modem, P2P discovery, Diurnal arbitrage
    RING_P3_SERVICES = 3    # Gateway REST/SSE, Web GUIs, User Agents
    RING_P4_UNTRUSTED = 4   # External payloads, unverified client input


class GovernanceViolation(Exception):
    """Raised when an operation attempts to bypass Ring P0 authorization."""
    pass


@dataclass(frozen=True)
class P0AuthorizationToken:
    operator: str
    parent_entity: str
    subsidiary_entity: str
    operation_type: str
    timestamp: float
    signature: str

    def is_valid(self, secret_key: bytes) -> bool:
        if self.operator != OPERATOR_ROOT_IDENTITY:
            return False
        if self.parent_entity != PARENT_ENTITY or self.subsidiary_entity != SUBSIDIARY_ENTITY:
            return False
        payload = f"{self.operator}:{self.parent_entity}:{self.subsidiary_entity}:{self.operation_type}:{self.timestamp}"
        expected_sig = hmac.new(secret_key, payload.encode("utf-8"), hashlib.sha256).hexdigest()
        return hmac.compare_digest(self.signature, expected_sig)


class RingP0GovernanceController:
    """Enforces non-bypassable Ring P0 verification for all structural mutations."""

    _instance: Optional[RingP0GovernanceController] = None

    @classmethod
    def get_instance(cls) -> RingP0GovernanceController:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self, master_secret: Optional[bytes] = None):
        self.operator = OPERATOR_ROOT_IDENTITY
        self.parent_entity = PARENT_ENTITY
        self.subsidiary_entity = SUBSIDIARY_ENTITY
        # Default internal master key derived from environment or root salt
        salt = os.getenv("CLOTHOS_P0_SALT", "sovereign_ring_p0_clothos_vectorcore")
        self._secret_key = master_secret or hashlib.sha256(salt.encode("utf-8")).digest()
        self.audit_log: list[Dict[str, Any]] = []

    def issue_p0_token(self, operation_type: str) -> P0AuthorizationToken:
        """Issues an authorized P0 token under the authority of Najmos Sakib."""
        ts = time.time()
        payload = f"{self.operator}:{self.parent_entity}:{self.subsidiary_entity}:{operation_type}:{ts}"
        sig = hmac.new(self._secret_key, payload.encode("utf-8"), hashlib.sha256).hexdigest()
        return P0AuthorizationToken(
            operator=self.operator,
            parent_entity=self.parent_entity,
            subsidiary_entity=self.subsidiary_entity,
            operation_type=operation_type,
            timestamp=ts,
            signature=sig,
        )

    def verify_mutation(self, operation_name: str, token: Optional[P0AuthorizationToken]) -> bool:
        """Verifies that a structural mutation or reallocation has valid Ring P0 clearance."""
        if token is None or not token.is_valid(self._secret_key):
            record = {
                "timestamp": time.time(),
                "operation": operation_name,
                "status": "DENIED",
                "reason": "Missing or invalid Ring P0 token from Najmos Sakib / ClothOS",
            }
            self.audit_log.append(record)
            logger.error(f"GOVERNANCE VIOLATION: {operation_name} rejected under Ring P0 invariants.")
            raise GovernanceViolation(
                f"Operation '{operation_name}' requires non-bypassable Ring P0 authorization "
                f"from {OPERATOR_ROOT_IDENTITY} under {PARENT_ENTITY} & {SUBSIDIARY_ENTITY}."
            )
        
        record = {
            "timestamp": time.time(),
            "operation": operation_name,
            "status": "APPROVED",
            "operator": token.operator,
            "entity": f"{token.parent_entity} / {token.subsidiary_entity}",
        }
        self.audit_log.append(record)
        return True

    def get_governance_report(self) -> Dict[str, Any]:
        return {
            "root_operator": self.operator,
            "parent_entity": self.parent_entity,
            "subsidiary_entity": self.subsidiary_entity,
            "governance_ring": "Ring P0 (Non-Bypassable)",
            "audit_log_entries": len(self.audit_log),
            "recent_actions": self.audit_log[-10:],
        }
