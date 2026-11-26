# Copyright (c) 2026 Najmos Sakib / VectorCore Holdings, LLC.
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Comprehensive Verification Suite for ClothOS Tiered Upgrade (P1-P3, Tiers 1-3).
==============================================================================
Validates:
1. Ring P0 Governance Root of Trust (Najmos Sakib / ClothOS / Vector Core Holdings)
2. Base-12 Duodecimal Codec, Fractions, and Entropy Reduction
3. Base-16 Nibble Codec, Endianness, CRC32, and DMA Packet Framing
4. 2-Bit ATGC Genomic Codec, Exact Tail-Bits, Complement, and Rolling k-mers
5. RISC-V RV64GCVB Execution Engine, Vector Unit (RVV 1.0), and Offload Hooks
6. 2D Heterogeneous Tile Mesh, XY Routing, and Node 2 Purity
7. Seamless Compute Gateway Integration and VFS vs SPA REST Route Isolation
"""

import pytest
from fastapi.testclient import TestClient

from loom.governance.ring_p0 import (
    GovernanceViolation,
    P0AuthorizationToken,
    RingP0GovernanceController,
    OPERATOR_ROOT_IDENTITY,
    PARENT_ENTITY,
    SUBSIDIARY_ENTITY,
)
from loom.base12.codec import (
    Base12Codec,
    DozenalFixedPoint,
    DozenalSymbolSet,
)
from loom.base16.codec import (
    Base16Codec,
    DmaPacketHeader,
    Endianness,
)
from loom.atgc.codec import (
    AtgcCodec,
    PackedDNA,
)
from loom.arch.riscv.types import (
    PmpEntry,
    PrivilegeMode,
    RiscvRegisterFile,
)
from loom.arch.riscv.vector import (
    RiscvVectorUnit,
    VectorLmul,
    VectorSew,
)
from loom.arch.riscv.cpu import RiscvCpu
from loom.fabric.tile_mesh import (
    ComputeTile,
    HeterogeneousTileMesh,
    TileClass,
    TileStatus,
)
from loom.hardware.seamless_gateway import SeamlessComputeGateway
from loom.gateway.app import app


# =============================================================================
# 1. Governance & Root of Trust Tests
# =============================================================================
def test_ring_p0_governance_invariants():
    gov = RingP0GovernanceController.get_instance()
    assert gov.operator == "Najmos Sakib"
    assert gov.parent_entity == "ClothOS"
    assert gov.subsidiary_entity == "Vector Core Holdings, LLC"

    # 1. Authorized mutation with valid P0 token
    token = gov.issue_p0_token("REALLOCATE_HETEROGENEOUS_TILES")
    assert gov.verify_mutation("REALLOCATE_HETEROGENEOUS_TILES", token) is True

    # 2. Unauthorized mutation fails closed
    with pytest.raises(GovernanceViolation):
        gov.verify_mutation("UNAUTHORIZED_CLUSTER_MUTATION", None)


# =============================================================================
# 2. Base-12 (Duodecimal) Codec & Fixed-Point Tests
# =============================================================================
def test_base12_integer_roundtrip():
    b12 = Base12Codec(DozenalSymbolSet.ASCII)
    
    # 0, positives, negatives
    assert b12.encode_int(0) == "0"
    assert b12.decode_int("0") == 0
    assert b12.encode_int(10) == "X"
    assert b12.decode_int("X") == 10
    assert b12.encode_int(11) == "E"
    assert b12.decode_int("E") == 11
    assert b12.encode_int(12) == "10"
    assert b12.decode_int("10") == 12
    assert b12.encode_int(144) == "100"
    assert b12.decode_int("100") == 144
    assert b12.encode_int(-1728) == "-1000"
    assert b12.decode_int("-1000") == -1728


def test_base12_clean_fractions():
    b12 = Base12Codec(DozenalSymbolSet.ASCII)
    
    # Fundamental harmonic fractions terminate cleanly in Base-12
    # 1/2 = 0.6_12
    fp_half = b12.encode_float(0.5)
    assert fp_half.integral_digits == "0"
    assert fp_half.fractional_digits == "6"

    # 1/3 = 0.4_12 (vs 0.3333... recurring in Base-10)
    fp_third = b12.encode_float(1.0 / 3.0)
    assert fp_third.integral_digits == "0"
    assert fp_third.fractional_digits == "4"

    # 1/4 = 0.3_12
    fp_fourth = b12.encode_float(0.25)
    assert fp_fourth.fractional_digits == "3"

    # 1/6 = 0.2_12
    fp_sixth = b12.encode_float(1.0 / 6.0)
    assert fp_sixth.fractional_digits == "2"

    # Semicolon parsing
    parsed = b12.decode_fixed_point("14;4")
    assert parsed.integral_digits == "14"
    assert parsed.fractional_digits == "4"
    assert abs(parsed.to_float() - 16.33333333) < 1e-5


def test_base12_entropy_reduction():
    b12 = Base12Codec()
    metrics = b12.evaluate_entropy_reduction()
    assert metrics["tested_fractions_count"] >= 7
    assert metrics["entropy_reduction_pct"] > 35.0 # Confirmed entropy reduction


# =============================================================================
# 3. Base-16 (Hexadecimal) & DMA Packet Framing Tests
# =============================================================================
def test_base16_nibbles_and_crc():
    b16 = Base16Codec(uppercase=True)
    
    # Nibble extraction
    hi, lo = b16.extract_nibbles(0xA5)
    assert hi == 0x0A
    assert lo == 0x05
    assert b16.pack_nibbles(hi, lo) == 0xA5

    # CRC-32
    data = b"Loom Fabric Modem DMA Payload 2026"
    crc_hex = b16.compute_checksum_hex(data)
    assert crc_hex.startswith("0x")
    assert len(crc_hex) == 10

    # Framing and unframing
    framed = b16.frame_dma_packet(data, sequence_id=42, endianness=Endianness.BIG)
    assert len(framed) == len(data) + 14
    hdr, extracted_payload = b16.unframe_dma_packet(framed, endianness=Endianness.BIG)
    assert hdr.magic == 0xFA81
    assert hdr.sequence_id == 42
    assert hdr.payload_length == len(data)
    assert extracted_payload == data

    # Corrupted payload detection
    corrupted = bytearray(framed)
    corrupted[-1] ^= 0xFF # Flip bit
    with pytest.raises(ValueError, match="CRC32 mismatch"):
        b16.unframe_dma_packet(bytes(corrupted))


# =============================================================================
# 4. 2-Bit ATGC Genomic Codec & Exact Tail-Bit Tracking
# =============================================================================
def test_atgc_exact_length_and_tail_bits():
    # Length 1 (Tail bits = 6)
    dna1 = AtgcCodec.encode("A")
    assert dna1.total_bases == 1
    assert dna1.byte_count == 1
    assert dna1.tail_bits == 6
    assert dna1.to_string() == "A"

    # Length 5 (Byte 0: 4 bases, Byte 1: 1 base, Tail bits = 6)
    # Critical invariant: Trailing 00 bits in byte 1 must NOT be decoded as 'A's!
    dna5 = AtgcCodec.encode("CGTAC")
    assert dna5.total_bases == 5
    assert dna5.byte_count == 2
    assert dna5.tail_bits == 6
    assert dna5.to_string() == "CGTAC"

    # Length 7 (Tail bits = 2)
    dna7 = AtgcCodec.encode("GATTACA")
    assert dna7.total_bases == 7
    assert dna7.tail_bits == 2
    assert dna7.to_string() == "GATTACA"

    # Complement & Reverse Complement
    comp = AtgcCodec.complement(dna7)
    assert comp.to_string() == "CTAATGT" # G->C, A->T, T->A, T->A, A->T, C->G, A->T
    rev_comp = AtgcCodec.reverse_complement(dna7)
    assert rev_comp.to_string() == "TGTAATC"

    # Hamming distance
    d1 = AtgcCodec.encode("ACGTACGT")
    d2 = AtgcCodec.encode("ACGTTCGT") # 1 mismatch at index 4
    assert AtgcCodec.hamming_distance(d1, d2) == 1

    # Motif finding & k-mers
    seq = "ATGCGATCGATCGATCGATCGATC"
    motif_matches = AtgcCodec.find_motif(seq, "GATC")
    assert len(motif_matches) >= 3


# =============================================================================
# 5. RISC-V RV64GCVB Execution Engine & Vector Unit Tests
# =============================================================================
def test_riscv_base_and_m_extensions():
    cpu = RiscvCpu(hart_id=0)
    
    # x0 is hardwired zero
    cpu.regs.write(0, 99999)
    assert cpu.regs.read(0) == 0

    # Registers x1, x2
    cpu.regs.write(1, 100)
    cpu.regs.write(2, 25)

    # Mul
    cpu.exec_mul(3, 1, 2)
    assert cpu.regs.read(3) == 2500

    # Div
    cpu.exec_div(4, 1, 2)
    assert cpu.regs.read(4) == 4

    # Rem
    cpu.exec_rem(5, 1, 2)
    assert cpu.regs.read(5) == 0


def test_riscv_atomic_operations():
    cpu = RiscvCpu()
    addr = cpu.mem_base + 0x100
    cpu.write_mem_bytes(addr, (10).to_bytes(8, "little"))
    cpu.regs.write(1, addr)
    cpu.regs.write(2, 5)

    # AMOADD.D
    cpu.exec_amoadd_d(3, 1, 2)
    assert cpu.regs.read(3) == 10 # Returns old value
    new_mem = int.from_bytes(cpu.read_mem_bytes(addr, 8), "little")
    assert new_mem == 15 # Memory updated atomically


def test_riscv_vector_extension_rvv():
    vunit = RiscvVectorUnit(vlen_bits=128)
    vl = vunit.vsetvli(avl=4, vsew=VectorSew.SEW_32, vlmul=VectorLmul.LMUL_1)
    assert vl == 4

    vunit.write_elements(1, [10, 20, 30, 40])
    vunit.write_elements(2, [1, 2, 3, 4])
    vunit.execute_vadd(vd=3, vs1=1, vs2=2)
    res = vunit.read_elements(3)
    assert res == [11, 22, 33, 44]

    dot = vunit.execute_vdot(vs1=1, vs2=2)
    # (10*1) + (20*2) + (30*3) + (40*4) = 10 + 40 + 90 + 160 = 300
    assert dot == 300


def test_riscv_custom_offload_hooks():
    cpu = RiscvCpu()
    
    # 1. Base-12 offload
    r_b12 = cpu.execute_custom_offload("X_BASE12_CONVERT", 0.5)
    assert r_b12["status"] == "HW_ACCELERATED"
    assert "0;6" in r_b12["result"]

    # 2. Base-16 CRC32 offload
    r_b16 = cpu.execute_custom_offload("X_BASE16_CRC32", b"LoomMesh")
    assert r_b16["status"] == "HW_ACCELERATED"
    assert r_b16["result"].startswith("0x")

    # 3. 2-Bit ATGC offload
    r_atgc = cpu.execute_custom_offload("X_ATGC_ENCODE", "ACGTACGT")
    assert r_atgc["status"] == "HW_ACCELERATED"
    assert r_atgc["total_bases"] == 8
    assert r_atgc["packed_bytes"] == 2


# =============================================================================
# 6. Heterogeneous 2D Tile Mesh & Node 2 Purity Tests
# =============================================================================
def test_tile_mesh_and_node2_purity():
    mesh = HeterogeneousTileMesh(width=4, height=4)
    
    # Verify tile classes
    dpu = mesh.get_tile(0, 0)
    assert dpu.tile_class == TileClass.DPU_SMARTNIC
    
    gpu_node1 = mesh.get_tile(0, 1)
    assert gpu_node1.node_id == "skyTech-Worker"
    assert gpu_node1.backend_driver == "CUDA"
    assert gpu_node1.is_pure_amd is False

    gpu_node2 = mesh.get_tile(2, 2)
    assert gpu_node2.node_id == "Ryzen7-Head"
    assert gpu_node2.is_pure_amd is True # Node 2 Purity flag set

    # Node 2 Purity: Workload requiring NVIDIA CUDA must be rejected on Node 2 and diverted to Node 1
    selected, lat, route = mesh.dispatch_workload(
        tile_class_preference=TileClass.GPU_SIMT,
        requires_nvidia=True,
        target_node="Ryzen7-Head",
    )
    assert selected.node_id == "skyTech-Worker" # Diverted to Node 1
    assert selected.is_pure_amd is False


# =============================================================================
# 7. Seamless Compute Gateway Integration & Route Isolation Tests
# =============================================================================
def test_seamless_gateway_specialized_dispatch():
    gw = SeamlessComputeGateway.get_instance()
    
    # Base-12 dispatch
    res_b12 = gw.dispatch("0.3333333333333333", workload_type="base12_convert")
    assert res_b12.status == "SUCCESS"
    assert "0;4" in res_b12.result_text

    # Base-16 framing dispatch
    res_b16 = gw.dispatch("ActivationMatrixBuffer_L12", workload_type="base16_frame")
    assert res_b16.status == "SUCCESS"
    assert "Framed" in res_b16.result_text

    # ATGC analysis dispatch
    res_atgc = gw.dispatch("ATGCGATCGATC", workload_type="atgc_analysis")
    assert res_atgc.status == "SUCCESS"
    assert res_atgc.payload_metadata["total_bases"] == 12


def test_vfs_vs_spa_route_isolation():
    client = TestClient(app)

    # 1. API request (Accept: application/json) -> returns JSON telemetry
    r_json = client.get("/v1/fabric/modem/status", headers={"Accept": "application/json"})
    assert r_json.status_code == 200
    assert r_json.headers["content-type"].startswith("application/json")
    assert "state" in r_json.json()

    # 2. Browser request (Accept: text/html) -> returns isolated HTML status card
    r_html = client.get("/v1/fabric/modem/status", headers={"Accept": "text/html"})
    assert r_html.status_code == 200
    assert "text/html" in r_html.headers["content-type"]
    assert "FABRIC COMPUTE MESH" in r_html.text

    # 3. Governance report endpoint
    r_gov = client.get("/v1/fabric/modem/governance")
    assert r_gov.status_code == 200
    assert r_gov.json()["root_operator"] == "Najmos Sakib"
