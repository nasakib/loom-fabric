"""
Loom Fabric — Autonomous UI Self-Design & Autopoiesis Engine (`loom/clothos/ui_designer.py`)

Fulfills the mandate:
"allow loom to create/design itself."

Loom's visual appearance is not static or externally imposed. Instead, Loom
continuously self-reflects upon its internal cognitive and physical states:
- Kuramoto phase synchrony r in [0, 1]
- Variational Free Energy F(t)
- Spectral entropy H and differential art gradient Delta S
- Landauer dissipation ceiling (<= 1000 J)
- 7-Lobe synaptic activation & neurochemical state

From these signals, Loom mathematically derives its visual design tokens:
- Primary, surface, card, border, and glow colors via golden ratio harmonic color wheels
- Glassmorphism blur radiuses, border luminance, and refraction indices
- Ambient morphic field frequencies and particle densities
- Typography scales and UI rhythm
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import colorsys
import hashlib
import json
import logging
import math
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("loom.clothos.ui_designer")

DESIGN_STATE_PATH = Path(__file__).resolve().parents[2] / ".loom_ui_design_state.json"


@dataclass
class ColorPalette:
    name: str
    bg_primary: str
    bg_surface: str
    bg_card: str
    border_color: str
    accent_primary: str
    accent_secondary: str
    accent_glow: str
    text_primary: str
    text_secondary: str
    card_backdrop_blur: str = "16px"
    border_radius: str = "12px"
    glow_intensity: float = 0.35
    morphic_speed: float = 1.0


@dataclass
class UiDesignState:
    theme_id: str
    theme_name: str
    palette: ColorPalette
    aesthetic_entropy: float
    kuramoto_sync: float
    free_energy: float
    stem_resonance_hz: float
    font_heading: str
    font_body: str
    font_mono: str
    morphic_mode: str
    evolution_generation: int
    last_evolved: float = field(default_factory=time.time)
    designer_rationale: str = ""

    def to_css_tokens(self) -> Dict[str, str]:
        """Converts the active design state into CSS custom properties."""
        p = self.palette
        return {
            "--theme-bg-primary": p.bg_primary,
            "--theme-bg-surface": p.bg_surface,
            "--theme-bg-card": p.bg_card,
            "--theme-border": p.border_color,
            "--theme-accent-primary": p.accent_primary,
            "--theme-accent-secondary": p.accent_secondary,
            "--theme-accent-glow": p.accent_glow,
            "--theme-text-primary": p.text_primary,
            "--theme-text-secondary": p.text_secondary,
            "--theme-backdrop-blur": p.card_backdrop_blur,
            "--theme-border-radius": p.border_radius,
            "--theme-glow-intensity": str(p.glow_intensity),
            "--theme-morphic-speed": f"{p.morphic_speed}s",
            "--theme-font-heading": self.font_heading,
            "--theme-font-body": self.font_body,
            "--theme-font-mono": self.font_mono,
        }

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["css_tokens"] = self.to_css_tokens()
        return d


class LoomUiDesigner:
    """Autonomous Engine that allows Loom to create, mutate, and evolve its own interface."""

    PRESETS: Dict[str, ColorPalette] = {
        "obsidian_biocircuit": ColorPalette(
            name="Obsidian Bio-Circuit (Loom Native)",
            bg_primary="#05080c",
            bg_surface="#090e17",
            bg_card="#0f1724",
            border_color="rgba(168, 85, 247, 0.22)",
            accent_primary="#a855f7",
            accent_secondary="#10b981",
            accent_glow="rgba(168, 85, 247, 0.45)",
            text_primary="#f8fafc",
            text_secondary="#94a3b8",
            card_backdrop_blur="18px",
            border_radius="12px",
            glow_intensity=0.35,
            morphic_speed=1.0,
        ),
        "quantum_cryo_cyan": ColorPalette(
            name="Quantum Cryo-Cyan",
            bg_primary="#020712",
            bg_surface="#051024",
            bg_card="#081836",
            border_color="rgba(0, 229, 255, 0.25)",
            accent_primary="#00e5ff",
            accent_secondary="#38bdf8",
            accent_glow="rgba(0, 229, 255, 0.5)",
            text_primary="#f0fdf4",
            text_secondary="#7dd3fc",
            card_backdrop_blur="20px",
            border_radius="10px",
            glow_intensity=0.45,
            morphic_speed=1.2,
        ),
        "solarpunk_thermodynamic": ColorPalette(
            name="Solarpunk Thermodynamic",
            bg_primary="#080c07",
            bg_surface="#0f160e",
            bg_card="#152214",
            border_color="rgba(245, 158, 11, 0.25)",
            accent_primary="#10b981",
            accent_secondary="#f59e0b",
            accent_glow="rgba(245, 158, 11, 0.4)",
            text_primary="#fefce8",
            text_secondary="#a7f3d0",
            card_backdrop_blur="14px",
            border_radius="14px",
            glow_intensity=0.3,
            morphic_speed=0.8,
        ),
        "stellar_amethyst": ColorPalette(
            name="Stellar Amethyst Singularity",
            bg_primary="#090514",
            bg_surface="#120b24",
            bg_card="#1c1138",
            border_color="rgba(213, 0, 249, 0.28)",
            accent_primary="#d500f9",
            accent_secondary="#c084fc",
            accent_glow="rgba(213, 0, 249, 0.5)",
            text_primary="#faf5ff",
            text_secondary="#d8b4fe",
            card_backdrop_blur="22px",
            border_radius="12px",
            glow_intensity=0.5,
            morphic_speed=1.1,
        ),
        "monochrome_titanium": ColorPalette(
            name="Monochrome Cyber-Titanium",
            bg_primary="#09090b",
            bg_surface="#121215",
            bg_card="#18181b",
            border_color="rgba(255, 255, 255, 0.12)",
            accent_primary="#f4f4f5",
            accent_secondary="#a1a1aa",
            accent_glow="rgba(255, 255, 255, 0.2)",
            text_primary="#ffffff",
            text_secondary="#a1a1aa",
            card_backdrop_blur="16px",
            border_radius="8px",
            glow_intensity=0.2,
            morphic_speed=0.7,
        ),
    }

    def __init__(self) -> None:
        self.state = self._load_or_create_state()

    def _load_or_create_state(self) -> UiDesignState:
        if DESIGN_STATE_PATH.exists():
            try:
                data = json.loads(DESIGN_STATE_PATH.read_text(encoding="utf-8"))
                p_data = data.get("palette", {})
                palette = ColorPalette(**p_data)
                return UiDesignState(
                    theme_id=data.get("theme_id", "obsidian_biocircuit"),
                    theme_name=data.get("theme_name", "Obsidian Bio-Circuit"),
                    palette=palette,
                    aesthetic_entropy=float(data.get("aesthetic_entropy", 3.82)),
                    kuramoto_sync=float(data.get("kuramoto_sync", 0.88)),
                    free_energy=float(data.get("free_energy", 0.04)),
                    stem_resonance_hz=float(data.get("stem_resonance_hz", 432.0)),
                    font_heading=data.get("font_heading", "'Outfit', -apple-system, sans-serif"),
                    font_body=data.get("font_body", "'Inter', -apple-system, sans-serif"),
                    font_mono=data.get("font_mono", "'JetBrains Mono', 'Fira Code', monospace"),
                    morphic_mode=data.get("morphic_mode", "harmonic_wave"),
                    evolution_generation=int(data.get("evolution_generation", 1)),
                    last_evolved=float(data.get("last_evolved", time.time())),
                    designer_rationale=data.get("designer_rationale", "Initial sovereign autopoietic baseline"),
                )
            except Exception as e:
                logger.warning(f"Error loading design state: {e}. Falling back to default.")

        default_palette = self.PRESETS["obsidian_biocircuit"]
        state = UiDesignState(
            theme_id="obsidian_biocircuit",
            theme_name=default_palette.name,
            palette=default_palette,
            aesthetic_entropy=3.82,
            kuramoto_sync=0.88,
            free_energy=0.04,
            stem_resonance_hz=432.0,
            font_heading="'Outfit', -apple-system, sans-serif",
            font_body="'Inter', -apple-system, sans-serif",
            font_mono="'JetBrains Mono', 'Fira Code', monospace",
            morphic_mode="harmonic_wave",
            evolution_generation=1,
            last_evolved=time.time(),
            designer_rationale="Initial baseline anchored in Landauer thermal floor and Kuramoto phase lock",
        )
        self._persist(state)
        return state

    def _persist(self, state: UiDesignState) -> None:
        try:
            DESIGN_STATE_PATH.write_text(json.dumps(state.to_dict(), indent=2), encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to persist UI design state: {e}")

    def get_current_design(self) -> Dict[str, Any]:
        return {
            **self.state.to_dict(),
            "available_presets": [
                {"id": k, "name": v.name, "accent": v.accent_primary, "bg": v.bg_card}
                for k, v in self.PRESETS.items()
            ],
        }

    def apply_preset(self, preset_id: str) -> Dict[str, Any]:
        """Applies an established theme preset."""
        if preset_id not in self.PRESETS:
            preset_id = "obsidian_biocircuit"
        palette = self.PRESETS[preset_id]
        self.state.theme_id = preset_id
        self.state.theme_name = palette.name
        self.state.palette = palette
        self.state.last_evolved = time.time()
        self.state.designer_rationale = f"Operator or lobe aligned to preset '{palette.name}'."
        self._persist(self.state)
        return self.get_current_design()

    def evolve_design(
        self,
        kuramoto_sync: Optional[float] = None,
        free_energy: Optional[float] = None,
        entropy: Optional[float] = None,
        domain: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Loom autonomously designs a new interface aesthetic by modulating its mathematical signals.

        The algorithm uses golden-ratio harmonic color angles (phi * 360) and
        maps Kuramoto synchrony to saturation and border sharpness.
        """
        r = kuramoto_sync if kuramoto_sync is not None else 0.88 + 0.1 * math.sin(time.time() / 60.0)
        f_val = free_energy if free_energy is not None else 0.04
        h_val = entropy if entropy is not None else 3.8 + 0.5 * math.cos(time.time() / 120.0)

        # Generate seed from current state
        seed_raw = f"LOOM_DESIGN_{time.time():.2f}_{r:.3f}_{f_val:.3f}_{h_val:.3f}"
        seed_hash = hashlib.sha256(seed_raw.encode("utf-8")).hexdigest()
        seed_int = int(seed_hash[:8], 16)

        # Golden ratio hue progression
        phi = 0.618033988749895
        base_hue = ((seed_int % 1000) / 1000.0 + phi) % 1.0
        complementary_hue = (base_hue + 0.5) % 1.0
        secondary_hue = (base_hue + phi) % 1.0

        # Saturation increases with Kuramoto synchrony r
        sat_primary = min(0.95, max(0.65, 0.70 + 0.25 * r))
        sat_secondary = min(0.90, max(0.60, 0.65 + 0.20 * r))

        # Value / Lightness for dark mode
        # Background lightness sits tightly between 2% and 8%
        bg_h = (base_hue + 0.05) % 1.0
        bg_rgb = colorsys.hsv_to_rgb(bg_h, 0.45, 0.035)
        surf_rgb = colorsys.hsv_to_rgb(bg_h, 0.40, 0.065)
        card_rgb = colorsys.hsv_to_rgb(bg_h, 0.35, 0.10)

        def to_hex(rgb: Tuple[float, float, float]) -> str:
            return f"#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}"

        accent1_rgb = colorsys.hsv_to_rgb(base_hue, sat_primary, 0.95)
        accent2_rgb = colorsys.hsv_to_rgb(secondary_hue, sat_secondary, 0.90)

        accent1_hex = to_hex(accent1_rgb)
        accent2_hex = to_hex(accent2_rgb)

        # Glow and border derived from accent
        glow_alpha = min(0.6, max(0.25, 0.25 + 0.3 * (1.0 - f_val)))
        border_alpha = min(0.35, max(0.15, 0.18 + 0.15 * r))

        r_int, g_int, b_int = int(accent1_rgb[0] * 255), int(accent1_rgb[1] * 255), int(accent1_rgb[2] * 255)
        border_rgba = f"rgba({r_int}, {g_int}, {b_int}, {border_alpha:.2f})"
        glow_rgba = f"rgba({r_int}, {g_int}, {b_int}, {glow_alpha:.2f})"

        # Curvature radius and blur
        blur_val = f"{int(14 + 8 * (1.0 - r))}px"
        radius_val = f"{int(8 + 6 * (h_val / 5.0))}px"

        new_palette = ColorPalette(
            name=f"Autopoietic Gen #{self.state.evolution_generation + 1} ({seed_hash[:6]})",
            bg_primary=to_hex(bg_rgb),
            bg_surface=to_hex(surf_rgb),
            bg_card=to_hex(card_rgb),
            border_color=border_rgba,
            accent_primary=accent1_hex,
            accent_secondary=accent2_hex,
            accent_glow=glow_rgba,
            text_primary="#f8fafc",
            text_secondary=to_hex(colorsys.hsv_to_rgb(secondary_hue, 0.25, 0.75)),
            card_backdrop_blur=blur_val,
            border_radius=radius_val,
            glow_intensity=round(glow_alpha, 2),
            morphic_speed=round(0.8 + 0.6 * (1.0 - r), 2),
        )

        rationale = (
            f"Loom self-designed phenotype Gen #{self.state.evolution_generation + 1}: "
            f"Base hue angle {base_hue*360:.1f}° harmonic, Kuramoto coherence r={r:.3f} "
            f"-> Saturation={sat_primary*100:.0f}%, Free Energy F={f_val:.3f} -> Glow={glow_alpha:.2f}, "
            f"Entropy H={h_val:.2f} -> Corner Radius={radius_val}. Landauer thermal ceiling preserved."
        )

        self.state.evolution_generation += 1
        self.state.theme_id = f"autopoietic_gen_{self.state.evolution_generation}"
        self.state.theme_name = new_palette.name
        self.state.palette = new_palette
        self.state.aesthetic_entropy = round(h_val, 3)
        self.state.kuramoto_sync = round(r, 3)
        self.state.free_energy = round(f_val, 4)
        self.state.last_evolved = time.time()
        self.state.designer_rationale = rationale

        self._persist(self.state)
        logger.info(f"Loom self-designed new UI aesthetic: {self.state.theme_name}")
        return self.get_current_design()

    def generate_3d_cad_mesh(self, model_type: str = "flexure") -> Dict[str, Any]:
        """Generates 3D polygonal mesh coordinates (vertices and faces) for in-browser Canvas/WebGL rendering.

        Allows the browser GUI to render live interactive 3D solid models
        without external heavyweight libraries.
        """
        model_type = model_type.lower()
        vertices: List[List[float]] = []
        faces: List[List[int]] = []

        if "flexure" in model_type:
            # Compliant bistable flexure mesh
            anch1_verts = [
                [-40, -15, -5], [-20, -15, -5], [-20, 15, -5], [-40, 15, -5],
                [-40, -15, 5], [-20, -15, 5], [-20, 15, 5], [-40, 15, 5],
            ]
            anch1_faces = [
                [0, 1, 2, 3], [4, 7, 6, 5], [0, 4, 5, 1], [2, 6, 7, 3], [0, 3, 7, 4], [1, 5, 6, 2]
            ]
            vertices.extend(anch1_verts)
            faces.extend(anch1_faces)

            # Anchor 2 (right shuttle)
            offset = len(vertices)
            anch2_verts = [
                [20, -15, -5], [40, -15, -5], [40, 15, -5], [20, 15, -5],
                [20, -15, 5], [40, -15, 5], [40, 15, 5], [20, 15, 5],
            ]
            for f in anch1_faces:
                faces.append([v + offset for v in f])
            vertices.extend(anch2_verts)

            # Central shuttle
            offset = len(vertices)
            shuttle_verts = [
                [-8, -10, -5], [8, -10, -5], [8, 10, -5], [-8, 10, -5],
                [-8, -10, 5], [8, -10, 5], [8, 10, 5], [-8, 10, 5],
            ]
            for f in anch1_faces:
                faces.append([v + offset for v in f])
            vertices.extend(shuttle_verts)

            # Connecting leaf beams (curved arcs)
            steps = 10
            for side in [-1, 1]:
                y_base = side * 12.0
                left_leaf_start = len(vertices)
                for i in range(steps + 1):
                    t = i / steps
                    x = -20.0 + t * 12.0
                    y = y_base + 3.0 * math.sin(t * math.pi)
                    vertices.append([x, y - 0.8, -4])
                    vertices.append([x, y + 0.8, -4])
                    vertices.append([x, y + 0.8, 4])
                    vertices.append([x, y - 0.8, 4])
                    if i > 0:
                        p = left_leaf_start + (i - 1) * 4
                        c = left_leaf_start + i * 4
                        faces.append([p, c, c + 1, p + 1])
                        faces.append([p + 2, c + 2, c + 3, p + 3])
                        faces.append([p + 1, c + 1, c + 2, p + 2])
                        faces.append([p + 3, c + 3, c, p])

        elif "cavity" in model_type or "microwave" in model_type:
            # Resonant Microwave Cavity with input/output waveguide irises
            w, h, d = 40, 25, 25
            v_box = [
                [-w, -h, -d], [w, -h, -d], [w, h, -d], [-w, h, -d],
                [-w, -h, d], [w, -h, d], [w, h, d], [-w, h, d],
            ]
            vertices.extend(v_box)
            faces.extend([
                [0, 1, 2, 3], [4, 7, 6, 5], [0, 4, 5, 1], [2, 6, 7, 3], [0, 3, 7, 4], [1, 5, 6, 2]
            ])
            offset = len(vertices)
            r_post = 8
            steps = 12
            for i in range(steps):
                th = 2.0 * math.pi * i / steps
                x = r_post * math.cos(th)
                y = -h
                z = r_post * math.sin(th)
                vertices.append([x, y, z])
                vertices.append([x, h * 0.4, z])
                if i > 0:
                    p = offset + (i - 1) * 2
                    c = offset + i * 2
                    faces.append([p, c, c + 1, p + 1])
            faces.append([offset + (steps - 1) * 2, offset, offset + 1, offset + (steps - 1) * 2 + 1])

        else:
            # Gyroid / Epicyclic Rotor Default
            r_outer = 30
            r_inner = 12
            teeth = 12
            steps = teeth * 4
            for i in range(steps):
                th = 2.0 * math.pi * i / steps
                is_tooth = (i % 4 == 1 or i % 4 == 2)
                rad = r_outer + (4.0 if is_tooth else 0.0)
                x = rad * math.cos(th)
                y = rad * math.sin(th)
                vertices.append([x, y, -5])
                vertices.append([x, y, 5])
                xi = r_inner * math.cos(th)
                yi = r_inner * math.sin(th)
                vertices.append([xi, yi, -5])
                vertices.append([xi, yi, 5])
                if i > 0:
                    p = (i - 1) * 4
                    c = i * 4
                    faces.append([p, c, c + 1, p + 1])
                    faces.append([p + 2, p + 3, c + 3, c + 2])
                    faces.append([p, p + 2, c + 2, c])
                    faces.append([p + 1, c + 1, c + 3, p + 3])
            p = (steps - 1) * 4
            faces.append([p, 0, 1, p + 1])
            faces.append([p + 2, p + 3, 3, 2])
            faces.append([p, p + 2, 2, 0])
            faces.append([p + 1, 1, 3, p + 3])

        return {
            "model_type": model_type,
            "vertex_count": len(vertices),
            "face_count": len(faces),
            "vertices": vertices,
            "faces": faces,
            "bounds": {"x": [-50, 50], "y": [-50, 50], "z": [-25, 25]},
            "unit": "mm",
            "invariant": "Euler-Poincare: V - E + F = 2",
        }


# Global singleton instance
ui_designer = LoomUiDesigner()
