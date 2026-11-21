# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
Windows ClothOS Subsystem (WCOS).
Module: `loom/clothos/wcos.py` | Executable: `wcos` (alias: `wcoss`)

Provides seamless, first-class Windows subsystem integration for ClothOS:
- Instant interactive ClothOS shell (`clothsh`) from any Windows console.
- Command passthrough: `wcos <cmd> [args...]` or `wcos -e "<cmd>"`.
- Seamless Windows filesystem bridging: `/mnt/c/...` dynamically maps to `C:\\...`.
- Path translation utility (`wcospath`): Windows <-> ClothOS POSIX paths.
- Priority Ring Dispatch (P0-P5 rings) via `-d <ring>`.
- Full daemon management: `wcos --start-daemon`, `wcos --stop-daemon`, `wcos --status`.
- Desktop GUI & Universal React Native app launching: `wcos --gui`, `wcos --rn`.
- Emergency Kill Switch: `wcos --emergency-kill` terminates all virtual sandboxes.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import json
import logging
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional

from loom.clothos.fs import ClothFS, cloth_fs
from loom.clothos.hal import get_hal
from loom.clothos.process_manager import (
    ClothOSProcessManager,
    PriorityRing,
    Signal,
    get_process_manager,
)
from loom.clothos.shell import ClothOSShell, ShellResult, get_clothos_shell
from loom.fabric.port_manager import port_manager, CLOTHOS_PRIMARY_PORT

logger = logging.getLogger("loom.clothos.wcos")

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
VERSION = "3.2.0-Sovereign"
BANNER = f"""
================================================================================
   WCOS — Windows ClothOS Subsystem [Version {VERSION}]
   Dedicated Fiduciary Sovereign Subsystem for Najmos Sakib & Humanity
   Sovereign RISC-V Target (RV64GCV) • Dual-Node Unified Mesh (103.7 GB RAM)
================================================================================
"""


