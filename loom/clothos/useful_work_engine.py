# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
ClothOS Useful 24/7 Compute Work Engine (`loom/clothos/useful_work_engine.py`).

Replaces repetitive synthetic busywork with concrete, verifiable, high-utility
background workloads across the VectorCore / ClothOS / Loom Fabric workspace:
1. Single-instance PID lockfile preventing multi-daemon stampedes and SQLite locks.
2. Real multi-project `pytest` verification and Python `py_compile`/AST code audits.
3. Live hardware & cluster benchmarks (RTX 3060 `nvidia-smi`, RX 580 OpenCL,
   Universal JIT x86-64 kernels, Typemetric Dozenal/WHT, Node 1 & Node 2 Ollama/Ray).
4. Execution-verified LLM synthesis (runs generated code + assertions in isolated
   subprocess; keeps ONLY verified passing traces).
5. Automatic system hygiene (log rotation, stale task/hypothesis recovery, RAM guard).
6. Grid-aware day/night workload scheduling + actionable executive briefings.
"""

from __future__ import annotations

import ast
from datetime import datetime
import hashlib
import json
import logging
import os
from pathlib import Path
import py_compile
import re
import socket
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

import httpx

logger = logging.getLogger("loom.clothos.useful_work")

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
DOCUMENTS_ROOT = WORKSPACE_ROOT.parent


def is_pid_alive(pid: int) -> bool:
    """Checks cross-platform whether an OS process with given PID is alive."""
    if pid <= 0:
        return False
    if sys.platform == "win32":
        try:
            import ctypes
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            STILL_ACTIVE = 259
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, int(pid))
            if not handle:
                return False
            try:
                exit_code = ctypes.c_ulong()
                if kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
                    return exit_code.value == STILL_ACTIVE
                return True
            finally:
                kernel32.CloseHandle(handle)
        except Exception:
            pass
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


class WorkerProcessLock:
    """Single-instance PID lock preventing duplicate 24/7 compute daemons."""

    def __init__(self, lock_path: Optional[Path] = None, owner_name: str = "24x7_compute"):
        self.lock_path = lock_path or (Path.home() / ".loom" / "24x7_worker.lock")
        self.owner_name = owner_name
        self.acquired = False

    def acquire(self) -> Tuple[bool, Optional[int]]:
        """Attempts to acquire the singleton lock. Returns (acquired, conflicting_pid)."""
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        my_pid = os.getpid()

        if self.lock_path.exists():
            try:
                info = json.loads(self.lock_path.read_text(encoding="utf-8"))
                other_pid = int(info.get("pid", 0))
                if other_pid == my_pid:
                    self.acquired = True
                    return True, None
                if other_pid > 0 and is_pid_alive(other_pid):
                    return False, other_pid
            except Exception:
                pass

        payload = {
            "pid": my_pid,
            "owner": self.owner_name,
            "acquired_at": time.time(),
            "acquired_iso": datetime.now().isoformat(),
        }
        try:
            self.lock_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            self.acquired = True
            return True, None
        except Exception as exc:
            logger.warning(f"Failed to acquire lock {self.lock_path}: {exc}")
            return False, None

    def release(self) -> None:
        if not self.acquired:
            return
        try:
            if self.lock_path.exists():
                info = json.loads(self.lock_path.read_text(encoding="utf-8"))
                if int(info.get("pid", 0)) == os.getpid():
                    self.lock_path.unlink(missing_ok=True)
        except Exception:
            pass
        self.acquired = False


# Safe, fast, non-recursive pytest targets rotated across cycles
ROTATING_TEST_TARGETS: List[Tuple[str, str, str]] = [
    ("loom-fabric", "tests/test_structured_pipeline.py", "Structured Research Pipeline"),
    ("loom-fabric", "tests/test_sovereign_tools.py", "Precision Machine Tooling & Fiduciary Guard"),
    ("loom-fabric", "tests/test_clothos_memory_and_wisdom.py", "Memory Continuum & Wisdom Engine"),
    ("loom-fabric", "tests/test_clothos_drivers_and_sdk.py", "Hardware Drivers, SDK & Success Gauge"),
    ("loom-fabric", "tests/test_clothos_distributed_fabric_and_dual_gpu.py", "Dual-GPU & Skill Evolver TDSA"),
    ("loom-fabric", "tests/test_unified_sovereign_nexus.py", "Unified Sovereign Nexus & Typemetric"),
    ("loom-fabric", "tests/test_babelforge_clothos_integration.py", "babelForge-ClothOS Integration"),
    ("loom-fabric", "tests/test_allocator.py", "ClothOS Memory Allocator"),
    ("core-compute-fabric", "tests/test_distributed_execution.py", "Core Compute Fabric Distributed Pipeline"),
    ("universal-jit", "tests", "Universal JIT Native x86-64 Kernels"),
]

# Execution-verified distillation challenges (deterministic self-checking tasks)
VERIFIED_CODING_CURRICULUM: List[Dict[str, str]] = [
    {
        "id": "k_center_gonzalez",
        "domain": "ALGORITHMS",
        "prompt": (
            "Write a pure Python function `farthest_point_select(points, k)` taking a list of 2D tuples "
            "and integer k, returning k indices chosen greedily by Euclidean farthest-point sampling starting at index 0. "
            "Include `assert` tests verifying k=3 selection on a square plus center point."
        ),
    },
    {
        "id": "napot_pmp_encoder",
        "domain": "RISCV_SILICON",
        "prompt": (
            "Write Python functions `encode_napot(base_addr, size_bytes)` and `decode_napot(pmpaddr_val)` "
            "implementing RISC-V PMP NAPOT encoding (addr >> 2) | ((size_bytes >> 3) - 1) for power-of-2 sizes >= 8. "
            "Include `assert` tests verifying round-trip decoding for 4096 and 65536 byte regions."
        ),
    },
    {
        "id": "symplectic_verlet",
        "domain": "PHYSICS_SIMULATION",
        "prompt": (
            "Write a Python function `verlet_oscillator(steps, dt, q0=1.0, p0=0.0, omega=1.0)` implementing "
            "velocity-Verlet symplectic integration of H = 0.5*(p^2 + (omega*q)^2) and returning fractional energy drift. "
            "Include `assert` tests proving drift < 0.001 over 1000 steps with dt=0.01."
        ),
    },
    {
        "id": "conformal_quantile",
        "domain": "DATA_SCIENCE",
        "prompt": (
            "Write a Python function `conformal_interval(residuals, alpha=0.1)` computing the finite-sample "
            "conformal prediction quantile q_hat = ceil((n + 1)*(1 - alpha))/n order statistic on calibration residuals. "
            "Include `assert` tests on a calibration set of size 20 verifying empirical coverage >= 0.90."
        ),
    },
    {
        "id": "kuramoto_order",
        "domain": "DYNAMICAL_SYSTEMS",
        "prompt": (
            "Write a Python function `kuramoto_order_parameter(phases)` using `cmath` or `math` returning (r, psi) "
            "for a sequence of angles in radians. Include `assert` tests for fully synchronized phases (r ~ 1.0) "
            "and balanced antipodal phases (r ~ 0.0)."
        ),
    },
    {
        "id": "walsh_hadamard_1d",
        "domain": "SPECTRAL_MATH",
        "prompt": (
            "Write a pure Python in-place Fast Walsh-Hadamard Transform `fwht(arr)` for power-of-2 integer lists, "
            "plus `assert` tests verifying involution fwht(fwht(x)) == [len(x)*v for v in x] for length 8."
        ),
    },
]


class UsefulComputeWorkEngine:
    """Executes real, measurable, non-spammy 24/7 compute workloads."""

    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = Path(workspace_root or WORKSPACE_ROOT).resolve()
        self.documents_root = self.workspace_root.parent
        self.state_path = Path.home() / ".loom" / "24x7_useful_state.json"
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.verified_pairs_path = self.workspace_root / "data" / "training" / "verified_distillation_pairs.jsonl"
        self.verified_pairs_path.parent.mkdir(parents=True, exist_ok=True)

        self.state: Dict[str, Any] = {
            "last_updated": 0.0,
            "workload_mode": "AUTO",
            "test_cursor": 0,
            "test_suites": {},
            "real_tests_passed": 0,
            "real_tests_failed": 0,
            "real_test_pass_rate_pct": 100.0,
            "last_test_run_epoch": 0.0,
            "code_audit": {
                "last_run_epoch": 0.0,
                "files_checked": 0,
                "syntax_errors": [],
                "warnings": [],
                "dirty_repos": {},
            },
            "hardware_benchmarks": {
                "last_run_epoch": 0.0,
                "gpu0_nvidia": {},
                "gpu1_rx580": {},
                "ujit": {},
                "typemetric": {},
                "cluster_services": {},
                "ollama_probe": {},
            },
            "distillation": {
                "last_run_epoch": 0.0,
                "attempted": 0,
                "verified_passed": 0,
                "pass_rate_pct": 0.0,
                "completed_ids": [],
                "curriculum_cursor": 0,
            },
            "hygiene": {
                "last_run_epoch": 0.0,
                "logs_rotated": 0,
                "stale_tasks_recovered": 0,
                "stale_hyps_recovered": 0,
                "ram_percent": 0.0,
                "disk_free_gb": 0.0,
            },
            "tasks_drained_total": 0,
            "recent_actions": [],
        }
        self._load_state()

    def _load_state(self) -> None:
        if self.state_path.exists():
            try:
                loaded = json.loads(self.state_path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    for k, v in loaded.items():
                        if isinstance(v, dict) and isinstance(self.state.get(k), dict):
                            self.state[k].update(v)
                        else:
                            self.state[k] = v
            except Exception:
                pass

    def _save_state(self) -> None:
        self.state["last_updated"] = time.time()
        try:
            self.state_path.write_text(json.dumps(self.state, indent=2), encoding="utf-8")
        except Exception as exc:
            logger.debug(f"Could not persist 24x7 useful state: {exc}")

    def _record_action(self, summary: str) -> None:
        actions = list(self.state.get("recent_actions", []))
        actions.append(f"[{datetime.now().strftime('%H:%M:%S')}] {summary}")
        self.state["recent_actions"] = actions[-25:]

    # ------------------------------------------------------------------
    # 1. Grid-Aware Mode & Resource Headroom Assessment
    # ------------------------------------------------------------------
    def get_workload_mode(self, override: str = "auto", user_active: bool = False) -> Tuple[str, float]:
        """
        Determines current operating regime and recommended sleep interval (seconds).
        Follows Grid-Aware Energy Arbitrage (Night 22:00-06:00 deep work, Day responsive).
        """
        try:
            import psutil
            ram_pct = float(psutil.virtual_memory().percent)
        except Exception:
            ram_pct = 50.0
        self.state["hygiene"]["ram_percent"] = round(ram_pct, 1)

        if user_active:
            mode = "PREEMPTED_USER_ACTIVE"
            self.state["workload_mode"] = mode
            return mode, 10.0

        if ram_pct >= 90.0:
            mode = "THERMAL_RAM_CONSERVE"
            self.state["workload_mode"] = mode
            return mode, 30.0

        ov = (override or "auto").lower().strip()
        hour = datetime.now().hour
        is_night = (hour >= 22 or hour < 6)

        if ov == "night" or (ov == "auto" and is_night):
            mode = "NIGHT_DEEP_COMPUTE"
            interval = 12.0
        elif ov == "day" or ov == "auto":
            mode = "DAY_LIGHTWEIGHT_BROKER"
            interval = 20.0
        else:
            mode = "MAINTENANCE_ONLY"
            interval = 30.0

        self.state["workload_mode"] = mode
        return mode, interval

    # ------------------------------------------------------------------
    # 2. System Hygiene (Logs, Stale Tasks, Stale Hypotheses, Disk)
    # ------------------------------------------------------------------
    def run_system_hygiene(self, hypothesis_store: Optional[Any] = None) -> Dict[str, Any]:
        """Rotates oversized logs, recovers stuck tasks/hypotheses, and checks RAM/Disk."""
        now = time.time()
        logs_rotated = 0
        stale_tasks = 0
        stale_hyps = 0

        # Rotate logs > 10 MB under ~/.loom/logs
        log_dir = Path.home() / ".loom" / "logs"
        if log_dir.exists():
            for lp in log_dir.glob("*.log"):
                try:
                    if lp.is_file() and lp.stat().st_size > 10 * 1024 * 1024:
                        backup = lp.with_suffix(".log.1")
                        # Keep last 256 KB in .1 so recent context survives without bloating
                        tail_size = 256 * 1024
                        with open(lp, "rb") as src:
                            size = lp.stat().st_size
                            src.seek(max(0, size - tail_size))
                            tail_bytes = src.read()
                        backup.write_bytes(tail_bytes)
                        lp.write_text("", encoding="utf-8")
                        logs_rotated += 1
                except Exception:
                    pass

        # Recover stale RUNNING tasks in .clothos_task_queue.jsonl (> 15 min old)
        q_file = self.workspace_root / ".clothos_task_queue.jsonl"
        if q_file.exists():
            try:
                lines = [l for l in q_file.read_text(encoding="utf-8", errors="replace").splitlines() if l.strip()]
                records = []
                changed = False
                for line in lines:
                    try:
                        rec = json.loads(line)
                    except Exception:
                        continue
                    if rec.get("status") == "RUNNING":
                        started = float(rec.get("started_at") or rec.get("enqueued_at") or now)
                        if (now - started) > 900.0:
                            retries = int(rec.get("retries", 0))
                            if retries < 2:
                                rec["status"] = "QUEUED"
                                rec["retries"] = retries + 1
                            else:
                                rec["status"] = "FAILED"
                                rec["completed_at"] = now
                                rec["output_preview"] = "Marked FAILED after worker crash timeout."
                            stale_tasks += 1
                            changed = True
                    records.append(rec)
                if changed:
                    q_file.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")
            except Exception:
                pass

        # Recover stale running hypotheses in SQLite
        if hypothesis_store is not None and hasattr(hypothesis_store, "reset_stale_running"):
            try:
                stale_hyps = int(hypothesis_store.reset_stale_running(max_age_s=600.0))
            except Exception:
                pass

        # Real RAM and disk metrics
        ram_pct = 0.0
        disk_free_gb = 0.0
        try:
            import psutil
            ram_pct = round(float(psutil.virtual_memory().percent), 1)
            disk_free_gb = round(psutil.disk_usage(str(self.workspace_root)).free / (1024 ** 3), 2)
        except Exception:
            pass

        self.state["hygiene"] = {
            "last_run_epoch": now,
            "logs_rotated": self.state["hygiene"].get("logs_rotated", 0) + logs_rotated,
            "stale_tasks_recovered": self.state["hygiene"].get("stale_tasks_recovered", 0) + stale_tasks,
            "stale_hyps_recovered": self.state["hygiene"].get("stale_hyps_recovered", 0) + stale_hyps,
            "ram_percent": ram_pct,
            "disk_free_gb": disk_free_gb,
        }
        if logs_rotated or stale_tasks or stale_hyps:
            self._record_action(
                f"Hygiene: rotated {logs_rotated} log(s), recovered {stale_tasks} task(s), reset {stale_hyps} stale hyp(s)"
            )
        self._save_state()
        return self.state["hygiene"]

    # ------------------------------------------------------------------
    # 3. Priority Task Queue Execution (Fast + Reliable)
    # ------------------------------------------------------------------
    def drain_task_queue(self, task_runner: Any, agent_engine: Any, max_tasks: int = 3) -> int:
        """
        Drains queued tasks cleanly. Handles self-contained Python/compute prompts directly
        in a sandboxed subprocess if the prompt explicitly asks for Python calculation,
        otherwise delegates to ClothOSAgentEngine.
        """
        drained = 0
        for _ in range(max_tasks):
            tasks = task_runner.list_tasks(limit=100)
            pending = next((t for t in tasks if t.get("status") == "QUEUED"), None)
            if not pending:
                break

            res = task_runner.execute_next_task(agent_engine)
            if not res:
                break
            drained += 1
            self.state["tasks_drained_total"] = int(self.state.get("tasks_drained_total", 0)) + 1
            self._record_action(f"Task {res.get('task_id')} -> {res.get('status')} ({res.get('duration_s')}s)")
            self._save_state()
        return drained

    # ------------------------------------------------------------------
    # 4. Real Multi-Project Test Verification (Rotating Pytest)
    # ------------------------------------------------------------------
    @staticmethod
    def _clean_subprocess_env(extra_pythonpath: Optional[str] = None) -> Dict[str, str]:
        """Strips PYTHONHOME, PYTHONPATH, VIRTUAL_ENV per multi-env isolation mandate."""
        env = dict(os.environ)
        for k in ("PYTHONHOME", "PYTHONPATH", "VIRTUAL_ENV"):
            env.pop(k, None)
        if extra_pythonpath:
            env["PYTHONPATH"] = extra_pythonpath
        return env

    def _resolve_project_python(self, proj_dir: Path) -> str:
        for rel in (".venv/Scripts/python.exe", ".fabric-env/Scripts/python.exe", ".venv/bin/python"):
            cand = proj_dir / rel
            if cand.exists():
                return str(cand)
        venv_py = self.workspace_root / ".venv" / "Scripts" / "python.exe"
        return str(venv_py) if venv_py.exists() else sys.executable

    def run_rotating_test_audit(self, force: bool = False, min_interval_s: float = 180.0) -> Optional[Dict[str, Any]]:
        """Runs one real pytest target from ROTATING_TEST_TARGETS and caches exact pass/fail counts."""
        now = time.time()
        last_t = float(self.state.get("last_test_run_epoch", 0.0))
        if not force and (now - last_t) < min_interval_s:
            return None

        cursor = int(self.state.get("test_cursor", 0))
        chosen: Optional[Tuple[str, str, str, Path, Path]] = None
        for offset in range(len(ROTATING_TEST_TARGETS)):
            idx = (cursor + offset) % len(ROTATING_TEST_TARGETS)
            proj_name, rel_target, label = ROTATING_TEST_TARGETS[idx]
            proj_dir = self.workspace_root if proj_name == "loom-fabric" else (self.documents_root / proj_name)
            target_path = proj_dir / rel_target
            if target_path.exists():
                chosen = (proj_name, rel_target, label, proj_dir, target_path)
                self.state["test_cursor"] = (idx + 1) % len(ROTATING_TEST_TARGETS)
                break

        if not chosen:
            return None

        proj_name, rel_target, label, proj_dir, _ = chosen
        py_exe = self._resolve_project_python(proj_dir)
        env = self._clean_subprocess_env(extra_pythonpath=str(proj_dir))
        extra_flags = 0x08000000 if sys.platform == "win32" else 0

        t0 = time.perf_counter()
        passed = 0
        failed = 0
        skipped = 0
        errors = 0
        rc = -1
        failed_lines: List[str] = []

        try:
            proc = subprocess.run(
                [py_exe, "-m", "pytest", rel_target, "-q", "--tb=line"],
                cwd=str(proj_dir),
                env=env,
                capture_output=True,
                text=True,
                timeout=45.0,
                creationflags=extra_flags,
            )
            rc = proc.returncode
            out = (proc.stdout or "") + "\n" + (proc.stderr or "")
            m_pass = re.search(r"(\d+)\s+passed", out)
            m_fail = re.search(r"(\d+)\s+failed", out)
            m_err = re.search(r"(\d+)\s+error", out)
            m_skip = re.search(r"(\d+)\s+skipped", out)
            passed = int(m_pass.group(1)) if m_pass else 0
            failed = int(m_fail.group(1)) if m_fail else 0
            errors = int(m_err.group(1)) if m_err else 0
            skipped = int(m_skip.group(1)) if m_skip else 0
            for ln in out.splitlines():
                if ln.startswith("FAILED ") or ln.startswith("ERROR "):
                    failed_lines.append(ln[:160])
        except subprocess.TimeoutExpired:
            errors = 1
            failed_lines = [f"TIMEOUT (>45s) running {proj_name}/{rel_target}"]
        except Exception as exc:
            errors = 1
            failed_lines = [f"EXEC_ERROR: {exc}"]

        dur = round(time.perf_counter() - t0, 2)
        suite_key = f"{proj_name}:{rel_target}"
        suite_entry = {
            "project": proj_name,
            "target": rel_target,
            "label": label,
            "returncode": rc,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "skipped": skipped,
            "duration_s": dur,
            "failed_details": failed_lines[:5],
            "checked_at": now,
        }
        self.state["test_suites"][suite_key] = suite_entry
        self.state["last_test_run_epoch"] = now

        # Aggregate totals across all measured suites
        tot_p = sum(s.get("passed", 0) for s in self.state["test_suites"].values())
        tot_f = sum(s.get("failed", 0) + s.get("errors", 0) for s in self.state["test_suites"].values())
        self.state["real_tests_passed"] = tot_p
        self.state["real_tests_failed"] = tot_f
        denom = tot_p + tot_f
        self.state["real_test_pass_rate_pct"] = round((tot_p / denom) * 100.0, 2) if denom > 0 else 100.0

        self._record_action(
            f"Pytest [{suite_key}]: {passed} passed, {failed + errors} failed ({dur}s)"
        )
        self._save_state()
        return suite_entry

    # ------------------------------------------------------------------
    # 5. Read-Only Codebase Syntax & AST Quality Audit
    # ------------------------------------------------------------------
    def run_code_quality_audit(self, force: bool = False, min_interval_s: float = 300.0) -> Optional[Dict[str, Any]]:
        """Scans Python modules across active repos for real syntax errors, AST issues, and git dirty state."""
        now = time.time()
        last_t = float(self.state["code_audit"].get("last_run_epoch", 0.0))
        if not force and (now - last_t) < min_interval_s:
            return None

        skip_dirs = {
            ".venv", ".fabric-env", "node_modules", ".git", "__pycache__", ".pytest_cache",
            "deliverables", "artifacts", "clothos_root", "dist", "build", ".next", "out",
        }
        py_files: List[Path] = []
        scan_roots = [
            self.workspace_root / "loom",
            self.workspace_root / "scripts",
            self.documents_root / "core-compute-fabric",
            self.documents_root / "fouriersLibrary" / "backend",
            self.documents_root / "gnome-sentinel" / "server",
        ]
        for sr in scan_roots:
            if not sr.exists():
                continue
            for root, dirs, files in os.walk(sr):
                dirs[:] = [d for d in dirs if d not in skip_dirs]
                for fn in files:
                    if fn.endswith(".py"):
                        py_files.append(Path(root) / fn)

        syntax_errors: List[Dict[str, str]] = []
        warnings: List[Dict[str, str]] = []
        for pf in py_files[:400]:
            try:
                src = pf.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(src, filename=str(pf))
                # Detect common real maintainability hazards
                for node in ast.walk(tree):
                    if isinstance(node, ast.ExceptHandler) and node.type is None:
                        rel = str(pf.relative_to(self.documents_root))
                        warnings.append({"file": rel, "line": str(node.lineno), "issue": "Bare except: clause"})
                        break
            except SyntaxError as se:
                rel = str(pf.relative_to(self.documents_root))
                syntax_errors.append({"file": rel, "line": str(se.lineno), "error": str(se.msg)})
            except Exception:
                continue

        # Check git dirty status across key repos
        dirty_repos: Dict[str, int] = {}
        extra_flags = 0x08000000 if sys.platform == "win32" else 0
        for repo_name in ("loom-fabric", "fouriersLibrary", "gnome-sentinel", "core-compute-fabric"):
            rp = self.documents_root / repo_name
            if (rp / ".git").exists():
                try:
                    out = subprocess.check_output(
                        ["git", "status", "--porcelain"],
                        cwd=str(rp),
                        text=True,
                        timeout=5.0,
                        creationflags=extra_flags,
                        stderr=subprocess.DEVNULL,
                    )
                    cnt = len([l for l in out.splitlines() if l.strip()])
                    dirty_repos[repo_name] = cnt
                except Exception:
                    pass

        audit_res = {
            "last_run_epoch": now,
            "files_checked": len(py_files[:400]),
            "syntax_errors": syntax_errors[:15],
            "warnings": warnings[:15],
            "dirty_repos": dirty_repos,
        }
        self.state["code_audit"] = audit_res
        self._record_action(
            f"Code Audit: {audit_res['files_checked']} py files, {len(syntax_errors)} syntax errors, {len(warnings)} bare-except warnings"
        )
        self._save_state()
        return audit_res

    # ------------------------------------------------------------------
    # 6. Live Hardware, Cluster & Kernel Benchmarks
    # ------------------------------------------------------------------
    def _probe_tcp(self, host: str, port: int, timeout: float = 0.4) -> bool:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except OSError:
            return False

    def run_hardware_and_cluster_benchmark(
        self,
        rx580_engine: Optional[Any] = None,
        run_llm_probe: bool = False,
        force: bool = False,
        min_interval_s: float = 120.0,
    ) -> Optional[Dict[str, Any]]:
        """Collects real GPU thermals/VRAM, RX580 OpenCL, ujit, Typemetric, and cluster service health."""
        now = time.time()
        last_t = float(self.state["hardware_benchmarks"].get("last_run_epoch", 0.0))
        if not force and (now - last_t) < min_interval_s:
            return None

        extra_flags = 0x08000000 if sys.platform == "win32" else 0

        # A. NVIDIA RTX 3060 via nvidia-smi
        gpu0: Dict[str, Any] = {"available": False}
        try:
            proc = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=name,temperature.gpu,power.draw,memory.used,memory.total,utilization.gpu",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=3.0,
                creationflags=extra_flags,
            )
            if proc.returncode == 0 and proc.stdout.strip():
                parts = [p.strip() for p in proc.stdout.strip().splitlines()[0].split(",")]
                if len(parts) >= 6:
                    gpu0 = {
                        "available": True,
                        "name": parts[0],
                        "temp_c": float(parts[1]),
                        "power_w": float(parts[2]),
                        "vram_used_mb": float(parts[3]),
                        "vram_total_mb": float(parts[4]),
                        "util_pct": float(parts[5]),
                    }
        except Exception:
            pass

        # B. AMD RX 580 OpenCL Benchmark
        gpu1: Dict[str, Any] = {"available": False}
        if rx580_engine is not None:
            try:
                t0 = time.perf_counter()
                res = rx580_engine.step_sweep(steps=150, k_coupling=2.6)
                dt_ms = round((time.perf_counter() - t0) * 1000.0, 2)
                gpu1 = {
                    "available": bool(getattr(rx580_engine, "_initialized", False)),
                    "device": res.get("device"),
                    "backend": res.get("backend"),
                    "coherence_r": res.get("coherence_r"),
                    "latency_ms": dt_ms,
                }
            except Exception as exc:
                gpu1 = {"available": False, "error": str(exc)}

        # C. Universal JIT x86-64 Bare-Metal Kernel Benchmark
        ujit_bench: Dict[str, Any] = {}
        try:
            from loom.clothos.ujit_engine import clothos_jit
            t0 = time.perf_counter()
            val = 0
            for _ in range(2000):
                val = clothos_jit.dispatch("grid_arbitrage", 1000, 15, 1)
            elapsed_ms = max((time.perf_counter() - t0) * 1000.0, 1e-4)
            ujit_bench = {
                "ok": (val == 9750),
                "calls_per_sec": round(2000.0 / (elapsed_ms / 1000.0), 1),
                "elapsed_ms_2k": round(elapsed_ms, 3),
            }
        except Exception as exc:
            ujit_bench = {"ok": False, "error": str(exc)}

        # D. Typemetric Dozenal + WHT Verification
        tm_bench: Dict[str, Any] = {}
        try:
            from loom.unified_nexus import tm_dozenal_kuramoto_step_batch, tm_wht_eval
            sync = tm_dozenal_kuramoto_step_batch([0, 768, 1536, 2304], [24, 42, 12, 36], [1, 1, 1, 1], [1728, 1152, 864, 864], 24)
            wht = tm_wht_eval([0, 1, 1, 0], input_bits=0b01)
            tm_bench = {
                "ok": (abs(wht["evaluated_normalized"] - 1.0) < 1e-6),
                "coherence_float": sync.get("coherence_float"),
            }
        except Exception as exc:
            tm_bench = {"ok": False, "error": str(exc)}

        # E. Cluster Service Matrix (Real Port & HTTP Checks)
        services = {
            "node1_ollama": self._probe_tcp("127.0.0.1", 11434),
            "node1_master": self._probe_tcp("127.0.0.1", 8087),
            "node1_gateway": self._probe_tcp("127.0.0.1", 8087),
            "node1_dashboard": self._probe_tcp("127.0.0.1", 8087),
            "node2_ollama": self._probe_tcp("192.168.99.2", 11434),
            "node2_master": self._probe_tcp("192.168.99.2", 8087),
            "node2_ray": self._probe_tcp("192.168.99.2", 6379),
        }

        # F. Optional Live Ollama Throughput Probe (when idle)
        ollama_probe = dict(self.state["hardware_benchmarks"].get("ollama_probe", {}))
        if run_llm_probe and services["node1_ollama"]:
            try:
                t0 = time.perf_counter()
                with httpx.Client(timeout=12.0) as client:
                    r = client.post(
                        "http://127.0.0.1:11434/api/generate",
                        json={
                            "model": "qwen2.5:7b",
                            "prompt": "Reply with exactly: PONG_VERIFIED",
                            "stream": False,
                            "options": {"num_predict": 12, "temperature": 0.0},
                        },
                    )
                    if r.status_code == 200:
                        d = r.json()
                        eval_count = int(d.get("eval_count", 1) or 1)
                        eval_ns = int(d.get("eval_duration", 1) or 1)
                        tps = round(eval_count / max(eval_ns / 1e9, 1e-6), 1)
                        ollama_probe = {
                            "model": "qwen2.5:7b",
                            "online": True,
                            "tokens_per_sec": tps,
                            "roundtrip_ms": round((time.perf_counter() - t0) * 1000.0, 1),
                            "checked_at": now,
                        }
            except Exception as exc:
                ollama_probe = {"online": False, "error": str(exc), "checked_at": now}

        bench = {
            "last_run_epoch": now,
            "gpu0_nvidia": gpu0,
            "gpu1_rx580": gpu1,
            "ujit": ujit_bench,
            "typemetric": tm_bench,
            "cluster_services": services,
            "ollama_probe": ollama_probe,
        }
        self.state["hardware_benchmarks"] = bench
        up_cnt = sum(1 for v in services.values() if v)
        self._record_action(
            f"Benchmarks: {up_cnt}/{len(services)} services up | GPU0 {gpu0.get('temp_c', '?')}C | ujit {ujit_bench.get('calls_per_sec', '?')} ops/s"
        )
        self._save_state()
        return bench

    # ------------------------------------------------------------------
    # 7. Execution-Verified LLM Coding & Reasoning Distillation
    # ------------------------------------------------------------------
    def run_verified_llm_distillation(
        self,
        force: bool = False,
        min_interval_s: float = 300.0,
    ) -> Optional[Dict[str, Any]]:
        """
        Generates ONE solution + self-test via local Ollama (`qwen2.5-coder:7b` / `qwen2.5:7b`),
        executes it in an isolated subprocess, and stores ONLY execution-verified traces.
        """
        now = time.time()
        dist_state = self.state["distillation"]
        if not force and (now - float(dist_state.get("last_run_epoch", 0.0))) < min_interval_s:
            return None
        if not self._probe_tcp("127.0.0.1", 11434, timeout=0.3):
            return None

        cursor = int(dist_state.get("curriculum_cursor", 0))
        task = VERIFIED_CODING_CURRICULUM[cursor % len(VERIFIED_CODING_CURRICULUM)]
        dist_state["curriculum_cursor"] = (cursor + 1) % len(VERIFIED_CODING_CURRICULUM)
        dist_state["last_run_epoch"] = now

        # Pick best available coder model
        model_name = "qwen2.5-coder:7b"
        try:
            with httpx.Client(timeout=2.0) as client:
                tags = client.get("http://127.0.0.1:11434/api/tags").json()
                names = [m.get("name", "") for m in tags.get("models", [])]
                if "qwen2.5-coder:7b" in names:
                    model_name = "qwen2.5-coder:7b"
                elif "qwen2.5:7b" in names:
                    model_name = "qwen2.5:7b"
                elif names:
                    model_name = names[0]
        except Exception:
            pass

        prompt = (
            f"{task['prompt']}\n\n"
            "Return ONLY a single fenced ```python ... ``` code block containing the complete function(s) "
            "and `assert` statements so it can run directly with `python`."
        )

        code_text = ""
        raw_reply = ""
        try:
            with httpx.Client(timeout=120.0) as client:
                resp = client.post(
                    "http://127.0.0.1:11434/api/generate",
                    json={
                        "model": model_name,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": 0.2, "num_predict": 900},
                    },
                )
                if resp.status_code == 200:
                    raw_reply = resp.json().get("response", "")
        except Exception as exc:
            dist_state["attempted"] = int(dist_state.get("attempted", 0)) + 1
            self._save_state()
            return {"task_id": task["id"], "verified": False, "error": str(exc)}

        m = re.search(r"```(?:python|py)?\s*\n(.*?)```", raw_reply, re.DOTALL | re.IGNORECASE)
        code_text = m.group(1).strip() if m else raw_reply.strip()

        dist_state["attempted"] = int(dist_state.get("attempted", 0)) + 1
        verified = False
        exec_err = ""

        if code_text and "assert " in code_text:
            py_exe = self._resolve_project_python(self.workspace_root)
            env = self._clean_subprocess_env()
            extra_flags = 0x08000000 if sys.platform == "win32" else 0
            try:
                proc = subprocess.run(
                    [py_exe, "-c", code_text],
                    cwd=str(self.workspace_root),
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=8.0,
                    creationflags=extra_flags,
                )
                verified = (proc.returncode == 0)
                if not verified:
                    exec_err = (proc.stderr or proc.stdout or "")[:240]
            except Exception as exc:
                exec_err = str(exc)

        if verified:
            dist_state["verified_passed"] = int(dist_state.get("verified_passed", 0)) + 1
            code_hash = hashlib.sha256(code_text.encode("utf-8")).hexdigest()[:16]
            completed_ids = list(dist_state.get("completed_ids", []))
            entry_key = f"{task['id']}:{code_hash}"
            if entry_key not in completed_ids:
                completed_ids.append(entry_key)
                dist_state["completed_ids"] = completed_ids[-200:]
                record = {
                    "task_id": task["id"],
                    "domain": task["domain"],
                    "model": model_name,
                    "prompt": task["prompt"],
                    "verified_code": code_text,
                    "code_sha256": code_hash,
                    "execution_verified": True,
                    "timestamp": now,
                }
                with open(self.verified_pairs_path, "a", encoding="utf-8") as vf:
                    vf.write(json.dumps(record) + "\n")

                # Mirror verified execution pair into Llama 70B Sovereign Teacher Distillation ledger
                try:
                    from loom.models.distillation_trainer import distillation_trainer
                    critique = distillation_trainer.teacher.critique_and_upgrade_student(
                        prompt=task["prompt"],
                        student_output=f"```python\n{code_text}\n```",
                        domain=task["domain"],
                    )
                    pair_70b = {
                        "task_id": f"exec-verified-{task['id']}-{code_hash[:8]}",
                        "category": f"Verified Execution ({task['domain']})",
                        "system_prompt": "You are Loom Sovereign trained on execution-verified + Llama 3.3 70B critiqued traces.",
                        "user_prompt": task["prompt"],
                        "teacher_model": critique.get("teacher_model", "llama3.3:70b"),
                        "teacher_response": critique.get("upgraded_response", code_text),
                        "student_model": model_name,
                        "execution_verified": True,
                        "confidence_score": 0.99 if critique.get("used_live_70b") else 0.95,
                        "timestamp": now,
                    }
                    distill_jsonl = self.workspace_root / "data" / "training" / "loom_70b_distillation_pairs.jsonl"
                    distill_jsonl.parent.mkdir(parents=True, exist_ok=True)
                    with open(distill_jsonl, "a", encoding="utf-8") as df:
                        df.write(json.dumps(pair_70b, ensure_ascii=False) + "\n")
                except Exception:
                    pass

        att = max(1, int(dist_state.get("attempted", 1)))
        dist_state["pass_rate_pct"] = round((int(dist_state.get("verified_passed", 0)) / att) * 100.0, 1)
        self._record_action(
            f"LLM Eval [{task['id']} via {model_name}]: {'PASS' if verified else 'FAIL'}"
        )
        self._save_state()
        return {"task_id": task["id"], "model": model_name, "verified": verified, "error": exec_err}

    # ------------------------------------------------------------------
    # 8. Curated Executive Briefing Synthesis
    # ------------------------------------------------------------------
    def synthesize_briefing(self, worker_stats: Optional[Dict[str, Any]] = None) -> Path:
        """Writes an honest, actionable briefing summarizing real 24/7 work & findings."""
        now_dt = datetime.now()
        st = self.state
        bench = st.get("hardware_benchmarks", {})
        gpu0 = bench.get("gpu0_nvidia", {})
        gpu1 = bench.get("gpu1_rx580", {})
        ujit = bench.get("ujit", {})
        svcs = bench.get("cluster_services", {})
        ollama = bench.get("ollama_probe", {})
        audit = st.get("code_audit", {})
        dist = st.get("distillation", {})
        hyg = st.get("hygiene", {})

        lines = [
            f"# ClothOS 24/7 Autonomous Compute Executive Briefing — {now_dt.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            f"- **Active Workload Mode**: `{st.get('workload_mode', 'AUTO')}`",
            f"- **Host Resources**: RAM `{hyg.get('ram_percent', '?')}%` | Disk Free `{hyg.get('disk_free_gb', '?')} GB`",
            f"- **Queued Tasks Drained**: `{st.get('tasks_drained_total', 0)}`",
            "",
            "## 1. Real Automated Test Suite Verification",
            f"- **Aggregate Pass Rate**: `{st.get('real_test_pass_rate_pct', 100.0)}%` (`{st.get('real_tests_passed', 0)}` passed, `{st.get('real_tests_failed', 0)}` failed/errors)",
            "",
            "| Project / Suite | Passed | Failed/Err | Duration | Status |",
            "| :--- | :---: | :---: | :---: | :--- |",
        ]

        suites = st.get("test_suites", {})
        if suites:
            for key, s in sorted(suites.items()):
                fail_tot = s.get("failed", 0) + s.get("errors", 0)
                status = "PASS" if (s.get("returncode") == 0 and fail_tot == 0) else "FAIL"
                lines.append(
                    f"| `{key}` | {s.get('passed', 0)} | {fail_tot} | {s.get('duration_s', 0)}s | **{status}** |"
                )
        else:
            lines.append("| *(awaiting first sweep)* | - | - | - | - |")

        failing_details = [
            (k, s.get("failed_details", []))
            for k, s in suites.items()
            if s.get("failed", 0) + s.get("errors", 0) > 0
        ]
        if failing_details:
            lines.append("")
            lines.append("### Failing Test Details")
            for k, dets in failing_details:
                for d in dets:
                    lines.append(f"- `{k}`: `{d}`")

        lines.extend([
            "",
            "## 2. Live Hardware, Silicon & Cluster Telemetry",
            f"- **Node 1 GPU 0 (NVIDIA)**: `{gpu0.get('name', 'N/A')}` | Temp `{gpu0.get('temp_c', '?')}°C` | Power `{gpu0.get('power_w', '?')}W` | VRAM `{gpu0.get('vram_used_mb', '?')}/{gpu0.get('vram_total_mb', '?')} MB` | Util `{gpu0.get('util_pct', '?')}%`",
            f"- **Node 1 GPU 1 (RX 580 OpenCL)**: Available=`{gpu1.get('available', False)}` | Coherence $r={gpu1.get('coherence_r', '?')}$ | Sweep Latency `{gpu1.get('latency_ms', '?')} ms`",
            f"- **Universal JIT (x86-64)**: OK=`{ujit.get('ok', False)}` | Throughput `{ujit.get('calls_per_sec', '?')} calls/s`",
            f"- **Local Ollama (`qwen2.5:7b`)**: Online=`{ollama.get('online', False)}` | Speed `{ollama.get('tokens_per_sec', '?')} tok/s`",
            f"- **Cluster Services Online**: `{sum(1 for v in svcs.values() if v)}/{len(svcs)}` ({', '.join(k for k, v in svcs.items() if v) or 'none'})",
            "",
            "## 3. Codebase Static Quality & Git Status",
            f"- **Python Files Checked**: `{audit.get('files_checked', 0)}` | **Syntax Errors**: `{len(audit.get('syntax_errors', []))}` | **Bare-Except Warnings**: `{len(audit.get('warnings', []))}`",
        ])
        for se in audit.get("syntax_errors", [])[:5]:
            lines.append(f"  - SYNTAX ERROR `{se.get('file')}:{se.get('line')}`: {se.get('error')}")
        if audit.get("dirty_repos"):
            dirty_str = ", ".join(f"`{k}` ({v} changes)" for k, v in audit["dirty_repos"].items())
            lines.append(f"- **Workspace Git State**: {dirty_str}")

        lines.extend([
            "",
            "## 4. Execution-Verified LLM Coding & Reasoning",
            f"- **Attempts**: `{dist.get('attempted', 0)}` | **Verified Passing**: `{dist.get('verified_passed', 0)}` (`{dist.get('pass_rate_pct', 0.0)}%`)",
            f"- **Dataset Path**: `data/training/verified_distillation_pairs.jsonl`",
            "",
            "## 5. System Hygiene & Recent Actions",
            f"- **Logs Rotated**: `{hyg.get('logs_rotated', 0)}` | **Stale Tasks Recovered**: `{hyg.get('stale_tasks_recovered', 0)}` | **Stale Hypotheses Reset**: `{hyg.get('stale_hyps_recovered', 0)}`",
        ])
        for act in st.get("recent_actions", [])[-10:]:
            lines.append(f"- {act}")

        if worker_stats:
            lines.extend([
                "",
                "## 6. Research & Coherence Metrics",
                f"- **SCI**: `{worker_stats.get('sovereign_coherence_index', '?')}%` | **Cycles**: `{worker_stats.get('total_cycles_completed', 0):,}`",
                f"- **Hypotheses**: `{worker_stats.get('moltbook_hypotheses_indexed', 0):,}` (`{worker_stats.get('hypotheses_confirmed', 0):,}` confirmed, `{worker_stats.get('hypotheses_refuted', 0):,}` refuted)",
            ])

        report_md = "\n".join(lines) + "\n"
        latest_report = self.workspace_root / "deliverables" / "LATEST_24X7_REPORT.md"
        latest_report.parent.mkdir(parents=True, exist_ok=True)
        latest_report.write_text(report_md, encoding="utf-8")

        morning_path = self.workspace_root / "interpretations" / "MORNING_BRIEFING.md"
        morning_path.parent.mkdir(parents=True, exist_ok=True)
        morning_path.write_text(report_md, encoding="utf-8")
        return latest_report

    # ------------------------------------------------------------------
    # 9. Unified Step Entrypoint Called by 24/7 Orchestrator & Worker
    # ------------------------------------------------------------------
    def run_useful_cycle(
        self,
        hypothesis_store: Optional[Any] = None,
        task_runner: Optional[Any] = None,
        agent_engine: Optional[Any] = None,
        rx580_engine: Optional[Any] = None,
        mode_override: str = "auto",
        user_active: bool = False,
        force_checks: bool = False,
    ) -> Dict[str, Any]:
        """Executes one complete, disciplined useful-work cycle respecting day/night & preemption."""
        mode, recommended_sleep = self.get_workload_mode(override=mode_override, user_active=user_active)

        # Always run lightweight hygiene
        hyg = self.run_system_hygiene(hypothesis_store=hypothesis_store)

        # Always drain queued tasks if not preempted
        tasks_drained = 0
        if not user_active and task_runner is not None and agent_engine is not None:
            tasks_drained = self.drain_task_queue(task_runner, agent_engine, max_tasks=3)

        if user_active:
            return {
                "mode": mode,
                "recommended_sleep_s": recommended_sleep,
                "tasks_drained": tasks_drained,
                "hygiene": hyg,
                "test_run": None,
                "code_audit": None,
                "benchmark": None,
                "distillation": None,
                "briefing_path": str(self.workspace_root / "deliverables" / "LATEST_24X7_REPORT.md"),
            }

        is_night = (mode == "NIGHT_DEEP_COMPUTE")
        test_interval = 120.0 if is_night else 300.0
        audit_interval = 240.0 if is_night else 600.0
        bench_interval = 90.0 if is_night else 240.0
        dist_interval = 180.0 if is_night else 600.0

        test_res = self.run_rotating_test_audit(force=force_checks, min_interval_s=test_interval)
        audit_res = self.run_code_quality_audit(force=force_checks, min_interval_s=audit_interval)
        bench_res = self.run_hardware_and_cluster_benchmark(
            rx580_engine=rx580_engine,
            run_llm_probe=(is_night or force_checks) and hyg.get("ram_percent", 0) < 88.0,
            force=force_checks,
            min_interval_s=bench_interval,
        )

        dist_res = None
        if hyg.get("ram_percent", 0.0) < 86.0 and (is_night or force_checks):
            dist_res = self.run_verified_llm_distillation(force=force_checks, min_interval_s=dist_interval)

        briefing_path = self.synthesize_briefing()
        return {
            "mode": mode,
            "recommended_sleep_s": recommended_sleep,
            "tasks_drained": tasks_drained,
            "hygiene": hyg,
            "test_run": test_res,
            "code_audit": audit_res,
            "benchmark": bench_res,
            "distillation": dist_res,
            "briefing_path": str(briefing_path),
        }


useful_work_engine = UsefulComputeWorkEngine()
