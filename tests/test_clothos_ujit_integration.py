"""
ClothOS Universal JIT Integration Verification Suite
Tests native kernel execution, shell commands, and stateful session integration.
"""

import sys
from pathlib import Path

# Add loom-fabric workspace to sys.path
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from loom.clothos.ujit_engine import ClothOSJITKernelEngine, clothos_jit
from loom.clothos.shell import ClothOSShell
from loom.clothos.code_interpreter import StatefulPythonSession


def test_clothos_jit_kernels():
    print("[1] Testing ClothOS Pre-compiled Native Kernels...")
    # Grid arbitrage
    off_peak = clothos_jit.dispatch("grid_arbitrage", 1000, 15, 1)
    day_peak = clothos_jit.dispatch("grid_arbitrage", 1000, 15, 0)
    assert off_peak == 9750, f"Expected 9750, got {off_peak}"
    assert day_peak == 17250, f"Expected 17250, got {day_peak}"
    print(f"  * grid_arbitrage: off_peak={off_peak}, day_peak={day_peak} [PASS]")

    # Kuramoto phase step
    next_phase = clothos_jit.dispatch("kuramoto_phase_step", 1000, 20, 50, 10)
    # influence = (50 * 10) / 100 = 5; 1000 + 20 + 5 = 1025
    assert next_phase == 1025, f"Expected 1025, got {next_phase}"
    print(f"  * kuramoto_phase_step: next_phase={next_phase} [PASS]")

    # Ternary MAC
    acc1 = clothos_jit.dispatch("ternary_mac", 100, 1, 42)
    acc2 = clothos_jit.dispatch("ternary_mac", 100, -1, 42)
    acc3 = clothos_jit.dispatch("ternary_mac", 100, 0, 42)
    assert acc1 == 142 and acc2 == 58 and acc3 == 100
    print(f"  * ternary_mac: acc(+1)={acc1}, acc(-1)={acc2}, acc(0)={acc3} [PASS]")


def test_clothos_shell_ujit():
    print("\n[2] Testing ClothOS Shell 'ujit' Builtin Command...")
    shell = ClothOSShell()

    # ujit list
    res_list = shell.execute("ujit list")
    assert res_list.exit_code == 0
    assert "grid_arbitrage" in res_list.stdout
    assert "kuramoto_phase_step" in res_list.stdout
    print("  * 'ujit list' output:\n" + "    " + res_list.stdout.replace("\n", "\n    ").strip())

    # ujit eval
    res_eval = shell.execute('ujit eval "fn multiply(a: int, b: int) -> int { return a * b }" multiply 7 8')
    assert res_eval.exit_code == 0
    assert "56" in res_eval.stdout
    print(f"  * 'ujit eval': result={res_eval.stdout.strip()} [PASS]")

    # ujit bench
    res_bench = shell.execute("ujit bench grid_arbitrage 100000")
    assert res_bench.exit_code == 0
    assert "Throughput:" in res_bench.stdout
    print("  * 'ujit bench' output:\n" + "    " + res_bench.stdout.replace("\n", "\n    ").strip())


def test_code_interpreter_session():
    print("\n[3] Testing Stateful Python Session with JIT...")
    session = StatefulPythonSession()
    code = """
kernel = clothos_jit.compile_kernel("custom_harmonic", '''
fn custom_harmonic(freq: int, phase: int) -> int {
    return (freq * 12 + phase) % 3072
}
''')
result = kernel(100, 40)
"""
    res = session.execute(code)
    assert res["success"] is True, f"Execution failed: {res.get('error')}"
    assert session.globals.get("result") == (100 * 12 + 40) % 3072
    print(f"  * Stateful session result: {session.globals.get('result')} [PASS]")


if __name__ == "__main__":
    print("=== ClothOS Universal JIT Integration Test Suite ===\n")
    test_clothos_jit_kernels()
    test_clothos_shell_ujit()
    test_code_interpreter_session()
    print("\n>>> All ClothOS Universal JIT integration tests passed successfully! <<<")
