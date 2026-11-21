# Copyright (c) 2026 Najmos Sakib / VectorCore Holdings, LLC.
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Canonical Base-12 (Duodecimal / Dozenal) Codec & Fixed-Point Arithmetic.
=======================================================================
Implements exact duodecimal encoding, decoding, and fixed-point representation.
Resolves binary/decimal recurring fractions (1/3, 1/4, 1/6) into terminating digits,
minimizing entropy loss in rotary positional embeddings (RoPE) and harmonic tensors.

Reference:
- Pitman, Sir Isaac (1852): Phonotypic Journal (Base-12 notation).
- Dozenal Society of America / Great Britain mathematical standards.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

ASCII_DOZENAL_SYMBOLS = "0123456789XE"    # 10=X, 11=E (Standard ASCII Dozenal)
ALPHA_DOZENAL_SYMBOLS = "0123456789AB"    # 10=A, 11=B (Programmer notation)
PITMAN_DOZENAL_SYMBOLS = "0123456789ᘔƐ"   # 10=ᘔ (dek), 11=Ɛ (el)


class DozenalSymbolSet(str, Enum):
    ASCII = "ASCII"       # 0-9, X, E
    ALPHA = "ALPHA"       # 0-9, A, B
    PITMAN = "PITMAN"     # 0-9, ᘔ, Ɛ


@dataclass(frozen=True)
class DozenalFixedPoint:
    """Exact Base-12 fixed-point representation with integer and duodecimal fractional parts."""
    negative: bool
    integral_digits: str
    fractional_digits: str
    symbol_set: DozenalSymbolSet

    def to_string(self) -> str:
        sign = "-" if self.negative else ""
        if self.fractional_digits:
            return f"{sign}{self.integral_digits};{self.fractional_digits}"
        return f"{sign}{self.integral_digits}"

    def to_float(self) -> float:
        val = 0.0
        # Compute integral
        syms = get_symbol_map(self.symbol_set)
        for char in self.integral_digits:
            val = val * 12.0 + syms[char]
        # Compute fraction
        scale = 12.0
        for char in self.fractional_digits:
            val += syms[char] / scale
            scale *= 12.0
        return -val if self.negative else val


def get_symbol_string(sym_set: DozenalSymbolSet) -> str:
    if sym_set == DozenalSymbolSet.ASCII:
        return ASCII_DOZENAL_SYMBOLS
    elif sym_set == DozenalSymbolSet.ALPHA:
        return ALPHA_DOZENAL_SYMBOLS
    elif sym_set == DozenalSymbolSet.PITMAN:
        return PITMAN_DOZENAL_SYMBOLS
    return ASCII_DOZENAL_SYMBOLS


def get_symbol_map(sym_set: DozenalSymbolSet) -> Dict[str, int]:
    syms = get_symbol_string(sym_set)
    mapping = {c: i for i, c in enumerate(syms)}
    # Include uppercase/lowercase fallbacks
    if sym_set == DozenalSymbolSet.ASCII:
        mapping['x'] = 10
        mapping['e'] = 11
    elif sym_set == DozenalSymbolSet.ALPHA:
        mapping['a'] = 10
        mapping['b'] = 11
    return mapping


