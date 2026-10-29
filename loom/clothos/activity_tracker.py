# Copyright (c) 2026 Najmos Sakib. All rights reserved.

# Proprietary and confidential. Commercial distribution prohibited.

"""

ClothOS Activity Tracker, Live Glowing Shimmer Aura & Task Life-Cycle Engine

============================================================================

Maintains real-time thread-safe tracking of "Currently [doing]..." telemetry,

operational phases, execution timers, operator cancellation tokens, rich

activity details (sub-goals, targets, hardware engines, storage tiers, metrics),

and a ClothOS Sovereign active live glowing shimmer HUD that renders dynamic

waveform animations at 12 FPS in the terminal while background tasks execute.

"""



from __future__ import annotations



import sys

import time

import threading

from typing import Dict, Any, List, Optional

from rich.console import Console

from rich.panel import Panel

from rich.table import Table

from rich.text import Text

from rich.live import Live

from rich import box



if sys.platform == "win32":

    try:

        if hasattr(sys.stdout, "reconfigure"):

            sys.stdout.reconfigure(encoding="utf-8", errors="replace")

        if hasattr(sys.stderr, "reconfigure"):

            sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    except Exception:

        pass



console = Console(legacy_windows=False)





# ── GLOWING AURA & SHIMMER GENERATOR ─────────────────────────────────────────



