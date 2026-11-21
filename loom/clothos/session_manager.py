"""
ClothOS Session Management Subsystem
===================================
Manages isolated, persistent conversation sessions.
By default, every ClothOS launch starts a fresh, new session,
while preserving full capability to browse, search, resume,
export, and manage historical sessions.
"""

import os
import sys
import json
import time
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Dict, Any, List, Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console(legacy_windows=False)


@dataclass
class SessionMetadata:
    session_id: str
    created_at: float
    updated_at: float
    workspace_root: str
    title: str = "New Session"
    message_count: int = 0
    active_head: str = "loom-sovereign"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SessionManager:
    """Orchestrates creation, persistence, enumeration, and resumption of ClothOS sessions."""

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root.resolve()
        self.sessions_dir = Path.home() / ".clothos" / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.current_session_id = self.generate_session_id()
        self.session_file = self.sessions_dir / f"{self.current_session_id}.json"
        self.metadata = SessionMetadata(
            session_id=self.current_session_id,
            created_at=time.time(),
            updated_at=time.time(),
            workspace_root=str(self.workspace_root),
            title="Fresh Session",
            message_count=0
        )

    @staticmethod
    def generate_session_id() -> str:
        """Generates a clean, timestamped session identifier."""
        t_str = time.strftime("%Y%m%d_%H%M%S")
        rand_suffix = f"{int(time.time() * 1000) % 10000:04d}"
        return f"session_{t_str}_{rand_suffix}"

    def create_new_session(self, title: str = "New Session") -> str:
        """Initializes and returns a new session ID, resetting active session state."""
        self.current_session_id = self.generate_session_id()
        self.session_file = self.sessions_dir / f"{self.current_session_id}.json"
        self.metadata = SessionMetadata(
            session_id=self.current_session_id,
            created_at=time.time(),
            updated_at=time.time(),
            workspace_root=str(self.workspace_root),
            title=title,
            message_count=0
        )
        return self.current_session_id

    def save_session(self, history: List[Dict[str, str]], active_head: str = "loom-sovereign") -> None:
        """Saves current session messages and metadata to disk."""
        try:
            self.metadata.updated_at = time.time()
            self.metadata.message_count = len(history)
            self.metadata.active_head = active_head

            # Auto-generate title from first user query if still generic
            if (self.metadata.title in ["Fresh Session", "New Session"]) and history:
                first_query = history[0].get("user", "").strip()
                if first_query:
                    # Truncate cleanly
                    clean_title = first_query.replace("\n", " ")[:60]
                    self.metadata.title = clean_title + ("…" if len(first_query) > 60 else "")

            payload = {
                "metadata": self.metadata.to_dict(),
                "history": history[-100:]  # Keep up to 100 recent turns
            }
            self.session_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except Exception:
            pass

    def load_session(self, session_id: str) -> Optional[List[Dict[str, str]]]:
        """Loads and switches to a specific session by ID or prefix."""
        target_file = None
        # Exact match
        exact = self.sessions_dir / f"{session_id}.json"
        if exact.exists():
            target_file = exact
        else:
            # Prefix search
            candidates = list(self.sessions_dir.glob(f"*{session_id}*.json"))
            if candidates:
                target_file = candidates[0]

        if not target_file or not target_file.exists():
            return None

        try:
            data = json.loads(target_file.read_text(encoding="utf-8"))
            meta = data.get("metadata", {})
            self.current_session_id = meta.get("session_id", target_file.stem)
            self.session_file = target_file
            self.metadata = SessionMetadata(
                session_id=self.current_session_id,
                created_at=meta.get("created_at", time.time()),
                updated_at=meta.get("updated_at", time.time()),
                workspace_root=meta.get("workspace_root", str(self.workspace_root)),
                title=meta.get("title", "Resumed Session"),
                message_count=meta.get("message_count", len(data.get("history", []))),
                active_head=meta.get("active_head", "loom-sovereign")
            )
            return data.get("history", [])
        except Exception as ex:
            console.print(f"[red]Failed to load session {session_id}: {ex}[/red]")
            return None

    def list_sessions(self, limit: int = 15) -> List[Dict[str, Any]]:
        """Scans and lists stored historical sessions ordered by last updated."""
        sessions = []
        for p in self.sessions_dir.glob("session_*.json"):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                meta = data.get("metadata", {})
                sessions.append({
                    "session_id": meta.get("session_id", p.stem),
                    "created_at": meta.get("created_at", p.stat().st_ctime),
                    "updated_at": meta.get("updated_at", p.stat().st_mtime),
                    "title": meta.get("title", "Untitled Session"),
                    "message_count": meta.get("message_count", len(data.get("history", []))),
                    "active_head": meta.get("active_head", "sovereign"),
                    "file_path": str(p)
                })
            except Exception:
                continue

        sessions.sort(key=lambda s: s["updated_at"], reverse=True)
        return sessions[:limit]

    def render_sessions_table(self, limit: int = 15) -> Table:
        """Renders an eye-catching Green/White/Purple table of historical sessions."""
        sessions = self.list_sessions(limit=limit)

        table = Table(
            title="[bold #00ff7f]✦ CLOTHOS HISTORICAL SESSIONS CATALOGUE[/bold #00ff7f]",
            border_style="#a855f7",
            header_style="bold #00ff7f",
            padding=(0, 1)
        )
        table.add_column("Session ID", style="bold white", width=30)
        table.add_column("Last Active", style="dim #a855f7", width=18)
        table.add_column("Turns", justify="right", style="#00ff7f", width=7)
        table.add_column("Topic / Initial Query", style="white")

        if not sessions:
            table.add_row("[dim]No historical sessions recorded[/dim]", "-", "-", "-")
            return table

        for s in sessions:
            is_active = s["session_id"] == self.current_session_id
            active_marker = " [bold #00ff7f]● (active)[/bold #00ff7f]" if is_active else ""
            sid_str = f"{s['session_id']}{active_marker}"
            t_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(s["updated_at"]))
            title_str = s["title"][:50] + ("…" if len(s["title"]) > 50 else "")
            table.add_row(sid_str, t_str, str(s["message_count"]), title_str)

        return table
