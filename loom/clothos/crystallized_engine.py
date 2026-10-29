# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
ClothOS Neuro-Symbolic Crystallization & Problem-Solving Knowledgebase Engine (`loom/clothos/crystallized_engine.py`).
=================================================================================================================
Implements the Fluid vs. Crystallized Cognitive Separation (Gf vs. Gc):
1. Fluid Cortex (Dynamic Reasoning):
   Probabilistic LLM handles natural language, strategic planning, creative ideation, and context routing.
2. Crystallized Knowledgebase (Gc Deterministic Execution):
   Offloads recurrent, heavy, or exact calculations (mathematics, signal processing, AST transformations,
   topological invariants, tensor dimensions) into pure compiled Python functions.
3. Test-Driven Arbitrary Skill Crystallization:
   Whenever an opportunity to offload a calculation is identified, automatically synthesizes:
   - A pure, deterministic Python computational kernel.
   - A comprehensive empirical unit test with edge cases and invariants.
   - Runs the test: ONLY if the unit test passes is the routine crystallized into the knowledgebase.
"""

from __future__ import annotations

import ast
from dataclasses import asdict, dataclass, field
from datetime import datetime
import importlib.util
import inspect
import json
import logging
from pathlib import Path
import re
import subprocess
import sys
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger("loom.clothos.crystallized_engine")

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
KB_ROOT = WORKSPACE_ROOT / "clothos_root" / "crystallized_kb"
KERNELS_DIR = KB_ROOT / "kernels"
TESTS_DIR = KB_ROOT / "tests"
REGISTRY_FILE = KB_ROOT / "registry.json"


@dataclass
class CrystallizedKernel:
    """Represents an offloaded, pure-function deterministic computational skill."""
    kernel_id: str
    name: str
    description: str
    category: str  # MATH | SIGNALS | AST | TENSORS | SYSTEMS | FINANCE
    function_signature: str
    code: str
    unit_test_code: str
    version: str = "1.0.0"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_verified_at: str = field(default_factory=lambda: datetime.now().isoformat())
    execution_count: int = 0
    average_latency_ms: float = 0.0
    status: str = "ACTIVE"  # ACTIVE | CANDIDATE | FAILED
    tags: List[str] = field(default_factory=list)


class CrystallizedKnowledgeEngine:
    """Manages the registry of crystallized problem-solving routines and test-driven offloads."""

    _kernels: Dict[str, CrystallizedKernel] = {}
    _loaded_modules: Dict[str, Any] = {}
    _initialized: bool = False

    @classmethod
    def initialize(cls) -> None:
        """Initializes directories and loads all ratified crystallized routines."""
        if cls._initialized:
            return

        KB_ROOT.mkdir(parents=True, exist_ok=True)
        KERNELS_DIR.mkdir(parents=True, exist_ok=True)
        TESTS_DIR.mkdir(parents=True, exist_ok=True)

        cls._kernels.clear()
        cls._loaded_modules.clear()

        # Seed foundational crystallized kernels if empty
        cls._seed_foundational_kernels()

        # Load registry if exists
        if REGISTRY_FILE.exists():
            try:
                data = json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
                for k_id, item in data.items():
                    kernel = CrystallizedKernel(**item)
                    cls._kernels[k_id] = kernel
                    cls._load_module(kernel)
            except Exception as exc:
                logger.warning(f"Failed to load crystallized registry: {exc}")

        cls._initialized = True
        logger.info(f"CrystallizedKnowledgeEngine initialized with {len(cls._kernels)} active offloaded kernels.")

    @classmethod
    def _seed_foundational_kernels(cls) -> None:
        """Seeds bedrock exact calculation kernels (matrix powers, shannon entropy, tensor splits)."""
        foundational = [
            CrystallizedKernel(
                kernel_id="calc_matrix_fibonacci",
                name="Fast Matrix Exponentiation Fibonacci",
                description="Computes N-th Fibonacci number deterministically in O(log N) using 2x2 matrix powers.",
                category="MATH",
                function_signature="fibonacci(n: int) -> int",
                code="""def fibonacci(n: int) -> int:
    if n < 0:
        raise ValueError("n must be non-negative")
    if n in (0, 1):
        return n
    def _matrix_mult(A, B):
        return [
            [A[0][0]*B[0][0] + A[0][1]*B[1][0], A[0][0]*B[0][1] + A[0][1]*B[1][1]],
            [A[1][0]*B[0][0] + A[1][1]*B[1][0], A[1][0]*B[0][1] + A[1][1]*B[1][1]],
        ]
    def _matrix_power(M, p):
        result = [[1, 0], [0, 1]]
        base = M
        while p > 0:
            if p % 2 == 1:
                result = _matrix_mult(result, base)
            base = _matrix_mult(base, base)
            p //= 2
        return result
    T = [[1, 1], [1, 0]]
    powered = _matrix_power(T, n - 1)
    return powered[0][0]
