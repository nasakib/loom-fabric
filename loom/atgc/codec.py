# Copyright (c) 2026 Najmos Sakib / VectorCore Holdings, LLC.
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Canonical 2-Bit ATGC Genomic Codec & Sequence Analysis Engine.
==============================================================
Encodes nucleotide sequences at 2 bits per base (4 bases/byte, 8 bases/16-bit word).
Guarantees exact length and tail-bit tracking to prevent zero-padding from being
misinterpreted as Adenine ('A').

Encoding Schema:
- Adenine  (A) = 00_2 (0)
- Cytosine (C) = 01_2 (1)
- Guanine  (G) = 10_2 (2)
- Thymine  (T) = 11_2 (3) (Uracil 'U' normalized to 'T')

Bit Packing Order (MSB-to-LSB):
- Byte: [Base 0 (7:6) | Base 1 (5:4) | Base 2 (3:2) | Base 3 (1:0)]
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Generator, Iterator, List, Optional, Tuple, Union

BASE_TO_2BIT = {
    'A': 0, 'a': 0,
    'C': 1, 'c': 1,
    'G': 2, 'g': 2,
    'T': 3, 't': 3,
    'U': 3, 'u': 3, # RNA Uracil mapped to Thymine
}

TWO_BIT_TO_BASE = ['A', 'C', 'G', 'T']
COMPLEMENT_MAP = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}


@dataclass(frozen=True)
class PackedDNA:
    """Stores bit-packed nucleotide data with explicit length and tail-bit boundaries."""
    packed_bytes: bytes
    total_bases: int

    @property
    def byte_count(self) -> int:
        return len(self.packed_bytes)

    @property
    def tail_bits(self) -> int:
        """Returns number of unused padding bits in the final byte."""
        rem = self.total_bases % 4
        return 0 if rem == 0 else (4 - rem) * 2

    def to_string(self) -> str:
        """Decodes packed bytes back to canonical string, respecting total_bases boundary."""
        if self.total_bases == 0:
            return ""
        chars: List[str] = []
        bases_read = 0
        for b in self.packed_bytes:
            for shift in (6, 4, 2, 0):
                if bases_read >= self.total_bases:
                    break
                val = (b >> shift) & 0x03
                chars.append(TWO_BIT_TO_BASE[val])
                bases_read += 1
        return "".join(chars)


