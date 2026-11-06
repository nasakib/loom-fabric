# ClothOS Sovereign Operating System — User & Operations Manual

> **Official User Guide & Operations Manual for ClothOS v1.0.0-PROD**  
> **Repository**: `Documents/loom-fabric`  
> **Release Codename**: *Loom Sovereign Weaver*  
> **Architect**: Najmos Sakib  

---

## 1. Welcome to ClothOS

**ClothOS** is a sovereign, self-healing operating system architected from the silicon up for **Autonomous General Intelligence (AGI)** and **Heterogeneous Distributed Computing**. 

Unlike legacy operating systems (Linux, Windows, macOS) which treat AI accelerators as dumb external peripherals, ClothOS weaves heterogeneous compute (NVIDIA CUDA, AMD OpenCL, Ryzen APU, RISC-V 64-bit cores, and TPU Systolic Arrays) into a **single unified memory space** governed by thermodynamic energy bounds and zero-trust security rings.

---

## 2. Quickstart: Interactive Launchers

ClothOS provides dedicated one-click launchers in the repository root:

| Launcher Script | What It Does |
| :--- | :--- |
| [`Launch-ClothOS-Desktop.bat`](file:///c:/Users/natsa/Documents/loom-fabric/Launch-ClothOS-Desktop.bat) | Starts the local desktop server and opens the **Ubuntu / macOS-styled Web Desktop GUI** at `http://127.0.0.1:8088/` in your browser. |
| [`Run-ClothOS-Release.bat`](file:///c:/Users/natsa/Documents/loom-fabric/Run-ClothOS-Release.bat) | Master 8-option interactive console menu (Desktop, CLI Shell, RISC-V TPU, x86 HAL, Diagnostics Doctor, USB Creator, Release Audit). |
| [`Make-Bootable-USB.bat`](file:///c:/Users/natsa/Documents/loom-fabric/Make-Bootable-USB.bat) | Synthesizes the hybrid UEFI/BIOS bootable flashdrive images (`clothos-live-usb.img` & `clothos-sovereign-live-installer.iso`). |
| [`Start-24-7-Compute.bat`](file:///c:/Users/natsa/Documents/loom-fabric/Start-24-7-Compute.bat) | Launches the autonomous self-evolution daemon that continuously harvests Reddit/GitHub research and improves the kernel. |

---

## 3. The Desktop Experience (Ubuntu / macOS Hybrid)

The graphical desktop combines the fluid, frosted-glass elegance of macOS with the clean, powerful productivity of Ubuntu GNOME:

### A. Top Status Bar
* **ClothOS Menu (🧶)**: Access system settings, about dialog, and power state.
* **Active User Pill**: Displays active user (`clothos` or `root`) and capability ring ($P_0$–$P_4$).
* **⚡ Landauer Joule Meter**: Real-time compute energy dissipation against the thermodynamic ceiling ($E \le 1000\text{ J}$).
* **🧠 Kuramoto Sync ($r$)**: Collective phase coherence across distributed cluster oscillators ($r \ge 0.965$).
* **🌐 2.5GbE Mesh Link**: Real-time socket sync between Worker Node 1 (`192.168.99.1`) and Head Node 2 (`192.168.99.2`).
* **🕒 Live UTC Clock**: Cryptographically synchronized wall clock.

### B. Floating Frosted Dock & Applications
1. 💻 **Unix Terminal (`bash` / POSIX ABI)**:
   - True monospace terminal with Starship powerline prompt: `clothos@sovereign:~$ `
   - Integrated with the live ClothOS microkernel. Run standard Linux utilities (`ls -la`, `top`, `ps`, `free`, `df`, `cat /etc/os-release`, `neofetch`, `tpu-smi`).
2. 📝 **ClothCode Studio**:
   - Integrated development environment for writing and compiling Rust, Python, Java, and C/C++ programs directly in ClothFS (`/home/clothos/Code/`).
3. 🌐 **Sovereign Surf Navigator**:
   - In-desktop web navigator. All outbound requests pass through the local **Torque RehydrationVault**, preventing personal data or private IP from leaking to surveillance tech giants.
4. 🛍️ **Software Center (App Store)**:
   - Graphical package installer for 1-click downloading: Rust Toolchain, OpenJDK 21, Python 3.14 AI, Git, Neofetch, and Productivity Tools.
5. 👤 **User Accounts Manager**:
   - Manage multi-user profiles, change passwords, and inspect security rings ($P_0$ Superuser vs. $P_1$ Admin vs. $P_3$ User).
6. 🧮 **Scientific Calculator**:
   - Precision decimal, hexadecimal, and duodecimal matrix calculator.
7. 📊 **Activity Monitor & Silicon TPU Management**:
   - Real-time graphical load bars for NVIDIA RTX 3060, AMD RX 580, RISC-V 16x16 Systolic MXU (256 PEs), and 103.5 GB Pooled Memory.

---

## 4. UNIX / POSIX Command Reference

ClothOS provides standard UNIX commands through its POSIX compatibility layer:

### System & Hardware Inspection
```bash
uname -a        # Prints ClothOS kernel version and architecture (RV64GCV + x86_64)
neofetch        # Colorized ClothOS ASCII art and full system hardware summary
tpu-smi         # Systolic Matrix Multiply Unit and dual-GPU load manager
diag            # Full-system diagnostic scan and invariant health verification
free            # Displays 103.5 GB distributed memory allocation
df -h           # Displays ClothFS VFS mountpoints and disk capacity
```

### Multi-User & Security Administration
```bash
whoami          # Prints active user (clothos or root)
id              # Displays UID, GID, groups, and capability ring level
sudo <command>  # Elevates command execution to Ring P0 (Full Kernel Access)
useradd <name>  # Creates a new user with dedicated /home/<name>/ directory
su <name>       # Switches active session to specified user
passwd <name>   # Updates salted SHA-256 password hash in /etc/shadow
```

### Package Management (`cloth-apt`)
```bash
cloth-apt update          # Refreshes certified repository package indexes
cloth-apt search <query>  # Searches available development and productivity packages
cloth-apt install <pkg>   # Downloads and installs software into /usr/bin/
cloth-apt list            # Lists all installed and available packages
```

### Development Runtimes
```bash
rustc --version           # Executes Rust compiler (1.84.0-clothos)
cargo build               # Runs Rust build orchestrator
java -version             # OpenJDK 21 LTS 64-Bit Server VM
python3 --version         # Next-gen Python 3.14.4 runtime
git status                # Version control with RehydrationVault commit signing
ping 192.168.99.2         # Tests round-trip latency to remote cluster head node
```

---

## 5. How to Make a Bootable Flashdrive & Boot Physical PC

ClothOS is ready to boot directly on physical x86_64 and RISC-V hardware:

### Step 1: Bake the Live Image
Run [`Make-Bootable-USB.bat`](file:///c:/Users/natsa/Documents/loom-fabric/Make-Bootable-USB.bat). This generates:
* `deliverables/bootable_images/clothos-live-usb.img` (Raw Hybrid Disk Image)
* `deliverables/bootable_images/clothos-sovereign-live-installer.iso` (Bootable ISO Image)

### Step 2: Flash to USB Media
1. Download and open **Rufus** ([rufus.ie](https://rufus.ie)) or **Balena Etcher**.
2. Insert a USB flash drive ($\ge 8\text{ GB}$).
3. In Rufus:
   - **Device**: Select your USB drive.
   - **Boot Selection**: Click `SELECT` and choose `clothos-sovereign-live-installer.iso`.
   - **Partition Scheme**: `GPT` (for UEFI) or `MBR` (for Legacy BIOS).
   - **Target System**: `UEFI (non CSM)`.
4. Click **START** to write the drive.

### Step 3: Boot on Your Physical PC
1. Plug the USB into your target computer.
2. Power on the machine and immediately press the Boot Menu key:
   * **ASUS / ASRock**: `F8` or `F11`
   * **Gigabyte**: `F12`
   * **MSI**: `F11`
   * **Dell**: `F12`
   * **HP**: `F9`
   * **Lenovo**: `F12`
3. Select **UEFI: ClothOS Live Installer** from the list.
4. ClothOS boots into the live environment with default user `clothos` (password: `clothos`) or `root` (password: `sovereign`).

---

## 6. Decentralized Compute Service Network (CSP / CSC)

ClothOS includes native market economics:
* **As a Compute Service Provider (CSP)**: Rent out spare cycles on your NVIDIA RTX 3060, AMD RX 580, or RISC-V TPU during off-peak hours to earn revenue.
* **As a Compute Service Consumer (CSC)**: When training massive models or running saturation mutagenesis, burst your workloads out across the P2P mesh without risking IP leaks (enforced by the Torque RehydrationVault).
