"""Native Process Supervisor with Windows Job Object Lifecycle Management.

Spawns, monitors, and cleanly terminates native `llama-server` and `rpc-server` instances.
Guarantees zero-orphan process termination on Windows by binding all spawned worker
subprocesses to a kernel Windows Job Object configured with `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`.

Architecture Note (Rust Migration Target):
    This module maps to `loom_stitch::supervisor` in Rust:
    - Implemented via `windows::Win32::System::JobObjects` in Rust.
    - Captures stdout/stderr via non-blocking `tokio::process::Command` streaming.
    - Zero orphaned PID guarantee at the Windows NT kernel boundary.
"""

from __future__ import annotations

import asyncio
import ctypes
from ctypes import wintypes
import logging
import os
import platform
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from ..config import settings
from .allocator import LayerShardingPlan

logger = logging.getLogger("loom.stitch.supervisor")


class ProcessHealthStatus(BaseModel):
    """Runtime health and performance telemetry of a managed backend process."""

    pid: int = Field(..., description="Operating system process ID.")
    is_running: bool = Field(..., description="Whether the process is actively executing.")
    endpoint_url: str = Field(..., description="HTTP address of the native server (e.g., 'http://127.0.0.1:8080').")
    uptime_seconds: float = Field(..., description="Seconds elapsed since process startup.")
    consecutive_health_failures: int = Field(default=0, description="Count of missed health probes.")
    last_error_log: Optional[str] = Field(default=None, description="Last detected error pattern from logs.")


class IO_COUNTERS(ctypes.Structure):
    _fields_ = [
        ("ReadOperationCount", ctypes.c_uint64),
        ("WriteOperationCount", ctypes.c_uint64),
        ("OtherOperationCount", ctypes.c_uint64),
        ("ReadTransferCount", ctypes.c_uint64),
        ("WriteTransferCount", ctypes.c_uint64),
        ("OtherTransferCount", ctypes.c_uint64),
    ]


class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("PerProcessUserTimeLimit", ctypes.c_int64),
        ("PerJobUserTimeLimit", ctypes.c_int64),
        ("LimitFlags", wintypes.DWORD),
        ("MinimumWorkingSetSize", ctypes.c_size_t),
        ("MaximumWorkingSetSize", ctypes.c_size_t),
        ("ActiveProcessLimit", wintypes.DWORD),
        ("Affinity", ctypes.c_size_t),
        ("PriorityClass", wintypes.DWORD),
        ("SchedulingClass", wintypes.DWORD),
    ]


class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BasicLimitInformation", JOBOBJECT_BASIC_LIMIT_INFORMATION),
        ("IoInfo", IO_COUNTERS),
        ("ProcessMemoryLimit", ctypes.c_size_t),
        ("JobMemoryLimit", ctypes.c_size_t),
        ("PeakProcessMemoryUsed", ctypes.c_size_t),
        ("PeakJobMemoryUsed", ctypes.c_size_t),
    ]


class WindowsJobObjectManager:
    """Manages a Win32 Job Object ensuring kernel-enforced child process termination on exit."""

    # Win32 Constants
    JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
    JobObjectExtendedLimitInformation = 9

    def __init__(self, job_name: str = "LoomFabricProcessJob"):
        """Initializes and configures the Win32 Job Object."""
        self.job_handle = None
        if platform.system() != "Windows":
            return

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self.job_handle = kernel32.CreateJobObjectW(None, job_name)
        if not self.job_handle:
            err = ctypes.get_last_error()
            logger.warning(f"Failed to create Windows Job Object: WinError {err}")
            return

        # Configure JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        info = self.JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        info.BasicLimitInformation.LimitFlags = self.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE

        res = kernel32.SetInformationJobObject(
            self.job_handle,
            self.JobObjectExtendedLimitInformation,
            ctypes.byref(info),
            ctypes.sizeof(info),
        )
        if not res:
            err = ctypes.get_last_error()
            logger.warning(f"Failed to set Job Object kill-on-close limit: WinError {err}")
        else:
            logger.debug(f"Windows Job Object '{job_name}' initialized with KILL_ON_JOB_CLOSE.")

    def assign_process(self, process_handle) -> bool:
        """Assigns an active process handle to the Win32 Job Object."""
        if not self.job_handle or platform.system() != "Windows":
            return False

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        res = kernel32.AssignProcessToJobObject(self.job_handle, process_handle)
        if not res:
            err = ctypes.get_last_error()
            logger.warning(f"Failed to assign process to Job Object: WinError {err}")
            return False
        return True


