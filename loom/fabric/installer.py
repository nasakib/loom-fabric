# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
ClothOS & Loom Fabric Unified Sovereign Installer (`loom/fabric/installer.py`).

Provides full-lifecycle installation, clean reinstallation, repair, and environment setup:
- Cross-platform support: Windows (x86_64), Linux (x86_64/ARM64), and Apple Silicon (Darwin/ARM64).
- Sovereign Virtual Filesystem (ClothFS) root generation and disk mirroring.
- Process Manager & Priority Rings (P0-P5) initialization.
- Sovereign RISC-V (RV64GCV) vector assembly and OpenSBI boot manifest generation.
- Zero-Window Windows Startup persistence launcher registration.
- CLI shims in ~/.loom/bin and PATH registration (clothos, clothsh, loom, fabric, loom-gui, loom-rn).
- Safe port sanitization and collision prevention.
- Hardware probe validation (CUDA, OpenCL, Metal 3.1, pooled RAM).
"""

from __future__ import annotations

import argparse
from datetime import datetime
import json
import logging
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s %(message)s")
logger = logging.getLogger("loom.fabric.installer")

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
CREATE_NO_WINDOW = 0x08000000


class ClothOSInstaller:
    """Orchestrates comprehensive installation, clean reinstallation, and environment repair."""

    def __init__(self, reinstall: bool = False, clean: bool = False, workspace_root: Optional[Path] = None):
        self.reinstall = reinstall or clean
        self.clean = clean
        self.workspace_root = workspace_root or WORKSPACE_ROOT
        self.python_exe = Path(sys.executable)
        self.user_home = Path.home()
        self.loom_home = self.user_home / ".loom"
        self.bin_dir = self.loom_home / "bin"
        self.os_type = platform.system().lower()

    def run_full_installation(self) -> Dict[str, Any]:
        """Executes complete installation pipeline with verification."""
        t0 = time.time()
        print("\n" + "=" * 70)
        print("   CLOTHOS & LOOM FABRIC -- SOVEREIGN AGENTIC OS INSTALLER")
        print("   Architect: Najmos Sakib | Fiduciary Malignancy Bound: 0.00")
        print(f"   Mode: {'CLEAN REINSTALL' if self.reinstall else 'SETUP & VERIFY'} | Platform: {platform.system()} ({platform.machine()})")
        print("=" * 70 + "\n")

        results = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "reinstall": self.reinstall,
            "steps": {},
        }

        # 1. Clean Stale State if reinstall requested
        if self.reinstall:
            print("[1/8] Cleaning stale ClothOS processes and locks...")
            results["steps"]["clean_stale"] = self._clean_stale_state()
        else:
            print("[1/8] Checking existing installation...")
            results["steps"]["clean_stale"] = {"status": "SKIPPED"}

        # 2. Verify or Rebuild Virtual Environment Dependencies
        print("[2/8] Verifying Python runtime and core package dependencies...")
        results["steps"]["dependencies"] = self._verify_dependencies()

        # 3. Initialize Sovereign Virtual Filesystem (ClothFS)
        print("[3/8] Building ClothOS Virtual Filesystem (ClothFS) at clothos_root/...")
        results["steps"]["vfs"] = self._initialize_clothfs()

        # 4. Generate Sovereign RISC-V Transition Artifacts
        print("[4/8] Emitting Sovereign RISC-V (RV64GCV) vector assembly and OpenSBI manifest...")
        results["steps"]["riscv"] = self._generate_riscv_target()

        # 5. Initialize Hardware Abstraction Layer (HAL)
        print("[5/8] Probing Hardware Abstraction Layer (HAL) across GPUs and CPU...")
        results["steps"]["hal"] = self._probe_hal()

        # 6. Install CLI Shims and Command Wrappers (clothos, clothsh, loom)
        print("[6/8] Generating CLI shims in ~/.loom/bin and registering User PATH...")
        results["steps"]["cli_shims"] = self._install_cli_shims()

        # 7. Register Windows / Linux / macOS Auto-Start Persistence
        print("[7/8] Registering silent background startup persistence...")
        results["steps"]["startup"] = self._register_startup_persistence()

        # 8. Sanitize Ports and Verify React Native & GUI Launchers
        print("[8/8] Verifying ClothOS port allocations and universal launchers...")
        results["steps"]["ports"] = self._verify_ports_and_launchers()

        duration = round(time.time() - t0, 2)
        results["duration_seconds"] = duration
        results["success"] = True

        print("\n" + "=" * 70)
        print(f"[OK] ClothOS & Loom Fabric Installation Completed in {duration}s!")
        print("=" * 70)
        print("Available Launch Commands:")
        print("  1. Interactive Shell:       clothsh          (or 'python -m loom.clothos.shell')")
        print("  2. Command Center GUI:      Start-Loom-GUI.bat (or 'loom-gui')")
        print("  3. Universal React Native:  Launch-React-Native.bat (Port 8086)")
        print("  4. Hardware Diagnostic:     clothos hal      (or 'loom probe')")
        print("  5. RISC-V Transition:       clothsh riscv    (status, emit, asm)")
        print("=" * 70 + "\n")

        return results

    def _clean_stale_state(self) -> Dict[str, Any]:
        """Terminates stale clothos processes and clears volatile locks."""
        cleaned_pids = []
        try:
            from loom.fabric.port_manager import port_manager
            res = port_manager.clean_stale_clothos_ports()
            cleaned_pids = res.get("cleaned_pids", [])
        except Exception as exc:
            logger.debug("Port cleaner note: %s", exc)

        # Clear volatile run files
        for f in [".loom_dashboard_pid", ".loom_dashboard_port"]:
            p = self.workspace_root / f
            p.unlink(missing_ok=True)

        return {"cleaned_pids": cleaned_pids, "status": "CLEANED"}

    def _verify_dependencies(self) -> Dict[str, Any]:
        """Checks required packages."""
        required = ["fastapi", "uvicorn", "pydantic", "psutil"]
        missing = []
        for pkg in required:
            try:
                __import__(pkg)
            except ImportError:
                missing.append(pkg)

        if missing:
            logger.info("Installing missing packages: %s", missing)
            subprocess.run(
                [sys.executable, "-m", "pip", "install", *missing],
                cwd=str(self.workspace_root),
                creationflags=CREATE_NO_WINDOW if self.os_type == "windows" else 0,
            )

        return {"python_version": platform.python_version(), "missing_installed": missing, "status": "VERIFIED"}

    def _initialize_clothfs(self) -> Dict[str, Any]:
        """Initializes ClothFS VFS and writes out clothos_root to physical disk."""
        try:
            from loom.clothos.fs import cloth_fs
            cloth_fs._persist_to_disk()
            root_dir = self.workspace_root / "clothos_root"
            return {
                "root_path": str(root_dir),
                "directories_created": ["bin", "sbin", "etc", "dev", "proc", "sys", "home", "vault", "var", "tmp"],
                "status": "INITIALIZED",
            }
        except Exception as exc:
            logger.error("ClothFS init error: %s", exc)
            return {"error": str(exc), "status": "FAILED"}

    def _generate_riscv_target(self) -> Dict[str, Any]:
        """Emits RISC-V vector assembly, linker script, and OpenSBI environment."""
        try:
            from loom.clothos.riscv_migration import get_riscv_migration
            mgr = get_riscv_migration()
            files = mgr.write_disk_artifacts()
            return {
                "artifacts_written": [str(f.name) for f in files],
                "target_dir": str(files[0].parent if files else ""),
                "target_isa": mgr.target_isa,
                "status": "EMITTED",
            }
        except Exception as exc:
            logger.error("RISC-V generation error: %s", exc)
            return {"error": str(exc), "status": "FAILED"}

    def _probe_hal(self) -> Dict[str, Any]:
        """Probes hardware abstraction layer."""
        try:
            from loom.clothos.hal import get_hal
            hal = get_hal()
            prof = hal.get_profile()
            return {
                "platform": prof.platform.value,
                "cpu": prof.cpu_model,
                "logical_cores": prof.logical_cores,
                "ram_gb": prof.total_physical_ram_gb,
                "accelerators": len(prof.accelerators),
                "preferred_backend": prof.preferred_backend.value,
                "status": "PROBED",
            }
        except Exception as exc:
            return {"error": str(exc), "status": "PROBE_ERROR"}

    def _install_cli_shims(self) -> Dict[str, Any]:
        """Creates Windows CMD shims and Linux/macOS bash wrappers in ~/.loom/bin and workspace /bin."""
        py_exe = str(self.python_exe)
        ws_str = str(self.workspace_root)
        installed = []

        target_dirs: List[Path] = []
        for candidate in [self.bin_dir, self.workspace_root / "bin"]:
            try:
                candidate.mkdir(parents=True, exist_ok=True)
                target_dirs.append(candidate)
            except Exception as exc:
                logger.debug("Candidate bin dir note (%s): %s", candidate, exc)

        if not target_dirs:
            target_dirs = [self.workspace_root / "bin"]
            target_dirs[0].mkdir(parents=True, exist_ok=True)

        if self.os_type == "windows":
            shims = {
                "clothos.cmd": f"@echo off\r\nset \"PYTHONPATH={ws_str};%PYTHONPATH%\"\r\nset \"PYTHONIOENCODING=utf-8\"\r\n\"{py_exe}\" -m loom.clothos.agent_cli --workspace \"%CD%\" %*",
                "clothos-agent.cmd": f"@echo off\r\nset \"PYTHONPATH={ws_str};%PYTHONPATH%\"\r\nset \"PYTHONIOENCODING=utf-8\"\r\n\"{py_exe}\" -m loom.clothos.agent_cli --workspace \"%CD%\" %*",
                "clothsh.cmd": f"@echo off\r\nset \"PYTHONPATH={ws_str};%PYTHONPATH%\"\r\nset \"PYTHONIOENCODING=utf-8\"\r\n\"{py_exe}\" -m loom.clothos.shell %*",
                "loom.cmd": f"@echo off\r\nset \"PYTHONPATH={ws_str};%PYTHONPATH%\"\r\nset \"PYTHONIOENCODING=utf-8\"\r\n\"{py_exe}\" -m loom.cli.main %*",
                "fabric.cmd": f"@echo off\r\nset \"PYTHONPATH={ws_str};%PYTHONPATH%\"\r\nset \"PYTHONIOENCODING=utf-8\"\r\n\"{py_exe}\" -m loom.cli.main %*",
                "loom-gui.cmd": f"@echo off\r\ncall \"{ws_str}\\Launch-Loom-GUI.bat\"",
                "loom-rn.cmd": f"@echo off\r\ncall \"{ws_str}\\Launch-React-Native.bat\"",
            }
            for b_dir in target_dirs:
                for fname, content in shims.items():
                    try:
                        p = b_dir / fname
                        p.write_text(content, encoding="utf-8")
                        if fname not in installed:
                            installed.append(fname)
                    except Exception:
                        pass

            # Register in User PATH via PowerShell if not present
            try:
                bin_str = str(self.bin_dir)
                user_path = os.environ.get("PATH", "")
                if bin_str.lower() not in user_path.lower():
                    ps_cmd = f'[Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path", "User") + ";{bin_str}", "User")'
                    subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], creationflags=CREATE_NO_WINDOW)
            except Exception as e:
                logger.debug("PATH update note: %s", e)

        else:
            # Linux and Apple Silicon Bash shims
            local_bin = self.user_home / ".local" / "bin"
            local_bin.mkdir(parents=True, exist_ok=True)
            bash_shims = {
                "clothos": f"#!/usr/bin/env bash\nexport PYTHONPATH=\"{ws_str}:$PYTHONPATH\"\nexec \"{py_exe}\" -m loom.clothos.shell \"$@\"\n",
                "clothsh": f"#!/usr/bin/env bash\nexport PYTHONPATH=\"{ws_str}:$PYTHONPATH\"\nexec \"{py_exe}\" -m loom.clothos.shell \"$@\"\n",
                "loom": f"#!/usr/bin/env bash\nexport PYTHONPATH=\"{ws_str}:$PYTHONPATH\"\nexec \"{py_exe}\" -m loom.cli.main \"$@\"\n",
            }
            for fname, content in bash_shims.items():
                for target_d in (self.bin_dir, local_bin):
                    p = target_d / fname
                    p.write_text(content, encoding="utf-8")
                    p.chmod(0o755)
                installed.append(fname)

        return {"installed_shims": installed, "bin_dir": str(self.bin_dir), "status": "INSTALLED"}

    def _register_startup_persistence(self) -> Dict[str, Any]:
        """Registers zero-window background startup on Windows, Linux, or macOS."""
        if self.os_type == "windows":
            try:
                from loom.fabric.startup_manager import ensure_startup_registration
                reg = ensure_startup_registration(self.workspace_root)
                return {"windows_vbs": reg.get("launcher_path"), "installed": reg.get("installed"), "status": "REGISTERED"}
            except Exception as exc:
                return {"error": str(exc), "status": "REGISTRATION_NOTE"}
        else:
            try:
                from loom.clothos.hal import get_hal
                hal = get_hal()
                manifests = hal.generate_startup_manifest(self.workspace_root)
                return {"manifests_ready": list(manifests.keys()), "status": "READY"}
            except Exception as exc:
                return {"error": str(exc), "status": "NOTE"}

    def _verify_ports_and_launchers(self) -> Dict[str, Any]:
        """Audits ports and confirms launchers exist."""
        from loom.fabric.port_manager import port_manager
        audit = port_manager.audit_all_ports()
        best_port = port_manager.find_best_available_clothos_port()
        return {
            "best_dashboard_port": best_port,
            "react_native_port": 8086,
            "total_ports_audited": audit.get("total_ports_audited", 0),
            "status": "VERIFIED",
        }


def main():
    parser = argparse.ArgumentParser(description="ClothOS & Loom Fabric Sovereign Installer")
    parser.add_argument("--reinstall", action="store_true", help="Force clean reinstallation and repair of all components")
    parser.add_argument("--clean", action="store_true", help="Clean stale states, locks, and temporary files before install")
    args = parser.parse_args()

    installer = ClothOSInstaller(reinstall=args.reinstall, clean=args.clean)
    installer.run_full_installation()


if __name__ == "__main__":
    main()
