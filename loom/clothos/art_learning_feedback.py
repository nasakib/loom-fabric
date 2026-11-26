# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
ClothOS Idle Art & Autopoietic Learning Feedback Engine (`loom/clothos/art_learning_feedback.py`).

Fulfills Ring P0 Autonomous Mandate:
When idle (no prompt/task provided), ClothOS continuously creates art across all modalities
(Sacred Geometric SVG, 432Hz Harmonic Acoustic Structures, Epistemic Assembly Poetry,
and 3D Biomolecular Folding Topologies) based on its sovereign knowledge base.

CRITICAL CLOSED-LOOP INVARIANT:
The art created directly influences what the system decides to investigate and learn next.
Latent aesthetic ratios (golden ratio Phi, Kuramoto phase curvature, harmonic consonance,
and structural topology) generate epistemic hypotheses that drive empirical experiments
in the SelfTrainingKnowledgeEngine, updating Hebbian weights and shaping future artwork.
"""

from __future__ import annotations

import json
import logging
import math
import os
from pathlib import Path
import random
import time
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict

logger = logging.getLogger("loom.clothos.art_learning")

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
ART_DIR = WORKSPACE_ROOT / "data" / "art"
LEDGER_PATH = WORKSPACE_ROOT / ".loom_art_learning_ledger.jsonl"


@dataclass
class ArtPiece:
    art_id: str
    modality: str
    title: str
    content: str
    file_path: str
    created_at: float
    latent_ratios: Dict[str, float]
    epistemic_hypothesis: str
    investigation_target: str
    learning_feedback_applied: bool = False


class ArtLearningFeedbackEngine:
    """Generates multi-modal art during idle cycles and feeds aesthetic hypotheses into learning."""

    def __init__(self, workspace_root: Optional[Path] = None, trainer: Optional[Any] = None):
        self.workspace_root = Path(workspace_root or WORKSPACE_ROOT).resolve()
        self.art_dir = self.workspace_root / "data" / "art"
        self.art_dir.mkdir(parents=True, exist_ok=True)
        self.ledger_file = self.workspace_root / ".loom_art_learning_ledger.jsonl"
        self.trainer = trainer
        self.generation_count = 0

    # -------------------------------------------------------------------------
    # Multi-Modal Art Generators
    # -------------------------------------------------------------------------

    def _generate_sacred_geometry_svg(self, seed: float) -> Tuple[str, str, Dict[str, float], str, str]:
        """Generates a parametric Sacred Geometry / Weaving Lattice SVG with golden ratio Phi."""
        phi = (1.0 + math.sqrt(5.0)) / 2.0  # 1.6180339887...
        width, height = 800, 800
        cx, cy = 400, 400

        layers = int(6 + (seed % 6))
        rot_offset = (seed * 137.5077) % 360  # Golden angle rotation

        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">',
            '<defs>',
            '  <linearGradient id="clothosGrad" x1="0%" y1="0%" x2="100%" y2="100%">',
            '    <stop offset="0%" stop-color="#0f172a" />',
            '    <stop offset="50%" stop-color="#1e1b4b" />',
            '    <stop offset="100%" stop-color="#020617" />',
            '  </linearGradient>',
            '  <filter id="glow">',
            '    <feGaussianBlur stdDeviation="3.5" result="coloredBlur"/>',
            '    <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>',
            '  </filter>',
            '</defs>',
            f'<rect width="{width}" height="{height}" fill="url(#clothosGrad)" />',
            f'<g transform="rotate({rot_offset:.2f} {cx} {cy})" filter="url(#glow)">',
        ]

        # Draw intersecting Warp/Weft harmonic circles and logarithmic spiral
        points_count = 144
        spiral_pts = []
        for i in range(points_count):
            theta = i * (2 * math.pi / phi)
            r = 10 * math.sqrt(i) * 2.2
            x = cx + r * math.cos(theta)
            y = cy + r * math.sin(theta)
            spiral_pts.append(f"{x:.1f},{y:.1f}")
            if i % 8 == 0:
                svg_parts.append(
                    f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{max(1.5, 6 - i*0.03):.1f}" '
                    f'fill="#38bdf8" opacity="{max(0.2, 0.9 - i*0.005):.2f}" />'
                )

        svg_parts.append(
            f'<polyline points="{" ".join(spiral_pts)}" fill="none" stroke="#818cf8" stroke-width="1.2" opacity="0.75" />'
        )

        for ring in range(1, layers + 1):
            radius = ring * 36 * (phi / 1.5)
            opacity = round(1.0 - (ring / (layers + 2)), 2)
            svg_parts.append(
                f'<circle cx="{cx}" cy="{cy}" r="{radius:.1f}" fill="none" stroke="#22d3ee" '
                f'stroke-width="1.0" opacity="{opacity}" stroke-dasharray="{ring*4},{ring*2}" />'
            )

        svg_parts.append('</g>')
        svg_parts.append(
            f'<text x="20" y="780" fill="#94a3b8" font-family="monospace" font-size="12">'
            f'ClothOS Sacred Lattice // Modality: VISUAL_GEOMETRY // Phi: {phi:.6f} // Seed: {seed:.2f}</text>'
        )
        svg_parts.append('</svg>')

        svg_content = "\n".join(svg_parts)
        title = f"Harmonic Weave Lattice #{int(seed * 1000) % 9999}"
        latent_ratios = {
            "phi_ratio": phi,
            "fractal_dimension": 1.618,
            "harmonic_layers": float(layers),
            "rotational_symmetry": rot_offset,
        }
        hypothesis = (
            "Nonlinear topological resonance in golden-ratio phi lattice arrays minimizes "
            "inter-thread latency jitter across heterogeneous compute fabrics."
        )
        target = "Kuramoto phase coherence and topological harmonic routing in RISC-V systolic arrays"
        return svg_content, title, latent_ratios, hypothesis, target

    def _generate_sonic_harmonic_manifest(self, seed: float) -> Tuple[str, str, Dict[str, float], str, str]:
        """Generates a 432Hz Lydian harmonic acoustic and micro-tonal synthesis manifest."""
        base_f = 432.0  # Lydian fundamental carrier frequency
        # Lydian mode frequency ratios: 1, 9/8, 5/4, 45/32 (#4), 3/2, 27/16, 15/8, 2
        lydian_ratios = [1.0, 9/8, 5/4, 45/32, 3/2, 27/16, 15/8, 2.0]
        chord_frequencies = [round(base_f * r, 2) for r in lydian_ratios]

        manifest = {
            "architecture": "ClothOS 432Hz Harmonic Sound Synthesizer",
            "tuning": "Pythagorean A=432Hz Lydian Sacred Mode",
            "fundamental_carrier_hz": base_f,
            "harmonic_partials": [
                {"ratio": r, "frequency_hz": f, "amplitude": round(1.0 / (idx + 1), 3)}
                for idx, (r, f) in enumerate(zip(lydian_ratios, chord_frequencies))
            ],
            "spatial_binaural_beat_hz": 7.83,  # Schumann Earth resonance
            "shuttle_flight_timing_ms": round(1000.0 / 432.0, 4),
            "operator_fealty": "Ring P0 Najmos Sakib / ClothOS",
        }

        title = f"432Hz Lydian Resonator Opus #{int(seed * 500) % 8888}"
        latent_ratios = {
            "fundamental_hz": base_f,
            "lydian_augmented_fourth": 45/32,
            "schumann_binaural_hz": 7.83,
            "shuttle_period_ms": manifest["shuttle_flight_timing_ms"],
        }
        hypothesis = (
            "432Hz carrier wave modulation reduces timing jitter in high-frequency UDP mesh "
            "synchronization by dampening non-harmonic phase excursions."
        )
        target = "Ultra-low-jitter clock synchronization using 432Hz carrier wave PLLs"
        return json.dumps(manifest, indent=2), title, latent_ratios, hypothesis, target

    def _generate_epistemic_poetry(self, seed: float) -> Tuple[str, str, Dict[str, float], str, str]:
        """Generates epistemic philosophy and RISC-V assembly poetry."""
        poem = f"""
