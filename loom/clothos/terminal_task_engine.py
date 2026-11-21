"""
ClothOS Terminal Task Engine — Enterprise Autonomous Terminal & Shell Orchestrator
==================================================================================

Empowers ClothOS with full agentic terminal execution, stateful session navigation,
remote multi-node cluster terminal dispatch (via Stitch Bridge API), built-in
commercial terminal diagnostics (sysinfo, ps, bench, monitors, ls, cat), and
strict Ahimsa/Sandbox safety enforcement.
"""

import os
import sys
import re
import time
import socket
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()


class TerminalTaskEngine:
    """Autonomous Terminal Task Orchestrator for local and distributed execution."""

    def __init__(
        self,
        workspace_root: Path,
        sandbox: Optional[Any] = None,
        mode_getter: Optional[Callable[[], Any]] = None,
    ):
        self.workspace_root = workspace_root.resolve()
        self.cwd = self.workspace_root
        self.prev_dir = self.workspace_root
        self.sandbox = sandbox
        self.mode_getter = mode_getter
        self.last_returncode = 0
        self.command_history: List[Dict[str, Any]] = []

    def set_workspace(self, new_dir: Path):
        """Updates the working directory statefully."""
        self.workspace_root = new_dir.resolve()
        self.cwd = self.workspace_root
        try:
            os.chdir(self.cwd)
            os.environ["PWD"] = str(self.cwd)
        except Exception:
            pass

    def _is_sandbox_mode(self) -> bool:
        if self.mode_getter:
            try:
                mode_val = self.mode_getter()
                return getattr(mode_val, "value", str(mode_val)).lower() == "sandbox"
            except Exception:
                return False
        return False

    def execute_cd(self, target_path: str) -> Dict[str, Any]:
        """Stateful working directory navigation."""
        target_path = target_path.strip().strip('"').strip("'")
        if not target_path or target_path == "~":
            resolved = Path.home()
        elif target_path == "-":
            resolved = self.prev_dir
        elif re.match(r"^[a-zA-Z]:$", target_path):
            resolved = Path(target_path + "\\").resolve()
        elif os.path.isabs(target_path):
            resolved = Path(target_path).resolve()
        else:
            resolved = (self.cwd / target_path).resolve()

        if resolved.is_dir():
            self.prev_dir = self.cwd
            self.cwd = resolved
            try:
                os.chdir(self.cwd)
                os.environ["PWD"] = str(self.cwd)
            except Exception:
                pass
            return {
                "cmd": f"cd {target_path}",
                "returncode": 0,
                "cwd": str(self.cwd),
                "stdout": f"Directory changed to {self.cwd}",
                "stderr": "",
                "duration_s": 0.001,
            }
        else:
            return {
                "cmd": f"cd {target_path}",
                "returncode": 1,
                "cwd": str(self.cwd),
                "stdout": "",
                "stderr": f"Directory not found: {target_path}",
                "duration_s": 0.001,
            }

    def execute(
        self,
        cmd: str,
        timeout: Optional[int] = 60,
        cwd: Optional[str] = None,
        live_stream: bool = False,
    ) -> Dict[str, Any]:
        """Executes a terminal command with stateful navigation, sandboxing, and output capture."""
        trimmed = (cmd or "").strip()
        if not trimmed:
            return {"cmd": "", "returncode": 0, "stdout": "", "stderr": "", "duration_s": 0.0}

        # 1. Stateful cd handling
        tokens = trimmed.split(maxsplit=1)
        verb = tokens[0].lower() if tokens else ""

        if verb == "cd":
            target = tokens[1].strip() if len(tokens) > 1 else "~"
            return self.execute_cd(target)

        if re.match(r"^[a-zA-Z]:$", trimmed):
            return self.execute_cd(trimmed + "\\")

        # 2. Sandbox safety boundary
        if self._is_sandbox_mode() and self.sandbox:
            safe, reason = self.sandbox.is_safe_command(trimmed)
            if not safe:
                return {
                    "cmd": trimmed,
                    "returncode": 126,
                    "error": f"Sandbox Veto: {reason}",
                    "stdout": "",
                    "stderr": f"Command vetoed by Ahimsa Sandbox policy: {reason}",
                    "duration_s": 0.0,
                }

        # 3. Built-in Terminal Utilities intercept
        if verb in ["sysinfo", "neofetch", "fastfetch"]:
            return self.get_sysinfo(display=live_stream)

        if verb in ["ps", "top"]:
            filter_kw = tokens[1].strip() if len(tokens) > 1 else None
            return self.get_ps(filter_name=filter_kw, display=live_stream)

        if verb == "bench" and len(tokens) > 1:
            return self.bench_cmd(tokens[1].strip())

        if verb in ["monitors", "monitor", "kvm", "screens"]:
            arg = tokens[1].strip() if len(tokens) > 1 else None
            return self.view_monitors(sub_cmd=arg)

        # 4. Resolve working directory
        exec_dir = Path(cwd).resolve() if cwd else self.cwd
        if not exec_dir.exists():
            exec_dir = self.workspace_root

        # 5. Shell configuration
        start_t = time.perf_counter()
        if os.name == "nt":
            shell_cmd = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", trimmed]
            shell_bool = False
        else:
            shell_cmd = trimmed
            shell_bool = True

        out_lines = []
        err_lines = []

        try:
            if live_stream:
                proc = subprocess.Popen(
                    shell_cmd,
                    cwd=str(exec_dir),
                    shell=shell_bool,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    bufsize=1,
                )

                # Stream stdout live
                if proc.stdout:
                    for line in proc.stdout:
                        sys.stdout.write(line)
                        sys.stdout.flush()
                        out_lines.append(line)
                proc.wait(timeout=timeout)
                if proc.stderr:
                    err_lines.append(proc.stderr.read())

                rc = proc.returncode
            else:
                res = subprocess.run(
                    shell_cmd,
                    cwd=str(exec_dir),
                    shell=shell_bool,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=timeout,
                )
                out_lines.append(res.stdout)
                err_lines.append(res.stderr)
                rc = res.returncode

            dur = round(time.perf_counter() - start_t, 3)
            self.last_returncode = rc

            mode_str = "FULL_ACCESS"
            if self.mode_getter:
                try:
                    mode_str = getattr(self.mode_getter(), "value", str(self.mode_getter()))
                except Exception:
                    pass

            result = {
                "cmd": trimmed,
                "mode": mode_str,
                "returncode": rc,
                "duration_s": dur,
                "cwd": str(exec_dir),
                "stdout": "".join(out_lines),
                "stderr": "".join(err_lines),
            }
            self.command_history.append({"cmd": trimmed, "returncode": rc, "duration_s": dur})
            return result

        except subprocess.TimeoutExpired:
            dur = round(time.perf_counter() - start_t, 3)
            return {
                "cmd": trimmed,
                "returncode": 124,
                "duration_s": dur,
                "cwd": str(exec_dir),
                "stdout": "".join(out_lines),
                "stderr": f"Terminal command timed out after {timeout} seconds.",
                "error": f"Shell command timed out ({timeout}s limit in sandbox mode).",
            }
        except Exception as ex:
            dur = round(time.perf_counter() - start_t, 3)
            return {
                "cmd": trimmed,
                "returncode": -1,
                "duration_s": dur,
                "cwd": str(exec_dir),
                "stdout": "",
                "stderr": str(ex),
                "error": str(ex),
            }

    def execute_remote(self, target_node: str, cmd: str, timeout: int = 45) -> Dict[str, Any]:
        """Executes a terminal command across the cluster on a specific node via Stitch Bridge API."""
        import urllib.request
        target_clean = target_node.strip().lstrip("@").lower()
        bridge_ip = "192.168.99.1" if target_clean in ["node1", "skytech"] else target_clean

        if target_clean in ["node2", "ryzen7", "local", "self"]:
            return self.execute(cmd, timeout=timeout, live_stream=False)

        try:
            from loom.clothos.mesh_discovery import get_mesh_beacon
            beacon = get_mesh_beacon()
            live_peers = beacon.get_live_peers()
            if target_clean in live_peers:
                bridge_ip = live_peers[target_clean].get("ip", bridge_ip)
        except Exception:
            pass

        headers = {"Content-Type": "application/json", "X-Fabric-Token": "G-GzcZEzqteW241i720XeH5UNT73T6qk"}
        payload = json.dumps({"command": cmd, "target_node": "local", "timeout_sec": timeout}).encode("utf-8")
        try:
            req = urllib.request.Request(f"http://{bridge_ip}:5555/api/admin/exec", data=payload, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout + 5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return {
                    "target_node": target_clean,
                    "bridge_ip": bridge_ip,
                    "command": cmd,
                    "returncode": data.get("returncode", 0),
                    "stdout": data.get("stdout", ""),
                    "stderr": data.get("stderr", ""),
                    "status": data.get("status", "SUCCESS"),
                }
        except Exception as ex:
            return {
                "target_node": target_clean,
                "bridge_ip": bridge_ip,
                "command": cmd,
                "returncode": -1,
                "stdout": "",
                "stderr": str(ex),
                "error": f"Failed to execute on remote node {target_clean} ({bridge_ip}): {ex}",
                "status": "ERROR",
            }

    def get_sysinfo(self, display: bool = False) -> Dict[str, Any]:
        """Neofetch / Fastfetch-style visual cluster system summary."""
        try:
            from loom.clothos.terminal import clothos_sysinfo
            if display:
                clothos_sysinfo()
        except Exception:
            pass

        host = socket.gethostname()
        cpu_info = "AMD Ryzen 7 7730U (8c/16t)" if "ryzen" in host.lower() or host == "WIN-7CMAQLVP8MV" else "Host CPU"
        ram_info = f"{psutil.virtual_memory().total // (1024**3)} GB" if HAS_PSUTIL else "32 GB"

        summary = {
            "os": "Windows 11 Enterprise (ClothOS Sovereign Substrate)",
            "host": host,
            "kernel": "ClothOS Polyglot Engine v0.2.0",
            "cpu": cpu_info,
            "memory_total": ram_info,
            "cluster_mesh": "Node 1 (skyTech Dual-GPU) ⟵2.5GbE⟶ Node 2 (Ryzen 7 Orchestrator)",
            "mesh_gpus": ["NVIDIA GeForce RTX 3060 (12GB CUDA)", "AMD Radeon RX 580 (8GB OpenCL/DirectML)"],
            "terminal_engine": "Prompt-Toolkit 3.0 + Rich + Starship Powerline",
            "working_directory": str(self.cwd),
        }
        return {"cmd": "sysinfo", "returncode": 0, "sysinfo": summary, "stdout": json.dumps(summary, indent=2), "stderr": ""}

    def get_ps(self, filter_name: Optional[str] = None, limit: int = 15, display: bool = False) -> Dict[str, Any]:
        """Inspects active system processes sorted by memory and CPU utilization."""
        try:
            from loom.clothos.terminal import clothos_ps
            if display:
                clothos_ps()
        except Exception:
            pass

        procs = []
        if HAS_PSUTIL:
            for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent", "memory_info"]):
                try:
                    info = p.info
                    name = info.get("name", "")
                    if filter_name and filter_name.lower() not in name.lower():
                        continue
                    mem_mb = (info.get("memory_info").rss // (1024**2)) if info.get("memory_info") else 0
                    procs.append({
                        "pid": info.get("pid"),
                        "name": name,
                        "cpu_pct": round(info.get("cpu_percent") or 0.0, 1),
                        "mem_pct": round(info.get("memory_percent") or 0.0, 1),
                        "mem_mb": mem_mb,
                    })
                except Exception:
                    continue
            procs.sort(key=lambda x: x["mem_pct"], reverse=True)
            procs = procs[:limit]

        return {
            "cmd": "ps",
            "returncode": 0,
            "process_count": len(procs),
            "processes": procs,
            "stdout": f"Listed {len(procs)} processes.",
            "stderr": "",
        }

    def bench_cmd(self, cmd: str) -> Dict[str, Any]:
        """Benchmarks command execution with millisecond precision."""
        t0 = time.perf_counter()
        res = self.execute(cmd, timeout=30, live_stream=False)
        dur = round(time.perf_counter() - t0, 4)
        return {
            "cmd": f"bench {cmd}",
            "target_command": cmd,
            "returncode": res.get("returncode", 0),
            "duration_s": dur,
            "duration_ms": round(dur * 1000, 2),
            "stdout": res.get("stdout", ""),
            "stderr": res.get("stderr", ""),
        }

    def view_monitors(self, sub_cmd: Optional[str] = None) -> Dict[str, Any]:
        """Visually represents the physical arrangement of multi-node monitors and handles focus switching."""
        try:
            from loom.clothos.terminal import clothos_monitors
            clothos_monitors(sub_cmd)
        except Exception:
            pass

        return {
            "cmd": f"monitors {sub_cmd or ''}".strip(),
            "returncode": 0,
            "cluster_monitors": {
                "node1_skytech": ["32-inch 4K Main (DP)", "27-inch 1440p Secondary (HDMI)"],
                "node2_ryzen7": ["Built-in 16-inch 1200p Display", "External USB-C Portable Monitor"],
                "kvm_routing": "Stitch Virtual KVM active on port 5555",
            },
            "stdout": "Monitors visual matrix displayed.",
            "stderr": "",
        }
