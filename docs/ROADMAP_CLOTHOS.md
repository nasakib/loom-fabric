# ClothOS Roadmap: Evolution from Loom Fabric to RISC-V Unikernel

> **Target Platform**: Bare-Metal RISC-V RV64GCV Silicon  
> **Kernel Architecture**: Capability-Based `no_std` Microkernel / Unikernel in Rust  
> **Acceleration Target**: Custom Systolic Array TPU Coprocessors + Vector Extensions (RVV 1.0)

---

## 1. Architectural Motivation

Modern AI operating systems suffer from severe layers of legacy abstraction:
- Linux/Windows virtual memory paging (`mmap`) introduces TLB shootdowns and non-deterministic latency.
- PCI Express driver communication requires multiple user-to-kernel memory copies.
- Operating system schedulers treat matrix multipliers as opaque peripheral accelerators rather than first-class compute pipelines.

**ClothOS** eliminates the OS tax entirely by making **Tensor Memory (`tmap`)** and **Systolic Matrix Multiplies** the native primitives of the kernel itself.

---

## 2. Phase-by-Phase Evolution

```mermaid
flowchart LR
    Phase1["Phase 1: Loom Fabric (Python/Ray/Win32)"] --> Phase2["Phase 2: loom-core Native Rust Crate"]
    Phase2 --> Phase3["Phase 3: Hybrid Linux/KVM Microkernel"]
    Phase3 --> Phase4["Phase 4: ClothOS Bare-Metal RV64GCV"]
```

### Phase 1: Loom Fabric (Current Baseline)
- Multi-node heterogeneous orchestration across Windows 11 (CUDA/Vulkan) and Head Node (Ryzen 7).
- Mathematical layer allocation, zero-trust Torque enclaves, Win32 Job Object lifecycle guards, and Ray mesh communication.
- Strict functional contracts in Python mimicking Rust traits (`typing.Protocol`) and frozen Pydantic DTOs.

### Phase 2: `loom-core` (Native Rust Crate)
- Port pure computational subsystems into a unified `no_std`-compatible Rust library:
  - `loom-types`: Core immutable DTOs and result wrappers.
  - `loom-torque`: Zero-trust regex/Aho-Corasick enclave scrubber and `RehydrationVault`.
  - `loom-stitch`: Zero-OOM mathematical allocator calculating layer splits and KV-cache footprints.
- Replace HTTP loopback overhead with lock-free shared memory ring buffers (`shm_open`).

### Phase 3: Hybrid Microkernel Emulation
- Deploy `loom-core` within a minimal hypervisor environment (KVM / Cloud-Hypervisor).
- Implement `tmap`: Hardware-assisted PagedAttention integrated directly into virtual address space translation.
- Replace process boundaries with capability tokens (seL4-style capability architecture).

### Phase 4: ClothOS Bare-Metal on RISC-V
- Target hardware: **RISC-V RV64GCV** (RV64I + M + A + F + D + C + Vector 1.0 with $VLEN=512$).
- Pure `no_std` unikernel bootloader initialized via OpenSBI (Supervisor Binary Interface).
- Systolic TPU instructions mapped to custom RISC-V opcode extensions (e.g., `tpu.matmul.f16`).
- Physical memory partitioned directly into:
  1. Kernel text & capability tables ($\le 16\text{ MB}$).
  2. Weight matrices (continuous physically contiguous pages).
  3. Dynamic KV-cache ring buffers.

---

## 3. RISC-V RVV & Systolic Hardware Co-Design

| Feature | Standard OS + Driver | ClothOS Native Microkernel |
| :--- | :--- | :--- |
| **Memory Architecture** | 4KB / 2MB POSIX Virtual Pages | 64MB Contiguous Tensor Tiles (`tmap`) |
| **Driver Boundary** | User Space $\to$ Kernel $\to$ Hardware | Zero-Copy Capability Ring Buffer |
| **Security Enclave** | Userspace Regex Scrubber | Hardware Page-Permission Cryptographic Enclave |
---

## 4. Vision: Dual-Subsystem Hardware Evolution & Bare-Metal Transition

ClothOS defines a staged dual-personality roadmap bridging present standard workstation silicon to future sovereign bare-metal hardware:

```mermaid
graph TD
    subgraph STAGE_NOW ["Stage 1 (Current): Host Subsystem (WCOS / LCOS)"]
        HOST_OS["Host Workstation (Windows 11 x86_64 / Linux)"]
        WCOS_LAYER["ClothOS POSIX & Virtual Subsystem (`loom/clothos/posix_compat.py`)"]
        EMU_TPU["Systolic Array Emulation (`loom/clothos/riscv_tpu_emulator.py`)"]
        HOST_DEVICES["Accelerators (RTX 3060 CUDA, RX 580 OpenCL, 2.5GbE Mesh)"]
        
        HOST_OS --> WCOS_LAYER
        WCOS_LAYER --> EMU_TPU
        WCOS_LAYER --> HOST_DEVICES
    end

    subgraph STAGE_FUTURE ["Stage 2 (Vision Roadmap): Sovereign Bare-Metal OS"]
        FIRMWARE["OpenSBI / U-Boot Firmware (`uEnv.txt`)"]
        RV_KERNEL["ClothOS Sovereign RV64GCV Rust Unikernel (`clothos_rv64.ld`)"]
        PMP["Hardware Physical Memory Protection (`pmpcfg0` CSR 0x3A0 / 0x9D NAPOT)"]
        RVV["RISC-V Vector 1.0 (RVV) VLEN=512"]
        HW_TPU["Physical Systolic Array Matrix Processing Units (TPU MXUs MMIO)"]
        
        FIRMWARE --> RV_KERNEL
        RV_KERNEL --> PMP
        RV_KERNEL --> RVV
        RV_KERNEL --> HW_TPU
    end
```

### Staged Silicon Architecture Matrix

| Architectural Subsystem | Present Implementation (Stage 1: Host Workstation) [Status: Implemented] | Future Hardware Target (Stage 2: Bare-Metal Unikernel) [Status: Planned] |
| :--- | :--- | :--- |
| **Execution Mode** | WCOS/POSIX guest layer running under Windows 11 / Linux with `/proc`, `/dev`, and virtual VFS. | Primary bootable operating system with direct bare-metal hardware ownership (no host OS or hypervisor). |
| **Silicon Platform** | Heterogeneous x86_64 dual-node cluster (skyTech RTX 3060 + AMD RX 580 + Node 2 AMD Ryzen 7). | Custom RV64GCV RISC-V SoC with integrated 2D systolic array TPU coprocessor. |
| **Memory Isolation** | Sandboxed virtualization with Ring P0–P5 hierarchical capabilities in Python/C++. | Hardware-enforced RISC-V Physical Memory Protection (`pmpcfg0` CSR 0x3A0, byte `0x9D` locked NAPOT). |
| **Matrix Processing** | Cycle-accurate 2D systolic array emulation (`riscv_tpu_emulator.py`) + CUDA/OpenCL dispatch. | Direct MMIO and memory-mapped PCIe streaming into physical 2D systolic TPU Matrix Units (MXUs). |
| **Kernel Entry** | CLI entry points (`wcos`, `wcoss`, `clothsh`, or `python -m loom.cli.main`). | Hardware reset vector initialized via OpenSBI Supervisor Binary Interface into `clothos_rv64.ld`. |
| **Memory Architecture** | Dynamic host RAM metrology (psutil) + Tailscale/2.5GbE distributed mesh pooling. | Contiguous 64MB tensor tiles (`tmap`) with zero-copy capability ring buffers. |
