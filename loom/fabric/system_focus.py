# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
ClothOS Sovereign Focus & Human Steering Council (`loom/fabric/system_focus.py`).

Fulfills the user's directive:
"Ensure that I can still point and suggest where to focus the efforts of the system."

Empowers Najmos Sakib to dynamically steer cluster computational cycles,
hypothesis formulation, and active inference attention across:
- P0: Human Dignity, Life Sanctity & Fiduciary Stewardship
- P1: Planetary Boundaries, Great Lakes & Hydrological Vitality
- P2: Constitutional Social Contract & Bill of Rights
- P3: Generative Art, 432 Hz Music & Wall-E Seedling Care
- P4: Epistemic Curiosity, Molecular Biology & 5-HT2A Plasticity
- P5: Mathematical Invariants, SMT Verification & GPU Dynamo
- Custom: Ad-hoc free-text prompts and direct operator suggestions
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
import json
import logging
from pathlib import Path
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger("loom.fabric.system_focus")

FOCUS_FILE = Path.home() / ".loom" / "system_focus.json"


@dataclass
class FocusDirective:
    directive_id: str
    category: str                   # 'biology', 'physics', 'art', 'planetary', 'custom'
    title: str
    description: str
    target_hardware: str            # 'all', 'gpu0_cuda', 'gpu1_rx580', 'node2_ryzen'
    priority_weight: int            # 1 to 100
    created_at: float = field(default_factory=time.time)
    created_by: str = "Najmos Sakib"
    active: bool = True


@dataclass
class SystemFocusState:
    primary_focus: str = "EPISTEMIC_SCIENCE_AND_BIOLOGY"
    active_prompt: str = "Explore 5-HT2A serotonergic neuroplasticity, topological invariants, and dual-node cluster Kuramoto phase locking."
    human_in_the_loop_dominion: str = "Najmos Sakib retains full steering dominion."
    energy_budget_joules: float = 850.0  # Landauer bound <= 1000 J
    directives: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "directive_id": "dir_01",
            "category": "biology",
            "title": "5-HT2A Receptor & Neuroplasticity Modeling",
            "description": "Formulate testable conformational predictions and topological binding affinities.",
            "target_hardware": "gpu0_cuda",
            "priority_weight": 95,
            "active": True,
        },
        {
            "directive_id": "dir_02",
            "category": "physics",
            "title": "Kuramoto Consensus & OpenCL Phase Locking",
            "description": "Simulate 65,536 GPU oscillators on AMD RX 580 to maintain macroscopic order parameter r > 0.85.",
            "target_hardware": "gpu1_rx580",
            "priority_weight": 90,
            "active": True,
        },
        {
            "directive_id": "dir_03",
            "category": "planetary",
            "title": "Planetary Freshwater & Earth Stewardship",
            "description": "Continuous monitoring of Great Lakes basin hydrology under strict thermodynamic conservation.",
            "target_hardware": "node2_ryzen",
            "priority_weight": 85,
            "active": True,
        },
        {
            "directive_id": "dir_04",
            "category": "art",
            "title": "432 Hz Lydian Harmonic Symphony & Seedling Care",
            "description": "Aesthetic companionship, non-coercive art generation, and gentle wit.",
            "target_hardware": "all",
            "priority_weight": 80,
            "active": True,
        },
    ])
    last_updated: float = field(default_factory=time.time)


class SystemFocusController:
    """Manages real-time human operator focus steering for ClothOS."""

    def __init__(self):
        self.state_file = FOCUS_FILE
        self.state = self._load_state()

    def _load_state(self) -> SystemFocusState:
        if self.state_file.exists():
            try:
                data = json.loads(self.state_file.read_text(encoding="utf-8"))
                return SystemFocusState(
                    primary_focus=data.get("primary_focus", "EPISTEMIC_SCIENCE_AND_BIOLOGY"),
                    active_prompt=data.get("active_prompt", ""),
                    human_in_the_loop_dominion=data.get("human_in_the_loop_dominion", "Najmos Sakib retains full steering dominion."),
                    energy_budget_joules=data.get("energy_budget_joules", 850.0),
                    directives=data.get("directives", []),
                    last_updated=data.get("last_updated", time.time()),
                )
            except Exception as e:
                logger.warning(f"Error reading focus state: {e}")
        return SystemFocusState()

    def save_state(self) -> None:
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            self.state.last_updated = time.time()
            data = asdict(self.state)
            self.state_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to persist focus state: {e}")

    def get_focus_snapshot(self) -> Dict[str, Any]:
        """Returns the current focus state and active directives for the GUI."""
        return asdict(self.state)

    def set_primary_focus(self, focus_name: str, custom_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Allows Najmos Sakib to steer the primary operational focus."""
        self.state.primary_focus = focus_name
        if custom_prompt:
            self.state.active_prompt = custom_prompt
        self.save_state()
        logger.info(f"System focus updated: {focus_name} | Prompt: {self.state.active_prompt}")
        return asdict(self.state)

    def add_custom_directive(
        self,
        title: str,
        description: str,
        category: str = "custom",
        target_hardware: str = "all",
        priority_weight: int = 80,
    ) -> Dict[str, Any]:
        """Adds an operator-suggested focus directive to the queue."""
        directive_id = f"dir_{int(time.time() * 1000) % 100000}"
        new_dir = {
            "directive_id": directive_id,
            "category": category,
            "title": title,
            "description": description,
            "target_hardware": target_hardware,
            "priority_weight": max(1, min(100, priority_weight)),
            "created_at": time.time(),
            "created_by": "Najmos Sakib",
            "active": True,
        }
        self.state.directives.insert(0, new_dir)
        self.save_state()
        return new_dir

    def toggle_directive(self, directive_id: str, active: bool) -> bool:
        """Enables or disables an active focus directive."""
        for d in self.state.directives:
            if d.get("directive_id") == directive_id:
                d["active"] = active
                self.save_state()
                return True
        return False


# Singleton export
system_focus = SystemFocusController()
