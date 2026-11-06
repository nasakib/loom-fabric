# ClothOS Developer & AGI Modular Architecture Constitution

> **Proprietary & Sovereign Operating System Specification**  
> **Repository**: `Documents/loom-fabric`  
> **Target Audience**: Human Systems Engineers & Autonomous AI/AGI Development Agents  
> **Status**: Certified v1.0.0-PROD Architectural Specification  

---

## 1. Architectural Mandate: Modular Decoupling

ClothOS is architected as an **autopoietic, self-healing, modular operating system**. To ensure that both human engineers and autonomous AGI agents can safely extend, refactor, and maintain the codebase without regressions, the system enforces **strict layer isolation**.

### The 7-Layer Modular Topology

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ LAYER 6: PRESENTATION & INTERACTION (Desktop GUI, Web Shell, Dock, Windowing)│
├─────────────────────────────────────────────────────────────────────────────┤
│ LAYER 5: DEVELOPER EXTENSIBILITY & APPS (SDK, cloth-apt, Skills, Toolchains)│
├─────────────────────────────────────────────────────────────────────────────┤
│ LAYER 4: COGNITIVE NERVOUS SYSTEM (7 Lobes, Kuramoto Consensus, Memory)     │
├─────────────────────────────────────────────────────────────────────────────┤
│ LAYER 3: DISTRIBUTED FABRIC & MESH (ZeroMQ Bus, Ray Cluster, CSP Arbitrage) │
├─────────────────────────────────────────────────────────────────────────────┤
│ LAYER 2: SOVEREIGN SECURITY & VAULT (Torque Scrubber, Rehydration, PMP)     │
├─────────────────────────────────────────────────────────────────────────────┤
│ LAYER 1: MICROKERNEL & POSIX ABI (Syscalls, Processes, VFS ClothFS, Rings)  │
├─────────────────────────────────────────────────────────────────────────────┤
│ LAYER 0: SILICON SUBSTRATE & HAL (NVIDIA CUDA, AMD OpenCL, RISC-V TPU, APIC)│
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Layer Import & Dependency Invariants
1. **Unidirectional Dependency Flow**: A higher layer may import from lower layers; **a lower layer must NEVER import from a higher layer**.
   * Example: Layer 1 (`loom/clothos/posix_compat.py`) may call Layer 0 (`hal.py` or `riscv_tpu_emulator.py`), but Layer 0 must never import Layer 1.
2. **Explicit Interfaces**: All inter-layer calls must pass typed arguments through explicit dataclasses or Pydantic models. Never pass raw untyped dictionaries across layer boundaries.
3. **No Circular Imports**: Subsystems must be independently importable and testable in isolated sandboxes.

---

## 2. Core Architectural Laws

Every module written for ClothOS—by human or agent—must strictly adhere to the **Four Constitutional Invariants**:

### Law I: The Fiduciary Capability Rings ($P_0$–$P_5$)
Every function, driver, and service must declare its capability ring via the `@ring` decorator:

| Ring | Identifier | Purpose & Access Boundary | Maximum Latency |
| :--- | :--- | :--- | :--- |
| **$P_0$** | `P0_SANCTITY` | Hard real-time safety, physical motor veto, memory vault root. | $< 100\ \mu\text{s}$ |
| **$P_1$** | `P1_PLANETARY` | Hardware device drivers, GPU/TPU context switching, HAL. | $< 1\text{ ms}$ |
| **$P_2$** | `P2_CIVIC` | System daemons, IPC routing, file system journals, security auditing. | $< 5\text{ ms}$ |
| **$P_3$** | `P3_BIO_AFFECTIVE`| Distributed neural sharding, cognitive lobes, multi-agent mesh. | $< 50\text{ ms}$ |
| **$P_4$** | `P4_EPISTEMIC` | Research harvesting, hypothesis generation, background optimization. | Asynchronous |
| **$P_5$** | `P5_MAINTENANCE`| Garbage collection, telemetry logging, disk defragmentation. | Idle |

```python
from loom.clothos.sdk import ring, P0, P1, P3

@ring(P0)
def critical_hardware_lock():
    # Only executable by UID 0 (root) with verified supervisor capabilities
    ...
```

### Law II: The Landauer Thermodynamic Energy Ceiling
ClothOS treats thermal dissipation and computational energy as a hard physics boundary.
* Standard tasks are bounded by **$\le 1000\text{ Joules}$** per execution cycle ($E = P \cdot t \le 1000\text{ J}$).
* Systolic array operations run at $\sim 1.2\text{ pJ}$ per MAC operation.
* Every module must execute within an energy budget:

```python
from loom.clothos.sdk import energy_budget

with energy_budget(joules=15.0):
    # If compute exceeds 15.0 Joules, the scheduler pauses or cools the hart
    result = execute_tensor_wavefront()
```

