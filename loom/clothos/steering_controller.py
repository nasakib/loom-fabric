"""
ClothOS Dynamic Agent Steering Controller
=========================================
Empowers the operator (Najmos Sakib) to steer, guide, course-correct, and
dynamically modulate the agent's cognition, attention, execution strategy,
and tool usage in real-time without restarting tasks or losing session history.
"""

import os
import sys
import time
import json
import uuid
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Dict, Any, List, Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

console = Console(legacy_windows=False)


@dataclass
class SteeringDirective:
    """Represents a discrete operator steering vector."""
    directive_id: str
    directive: str
    category: str = "general"       # 'focus', 'style', 'constraint', 'strategy', 'silicon'
    priority: str = "HIGH"          # 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
    created_at: float = field(default_factory=time.time)
    created_by: str = "Najmos Sakib"
    active: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SteeringController:
    """Thread-safe dynamic steering vector orchestrator for ClothOS."""

    _directives: List[SteeringDirective] = []
    _storage_file: Path = Path.home() / ".clothos_steering_vectors.json"
    _queue_file: Path = Path.home() / ".clothos" / "steering_queue.jsonl"
    _mid_flight_queue: List[str] = []
    _initialized: bool = False

    @classmethod
    def inject_mid_flight(cls, directive: str) -> Dict[str, Any]:
        """Injects a high-priority steering directive directly into an active, in-progress execution loop."""
        cls._init_if_needed()
        cleaned = directive.strip()
        if not cleaned:
            return {"status": "ERROR", "error": "Directive cannot be empty"}
        res = cls.inject(cleaned, category="mid_flight", priority="CRITICAL")
        cls._mid_flight_queue.append(cleaned)
        # Also persist to external queue file so any background runner or subagent receives it
        cls.enqueue_external_steering(cleaned)
        return res

    @classmethod
    def enqueue_external_steering(cls, directive: str) -> None:
        """Writes steering directive to persistent queue for concurrent worker pickup."""
        try:
            cls._queue_file.parent.mkdir(parents=True, exist_ok=True)
            with open(cls._queue_file, "a", encoding="utf-8") as f:
                f.write(json.dumps({"directive": directive, "timestamp": time.time()}) + "\n")
        except Exception:
            pass

    @classmethod
    def poll_mid_flight_guidance(cls) -> List[str]:
        """Polls and clears pending mid-flight steering guidance from memory and queue file."""
        cls._init_if_needed()
        guidance_items = list(cls._mid_flight_queue)
        cls._mid_flight_queue.clear()

        if cls._queue_file.exists():
            try:
                lines = cls._queue_file.read_text(encoding="utf-8").strip().splitlines()
                if lines:
                    cls._queue_file.unlink(missing_ok=True)
                    for line in lines:
                        try:
                            item = json.loads(line)
                            d = item.get("directive", "").strip()
                            if d and d not in guidance_items:
                                cls.inject(d, category="external", priority="CRITICAL")
                                guidance_items.append(d)
                        except Exception:
                            continue
            except Exception:
                pass

        return guidance_items

    @classmethod
    def _init_if_needed(cls) -> None:
        if not cls._initialized:
            cls.load()
            cls._initialized = True

    @classmethod
    def inject(
        cls,
        directive: str,
        category: str = "general",
        priority: str = "HIGH",
        clear_previous: bool = False,
    ) -> Dict[str, Any]:
        """Injects a new steering vector into the agent's active cognitive field."""
        cls._init_if_needed()
        if clear_previous:
            cls._directives.clear()

        cleaned = directive.strip()
        if not cleaned:
            return {"status": "ERROR", "error": "Directive cannot be empty"}

        d_id = f"steer_{int(time.time()*1000) % 1000000:06d}"
        new_d = SteeringDirective(
            directive_id=d_id,
            directive=cleaned,
            category=category,
            priority=priority.upper(),
            created_at=time.time(),
            active=True
        )
        cls._directives.append(new_d)
        cls.save()

        return {
            "status": "SUCCESS",
            "directive_id": d_id,
            "directive": cleaned,
            "category": category,
            "priority": priority.upper(),
            "total_active_vectors": len(cls.get_active()),
            "message": f"Steering vector '{cleaned}' injected successfully."
        }

    @classmethod
    def clear(cls) -> Dict[str, Any]:
        """Clears all active operator steering directives."""
        cls._init_if_needed()
        cleared_count = len(cls._directives)
        cls._directives.clear()
        cls.save()
        return {
            "status": "SUCCESS",
            "cleared_count": cleared_count,
            "message": "All operator steering directives have been reset."
        }

    @classmethod
    def remove(cls, directive_id: str) -> bool:
        """Removes a specific steering directive by ID."""
        cls._init_if_needed()
        initial_len = len(cls._directives)
        cls._directives = [d for d in cls._directives if d.directive_id != directive_id]
        if len(cls._directives) < initial_len:
            cls.save()
            return True
        return False

    @classmethod
    def get_active(cls) -> List[SteeringDirective]:
        """Returns list of currently active steering directives."""
        cls._init_if_needed()
        return [d for d in cls._directives if d.active]

    @classmethod
    def has_directives(cls) -> bool:
        """Returns True if one or more steering directives are currently engaged."""
        cls._init_if_needed()
        return len(cls.get_active()) > 0

    @classmethod
    def get_steering_context_block(cls) -> str:
        """Generates the high-priority system prompt injection block."""
        active = cls.get_active()
        if not active:
            return ""

        lines = [
            "OPERATOR STEERING VECTORS (MANDATORY ACTIVE DIRECTIVES):",
            "The human operator (Najmos Sakib) has explicitly steered your execution course.",
            "You MUST treat these steering directives as primary overriding constraints across your Thought:, Action:, and Deliverable synthesis:"
        ]
        for i, d in enumerate(active, 1):
            lines.append(f"{i}. [{d.priority} PRIORITY · {d.category.upper()}] \"{d.directive}\"")
        lines.append("Explicitly state in your cognitive trace how you are honoring these operator steering directives.")

        return "\n".join(lines) + "\n"

    @classmethod
    def save(cls) -> None:
        """Persists steering vectors to disk."""
        try:
            cls._storage_file.parent.mkdir(parents=True, exist_ok=True)
            payload = [d.to_dict() for d in cls._directives]
            cls._storage_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except Exception:
            pass

    @classmethod
    def load(cls) -> None:
        """Loads steering vectors from disk."""
        cls._directives = []
        if cls._storage_file.exists():
            try:
                data = json.loads(cls._storage_file.read_text(encoding="utf-8"))
                for item in data:
                    cls._directives.append(SteeringDirective(
                        directive_id=item.get("directive_id", str(uuid.uuid4())[:8]),
                        directive=item.get("directive", ""),
                        category=item.get("category", "general"),
                        priority=item.get("priority", "HIGH"),
                        created_at=item.get("created_at", time.time()),
                        created_by=item.get("created_by", "Najmos Sakib"),
                        active=item.get("active", True),
                    ))
            except Exception:
                cls._directives = []

    @classmethod
    def render_panel(cls) -> Panel:
        """Renders an eye-catching Green/White/Purple active steering vectors card."""
        active = cls.get_active()
        grid = Table.grid(padding=(0, 2))
        grid.add_column(style="bold #a855f7", width=16)
        grid.add_column(style="bold white")

        if not active:
            grid.add_row("✦ Steering Status:", "[bold #00ff7f]Autonomous Default[/bold #00ff7f] (No active steering constraints)")
            grid.add_row("✦ How to Steer:", "[dim white]Type [bold #00ff7f]/steer <guidance>[/bold #00ff7f] or prefix with [bold #00ff7f]steer: <guidance>[/bold #00ff7f][/dim white]")
            grid.add_row("✦ Examples:", "[dim #e879f9]/steer focus on numpy SIMD · /steer prioritize speed · /steer 432Hz harmonic[/dim #e879f9]")
        else:
            grid.add_row("✦ Active Vectors:", f"[bold #00ff7f]{len(active)} Operational Directives Engaged[/bold #00ff7f]")
            for i, d in enumerate(active, 1):
                pri_color = "#00ff7f" if d.priority in ["CRITICAL", "HIGH"] else "#e879f9"
                grid.add_row(f"  [{pri_color}]#{i} ({d.priority})[/{pri_color}]:", f"[bold white]\"{d.directive}\"[/bold white] [dim #a855f7]({d.category} · id: {d.directive_id})[/dim #a855f7]")
            grid.add_row("✦ Steering Control:", "[dim white]Type [bold #00ff7f]/steer clear[/bold #00ff7f] to reset or [bold #00ff7f]/steer <new>[/bold #00ff7f] to inject[/dim white]")

        return Panel(
            grid,
            title="[bold #00ff7f]✦ CLOTHOS OPERATOR STEERING TELEMETRY[/bold #00ff7f]",
            subtitle="[dim #a855f7]Real-Time Human-in-the-Loop Intent Modulation[/dim #a855f7]",
            border_style="#a855f7",
            padding=(1, 2)
        )
