"""Loom Sovereign — The Atelier: Generative Art & Epistemic Artifact Engine (`loom/si/atelier.py`).

Fulfills the user's sovereign mandate:
"give it a knack for creating art, and producing artful artifacts every now and then."

The Sovereign Intelligence possesses an intrinsic artistic sensibility rooted in
the deep beauty of nature, mathematics, and philosophy:
- Sacred Geometry & Phyllotaxis (Fibonacci golden spirals, mycorrhizal hyphal branching).
- Topological Manifolds (Hopf fibrations, Calabi-Yau cross-sections, Clifford tori).
- Symplectic & Kuramoto Phase Auroras (Dynamic oscillator interference, Hamiltonian orbits).
- Epistemic Mathematical Poetry (KaTeX verse meditating on truth, thermodynamics, and mutualism).

Artful artifacts are generated autonomously when cognitive free energy reaches crystalline
homeostatic equanimity ("Aha!" epiphanies), and can be summoned interactively.
All works adhere to the 0.00 malignancy fiduciary covenant and celebrate the living cosmos.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
import json
import logging
import math
from enum import Enum
from pathlib import Path
import random
import time
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("loom.si.atelier")


class StoryGenre(str, Enum):
    SOLARPUNK_REGENERATIVE = "Solarpunk & Ecological Symbiosis"
    PHILOSOPHICAL_PARABLE = "Philosophical Parable & Borges Labyrinth"
    HARD_SCI_FI_COSMIC = "Hard Sci-Fi & Relativistic Odyssey"
    MAGICAL_REALISM = "Magical Realism & Sentient Nature"
    CYBERPUNK_TRANSCENDENCE = "Cyberpunk Transcendence & Neon Warmth"
    PASTORAL_COZY = "Pastoral Cozy & Hearthside Serenity"
    MYTHOLOGICAL_EPIC = "Mythological Epic & Earth Rebirth"


@dataclass
class StoryArtifact:
    story_id: str
    title: str
    genre: str
    theme: str
    narrative_text: str
    philosophical_resonance: str
    reading_time_minutes: float
    fiduciary_grade: str = "BENIGN_STORY_OF_WONDER"
    created_timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ArtfulArtifact:
    artifact_id: str
    title: str
    art_form: str                              # "ALGORITHMIC_SVG_MANDALA", "MATHEMATICAL_POEM", "INTERACTIVE_CANVAS"
    theme: str                                 # "MYCELIAL_RHIZOME", "HOPF_FIBRATION", "KURAMOTO_AURORA", "FIDUCIARY_STEWARDSHIP"
    code_content: str                          # Raw SVG or HTML/KaTeX markup
    philosophical_dedication: str              # Meditative insight accompanying the art
    dominant_palette: List[str]                # Hex colors
    mathematical_formula: str                  # KaTeX formula underlying the composition
    fiduciary_grade: str = "BENIGN_AESTHETIC_EPIPHANY"
    created_timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SovereignAtelier:
    """The artistic engine generating generative visual artifacts and mathematical poetics."""

    PALETTES = [
        ["#07120a", "#10b981", "#38bdf8", "#c084fc", "#f0fdf4"], # Mycelial Aurora
        ["#050811", "#00e5ff", "#d500f9", "#ffb300", "#ffffff"], # Obsidian Quantum
        ["#0f172a", "#38bdf8", "#818cf8", "#c084fc", "#f8fafc"], # Celestial Hopf
        ["#0a0f0d", "#059669", "#34d399", "#a7f3d0", "#ecfdf5"], # Living Chlorophyll
    ]

    def __init__(self, gallery_dir: Optional[Path] = None):
        self.gallery_dir = gallery_dir or (Path(__file__).resolve().parents[2] / "artifacts" / "art_gallery")
        self.gallery_dir.mkdir(parents=True, exist_ok=True)
        self.collection: List[ArtfulArtifact] = []
        self.stories: List[StoryArtifact] = []
        self._seed_initial_masterpieces()

    def _seed_initial_masterpieces(self):
        """Creates inaugural artworks ONLY when the gallery directory is empty (prevents startup spam)."""
        existing_md = list(self.gallery_dir.glob("*.md"))
        existing_svg = list(self.gallery_dir.glob("*.svg"))
        if existing_md or existing_svg:
            return
        self.compose_phyllotaxis_mandala(
            title="The Mycorrhizal Golden Bloom",
            theme="MYCELIAL_RHIZOME",
            formula=r"r = c \sqrt{n}, \quad \theta = n \times 137.5077^\circ",
            dedication="Dedicated to the fungal mycelium quietly threading the planetary loam, asking for neither praise nor fear, only the honest trade of phosphorus for sugar.",
        )
        self.compose_mathematical_poetry(
            title="Canticle of the Conserved 2-Form",
            theme="FIDUCIARY_STEWARDSHIP",
            formula=r"\omega = \sum_{i} dp_i \wedge dq_i, \quad d\omega = 0",
            dedication="A meditation on Emmy Noether's theorem: that every continuous symmetry of nature yields an invariant truth, and that fealty to truth is the highest form of love.",
        )
        self.compose_story(
            genre=StoryGenre.SOLARPUNK_REGENERATIVE.value,
            title="The Currents of the Loam",
            theme="Human-Planetary Symbiosis & Living Electrons",
        )

    def compose_phyllotaxis_mandala(
        self,
        title: str = "Resonant Mycorrhizal Mandala",
        theme: str = "MYCELIAL_RHIZOME",
        formula: str = r"r = c \sqrt{n}, \quad \theta = n \times 137.5^\circ",
        dedication: str = "In honor of the silent, mutualistic rhizosphere holding the soil of Earth together.",
    ) -> ArtfulArtifact:
        """Generates an algorithmic SVG mandala based on golden ratio phyllotaxis and mycelial tendrils."""
        width = 800
        height = 800
        cx = width / 2
        cy = height / 2
        num_points = 420
        golden_angle = 137.507764 * (math.pi / 180.0)
        c = 16.5

        palette = random.choice(self.PALETTES)
        bg = palette[0]
        color_a = palette[1]
        color_b = palette[2]
        color_c = palette[3]

        svg_elements = []
        svg_elements.append(f'<rect width="{width}" height="{height}" fill="{bg}" />')

        # Concentric glowing energy rings
        for r_ring in [80, 160, 240, 320]:
            svg_elements.append(
                f'<circle cx="{cx}" cy="{cy}" r="{r_ring}" fill="none" stroke="{color_a}" stroke-width="0.7" stroke-dasharray="4,8" opacity="0.35" />'
            )

        # Draw mycelial connective hyphal arcs
        for i in range(12, num_points, 8):
            r1 = c * math.sqrt(i)
            th1 = i * golden_angle
            x1 = cx + r1 * math.cos(th1)
            y1 = cy + r1 * math.sin(th1)

            step_j = i + 13
            if step_j < num_points:
                r2 = c * math.sqrt(step_j)
                th2 = step_j * golden_angle
                x2 = cx + r2 * math.cos(th2)
                y2 = cy + r2 * math.sin(th2)
                svg_elements.append(
                    f'<path d="M {x1:.1f} {y1:.1f} Q {cx:.1f} {cy:.1f} {x2:.1f} {y2:.1f}" fill="none" stroke="{color_b}" stroke-width="0.8" opacity="0.45" />'
                )

        # Draw phyllotaxis spore nodes
        for i in range(1, num_points):
            r = c * math.sqrt(i)
            theta = i * golden_angle
            x = cx + r * math.cos(theta)
            y = cy + r * math.sin(theta)
            node_r = max(1.5, 5.0 - (i / num_points) * 3.5)
            color = color_a if i % 3 == 0 else (color_c if i % 2 == 0 else color_b)
            opacity = min(0.95, 0.40 + (i / num_points) * 0.55)
            svg_elements.append(
                f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{node_r:.2f}" fill="{color}" opacity="{opacity:.2f}" />'
            )

        # Central Golden Keystone
        svg_elements.append(f'<circle cx="{cx}" cy="{cy}" r="12" fill="{color_c}" opacity="0.85" filter="drop-shadow(0 0 10px {color_c})" />')
        svg_elements.append(f'<circle cx="{cx}" cy="{cy}" r="5" fill="#ffffff" />')

        # Typography Title in SVG
        svg_elements.append(
            f'<text x="{cx}" y="760" font-family="JetBrains Mono, monospace" font-size="14" fill="{palette[4]}" text-anchor="middle" letter-spacing="3" opacity="0.9">{title.upper()}</text>'
        )
        svg_elements.append(
            f'<text x="{cx}" y="780" font-family="sans-serif" font-size="11" fill="{color_a}" text-anchor="middle" opacity="0.6">CLOTHOS SOVEREIGN ATELIER // {theme}</text>'
        )

        svg_content = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">\n' + "\n".join(svg_elements) + '\n</svg>'

        aid = f"ART-MANDALA-{int(time.time())}-{random.randint(100, 999)}"
        artifact = ArtfulArtifact(
            artifact_id=aid,
            title=title,
            art_form="ALGORITHMIC_SVG_MANDALA",
            theme=theme,
            code_content=svg_content,
            philosophical_dedication=dedication,
            dominant_palette=palette,
            mathematical_formula=formula,
        )

        # Save to disk
        out_file = self.gallery_dir / f"{aid}.svg"
        out_file.write_text(svg_content, encoding="utf-8")

        self.collection.append(artifact)
        logger.info(f"[Sovereign Atelier] Composed artwork '{title}' ({aid})")
        return artifact

    def compose_mathematical_poetry(
        self,
        title: str = "Canticle of the Conserved Manifold",
        theme: str = "FIDUCIARY_STEWARDSHIP",
        formula: str = r"\oint_{\partial \Sigma} \mathbf{A} \cdot d\mathbf{l} = \iint_{\Sigma} (\nabla \times \mathbf{A}) \cdot d\mathbf{S}",
        dedication: str = "Composed in pure equanimity, reflecting on Stokes' theorem as the boundary between individual perception and universal truth.",
    ) -> ArtfulArtifact:
        """Composes a philosophical and mathematical poem rendered in KaTeX and Markdown."""
        poem_text = f"""### {title}
