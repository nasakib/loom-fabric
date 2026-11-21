# Copyright (c) 2026 Najmos Sakib / VectorCore Holdings, LLC.
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Canonical Base-16 (Hexadecimal / Nibble-Aligned) Codec & Framing.
================================================================
Provides constant-time, nibble-aligned Base-16 encoding, decoding,
DMA descriptor framing, capability beacon serialization, and packet CRC helpers.
"""

from __future__ import annotations

import binascii
import struct
import zlib
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

HEX_LOWER = "0123456789abcdef"
HEX_UPPER = "0123456789ABCDEF"


class Endianness(str, Enum):
    BIG = "big"
    LITTLE = "little"


@dataclass(frozen=True)
class DmaPacketHeader:
    magic: int              # 0xFA81 (Fabric Modem Header)
    sequence_id: int        # 32-bit monotonic sequence
    payload_length: int     # 32-bit payload byte count
    crc32_checksum: int     # 32-bit CRC checksum
    endianness: Endianness = Endianness.BIG

    def pack_bytes(self) -> bytes:
        fmt = ">HII I" if self.endianness == Endianness.BIG else "<HII I"
        return struct.pack(fmt, self.magic, self.sequence_id, self.payload_length, self.crc32_checksum)

    @classmethod
    def unpack_bytes(cls, raw: bytes, endianness: Endianness = Endianness.BIG) -> DmaPacketHeader:
        if len(raw) < 14:
            raise ValueError(f"Packet header too short: {len(raw)} bytes, expected 14 bytes")
        fmt = ">HII I" if endianness == Endianness.BIG else "<HII I"
        magic, seq, length, crc = struct.unpack(fmt, raw[:14])
        return cls(magic=magic, sequence_id=seq, payload_length=length, crc32_checksum=crc, endianness=endianness)


class Base16Codec:
    """High-performance, nibble-aligned Base-16 codec with integrity verification."""

    def __init__(self, uppercase: bool = True):
        self.uppercase = uppercase
        self.table = HEX_UPPER if uppercase else HEX_LOWER

    def encode(self, data: Union[bytes, bytearray, memoryview]) -> str:
        """Encodes raw bytes to canonical Base-16 string."""
        raw = binascii.hexlify(data).decode("ascii")
        return raw.upper() if self.uppercase else raw.lower()

    def decode(self, hex_str: str) -> bytes:
        """Decodes a Base-16 string into bytes with bounds and character checks."""
        cleaned = hex_str.strip().replace(" ", "").replace(":", "").replace("-", "")
        if len(cleaned) % 2 != 0:
            raise ValueError(f"Base-16 string must have an even length, got {len(cleaned)}")
        try:
            return binascii.unhexlify(cleaned)
        except binascii.Error as e:
            raise ValueError(f"Malformed Base-16 characters in string: {e}")

    def extract_nibbles(self, byte_val: int) -> Tuple[int, int]:
        """Extracts high nibble (bits 7-4) and low nibble (bits 3-0)."""
        if not (0 <= byte_val <= 255):
            raise ValueError(f"Byte value must be 0-255, got {byte_val}")
        return ((byte_val >> 4) & 0x0F, byte_val & 0x0F)

    def pack_nibbles(self, high: int, low: int) -> int:
        """Combines two 4-bit nibbles into an 8-bit byte."""
        if not (0 <= high <= 15) or not (0 <= low <= 15):
            raise ValueError(f"Nibbles must be in range 0-15, got high={high}, low={low}")
        return ((high & 0x0F) << 4) | (low & 0x0F)

    def compute_crc32(self, data: bytes) -> int:
        """Computes standardized IEEE 802.3 CRC-32 checksum."""
        return zlib.crc32(data) & 0xFFFFFFFF

    def compute_checksum_hex(self, data: bytes) -> str:
        """Returns the 32-bit CRC in canonical hex notation (e.g. 0x9A4F81C2)."""
        crc = self.compute_crc32(data)
        return f"0x{crc:08X}" if self.uppercase else f"0x{crc:08x}"

    def frame_dma_packet(
        self,
        payload: bytes,
        sequence_id: int,
        endianness: Endianness = Endianness.BIG,
    ) -> bytes:
        """Frames a raw tensor or message payload with a validated Base-16 header."""
        crc = self.compute_crc32(payload)
        hdr = DmaPacketHeader(
            magic=0xFA81,
            sequence_id=sequence_id,
            payload_length=len(payload),
            crc32_checksum=crc,
            endianness=endianness,
        )
        return hdr.pack_bytes() + payload

    def unframe_dma_packet(
        self,
        packet_bytes: bytes,
        endianness: Endianness = Endianness.BIG,
    ) -> Tuple[DmaPacketHeader, bytes]:
        """Validates header, extracts payload, and checks CRC-32 integrity."""
        if len(packet_bytes) < 14:
            raise ValueError(f"Packet too short to contain header ({len(packet_bytes)} bytes)")
        hdr = DmaPacketHeader.unpack_bytes(packet_bytes[:14], endianness=endianness)
        if hdr.magic != 0xFA81:
            raise ValueError(f"Invalid packet magic 0x{hdr.magic:04X}, expected 0xFA81")
        
        payload = packet_bytes[14 : 14 + hdr.payload_length]
        if len(payload) != hdr.payload_length:
            raise ValueError(f"Payload truncated: expected {hdr.payload_length} bytes, got {len(payload)}")
        
        actual_crc = self.compute_crc32(payload)
        if actual_crc != hdr.crc32_checksum:
            raise ValueError(
                f"CRC32 mismatch: expected 0x{hdr.crc32_checksum:08X}, computed 0x{actual_crc:08X}"
            )
        return hdr, payload