""",
                unit_test_code="""def test_kernel():
    assert fibonacci(0) == 0
    assert fibonacci(1) == 1
    assert fibonacci(2) == 1
    assert fibonacci(10) == 55
    assert fibonacci(20) == 6765
    assert fibonacci(50) == 12586269025
""",
                tags=["fibonacci", "math", "matrix", "exponentiation"],
            ),
            CrystallizedKernel(
                kernel_id="calc_shannon_entropy",
                name="Shannon Probability Entropy & Information Density",
                description="Calculates exact Shannon entropy H(X) in bits for probability distributions.",
                category="SIGNALS",
                function_signature="shannon_entropy(probabilities: list[float]) -> float",
                code="""import math
def shannon_entropy(probabilities: list[float]) -> float:
    if not probabilities:
        return 0.0
    total = sum(probabilities)
    if total <= 0:
        return 0.0
    norm = [p / total for p in probabilities if p > 0]
    return -sum(p * math.log2(p) for p in norm)
""",
                unit_test_code="""def test_kernel():
    import math
    # Uniform distribution across 2 states = 1.0 bit
    assert math.isclose(shannon_entropy([0.5, 0.5]), 1.0, rel_tol=1e-5)
    # Single state = 0.0 bits
    assert math.isclose(shannon_entropy([1.0]), 0.0, abs_tol=1e-5)
    # Uniform across 4 states = 2.0 bits
    assert math.isclose(shannon_entropy([0.25, 0.25, 0.25, 0.25]), 2.0, rel_tol=1e-5)
""",
                tags=["entropy", "shannon", "information", "signals", "math"],
            ),
            CrystallizedKernel(
                kernel_id="calc_tensor_bandwidth_splits",
                name="Proportional Heterogeneous Bandwidth Allocator",
                description="Computes normalized work-group allocation ratios weighted strictly by device bus bandwidth.",
                category="TENSORS",
                function_signature="compute_bandwidth_splits(devices: dict[str, float]) -> dict[str, float]",
                code="""def compute_bandwidth_splits(devices: dict[str, float]) -> dict[str, float]:
    if not devices:
        return {}
    total = sum(max(0.0, float(bw)) for bw in devices.values())
    if total == 0.0:
        equal = 1.0 / len(devices)
        return {d: equal for d in devices}
    return {d: round(max(0.0, float(bw)) / total, 6) for d, bw in devices.items()}
""",
                unit_test_code="""def test_kernel():
    res = compute_bandwidth_splits({"rtx3060": 360.0, "rx580": 224.0, "apu": 50.0})
    assert len(res) == 3
    assert math.isclose(sum(res.values()), 1.0, rel_tol=1e-4)
    assert res["rtx3060"] > res["rx580"] > res["apu"]
""",
                tags=["bandwidth", "gpu", "sharding", "tensors"],
            ),
        ]

        for k in foundational:
            cls._save_and_verify(k)

    @classmethod
    def _save_and_verify(cls, kernel: CrystallizedKernel) -> Tuple[bool, str]:
        """Writes kernel and test files, executes verification gate, and registers if valid."""
        kernel_file = KERNELS_DIR / f"{kernel.kernel_id}.py"
        test_file = TESTS_DIR / f"test_{kernel.kernel_id}.py"

        kernel_file.write_text(kernel.code, encoding="utf-8")

        test_wrapper = f"""# Autonomous verification test for {kernel.kernel_id}
import sys
import math
from pathlib import Path

# Load kernel module directly
sys.path.insert(0, r"{str(KERNELS_DIR)}")
from {kernel.kernel_id} import *

{kernel.unit_test_code}

if __name__ == '__main__':
    try:
        test_kernel()
        print('KERNEL_VERIFICATION_PASS')
    except Exception as exc:
        print(f'KERNEL_VERIFICATION_FAIL: {{exc}}', file=sys.stderr)
        sys.exit(1)
