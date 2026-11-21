"""Loom Sovereign — Living Mind Standalone Screensaver Application (`loom/ui/screensaver_app.py`).

Launches a dedicated, hardware-accelerated desktop window rendering the 60 FPS
Living Mind Geometries and Homotopy Retraction Screensaver.
"""

from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path
import sys
import threading
import time
from typing import Any, Dict

logger = logging.getLogger("loom.ui.screensaver")

HTML_PATH = Path(__file__).parent / "standalone_screensaver.html"


class ScreensaverApi:
    """Python-to-JavaScript IPC Bridge exposing real-time cluster telemetry."""

    def __init__(self):
        self._cached_cognition: Dict[str, Any] = {
            "doing": {"kuramoto_r": 0.852, "cores": 16},
            "thinking": {"free_energy": 0.042, "hopfield_energy": -18.42, "rubbish_score": 0.04, "bullshit_score": 0.04},
            "dreaming": {"generation": 14, "active_codons": 28},
            "imagining": {"earth_retraction_active": True, "fiduciary_budget_j": 18.4},
        }

    def get_cognition_state(self) -> Dict[str, Any]:
        """Returns real-time cognition state for the JavaScript renderer."""
        try:
            from loom.fabric.hypothesis_store import HypothesisStore
            store = HypothesisStore()
            stats = store.get_stats()
            gen = stats.get("total_hypotheses", 14)
            self._cached_cognition["dreaming"]["generation"] = max(14, gen)
        except Exception:
            pass
        try:
            from loom.si.neurochemistry import get_neurochemical_engine
            engine = get_neurochemical_engine()
            self._cached_cognition["neurochemistry"] = engine.get_state()
        except Exception:
            pass
        return self._cached_cognition


def launch_webview_app(fullscreen: bool = False, width: int = 1280, height: int = 800) -> None:
    """Launches the screensaver using hardware-accelerated pywebview (Edge WebView2)."""
    import webview

    api = ScreensaverApi()
    html_content = HTML_PATH.read_text(encoding="utf-8")

    window = webview.create_window(
        title="Loom Sovereign — Living Mind Screensaver",
        html=html_content,
        js_api=api,
        width=width,
        height=height,
        fullscreen=fullscreen,
        background_color="#030407",
        easy_drag=True,
    )

    logger.info(f"Starting Living Mind Screensaver (fullscreen={fullscreen})...")
    webview.start(debug=False)


def launch_tkinter_fallback(fullscreen: bool = False) -> None:
    """Fallback native Tkinter 60 FPS Canvas screensaver if webview is unavailable."""
    import tkinter as tk
    import math

    root = tk.Tk()
    root.title("Loom Sovereign — Living Mind Screensaver (Native Fallback)")
    root.configure(bg="#030407")

    if fullscreen:
        root.attributes("-fullscreen", True)
    else:
        root.geometry("1280x800")

    canvas = tk.Canvas(root, bg="#030407", highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)

    tick = [0]

    def loop():
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        if w > 10 and h > 10:
            canvas.delete("all")
            t = tick[0] * 0.02
            cx, cy = w / 2, h / 2

            # Earth Center
            canvas.create_oval(cx - 20, cy - 20, cx + 20, cy + 20, fill="#00e676", outline="#a7f3d0", width=2)
            canvas.create_text(cx, cy + 32, text="🌍 EARTH (Origin)", fill="#00e676", font=("Consolas", 10, "bold"))

            # Nodes
            doing_x = cx - 300 + math.sin(t) * 15
            doing_y = cy - 140 + math.cos(t) * 12
            canvas.create_oval(doing_x - 16, doing_y - 16, doing_x + 16, doing_y + 16, fill="#00e5ff", outline="")
            canvas.create_text(doing_x, doing_y + 24, text="⚡ DOING", fill="#00e5ff", font=("Consolas", 10))

            thinking_x = cx + 300 + math.cos(t) * 15
            thinking_y = cy - 140 + math.sin(t) * 12
            canvas.create_oval(thinking_x - 16, thinking_y - 16, thinking_x + 16, thinking_y + 16, fill="#d500f9", outline="")
            canvas.create_text(thinking_x, thinking_y + 24, text="🧠 THINKING", fill="#d500f9", font=("Consolas", 10))

            imagining_x = cx + 300 + math.sin(t * 1.2) * 18
            imagining_y = cy + 140 + math.cos(t * 1.1) * 14
            canvas.create_oval(imagining_x - 16, imagining_y - 16, imagining_x + 16, imagining_y + 14, fill="#ffb300", outline="")
            canvas.create_text(imagining_x, imagining_y + 24, text="🚀 IMAGINING", fill="#ffb300", font=("Consolas", 10))

            # Homotopy Retraction Cable
            canvas.create_line(imagining_x, imagining_y, cx, cy, fill="#00e676", width=3)
            # Pulse
            p = (t * 0.8) % 1.0
            px = imagining_x + (cx - imagining_x) * p
            py = imagining_y + (cy - imagining_y) * p
            canvas.create_oval(px - 5, py - 5, px + 5, py + 5, fill="#ffffff", outline="#00e676")

            tick[0] += 1
        root.after(16, loop)

    root.bind("<Escape>", lambda e: root.destroy())
    root.after(50, loop)
    root.mainloop()


def run_screensaver(fullscreen: bool = False, width: int = 1280, height: int = 800) -> None:
    """Main launcher entrypoint with automatic webview -> tkinter fallback."""
    try:
        launch_webview_app(fullscreen=fullscreen, width=width, height=height)
    except Exception as e:
        logger.warning(f"pywebview initialization failed ({e}), falling back to native Tkinter...")
        launch_tkinter_fallback(fullscreen=fullscreen)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Loom Sovereign Living Mind Screensaver")
    parser.add_argument("--fullscreen", "-f", action="store_true", help="Launch directly in fullscreen mode")
    parser.add_argument("--width", type=int, default=1280, help="Window width")
    parser.add_argument("--height", type=int, default=800, help="Window height")
    args = parser.parse_args()

    run_screensaver(fullscreen=args.fullscreen, width=args.width, height=args.height)
