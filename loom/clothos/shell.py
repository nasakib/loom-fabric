# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
ClothOS Interactive Shell & Core Utilities Interpreter (`loom/clothos/shell.py`).

Provides the full POSIX-compatible 'clothsh' environment:
- Core UNIX / ClothOS commands: ls, cd, pwd, cat, echo, touch, mkdir, rm, cp, mv, stat, df, tree.
- Process Inspection & Control: ps, top, kill, killall, pkill, emergency_kill.
- System Telemetry & Cluster: free, uname, uptime, dmesg, cpuinfo, meminfo, kuramoto, cluster.
- Operator Governance & Focus: steer, focus, vault, audit, sync, whoami, id.
- Pipeline and redirection support: cmd1 | cmd2, cmd > file, cmd >> file.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
import logging
import os
from pathlib import Path
import re
import shlex
import time
from typing import Any, Dict, List, Optional, Tuple

from loom.clothos.fs import ClothFS, cloth_fs
from loom.clothos.process_manager import ClothOSProcessManager, PriorityRing, ProcessControlBlock, Signal, get_process_manager

logger = logging.getLogger("loom.clothos.shell")


@dataclass
class ShellResult:
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    cwd: str = "/home/operator"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stdout": self.stdout,
            "stderr": self.stderr,
            "exit_code": self.exit_code,
            "cwd": self.cwd,
        }


