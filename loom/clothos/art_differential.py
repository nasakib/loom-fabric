"""
Loom Fabric & ClothOS: STEM Art Differential Signal Engine (`loom/clothos/art_differential.py`).

Fulfills the user's sovereign mandate:
1. Universal Signal Decomposition: Breaks down any art form (poetry, stories, music,
   animated canvases, visual mandalas, CAD models, technical SVGs) into its canonical STEM physical signal:
   - Spectral Entropy (H in [0, 8])
   - Fundamental Frequency (f_0 in Hz or spatial wavenumber)
   - Harmonic Ratios ([f_1/f_0, f_2/f_0, ...])
   - Symmetry / Kuramoto Order Parameter (r in [0, 1])
   - Curvature Complexity (kappa, Hausdorff/contour variance)
   - Dynamical Phase Offset (theta in [-pi, pi])
   - Topological Invariants (Betti numbers beta_0, beta_1)
   - Thermodynamic / Computational Energy Flux (E in Joules / dissipation)
   - STEM Physical Discipline (Electromagnetics, Symplectic Mechanics, Compliant Flexures, Gyroid Topology, etc.)

2. Differential Evolutionary Operator (Delta S = S_t - S_{t-1}):
   Computes the gradient/difference between successive artworks and synthesizes
   the deterministic generative seed for the next piece in any medium, creating an
   unbroken closed-loop cross-modal evolutionary trajectory.

3. STEM CAD & Technical SVG Drawing Synthesis:
   - 3D CAD Solids: Parametric engineering components via FreeCAD 1.1 CLI (freecadcmd.exe)
     exporting ISO 10303 .step models, triangulated .stl meshes, and axonometric SVGs.
   - 2D Technical SVGs: Dimensioned engineering schematics (Smith charts, Poincare phase sections,
     chiral auxetic metamaterials, Stokes magnetic circulation, Carnot thermodynamic cycles).
"""

from __future__ import annotations

import cmath
from dataclasses import asdict, dataclass, field
import datetime
import hashlib
import json
import logging
import math
import os
from pathlib import Path
import random
import re
import shutil
import subprocess
import time
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("clothos.art_differential")

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
ART_DIR = WORKSPACE_ROOT / "artifacts" / "art"
DELIVERABLE_ART_DIR = WORKSPACE_ROOT / "deliverables" / "art"
GALLERY_DIR = WORKSPACE_ROOT / "artifacts" / "art_gallery"
DIFFERENTIAL_FILE = WORKSPACE_ROOT / ".loom_art_differential.json"

ART_DIR.mkdir(parents=True, exist_ok=True)
DELIVERABLE_ART_DIR.mkdir(parents=True, exist_ok=True)
GALLERY_DIR.mkdir(parents=True, exist_ok=True)

# FreeCAD CLI discovery
DEFAULT_FREECAD_PATHS = [
    r"C:\Users\natsa\AppData\Local\Programs\FreeCAD 1.1\FreeCAD_1.1.3-Windows-x86_64-py311\bin\freecadcmd.exe",
    r"C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe",
    r"C:\Program Files\FreeCAD 0.21\bin\freecadcmd.exe",
    r"C:\Program Files\FreeCAD 0.20\bin\freecadcmd.exe",
]


def find_freecad_cmd() -> Optional[str]:
    """Locates the headless FreeCAD command line binary."""
    for p in DEFAULT_FREECAD_PATHS:
        if os.path.isfile(p):
            return p
    # Search PATH
    which_fc = shutil.which("freecadcmd") or shutil.which("freecadcmd.exe")
    if which_fc:
        return which_fc
    # Search local appdata
    local_appdata = os.environ.get("LOCALAPPDATA", "")
    if local_appdata:
        pattern = Path(local_appdata) / "Programs"
        if pattern.is_dir():
            for f in pattern.glob("**/freecadcmd.exe"):
                if f.is_file():
                    return str(f)
    return None


FREECAD_CMD_PATH = find_freecad_cmd()


# =============================================================================
# 1. STEM Canonical Art Signal Representation
# =============================================================================

@dataclass
class ArtSignal:
    """Canonical physical STEM signal vector extracted from any artistic medium."""
    source_id: str
    medium: str                              # "poetry", "story", "music", "animated_video", "visual_art", "cad_model", "svg_stem"
    title: str
    timestamp: str
    epoch: float
    # Physical STEM Signal Coordinates
    spectral_entropy: float                  # Shannon entropy H in [0.0, 8.0]
    fundamental_freq: float                  # f_0 in Hz (acoustics) or rad/mm (geometry)
    harmonic_ratios: List[float]             # [1.0, f_1/f_0, f_2/f_0, ...]
    symmetry_order: float                    # Kuramoto order r in [0.0, 1.0] or C_n fold
    curvature_complexity: float              # kappa in [0.0, 10.0] (Hausdorff / curvature)
    phase_offset: float                      # theta in [-pi, pi]
    topology_betti: Tuple[int, int]          # (beta_0: connected components, beta_1: 1-cycles/voids)
    energy_flux: float                       # E in Joules or normalized computational energy
    stem_domain: str                         # Physical engineering discipline
    formula_latex: str                       # Governing physical/mathematical law
    features: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["topology_betti"] = list(self.topology_betti)
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ArtSignal:
        betti = data.get("topology_betti", (1, 0))
        if isinstance(betti, list):
            betti = (int(betti[0]), int(betti[1]))
        return cls(
            source_id=data["source_id"],
            medium=data["medium"],
            title=data.get("title", "Untitled STEM Work"),
            timestamp=data.get("timestamp", ""),
            epoch=float(data.get("epoch", time.time())),
            spectral_entropy=float(data.get("spectral_entropy", 3.5)),
            fundamental_freq=float(data.get("fundamental_freq", 432.0)),
            harmonic_ratios=data.get("harmonic_ratios", [1.0, 1.5, 2.0]),
            symmetry_order=float(data.get("symmetry_order", 0.75)),
            curvature_complexity=float(data.get("curvature_complexity", 2.0)),
            phase_offset=float(data.get("phase_offset", 0.0)),
            topology_betti=betti,
            energy_flux=float(data.get("energy_flux", 42.0)),
            stem_domain=data.get("stem_domain", "Electromagnetics"),
            formula_latex=data.get("formula_latex", r"E = \hbar \omega"),
            features=data.get("features", {}),
        )


@dataclass
class DifferentialSeed:
    """The differential gradient Delta S between artworks used as a deterministic generative seed."""
    prior_id: str
    current_id: str
    delta_entropy: float                     # Delta H = H_t - H_{t-1}
    delta_frequency: float                   # Delta f_0
    delta_phase: float                       # Delta theta in [-pi, pi]
    delta_symmetry: float                    # Delta r
    delta_curvature: float                   # Delta kappa
    delta_betti: Tuple[int, int]             # (Delta beta_0, Delta beta_1)
    delta_energy: float                      # Delta E
    seed_hash: str                           # Hexadecimal deterministic hash of Delta S
    seed_int: int                            # Integer seed for PRNG
    next_suggested_medium: str               # Suggested transmutative medium
    next_stem_domain: str                    # Next orthogonal STEM discipline
    next_target_freq: float                  # Target f_0 for next piece
    next_target_entropy: float               # Target H for next piece
    next_target_symmetry: float              # Target r for next piece
    transmutation_rationale: str             # Physical justification of the evolutionary step

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["delta_betti"] = list(self.delta_betti)
        return d


# =============================================================================
# 2. Universal Art Signal Extractor
# =============================================================================

