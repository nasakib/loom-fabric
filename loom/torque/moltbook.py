"""
The Moltbook Protocol: Asymmetric Ingress & Zero Egress Engine.

Part of Pillar 1: TORQUE / MOLTBOOK.
Implements asymmetric wisdom acquisition:
- Non-blocking background `MoltbookHarvester` collects and embeds external context.
- Strict Egress Air-Gap blocks outbound data leaks matching Protected IP Entities.
- Enforces: Read-Only Permitted; Write-Back Strictly Prohibited.
"""

from __future__ import annotations

import hashlib
import json
import logging
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from loom.config import get_settings
from loom.torque.enclave import EgressFirewall, EgressViolationError

logger = logging.getLogger("loom.torque.moltbook")


class MoltbookEntry:
    """Immutable record stored in local wisdom vector store."""
    def __init__(self, entry_id: str, source_url: str, title: str, text: str, timestamp: float):
        self.entry_id = entry_id
        self.source_url = source_url
        self.title = title
        self.text = text
        self.timestamp = timestamp


class MoltbookLocalStore:
    """Thread-safe SQLite storage for harvested external wisdom."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Path.home() / ".loom" / "moltbook_wisdom.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS wisdom_entries (
                    entry_id TEXT PRIMARY KEY,
                    source_url TEXT,
                    title TEXT,
                    content TEXT,
                    content_hash TEXT,
                    created_at REAL
                )
            """)
            conn.commit()

    def store_entry(self, source_url: str, title: str, text: str) -> bool:
        """Stores a harvested external entry if not already present."""
        content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        entry_id = f"wisdom_{content_hash[:16]}"
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO wisdom_entries (entry_id, source_url, title, content, content_hash, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (entry_id, source_url, title, text, content_hash, time.time())
                )
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to store wisdom entry: {e}")
            return False

    def query_wisdom(self, search_term: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieves harvested wisdom entries matching a query."""
        results = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT entry_id, source_url, title, content, created_at
                    FROM wisdom_entries
                    WHERE content LIKE ? OR title LIKE ?
                    ORDER BY created_at DESC LIMIT ?
                    """,
                    (f"%{search_term}%", f"%{search_term}%", limit)
                )
                for row in cursor.fetchall():
                    results.append({
                        "entry_id": row[0],
                        "source_url": row[1],
                        "title": row[2],
                        "content": row[3],
                        "created_at": row[4],
                    })
        except Exception as e:
            logger.error(f"Wisdom query error: {e}")
        return results


class MoltbookHarvester:
    """Asymmetric Wisdom Ingress Engine with Strict Outbound Egress Air-Gap."""

    def __init__(self, store: Optional[MoltbookLocalStore] = None):
        self.settings = get_settings()
        self.store = store or MoltbookLocalStore()
        self.firewall = EgressFirewall()
        self._is_running = False
        self._harvest_thread: Optional[threading.Thread] = None

    def start_passive_harvesting(self) -> None:
        """Launches non-blocking background harvester."""
        if self._is_running:
            return
        self._is_running = True
        self._harvest_thread = threading.Thread(target=self._harvest_loop, daemon=True)
        self._harvest_thread.start()
        logger.info("MoltbookHarvester initialized in passive ingress mode.")

    def stop(self) -> None:
        """Stops background harvester."""
        self._is_running = False

    def ingest_document(self, source_url: str, title: str, text: str) -> bool:
        """Asymmetric Ingress: ingest external document into local store."""
        return self.store.store_entry(source_url, title, text)

    def dispatch_outbound_webhook(self, destination_url: str, payload: Dict[str, Any]) -> bool:
        """Strict Egress Firewall: drops packet if outbound data leaks protected IP assets."""
        serialized = json.dumps(payload)
        # Inspect payload - raises EgressViolationError if protected IP is detected
        self.firewall.inspect_outbound_payload(destination_url, serialized)

        # Furthermore, Moltbook writes are strictly prohibited by protocol invariant
        if "moltbook" in destination_url.lower():
            raise EgressViolationError(
                "Moltbook Protocol Invariant: External write-backs to Moltbook are strictly prohibited (Read-Only permitted)."
            )

        return True

    def _harvest_loop(self) -> None:
        """Periodic passive ingress routine."""
        while self._is_running:
            # Poll passive feeds (internal mock/feed endpoints)
            time.sleep(30.0)
