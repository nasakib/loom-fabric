# SOVEREIGN COMPUTE DISTRIBUTION LICENSE (SCDL)
**Version:** 1.0  
**Licensor:** VectorCore Holdings / BRAND  
**Jurisdiction:** Sovereign Distributed Ledger & Universal Common Law Covenant  
**Standard Identifier:** `SCDL-1.0-RECIPROCAL-COMMERCIAL`  

---

## PREAMBLE

The **Sovereign Compute Distribution License (SCDL)** establishes a legally binding and cryptographically enforceable social-technical contract governing the pooling, leasing, sharing, and commercial monetization of computational resources (including but not limited to Graphics Processing Units, Central Processing Units, Neural Processing Units, volatile memory, and interconnect bandwidth) within the **Loom Fabric** and **ClothOS** ecosystem.

The philosophy of this License is grounded in three immutable axioms:
1. **Computational Sovereignty:** Every individual has the inalienable right to execute inference, train neural models, and preserve cryptographic autonomy without mandatory reliance on centralized hyperscalers.
2. **Reciprocal Equity (The Seeder/Leecher Compact):** Those who contribute idle compute are entitled to draw upon collective compute; those who consume without contribution must equitably compensate the providers.
3. **Absolute Zero-Exfiltration:** Data, prompts, latent activations, and model weights processed across distributed nodes must remain mathematically and operationally sovereign, immune to surveillance, unauthorized telemetry, or third-party harvesting.

---

## TERMS AND CONDITIONS

### 1. DEFINITIONS
- **"Network"** means the Loom Fabric distributed P2P compute mesh, orchestrators, bridges, and interconnected nodes.
- **"Node"** means any physical or virtualized hardware device participating in the Network.
- **"Seeder"** means a Node that contributes verified compute, VRAM, or storage capacity to peers.
- **"Leecher"** means a Node that requests and consumes compute cycles from peers.
- **"Compute Credit ($\Xi$)"** means the standardized, cryptographic unit of computational energy and capacity accounted for within the ClothOS Choice and Credit Ledger.
- **"Proximity Swarm"** means a localized cluster of Nodes interconnected via Low-Latency Interconnects (LAN, Wi-Fi 6 Direct, fiber, or authenticated point-to-point tunnels).

---

### 2. GRANT OF RIGHTS

#### 2.1 Non-Commercial & Reciprocal Use
Subject to compliance with Section 3, the Licensor hereby grants any individual or non-profit organization a worldwide, royalty-free, non-exclusive license to:
1. Run, modify, and deploy Loom Fabric and ClothOS nodes.
2. Pool hardware with other peers in personal, home, or academic Proximity Swarms.
3. Consume compute from the swarm proportional to earned Compute Credits ($\Xi$).

#### 2.2 Commercial Compute Licensing
Any commercial entity, enterprise, or individual utilizing Loom Fabric for commercial revenue generation, or operating purely as a Leecher without reciprocal hardware contribution, is granted rights under the **Commercial Compute Rider**:
1. Commercial Leechers must acquire Compute Credits through sanctioned clearing mechanisms at prevailing market rates.
2. Seeders offering commercial-grade Service Level Agreements (SLAs) are entitled to retain revenues generated from their compute contributions, subject to a protocol clearing fee defined by VectorCore Holdings.

---

### 3. THE SEEDER-LEECHER RECIPROCAL COVENANT

1. **Tit-for-Tat Fairness:** A Node operating within a public or federated Proximity Swarm must maintain an overall Seeding Ratio ($R = \text{Credits Contributed} / \text{Credits Consumed}$) greater than or equal to $0.8$ over a rolling 30-day epoch, unless compensatory monetary credits are posted.
2. **Graceful De-Prioritization:** In conditions of network congestion, requests originating from Nodes with higher Seeding Ratios shall be granted preemptive scheduling priority over Nodes operating in sustained deficit.
3. **No Parasitic Ingestion:** Scrubbing, proxying, or harvesting compute from the Network to resell as an opaque API without registering as an authorized commercial gateway constitutes a material breach and triggers automatic revocation of license.

---

### 4. DATA PRIVACY & ZERO-EXFILTRATION COVENANT

1. **Ephemeral Activation Rule:** Seeders processing tensor shards for peers are strictly forbidden from logging, serializing, persisting, or transmitting intermediate activations, input tokens, or output tokens outside the verified execution pipeline.
2. **Cryptographic Erasure:** Upon completion of a forward-pass or generation stream, all intermediate Key-Value (KV) cache pages and scratchpad activations must be immediately zeroized in physical memory.
3. **Auditability & Attestation:** Seeders must execute verifiable runtimes that permit periodic integrity challenges via the ClothOS Sentinel harness.

---

### 5. CLOTHOS CONSTITUTION & DESIGN INTEGRITY

1. **Radix Compliance:** All distributed scheduling, tensor batching, and invariant checks conducted under this License must preserve compatibility with ClothOS's Dozenal (Base-12) division structures and Balanced Ternary ($T \in \{-1, 0, +1\}$) decision paths.
2. **Immune Exclusion:** Any Node detected deliberately injecting corrupted weights, adversarial gradient poisoning, or falsified Proof-of-Inference telemetry shall be immutably registered in the CRISPR Immune Spacer Ledger (`.clothos_learned_patterns.json`) and permanently barred from peer discovery.

---

### 6. DISCLAIMER OF WARRANTY & LIMITATION OF LIABILITY

THE SOFTWARE AND NETWORK PROTOCOLS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT. IN NO EVENT SHALL VECTORCORE HOLDINGS, BRAND, OR CONTRIBUTORS BE LIABLE FOR ANY CLAIM, DAMAGES, OR HARDWARE LOSS ARISING FROM SILICON OVERCLOCKING, THERMAL RUNAWAY, OR DISTRIBUTED EXECUTION ERRORS.

---

### 7. GOVERNING LAW & SOVEREIGN JURISDICTION

This License is executed under the Sovereign Architectural Charter of VectorCore Holdings / BRAND. Disputes regarding compute accounting or cryptographic compliance shall be resolved through deterministic, on-chain or cryptographic multi-party dispute arbitration.