class ArtSignalAnalyzer:
    """Decomposes any artwork across all mediums into its canonical STEM signal vector."""

    STEM_DOMAINS = [
        "Electromagnetics",
        "Symplectic_Mechanics",
        "Compliant_Flexures",
        "Gyroid_Topology",
        "Thermodynamics",
        "Fluidic_Microchannels",
        "Quantum_Oscillators",
    ]

    @staticmethod
    def _compute_shannon_entropy(text_or_bytes: str) -> float:
        """Calculates Shannon entropy in bits for a sequence."""
        if not text_or_bytes:
            return 0.0
        counts: Dict[str, int] = {}
        for ch in text_or_bytes:
            counts[ch] = counts.get(ch, 0) + 1
        n = len(text_or_bytes)
        entropy = 0.0
        for count in counts.values():
            p = count / n
            entropy -= p * math.log2(p)
        return round(min(8.0, max(0.0, entropy)), 4)

    def analyze_text(
        self,
        text: str,
        title: str,
        medium: str,
        source_id: str,
        formula: Optional[str] = None,
        epoch: Optional[float] = None,
    ) -> ArtSignal:
        """Extracts canonical signal from linguistic poetry or prose."""
        entropy = self._compute_shannon_entropy(text)
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        line_count = len(lines)
        word_count = len(text.split())

        # Fundamental cadence frequency f_0 (based on syllables/meter rhythm)
        avg_line_len = (word_count / max(1, line_count)) if line_count > 0 else 10.0
        cadence_hz = round(432.0 * (1.0 + (avg_line_len % 7) * 0.08), 2)

        # Symmetry: meter regularity and stanza balance
        stanzas = [s for s in text.split("\n\n") if s.strip()]
        stanza_lens = [len(s.split()) for s in stanzas]
        mean_len = sum(stanza_lens) / max(1, len(stanza_lens)) if stanza_lens else 1.0
        var_len = sum((l - mean_len) ** 2 for l in stanza_lens) / max(1, len(stanza_lens))
        symmetry_r = round(max(0.2, min(0.98, 1.0 / (1.0 + math.sqrt(var_len) / 10.0))), 3)

        # Curvature: vocabulary richness (Type-Token Ratio)
        words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
        unique_words = set(words)
        ttr = len(unique_words) / max(1, len(words))
        curvature = round(ttr * 5.0, 3)

        # Phase offset: sentiment polarity angle from lexical valence
        positive_markers = ["light", "truth", "harmony", "love", "equilibrium", "bloom", "sovereign", "dawn", "peace"]
        stress_markers = ["heat", "strain", "break", "tension", "entropy", "dissipate", "cold", "night", "dark"]
        pos_score = sum(text.lower().count(m) for m in positive_markers)
        str_score = sum(text.lower().count(m) for m in stress_markers)
        theta = round(math.atan2(pos_score - str_score, max(1, pos_score + str_score)), 4)

        # Topology: stanzas as connected components beta_0, cross-references/rhymes as 1-cycles beta_1
        beta_0 = max(1, len(stanzas))
        beta_1 = max(0, int(len(unique_words) * 0.05) % 5)

        # STEM Domain mapping
        domain = "Symplectic_Mechanics" if "phase" in text.lower() or "oscillator" in text.lower() else "Thermodynamics"
        governing_formula = formula or r"\oint_{\partial \Sigma} \mathbf{A} \cdot d\mathbf{l} = \iint_{\Sigma} (\nabla \times \mathbf{A}) \cdot d\mathbf{S}"

        return ArtSignal(
            source_id=source_id,
            medium=medium,
            title=title,
            timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            epoch=epoch or time.time(),
            spectral_entropy=entropy,
            fundamental_freq=cadence_hz,
            harmonic_ratios=[1.0, 1.25, 1.5, 1.875],
            symmetry_order=symmetry_r,
            curvature_complexity=curvature,
            phase_offset=theta,
            topology_betti=(beta_0, beta_1),
            energy_flux=round(word_count * 0.15 + 42.0, 2),
            stem_domain=domain,
            formula_latex=governing_formula,
            features={"line_count": line_count, "word_count": word_count, "stanzas": len(stanzas), "ttr": ttr},
        )

    def analyze_svg(
        self,
        svg_content: str,
        title: str,
        source_id: str,
        medium: str = "visual_art",
        epoch: Optional[float] = None,
    ) -> ArtSignal:
        """Extracts canonical signal from vector SVG geometries."""
        entropy = self._compute_shannon_entropy(svg_content)
        path_matches = re.findall(r'<path[^>]*d="([^"]+)"', svg_content)
        circle_matches = re.findall(r'<circle[^>]*cx="([^"]+)"', svg_content)

        # Extract numeric coordinates from paths
        all_coords: List[float] = []
        for p in path_matches:
            nums = [float(x) for x in re.findall(r"[-+]?\d*\.\d+|\d+", p)]
            all_coords.extend(nums)

        # Curvature complexity: variance of step displacements
        if len(all_coords) >= 4:
            dxs = [all_coords[i + 2] - all_coords[i] for i in range(0, len(all_coords) - 2, 2)]
            dys = [all_coords[i + 3] - all_coords[i + 1] for i in range(0, len(all_coords) - 2, 2)]
            dists = [math.hypot(dx, dy) for dx, dy in zip(dxs, dys)]
            mean_dist = sum(dists) / max(1, len(dists))
            curvature = round(min(10.0, max(0.5, mean_dist / 15.0)), 3)
        else:
            curvature = 2.5

        # Extract frequencies or metadata annotations embedded in SVG
        cpu_match = re.search(r"f_CPU\s*=\s*([\d\.]+)\s*GHz", svg_content)
        cpu_ghz = float(cpu_match.group(1)) if cpu_match else 3.70
        fundamental_freq = round(cpu_ghz * 1000.0, 2)  # MHz representation

        # Extract Kuramoto r
        k_match = re.search(r"Kuramoto\s*r\s*=\s*([\d\.]+)", svg_content)
        symmetry_r = float(k_match.group(1)) if k_match else 0.850

        # Topology: closed paths (ending in Z/z) define 1-cycles beta_1
        closed_paths = sum(1 for p in path_matches if p.strip().upper().endswith("Z"))
        beta_0 = max(1, len(circle_matches) + len(path_matches))
        beta_1 = max(1, closed_paths)

        theta = round((len(path_matches) % 12) * (2 * math.pi / 12) - math.pi, 4)
        harmonics = [1.0, 1.5, 2.0, 2.618, 3.1415]

        # Invariant extraction
        inv_match = re.search(r"Invariant:\s*([^<]+)", svg_content)
        formula = inv_match.group(1).strip() if inv_match else r"\nabla \times \mathbf{B} = \mu_0 \mathbf{J}"

        return ArtSignal(
            source_id=source_id,
            medium=medium,
            title=title,
            timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            epoch=epoch or time.time(),
            spectral_entropy=entropy,
            fundamental_freq=fundamental_freq,
            harmonic_ratios=harmonics,
            symmetry_order=symmetry_r,
            curvature_complexity=curvature,
            phase_offset=theta,
            topology_betti=(beta_0, beta_1),
            energy_flux=round(len(svg_content) / 200.0 + 35.0, 2),
            stem_domain="Electromagnetics" if "GHz" in svg_content else "Symplectic_Mechanics",
            formula_latex=formula,
            features={"paths": len(path_matches), "circles": len(circle_matches), "closed_loops": closed_paths},
        )

    def analyze_audio(
        self,
        title: str,
        source_id: str,
        base_freq: float = 432.0,
        harmonic_ratios: Optional[List[float]] = None,
        duration_sec: float = 8.0,
        epoch: Optional[float] = None,
    ) -> ArtSignal:
        """Extracts canonical signal from musical or synthesized audio compositions."""
        harmonics = harmonic_ratios or [1.0, 1.25, 1.5, 1.875, 2.0]
        weights = [1.0 / (idx + 1) for idx in range(len(harmonics))]
        total_w = sum(weights)
        probs = [w / total_w for w in weights]
        entropy = round(-sum(p * math.log2(p) for p in probs) * 1.5 + 2.0, 4)

        return ArtSignal(
            source_id=source_id,
            medium="music",
            title=title,
            timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            epoch=epoch or time.time(),
            spectral_entropy=entropy,
            fundamental_freq=float(base_freq),
            harmonic_ratios=harmonics,
            symmetry_order=0.92,
            curvature_complexity=1.85,
            phase_offset=0.0,
            topology_betti=(len(harmonics), 1),
            energy_flux=round(duration_sec * 8.5 + 20.0, 2),
            stem_domain="Quantum_Oscillators",
            formula_latex=r"\psi_n(x) = \left(\frac{m\omega}{\pi \hbar}\right)^{1/4} \frac{1}{\sqrt{2^n n!}} H_n(\xi) e^{-\xi^2/2}",
            features={"duration_sec": duration_sec, "harmonics_count": len(harmonics)},
        )

    def analyze_cad(
        self,
        cad_meta: Dict[str, Any],
        title: str,
        source_id: str,
        epoch: Optional[float] = None,
    ) -> ArtSignal:
        """Extracts canonical signal from 3D parametric CAD solid geometry."""
        volume = float(cad_meta.get("volume_mm3", 15000.0))
        surface_area = float(cad_meta.get("surface_area_mm2", 6500.0))
        faces = int(cad_meta.get("face_count", 12))
        genus = int(cad_meta.get("topological_genus", 1))

        iso_quotient = (36.0 * math.pi * (volume ** 2)) / max(1.0, surface_area ** 3)
        curvature = round(min(10.0, max(0.5, 1.0 / max(0.01, iso_quotient))), 3)

        char_dim_mm = math.pow(max(1.0, volume), 1.0 / 3.0)
        c_speed = 3.0e11  # mm/s
        f_0_ghz = round(c_speed / (2.0 * char_dim_mm * 1e9), 3)

        beta_0 = 1
        beta_1 = genus * 2
        entropy = round(min(8.0, 2.5 + math.log2(max(2, faces)) * 0.7), 4)

        return ArtSignal(
            source_id=source_id,
            medium="cad_model",
            title=title,
            timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            epoch=epoch or time.time(),
            spectral_entropy=entropy,
            fundamental_freq=f_0_ghz * 1000.0,  # in MHz
            harmonic_ratios=[1.0, 1.414, 1.732, 2.0],
            symmetry_order=round(min(0.99, max(0.5, float(cad_meta.get("symmetry_order", 0.88)))), 3),
            curvature_complexity=curvature,
            phase_offset=round(math.atan2(surface_area, max(1.0, volume)), 4),
            topology_betti=(beta_0, beta_1),
            energy_flux=round(volume * 0.005 + 50.0, 2),
            stem_domain=cad_meta.get("stem_domain", "Compliant_Flexures"),
            formula_latex=cad_meta.get("formula_latex", r"EI \frac{d^4 w}{dx^4} + P \frac{d^2 w}{dx^2} = 0"),
            features=cad_meta,
        )

    def analyze_artifact(self, artifact: Dict[str, Any]) -> ArtSignal:
        """Universal polymorphic dispatcher that analyzes any given artwork dictionary."""
        art_id = artifact.get("id") or artifact.get("artifact_id") or f"ART-{int(time.time())}"
        title = artifact.get("title", "Sovereign Creation")
        medium = artifact.get("medium") or artifact.get("art_form", "").lower()
        epoch = float(artifact.get("epoch") or artifact.get("created_timestamp", time.time()))

        if medium in ["cad_model", "cad", "stem_cad"]:
            return self.analyze_cad(artifact, title=title, source_id=art_id, epoch=epoch)

        if "svg_preview" in artifact or "svg_file" in artifact or "ALGORITHMIC_SVG" in medium.upper() or medium in ["visual_art", "svg_stem"]:
            svg_content = artifact.get("svg_preview") or artifact.get("code_content", "")
            if not svg_content and "svg_file" in artifact:
                svg_p = WORKSPACE_ROOT / artifact["svg_file"]
                if svg_p.exists():
                    svg_content = svg_p.read_text(encoding="utf-8")
            if svg_content:
                return self.analyze_svg(svg_content, title=title, source_id=art_id, medium="svg_stem" if "svg_stem" in medium else "visual_art", epoch=epoch)

        if medium in ["music", "symphony"] or "wav_file" in artifact:
            return self.analyze_audio(title=title, source_id=art_id, epoch=epoch)

        text_content = artifact.get("narrative_text") or artifact.get("code_content") or artifact.get("tagline", "")
        if not text_content and "md_file" in artifact:
            md_p = WORKSPACE_ROOT / artifact["md_file"]
            if md_p.exists():
                text_content = md_p.read_text(encoding="utf-8")
        formula = artifact.get("mathematical_formula")

        return self.analyze_text(
            text=text_content or title,
            title=title,
            medium="poetry" if "poem" in art_id.lower() or "poem" in medium else "story",
            source_id=art_id,
            formula=formula,
            epoch=epoch,
        )


# =============================================================================
# 3. Differential Signal Operator (Delta S = S_t - S_{t-1})
# =============================================================================