class Base12Codec:
    """Canonical duodecimal encoder and decoder."""

    def __init__(self, symbol_set: DozenalSymbolSet = DozenalSymbolSet.ASCII):
        self.symbol_set = symbol_set
        self.symbols = get_symbol_string(symbol_set)
        self.char_map = get_symbol_map(symbol_set)

    def encode_int(self, value: int) -> str:
        """Encodes an integer into exact canonical Base-12 representation."""
        if value == 0:
            return self.symbols[0]
        negative = value < 0
        n = abs(value)
        digits: List[str] = []
        while n > 0:
            digits.append(self.symbols[n % 12])
            n //= 12
        res = "".join(reversed(digits))
        return f"-{res}" if negative else res

    def decode_int(self, s: str) -> int:
        """Decodes a Base-12 string into an integer."""
        s = s.strip()
        if not s:
            raise ValueError("Empty string cannot be decoded as duodecimal integer")
        negative = s.startswith("-")
        if negative or s.startswith("+"):
            s = s[1:]
        val = 0
        for char in s:
            if char not in self.char_map:
                raise ValueError(f"Invalid duodecimal character '{char}' for symbol set {self.symbol_set.value}")
            val = val * 12 + self.char_map[char]
        return -val if negative else val

    def encode_float(self, value: float, precision: int = 8) -> DozenalFixedPoint:
        """Converts an IEEE 754 float into a canonical Base-12 fixed-point representation."""
        if math.isnan(value) or math.isinf(value):
            raise ValueError(f"Cannot encode NaN or Infinite float to duodecimal: {value}")
        
        negative = value < 0
        v = abs(value)
        int_part = int(math.floor(v))
        frac_part = v - int_part

        int_digits = self.encode_int(int_part)
        if int_digits.startswith("-"):
            int_digits = int_digits[1:]

        frac_digits: List[str] = []
        for _ in range(precision):
            frac_part *= 12.0
            digit = int(frac_part)
            frac_digits.append(self.symbols[digit])
            frac_part -= digit
            if frac_part < 1e-12:
                break # Terminated cleanly

        return DozenalFixedPoint(
            negative=negative,
            integral_digits=int_digits,
            fractional_digits="".join(frac_digits),
            symbol_set=self.symbol_set,
        )

    def decode_fixed_point(self, s: str) -> DozenalFixedPoint:
        """Parses a Base-12 string with optional semicolon or period radix separator."""
        s = s.strip()
        if not s:
            raise ValueError("Cannot parse empty duodecimal string")
        negative = s.startswith("-")
        if negative or s.startswith("+"):
            s = s[1:]

        separator = ";" if ";" in s else ("." if "." in s else None)
        if separator:
            int_part, frac_part = s.split(separator, 1)
        else:
            int_part = s
            frac_part = ""

        # Validate characters
        for c in int_part:
            if c not in self.char_map:
                raise ValueError(f"Invalid integer digit '{c}' in duodecimal string '{s}'")
        for c in frac_part:
            if c not in self.char_map:
                raise ValueError(f"Invalid fractional digit '{c}' in duodecimal string '{s}'")

        return DozenalFixedPoint(
            negative=negative,
            integral_digits=int_part or "0",
            fractional_digits=frac_part,
            symbol_set=self.symbol_set,
        )

    def evaluate_entropy_reduction(self, rational_fractions: Optional[List[Tuple[int, int]]] = None) -> Dict[str, Any]:
        """Evaluates roundoff entropy reduction of Base-12 vs Base-10 for standard harmonic divisions."""
        fractions = rational_fractions or [
            (1, 2), (1, 3), (1, 4), (1, 6), (1, 8), (1, 9), (1, 12), (5, 12), (7, 12)
        ]
        
        base10_entropy_bits = 0.0
        base12_entropy_bits = 0.0

        details = []
        for num, den in fractions:
            val = num / den
            # In Base-10: check if denominator factors are only 2 and 5
            temp_den = den
            while temp_den % 2 == 0: temp_den //= 2
            while temp_den % 5 == 0: temp_den //= 5
            terminates_b10 = (temp_den == 1)

            # In Base-12: check if denominator factors are only 2 and 3
            temp_den12 = den
            while temp_den12 % 2 == 0: temp_den12 //= 2
            while temp_den12 % 3 == 0: temp_den12 //= 3
            terminates_b12 = (temp_den12 == 1)

            # Recurring loss contributes entropy uncertainty
            e_b10 = 0.0 if terminates_b10 else 1.585 # ~log2(3) bits of recurring loss
            e_b12 = 0.0 if terminates_b12 else 1.585

            base10_entropy_bits += e_b10
            base12_entropy_bits += e_b12

            fp12 = self.encode_float(val, precision=6)
            details.append({
                "fraction": f"{num}/{den}",
                "decimal": f"{val:.6f}",
                "dozenal": fp12.to_string(),
                "terminates_b10": terminates_b10,
                "terminates_b12": terminates_b12,
            })

        reduction_pct = 0.0
        if base10_entropy_bits > 0:
            reduction_pct = ((base10_entropy_bits - base12_entropy_bits) / base10_entropy_bits) * 100.0

        return {
            "tested_fractions_count": len(fractions),
            "base10_total_entropy_bits": round(base10_entropy_bits, 3),
            "base12_total_entropy_bits": round(base12_entropy_bits, 3),
            "entropy_reduction_pct": round(reduction_pct, 2),
            "details": details,
        }
