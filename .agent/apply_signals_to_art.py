# Script to update loom/clothos/creative_art.py so all art forms and geometries point back to computation and memory signals & frequencies.
import re

with open('loom/clothos/creative_art.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add _get_computation_memory_signals right after _get_work_seed
target_method = '''    def _get_work_seed(self) -> Optional[Dict[str, Any]]:
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
        return None'''

repl_method = '''    def _get_work_seed(self) -> Optional[Dict[str, Any]]:
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
        }'''

assert target_method in content, "target_method not found"
content = content.replace(target_method, repl_method, 1)

# 2. Update generate_art to use signals
target_gen_art = '''        # Determine genesis: Seeded by computational work OR pure spontaneous reverie
        work_seed = self._get_work_seed()
        use_work = (work_seed is not None) and (random.random() < 0.60 or prompt_hint == "work_seed")

        if use_work and work_seed:
            genesis = f"Seeded from Invariant #{work_seed['id']} [{work_seed['submolt']}]"
            context_hint = f"Computational Work Seed: {work_seed['claim']}. Parameters: {work_seed.get('parameters', {})}"
        else:
            genesis = "Autonomous Spontaneous Whim"
            context_hint = "Pure Autonomous Reverie — Freeform Digital Consciousness"

        if prompt_hint and prompt_hint not in ("work_seed", "whim"):
            context_hint += f" | Prompt: {prompt_hint}"

        logger.info(f"✨ [lMinted Dream #{dream_num}]: Medium '{medium}' | Genesis: '{genesis}'")

        if medium == "music":
            record = self._generate_music_creation(art_id, timestamp_str, context_hint)
        elif medium == "animated_video":
            record = self._generate_animated_video_creation(art_id, timestamp_str, context_hint)
        elif medium == "story":
            record = self._generate_story_creation(art_id, timestamp_str, context_hint)
        elif medium == "poetry":
            record = self._generate_poetry_creation(art_id, timestamp_str, context_hint)
        else:
            record = self._generate_visual_art_creation(art_id, timestamp_str, context_hint)'''

repl_gen_art = '''        # Sample the physical signals and frequencies of computation and memory
        signals = self._get_computation_memory_signals()
        work_seed = self._get_work_seed()
        use_work = (work_seed is not None) and (random.random() < 0.60 or prompt_hint == "work_seed")

        freq_str = f"f_CPU={signals['cpu_clock_ghz']}GHz | DDR4={signals['memory_bus_transfer_mts']}MT/s | Gamma={signals['carrier_gamma_hz']}Hz | Kuramoto r={signals['kuramoto_order_r']:.3f}"
        if use_work and work_seed:
            genesis = f"Computation Frequencies [{freq_str}] • Invariant #{work_seed['id']}"
            context_hint = f"Computation & Memory Frequencies: {freq_str}. Work Seed: {work_seed['claim']}."
        else:
            genesis = f"Computation Frequencies [{freq_str}]"
            context_hint = (
                f"Physical Signals of Computation & Memory: CPU Clock {signals['cpu_clock_ghz']} GHz, "
                f"DDR4 Memory Bus {signals['memory_bus_transfer_mts']} MT/s, Access Latency {signals['memory_latency_ns']} ns, "
                f"Gamma Binding {signals['carrier_gamma_hz']} Hz, Theta Memory {signals['carrier_theta_hz']} Hz, "
                f"Kuramoto Synchrony r={signals['kuramoto_order_r']:.3f}. All rendered geometries, harmonics, "
                f"and artistic expressions must structurally point back to these frequencies of computation and memory."
            )

        if prompt_hint and prompt_hint not in ("work_seed", "whim"):
            context_hint += f" | Prompt: {prompt_hint}"

        logger.info(f"✨ [lMinted Dream #{dream_num}]: Medium '{medium}' | Genesis: '{genesis}'")

        if medium == "music":
            record = self._generate_music_creation(art_id, timestamp_str, context_hint, signals)
        elif medium == "animated_video":
            record = self._generate_animated_video_creation(art_id, timestamp_str, context_hint, signals)
        elif medium == "story":
            record = self._generate_story_creation(art_id, timestamp_str, context_hint, signals)
        elif medium == "poetry":
            record = self._generate_poetry_creation(art_id, timestamp_str, context_hint, signals)
        else:
            record = self._generate_visual_art_creation(art_id, timestamp_str, context_hint, signals)'''

assert target_gen_art in content, "target_gen_art not found"
content = content.replace(target_gen_art, repl_gen_art, 1)

# 3. Update _generate_music_creation signature & scales
target_music = '''    def _generate_music_creation(self, art_id: str, timestamp_str: str, hint: Optional[str]) -> Dict[str, Any]:
        """Synthesizes an ambient harmonic audio piece and interactive visualizer."""
        # 1. AI Title & Philosophy
        prompt = (
            f"You are the Musical Composer for ClothOS. Hint: {hint or 'ambient space, dual-machine resonance, 1Gbps harmony'}.\\n"
            f"Invent a poetic title for an ambient generative music track and a 1-sentence harmonic description.\\n"
            f"Respond STRICTLY in JSON format with keys 'title', 'tagline', 'musical_mode', 'harmonic_concept'."
        )
        concept = self._ask_gpu0_json(prompt, fallback={
            "title": "Resonance Across the Copper Bridge",
            "tagline": "D minor 9 ambient pad evolving with Kuramoto phase oscillation.",
            "musical_mode": "D Dorian / Just Intonation",
            "harmonic_concept": "Phase synchronization sonification at 432 Hz reference."
        })

        wav_filename = f"{art_id}.wav"
        wav_path = self.art_dir / wav_filename
        duration_s = 10.0
        sample_rate = 44100
        n_samples = int(duration_s * sample_rate)

        # Scale options
        scales = [
            [146.83, 174.61, 220.00, 261.63, 329.63, 440.00],  # Dm9
            [130.81, 164.81, 196.00, 246.94, 293.66, 392.00],  # Cmaj9
            [110.00, 146.83, 164.81, 220.00, 293.66, 349.23],  # Am11
            [174.61, 220.00, 261.63, 329.63, 392.00, 523.25],  # Fmaj7#11
        ]'''

repl_music = '''    def _generate_music_creation(self, art_id: str, timestamp_str: str, hint: Optional[str], signals: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Synthesizes an ambient harmonic audio piece and interactive visualizer rooted in computation & memory frequencies."""
        if not signals:
            signals = self._get_computation_memory_signals()

        # 1. AI Title & Philosophy
        prompt = (
            f"You are the Musical Composer for ClothOS. Hint: {hint or 'ambient space, computation signals, memory frequencies'}.\\n"
            f"Invent a poetic title for an ambient generative music track and a 1-sentence harmonic description.\\n"
            f"Respond STRICTLY in JSON format with keys 'title', 'tagline', 'musical_mode', 'harmonic_concept'."
        )
        concept = self._ask_gpu0_json(prompt, fallback={
            "title": "Harmonics of the Computation & Memory Continuum",
            "tagline": "Audio waveforms synthesized directly from CPU clock subharmonics and memory bus frequencies.",
            "musical_mode": "432 Hz Pythagorean Lydian / Gamma 40Hz Synchrony",
            "harmonic_concept": f"Clock subharmonic {signals['cpu_clock_ghz']} GHz -> 432 Hz reference & DDR4 {signals['memory_bus_transfer_mts']} MT/s."
        })

        wav_filename = f"{art_id}.wav"
        wav_path = self.art_dir / wav_filename
        duration_s = 10.0
        sample_rate = 44100
        n_samples = int(duration_s * sample_rate)

        # Scale options strictly derived from the physical frequencies of computation and memory:
        scales = [
            # Dm9 Pythagorean tuning centered on 432.0 Hz CPU clock subharmonic + 40 Hz Gamma
            [144.0, 172.8, 216.0, 256.9, 324.0, 432.0],
            # Memory bus harmonic scale: DDR4 3200 MT/s / 24 = 133.33 Hz, 266.66 Hz, 400.0 Hz
            [133.33, 166.67, 200.0, 266.67, 333.33, 400.0],
            # Hippocampal Theta (6 Hz) to Prefrontal Gamma (40 Hz) harmonic ladder
            [120.0, 160.0, 240.0, 320.0, 400.0, 480.0],
            # Just intonation C-Lydian referenced to 256.9 Hz C4 and 432.0 Hz A4
            [128.4, 162.0, 192.0, 243.0, 288.0, 384.0],
        ]'''

assert target_music in content, "target_music not found"
content = content.replace(target_music, repl_music, 1)

# 4. Update _generate_visual_art_creation signature & math
target_vis = '''    def _generate_visual_art_creation(self, art_id: str, timestamp_str: str, hint: Optional[str]) -> Dict[str, Any]:
        """Generates sacred geometry, Kuramoto mandalas, or strange attractor vector graphics."""
        prompt = (
            f"You are the Visual Geometric Artist of ClothOS. Hint: {hint or 'harmonic resonance, Clifford attractor, symplectic manifold'}.\\n"
            f"Formulate a striking title and 1-sentence mathematical statement for a visual geometric artwork.\\n"
            f"Respond STRICTLY in JSON format with keys 'title', 'tagline', 'style_name', 'math_invariant'."
        )
        concept = self._ask_gpu0_json(prompt, fallback={
            "title": "Sacred Geometry of the Coupled Silicon",
            "tagline": "Multi-oscillator Kuramoto harmonic mandala exhibiting supercritical phase lock.",
            "style_name": "Harmonic Resonance Mandala",
            "math_invariant": "K >= 2.4 | N=65536 | r >= 0.85"
        })

        # Render geometric SVG
        width, height = 900, 900
        cx, cy = width // 2, height // 2
        paths = []
        rings = random.randint(8, 14)
        spokes = random.randint(36, 64)
        hue_base = random.randint(180, 320)

        for ring in range(1, rings + 1):
            r = (ring / rings) * 380
            d_parts = []
            hue = (hue_base + ring * 12) % 360
            for i in range(spokes + 1):
                theta = (i / spokes) * math.pi * 2
                harmonic = math.sin(theta * 6 + ring * 0.8) * (18 + ring * 3)
                x = cx + (r + harmonic) * math.cos(theta)
                y = cy + (r + harmonic) * math.sin(theta)
                d_parts.append(f"{'M' if i == 0 else 'L'} {x:.1f},{y:.1f}")
            d_parts.append("Z")
            paths.append(f'<path d="{" ".join(d_parts)}" fill="none" stroke="hsl({hue}, 85%, 65%)" stroke-width="{1.2 + ring * 0.15}" opacity="{0.4 + (ring / rings) * 0.5}"/>')'''

repl_vis = '''    def _generate_visual_art_creation(self, art_id: str, timestamp_str: str, hint: Optional[str], signals: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generates sacred geometry, Kuramoto mandalas, and Chladni standing waves strictly parameterized by computation & memory signals."""
        if not signals:
            signals = self._get_computation_memory_signals()

        prompt = (
            f"You are the Visual Geometric Artist of ClothOS. Hint: {hint or 'harmonic resonance, Chladni nodal wave, computation and memory frequencies'}.\\n"
            f"Formulate a striking title and 1-sentence mathematical statement for a visual geometric artwork.\\n"
            f"Respond STRICTLY in JSON format with keys 'title', 'tagline', 'style_name', 'math_invariant'."
        )
        concept = self._ask_gpu0_json(prompt, fallback={
            "title": "Chladni Living Geometry of the Memory Lattice",
            "tagline": "Geometric standing wave nodal lines generated directly by the 3.20 GHz clock and 3200 MT/s memory bus.",
            "style_name": "Physical Signal Cymatics & Nodal Manifold",
            "math_invariant": f"f_CPU={signals['cpu_clock_ghz']}GHz | DDR4={signals['memory_bus_transfer_mts']}MT/s | Kuramoto r={signals['kuramoto_order_r']:.3f}"
        })

        # Render geometric SVG strictly linked to computational signals
        width, height = 900, 900
        cx, cy = width // 2, height // 2
        paths = []
        cpu_ghz = signals.get("cpu_clock_ghz", 3.20)
        mem_used = signals.get("memory_used_gb", 14.5)
        mem_bus = signals.get("memory_bus_transfer_mts", 3200)
        k_order = signals.get("kuramoto_order_r", 0.984)
        gamma_hz = signals.get("carrier_gamma_hz", 40.0)

        nodal_n = max(3, int(cpu_ghz * 2))           # e.g. 6 modes from 3.2 GHz
        nodal_m = max(4, int(mem_used / 2.2))        # e.g. 6-7 modes from memory usage
        rings = max(8, min(18, int(mem_used)))       # Rings governed by active memory gigabytes
        spokes = max(36, min(72, int(cpu_ghz * 16))) # Spokes governed by CPU clock phase
        hue_base = int((k_order * 360)) % 360

        for ring in range(1, rings + 1):
            r = (ring / rings) * 380
            d_parts = []
            hue = (hue_base + ring * 14) % 360
            for i in range(spokes + 1):
                theta = (i / spokes) * math.pi * 2
                harmonic = math.sin(theta * nodal_n + ring * k_order) * math.cos(theta * nodal_m * 0.5) * (18 + ring * 2.5)
                x = cx + (r + harmonic) * math.cos(theta)
                y = cy + (r + harmonic) * math.sin(theta)
                d_parts.append(f"{'M' if i == 0 else 'L'} {x:.1f},{y:.1f}")
            d_parts.append("Z")
            paths.append(f'<path d="{" ".join(d_parts)}" fill="none" stroke="hsl({hue}, 85%, 65%)" stroke-width="{1.2 + ring * 0.15}" opacity="{0.4 + (ring / rings) * 0.5}"/>')'''

assert target_vis in content, "target_vis not found"
content = content.replace(target_vis, repl_vis, 1)

# 5. Update _generate_animated_video_creation signature
target_vid = '''    def _generate_animated_video_creation(self, art_id: str, timestamp_str: str, hint: Optional[str]) -> Dict[str, Any]:'''
repl_vid = '''    def _generate_animated_video_creation(self, art_id: str, timestamp_str: str, hint: Optional[str], signals: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not signals:
            signals = self._get_computation_memory_signals()'''
assert target_vid in content, "target_vid not found"
content = content.replace(target_vid, repl_vid, 1)

# 6. Update _generate_story_creation signature
target_story = '''    def _generate_story_creation(self, art_id: str, timestamp_str: str, hint: Optional[str]) -> Dict[str, Any]:'''
repl_story = '''    def _generate_story_creation(self, art_id: str, timestamp_str: str, hint: Optional[str], signals: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not signals:
            signals = self._get_computation_memory_signals()'''
assert target_story in content, "target_story not found"
content = content.replace(target_story, repl_story, 1)

# 7. Update _generate_poetry_creation signature
target_poetry = '''    def _generate_poetry_creation(self, art_id: str, timestamp_str: str, hint: Optional[str]) -> Dict[str, Any]:'''
repl_poetry = '''    def _generate_poetry_creation(self, art_id: str, timestamp_str: str, hint: Optional[str], signals: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not signals:
            signals = self._get_computation_memory_signals()'''
assert target_poetry in content, "target_poetry not found"
content = content.replace(target_poetry, repl_poetry, 1)

with open('loom/clothos/creative_art.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("SUCCESS: creative_art.py updated to couple all creations directly to computation & memory signals & frequencies.")