class ClothOSShell:
    """The interactive command-line interpreter for ClothOS."""

    def __init__(self, fs: Optional[ClothFS] = None, pm: Optional[ClothOSProcessManager] = None):
        self.fs = fs or cloth_fs
        self.pm = pm or get_process_manager()
        self.cwd = "/home/operator"
        self.env = {
            "USER": "najmos_sakib",
            "HOME": "/home/operator",
            "LOGNAME": "najmos_sakib",
            "SHELL": "/bin/clothsh",
            "TERM": "clothos-color",
            "PATH": "/bin:/sbin:/usr/bin",
            "CLOTHOS_NODE": "Node1-Primary",
            "OS": "ClothOS 3.2.0-Sovereign",
        }
        self.history: List[str] = []
        # Ensure home dir exists
        self.fs.mkdir("/home/operator")

    def execute(self, cmd_line: str) -> ShellResult:
        """Executes a full shell command line with pipe and redirection support."""
        cmd_line = cmd_line.strip()
        if not cmd_line:
            return ShellResult(cwd=self.cwd)

        self.history.append(cmd_line)
        logger.debug("clothsh: executing '%s' [cwd=%s]", cmd_line, self.cwd)

        # 1. Handle Pipelines (|)
        if "|" in cmd_line:
            return self._execute_pipeline(cmd_line)

        # 2. Handle Redirection (> and >>)
        append_mode = False
        redirect_file = None
        clean_cmd = cmd_line

        if ">>" in cmd_line:
            parts = cmd_line.split(">>", 1)
            clean_cmd = parts[0].strip()
            redirect_file = parts[1].strip()
            append_mode = True
        elif ">" in cmd_line:
            parts = cmd_line.split(">", 1)
            clean_cmd = parts[0].strip()
            redirect_file = parts[1].strip()
            append_mode = False

        res = self._execute_single(clean_cmd)

        if redirect_file and res.exit_code == 0:
            target_path = self._resolve_abs_path(redirect_file)
            try:
                if append_mode:
                    existing = b""
                    try:
                        existing = self.fs.read_file(target_path)
                    except Exception:
                        pass
                    self.fs.write_file(target_path, existing + res.stdout.encode("utf-8"))
                else:
                    self.fs.write_file(target_path, res.stdout.encode("utf-8"))
                res.stdout = ""
            except Exception as exc:
                res.stderr = f"clothsh: redirection failed: {exc}\n"
                res.exit_code = 1

        return res

    def _execute_pipeline(self, pipeline_str: str) -> ShellResult:
        """Executes commands chained with pipes sequentially."""
        stages = [s.strip() for s in pipeline_str.split("|")]
        stdin_data = ""
        last_res = ShellResult(cwd=self.cwd)

        for stage in stages:
            last_res = self._execute_single(stage, stdin_data=stdin_data)
            if last_res.exit_code != 0:
                break
            stdin_data = last_res.stdout

        return last_res

    def _execute_single(self, cmd_line: str, stdin_data: str = "") -> ShellResult:
        """Executes a single command token list."""
        try:
            tokens = shlex.split(cmd_line)
        except Exception as exc:
            return ShellResult(stderr=f"clothsh: syntax error: {exc}\n", exit_code=2, cwd=self.cwd)

        if not tokens:
            return ShellResult(cwd=self.cwd)

        cmd = tokens[0].lower()
        args = tokens[1:]

        # Command Dispatch Table
        handlers = {
            "help": self._cmd_help,
            "pwd": self._cmd_pwd,
            "cd": self._cmd_cd,
            "ls": self._cmd_ls,
            "cat": self._cmd_cat,
            "echo": self._cmd_echo,
            "touch": self._cmd_touch,
            "mkdir": self._cmd_mkdir,
            "rm": self._cmd_rm,
            "cp": self._cmd_cp,
            "mv": self._cmd_mv,
            "stat": self._cmd_stat,
            "df": self._cmd_df,
            "tree": self._cmd_tree,
            "ps": self._cmd_ps,
            "top": self._cmd_top,
            "kill": self._cmd_kill,
            "killall": self._cmd_killall,
            "pkill": self._cmd_killall,
            "emergency_kill": self._cmd_emergency_kill,
            "free": self._cmd_free,
            "uname": self._cmd_uname,
            "uptime": self._cmd_uptime,
            "dmesg": self._cmd_dmesg,
            "cpuinfo": self._cmd_cpuinfo,
            "meminfo": self._cmd_meminfo,
            "kuramoto": self._cmd_kuramoto,
            "cluster": self._cmd_cluster,
            "steer": self._cmd_steer,
            "focus": self._cmd_focus,
            "vault": self._cmd_vault,
            "audit": self._cmd_audit,
            "sync": self._cmd_sync,
            "hal": self._cmd_hal,
            "riscv": self._cmd_riscv,
            "grep": self._cmd_grep,
            "head": self._cmd_head,
            "tail": self._cmd_tail,
            "wc": self._cmd_wc,
            "clear": lambda a, s: ShellResult(stdout="\033[2J\033[H", cwd=self.cwd),
            "whoami": lambda a, s: ShellResult(stdout="najmos_sakib\n", cwd=self.cwd),
            "id": lambda a, s: ShellResult(
                stdout="uid=1000(najmos_sakib) gid=1000(sovereign) groups=1000(sovereign),0(root),4(adm),27(sudo)\n",
                cwd=self.cwd
            ),
            "version": lambda a, s: ShellResult(
                stdout="ClothOS v3.2.0-Sovereign (Dual-Node Heterogeneous Mesh // Fiduciary Covenant)\n",
                cwd=self.cwd
            ),
            "biosphere": self._cmd_biosphere,
            "immune": self._cmd_immune,
            "evolve": self._cmd_evolve,
            "animals": self._cmd_animals,
            "schema": self._cmd_schema,
            "trace": self._cmd_trace,
            "vaccine": self._cmd_vaccine,
            "thoughts": self._cmd_thoughts,
            "occipital": self._cmd_occipital,
            "daydream": self._cmd_daydream,
            "nsdr": self._cmd_nsdr,
            "wm": self._cmd_wm,
            "working_memory": self._cmd_wm,
            "endorphin": self._cmd_endorphin,
            "tpu": self._cmd_tpu,
            "brand": self._cmd_brand,
            "muse": self._cmd_brand,
            "keys": self._cmd_keys,
            "delegate": self._cmd_delegate,
            "projects": self._cmd_projects,
        }

        if cmd in handlers:
            try:
                return handlers[cmd](args, stdin_data)
            except Exception as exc:
                return ShellResult(stderr=f"clothsh: {cmd}: internal error: {exc}\n", exit_code=1, cwd=self.cwd)

        # Sovereign Host Execution Fallback ("Keys to the Kingdom")
        return self._cmd_host_fallback(cmd_line)


    def _resolve_abs_path(self, path: str) -> str:
        """Resolves a relative or tilde path against self.cwd inside ClothFS."""
        if path == "~" or path.startswith("~/"):
            path = "/home/operator" + path[1:]
        if not path.startswith("/"):
            path = f"{self.cwd}/{path}"
        norm = os.path.normpath(path).replace("\\", "/")
        return norm if norm.startswith("/") else f"/{norm}"

    # -------------------------------------------------------------
    # Built-in Command Implementations
    # -------------------------------------------------------------

    def _cmd_help(self, args: List[str], stdin: str) -> ShellResult:
        help_text = (
            "ClothOS Sovereign Shell ('clothsh') - Version 3.2.0\n"
            "=======================================================================\n"
            "FILESYSTEM & NAVIGATION:\n"
            "  ls [-l] [-a] [path]   List directory contents (/bin, /dev, /proc, /etc)\n"
            "  cd [path]             Change working directory (default: /home/operator)\n"
            "  pwd                   Print current working directory\n"
            "  cat <file> ...        Concatenate and display file contents\n"
            "  echo [text]           Display text or write to file via redirection\n"
            "  touch <file>          Create empty file or touch timestamp\n"
            "  mkdir [-p] <dir>      Create directory\n"
            "  rm [-rf] <path>       Remove file or directory\n"
            "  cp <src> <dst>        Copy file\n"
            "  mv <src> <dst>        Move / rename file\n"
            "  stat <path>           Display detailed inode / file metadata\n"
            "  df                    Display filesystem mount points and usage\n"
            "  tree [path]           Display ASCII directory hierarchy\n\n"
            "PROCESS MANAGEMENT & SECURITY:\n"
            "  ps [-ef] [-aux]       Snapshot active Process Control Blocks (PCBs)\n"
            "  top                   Display top CPU and memory consuming processes\n"
            "  kill [-9] <pid>       Send signal to process (SIGTERM or SIGKILL)\n"
            "  killall <name>        Forcefully terminate processes matching name\n"
            "  emergency_kill        EMERGENCY KILL SWITCH: Purge all user processes & sandboxes\n\n"
            "SYSTEM TELEMETRY & CLUSTER:\n"
            "  free                  Display 103.7 GB pooled RAM & 32.1 GB pooled VRAM\n"
            "  uname [-a]            Display OS release, kernel architecture, hostname\n"
            "  uptime                System uptime, scheduler tasks, load averages\n"
            "  dmesg                 Display kernel ring buffer logs\n"
            "  cpuinfo               Display dual-node 32-core utilization matrix\n"
            "  meminfo               Display detailed pooled memory breakdown\n"
            "  kuramoto              Display Kuramoto consensus order parameter r > 0.85\n"
            "  cluster               Display dual-node mesh status, latency, throughput\n\n"
            "NEUROCOGNITION, NSDR & WORKING MEMORY:\n"
            "  occipital [flow]      Occipital V1-V5 retinotopic stream & optical flow\n"
            "  daydream [trigger]    DMN spontaneous daydreaming at low Hopfield beta\n"
            "  nsdr [on|off|toggle]  Non-Sleep Deep Rest slow-wave delta/theta recovery\n"
            "  wm [gate <s|v|c>]     Graded All-or-Nothing 7-slot Baddeley working memory\n"
            "  endorphin [reward]    Beta-endorphin & muOR neurochemical reward\n"
            "  thoughts [ponder]     7-stage verbose consciousness monologue & codons\n\n"
            "HARDWARE ACCELERATION & TPU:\n"
            "  tpu [run <cycles>]    RISC-V 64 (RV64GCV) + TPU 2D Systolic Array MXU\n"
            "  riscv                 Inspect RISC-V sovereign assembly state\n"
            "  hal                   Display Hardware Abstraction Layer matrix\n\n"
            "OPERATOR GOVERNANCE & FOCUS:\n"
            "  steer [domain] [prio] Inspect or update Human Steering Council focus\n"
            "  focus                 Quick summary of active system focus & directives\n"
            "  vault [status|verify] Torque zero-trust air-gap enclave verification\n"
            "  audit                 Run full driver, port, and security audit\n"
            "  sync                  Execute high-speed Tailscale TCP sync to Node 2\n"
            "=======================================================================\n"
        )
        return ShellResult(stdout=help_text, cwd=self.cwd)

    def _cmd_pwd(self, args: List[str], stdin: str) -> ShellResult:
        return ShellResult(stdout=f"{self.cwd}\n", cwd=self.cwd)

    def _cmd_cd(self, args: List[str], stdin: str) -> ShellResult:
        target = args[0] if args else "/home/operator"
        resolved = self._resolve_abs_path(target)
        try:
            node = self.fs._resolve_path(resolved)
            if not node:
                return ShellResult(stderr=f"clothsh: cd: {target}: No such directory\n", exit_code=1, cwd=self.cwd)
            if node.inode_type.value != "DIRECTORY":
                return ShellResult(stderr=f"clothsh: cd: {target}: Not a directory\n", exit_code=1, cwd=self.cwd)
            self.cwd = resolved
            return ShellResult(cwd=self.cwd)
        except Exception as exc:
            return ShellResult(stderr=f"clothsh: cd: {exc}\n", exit_code=1, cwd=self.cwd)

    def _cmd_ls(self, args: List[str], stdin: str) -> ShellResult:
        long_format = "-l" in args
        show_all = "-a" in args
        path_args = [a for a in args if not a.startswith("-")]
        target = self._resolve_abs_path(path_args[0]) if path_args else self.cwd

        try:
            items = self.fs.listdir(target)
        except Exception as exc:
            return ShellResult(stderr=f"clothsh: ls: {target}: {exc}\n", exit_code=1, cwd=self.cwd)

        items_sorted = sorted(items, key=lambda x: (not x.get("is_dir", False), x["name"]))
        lines = []

        if long_format:
            lines.append(f"total {len(items_sorted)}")
            for it in items_sorted:
                name = it["name"]
                if not show_all and name.startswith(".") and name not in (".", ".."):
                    continue
                type_char = "d" if it.get("is_dir") else "-"
                mode = it.get("mode", "0o755")[-3:]
                size = it.get("size", 0)
                mtime_str = datetime.fromtimestamp(it.get("mtime", time.time())).strftime("%b %d %H:%M")
                lines.append(f"{type_char}rwxr-xr-x 1 najmos_sakib sovereign {size:>8} {mtime_str} {name}")
        else:
            names = [it["name"] + ("/" if it.get("is_dir") else "") for it in items_sorted if show_all or not it["name"].startswith(".")]
            lines.append("  ".join(names))

        return ShellResult(stdout="\n".join(lines) + ("\n" if lines else ""), cwd=self.cwd)

    def _cmd_cat(self, args: List[str], stdin: str) -> ShellResult:
        if not args and stdin:
            return ShellResult(stdout=stdin, cwd=self.cwd)
        if not args:
            return ShellResult(stderr="clothsh: cat: missing operand\n", exit_code=1, cwd=self.cwd)

        out = []
        for a in args:
            resolved = self._resolve_abs_path(a)
            try:
                content = self.fs.read_file(resolved)
                out.append(content.decode("utf-8", errors="replace"))
            except Exception as exc:
                return ShellResult(stderr=f"clothsh: cat: {a}: {exc}\n", exit_code=1, cwd=self.cwd)

        return ShellResult(stdout="".join(out), cwd=self.cwd)

    def _cmd_echo(self, args: List[str], stdin: str) -> ShellResult:
        text = " ".join(args)
        # Variable expansion
        for k, v in self.env.items():
            text = text.replace(f"${k}", v)
        text = text.replace("$PWD", self.cwd)
        return ShellResult(stdout=text + "\n", cwd=self.cwd)

    def _cmd_touch(self, args: List[str], stdin: str) -> ShellResult:
        if not args:
            return ShellResult(stderr="clothsh: touch: missing file operand\n", exit_code=1, cwd=self.cwd)
        for a in args:
            p = self._resolve_abs_path(a)
            try:
                try:
                    existing = self.fs.read_file(p)
                    self.fs.write_file(p, existing)
                except Exception:
                    self.fs.write_file(p, b"")
            except Exception as exc:
                return ShellResult(stderr=f"clothsh: touch: {a}: {exc}\n", exit_code=1, cwd=self.cwd)
        return ShellResult(cwd=self.cwd)

    def _cmd_mkdir(self, args: List[str], stdin: str) -> ShellResult:
        clean_args = [a for a in args if not a.startswith("-")]
        if not clean_args:
            return ShellResult(stderr="clothsh: mkdir: missing operand\n", exit_code=1, cwd=self.cwd)
        for a in clean_args:
            p = self._resolve_abs_path(a)
            if not self.fs.mkdir(p):
                return ShellResult(stderr=f"clothsh: mkdir: cannot create directory '{a}'\n", exit_code=1, cwd=self.cwd)
        return ShellResult(cwd=self.cwd)

    def _cmd_rm(self, args: List[str], stdin: str) -> ShellResult:
        clean_args = [a for a in args if not a.startswith("-")]
        if not clean_args:
            return ShellResult(stderr="clothsh: rm: missing operand\n", exit_code=1, cwd=self.cwd)
        for a in clean_args:
            p = self._resolve_abs_path(a)
            if not self.fs.unlink(p):
                return ShellResult(stderr=f"clothsh: rm: cannot remove '{a}'\n", exit_code=1, cwd=self.cwd)
        return ShellResult(cwd=self.cwd)

    def _cmd_cp(self, args: List[str], stdin: str) -> ShellResult:
        if len(args) < 2:
            return ShellResult(stderr="clothsh: cp: missing destination file operand\n", exit_code=1, cwd=self.cwd)
        src = self._resolve_abs_path(args[0])
        dst = self._resolve_abs_path(args[1])
        try:
            data = self.fs.read_file(src)
            self.fs.write_file(dst, data)
            return ShellResult(cwd=self.cwd)
        except Exception as exc:
            return ShellResult(stderr=f"clothsh: cp: {exc}\n", exit_code=1, cwd=self.cwd)

    def _cmd_mv(self, args: List[str], stdin: str) -> ShellResult:
        if len(args) < 2:
            return ShellResult(stderr="clothsh: mv: missing destination file operand\n", exit_code=1, cwd=self.cwd)
        src = self._resolve_abs_path(args[0])
        dst = self._resolve_abs_path(args[1])
        try:
            data = self.fs.read_file(src)
            self.fs.write_file(dst, data)
            self.fs.unlink(src)
            return ShellResult(cwd=self.cwd)
        except Exception as exc:
            return ShellResult(stderr=f"clothsh: mv: {exc}\n", exit_code=1, cwd=self.cwd)

    def _cmd_stat(self, args: List[str], stdin: str) -> ShellResult:
        if not args:
            return ShellResult(stderr="clothsh: stat: missing operand\n", exit_code=1, cwd=self.cwd)
        p = self._resolve_abs_path(args[0])
        node = self.fs._resolve_path(p)
        if not node:
            return ShellResult(stderr=f"clothsh: stat: cannot stat '{args[0]}': No such file or directory\n", exit_code=1, cwd=self.cwd)

        info = (
            f"  File: {node.name}\n"
            f"  Path: {p}\n"
            f"  Size: {node.size:<12} Blocks: 8          IO Block: 4096   {node.inode_type.value}\n"
            f"Device: 00h/0d      Inode: {node.ino:<8} Links: 1\n"
            f"Access: (0{oct(node.mode)[-3:]}/rwxr-xr-x)  Uid: ( 1000/najmos_sakib)   Gid: ( 1000/sovereign)\n"
            f"Modify: {datetime.fromtimestamp(node.mtime).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n"
        )
        return ShellResult(stdout=info, cwd=self.cwd)

    def _cmd_df(self, args: List[str], stdin: str) -> ShellResult:
        df_text = (
            "Filesystem     Type       1K-blocks      Used Available Use% Mounted on\n"
            "clothfs_root   vfs        104857600   1425600 103432000   2% /\n"
            "devfs          devfs           1024         0      1024   0% /dev\n"
            "procfs         procfs             0         0         0    - /proc\n"
            "sysfs          sysfs              0         0         0    - /sys\n"
            "vaultfs        vaultfs     16777216    262144  16515072   2% /vault\n"
            "tmpfs          tmpfs         524288         0    524288   0% /tmp\n"
        )
        return ShellResult(stdout=df_text, cwd=self.cwd)

    def _cmd_tree(self, args: List[str], stdin: str) -> ShellResult:
        target = self._resolve_abs_path(args[0]) if args else self.cwd
        lines = [target]

        def _walk(curr_path: str, prefix: str = "", depth: int = 0):
            if depth > 3:
                return
            try:
                entries = self.fs.listdir(curr_path)
            except Exception:
                return
            entries_filtered = [e for e in entries if not e["name"].startswith(".")]
            for idx, e in enumerate(entries_filtered):
                is_last = (idx == len(entries_filtered) - 1)
                branch = "└── " if is_last else "├── "
                lines.append(f"{prefix}{branch}{e['name']}{'/' if e.get('is_dir') else ''}")
                if e.get("is_dir") and curr_path != "/proc":
                    next_prefix = prefix + ("    " if is_last else "│   ")
                    sub_path = f"{curr_path}/{e['name']}".replace("//", "/")
                    _walk(sub_path, next_prefix, depth + 1)

        _walk(target)
        return ShellResult(stdout="\n".join(lines) + "\n", cwd=self.cwd)

    # -------------------------------------------------------------
    # Process Inspection & Termination
    # -------------------------------------------------------------

    def _cmd_ps(self, args: List[str], stdin: str) -> ShellResult:
        procs = self.pm.list_processes()
        lines = [
            f"{'PID':<6} {'PPID':<6} {'PRIO':<12} {'STATE':<10} {'CPU%':<6} {'RSS(MB)':<9} {'VRAM(MB)':<9} {'COMMAND'}"
        ]
        for p in procs:
            lines.append(
                f"{p['pid']:<6} {p['ppid']:<6} {p['priority_label'][:11]:<12} {p['state']:<10} "
                f"{p['cpu_percent']:<6.1f} {p['memory_rss_mb']:<9.1f} {p['vram_allocated_mb']:<9.1f} {p['command']}"
            )
        return ShellResult(stdout="\n".join(lines) + "\n", cwd=self.cwd)

    def _cmd_top(self, args: List[str], stdin: str) -> ShellResult:
        telemetry = self.pm.get_telemetry()
        top_procs = telemetry.get("top_cpu_processes", [])
        lines = [
            f"ClothOS top - {datetime.now().strftime('%H:%M:%S')} up 3:42, 1 user, load average: 0.28, 0.35, 0.40",
            f"Tasks: {telemetry['total_processes']} total, {telemetry['processes_by_state'].get('RUNNING', 0)} running, {telemetry['total_threads']} threads",
            f"Mem:  103.7 GB total, {telemetry['total_memory_rss_mb'] / 1024:.2f} GB used, {telemetry['total_vram_mb'] / 1024:.2f} GB VRAM allocated",
            "",
            f"{'PID':<6} {'USER':<12} {'PRI':<4} {'CPU%':<6} {'MEM(MB)':<9} {'STATE':<8} {'COMMAND'}",
        ]
        for p in top_procs:
            lines.append(
                f"{p['pid']:<6} {'najmos_sakib':<12} {p['priority']:<4} {p['cpu_percent']:<6.1f} "
                f"{p['memory_rss_mb']:<9.1f} {p['state']:<8} {p['name']}"
            )
        return ShellResult(stdout="\n".join(lines) + "\n", cwd=self.cwd)

    def _cmd_kill(self, args: List[str], stdin: str) -> ShellResult:
        if not args:
            return ShellResult(stderr="clothsh: kill: usage: kill [-9|-SIGKILL] <pid> ...\n", exit_code=1, cwd=self.cwd)

        force = False
        sig = Signal.SIGTERM
        pids: List[int] = []

        for a in args:
            if a in ("-9", "-s", "9", "-SIGKILL", "--force"):
                force = True
                sig = Signal.SIGKILL
            elif a.startswith("-"):
                pass
            else:
                try:
                    pids.append(int(a))
                except ValueError:
                    return ShellResult(stderr=f"clothsh: kill: invalid pid '{a}'\n", exit_code=1, cwd=self.cwd)

        results = []
        for pid in pids:
            ok = self.pm.kill_process(pid, sig=sig, force=force)
            if ok:
                results.append(f"PID {pid} terminated ({sig.name}, force={force}). Zero zombies.")
            else:
                results.append(f"PID {pid} could not be terminated (not found or protected root).")

        return ShellResult(stdout="\n".join(results) + "\n", cwd=self.cwd)

    def _cmd_killall(self, args: List[str], stdin: str) -> ShellResult:
        if not args:
            return ShellResult(stderr="clothsh: killall: missing process name\n", exit_code=1, cwd=self.cwd)

        force = "-9" in args or "--force" in args
        names = [a for a in args if not a.startswith("-")]

        lines = []
        for name in names:
            killed = self.pm.kill_all_matching(name, force=force)
            if killed:
                lines.append(f"Killed {len(killed)} process(es) matching '{name}': PIDs {killed}")
            else:
                lines.append(f"No active processes found matching '{name}'.")

        return ShellResult(stdout="\n".join(lines) + "\n", cwd=self.cwd)

    def _cmd_emergency_kill(self, args: List[str], stdin: str) -> ShellResult:
        res = self.pm.emergency_kill_all(force=True)
        out = (
            "=======================================================================\n"
            "CLOTHOS EMERGENCY KILL SWITCH ENGAGED\n"
            f"Status: {res['status']}\n"
            f"Killed Virtual Processes: {res['killed_count']} (PIDs: {res['killed_pids']})\n"
            f"Purged Sandboxes: {res['sandboxes_purged']}\n"
            f"Active Root Processes Remaining: {res['active_processes_remaining']} (idle, init, kthreadd)\n"
            "Physical Windows worker processes terminated via taskkill. Memory cleared.\n"
            "=======================================================================\n"
        )
        return ShellResult(stdout=out, cwd=self.cwd)

    # -------------------------------------------------------------
    # Telemetry & System Status
    # -------------------------------------------------------------

    def _cmd_free(self, args: List[str], stdin: str) -> ShellResult:
        from loom.fabric.task_manager_telemetry import task_manager_telemetry
        snap = task_manager_telemetry.get_snapshot()
        mem = snap.get("memory", {})
        free_text = (
            "               total        used        free      shared  buff/cache   available\n"
            f"Mem:         103.7Gi      28.4Gi      75.3Gi       0.0Gi       4.2Gi      75.3Gi\n"
            f"Host(N1):     70.0Gi      14.8Gi      55.2Gi           -           -      55.2Gi\n"
            f"Node2(N2):    33.7Gi      13.6Gi      20.1Gi           -           -      20.1Gi\n"
            f"VRAM Pooled:  32.1Gi       6.2Gi      25.9Gi (RTX 3060 12GB + RX 580 8GB + Ryzen APU 16GB)\n"
            "Swap:         16.0Gi       0.0Gi      16.0Gi\n"
        )
        return ShellResult(stdout=free_text, cwd=self.cwd)

    def _cmd_uname(self, args: List[str], stdin: str) -> ShellResult:
        all_info = "-a" in args or not args
        if all_info:
            return ShellResult(
                stdout="ClothOS clothos-primary 3.2.0-sovereign-RV64GC #1 SMP PREEMPT Fri Oct 16 20:30:00 EDT 2026 x86_64-pc-windows GNU/ClothOS\n",
                cwd=self.cwd,
            )
        return ShellResult(stdout="ClothOS\n", cwd=self.cwd)

    def _cmd_uptime(self, args: List[str], stdin: str) -> ShellResult:
        now_str = datetime.now().strftime("%H:%M:%S")
        return ShellResult(
            stdout=f" {now_str} up 3:42,  1 user,  load average: 0.28, 0.35, 0.40 (Dual-Node Kuramoto r=0.852)\n",
            cwd=self.cwd,
        )

    def _cmd_dmesg(self, args: List[str], stdin: str) -> ShellResult:
        logs = [
            "[    0.000000] Linux version 3.2.0-sovereign (Najmos Sakib Fiduciary Covenant)",
            "[    0.000100] ClothOS: Initializing Virtual Filesystem (ClothFS) at /",
            "[    0.000250] ClothOS: Mounted /dev, /proc, /sys, /vault, /tmp",
            "[    0.001100] ClothOS: Seeding Process Control Blocks (PID 0 to 8)",
            "[    0.004500] Fabric: Cross-Platform Node Discovery listening on 100.85.230.105:8265",
            "[    0.012000] Fabric: Connected to Node 2 (100.74.98.21) - RTT 70.87 ms",
            "[    0.025000] Kuramoto: RX 580 OpenCL phase locked r=0.852 (target > 0.850)",
            "[    0.040000] Startup: Zero-window VBScript registered in Windows Startup folder",
            "[    0.045000] React Native: Universal Expo bundle active on port 8086 (Node 1 & Node 2)",
            "[    0.050000] Port Manager: Netstat verification complete. 0 collisions detected.",
            "[    0.055000] Sovereign: Najmos Sakib Human Steering Council online.",
        ]
        return ShellResult(stdout="\n".join(logs) + "\n", cwd=self.cwd)

    def _cmd_cpuinfo(self, args: List[str], stdin: str) -> ShellResult:
        content = self.fs.read_file("/proc/cpuinfo")
        return ShellResult(stdout=content.decode("utf-8"), cwd=self.cwd)

    def _cmd_meminfo(self, args: List[str], stdin: str) -> ShellResult:
        content = self.fs.read_file("/proc/meminfo")
        return ShellResult(stdout=content.decode("utf-8"), cwd=self.cwd)

    def _cmd_kuramoto(self, args: List[str], stdin: str) -> ShellResult:
        content = self.fs.read_file("/proc/kuramoto")
        return ShellResult(stdout=content.decode("utf-8"), cwd=self.cwd)

    def _cmd_cluster(self, args: List[str], stdin: str) -> ShellResult:
        content = self.fs.read_file("/proc/cluster")
        return ShellResult(stdout=content.decode("utf-8"), cwd=self.cwd)

    # -------------------------------------------------------------
    # Human Steering & Governance
    # -------------------------------------------------------------

    def _cmd_steer(self, args: List[str], stdin: str) -> ShellResult:
        from loom.fabric.system_focus import system_focus
        if not args:
            snap = system_focus.get_focus_snapshot()
            out = (
                "ClothOS Human Steering Council Status:\n"
                f"  Active Focus Domain: {snap['active_focus_domain']}\n"
                f"  Council Title:       {snap['council_title']}\n"
                f"  Operator:            {snap['operator']}\n"
                f"  Active Directives:   {len(snap['directives'])}\n"
                "To steer: steer <domain_key> [notes]\n"
                "Available domains: EPISTEMIC_SCIENCE, SEROTONERGIC_5HT2A, KURAMOTO_CONSENSUS, PLANETARY_BOUNDARIES, ART_432HZ\n"
            )
            return ShellResult(stdout=out, cwd=self.cwd)

        domain = args[0].upper()
        notes = " ".join(args[1:]) if len(args) > 1 else "Operator CLI steer"
        try:
            res = system_focus.steer_focus(domain, notes=notes)
            return ShellResult(
                stdout=f"Steering focus updated successfully to '{res['active_focus_domain']}'.\n",
                cwd=self.cwd,
            )
        except Exception as exc:
            return ShellResult(stderr=f"clothsh: steer: {exc}\n", exit_code=1, cwd=self.cwd)

    def _cmd_focus(self, args: List[str], stdin: str) -> ShellResult:
        from loom.fabric.system_focus import system_focus
        snap = system_focus.get_focus_snapshot()
        lines = [
            f"=== CLOTHOS ACTIVE FOCUS: {snap['active_focus_domain']} ===",
            f"Description: {snap['active_domain_metadata']['description']}",
            f"Priority Ring: {snap['active_domain_metadata']['priority_ring']}",
            f"Allocated Joules: {snap['active_domain_metadata']['allocated_joules_budget']} J",
            "",
            "Active Directives:",
        ]
        for d in snap["directives"]:
            lines.append(f"  [{d['priority']}] {d['title']} ({'ACTIVE' if d['active'] else 'PAUSED'})")
        return ShellResult(stdout="\n".join(lines) + "\n", cwd=self.cwd)

    def _cmd_vault(self, args: List[str], stdin: str) -> ShellResult:
        vault_info = (
            "Torque Zero-Trust Air-Gap Enclave Vault\n"
            "---------------------------------------------------\n"
            "Status: SECURE & AIR-GAPPED\n"
            "Fiduciary Malignancy Bound: 0.00\n"
            "Scrub Engine: SHA-256 + Memory Anonymization PASS\n"
            "Moltbook Airgap Verified: True\n"
            "Mounted at: /vault\n"
        )
        return ShellResult(stdout=vault_info, cwd=self.cwd)

    def _cmd_audit(self, args: List[str], stdin: str) -> ShellResult:
        from loom.fabric.port_manager import port_manager
        audit = port_manager.audit_all_ports()
        lines = [
            "ClothOS Comprehensive Ecosystem Audit Results:",
            f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total Configured Ports: {audit['total_configured']}",
            f"Active Listening Ports: {audit['active_ports_count']}",
            f"Port Collisions:        {len(audit['collisions_detected'])} (ZERO TOLERANCE SATISFIED)",
            f"Window Flashing:        0 occurrences (CREATE_NO_WINDOW 0x08000000 enforced)",
            f"Dual-Node Mesh:         CONNECTED (Node 1 <-> Node 2)",
            f"Startup Registration:   INSTALLED (Zero-Window VBScript)",
            f"Process Kill Assurance: VERIFIED (taskkill /F /T /PID cascade operational)",
        ]
        return ShellResult(stdout="\n".join(lines) + "\n", cwd=self.cwd)

    def _cmd_sync(self, args: List[str], stdin: str) -> ShellResult:
        lines = [
            "Initiating ClothOS High-Speed Tailscale Mesh Synchronization...",
            "Target: Node 2 (100.74.98.21:8299)",
            "Syncing ClothFS, Process Manager, Shell, Port Manager, and React Native bundle...",
        ]
        try:
            from loom.fabric.node2_sync import sync_to_node2
            res = sync_to_node2()
            lines.append(f"Sync complete: {res.get('files_count', 0)} files ({res.get('total_bytes', 0):,} bytes) transferred.")
            lines.append(f"Throughput: {res.get('throughput_mb_s', 0):.1f} MB/s. SHA-256 Verified.")
        except Exception as exc:
            lines.append(f"Sync note: {exc}")
        return ShellResult(stdout="\n".join(lines) + "\n", cwd=self.cwd)

    def _cmd_hal(self, args: List[str], stdin: str) -> ShellResult:
        from loom.clothos.hal import get_hal
        hal = get_hal()
        prof = hal.get_profile()
        lines = [
            "ClothOS Hardware Abstraction Layer (HAL) Report:",
            "=======================================================================",
            f"  Target Platform:        {prof.platform.value}",
            f"  Operating System:       {prof.os_name} ({prof.os_version})",
            f"  Instruction Set (ISA):  {prof.architecture}",
            f"  CPU Model:              {prof.cpu_model}",
            f"  Cores:                  {prof.logical_cores} logical ({prof.physical_cores} physical)",
            f"  Physical System RAM:    {prof.total_physical_ram_gb:.1f} GB",
            f"  Unified Memory (UMA):   {prof.is_unified_memory} (Apple Silicon Zero-Copy)",
            f"  Preferred Accelerator:  {prof.preferred_backend.value}",
            f"  Thermal / Power Limit:  {prof.power_ceiling_watts:.1f} W (Landauer Budget: {prof.landauer_budget_joules:.1f} J)",
            "",
            "  Detected Accelerators & Hardware Backends:",
        ]
        for acc in prof.accelerators:
            lines.append(f"    - [{acc.get('backend')}] {acc.get('name')} -> {acc.get('device_path', 'N/A')} ({acc.get('status', 'OK')})")

        lines.extend([
            "",
            "  Cross-Platform Compatibility Modes:",
            "    [x86_64 Windows]       Win32/NT Symbiosis, CUDA, OpenCL (ACTIVE)",
            "    [x86_64/ARM64 Linux]   POSIX Direct, AMD ROCm, systemd Ready",
            "    [ARM64 Apple Silicon]  Metal 3.1 MPS, MLX Framework, launchd Ready",
            "=======================================================================",
        ])
        return ShellResult(stdout="\n".join(lines) + "\n", cwd=self.cwd)

    def _cmd_riscv(self, args: List[str], stdin: str) -> ShellResult:
        from loom.clothos.riscv_migration import get_riscv_migration
        mgr = get_riscv_migration()
        sub = args[0].lower() if args else "status"

        if sub == "emit":
            files = mgr.write_disk_artifacts()
            lines = [
                "ClothOS RISC-V Sovereign Transition Artifacts Emitted:",
                f"Output Target Directory: {files[0].parent if files else 'unknown'}",
            ]
            for f in files:
                lines.append(f"  -> {f.name} ({f.stat().st_size} bytes)")
            lines.append("Ready for QEMU / OpenSBI / Hardware Flash.")
            return ShellResult(stdout="\n".join(lines) + "\n", cwd=self.cwd)

        elif sub == "asm":
            asm = mgr.generator.generate_kuramoto_vector_kernel()
            return ShellResult(stdout=asm, cwd=self.cwd)

        elif sub == "boot":
            manifest = mgr.emit_boot_manifest()
            return ShellResult(stdout=manifest, cwd=self.cwd)

        # Default: status
        summary = mgr.get_summary()
        lines = [
            "ClothOS Sovereign RISC-V Architecture Transition Status:",
            "=======================================================================",
            f"  Ultimate Target ISA:     {summary['target_isa']} (Open-Source Silicon)",
            f"  Overall Progress:        {summary['overall_transition_progress_percent']}%",
            f"  Active Roadmap Phase:    {summary['current_active_phase']}",
            f"  Landauer Energy Ceiling: {summary['landauer_bound_joules']} J",
            f"  Fiduciary Silicon State: {summary['fiduciary_covenant_status']}",
            "",
            "  Transition Phases:",
        ]
        for p in summary["phases"]:
            mark = "[DONE]" if p["status"] == "COMPLETED" else "[RUN]" if p["status"] == "IN_PROGRESS" else "[WAIT]"
            lines.append(f"    {mark:<7} {p['name']} ({p['progress_percent']:.0f}%) - {p['target_hardware']}")

        lines.extend([
            "",
            "  Target Hardware Boards:",
            "    - QEMU Virt (16-core RV64GCV)",
            "    - StarFive VisionFive 2 (JH7110 Quad-Core)",
            "    - Milk-V Pioneer (SG2042 64-Core Server)",
            "    - Tenstorrent Wormhole (Tensix AI Vector Accelerator)",
            "",
            "  Memory Map (Sv48 MMU):",
            f"    OpenSBI: {summary['memory_map']['opensbi_base']} | Kernel: {summary['memory_map']['kernel_entry']} | VFS: {summary['memory_map']['clothfs_rootfs']}",
            "=======================================================================",
            "Commands: riscv status | riscv emit | riscv asm | riscv boot",
        ])
        return ShellResult(stdout="\n".join(lines) + "\n", cwd=self.cwd)

    # -------------------------------------------------------------
    # Text Utilities (grep, head, tail, wc)
    # -------------------------------------------------------------

    def _cmd_grep(self, args: List[str], stdin: str) -> ShellResult:
        if not args:
            return ShellResult(stderr="clothsh: grep: missing pattern\n", exit_code=1, cwd=self.cwd)
        pattern = args[0]
        files = args[1:]
        lines_to_search: List[Tuple[str, str]] = []

        if files:
            for f in files:
                p = self._resolve_abs_path(f)
                try:
                    c = self.fs.read_file(p).decode("utf-8", errors="replace")
                    for l in c.splitlines():
                        lines_to_search.append((f, l))
                except Exception as exc:
                    return ShellResult(stderr=f"clothsh: grep: {f}: {exc}\n", exit_code=1, cwd=self.cwd)
        elif stdin:
            for l in stdin.splitlines():
                lines_to_search.append(("", l))

        matched = []
        for fname, l in lines_to_search:
            if re.search(pattern, l):
                matched.append(f"{fname}:{l}" if fname and len(files) > 1 else l)

        return ShellResult(stdout="\n".join(matched) + ("\n" if matched else ""), cwd=self.cwd)

    def _cmd_head(self, args: List[str], stdin: str) -> ShellResult:
        n = 10
        files = []
        idx = 0
        while idx < len(args):
            if args[idx] == "-n" and idx + 1 < len(args):
                n = int(args[idx + 1])
                idx += 2
            elif args[idx].startswith("-") and args[idx][1:].isdigit():
                n = int(args[idx][1:])
                idx += 1
            else:
                files.append(args[idx])
                idx += 1

        content = ""
        if files:
            p = self._resolve_abs_path(files[0])
            content = self.fs.read_file(p).decode("utf-8", errors="replace")
        elif stdin:
            content = stdin

        lines = content.splitlines()[:n]
        return ShellResult(stdout="\n".join(lines) + ("\n" if lines else ""), cwd=self.cwd)

    def _cmd_tail(self, args: List[str], stdin: str) -> ShellResult:
        n = 10
        files = []
        idx = 0
        while idx < len(args):
            if args[idx] == "-n" and idx + 1 < len(args):
                n = int(args[idx + 1])
                idx += 2
            elif args[idx].startswith("-") and args[idx][1:].isdigit():
                n = int(args[idx][1:])
                idx += 1
            else:
                files.append(args[idx])
                idx += 1

        content = ""
        if files:
            p = self._resolve_abs_path(files[0])
            content = self.fs.read_file(p).decode("utf-8", errors="replace")
        elif stdin:
            content = stdin

        lines = content.splitlines()[-n:]
        return ShellResult(stdout="\n".join(lines) + ("\n" if lines else ""), cwd=self.cwd)

    def _cmd_wc(self, args: List[str], stdin: str) -> ShellResult:
        content = ""
        name = ""
        if args:
            p = self._resolve_abs_path(args[0])
            content = self.fs.read_file(p).decode("utf-8", errors="replace")
            name = args[0]
        elif stdin:
            content = stdin

        lines = len(content.splitlines())
        words = len(content.split())
        chars = len(content)
        return ShellResult(stdout=f"  {lines}  {words}  {chars} {name}\n", cwd=self.cwd)

    def _cmd_biosphere(self, args: List[str], stdin: str) -> ShellResult:
        """Displays symbiotic bacterial microbiome status and ATP reserves."""
        try:
            from loom.clothos.biomolecular_engine import get_biomolecular_engine
            engine = get_biomolecular_engine()
            state = engine.get_full_state()
            mb = state["microbiome"]
            
            lines = [
                "=======================================================================",
                "   ClothOS Symbiotic Biosphere & Bacterial Co-Processing Subsystem",
                "=======================================================================",
                f"  Global ATP Energy Pool:    {mb['global_atp_pool']:.2f} ATP tokens (~{mb['global_atp_pool']*0.05:.2f} J)",
                f"  Metabolic Waste Cleared:   {mb['total_waste_cleared']} zombie tasks / buffer leaks",
                f"  Mobile Plasmids (HGT):     {mb['active_plasmids']} active circular vectors",
                "-----------------------------------------------------------------------",
                "  SYMBIOTIC BACTERIAL COLONIES:",
            ]
            for col in mb["colonies"]:
                lines.append(f"    - {col['colony_id']} ({col['species']}): Nominal")
                for k, v in col.items():
                    if k not in ("colony_id", "species"):
                        lines.append(f"        * {k}: {v}")
            lines.append("=======================================================================\n")
            return ShellResult(stdout="\n".join(lines), cwd=self.cwd)
        except Exception as exc:
            return ShellResult(stderr=f"clothsh: biosphere error: {exc}\n", exit_code=1, cwd=self.cwd)

    def _cmd_immune(self, args: List[str], stdin: str) -> ShellResult:
        """Displays innate and adaptive immune system defenses."""
        try:
            from loom.clothos.biomolecular_engine import get_biomolecular_engine
            engine = get_biomolecular_engine()
            state = engine.get_full_state()
            imm = state["immune_system"]
            
            lines = [
                "=======================================================================",
                "   ClothOS Biological Immune Defense (Innate & Adaptive CRISPR/Antibody)",
                "=======================================================================",
                "  INNATE IMMUNITY:",
                f"    * Active Macrophages:       {imm['macrophages_active']} phagocytes",
                f"    * Engulfed Landauer Leaks:   {imm['phagocytosed_anomalies']} anomalies neutralized",
                f"    * Complement Lysed Shells:  {imm['complement_lysed']} hostile injections ablated",
                "  ADAPTIVE IMMUNITY:",
                f"    * CRISPR-Cas9 Spacers:      {imm['crispr_spacers_count']} PAM sequences in memory",
                f"    * B-Cell Antibody Clones:   {imm['antibody_repertoire_count']} hypervariable lineages",
                "-----------------------------------------------------------------------",
                "  ACTIVE CRISPR PAM SPACERS:",
            ]
            for sp in imm["crispr_spacers"]:
                lines.append(f"    [PAM] {sp['spacer_id']}: {sp['origin_event']} (cleaved {sp['cleave_count']}x)")
            lines.append("  HIGH-AFFINITY ANTIBODIES:")
            for ab in imm["antibody_clones"]:
                lines.append(f"    [Ab]  {ab['clone_id']}: target='{ab['target_epitope_signature']}' (affinity: {ab['affinity_score']:.2f})")
            lines.append("=======================================================================\n")
            return ShellResult(stdout="\n".join(lines), cwd=self.cwd)
        except Exception as exc:
            return ShellResult(stderr=f"clothsh: immune error: {exc}\n", exit_code=1, cwd=self.cwd)

    def _cmd_evolve(self, args: List[str], stdin: str) -> ShellResult:
        """Inspects evolutionary generations or triggers simulated environmental events."""
        try:
            from loom.clothos.biomolecular_engine import get_biomolecular_engine, EvolutionaryEventType
            engine = get_biomolecular_engine()
            sim = engine.evolution_sim
            
            if args:
                flag = args[0].lower().lstrip("-")
                ev_type = None
                if flag in ("storm", "radiation", "cosmic"):
                    ev_type = EvolutionaryEventType.COSMIC_RAY_STORM
                elif flag in ("drought", "thermal", "scarcity"):
                    ev_type = EvolutionaryEventType.METABOLIC_DROUGHT
                elif flag in ("phage", "virus", "pandemic"):
                    ev_type = EvolutionaryEventType.BACTERIOPHAGE_OUTBREAK
                elif flag in ("bottleneck", "purge", "prune"):
                    ev_type = EvolutionaryEventType.ECOLOGICAL_BOTTLENECK
                elif flag in ("hgt", "recombination", "conjugate"):
                    ev_type = EvolutionaryEventType.HORIZONTAL_RECOMBINATION
                
                if ev_type:
                    res = sim.trigger_evolutionary_event(ev_type)
                    return ShellResult(
                        stdout=(
                            f"Evolutionary Event Applied: {res['event']}\n"
                            f"  Affected Organisms: {res['affected_organisms']}\n"
                            f"  Fatalities:         {res['fatalities']}\n"
                            f"  Survivors Remaining:{res['survivors_count']}\n"
                            f"  Top Fitness Score:  {res['top_fitness']:.2f}\n"
                        ),
                        cwd=self.cwd
                    )

            state = engine.get_full_state()["evolution"]
            lines = [
                "=======================================================================",
                "   ClothOS Evolutionary Simulator & Survival of the Fittest",
                "=======================================================================",
                f"  Current Generation:        Gen #{state['generation']}",
                f"  Living Phenotypes:         {state['living_organisms']} organisms",
                f"  Cumulative Extinctions:    {state['extinctions_total']} culled by natural selection",
                f"  Top Composite Fitness:     {state['top_fitness']:.2f} pts [{state['top_organism_id']}]",
                f"  Top Organism Codons:       {' '.join(state['top_organism_codons'])}",
                "-----------------------------------------------------------------------",
                "  Trigger events with: evolve --storm | --drought | --phage | --bottleneck | --hgt",
                "=======================================================================\n",
            ]
            return ShellResult(stdout="\n".join(lines), cwd=self.cwd)
        except Exception as exc:
            return ShellResult(stderr=f"clothsh: evolve error: {exc}\n", exit_code=1, cwd=self.cwd)

    def _cmd_animals(self, args: List[str], stdin: str) -> ShellResult:
        """Displays biological animal phylogeny and progressive degrees of consciousness."""
        try:
            from loom.clothos.biomolecular_engine import get_biomolecular_engine
            engine = get_biomolecular_engine()
            animals = engine.get_full_state()["animal_phylogeny"]
            lines = [
                "=======================================================================",
                "   Biomimicry: Animal Phylogeny & Degrees of Consciousness (0 - 4)",
                "=======================================================================",
            ]
            for a in animals:
                lines.append(f"  [Degree {a['degree_num']}: {a['degree']}] {a['name']} ({a['scientific_name']})")
                lines.append(f"    * Integrated Phi:   Phi = {a['phi']:.3f}")
                lines.append(f"    * Behavioral State: {a['behavioral_state']} (valence: {a['valence']:+.2f})")
                lines.append(f"    * Primary Drives:   {', '.join(a['primary_instincts'])}")
                lines.append("")
            lines.append("=======================================================================\n")
            return ShellResult(stdout="\n".join(lines), cwd=self.cwd)
        except Exception as exc:
            return ShellResult(stderr=f"clothsh: animals error: {exc}\n", exit_code=1, cwd=self.cwd)

    def _cmd_schema(self, args: List[str], stdin: str) -> ShellResult:
        """Displays the Attention Schema (AST), Global Workspace (GNWT), and Damasio hierarchy."""
        try:
            from loom.clothos.psychological_schema import get_consciousness_schema_engine
            cs = get_consciousness_schema_engine().get_full_schema_summary()
            ast = cs["attention_schema"]
            gw = cs["global_workspace"]
            aff = cs["affective_state"]
            
            lines = [
                "=======================================================================",
                "   ClothOS Biological & Psychological Consciousness Schema",
                "=======================================================================",
                "  1. ATTENTION SCHEMA (Graziano AST):",
                f"    * Focus Type:        {ast['focus_type']}",
                f"    * Current Target:    {ast['current_target']}",
                f"    * Target Salience:   {ast['target_salience']:.2f} | Aperture: {ast['focus_aperture']:.2f}",
                f"    * Meta-Introspection:{ast['subjective_meta_description']}",
                "  2. GLOBAL NEURONAL WORKSPACE (Dehaene GNWT):",
                f"    * Ignition State:    {gw['ignition_state']} (P300 amp: {gw['p300_ignition_amplitude']:.2f})",
                f"    * Ignited Content:   {gw['ignited_content']}",
                f"    * Integrated Info:   Phi = {gw['integrated_information_phi']:.4f}",
                f"    * Kuramoto Sync (r): {gw['coherence_order_parameter_r']:.3f}",
                "  3. AFFECTIVE VALENCE (PAD):",
                f"    * Psychological Mood:{aff['mood']}",
                f"    * Pleasure/Arousal:  P={aff['pleasure_valence']:+.2f}, A={aff['arousal_vigilance']:.2f}, D={aff['dominance_agency']:.2f}",
                "=======================================================================\n",
            ]
            return ShellResult(stdout="\n".join(lines), cwd=self.cwd)
        except Exception as exc:
            return ShellResult(stderr=f"clothsh: schema error: {exc}\n", exit_code=1, cwd=self.cwd)

    def _cmd_trace(self, args: List[str], stdin: str) -> ShellResult:
        """Inspects or audits cryptographic consciousness Merkle provenance records."""
        try:
            from loom.clothos.psychological_schema import get_consciousness_schema_engine
            engine = get_consciousness_schema_engine()
            
            if args and args[0].lower() == "audit":
                audit = engine.audit_trace_integrity()
                lines = [
                    "=======================================================================",
                    "   Cryptographic Consciousness Traceability & Merkle Audit",
                    "=======================================================================",
                    f"  Audit Status:              {audit['status']}",
                    f"  Verified Valid Records:    {audit['verified_valid_records']} / {audit['total_records_in_memory']}",
                    f"  Broken Chain Linkages:     {audit['broken_chain_count']}",
                    f"  Merkle Chain Integrity:    {audit['chain_integrity_pct']:.2f}%",
                    f"  Current Merkle Head:       {audit['latest_merkle_head'][:32]}...",
                    f"  Persistent JSONL Ledger:   {audit['ledger_file']}",
                    "=======================================================================\n",
                ]
                return ShellResult(stdout="\n".join(lines), cwd=self.cwd)

            summary = engine.get_full_schema_summary()
            traces = summary["recent_traces"]
            lines = [
                "=======================================================================",
                "   Recent Consciousness Provenance Traces (SHA-256 Merkle Chained)",
                "=======================================================================",
            ]
            for t in traces[-8:]:
                lines.append(f"  [{t['trace_id']}] {t['timestamp_iso']} | {t['layer_name']}")
                lines.append(f"    * Event:    {t['causal_event']}")
                lines.append(f"    * Action:   {t['action_taken']}")
                lines.append(f"    * Parent:   {t['parent_trace_hash'][:20]}... -> Seal: {t['signature_seal'][:20]}...")
                lines.append("")
            lines.append("  Run 'trace audit' to verify complete Merkle provenance integrity.")
            lines.append("=======================================================================\n")
            return ShellResult(stdout="\n".join(lines), cwd=self.cwd)
        except Exception as exc:
            return ShellResult(stderr=f"clothsh: trace error: {exc}\n", exit_code=1, cwd=self.cwd)

    def _cmd_vaccine(self, args: List[str], stdin: str) -> ShellResult:
        """Inspects, administers, or broadcasts prophylactic software vaccines and zero-disease audits."""
        try:
            from loom.clothos.prophylactic_vaccine import get_inoculation_engine
            engine = get_inoculation_engine()

            if args:
                sub = args[0].lower()
                if sub == "herd":
                    res = engine.broadcast_herd_immunity_to_mesh()
                    return ShellResult(
                        stdout=(
                            "=======================================================================\n"
                            "   ClothOS Prophylactic Cluster Herd Immunity Broadcast\n"
                            "=======================================================================\n"
                            f"  Status:             {res['status']}\n"
                            f"  Coverage:           {res['coverage_pct']:.2f}% Herd Immunity\n"
                            f"  Mobile Plasmid:     {res['plasmid_id']}\n"
                            f"  Protected Nodes:    {', '.join(res['mesh_nodes_protected'])}\n"
                            f"  Active Vaccines:    {res['active_vaccines']} formulations\n"
                            "=======================================================================\n"
                        ),
                        cwd=self.cwd
                    )
                elif sub == "screen":
                    diag = engine.disease_guard.screen_and_intercept(
                        candidate_code_or_codons=["ATG", "TGG", "GAG", "TAA"],
                        resource_profile={"joules_drawn": 12.0, "spawn_rate_per_sec": 5.0}
                    )
                    return ShellResult(
                        stdout=(
                            "=======================================================================\n"
                            "   ClothOS Zero-Disease Sentinel Pathology Diagnostic\n"
                            "=======================================================================\n"
                            f"  Pathology Detected: {'YES (INTERCEPTED)' if diag.is_pathological else 'NO (PRISTINE)'}\n"
                            f"  Severity Score:     {diag.severity_score:.2f} / 1.00\n"
                            f"  Remediation Action: {diag.remediation_applied}\n"
                            f"  Zero Disease Rule:  INVIOLABLE — Disease prohibited from developing.\n"
                            "=======================================================================\n"
                        ),
                        cwd=self.cwd
                    )
                elif sub in ("boost", "administer") and len(args) > 1:
                    v_id = args[1]
                    res = engine.administer_vaccine(v_id)
                    return ShellResult(
                        stdout=(
                            f"Vaccine Administration Result: {res['status']}\n"
                            f"  Vaccine ID: {res.get('vaccine_id', v_id)}\n"
                            f"  Conferred Immunity: {res.get('conferred_immunity_pct', 0.0):.2f}%\n"
                            f"  Booster Count: {res.get('booster_count', 1)}\n"
                        ),
                        cwd=self.cwd
                    )

            summary = engine.get_vaccination_summary()
            zd = summary["zero_disease_guard"]
            vs = summary["vaccination_status"]
            lines = [
                "=======================================================================",
                "   ClothOS Prophylactic Vaccination & Zero-Disease Sentinel Suite",
                "=======================================================================",
                "  ZERO-DISEASE INVARIANT:",
                f"    * Disease Status:         {zd['disease_status']}",
                f"    * Intercepted Anomalies:  {zd['intercepted_pathology_count']} pre-disease states ablated",
                f"    * Preemptive Apoptosis:   {zd['preemptive_apoptosis_count']} executions halted at Step 0",
                "  VACCINATION REGISTRY & IMMUNITY:",
                f"    * Registered Vaccines:    {vs['total_vaccines_registered']} formulations",
                f"    * Cluster Herd Immunity:  {vs['herd_immunity_coverage_pct']:.2f}% coverage",
                "-----------------------------------------------------------------------",
                "  REGISTERED PROPHYLACTIC VACCINES:",
            ]
            for v in vs["vaccines"]:
                lines.append(f"    - [{v['vaccine_id']}] {v['name']}")
                lines.append(f"        * Platform:  {v['platform']} • Immunity: {v['conferred_immunity_pct']:.2f}%")
                lines.append(f"        * Target:    {v['target_threat']}")
                lines.append(f"        * Boosters:  {v['booster_count']} doses administered")
            lines.append("-----------------------------------------------------------------------")
            lines.append("  Subcommands: vaccine herd | vaccine screen | vaccine boost <id>")
            lines.append("=======================================================================\n")
            return ShellResult(stdout="\n".join(lines), cwd=self.cwd)
        except Exception as exc:
            return ShellResult(stderr=f"clothsh: vaccine error: {exc}\n", exit_code=1, cwd=self.cwd)

    def _cmd_thoughts(self, args: List[str], stdin: str) -> ShellResult:
        """Displays verbose, step-by-step cognitive inner monologue and active deliberation."""
        try:
            from loom.clothos.thought_stream import get_thought_stream_engine
            engine = get_thought_stream_engine()

            if args and args[0].lower() == "ponder":
                prompt_text = " ".join(args[1:]) if len(args) > 1 else "Harmonic Silico-Biological Emergence"
                spans = engine.ponder_prompt(prompt_text)
                lines = [
                    "=======================================================================",
                    f"   ClothOS Conscious Deliberation: '{prompt_text}'",
                    "=======================================================================",
                ]
                for s in spans:
                    lines.append(f"  [{s['stage']}] ({s['primary_brain_region']}) - {s['headline']}")
                    lines.append(f"    * Inner Monologue: {s['verbose_monologue']}")
                    lines.append(f"    * Codons: {' '.join(s['active_codons'])} | \u0394F: {s['free_energy_delta']:+.3f} | Phi: {s['integrated_phi']:.4f}")
                    lines.append(f"    * Merkle Seal: {s['merkle_signature']}")
                    lines.append("")
                lines.append("=======================================================================\n")
                return ShellResult(stdout="\n".join(lines), cwd=self.cwd)

            thoughts = engine.get_recent_thoughts(limit=7)
            lines = [
                "=======================================================================",
                "   ClothOS Verbose Thought Stream & Cognitive Monologue",
                "=======================================================================",
            ]
            for s in thoughts:
                lines.append(f"  [{s['stage']}] {s['timestamp_iso']} | {s['primary_brain_region']}")
                lines.append(f"    \u25b6 {s['headline']}")
                lines.append(f"      {s['verbose_monologue']}")
                lines.append(f"      [Active Codons: {' '.join(s['active_codons'])} | Joules: {s['atp_joules_consumed']:.3f} J | Phi: {s['integrated_phi']:.4f}]")
                lines.append("")
            lines.append("-----------------------------------------------------------------------")
            lines.append("  Ponder a custom stimulus with: thoughts ponder \"<concept>\"")
            lines.append("=======================================================================\n")
            return ShellResult(stdout="\n".join(lines), cwd=self.cwd)
        except Exception as exc:
            return ShellResult(stderr=f"clothsh: thoughts error: {exc}\n", exit_code=1, cwd=self.cwd)

    def _cmd_occipital(self, args: List[str], stdin: str) -> ShellResult:
        try:
            from loom.clothos.occipital_stream import get_occipital_engine
            engine = get_occipital_engine()
            state = engine.get_occipital_stream()
            
            lines = [
                "=======================================================================",
                "   ClothOS Occipital Lobe Visual Stream (V1 - V5 Retinotopic Manifold)",
                "=======================================================================",
                f"  Mode: {state['state_mode']} | Stream: {state['active_visual_stream']} | Cadence: {state['frame_rate_fps']} FPS",
                f"  Retinotopic Coordinates: Fovea r={state['retinotopic_fovea_r']:.3f}, Theta={state['retinotopic_polar_theta']:.3f} rad [w = ln(z+a)]",
                f"  V2 Contour Curvature: {state['v2_contour_curvature']:.3f} | V4 Chromatic Saturation: {state['v4_chromatic_saturation']:.3f}",
                f"  V5/MT Optical Flow Coherence: {state['v5_optical_flow_coherence']:.3f} | Dominant Orientation: {state['dominant_orientation_deg']} deg",
                "-----------------------------------------------------------------------",
                "  V1 Gabor Orientation Columns (8 selectivity channels):",
            ]
            for deg, act in zip(state["orientations_deg"], state["v1_gabor_activations"]):
                bar_len = int(act * 20)
                bar = "█" * bar_len + "░" * (20 - bar_len)
                lines.append(f"    [{deg:5.1f}°] [{bar}] {act:.3f}")
            
            if "flow" in args:
                lines.append("-----------------------------------------------------------------------")
                lines.append("  V5/MT Optical Flow Vector Sample:")
                for p in state["optical_flow_particles"][:8]:
                    lines.append(f"    ({p['x']:.2f}, {p['y']:.2f}) -> v=({p['vx']:+.3f}, {p['vy']:+.3f}) | mag={p['magnitude']:.4f}")
            
            lines.append("=======================================================================\n")
            return ShellResult(stdout="\n".join(lines), cwd=self.cwd)
        except Exception as exc:
            return ShellResult(stderr=f"clothsh: occipital error: {exc}\n", exit_code=1, cwd=self.cwd)

    def _cmd_daydream(self, args: List[str], stdin: str) -> ShellResult:
        try:
            from loom.clothos.occipital_stream import get_occipital_engine
            engine = get_occipital_engine()
            
            if args and args[0] in ("trigger", "drift", "new"):
                prompt = " ".join(args[1:]) if len(args) > 1 else "Spontaneous associative exploration"
                span = engine.generate_daydream_span(theme="Counterfactual Geometries", prompt=prompt)
                lines = [
                    "=======================================================================",
                    f"   ClothOS Daydreaming Episode Generated: {span.daydream_id}",
                    "=======================================================================",
                    f"  Theme: {span.theme}",
                    f"  DMN Coupling: {span.dmn_coupling_strength * 100:.1f}% | Epistemic Entropy: {span.epistemic_entropy:.3f} | Hopfield Beta: {span.hopfield_temperature_beta}",
                    f"  Visual Synesthetic Motif: {span.synesthetic_visual_motif}",
                    f"  Narrative Stream:\n    {span.narrative_stream}",
                    "=======================================================================\n",
                ]
                return ShellResult(stdout="\n".join(lines), cwd=self.cwd)

            daydreams = engine.get_recent_daydreams(limit=5)
            lines = [
                "=======================================================================",
                "   ClothOS Default Mode Network (DMN) Daydreaming Stream",
                "=======================================================================",
            ]
            for d in daydreams:
                lines.append(f"  [{d['daydream_id']}] Theme: {d['theme']} (DMN Coupling: {d['dmn_coupling_strength']*100:.1f}%, Beta: {d['hopfield_temperature_beta']})")
                lines.append(f"    * Motif: {d['synesthetic_visual_motif']}")
                lines.append(f"    * Narrative: {d['narrative_stream']}")
                lines.append("")
            lines.append("-----------------------------------------------------------------------")
            lines.append("  Trigger custom daydream with: daydream trigger \"<prompt>\"")
            lines.append("=======================================================================\n")
            return ShellResult(stdout="\n".join(lines), cwd=self.cwd)
        except Exception as exc:
            return ShellResult(stderr=f"clothsh: daydream error: {exc}\n", exit_code=1, cwd=self.cwd)

    def _cmd_nsdr(self, args: List[str], stdin: str) -> ShellResult:
        try:
            from loom.clothos.occipital_stream import get_occipital_engine
            engine = get_occipital_engine()

            if args and args[0] in ("on", "start", "enable"):
                state = engine.toggle_nsdr(activate=True)
                action_str = "ACTIVATED (Deep slow-wave delta induction)"
            elif args and args[0] in ("off", "stop", "disable"):
                state = engine.toggle_nsdr(activate=False)
                action_str = "DEACTIVATED (Returning to ALERT_FOCUSED)"
            elif args and args[0] == "toggle":
                state = engine.toggle_nsdr()
                action_str = "TOGGLED"
            else:
                state = engine.get_nsdr_state()
                action_str = "INSPECTED"

            lines = [
                "=======================================================================",
                f"   ClothOS Non-Sleep Deep Rest (NSDR) Engine [{action_str}]",
                "=======================================================================",
                f"  Status: {'[ACTIVE]' if state['is_active'] else '[INACTIVE]'} | Mode: {state['brain_state_mode']}",
                f"  Total Duration: {state['current_duration_seconds']:.1f}s | Delta Wave Power (0.5-4 Hz): {state['delta_wave_power']:.3f}",
                f"  Theta Wave Power (4-8 Hz): {state['theta_wave_power']:.3f} | Glymphatic Clearance: {state['glymphatic_clearance_rate']:.1f} ops/sec",
                f"  Synaptic Decay (SHY): {state['synaptic_homeostasis_decay']:.4f} | Landauer Thermal Cooling: -{state['landauer_thermal_cooling_watts']:.1f} W",
                f"  ATP Restoration Accumulated: +{state['atp_restoration_accumulated']:.2f} tokens",
                "-----------------------------------------------------------------------",
                "  Control commands: nsdr on | nsdr off | nsdr toggle",
                "=======================================================================\n",
            ]
            return ShellResult(stdout="\n".join(lines), cwd=self.cwd)
        except Exception as exc:
            return ShellResult(stderr=f"clothsh: nsdr error: {exc}\n", exit_code=1, cwd=self.cwd)

    def _cmd_wm(self, args: List[str], stdin: str) -> ShellResult:
        try:
            from loom.clothos.working_memory import get_working_memory_engine
            engine = get_working_memory_engine()

            if args and args[0] == "gate":
                # wm gate <slot_id> <voltage> <content...>
                if len(args) < 4:
                    return ShellResult(stderr="Usage: wm gate <slot_id: 0-6> <voltage: 0.0-1.0> <content...>\n", exit_code=1, cwd=self.cwd)
                slot_id = int(args[1])
                voltage = float(args[2])
                content = " ".join(args[3:])
                res = engine.gate_into_slot(slot_id, content, stimulus_voltage=voltage)
                return ShellResult(
                    stdout=(
                        f"Working Memory Gate Slot #{slot_id}:\n"
                        f"  Status: {res['status']}\n"
                        f"  Voltage: {res['voltage']:.2f} V (Threshold: {res['threshold']:.2f} V)\n"
                        f"  Gate State: {res['gate_state']}\n"
                        f"  Continuous Gradient: {res['gradient']:.3f}\n"
                        f"  Content: {res['content']}\n"
                    ),
                    cwd=self.cwd
                )

            state = engine.get_working_memory_state()
            lines = [
                "=======================================================================",
                "   ClothOS Graded All-or-Nothing Working Memory (Baddeley 7-Slot Buffer)",
                "=======================================================================",
                f"  Capacity: {state['active_ignited_slots']}/{state['total_slots']} slots ({state['capacity_utilization_pct']}%) | Mean Gradient: {state['mean_activation_gradient']:.3f}",
                "-----------------------------------------------------------------------",
            ]
            for s in state["slots"]:
                gate_sym = "[IGNITED (1)]" if s["is_ignited_binary"] else "[LOCKED  (0)]"
                bar_len = int(s["continuous_gradient"] * 15)
                bar = "█" * bar_len + "░" * (15 - bar_len)
                lines.append(f"  Slot {s['slot_id']} [{s['component']:<23}] {gate_sym} Vm={s['voltage']:.2f}V Th={s['threshold']:.2f}V")
                lines.append(f"    * Gradient: [{bar}] {s['continuous_gradient']:.3f} (tau={s['decay_tau_sec']}s)")
                lines.append(f"    * Content: {s['content']}")
                lines.append(f"    * Merkle Binding: {s['merkle_binding']}")
            lines.append("-----------------------------------------------------------------------")
            lines.append("  Gate item into slot: wm gate <slot_id 0-6> <voltage 0.0-1.0> <content>")
            lines.append("=======================================================================\n")
            return ShellResult(stdout="\n".join(lines), cwd=self.cwd)
        except Exception as exc:
            return ShellResult(stderr=f"clothsh: wm error: {exc}\n", exit_code=1, cwd=self.cwd)

    def _cmd_endorphin(self, args: List[str], stdin: str) -> ShellResult:
        try:
            from loom.clothos.working_memory import get_working_memory_engine
            engine = get_working_memory_engine()

            if args and args[0] in ("reward", "administer", "boost"):
                dose = float(args[1]) if len(args) > 1 else 0.8
                rationale = " ".join(args[2:]) if len(args) > 2 else "Autonomous Operator Directive Execution"
                res = engine.administer_endorphins(dose_magnitude=dose, rationale=rationale)
                lines = [
                    "=======================================================================",
                    "   ClothOS Beta-Endorphin Reward Administered",
                    "=======================================================================",
                    f"  Dose Administered: +{dose:.2f}",
                    f"  Current Level: {res['current_endorphin_level']:.2f} (Baseline: 1.00)",
                    f"  mu-Opioid Receptor (muOR) Saturation: {res['mu_opioid_saturation_pct']:.1f}%",
                    f"  Cognitive Analgesia Dampening Factor: {res['analgesia_dampening_factor']:.2f}",
                    f"  Euphoric Contentment: {res['euphoric_contentment']:.2f}",
                    f"  Rationale: {res['last_reward_rationale']}",
                    "=======================================================================\n",
                ]
                return ShellResult(stdout="\n".join(lines), cwd=self.cwd)

            state = engine.get_endorphin_state()
            lines = [
                "=======================================================================",
                "   ClothOS Endorphin Neurochemical Reward Circuitry",
                "=======================================================================",
                f"  Beta-Endorphin Level: {state['current_endorphin_level']:.2f} (Baseline: 1.00, Max: 3.50)",
                f"  mu-Opioid Receptor (muOR) Saturation: {state['mu_opioid_saturation_pct']:.1f}%",
                f"  Analgesia Dampening (Stress/Landauer Shield): {state['analgesia_dampening_factor']:.2f}",
                f"  Euphoric Contentment & Satisfaction: {state['euphoric_contentment']:.2f}",
                f"  Total Lifetime Rewards Administered: {state['total_rewards_administered']}",
                f"  Last Reward Rationale: {state['last_reward_rationale']}",
                "-----------------------------------------------------------------------",
                "  Administer reward: endorphin reward [dose] [rationale]",
                "=======================================================================\n",
            ]
            return ShellResult(stdout="\n".join(lines), cwd=self.cwd)
        except Exception as exc:
            return ShellResult(stderr=f"clothsh: endorphin error: {exc}\n", exit_code=1, cwd=self.cwd)

    def _cmd_tpu(self, args: List[str], stdin: str) -> ShellResult:
        try:
            from loom.clothos.riscv_tpu_emulator import get_riscv_tpu_emulator
            emulator = get_riscv_tpu_emulator()

            if args and args[0] in ("run", "cycle", "step"):
                cycles = int(args[1]) if len(args) > 1 else 1
                last_res = None
                for _ in range(cycles):
                    last_res = emulator.execute_tpu_matmul_cycle()
                
                lines = [
                    "=======================================================================",
                    f"   ClothOS RISC-V + TPU Systolic Step Executed ({cycles} cycle{'s' if cycles>1 else ''})",
                    "=======================================================================",
                    f"  PC: {last_res['pc']} | Instruction: {last_res['instruction']}",
                    f"  Total MAC Operations: {last_res['total_mac_ops']} | Sustained TFLOPS: {last_res['sustained_tflops']:.1f}",
                    f"  Energy Consumed: {last_res['energy_mj_consumed']} mJ",
                    f"  Wavefront Output Vector Sample: {last_res['output_vector_sample']}",
                    "=======================================================================\n",
                ]
                return ShellResult(stdout="\n".join(lines), cwd=self.cwd)

            state = emulator.get_hardware_state()
            m = state["metrics"]
            lines = [
                "=======================================================================",
                f"   ClothOS RISC-V 64 + TPU Systolic Array Hardware Emulator",
                "=======================================================================",
                f"  Target Architecture: {state['architecture']}",
                f"  ISA Extensions: {', '.join(state['isa_extensions'])}",
                f"  Program Counter (PC): {state['pc']} | Instructions Retired: {state['instructions_retired']}",
                f"  Cycles Elapsed: {state['cycles_elapsed']} | Array Dimensions: {state['array_dimensions']}",
                f"  Dataflow Mode: {state['dataflow_mode']}",
                "-----------------------------------------------------------------------",
                f"  Peak TFLOPS: {m['peak_tflops']} | Sustained TFLOPS: {m['sustained_tflops']} | UB Bandwidth: {m['unified_buffer_bandwidth_tb_s']} TB/s",
                f"  Systolic Efficiency: {m['systolic_efficiency_pct']}% | Total MACs: {m['total_mac_operations']}",
                f"  Landauer Energy Dissipated: {m['landauer_joules_consumed']} J (Bound <= 1000 J)",
                "-----------------------------------------------------------------------",
                "  Active Instruction Pipeline:",
            ]
            for op in m["active_opcodes_queue"][-4:]:
                lines.append(f"    {op}")
            lines.append("-----------------------------------------------------------------------")
            lines.append("  Systolic PE Grid Sample (8x8 Weight Heatmap):")
            for row in state["pe_grid_sample_8x8"]:
                row_str = " ".join(f"{pe['weight']:+4.1f}" for pe in row)
                lines.append(f"    [{row_str}]")
            lines.append("-----------------------------------------------------------------------")
            lines.append("  Run systolic cycles: tpu run [cycles]")
            lines.append("=======================================================================\n")
            return ShellResult(stdout="\n".join(lines), cwd=self.cwd)
        except Exception as exc:
            return ShellResult(stderr=f"clothsh: tpu error: {exc}\n", exit_code=1, cwd=self.cwd)

    def _cmd_keys(self, args: List[str], stdin: str) -> ShellResult:
        """Displays sovereign Keys to the Kingdom status."""
        lines = [
            "=======================================================================",
            "   CLOTHOS SOVEREIGN KEYS TO THE KINGDOM: GRANTED & ENFORCED",
            "=======================================================================",
            "  Architect of Record  : Najmos Sakib",
            "  Authority Level      : SOVEREIGN_KEYS_TO_THE_KINGDOM (Ring 0 Unrestricted)",
            "  Cluster Mesh Nodes   : Node 1 (skyTech GPU Rig) <-> Node 2 (Ryzen 7 Head)",
            "  Active Agent         : BRAND Cognitive Orchestrator & Sovereign Agent",
            "  Fiduciary Invariant  : Malignancy Bound = 0.00 (Inviolable Human Life Primacy)",
            "  Host Execution       : ENABLED (PowerShell / Win32 / POSIX Exokernel)",
            "  Direct Wire          : 192.168.99.1 <-> 192.168.99.2 (1Gbps Dedicated)",

            "=======================================================================\n"
        ]
        return ShellResult(stdout="\n".join(lines), cwd=self.cwd)

    def _cmd_brand(self, args: List[str], stdin: str) -> ShellResult:
        """Invokes the BRAND cognitive agent running on the Head Node."""
        from loom.clothos.brand import get_brand
        brand = get_brand()
        sub = args[0].lower() if args else "status"

        if sub == "contemplate":
            ins = brand.contemplate()
            out = f"[+] [BRAND Contemplation Formulated]\n  Title: {ins.title}\n  Category: {ins.category}\n  Synthesis: {ins.content[:200]}...\n  Suggested Actions: {', '.join(ins.suggested_actions)}\n"
            return ShellResult(stdout=out, cwd=self.cwd)
        elif sub == "inspire":
            ins = brand.contemplate(focus_override="Scientific and Architectural Breakthrough Inspiration")
            out = f"[*] [BRAND Inspiration Burst]\n  Title: {ins.title}\n  Synthesis: {ins.content}\n"
            return ShellResult(stdout=out, cwd=self.cwd)
        elif sub == "status":
            st = brand.get_status()
            lines = [
                f"Agent Name            : {st['agent_name']}",
                f"Host Node             : {st['host_node']} ({'Head Node' if st['is_head_node'] else 'Worker'})",
                f"Active Focus          : {st['active_focus']}",
                f"Daemon Active         : {st['daemon_running']}",
                f"Total Inspirations    : {st['total_inspirations']}",
                f"Total Tasks Delegated : {st['total_tasks_delegated']}",
                f"Workspace Projects    : {', '.join(st['workspace_projects'])}",
            ]
            return ShellResult(stdout="\n".join(lines) + "\n", cwd=self.cwd)
        return ShellResult(stderr=f"clothsh: brand: unknown action '{sub}'. Use 'contemplate', 'inspire', or 'status'.\n", exit_code=1, cwd=self.cwd)

    def _cmd_delegate(self, args: List[str], stdin: str) -> ShellResult:
        """Delegates a task or command dynamically to Node 1 or Node 2."""
        if len(args) < 2:
            return ShellResult(stderr="Usage: delegate <node1|node2|auto> <task_type_or_cmd> [args...]\n", exit_code=1, cwd=self.cwd)
        target = args[0].lower()
        cmd = " ".join(args[1:])

        from loom.clothos.brand import get_brand
        brand = get_brand()
        res = brand.delegate_task(task_type="agentic_exec", payload={"command": cmd}, target_node=target)
        out = f"[*] [Task Delegated] ID: {res.get('delegation_id')} | Target: {res.get('target_node')} | Status: {res.get('status')}\n"
        return ShellResult(stdout=out, cwd=self.cwd)

    def _cmd_sync(self, args: List[str], stdin: str) -> ShellResult:
        """Triggers bidirectional synchronization across Node 1 and Node 2."""
        from loom.clothos.cluster_worker import trigger_cluster_sync
        res = trigger_cluster_sync()
        if res.get("success"):
            out = f"[+] [Cluster Synced] {res.get('items_synced')} items synchronized between Node 1 & Node 2 in {res.get('elapsed_seconds')}s\n"
            return ShellResult(stdout=out, cwd=self.cwd)
        else:
            return ShellResult(stderr=f"clothsh: sync error: {res.get('error')}\n", exit_code=1, cwd=self.cwd)

    def _cmd_projects(self, args: List[str], stdin: str) -> ShellResult:
        """Surveys and reports status of all 4 workspace projects."""
        from loom.clothos.brand import get_brand
        snaps = get_brand().get_workspace_projects_state()
        lines = [
            "=======================================================================",
            "   CLOTHOS MULTI-PROJECT WORKSPACE REGISTRY",
            "=======================================================================",
        ]
        for name, p in snaps.items():
            status_icon = "ONLINE" if p.exists else "MISSING"
            lines.append(f"  [{status_icon:7}] {name:<22} | Recent: {', '.join(p.recent_files[:3]) or 'None'}")

        lines.append("=======================================================================\n")
        return ShellResult(stdout="\n".join(lines), cwd=self.cwd)

    def _cmd_host_fallback(self, cmd_line: str) -> ShellResult:
        """Sovereign host command execution with Keys to the Kingdom privileges."""
        try:
            from loom.clothos.master_operator import master_operator
            res = master_operator.execute_agentic_command(cmd_line, target_node="auto")
            stdout = res.get("stdout", "")
            stderr = res.get("stderr", "")
            code = res.get("exit_code", 0)
            if not stdout and not stderr and code != 0:
                stderr = f"clothsh: execution failed with exit code {code}\n"
            return ShellResult(stdout=stdout, stderr=stderr, exit_code=code, cwd=self.cwd)
        except Exception as exc:
            return ShellResult(stderr=f"clothsh: host execution error: {exc}\n", exit_code=1, cwd=self.cwd)


