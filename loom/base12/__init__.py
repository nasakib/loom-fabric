# Copyright (c) 2026 Najmos Sakib / VectorCore Holdings, LLC.
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Loom Base-12 Subsystem: Canonical Duodecimal (Dozenal) Computing.
"""

from loom.base12.codec import (
    Base12Codec,
    DozenalFixedPoint,
    DozenalSymbolSet,
    ASCII_DOZENAL_SYMBOLS,
    ALPHA_DOZENAL_SYMBOLS,
    PITMAN_DOZENAL_SYMBOLS,
)

__all__ = [
    "Base12Codec",
    "DozenalFixedPoint",
    "DozenalSymbolSet",
    "ASCII_DOZENAL_SYMBOLS",
    "ALPHA_DOZENAL_SYMBOLS",
    "PITMAN_DOZENAL_SYMBOLS",
]
