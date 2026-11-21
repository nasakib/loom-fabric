# ClothOS Fabric Modem & Fiber Optics Networking Architecture

**System:** ClothOS / Loom Fabric Cyber-Physical Operating System  
**Entity:** Vector Core Holdings, LLC / Apostrophie  
**Root of Trust (Ring P0):** Najmos Sakib (`p0_operator_wallet`)  
**Document Classification:** Engineering Architecture & Hardware Specification  
**Status:** Approved for Hardware Prototype & Fiber Deployment  
**Date:** November 2026  

---

## 1. Executive Summary & Design Philosophy

The vision of **ClothOS** is simple yet radical: **using distributed compute should feel exactly like using the internet.** A user should be able to submit an artificial intelligence workload, stream an interactive 120 FPS 4K game, or shard a 70B parameter model across proximate nodes without configuring IP addresses, provisioning cloud instances, or suffering centralized platform taxes.

To realize this vision in physical silicon and glass, this document specifies:
1. **The ClothOS Fabric Modem (Hardware & Silicon Architecture):** A dedicated PCIe/CXL add-in card and external USB4/Thunderbolt device featuring a custom FPGA/ASIC, Base-16 DMA acceleration, hardware Gas Metering (GMU), line-rate Proof of Verifiable Computation (PoVC) cryptographic engines, and a physical Air-Gap isolation switch.
2. **The Dual-PHY Front-End:** Seamlessly bridging single-mode optical fiber (100G/25G BiDi) with line-of-sight 60GHz millimeter-wave wireless (IEEE 802.11ay) and Wi-Fi 7 (IEEE 802.11be MLO).
3. **The Fiber Optics Networking Architecture:** An engineering analysis of **when fiber optics IS required** (sub-millisecond cloud gaming, all-reduce tensor sharding, dedicated dark-fiber lambda meshes) versus **when fiber is NOT required** (60GHz mmWave rooftop links, CXL copper intra-chassis, and WireGuard overlays over consumer broadband).

---

## 2. When Fiber Optics IS vs. When It Is NOT Required

A fundamental engineering question in building a decentralized compute fabric is whether physical fiber trenching is strictly mandatory. The answer is **hierarchical and workload-dependent**:

```
                               ┌───────────────────────────────────────────────┐
                               │           Target Compute Workload             │
                               └───────────────────────┬───────────────────────┘
                                                       │
         ┌─────────────────────────────────────────────┼─────────────────────────────────────────────┐
         ▼                                             ▼                                             ▼
┌───────────────────────────────┐       ┌───────────────────────────────┐       ┌───────────────────────────────┐
│     TIER 1: OPTICAL FIBER     │       │     TIER 2: 60GHz mmWAVE      │       │     TIER 3: Wi-Fi 7 / CXL     │
│       (Fiber IS Required)     │       │   (Fiber is NOT Required)     │       │   (Fiber is NOT Required)     │
├───────────────────────────────┤       ├───────────────────────────────┤       ├───────────────────────────────┤
│ • Sub-16ms 4K/120 FPS Gaming  │       │ • Neighborhood Rooftop Mesh   │       │ • Intra-chassis / Intra-room  │
│ • Distributed Model Training  │       │ • Inter-building (50–500m)    │       │ • Zero-trenching residential  │
│ • Ring-Attention & Tensor All-│       │ • 20–40 Gbps Line-of-Sight    │       │ • 5–15 Gbps multi-band MLO    │
│   Reduce (100 Gbps, <100ns)   │       │ • 1.0–2.0 ms latency budget   │       │ • CXL 3.0 copper (<50ns bus)  │
│ • Zero-jitter memory pooling  │       │ • Rapid deployment ($0 trench)│       │ • WireGuard P2P ISP fallback  │
└───────────────────────────────┘       └───────────────────────────────┘       └───────────────────────────────┘
```

### Comprehensive Technical & Economic Comparison