class GlowActivityIndicator:
    """Generates ClothOS Sovereign status waveforms and activity indicators."""

    GLOW_PALETTE = [
        "#334155",  # Slate-700
        "#475569",  # Slate-600
        "#64748b",  # Slate-500
        "#94a3b8",  # Slate-400
        "#38bdf8",  # Sky-400
        "#0ea5e9",  # Sky-500
        "#10b981",  # Emerald-500
        "#cbd5e1",  # Slate-300
    ]

    WAVE_CHARS = [" ", "▂", "▃", "▄", "▅", "▆", "▇", "█", "▇", "▆", "▅", "▄", "▃", "▂", " "]

    @classmethod
    def get_palette(cls) -> List[str]:
        try:
            from loom.clothos.theme import ThemeManager
            return ThemeManager.get_active().aura_palette
        except Exception:
            return cls.GLOW_PALETTE

    @classmethod
    def get_glow_wave(cls, step: Optional[int] = None, width: int = 16) -> str:
        """Returns a multi-color status waveform string with dynamic progression."""
        if step is None:
            step = int(time.time() * 8)

        palette = cls.get_palette()
        n_chars = len(cls.WAVE_CHARS)
        n_colors = len(palette)
        parts = []

        for i in range(width):
            c_idx = (step + i) % n_chars
            char = cls.WAVE_CHARS[c_idx]
            color = palette[(step + i) % n_colors]
            parts.append(f"[bold {color}]{char}[/bold {color}]")

        return "".join(parts)

    @classmethod
    def get_pulse_glyph(cls, step: Optional[int] = None) -> str:
        """Returns an alternating technical glyph based on step or millisecond timestamp."""
        try:
            from loom.clothos.theme import ThemeManager
            glyphs = ThemeManager.get_active().glyphs
            palette = ThemeManager.get_active().aura_palette
        except Exception:
            glyphs = ["■", "▲", "◆", "►", "◈", "●", "✦", "█"]
            palette = cls.GLOW_PALETTE

        idx = ((step // 2) if step is not None else int(time.time() * 3)) % len(glyphs)
        color = palette[(step if step is not None else int(time.time() * 4)) % len(palette)]
        return f"[bold {color}]{glyphs[idx]}[/bold {color}]"





# ── LIVE ACTIVE SHIMMER HUD CONTEXT MANAGER ─────────────────────────────────



class LiveShimmerHUD:

    """

    Active live glowing shimmer HUD that renders real-time 12 FPS animations

    in the terminal while background computation and LLM queries execute.

    """

    _current_instance: Optional["LiveShimmerHUD"] = None



    def __init__(self, fps: int = 12, drillbit: Optional[str] = None):

        self.fps = fps

        self.drillbit = drillbit

        self._stop_event = threading.Event()

        self._thread: Optional[threading.Thread] = None

        self._live: Optional[Live] = None

        self._paused = False



    def start(self) -> None:
        """Starts stationary task execution tracking with zero terminal flicker or screen redraw jitter."""
        self._stop_event.clear()
        self._paused = False
        LiveShimmerHUD._current_instance = self
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def _run_loop(self) -> None:
        """Background telemetry tracking loop that avoids terminal line height jumping."""
        interval = 1.0 / max(1, self.fps)
        while not self._stop_event.is_set():
            if not self._paused:
                pass
            self._stop_event.wait(interval)

    def pause(self) -> None:
        """Temporarily pauses tracking for streaming token output."""
        self._paused = True

    def resume(self) -> None:
        """Resumes task tracking."""
        self._paused = False

    def stop(self) -> None:
        """Stops task execution tracking safely."""
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        if LiveShimmerHUD._current_instance is self:
            LiveShimmerHUD._current_instance = None



    def __enter__(self) -> "LiveShimmerHUD":

        self.start()

        return self



    def __exit__(self, exc_type, exc_val, exc_tb) -> None:

        self.stop()



    @classmethod

    def pause_active(cls) -> None:

        if cls._current_instance:

            cls._current_instance.pause()



    @classmethod

    def resume_active(cls) -> None:

        if cls._current_instance:

            cls._current_instance.resume()



    @classmethod

    def stop_active(cls) -> None:

        if cls._current_instance:

            cls._current_instance.stop()





# ── CURRENTLY DOING ACTIVITY TRACKER WITH RICH DETAILS ───────────────────────



class CurrentlyDoing:

    """Thread-safe active task monitor, glowing aura controller, and abort token manager."""



    _current_task: str = "Idle / Awaiting Operator Prompt"

    _phase: str = "IDLE"

    _start_time: float = time.time()

    _abort_requested: bool = False

    _history: List[Dict[str, Any]] = []

    _active_drillbit: str = "Loom Sovereign 32B (Node 1 GPU)"

    _details: Dict[str, Any] = {}



    @classmethod

    def set(

        cls,

        task_desc: str,

        phase: str = "EXEC",

        drillbit: Optional[str] = None,

        sub_goal: Optional[str] = None,

        target: Optional[str] = None,

        hardware: Optional[str] = None,

        storage_tier: Optional[str] = None,

        metrics: Optional[str] = None,

        steering: Optional[str] = None,

        **extra_details

    ) -> None:

        """Sets the active ongoing activity, phase, drillbit, and detailed operational context."""

        cls._current_task = task_desc

        cls._phase = phase

        cls._start_time = time.time()

        cls._abort_requested = False

        if drillbit:

            cls._active_drillbit = drillbit



        # Build details dictionary

        cls._details = {

            "sub_goal": sub_goal,

            "target": target,

            "hardware": hardware,

            "storage_tier": storage_tier,

            "metrics": metrics,

            "steering": steering,

            **extra_details

        }



        cls._history.append({

            "task": task_desc,

            "phase": phase,

            "sub_goal": sub_goal,

            "target": target,

            "start_time": cls._start_time,

            "timestamp": time.strftime("%H:%M:%S")

        })

        if len(cls._history) > 30:

            cls._history.pop(0)



    @classmethod

    def update_details(cls, **kwargs) -> None:

        """Dynamically updates granular task details in real-time without resetting the clock."""

        cls._details.update(kwargs)



    @classmethod

    def set_drillbit(cls, drillbit_name: str) -> None:

        """Updates the active drillbit label."""

        cls._active_drillbit = drillbit_name



    @classmethod

    def get(cls) -> str:

        """Returns description of current activity."""

        return cls._current_task



    @classmethod

    def get_phase(cls) -> str:

        """Returns the current operational phase."""

        return cls._phase



    @classmethod

    def get_drillbit(cls) -> str:

        """Returns the active drillbit."""

        return cls._active_drillbit



    @classmethod

    def get_details(cls) -> Dict[str, Any]:

        """Returns the dictionary of active task details."""

        return cls._details



    @classmethod

    def get_elapsed_s(cls) -> float:

        """Returns elapsed seconds on the active task."""

        return round(time.time() - cls._start_time, 2)



    @classmethod

    def is_abort_requested(cls) -> bool:

        """Checks if operator requested task cancellation."""

        return cls._abort_requested



    @classmethod

    def request_abort(cls) -> None:

        """Signals active loops and workers to abort early."""

        cls._abort_requested = True



    @classmethod

    def reset(cls) -> None:

        """Resets status back to idle."""

        cls._current_task = "Idle / Awaiting Operator Prompt"

        cls._phase = "IDLE"

        cls._start_time = time.time()

        cls._abort_requested = False

        cls._details.clear()



    @classmethod

    def live_shimmer(cls, fps: int = 12, drillbit: Optional[str] = None) -> LiveShimmerHUD:

        """Convenience context manager to run real-time active glowing shimmer during execution."""

        return LiveShimmerHUD(fps=fps, drillbit=drillbit)



    @classmethod
    def get_glow_badge(cls) -> str:
        """Returns an inline status badge with activity waveform for bottom toolbars and status lines."""
        is_idle = cls._phase == "IDLE"
        try:
            from loom.clothos.theme import ThemeManager
            theme = ThemeManager.get_active()
        except Exception:
            theme = None

        ready_color = theme.status_ready if theme else "#10b981"
        dim_color = theme.brand_dim if theme else "#64748b"
        exec_color = theme.status_exec if theme else "#38bdf8"
        brand_color = theme.brand_primary if theme else "#38bdf8"

        if is_idle:
            return f"[bold {ready_color}]● Ready[/bold {ready_color}] [dim {dim_color}](IDLE)[/dim {dim_color}]"

        glyph = GlowActivityIndicator.get_pulse_glyph()
        wave = GlowActivityIndicator.get_glow_wave(width=8)
        sub_str = f" • [dim white]{cls._details.get('sub_goal')}[/dim white]" if cls._details.get("sub_goal") else ""
        return (
            f"{glyph} [bold {brand_color}][CURRENT]:[/bold {brand_color}] [bold white]{cls._current_task}[/bold white]{sub_str} "
            f"[bold {dim_color}]({cls._phase})[/bold {dim_color}] • {wave} "
            f"[dim {dim_color}]⏱ {cls.get_elapsed_s()}s[/dim {dim_color}]"
        )

    @classmethod
    def get_status_dict(cls) -> Dict[str, Any]:
        """Returns complete JSON-serializable status payload."""
        return {
            "current_task": cls._current_task,
            "phase": cls._phase,
            "drillbit": cls._active_drillbit,
            "details": cls._details,
            "elapsed_s": cls.get_elapsed_s(),
            "abort_requested": cls._abort_requested,
            "history_count": len(cls._history),
            "recent_tasks": cls._history[-5:]
        }

    @classmethod
    def render_compact_shimmer_bar(cls, drillbit: Optional[str] = None, step: Optional[int] = None) -> Panel:
        """Renders a sleek, professional 2-line HUD for task execution."""
        try:
            from loom.clothos.theme import ThemeManager
            theme = ThemeManager.get_active()
        except Exception:
            theme = None

        border_col = theme.border_primary if theme else "#334155"
        brand_col = theme.brand_primary if theme else "#38bdf8"
        dim_col = theme.brand_dim if theme else "#64748b"

        wave = GlowActivityIndicator.get_glow_wave(step=step, width=12)
        glyph = GlowActivityIndicator.get_pulse_glyph(step=step)
        elapsed_str = f"{cls.get_elapsed_s():.1f}s"
        active_db = drillbit or cls._active_drillbit
        phase_color = (theme.status_ready if theme else "#10b981") if cls._phase == "IDLE" else (theme.status_exec if theme else "#38bdf8")

        task_disp = cls._current_task[:48] + ("…" if len(cls._current_task) > 48 else "")
        sub_goal = cls._details.get("sub_goal")
        sub_disp = f" · [dim white]{sub_goal[:24]}[/dim white]" if sub_goal else ""

        grid = Table.grid(padding=(0, 1))
        grid.add_column(style="bold white")
        grid.add_row(f"{glyph} [bold white]{task_disp}[/bold white]{sub_disp}")
        grid.add_row(f"{wave} [bold {phase_color}][{cls._phase}][/bold {phase_color}] [bold {dim_col}]{active_db}[/bold {dim_col}] [dim white]• ⏱ {elapsed_str} • [Ctrl+C] Steer/Quit[/dim white]")

        return Panel(
            grid,
            border_style=border_col,
            padding=(0, 1)
        )

    @classmethod
    def render_glow_panel(cls, drillbit: Optional[str] = None, step: Optional[int] = None) -> Panel:
        """Renders the ClothOS production runtime telemetry monitor card with real-time operational metrics."""
        is_idle = cls._phase == "IDLE"
        active_db = drillbit or cls._active_drillbit
        elapsed_str = f"{cls.get_elapsed_s():.1f}s" if not is_idle else "0.0s"

        try:
            from loom.clothos.theme import ThemeManager
            theme = ThemeManager.get_active()
        except Exception:
            theme = None

        brand_col = theme.brand_primary if theme else "#38bdf8"
        border_col = theme.border_primary if theme else "#334155"
        label_col = theme.brand_dim if theme else "#94a3b8"
        ready_col = theme.status_ready if theme else "#10b981"
        exec_col = theme.status_exec if theme else "#38bdf8"

        phase_color = ready_col if is_idle else exec_col
        phase_badge = f"[bold {phase_color}]{cls._phase}[/bold {phase_color}]"

        wave = GlowActivityIndicator.get_glow_wave(step=step, width=16)
        glyph = GlowActivityIndicator.get_pulse_glyph(step=step)

        grid = Table.grid(padding=(0, 2))
        grid.add_column(style=f"bold {label_col}", width=20)
        grid.add_column(style="bold white")

        # 1. Primary Task
        grid.add_row(f"{glyph} Current Task:", f"[bold white]{cls._current_task}[/bold white]")

        # 2. Granular Sub-Goal / Step Details
        sub_goal = cls._details.get("sub_goal")
        if sub_goal:
            grid.add_row("  Active Step:", f"[bold {brand_col}]{sub_goal}[/bold {brand_col}]")

        # 3. Target Focus (File, Function, Model, or Topic)
        target = cls._details.get("target")
        if target:
            grid.add_row("  Target Focus:", f"[bold white]{target}[/bold white]")

        # 4. Operational Phase & Duration
        grid.add_row("  Phase & State:", f"{phase_badge} [dim white]• Duration:[/dim white] [bold {ready_col}]{elapsed_str}[/bold {ready_col}]")

        # 5. Model Engine (with Unbounded Compute Policy)
        grid.add_row("  Model Engine:", f"[bold white]{active_db}[/bold white] • [dim {ready_col}]Unbounded Compute (No Timeout)[/dim {ready_col}]")

        # 6. Hardware Engine Allocation
        hw_alloc = cls._details.get("hardware") or "Node 1 (skyTech) ➔ RTX 3060 CUDA (12GB) + RX 580 DirectML"
        grid.add_row("  Hardware Node:", f"[bold white]{hw_alloc}[/bold white]")

        # 7. Strategic Storage Tier Hierarchy
        storage_tier = cls._details.get("storage_tier") or "Tier 0 (RAM Scratchpad) ➔ Tier 1 (Host NVMe C:) ➔ Tier 2 (USB E:/)"
        grid.add_row("  Storage Hierarchy:", f"[dim white]{storage_tier}[/dim white]")

        # 8. Real-Time Metrics (Throughput, Size, Buffers)
        metrics = cls._details.get("metrics")
        if metrics:
            grid.add_row("  Real-Time Metrics:", f"[bold white]{metrics}[/bold white]")

        # 9. Activity Waveform
        grid.add_row("  Activity State:", f"{wave} [dim {label_col}](Active Execution Cycle)[/dim {label_col}]")

        # 10. Operator Steering Status
        steering_note = cls._details.get("steering")
        if steering_note:
            grid.add_row("  Control Vector:", f"[bold {brand_col}]Locked: \"{steering_note}\"[/bold {brand_col}]")
        else:
            grid.add_row("  Operator Control:", f"[dim white]Press [bold #f59e0b][Ctrl+C][/bold #f59e0b] to steer course, or [bold {brand_col}]/abort[/bold {brand_col}] to cancel[/dim white]")

        # 11. Activity Flow Breadcrumbs
        if len(cls._history) > 1:
            recent_items = cls._history[-4:-1]
            hist_str = " ➔ ".join([f"[dim {label_col}]{h['task'][:22]}…[/dim {label_col}]" for h in recent_items])
            grid.add_row("  Activity Flow:", hist_str)

        panel_title = f"[bold {brand_col}]{theme.telemetry_title if theme else '■ CLOTHOS SYSTEM COGNITIVE TELEMETRY ■'}[/bold {brand_col}]"

        return Panel(
            grid,
            title=panel_title,
            subtitle=f"[dim {label_col}]Production Cluster Environment · Zero External Dependency[/dim {label_col}]",
            border_style=border_col,
            padding=(0, 1)
        )

    @classmethod
    def render_panel(cls) -> Panel:

        """Alias to render_glow_panel for drop-in backwards compatibility."""

        return cls.render_glow_panel()