class AtgcCodec:
    """High-performance 2-bit genomic encoder, scanner, and search accelerator."""

    @staticmethod
    def encode(sequence: str) -> PackedDNA:
        """Packs a nucleotide string into 2 bits per base, tracking exact tail length."""
        cleaned = sequence.strip()
        n = len(cleaned)
        if n == 0:
            return PackedDNA(packed_bytes=b"", total_bases=0)

        out = bytearray((n + 3) // 4)
        for i, char in enumerate(cleaned):
            if char not in BASE_TO_2BIT:
                raise ValueError(f"Invalid nucleotide character '{char}' at position {i}. Must be A, C, G, T, or U.")
            val = BASE_TO_2BIT[char]
            byte_idx = i // 4
            shift = 6 - ((i % 4) * 2)
            out[byte_idx] |= (val << shift)

        return PackedDNA(packed_bytes=bytes(out), total_bases=n)

    @staticmethod
    def decode(packed: PackedDNA) -> str:
        """Decodes PackedDNA to canonical nucleotide string without reading padding."""
        return packed.to_string()

    @staticmethod
    def complement(packed: PackedDNA) -> PackedDNA:
        """Computes bitwise complement (A<->T, C<->G) across packed bytes."""
        if packed.total_bases == 0:
            return packed

        # In 2-bit space: A(00)^11=T(11), C(01)^11=G(10), G(10)^11=C(01), T(11)^11=A(00)
        # Simply bitwise invert each byte, but mask out trailing padding in the last byte
        raw = bytearray(b ^ 0xFF for b in packed.packed_bytes)
        
        # Zero out padding bits in the final byte so they stay 00
        rem = packed.total_bases % 4
        if rem != 0:
            mask = 0xFF << ((4 - rem) * 2)
            raw[-1] &= mask

        return PackedDNA(packed_bytes=bytes(raw), total_bases=packed.total_bases)

    @staticmethod
    def reverse_complement(packed: PackedDNA) -> PackedDNA:
        """Computes reverse complement of packed sequence."""
        if packed.total_bases == 0:
            return packed
        
        # Decode -> reverse complement -> re-encode for strict bit-accuracy
        s = packed.to_string()
        rev_comp = "".join(COMPLEMENT_MAP[c] for c in reversed(s))
        return AtgcCodec.encode(rev_comp)

    @staticmethod
    def hamming_distance(seq1: PackedDNA, seq2: PackedDNA) -> int:
        """Calculates Hamming distance (mismatches) between two equal-length packed sequences."""
        if seq1.total_bases != seq2.total_bases:
            raise ValueError(f"Sequences must have equal length: {seq1.total_bases} vs {seq2.total_bases}")
        if seq1.total_bases == 0:
            return 0

        dist = 0
        bases_checked = 0
        for b1, b2 in zip(seq1.packed_bytes, seq2.packed_bytes):
            diff = b1 ^ b2
            for shift in (6, 4, 2, 0):
                if bases_checked >= seq1.total_bases:
                    break
                if (diff >> shift) & 0x03 != 0:
                    dist += 1
                bases_checked += 1
        return dist

    @staticmethod
    def extract_kmers(sequence: str, k: int) -> Generator[Tuple[int, int], None, None]:
        """Extracts rolling k-mers (k <= 31) as 64-bit integer hashes with 0-based positions."""
        if k <= 0 or k > 31:
            raise ValueError(f"k-mer size must be in range 1-31, got {k}")
        cleaned = sequence.strip()
        n = len(cleaned)
        if n < k:
            return

        mask = (1 << (2 * k)) - 1
        current_hash = 0

        # Prime the first k-1 bases
        for i in range(k - 1):
            c = cleaned[i]
            if c not in BASE_TO_2BIT:
                raise ValueError(f"Invalid base '{c}' at index {i}")
            current_hash = (current_hash << 2) | BASE_TO_2BIT[c]

        # Slide window
        for i in range(k - 1, n):
            c = cleaned[i]
            if c not in BASE_TO_2BIT:
                raise ValueError(f"Invalid base '{c}' at index {i}")
            current_hash = ((current_hash << 2) | BASE_TO_2BIT[c]) & mask
            pos = i - k + 1
            yield (pos, current_hash)

    @staticmethod
    def find_motif(sequence: str, motif: str) -> List[int]:
        """Bit-parallel motif finder returning 0-based match indices."""
        k = len(motif)
        if k == 0 or len(sequence) < k:
            return []
        
        target_dna = AtgcCodec.encode(motif)
        target_hash = 0
        for c in motif:
            target_hash = (target_hash << 2) | BASE_TO_2BIT[c]

        matches: List[int] = []
        for pos, khash in AtgcCodec.extract_kmers(sequence, k):
            if khash == target_hash:
                matches.append(pos)
        return matches

    @staticmethod
    def compute_gc_content(packed: PackedDNA) -> float:
        """Calculates exact GC percentage from bit-packed representation."""
        if packed.total_bases == 0:
            return 0.0
        gc_count = 0
        bases_read = 0
        for b in packed.packed_bytes:
            for shift in (6, 4, 2, 0):
                if bases_read >= packed.total_bases:
                    break
                val = (b >> shift) & 0x03
                # G=2 (10_2), C=1 (01_2)
                if val == 1 or val == 2:
                    gc_count += 1
                bases_read += 1
        return round((gc_count / packed.total_bases) * 100.0, 2)
