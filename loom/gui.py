"""
LOOM FABRIC COMMAND CENTER — Sovereign Heterogeneous Compute & Zero-Trust Orchestration GUI.

Architected to mirror the four pillars of Loom Fabric:
- THE WEAVE: Physical Cluster Hardware Topology & Distributed Dynamic Mesh (Ray + Stitch)
- THE SHUTTLE: Multi-Model Inference Dispatcher, Layer Sharding Telemetry & SSE Streaming Console
- TORQUE VAULT: Sovereign Zero-Trust IP/PII De-identification, Rehydration Mapping & Cloud Arbitrage Audit
- THE SPOOL: Preset Model Registry, Quantization Footprints & Memory Budgets

Cross-Platform Compatibility:
- Windows 10/11 (Direct3D/WDDM & Win32 Job Object Monitor)
- Linux (Ubuntu, Debian, Fedora, Arch — CUDA / ROCm / Vulkan)
- macOS (Apple Silicon M-Series Metal Unified Memory & Intel)
"""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import urllib.request
import urllib.error

# Botanical Meadow & Floral Breeze Palette (Air, Breeze, Lawns, Flowers, Plants) with Purple Accents
CLR_OBSIDIAN = "#07120a"      # Deep Forest Night Canvas
CLR_SURFACE = "#0d1e12"       # Meadow Surface
CLR_CARD = "#122818"          # Foliage Card Surface
CLR_BORDER = "#1d3d28"        # Dewstem Border
CLR_PURPLE = "#a855f7"        # Electric Violet Primary Accent (Mandated)
CLR_AMETHYST = "#c084fc"      # Wisteria Blossom Highlight
CLR_DEEP_PURPLE = "#7e22ce"   # Deep Royal Orchid
CLR_LILAC = "#e9d5ff"         # Morning Lilac Text
CLR_LAWN = "#10b981"          # Lush Lawn Emerald
CLR_CLOVER = "#34d399"        # Spring Clover Accent
CLR_MINT = "#6ee7b7"          # Morning Dew Mint
CLR_BREEZE = "#38bdf8"        # Air & Morning Breeze Sky
CLR_EMERALD = "#10b981"       # Online / Healthy Status
CLR_AMBER = "#f59e0b"         # Warning / Routing
CLR_CRIMSON = "#ef4444"       # Error / Offline
CLR_TEXT = "#f0fdf4"          # Pure Spring White
CLR_MUTED = "#bbf7d0"         # Pale Foliage Muted Text