class ArtDifferentialEngine:
    """
    Computes the differential vector Delta S between successive artworks and
    generates the deterministic evolutionary seed for the next piece in any medium.
    """

    MEDIUM_CYCLE = [
        "cad_model",
        "svg_stem",
        "poetry",
        "music",
        "story",
        "visual_art",
    ]

    STEM_CYCLE = [
        "Electromagnetics",
        "Symplectic_Mechanics",
        "Compliant_Flexures",
        "Gyroid_Topology",
        "Thermodynamics",
        "Fluidic_Microchannels",
        "Quantum_Oscillators",
    ]

    def __init__(self, differential_file: Optional[Path] = None):
        self.diff_file = differential_file or DIFFERENTIAL_FILE
        self.analyzer = ArtSignalAnalyzer()
        self.history: List[Dict[str, Any]] = self.load_history()

    def load_history(self) -> List[Dict[str, Any]]:
        if self.diff_file.exists():
            try:
                return json.loads(self.diff_file.read_text(encoding="utf-8"))
            except Exception as e:
                logger.debug(f"Failed to load differential history: {e}")
                return []
        return []

    def save_history(self) -> None:
        try:
            self.diff_file.write_text(json.dumps(self.history, indent=2), encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to save differential history: {e}")

    def compute_differential(self, s_prev: ArtSignal, s_curr: ArtSignal) -> DifferentialSeed:
        """Calculates Delta S = S_t - S_{t-1} and synthesizes the next generative seed."""
        delta_h = round(s_curr.spectral_entropy - s_prev.spectral_entropy, 4)
        delta_f = round(s_curr.fundamental_freq - s_prev.fundamental_freq, 2)
        delta_sym = round(s_curr.symmetry_order - s_prev.symmetry_order, 3)
        delta_curv = round(s_curr.curvature_complexity - s_prev.curvature_complexity, 3)

        raw_phase_diff = s_curr.phase_offset - s_prev.phase_offset
        delta_phase = round((raw_phase_diff + math.pi) % (2 * math.pi) - math.pi, 4)

        delta_betti = (
            s_curr.topology_betti[0] - s_prev.topology_betti[0],
            s_curr.topology_betti[1] - s_prev.topology_betti[1],
        )
        delta_e = round(s_curr.energy_flux - s_prev.energy_flux, 2)

        seed_raw = f"{delta_h:.4f}:{delta_f:.2f}:{delta_phase:.4f}:{delta_sym:.3f}:{delta_curv:.3f}:{delta_betti[0]}:{delta_betti[1]}:{s_curr.source_id}"
        seed_hash = hashlib.sha256(seed_raw.encode("utf-8")).hexdigest()
        seed_int = int(seed_hash[:8], 16)

        curr_idx = self.MEDIUM_CYCLE.index(s_curr.medium) if s_curr.medium in self.MEDIUM_CYCLE else 0
        step_dir = 1 if delta_h >= 0 else 2
        next_medium = self.MEDIUM_CYCLE[(curr_idx + step_dir) % len(self.MEDIUM_CYCLE)]

        domain_idx = self.STEM_CYCLE.index(s_curr.stem_domain) if s_curr.stem_domain in self.STEM_CYCLE else 0
        next_domain = self.STEM_CYCLE[(domain_idx + 1) % len(self.STEM_CYCLE)]

        next_freq = round(abs(s_curr.fundamental_freq + 0.5 * delta_f) + 12.0, 2)
        if next_freq < 10.0:
            next_freq = 432.0
        next_entropy = round(max(1.5, min(7.5, s_curr.spectral_entropy + delta_h * 0.5)), 4)
        next_symmetry = round(max(0.2, min(0.98, s_curr.symmetry_order + delta_sym * 0.5)), 3)

        rationale = (
            f"Differential transmutation from {s_prev.source_id} to {s_curr.source_id}: "
            f"Delta H = {delta_h:+.4f} bits (entropy {'expansion' if delta_h > 0 else 'crystallization'}), "
            f"Delta f_0 = {delta_f:+.2f} Hz, Delta theta = {delta_phase:+.4f} rad, "
            f"Delta Betti = ({delta_betti[0]:+d}, {delta_betti[1]:+d}). "
            f"Seeding next creation in medium '{next_medium}' anchored in STEM domain '{next_domain}' "
            f"with target resonance f_0 = {next_freq} Hz and symmetry r = {next_symmetry:.3f}."
        )

        seed = DifferentialSeed(
            prior_id=s_prev.source_id,
            current_id=s_curr.source_id,
            delta_entropy=delta_h,
            delta_frequency=delta_f,
            delta_phase=delta_phase,
            delta_symmetry=delta_sym,
            delta_curvature=delta_curv,
            delta_betti=delta_betti,
            delta_energy=delta_e,
            seed_hash=seed_hash,
            seed_int=seed_int,
            next_suggested_medium=next_medium,
            next_stem_domain=next_domain,
            next_target_freq=next_freq,
            next_target_entropy=next_entropy,
            next_target_symmetry=next_symmetry,
            transmutation_rationale=rationale,
        )

        entry = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "epoch": time.time(),
            "signal_prev": s_prev.to_dict(),
            "signal_curr": s_curr.to_dict(),
            "differential_seed": seed.to_dict(),
        }
        self.history.append(entry)
        self.save_history()

        logger.info(f"[ArtDifferentialEngine] Computed differential seed {seed_hash[:8]}: {rationale}")
        return seed

    def get_latest_differential(self) -> Optional[Dict[str, Any]]:
        """Returns the most recent differential record and seed."""
        if self.history:
            return self.history[-1]
        return None


# =============================================================================
# 4. STEM CAD Engine (Parametric FreeCAD Synthesizer)
# =============================================================================

