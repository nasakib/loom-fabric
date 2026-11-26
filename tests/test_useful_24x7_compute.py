"""Unit tests verifying that 24/7 compute performs bounded, non-spammy, useful work."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from loom.clothos import useful_work_engine as uwe
from loom.clothos.self_training_knowledge_engine import SelfTrainingKnowledgeEngine
from loom.clothos.useful_work_engine import UsefulComputeWorkEngine, WorkerProcessLock
from loom.fabric.deliverable_synthesizer import DeliverableSynthesizer
from loom.fabric.experimentation_engine import ExperimentationEngine
from loom.fabric.hypothesis_store import HypothesisStore
from loom.fabric.moltbook_hypothesis import MoltbookHypothesisEngine
from loom.tools import ratchet as ratchet_mod
from loom.tools.ratchet import RatchetEngine


class TestRatchetCompactionAndDedup:
    def test_auto_compacts_oversized_ledger_and_deduplicates(self, tmp_path, monkeypatch):
        monkeypatch.setattr(ratchet_mod, "COMPACT_THRESHOLD_BYTES", 1024)
        monkeypatch.setattr(ratchet_mod, "MAX_IN_MEMORY_AXIOMS", 5)

        ledger = tmp_path / "ratchet.json"
        home_ledger = tmp_path / "home_ratchet.json"
        catch_file = tmp_path / "catch.json"

        axioms = [
            {
                "tooth_index": 12320 + i,
                "axiom_id": f"AX_{i}",
                "claim": f"Sample verified claim {i} " + ("x" * 60),
                "proof_hash": f"hash_{i}",
                "confidence": 0.95,
                "timestamp_epoch": 1700000000.0 + i,
                "node_origin": "node1",
            }
            for i in range(25)
        ]
        ledger.write_text(
            json.dumps({"tooth_count": 12345, "axioms": axioms}),
            encoding="utf-8",
        )
        orig_size = ledger.stat().st_size
        assert orig_size > 1024

        eng = RatchetEngine(
            workspace_root=tmp_path,
            ledger_file=ledger,
            home_ledger=home_ledger,
            catch_file=catch_file,
        )

        assert eng.tooth_count == 12345
        assert len(eng.axioms) <= 5
        assert (tmp_path / "ratchet.archive.json").exists() or ledger.with_suffix(".archive.json").exists()
        assert ledger.stat().st_size < orig_size // 2

        # Claim deduplication check
        assert eng.click("DEDUP_1", "Unique topological claim", "p1", deduplicate_claim=True) is True
        assert eng.tooth_count == 12346
        assert eng.click("DEDUP_2", "Unique topological claim", "p2", deduplicate_claim=True) is False
        assert eng.tooth_count == 12346
        assert eng.click("DEDUP_3", "Distinct second claim", "p3", deduplicate_claim=True) is True
        assert eng.tooth_count == 12347


class TestWorkerProcessLock:
    def test_singleton_lock_blocks_live_other_and_recovers_dead(self, tmp_path, monkeypatch):
        lock_path = tmp_path / "24x7_worker.lock"
        lock1 = WorkerProcessLock(lock_path=lock_path, owner_name="primary")
        acquired, holder = lock1.acquire()
        assert acquired is True
        assert holder is None
        assert lock_path.exists()

        # Re-entrant by same PID succeeds
        acquired_again, holder_again = lock1.acquire()
        assert acquired_again is True
        assert holder_again is None

        # Simulate another live PID holding lock
        lock_path.write_text(json.dumps({"pid": 999999, "owner": "rival"}), encoding="utf-8")
        monkeypatch.setattr(uwe, "is_pid_alive", lambda pid: pid == 999999)
        lock2 = WorkerProcessLock(lock_path=lock_path, owner_name="secondary")
        acq2, holder2 = lock2.acquire()
        assert acq2 is False
        assert holder2 == 999999

        # Dead PID holder should be cleanly superseded
        monkeypatch.setattr(uwe, "is_pid_alive", lambda pid: False)
        acq3, holder3 = lock2.acquire()
        assert acq3 is True
        assert holder3 is None

        lock2.release()
        assert not lock_path.exists()


class TestUsefulComputeWorkEngine:
    def test_hygiene_code_audit_pytest_distillation_and_briefing(self, tmp_path, monkeypatch):
        monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))

        # 1. Oversized log (>10 MiB) + stale RUNNING queue task + stale SQLite hypothesis
        log_dir = tmp_path / ".loom" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        big_log = log_dir / "continuous_worker.log"
        big_log.write_bytes(b"stale noise line\n" * (700 * 1024))  # ~11.9 MB

        q_file = tmp_path / ".clothos_task_queue.jsonl"
        stale_task = {
            "task_id": "t-stale-1",
            "prompt": "Compute invariant",
            "status": "RUNNING",
            "started_at": time.time() - 2000.0,
            "retries": 0,
        }
        q_file.write_text(json.dumps(stale_task) + "\n", encoding="utf-8")

        store = HypothesisStore(db_path=tmp_path / "hyp.db", workspace_root=tmp_path)
        hyp_id = store.add_hypothesis(
            topic="stale_recovery",
            claim="Stale running hyp should reset to pending",
            prediction="status == pending",
            experiment_type="code_invariant_audit",
        )
        store.mark_running(hyp_id)
        store.conn.execute(
            "UPDATE hypotheses SET updated_at = ? WHERE id = ?",
            (time.time() - 1500.0, hyp_id),
        )
        store.conn.commit()

        eng = UsefulComputeWorkEngine(workspace_root=tmp_path)
        eng.documents_root = tmp_path

        hyg = eng.run_system_hygiene(hypothesis_store=store)
        assert hyg["logs_rotated"] == 1
        assert hyg["stale_tasks_recovered"] == 1
        assert hyg["stale_hyps_recovered"] == 1
        assert big_log.stat().st_size == 0
        assert (log_dir / "continuous_worker.log.1").exists()
        recovered_task = json.loads(q_file.read_text(encoding="utf-8").strip())
        assert recovered_task["status"] == "QUEUED"
        assert recovered_task["retries"] == 1
        assert store.get_next_pending()["id"] == hyp_id

        # 2. Code quality audit detects SyntaxError and bare except:
        loom_dir = tmp_path / "loom"
        loom_dir.mkdir(parents=True, exist_ok=True)
        (loom_dir / "clean.py").write_text("def ok():\n    return 42\n", encoding="utf-8")
        (loom_dir / "bad_syntax.py").write_text("def broken(:\n    pass\n", encoding="utf-8")
        (loom_dir / "bare_except.py").write_text(
            "def risky():\n    try:\n        return 1\n    except:\n        return 0\n",
            encoding="utf-8",
        )

        audit = eng.run_code_quality_audit(force=True)
        assert audit is not None
        assert audit["files_checked"] == 3
        assert len(audit["syntax_errors"]) == 1
        assert len(audit["warnings"]) == 1

        # 3. Rotating pytest audit parses real pass/fail output (scoped so subprocess.run isn't mocked during distillation)
        (tmp_path / "tests").mkdir(parents=True, exist_ok=True)
        (tmp_path / "tests" / "test_dummy.py").write_text("def test_x(): assert True\n", encoding="utf-8")
        with monkeypatch.context() as mp:
            mp.setattr(
                uwe,
                "ROTATING_TEST_TARGETS",
                [("loom-fabric", "tests/test_dummy.py", "Dummy Target")],
            )
            mp.setattr(
                subprocess,
                "run",
                lambda *a, **kw: SimpleNamespace(returncode=0, stdout="5 passed in 0.08s\n", stderr=""),
            )
            test_res = eng.run_rotating_test_audit(force=True)
        assert test_res is not None
        assert test_res["passed"] == 5
        assert test_res["failed"] == 0
        assert eng.state["real_tests_passed"] == 5
        assert eng.state["real_test_pass_rate_pct"] == 100.0

        # 4. Execution-verified distillation keeps PASS code and rejects FAIL code
        monkeypatch.setattr(eng, "_probe_tcp", lambda *a, **kw: True)
        monkeypatch.setattr(eng, "_resolve_project_python", lambda _p: sys.executable)

        responses = [
            "```python\ndef add(a, b): return a + b\nassert add(2, 3) == 5\n```",
            "```python\ndef bad(): return 0\nassert bad() == 1, 'mismatch'\n```",
        ]

        class FakeResp:
            def __init__(self, status_code, payload):
                self.status_code = status_code
                self._payload = payload

            def json(self):
                return self._payload

        class FakeClient:
            def __init__(self, *a, **kw):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def get(self, url):
                return FakeResp(200, {"models": [{"name": "qwen2.5-coder:7b"}]})

            def post(self, url, json=None):
                return FakeResp(200, {"response": responses.pop(0)})

        monkeypatch.setattr(uwe.httpx, "Client", FakeClient)

        res_ok = eng.run_verified_llm_distillation(force=True)
        res_fail = eng.run_verified_llm_distillation(force=True)
        assert res_ok["verified"] is True
        assert res_fail["verified"] is False
        assert eng.state["distillation"]["attempted"] == 2
        assert eng.state["distillation"]["verified_passed"] == 1
        assert eng.state["distillation"]["pass_rate_pct"] == 50.0
        saved_lines = eng.verified_pairs_path.read_text(encoding="utf-8").strip().splitlines()
        assert len(saved_lines) == 1

        # 5. Executive briefing synthesis
        brief_path = eng.synthesize_briefing(
            worker_stats={"sovereign_coherence_index": 97.2, "total_cycles_completed": 7}
        )
        assert brief_path.exists()
        brief_text = brief_path.read_text(encoding="utf-8")
        assert "5 passed" in brief_text
        assert "Syntax Errors" in brief_text
        assert (tmp_path / "interpretations" / "MORNING_BRIEFING.md").exists()
        store.close()


class TestMoltbookAndExperimentationDiversity:
    def test_domain_diversity_and_new_experiment_handlers(self, tmp_path):
        store = HypothesisStore(db_path=tmp_path / "div.db", workspace_root=tmp_path)
        molt = MoltbookHypothesisEngine(store)

        for _ in range(6):
            molt.synthesize_new_hypothesis_from_moltbook(ollama_url="http://127.0.0.1:1")

        exp_types = {
            r[0]
            for r in store.conn.execute("SELECT DISTINCT experiment_type FROM hypotheses").fetchall()
        }
        assert len(exp_types) >= 3

        exp_eng = ExperimentationEngine(store=store, rx580=None, bullshit_meter=None)
        for etype in (
            "code_invariant_audit",
            "jit_kernel_benchmark",
            "z3_smt_verification",
            "empirical_grounding_sweep",
            "variational_inference_sweep",
        ):
            hid = store.add_hypothesis(
                topic=f"test_{etype}",
                claim=f"Verify {etype} executes cleanly",
                prediction="verdict resolved",
                experiment_type=etype,
                parameters={"domain": etype},
            )
            hyp = dict(
                id=hid,
                topic=f"test_{etype}",
                claim=f"Verify {etype} executes cleanly",
                prediction="verdict resolved",
                experiment_type=etype,
                parameters={"domain": etype},
            )
            res = exp_eng.execute_hypothesis(hyp)
            assert "error" not in res
            assert res["verdict"] in ("confirmed", "refuted")
        store.close()


class TestDeliverableGatingAndSelfTraining:
    def test_deliverable_gating_and_self_training_dedup(self, tmp_path, monkeypatch):
        monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
        store = HypothesisStore(db_path=tmp_path / "gate.db", workspace_root=tmp_path)
        synth = DeliverableSynthesizer(workspace_root=tmp_path, store=store)

        assert synth.should_synthesize() is False

        # Add 3 completed experiments -> triggers initial deliverable
        for i in range(3):
            hid = store.add_hypothesis(
                topic=f"topic_{i}",
                claim=f"Claim {i}",
                prediction="pred",
                experiment_type="code_invariant_audit",
            )
            store.record_experiment(
                hypothesis_id=hid,
                method="ast_audit",
                parameters={},
                raw_result={"ok": True},
                measurements={"files": 10},
                verdict="confirmed",
                duration_s=0.1,
            )

        assert synth.should_synthesize(min_new_experiments=20, min_interval_s=900.0) is True
        out = synth.compile_deliverable(cycle_range="1-3")
        assert out is not None and out.exists()
        assert (tmp_path / "deliverables" / "LATEST_24X7_REPORT.md").exists()

        # Zero new experiments since deliverable -> gated False
        assert synth.should_synthesize(min_new_experiments=20, min_interval_s=0.0) is False

        # SelfTrainingKnowledgeEngine deduplication and bounded fitness
        stk = SelfTrainingKnowledgeEngine(workspace_root=tmp_path)
        r1 = stk.execute_self_training_cycle()
        count_after_first = len(stk.pairs_path.read_text(encoding="utf-8").splitlines()) if stk.pairs_path.exists() else 0
        r2 = stk.execute_complete_self_training_cycle()
        count_after_second = len(stk.pairs_path.read_text(encoding="utf-8").splitlines()) if stk.pairs_path.exists() else 0

        assert 0.0 <= r1.starting_fitness <= 1.0
        assert 0.0 <= r1.ending_fitness <= 1.0
        assert 0.0 <= r2.starting_fitness <= 1.0
        assert 0.0 <= r2.ending_fitness <= 1.0
        assert count_after_second == count_after_first
        store.close()