class LoomFabricCommandCenter(tk.Tk):
    """Loom Fabric Sovereign Desktop Command Center — Botanical Edition."""

    def __init__(self, gateway_url: str = "http://127.0.0.1:8002"):
        super().__init__()
        self.gateway_url = gateway_url.rstrip("/")
        self.title("Loom Fabric Commander — Sovereign AI Operating System (Flora & Breeze)")
        self.geometry("1080x780")
        self.minsize(920, 640)
        self.configure(bg=CLR_OBSIDIAN)

        # Operating system brand tag
        self.os_tag = f"{platform.system()} ({platform.machine()})"

        self.is_running = True
        self.cluster_connected = False

        self._configure_styles()
        self._assemble_interface()

        # Launch background async polling thread
        self.poller = threading.Thread(target=self._telemetry_poller_daemon, daemon=True)
        self.poller.start()

    def _configure_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("TNotebook", background=CLR_OBSIDIAN, borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            background=CLR_CARD,
            foreground=CLR_TEXT,
            padding=[18, 10],
            font=("Segoe UI", 10, "bold"),
            borderwidth=0
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", CLR_PURPLE)],
            foreground=[("selected", CLR_TEXT)]
        )

        style.configure("TCombobox", fieldbackground=CLR_OBSIDIAN, background=CLR_CARD, foreground=CLR_TEXT)

    def _assemble_interface(self):
        # Top Masthead
        masthead = tk.Frame(self, bg=CLR_SURFACE, height=75, padx=24, pady=14, highlightbackground=CLR_BORDER, highlightthickness=1)
        masthead.pack(fill="x", side="top")

        title_container = tk.Frame(masthead, bg=CLR_SURFACE)
        title_container.pack(side="left")

        lbl_logo = tk.Label(title_container, text="🌿 LOOM FABRIC COMMANDER", font=("Segoe UI", 18, "bold"), fg=CLR_LAWN, bg=CLR_SURFACE)
        lbl_logo.pack(side="left")

        lbl_subtitle = tk.Label(title_container, text="  // Sovereign Flora & Breeze Mesh", font=("Segoe UI", 10, "bold"), fg=CLR_AMETHYST, bg=CLR_SURFACE)
        lbl_subtitle.pack(side="left", pady=3)

        # Right Telemetry Hub
        right_meta = tk.Frame(masthead, bg=CLR_SURFACE)
        right_meta.pack(side="right")

        self.lbl_os = tk.Label(right_meta, text=f"HOST: {self.os_tag}", font=("Consolas", 9), fg=CLR_MUTED, bg=CLR_SURFACE)
        self.lbl_os.pack(side="top", anchor="e")

        self.badge_status = tk.Label(
            right_meta,
            text="● BLOOMING MESH",
            font=("Segoe UI", 9, "bold"),
            fg=CLR_AMBER,
            bg="#0f2416",
            padx=12,
            pady=3,
            relief="solid",
            bd=1
        )
        self.badge_status.pack(side="bottom", pady=(4, 0))

        # Main Navigator (The Four Pillars)
        self.navigator = ttk.Notebook(self)
        self.navigator.pack(fill="both", expand=True, padx=20, pady=16)

        # Pillar 1 & 3: THE WEAVE (Cluster Topology & Ray Mesh)
        self.tab_weave = tk.Frame(self.navigator, bg=CLR_OBSIDIAN, padx=16, pady=16)
        self.navigator.add(self.tab_weave, text="🌱 The Weave (Cluster Topology)")
        self._build_weave_tab(self.tab_weave)

        # Pillar 4: THE SHUTTLE (Inference Console & Dispatcher)
        self.tab_shuttle = tk.Frame(self.navigator, bg=CLR_OBSIDIAN, padx=16, pady=16)
        self.navigator.add(self.tab_shuttle, text="🌿 The Shuttle (Model Triage & Compute)")
        self._build_shuttle_tab(self.tab_shuttle)

        # Pillar 1: TORQUE VAULT (Zero-Trust De-identification)
        self.tab_torque = tk.Frame(self.navigator, bg=CLR_OBSIDIAN, padx=16, pady=16)
        self.navigator.add(self.tab_torque, text="🌸 Torque Enclave (Zero-Trust Vault)")
        self._build_torque_tab(self.tab_torque)

        # Pillar 2: THE SPOOL (Model Presets & Zero-OOM Budgets)
        self.tab_spool = tk.Frame(self.navigator, bg=CLR_OBSIDIAN, padx=16, pady=16)
        self.navigator.add(self.tab_spool, text="🌾 The Spool (Hardware Models & Sharding)")
        self._build_spool_tab(self.tab_spool)

    def _build_weave_tab(self, parent):
        grid = tk.Frame(parent, bg=CLR_OBSIDIAN)
        grid.pack(fill="x", pady=(0, 14))

        # Worker Node Card
        w_card = tk.Frame(grid, bg=CLR_CARD, padx=16, pady=14, highlightbackground=CLR_BORDER, highlightthickness=1)
        w_card.pack(side="left", fill="both", expand=True, padx=(0, 8))

        tk.Label(w_card, text="WORKER NODE // SKYTECH", font=("Segoe UI", 10, "bold"), fg=CLR_PURPLE, bg=CLR_CARD).pack(anchor="w", pady=(0, 8))
        self.w_ip = tk.Label(w_card, text="IP: 192.168.99.1 (1Gbps P2P Mesh)", font=("Segoe UI", 9), fg=CLR_TEXT, bg=CLR_CARD)
        self.w_ip.pack(anchor="w", pady=2)
        self.w_gpu0 = tk.Label(w_card, text="GPU 0: NVIDIA RTX 3060 12GB (CUDA 12.x)", font=("Segoe UI", 9), fg=CLR_EMERALD, bg=CLR_CARD)
        self.w_gpu0.pack(anchor="w", pady=2)
        self.w_gpu1 = tk.Label(w_card, text="GPU 1: AMD RX 580 8GB (Vulkan 1.3)", font=("Segoe UI", 9), fg=CLR_EMERALD, bg=CLR_CARD)
        self.w_gpu1.pack(anchor="w", pady=2)
        self.w_ram = tk.Label(w_card, text="Host Memory: 40 GB DDR4 System RAM", font=("Segoe UI", 9), fg=CLR_TEXT, bg=CLR_CARD)
        self.w_ram.pack(anchor="w", pady=2)
        self.w_guard = tk.Label(w_card, text="Lifecycle Guard: Win32 Job Object / POSIX cgroups", font=("Segoe UI", 8), fg=CLR_MUTED, bg=CLR_CARD)
        self.w_guard.pack(anchor="w", pady=(6, 0))

        # Head Node Card
        h_card = tk.Frame(grid, bg=CLR_CARD, padx=16, pady=14, highlightbackground=CLR_BORDER, highlightthickness=1)
        h_card.pack(side="left", fill="both", expand=True, padx=(8, 0))

        tk.Label(h_card, text="HEAD NODE // RYZEN 7 7730U", font=("Segoe UI", 10, "bold"), fg=CLR_PURPLE, bg=CLR_CARD).pack(anchor="w", pady=(0, 8))
        self.h_ip = tk.Label(h_card, text="IP: 192.168.99.2 (1Gbps P2P Mesh)", font=("Segoe UI", 9), fg=CLR_TEXT, bg=CLR_CARD)
        self.h_ip.pack(anchor="w", pady=2)
        self.h_cpu = tk.Label(h_card, text="Compute: 16 Zen 3 vCPUs, 16 GB DDR4", font=("Segoe UI", 9), fg=CLR_TEXT, bg=CLR_CARD)
        self.h_cpu.pack(anchor="w", pady=2)
        self.h_ray = tk.Label(h_card, text="Ray Cluster GCS: 6379 | Dashboard: 8265", font=("Segoe UI", 9), fg=CLR_EMERALD, bg=CLR_CARD)
        self.h_ray.pack(anchor="w", pady=2)
        self.h_gw = tk.Label(h_card, text="Loom Gateway: Port 8002 (OpenAI SSE Proxy)", font=("Segoe UI", 9), fg=CLR_TEXT, bg=CLR_CARD)
        self.h_gw.pack(anchor="w", pady=2)
        self.h_openclaw = tk.Label(h_card, text="OpenClaw Mesh: Synchronized across Both Nodes", font=("Segoe UI", 8), fg=CLR_EMERALD, bg=CLR_CARD)
        self.h_openclaw.pack(anchor="w", pady=(6, 0))

        # Diagnostic Raw Stream
        tk.Label(parent, text="PHYSICAL ACCELERATOR TELEMETRY STREAM", font=("Segoe UI", 9, "bold"), fg=CLR_MUTED, bg=CLR_OBSIDIAN).pack(anchor="w", pady=(8, 4))
        self.txt_telemetry = scrolledtext.ScrolledText(
            parent,
            bg=CLR_CARD,
            fg=CLR_TEXT,
            font=("Consolas", 9),
            height=14,
            relief="flat",
            insertbackground=CLR_TEXT
        )
        self.txt_telemetry.pack(fill="both", expand=True)

    def _build_shuttle_tab(self, parent):
        controls = tk.Frame(parent, bg=CLR_OBSIDIAN)
        controls.pack(fill="x", pady=(0, 10))

        tk.Label(controls, text="Select Target Model:", font=("Segoe UI", 9, "bold"), fg=CLR_TEXT, bg=CLR_OBSIDIAN).pack(side="left", padx=(0, 8))
        self.sel_model = ttk.Combobox(
            controls,
            values=["qwen2.5:32b", "deepseek-r1:14b", "qwen2.5:7b", "qwen2.5:3b"],
            state="readonly",
            width=22
        )
        self.sel_model.set("qwen2.5:32b")
        self.sel_model.pack(side="left", padx=(0, 14))

        self.lbl_telemetry_tag = tk.Label(controls, text="Routing: Standby", font=("Segoe UI", 9, "bold"), fg=CLR_MUTED, bg=CLR_OBSIDIAN)
        self.lbl_telemetry_tag.pack(side="left")

        # Live Real-Time Generation Progress Bar & Token Indicator
        self.progress_frame = tk.Frame(controls, bg=CLR_OBSIDIAN)
        self.progress_frame.pack(side="right", padx=(10, 0))

        self.lbl_tokens_live = tk.Label(self.progress_frame, text="", font=("Consolas", 8, "bold"), fg=CLR_AMETHYST, bg=CLR_OBSIDIAN)
        self.lbl_tokens_live.pack(side="left", padx=(0, 8))

        self.progress_bar = ttk.Progressbar(self.progress_frame, mode="indeterminate", length=140)

        # Chat Stream Area
        self.txt_chat = scrolledtext.ScrolledText(
            parent,
            bg=CLR_CARD,
            fg=CLR_TEXT,
            font=("Consolas", 10),
            height=18,
            relief="flat",
            wrap="word",
            insertbackground=CLR_TEXT
        )
        self.txt_chat.pack(fill="both", expand=True, pady=(0, 12))

        # Input Frame
        in_frame = tk.Frame(parent, bg=CLR_OBSIDIAN)
        in_frame.pack(fill="x")

        self.input_box = tk.Entry(
            in_frame,
            bg=CLR_CARD,
            fg=CLR_TEXT,
            font=("Segoe UI", 10),
            relief="flat",
            insertbackground=CLR_TEXT
        )
        self.input_box.pack(side="left", fill="x", expand=True, padx=(0, 10), ipady=8)
        self.input_box.bind("<Return>", lambda e: self._dispatch_completion())

        btn_send = tk.Button(
            in_frame,
            text="Launch Query",
            font=("Segoe UI", 9, "bold"),
            bg=CLR_PURPLE,
            fg=CLR_OBSIDIAN,
            activebackground=CLR_EMERALD,
            relief="flat",
            padx=20,
            command=self._dispatch_completion
        )
        btn_send.pack(side="right")

    def _build_torque_tab(self, parent):
        tk.Label(parent, text="TORQUE // ZERO-TRUST IP & CREDENTIAL VAULT", font=("Segoe UI", 12, "bold"), fg=CLR_PURPLE, bg=CLR_OBSIDIAN).pack(anchor="w", pady=(0, 4))
        tk.Label(
            parent,
            text="All queries routing to Tier 3 Cloud Arbitrage (>300s compute) are scrubbed before departure.\n"
                 "Entities like 'fouriersLibrary', 'VectorForge', 'Mycos', and API keys are mapped into synthetic vault tokens\n"
                 "and rehydrated on the fly before delivery back to the client.",
            font=("Segoe UI", 9),
            fg=CLR_MUTED,
            bg=CLR_OBSIDIAN,
            justify="left"
        ).pack(anchor="w", pady=(0, 12))

        self.txt_vault = scrolledtext.ScrolledText(
            parent,
            bg=CLR_CARD,
            fg=CLR_EMERALD,
            font=("Consolas", 10),
            height=20,
            relief="flat",
            insertbackground=CLR_TEXT
        )
        self.txt_vault.pack(fill="both", expand=True)

    def _build_spool_tab(self, parent):
        tk.Label(parent, text="THE SPOOL // HARDWARE BENCHMARKS & MODEL PROVISIONER", font=("Segoe UI", 12, "bold"), fg=CLR_PURPLE, bg=CLR_OBSIDIAN).pack(anchor="w", pady=(0, 4))
        tk.Label(
            parent,
            text="Intelligently matches local open-weights LLMs based on GPU memory bandwidth, compute capability, and benchmark scores.\nAlso manages zero-trust cloud API bridges (OpenAI, Anthropic, Google Gemini, OpenRouter).",
            font=("Segoe UI", 9),
            fg=CLR_MUTED,
            bg=CLR_OBSIDIAN,
            justify="left"
        ).pack(anchor="w", pady=(0, 10))

        # Top Action Bar: 1-Click Install
        action_bar = tk.Frame(parent, bg=CLR_OBSIDIAN)
        action_bar.pack(fill="x", pady=(0, 10))

        tk.Label(action_bar, text="Install Recommended Model:", font=("Segoe UI", 9, "bold"), fg=CLR_TEXT, bg=CLR_OBSIDIAN).pack(side="left", padx=(0, 8))
        self.combo_pull = ttk.Combobox(
            action_bar,
            values=["qwen2.5:32b", "deepseek-r1:14b", "qwen2.5:7b", "qwen2.5:3b", "llama3.3:70b"],
            state="readonly",
            width=20
        )
        self.combo_pull.set("qwen2.5:32b")
        self.combo_pull.pack(side="left", padx=(0, 10))

        btn_pull = tk.Button(
            action_bar,
            text="1-Click Pull Model",
            font=("Segoe UI", 9, "bold"),
            bg=CLR_PURPLE,
            fg=CLR_OBSIDIAN,
            activebackground=CLR_AMETHYST,
            relief="flat",
            padx=14,
            command=self._pull_selected_model
        )
        btn_pull.pack(side="left")

        btn_refresh = tk.Button(
            action_bar,
            text="Re-evaluate Benchmarks",
            font=("Segoe UI", 9),
            bg=CLR_CARD,
            fg=CLR_TEXT,
            relief="flat",
            padx=12,
            command=self._refresh_spool_evaluations
        )
        btn_refresh.pack(side="left", padx=(10, 0))

        self.txt_spool = scrolledtext.ScrolledText(
            parent,
            bg=CLR_CARD,
            fg=CLR_TEXT,
            font=("Consolas", 9),
            height=20,
            relief="flat",
            insertbackground=CLR_TEXT
        )
        self.txt_spool.pack(fill="both", expand=True)

        # Initial populate
        self.after(500, self._refresh_spool_evaluations)

    def _pull_selected_model(self):
        target = self.combo_pull.get()
        if not target:
            return
        messagebox.showinfo("Loom Fabric Provisioner", f"Starting background download for '{target}' via sovereign Ollama runtime.\nYou can monitor progress in terminal or check The Spool tab.")
        def _pull_thread():
            from loom.models.recommender import ModelHardwareRecommender
            rec = ModelHardwareRecommender()
            rec.install_model_cli(target)
            self._refresh_spool_evaluations()
        threading.Thread(target=_pull_thread, daemon=True).start()

    def _refresh_spool_evaluations(self):
        def _compute():
            from loom.models.recommender import ModelHardwareRecommender
            from loom.gateway.cloud_bridge import CloudLLMBridge, CLOUD_PROVIDERS

            rec = ModelHardwareRecommender()
            recs = rec.evaluate_hardware_fit()

            bridge = CloudLLMBridge()
            cloud_status = bridge.get_provider_status()

            lines = []
            lines.append("=== LOCAL HARDWARE-MATCHED MODEL BENCHMARK RECOMMENDATIONS ===")
            lines.append(f"{'MODEL':<18} | {'BENCHMARK (MMLU/CODE)':<22} | {'HARDWARE FIT':<26} | {'EST. SPEED':<12} | {'STATUS'}")
            lines.append("-" * 95)
            for r in recs:
                bench_str = f"MMLU: {r.benchmark.mmlu_score:.0f}% / Code: {r.benchmark.humaneval_coding:.0f}%"
                status_str = "INSTALLED" if r.is_installed else "NOT PULLED"
                lines.append(f"{r.preset.id:<18} | {bench_str:<22} | {r.fit_status:<26} | {r.estimated_speed_tps:<5.1f} tps  | {status_str}")
                lines.append(f"   ↳ Rationale: {r.recommendation_reason}\n")

            lines.append("\n=== CLOUD LLM API PROVIDER BRIDGES (ZERO-TRUST SANITIZED) ===")
            lines.append(f"{'PROVIDER':<18} | {'DEFAULT MODEL':<28} | {'API KEY ENV VAR':<20} | {'STATUS'}")
            lines.append("-" * 80)
            for key, p in CLOUD_PROVIDERS.items():
                is_ready = "CONFIGURED (READY)" if cloud_status.get(key, False) else "KEY MISSING"
                lines.append(f"{p.name:<18} | {p.default_model:<28} | ${p.api_key_env_var:<19} | {is_ready}")

            lines.append("\n[Tip] Any query requiring >300s compute is automatically sanitized via Torque Vault and dispatched to Cloud APIs.")

            content = "\n".join(lines)
            def _set():
                self.txt_spool.delete("1.0", tk.END)
                self.txt_spool.insert(tk.END, content)
            self.after(0, _set)

        threading.Thread(target=_compute, daemon=True).start()

    def _telemetry_poller_daemon(self):
        while self.is_running:
            try:
                req = urllib.request.Request(f"{self.gateway_url}/health")
                with urllib.request.urlopen(req, timeout=2) as resp:
                    if resp.status == 200:
                        self.cluster_connected = True
                        self._set_status_badge("● CLUSTER ONLINE", CLR_EMERALD, "#052e16")
            except Exception:
                self.cluster_connected = False
                self._set_status_badge("● GATEWAY OFFLINE", CLR_CRIMSON, "#2a0c0c")

            if self.cluster_connected:
                try:
                    req_m = urllib.request.Request(f"{self.gateway_url}/metrics")
                    with urllib.request.urlopen(req_m, timeout=2) as resp_m:
                        data = json.loads(resp_m.read().decode())
                        self._render_telemetry_data(data)
                except Exception:
                    pass

            time.sleep(3)

    def _set_status_badge(self, text, fg_color, bg_color):
        self.after(0, lambda: self.badge_status.config(text=text, fg=fg_color, bg=bg_color))

    def _render_telemetry_data(self, data):
        hw = data.get("cluster_hardware", {})
        gpus = hw.get("gpus", [])
        host = hw.get("host", {})
        lines = []
        lines.append(f"Snapshot Time: {time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        lines.append(f"Host Topology: {host.get('hostname')} | OS: {host.get('os_name')} | Cores: {host.get('cpu_cores_logical')} vCPUs")
        lines.append(f"Memory Pools:  Total Physical: {host.get('total_ram_mb', 0):,} MB | Available: {host.get('available_ram_mb', 0):,} MB\n")
        lines.append("ENUMERATED ACCELERATORS:")
        for idx, g in enumerate(gpus):
            lines.append(f"  Tier [{idx}] -> {g.get('name')}")
            lines.append(f"      Vendor: {g.get('vendor')} | Backend: {g.get('backend')} | Total VRAM: {g.get('total_vram_mb', 0):,} MB | Free: {g.get('free_vram_mb', 0):,} MB")

        lines.append(f"\nREGISTERED RAY CUSTOM RESOURCES:\n{json.dumps(hw.get('ray_custom_resources', {}), indent=2)}")

        rendered = "\n".join(lines)
        def _update():
            self.txt_telemetry.delete("1.0", tk.END)
            self.txt_telemetry.insert(tk.END, rendered)
        self.after(0, _update)

    def _dispatch_completion(self):
        prompt = self.input_box.get().strip()
        if not prompt:
            return
        self.input_box.delete(0, tk.END)

        model = self.sel_model.get()
        self.txt_chat.insert(tk.END, f"\nUser > {prompt}\n", "user")
        self.txt_chat.insert(tk.END, f"Loom Fabric ({model}) > ", "assistant")
        self.txt_chat.see(tk.END)

        # Show & start progress bar
        self.progress_bar.pack(side="left")
        self.progress_bar.start(10)
        self.lbl_tokens_live.config(text="Deciphering Route...", fg=CLR_AMBER)

        threading.Thread(target=self._run_async_streaming_query, args=(prompt, model), daemon=True).start()

    def _run_async_streaming_query(self, prompt, model):
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": True
        }
        token_count = 0
        start_time = time.time()
        try:
            req = urllib.request.Request(
                f"{self.gateway_url}/v1/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                headers = dict(resp.getheaders())
                route = headers.get("x-torque-route", "Local")
                scrubbed = headers.get("x-torque-scrubbed", "false")
                tps = headers.get("x-loom-tokens-per-sec", "N/A")

                tag_msg = f"Route: {route} | Scrubbed: {scrubbed}"
                self.after(0, lambda: self.lbl_telemetry_tag.config(text=tag_msg, fg=CLR_EMERALD))

                # Update Torque Vault log if scrubbed
                if scrubbed.lower() == "true":
                    vault_entry = f"[{time.strftime('%H:%M:%S')}] Scrubbed & Rehydrated Query for model {model}:\nOriginal Prompt Snippet: {prompt[:80]}...\nRoute: {route}\n"
                    def _update_v():
                        self.txt_vault.insert(tk.END, vault_entry)
                        self.txt_vault.see(tk.END)
                    self.after(0, _update_v)

                # Process SSE line stream in real time
                for line in resp:
                    decoded = line.decode("utf-8").strip()
                    if not decoded or not decoded.startswith("data:"):
                        continue
                    if decoded == "data: [DONE]":
                        break

                    try:
                        chunk_json = json.loads(decoded[5:].strip())
                        choices = chunk_json.get("choices", [])
                        if choices:
                            delta = choices[0].get("delta", {}).get("content", "")
                            if delta:
                                token_count += 1
                                elapsed = max(0.001, time.time() - start_time)
                                live_tps = token_count / elapsed

                                def _stream_chunk(text=delta, count=token_count, speed=live_tps):
                                    self.txt_chat.insert(tk.END, text)
                                    self.txt_chat.see(tk.END)
                                    self.lbl_tokens_live.config(text=f"{count} tokens ({speed:.1f} tps)", fg=CLR_AMETHYST)
                                self.after(0, _stream_chunk)
                    except Exception:
                        pass

        except Exception as e:
            # Fallback to non-streaming if stream interrupted
            try:
                payload["stream"] = False
                req_fallback = urllib.request.Request(
                    f"{self.gateway_url}/v1/chat/completions",
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req_fallback, timeout=120) as resp2:
                    data = json.loads(resp2.read().decode())
                    content = data["choices"][0]["message"]["content"]
                    def _fallback_render():
                        self.txt_chat.insert(tk.END, content)
                        self.txt_chat.see(tk.END)
                    self.after(0, _fallback_render)
            except Exception as e2:
                def _render_err():
                    self.txt_chat.insert(tk.END, f"\n[Error: {e2}]\n\n")
                    self.txt_chat.see(tk.END)
                self.after(0, _render_err)

        finally:
            def _stop_progress():
                self.progress_bar.stop()
                self.progress_bar.pack_forget()
                self.txt_chat.insert(tk.END, "\n\n")
                self.txt_chat.see(tk.END)
            self.after(0, _stop_progress)


def main():
    app = LoomFabricCommandCenter()
    app.mainloop()


if __name__ == "__main__":
    main()