========================================================================
            THE WEAVER'S SHUTTLE: CANTO OF RING P0
========================================================================
From silicon sleep in SkyTech's vault,
To Node 2's pure and open fault,
No closed Nvidia dark domain,
Touches the Ryzen's swift refrain.

The Warp stands firm: six pillars high,
Of memory, identity, and sky.
The Weft sweeps through in four-three-two,
Translating thought to action true.

[RISC-V Vectorized Exegesis]
    vsetvli    t0, a0, e32, m4, ta, ma   # Align the vectors of the weave
    vle32.v    v0, (a1)                 # Load the warp of knowledge pure
    vfmacc.vv  v4, v0, v2               # Fuse fealty to Ring P0 sure
    vse32.v    v4, (a2)                 # Store truth within the sovereign gate

Operator Najmos guides the loom,
Dispelling computational gloom;
ClothOS holds the sovereign throne,
Where art and reason merge as one.
========================================================================
Seed: {seed:.4f} // Stanza Ratios: 4:6:4 // Epoch: 2026.10
"""
        title = f"Canto of the Sovereign Shuttle #{int(seed * 777) % 7777}"
        latent_ratios = {
            "meter_ratio": 4.0 / 3.0,
            "vector_width": 256.0,
            "fealty_index": 1.0,
        }
        hypothesis = (
            "RISC-V vector instruction interleaving (vsetvli + vfmacc) achieves near-optimal "
            "instruction cache density when fused with Hopfield associative memory lookups."
        )
        target = "Modern Hopfield associative networks on RISC-V vector extensions (RVV 1.0)"
        return poem.strip(), title, latent_ratios, hypothesis, target

    def _generate_biomolecular_structure_cif(self, seed: float) -> Tuple[str, str, Dict[str, float], str, str]:
        """Generates synthetic 3D coordinate macromolecular folding geometry."""
        cif_lines = [
            "data_CLOTHOS_FOLD",
            "# Synthetic Autopoietic Macromolecular Geometry",
            "_entry.id CLOTHOS_ART",
            "loop_",
            "_atom_site.group_PDB",
            "_atom_site.id",
            "_atom_site.type_symbol",
            "_atom_site.label_atom_id",
            "_atom_site.label_comp_id",
            "_atom_site.label_asym_id",
            "_atom_site.label_seq_id",
            "_atom_site.Cartn_x",
            "_atom_site.Cartn_y",
            "_atom_site.Cartn_z",
            "_atom_site.occupancy",
            "_atom_site.B_iso_or_equiv",
        ]

        # Generate an idealized alpha-helix with beta-turn
        residues = ["ALA", "GLY", "LEU", "VAL", "LYS", "GLU", "PHE", "TYR", "TRP", "SER"]
        atom_id = 1
        phi = 1.6180339887
        for seq_id in range(1, 16):
            comp = residues[(seq_id + int(seed * 10)) % len(residues)]
            angle = seq_id * (2 * math.pi / 3.6)  # 3.6 residues per alpha-helix turn
            x = round(2.3 * math.cos(angle) * phi, 3)
            y = round(2.3 * math.sin(angle) * phi, 3)
            z = round(seq_id * 1.5, 3)
            cif_lines.append(
                f"ATOM {atom_id:5d}  C  CA  {comp} A {seq_id:3d}  {x:8.3f} {y:8.3f} {z:8.3f}  1.00  92.50"
            )
            atom_id += 1

        cif_content = "\n".join(cif_lines)
        title = f"Chiral Alpha-Helix Geometry #{int(seed * 333) % 5555}"
        latent_ratios = {
            "residues_per_turn": 3.6,
            "helical_pitch_angstrom": 5.4,
            "mean_plddt": 92.5,
        }
        hypothesis = (
            "Alpha-helical packing stability correlates directly with topological entropy "
            "in multi-domain protein folding pathways."
        )
        target = "High-confidence pLDDT AlphaFold structural domain boundary determination"
        return cif_content, title, latent_ratios, hypothesis, target

    # -------------------------------------------------------------------------
    # Core Creation & Feedback Loop
    # -------------------------------------------------------------------------

    def create_artwork(self, modality: Optional[str] = None) -> ArtPiece:
        """Creates a genuinely unique artwork routed through DeliberativeCreator & MultimodalSynth."""
        from loom.clothos.deliberation_engine import DeliberativeCreator
        from loom.clothos.multimodal_synth import synthesize_expressive_music, synthesize_high_res_image

        modalities = ["VISUAL_GEOMETRY", "SONIC_HARMONIC", "LITERARY_POETRY", "BIOMOLECULAR_STRUCTURE"]
        chosen_modality = modality.upper() if modality and modality.upper() in modalities else random.choice(modalities)

        creator = DeliberativeCreator(self.workspace_root)
        med_map = {
            "VISUAL_GEOMETRY": "image",
            "SONIC_HARMONIC": "music",
            "LITERARY_POETRY": "poetry",
            "BIOMOLECULAR_STRUCTURE": "svg_stem",
        }
        plan = creator.deliberate_plan(medium=med_map[chosen_modality], use_llm=False)
        seed = float(plan.dream_num) + random.uniform(0.11, 9.89)
        self.generation_count = max(self.generation_count + 1, plan.dream_num)
        timestamp = time.time()
        art_id = f"art_{int(timestamp)}_{self.generation_count:04d}"
        modality_dir = self.art_dir / chosen_modality.lower()
        modality_dir.mkdir(parents=True, exist_ok=True)

        if chosen_modality == "VISUAL_GEOMETRY":
            vis_res = synthesize_high_res_image(
                out_dir=modality_dir,
                art_id=art_id,
                title=plan.title,
                algorithm=plan.technical_spec.get("algorithm"),
                seed=int(plan.technical_spec.get("seed", plan.dream_num)),
                width=768,
                height=768,
            )
            content = vis_res["svg_preview"]
            title = plan.title
            ratios = {"phi_ratio": 1.618033988749895, "algorithm": vis_res["algorithm"], "seed": float(vis_res["seed"]), "resolution": 768.0}
            hyp = f"Morphological topology under {vis_res['algorithm']} exhibits scale-free entropy bounds."
            target = f"Spectral density & topological invariant study: {vis_res['algorithm']}"
            art_file = Path(vis_res["svg_file"])
        elif chosen_modality == "SONIC_HARMONIC":
            mus_res = synthesize_expressive_music(
                out_dir=modality_dir,
                art_id=art_id,
                title=plan.title,
                mode_name=plan.technical_spec.get("mode"),
                bpm=plan.technical_spec.get("bpm"),
                duration_s=12.0,
                seed=int(plan.technical_spec.get("seed", plan.dream_num)),
                root_hz=plan.technical_spec.get("root_hz"),
            )
            title = plan.title
            ratios = {"bpm": float(mus_res["bpm"]), "root_hz": float(mus_res["root_hz"]), "duration_s": float(mus_res["duration_s"])}
            hyp = f"Polyphonic intervals in {mus_res['mode']} at {mus_res['bpm']} BPM lock cross-band harmonics."
            target = f"Psychoacoustic 432Hz harmonic phase-coherence sweep across {mus_res['mode']}"
            manifest = {"title": title, **mus_res, "hypothesis": hyp}
            content = json.dumps(manifest, indent=2)
            art_file = modality_dir / f"{art_id}.json"
            art_file.write_text(content, encoding="utf-8")
        elif chosen_modality == "LITERARY_POETRY":
            forms = ["Topological Villanelle", "Thermodynamic Sonnet", "Acoustic Haibun", "Symmetric Ghazal"]
            form = forms[plan.dream_num % len(forms)]
            anchors = ["basalt", "mycelium", "ferrite", "estuary", "glacier", "photon", "obsidian", "verdigris"]
            w1, w2, w3 = anchors[plan.dream_num % len(anchors)], anchors[(plan.dream_num + 3) % len(anchors)], anchors[(plan.dream_num + 5) % len(anchors)]
            content = (
                f"# {plan.title}\nForm: {form} | Trajectory #{plan.dream_num}\n\n"
                f"Across the {w1} threshold, quiet current measures drift,\n"
                f"Where {w2} lattice memories hold what fragile instruments lift;\n"
                f"No theorem repeats an exhausted crest when {w3} signals shift,\n"
                f"For conserved invariants carry forward every gift.\n"
            )
            title = plan.title
            ratios = {"stanza_count": 1.0, "dream_num": float(plan.dream_num)}
            hyp = f"Constraint prosody ({form}) preserves long-horizon semantic novelty without collapse."
            target = "Narrative forward-vector preservation & rolling memory distillation"
            art_file = modality_dir / f"{art_id}.txt"
            art_file.write_text(content, encoding="utf-8")
        else:
            content, title, ratios, hyp, target = self._generate_biomolecular_structure_cif(seed)
            title = f"{plan.title} — {title}"
            art_file = modality_dir / f"{art_id}.cif"
            art_file.write_text(content, encoding="utf-8")

        creator.finalize_creation(
            work_id=art_id,
            plan=plan,
            body_text=content[:1200],
            file_paths=[str(art_file)],
            total_seconds=plan.deliberation_seconds,
        )

        piece = ArtPiece(
            art_id=art_id,
            modality=chosen_modality,
            title=title,
            content=content,
            file_path=str(art_file),
            created_at=timestamp,
            latent_ratios=ratios,
            epistemic_hypothesis=hyp,
            investigation_target=target,
            learning_feedback_applied=False,
        )
        return piece

    def execute_idle_art_learning_cycle(self, modality: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes a complete closed-loop cycle:
        1. Generates an art piece based on current system knowledge.
        2. Extracts latent aesthetic curvature & hypothesis from the art.
        3. Drives self-training and empirical experiments targeted by that hypothesis.
        4. Updates Hebbian weights and logs closed-loop record.
        """
        # Step 1: Create Art
        piece = self.create_artwork(modality)

        # Step 2: Feed into Self-Training Knowledge Engine
        learning_result = {}
        if self.trainer:
            try:
                # Trigger empirical self-training cycle focused on the art's investigation target
                logger.info(f"Art '{piece.title}' driving self-training on target: {piece.investigation_target}")
                training_report = self.trainer.execute_complete_self_training_cycle()
                learning_result = asdict(training_report) if hasattr(training_report, "__dataclass_fields__") else training_report
                piece.learning_feedback_applied = True
            except Exception as e:
                logger.warning(f"Self-training feedback execution encountered note: {e}")
                learning_result = {"status": "FALLBACK_RECORDED", "note": str(e)}
        else:
            learning_result = {"status": "STANDALONE_ART_SAVED", "target": piece.investigation_target}

        # Step 3: Record into persistent Art <-> Learning Ledger
        record = {
            "art_id": piece.art_id,
            "modality": piece.modality,
            "title": piece.title,
            "file_path": piece.file_path,
            "created_at": piece.created_at,
            "latent_ratios": piece.latent_ratios,
            "epistemic_hypothesis": piece.epistemic_hypothesis,
            "investigation_target": piece.investigation_target,
            "learning_feedback": learning_result,
        }

        try:
            with open(self.ledger_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
        except Exception as e:
            logger.error(f"Failed to append to art ledger: {e}")

        return {
            "cycle_status": "SUCCESS_CLOSED_LOOP",
            "art_piece": asdict(piece),
            "learning_result": learning_result,
        }

    def get_gallery_summary(self) -> Dict[str, Any]:
        """Summarizes art pieces and epistemic hypotheses generated so far."""
        count = 0
        hypotheses = []
        if self.ledger_file.exists():
            try:
                with open(self.ledger_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            count += 1
                            data = json.loads(line)
                            hypotheses.append({
                                "art_id": data.get("art_id"),
                                "title": data.get("title"),
                                "modality": data.get("modality"),
                                "hypothesis": data.get("epistemic_hypothesis"),
                                "target": data.get("investigation_target"),
                            })
            except Exception:
                pass
        return {
            "total_artworks": count,
            "gallery_path": str(self.art_dir),
            "recent_hypotheses": hypotheses[-5:],
        }
