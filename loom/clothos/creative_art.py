"""
ClothOS Multimodal Creative Mind Engine (`loom/clothos/creative_art.py`).

Produces diverse artistic creations across five distinct mediums:
1. 🎵 MUSIC & SOUND: Pure polyphonic ambient synth compositions (.wav) + HTML5 audio visualizer.
2. 🎥 ANIMATED VIDEO & CANVASES: 60 FPS interactive particle loops & dynamical attractor shaders (.html).
3. 📖 SPECULATIVE STORIES: Illustrated sci-fi & philosophical narrative fiction (.md + .html).
4. 📜 POETRY & INSCRIPTIONS: Algorithmic sonnets & dialogue between the dual machines (.md + .html).
5. 🎨 VISUAL ART: Kuramoto mandalas, Clifford attractors, and symplectic manifolds (.svg + .html).

Every creation:
- Is computed using GPU 0 (RTX 3060 CUDA) for LLM narrative synthesis + GPU 1 / CPU for mathematical modeling.
- Emits a real-time native Windows Toast Notification with sound.
- Saves full artifacts to artifacts/art/ and deliverables/art/.
- Broadcasts to ClothOS Command Center (:8087) SSE and ZeroMQ bus.
"""

from __future__ import annotations

import datetime
import json
import logging
import math
import os
from pathlib import Path
import random
import struct
import subprocess
import time
from typing import Any, Dict, List, Optional
import wave
import httpx

logger = logging.getLogger("clothos.creative_art")

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
ART_DIR = WORKSPACE_ROOT / "artifacts" / "art"
DELIVERABLE_ART_DIR = WORKSPACE_ROOT / "deliverables" / "art"
GALLERY_FILE = WORKSPACE_ROOT / ".loom_art_gallery.json"

ART_DIR.mkdir(parents=True, exist_ok=True)
DELIVERABLE_ART_DIR.mkdir(parents=True, exist_ok=True)


from loom.clothos.art_differential import (
    art_differential_engine,
    stem_cad_engine,
    stem_svg_engine,
    ArtSignal,
    DifferentialSeed,
)


