"""
Deliberative Trajectory & Anti-Mode-Collapse Engine (`loom/clothos/deliberation_engine.py`).

Prevents repetitive outputs ("mode collapse" across long autonomous runs) by:
1. Maintaining a persistent Rolling Trajectory Ledger (`data/deliberation_trajectory.json`)
   with monotonic `next_dream_num`, rolling chronological arc summaries, structural signatures,
   and token/shingle similarity indexes across all prior works.
2. Enforcing a multi-stage pipeline:
   Plan (explicit forward-vector brief) -> Deliberate (Llama 70B / Sovereign model with generous
   time budget, quality > speed) -> Novelty Gate (rejects near-duplicate titles, structures, or
   prose) -> Generate -> Critique & Record.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import random
import re
import threading
import time
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

try:
    import psutil
except Exception:
    psutil = None

try:
    import httpx
except Exception:
    httpx = None


_DEFAULT_ROOT = Path(__file__).resolve().parents[2]
_LOCK = threading.RLock()

# Orthogonal creative & STEM domains used to ensure deliberate diversity
CURRICULUM_DOMAINS: List[Tuple[str, str]] = [
    ("Topos & Symplectic Geometry", "visual_art"),
    ("Algorithmic Counterpoint & Just Intonation", "music"),
    ("Cellular Morphogenesis & Turing Patterns", "image"),
    ("Non-Equilibrium Fluid & Magnetohydrodynamics", "animated_video"),
    ("Distributed Thermodynamic Computing Parable", "story"),
    ("Formal Topological Verse & Epistemic Odes", "poetry"),
    ("Deployable Compliant-Mechanism & Fold-Lock CAD", "cad_model"),
    ("Reversible Silicon & Photonic Routing Schematic", "svg_stem"),
    ("Cross-Domain Scientific Discovery Synthesis", "deliverable"),
]

_STOPWORDS: Set[str] = {
    "the", "and", "for", "with", "that", "this", "from", "into", "over", "under",
    "between", "across", "their", "there", "where", "which", "while", "being",
    "clothos", "loom", "fabric", "sovereign", "lminted", "dream", "art", "cycle",
}


def _tokenize_significant(text: str) -> List[str]:
    tokens = re.findall(r"[a-z0-9_]{3,}", (text or "").lower())
    return [t for t in tokens if t not in _STOPWORDS]


def _shingles(tokens: Sequence[str], k: int = 3) -> Set[str]:
    if len(tokens) < k:
        return {" ".join(tokens)} if tokens else set()
    return {" ".join(tokens[i : i + k]) for i in range(len(tokens) - k + 1)}


def compute_text_similarity(a: str, b: str) -> float:
    """Computes blended token + 3-gram Jaccard similarity in [0, 1]."""
    ta = _tokenize_significant(a)
    tb = _tokenize_significant(b)
    if not ta or not tb:
        return 0.0
    sa, sb = set(ta), set(tb)
    tok_jacc = len(sa & sb) / max(1, len(sa | sb))
    sha, shb = _shingles(ta, 3), _shingles(tb, 3)
    sh_jacc = len(sha & shb) / max(1, len(sha | shb))
    return 0.45 * tok_jacc + 0.55 * sh_jacc


def _normalize_title(title: str) -> str:
    cleaned = re.sub(r"lminted\s*dream\s*#?\d+\s*:?", "", (title or "").lower())
    cleaned = re.sub(r"[^a-z0-9]+", " ", cleaned).strip()
    return cleaned


@dataclass
class DeliberationPlan:
    dream_num: int
    medium: str
    title: str
    theme: str
    stem_domain: str
    structural_form: str
    thesis_or_arc: str
    technical_spec: Dict[str, Any] = field(default_factory=dict)
    differentiation_note: str = ""
    model_used: str = "procedural_orthogonal"
    deliberation_seconds: float = 0.0
    planned_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class TrajectoryLedger:
    """
    Persistent rolling memory + novelty index for all ClothOS creative works
    and research deliverables.
    """

    def __init__(self, workspace_root: Optional[Path] = None):
        self.root = Path(workspace_root) if workspace_root else _DEFAULT_ROOT
        self.ledger_path = self.root / "data" / "deliberation_trajectory.json"
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        self._state = self._load_unlocked()

    def _bootstrap_dream_counter(self) -> int:
        highest = 0
        gallery_path = self.root / "artifacts" / "art" / "art_gallery.json"
        if gallery_path.exists():
            try:
                data = json.loads(gallery_path.read_text(encoding="utf-8", errors="ignore"))
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict):
                            dn = item.get("dream_num")
                            if isinstance(dn, int) and dn > highest:
                                highest = dn
                            m = re.search(r"#(\d+)", str(item.get("title", "")))
                            if m:
                                highest = max(highest, int(m.group(1)))
            except Exception:
                pass
        art_dir = self.root / "deliverables" / "art"
        if art_dir.exists():
            try:
                # Sample up to 300 filenames quickly without blocking startup on 100k files
                for idx, entry in enumerate(os.scandir(art_dir)):
                    if idx >= 400:
                        break
                    m = re.search(r"(?:DREAM|LMINT)_(\d+)", entry.name, re.IGNORECASE)
                    if m:
                        highest = max(highest, int(m.group(1)))
            except Exception:
                pass
        return max(highest + 1, 1)

    def _load_unlocked(self) -> Dict[str, Any]:
        with _LOCK:
            if self.ledger_path.exists():
                try:
                    raw = json.loads(self.ledger_path.read_text(encoding="utf-8"))
                    if isinstance(raw, dict):
                        raw.setdefault("next_dream_num", self._bootstrap_dream_counter())
                        raw.setdefault("rolling_summary", "")
                        raw.setdefault("entries", [])
                        raw.setdefault("content_hashes", [])
                        raw.setdefault("title_norms", [])
                        return raw
                except Exception:
                    pass
            return {
                "version": 1,
                "next_dream_num": self._bootstrap_dream_counter(),
                "rolling_summary": "Genesis trajectory initialized. Prioritize diverse domains, orthogonal visual/sonic algorithms, and evolving narrative arcs.",
                "entries": [],
                "content_hashes": [],
                "title_norms": [],
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }

    def reload(self) -> None:
        self._state = self._load_unlocked()

    def _save_unlocked(self) -> None:
        with _LOCK:
            self._state["updated_at"] = datetime.now(timezone.utc).isoformat()
            tmp = self.ledger_path.with_suffix(".tmp")
            tmp.write_text(json.dumps(self._state, indent=2, ensure_ascii=False), encoding="utf-8")
            os.replace(tmp, self.ledger_path)

    def allocate_dream_num(self) -> int:
        with _LOCK:
            self._state = self._load_unlocked()
            dn = int(self._state.get("next_dream_num", 1))
            self._state["next_dream_num"] = dn + 1
            self._save_unlocked()
            return dn

    def check_novelty(
        self,
        title: str,
        body_text: str,
        medium: Optional[str] = None,
        similarity_threshold: float = 0.56,
    ) -> Tuple[bool, str, float]:
        """
        Verifies a proposed work is genuinely distinct from prior works.
        Returns `(is_unique, reason, max_similarity)`.
        """
        with _LOCK:
            norm_t = _normalize_title(title)
            title_norms = set(self._state.get("title_norms", []))
            if norm_t and norm_t in title_norms:
                return False, f"Title collision with prior work ('{norm_t}')", 1.0

            clean_body = (body_text or "").strip()
            body_hash = hashlib.sha256(clean_body.encode("utf-8", errors="ignore")).hexdigest()
            if clean_body and body_hash in set(self._state.get("content_hashes", [])):
                return False, f"Exact SHA-256 duplicate content ({body_hash[:12]})", 1.0

            entries = self._state.get("entries", [])
            recent_same = [
                e for e in entries[-120:]
                if not medium or e.get("medium") == medium
            ][-40:]
            compare_pool = recent_same + entries[-15:]

            max_sim = 0.0
            worst_match = ""
            probe = f"{norm_t} {clean_body[:2500]}"
            for prev in compare_pool:
                prev_probe = f"{prev.get('title_norm', '')} {prev.get('excerpt', '')}"
                sim = compute_text_similarity(probe, prev_probe)
                if sim > max_sim:
                    max_sim = sim
                    worst_match = prev.get("title", prev.get("id", "unknown"))

            if max_sim >= similarity_threshold:
                return False, f"Too similar ({max_sim:.2f} >= {similarity_threshold:.2f}) to '{worst_match}'", max_sim

            return True, "Unique relative to trajectory history", max_sim

    def record_work(
        self,
        work_id: str,
        title: str,
        medium: str,
        theme: str,
        body_text: str,
        structural_form: str = "",
        file_paths: Optional[List[str]] = None,
        deliberation_seconds: float = 0.0,
        teacher_score: Optional[float] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        with _LOCK:
            self._state = self._load_unlocked()
            norm_t = _normalize_title(title)
            digest = hashlib.sha256((body_text or title).encode("utf-8", errors="ignore")).hexdigest()

            title_norms: List[str] = self._state.setdefault("title_norms", [])
            if norm_t and norm_t not in title_norms:
                title_norms.append(norm_t)
                if len(title_norms) > 5000:
                    del title_norms[:-4000]

            hashes: List[str] = self._state.setdefault("content_hashes", [])
            if digest not in hashes:
                hashes.append(digest)
                if len(hashes) > 8000:
                    del hashes[:-6000]

            excerpt = re.sub(r"\s+", " ", (body_text or "").strip())[:700]
            entry = {
                "id": work_id,
                "title": title,
                "title_norm": norm_t,
                "medium": medium,
                "theme": theme,
                "structural_form": structural_form,
                "excerpt": excerpt,
                "sha256": digest,
                "files": file_paths or [],
                "deliberation_seconds": round(deliberation_seconds, 2),
                "teacher_score": teacher_score,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            if extra:
                entry["extra"] = extra

            entries: List[Dict[str, Any]] = self._state.setdefault("entries", [])
            entries.append(entry)
            if len(entries) > 600:
                del entries[:-500]

            self._update_rolling_summary_unlocked()
            self._save_unlocked()
            return entry

    def _update_rolling_summary_unlocked(self) -> None:
        entries = self._state.get("entries", [])
        if not entries:
            return
        recent = entries[-14:]
        medium_counts: Dict[str, int] = {}
        for e in entries[-50:]:
            m = str(e.get("medium", "unknown"))
            medium_counts[m] = medium_counts.get(m, 0) + 1

        arcs = [
            f"[{e.get('medium')}] {e.get('title')} (form={e.get('structural_form') or 'free'}, theme={str(e.get('theme', ''))[:60]})"
            for e in recent[-8:]
        ]
        summary = (
            f"Completed works tracked: {len(entries)} (next dream #{self._state.get('next_dream_num', 1)}). "
            f"Recent medium distribution: {json.dumps(medium_counts)}. "
            f"Most recent trajectory beats (MUST NOT repeat these titles, imagery, or templates):\n- "
            + "\n- ".join(arcs)
        )
        self._state["rolling_summary"] = summary[:2200]

    def get_trajectory_brief(self) -> Dict[str, Any]:
        with _LOCK:
            self._state = self._load_unlocked()
            recent = self._state.get("entries", [])[-12:]
            recent_mediums = [e.get("medium") for e in recent[-5:]]
            recent_forms = [e.get("structural_form") for e in recent if e.get("structural_form")]
            return {
                "next_dream_num": int(self._state.get("next_dream_num", 1)),
                "total_recorded": len(self._state.get("entries", [])),
                "rolling_summary": self._state.get("rolling_summary", ""),
                "recent_titles": [e.get("title") for e in recent],
                "recent_mediums": recent_mediums,
                "recent_forms": recent_forms,
            }


def _select_deliberation_model(prefer_teacher: bool = False) -> str:
    """
    Chooses best local Ollama model respecting VRAM fit, RAM headroom, and warm `/api/ps` models.
    - `prefer_teacher=True` targets `llama3.3:70b` / `loom-sovereign:latest` for deep synthesis/distillation.
    - `prefer_teacher=False` prefers warm-loaded models first, then VRAM-resident 7B-14B models on RTX 3060.
    """
    ordered = (
        ["llama3.3:70b", "loom-70b:latest", "loom-sovereign:latest", "qwen2.5:32b", "deepseek-r1:14b", "qwen2.5:7b"]
        if prefer_teacher
        else ["loom-sovereign-fast:latest", "qwen2.5:7b", "deepseek-r1:14b", "loom-sovereign:latest", "qwen2.5:32b"]
    )
    if httpx is None:
        return "procedural_orthogonal"

    ram_avail_gb = 32.0
    if psutil is not None:
        try:
            ram_avail_gb = psutil.virtual_memory().available / (1024 ** 3)
        except Exception:
            pass

    try:
        with httpx.Client(timeout=2.5) as client:
            # Prefer already warm-loaded model in VRAM/RAM to prevent cold-swap stalls
            try:
                ps_resp = client.get("http://127.0.0.1:11434/api/ps")
                if ps_resp.status_code == 200:
                    running = {m.get("name") for m in ps_resp.json().get("models", []) if isinstance(m, dict)}
                    for cand in ordered:
                        if cand in running:
                            return cand
            except Exception:
                pass

            resp = client.get("http://127.0.0.1:11434/api/tags")
            if resp.status_code != 200:
                return "procedural_orthogonal"
            installed = {m.get("name") for m in resp.json().get("models", []) if isinstance(m, dict)}
            for cand in ordered:
                if cand in installed:
                    if "70b" in cand and (not prefer_teacher or ram_avail_gb < 22.0):
                        continue
                    if "32b" in cand and ram_avail_gb < 14.0:
                        continue
                    return cand
            return next(iter(installed), "procedural_orthogonal")
    except Exception:
        return "procedural_orthogonal"


def _query_ollama_json(
    model: str,
    prompt: str,
    timeout_s: float = 180.0,
    temperature: float = 0.85,
    num_predict: int = 900,
) -> Optional[Dict[str, Any]]:
    if httpx is None or model == "procedural_orthogonal":
        return None
    try:
        with httpx.Client(timeout=timeout_s) as client:
            r = client.post(
                "http://127.0.0.1:11434/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                    "options": {"temperature": temperature, "num_predict": num_predict},
                },
            )
            if r.status_code != 200:
                return None
            raw = r.json().get("response", "").strip()
            cleaned = re.sub(r"^```(?:json)?|```$", "", raw, flags=re.MULTILINE).strip()
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            return json.loads(cleaned)
    except Exception:
        return None


def _query_ollama_text(
    model: str,
    prompt: str,
    timeout_s: float = 240.0,
    temperature: float = 0.82,
    num_predict: int = 1600,
) -> Optional[str]:
    if httpx is None or model == "procedural_orthogonal":
        return None
    try:
        with httpx.Client(timeout=timeout_s) as client:
            r = client.post(
                "http://127.0.0.1:11434/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": temperature, "num_predict": num_predict},
                },
            )
            if r.status_code != 200:
                return None
            return r.json().get("response", "").strip() or None
    except Exception:
        return None


# Rich orthogonal seed pools for deterministic yet high-diversity offline/assisted planning
_MUSIC_MODES = ["Lydian_432", "Dorian_Nocturne", "Phrygian_Modal", "Pentatonic_Zen", "Just_Intonation_Lattice", "Harmonic_Minor_Baroque", "Mixolydian_Solar"]
_IMAGE_ENGINES = ["gray_scott_reaction_diffusion", "clifford_dejong_attractor", "chladni_spectral_plate", "domain_warped_fbm", "julia_holomorphic_fractal", "symplectic_phyllotaxis_orbit", "geometric_fingerprint_stgnn"]
_VIDEO_ENGINES = ["attractor_morph", "lorenz_3d_projection", "wave_interference", "boids_flocking", "neural_pulsar_field"]
_STORY_SETTINGS = [
    "Subglacial ocean acoustic observatory under Europa",
    "Tidal geothermal library carved inside basalt sea stacks",
    "High-altitude stratigraphic seed vault powered by wind harps",
    "Desert aerogel solar condenser listening to atmospheric whistlers",
    "Benthic hydrothermal cable relay node tended by autonomous gliders",
    "Archival astronomical clocktower synchronizing pulsar timing arrays",
    "Floating mangrove phytoremediation barge along an estuary delta",
    "Deep-borehole neutrino scintillator cavern beneath granite bedrock",
]
_STORY_CONFLICTS = [
    "calibrating a drifting phase reference without losing historical calibration lineage",
    "reconciling conflicting sensor memories from two storm-separated autonomous relays",
    "translating non-stationary seismic harmonics into early tsunami warning geometry",
    "discovering an unexpected biological symbiosis altering copper patina conductivity",
    "restoring archival magnetic tapes degraded by solar proton event bursts",
    "designing an origami mirror array that survives katabatic shear winds",
]
_POETRY_FORMS = ["Terza Rima Topological", "Sapphic Stanza Counterpoint", "Algorithmic Villancico", "Axiomatic Haibun", "Symmetric Ghazal", "Syllabic Fibonacci Ode"]


class DeliberativeCreator:
    """
    Plans, deliberates, novelty-checks, generates, and critiques unique works.
    Speed is explicitly secondary to deliberative depth and structural uniqueness.
    """

    def __init__(self, workspace_root: Optional[Path] = None):
        self.root = Path(workspace_root) if workspace_root else _DEFAULT_ROOT
        self.ledger = TrajectoryLedger(self.root)

    def choose_next_medium(self, requested: Optional[str] = None, exclude_recent: bool = True) -> str:
        valid = ["music", "animated_video", "image", "visual_art", "story", "poetry", "cad_model", "svg_stem"]
        if requested:
            norm = requested.strip().lower()
            aliases = {"video": "animated_video", "img": "image", "picture": "image", "png": "image", "audio": "music", "cad": "cad_model"}
            return aliases.get(norm, norm if norm in valid else "visual_art")

        brief = self.ledger.get_trajectory_brief()
        recent = brief.get("recent_mediums", []) if exclude_recent else []
        candidates = [m for m in valid if m not in recent[-3:]] or valid
        # Slight preference weight towards rich under-represented mediums
        return random.choice(candidates)

    def deliberate_plan(
        self,
        medium: Optional[str] = None,
        prompt_hint: Optional[str] = None,
        differential_context: Optional[Dict[str, Any]] = None,
        prefer_teacher: bool = False,
        timeout_s: float = 180.0,
        use_llm: bool = True,
    ) -> DeliberationPlan:
        """
        Stage 1 & 2: Formulates an explicit forward-vector creative/research plan
        with rolling-memory awareness and retries if similarity is too close to prior work.
        """
        t0 = time.monotonic()
        chosen_medium = self.choose_next_medium(medium)
        dream_num = self.ledger.allocate_dream_num()
        brief = self.ledger.get_trajectory_brief()

        model = _select_deliberation_model(prefer_teacher=prefer_teacher) if use_llm else "procedural_orthogonal"
        avoid_forms = set(brief.get("recent_forms", [])[-5:])

        plan: Optional[DeliberationPlan] = None
        rejection_notes: List[str] = []

        for attempt in range(3):
            spec_hint = self._build_orthogonal_spec(chosen_medium, dream_num + attempt * 17, avoid_forms, differential_context)
            llm_plan = None

            if model != "procedural_orthogonal":
                diff_txt = json.dumps(differential_context or {}, default=str)[:500]
                reject_txt = f"\nPrevious draft rejected because: {'; '.join(rejection_notes)}" if rejection_notes else ""
                prompt = f"""You are ClothOS Deliberative Planner creating UNIQUE Artifact #{dream_num}.
