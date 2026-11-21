# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
Comprehensive Test Suite for ClothOS Dual-Track Boot Architecture (`tests/test_clothos_dual_track_boot.py`).

Verifies:
1. Platforms Directory Integrity: RISC-V and x86 platform configurations.
2. x86 HAL Emulation: Real -> Protected -> Long mode staging, Multiboot 1.0 headers, 4-level paging, and APIC.
3. RISC-V TPU Emulation: Systolic array PE matrix multiplication and Landauer thermodynamic bounds.
4. Dual-Track Boot Image Builder: Baking of 'clothos-rv64-tpu.img' and 'clothos-x86_64.iso' with SHA256 verification.
5. Epistemic Harvester Dual-Track Classification: Topic classification for both RISC-V and x86 architectural signals.
"""

from pathlib import Path
import json
import pytest

from loom.clothos.x86_hal_emulator import X86HalEmulator, X86CpuMode, X86Ring
from loom.clothos.riscv_tpu_emulator import RiscvTpuEmulator, TpuOpcode
from loom.clothos.dual_track_boot_builder import DualTrackBootBuilder
from loom.clothos.research_harvester import OSResearchHarvester


def test_platforms_directory_integrity():
    workspace = Path(__file__).resolve().parent.parent
    riscv_dir = workspace / "platforms" / "clothos-riscv"
    x86_dir = workspace / "platforms" / "clothos-x86"

    assert riscv_dir.exists(), "RISC-V platform directory missing"
    assert (riscv_dir / "Cargo.toml").exists(), "RISC-V Cargo.toml missing"
    assert (riscv_dir / "src" / "main.rs").exists(), "RISC-V main.rs missing"

    assert x86_dir.exists(), "x86 platform directory missing"
    assert (x86_dir / "Cargo.toml").exists(), "x86 Cargo.toml missing"
    assert (x86_dir / "src" / "main.rs").exists(), "x86 main.rs missing"
    assert (x86_dir / "src" / "multiboot.rs").exists(), "x86 multiboot.rs missing"
    assert (x86_dir / "src" / "paging.rs").exists(), "x86 paging.rs missing"


def test_x86_hal_emulator_pipeline():
    emu = X86HalEmulator()
    assert emu.cpu_mode == X86CpuMode.REAL_16

    # Test transitions
    m1, _ = emu.step_boot_mode_transition()
    assert m1 == X86CpuMode.PROTECTED_32

    m2, _ = emu.step_boot_mode_transition()
    assert m2 == X86CpuMode.LONG_64

    # Multiboot validation
    magic = 0x1BADB002
    flags = 0x00000003
    checksum = (-(magic + flags)) & 0xFFFFFFFF
    assert emu.validate_multiboot_header(magic, flags, checksum) is True
    assert emu.validate_multiboot_header(0x12345678, 0, 0) is False

    # Paging MMU and Ring 3 RehydrationVault isolation
    kernel_trans = emu.mmu_translate_address(0x00500000, X86Ring.RING_0_KERNEL)
    assert kernel_trans["page_fault"] is False

    user_trans = emu.mmu_translate_address(0x00500000, X86Ring.RING_3_USER)
    assert user_trans["page_fault"] is True
    assert "Page-Fault" in user_trans["fault_reason"]

    # APIC & PCIe
    assert emu.tick_apic_timer(150000) is True
    pci_devs = emu.scan_pci_bus()
    assert len(pci_devs) >= 4

    # Full pipeline test
    pipeline_res = emu.verify_x86_hal_pipeline()
    assert pipeline_res["passed"] is True
    assert pipeline_res["multiboot_valid"] is True


def test_riscv_tpu_emulator_systolic_wavefront():
    emu = RiscvTpuEmulator()
    benchmark = emu.run_full_system_benchmark(timesteps=3)
    assert benchmark["systolic_pipeline"]["active_pes"] > 0
    assert benchmark["systolic_pipeline"]["array_dimensions"] == "16x16"
    assert benchmark["joules_per_second"] > 0.0
    assert benchmark["landauer_efficiency_rating"] == "OPTIMAL"


def test_dual_track_boot_builder():
    builder = DualTrackBootBuilder.get_instance()
    manifest = builder.build_both_images()

    assert manifest["total_images"] == 2
    assert manifest["verification_status"]["both_passed"] is True

    images = manifest["images"]
    arch_set = {img["architecture"] for img in images}
    assert "riscv64gc+rvv+rocc_tpu" in arch_set
    assert "x86_64+x86_32_multiboot" in arch_set

    for img in images:
        path = Path(img["image_path"])
        assert path.exists()
        assert path.stat().st_size >= 4 * 1024 * 1024
        assert len(img["sha256_checksum"]) == 64


def test_research_harvester_dual_track_classification():
    harvester = OSResearchHarvester.get_instance()

    riscv_topic = harvester._classify_topic("Writing an OpenSBI payload with RoCC TPU coprocessor on RV64GC")
    assert riscv_topic == "ARCH_RISCV_TPU"

    x86_topic = harvester._classify_topic("Implementing Multiboot 1.0 with 4-level PML4 paging and Local APIC")
    assert x86_topic == "ARCH_X86_HAL"
