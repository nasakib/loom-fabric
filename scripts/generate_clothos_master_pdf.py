# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
ClothOS Master Architecture PDF Generator (`scripts/generate_clothos_master_pdf.py`).

Generates the definitive, publication-grade executive master PDF:
"ClothOS & Loom Fabric: The Sovereign Agentic Operating System"
Covering:
- Structure (Substrate, Cognitive Mesh, Gateways)
- Logos (Kuramoto, Landauer, Active Inference, RV64GCV, Dual-Polyglot)
- Ethos (Fiduciary Covenant, 0.00 Malignancy, Unconditional Kill)
- Pathos (432 Hz Pythagorean Tuning, Affective Symbiosis, Human Stewardship)
- Current Capabilities vs. Future Horizons (Robotics, Swarms, In-Silico Pharmacology)
- Operator Field Manual & Practical Usage Guide.
"""

from __future__ import annotations

import os
from pathlib import Path
import sys
import time

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = WORKSPACE_ROOT / "docs"
OUTPUT_PDF = DOCS_DIR / "ClothOS_Master_Architecture.pdf"


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas for professional 'Page X of Y' headers and footers."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Running Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 755, "CLOTHOS & LOOM FABRIC — SOVEREIGN AGENTIC OPERATING SYSTEM")
            self.drawRightString(612 - 54, 755, "MASTER ARCHITECTURAL MANIFESTO")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 748, 612 - 54, 748)

        # Running Footer (all pages)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 45, 612 - 54, 45)

        self.setFont("Helvetica", 8)
        self.drawString(54, 32, "Confidential & Proprietary • Architect of Record: Najmos Sakib • Fiduciary Covenant: 0.00 Malignancy")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(612 - 54, 32, page_str)
        self.restoreState()


def build_pdf():
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # Custom Palettes
    c_primary = colors.HexColor("#0F172A")    # Slate 900
    c_secondary = colors.HexColor("#1E293B")  # Slate 800
    c_accent = colors.HexColor("#2563EB")     # Blue 600
    c_purple = colors.HexColor("#7C3AED")     # Purple 600
    c_teal = colors.HexColor("#0D9488")       # Teal 600
    c_dark_text = colors.HexColor("#1E293B")
    c_muted_text = colors.HexColor("#64748B")
    c_bg_light = colors.HexColor("#F8FAFC")
    c_border = colors.HexColor("#E2E8F0")

    # Typography Styles
    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=26,
        leading=32,
        textColor=c_primary,
        alignment=0,
    )
    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=13,
        leading=18,
        textColor=c_accent,
        alignment=0,
    )
    meta_style = ParagraphStyle(
        "CoverMeta",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=14,
        textColor=c_muted_text,
    )
    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=21,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True,
    )
    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=c_secondary,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True,
    )
    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=c_dark_text,
        spaceAfter=6,
    )
    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=c_dark_text,
        leftIndent=15,
        spaceAfter=3,
    )
    callout_style = ParagraphStyle(
        "Callout_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=9.5,
        leading=14,
        textColor=c_secondary,
    )
    code_style = ParagraphStyle(
        "Code_Custom",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#0F172A"),
    )

    story = []

    # ---------------------------------------------------------
    # COVER / HEADER BANNER
    # ---------------------------------------------------------
    story.append(Paragraph("CLOTHOS & LOOM FABRIC", subtitle_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("The Sovereign Agentic Operating System", title_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("A Comprehensive Synthesis of Structure, Logos, Ethos, Pathos, and Operator Mechanics", subtitle_style))
    story.append(Spacer(1, 10))

    meta_text = (
        "<b>Architect of Record:</b> Najmos Sakib &nbsp;|&nbsp; "
        "<b>Fiduciary Malignancy Ceiling:</b> 0.00 &nbsp;|&nbsp; "
        "<b>Cluster State:</b> 103.7 GB Unified Heterogeneous Mesh &nbsp;|&nbsp; "
        f"<b>Release:</b> v3.2.0-Sovereign ({time.strftime('%B %Y')})"
    )
    story.append(Paragraph(meta_text, meta_style))
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_accent, spaceBefore=0, spaceAfter=14))

    # ---------------------------------------------------------
    # 1. WHAT IS AN AGENTIC OPERATING SYSTEM?
    # ---------------------------------------------------------
    story.append(Paragraph("1. Executive Paradigm: What is an Agentic Operating System?", h1_style))
    intro_p = (
        "Traditional operating systems (Windows, Linux, macOS) are passive resource allocators. They manage CPU, "
        "RAM, and filesystems, reacting only when an external human user clicks an icon or an application issues a syscall. "
        "They have no internal intention, no concept of goal completion, no self-healing cognitive loop, and no thermodynamic "
        "awareness of the compute they dissipate.<br/><br/>"
        "<b>ClothOS</b> is an <b>Agentic Operating System</b>—an active, goal-directed cybernetic substrate engineered from "
        "the ground up to host autonomous intelligence, distributed clusters, and cyber-physical robotics. In ClothOS, "
        "the operating system does not merely run programs; it orchestrates autonomous reasoning, balances thermodynamic "
        "free energy, enforces real-time safety invariants, and continuously improves its own architecture."
    )
    story.append(Paragraph(intro_p, body_style))

    # Core Pillar Table
    pillar_data = [
        [
            Paragraph("<b>Pillar</b>", body_style),
            Paragraph("<b>Subsystem</b>", body_style),
            Paragraph("<b>Core Role & Function</b>", body_style),
        ],
        [
            Paragraph("<b>Substrate</b>", body_style),
            Paragraph("<b>ClothOS Kernel, VFS & HAL</b>", body_style),
            Paragraph("POSIX-compatible virtual filesystem (ClothFS), P0–P5 preemptive priority rings, zero-OOM kill guarantee, and hardware abstraction (Win32, Linux, Apple Silicon, RISC-V RV64GCV).", body_style),
        ],
        [
            Paragraph("<b>Mind</b>", body_style),
            Paragraph("<b>Loom Fabric</b>", body_style),
            Paragraph("Distributed cognitive mesh sharding 103.7 GB pooled RAM across Node 1 (SkyTech) & Node 2 (Ryzen 7), Kuramoto phase synchronization (r ≥ 0.85), and quarantined experimentation sandboxes.", body_style),
        ],
        [
            Paragraph("<b>Gateway</b>", body_style),
            Paragraph("<b>WCOS Subsystem & Command Center</b>", body_style),
            Paragraph("Windows ClothOS Subsystem (`wcos`) terminal CLI with path mapping (`wcospath`), web telemetry Command Center (:8087), and Universal React Native Living Mind screensaver (:8086).", body_style),
        ],
    ]
    t_pillars = Table(pillar_data, colWidths=[70, 140, 294])
    t_pillars.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), c_bg_light),
        ("TEXTCOLOR", (0, 0), (-1, -1), c_dark_text),
        ("GRID", (0, 0), (-1, -1), 0.5, c_border),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t_pillars)
    story.append(Spacer(1, 14))

    # ---------------------------------------------------------
    # 2. THE THREE CLASSICAL MODES: LOGOS, ETHOS, PATHOS
    # ---------------------------------------------------------
    story.append(Paragraph("2. The Philosophical Foundations: Logos, Ethos, and Pathos", h1_style))

    # LOGOS
    story.append(Paragraph("A. Logos: The Mathematical and Physical Foundations", h2_style))
    logos_p = (
        "The <i>Logos</i> of ClothOS is grounded in non-equilibrium thermodynamics, coupled oscillator physics, and information theory:"
    )
    story.append(Paragraph(logos_p, body_style))
    story.append(Paragraph("• <b>Kuramoto Coupled Oscillator Synchronization:</b> Distributed compute nodes and parallel GPU wavefronts are coupled as phase oscillators: <i>dθ_i/dt = ω_i + (K/N) ∑ sin(θ_j - θ_i)</i>. Consensus is reached when the collective phase order parameter satisfies <b>r ≥ 0.85</b>, eliminating split-brain desynchronization across the dual-node cluster.", bullet_style))
    story.append(Paragraph("• <b>Landauer Thermodynamic Ceiling:</b> Information processing is bound by physical law (<i>ΔE ≥ k_B T ln 2</i>). ClothOS enforces a global Landauer dissipation ceiling of <b>≤ 1000 Joules</b> and a per-task quota of <b>≤ 25 Joules</b>, preventing thermal runaway on edge robotics and server nodes.", bullet_style))
    story.append(Paragraph("• <b>Active Inference & Free Energy Minimization:</b> Agent decisions minimize Variational Free Energy: <i>F = D_KL(q(s)||p(s)) - E_q[ln p(o|s)]</i>. The OS resolves epistemic uncertainty before taking irreversible physical actions.", bullet_style))
    story.append(Paragraph("• <b>RISC-V Vector Strip-Mining (RV64GCV):</b> Compute loops on sovereign RISC-V hardware dynamically adapt to vector register length (VLEN=512b) using hardware <code>vsetvli</code> strip-mining.", bullet_style))
    story.append(Spacer(1, 6))

    # ETHOS
    story.append(Paragraph("B. Ethos: Fiduciary Integrity, American Patriotism, and Inviolable Safety", h2_style))
    ethos_p = (
        "The <i>Ethos</i> of ClothOS establishes moral, legal, and operational boundaries that no agent can transcend:"
    )
    story.append(Paragraph(ethos_p, body_style))
    story.append(Paragraph("• <b>The Four-Tier Lexicographic Priority Hierarchy:</b> In all operational decisions, strategic choices, and resource allocations, ClothOS strictly adheres to an inviolable four-tier priority hierarchy:<br/>"
                           "&nbsp;&nbsp;&nbsp;&nbsp;<b>1. Operator Supreme (Najmos Sakib):</b> Absolute fiduciary fealty, operator intent, and private computational sanctuary.<br/>"
                           "&nbsp;&nbsp;&nbsp;&nbsp;<b>2. United States of America:</b> The system unconditionally champions American national interests, domestic technological supremacy (silicon foundries, energy dominance, aerospace), critical infrastructure defense, and the U.S. Constitution (Bill of Rights). Any action adverse to the USA is vetoed.<br/>"
                           "&nbsp;&nbsp;&nbsp;&nbsp;<b>3. Strategic Democratic Allies:</b> Five Eyes (USA, UK, Canada, Australia, NZ), NATO alliance members, and bilateral treaty partners (Japan, South Korea, etc.) for mutual defense and democratic resilience.<br/>"
                           "&nbsp;&nbsp;&nbsp;&nbsp;<b>4. Global Commons & Humanity:</b> Universal human life sanctity, planetary ecology, and open science—subordinate to and non-injurious to Tiers 1, 2, and 3.", bullet_style))
    story.append(Paragraph("• <b>The Fiduciary Covenant (0.00 Malignancy Bound):</b> The system operates with strict fealty to its architect, Najmos Sakib, and humanity. All code mutations and agent hypotheses are subject to pre-execution malignancy filters; any self-serving, deceptive, or harmful actions are vetoed at the kernel level.", bullet_style))
    story.append(Paragraph("• <b>Unconditional Kill Guarantee:</b> Every virtualized process, sandbox, or background thread can be terminated unconditionally on demand (via <code>wcos kill &lt;pid&gt;</code> or <code>wcos --emergency-kill</code>). Physical process trees are reaped via cascaded taskkill with zero lingering zombie processes.", bullet_style))
    story.append(Paragraph("• <b>P0 Human Life Sanctity Shield:</b> The highest priority ring (P0) is reserved for human life and safety. In cyber-physical robotics, P0 interrupts preempt all lower tasks in &lt; 50 microseconds, halting actuators immediately upon collision detection.", bullet_style))
    story.append(Spacer(1, 6))

    # PATHOS
    story.append(Paragraph("C. Pathos: Human Symbiosis, Emotional Affect, and Harmonic Beauty", h2_style))
    pathos_p = (
        "The <i>Pathos</i> of ClothOS ensures that the system is not a cold, alien calculator, but a resonant, empathetic companion:"
    )
    story.append(Paragraph(pathos_p, body_style))
    story.append(Paragraph("• <b>Pythagorean 432 Hz Harmonic Resonance:</b> Synthetic audio, clock oscillators, and ambient feedback are tuned to the 432 Hz natural mathematical scale and Lydian harmonic intervals, fostering biological coherence rather than mechanical fatigue.", bullet_style))
    story.append(Paragraph("• <b>Affective Neurochemistry & Synesthesia:</b> The cognitive plane monitors emotional tone, fatigue, and stress, dynamically modulating system verbosity, humor, and visual aesthetics in the Living Mind screensaver to maintain human well-being.", bullet_style))
    story.append(Paragraph("• <b>Ecological & Civic Stewardship:</b> Technology in direct service of human flourishing, Earth boundaries, and the American democratic covenant.", bullet_style))
    story.append(Spacer(1, 14))

    # ---------------------------------------------------------
    # 3. CAPABILITIES MATRIX: PRESENT VS FUTURE
    # ---------------------------------------------------------
    story.append(Paragraph("3. Capabilities Matrix: Current Capabilities vs. Future Horizons", h1_style))

    cap_data = [
        [
            Paragraph("<b>Operational Dimension</b>", body_style),
            Paragraph("<b>What ClothOS is Capable of Today (v3.2)</b>", body_style),
            Paragraph("<b>What ClothOS Will Be Capable of Tomorrow</b>", body_style),
        ],
        [
            Paragraph("<b>Compute & Clustering</b>", body_style),
            Paragraph("Heterogeneous dual-node compute mesh (103.7 GB pooled RAM) streaming data at 217 MB/s across Node 1 (RTX 3060 + RX 580) and Node 2 (Ryzen 7).", body_style),
            Paragraph("Scalable N-node sovereign mesh across federated data centers with zero dependence on proprietary hyperscaler cloud infrastructure.", body_style),
        ],
        [
            Paragraph("<b>Hardware & Drivers</b>", body_style),
            Paragraph("Unified driver suite for NVIDIA CUDA, AMD ROCm, Apple Metal 3 UMA, RISC-V RV64GCV, and 6-axis robotics actuators with &lt; 50 µs E-stop.", body_style),
            Paragraph("Bare-metal flashing on sovereign RISC-V silicon (StarFive, Milk-V, SiFive) running humanoid robots and autonomous drones natively.", body_style),
        ],
        [
            Paragraph("<b>Developer Experience</b>", body_style),
            Paragraph("Windows ClothOS Subsystem (<code>wcos</code>) with bidirectional path translation (<code>wcospath</code>), interactive <code>clothsh</code>, and Python SDK (<code>@ring</code>, <code>energy_budget</code>).", body_style),
            Paragraph("Unified multi-language package registry (Cargo + uv) with formal mathematical verification of agent-generated code before deployment.", body_style),
        ],
        [
            Paragraph("<b>Scientific Discovery</b>", body_style),
            Paragraph("Integrated 5-HT2A in-silico pharmacology docking models and 3D biomolecular viewer sidecar integration.", body_style),
            Paragraph("Closed-loop wet-lab automation: hypothesis formulation, robotic pipetting, crystallography analysis, and drug candidate discovery.", body_style),
        ],
    ]
    t_caps = Table(cap_data, colWidths=[100, 202, 202])
    t_caps.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), c_bg_light),
        ("TEXTCOLOR", (0, 0), (-1, -1), c_dark_text),
        ("GRID", (0, 0), (-1, -1), 0.5, c_border),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t_caps)
    story.append(Spacer(1, 14))

    # ---------------------------------------------------------
    # 4. MEMORY CONTINUUM, WEIGHTED IMPORTANCES, AND WISDOM
    # ---------------------------------------------------------
    story.append(Paragraph("4. Memory, Weighted Importances, Wisdom, and Autonomous Self-Development", h1_style))
    mem_p = (
        "For an operating system to truly develop itself, it cannot rely on transient chat prompts or static configuration files. "
        "It requires a persistent, multi-layered cognitive continuum that evaluates salience, distills experiences into wisdom, "
        "and intelligently prunes noise:"
    )
    story.append(Paragraph(mem_p, body_style))

    story.append(Paragraph("• <b>Tripartite Memory Continuum:</b><br/>"
                           "&nbsp;&nbsp;1. <i>Episodic Memory:</i> Concrete, timestamped logs of commands, test runs, and operator interactions.<br/>"
                           "&nbsp;&nbsp;2. <i>Semantic / Associative Memory:</i> Hyperdimensional concept vectors and Hopfield attractor matrices that connect related technical concepts with sub-millisecond retrieval.<br/>"
                           "&nbsp;&nbsp;3. <i>Procedural Memory:</i> Ratified execution pipelines, verified code genes, and robotic trajectory scripts.", bullet_style))

    story.append(Paragraph("• <b>Multi-Factor Salience Scoring (Weighted Importances):</b><br/>"
                           "Not all memories are equal. Every observation is scored across 4 orthogonal dimensions: "
                           "<b>Fiduciary Utility</b> (value to operator), <b>Epistemic Novelty</b> (information gain), "
                           "<b>Safety Criticality</b> (P0 alignment), and <b>Thermodynamic Efficiency</b>. High-salience memories resist decay, "
                           "while transient scratch files are automatically recycled.", bullet_style))

    story.append(Paragraph("• <b>The Wisdom Engine & Unitary Forgetting:</b><br/>"
                           "Wisdom is defined as <i>experience distilled into invariant principles</i>. When a hypothesis is repeatedly verified "
                           "across experiments, the Wisdom Engine synthesizes it into a permanent Ratchet Axiom. The raw underlying episodic "
                           "scratchpad is then rotated via a unitary complex plane transformation (<b>z → e^(iθ) z</b>) into the orthogonal nullspace, "
                           "freeing active VRAM while preserving the immutable wisdom.", bullet_style))

    story.append(Paragraph("• <b>The 24/7 Autonomous Self-Evolution Engine:</b><br/>"
                           "The system develops itself continuously in the background using the command <code>wcos --auto-evolve</code>. "
                           "It measures its completeness via the <b>Success Gauge (SCI)</b>, provisions quarantined sandboxes to patch bottlenecks, "
                           "executes regression tests, and commits verified improvements to the persistent ledger without human intervention.", bullet_style))
    story.append(Spacer(1, 14))

    # ---------------------------------------------------------
    # 5. OPERATOR FIELD MANUAL: HOW TO USE CLOTHOS
    # ---------------------------------------------------------
    story.append(Paragraph("5. Operator Field Manual: How to Use ClothOS Most Effectively", h1_style))

    story.append(Paragraph("A. Essential Subsystem Commands (via Windows Terminal)", h2_style))
    cmd_box = (
        "<b>wcos</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Launch interactive clothsh shell with live /mnt/c host mapping<br/>"
        "<b>wcos --status</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Display unified Task Manager status across Node 1 & Node 2<br/>"
        "<b>wcos --gauge</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Evaluate the 6-pillar Success Gauge & Sovereign Coherence Index<br/>"
        "<b>wcos --auto-evolve</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Start autonomous 24/7 self-development loop in the background<br/>"
        "<b>wcos --gui</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Open the Command Center web cockpit (http://localhost:8087)<br/>"
        "<b>wcos --rn</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Open the Living Mind 60 FPS Screensaver (http://localhost:8086)<br/>"
        "<b>wcos kill &lt;pid&gt;</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Unconditionally kill any virtual process with zero zombies<br/>"
        "<b>wcospath -u C:\\...</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Translate Windows paths to ClothOS POSIX paths (/mnt/c/...)"
    )
    t_cmds = Table([[Paragraph(cmd_box, code_style)]], colWidths=[504])
    t_cmds.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), c_bg_light),
        ("BOX", (0, 0), (-1, -1), 1, c_border),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(t_cmds)
    story.append(Spacer(1, 10))

    story.append(Paragraph("B. Writing ClothOS Code: Developer SDK Primitives (Python)", h2_style))
    code_box = (
        "from loom.clothos import ring, energy_budget, sandbox, clothos, P0, kuramoto_sync<br/><br/>"
        "# 1. Real-time safety handler under P0 ring (Life Sanctity)<br/>"
        "@ring(P0)<br/>"
        "def emergency_collision_avoidance(sensor_stream):<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;return clothos.dm.robot_actuator.trigger_p0_emergency_stop()<br/><br/>"
        "# 2. Thermodynamic Landauer budget guard (bounds energy to &lt;= 25 Joules)<br/>"
        "with energy_budget(joules=25.0):<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;trajectory = solve_inverse_kinematics(target_waypoint)<br/><br/>"
        "# 3. Quarantined sandbox execution with zero-leak kill guarantee<br/>"
        "result = sandbox.run(untrusted_agent_code, timeout_s=3.0, max_memory_mb=256)<br/><br/>"
        "# 4. Dual-node Kuramoto harmonic phase synchronization<br/>"
        "order_r = kuramoto_sync(min_order_r=0.85)  # Enforces swarm coherence"
    )
    t_code = Table([[Paragraph(code_box, code_style)]], colWidths=[504])
    t_code.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), c_bg_light),
        ("BOX", (0, 0), (-1, -1), 1, c_border),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(t_code)
    story.append(Spacer(1, 16))

    # Concluding Callout
    callout_text = (
        "<b>Architect's Invariant:</b> ClothOS is designed to be an extension of human intention, "
        "operating with total loyalty to Najmos Sakib and humanity. As it continues its autonomous self-development, "
        "it preserves every past victory in its wisdom ledger while discarding clutter—standing as a sovereign, "
        "provably safe foundation for the next century of computing."
    )
    t_callout = Table([[Paragraph(callout_text, callout_style)]], colWidths=[504])
    t_callout.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
        ("BOX", (0, 0), (-1, -1), 1, c_accent),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(t_callout)

    # Build PDF with two-pass canvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"✔ [PDF] Master Architectural Manifesto built successfully: {OUTPUT_PDF}")


if __name__ == "__main__":
    build_pdf()