Quality and genuine originality matter far more than speed.

ROLLING TRAJECTORY MEMORY (DO NOT REPEAT ANY PRIOR TITLE, PLOT, MOTIF, OR PARAMETER SET):
{brief.get('rolling_summary', 'None')}

ASSIGNED MEDIUM: {chosen_medium}
USER/SYSTEM HINT: {prompt_hint or 'Synthesize an original high-craft scientific, ecological, or artistic artifact'}
DIFFERENTIAL SIGNAL CONTEXT: {diff_txt}
SUGGESTED STRUCTURAL ENGINE: {json.dumps(spec_hint)}{reject_txt}

Return strictly JSON:
{{
  "title": "A vivid, concrete, unique title (NO clichés like 'Dual Cores', 'Sacred Symphony', or 'Oort Cloud')",
  "theme": "Specific conceptual thesis or subject",
  "stem_domain": "Concrete scientific or artistic discipline",
  "structural_form": "Specific form/algorithm/structure name",
  "thesis_or_arc": "2-4 sentence architectural plan describing beginning, development, and resolution/discovery",
  "differentiation_note": "How this diverges sharply from the prior works listed above",
  "technical_spec": {{}}
}}"""
                llm_plan = _query_ollama_json(model, prompt, timeout_s=timeout_s, temperature=0.88 + attempt * 0.04, num_predict=700)
                if not llm_plan:
                    # Do not retry a timed-out/unresponsive LLM across subsequent novelty attempts
                    model = "procedural_orthogonal"

            if llm_plan and llm_plan.get("title"):
                tech = dict(spec_hint)
                if isinstance(llm_plan.get("technical_spec"), dict):
                    tech.update(llm_plan["technical_spec"])
                cand = DeliberationPlan(
                    dream_num=dream_num,
                    medium=chosen_medium,
                    title=str(llm_plan["title"]).strip()[:140],
                    theme=str(llm_plan.get("theme") or "Original Sovereign Synthesis").strip()[:240],
                    stem_domain=str(llm_plan.get("stem_domain") or spec_hint.get("stem_domain", "Computational Naturalism")).strip()[:120],
                    structural_form=str(llm_plan.get("structural_form") or spec_hint.get("algorithm", chosen_medium)).strip()[:120],
                    thesis_or_arc=str(llm_plan.get("thesis_or_arc") or "").strip()[:800],
                    technical_spec=tech,
                    differentiation_note=str(llm_plan.get("differentiation_note") or "LLM deliberated orthogonal trajectory").strip()[:400],
                    model_used=model,
                    deliberation_seconds=round(time.monotonic() - t0, 2),
                )
            else:
                cand = self._procedural_plan(
                    dream_num=dream_num,
                    attempt=attempt,
                    medium=chosen_medium,
                    prompt_hint=prompt_hint,
                    spec_hint=spec_hint,
                    differential_context=differential_context,
                    elapsed_s=round(time.monotonic() - t0, 2),
                )

            ok, reason, sim = self.ledger.check_novelty(
                cand.title,
                f"{cand.theme} {cand.structural_form} {cand.thesis_or_arc}",
                medium=chosen_medium,
                similarity_threshold=0.55,
            )
            if ok:
                plan = cand
                break
            rejection_notes.append(f"Attempt {attempt + 1} ('{cand.title}'): {reason} (sim={sim:.2f})")
            avoid_forms.add(cand.structural_form)

        if plan is None:
            # Force salt differentiation on final fallback
            salt_hex = hashlib.sha256(f"{dream_num}:{time.time_ns()}:{random.random()}".encode()).hexdigest()[:6].upper()
            spec_hint = self._build_orthogonal_spec(chosen_medium, dream_num + 97, avoid_forms, differential_context)
            plan = self._procedural_plan(
                dream_num=dream_num,
                attempt=7,
                medium=chosen_medium,
                prompt_hint=f"{prompt_hint or ''} [Trajectory {salt_hex}]".strip(),
                spec_hint=spec_hint,
                differential_context=differential_context,
                elapsed_s=round(time.monotonic() - t0, 2),
            )
        return plan

    def _build_orthogonal_spec(
        self,
        medium: str,
        seed_val: int,
        avoid_forms: Set[str],
        differential_context: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        rng = random.Random(seed_val ^ int(time.time() * 1000))
        base_freq = 432.0
        if differential_context and isinstance(differential_context.get("next_target_freq"), (int, float)):
            base_freq = float(differential_context["next_target_freq"])
            base_freq = max(180.0, min(640.0, base_freq))

        if medium == "music":
            modes = [m for m in _MUSIC_MODES if m not in avoid_forms] or _MUSIC_MODES
            mode = rng.choice(modes)
            return {
                "algorithm": mode,
                "mode": mode,
                "root_hz": round(base_freq / 2.0, 2),
                "bpm": rng.choice([72, 84, 92, 104, 116, 126]),
                "duration_s": rng.uniform(18.0, 28.0),
                "stem_domain": "Acoustic Signal Processing & Psychoacoustics",
                "seed": rng.randint(1000, 999999),
            }
        if medium in ("image", "visual_art"):
            engs = [e for e in _IMAGE_ENGINES if e not in avoid_forms] or _IMAGE_ENGINES
            eng = rng.choice(engs)
            return {
                "algorithm": eng,
                "width": 1024,
                "height": 1024,
                "palette_hue": round(rng.uniform(0.0, 1.0), 3),
                "stem_domain": "Dynamical Systems & Morphological Rendering",
                "seed": rng.randint(1000, 999999),
            }
        if medium == "animated_video":
            engs = [e for e in _VIDEO_ENGINES if e not in avoid_forms] or _VIDEO_ENGINES
            eng = rng.choice(engs)
            return {
                "algorithm": eng,
                "fps": 24,
                "duration_s": 5.0,
                "width": 512,
                "height": 512,
                "stem_domain": "Time-Evolving Continuum Mechanics",
                "seed": rng.randint(1000, 999999),
            }
        if medium == "story":
            setting = rng.choice(_STORY_SETTINGS)
            conflict = rng.choice(_STORY_CONFLICTS)
            return {
                "algorithm": setting[:48],
                "setting": setting,
                "conflict": conflict,
                "stem_domain": "Speculative Scientific Literature",
                "seed": rng.randint(1000, 999999),
            }
        if medium == "poetry":
            form = rng.choice([f for f in _POETRY_FORMS if f not in avoid_forms] or _POETRY_FORMS)
            return {
                "algorithm": form,
                "form": form,
                "stem_domain": "Formal Prosody & Symbolic Dynamics",
                "seed": rng.randint(1000, 999999),
            }
        return {
            "algorithm": f"stem_{medium}_{rng.randint(100, 999)}",
            "stem_domain": "Parametric Engineering & Topological CAD",
            "seed": rng.randint(1000, 999999),
        }

    def _procedural_plan(
        self,
        dream_num: int,
        attempt: int,
        medium: str,
        prompt_hint: Optional[str],
        spec_hint: Dict[str, Any],
        differential_context: Optional[Dict[str, Any]],
        elapsed_s: float,
    ) -> DeliberationPlan:
        rng = random.Random(dream_num * 997 + attempt * 31 + int(spec_hint.get("seed", 1)))
        adjs = ["Basalt", "Pelagic", "Boreal", "Isotropic", "Aeolian", "Bragg", "Holomorphic", "Diurnal", "Crystalline", "Catabatic", "Tidal", "Spectral", "Geodesic", "Stratified", "Mycelial", "Solsticial"]
        nouns = ["Nocturne", "Lattice", "Chronicle", "Canticle", "Manifold", "Bathymetry", "Trajectory", "Equilibrium", "Refractory", "Compass", "Aperture", "Fugue", "Observatory", "Monograph", "Horizon", "Resonator"]
        algo = str(spec_hint.get("algorithm", medium))
        suffix = f" ({prompt_hint[:28].strip()})" if prompt_hint and len(prompt_hint.strip()) > 3 else f" [{algo.replace('_', ' ').title()}]"
        title = f"{rng.choice(adjs)} {rng.choice(nouns)} No.{dream_num}{suffix}"

        hint_text = (prompt_hint or "").strip()
        if medium == "story":
            theme = hint_text or f"{spec_hint.get('setting')} — {spec_hint.get('conflict')}"
            arc = (
                f"Set in {spec_hint.get('setting')}, an engineer-protagonist confronts {spec_hint.get('conflict')}, "
                f"measuring empirical drifts across instruments before synthesizing a stable reversible configuration."
            )
        elif medium == "music":
            theme = hint_text or f"Multi-movement {spec_hint.get('mode')} acoustic study at {spec_hint.get('bpm')} BPM ({spec_hint.get('root_hz')} Hz root)"
            arc = f"Moves through exposition, modal harmonic development, spatial reverb bloom, and tonic settlement in {spec_hint.get('mode')}."
        elif medium in ("image", "visual_art"):
            theme = hint_text or f"High-resolution {algo.replace('_', ' ')} mathematical field"
            arc = f"Computes continuous field topology with spectral transfer curves tuned to hue {spec_hint.get('palette_hue')} and seed {spec_hint.get('seed')}."
        elif medium == "animated_video":
            theme = hint_text or f"Time-evolving {algo.replace('_', ' ')} audiovisual study with stereo accompaniment"
            arc = f"Integrates {spec_hint.get('duration_s')}s of dynamical state evolution at {spec_hint.get('fps')} fps into MJPEG AVI, GIF, WebP, and WebGL."
        else:
            theme = hint_text or f"Original {medium} creation via {algo}"
            arc = f"Structured multi-stage synthesis anchored to differential seed and rolling trajectory state #{dream_num}."

        return DeliberationPlan(
            dream_num=dream_num,
            medium=medium,
            title=title,
            theme=theme,
            stem_domain=str(spec_hint.get("stem_domain", "Interdisciplinary Science")),
            structural_form=algo,
            thesis_or_arc=arc,
            technical_spec=spec_hint,
            differentiation_note=f"Orthogonal selection (attempt {attempt + 1}) with novelty verification against trajectory ledger",
            model_used="procedural_orthogonal",
            deliberation_seconds=elapsed_s,
        )

    def deliberate_longform_text(
        self,
        plan: DeliberationPlan,
        prompt: str,
        fallback_builder: Any,
        timeout_s: float = 240.0,
        prefer_teacher: bool = False,
        min_chars: int = 280,
        use_llm: bool = True,
    ) -> Tuple[str, str]:
        """
        Generates rich prose/poetry/analysis for `plan` with novelty verification.
        Falls back to `fallback_builder(plan, attempt)` only if local LLMs are unavailable
        or `use_llm=False`, retrying if similarity to previous entries is too high.
        """
        model = _select_deliberation_model(prefer_teacher=prefer_teacher) if use_llm else "procedural_orthogonal"
        best_text = ""
        used_model = model

        for attempt in range(3):
            candidate = None
            if model != "procedural_orthogonal":
                extra_guard = "" if attempt == 0 else "\nCRITICAL: Your prior draft echoed existing works. Use completely fresh concrete imagery, vocabulary, numbers, and structure."
                candidate = _query_ollama_text(model, prompt + extra_guard, timeout_s=timeout_s)
                if candidate:
                    used_model = model
                else:
                    model = "procedural_orthogonal"

            if not candidate or len(candidate) < min_chars:
                candidate = fallback_builder(plan, attempt)
                used_model = "procedural_orthogonal"

            ok, _, _ = self.ledger.check_novelty(
                f"{plan.title}#{attempt}",
                candidate,
                medium=plan.medium,
                similarity_threshold=0.58,
            )
            best_text = candidate
            if ok:
                break

        return best_text, used_model

    def finalize_creation(
        self,
        work_id: str,
        plan: DeliberationPlan,
        body_text: str,
        file_paths: List[str],
        total_seconds: float,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return self.ledger.record_work(
            work_id=work_id,
            title=plan.title,
            medium=plan.medium,
            theme=plan.theme,
            body_text=body_text,
            structural_form=plan.structural_form,
            file_paths=file_paths,
            deliberation_seconds=total_seconds,
            extra=extra,
        )