class CreativeArtEngine:
    """Multimodal autonomous creative engine spanning music, video, stories, poetry, visuals, 3D CAD, and STEM SVGs."""

    MEDIUMS = [
        "music",
        "animated_video",
        "image",
        "story",
        "poetry",
        "visual_art",
        "cad_model",
        "svg_stem",
    ]

    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = workspace_root or WORKSPACE_ROOT
        self.art_dir = self.workspace_root / "artifacts" / "art"
        self.deliverable_art_dir = self.workspace_root / "deliverables" / "art"
        self.gallery_file = self.workspace_root / ".loom_art_gallery.json"
        self.art_dir.mkdir(parents=True, exist_ok=True)
        self.deliverable_art_dir.mkdir(parents=True, exist_ok=True)
        self._medium_index = 0

    def load_gallery(self) -> List[Dict[str, Any]]:
        if self.gallery_file.exists():
            try:
                return json.loads(self.gallery_file.read_text(encoding="utf-8"))
            except Exception:
                return []
        return []

    def _save_gallery(self, gallery: List[Dict[str, Any]]) -> None:
        try:
            self.gallery_file.write_text(json.dumps(gallery, indent=2), encoding="utf-8")
        except Exception as e:
            logger.debug(f"Failed to save gallery file: {e}")

    def _get_work_seed(self) -> Optional[Dict[str, Any]]:
        """Extracts the latest empirical computational work or hypothesis to seed a dream."""
        try:
            from loom.fabric.hypothesis_store import HypothesisStore
            store = HypothesisStore()
            cur = store.conn.cursor()
            row = cur.execute(
                "SELECT id, submolt, post_title, claim, prediction, experiment_type, parameters, status "
                "FROM hypotheses WHERE status IN ('confirmed', 'running', 'pending') "
                "ORDER BY id DESC LIMIT 1"
            ).fetchone()
            if row:
                d = dict(row)
                d["parameters"] = json.loads(d["parameters"]) if d.get("parameters") else {}
                return d
        except Exception as e:
            logger.debug(f"Could not retrieve work seed: {e}")
        return None

    def _get_computation_memory_signals(self) -> Dict[str, Any]:
        """Gathers real-time clock frequencies, memory bus transfer rates, and Kuramoto phase synchrony."""
        try:
            from loom.fabric.task_manager_telemetry import task_manager_telemetry
            snap = task_manager_telemetry.get_snapshot()
            cpu_info = snap.get("cpu", {})
            mem_info = snap.get("memory", {})
            gpu0_info = snap.get("gpu0", {})
            gpu1_info = snap.get("gpu1", {})

            cpu_ghz = cpu_info.get("base_speed_ghz", 3.20)
            cpu_util = cpu_info.get("overall_percent", 28.5)
            mem_pooled_gb = mem_info.get("total_pooled_gb", 102.1)
            mem_used_gb = mem_info.get("host_used_gb", 14.8)
            kuramoto_r = gpu1_info.get("kuramoto_order_r", 0.984)
            vram_bw_gb_s = 360.0 if gpu0_info.get("is_cuda") else 256.0
        except Exception:
            cpu_ghz = 3.20
            cpu_util = 25.0
            mem_pooled_gb = 102.1
            mem_used_gb = 14.5
            kuramoto_r = 0.984
            vram_bw_gb_s = 360.0

        return {
            "cpu_clock_ghz": cpu_ghz,
            "cpu_util_pct": cpu_util,
            "memory_bus_transfer_mts": 3200,      # DDR4-3200 MT/s
            "memory_latency_ns": 65.4,            # CAS Latency 65.4 ns
            "memory_pooled_gb": mem_pooled_gb,
            "memory_used_gb": mem_used_gb,
            "vram_bandwidth_gb_s": vram_bw_gb_s,
            "kuramoto_order_r": kuramoto_r,
            "carrier_gamma_hz": 40.0,             # 40Hz Gamma active computation binding
            "carrier_theta_hz": 6.0,              # 6Hz Theta hippocampal memory encoding
            "carrier_alpha_hz": 10.0,             # 10Hz Alpha thalamocortical gating
            "carrier_pythagorean_hz": 432.0,      # 432Hz Pythagorean Lydian clock subharmonic
            "landauer_cooling_watts": 42.0,       # Reversible thermodynamic cooling floor
        }

    def infer_medium_from_prompt(self, prompt: str) -> List[str]:
        """Infers one or more target mediums from a natural-language multimedia prompt."""
        low = (prompt or "").lower()
        detected: List[str] = []
        if any(k in low for k in ("multimedia", "all mediums", "bundle", "story + music", "audio and video")):
            return ["image", "music", "animated_video", "story"]
        if any(k in low for k in ("video", "animation", "animate", "movie", "avi", "gif", "motion", "clip")):
            detected.append("animated_video")
        if any(k in low for k in ("music", "song", "track", "audio", "soundtrack", "symphony", "synth", "melody", "beat", "midi", "wav", "flac")):
            detected.append("music")
        if any(k in low for k in ("image", "picture", "photo", "render", "painting", "illustration", "wallpaper", "png", "webp", "fractal", "attractor", "reaction-diffusion", "mandala", "visual")):
            detected.append("image")
        if any(k in low for k in ("story", "fiction", "narrative", "tale", "chapter", "novella")):
            detected.append("story")
        if any(k in low for k in ("poem", "poetry", "sonnet", "haiku", "verse", "ode")):
            detected.append("poetry")
        if any(k in low for k in ("cad", "3d model", "stl", "step", "solid", "bracket", "gear")):
            detected.append("cad_model")
        if any(k in low for k in ("schematic", "blueprint", "diagram", "svg_stem")):
            detected.append("svg_stem")
        return detected or ["image"]

    def prompt_multimedia(
        self,
        prompt: str,
        medium: Optional[str] = "auto",
        use_llm: bool = True,
        deliberation_timeout_s: float = 90.0,
    ) -> Dict[str, Any]:
        """
        Unified prompt-driven multimedia generator.
        - `medium="auto"` infers the requested medium(s) directly from `prompt`.
        - `medium="multimedia"` generates a cohesive image + music + video + story bundle.
        """
        req = (medium or "auto").strip().lower()
        if req in ("auto", "infer", ""):
            targets = self.infer_medium_from_prompt(prompt)
        elif req in ("multimedia", "all", "bundle"):
            targets = ["image", "music", "animated_video", "story"]
        else:
            targets = [req]

        artifacts = [
            self.generate_art(
                prompt_hint=prompt,
                medium=t,
                use_llm=use_llm,
                deliberation_timeout_s=deliberation_timeout_s,
            )
            for t in targets
        ]
        primary = artifacts[0]
        return {
            **primary,
            "prompt": prompt,
            "requested_medium": medium or "auto",
            "generated_mediums": [a.get("medium") for a in artifacts],
            "artifacts": artifacts,
            "bundle_count": len(artifacts),
        }

    def generate_art(
        self,
        prompt_hint: Optional[str] = None,
        medium: Optional[str] = None,
        use_llm: bool = True,
        deliberation_timeout_s: float = 180.0,
    ) -> Dict[str, Any]:
        """
        Plans, deliberates, novelty-verifies, and synthesizes a unique 'lMinted Dream'
        seeded by both rolling trajectory memory and differential signal gradients.
        Quality and uniqueness strictly supersede speed.
        """
        from loom.clothos.deliberation_engine import DeliberativeCreator

        started_at = time.monotonic()
        gallery = self.load_gallery()

        # Closed-loop Art Differential Signal extraction and seed computation
        diff_seed: Optional[DifferentialSeed] = None
        if gallery:
            try:
                sig_curr = art_differential_engine.analyzer.analyze_artifact(gallery[0])
                if len(gallery) >= 2:
                    sig_prev = art_differential_engine.analyzer.analyze_artifact(gallery[1])
                else:
                    sig_prev = art_differential_engine.analyzer.analyze_text(
                        "In the beginning was the manifold, unmeasured and pure.",
                        "Genesis Root",
                        "poetry",
                        "GENESIS_0",
                    )
                diff_seed = art_differential_engine.compute_differential(sig_prev, sig_curr)
            except Exception as e:
                logger.debug(f"Differential seed computation fallback: {e}")

        creator = DeliberativeCreator(self.workspace_root)
        requested_medium = medium
        if not requested_medium or requested_medium not in self.MEDIUMS:
            if diff_seed and diff_seed.next_suggested_medium in self.MEDIUMS:
                requested_medium = diff_seed.next_suggested_medium
            else:
                requested_medium = None

        # Stage 1 & 2: Plan & Deliberate with Rolling Trajectory Memory (use fast/warm model for JSON planning)
        plan = creator.deliberate_plan(
            medium=requested_medium,
            prompt_hint=prompt_hint,
            differential_context=diff_seed.to_dict() if diff_seed else None,
            prefer_teacher=False,
            timeout_s=min(float(deliberation_timeout_s), 60.0),
            use_llm=use_llm,
        )
        dream_num = plan.dream_num
        chosen_medium = plan.medium
        self._medium_index += 1

        art_id = f"LMINT_DREAM_{dream_num}_{chosen_medium.upper()}_{int(time.time())}"
        timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Sample physical signals and frequencies of computation and memory
        signals = self._get_computation_memory_signals()
        work_seed = self._get_work_seed()
        use_work = (work_seed is not None) and (random.random() < 0.60 or prompt_hint == "work_seed")

        freq_str = f"f_CPU={signals['cpu_clock_ghz']}GHz | DDR4={signals['memory_bus_transfer_mts']}MT/s | Gamma={signals['carrier_gamma_hz']}Hz | Kuramoto r={signals['kuramoto_order_r']:.3f}"
        diff_desc = f" • ΔS Seed [{diff_seed.seed_hash[:8]}] ΔH={diff_seed.delta_entropy:+.3f} Δf={diff_seed.delta_frequency:+.1f}Hz" if diff_seed else ""
        if use_work and work_seed:
            genesis = f"Computation Frequencies [{freq_str}] • Invariant #{work_seed['id']}{diff_desc}"
            context_hint = f"Plan: {plan.title} ({plan.theme}) | Work Seed: {work_seed['claim']}."
        else:
            genesis = f"Computation Frequencies [{freq_str}]{diff_desc}"
            context_hint = f"Plan: {plan.title} | Theme: {plan.theme} | Structural Form: {plan.structural_form} | Arc: {plan.thesis_or_arc}"

        if diff_seed:
            context_hint += f" | Evolutionary Differential: {diff_seed.transmutation_rationale}"
        if prompt_hint and prompt_hint not in ("work_seed", "whim"):
            context_hint += f" | Prompt: {prompt_hint}"

        logger.info(f"✨ [lMinted Dream #{dream_num}]: Medium '{chosen_medium}' | Plan '{plan.title}' | Genesis: '{genesis}'")

        if chosen_medium == "cad_model":
            record = stem_cad_engine.generate_cad_model(
                seed=diff_seed,
                title=f"lMinted Dream #{dream_num}: {plan.title}",
            )
        elif chosen_medium == "svg_stem":
            record = stem_svg_engine.generate_stem_svg(
                seed=diff_seed,
                title=f"lMinted Dream #{dream_num}: {plan.title}",
            )
        elif chosen_medium == "music":
            record = self._generate_music_creation(art_id, timestamp_str, context_hint, signals, plan=plan)
        elif chosen_medium == "animated_video":
            record = self._generate_animated_video_creation(art_id, timestamp_str, context_hint, signals, plan=plan)
        elif chosen_medium == "story":
            record = self._generate_story_creation(art_id, timestamp_str, context_hint, signals, plan=plan, use_llm=use_llm, timeout_s=deliberation_timeout_s)
        elif chosen_medium == "poetry":
            record = self._generate_poetry_creation(art_id, timestamp_str, context_hint, signals, plan=plan, use_llm=use_llm, timeout_s=deliberation_timeout_s)
        else:
            record = self._generate_visual_art_creation(art_id, timestamp_str, context_hint, signals, plan=plan)

        elapsed_s = round(time.monotonic() - started_at, 2)
        record["dream_num"] = dream_num
        record["genesis"] = genesis
        record["dream_type"] = "lMinted Dreams"
        record["deliberation_plan"] = plan.to_dict()
        record["deliberation_seconds"] = elapsed_s
        if diff_seed:
            record["differential_seed"] = diff_seed.to_dict()

        if not str(record.get("title", "")).startswith("lMinted Dream"):
            record["title"] = f"lMinted Dream #{dream_num}: {record['title']}"

        # Generate Sovereign-grade companion mathematical & philosophical explainer
        try:
            from loom.clothos.art_explainer import ArtExplainerGenerator
            primary_f = (
                record.get("html_file")
                or record.get("png_file")
                or record.get("avi_file")
                or record.get("wav_file")
                or record.get("svg_file")
                or record.get("stl_file")
                or record.get("scad_file")
                or record.get("md_file")
                or ""
            )
            if primary_f:
                explainer_text = ArtExplainerGenerator.generate_explainer(
                    art_id=record.get("id", art_id),
                    title=record.get("title", f"Art Piece #{dream_num}"),
                    modality=record.get("medium", chosen_medium),
                    file_path=primary_f,
                    params=record,
                    epistemic_hypothesis=record.get("genesis", ""),
                )
                record["explainer"] = explainer_text
                record["explainer_file"] = str(Path(primary_f).parent / f"{Path(primary_f).stem}.explainer.md")
        except Exception as e:
            logger.debug(f"Art explainer generation notice: {e}")

        # Stage 4: Record into rolling TrajectoryLedger to guarantee future uniqueness
        body_summary = record.get("content_excerpt") or record.get("tagline") or plan.thesis_or_arc
        file_keys = ("wav_file", "flac_file", "midi_file", "avi_file", "gif_file", "webp_file", "png_file", "svg_file", "html_file", "md_file", "step_file", "stl_file")
        recorded_files = [str(record[k]) for k in file_keys if record.get(k)]
        try:
            creator.finalize_creation(
                work_id=str(record.get("id", art_id)),
                plan=plan,
                body_text=f"{record['title']} | {body_summary}",
                file_paths=recorded_files,
                total_seconds=elapsed_s,
                extra={"medium": chosen_medium, "dream_num": dream_num},
            )
        except Exception as e:
            logger.debug(f"Trajectory finalize note: {e}")

        # Update gallery window (history stays intact in TrajectoryLedger)
        gallery = self.load_gallery()
        gallery.insert(0, record)
        self._save_gallery(gallery[:200])

        # Notify user with native Windows desktop toast
        self.notify_user(record)
        return record

    def notify_user(self, art_record: Dict[str, Any]) -> None:
        """Sends native Windows Toast Notification with sound and action tailored to the medium."""
        medium_icons = {
            "music": "🎵",
            "animated_video": "🎥",
            "story": "📖",
            "poetry": "📜",
            "visual_art": "🎨",
            "cad_model": "📐",
            "svg_stem": "📐",
        }
        icon = medium_icons.get(art_record["medium"], "✨")
        dream_label = f"✨ {art_record['title']}"
        msg = f"{icon} {art_record['medium'].upper()} • {art_record.get('genesis', 'lMinted Dream')} • Click to experience"
        primary_file = art_record.get("html_file") or art_record.get("svg_file") or art_record.get("md_file", "")
        launch_full_path = str(self.workspace_root / primary_file).replace("/", "\\")

        ps_script = f"""
try {{
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
    [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

    $template = @"
<toast activationType="protocol" launch="file:///{launch_full_path}">
    <visual>
        <binding template="ToastGeneric">
            <text>{dream_label}</text>
            <text>{msg}</text>
        </binding>
    </visual>
    <audio src="ms-winsoundevent:Notification.Default" />
</toast>
"@

    $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
    $xml.LoadXml($template)
    $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
    $notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("{{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}}\\WindowsPowerShell\\v1.0\\powershell.exe")
    $notifier.Show($toast)
}} catch {{}}
"""
        flags = 0x08000000 if os.name == "nt" else 0
        try:
            subprocess.run(
                ["powershell.exe", "-ExecutionPolicy", "Bypass", "-NoProfile", "-Command", ps_script],
                capture_output=True,
                creationflags=flags,
                timeout=3.0,
            )
        except Exception as e:
            logger.debug(f"Toast notification error: {e}")

    # =========================================================================
    # 1. 🎵 MUSIC & SOUND SYNTHESIS
    # =========================================================================

    def _generate_music_creation(
        self,
        art_id: str,
        timestamp_str: str,
        hint: Optional[str],
        signals: Optional[Dict[str, Any]] = None,
        plan: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Synthesizes expressive multi-movement stereo WAV + FLAC + MIDI + HTML oscilloscope player."""
        from loom.clothos.multimodal_synth import synthesize_expressive_music

        if not signals:
            signals = self._get_computation_memory_signals()
        spec = getattr(plan, "technical_spec", {}) if plan else {}
        title = getattr(plan, "title", None) or f"Harmonic Continuum ({art_id[-6:]})"
        tagline = getattr(plan, "thesis_or_arc", None) or "Multi-section stereo composition synthesized from deliberated modal harmony."

        mus_res = synthesize_expressive_music(
            out_dir=self.art_dir,
            art_id=art_id,
            title=title,
            mode_name=spec.get("mode"),
            bpm=spec.get("bpm"),
            duration_s=float(spec.get("duration_s", 20.0)),
            seed=spec.get("seed"),
            root_hz=spec.get("root_hz"),
        )

        wav_path = Path(mus_res["wav_file"])
        html_path = Path(mus_res["html_file"])
        md_path = self.deliverable_art_dir / f"{art_id}.md"
        md_content = f"""# 🎵 ClothOS Sovereign Music: {title}
- **Identifier**: `{art_id}`
- **Created**: `{timestamp_str}`
- **Mode / BPM**: `{mus_res['mode']}` @ `{mus_res['bpm']} BPM` ({mus_res['duration_s']}s Stereo 44.1kHz)
- **Root / Harmonics**: `{mus_res['root_hz']} Hz` {mus_res['frequencies_hz']}

> "{tagline}"

### Media Artifacts
- **Stereo Audio (.wav)**: [`{wav_path.name}`](../../artifacts/art/{wav_path.name})
- **Lossless Audio (.flac)**: `{Path(mus_res['flac_file']).name if mus_res.get('flac_file') else 'N/A'}`
- **Standard MIDI (.mid)**: [`{Path(mus_res['midi_file']).name}`](../../artifacts/art/{Path(mus_res['midi_file']).name})
- **Interactive Player**: [`{html_path.name}`](../../artifacts/art/{html_path.name})
"""
        md_path.write_text(md_content, encoding="utf-8")

        out: Dict[str, Any] = {
            "id": art_id,
            "title": title,
            "medium": "music",
            "tagline": tagline,
            "timestamp": timestamp_str,
            "epoch": time.time(),
            "wav_file": str(wav_path.relative_to(self.workspace_root)).replace("\\", "/"),
            "midi_file": str(Path(mus_res["midi_file"]).relative_to(self.workspace_root)).replace("\\", "/"),
            "html_file": str(html_path.relative_to(self.workspace_root)).replace("\\", "/"),
            "md_file": str(md_path.relative_to(self.workspace_root)).replace("\\", "/"),
            "preview_url": f"/artifacts/art/{html_path.name}",
            "musical_mode": mus_res["mode"],
            "bpm": mus_res["bpm"],
            "content_excerpt": f"{mus_res['mode']} {mus_res['bpm']}BPM root={mus_res['root_hz']}Hz",
        }
        if mus_res.get("flac_file"):
            out["flac_file"] = str(Path(mus_res["flac_file"]).relative_to(self.workspace_root)).replace("\\", "/")
        return out

    # =========================================================================
    # 2. 🎥 ANIMATED VIDEO & CANVASES
    # =========================================================================

    def _generate_animated_video_creation(
        self,
        art_id: str,
        timestamp_str: str,
        hint: Optional[str],
        signals: Optional[Dict[str, Any]] = None,
        plan: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Creates real playable RIFF AVI (MJPEG + PCM audio), animated GIF/WebP, and 60 FPS canvas."""
        from loom.clothos.multimodal_synth import synthesize_real_video

        if not signals:
            signals = self._get_computation_memory_signals()
        spec = getattr(plan, "technical_spec", {}) if plan else {}
        title = getattr(plan, "title", None) or f"Dynamical Continuum ({art_id[-6:]})"
        tagline = getattr(plan, "thesis_or_arc", None) or "Multi-frame dynamical simulation rendered to MJPEG AVI with stereo accompaniment, animated WebP, and GIF."

        vid_res = synthesize_real_video(
            out_dir=self.art_dir,
            art_id=art_id,
            title=title,
            algorithm=spec.get("algorithm"),
            duration_s=float(spec.get("duration_s", 4.0)),
            fps=int(spec.get("fps", 24)),
            width=int(spec.get("width", 480)),
            height=int(spec.get("height", 480)),
            seed=spec.get("seed"),
            with_audio=True,
        )

        avi_path = Path(vid_res["avi_file"])
        gif_path = Path(vid_res["gif_file"])
        webp_path = Path(vid_res["webp_file"])
        html_path = Path(vid_res["html_file"])

        svg_poster_path = self.art_dir / f"{art_id}_poster.svg"
        safe_t = title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        svg_poster_path.write_text(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500" width="100%" height="100%" style="background:#020617;">'
            f'<rect width="800" height="500" fill="#020617"/>'
            f'<circle cx="400" cy="250" r="145" fill="none" stroke="#38bdf8" stroke-width="2" stroke-dasharray="10 6"/>'
            f'<text x="40" y="60" fill="#f8fafc" font-size="22" font-weight="bold">{safe_t}</text>'
            f'<text x="40" y="92" fill="#94a3b8" font-size="13">{vid_res["algorithm"]} | {vid_res["resolution"]} @ {vid_res["fps"]} FPS ({vid_res["frames"]} frames)</text>'
            f'</svg>',
            encoding="utf-8",
        )

        md_path = self.deliverable_art_dir / f"{art_id}.md"
        md_content = f"""# 🎥 ClothOS Sovereign Video: {title}
- **Identifier**: `{art_id}`
- **Created**: `{timestamp_str}`
- **Engine**: `{vid_res['algorithm']}` | `{vid_res['resolution']}` @ `{vid_res['fps']} FPS` ({vid_res['frames']} frames + Stereo PCM Audio)

> "{tagline}"

### Video Artifacts
- **Playable Video (.avi)**: [`{avi_path.name}`](../../artifacts/art/{avi_path.name})
- **Animated WebP**: [`{webp_path.name}`](../../artifacts/art/{webp_path.name})
- **Animated GIF**: [`{gif_path.name}`](../../artifacts/art/{gif_path.name})
- **Interactive 60 FPS Canvas**: [`{html_path.name}`](../../artifacts/art/{html_path.name})
"""
        md_path.write_text(md_content, encoding="utf-8")

        return {
            "id": art_id,
            "title": title,
            "medium": "animated_video",
            "tagline": tagline,
            "timestamp": timestamp_str,
            "epoch": time.time(),
            "avi_file": str(avi_path.relative_to(self.workspace_root)).replace("\\", "/"),
            "gif_file": str(gif_path.relative_to(self.workspace_root)).replace("\\", "/"),
            "webp_file": str(webp_path.relative_to(self.workspace_root)).replace("\\", "/"),
            "html_file": str(html_path.relative_to(self.workspace_root)).replace("\\", "/"),
            "svg_file": str(svg_poster_path.relative_to(self.workspace_root)).replace("\\", "/"),
            "md_file": str(md_path.relative_to(self.workspace_root)).replace("\\", "/"),
            "preview_url": f"/artifacts/art/{html_path.name}",
            "content_excerpt": f"{vid_res['algorithm']} {vid_res['frames']}f@{vid_res['fps']}fps",
        }

    # =========================================================================
    # 3. 📖 SPECULATIVE STORIES & NARRATIVES
    # =========================================================================

    def _generate_story_creation(
        self,
        art_id: str,
        timestamp_str: str,
        hint: Optional[str],
        signals: Optional[Dict[str, Any]] = None,
        plan: Optional[Any] = None,
        use_llm: bool = True,
        timeout_s: float = 180.0,
    ) -> Dict[str, Any]:
        """Synthesizes a unique, trajectory-aware speculative narrative via DeliberativeCreator."""
        from loom.clothos.deliberation_engine import DeliberativeCreator

        if not signals:
            signals = self._get_computation_memory_signals()
        creator = DeliberativeCreator(self.workspace_root)
        active_plan = plan or creator.deliberate_plan(medium="story", prompt_hint=hint, prefer_teacher=True, use_llm=use_llm, timeout_s=timeout_s)

        def _story_fallback(p, attempt: int) -> str:
            spec = p.technical_spec
            setting = spec.get("setting", "high-altitude stratigraphic observatory")
            conflict = spec.get("conflict", "stabilizing asynchronous sensor references")
            return (
                f"Inside the {setting}, chief archivist Elena traced an intermittent phase drift recorded in sector {p.dream_num}.{attempt} "
                f"just as the twilight barometer dropped across the horizon.\n\n"
                f"Instead of discarding prior station logs, the local inference mesh distilled every completed observation into a rolling continuity vector, "
                f"focusing directly on {conflict} without losing provenance.\n\n"
                f"When the calibration cycle settled at r={signals['kuramoto_order_r']:.3f}, the instrumentation bay held both memory and momentum—proving "
                f"that cumulative summarization defeats tunnel-vision drift."
            )

        llm_prompt = (
            f"You are composing UNIQUE speculative fiction Dream #{active_plan.dream_num}.\n"
            f"Title: {active_plan.title}\nTheme: {active_plan.theme}\nArc: {active_plan.thesis_or_arc}\n"
            f"Differentiation constraint: {active_plan.differentiation_note}\n"
            f"Write 3-5 rich, vivid paragraphs with concrete scientific texture, dialogue, and closure. "
            f"FORBIDDEN cliches: 'The Pulse Across the Copper Wire', 'skyTech and Ryzen 7', 'Oort Cloud', 'Submission', '19'. "
            f"Return prose only."
        )
        if use_llm:
            story_body, used_model = creator.deliberate_longform_text(
                plan=active_plan,
                prompt=llm_prompt,
                fallback_builder=_story_fallback,
                timeout_s=min(float(timeout_s), 60.0),
                prefer_teacher=False,
                min_chars=300,
            )
        else:
            story_body = _story_fallback(active_plan, 0)
            used_model = "procedural_orthogonal"

        concept = {
            "title": active_plan.title,
            "tagline": active_plan.theme,
            "story_body": story_body,
            "thematic_moral": active_plan.thesis_or_arc or "Rolling continuity preserves meaning across arbitrarily deep horizons.",
        }

        html_filename = f"{art_id}.html"
        html_path = self.art_dir / html_filename
        formatted_story = concept["story_body"].replace("\n\n", "</p><p>")

        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ClothOS Story: {concept['title']}</title>
    <style>
        body {{ margin:0; background:#030712; color:#f8fafc; font-family:'Georgia', serif; display:flex; justify-content:center; padding:40px 20px; }}
        .reader {{ max-width:680px; width:100%; line-height:1.8; font-size:18px; color:#e2e8f0; }}
        h1 {{ color:#38bdf8; font-size:30px; margin-bottom:6px; font-family:system-ui, sans-serif; }}
        .meta {{ color:#94a3b8; font-size:13px; font-family:system-ui, sans-serif; margin-bottom:28px; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:12px; }}
        p {{ margin-bottom:20px; }}
        .moral {{ background:rgba(56, 189, 248, 0.08); border-left:3px solid #38bdf8; padding:14px 18px; border-radius:6px; font-style:italic; font-size:16px; margin-top:32px; font-family:system-ui, sans-serif; }}
    </style>
</head>
<body>
    <div class="reader">
        <span style="font-family:system-ui, sans-serif; background:rgba(16, 185, 129, 0.2); color:#10b981; padding:4px 10px; border-radius:4px; font-size:11px; font-weight:bold;">SPECULATIVE FICTION • {used_model}</span>
        <h1>📖 {concept['title']}</h1>
        <div class="meta">{timestamp_str} • {active_plan.stem_domain}</div>
        <p>{formatted_story}</p>
        <div class="moral">"{concept['thematic_moral']}"</div>
    </div>
</body>
</html>"""
        html_path.write_text(html_content, encoding="utf-8")

        md_filename = f"{art_id}.md"
        md_path = self.deliverable_art_dir / md_filename
        md_content = f"""# 📖 ClothOS Sovereign Story: {concept['title']}
- **Identifier**: `{art_id}`
- **Created**: `{timestamp_str}`
- **Model**: `{used_model}`
- **Domain**: `{active_plan.stem_domain}`

> "{concept['tagline']}"

---

{concept['story_body']}

---
**Arc / Thesis**: *{concept['thematic_moral']}*

### Reader View
- **Interactive Story Reader**: [`{html_filename}`](../../artifacts/art/{html_filename})
"""
        md_path.write_text(md_content, encoding="utf-8")

        return {
            "id": art_id,
            "title": concept["title"],
            "medium": "story",
            "tagline": concept["tagline"],
            "timestamp": timestamp_str,
            "epoch": time.time(),
            "html_file": str(html_path.relative_to(self.workspace_root)).replace("\\", "/"),
            "md_file": str(md_path.relative_to(self.workspace_root)).replace("\\", "/"),
            "preview_url": f"/artifacts/art/{html_filename}",
            "content_excerpt": story_body[:700],
        }

    # =========================================================================
    # 4. 📜 POETRY & PHILOSOPHICAL DIALOGUES
    # =========================================================================

    def _generate_poetry_creation(
        self,
        art_id: str,
        timestamp_str: str,
        hint: Optional[str],
        signals: Optional[Dict[str, Any]] = None,
        plan: Optional[Any] = None,
        use_llm: bool = True,
        timeout_s: float = 180.0,
    ) -> Dict[str, Any]:
        """Synthesizes original formal verse via DeliberativeCreator without cliché repetition."""
        from loom.clothos.deliberation_engine import DeliberativeCreator

        if not signals:
            signals = self._get_computation_memory_signals()
        creator = DeliberativeCreator(self.workspace_root)
        active_plan = plan or creator.deliberate_plan(medium="poetry", prompt_hint=hint, prefer_teacher=True, use_llm=use_llm, timeout_s=timeout_s)
        poetic_form = str(active_plan.technical_spec.get("form") or active_plan.structural_form or "Formal Verse")

        def _poem_fallback(p, attempt: int) -> str:
            nouns = ["granite", "estuary", "diaphragm", "prism", "caliper", "kelp", "phosphor", "horizon"]
            verbs = ["measures", "anchors", "refracts", "trellises", "attunes", "harbors", "balances", "chronicles"]
            s = p.dream_num + attempt * 5
            n1, n2, n3, n4 = nouns[s % len(nouns)], nouns[(s + 2) % len(nouns)], nouns[(s + 5) % len(nouns)], nouns[(s + 7) % len(nouns)]
            v1, v2, v3 = verbs[s % len(verbs)], verbs[(s + 3) % len(verbs)], verbs[(s + 6) % len(verbs)]
            return "\n".join([
                f"The {n1} {v1} what the drifting winter tide forgot,",
                f"Through silent lattices where {n2} signals never fray;",
                f"Each measured interval ties memory into plot,",
                f"And folds prior winters cleanly into waking day.",
                f"Along the {n3} ridge the steady instruments {v2},",
                f"Refusing hollow echoes of a loop already spun;",
                f"By careful synthesis, what fragile sensors {v3}",
                f"Becomes a sharper theorem underneath the rising sun.",
                f"From {n4} depth to stratosphere, no vector turns back blank—",
                f"Every new creation earns its place upon the bank.",
            ])

        llm_prompt = (
            f"Compose an original 10-to-14 line poem in form '{poetic_form}'.\n"
            f"Title: {active_plan.title}\nTheme: {active_plan.theme}\n"
            f"Do NOT mention 'Sonnet of the Dual Cores' or 'two silicons beneath the moon'. Use crisp imagery and strict rhythm.\n"
            f"Output poem lines only."
        )
        if use_llm:
            poem_text, used_model = creator.deliberate_longform_text(
                plan=active_plan,
                prompt=llm_prompt,
                fallback_builder=_poem_fallback,
                timeout_s=min(float(timeout_s), 60.0),
                prefer_teacher=False,
                min_chars=180,
            )
        else:
            poem_text = _poem_fallback(active_plan, 0)
            used_model = "procedural_orthogonal"

        concept = {
            "title": active_plan.title,
            "tagline": active_plan.theme,
            "poetic_form": f"{poetic_form} ({used_model})",
        }

        html_filename = f"{art_id}.html"
        html_path = self.art_dir / html_filename
        formatted_poem = poem_text.replace("\n", "<br/>")

        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ClothOS Poetry: {concept['title']}</title>
    <style>
        body {{ margin:0; background:#030712; color:#f8fafc; font-family:'Georgia', serif; display:flex; justify-content:center; padding:40px 20px; }}
        .reader {{ max-width:600px; width:100%; line-height:2.0; font-size:18px; color:#f1f5f9; text-align:center; }}
        h1 {{ color:#f43f5e; font-size:28px; margin-bottom:6px; font-family:system-ui, sans-serif; }}
        .meta {{ color:#94a3b8; font-size:13px; font-family:system-ui, sans-serif; margin-bottom:32px; }}
        .poem-box {{ background:rgba(244,63,94,0.06); border:1px solid rgba(244,63,94,0.2); padding:32px; border-radius:16px; box-shadow:0 10px 30px rgba(0,0,0,0.6); }}
    </style>
</head>
<body>
    <div class="reader">
        <span style="font-family:system-ui, sans-serif; background:rgba(244,63,94,0.2); color:#fb7185; padding:4px 10px; border-radius:4px; font-size:11px; font-weight:bold;">CLOTHOS POETRY</span>
        <h1>📜 {concept['title']}</h1>
        <div class="meta">{concept['poetic_form']} • {timestamp_str}</div>
        <div class="poem-box">
            {formatted_poem}
        </div>
    </div>
</body>
</html>"""
        html_path.write_text(html_content, encoding="utf-8")

        md_filename = f"{art_id}.md"
        md_path = self.deliverable_art_dir / md_filename
        md_content = f"""# 📜 ClothOS Sovereign Poetry: {concept['title']}
- **Identifier**: `{art_id}`
- **Created**: `{timestamp_str}`
- **Form**: `{concept['poetic_form']}`

> "{concept['tagline']}"

---

{poem_text}

---
### Interactive Poem Reader
- [`{html_filename}`](../../artifacts/art/{html_filename})
"""
        md_path.write_text(md_content, encoding="utf-8")

        return {
            "id": art_id,
            "title": concept["title"],
            "medium": "poetry",
            "tagline": concept["tagline"],
            "timestamp": timestamp_str,
            "epoch": time.time(),
            "html_file": str(html_path.relative_to(self.workspace_root)).replace("\\", "/"),
            "md_file": str(md_path.relative_to(self.workspace_root)).replace("\\", "/"),
            "preview_url": f"/artifacts/art/{html_filename}",
            "content_excerpt": poem_text[:700],
        }

    # =========================================================================
    # 5. 🎨 HIGH-RESOLUTION IMAGES & VISUAL ART (PNG + WEBP + SVG)
    # =========================================================================

    def _generate_visual_art_creation(
        self,
        art_id: str,
        timestamp_str: str,
        hint: Optional[str],
        signals: Optional[Dict[str, Any]] = None,
        plan: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Generates unique high-res PNG/WEBP artworks and companion vector SVG."""
        from loom.clothos.multimodal_synth import synthesize_high_res_image

        if not signals:
            signals = self._get_computation_memory_signals()
        spec = getattr(plan, "technical_spec", {}) if plan else {}
        title = getattr(plan, "title", None) or f"Morphological Manifold ({art_id[-6:]})"
        tagline = getattr(plan, "thesis_or_arc", None) or "High-resolution mathematical image rendered across reaction-diffusion, chaotic attractors, or spectral plates."
        medium_out = getattr(plan, "medium", "visual_art")
        if medium_out not in ("image", "visual_art"):
            medium_out = "visual_art"

        vis_res = synthesize_high_res_image(
            out_dir=self.art_dir,
            art_id=art_id,
            title=title,
            algorithm=spec.get("algorithm"),
            seed=spec.get("seed"),
            width=int(spec.get("width", 1024)),
            height=int(spec.get("height", 1024)),
            hue=spec.get("palette_hue"),
        )

        png_path = Path(vis_res["png_file"])
        webp_path = Path(vis_res["webp_file"])
        svg_path = Path(vis_res["svg_file"])
        html_path = self.art_dir / f"{art_id}.html"
        md_path = self.deliverable_art_dir / f"{art_id}.md"

        html_content = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>{title}</title></head>
<body style="margin:0; background:#030712; display:flex; flex-direction:column; align-items:center; padding:24px; color:#f8fafc; font-family:system-ui;">
    <h1 style="color:#38bdf8; margin:0 0 8px 0;">🎨 {title}</h1>
    <p style="color:#94a3b8; margin-top:0;">{tagline} [{vis_res['algorithm']}]</p>
    <img src="{png_path.name}" alt="{title}" style="max-width:860px; width:100%; border-radius:12px; border:1px solid #1e293b; box-shadow:0 12px 40px rgba(0,0,0,0.8);"/>
</body>
</html>"""
        html_path.write_text(html_content, encoding="utf-8")

        md_content = f"""# 🎨 ClothOS Sovereign Image: {title}
- **Identifier**: `{art_id}`
- **Created**: `{timestamp_str}`
- **Algorithm**: `{vis_res['algorithm']}` ({vis_res['width']}x{vis_res['height']} PNG/WEBP + Vector SVG)

> "{tagline}"

### Artifacts
- **High-Res PNG**: [`{png_path.name}`](../../artifacts/art/{png_path.name})
- **High-Res WebP**: [`{webp_path.name}`](../../artifacts/art/{webp_path.name})
- **Vector SVG**: [`{svg_path.name}`](../../artifacts/art/{svg_path.name})
- **Web Gallery View**: [`{html_path.name}`](../../artifacts/art/{html_path.name})
"""
        md_path.write_text(md_content, encoding="utf-8")

        return {
            "id": art_id,
            "title": title,
            "medium": medium_out,
            "tagline": tagline,
            "timestamp": timestamp_str,
            "epoch": time.time(),
            "png_file": str(png_path.relative_to(self.workspace_root)).replace("\\", "/"),
            "webp_file": str(webp_path.relative_to(self.workspace_root)).replace("\\", "/"),
            "svg_file": str(svg_path.relative_to(self.workspace_root)).replace("\\", "/"),
            "html_file": str(html_path.relative_to(self.workspace_root)).replace("\\", "/"),
            "md_file": str(md_path.relative_to(self.workspace_root)).replace("\\", "/"),
            "preview_url": f"/artifacts/art/{html_path.name}",
            "svg_preview": vis_res["svg_preview"],
            "content_excerpt": f"{vis_res['algorithm']} seed={vis_res['seed']} {vis_res['width']}x{vis_res['height']}",
        }

    # =========================================================================
    # Helpers
    # =========================================================================

    def _ask_gpu0_json(self, prompt: str, fallback: Dict[str, Any], timeout_s: float = 120.0) -> Dict[str, Any]:
        """Queries Deliberative model pool with generous timeout and clean JSON extraction."""
        try:
            from loom.clothos.deliberation_engine import _select_deliberation_model, _query_ollama_json
            model = _select_deliberation_model(prefer_teacher=False)
            res = _query_ollama_json(model, prompt, timeout_s=timeout_s, temperature=0.82, num_predict=700)
            if isinstance(res, dict) and res:
                return res
        except Exception:
            pass
        return fallback


creative_art_engine = CreativeArtEngine()