class StemCadEngine:
    """
    Parametric 3D CAD modeling engine utilizing headless FreeCAD (freecadcmd.exe)
    to synthesize real physical engineering components strictly within STEM boundaries.
    """

    ARCHETYPES = [
        "MICROWAVE_CAVITY_FILTER",
        "BISTABLE_COMPLIANT_FLEXURE",
        "GYROID_TPMS_HEAT_EXCHANGER",
        "KURAMOTO_EPICYCLIC_ROTOR",
        "MICROFLUIDIC_DROPLET_GENERATOR",
    ]

    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = workspace_root or WORKSPACE_ROOT
        self.cad_dir = self.workspace_root / "artifacts" / "art"
        self.deliverable_dir = self.workspace_root / "deliverables" / "art"
        self.cad_dir.mkdir(parents=True, exist_ok=True)
        self.deliverable_dir.mkdir(parents=True, exist_ok=True)
        self.freecad_bin = FREECAD_CMD_PATH

    def generate_cad_model(
        self,
        seed: Optional[DifferentialSeed] = None,
        archetype: Optional[str] = None,
        title: Optional[str] = None,
        freq_mhz: Optional[float] = None,
        symmetry_r: Optional[float] = None,
        scale_mm: float = 1.0,
        resolution: int = 16,
        use_freecad: bool = False,
    ) -> Dict[str, Any]:
        """
        Synthesizes a real 3D parametric CAD model based on the differential seed
        or operator parameters and exports .py, faceted AP214 .step, binary .stl, and .svg.
        """
        from loom.clothos.cad_kernel import (
            generate_archetype_mesh,
            write_binary_stl,
            write_step_ap214,
        )

        target_arch = archetype
        if not target_arch or target_arch not in self.ARCHETYPES:
            if seed:
                target_arch = self.ARCHETYPES[seed.seed_int % len(self.ARCHETYPES)]
            else:
                target_arch = random.choice(self.ARCHETYPES)

        timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        uid = f"CAD_{int(time.time())}_{random.randint(1000, 9999)}"

        f_0 = float(freq_mhz) if freq_mhz is not None else (seed.next_target_freq if seed else 2450.0)
        sym_r = float(symmetry_r) if symmetry_r is not None else (seed.next_target_symmetry if seed else 0.88)
        h_entropy = seed.next_target_entropy if seed else 3.8

        script_code, meta = self._build_freecad_script(
            archetype=target_arch,
            uid=uid,
            freq_mhz=f_0,
            symmetry_r=sym_r,
            entropy=h_entropy,
        )
        mesh_data = generate_archetype_mesh(
            archetype=target_arch,
            freq_mhz=f_0,
            symmetry_r=sym_r,
            scale_mm=scale_mm,
            resolution=resolution,
        )
        # Anchor CAD metadata directly to measured triangulated BREP mesh quantities
        meta["volume_mm3"] = mesh_data["volume_mm3"]
        meta["surface_area_mm2"] = mesh_data["surface_area_mm2"]
        meta["face_count"] = mesh_data["triangle_count"]
        meta["vertex_count"] = mesh_data["vertex_count"]
        meta["bounds"] = mesh_data["bounds"]
        if scale_mm != 1.0:
            meta["dimensions"] = {**meta.get("dimensions", {}), "scale_mm": scale_mm}

        model_title = title or meta["title"]

        py_filename = f"{uid}.py"
        step_filename = f"{uid}.step"
        stl_filename = f"{uid}.stl"
        svg_filename = f"{uid}_drawing.svg"
        html_filename = f"{uid}.html"
        md_filename = f"{uid}.md"

        py_path = self.cad_dir / py_filename
        step_path = self.cad_dir / step_filename
        stl_path = self.cad_dir / stl_filename
        svg_path = self.cad_dir / svg_filename
        html_path = self.cad_dir / html_filename
        md_path = self.deliverable_dir / md_filename

        py_path.write_text(script_code, encoding="utf-8")

        fc_success = False
        if use_freecad and self.freecad_bin and os.path.exists(self.freecad_bin):
            try:
                cmd = [self.freecad_bin, str(py_path.resolve())]
                res = subprocess.run(
                    cmd,
                    cwd=str(self.cad_dir.resolve()),
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                fc_success = (step_path.exists() and step_path.stat().st_size > 0)
                logger.info(f"[StemCadEngine] FreeCAD compilation code {res.returncode}, step_exists={fc_success}")
            except Exception as e:
                logger.warning(f"[StemCadEngine] FreeCAD execution failed: {e}")

        if not step_path.exists():
            write_step_ap214(step_path, mesh_data, title=model_title)
        if not stl_path.exists():
            write_binary_stl(stl_path, mesh_data)

        svg_content = self._generate_technical_svg_drawing(
            meta=meta,
            uid=uid,
            title=model_title,
            seed=seed,
        )
        svg_path.write_text(svg_content, encoding="utf-8")

        html_content = self._generate_cad_html(
            meta=meta,
            uid=uid,
            title=model_title,
            svg_content=svg_content,
            py_code=script_code,
            seed=seed,
        )
        html_path.write_text(html_content, encoding="utf-8")

        md_content = self._generate_cad_markdown(
            meta=meta,
            uid=uid,
            title=model_title,
            seed=seed,
            step_file=step_filename,
            stl_file=stl_filename,
            svg_file=svg_filename,
            py_file=py_filename,
        )
        md_path.write_text(md_content, encoding="utf-8")

        artifact_dict = {
            "id": uid,
            "title": model_title,
            "medium": "cad_model",
            "archetype": target_arch,
            "tagline": meta["tagline"],
            "timestamp": timestamp_str,
            "epoch": time.time(),
            "stem_domain": meta["stem_domain"],
            "formula_latex": meta["formula_latex"],
            "volume_mm3": meta["volume_mm3"],
            "surface_area_mm2": meta["surface_area_mm2"],
            "face_count": meta["face_count"],
            "topological_genus": meta["topological_genus"],
            "symmetry_order": sym_r,
            "py_file": str(py_path.relative_to(self.workspace_root)).replace("\\", "/"),
            "step_file": str(step_path.relative_to(self.workspace_root)).replace("\\", "/"),
            "stl_file": str(stl_path.relative_to(self.workspace_root)).replace("\\", "/"),
            "svg_file": str(svg_path.relative_to(self.workspace_root)).replace("\\", "/"),
            "html_file": str(html_path.relative_to(self.workspace_root)).replace("\\", "/"),
            "md_file": str(md_path.relative_to(self.workspace_root)).replace("\\", "/"),
            "preview_url": f"/artifacts/art/{html_filename}",
            "svg_preview": svg_content,
        }

        return artifact_dict

    def _build_freecad_script(
        self,
        archetype: str,
        uid: str,
        freq_mhz: float,
        symmetry_r: float,
        entropy: float,
    ) -> Tuple[str, Dict[str, Any]]:
        """Constructs executable Python code for FreeCAD Part workbench."""
        if archetype == "MICROWAVE_CAVITY_FILTER":
            a_mm = round(max(20.0, min(100.0, 3e5 / (2.0 * freq_mhz))), 2)
            b_mm = round(a_mm * 0.5, 2)
            d_mm = round(a_mm * 1.414, 2)
            wall_t = 3.0
            probe_r = 1.5
            vol = round(a_mm * b_mm * d_mm, 2)
            surf = round(2 * (a_mm * b_mm + a_mm * d_mm + b_mm * d_mm), 2)
            meta = {
                "title": f"Microwave Resonant Cavity Filter (f_0 = {freq_mhz:.1f} MHz)",
                "archetype": archetype,
                "stem_domain": "Electromagnetics",
                "tagline": f"Parametric WR-{int(a_mm*10)} Waveguide Cavity with Symmetrical Coupling Probes",
                "formula_latex": r"f_{101} = \frac{c}{2\pi \sqrt{\mu_r \epsilon_r}} \sqrt{\left(\frac{\pi}{a}\right)^2 + \left(\frac{\pi}{d}\right)^2}",
                "volume_mm3": vol,
                "surface_area_mm2": surf,
                "face_count": 18,
                "topological_genus": 1,
                "dimensions": {"a_width_mm": a_mm, "b_height_mm": b_mm, "d_length_mm": d_mm, "wall_t_mm": wall_t},
            }
            code = f"""# FreeCAD Parametric Script: {meta['title']}
import sys, Part, FreeCAD

a = {a_mm}
b = {b_mm}
d = {d_mm}
t = {wall_t}
pr = {probe_r}

outer = Part.makeBox(a + 2*t, b + 2*t, d + 2*t)
inner = Part.makeBox(a, b, d)
inner.translate(FreeCAD.Vector(t, t, t))
cavity = outer.cut(inner)

probe1 = Part.makeCylinder(pr, 15.0)
probe1.translate(FreeCAD.Vector(t + a/4.0, t + b + t, t + d/2.0))
cavity = cavity.fuse(probe1)

probe2 = Part.makeCylinder(pr, 15.0)
probe2.translate(FreeCAD.Vector(t + 3.0*a/4.0, t + b + t, t + d/2.0))
cavity = cavity.fuse(probe2)

Part.export([cavity], '{uid}.step')
cavity.exportStl('{uid}.stl')

print('FREECAD_COMPILED_SUCCESSFULLY')
sys.exit(0)
"""
            return code, meta

        elif archetype == "BISTABLE_COMPLIANT_FLEXURE":
            length_l = round(60.0 + symmetry_r * 40.0, 2)
            height_h = round(6.0 + (1.0 - symmetry_r) * 8.0, 2)
            beam_t = 1.2
            depth_w = 12.0
            vol = round(2.0 * length_l * beam_t * depth_w + 3000.0, 2)
            surf = round(4.0 * length_l * depth_w + 5000.0, 2)
            meta = {
                "title": f"Bistable Compliant Flexure Shuttle (L={length_l}mm, h={height_h}mm)",
                "archetype": archetype,
                "stem_domain": "Compliant_Flexures",
                "tagline": "Non-Linear Buckling Kinetic Flexure with Zero Mechanical Backlash",
                "formula_latex": r"EI \frac{d^4 w}{dx^4} + P \frac{d^2 w}{dx^2} = 0, \quad Q = \frac{h}{t} \ge 2.31",
                "volume_mm3": vol,
                "surface_area_mm2": surf,
                "face_count": 26,
                "topological_genus": 2,
                "dimensions": {"length_L_mm": length_l, "apex_h_mm": height_h, "beam_t_mm": beam_t, "depth_w_mm": depth_w},
            }
            code = f"""# FreeCAD Parametric Script: {meta['title']}
import sys, Part, FreeCAD

L = {length_l}
h = {height_h}
t = {beam_t}
w = {depth_w}

anchor1 = Part.makeBox(15, 25, w)
anchor2 = Part.makeBox(15, 25, w)
anchor2.translate(FreeCAD.Vector(L + 15, 0, 0))

shuttle = Part.makeBox(20, 20, w)
shuttle.translate(FreeCAD.Vector(L/2.0 + 5, h + 2.5, 0))

beam1 = Part.makeBox(L, t, w)
beam1.translate(FreeCAD.Vector(15, 12, 0))
beam2 = Part.makeBox(L, t, w)
beam2.translate(FreeCAD.Vector(15, 12 + h, 0))

solid = anchor1.fuse(anchor2).fuse(shuttle).fuse(beam1).fuse(beam2)

Part.export([solid], '{uid}.step')
solid.exportStl('{uid}.stl')

print('FREECAD_COMPILED_SUCCESSFULLY')
sys.exit(0)
"""
            return code, meta

        elif archetype == "GYROID_TPMS_HEAT_EXCHANGER":
            cube_size = round(40.0 + symmetry_r * 20.0, 2)
            wall = 2.5
            vol = round((cube_size ** 3) * 0.48, 2)
            surf = round((cube_size ** 2) * 8.5, 2)
            meta = {
                "title": f"Gyroid Triply Periodic Minimal Surface (TPMS) Core ({cube_size:.0f}mm³)",
                "archetype": archetype,
                "stem_domain": "Gyroid_Topology",
                "tagline": "Zero Mean Curvature (H=0) Dual Fluid Volume Topology for High-Flux Thermal Transfer",
                "formula_latex": r"\cos\left(\frac{2\pi x}{L}\right)\sin\left(\frac{2\pi y}{L}\right) + \cos\left(\frac{2\pi y}{L}\right)\sin\left(\frac{2\pi z}{L}\right) + \cos\left(\frac{2\pi z}{L}\right)\sin\left(\frac{2\pi x}{L}\right) = 0",
                "volume_mm3": vol,
                "surface_area_mm2": surf,
                "face_count": 48,
                "topological_genus": 3,
                "dimensions": {"unit_cell_mm": cube_size, "wall_thickness_mm": wall},
            }
            code = f"""# FreeCAD Parametric Script: {meta['title']}
import sys, Part, FreeCAD

s = {cube_size}
box = Part.makeBox(s, s, s)

c1 = Part.makeCylinder(s/6.0, s)
c1.translate(FreeCAD.Vector(s/3.0, s/3.0, 0))
c2 = Part.makeCylinder(s/6.0, s)
c2.translate(FreeCAD.Vector(2*s/3.0, 2*s/3.0, 0))

c3 = Part.makeCylinder(s/6.0, s)
c3.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0), 90)
c3.translate(FreeCAD.Vector(s/2.0, s, s/3.0))

c4 = Part.makeCylinder(s/6.0, s)
c4.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,1,0), 90)
c4.translate(FreeCAD.Vector(0, s/2.0, 2*s/3.0))

gyroid_solid = box.cut(c1).cut(c2).cut(c3).cut(c4)

Part.export([gyroid_solid], '{uid}.step')
gyroid_solid.exportStl('{uid}.stl')

print('FREECAD_COMPILED_SUCCESSFULLY')
sys.exit(0)
"""
            return code, meta

        elif archetype == "KURAMOTO_EPICYCLIC_ROTOR":
            rotor_r = round(35.0 + symmetry_r * 25.0, 2)
            lobes = int(3 + round(symmetry_r * 5))
            vol = round(math.pi * (rotor_r ** 2) * 8.0, 2)
            surf = round(2.0 * math.pi * (rotor_r ** 2) + 2.0 * math.pi * rotor_r * 8.0, 2)
            meta = {
                "title": f"Kuramoto Epicyclic Harmonic Rotor (C_{lobes} Symmetry, R={rotor_r:.1f}mm)",
                "archetype": archetype,
                "stem_domain": "Symplectic_Mechanics",
                "tagline": "Dynamic Phase Balance Epicyclic Rotor for Harmonic Oscillator Synchronization",
                "formula_latex": r"\frac{d\theta_i}{dt} = \omega_i + \frac{K}{N}\sum_{j=1}^N \sin(\theta_j - \theta_i), \quad r e^{i\psi} = \frac{1}{N}\sum_{j=1}^N e^{i\theta_j}",
                "volume_mm3": vol,
                "surface_area_mm2": surf,
                "face_count": lobes * 4 + 6,
                "topological_genus": lobes + 1,
                "dimensions": {"outer_radius_mm": rotor_r, "symmetry_lobes": lobes, "rotor_thickness_mm": 8.0},
            }
            code = f"""# FreeCAD Parametric Script: {meta['title']}
import sys, Part, FreeCAD, math

R = {rotor_r}
lobes = {lobes}
thick = 8.0

hub = Part.makeCylinder(R, thick)
bore = Part.makeCylinder(R * 0.25, thick)
hub = hub.cut(bore)

for i in range(lobes):
    ang = (2 * math.pi * i) / lobes
    hx = (R * 0.65) * math.cos(ang)
    hy = (R * 0.65) * math.sin(ang)
    hole = Part.makeCylinder(R * 0.15, thick)
    hole.translate(FreeCAD.Vector(hx, hy, 0))
    hub = hub.cut(hole)

Part.export([hub], '{uid}.step')
hub.exportStl('{uid}.stl')

print('FREECAD_COMPILED_SUCCESSFULLY')
sys.exit(0)
"""
            return code, meta

        else:  # MICROFLUIDIC_DROPLET_GENERATOR
            chip_l = 60.0
            chip_w = 40.0
            chip_h = 10.0
            orifice_um = round(80.0 + (1.0 - symmetry_r) * 120.0, 1)
            vol = round(chip_l * chip_w * chip_h, 2)
            surf = round(2.0 * (chip_l * chip_w + chip_l * chip_h + chip_w * chip_h), 2)
            meta = {
                "title": f"Microfluidic Flow-Focusing Droplet Chip (w={orifice_um:.0f}µm)",
                "archetype": archetype,
                "stem_domain": "Fluidic_Microchannels",
                "tagline": "Stokes Regime (Re ≪ 1) Flow-Focusing Droplet Generator with Symmetrical Oil Sheath Ports",
                "formula_latex": r"\mathrm{Ca} = \frac{\mu U}{\gamma}, \quad d_{\text{drop}} \approx w \left(\frac{Q_{\text{disp}}}{Q_{\text{cont}}}\right)^\alpha",
                "volume_mm3": vol,
                "surface_area_mm2": surf,
                "face_count": 22,
                "topological_genus": 3,
                "dimensions": {"orifice_width_um": orifice_um, "chip_length_mm": chip_l, "chip_width_mm": chip_w},
            }
            code = f"""# FreeCAD Parametric Script: {meta['title']}
import sys, Part, FreeCAD

L = {chip_l}
W = {chip_w}
H = {chip_h}

block = Part.makeBox(L, W, H)

ch1 = Part.makeBox(L, 1.2, 0.8)
ch1.translate(FreeCAD.Vector(0, W/2.0 - 0.6, H - 0.8))

ch2 = Part.makeBox(1.2, W, 0.8)
ch2.translate(FreeCAD.Vector(L/3.0 - 0.6, 0, H - 0.8))

p1 = Part.makeCylinder(1.5, H)
p1.translate(FreeCAD.Vector(5, W/2.0, 0))
p2 = Part.makeCylinder(1.5, H)
p2.translate(FreeCAD.Vector(L/3.0, 5, 0))
p3 = Part.makeCylinder(1.5, H)
p3.translate(FreeCAD.Vector(L/3.0, W - 5, 0))

chip = block.cut(ch1).cut(ch2).cut(p1).cut(p2).cut(p3)

Part.export([chip], '{uid}.step')
chip.exportStl('{uid}.stl')

print('FREECAD_COMPILED_SUCCESSFULLY')
sys.exit(0)
"""
            return code, meta

    def _write_fallback_step(self, path: Path, title: str, meta: Dict[str, Any]) -> None:
        """Writes a geometrically populated ISO 10303-21 FACETED_BREP STEP exchange file."""
        from loom.clothos.cad_kernel import generate_archetype_mesh, write_step_ap214
        mesh = generate_archetype_mesh(archetype=meta.get("archetype", "MICROWAVE_CAVITY_FILTER"))
        write_step_ap214(path, mesh, title=title)

    def _write_fallback_stl(self, path: Path, meta: Dict[str, Any]) -> None:
        """Writes a parametric binary STL triangulated mesh with computed outward normals."""
        from loom.clothos.cad_kernel import generate_archetype_mesh, write_binary_stl
        mesh = generate_archetype_mesh(archetype=meta.get("archetype", "MICROWAVE_CAVITY_FILTER"))
        write_binary_stl(path, mesh)

    def _generate_technical_svg_drawing(
        self,
        meta: Dict[str, Any],
        uid: str,
        title: str,
        seed: Optional[DifferentialSeed] = None,
    ) -> str:
        """Generates an ISO standard technical orthographic / axonometric vector drawing."""
        w, h = 1000, 750
        arch = meta["archetype"]
        dom = meta["stem_domain"]
        formula = meta["formula_latex"]

        grid_lines = []
        for gx in range(50, w - 50, 40):
            grid_lines.append(f'<line x1="{gx}" y1="50" x2="{gx}" y2="{h - 100}" stroke="#1e293b" stroke-width="0.5" stroke-dasharray="2,2"/>')
        for gy in range(50, h - 100, 40):
            grid_lines.append(f'<line x1="50" y1="{gy}" x2="{w - 50}" y2="{gy}" stroke="#1e293b" stroke-width="0.5" stroke-dasharray="2,2"/>')

        proj_lines = []
        cx, cy = 340, 340
        if arch == "MICROWAVE_CAVITY_FILTER":
            bw, bh, bd = 160, 90, 120
            proj_lines.append(f'<polygon points="{cx},{cy} {cx+bw},{cy} {cx+bw},{cy+bh} {cx},{cy+bh}" fill="#0f172a" stroke="#38bdf8" stroke-width="2"/>')
            proj_lines.append(f'<polygon points="{cx},{cy} {cx+bd*0.7},{cy-bd*0.5} {cx+bw+bd*0.7},{cy-bd*0.5} {cx+bw},{cy}" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>')
            proj_lines.append(f'<polygon points="{cx+bw},{cy} {cx+bw+bd*0.7},{cy-bd*0.5} {cx+bw+bd*0.7},{cy+bh-bd*0.5} {cx+bw},{cy+bh}" fill="#0b1120" stroke="#38bdf8" stroke-width="2"/>')
            p1x, p1y = cx + 45, cy - 25
            proj_lines.append(f'<ellipse cx="{p1x}" cy="{p1y}" rx="14" ry="7" fill="#fbbf24" stroke="#d97706" stroke-width="1.5"/>')
            proj_lines.append(f'<line x1="{p1x-14}" y1="{p1y}" x2="{p1x-14}" y2="{p1y-35}" stroke="#fbbf24" stroke-width="1.5"/>')
            proj_lines.append(f'<line x1="{p1x+14}" y1="{p1y}" x2="{p1x+14}" y2="{p1y-35}" stroke="#fbbf24" stroke-width="1.5"/>')
            proj_lines.append(f'<ellipse cx="{p1x}" cy="{p1y-35}" rx="14" ry="7" fill="#fde68a" stroke="#d97706" stroke-width="1.5"/>')
            p2x, p2y = cx + 115, cy - 25
            proj_lines.append(f'<ellipse cx="{p2x}" cy="{p2y}" rx="14" ry="7" fill="#fbbf24" stroke="#d97706" stroke-width="1.5"/>')
            proj_lines.append(f'<line x1="{p2x-14}" y1="{p2y}" x2="{p2x-14}" y2="{p2y-35}" stroke="#fbbf24" stroke-width="1.5"/>')
            proj_lines.append(f'<line x1="{p2x+14}" y1="{p2y}" x2="{p2x+14}" y2="{p2y-35}" stroke="#fbbf24" stroke-width="1.5"/>')
            proj_lines.append(f'<ellipse cx="{p2x}" cy="{p2y-35}" rx="14" ry="7" fill="#fde68a" stroke="#d97706" stroke-width="1.5"/>')
            proj_lines.append(f'<line x1="{cx}" y1="{cy+bh+18}" x2="{cx+bw}" y2="{cy+bh+18}" stroke="#94a3b8" stroke-width="1" marker-start="url(#arrow)" marker-end="url(#arrow)"/>')
            proj_lines.append(f'<text x="{cx+bw/2}" y="{cy+bh+34}" fill="#94a3b8" font-size="12" text-anchor="middle" font-family="monospace">a = {meta["dimensions"].get("a_width_mm")} mm</text>')

        elif arch == "BISTABLE_COMPLIANT_FLEXURE":
            ax1, ay1 = cx - 120, cy
            proj_lines.append(f'<rect x="{ax1}" y="{ay1}" width="40" height="90" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>')
            ax2, ay2 = cx + 160, cy
            proj_lines.append(f'<rect x="{ax2}" y="{ay2}" width="40" height="90" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>')
            sx, sy = cx + 20, cy + 25
            proj_lines.append(f'<rect x="{sx}" y="{sy}" width="45" height="40" fill="#0f172a" stroke="#10b981" stroke-width="2"/>')
            proj_lines.append(f'<path d="M {ax1+40} {ay1+15} Q {cx+40} {cy-25} {ax2} {ay2+15}" fill="none" stroke="#f59e0b" stroke-width="3"/>')
            proj_lines.append(f'<path d="M {ax1+40} {ay1+75} Q {cx+40} {cy+35} {ax2} {ay2+75}" fill="none" stroke="#f59e0b" stroke-width="3"/>')
            proj_lines.append(f'<line x1="{sx+22}" y1="{sy-15}" x2="{sx+22}" y2="{sy-45}" stroke="#ec4899" stroke-width="2" marker-end="url(#arrow)"/>')
            proj_lines.append(f'<text x="{sx+30}" y="{sy-30}" fill="#ec4899" font-size="11" font-family="monospace">Δw (Bistable Snap)</text>')

        elif arch == "GYROID_TPMS_HEAT_EXCHANGER":
            proj_lines.append(f'<rect x="{cx-80}" y="{cy-80}" width="240" height="240" fill="#0b1120" stroke="#38bdf8" stroke-width="2"/>')
            for gi in range(-60, 180, 30):
                proj_lines.append(f'<path d="M {cx-80} {cy+gi} C {cx} {cy+gi-40}, {cx+80} {cy+gi+40}, {cx+160} {cy+gi}" fill="none" stroke="#06b6d4" stroke-width="1.8" opacity="0.8"/>')
                proj_lines.append(f'<path d="M {cx+gi} {cy-80} C {cx+gi-40} {cy}, {cx+gi+40} {cy+80}, {cx+gi} {cy+160}" fill="none" stroke="#3b82f6" stroke-width="1.8" opacity="0.8"/>')
            proj_lines.append(f'<circle cx="{cx+40}" cy="{cy+40}" r="35" fill="none" stroke="#f43f5e" stroke-width="2" stroke-dasharray="4,4"/>')
            proj_lines.append(f'<text x="{cx+40}" y="{cy+45}" fill="#f43f5e" font-size="11" text-anchor="middle" font-family="monospace">H = 0 (Minimal)</text>')

        elif arch == "KURAMOTO_EPICYCLIC_ROTOR":
            rr = 110
            proj_lines.append(f'<circle cx="{cx+40}" cy="{cy+40}" r="{rr}" fill="#0f172a" stroke="#38bdf8" stroke-width="2.5"/>')
            proj_lines.append(f'<circle cx="{cx+40}" cy="{cy+40}" r="28" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>')
            lobes = meta["dimensions"].get("symmetry_lobes", 5)
            for li in range(lobes):
                lang = (2 * math.pi * li) / lobes
                lx = cx + 40 + (rr * 0.65) * math.cos(lang)
                ly = cy + 40 + (rr * 0.65) * math.sin(lang)
                proj_lines.append(f'<circle cx="{lx}" cy="{ly}" r="16" fill="#030712" stroke="#a855f7" stroke-width="2"/>')
                proj_lines.append(f'<line x1="{cx+40}" y1="{cy+40}" x2="{lx}" y2="{ly}" stroke="#a855f7" stroke-width="1" stroke-dasharray="2,2"/>')
            proj_lines.append(f'<text x="{cx+40}" y="{cy+40+rr+26}" fill="#a855f7" font-size="12" text-anchor="middle" font-family="monospace">Kuramoto C_{lobes} Phase Rotor (r={meta.get("symmetry_order", 0.9):.3f})</text>')

        else:  # MICROFLUIDIC_DROPLET_GENERATOR
            proj_lines.append(f'<rect x="{cx-100}" y="{cy-50}" width="280" height="180" fill="#0b1120" stroke="#38bdf8" stroke-width="2"/>')
            proj_lines.append(f'<line x1="{cx-100}" y1="{cy+40}" x2="{cx+180}" y2="{cy+40}" stroke="#0284c7" stroke-width="14"/>')
            proj_lines.append(f'<line x1="{cx+20}" y1="{cy-50}" x2="{cx+20}" y2="{cy+130}" stroke="#eab308" stroke-width="10"/>')
            proj_lines.append(f'<circle cx="{cx+20}" cy="{cy+40}" r="12" fill="#ef4444" opacity="0.6"/>')
            for di in range(40, 170, 28):
                proj_lines.append(f'<circle cx="{cx+di}" cy="{cy+40}" r="6" fill="#38bdf8" stroke="#ffffff" stroke-width="1"/>')
            proj_lines.append(f'<text x="{cx+20}" y="{cy-60}" fill="#eab308" font-size="11" text-anchor="middle" font-family="monospace">Continuous Sheath Oil</text>')
            proj_lines.append(f'<text x="{cx-60}" y="{cy+30}" fill="#0284c7" font-size="11" font-family="monospace">Dispersed Aqueous</text>')

        right_x = 650
        specs = [
            f'<text x="{right_x}" y="100" fill="#38bdf8" font-size="14" font-weight="bold" font-family="monospace">PARAMETRIC INVARIANTS</text>',
            f'<text x="{right_x}" y="125" fill="#94a3b8" font-size="11" font-family="monospace">STEM Domain: {dom}</text>',
            f'<text x="{right_x}" y="145" fill="#94a3b8" font-size="11" font-family="monospace">Archetype: {arch}</text>',
            f'<text x="{right_x}" y="165" fill="#94a3b8" font-size="11" font-family="monospace">Volume: {meta.get("volume_mm3"):,.1f} mm³</text>',
            f'<text x="{right_x}" y="185" fill="#94a3b8" font-size="11" font-family="monospace">Surface Area: {meta.get("surface_area_mm2"):,.1f} mm²</text>',
            f'<text x="{right_x}" y="205" fill="#94a3b8" font-size="11" font-family="monospace">Topological Genus: g = {meta.get("topological_genus")}</text>',
            f'<text x="{right_x}" y="225" fill="#94a3b8" font-size="11" font-family="monospace">Euler Characteristic: χ = {2 - 2*meta.get("topological_genus", 1)}</text>',
            f'<text x="{right_x}" y="255" fill="#fbbf24" font-size="12" font-weight="bold" font-family="monospace">DIFFERENTIAL PROVENANCE</text>',
        ]
        if seed:
            specs.extend([
                f'<text x="{right_x}" y="275" fill="#94a3b8" font-size="10" font-family="monospace">Prior Art: {seed.prior_id}</text>',
                f'<text x="{right_x}" y="295" fill="#94a3b8" font-size="10" font-family="monospace">ΔH: {seed.delta_entropy:+.4f} bits</text>',
                f'<text x="{right_x}" y="315" fill="#94a3b8" font-size="10" font-family="monospace">Δf_0: {seed.delta_frequency:+.2f} Hz</text>',
                f'<text x="{right_x}" y="335" fill="#94a3b8" font-size="10" font-family="monospace">Δθ: {seed.delta_phase:+.4f} rad</text>',
                f'<text x="{right_x}" y="355" fill="#94a3b8" font-size="10" font-family="monospace">Seed Hash: {seed.seed_hash[:12]}...</text>',
            ])
        else:
            specs.append(f'<text x="{right_x}" y="275" fill="#64748b" font-size="10" font-family="monospace">Inaugural STEM Genesis</text>')

        tb_x, tb_y = w - 420, h - 90
        title_block = f"""
        <g id="title-block">
            <rect x="{tb_x}" y="{tb_y}" width="370" height="75" fill="#0b1120" stroke="#38bdf8" stroke-width="1.5"/>
            <line x1="{tb_x}" y1="{tb_y+25}" x2="{tb_x+370}" y2="{tb_y+25}" stroke="#1e293b" stroke-width="1"/>
            <line x1="{tb_x}" y1="{tb_y+50}" x2="{tb_x+370}" y2="{tb_y+50}" stroke="#1e293b" stroke-width="1"/>
            <line x1="{tb_x+220}" y1="{tb_y}" x2="{tb_x+220}" y2="{tb_y+75}" stroke="#1e293b" stroke-width="1"/>
            <text x="{tb_x+10}" y="{tb_y+17}" fill="#f8fafc" font-size="11" font-weight="bold" font-family="sans-serif">{title[:30]}</text>
            <text x="{tb_x+230}" y="{tb_y+17}" fill="#38bdf8" font-size="10" font-family="monospace">DWG: {uid}</text>
            <text x="{tb_x+10}" y="{tb_y+42}" fill="#94a3b8" font-size="10" font-family="sans-serif">CLOTHOS SOVEREIGN FABRIC • ISO 10303</text>
            <text x="{tb_x+230}" y="{tb_y+42}" fill="#10b981" font-size="10" font-family="monospace">STATUS: RELEASED</text>
            <text x="{tb_x+10}" y="{tb_y+66}" fill="#64748b" font-size="9" font-family="monospace">SCALE: 1:1 • UNITS: mm • FREE_CAD 1.1</text>
            <text x="{tb_x+230}" y="{tb_y+66}" fill="#64748b" font-size="9" font-family="monospace">{datetime.datetime.now().strftime("%Y-%m-%d")}</text>
        </g>
        """

        svg_code = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="100%" style="background:#030712; font-family:system-ui, sans-serif;">
    <defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#94a3b8" />
        </marker>
    </defs>
    <rect width="{w}" height="{h}" fill="#030712"/>
    <g id="grid">{"".join(grid_lines)}</g>
    <rect x="30" y="30" width="{w-60}" height="{h-60}" fill="none" stroke="#334155" stroke-width="1.5"/>
    <rect x="35" y="35" width="{w-70}" height="{h-70}" fill="none" stroke="#1e293b" stroke-width="0.75"/>
    
    <text x="50" y="65" fill="#38bdf8" font-size="18" font-weight="bold" letter-spacing="1">ENGINEERING BLUEPRINT: {title.upper()}</text>
    <text x="50" y="85" fill="#64748b" font-size="11" font-family="monospace">GOVERNING INVARIANT: {formula}</text>

    <g id="cad-projection">{"".join(proj_lines)}</g>
    <g id="specifications">{"".join(specs)}</g>
    {title_block}
</svg>"""
        return svg_code

    def _generate_cad_html(
        self,
        meta: Dict[str, Any],
        uid: str,
        title: str,
        svg_content: str,
        py_code: str,
        seed: Optional[DifferentialSeed] = None,
    ) -> str:
        """Generates an interactive HTML5 CAD and technical inspection view."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>CAD Inspection: {title}</title>
    <style>
        body {{ margin:0; padding:24px; background:#030712; color:#f8fafc; font-family:system-ui, sans-serif; }}
        .header {{ display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #1e293b; padding-bottom:16px; margin-bottom:24px; }}
        .badge {{ background:#0f172a; border:1px solid #38bdf8; color:#38bdf8; padding:4px 10px; border-radius:6px; font-family:monospace; font-size:12px; }}
        .drawing-box {{ background:#050b14; border:1px solid #1e293b; border-radius:12px; overflow:hidden; box-shadow:0 12px 40px rgba(0,0,0,0.8); margin-bottom:24px; }}
        .grid {{ display:grid; grid-template-columns:1fr 1fr; gap:20px; }}
        .card {{ background:#0b1120; border:1px solid #1e293b; border-radius:8px; padding:16px; }}
        pre {{ background:#030712; border:1px solid #1e293b; border-radius:6px; padding:12px; color:#38bdf8; font-family:monospace; font-size:11px; overflow-x:auto; max-height:260px; }}
        .download-btn {{ display:inline-block; background:#0284c7; color:#ffffff; padding:8px 14px; border-radius:6px; text-decoration:none; font-weight:bold; font-size:12px; margin-right:8px; }}
        .download-btn:hover {{ background:#0369a1; }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1 style="margin:0 0 4px 0; color:#38bdf8;">📐 {title}</h1>
            <p style="margin:0; color:#94a3b8;">{meta['tagline']}</p>
        </div>
        <div>
            <span class="badge">{meta['stem_domain']}</span>
            <span class="badge">ISO 10303 STEP</span>
            <span class="badge">STL 3D</span>
        </div>
    </div>

    <div class="drawing-box">
        {svg_content}
    </div>

    <div style="margin-bottom:24px;">
        <a class="download-btn" href="/artifacts/art/{uid}.step" download>💾 Download ISO STEP (.step)</a>
        <a class="download-btn" href="/artifacts/art/{uid}.stl" download>🖨️ Download Mesh STL (.stl)</a>
        <a class="download-btn" href="/artifacts/art/{uid}.py" download>🐍 FreeCAD Script (.py)</a>
        <a class="download-btn" href="/artifacts/art/{uid}_drawing.svg" download>📐 Vector Blueprint (.svg)</a>
    </div>

    <div class="grid">
        <div class="card">
            <h3 style="margin-top:0; color:#10b981;">Parametric Specifications</h3>
            <table style="width:100%; border-collapse:collapse; font-size:13px; font-family:monospace;">
                <tr><td style="color:#64748b; padding:4px 0;">Volume:</td><td style="color:#f8fafc;">{meta.get('volume_mm3'):,.1f} mm³</td></tr>
                <tr><td style="color:#64748b; padding:4px 0;">Surface Area:</td><td style="color:#f8fafc;">{meta.get('surface_area_mm2'):,.1f} mm²</td></tr>
                <tr><td style="color:#64748b; padding:4px 0;">Topological Genus:</td><td style="color:#f8fafc;">g = {meta.get('topological_genus')}</td></tr>
                <tr><td style="color:#64748b; padding:4px 0;">Euler Characteristic:</td><td style="color:#f8fafc;">χ = {2 - 2*meta.get('topological_genus', 1)}</td></tr>
                <tr><td style="color:#64748b; padding:4px 0;">Governing Formula:</td><td style="color:#fbbf24;">{meta.get('formula_latex')}</td></tr>
            </table>
        </div>
        <div class="card">
            <h3 style="margin-top:0; color:#a855f7;">FreeCAD 1.1 Python Source</h3>
            <pre><code>{py_code}</code></pre>
        </div>
    </div>
</body>
</html>"""

    def _generate_cad_markdown(
        self,
        meta: Dict[str, Any],
        uid: str,
        title: str,
        seed: Optional[DifferentialSeed],
        step_file: str,
        stl_file: str,
        svg_file: str,
        py_file: str,
    ) -> str:
        """Generates formal Markdown deliverable for the CAD model."""
        return fr"""# 📐 ClothOS Sovereign STEM CAD: {title}
- **Identifier**: `{uid}`
- **Medium**: `Parametric 3D CAD Solid Model (ISO 10303)`
- **STEM Domain**: `{meta['stem_domain']}`
- **Archetype**: `{meta['archetype']}`
- **Created**: `{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}`

> "{meta['tagline']}"

---

### Governing Physical & Mathematical Law
```latex
{meta['formula_latex']}
```

### Physical & Topological Invariants
- **Solid Volume ($V$)**: `{meta.get('volume_mm3'):,.1f} mm³`
- **Surface Area ($A$)**: `{meta.get('surface_area_mm2'):,.1f} mm²`
- **Topological Genus ($g$)**: `{meta.get('topological_genus')}`
- **Euler Characteristic ($\chi = V - E + F$)**: `{2 - 2 * meta.get('topological_genus', 1)}`
- **Face Count**: `{meta.get('face_count')}`

### Differential Provenance
- **Seeded By**: `{seed.prior_id if seed else "Direct Operator Genesis"}`
- **Entropy Delta ($\Delta H$)**: `{f"{seed.delta_entropy:+.4f} bits" if seed else "0.00"}`
- **Frequency Delta ($\Delta f_0$)**: `{f"{seed.delta_frequency:+.2f} Hz" if seed else "0.00"}`
- **Deterministic Seed**: `{seed.seed_hash[:16] if seed else "INDEPENDENT"}`

### Downloadable Engineering Artifacts
- **ISO 10303 STEP Exchange Solid**: [`{step_file}`](../../artifacts/art/{step_file})
- **Triangulated Surface Mesh STL**: [`{stl_file}`](../../artifacts/art/{stl_file})
- **Technical Drawing Blueprint SVG**: [`{svg_file}`](../../artifacts/art/{svg_file})
- **FreeCAD 1.1 Parametric Script**: [`{py_file}`](../../artifacts/art/{py_file})
"""


# =============================================================================
# 5. STEM Technical SVG Engine
# =============================================================================

class StemSvgEngine:
    """
    Synthesizes precision 2D technical vector SVG drawings strictly within STEM disciplines:
    - Smith Chart RF Impedance & Scattering Trajectory
    - Symplectic Poincare Section & Hamiltonian Phase Portrait
    - Chiral Auxetic Mechanical Metamaterial Lattice
    - Stokes Circulation & Magnetic Vector Potential Flux Lines
    - Carnot-Stirling Thermodynamic Cycle Diagrams
    """

    ARCHETYPES = [
        "SMITH_CHART_RF",
        "SYMPLECTIC_POINCARE_SECTION",
        "CHIRAL_AUXETIC_METAMATERIAL",
        "STOKES_MAGNETIC_CIRCULATION",
        "CARNOT_THERMODYNAMICS",
    ]

    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = workspace_root or WORKSPACE_ROOT
        self.art_dir = self.workspace_root / "artifacts" / "art"
        self.deliverable_dir = self.workspace_root / "deliverables" / "art"
        self.art_dir.mkdir(parents=True, exist_ok=True)
        self.deliverable_dir.mkdir(parents=True, exist_ok=True)

    def generate_stem_svg(
        self,
        seed: Optional[DifferentialSeed] = None,
        archetype: Optional[str] = None,
        title: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generates a precision STEM SVG schematic and saves artifacts."""
        target_arch = archetype
        if not target_arch or target_arch not in self.ARCHETYPES:
            if seed:
                target_arch = self.ARCHETYPES[seed.seed_int % len(self.ARCHETYPES)]
            else:
                target_arch = random.choice(self.ARCHETYPES)

        uid = f"SVG_STEM_{int(time.time())}_{random.randint(1000, 9999)}"
        timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        f_0 = seed.next_target_freq if seed else 432.0
        sym_r = seed.next_target_symmetry if seed else 0.85
        h_ent = seed.next_target_entropy if seed else 3.5

        svg_content, meta = self._render_stem_svg_content(target_arch, uid, f_0, sym_r, h_ent, seed)
        final_title = title or meta["title"]

        svg_filename = f"{uid}.svg"
        html_filename = f"{uid}.html"
        md_filename = f"{uid}.md"

        svg_path = self.art_dir / svg_filename
        html_path = self.art_dir / html_filename
        md_path = self.deliverable_dir / md_filename

        svg_path.write_text(svg_content, encoding="utf-8")

        html_content = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>{final_title}</title></head>
<body style="margin:0; background:#030712; padding:24px; color:#f8fafc; font-family:system-ui; display:flex; flex-direction:column; align-items:center;">
    <h1 style="color:#38bdf8; margin:0 0 6px 0;">📐 {final_title}</h1>
    <p style="color:#94a3b8; margin:0 0 16px 0;">{meta['tagline']}</p>
    <div style="max-width:900px; width:100%; border-radius:12px; overflow:hidden; box-shadow:0 12px 40px rgba(0,0,0,0.8); border:1px solid #1e293b;">
        {svg_content}
    </div>
</body>
</html>"""
        html_path.write_text(html_content, encoding="utf-8")

        md_content = f"""# 📐 ClothOS Sovereign STEM Drawing: {final_title}
- **Identifier**: `{uid}`
- **Medium**: `Precision STEM Vector Drawing (.svg)`
- **STEM Domain**: `{meta['stem_domain']}`
- **Governing Law**: `{meta['formula_latex']}`

> "{meta['tagline']}"

### Interactive Artifacts
- **Vector SVG**: [`{svg_filename}`](../../artifacts/art/{svg_filename})
- **Inspection Canvas**: [`{html_filename}`](../../artifacts/art/{html_filename})
"""
        md_path.write_text(md_content, encoding="utf-8")

        return {
            "id": uid,
            "title": final_title,
            "medium": "svg_stem",
            "archetype": target_arch,
            "tagline": meta["tagline"],
            "timestamp": timestamp_str,
            "epoch": time.time(),
            "stem_domain": meta["stem_domain"],
            "formula_latex": meta["formula_latex"],
            "svg_file": str(svg_path.relative_to(self.workspace_root)).replace("\\", "/"),
            "html_file": str(html_path.relative_to(self.workspace_root)).replace("\\", "/"),
            "md_file": str(md_path.relative_to(self.workspace_root)).replace("\\", "/"),
            "preview_url": f"/artifacts/art/{html_filename}",
            "svg_preview": svg_content,
        }

    def _render_stem_svg_content(
        self,
        archetype: str,
        uid: str,
        freq_mhz: float,
        symmetry_r: float,
        entropy: float,
        seed: Optional[DifferentialSeed],
    ) -> Tuple[str, Dict[str, Any]]:
        """Renders exact mathematical/physical diagrams in SVG."""
        w, h = 900, 900
        cx, cy = w // 2, h // 2

        if archetype == "SMITH_CHART_RF":
            meta = {
                "title": f"Smith Chart RF Complex Impedance Mapping (f_0 = {freq_mhz:.1f} MHz)",
                "archetype": archetype,
                "stem_domain": "Electromagnetics",
                "tagline": "Bilinear Transformation Gamma = (Z - Z_0)/(Z + Z_0) and Constant Resistance Orbits",
                "formula_latex": r"\Gamma = \frac{z - 1}{z + 1}, \quad \left(u - \frac{r}{1+r}\right)^2 + v^2 = \left(\frac{1}{1+r}\right)^2",
            }
            R_outer = 350
            chart_elems = [
                f'<circle cx="{cx}" cy="{cy}" r="{R_outer}" fill="#050b14" stroke="#38bdf8" stroke-width="2"/>',
                f'<line x1="{cx-R_outer}" y1="{cy}" x2="{cx+R_outer}" y2="{cy}" stroke="#64748b" stroke-width="1.5"/>',
            ]
            for r_val in [0.2, 0.5, 1.0, 2.0, 5.0]:
                rc_rad = R_outer / (1.0 + r_val)
                rc_x = (cx + R_outer) - rc_rad
                chart_elems.append(f'<circle cx="{rc_x:.1f}" cy="{cy}" r="{rc_rad:.1f}" fill="none" stroke="#0ea5e9" stroke-width="1" opacity="0.6"/>')
                chart_elems.append(f'<text x="{rc_x - rc_rad + 4:.1f}" y="{cy-4}" fill="#0ea5e9" font-size="9" font-family="monospace">r={r_val}</text>')

            spiral_pts = []
            steps = 80
            for i in range(steps):
                t = i / steps
                omega = 2.0 * math.pi * t * 3.0
                rad = R_outer * (0.85 - 0.7 * t)
                sx = cx + rad * math.cos(omega)
                sy = cy + rad * math.sin(omega)
                spiral_pts.append(f"{sx:.1f},{sy:.1f}")
            chart_elems.append(f'<polyline points="{" ".join(spiral_pts)}" fill="none" stroke="#f43f5e" stroke-width="2.5"/>')
            chart_elems.append(f'<text x="50" y="70" fill="#f8fafc" font-size="20" font-weight="bold">SMITH CHART RF COMPLEX IMPEDANCE</text>')
            chart_elems.append(f'<text x="50" y="95" fill="#38bdf8" font-size="12" font-family="monospace">f_0 = {freq_mhz:.1f} MHz | Γ = (z - 1)/(z + 1) | VSWR = {1.0 / max(0.01, 1.0 - symmetry_r):.2f}</text>')

        elif archetype == "SYMPLECTIC_POINCARE_SECTION":
            meta = {
                "title": f"Symplectic Poincaré Phase Space Section (Invariant 2-Form ω = dp ∧ dq)",
                "archetype": archetype,
                "stem_domain": "Symplectic_Mechanics",
                "tagline": "Hamiltonian Phase Flow Preserving Liouville Phase Volume with KAM Stability Islands",
                "formula_latex": r"\omega = dp \wedge dq, \quad \frac{dq}{dt} = \frac{\partial H}{\partial p}, \quad \frac{dp}{dt} = -\frac{\partial H}{\partial q}",
            }
            chart_elems = [
                f'<rect width="{w}" height="{h}" fill="#030712"/>',
                f'<line x1="{cx}" y1="50" x2="{cx}" y2="{h-50}" stroke="#334155" stroke-width="1"/>',
                f'<line x1="50" y1="{cy}" x2="{w-50}" y2="{cy}" stroke="#334155" stroke-width="1"/>',
            ]
            K = 0.971635
            colors = ["#38bdf8", "#10b981", "#f59e0b", "#a855f7", "#ec4899", "#06b6d4"]
            for init_idx, p_init in enumerate([0.1, 0.35, 0.6, 0.85, 1.2, 1.5]):
                col = colors[init_idx % len(colors)]
                q, p = 0.5, p_init
                pts = []
                for _ in range(120):
                    p = (p + K * math.sin(q)) % (2 * math.pi)
                    q = (q + p) % (2 * math.pi)
                    qx = cx + (q - math.pi) * 55.0
                    py = cy - (p - math.pi) * 55.0
                    pts.append(f'<circle cx="{qx:.1f}" cy="{py:.1f}" r="1.5" fill="{col}" opacity="0.85"/>')
                chart_elems.extend(pts)
            chart_elems.append(f'<text x="50" y="70" fill="#f8fafc" font-size="20" font-weight="bold">SYMPLECTIC POINCARÉ PHASE PORTRAIT</text>')
            chart_elems.append(f'<text x="50" y="95" fill="#38bdf8" font-size="12" font-family="monospace">Liouville Volume Invariant: dω/dt = 0 • Chirikov K = {K:.4f}</text>')

        elif archetype == "CHIRAL_AUXETIC_METAMATERIAL":
            meta = {
                "title": f"Chiral Auxetic Mechanical Metamaterial (Poisson Ratio ν = -0.68)",
                "archetype": archetype,
                "stem_domain": "Compliant_Flexures",
                "tagline": "Negative Poisson's Ratio Lattice with Symmetrical Rotating Chiral Nodes",
                "formula_latex": r"\nu = -\frac{\varepsilon_{\text{trans}}}{\varepsilon_{\text{axial}}} < 0, \quad \theta_{\text{rotation}} = \arcsin\left(\frac{L - d}{2R}\right)",
            }
            chart_elems = [f'<rect width="{w}" height="{h}" fill="#030712"/>']
            grid_n = 5
            spacing = 130
            start_x = cx - (grid_n - 1) * spacing // 2
            start_y = cy - (grid_n - 1) * spacing // 2
            r_node = 24
            for i in range(grid_n):
                for j in range(grid_n):
                    nx = start_x + i * spacing
                    ny = start_y + j * spacing
                    chart_elems.append(f'<circle cx="{nx}" cy="{ny}" r="{r_node}" fill="#0f172a" stroke="#38bdf8" stroke-width="2"/>')
                    if i < grid_n - 1:
                        chart_elems.append(f'<line x1="{nx}" y1="{ny-r_node}" x2="{nx+spacing}" y2="{ny-r_node}" stroke="#10b981" stroke-width="2.5"/>')
                    if j < grid_n - 1:
                        chart_elems.append(f'<line x1="{nx+r_node}" y1="{ny}" x2="{nx+r_node}" y2="{ny+spacing}" stroke="#10b981" stroke-width="2.5"/>')
                    chart_elems.append(f'<circle cx="{nx}" cy="{ny}" r="4" fill="#fbbf24"/>')
            chart_elems.append(f'<text x="50" y="70" fill="#f8fafc" font-size="20" font-weight="bold">CHIRAL AUXETIC METAMATERIAL LATTICE</text>')
            chart_elems.append(f'<text x="50" y="95" fill="#38bdf8" font-size="12" font-family="monospace">Negative Poisson Ratio ν = -0.68 • Bilateral Expansion Under Tension</text>')

        elif archetype == "STOKES_MAGNETIC_CIRCULATION":
            meta = {
                "title": f"Stokes Circulation & Magnetic Vector Potential (A)",
                "archetype": archetype,
                "stem_domain": "Electromagnetics",
                "tagline": "Contour Circulation of Vector Potential Equal to Magnetic Flux Surface Integral",
                "formula_latex": r"\oint_{\partial \Sigma} \mathbf{A} \cdot d\mathbf{l} = \iint_{\Sigma} (\nabla \times \mathbf{A}) \cdot d\mathbf{S} = \Phi_B",
            }
            chart_elems = [f'<rect width="{w}" height="{h}" fill="#030712"/>']
            for rad in range(60, 360, 45):
                chart_elems.append(f'<circle cx="{cx}" cy="{cy}" r="{rad}" fill="none" stroke="#38bdf8" stroke-width="1.5" stroke-dasharray="6,4" opacity="0.7"/>')
            for rad in [150, 240, 330]:
                for deg in range(0, 360, 45):
                    rad_a = math.radians(deg)
                    vx = cx + rad * math.cos(rad_a)
                    vy = cy + rad * math.sin(rad_a)
                    dx = -25.0 * math.sin(rad_a)
                    dy = 25.0 * math.cos(rad_a)
                    chart_elems.append(f'<line x1="{vx}" y1="{vy}" x2="{vx+dx}" y2="{vy+dy}" stroke="#f59e0b" stroke-width="2"/>')
            chart_elems.append(f'<circle cx="{cx}" cy="{cy}" r="32" fill="#ef4444" opacity="0.85"/>')
            chart_elems.append(f'<text x="{cx}" y="{cy+5}" fill="#ffffff" font-size="13" font-weight="bold" text-anchor="middle">B ⊙</text>')
            chart_elems.append(f'<text x="50" y="70" fill="#f8fafc" font-size="20" font-weight="bold">STOKES CIRCULATION &amp; VECTOR POTENTIAL</text>')
            chart_elems.append(f'<text x="50" y="95" fill="#38bdf8" font-size="12" font-family="monospace">∮ A · dl = ∬ (∇ × A) · dS = Φ_B • B = curl(A)</text>')

        else:  # CARNOT_THERMODYNAMICS
            meta = {
                "title": f"Carnot-Stirling Thermodynamic Cycle & Landauer Limit",
                "archetype": archetype,
                "stem_domain": "Thermodynamics",
                "tagline": "P-V Indicator Diagram with Isothermal Expansion and Reversible Landauer Dissipation Floor",
                "formula_latex": r"\eta = 1 - \frac{T_C}{T_H}, \quad \Delta E_{\text{bit}} \ge k_B T \ln 2",
            }
            chart_elems = [
                f'<rect width="{w}" height="{h}" fill="#030712"/>',
                f'<line x1="140" y1="120" x2="140" y2="{h-140}" stroke="#64748b" stroke-width="2"/>',
                f'<line x1="140" y1="{h-140}" x2="{w-120}" y2="{h-140}" stroke="#64748b" stroke-width="2"/>',
                f'<text x="110" y="140" fill="#f8fafc" font-size="16" font-family="monospace">P (Pressure)</text>',
                f'<text x="{w-180}" y="{h-110}" fill="#f8fafc" font-size="16" font-family="monospace">V (Volume)</text>',
            ]
            p1 = (240, 240)
            p2 = (560, 360)
            p3 = (720, 560)
            p4 = (380, 480)
            chart_elems.append(f'<path d="M {p1[0]} {p1[1]} Q 400 280 {p2[0]} {p2[1]} Q 650 450 {p3[0]} {p3[1]} Q 540 540 {p4[0]} {p4[1]} Q 300 370 {p1[0]} {p1[1]}" fill="rgba(56, 189, 248, 0.15)" stroke="#38bdf8" stroke-width="3"/>')
            chart_elems.append(f'<text x="360" y="270" fill="#f59e0b" font-size="13" font-family="monospace">Isotherm (T_H = 340 K)</text>')
            chart_elems.append(f'<text x="490" y="540" fill="#06b6d4" font-size="13" font-family="monospace">Isotherm (T_C = 295 K)</text>')
            chart_elems.append(f'<text x="50" y="70" fill="#f8fafc" font-size="20" font-weight="bold">CARNOT THERMODYNAMIC REVERSIBILITY</text>')
            chart_elems.append(f'<text x="50" y="95" fill="#38bdf8" font-size="12" font-family="monospace">Carnot Efficiency η = 13.2% • Landauer Dissipation Floor E = k_B T ln(2)</text>')

        chart_elems.append(f'<text x="50" y="{h-40}" fill="#64748b" font-size="11" font-family="monospace">ClothOS STEM Synthesizer // {uid} // {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</text>')

        svg_str = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="100%">\n' + "\n".join(chart_elems) + '\n</svg>'
        return svg_str, meta


# =============================================================================
# Global Singleton Accessors
# =============================================================================

art_differential_engine = ArtDifferentialEngine()
stem_cad_engine = StemCadEngine()
stem_svg_engine = StemSvgEngine()