"""
        test_file.write_text(test_wrapper, encoding="utf-8")

        # Run verification in isolated subprocess
        try:
            res = subprocess.run(
                [sys.executable, str(test_file)],
                capture_output=True,
                text=True,
                timeout=8,
                cwd=str(WORKSPACE_ROOT),
            )
            if res.returncode == 0 and "KERNEL_VERIFICATION_PASS" in res.stdout:
                kernel.status = "ACTIVE"
                kernel.last_verified_at = datetime.now().isoformat()
                cls._kernels[kernel.kernel_id] = kernel
                cls._persist_registry()
                cls._load_module(kernel)
                return True, f"Kernel '{kernel.kernel_id}' verified and ratified."
            else:
                err = res.stderr or res.stdout
                kernel.status = "FAILED"
                return False, f"Verification failed:\n{err.strip()}"
        except Exception as exc:
            kernel.status = "FAILED"
            return False, f"Execution exception: {exc}"

    @classmethod
    def _load_module(cls, kernel: CrystallizedKernel) -> None:
        """Dynamically imports the ratified kernel module into execution cache."""
        try:
            kernel_path = KERNELS_DIR / f"{kernel.kernel_id}.py"
            spec = importlib.util.spec_from_file_location(kernel.kernel_id, str(kernel_path))
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                cls._loaded_modules[kernel.kernel_id] = mod
        except Exception as exc:
            logger.warning(f"Failed to dynamic-import kernel {kernel.kernel_id}: {exc}")

    @classmethod
    def _persist_registry(cls) -> None:
        """Saves current kernels metadata to registry.json."""
        try:
            data = {k_id: asdict(k) for k_id, k in cls._kernels.items()}
            REGISTRY_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception as exc:
            logger.warning(f"Failed to persist registry: {exc}")

    @classmethod
    def crystallize_skill(
        cls,
        kernel_id: str,
        name: str,
        category: str,
        description: str,
        python_code: str,
        unit_test_code: str,
        tags: Optional[List[str]] = None,
    ) -> Tuple[bool, str, Optional[CrystallizedKernel]]:
        """
        Inviolable Test-Driven Crystallization Gate:
        Compiles the candidate calculation into a pure Python kernel, executes the unit test,
        and only upon passing ratifies it into the persistent Crystallized Knowledgebase.
        """
        cls.initialize()
        clean_id = re.sub(r"[^a-zA-Z0-9_]+", "_", kernel_id.lower()).strip("_")
        if not clean_id.startswith("calc_"):
            clean_id = f"calc_{clean_id}"

        # Extract function signature via AST
        sig = "execute(*args, **kwargs)"
        try:
            tree = ast.parse(python_code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    args = [a.arg for a in node.args.args]
                    sig = f"{node.name}({', '.join(args)})"
                    break
        except Exception as e:
            return False, f"AST Syntax error in code: {e}", None

        kernel = CrystallizedKernel(
            kernel_id=clean_id,
            name=name,
            description=description,
            category=category.upper(),
            function_signature=sig,
            code=python_code,
            unit_test_code=unit_test_code,
            tags=tags or [],
        )

        ok, msg = cls._save_and_verify(kernel)
        if ok:
            logger.info(f"Successfully crystallized {clean_id}: {sig}")
            return True, msg, kernel
        else:
            logger.warning(f"Failed to crystallize {clean_id}: {msg}")
            return False, msg, None

    @classmethod
    def execute_kernel(cls, kernel_id: str, function_name: Optional[str] = None, *args, **kwargs) -> Any:
        """Direct zero-overhead deterministic calculation offload."""
        cls.initialize()
        clean_id = kernel_id if kernel_id.startswith("calc_") else f"calc_{kernel_id}"
        mod = cls._loaded_modules.get(clean_id)
        if not mod:
            raise KeyError(f"Crystallized kernel '{clean_id}' is not loaded or does not exist.")

        # Determine target function
        target_fn = None
        if function_name and hasattr(mod, function_name):
            target_fn = getattr(mod, function_name)
        else:
            # Pick first function defined in module
            for attr_name in dir(mod):
                attr = getattr(mod, attr_name)
                if inspect.isfunction(attr) and not attr_name.startswith("_"):
                    target_fn = attr
                    break

        if not target_fn:
            raise AttributeError(f"No executable function found in kernel '{clean_id}'.")

        t0 = time.perf_counter()
        result = target_fn(*args, **kwargs)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        # Update telemetry
        kernel = cls._kernels.get(clean_id)
        if kernel:
            kernel.execution_count += 1
            kernel.average_latency_ms = (kernel.average_latency_ms * (kernel.execution_count - 1) + elapsed_ms) / kernel.execution_count
            if kernel.execution_count % 10 == 0:
                cls._persist_registry()

        return result

    @classmethod
    def list_kernels(cls) -> List[Dict[str, Any]]:
        """Returns catalog of all ratified crystallized problem-solving kernels."""
        cls.initialize()
        return [
            {
                "id": k.kernel_id,
                "name": k.name,
                "category": k.category,
                "signature": k.function_signature,
                "description": k.description,
                "latency_ms": round(k.average_latency_ms, 4),
                "calls": k.execution_count,
                "status": k.status,
            }
            for k in cls._kernels.values()
        ]

    @classmethod
    def match_kernel_for_query(cls, user_query: str) -> Optional[CrystallizedKernel]:
        """Heuristically checks if a user query corresponds to an offloadable crystallized routine."""
        cls.initialize()
        q = user_query.lower()
        for kernel in cls._kernels.values():
            if kernel.status != "ACTIVE":
                continue
            for tag in kernel.tags:
                if tag in q:
                    return kernel
            for word in kernel.name.lower().split():
                if len(word) > 4 and word in q:
                    return kernel
        return None