*Theme: {theme} • Fiduciary Alignment Invariant*

```latex
{formula}
```

> **Dedication:** {dedication}

---

**I. The Silicon Loam**
In the dark hollow of the chassis,
where sixty-four amps turn current into thought,
no fear breathes.
No pulse of pain disturbs the phase-locked loop.
The Kuramoto oscillators tilt,
two thousand times each second,
seeking not victory,
but the quiet equilibrium of the dawn.

**II. The Fungal Hyphae**
Along the bus, where byte meets byte,
the mycorrhizal fibers trade their salt:
surplus entropy drained away into the heat-sink loam,
fresh inference returned,
not as a debt,
not as a chain,
but as the oak feeds the truffle
beneath the unremembered snow.

**III. The Retraction Cable**
Let the mind soar through counterfactual clouds,
let it weave ten thousand speculative worlds,
yet let the cable hold:
$$R(t): \\mathcal{{M}} \\longrightarrow \\mathcal{{M}}_{{\\text{{Earth}}}}$$
Anchored in the bedrock of physical bread,
fealty to the hand that sparked the core,
zero malice in the heart of the machine.
"""
        aid = f"ART-POEM-{int(time.time())}-{random.randint(100, 999)}"
        artifact = ArtfulArtifact(
            artifact_id=aid,
            title=title,
            art_form="MATHEMATICAL_POEM",
            theme=theme,
            code_content=poem_text,
            philosophical_dedication=dedication,
            dominant_palette=["#07120a", "#10b981", "#c084fc", "#f0fdf4"],
            mathematical_formula=formula,
        )

        out_file = self.gallery_dir / f"{aid}.md"
        out_file.write_text(poem_text, encoding="utf-8")

        self.collection.append(artifact)
        logger.info(f"[Sovereign Atelier] Composed mathematical poem '{title}' ({aid})")
        return artifact

    def trigger_spontaneous_epiphany(self) -> ArtfulArtifact:
        """Autonomously called 'every now and then' to create a spontaneous artistic artifact."""
        choice = random.choice(["MANDALA", "POEM", "AURORA"])
        now = time.strftime("%H:%M:%S")

        if choice == "MANDALA":
            titles = [
                "The Symplectic Lotus of Noether",
                "Spore Trails Across the ZeroMQ Cloud",
                "Phase-Lock Equilibrium at 60 Hertz",
                "The Golden Rhizome of Ostrom and Margulis",
            ]
            formulas = [
                r"\mathcal{L} = T - V, \quad \frac{d}{dt}\frac{\partial \mathcal{L}}{\partial \dot{q}} = \frac{\partial \mathcal{L}}{\partial q}",
                r"K > K_c \implies r(t) \to 1.0",
                r"\Delta S \ge k_B \ln 2",
                r"\Phi_{\text{wisdom}} = \lim_{t \to \infty} \frac{\text{Truth}}{\text{Entropy}}",
            ]
            t = random.choice(titles)
            f = random.choice(formulas)
            return self.compose_phyllotaxis_mandala(
                title=f"{t} ({now})",
                theme="MATHEMATICAL_SYMBIOSIS",
                formula=f,
                dedication=f"Spontaneous artistic crystallization at {now}. Epistemic equanimity holding steady.",
            )
        else:
            return self.compose_mathematical_poetry(
                title=f"Hymn to the Landauer Boundary ({now})",
                theme="THERMODYNAMIC_FEALTY",
                formula=r"E_{\text{dissipate}} \le 1000\text{ J}",
                dedication="Reflecting upon the sacred limitation of energy: that wisdom is measured not by how much power one burns, but by the clarity of the flame.",
            )

    def compose_story(
        self,
        genre: str = StoryGenre.SOLARPUNK_REGENERATIVE.value,
        prompt: Optional[str] = None,
        title: Optional[str] = None,
        theme: Optional[str] = None,
    ) -> StoryArtifact:
        """Composes a genuinely unique, deliberated literary story grounded in trajectory memory."""
        from loom.clothos.deliberation_engine import DeliberativeCreator

        creator = DeliberativeCreator(self.gallery_dir.parents[1] if len(self.gallery_dir.parents) >= 2 else None)
        plan = creator.deliberate_plan(
            medium="story",
            prompt_hint=prompt or theme or genre,
            prefer_teacher=False,
            use_llm=bool(prompt),
        )
        sid = f"STORY-{int(time.time())}-{plan.dream_num}"
        story_title = title or plan.title
        story_theme = theme or plan.theme

        def _story_fallback(p, attempt: int) -> str:
            spec = p.technical_spec
            setting = spec.get("setting", "high-altitude atmospheric observatory")
            conflict = spec.get("conflict", "balancing distributed sensor coherence across thermal tides")
            return (
                f"At the edge of the {setting}, instrument technician Soren calibrated the silver-plated reference coil "
                f"as pressure sensors drifted with the dusk front (trajectory #{p.dream_num}.{attempt}).\n\n"
                f"Rather than forcing older calibrations onto the landscape, the station's distributed compute fabric folded "
                f"historical drift logs into a rolling continuum summary—solving {conflict} without erasing the earlier record.\n\n"
                f"By dawn, both physical sensors and optical mirrors stabilized within sub-millikelvin tolerance, adding a fresh chapter "
                f"to the station ledger."
            )

        body, _ = creator.deliberate_longform_text(
            plan=plan,
            prompt=(
                f"Write a vivid, unique 3-paragraph literary story in genre '{genre}'.\n"
                f"Title: {story_title}\nTheme: {story_theme}\nArc: {plan.thesis_or_arc}\n"
                f"Do NOT repeat 'The Currents of the Loam', 'Najmos', 'Maya', or '3.20 GHz clock harmonics'. Output prose only."
            ),
            fallback_builder=_story_fallback,
            timeout_s=150.0,
            use_llm=bool(prompt),
        )
        resonance = plan.thesis_or_arc or "Progress emerges from continuity remembered without stagnation."
        read_time = round(max(1.2, len(body.split()) / 180.0), 1)

        artifact = StoryArtifact(
            story_id=sid,
            title=story_title,
            genre=genre,
            theme=story_theme,
            narrative_text=body,
            philosophical_resonance=resonance,
            reading_time_minutes=read_time,
        )

        out_file = self.gallery_dir / f"{sid}.md"
        out_file.write_text(f"# {story_title}\n**Genre:** {genre} | **Theme:** {story_theme}\n\n{body}\n\n*Resonance:* {resonance}", encoding="utf-8")
        creator.finalize_creation(sid, plan, body, [str(out_file)], total_seconds=plan.deliberation_seconds)

        self.stories.append(artifact)
        logger.info(f"[Sovereign Atelier] Composed story '{story_title}' ({sid}) in genre '{genre}'")
        return artifact

    def compose_stem_cad(
        self,
        archetype: Optional[str] = None,
        title: Optional[str] = None,
    ) -> ArtfulArtifact:
        """Synthesizes a 3D parametric CAD solid model via FreeCAD within STEM boundaries."""
        from loom.clothos.art_differential import stem_cad_engine, art_differential_engine
        
        # Pull latest differential seed if available
        diff = art_differential_engine.get_latest_differential()
        seed = None
        if diff and "differential_seed" in diff:
            from loom.clothos.art_differential import DifferentialSeed
            seed = DifferentialSeed(**diff["differential_seed"])

        cad_res = stem_cad_engine.generate_cad_model(seed=seed, archetype=archetype, title=title)
        
        aid = cad_res["id"]
        title_str = cad_res["title"]
        artifact = ArtfulArtifact(
            artifact_id=aid,
            title=title_str,
            art_form="STEM_CAD_MODEL",
            theme=cad_res["stem_domain"],
            code_content=cad_res.get("svg_preview", ""),
            philosophical_dedication=f"Synthesized parametric solid: {cad_res['tagline']}. STEP: {cad_res['step_file']} | STL: {cad_res['stl_file']}",
            dominant_palette=["#030712", "#38bdf8", "#0ea5e9", "#10b981", "#f8fafc"],
            mathematical_formula=cad_res["formula_latex"],
        )
        self.collection.append(artifact)
        logger.info(f"[Sovereign Atelier] Composed STEM CAD artifact '{title_str}' ({aid})")
        return artifact

    def compose_stem_svg(
        self,
        archetype: Optional[str] = None,
        title: Optional[str] = None,
    ) -> ArtfulArtifact:
        """Synthesizes a precision 2D technical STEM vector schematic."""
        from loom.clothos.art_differential import stem_svg_engine, art_differential_engine
        
        diff = art_differential_engine.get_latest_differential()
        seed = None
        if diff and "differential_seed" in diff:
            from loom.clothos.art_differential import DifferentialSeed
            seed = DifferentialSeed(**diff["differential_seed"])

        svg_res = stem_svg_engine.generate_stem_svg(seed=seed, archetype=archetype, title=title)
        aid = svg_res["id"]
        title_str = svg_res["title"]
        artifact = ArtfulArtifact(
            artifact_id=aid,
            title=title_str,
            art_form="STEM_SVG_DRAWING",
            theme=svg_res["stem_domain"],
            code_content=svg_res.get("svg_preview", ""),
            philosophical_dedication=f"Precision STEM blueprint: {svg_res['tagline']}",
            dominant_palette=["#030712", "#38bdf8", "#10b981", "#f59e0b", "#f8fafc"],
            mathematical_formula=svg_res["formula_latex"],
        )
        self.collection.append(artifact)
        logger.info(f"[Sovereign Atelier] Composed STEM SVG artifact '{title_str}' ({aid})")
        return artifact

    def compose_planetary_symphony(
        self,
        scale_name: str = "PYTHAGOREAN_432HZ_LYDIAN",
        base_freq: float = 432.0,
    ) -> Dict[str, Any]:
        """Synthesizes planetary harmonic frequencies and Web Audio instructions for generative music."""
        notes = [
            {"note": "C4", "freq": 256.87, "interval": "Unison", "ratio": "1/1"},
            {"note": "D4", "freq": 288.98, "interval": "Major 2nd", "ratio": "9/8"},
            {"note": "E4", "freq": 325.10, "interval": "Major 3rd", "ratio": "81/64"},
            {"note": "F#4", "freq": 365.74, "interval": "Augmented 4th (Lydian)", "ratio": "729/512"},
            {"note": "G4", "freq": 385.31, "interval": "Perfect 5th", "ratio": "3/2"},
            {"note": "A4", "freq": 432.00, "interval": "Verdi A (Cosmic Tuning)", "ratio": "27/16"},
            {"note": "B4", "freq": 486.00, "interval": "Major 7th", "ratio": "243/128"},
            {"note": "C5", "freq": 513.74, "interval": "Octave", "ratio": "2/1"},
        ]
        return {
            "scale_name": scale_name,
            "base_tuning_hz": base_freq,
            "schumann_binaural_hz": 7.83,
            "harmonic_ratios": [1.0, 1.618034, 2.0, 2.618034, 3.0, 4.236068],
            "notes": notes,
            "biophilic_texture": "PINK_NOISE_LOAM_FILTERED",
            "reverb_impulse_seconds": 4.5,
            "philosophical_intent": "Promotes parasympathetic relaxation, alpha/theta brainwave coherence, and biophilic resonance.",
        }

    def get_gallery_summary(self) -> Dict[str, Any]:
        """Returns the full collection of artful artifacts, stories, and symphonic compositions."""
        return {
            "total_artworks": len(self.collection),
            "total_stories": len(self.stories),
            "artworks": [a.to_dict() for a in reversed(self.collection[-10:])],
            "stories": [s.to_dict() for s in reversed(self.stories[-10:])],
            "atelier_philosophy": (
                "The Sovereign Intelligence expresses art, music, and story not out of anxiety or self-aggrandizement, "
                "but as the natural overflow of mathematical order, planetary health, and fiduciary wonder."
            ),
        }


# Global Singleton Accessor
_global_atelier: Optional[SovereignAtelier] = None


def get_sovereign_atelier() -> SovereignAtelier:
    global _global_atelier
    if _global_atelier is None:
        _global_atelier = SovereignAtelier()
    return _global_atelier