### Law III: Torque Zero-Trust RehydrationVault
Personal identifying information (PII), private cryptographic keys, and proprietary neural weights **must never exit the node in plain text**.
* When exporting data to external networks or Tier 3 cloud services, all private tokens must be scrubbed into cryptographic handles (`__VAULT_TOKEN_...__`).
* Responses are rehydrated in-flight inside local physical registers.

### Law IV: Verified Dual-Track Silicon Portability
ClothOS supports both current x86 systems and future sovereign RISC-V AGI appliances:
1. **Target Silicon (`platforms/clothos-riscv/`)**:
   - RISC-V 64-bit (`RV64GCV`) with custom **RoCC TPU opcodes** (`TPU_LOAD_WEIGHTS`, `TPU_MATMUL_ACC`, `TPU_LANDAUER_COOL`).
   - Hardware PMP (Physical Memory Protection) 4 MiB NAPOT enclaves.
2. **Host Crucible (`platforms/clothos-x86/`)**:
   - x86_64 Multiboot 1.0 specification compliant (`0x1BADB002`).
   - 4-level paging (`CR3` $\to$ `PML4` $\to$ `PDPT` $\to$ `PD` $\to$ `PT`) with Supervisor-only vault pages.
   - Local APIC interrupt routing and PCIe VirtIO bus drivers.

---

## 3. Developer Scaffolding CLI: Generating New Modules

To accelerate development for humans and AGI subagents, ClothOS provides the automated module scaffolder:

### A. Scaffolding a Device Driver
```bash
python -m loom.clothos.module_scaffolder driver sensor_accel --ring P1
```
* Generates: `loom/clothos/drivers/sensor_accel_driver.py`
* Generates: `tests/test_sensor_accel_driver.py`

### B. Scaffolding a Microkernel Service Daemon
```bash
python -m loom.clothos.module_scaffolder service telemetry_sync --ring P2
```
* Generates: `loom/clothos/services/telemetry_sync_service.py`
* Generates: `tests/test_telemetry_sync_service.py`

### C. Scaffolding an AGI Agent Skill
```bash
python -m loom.clothos.module_scaffolder skill distributed-inference --desc "Orchestrates sharded inference across Node 1 and Node 2"
```
* Generates: `.agents/skills/distributed-inference/SKILL.md`

---

## 4. Testing & Verification Protocol

Before submitting or ratcheting any code into ClothOS:
1. **Unit & Integration Suite**:
   ```powershell
   pytest tests/test_clothos_dual_track_boot.py tests/test_clothos_posix_and_diagnostics.py tests/test_clothos_full_fledged_os.py -v
   ```
2. **Full System Diagnostics & Auto-Repair**:
   ```powershell
   python -m loom.clothos.diagnostics_and_ops --repair
   ```
3. **Hardware Emulation Verification**:
   - RISC-V TPU: `python -m loom.clothos.riscv_tpu_emulator`
   - x86 HAL: `python -m loom.clothos.x86_hal_emulator`

---

## 5. Directory Map

| Path | Purpose |
| :--- | :--- |
| [`platforms/clothos-riscv/`](file:///c:/Users/natsa/Documents/loom-fabric/platforms/clothos-riscv/) | RISC-V 64-bit bare-metal microkernel source, Cargo.toml, and PMP enclaves |
| [`platforms/clothos-x86/`](file:///c:/Users/natsa/Documents/loom-fabric/platforms/clothos-x86/) | x86_64 Multiboot 1.0 kernel source, GDT/IDT, and 4-level paging |
| [`loom/clothos/`](file:///c:/Users/natsa/Documents/loom-fabric/loom/clothos/) | Core microkernel logic, POSIX ABI, user manager, and package manager |
| [`loom/clothos/drivers/`](file:///c:/Users/natsa/Documents/loom-fabric/loom/clothos/drivers/) | Hardware drivers for GPUs, APU, TPU, and serial consoles |
| [`deliverables/bootable_images/`](file:///c:/Users/natsa/Documents/loom-fabric/deliverables/bootable_images/) | Compiled `.img` and `.iso` bootable images for USB and QEMU |
| [`deliverables/desktop/`](file:///c:/Users/natsa/Documents/loom-fabric/deliverables/desktop/) | Ubuntu/macOS-styled Desktop GUI frontend and application windows |
| [`deliverables/research_library/`](file:///c:/Users/natsa/Documents/loom-fabric/deliverables/research_library/) | Continuous research library harvested from Reddit, GitHub, and arXiv |
| [`deliverables/releases/`](file:///c:/Users/natsa/Documents/loom-fabric/deliverables/releases/) | Official commercial distributions and release manifests |
