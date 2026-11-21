"""
VectorCore Sovereign Bank Vault & Reserve Engine.

Manages stored-value consumer float, provider compute escrow, 1.0% platform fee
treasury, and Silicon-Backed Asset Lending where hardware loans are repaid
automatically from streaming compute earnings under VectorCore Holdings, LLC.
"""

from __future__ import annotations

import hashlib
import hmac
import time
import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class BankAccount(BaseModel):
    """Sovereign account record held within the VectorCore Ledger."""
    account_id: str = Field(default_factory=lambda: f"vcb-{uuid.uuid4().hex[:12]}")
    owner_id: str
    account_type: str = Field(..., description="'consumer', 'provider_host', 'protocol_treasury', 'reserve_float'")
    balance_usd: float = Field(0.0, description="Available liquid fiat balance in USD")
    escrow_locked_usd: float = Field(0.0, description="Capital locked in active compute sessions")
    lifetime_earnings_usd: float = Field(0.0, description="Cumulative compute yield earned")
    created_at_epoch: float = Field(default_factory=time.time)


class SiliconHardwareLoan(BaseModel):
    """
    Asset-backed hardware financing for hosts purchasing GPUs / Mac Pros.
    Repaid automatically via daily streaming compute revenue splits.
    """
    loan_id: str = Field(default_factory=lambda: f"loan-{uuid.uuid4().hex[:8]}")
    borrower_account_id: str
    hardware_description: str = Field(..., description="e.g. 2x NVIDIA RTX 4090 24GB or Apple Mac Pro M2 Ultra")
    principal_amount_usd: float
    remaining_balance_usd: float
    repayment_split_pct: float = Field(
        0.50,
        description="Percentage of daily compute earnings withheld for loan principal repayment (50% default)"
    )
    interest_apr: float = Field(0.065, description="6.5% fixed APR")
    status: str = Field("active", description="'active', 'paid_in_full', 'defaulted'")
    originated_at_epoch: float = Field(default_factory=time.time)


