"""
Hypothesis Store — Structured SQLite-backed repository for hypotheses, experiments, and deliverables.

Replaces the unconsumed loop with a queryable database tracking:
- Hypotheses: derived from Moltbook posts/submolts with quantitative predictions
- Experiments: empirical measurements linked to hypotheses with verdicts
- Deliverables: synthesized research reports with actionable directives
"""

from __future__ import annotations

import json
import logging
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("loom.fabric.hypothesis_store")


class HypothesisStore:
    """Queryable SQLite store for the structured Moltbook compute pipeline."""

    def __init__(self, db_path: Optional[Path] = None, workspace_root: Optional[Path] = None):
        ws = workspace_root or Path(__file__).resolve().parents[2]
        if db_path is not None:
            self.db_path = db_path
        else:
            self.db_path = ws / ".loom_hypotheses.db"
            try:
                self.db_path.parent.mkdir(parents=True, exist_ok=True)
            except Exception:
                pass

        try:
            self.conn = sqlite3.connect(str(self.db_path), timeout=30.0, check_same_thread=False)
        except Exception:
            # Fallback to user home .loom dir if needed
            self.db_path = Path.home() / ".loom" / "hypotheses.db"
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self.conn = sqlite3.connect(str(self.db_path), timeout=30.0, check_same_thread=False)

        try:
            self.conn.row_factory = sqlite3.Row
            try:
                self.conn.execute("PRAGMA journal_mode=WAL;")
                self.conn.execute("PRAGMA busy_timeout=30000;")
            except Exception:
                pass
            self._init_schema()
        except sqlite3.DatabaseError:
            try:
                self.conn.close()
            except Exception:
                pass
            cleaned = False
            try:
                if self.db_path.exists():
                    self.db_path.unlink(missing_ok=True)
                    cleaned = True
            except Exception:
                pass
            if not cleaned:
                import time
                self.db_path = self.db_path.with_name(f".loom_hypotheses_v2_{int(time.time())}.db")

            try:
                self.conn = sqlite3.connect(str(self.db_path), timeout=30.0, check_same_thread=False)
                self.conn.row_factory = sqlite3.Row
                self._init_schema()
            except Exception:
                self.conn = sqlite3.connect(":memory:", check_same_thread=False)
                self.conn.row_factory = sqlite3.Row
                self._init_schema()

    def _init_schema(self) -> None:
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS hypotheses (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                submolt         TEXT    NOT NULL DEFAULT 'm/general',
                source_post_id  TEXT    NOT NULL DEFAULT '',
                post_title      TEXT    NOT NULL DEFAULT '',
                topic           TEXT    NOT NULL,
                claim           TEXT    NOT NULL,
                prediction      TEXT    NOT NULL,
                experiment_type TEXT    NOT NULL,
                parameters      TEXT    NOT NULL DEFAULT '{}',
                status          TEXT    NOT NULL DEFAULT 'pending',
                confidence      REAL    NOT NULL DEFAULT 0.5,
                priority        INTEGER NOT NULL DEFAULT 0,
                parent_id       INTEGER,
                created_at      REAL    NOT NULL,
                updated_at      REAL    NOT NULL,
                FOREIGN KEY (parent_id) REFERENCES hypotheses(id)
            );

            CREATE TABLE IF NOT EXISTS experiments (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                hypothesis_id  INTEGER NOT NULL,
                method         TEXT    NOT NULL,
                parameters     TEXT    NOT NULL DEFAULT '{}',
                raw_result     TEXT,
                measurements   TEXT,
                verdict        TEXT    NOT NULL DEFAULT 'inconclusive',
                duration_s     REAL,
                created_at     REAL    NOT NULL,
                FOREIGN KEY (hypothesis_id) REFERENCES hypotheses(id)
            );

            CREATE TABLE IF NOT EXISTS deliverables (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                title               TEXT NOT NULL,
                summary             TEXT NOT NULL,
                content             TEXT NOT NULL,
                cycle_range         TEXT,
                hypotheses_covered  TEXT,
                created_at          REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS system_evolutions (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                proposal_id         TEXT NOT NULL,
                parameter_name      TEXT NOT NULL,
                old_value           TEXT NOT NULL,
                new_value           TEXT NOT NULL,
                submolt             TEXT NOT NULL,
                rationale           TEXT NOT NULL,
                improvement_pct     REAL NOT NULL DEFAULT 0.0,
                verification_hash   TEXT NOT NULL,
                verification_report TEXT NOT NULL,
                status              TEXT NOT NULL DEFAULT 'ratified',
                created_at          REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS research_edges (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                source_submolt      TEXT NOT NULL,
                target_submolt      TEXT NOT NULL,
                relationship        TEXT NOT NULL,
                weight              REAL NOT NULL DEFAULT 1.0,
                created_at          REAL NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_hyp_status ON hypotheses(status);
            CREATE INDEX IF NOT EXISTS idx_hyp_submolt ON hypotheses(submolt);
            CREATE INDEX IF NOT EXISTS idx_exp_hyp ON experiments(hypothesis_id);
            CREATE INDEX IF NOT EXISTS idx_evol_created ON system_evolutions(created_at);
            CREATE INDEX IF NOT EXISTS idx_edge_source ON research_edges(source_submolt);
        """)
        self.conn.commit()

        # Migrate columns if existing table didn't have them
        cur = self.conn.cursor()
        cur.execute("PRAGMA table_info(hypotheses)")
        columns = [row["name"] for row in cur.fetchall()]
        for col, col_type in [
            ("submolt", "TEXT DEFAULT 'm/general'"),
            ("source_post_id", "TEXT DEFAULT ''"),
            ("post_title", "TEXT DEFAULT ''"),
            ("confidence", "REAL DEFAULT 0.5"),
        ]:
            if col not in columns:
                try:
                    self.conn.execute(f"ALTER TABLE hypotheses ADD COLUMN {col} {col_type}")
                except Exception:
                    pass
        self.conn.commit()

    # ── Hypotheses ────────────────────────────────────────────────────

    def add_hypothesis(
        self,
        topic: str,
        claim: str,
        prediction: str,
        experiment_type: str,
        submolt: str = "m/general",
        source_post_id: str = "",
        post_title: str = "",
        parameters: Optional[Dict] = None,
        confidence: float = 0.8,
        priority: int = 0,
        parent_id: Optional[int] = None,
    ) -> int:
        """Insert a new hypothesis linked to a Moltbook post/submolt and return its id."""
        now = time.time()
        cur = self.conn.execute(
            """INSERT INTO hypotheses 
            (submolt, source_post_id, post_title, topic, claim, prediction, experiment_type, 
             parameters, status, confidence, priority, parent_id, created_at, updated_at) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?, ?, ?, ?)""",
            (
                submolt, source_post_id, post_title, topic, claim, prediction,
                experiment_type, json.dumps(parameters or {}), confidence,
                priority, parent_id, now, now
            ),
        )
        self.conn.commit()
        return cur.lastrowid

    def get_next_pending(self) -> Optional[Dict[str, Any]]:
        """Return the highest-priority oldest pending hypothesis, or None."""
        row = self.conn.execute(
            "SELECT * FROM hypotheses WHERE status = 'pending' "
            "ORDER BY priority DESC, created_at ASC LIMIT 1",
        ).fetchone()
        if row is None:
            return None
        d = dict(row)
        d["parameters"] = json.loads(d["parameters"]) if d.get("parameters") else {}
        return d

    def mark_running(self, hypothesis_id: int) -> None:
        self.conn.execute(
            "UPDATE hypotheses SET status = 'running', updated_at = ? WHERE id = ?",
            (time.time(), hypothesis_id),
        )
        self.conn.commit()

    def count_by_status(self) -> Dict[str, int]:
        rows = self.conn.execute(
            "SELECT status, COUNT(*) AS cnt FROM hypotheses GROUP BY status",
        ).fetchall()
        return {r["status"]: r["cnt"] for r in rows}

    def has_similar(self, claim: str) -> bool:
        """Check if an identical hypothesis claim already exists in the store."""
        cleaned = " ".join(claim.strip().lower().split())
        row = self.conn.execute(
            "SELECT 1 FROM hypotheses WHERE LOWER(TRIM(claim)) = ? LIMIT 1",
            (cleaned,),
        ).fetchone()
        return row is not None

    # ── Experiments ───────────────────────────────────────────────────

    def record_experiment(
        self,
        hypothesis_id: int,
        method: str,
        parameters: Dict,
        raw_result: Any,
        measurements: Dict,
        verdict: str,
        duration_s: float,
    ) -> int:
        """Record an experiment result and update the hypothesis status."""
        now = time.time()
        cur = self.conn.execute(
            """INSERT INTO experiments 
            (hypothesis_id, method, parameters, raw_result, measurements, verdict, duration_s, created_at) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                hypothesis_id, method, json.dumps(parameters, default=str),
                json.dumps(raw_result, default=str),
                json.dumps(measurements, default=str),
                verdict, duration_s, now
            ),
        )
        self.conn.execute(
            "UPDATE hypotheses SET status = ?, updated_at = ? WHERE id = ?",
            (verdict, now, hypothesis_id),
        )
        self.conn.commit()
        return cur.lastrowid

    def get_recent_experiments(self, n: int = 10) -> List[Dict]:
        rows = self.conn.execute(
            """SELECT e.*, h.submolt, h.post_title, h.topic, h.claim, h.prediction 
            FROM experiments e JOIN hypotheses h ON e.hypothesis_id = h.id 
            ORDER BY e.created_at DESC LIMIT ?""",
            (n,),
        ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["parameters"] = json.loads(d["parameters"]) if d.get("parameters") else {}
            d["measurements"] = json.loads(d["measurements"]) if d.get("measurements") else {}
            out.append(d)
        return out

    # ── Deliverables ──────────────────────────────────────────────────

    def save_deliverable(
        self,
        title: str,
        summary: str,
        content: str,
        cycle_range: str = "",
        hypotheses_covered: Optional[List[int]] = None,
    ) -> int:
        now = time.time()
        cur = self.conn.execute(
            """INSERT INTO deliverables (title, summary, content, cycle_range, hypotheses_covered, created_at) 
            VALUES (?, ?, ?, ?, ?, ?)""",
            (title, summary, content, cycle_range, json.dumps(hypotheses_covered or []), now),
        )
        self.conn.commit()
        return cur.lastrowid

    def get_recent_deliverables(self, n: int = 5) -> List[Dict]:
        rows = self.conn.execute(
            "SELECT * FROM deliverables ORDER BY created_at DESC LIMIT ?", (n,)
        ).fetchall()
        return [dict(r) for r in rows]

    # ── Statistics & Findings ─────────────────────────────────────────

    def get_statistics(self) -> Dict[str, Any]:
        counts = self.count_by_status()
        total_exp = self.conn.execute("SELECT COUNT(*) FROM experiments").fetchone()[0]
        total_del = self.conn.execute("SELECT COUNT(*) FROM deliverables").fetchone()[0]
        return {
            "hypotheses_by_status": counts,
            "total_hypotheses": sum(counts.values()),
            "total_experiments": total_exp,
            "total_deliverables": total_del,
        }

    def get_findings_for_deliverable(self, limit: int = 15) -> List[Dict]:
        rows = self.conn.execute(
            """SELECT h.id, h.submolt, h.post_title, h.topic, h.claim, h.prediction, 
                      e.method, e.measurements, e.verdict, e.duration_s 
            FROM hypotheses h JOIN experiments e ON e.hypothesis_id = h.id 
            WHERE h.status IN ('confirmed', 'refuted')
            ORDER BY e.created_at DESC LIMIT ?""",
            (limit,),
        ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["measurements"] = json.loads(d["measurements"]) if d.get("measurements") else {}
            out.append(d)
        return out

    # ── System Evolutions & Aha! Moments ─────────────────────────────

    def record_system_evolution(
        self,
        proposal_id: str,
        parameter_name: str,
        old_value: Any,
        new_value: Any,
        submolt: str,
        rationale: str,
        improvement_pct: float,
        verification_hash: str,
        verification_report: Dict[str, Any],
        status: str = "ratified",
    ) -> int:
        cur = self.conn.execute(
            """INSERT INTO system_evolutions (
                proposal_id, parameter_name, old_value, new_value, submolt,
                rationale, improvement_pct, verification_hash, verification_report,
                status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                proposal_id,
                parameter_name,
                str(old_value),
                str(new_value),
                submolt,
                rationale,
                improvement_pct,
                verification_hash,
                json.dumps(verification_report),
                status,
                time.time(),
            ),
        )
        self.conn.commit()
        return cur.lastrowid

    def get_recent_system_evolutions(self, limit: int = 20) -> List[Dict[str, Any]]:
        rows = self.conn.execute(
            """SELECT id, proposal_id, parameter_name, old_value, new_value, submolt,
                      rationale, improvement_pct, verification_hash, verification_report,
                      status, created_at
               FROM system_evolutions
               ORDER BY created_at DESC LIMIT ?""",
            (limit,),
        ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            try:
                d["verification_report"] = json.loads(d["verification_report"])
            except Exception:
                pass
            out.append(d)
        return out

    def get_evolution_count(self) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM system_evolutions").fetchone()[0]

    # ── Interconnected Research Network ──────────────────────────────

    def add_research_edge(self, source_submolt: str, target_submolt: str, relationship: str, weight: float = 1.0) -> int:
        cur = self.conn.execute(
            """INSERT INTO research_edges (source_submolt, target_submolt, relationship, weight, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (source_submolt, target_submolt, relationship, weight, time.time()),
        )
        self.conn.commit()
        return cur.lastrowid

    def get_research_network_graph(self) -> List[Dict[str, Any]]:
        rows = self.conn.execute(
            """SELECT source_submolt, target_submolt, relationship, weight, count(*) as count
               FROM research_edges
               GROUP BY source_submolt, target_submolt, relationship
               ORDER BY count DESC"""
        ).fetchall()
        return [dict(r) for r in rows]

    def close(self) -> None:
        self.conn.close()