| Dimension | Dedicated Optical Fiber (BiDi SMF) | 60GHz mmWave (IEEE 802.11ay) | Wi-Fi 7 (IEEE 802.11be MLO) | CXL / PCIe Direct Copper |
|---|---|---|---|---|
| **Fiber Required?** | **YES** (OS2 Single-Mode Glass) | **NO** (Over-the-Air RF) | **NO** (Over-the-Air RF) | **NO** (Twinax Copper) |
| **Max Range** | 0.5 km – 20.0 km | 10 m – 500 m (Line-of-Sight) | 1 m – 30 m (Through Walls) | 0.5 m – 3.0 m (In-Rack) |
| **Physical Bandwidth** | 25 Gbps – 100 Gbps (per $\lambda$) | 20 Gbps – 40 Gbps | 5 Gbps – 15 Gbps | 64 GB/s (PCIe 5 x16) |
| **PHY Latency** | **$4.9\ \mu\text{s/km}$** ($< 0.05\text{ ms}$) | **$1.0\text{ ms} – 2.0\text{ ms}$** | **$2.5\text{ ms} – 5.0\text{ ms}$** | **$< 50\text{ ns}$** |
| **Packet Jitter** | $< 0.001\text{ ms}$ (Deterministic) | $0.2\text{ ms} – 0.5\text{ ms}$ | $0.5\text{ ms} – 2.0\text{ ms}$ | $0.0\text{ ms}$ (Bus clock) |
| **Weather Dependency** | **Zero** (Impervious to rain) | Rain fade (handled by QAM fallbacks) | Indoor only / negligible | Zero |
| **Capital Deployment Cost** | \$15k–\$40k / mile (trenching/aerial) | \$800–\$1,500 / node (rooftop kit) | \$150–\$300 / node | \$50–\$150 / cable |
| **Deployment Time** | Weeks / Months (permits & splicing) | Hours (mount antenna & align) | Minutes (plug in) | Seconds (plug in) |

---

### Scenario A: When Fiber Optics IS Required

1. **Sub-Millisecond Interactive Cloud Gaming & CAD Viewports:**
   - At 120 FPS, the total frame time budget is strictly **$8.33\text{ ms}$** (for 60 FPS: **$16.67\text{ ms}$**).
   - In a 6.28 ms frame pipeline, client input takes $0.4\text{ ms}$, GPU render/encode takes $4.3\text{ ms}$, and client decode takes $1.5\text{ ms}$. This leaves **$< 1.5\text{ ms}$ for total round-trip network transit**.
   - Fiber optic transmission travels at $\frac{c}{n} \approx \frac{299,792\text{ km/s}}{1.4682} \approx 204,190\text{ km/s}$, yielding **$4.897\ \mu\text{s/km}$**. For a 5 km neighborhood loop, propagation delay is just **$0.024\text{ ms}$**—virtually instantaneous.
   - Any wireless jitter or Wi-Fi contention will blow past the $8.33\text{ ms}$ frame deadline, resulting in stutter. Fiber is required for esports-grade remote gaming.

2. **Distributed Large-Model Sharding & Tensor Parallelism:**
   - Sharding models across nodes (e.g. Megatron-LM tensor parallel or Ring Attention) requires continuous exchange of high-dimensional activation matrices during the forward and backward passes.
   - If communication latency exceeds tensor compute time, GPUs stall on barrier synchronization (`MPI_Allreduce`).
   - Dedicated 100 Gbps single-mode fiber links allow distributed nodes across a block to operate as if they shared the same backplane.

3. **Zero-Switch CWDM/DWDM Passive Lambda Routing:**
   - Traditional internet routing passes packets through 5 to 15 intermediate ISP routers, each introducing bufferbloat, queuing delays, and jitter ($15\text{ ms} – 45\text{ ms}$).
   - With dedicated fiber, nodes can utilize **Coarse/Dense Wavelength Division Multiplexing (CWDM/DWDM)**. Each neighbor transmits on their own optical wavelength ($\lambda_i$) over a passive optical splitter. There are **zero active packet switches** in between—light travels uninterrupted from host transceiver to peer transceiver.

