# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
Unit and Integration Tests for ClothOS POSIX ABI, Diagnostics & Desktop Engine (`tests/test_clothos_posix_and_diagnostics.py`).
"""

from pathlib import Path
import pytest

from loom.clothos.posix_compat import ClothOSPosixSubsystem, clothos_posix
from loom.clothos.diagnostics_and_ops import ClothOSDiagnosticsAndOps, diagnostics_ops


def test_posix_uname_and_vfs():
    uts = clothos_posix.sys_uname()
    assert uts.sysname == "ClothOS"
    assert "clothos" in uts.release.lower()
    assert "64" in uts.machine

    # Test basic builtins
    res_pwd = clothos_posix.execute_shell_command("pwd")
    assert res_pwd["exit_code"] == 0
    assert "/home/clothos" in res_pwd["stdout"]

    res_uname = clothos_posix.execute_shell_command("uname -a")
    assert "GNU/Linux" in res_uname["stdout"]
    assert "ClothOS" in res_uname["stdout"]

    res_cat = clothos_posix.execute_shell_command("cat /etc/os-release")
    assert res_cat["exit_code"] == 0
    assert "ClothOS Sovereign Linux" in res_cat["stdout"]

    res_tpu = clothos_posix.execute_shell_command("tpu-smi")
    assert "TPU-SMI" in res_tpu["stdout"]
    assert "Systolic" in res_tpu["stdout"]


def test_diagnostics_scan_and_repair():
    report = diagnostics_ops.run_full_diagnostics()
    assert report.total_checks >= 5
    assert report.health_score >= 80.0
    assert report.overall_health in ("OPTIMAL", "DEGRADED")

    # Test auto repair
    repair_res = diagnostics_ops.auto_repair_system()
    assert repair_res["remediation_executed"] is True
    assert repair_res["final_score"] >= report.health_score


def test_desktop_frontend_artifact_integrity():
    workspace = Path(__file__).resolve().parent.parent
    html_file = workspace / "deliverables" / "desktop" / "clothos_desktop.html"
    bat_file = workspace / "Launch-ClothOS-Desktop.bat"

    assert html_file.exists()
    assert html_file.stat().st_size > 5000
    content = html_file.read_text(encoding="utf-8")
    assert "clothos@sovereign:~" in content
    assert "Activity Monitor" in content
    assert "tpu-smi" in content

    assert bat_file.exists()
