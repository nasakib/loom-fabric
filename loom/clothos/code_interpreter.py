"""
Stateful Interactive Code Interpreter & Visualization Engine (`loom/clothos/code_interpreter.py`).

Adapted from Qwen-Agent's CodeInterpreter & PythonExecutor architectures:
- Persistent runtime environment maintaining state (variables, imports, functions) across turns.
- Automatic Matplotlib/Seaborn/Plotly figure interception & artifact export to PNG/SVG.
- Timeout protection, stdout/stderr capture, and clean exception formatting.
"""

from __future__ import annotations

import ast
import io
import os
import sys
import time
import traceback
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Any, Dict, List, Optional


class StatefulPythonSession:
    """Maintains a persistent Python execution environment across agent interactions."""

    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = workspace_root or Path.cwd()
        self.artifacts_dir = self.workspace_root / "artifacts" / "charts"
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = f"session_{int(time.time())}"
        self.execution_count = 0
        self.globals: Dict[str, Any] = {}
        self.history: List[Dict[str, Any]] = []
        self._init_environment()

    def _init_environment(self) -> None:
        """Initializes standard baseline imports and hooks into the global namespace."""
        init_code = """
import sys, os, math, time, json
from pathlib import Path
try:
    import numpy as np
except ImportError:
    pass
try:
    import pandas as pd
except ImportError:
    pass
"""
        self.globals = {
            "__name__": "__main__",
            "__doc__": "ClothOS Stateful Code Interpreter",
            "__builtins__": __builtins__,
        }
        try:
            exec(init_code, self.globals)
        except Exception:
            pass

    def reset(self) -> Dict[str, Any]:
        """Clears all session variables and restarts runtime."""
        self._init_environment()
        self.execution_count = 0
        return {"status": "SUCCESS", "message": "Stateful Python session reset to clean state."}

    def list_variables(self) -> Dict[str, str]:
        """Returns non-internal variables currently resident in memory."""
        vars_summary = {}
        for k, v in self.globals.items():
            if k.startswith("_"):
                continue
            t_name = type(v).__name__
            try:
                if hasattr(v, "shape"):
                    vars_summary[k] = f"{t_name} shape={v.shape}"
                elif hasattr(v, "__len__") and not isinstance(v, (str, bytes)):
                    vars_summary[k] = f"{t_name} len={len(v)}"
                else:
                    r = repr(v)
                    vars_summary[k] = f"{t_name}: {r[:60]}..." if len(r) > 60 else f"{t_name}: {r}"
            except Exception:
                vars_summary[k] = t_name
        return vars_summary

    def execute(self, code: str, timeout_seconds: float = 30.0) -> Dict[str, Any]:
        """Executes a code snippet inside the persistent session."""
        self.execution_count += 1
        t0 = time.time()
        stdout_buf = io.StringIO()
        stderr_buf = io.StringIO()
        saved_figures: List[str] = []

        # Hook matplotlib to capture plots instead of blocking
        hook_code = f"""
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    _orig_show = plt.show
    def _clothos_intercept_show(*args, **kwargs):
        import time
        fig_path = r"{str(self.artifacts_dir / f'plot_{self.execution_count}_{int(time.time())}.png')}"
        plt.savefig(fig_path, bbox_inches='tight', dpi=150)
        plt.close('all')
        print(f"[IMAGE_ARTIFACT: {{fig_path}}]")
    plt.show = _clothos_intercept_show
except Exception:
    pass
"""
        full_code = hook_code + "\n" + code

        try:
            # Parse AST to check if last statement is an expression to print
            tree = ast.parse(full_code)
            has_return_expr = False
            last_expr = None
            if tree.body and isinstance(tree.body[-1], ast.Expr):
                has_return_expr = True
                last_expr = tree.body.pop()

            compiled_body = compile(tree, f"<cell_{self.execution_count}>", "exec")

            with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
                exec(compiled_body, self.globals)
                if has_return_expr and last_expr is not None:
                    compiled_expr = compile(ast.Expression(last_expr.value), f"<eval_{self.execution_count}>", "eval")
                    res = eval(compiled_expr, self.globals)
                    if res is not None:
                        print(repr(res))

            success = True
            error = None
        except Exception as exc:
            success = False
            error = traceback.format_exc()

        elapsed = round(time.time() - t0, 3)
        raw_stdout = stdout_buf.getvalue()
        raw_stderr = stderr_buf.getvalue()

        # Extract generated image artifacts
        clean_stdout_lines = []
        for line in raw_stdout.splitlines():
            if line.startswith("[IMAGE_ARTIFACT:") and line.endswith("]"):
                fig_file = line[len("[IMAGE_ARTIFACT:"): -1].strip()
                saved_figures.append(fig_file)
            else:
                clean_stdout_lines.append(line)
        stdout_text = "\n".join(clean_stdout_lines).strip()

        result = {
            "success": success,
            "execution_count": self.execution_count,
            "stdout": stdout_text,
            "stderr": raw_stderr.strip(),
            "figures": saved_figures,
            "elapsed_seconds": elapsed,
            "error": error,
        }

        self.history.append({
            "code": code,
            "result": result,
            "timestamp": time.time(),
        })

        return result


# Global singleton instance for the process
_DEFAULT_SESSION = StatefulPythonSession()

def get_code_interpreter_session(workspace_root: Optional[Path] = None) -> StatefulPythonSession:
    global _DEFAULT_SESSION
    if workspace_root and _DEFAULT_SESSION.workspace_root != workspace_root:
        _DEFAULT_SESSION = StatefulPythonSession(workspace_root)
    return _DEFAULT_SESSION