---

### Scenario B: When Fiber Optics is NOT Required

1. **Neighborhood Rooftop Line-of-Sight (60GHz mmWave Phased-Array):**
   - For neighbors living across the street or within 500 meters who cannot trench public roads due to municipal right-of-way regulations, **60GHz IEEE 802.11ay** provides a full 20 to 40 Gbps over the air.
   - Phased-array beamforming electronically steers high-gain RF beams directly toward peer antennas with 1.0–1.5 ms RTT.
   - Adaptive modulation dynamically downshifts from 4096-QAM to 64-QAM during heavy downpours, maintaining the link without fiber infrastructure.

2. **Intra-Home & Cluster Compute (CXL 3.0 / PCIe Direct Cable):**
   - Between computers in the same room or rack (e.g. Node 1 SkyTech and Node 2 Ryzen 7), PCIe 5.0 x16 copper cables or CXL 3.0 links provide 64 GB/s throughput with sub-50 nanosecond latency. Fiber is completely unnecessary at this scale.

3. **Asynchronous Batch Compute & LLM Inference (WireGuard Overlay):**
   - Non-interactive AI tasks (batch embedding generation, deep research sweeps, image generation, biological sequence folding) are latency-tolerant.
   - These workloads run seamlessly over existing residential broadband (GPON, cable, 5G) utilizing ClothOS's encrypted P2P WireGuard mesh with `TorqueScrubber` air-gapped scrubbing.

---

## 3. The ClothOS Fabric Modem Hardware Design

The **ClothOS Fabric Modem** is a cyber-physical communication and cryptographic co-processor designed to seat directly into a host PC or server.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        CLOTHOS FABRIC MODEM HARDWARE ARCHITECTURE                      │
│                                                                                        │
│  ┌───────────────────────────────┐          ┌───────────────────────────────────────┐  │
│  │   HOST PCIe / CXL BUS         │          │   PHYSICAL AIR-GAP CUT-OFF SWITCH     │  │
│  │   PCIe Gen 5 x16 (64 GB/s)    │          │   (Hardware-Enforced Ring P0 Gate)    │  │
│  └───────────────┬───────────────┘          └───────────────────┬───────────────────┘  │
│                  │                                              │                      │
│  ┌───────────────▼──────────────────────────────────────────────▼───────────────────┐  │
│  │                         FABRIC CORE PROCESSING ASIC / FPGA                        │  │
│  │                                                                                  │  │
│  │  ┌────────────────────────┐  ┌────────────────────────┐  ┌────────────────────┐  │  │
│  │  │ RISC-V RV64GC Core     │  │ Base-16 DMA Engine     │  │ PoVC Crypto Engine │  │  │
│  │  │ Embedded Control RTOS  │  │ 0xFA81 Magic Framing   │  │ Ed25519 & HMAC-    │  │  │
│  │  │ Mesh State Machine     │  │ Hardware CRC32 Shifter │  │ SHA256 Line-Rate   │  │  │
│  │  └────────────────────────┘  └────────────────────────┘  └────────────────────┘  │  │
│  │                                                                                  │  │
│  │  ┌────────────────────────┐  ┌────────────────────────┐  ┌────────────────────┐  │  │
│  │  │ Gas Metering Unit      │  │ Video Stream Engine    │  │ PTP IEEE 1588v2    │  │  │
│  │  │ Hardware Joule/VRAM    │  │ NVENC / AV1 Low-       │  │ Sub-Nanosecond     │  │  │
│  │  │ Microsecond Counters   │  │ Latency Slicing        │  │ Clock Sync         │  │  │
│  │  └────────────────────────┘  └────────────────────────┘  └────────────────────┘  │  │
│  └───────────────────────┬──────────────────────────────────────┬───────────────────┘  │
│                          │                                      │                      │
│            ┌─────────────▼──────────────┐         ┌─────────────▼──────────────┐       │
│            │      OPTICAL PHY BLOCK     │         │      WIRELESS RF PHY       │       │
│            │  2x SFP28 / QSFP28 (BiDi)  │         │  60GHz Phased-Array +      │       │
│            │  100G / 25G WDM Transceiver│         │  Wi-Fi 7 (320MHz MLO)      │       │
│            └─────────────┬──────────────┘         └─────────────┬──────────────┘       │
└──────────────────────────┼──────────────────────────────────────┼──────────────────────┘
                           │                                      │
                     Single-Mode Fiber                    Over-the-Air Airwaves
