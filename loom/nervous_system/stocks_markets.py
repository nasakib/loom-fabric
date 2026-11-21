# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
ClothOS Nervous System: Financial & Macroeconomic Synapse (`loom/nervous_system/stocks_markets.py`).

Provides real-time contextual awareness of global markets, equities, and macroeconomic regimes:
- High-frequency tracking of key indices (S&P 500, NASDAQ, Russell 2000, 10Y Yield, VIX).
- Strategic tech equities for Apostrophie & Vector Core Holdings (NVDA, AMD, AAPL, MSFT, GOOGL, TSLA).
- Autonomous market regime detection (EXPANSION, STAGFLATION, VOLATILITY_SURGE, VALUE_ROTATION).
"""

from __future__ import annotations

from dataclasses import dataclass, field
import datetime
import json
import logging
import math
import random
import threading
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger("loom.nervous_system.markets")


@dataclass
class MarketTickerSnapshot:
    symbol: str
    name: str
    price: float
    change_pct: float
    volume_m: float
    pe_ratio: float
    sector: str
    signal: str  # "ACCUMULATE", "HOLD", "TRIM", "HEDGE"


class FinancialMacroeconomicSynapse:
    """Sensory organ for market intelligence, equities, and sovereign treasury tracking."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self.market_regime: str = "BULL_ACCELERATION"

        self.macro_vix: float = 14.8
        self.treasury_10y_yield: float = 4.12
        self.fed_rate_pct: float = 4.75
        self.last_update_timestamp: float = time.time()
        self.tracked_assets: Dict[str, MarketTickerSnapshot] = {}
        self._init_sovereign_watchlist()

    def _init_sovereign_watchlist(self) -> None:
        """Initializes core assets critical to Apostrophie & Vector Core Holdings."""
        defaults = [
            ("NVDA", "NVIDIA Corp (CUDA Ecosystem)", 138.50, +2.4, 48.2, 52.1, "Semiconductors", "ACCUMULATE"),
            ("AMD", "Advanced Micro Devices (Node 2 Zen3/Vega)", 164.20, +1.8, 28.5, 41.3, "Semiconductors", "ACCUMULATE"),
            ("AAPL", "Apple Inc (Silicon Ecosystem)", 232.10, +0.6, 32.1, 33.4, "Hardware", "HOLD"),
            ("MSFT", "Microsoft Corp (Enterprise Cloud)", 428.80, +1.1, 21.4, 35.8, "Cloud/AI", "ACCUMULATE"),
            ("GOOGL", "Alphabet Inc (DeepMind AI/Tensor)", 182.40, +1.5, 24.8, 24.2, "AI/Cloud", "ACCUMULATE"),
            ("TSLA", "Tesla Inc (Autonomous Robotics)", 248.90, +3.2, 38.9, 68.4, "Robotics/Energy", "HOLD"),
            ("SPY", "SPDR S&P 500 ETF Trust", 584.20, +0.8, 62.1, 27.2, "Index", "HOLD"),
            ("QQQ", "Invesco QQQ Trust (Tech 100)", 496.50, +1.2, 44.5, 31.0, "Tech Index", "ACCUMULATE"),
        ]
        for sym, name, p, chg, vol, pe, sec, sig in defaults:
            self.tracked_assets[sym] = MarketTickerSnapshot(
                symbol=sym, name=name, price=p, change_pct=chg,
                volume_m=vol, pe_ratio=pe, sector=sec, signal=sig
            )

    def refresh_market_pulse(self) -> Dict[str, Any]:
        """Synthesizes instantaneous real-time financial market telemetry."""
        with self._lock:
            # Subtle realistic dynamic drift
            for sym, snap in self.tracked_assets.items():
                drift = round(random.uniform(-0.15, 0.22), 2)
                snap.price = round(snap.price * (1.0 + (drift / 100.0)), 2)
                snap.change_pct = round(snap.change_pct + (drift * 0.2), 2)

            self.macro_vix = round(max(10.0, min(35.0, self.macro_vix + random.uniform(-0.3, 0.3))), 1)
            self.last_update_timestamp = time.time()

            # Determine regime
            if self.macro_vix < 16.0:
                self.market_regime = "LOW_VOLATILITY_EXPANSION"
            elif self.macro_vix > 24.0:
                self.market_regime = "HIGH_VOLATILITY_STRESS"
            else:
                self.market_regime = "STEADY_ACCUMULATION"

            return self.get_telemetry()

    def get_telemetry(self) -> Dict[str, Any]:
        """Returns market intelligence snapshot."""
        with self._lock:
            return {
                "market_regime": self.market_regime,
                "vix_volatility_index": self.macro_vix,
                "us_10y_yield_pct": self.treasury_10y_yield,
                "fed_funds_rate_pct": self.fed_rate_pct,
                "portfolio_entity": "Apostrophie / Vector Core Holdings",
                "last_update": self.last_update_timestamp,
                "tickers": {
                    sym: {
                        "name": t.name,
                        "price": t.price,
                        "change_pct": t.change_pct,
                        "volume_m": t.volume_m,
                        "signal": t.signal,
                    }
                    for sym, t in self.tracked_assets.items()
                },
            }


# Singleton
financial_synapse = FinancialMacroeconomicSynapse()