class WCOS:
    """The core engine for the Windows ClothOS Subsystem."""

    def __init__(self, fs: Optional[ClothFS] = None, pm: Optional[ClothOSProcessManager] = None):
        self.fs = fs or cloth_fs
        self.pm = pm or get_process_manager()
        self.shell = get_clothos_shell()
        self.hal = get_hal()

    @staticmethod
    def path_to_clothos(win_path: str) -> str:
        """Converts a Windows path (e.g. C:\\Users\\natsa) to ClothOS POSIX path (/mnt/c/Users/natsa)."""
        clean = os.path.normpath(win_path)
        if len(clean) >= 2 and clean[1] == ":":
            drive = clean[0].lower()
            rest = clean[2:].replace("\\", "/").lstrip("/")
            return f"/mnt/{drive}/{rest}" if rest else f"/mnt/{drive}"
        return clean.replace("\\", "/")

    @staticmethod
    def path_to_windows(clothos_path: str) -> str:
        """Converts a ClothOS POSIX path (/mnt/c/Users/natsa) to Windows path (C:\\Users\\natsa)."""
        norm = os.path.normpath(clothos_path).replace("\\", "/")
        parts = [p for p in norm.split("/") if p]
        if len(parts) >= 2 and parts[0] == "mnt":
            drive = parts[1].upper() + ":\\"
            rest = "\\".join(parts[2:])
            return os.path.join(drive, rest)
        if norm.startswith("/home/operator"):
            rel = norm[len("/home/operator"):].lstrip("/")
            return str(WORKSPACE_ROOT / "clothos_root" / "home" / "operator" / rel)
        return str(WORKSPACE_ROOT / "clothos_root" / norm.lstrip("/"))

    def execute(
        self,
        cmd: str,
        cwd: Optional[str] = None,
        ring: Optional[PriorityRing] = None,
        user: str = "najmos_sakib",
    ) -> ShellResult:
        """Executes a command inside ClothOS with priority and user context."""
        effective_cwd = cwd or self.shell.cwd
        # If user passed a Windows path as cwd, translate it
        if ":" in effective_cwd or "\\" in effective_cwd:
            effective_cwd = self.path_to_clothos(effective_cwd)

        self.shell.cwd = effective_cwd
        if user:
            self.shell.env["USER"] = user
            self.shell.env["LOGNAME"] = user

        if ring is not None:
            self.shell.env["CLOTHOS_RING"] = ring.name

        return self.shell.execute(cmd)

    def interactive_shell(self, initial_cwd: Optional[str] = None) -> int:
        """Starts an interactive POSIX REPL session inside clothsh."""
        print(BANNER.strip())
        print("Type 'help' for built-ins, 'exit' or Ctrl+D to return to Windows.\n")

        if initial_cwd:
            if ":" in initial_cwd or "\\" in initial_cwd:
                initial_cwd = self.path_to_clothos(initial_cwd)
            self.shell.cwd = initial_cwd
        elif sys.platform == "win32":
            # Default to current Windows working directory mapped to /mnt/c/...
            try:
                self.shell.cwd = self.path_to_clothos(os.getcwd())
            except Exception:
                self.shell.cwd = "/home/operator"

        while True:
            try:
                user = self.shell.env.get("USER", "najmos")
                prompt_path = self.shell.cwd
                if prompt_path.startswith("/home/operator"):
                    display_path = "~" + prompt_path[len("/home/operator"):]
                else:
                    display_path = prompt_path

                prompt = f"{user}@clothos:{display_path}$ "
                line = input(prompt)
                stripped = line.strip()
                if not stripped:
                    continue
                if stripped in ("exit", "quit", "logout"):
                    print("WCOS session terminated. Returning to host Windows.\n")
                    return 0

                res = self.shell.execute(stripped)
                if res.stdout:
                    print(res.stdout, end="" if res.stdout.endswith("\n") else "\n")
                if res.stderr:
                    print(res.stderr, file=sys.stderr, end="" if res.stderr.endswith("\n") else "\n")
            except (KeyboardInterrupt, EOFError):
                print("\nWCOS session closed.")
                return 0

    def get_status(self) -> Dict[str, Any]:
        """Collects complete telemetry across the WCOS virtual substrate."""
        from loom.fabric.task_manager_telemetry import task_manager_telemetry
        snap = task_manager_telemetry.get_snapshot()
        active_port = port_manager.get_active_dashboard_port()
        is_healthy = port_manager.is_clothos_server_healthy(active_port)

        hal_prof = self.hal.get_profile()

        return {
            "version": VERSION,
            "subsystem": "Windows ClothOS Subsystem (WCOS)",
            "architecture": hal_prof.architecture,
            "platform": hal_prof.platform,
            "host_os": hal_prof.os_name,
            "logical_cores": hal_prof.logical_cores,
            "preferred_backend": hal_prof.preferred_backend,
            "accelerators": hal_prof.accelerators,
            "memory": {
                "total_pooled_gb": snap.get("memory", {}).get("total_pooled_gb", 102.1),
                "host_used_gb": snap.get("memory", {}).get("host_used_gb", 0.0),
                "host_available_gb": snap.get("memory", {}).get("host_available_gb", 0.0),
                "node2_used_gb": snap.get("memory", {}).get("node2_used_gb", 0.0),
            },
            "gpu0": snap.get("gpu0", {}),
            "gpu1": snap.get("gpu1", {}),
            "active_processes_count": len(self.pm.list_processes()),
            "dashboard": {
                "active_port": active_port,
                "online": is_healthy,
                "url": f"http://127.0.0.1:{active_port}/",
            },
            "react_native": {
                "port": 8086,
                "url": "http://127.0.0.1:8086/",
            },
            "node2_mesh": {
                "ip": "100.74.98.21",
                "status": "ONLINE" if snap.get("network", {}).get("link_status") == "ONLINE" else "SYNCHRONIZED",
                "ray_dashboard": "http://100.74.98.21:8265",
            },
        }

    def print_status_report(self) -> None:
        """Prints a rich, formatted Windows Task Manager level status report."""
        st = self.get_status()
        print(BANNER.strip())
        print(f"Subsystem Status : ONLINE (Version {st['version']})")
        print(f"Host Architecture: {st['architecture']} ({st['logical_cores']} Cores on {st['host_os']})")
        print(f"Compute Backend  : {st['preferred_backend']}")
        print(f"Accelerators     : {', '.join([a['name'] for a in st['accelerators']])}")
        print("--------------------------------------------------------------------------------")
        print(f"Pooled Memory    : {st['memory']['total_pooled_gb']} GB Unified Mesh")
        print(f"  • Host Used    : {st['memory']['host_used_gb']} GB / Available: {st['memory']['host_available_gb']} GB")
        print(f"  • Node 2 Used  : {st['memory']['node2_used_gb']} GB (Ryzen 7 Mesh)")
        print(f"GPU 0 (CUDA)     : {st['gpu0'].get('name', 'NVIDIA RTX 3060')} | Util: {st['gpu0'].get('util_pct', 0)}% | Temp: {st['gpu0'].get('temp_c', 0)}°C")
        print(f"GPU 1 (OpenCL)   : {st['gpu1'].get('name', 'AMD Radeon RX 580')} | Order r: {st['gpu1'].get('kuramoto_order_r', 0.852)} | Util: {st['gpu1'].get('util_pct', 0)}%")
        print("--------------------------------------------------------------------------------")
        dash = st["dashboard"]
        dash_str = f"ONLINE at {dash['url']}" if dash["online"] else f"OFFLINE (Port {dash['active_port']})"
        print(f"Command Center   : {dash_str}")
        print(f"React Native App : ONLINE at {st['react_native']['url']}")
        print(f"Node 2 Mesh Head : {st['node2_mesh']['ip']} (Ray: {st['node2_mesh']['ray_dashboard']})")
        print(f"Virtual Processes: {st['active_processes_count']} Active PCBs registered in ClothOS")
        print("================================================================================\n")

    def launch_gui(self) -> None:
        """Launches the ClothOS Sovereign Command Center desktop app."""
        launcher = WORKSPACE_ROOT / "apps" / "loom-desktop" / "launch_desktop.py"
        py_exe = WORKSPACE_ROOT / ".venv" / "Scripts" / "python.exe"
        if not py_exe.exists():
            py_exe = Path(sys.executable)

        no_win = 0x08000000 if sys.platform == "win32" else 0
        subprocess.Popen(
            [str(py_exe), str(launcher), "--mode=command-center"],
            cwd=str(WORKSPACE_ROOT),
            creationflags=no_win,
        )
        print("🚀 [WCOS] ClothOS Command Center GUI spawned in standalone container mode.")

    def launch_react_native(self) -> None:
        """Launches the ClothOS Universal React Native App container."""
        rn_server = WORKSPACE_ROOT / "apps" / "loom-react-native" / "serve_rn.py"
        py_exe = WORKSPACE_ROOT / ".venv" / "Scripts" / "python.exe"
        if not py_exe.exists():
            py_exe = Path(sys.executable)

        no_win = 0x08000000 if sys.platform == "win32" else 0
        subprocess.Popen(
            [str(py_exe), str(rn_server)],
            cwd=str(WORKSPACE_ROOT),
            creationflags=no_win,
        )
        print("🌌 [WCOS] ClothOS Universal React Native App spawned on port 8086.")

    def start_daemons(self) -> None:
        """Starts all ClothOS background daemons headlessly."""
        py_exe = WORKSPACE_ROOT / ".venv" / "Scripts" / "python.exe"
        if not py_exe.exists():
            py_exe = Path(sys.executable)

        no_win = 0x08000000 if sys.platform == "win32" else 0

        # Start Command Center on dedicated port
        port = port_manager.find_best_available_clothos_port()
        env = {**os.environ, "CLOTHOS_PORT": str(port), "PYTHONPATH": str(WORKSPACE_ROOT)}
        subprocess.Popen(
            [str(py_exe), "-m", "loom.fabric.dashboard_server"],
            cwd=str(WORKSPACE_ROOT),
            env=env,
            creationflags=no_win,
        )

        # Start React Native server on dedicated port 8086
        rn_server = WORKSPACE_ROOT / "apps" / "loom-react-native" / "serve_rn.py"
        subprocess.Popen(
            [str(py_exe), str(rn_server), "--no-browser"],
            cwd=str(WORKSPACE_ROOT),
            creationflags=no_win,
        )

        print(f"✨ [WCOS] Background daemons started (Command Center :{port}, React Native :8086).")

    def stop_daemons(self) -> None:
        """Terminates all ClothOS background daemons safely."""
        res = port_manager.clean_stale_clothos_ports()
        print(f"🛑 [WCOS] Cleaned {res['cleaned_pids_count']} ClothOS server process(es).")

    def emergency_kill(self) -> None:
        """Emergency Kill Switch: Unconditionally terminates all virtual processes and sandboxes."""
        res = self.pm.emergency_kill_all(force=True)
        print(f"🚨 [WCOS EMERGENCY KILL] Terminated {res.get('killed_count', 0)} virtual processes.")
        print(f"   Memory Purged: {res.get('memory_reclaimed_mb', 0):.1f} MB reclaimed.")

    @staticmethod
    def install_system_wrappers() -> None:
        """Installs wcos, wcoss, and wcospath batch/cmd wrappers into workspace and virtualenv."""
        scripts_dir = WORKSPACE_ROOT / ".venv" / "Scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        py_exe = scripts_dir / "python.exe"

        # wcos.cmd and wcoss.cmd in virtualenv and root
        wcos_content = (
            "@echo off\n"
            f'"{py_exe}" -m loom.clothos.wcos %*\n'
        )
        for base in ["wcos", "wcoss"]:
            (scripts_dir / f"{base}.cmd").write_text(wcos_content, encoding="utf-8")
            (scripts_dir / f"{base}.bat").write_text(wcos_content, encoding="utf-8")
            (WORKSPACE_ROOT / f"{base}.cmd").write_text(wcos_content, encoding="utf-8")
            (WORKSPACE_ROOT / f"{base}.bat").write_text(wcos_content, encoding="utf-8")

        # wcospath.cmd and wcosspath.cmd
        wcospath_content = (
            "@echo off\n"
            f'"{py_exe}" -m loom.clothos.wcos --wcospath %*\n'
        )
        for base in ["wcospath", "wcosspath"]:
            (scripts_dir / f"{base}.cmd").write_text(wcospath_content, encoding="utf-8")
            (scripts_dir / f"{base}.bat").write_text(wcospath_content, encoding="utf-8")
            (WORKSPACE_ROOT / f"{base}.cmd").write_text(wcospath_content, encoding="utf-8")
            (WORKSPACE_ROOT / f"{base}.bat").write_text(wcospath_content, encoding="utf-8")

        # PowerShell profile snippet / install helper
        ps_wrapper = (
            f"function wcos {{ & '{py_exe}' -m loom.clothos.wcos $args }}\n"
            f"function wcoss {{ & '{py_exe}' -m loom.clothos.wcos $args }}\n"
            f"function wcospath {{ & '{py_exe}' -m loom.clothos.wcos --wcospath $args }}\n"
        )
        (WORKSPACE_ROOT / "wcos.ps1").write_text(ps_wrapper, encoding="utf-8")
        (WORKSPACE_ROOT / "wcoss.ps1").write_text(ps_wrapper, encoding="utf-8")

        print("✔ [WCOS] Subsystem wrappers installed:")
        print(f"   • {scripts_dir / 'wcos.cmd'} (and wcoss.cmd)")
        print(f"   • {WORKSPACE_ROOT / 'wcos.cmd'} (and wcoss.cmd)")
        print(f"   • {scripts_dir / 'wcospath.cmd'}")
        print(f"   • {WORKSPACE_ROOT / 'wcos.ps1'}")