```

### 1. Form Factors
1. **PCIe Gen 5 x16 Low-Profile AIC (Add-In Card):** Standard PCIe expansion card for desktop rigs (SkyTech, gaming PCs, workstations). Requires no external power brick (draws up to 75W off PCIe slot + optional 6-pin 12V rail).
2. **OCP 3.0 NIC Form Factor:** SFF hot-swappable mezzanine card for enterprise server chassis and high-density compute nodes.
3. **External USB4 / Thunderbolt 5 "Fabric Puck":** Portable aluminum enclosure connecting via 80–120 Gbps Thunderbolt 5 cable, containing an integrated 60GHz beamforming array and one SFP28 optical cage for laptops and mini-PCs.

---

### 2. Silicon Subsystems & Functional Blocks

#### A. Host Interface (PCIe Gen 5 & CXL 3.0)
- **PCIe Gen 5 x16:** Delivers 63 GB/s bidirectional raw bandwidth, matching the full speed of host GPU GDDR6/HBM memory transfers.
- **CXL 3.0 Support (Type 2 / Type 3):** Enables coherent host memory access. A remote peer's VRAM or host memory can be mapped directly into the local CPU/GPU virtual address space without software OS kernel involvement.

#### B. Embedded Management Core (RISC-V RV64GC)
- Embedded 64-bit RISC-V microcontroller running a hardened real-time microkernel (ClothOS MicroRTOS).
- Manages the modem state machine (`SCANNING`, `ASSOCIATING`, `ONLINE_MESH`), automatic beam steering, beacon packet generation, and Tit-for-Tat credit balance accounting independently of host CPU load.

#### C. Base-16 DMA Acceleration Engine
- Hardware state machine that inspects incoming/outgoing memory buffers at line rate.
- Automatically packs raw bytes into canonical Base-16 nibble-aligned frames with `0xFA81` magic word headers, payload length indicators, and hardware-computed CRC32 checksums.
- Operates in zero-copy mode via direct bus-mastering.

#### D. Hardware Gas Metering Unit (GMU)
- Connected to onboard high-precision shunt resistors and host PMBus/SMBus power rails (monitoring 12V and 3.3V rails at 100 kHz).
- Hardware counters increment in real-time:
  - $\text{Total Joules} = \int V(t) \cdot I(t) \, dt$
  - Active VRAM-seconds allocated.
  - TFLOPS dispatched (monitoring GPU activity via PCIe counter interrupts).
- Computes Landauer thermodynamic dissipation ($1.2\text{ pJ}/\text{MAC}$) at hardware level, preventing software spoofing of compute metrics.

#### E. Line-Rate PoVC Cryptographic Accelerator
- Dual hardware cryptographic cores: **Ed25519** digital signature engine and **HMAC-SHA256** pipeline.
- When a compute piece or video frame completes, the PoVC engine hashes the input/output state root and signs the receipt in **$< 50\text{ nanoseconds}$**, introducing zero measurable latency into the compute pipeline.

#### F. Physical Air-Gap Cut-Off Switch (Ring P0 Sovereign Enclave)
- A physical hardware relay / solid-state optical switch positioned between the MAC layer and the optical lasers / RF power amplifiers.
- Controlled strictly by **Ring P0 root-of-trust authorization** (`Najmos Sakib`).
- When the gateway transitions to `HYPER_LOCAL_PRIVATE` mode, power to the optical laser diodes and RF power amplifiers is **physically cut**.
- **Security Guarantee:** Even in the event of an arbitrary kernel exploit or remote compromise, data egress to the external world is physically impossible because the physical transmission hardware is completely de-energized.

---

## 4. Fiber Optics Networking & Neighborhood Topology

### 1. Fiber Cable & Optical Specification
- **Glass Standard:** **ITU-T G.652.D / G.657.A2 OS2 Single-Mode Fiber (SMF)**. 
  - Core diameter: $9.0\ \mu\text{m}$; Cladding diameter: $125.0\ \mu\text{m}$.
  - G.657.A2 bend-insensitive fiber allows tight $7.5\text{ mm}$ bend radii, making it durable for residential conduit and doorframe routing.
- **Why Multi-Mode Fiber (OM4/OM5) is NOT Used:** Multi-mode fiber suffers modal dispersion, limiting 25G/100G signals to $< 100\text{ meters}$. Single-mode glass has zero modal dispersion and supports transmissions over 20+ kilometers.

### 2. Optical Transceiver Architecture: BiDi (Bidirectional WDM)
Traditional networking requires two fiber strands per link (one for TX, one for RX), doubling fiber procurement and splicing costs. ClothOS adopts **Bidirectional (BiDi) WDM Optics**:

```
[Host Node 1: SkyTech]                                        [Host Node 2: Ryzen 7 / Neighbor]
┌─────────────────────────┐                                      ┌─────────────────────────┐
│ ClothOS Fabric Modem    │                                      │ ClothOS Fabric Modem    │
│ SFP28 BiDi Transceiver  │                                      │ SFP28 BiDi Transceiver  │
│ ┌─────────────────────┐ │      Single-Strand OS2 Fiber Cable   │ ┌─────────────────────┐ │
│ │ TX: 1270nm Laser    ├─┼──────────────────────────────────────┼─┤ RX: 1270nm Photodiode│ │
│ │ RX: 1330nm Photodiode│ │                                      │ │ TX: 1330nm Laser    │ │
│ └─────────────────────┘ │                                      │ └─────────────────────┘ │
└─────────────────────────┘                                      └─────────────────────────┘
```

- **Upstream ($\lambda_1$):** $1270\text{ nm}$ DFB Laser (transmit from Node 1 to Node 2).
- **Downstream ($\lambda_2$):** $1330\text{ nm}$ DFB Laser (transmit from Node 2 to Node 1).
- **Single Optical Core:** Full duplex 25 Gbps or 100 Gbps communication over a **single strand of glass**.
- **Connector Type:** LC-APC (Angled Physical Contact, green connector) with $<-60\text{ dB}$ optical return loss, eliminating laser reflections.

---

### 3. Neighborhood Physical Topologies

#### Topology 1: Dedicated Point-to-Point (P2P) Star
Each participant runs a single-strand fiber drop cable to a central passive neighborhood enclosure (e.g. located in a utility shed, garage, or pole-mounted pedestal).
- **Pros:** Maximum security, dedicated 100 Gbps line-rate per participant, zero optical splitting loss.
- **Cons:** Requires home-run fiber pulls from each house.

#### Topology 2: Passive CWDM Lambda Ring (Zero Active Switches)
A single continuous fiber ring loops through the neighborhood. Each home is spliced into an **Optical Add-Drop Multiplexer (OADM)** tuned to a specific ITU grid wavelength:

```
                  ┌─────────────────────────────────────────────────────────┐
                  │                 Passive CWDM Optical Ring                │
                  │                                                         │
       ┌──────────┴──────────┐                                   ┌──────────┴──────────┐
       │   OADM 1: 1270nm    │                                   │   OADM 2: 1290nm    │
       │   (House A: SkyTech)│                                   │   (House B: Gamer)  │
       └──────────┬──────────┘                                   └──────────┬──────────┘
                  │                                                         │
       ┌──────────┴──────────┐                                   ┌──────────┴──────────┐
       │   OADM 4: 1330nm    │                                   │   OADM 3: 1310nm    │
       │   (House D: Creator)│                                   │   (House C: Node 2) │
       └─────────────────────┘                                   └─────────────────────┘
