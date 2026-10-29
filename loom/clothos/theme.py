# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
ClothOS Production-Grade Theme Subsystem (`loom/clothos/theme.py`).
==================================================================
Maintains first-class color palettes, border stylings, and aesthetic tokens for ClothOS.
Supports:
1. THEME_PRODUCTION (Active Default): High-density enterprise dark slate, precision steel
   blue (#38bdf8), subtle emerald (#10b981), and industrial zinc (#334155). Serious,
   professional, mission-critical production aesthetic.
2. THEME_FOREST_PURPLE (Preserved Copy): Nordic forest pine & deep canopy moss (#166534, #22c55e)
   with royal amethyst accents (#a855f7) over dark woodland slate.
3. THEME_8BIT_SCIENTIFIC (Preserved Copy): High-contrast laboratory CRT phosphor green (#00ff66)
   and oscilloscope cyan (#00f0ff).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
THEME_CONFIG_FILE = WORKSPACE_ROOT / "clothos_root" / "theme_config.json"


@dataclass
class ThemeDefinition:
    name: str
    label: str
    description: str

    # Primary brand colors
    brand_primary: str       # Main active color (banner wordmark, primary prompt)
    brand_secondary: str     # Main accent color
    brand_highlight: str     # Bright highlight (ice white / dewdrop)
    brand_dim: str           # Subdued text / captions

    # Telemetry & Status
    status_ready: str        # Ready / success indicator
    status_exec: str         # Running / cognition indicator
    status_alert: str        # Warning / attention indicator
    status_neutral: str      # Neutral / muted indicator

    # Terminal & Panel Chrome
    border_primary: str      # Panel border
    border_secondary: str    # Alternate panel border
    bg_dark: str             # Dark background
    bg_panel: str            # Surface background
    bg_accent: str           # Accent pill background

    # Waveform / Telemetry Palette
    aura_palette: List[str]

    # Glyphs (Executive / Technical)
    glyphs: List[str]

    # Tagline & Wordmark titles
    banner_tagline: str
    telemetry_title: str
    recon_title: str


# ── 1. ACTIVE DEFAULT: PRODUCTION-GRADE INDUSTRIAL SLATE ─────────────────────
THEME_PRODUCTION = ThemeDefinition(
    name="production",
    label="Production Industrial Slate",
    description="Mission-critical enterprise slate, precision steel blue (#38bdf8), subtle emerald, and industrial zinc.",
    brand_primary="#38bdf8",       # Precision Sky / Steel Blue
    brand_secondary="#0ea5e9",     # Deep Azure Accent
    brand_highlight="#f8fafc",     # Crisp Ice White
    brand_dim="#64748b",           # Industrial Slate-500
    status_ready="#10b981",        # Subtle Emerald
    status_exec="#38bdf8",         # Precision Blue
    status_alert="#f59e0b",        # Industrial Amber
    status_neutral="#94a3b8",      # Slate-400
    border_primary="#334155",      # Slate-700 Border (Minimalist, No Glare)
    border_secondary="#475569",    # Slate-600 Border
    bg_dark="#090d16",             # Deep Obsidian Dark
    bg_panel="#0f172a",            # Industrial Slate-900 Surface
    bg_accent="#1e293b",           # Slate-800 Accent Pill
    aura_palette=[
        "#334155",  # Slate-700
        "#475569",  # Slate-600
        "#64748b",  # Slate-500
        "#94a3b8",  # Slate-400
        "#38bdf8",  # Sky-400
        "#0ea5e9",  # Sky-500
        "#10b981",  # Emerald-500
        "#cbd5e1",  # Slate-300
    ],
    glyphs=["■", "▲", "◆", "►", "◈", "●", "✦", "█"],
    banner_tagline="■  CLOTHOS ENTERPRISE RUNTIME · DUAL-NODE SOVEREIGN CLUSTER · ZERO CLOUD LEAKAGE  ■",
    telemetry_title="■ CLOTHOS SYSTEM COGNITIVE TELEMETRY ■",
    recon_title="■ REPOSITORY & RUNTIME CONTEXT ■"
)


# ── 2. PRESERVED: EXECUTIVE FOREST PINE & AMETHYST THEME ─────────────────────
THEME_FOREST_PURPLE = ThemeDefinition(
    name="forest",
    label="Executive Forest Pine & Amethyst",
    description="Professional Nordic forest pine and deep canopy moss with royal amethyst and radiant orchid accents.",
    brand_primary="#22c55e",       # Vivid Forest Emerald
    brand_secondary="#a855f7",     # Royal Amethyst Purple Accent
    brand_highlight="#c084fc",     # Radiant Orchid Highlight
    brand_dim="#64748b",           # Slate Gray
    status_ready="#22c55e",        # Forest Green
    status_exec="#c084fc",         # Amethyst Bloom
    status_alert="#f59e0b",        # Autumn Amber
    status_neutral="#94a3b8",      # Slate Neutral
    border_primary="#166534",      # Deep Pine Green Border
    border_secondary="#a855f7",    # Amethyst Accent Border
    bg_dark="#0a1f14",             # Deep Woodland Slate Dark
    bg_panel="#0f291e",            # Forest Canopy Surface
    bg_accent="#581c87",           # Royal Purple Accent Pill
    aura_palette=[
        "#166534",  # Nordic Pine Green
        "#22c55e",  # Forest Emerald
        "#4ade80",  # Light Leaf Dew
        "#a855f7",  # Royal Amethyst
        "#c084fc",  # Radiant Orchid
        "#10b981",  # Fresh Emerald
        "#9333ea",  # Deep Violet
        "#f59e0b",  # Amber Resin
    ],
    glyphs=["✦", "◆", "◈", "■", "▲", "●", "❖", "█"],
    banner_tagline="✦  SOVEREIGN FOREST FABRIC · DUAL-NODE DISTRIBUTED CLUSTERING · ZERO CLOUD LEAKAGE  ✦",
    telemetry_title="✦ CLOTHOS ACTIVE COGNITIVE AURA & ACTIVITY TELEMETRY ✦",
    recon_title="■ CLOTHOS AUTO-RECONNAISSANCE & CODEBASE CONTEXT ■"
)


# ── 3. PRESERVED: 8-BIT RETRO-SCIENTIFIC LABORATORY THEME ────────────────────
THEME_8BIT_SCIENTIFIC = ThemeDefinition(
    name="scientific",
    label="8-Bit Retro-Scientific Laboratory",
    description="Authentic high-contrast laboratory CRT phosphor green, oscilloscope cyan, and ice white.",
    brand_primary="#00ff66",
    brand_secondary="#00f0ff",
    brand_highlight="#38bdf8",
    brand_dim="#64748b",
    status_ready="#00ff66",
    status_exec="#00f0ff",
    status_alert="#ffb000",
    status_neutral="#94a3b8",
    border_primary="#00f0ff",
    border_secondary="#00ff66",
    bg_dark="#020617",
    bg_panel="#0f172a",
    bg_accent="#0284c7",
    aura_palette=["#00ff66", "#00f0ff", "#38bdf8", "#f8fafc", "#00ff7f", "#0284c7", "#ffb000", "#22c55e"],
    glyphs=["■", "▲", "◆", "►", "◈", "●", "✦", "█"],
    banner_tagline="■  8-BIT RETRO-SCIENTIFIC LABORATORY FABRIC · DUAL-NODE MESH · ZERO CLOUD LEAKAGE  ■",
    telemetry_title="■ CLOTHOS//SCIENTIFIC TELEMETRY MATRIX ■",
    recon_title="■ CLOTHOS//SCIENTIFIC AUTO-RECONNAISSANCE ■"
)


class ThemeManager:
    """Manages active theme selection, dynamic switching, and persistent preference."""

    _themes: Dict[str, ThemeDefinition] = {
        "production": THEME_PRODUCTION,
        "slate": THEME_PRODUCTION,
        "enterprise": THEME_PRODUCTION,
        "forest": THEME_FOREST_PURPLE,
        "scientific": THEME_8BIT_SCIENTIFIC,
        "default": THEME_PRODUCTION,
    }

    _active_theme_name: str = "production"

    @classmethod
    def get_theme(cls, name: Optional[str] = None) -> ThemeDefinition:
        """Returns the specified theme or the active theme."""
        if name and name.lower() in cls._themes:
            return cls._themes[name.lower()]
        return cls._themes.get(cls._active_theme_name, THEME_PRODUCTION)

    @classmethod
    def get_active(cls) -> ThemeDefinition:
        """Returns the current active theme."""
        return cls.get_theme(cls._active_theme_name)

    @classmethod
    def set_theme(cls, name: str) -> ThemeDefinition:
        """Switches active theme and persists choice to configuration file."""
        target = name.lower()
        if target in cls._themes:
            cls._active_theme_name = target
            cls._save_config()
            return cls.get_active()
        return cls.get_active()

    @classmethod
    def list_themes(cls) -> List[Dict[str, str]]:
        """Returns catalogue of available themes."""
        return [
            {"name": "production", "label": THEME_PRODUCTION.label, "description": THEME_PRODUCTION.description},
            {"name": "forest", "label": THEME_FOREST_PURPLE.label, "description": THEME_FOREST_PURPLE.description},
            {"name": "scientific", "label": THEME_8BIT_SCIENTIFIC.label, "description": THEME_8BIT_SCIENTIFIC.description},
        ]

    @classmethod
    def _save_config(cls) -> None:
        try:
            THEME_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            THEME_CONFIG_FILE.write_text(json.dumps({"active_theme": cls._active_theme_name}, indent=2), encoding="utf-8")
        except Exception:
            pass

    @classmethod
    def load_config(cls) -> None:
        try:
            if THEME_CONFIG_FILE.exists():
                data = json.loads(THEME_CONFIG_FILE.read_text(encoding="utf-8"))
                saved = data.get("active_theme", "production")
                if saved in cls._themes:
                    cls._active_theme_name = saved
        except Exception:
            pass


# Load persistent preference on import
ThemeManager.load_config()