class VectorCoreBankVault:
    """
    The Central Banking & Reserve Engine for VectorCore Holdings and Spotlight-Local.
    """
    def __init__(self, treasury_secret: str = "vectorcore_bank_master_secret"):
        self.treasury_secret = treasury_secret.encode("utf-8")
        self.accounts: Dict[str, BankAccount] = {}
        self.loans: Dict[str, SiliconHardwareLoan] = {}
        
        # Instantiate master protocol accounts
        self.protocol_treasury = self._create_account("vectorcore_protocol_treasury", "protocol_treasury")
        self.reserve_float = self._create_account("vectorcore_reserve_float", "reserve_float")

    def _create_account(self, owner_id: str, account_type: str, initial_balance: float = 0.0) -> BankAccount:
        acc = BankAccount(
            owner_id=owner_id,
            account_type=account_type,
            balance_usd=initial_balance
        )
        self.accounts[acc.account_id] = acc
        return acc

    def get_or_create_account(self, owner_id: str, account_type: str) -> BankAccount:
        for acc in self.accounts.values():
            if acc.owner_id == owner_id and acc.account_type == account_type:
                return acc
        return self._create_account(owner_id, account_type)

    def deposit_fiat(self, account_id: str, amount_usd: float) -> BankAccount:
        """Consumer preloads funds (the Starbucks Float Model)."""
        if account_id not in self.accounts:
            raise KeyError(f"Account {account_id} not found.")
        acc = self.accounts[account_id]
        acc.balance_usd = round(acc.balance_usd + amount_usd, 4)
        
        # Update systemic reserve float pool
        self.reserve_float.balance_usd = round(self.reserve_float.balance_usd + amount_usd, 4)
        return acc

    def lock_compute_escrow(self, account_id: str, max_spend_usd: float) -> bool:
        acc = self.accounts.get(account_id)
        if not acc or acc.balance_usd < max_spend_usd:
            return False
        acc.balance_usd = round(acc.balance_usd - max_spend_usd, 4)
        acc.escrow_locked_usd = round(acc.escrow_locked_usd + max_spend_usd, 4)
        return True

    def settle_compute_transaction(
        self,
        consumer_account_id: str,
        provider_account_id: str,
        gross_cost_usd: float,
        platform_fee_pct: float = 0.010
    ) -> Dict[str, Any]:
        """
        Executes the atomic 1.0% Spotlight-Local fee split and loan withholding.
        """
        consumer = self.accounts[consumer_account_id]
        provider = self.accounts[provider_account_id]

        if consumer.escrow_locked_usd < gross_cost_usd:
            raise ValueError("Insufficient locked escrow for compute settlement.")

        # Unlock and deduct from consumer
        consumer.escrow_locked_usd = round(consumer.escrow_locked_usd - gross_cost_usd, 4)
        
        # Calculate the 1.0% sL platform fee and 99.0% host gross payout
        fee_amount = round(gross_cost_usd * platform_fee_pct, 6)
        host_gross = round(gross_cost_usd - fee_amount, 6)

        # Deposit platform fee to Protocol Treasury
        self.protocol_treasury.balance_usd = round(self.protocol_treasury.balance_usd + fee_amount, 6)

        # Check for active hardware loan withholding
        loan_deduction = 0.0
        active_loan = self._get_active_loan_for_borrower(provider.account_id)
        if active_loan:
            loan_deduction = round(host_gross * active_loan.repayment_split_pct, 6)
            active_loan.remaining_balance_usd = max(0.0, round(active_loan.remaining_balance_usd - loan_deduction, 6))
            if active_loan.remaining_balance_usd == 0.0:
                active_loan.status = "paid_in_full"

        net_host_credit = round(host_gross - loan_deduction, 6)
        provider.balance_usd = round(provider.balance_usd + net_host_credit, 6)
        provider.lifetime_earnings_usd = round(provider.lifetime_earnings_usd + host_gross, 6)

        # Generate cryptographic banking transaction record
        tx_hash = hashlib.sha256(
            f"{consumer_account_id}:{provider_account_id}:{gross_cost_usd}:{time.time()}".encode("utf-8")
        ).hexdigest()

        return {
            "tx_hash": tx_hash,
            "gross_cost_usd": gross_cost_usd,
            "sl_platform_fee_usd": fee_amount,
            "loan_repayment_usd": loan_deduction,
            "net_provider_payout_usd": net_host_credit,
            "consumer_remaining_balance": consumer.balance_usd,
            "provider_total_balance": provider.balance_usd
        }

    def originate_silicon_hardware_loan(
        self,
        borrower_account_id: str,
        hardware_description: str,
        principal_amount_usd: float
    ) -> SiliconHardwareLoan:
        """Originates an automated self-repaying hardware loan."""
        loan = SiliconHardwareLoan(
            borrower_account_id=borrower_account_id,
            hardware_description=hardware_description,
            principal_amount_usd=principal_amount_usd,
            remaining_balance_usd=principal_amount_usd
        )
        self.loans[loan.loan_id] = loan
        return loan

    def _get_active_loan_for_borrower(self, account_id: str) -> Optional[SiliconHardwareLoan]:
        for loan in self.loans.values():
            if loan.borrower_account_id == account_id and loan.status == "active":
                return loan
        return None

    def calculate_treasury_metrics(self, treasury_yield_apr: float = 0.045) -> Dict[str, Any]:
        """Calculates total customer float, annual treasury yield, and protocol earnings."""
        total_float = self.reserve_float.balance_usd
        annualized_float_yield = round(total_float * treasury_yield_apr, 2)
        total_fee_revenue = self.protocol_treasury.balance_usd
        return {
            "total_customer_float_usd": total_float,
            "annualized_treasury_float_yield_usd": annualized_float_yield,
            "accumulated_protocol_fees_usd": total_fee_revenue,
            "total_active_loans_count": len([l for l in self.loans.values() if l.status == "active"]),
            "total_loans_receivable_usd": sum(l.remaining_balance_usd for l in self.loans.values() if l.status == "active")
        }