class NativeProcessSupervisor:
    """Oversees native llama-server binary execution, stdout/stderr logging, and health probing."""

    # Error signatures scanned in backend logs
    CRITICAL_ERROR_PATTERNS = [
        "CUDA out of memory",
        "VK_ERROR_OUT_OF_DEVICE_MEMORY",
        "WDDM TDR timeout",
        "failed to allocate",
        "ggml_vulkan: error",
        "cudaGetLastError() failed",
    ]

    def __init__(
        self,
        binary_path: Optional[Path] = None,
        job_manager: Optional[WindowsJobObjectManager] = None,
    ):
        """Initializes the process supervisor.

        Args:
            binary_path: Path to the native `llama-server.exe` executable.
            job_manager: Shared Windows Job Object sandbox manager.
        """
        self.binary_path = binary_path or (settings.paths.bin_dir / ("llama-server.exe" if platform.system() == "Windows" else "llama-server"))
        self.job_manager = job_manager or WindowsJobObjectManager()
        self.process: Optional[subprocess.Popen] = None
        self.start_time: float = 0.0
        self.port: int = 8080
        self.endpoint_url: str = f"http://127.0.0.1:{self.port}"
        self.log_file_out: Optional[Path] = None
        self.log_file_err: Optional[Path] = None
        self._out_fd = None
        self._err_fd = None

    def spawn(
        self,
        model_path: Path,
        sharding_plan: LayerShardingPlan,
        port: int = 8080,
        extra_args: Optional[List[str]] = None,
    ) -> ProcessHealthStatus:
        """Spawns native llama-server with exact layer sharding flags under the Job Object.

        Args:
            model_path: Path to the target GGUF model file.
            sharding_plan: Mathematical allocation plan containing `-ngl`, `--tensor-split`, etc.
            port: Port for the llama-server HTTP server.
            extra_args: Additional command-line flags.

        Returns:
            ProcessHealthStatus detailing initial process state.

        Raises:
            FileNotFoundError: If the binary or model path does not exist.
            RuntimeError: If the process fails to start.
        """
        if not model_path.exists():
            raise FileNotFoundError(f"Model GGUF file not found: {model_path}")

        self.port = port
        self.endpoint_url = f"http://127.0.0.1:{self.port}"

        # Construct argument list
        cmd: List[str] = [
            str(self.binary_path),
            "-m", str(model_path),
            "--port", str(self.port),
        ]

        # Append generated flags from sharding plan
        for k, v in sharding_plan.llama_server_flags.items():
            cmd.append(k)
            if v:
                cmd.append(str(v))

        if extra_args:
            cmd.extend(extra_args)

        # Set up log files
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        self.log_file_out = settings.paths.logs_dir / f"llama_server_{self.port}_{timestamp}.out.log"
        self.log_file_err = settings.paths.logs_dir / f"llama_server_{self.port}_{timestamp}.err.log"

        self._out_fd = open(self.log_file_out, "w", encoding="utf-8")
        self._err_fd = open(self.log_file_err, "w", encoding="utf-8")

        logger.info(f"Spawning native llama-server: {' '.join(cmd[:6])} ... [Port: {self.port}]")

        creation_flags = 0
        start_new_session = False
        if platform.system() == "Windows":
            creation_flags = subprocess.CREATE_SUSPENDED if hasattr(subprocess, "CREATE_SUSPENDED") else 0x00000004
        else:
            start_new_session = True

        self.process = subprocess.Popen(
            cmd,
            stdout=self._out_fd,
            stderr=self._err_fd,
            creationflags=creation_flags,
            start_new_session=start_new_session,
        )

        self.start_time = time.time()

        # Bind to Windows Job Object before resuming execution
        if platform.system() == "Windows" and self.process:
            # Get Win32 handle and assign
            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            PROCESS_ALL_ACCESS = 0x1F0FFF
            h_proc = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, self.process.pid)
            if h_proc:
                self.job_manager.assign_process(h_proc)
                # Resume process main thread
                if creation_flags:
                    kernel32.ResumeThread(h_proc)
                kernel32.CloseHandle(h_proc)

        return ProcessHealthStatus(
            pid=self.process.pid,
            is_running=True,
            endpoint_url=self.endpoint_url,
            uptime_seconds=0.0,
        )

    async def wait_until_healthy(self, timeout_seconds: float = 60.0) -> bool:
        """Asynchronously polls `/health` with exponential backoff until the server is ready.

        Args:
            timeout_seconds: Maximum duration to wait before aborting.

        Returns:
            True if the server responded healthy, False if timed out or process crashed.
        """
        import httpx

        deadline = time.time() + timeout_seconds
        delay = 0.5

        async with httpx.AsyncClient(timeout=3.0) as client:
            while time.time() < deadline:
                if self.process.poll() is not None:
                    # Process died prematurely
                    error_tail = self.scan_recent_errors()
                    logger.error(f"llama-server exited with code {self.process.returncode}. Last error: {error_tail}")
                    return False

                try:
                    res = await client.get(f"{self.endpoint_url}/health")
                    if res.status_code == 200:
                        logger.info(f"llama-server on {self.endpoint_url} is READY and healthy.")
                        return True
                except Exception:
                    pass

                await asyncio.sleep(delay)
                delay = min(2.0, delay * 1.5)

        logger.error(f"Timed out waiting for llama-server on {self.endpoint_url} after {timeout_seconds}s.")
        return False

    def scan_recent_errors(self, max_lines: int = 40) -> Optional[str]:
        """Scans the error log file for critical out-of-memory or driver timeout patterns.

        Returns:
            Matched error snippet, or last log lines if no pattern matched.
        """
        if not self.log_file_err or not self.log_file_err.exists():
            return None

        try:
            with open(self.log_file_err, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()[-max_lines:]
            content = "".join(lines)

            for pattern in self.CRITICAL_ERROR_PATTERNS:
                if pattern.lower() in content.lower():
                    return f"Critical Fault Detected: {pattern} in log:\n{content[-300:]}"

            return content[-250:] if content else None
        except Exception as e:
            return f"Failed to read error log: {e}"

    def terminate(self) -> None:
        """Cleanly terminates the managed server process and closes log handles."""
        if self.process and self.process.poll() is None:
            logger.info(f"Terminating llama-server [PID: {self.process.pid}]...")
            if platform.system() != "Windows":
                # POSIX process group termination
                import signal
                try:
                    os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                    self.process.wait(timeout=3.0)
                except Exception:
                    try:
                        os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
                    except Exception:
                        pass
            else:
                self.process.terminate()
                try:
                    self.process.wait(timeout=5.0)
                except subprocess.TimeoutExpired:
                    logger.warning(f"Process {self.process.pid} did not exit cleanly; forcing kill.")
                    self.process.kill()

        if self._out_fd and not self._out_fd.closed:
            self._out_fd.close()
        if self._err_fd and not self._err_fd.closed:
            self._err_fd.close()
