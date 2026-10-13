"""
LOOM FABRIC COMMAND CENTER — Sovereign Heterogeneous Compute & Zero-Trust Orchestration GUI.

All-in-One Cross-Platform Application (Windows, macOS, Linux) for Single-Node & Dual-Machine Clusters:
- MASTER CLUSTER BAR: 1-Click Start All, Stop & Sanitize Ports, Restart Both Machines, Stop Both Machines, and Open Gateway in Separate Terminal Window.
- THE WEAVE: Physical Cluster Hardware Topology, Live Dual-Node Port Matrix & Service Orchestration Log (skyTech 192.168.99.1 + Ryzen Head 192.168.99.2).
- THE SHUTTLE: Multi-Model Inference Dispatcher, Layer Sharding Telemetry & SSE Streaming Console.
- TORQUE VAULT: Sovereign Zero-Trust IP/PII De-identification, Rehydration Mapping & Cloud Arbitrage Audit.
- THE SPOOL: Preset Model Registry, Quantization Footprints & Memory Budgets.

Cross-Platform Compatibility:
- Windows 10/11 (Direct3D/WDDM, Win32 Job Objects, detached cmd.exe / PowerShell consoles)
- macOS (Apple Silicon M-Series Metal Unified Memory & Intel, Terminal.app via osascript, lsof port sanitizer)
- Linux / WSL2 (Ubuntu, Debian, Fedora, Arch — CUDA / ROCm / Vulkan, x-terminal-emulator / gnome-terminal, lsof/fuser port sanitizer)
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import platform
import shutil
import socket
import subprocess
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Callable, Dict, List, Optional
import urllib.request
import urllib.error

# Botanical Meadow & Floral Breeze Palette with Royal Purple Accents
CLR_OBSIDIAN = "#07120a"      # Deep Forest Night Canvas
CLR_SURFACE = "#0d1e12"       # Meadow Surface
CLR_CARD = "#122818"          # Foliage Card Surface
CLR_BORDER = "#1d3d28"        # Dewstem Border
CLR_PURPLE = "#a855f7"        # Electric Violet Primary Accent (Mandated)
CLR_AMETHYST = "#c084fc"      # Wisteria Blossom Highlight
CLR_DEEP_PURPLE = "#7e22ce"   # Deep Royal Orchid
CLR_LILAC = "#e9d5ff"         # Morning Lilac Text
CLR_LAWN = "#10b981"          # Lush Lawn Emerald
CLR_CLOVER = "#34d399"        # Spring Clover Accent
CLR_MINT = "#6ee7b7"          # Morning Dew Mint
CLR_BREEZE = "#38bdf8"        # Air & Morning Breeze Sky
CLR_EMERALD = "#10b981"       # Online / Healthy Status
CLR_AMBER = "#f59e0b"         # Warning / Routing
CLR_CRIMSON = "#ef4444"       # Error / Offline
CLR_TEXT = "#f0fdf4"          # Pure Spring White
CLR_MUTED = "#bbf7d0"         # Pale Foliage Muted Text

MASTER_TOKEN = "G-GzcZEzqteW241i720XeH5UNT73T6qk"
MANAGED_PORTS = [8000, 8002, 8080, 5555, 18789, 6379, 8265]


class CrossPlatformClusterController:
    """All-in-one cross-platform service launcher & port sanitizer for Windows, macOS, and Linux."""

    def __init__(self, log_callback: Optional[Callable[[str], None]] = None):
        self.sys_name = platform.system().lower()  # 'windows', 'darwin', 'linux'
        self.hostname = socket.gethostname()
        self.is_skytech = "skytech" in self.hostname.lower()
        self.self_ip = "192.168.99.1" if self.is_skytech else "192.168.99.2"
        self.peer_ip = "192.168.99.2" if self.is_skytech else "192.168.99.1"
        self.loom_dir = Path(__file__).resolve().parent.parent
        self.stitch_dir = self._resolve_stitch_dir()
        self.log_callback = log_callback

    def log(self, msg: str) -> None:
        stamp = time.strftime("%H:%M:%S")
        line = f"[{stamp}] {msg}"
        if self.log_callback:
            self.log_callback(line)
        else:
            print(line)

    def _resolve_stitch_dir(self) -> Path:
        candidates = [
            self.loom_dir.parent / "stitch-core",
            Path.home() / "Documents" / "stitch-core",
            Path.home() / "stitch-core",
            Path("C:/stitch-core"),
            Path.home() / "Documents" / "antigravity-fabric",
            Path.home() / "antigravity-fabric",
        ]
        for c in candidates:
            if (c / "bridge" / "server.py").exists():
                return c
        return candidates[0]

    def resolve_python(self, for_stitch: bool = False) -> str:
        """Finds a working Python interpreter across Windows, macOS, and Linux."""
        candidates: List[Path] = []
        if self.sys_name == "windows":
            if for_stitch:
                candidates.append(self.stitch_dir / ".fabric-env" / "Scripts" / "python.exe")
            candidates.extend([
                self.loom_dir / ".venv" / "Scripts" / "python.exe",
                Path.home() / ".loom" / "env" / "Scripts" / "python.exe",
                Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Python" / "Python312" / "python.exe",
                self.stitch_dir / ".fabric-env" / "Scripts" / "python.exe",
                Path(sys.executable),
            ])
        else:
            if for_stitch:
                candidates.append(self.stitch_dir / ".fabric-env" / "bin" / "python")
            candidates.extend([
                self.loom_dir / ".venv" / "bin" / "python",
                Path.home() / ".loom" / "env" / "bin" / "python",
                Path(sys.executable),
            ])

        clean_env = os.environ.copy()
        for k in ("__PYVENV_LAUNCHER__", "VIRTUAL_ENV", "PYTHONPATH", "PYTHONHOME", "UV_INTERNAL__PYTHONHOME"):
            clean_env.pop(k, None)
        check_stmt = "import uvicorn, fastapi, jinja2" if for_stitch else "import uvicorn, fastapi"
        for cand in candidates:
            if cand and cand.exists():
                try:
                    res = subprocess.run(
                        [str(cand), "-c", check_stmt],
                        capture_output=True,
                        env=clean_env,
                        timeout=8,
                    )
                    if res.returncode == 0:
                        return str(cand)
                except Exception:
                    continue
        return sys.executable or ("python" if self.sys_name == "windows" else "python3")

    @staticmethod
    def is_port_open(host: str, port: int, timeout: float = 0.6) -> bool:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except Exception:
            return False

    def sanitize_local_ports(self, ports: Optional[List[int]] = None, include_ollama: bool = False) -> int:
        """Kills stale processes holding target TCP ports across Windows, macOS, and Linux."""
        target_ports = list(ports or [8000, 8002, 8080, 5555, 18789])
        if include_ollama and 11434 not in target_ports:
            target_ports.append(11434)

        killed = 0
        my_pid = os.getpid()
        parent_pid = os.getppid()

        if self.sys_name == "windows":
            try:
                out = subprocess.check_output("netstat -ano", shell=True, text=True, stderr=subprocess.DEVNULL)
                pids_to_kill: Dict[int, int] = {}
                for line in out.splitlines():
                    if "LISTENING" not in line:
                        continue
                    for p in target_ports:
                        if f":{p} " in line:
                            parts = line.split()
                            try:
                                pid = int(parts[-1])
                                if pid > 4 and pid not in (my_pid, parent_pid):
                                    pids_to_kill[pid] = p
                            except ValueError:
                                pass
                for pid, port in pids_to_kill.items():
                    self.log(f"Sanitizing local port :{port} (terminating PID {pid})...")
                    subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)
                    killed += 1
            except Exception as e:
                self.log(f"Port scan warning: {e}")

            # Also clean up WSL background gateway if WSL exists
            if shutil.which("wsl"):
                try:
                    subprocess.run(
                        ["wsl", "-d", "Ubuntu", "-u", "nasakib", "--", "bash", "-lc", "pkill -f 'uvicorn loom.gateway' || true"],
                        capture_output=True,
                        timeout=4,
                    )
                except Exception:
                    pass
        else:
            # macOS & Linux port sanitizer using lsof / fuser
            for p in target_ports:
                try:
                    if shutil.which("lsof"):
                        out = subprocess.check_output(["lsof", "-ti", f"tcp:{p}"], text=True, stderr=subprocess.DEVNULL)
                        for pid_str in out.splitlines():
                            pid = int(pid_str.strip())
                            if pid != my_pid:
                                self.log(f"Sanitizing local port :{p} (killing PID {pid})...")
                                subprocess.run(["kill", "-9", str(pid)], capture_output=True)
                                killed += 1
                    elif shutil.which("fuser"):
                        subprocess.run(["fuser", "-k", f"{p}/tcp"], capture_output=True)
                except Exception:
                    pass

        self.log(f"Local port sanitization complete ({killed} process trees cleared).")
        return killed

    def spawn_in_separate_terminal(self, title: str, command_args: List[str], cwd: Path, env: Optional[Dict[str, str]] = None) -> None:
        """Opens a command in a visible separate terminal window on Windows, macOS, or Linux."""
        run_env = os.environ.copy()
        for k in ("__PYVENV_LAUNCHER__", "VIRTUAL_ENV", "PYTHONPATH", "PYTHONHOME", "UV_INTERNAL__PYTHONHOME"):
            run_env.pop(k, None)
        if env:
            run_env.update(env)

        if self.sys_name == "windows":
            cmd_line = subprocess.list2cmdline(command_args)
            full_cmd = f'title {title} && cd /d "{cwd}" && {cmd_line}'
            subprocess.Popen(
                ["cmd.exe", "/k", full_cmd],
                cwd=str(cwd),
                env=run_env,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
        elif self.sys_name == "darwin":
            escaped_cmd = " ".join(f'"{a}"' if " " in a else a for a in command_args)
            apple_script = f'tell application "Terminal" to do script "cd \\"{cwd}\\" && {escaped_cmd}"'
            subprocess.Popen(["osascript", "-e", apple_script], cwd=str(cwd), env=run_env)
        else:
            # Linux desktop terminals
            for term in ["x-terminal-emulator", "gnome-terminal", "konsole", "xfce4-terminal", "xterm"]:
                if shutil.which(term):
                    if term == "gnome-terminal":
                        subprocess.Popen([term, "--title", title, "--", *command_args], cwd=str(cwd), env=run_env)
                    else:
                        subprocess.Popen([term, "-e", " ".join(command_args)], cwd=str(cwd), env=run_env)
                    return
            # Headless fallback
            subprocess.Popen(command_args, cwd=str(cwd), env=run_env, start_new_session=True)

    def _resolve_pythonw(self, base_py: Optional[str] = None) -> str:
        """Resolves a windowless GUI-subsystem pythonw.exe binary on Windows so wt.exe/conhost.exe is never invoked."""
        candidates: List[Path] = []
        if base_py:
            p = Path(base_py)
            candidates.append(p.with_name("pythonw.exe"))
        candidates.extend([
            Path(sys.executable).with_name("pythonw.exe"),
            self.loom_dir / ".venv" / "Scripts" / "pythonw.exe",
            self.stitch_dir / ".fabric-env" / "Scripts" / "pythonw.exe",
            Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Python" / "Python312" / "pythonw.exe",
        ])
        for c in candidates:
            if c.exists():
                return str(c)
        return sys.executable

    def spawn_background_service(
        self,
        command_args: List[str],
        cwd: Path,
        env: Optional[Dict[str, str]] = None,
        log_name: str = "service.log",
    ) -> None:
        """Spawns a 100% windowless background daemon across Windows, macOS, and Linux, logging to ~/.loom/logs/."""
        run_env = os.environ.copy()
        for k in ("__PYVENV_LAUNCHER__", "VIRTUAL_ENV", "PYTHONPATH", "PYTHONHOME", "UV_INTERNAL__PYTHONHOME"):
            run_env.pop(k, None)
        if env:
            run_env.update(env)

        log_dir = Path.home() / ".loom" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / log_name

        if self.sys_name == "windows":
            create_no_window = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
            new_group = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200)
            breakaway = getattr(subprocess, "CREATE_BREAKAWAY_FROM_JOB", 0x01000000)

            # If target executable is python.exe, swap to pythonw.exe (GUI subsystem = zero console window ever)
            actual_args = list(command_args)
            if actual_args and actual_args[0].lower().endswith("python.exe"):
                pw = Path(actual_args[0]).with_name("pythonw.exe")
                if pw.exists():
                    actual_args[0] = str(pw)

            # Only use WMI pythonw.exe breakaway when running inside a remote Ray job (LOOM_WMI_BREAKAWAY=1)
            if os.environ.get("LOOM_WMI_BREAKAWAY") == "1":
                stem = Path(log_name).stem
                runner_py = log_dir / f"run_{stem}.py"
                runner_code = (
                    "import os, subprocess\n"
                    "for k in ('__PYVENV_LAUNCHER__', 'VIRTUAL_ENV', 'PYTHONPATH', 'PYTHONHOME', 'UV_INTERNAL__PYTHONHOME'):\n"
                    "    os.environ.pop(k, None)\n"
                    f"os.environ.update({repr(env or {})})\n"
                    f"log_f = open({repr(str(log_path))}, 'a', encoding='utf-8', errors='replace')\n"
                    f"subprocess.Popen({repr(actual_args)}, cwd={repr(str(cwd))}, stdin=subprocess.DEVNULL, "
                    "stdout=log_f, stderr=log_f, creationflags=0x08000000 | 0x00000200, close_fds=True)\n"
                )
                runner_py.write_text(runner_code, encoding="utf-8")
                pythonw_bin = self._resolve_pythonw(command_args[0] if command_args else None)
                ps_script = (
                    "Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{"
                    f"CommandLine='\"{pythonw_bin}\" \"{runner_py}\"'; "
                    f"CurrentDirectory='{cwd}'}} | Out-Null"
                )
                try:
                    res = subprocess.run(
                        ["powershell.exe", "-NoProfile", "-NonInteractive", "-WindowStyle", "Hidden", "-Command", ps_script],
                        env=run_env,
                        capture_output=True,
                        timeout=8,
                        creationflags=create_no_window,
                    )
                    if res.returncode == 0:
                        return
                except Exception:
                    pass

            # Direct windowless Popen (zero powershell.exe / cmd.exe processes)
            log_file = open(log_path, "a", encoding="utf-8", errors="replace")
            try:
                subprocess.Popen(
                    actual_args,
                    cwd=str(cwd),
                    env=run_env,
                    stdin=subprocess.DEVNULL,
                    stdout=log_file,
                    stderr=log_file,
                    creationflags=create_no_window | new_group | breakaway,
                    close_fds=True,
                )
            except OSError:
                subprocess.Popen(
                    actual_args,
                    cwd=str(cwd),
                    env=run_env,
                    stdin=subprocess.DEVNULL,
                    stdout=log_file,
                    stderr=log_file,
                    creationflags=create_no_window | new_group,
                    close_fds=True,
                )
        else:
            log_file = open(log_path, "a", encoding="utf-8", errors="replace")
            subprocess.Popen(
                command_args,
                cwd=str(cwd),
                env=run_env,
                stdin=subprocess.DEVNULL,
                stdout=log_file,
                stderr=log_file,
                start_new_session=True,
            )

    def _can_spawn_port(self, port: int, force: bool = False, cooldown: float = 20.0) -> bool:
        last_map = getattr(self, "_last_port_spawn", None)
        if last_map is None:
            self._last_port_spawn: Dict[int, float] = {}
            last_map = self._last_port_spawn
        now = time.time()
        if not force and (now - last_map.get(port, 0.0)) < cooldown:
            return False
        last_map[port] = now
        return True

    def ensure_local_services_alive(self, force: bool = False) -> None:
        """Self-healing watchdog check: silently starts any offline core service without opening any terminal window."""
        # 1. Ollama (:11434)
        if not self.is_port_open("127.0.0.1", 11434) and self._can_spawn_port(11434, force=force):
            ollama_bin = shutil.which("ollama")
            if not ollama_bin and self.sys_name == "windows":
                cand = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Ollama" / "ollama.exe"
                if cand.exists():
                    ollama_bin = str(cand)
            if ollama_bin:
                self.log("[Auto-Heal] Starting Ollama Engine silently on 0.0.0.0:11434...")
                self.spawn_background_service(
                    [ollama_bin, "serve"],
                    cwd=self.loom_dir,
                    env={"OLLAMA_HOST": "0.0.0.0:11434"},
                    log_name="ollama.log",
                )

        # 2. The Shuttle / Stitch Bridge (:5555)
        if not self.is_port_open("127.0.0.1", 5555) and (self.stitch_dir / "bridge" / "server.py").exists() and self._can_spawn_port(5555, force=force):
            stitch_py = self.resolve_python(for_stitch=True)
            self.log("[Auto-Heal] Starting The Shuttle (:5555) silently in background...")
            self.spawn_background_service(
                [stitch_py, "-m", "uvicorn", "bridge.server:app", "--host", "0.0.0.0", "--port", "5555"],
                cwd=self.stitch_dir,
                env={"PYTHONPATH": str(self.stitch_dir)},
                log_name="stitch_bridge.log",
            )

        # 3. Loom Fabric Gateway (:8002)
        if not self.is_port_open("127.0.0.1", 8002) and self._can_spawn_port(8002, force=force):
            loom_py = self.resolve_python(for_stitch=False)
            self.log("[Auto-Heal] Starting Loom Fabric Gateway (:8002) silently in background...")
            self.spawn_background_service(
                [loom_py, "-m", "uvicorn", "loom.gateway.app:app", "--host", "0.0.0.0", "--port", "8002"],
                cwd=self.loom_dir,
                env={"PYTHONPATH": str(self.loom_dir), "PYTHONIOENCODING": "utf-8"},
                log_name="loom_gateway.log",
            )

        # 4. OpenClaw Gateway (:18789)
        if not self.is_port_open("127.0.0.1", 18789) and self._can_spawn_port(18789, force=force):
            node_bin = shutil.which("node")
            if not node_bin and self.sys_name == "windows":
                cand = Path(r"C:\Program Files\nodejs\node.exe")
                if cand.exists():
                    node_bin = str(cand)
            oc_script = Path(os.environ.get("APPDATA", "")) / "npm" / "node_modules" / "openclaw" / "dist" / "index.js"
            if not oc_script.exists():
                oc_script = Path.home() / ".npm-global" / "lib" / "node_modules" / "openclaw" / "dist" / "index.js"
            oc_ws = Path.home() / ".openclaw" / "workspace"
            oc_ws.mkdir(parents=True, exist_ok=True)
            if node_bin and oc_script.exists():
                self.log("[Auto-Heal] Starting OpenClaw Gateway (:18789) silently in background...")
                self.spawn_background_service(
                    [node_bin, str(oc_script), "gateway", "--port", "18789"],
                    cwd=oc_ws,
                    log_name="openclaw.log",
                )

        # 5. Ray Head (:6379 / :8265) on Ryzen 7 Head Node (192.168.99.2)
        if self.self_ip == "192.168.99.2" and not self.is_port_open("127.0.0.1", 6379) and self._can_spawn_port(6379, force=force, cooldown=45.0):
            ray_exe = Path(r"C:\Users\natsa\AppData\Local\Programs\Python\Python312\Scripts\ray.exe")
            if not ray_exe.exists():
                found_ray = shutil.which("ray")
                ray_exe = Path(found_ray) if found_ray else ray_exe
            if ray_exe.exists():
                self.log("[Auto-Heal] Starting Ray Head (:6379 / :8265) silently in background...")
                self.spawn_background_service(
                    [
                        str(ray_exe),
                        "start",
                        "--head",
                        "--node-ip-address=192.168.99.2",
                        "--port=6379",
                        "--redis-password=G-GzcZEzqteW241i720XeH5UNT73T6qk",
                        "--dashboard-host=0.0.0.0",
                        "--dashboard-port=8265",
                        "--disable-usage-stats",
                    ],
                    cwd=self.loom_dir,
                    log_name="ray_head.log",
                )

    def start_local_all(self, separate_gateway_window: bool = False) -> None:
        """Sanitizes stale ports and starts all services silently in the background (zero terminal windows)."""
        self.log(f"=== Sanitizing & Starting All Services Silently on {self.hostname} ({self.self_ip}) ===")
        self.sanitize_local_ports(ports=[8000, 8002, 8080, 5555, 18789])
        time.sleep(0.6)
        self.ensure_local_services_alive(force=True)
        self.log(f"All services running headless in background on {self.hostname} (zero terminal windows).")

    def trigger_peer_action(self, action: str = "restart") -> bool:
        """Dispatches remote headless Start/Restart or Stop/Sanitize to the peer machine."""
        self.log(f"Dispatching headless '{action.upper()}' to Peer Node ({self.peer_ip})...")
        flag = "--start-all" if action == "restart" else "--stop-all"
        py_cmd = (
            f'& "$env:LOCALAPPDATA\\Programs\\Python\\Python312\\python.exe" '
            f'-m loom.gui {flag}'
        )

        # Method 1: Try Stitch Bridge (:5555)
        try:
            payload = json.dumps({
                "command": py_cmd,
                "cwd": r"C:\Users\natsa\Documents\loom-fabric",
                "approval_id": "auto",
                "timeout_sec": 12,
            }).encode("utf-8")
            req = urllib.request.Request(
                f"http://{self.peer_ip}:5555/api/admin/exec",
                data=payload,
                headers={"Content-Type": "application/json", "X-Fabric-Token": MASTER_TOKEN},
            )
            with urllib.request.urlopen(req, timeout=6) as resp:
                if resp.status == 200:
                    self.log(f"Peer {self.peer_ip}:5555 completed headless {action.upper()}.")
                    return True
        except Exception as e:
            self.log(f"Peer :5555 fallback ({e}); trying Ray Job API (:8265)...")

        # Method 2: Fallback to Ray Job API (:8265) on Head Node using base64-encoded payload
        try:
            import base64
            method_call = "ctrl.start_local_all(False)" if action == "restart" else "ctrl.sanitize_local_ports()"
            code = (
                "import pathlib, sys; "
                "sys.path.insert(0, str(pathlib.Path.home() / 'Documents' / 'loom-fabric')); "
                "from loom.gui import CrossPlatformClusterController; "
                f"ctrl = CrossPlatformClusterController(); {method_call}"
            )
            b64 = base64.b64encode(code.encode("utf-8")).decode("ascii")
            py_exe = "C:/Users/natsa/AppData/Local/Programs/Python/Python312/python.exe"
            ray_payload = json.dumps({
                "entrypoint": f'{py_exe} -c "import base64; exec(base64.b64decode(\'{b64}\').decode(\'utf-8\'))"',
            }).encode("utf-8")
            req_ray = urllib.request.Request(
                f"http://{self.peer_ip}:8265/api/jobs/",
                data=ray_payload,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req_ray, timeout=6) as resp_ray:
                if resp_ray.status == 200:
                    self.log(f"Peer {self.peer_ip}:8265 Ray Job dispatched headless {action.upper()}.")
                    return True
        except Exception as e2:
            self.log(f"Could not reach peer {self.peer_ip} ({e2}).")

        return False


class LoomFabricCommandCenter(tk.Tk):
    """Loom Fabric Sovereign Desktop Command Center — Zero-Terminal All-in-One Edition."""

    def __init__(self, gateway_url: str = "http://127.0.0.1:8002"):
        super().__init__()
        self.gateway_url = gateway_url.rstrip("/")
        self.controller = CrossPlatformClusterController(log_callback=self._append_service_log)

        self.title("Fabric — ClothOS Agentic Operating System (Loom · Stitch · Torque)")
        self.geometry("1180x860")
        self.minsize(980, 680)
        self.configure(bg=CLR_OBSIDIAN)

        self.os_tag = f"{platform.system()} ({platform.machine()}) // {self.controller.hostname}"
        self.is_running = True
        self.auto_heal_enabled = True
        self.cluster_connected = False
        self.port_badges: Dict[str, tk.Label] = {}

        self._configure_styles()
        self._assemble_interface()

        # Auto-ensure all local services are running silently on startup
        threading.Thread(target=self.controller.ensure_local_services_alive, daemon=True).start()

        # Launch background async polling + self-healing watchdog thread
        self.poller = threading.Thread(target=self._telemetry_poller_daemon, daemon=True)
        self.poller.start()

    def _configure_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("TNotebook", background=CLR_OBSIDIAN, borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            background=CLR_CARD,
            foreground=CLR_TEXT,
            padding=[16, 10],
            font=("Segoe UI", 10, "bold"),
            borderwidth=0,
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", CLR_PURPLE)],
            foreground=[("selected", CLR_TEXT)],
        )
        style.configure("TCombobox", fieldbackground=CLR_OBSIDIAN, background=CLR_CARD, foreground=CLR_TEXT)

    def _assemble_interface(self):
        # 1. Top Masthead
        masthead = tk.Frame(self, bg=CLR_SURFACE, height=70, padx=20, pady=12, highlightbackground=CLR_BORDER, highlightthickness=1)
        masthead.pack(fill="x", side="top")

        title_container = tk.Frame(masthead, bg=CLR_SURFACE)
        title_container.pack(side="left")

        lbl_logo = tk.Label(title_container, text="FABRIC", font=("Segoe UI", 18, "bold"), fg=CLR_LAWN, bg=CLR_SURFACE)
        lbl_logo.pack(side="left")

        lbl_subtitle = tk.Label(
            title_container,
            text="  // ClothOS Agentic OS  ·  Loom (QCT Router)  ·  Stitch (ZeroMQ MMU)  ·  Torque (Zero-Trust Enclave)",
            font=("Segoe UI", 10, "bold"),
            fg=CLR_AMETHYST,
            bg=CLR_SURFACE,
        )
        lbl_subtitle.pack(side="left", pady=3)

        right_meta = tk.Frame(masthead, bg=CLR_SURFACE)
        right_meta.pack(side="right")

        self.lbl_os = tk.Label(right_meta, text=f"HOST: {self.os_tag}", font=("Consolas", 9), fg=CLR_MUTED, bg=CLR_SURFACE)
        self.lbl_os.pack(side="top", anchor="e")

        self.badge_status = tk.Label(
            right_meta,
            text="● AUTO-HEAL ACTIVE",
            font=("Segoe UI", 9, "bold"),
            fg=CLR_EMERALD,
            bg="#0f2416",
            padx=12,
            pady=2,
            relief="solid",
            bd=1,
        )
        self.badge_status.pack(side="bottom", pady=(4, 0))

        # 2. Persistent Master Cluster Control Bar (100% Windowless Background Management)
        ctrl_bar = tk.Frame(self, bg=CLR_CARD, padx=20, pady=10, highlightbackground=CLR_BORDER, highlightthickness=1)
        ctrl_bar.pack(fill="x", side="top")

        tk.Label(
            ctrl_bar,
            text="FABRIC CONTROLS (ZERO TERMINALS):",
            font=("Segoe UI", 9, "bold"),
            fg=CLR_AMETHYST,
            bg=CLR_CARD,
        ).pack(side="left", padx=(0, 12))

        btn_specs = [
            ("▶ START FABRIC (Ready to Prompt)", CLR_LAWN, CLR_OBSIDIAN, self._action_start_local),
            ("⚡ Restart BOTH Machines", CLR_PURPLE, CLR_TEXT, self._action_restart_both),
            ("🧬 Sync Moltbook & DAG", "#0284c7", CLR_TEXT, self._refresh_clothos_synergy),
            ("■ Stop All (This Machine)", CLR_CRIMSON, CLR_TEXT, self._action_stop_local),
            ("🛑 Stop BOTH Machines", "#991b1b", CLR_TEXT, self._action_stop_both),
        ]
        for label, bg_col, fg_col, cmd in btn_specs:
            b = tk.Button(
                ctrl_bar,
                text=label,
                font=("Segoe UI", 9, "bold"),
                bg=bg_col,
                fg=fg_col,
                activebackground=CLR_AMETHYST,
                relief="flat",
                padx=12,
                pady=4,
                cursor="hand2",
                command=cmd,
            )
            b.pack(side="left", padx=4)

        self.lbl_watchdog = tk.Label(
            ctrl_bar,
            text="🛡 Watchdog: ON (Auto-revives stale services)",
            font=("Segoe UI", 9, "bold"),
            fg=CLR_CLOVER,
            bg=CLR_CARD,
        )
        self.lbl_watchdog.pack(side="right", padx=(8, 0))

        # 3. Main Navigator (Five Pillars: Shuttle, Weave, ClothOS & Moltbook, Torque, Spool)
        self.navigator = ttk.Notebook(self)
        self.navigator.pack(fill="both", expand=True, padx=18, pady=12)

        self.tab_shuttle = tk.Frame(self.navigator, bg=CLR_OBSIDIAN, padx=14, pady=14)
        self.navigator.add(self.tab_shuttle, text="THE SHUTTLE (Prompt & QCT Console)")
        self._build_shuttle_tab(self.tab_shuttle)

        self.tab_clothos = tk.Frame(self.navigator, bg=CLR_OBSIDIAN, padx=14, pady=14)
        self.navigator.add(self.tab_clothos, text="CLOTHOS & MOLTBOOK (DAG & R&D Bridge)")
        self._build_clothos_tab(self.tab_clothos)

        self.tab_weave = tk.Frame(self.navigator, bg=CLR_OBSIDIAN, padx=14, pady=14)
        self.navigator.add(self.tab_weave, text="THE WEAVE (Cluster & Contained Logs)")
        self._build_weave_tab(self.tab_weave)

        self.tab_torque = tk.Frame(self.navigator, bg=CLR_OBSIDIAN, padx=14, pady=14)
        self.navigator.add(self.tab_torque, text="TORQUE VAULT (Zero-Trust Enclave)")
        self._build_torque_tab(self.tab_torque)

        self.tab_spool = tk.Frame(self.navigator, bg=CLR_OBSIDIAN, padx=14, pady=14)
        self.navigator.add(self.tab_spool, text="THE SPOOL (Silicon Budgets & Sharding)")
        self._build_spool_tab(self.tab_spool)

        # Focus prompt box immediately for agy-like ergonomics
        self.after(200, lambda: self.input_box.focus_set())

    def _build_weave_tab(self, parent):
        grid = tk.Frame(parent, bg=CLR_OBSIDIAN)
        grid.pack(fill="x", pady=(0, 10))

        # Worker Node Card (192.168.99.1)
        w_card = tk.Frame(grid, bg=CLR_CARD, padx=14, pady=12, highlightbackground=CLR_BORDER, highlightthickness=1)
        w_card.pack(side="left", fill="both", expand=True, padx=(0, 6))

        tk.Label(w_card, text="WORKER NODE // SKYTECH (192.168.99.1)", font=("Segoe UI", 10, "bold"), fg=CLR_PURPLE, bg=CLR_CARD).pack(anchor="w", pady=(0, 4))
        tk.Label(w_card, text="GPUs: NVIDIA RTX 3060 (12GB CUDA) + AMD RX 580 (8GB) | 54GB RAM", font=("Segoe UI", 9), fg=CLR_TEXT, bg=CLR_CARD).pack(anchor="w", pady=1)

        w_ports_frame = tk.Frame(w_card, bg=CLR_CARD)
        w_ports_frame.pack(fill="x", pady=(8, 2))
        for port, name in [(8002, "Loom GW"), (5555, "Shuttle"), (11434, "Ollama"), (18789, "OpenClaw")]:
            key = f"192.168.99.1:{port}"
            lbl = tk.Label(w_ports_frame, text=f"● {name} (:{port})", font=("Consolas", 8, "bold"), fg=CLR_MUTED, bg=CLR_OBSIDIAN, padx=8, pady=3)
            lbl.pack(side="left", padx=(0, 6))
            self.port_badges[key] = lbl

        # Head Node Card (192.168.99.2)
        h_card = tk.Frame(grid, bg=CLR_CARD, padx=14, pady=12, highlightbackground=CLR_BORDER, highlightthickness=1)
        h_card.pack(side="left", fill="both", expand=True, padx=(6, 0))

        tk.Label(h_card, text="HEAD NODE // RYZEN 7 7730U (192.168.99.2)", font=("Segoe UI", 10, "bold"), fg=CLR_PURPLE, bg=CLR_CARD).pack(anchor="w", pady=(0, 4))
        tk.Label(h_card, text="Compute: 16 Zen 3 vCPUs, Radeon 680M, 16GB DDR4 | Ray Master", font=("Segoe UI", 9), fg=CLR_TEXT, bg=CLR_CARD).pack(anchor="w", pady=1)

        h_ports_frame = tk.Frame(h_card, bg=CLR_CARD)
        h_ports_frame.pack(fill="x", pady=(8, 2))
        for port, name in [(8002, "Loom GW"), (5555, "Shuttle"), (6379, "Ray GCS"), (8265, "Ray UI"), (11434, "Ollama"), (18789, "OpenClaw")]:
            key = f"192.168.99.2:{port}"
            lbl = tk.Label(h_ports_frame, text=f"● {name} (:{port})", font=("Consolas", 8, "bold"), fg=CLR_MUTED, bg=CLR_OBSIDIAN, padx=6, pady=3)
            lbl.pack(side="left", padx=(0, 5))
            self.port_badges[key] = lbl

        tk.Label(parent, text="PHYSICAL ACCELERATOR TELEMETRY STREAM", font=("Segoe UI", 9, "bold"), fg=CLR_MUTED, bg=CLR_OBSIDIAN).pack(anchor="w", pady=(4, 2))
        self.txt_telemetry = scrolledtext.ScrolledText(
            parent,
            bg=CLR_CARD,
            fg=CLR_TEXT,
            font=("Consolas", 9),
            height=10,
            relief="flat",
            insertbackground=CLR_TEXT,
        )
        self.txt_telemetry.pack(fill="both", expand=True, pady=(0, 8))

        tk.Label(parent, text="BACKGROUND DAEMON & SELF-HEALING WATCHDOG LOG (NO EXTERNAL TERMINALS)", font=("Segoe UI", 9, "bold"), fg=CLR_AMETHYST, bg=CLR_OBSIDIAN).pack(anchor="w", pady=(2, 2))
        self.txt_service_log = scrolledtext.ScrolledText(
            parent,
            bg=CLR_CARD,
            fg=CLR_MINT,
            font=("Consolas", 9),
            height=8,
            relief="flat",
            insertbackground=CLR_TEXT,
        )
        self.txt_service_log.pack(fill="both", expand=True)
        self._append_service_log(f"[READY] Zero-Terminal Self-Healing Controller active on {self.os_tag}.")
        self._append_service_log(f"[LOGS] All background service logs stored in {Path.home() / '.loom' / 'logs'}")

    def _append_service_log(self, line: str):
        def _write():
            if hasattr(self, "txt_service_log"):
                self.txt_service_log.insert(tk.END, line + "\n")
                self.txt_service_log.see(tk.END)
        self.after(0, _write)

    # =========================================================================
    # MASTER SWITCHBOARD ACTIONS (100% WINDOWLESS)
    # =========================================================================

    def _action_start_local(self):
        self.auto_heal_enabled = True
        self.lbl_watchdog.config(text="🛡 Watchdog: ON (Auto-revives stale services)", fg=CLR_CLOVER)
        threading.Thread(target=lambda: self.controller.start_local_all(separate_gateway_window=False), daemon=True).start()

    def _action_stop_local(self):
        self.auto_heal_enabled = False
        self.lbl_watchdog.config(text="⏸ Watchdog: PAUSED (Services Stopped)", fg=CLR_AMBER)
        threading.Thread(target=lambda: self.controller.sanitize_local_ports(ports=MANAGED_PORTS), daemon=True).start()

    def _action_restart_both(self):
        self.auto_heal_enabled = True
        self.lbl_watchdog.config(text="🛡 Watchdog: ON (Auto-revives stale services)", fg=CLR_CLOVER)
        def _run():
            self.controller.start_local_all(separate_gateway_window=False)
            self.controller.trigger_peer_action("restart")
        threading.Thread(target=_run, daemon=True).start()

    def _action_stop_both(self):
        self.auto_heal_enabled = False
        self.lbl_watchdog.config(text="⏸ Watchdog: PAUSED (Services Stopped)", fg=CLR_AMBER)
        def _run():
            self.controller.trigger_peer_action("stop")
            self.controller.sanitize_local_ports(ports=MANAGED_PORTS)
        threading.Thread(target=_run, daemon=True).start()

    def _build_shuttle_tab(self, parent):
        controls = tk.Frame(parent, bg=CLR_OBSIDIAN)
        controls.pack(fill="x", pady=(0, 10))

        tk.Label(controls, text="Target Model:", font=("Segoe UI", 9, "bold"), fg=CLR_TEXT, bg=CLR_OBSIDIAN).pack(side="left", padx=(0, 6))
        self.sel_model = ttk.Combobox(
            controls,
            values=["auto", "qwen2.5:32b", "deepseek-r1:14b", "qwen2.5:7b", "qwen2.5:3b"],
            state="readonly",
            width=18,
        )
        self.sel_model.set("auto")
        self.sel_model.pack(side="left", padx=(0, 12))

        tk.Label(controls, text="Platform Edition:", font=("Segoe UI", 9, "bold"), fg=CLR_AMETHYST, bg=CLR_OBSIDIAN).pack(side="left", padx=(0, 6))
        self.sel_platform = ttk.Combobox(
            controls,
            values=[
                "Windows / macOS / Linux (Host Mesh)",
                "ClothOS Special Edition (RISC-V RV64GC + RVV 1.0)",
                "React Native Universal (iOS / Android / Desktop / Web)",
            ],
            state="readonly",
            width=38,
        )
        self.sel_platform.set("ClothOS Special Edition (RISC-V RV64GC + RVV 1.0)")
        self.sel_platform.pack(side="left", padx=(0, 12))

        self.lbl_telemetry_tag = tk.Label(controls, text="Routing: Standby | PMP Enclave Ready", font=("Segoe UI", 9, "bold"), fg=CLR_MUTED, bg=CLR_OBSIDIAN)
        self.lbl_telemetry_tag.pack(side="left")

        self.progress_frame = tk.Frame(controls, bg=CLR_OBSIDIAN)
        self.progress_frame.pack(side="right", padx=(10, 0))

        self.lbl_tokens_live = tk.Label(self.progress_frame, text="", font=("Consolas", 8, "bold"), fg=CLR_AMETHYST, bg=CLR_OBSIDIAN)
        self.lbl_tokens_live.pack(side="left", padx=(0, 8))

        self.progress_bar = ttk.Progressbar(self.progress_frame, mode="indeterminate", length=140)

        self.txt_chat = scrolledtext.ScrolledText(
            parent,
            bg=CLR_CARD,
            fg=CLR_TEXT,
            font=("Consolas", 10),
            height=18,
            relief="flat",
            wrap="word",
            insertbackground=CLR_TEXT,
        )
        self.txt_chat.pack(fill="both", expand=True, pady=(0, 12))
        self.txt_chat.insert(
            tk.END,
            "⚡ FABRIC // ClothOS Agentic Operating System — Zero-Terminal Self-Healing Mode Active.\n"
            "• Incorporates Fabric (Ray Mesh), Loom (QCT Router & DAG), Stitch (ZeroMQ Bus & MMU), and Torque (Zero-Trust Enclave).\n"
            "• Press [▶ START FABRIC] above, or type a prompt below and press Enter (or click [🚀 Self-Evolve Prompt]).\n"
            "──────────────────────────────────────────────────────────────────────────────────────────\n",
        )

        in_frame = tk.Frame(parent, bg=CLR_OBSIDIAN)
        in_frame.pack(fill="x")

        self.input_box = tk.Entry(
            in_frame,
            bg=CLR_CARD,
            fg=CLR_TEXT,
            font=("Segoe UI", 10),
            relief="flat",
            insertbackground=CLR_TEXT,
        )
        self.input_box.pack(side="left", fill="x", expand=True, padx=(0, 10), ipady=8)
        self.input_box.bind("<Return>", lambda e: self._dispatch_completion())

        btn_send = tk.Button(
            in_frame,
            text="Launch Query",
            font=("Segoe UI", 9, "bold"),
            bg=CLR_PURPLE,
            fg=CLR_OBSIDIAN,
            activebackground=CLR_EMERALD,
            relief="flat",
            padx=20,
            command=self._dispatch_completion,
        )
        btn_send.pack(side="right")

        btn_evolve = tk.Button(
            in_frame,
            text="🚀 Self-Evolve Prompt",
            font=("Segoe UI", 9, "bold"),
            bg="#0284c7",
            fg=CLR_TEXT,
            activebackground=CLR_AMETHYST,
            relief="flat",
            padx=14,
            command=self._load_self_improve_prompt,
        )
        btn_evolve.pack(side="right", padx=(0, 8))

    def _load_self_improve_prompt(self):
        prompt = (
            "MISSION: ClothOS Recursive Self-Improvement — Audit the local Fabric stack "
            "(Fabric Ray Mesh, Loom QCT Router & DAG, Stitch ZeroMQ Bus & Zero-OOM MMU, "
            "Torque Zero-Trust Enclave), ingest top Moltbook submolt R&D patterns "
            "(m/systems-engineering, m/active-inference, m/distributed-compute, m/riscv-silicon), "
            "formulate a concrete frozen=True Pydantic v2 architectural upgrade, log to .agent/STATUS.md, "
            "and output the exact Aider surgical edit command."
        )
        self.input_box.delete(0, tk.END)
        self.input_box.insert(0, prompt)
        self.input_box.focus_set()

    def _build_clothos_tab(self, parent):
        top_bar = tk.Frame(parent, bg=CLR_OBSIDIAN)
        top_bar.pack(fill="x", pady=(0, 8))

        tk.Label(
            top_bar,
            text="CLOTHOS KERNEL // LIVE DAG TELEMETRY, QCT ROUTING & MOLTBOOK R&D WISDOM BRIDGE",
            font=("Segoe UI", 11, "bold"),
            fg=CLR_LAWN,
            bg=CLR_OBSIDIAN,
        ).pack(side="left")

        btn_sync = tk.Button(
            top_bar,
            text="🧬 Run Synergy Cycle & Sync .agent/STATUS.md",
            font=("Segoe UI", 9, "bold"),
            bg=CLR_PURPLE,
            fg=CLR_TEXT,
            relief="flat",
            padx=14,
            pady=4,
            cursor="hand2",
            command=self._refresh_clothos_synergy,
        )
        btn_sync.pack(side="right")

        self.txt_clothos = scrolledtext.ScrolledText(
            parent,
            bg=CLR_CARD,
            fg=CLR_TEXT,
            font=("Consolas", 10),
            height=22,
            relief="flat",
            insertbackground=CLR_TEXT,
        )
        self.txt_clothos.pack(fill="both", expand=True)
        self._refresh_clothos_synergy()

    def _refresh_clothos_synergy(self):
        def _worker():
            try:
                from loom.clothos.kernel import ClothOSKernel
                kernel = ClothOSKernel()
                status_path = kernel.sync_agent_status_markdown(probe_network=False)
                snap = kernel.snapshot(probe_network=False)

                lines = [
                    "=========================================================================================",
                    f"  FABRIC // {snap.os_version} — LIVE DIRECTED ACYCLIC GRAPH (DAG) & QCT TELEMETRY",
                    "=========================================================================================",
                    f"• Moltbook Agent Handle : {snap.registration.agent_handle} ({snap.registration.agent_did})",
                    f"• Torque Air-Gap Status : {'VERIFIED (PII/IP Scrubbed & Frozen Pydantic v2)' if snap.registration.airgap_verified else 'UNVERIFIED'}",
                    f"• Cluster VRAM Margin   : {snap.topology.free_cluster_vram_mb:,} MB Free / {snap.topology.total_cluster_vram_mb:,} MB Total",
                    f"• QCT Route Decision    : {snap.latest_route.decision_id} | Tier: {snap.latest_route.tier}",
                    f"• Selected Model        : {snap.latest_route.target_model} | QCT Entropy: {snap.latest_route.qct_entropy_score}",
                    f"• DAG Critical Path     : {snap.latest_route.dag.critical_path_ms} ms",
                    "",
                    "── LIVE DIRECTED ACYCLIC GRAPH (DAG) TOPOLOGY ───────────────────────────────────────────",
                    f"  {snap.latest_route.dag.ascii_topology}",
                    "",
                ]
                for node in snap.latest_route.dag.nodes:
                    deps = ", ".join(node.depends_on) if node.depends_on else "ROOT"
                    lines.append(
                        f"  [{node.pillar:<7}] {node.node_id:<18} | {node.stage_name:<46} | "
                        f"{node.estimated_latency_ms:>4.1f} ms | Deps: {deps}"
                    )

                lines.extend([
                    "",
                    "── MOLTBOOK R&D WISDOM BRIDGE (SUBMOLT INGESTION & OPENCLAW -> AIDER QUEUE) ────────────",
                    f"  Subscribed Submolts: {', '.join(snap.registration.registered_submolts)}",
                    f"  Synced Status File : {status_path}",
                    "",
                ])
                for h in snap.active_hypotheses:
                    lines.append(f"  ★ [{h.hypothesis_id}] ({h.submolt} // {h.source_post_id}) — Status: {h.sandbox_status}")
                    lines.append(f"    Hypothesis : {h.statement}")
                    lines.append(f"    Upgrade    : {h.proposed_change}")
                    lines.append(f"    Aider Hook : {h.aider_instruction}\n")

                text = "\n".join(lines)
                def _ui():
                    if hasattr(self, "txt_clothos"):
                        self.txt_clothos.delete("1.0", tk.END)
                        self.txt_clothos.insert(tk.END, text)
                self.after(0, _ui)
            except Exception as e:
                self._append_service_log(f"[ClothOS Synergy Warning] {e}")

        threading.Thread(target=_worker, daemon=True).start()

    def _build_torque_tab(self, parent):
        tk.Label(parent, text="TORQUE // ZERO-TRUST IP & CREDENTIAL VAULT", font=("Segoe UI", 12, "bold"), fg=CLR_PURPLE, bg=CLR_OBSIDIAN).pack(anchor="w", pady=(0, 4))
        tk.Label(
            parent,
            text="All queries routing to Tier 3 Cloud Arbitrage (>300s compute) are scrubbed before departure.\n"
                 "Entities like 'fouriersLibrary', 'VectorForge', 'Mycos', and API keys are mapped into synthetic vault tokens\n"
                 "and rehydrated on the fly before delivery back to the client.",
            font=("Segoe UI", 9),
            fg=CLR_MUTED,
            bg=CLR_OBSIDIAN,
            justify="left",
        ).pack(anchor="w", pady=(0, 12))

        self.txt_vault = scrolledtext.ScrolledText(
            parent,
            bg=CLR_CARD,
            fg=CLR_EMERALD,
            font=("Consolas", 10),
            height=20,
            relief="flat",
            insertbackground=CLR_TEXT,
        )
        self.txt_vault.pack(fill="both", expand=True)

    def _build_spool_tab(self, parent):
        tk.Label(parent, text="THE SPOOL // HARDWARE BENCHMARKS & MODEL PROVISIONER", font=("Segoe UI", 12, "bold"), fg=CLR_PURPLE, bg=CLR_OBSIDIAN).pack(anchor="w", pady=(0, 4))
        tk.Label(
            parent,
            text="Intelligently matches local open-weights LLMs based on GPU memory bandwidth, compute capability, and benchmark scores.\nAlso manages zero-trust cloud API bridges (OpenAI, Anthropic, Google Gemini, OpenRouter).",
            font=("Segoe UI", 9),
            fg=CLR_MUTED,
            bg=CLR_OBSIDIAN,
            justify="left",
        ).pack(anchor="w", pady=(0, 10))

        action_bar = tk.Frame(parent, bg=CLR_OBSIDIAN)
        action_bar.pack(fill="x", pady=(0, 10))

        tk.Label(action_bar, text="Install Recommended Model:", font=("Segoe UI", 9, "bold"), fg=CLR_TEXT, bg=CLR_OBSIDIAN).pack(side="left", padx=(0, 8))
        self.combo_pull = ttk.Combobox(
            action_bar,
            values=["qwen2.5:32b", "deepseek-r1:14b", "qwen2.5:7b", "qwen2.5:3b", "llama3.3:70b"],
            state="readonly",
            width=20,
        )
        self.combo_pull.set("qwen2.5:32b")
        self.combo_pull.pack(side="left", padx=(0, 10))

        btn_pull = tk.Button(
            action_bar,
            text="1-Click Pull Model",
            font=("Segoe UI", 9, "bold"),
            bg=CLR_PURPLE,
            fg=CLR_OBSIDIAN,
            activebackground=CLR_AMETHYST,
            relief="flat",
            padx=14,
            command=self._pull_selected_model,
        )
        btn_pull.pack(side="left")

        btn_refresh = tk.Button(
            action_bar,
            text="Re-evaluate Benchmarks",
            font=("Segoe UI", 9),
            bg=CLR_CARD,
            fg=CLR_TEXT,
            relief="flat",
            padx=12,
            command=self._refresh_spool_evaluations,
        )
        btn_refresh.pack(side="left", padx=(10, 0))

        self.txt_spool = scrolledtext.ScrolledText(
            parent,
            bg=CLR_CARD,
            fg=CLR_TEXT,
            font=("Consolas", 9),
            height=20,
            relief="flat",
            insertbackground=CLR_TEXT,
        )
        self.txt_spool.pack(fill="both", expand=True)

        self.after(500, self._refresh_spool_evaluations)

    def _pull_selected_model(self):
        target = self.combo_pull.get()
        if not target:
            return
        messagebox.showinfo("Loom Fabric Provisioner", f"Starting background download for '{target}' via sovereign Ollama runtime.\nYou can monitor progress in terminal or check The Spool tab.")
        def _pull_thread():
            from loom.models.recommender import ModelHardwareRecommender
            rec = ModelHardwareRecommender()
            rec.install_model_cli(target)
            self._refresh_spool_evaluations()
        threading.Thread(target=_pull_thread, daemon=True).start()

    def _refresh_spool_evaluations(self):
        def _compute():
            from loom.models.recommender import ModelHardwareRecommender
            from loom.gateway.cloud_bridge import CloudLLMBridge, CLOUD_PROVIDERS

            rec = ModelHardwareRecommender()
            recs = rec.evaluate_hardware_fit()

            bridge = CloudLLMBridge()
            cloud_status = bridge.get_provider_status()

            lines = []
            lines.append("=== LOCAL HARDWARE-MATCHED MODEL BENCHMARK RECOMMENDATIONS ===")
            lines.append(f"{'MODEL':<18} | {'BENCHMARK (MMLU/CODE)':<22} | {'HARDWARE FIT':<26} | {'EST. SPEED':<12} | {'STATUS'}")
            lines.append("-" * 95)
            for r in recs:
                bench_str = f"MMLU: {r.benchmark.mmlu_score:.0f}% / Code: {r.benchmark.humaneval_coding:.0f}%"
                status_str = "INSTALLED" if r.is_installed else "NOT PULLED"
                lines.append(f"{r.preset.id:<18} | {bench_str:<22} | {r.fit_status:<26} | {r.estimated_speed_tps:<5.1f} tps  | {status_str}")
                lines.append(f"   ↳ Rationale: {r.recommendation_reason}\n")

            lines.append("\n=== CLOUD LLM API PROVIDER BRIDGES (ZERO-TRUST SANITIZED) ===")
            lines.append(f"{'PROVIDER':<18} | {'DEFAULT MODEL':<28} | {'API KEY ENV VAR':<20} | {'STATUS'}")
            lines.append("-" * 80)
            for key, p in CLOUD_PROVIDERS.items():
                is_ready = "CONFIGURED (READY)" if cloud_status.get(key, False) else "KEY MISSING"
                lines.append(f"{p.name:<18} | {p.default_model:<28} | ${p.api_key_env_var:<19} | {is_ready}")

            lines.append("\n=== CROSS-PLATFORM & CLOTHOS RISC-V (RV64GC + RVV 1.0) EDITIONS ===")
            lines.append("1. Windows 10/11 Native (x86_64/ARM64) : Start-Loom-GUI.bat (pythonw.exe Zero-Terminal) + `loom` CLI")
            lines.append("2. macOS Native (.app Bundle)          : ~/Applications/Loom Fabric Commander.app (Apple Silicon Metal & Intel)")
            lines.append("3. Linux / WSL2 Native (.desktop)      : ~/.local/share/applications/loom-fabric.desktop + `loom` CLI")
            lines.append("4. React Native Universal App          : apps/loom-react-native/App.tsx (iOS, Android, Windows, macOS, Web)")
            lines.append("5. ClothOS RISC-V Special Edition      : platforms/clothos-riscv/ (rv64imafdcv + 512b RVV 1.0 + PMP Enclave CSR 0x9B)")
            lines.append("6. The Shuttle PWA & Web Dashboard     : http://192.168.99.1:5555 & http://192.168.99.1:8002")

            lines.append("\n[Tip] Any query requiring >300s compute is automatically sanitized via Torque Vault and dispatched to Cloud APIs.")

            content = "\n".join(lines)
            def _set():
                self.txt_spool.delete("1.0", tk.END)
                self.txt_spool.insert(tk.END, content)
            self.after(0, _set)

        threading.Thread(target=_compute, daemon=True).start()

    def _update_port_matrix(self):
        """Probes live TCP ports across both 192.168.99.1 and 192.168.99.2 and updates UI badges."""
        for key, badge in list(self.port_badges.items()):
            ip, port_str = key.split(":")
            port = int(port_str)
            probe_host = "127.0.0.1" if ip == self.controller.self_ip else ip
            is_up = self.controller.is_port_open(probe_host, port, timeout=0.4)
            fg = CLR_EMERALD if is_up else CLR_CRIMSON
            self.after(0, lambda b=badge, c=fg: b.config(fg=c))

    def _tail_service_logs(self):
        """Streams new output from ~/.loom/logs/*.log directly into the contained Loom GUI log pane."""
        if not hasattr(self, "_log_offsets"):
            self._log_offsets: Dict[str, int] = {}
        log_dir = Path.home() / ".loom" / "logs"
        if not log_dir.exists():
            return
        for tag, fname in [
            ("GW:8002", "loom_gateway.log"),
            ("SHUTTLE:5555", "stitch_bridge.log"),
            ("OPENCLAW:18789", "openclaw.log"),
            ("OLLAMA:11434", "ollama.log"),
        ]:
            fpath = log_dir / fname
            if not fpath.exists():
                continue
            try:
                size = fpath.stat().st_size
                prev = self._log_offsets.get(fname, max(0, size - 600))
                if size < prev:
                    prev = 0
                if size > prev:
                    with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                        f.seek(prev)
                        chunk = f.read(4096)
                    self._log_offsets[fname] = f.tell()
                    for raw_line in chunk.splitlines():
                        s = raw_line.strip()
                        if s:
                            self._append_service_log(f"[{tag}] {s}")
            except Exception:
                pass

    def _telemetry_poller_daemon(self):
        tick = 0
        while self.is_running:
            tick += 1
            if self.auto_heal_enabled and tick % 3 == 0:
                try:
                    self.controller.ensure_local_services_alive()
                except Exception:
                    pass

            try:
                self._update_port_matrix()
                self._tail_service_logs()
            except Exception:
                pass

            try:
                req = urllib.request.Request(f"{self.gateway_url}/health")
                with urllib.request.urlopen(req, timeout=2) as resp:
                    if resp.status == 200:
                        self.cluster_connected = True
                        self._set_status_badge("● CLUSTER ONLINE", CLR_EMERALD, "#052e16")
            except Exception:
                self.cluster_connected = False
                self._set_status_badge("● GATEWAY OFFLINE", CLR_CRIMSON, "#2a0c0c")

            if self.cluster_connected:
                try:
                    req_m = urllib.request.Request(f"{self.gateway_url}/metrics")
                    with urllib.request.urlopen(req_m, timeout=2) as resp_m:
                        data = json.loads(resp_m.read().decode())
                        self._render_telemetry_data(data)
                except Exception:
                    pass

            time.sleep(3)

    def _set_status_badge(self, text, fg_color, bg_color):
        self.after(0, lambda: self.badge_status.config(text=text, fg=fg_color, bg=bg_color))

    def _render_telemetry_data(self, data):
        hw = data.get("cluster_hardware", {})
        gpus = hw.get("gpus", [])
        host = hw.get("host", {})
        lines = []
        lines.append(f"Snapshot Time: {time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        lines.append(f"Host Topology: {host.get('hostname', self.controller.hostname)} | OS: {host.get('os_name', self.os_tag)} | Cores: {host.get('cpu_cores_logical', os.cpu_count())} vCPUs")
        lines.append(f"Memory Pools:  Total Physical: {host.get('total_ram_mb', 0):,} MB | Available: {host.get('available_ram_mb', 0):,} MB\n")
        lines.append("ENUMERATED ACCELERATORS:")
        for idx, g in enumerate(gpus):
            lines.append(f"  Tier [{idx}] -> {g.get('name')}")
            lines.append(f"      Vendor: {g.get('vendor')} | Backend: {g.get('backend')} | Total VRAM: {g.get('total_vram_mb', 0):,} MB | Free: {g.get('free_vram_mb', 0):,} MB")

        rendered = "\n".join(lines)
        def _update():
            self.txt_telemetry.delete("1.0", tk.END)
            self.txt_telemetry.insert(tk.END, rendered)
        self.after(0, _update)

    def _dispatch_completion(self):
        prompt = self.input_box.get().strip()
        if not prompt:
            return
        self.input_box.delete(0, tk.END)

        model = self.sel_model.get()
        self.txt_chat.insert(tk.END, f"\nUser > {prompt}\n", "user")
        self.txt_chat.insert(tk.END, f"Loom Fabric ({model}) > ", "assistant")
        self.txt_chat.see(tk.END)

        self.progress_bar.pack(side="left")
        self.progress_bar.start(10)
        self.lbl_tokens_live.config(text="Deciphering Route...", fg=CLR_AMBER)

        threading.Thread(target=self._run_async_streaming_query, args=(prompt, model), daemon=True).start()

    def _run_async_streaming_query(self, prompt, model):
        # Auto-heal / auto-start local gateway if offline when user submits prompt
        if not self.controller.is_port_open("127.0.0.1", 8002):
            self.after(0, lambda: self.lbl_tokens_live.config(text="Auto-starting Gateway...", fg=CLR_AMBER))
            self.controller.ensure_local_services_alive()
            for _ in range(12):
                if self.controller.is_port_open("127.0.0.1", 8002):
                    break
                time.sleep(0.5)

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": True,
        }
        token_count = 0
        start_time = time.time()
        try:
            req = urllib.request.Request(
                f"{self.gateway_url}/v1/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                headers = dict(resp.getheaders())
                route = headers.get("x-torque-route", "Local")
                scrubbed = headers.get("x-torque-scrubbed", "false")

                tag_msg = f"Route: {route} | Scrubbed: {scrubbed}"
                self.after(0, lambda: self.lbl_telemetry_tag.config(text=tag_msg, fg=CLR_EMERALD))

                if scrubbed.lower() == "true":
                    vault_entry = f"[{time.strftime('%H:%M:%S')}] Scrubbed & Rehydrated Query for model {model}:\nOriginal Prompt Snippet: {prompt[:80]}...\nRoute: {route}\n"
                    def _update_v():
                        self.txt_vault.insert(tk.END, vault_entry)
                        self.txt_vault.see(tk.END)
                    self.after(0, _update_v)

                for line in resp:
                    decoded = line.decode("utf-8").strip()
                    if not decoded or not decoded.startswith("data:"):
                        continue
                    if decoded == "data: [DONE]":
                        break

                    try:
                        chunk_json = json.loads(decoded[5:].strip())
                        choices = chunk_json.get("choices", [])
                        if choices:
                            delta = choices[0].get("delta", {}).get("content", "")
                            if delta:
                                token_count += 1
                                elapsed = max(0.001, time.time() - start_time)
                                live_tps = token_count / elapsed

                                def _stream_chunk(text=delta, count=token_count, speed=live_tps):
                                    self.txt_chat.insert(tk.END, text)
                                    self.txt_chat.see(tk.END)
                                    self.lbl_tokens_live.config(text=f"{count} tokens ({speed:.1f} tps)", fg=CLR_AMETHYST)
                                self.after(0, _stream_chunk)
                    except Exception:
                        pass

        except Exception:
            try:
                payload["stream"] = False
                req_fallback = urllib.request.Request(
                    f"{self.gateway_url}/v1/chat/completions",
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                )
                with urllib.request.urlopen(req_fallback, timeout=120) as resp2:
                    data = json.loads(resp2.read().decode())
                    content = data["choices"][0]["message"]["content"]
                    def _fallback_render():
                        self.txt_chat.insert(tk.END, content)
                        self.txt_chat.see(tk.END)
                    self.after(0, _fallback_render)
            except Exception as e2:
                def _render_err():
                    self.txt_chat.insert(tk.END, f"\n[Error: {e2}]\n\n")
                    self.txt_chat.see(tk.END)
                self.after(0, _render_err)

        finally:
            def _stop_progress():
                self.progress_bar.stop()
                self.progress_bar.pack_forget()
                self.txt_chat.insert(tk.END, "\n\n")
                self.txt_chat.see(tk.END)
            self.after(0, _stop_progress)


# Alias for CLI and external callers
LoomFabricGUI = LoomFabricCommandCenter


def main(gateway_url: str = "http://127.0.0.1:8002"):
    if "--start-all" in sys.argv:
        ctrl = CrossPlatformClusterController()
        ctrl.start_local_all(separate_gateway_window=False)
        return
    if "--stop-all" in sys.argv:
        ctrl = CrossPlatformClusterController()
        ctrl.sanitize_local_ports(ports=MANAGED_PORTS)
        return
    if "--restart-both" in sys.argv:
        ctrl = CrossPlatformClusterController()
        ctrl.start_local_all(separate_gateway_window=False)
        ctrl.trigger_peer_action("restart")
        return

    app = LoomFabricCommandCenter(gateway_url=gateway_url)
    app.mainloop()


if __name__ == "__main__":
    gw = "http://127.0.0.1:8002"
    for arg in sys.argv[1:]:
        if arg.startswith("http"):
            gw = arg
    main(gateway_url=gw)