```

- House A communicates with House B by transmitting on $\lambda_2 = 1290\text{ nm}$.
- Light passes through all intermediate OADMs passively with only $\sim 0.8\text{ dB}$ insertion loss per node.
- **Latency Advantage:** Exactly speed-of-light optical transit ($4.9\ \mu\text{s/km}$). **Zero router queuing delays, zero switch bufferbloat, zero CPU processing hops.**

#### Topology 3: Hybrid Fiber-Wireless (HFW) Mesh
The pragmatic bootstrap architecture:
- One anchor home with existing high-speed fiber hosts a ClothOS Fabric Modem equipped with an external **60GHz mmWave 360-degree rooftop transceiver**.
- Neighbors within 500 meters mount small 60GHz subscriber units on their eaves, connecting wirelessly at 20–40 Gbps.
- As gas tax revenue accumulates in the Spotlight-Local treasury, the neighborhood funds micro-trenched fiber drops to replace the wireless links.

---

### 4. Optical Link Budget & Attenuation Math

To ensure carrier-grade reliability without optical amplifiers, the physical link budget is calculated as follows:

$$\text{Margin } (M) = P_{\text{tx}} - P_{\text{rx\_sens}} - \left( \alpha_{\text{fiber}} \cdot L + N_{\text{conn}} \cdot L_{\text{conn}} + N_{\text{splice}} \cdot L_{\text{splice}} + L_{\text{OADM}} \right)$$

For a **5.0 km** neighborhood optical fiber run with 4 LC-APC connectors and 2 fusion splices:
- **Transmitter Launch Power ($P_{\text{tx}}$):** $+3.0\text{ dBm}$ (Standard 25G BiDi DFB laser)
- **Receiver Sensitivity ($P_{\text{rx\_sens}}$):** $-20.0\text{ dBm}$ (PIN receiver sensitivity)
- **Total Power Budget:** $3.0 - (-20.0) = \mathbf{23.0\text{ dB}}$
- **Fiber Attenuation:** $5.0\text{ km} \times 0.35\text{ dB/km} = 1.75\text{ dB}$ (at $1310\text{ nm}$)
- **Connector Loss:** $4 \times 0.50\text{ dB} = 2.00\text{ dB}$
- **Splice Loss:** $2 \times 0.05\text{ dB} = 0.10\text{ dB}$
- **Total Channel Insertion Loss:** $1.75 + 2.00 + 0.10 = \mathbf{3.85\text{ dB}}$
- **Optical Link Margin:** $23.0 - 3.85 = \mathbf{+19.15\text{ dB}}$

> **Conclusion:** An optical margin of $+19.15\text{ dB}$ provides an extraordinary reliability buffer ($> 80\times$ reserve power). The link will operate completely error-free across all seasons, temperature swings ($-40^\circ\text{C}$ to $+85^\circ\text{C}$), and fiber aging over 25+ years.

---

## 5. Deployment Economics & Practical Playbook

### 1. Fabric Modem Bill of Materials (BOM Estimate)

| Subsystem Component | Example Silicon / Part | Estimated Cost (Volume 1k) |
|---|---|---|
| **FPGA / Core SoC** | AMD Xilinx Artix UltraScale+ / Versal Prime | \$180 – \$250 |
| **PCIe Gen 5 Retimer & PCB** | 8-layer low-loss Rogers / Megtron-6 PCB | \$45 – \$65 |
| **Optical PHY & Dual SFP28 Cages** | Marvell / Broadcom 25G/100G SerDes PHY | \$35 – \$50 |
| **Optical Transceiver Module** | 25G BiDi SFP28 10km (1270/1330nm LC-APC) | \$38 – \$55 |
| **60GHz Phased-Array RFIC** | Sivers Semiconductors / Qualcomm 60GHz RFIC | \$45 – \$70 |
| **Air-Gap Hardware Relay & Enclave** | Solid-state high-isolation RF/optical switch | \$12 – \$18 |
| **Gas Metering Shunt / PMBus IC** | TI INA3221 + Precision Shunt Array | \$6 – \$10 |
| **Enclosure, Heat Sink & Packaging** | CNC Aluminum heatsink with active blower | \$20 – \$30 |
| **Total Target BOM Cost** | **Complete ClothOS Fabric Modem** | **\$381 – \$548** |

*Target Retail / Host Price: **\$499 – \$699** (offset within 3–6 months through Spotlight-Local compute seeding payouts).*

---

### 2. Fiber Deployment Cost Analysis: Real-World Methods

| Method | Trenching Technique | Cost per Foot / Meter | Permitting Requirements | Ideal Application |
|---|---|---|---|---|
| **Aerial Lashed Fiber** | Lashed to existing power / telecom poles | \$3 – \$8 / ft (\$10 – \$25 / m) | Utility pole attachment agreement | Suburbs and rural communities with utility poles |
| **Micro-Trenching** | $1\text{ inch}$ wide, $12\text{ inch}$ deep saw cut in asphalt curb line | \$8 – \$15 / ft (\$25 – \$50 / m) | Municipal street right-of-way | Dense residential streets, paved neighborhoods |
| **Directional Boring** | Horizontal underground drill | \$20 – \$45 / ft (\$65 – \$150 / m) | Major street crossing permit | Crossing highways, railways, waterways |
| **60GHz mmWave (Wireless)** | **Zero Trenching (Over the air)** | **\$0 / ft (\$0 / m)** | None (Unlicensed 60GHz V-Band) | Immediate bootstrap deployment |

### 3. The 3-Phase Community Bootstrap Strategy
1. **Phase 1 (Immediate - Day 1):** Deploy ClothOS Fabric Modems using **60GHz mmWave rooftop links and Wi-Fi 7**. Zero municipal permits, zero trenching. Neighborhood begins earning compute credits ($\Xi$) and USD immediately.
2. **Phase 2 (Growth - Month 3 to 6):** As Spotlight-Local transaction volume grows, the 1.0% protocol platform fee funds a shared community infrastructure pool.
3. **Phase 3 (Physical Fiber Anchor - Month 6+):** Execute shallow micro-trenching or aerial lasher fiber runs along the highest-density compute corridors, replacing mmWave hops with dedicated 100G single-strand BiDi optical links for permanent speed-of-light gaming and training.

---

## 6. Software & Protocol Stack Verification

The physical hardware and optical networking models are integrated into the ClothOS test and runtime stack:
- **`loom.hardware.transceiver`:** Extended with `TransceiverBand.FIBER_BIDI_100G` and `TransceiverBand.FIBER_PON_10G`, accurately simulating single-mode optical attenuation ($0.35\text{ dB/km}$) and silica propagation speed ($4.897\ \mu\text{s/km}$).
- **`loom.hardware.fabric_modem`:** Connects peer discovery to optical carrier parameters.
- **`loom.hardware.seamless_gateway`:** Routes tasks across optical and RF transceivers based on latency constraints ($< 16.6\text{ ms}$ routing gaming tasks to optical fiber peers).
- **`tests.test_fabric_modem_seamless`:** Verified green across optical fiber propagation models.