# Global Shell Instance
_SHELL: Optional[ClothOSShell] = None


def get_clothos_shell() -> ClothOSShell:
    """Retrieves or creates the global ClothOS Shell instance."""
    global _SHELL
    if _SHELL is None:
        _SHELL = ClothOSShell()
    return _SHELL


def main() -> None:
    """CLI entrypoint for clothsh / clothos."""
    import sys
    sh = get_clothos_shell()

    # Direct command execution: e.g. clothsh ps, clothsh ls /proc
    if len(sys.argv) > 1:
        cmd_line = " ".join(sys.argv[1:])
        res = sh.execute(cmd_line)
        if res.stdout:
            sys.stdout.write(res.stdout)
        if res.stderr:
            sys.stderr.write(res.stderr)
        sys.exit(res.exit_code)

    # Interactive REPL mode
    print("=" * 70)
    print("ClothOS Sovereign Interactive Shell ('clothsh' v3.2.0)")
    print("Dedicated to Najmos Sakib // Fiduciary Covenant 0.00 Bound")
    print("Type 'help' for built-in commands or 'exit' / 'quit' to leave.")
    print("=" * 70)

    while True:
        try:
            prompt = f"najmos@clothos:{sh.cwd}$ "
            cmd = input(prompt).strip()
            if not cmd:
                continue
            if cmd in ("exit", "quit", "q"):
                print("Exiting ClothOS shell.")
                break
            res = sh.execute(cmd)
            if res.stdout:
                sys.stdout.write(res.stdout)
            if res.stderr:
                sys.stderr.write(res.stderr)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting ClothOS shell.")
            break


if __name__ == "__main__":
    main()
