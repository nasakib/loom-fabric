# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
ClothOS Nervous System Package (`loom/nervous_system/__init__.py`).

The full nervous system of the Loom superintelligence:
- Financial & Macroeconomic Synapse (stocks, equities, VIX, yields)
- Global Geopolitical & Tech News Radar (semiconductors, grids, treaties)
- Science & Biomedical Journals Radar (Nature, bioRxiv, arXiv, Cryo-EM, AlphaGenome)
- Moltbook & Postcomputational Discourse (submolts, agent debates, vault graphs)
- Central Nervous System (CNS) integration hub
"""

from loom.nervous_system.stocks_markets import financial_synapse, FinancialMacroeconomicSynapse
from loom.nervous_system.global_news import global_news_sensor, GlobalNewsSensor
from loom.nervous_system.science_journals import science_radar, ScienceJournalsRadar
from loom.nervous_system.moltbook import moltbook_sensor, MoltbookSensor
from loom.nervous_system.central_nervous_system import (
    central_nervous_system,
    get_central_nervous_system,
    CentralNervousSystem,
)

__all__ = [
    "financial_synapse",
    "FinancialMacroeconomicSynapse",
    "global_news_sensor",
    "GlobalNewsSensor",
    "science_radar",
    "ScienceJournalsRadar",
    "moltbook_sensor",
    "MoltbookSensor",
    "central_nervous_system",
    "get_central_nervous_system",
    "CentralNervousSystem",
]