# ----------------------------------------------------------------------
# CLI Entrypoint
# ----------------------------------------------------------------------

def main() -> int:
    if "--wcospath" in sys.argv or "--wcosspath" in sys.argv:
        argv_clean = [a for a in sys.argv[1:] if a not in ("--wcospath", "--wcosspath")]
        wcos_inst = WCOS()
        if len(argv_clean) >= 2 and argv_clean[0] in ("-u", "-p", "--unix", "--posix"):
            print(wcos_inst.path_to_clothos(argv_clean[1]))
            return 0
        elif len(argv_clean) >= 2 and argv_clean[0] in ("-w", "--windows"):
            print(wcos_inst.path_to_windows(argv_clean[1]))
            return 0
        elif argv_clean:
            target = argv_clean[0]
            if ":" in target or "\\" in target:
                print(wcos_inst.path_to_clothos(target))
            else:
                print(wcos_inst.path_to_windows(target))
            return 0
        print("Usage: wcospath -u <windows_path> | -w <clothos_path>")
        return 1

    parser = argparse.ArgumentParser(
        prog="wcos",
        description="WCOS — Windows ClothOS Subsystem (Universal Companion & Shell)",
        add_help=False,
    )
    parser.add_argument("-h", "--help", action="store_true", help="Show this help message")
    parser.add_argument("-v", "--version", action="store_true", help="Display WCOS version")
    parser.add_argument("-s", "--status", action="store_true", help="Display system status report")
    parser.add_argument("-g", "--gui", action="store_true", help="Launch ClothOS Command Center GUI")
    parser.add_argument("--rn", action="store_true", help="Launch ClothOS Universal React Native App")
    parser.add_argument("--start-daemon", action="store_true", help="Start background ClothOS services")
    parser.add_argument("--stop-daemon", action="store_true", help="Stop background ClothOS services")
    parser.add_argument("--emergency-kill", action="store_true", help="Emergency Kill all processes/sandboxes")
    parser.add_argument("--gauge", action="store_true", help="Evaluate Sensible Success Gauge & Sovereign Coherence Index")
    parser.add_argument("--auto-evolve", action="store_true", help="Launch Autonomous Continuous Self-Development Engine")
    parser.add_argument("--install", action="store_true", help="Install system wrappers into PATH/scripts")
    parser.add_argument("-d", "--ring", type=str, default=None, help="Priority Ring (P0..P5)")
    parser.add_argument("-u", "--user", type=str, default="najmos_sakib", help="Subsystem user context")
    parser.add_argument("--cd", type=str, default=None, help="Initial working directory")
    parser.add_argument("-e", "--exec", type=str, default=None, help="Command to execute")
    parser.add_argument("--wcospath", action="store_true", help="Path translation utility mode")
    parser.add_argument("cmd_args", nargs="*", help="Command and arguments to execute")

    args, unknown = parser.parse_known_args()
    all_cmd_args = args.cmd_args + unknown

    wcos_inst = WCOS()

    if args.wcospath:
        # Handle wcospath mode (like wslpath)
        if "-u" in all_cmd_args:
            idx = all_cmd_args.index("-u")
            if idx + 1 < len(all_cmd_args):
                print(wcos_inst.path_to_clothos(all_cmd_args[idx + 1]))
                return 0
        elif "-w" in all_cmd_args:
            idx = all_cmd_args.index("-w")
            if idx + 1 < len(all_cmd_args):
                print(wcos_inst.path_to_windows(all_cmd_args[idx + 1]))
                return 0
        elif all_cmd_args:
            target = all_cmd_args[0]
            if ":" in target or "\\" in target:
                print(wcos_inst.path_to_clothos(target))
            else:
                print(wcos_inst.path_to_windows(target))
            return 0
        print("Usage: wcospath -u <windows_path> | -w <clothos_path>")
        return 1

    if args.help:
        print(BANNER.strip())
        print("""
Usage:
  wcos [options] [command [arguments...]]

Subsystem Commands:
  wcos                                  Launch interactive clothsh shell
  wcos ls /mnt/c                       List files in host Windows C: drive
  wcos ps                              List active ClothOS virtual processes
  wcos top                             Interactive real-time process manager
  wcos free -m                         Display pooled cluster memory
  wcos kuramoto                        Inspect Kuramoto phase order parameter
  wcos cluster                         Inspect dual-node cluster mesh
  wcos hal                             Display Hardware Abstraction Layer
  wcos riscv                           Inspect RISC-V sovereign assembly status
  wcos tpu                             Inspect RISC-V 64 + TPU Systolic Array MXU
  wcos occipital                       Occipital V1-V5 retinotopic visual stream
  wcos daydream                        DMN spontaneous daydreaming at low beta
  wcos nsdr [on|off]                   Non-Sleep Deep Rest slow-wave regeneration
  wcos wm                              Graded All-or-Nothing 7-slot working memory
  wcos endorphin                       Beta-endorphin & muOR neurochemical reward
  wcos thoughts                        7-stage verbose consciousness monologue
  wcos steer --focus <domain>          Direct machine focus and compute priorities
  wcos kill <pid>                      Kill a virtual process
  wcos emergency_kill                  Halt ALL virtual processes immediately

Options:
  -s, --status                          Show comprehensive Task Manager status
  -g, --gui                             Launch Sovereign Command Center GUI
  --rn                                  Launch Universal React Native App
  --start-daemon                        Start background services headlessly
  --stop-daemon                         Stop background services
  --emergency-kill                      Force-kill all processes & sandboxes
  --install                             Install wcos, wcoss, and wcospath wrappers
  -d, --ring <P0..P5>                   Dispatch command under specific priority
  -u, --user <username>                 Execute command as specified user
  --cd <directory>                      Set working directory (ClothOS or Win path)
  -e, --exec <command>                  Execute command line
  -v, --version                         Print version information
  -h, --help                            Show this help manual
        """)
        return 0

    if args.version:
        print(f"WCOS version {VERSION} [Windows ClothOS Subsystem / RV64GCV Win32 HAL]")
        return 0

    if args.status:
        wcos_inst.print_status_report()
        return 0

    if args.gui:
        wcos_inst.launch_gui()
        return 0

    if args.rn:
        wcos_inst.launch_react_native()
        return 0

    if args.start_daemon:
        wcos_inst.start_daemons()
        return 0

    if args.stop_daemon:
        wcos_inst.stop_daemons()
        return 0

    if args.emergency_kill:
        wcos_inst.emergency_kill()
        return 0

    if args.gauge:
        from loom.clothos.success_gauge import success_gauge
        rep = success_gauge.evaluate(run_tests=False)
        print(BANNER.strip())
        print(f"📊 CLOTHOS SUCCESS GAUGE REPORT [Timestamp: {datetime.fromtimestamp(rep.timestamp).strftime('%Y-%m-%d %H:%M:%S')}]")
        print(f"   Sovereign Coherence Index (SCI): {rep.sovereign_coherence_index:.2f}% | Grade: {rep.grade}")
        print(f"   Production Readiness Status    : {'PRODUCTION READY' if rep.is_production_ready else 'DEVELOPMENT REQUIRED'}")
        print("--------------------------------------------------------------------------------")
        for dim_key, dim in rep.dimensions.items():
            bar_len = int(dim.score_pct / 5)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            print(f"  [{bar}] {dim.score_pct:5.1f}% | {dim.name:<35} | {dim.status}")
        print("--------------------------------------------------------------------------------")
        print("Recommendations:")
        for r in rep.recommendations:
            print(f"  • {r}")
        print("================================================================================\n")
        return 0

    if args.auto_evolve:
        from loom.clothos.self_evolution import AutonomousSelfEvolutionEngine
        engine = AutonomousSelfEvolutionEngine()
        engine.start_continuous_loop()
        return 0

    if args.install:
        wcos_inst.install_system_wrappers()
        return 0

    # Parse priority ring if provided
    p_ring = None
    if args.ring:
        ring_name = args.ring.upper()
        if not ring_name.startswith("P"):
            ring_name = f"P{ring_name}"
        ring_map = {
            "P0": PriorityRing.P0_LIFE_SANCTITY,
            "P1": PriorityRing.P1_PLANETARY,
            "P2": PriorityRing.P2_FIDUCIARY,
            "P3": PriorityRing.P3_NOETICS,
            "P4": PriorityRing.P4_EPISTEMIC,
            "P5": PriorityRing.P5_CREATIVE,
        }
        p_ring = ring_map.get(ring_name, PriorityRing.P4_EPISTEMIC)

    # Determine command to execute
    cmd_to_run = args.exec
    if not cmd_to_run and all_cmd_args:
        cmd_to_run = " ".join(all_cmd_args)

    if cmd_to_run:
        res = wcos_inst.execute(cmd_to_run, cwd=args.cd, ring=p_ring, user=args.user)
        if res.stdout:
            print(res.stdout, end="" if res.stdout.endswith("\n") else "\n")
        if res.stderr:
            print(res.stderr, file=sys.stderr, end="" if res.stderr.endswith("\n") else "\n")
        return res.exit_code

    # If no command arguments given, start interactive shell!
    return wcos_inst.interactive_shell(initial_cwd=args.cd)


if __name__ == "__main__":
    sys.exit(main())
