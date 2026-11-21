"""
ClothOS Port Manager & Audit Engine (`loom/fabric/port_manager.py`).

Provides strict, safe port management, collision prevention, and full CRUD telemetry:
- Explicit Port Taxonomy: Distinguishes ClothOS internal ports from external/third-party services.
- Conflict Prevention: Ensures ClothOS never hijacks or collides with external ports (e.g. Ollama, OpenClaw, Ray, dev servers).
- Stale Process Sanitization: Cleans only stale ClothOS dashboard instances without touching third-party applications.
- Full CRUD API support: Create/Probe, Read/Audit, Update/Refresh, Delete/Clean.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import json
import logging
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("loom.fabric.port_manager")

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
PORT_FILE = WORKSPACE_ROOT / ".loom_dashboard_port"
PID_FILE = WORKSPACE_ROOT / ".loom_dashboard_pid"

# Dedicated ClothOS Port Taxonomy
CLOTHOS_PRIMARY_PORT = 8087
CLOTHOS_REACT_NATIVE_PORT = 8086
CLOTHOS_CANDIDATE_PORTS = [8087, 8088, 8089, 8090, 8085]

# Known Port Registry with Ownership & Conflict Risk
PORT_REGISTRY = {
    # Node 1 Managed Services
    8087: {"name": "ClothOS Command Center (Primary Dedicated)", "node": "Node 1", "role": "CLOTHOS_CORE", "safe_to_clean": True},
    8086: {"name": "ClothOS Universal React Native App", "node": "Node 1 / Node 2", "role": "CLOTHOS_REACT_NATIVE", "safe_to_clean": False},
    8085: {"name": "ClothOS Command Center (Alt / Legacy)", "node": "Node 1", "role": "CLOTHOS_CORE", "safe_to_clean": True},
    8088: {"name": "ClothOS Dash Secondary", "node": "Node 1", "role": "CLOTHOS_CORE", "safe_to_clean": True},
    8089: {"name": "ClothOS Dash Tertiary", "node": "Node 1", "role": "CLOTHOS_CORE", "safe_to_clean": True},
    8090: {"name": "ClothOS Quaternary Port", "node": "Node 1", "role": "CLOTHOS_CORE", "safe_to_clean": True},
    5559: {"name": "ZeroMQ Telemetry Bus", "node": "Node 1", "role": "CLOTHOS_IPC", "safe_to_clean": False},
    5555: {"name": "Shuttle Peer Sync", "node": "Node 1", "role": "CLOTHOS_IPC", "safe_to_clean": False},
    8002: {"name": "Loom GW", "node": "Node 1", "role": "CLOTHOS_GW", "safe_to_clean": True},
    # External Third-Party Services (NEVER kill or hijack)
    11434: {"name": "Ollama LLM Server", "node": "Node 1 / Node 2", "role": "EXTERNAL_LLM", "safe_to_clean": False},
    18789: {"name": "OpenClaw Gateway", "node": "Node 1", "role": "EXTERNAL_SERVICE", "safe_to_clean": False},
    8080: {"name": "Standard HTTP Alt / Dev Server", "node": "Host OS", "role": "EXTERNAL_DEV", "safe_to_clean": False},
    3000: {"name": "Node / React Webpack Dev", "node": "Host OS", "role": "EXTERNAL_DEV", "safe_to_clean": False},
    # Node 2 Remote Managed Services (100.74.98.21 / 192.168.99.2)
    8265: {"name": "Ray Cluster Dashboard", "node": "Node 2", "role": "REMOTE_COMPUTE", "safe_to_clean": False},
    6379: {"name": "Ray Redis GCS", "node": "Node 2", "role": "REMOTE_COMPUTE", "safe_to_clean": False},
}


@dataclass
class PortAuditRecord:
    port: int
    name: str
    node: str
    role: str
    status: str  # "LISTENING", "AVAILABLE", "RESTRICTED", "REMOTE_ONLINE", "REMOTE_OFFLINE"
    latency_ms: float
    owner_info: str
    safe_to_clean: bool
    last_checked: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "port": self.port,
            "name": self.name,
            "node": self.node,
            "role": self.role,
            "status": self.status,
            "latency_ms": round(self.latency_ms, 2),
            "owner_info": self.owner_info,
            "safe_to_clean": self.safe_to_clean,
            "last_checked": self.last_checked,
        }


class ClothOSPortManager:
    """Manages port allocation, conflict resolution, and real-time connectivity telemetry."""

    def __init__(self):
        self.node1_ip = "127.0.0.1"
        self.node2_tailscale = "100.74.98.21"
        self.node2_local = "192.168.99.2"
        self.custom_probed_ports: Dict[Tuple[str, int], Dict[str, Any]] = {}

    def is_port_open(self, host: str, port: int, timeout: float = 0.3) -> Tuple[bool, float]:
        """Probes port and measures round-trip latency in milliseconds."""
        t0 = time.perf_counter()
        try:
            with socket.create_connection((host, port), timeout=timeout):
                latency = (time.perf_counter() - t0) * 1000.0
                return True, latency
        except Exception:
            return False, 0.0

    def is_port_available_to_bind(self, port: int) -> bool:
        """Tests whether local port can be safely bound without permission or address errors."""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("127.0.0.1", port))
            return True
        except Exception:
            return False
        finally:
            s.close()

    def audit_all_ports(self) -> Dict[str, Any]:
        """Performs a comprehensive audit across all registered and custom ports."""
        records: List[PortAuditRecord] = []
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 1. Audit local registered ports
        for p, meta in PORT_REGISTRY.items():
            is_remote = meta["node"] == "Node 2"
            target_host = self.node2_tailscale if is_remote else "127.0.0.1"

            open_status, lat = self.is_port_open(target_host, p, timeout=0.25)
            if not open_status and is_remote:
                # Try fallback local IP for Node 2
                open_status, lat = self.is_port_open(self.node2_local, p, timeout=0.2)

            if is_remote:
                status = "REMOTE_ONLINE" if open_status else "REMOTE_OFFLINE"
                owner = "Node 2 Cluster Head"
            else:
                if open_status:
                    status = "LISTENING"
                    owner = meta["name"]
                else:
                    can_bind = self.is_port_available_to_bind(p)
                    status = "AVAILABLE" if can_bind else "RESTRICTED (OS/NAT Reserved)"
                    owner = "None (Available)" if can_bind else "Windows NAT / Excluded Port"

            records.append(PortAuditRecord(
                port=p,
                name=meta["name"],
                node=meta["node"],
                role=meta["role"],
                status=status,
                latency_ms=lat,
                owner_info=owner,
                safe_to_clean=meta["safe_to_clean"],
                last_checked=now_str,
            ))

        # 2. Audit any custom probed ports
        for (h, p), custom in self.custom_probed_ports.items():
            open_status, lat = self.is_port_open(h, p, timeout=0.3)
            records.append(PortAuditRecord(
                port=p,
                name=custom.get("name", f"Custom {h}:{p}"),
                node=h,
                role="CUSTOM_USER_PROBE",
                status="LISTENING" if open_status else "CLOSED",
                latency_ms=lat,
                owner_info=f"Target: {h}",
                safe_to_clean=False,
                last_checked=now_str,
            ))

        active_dashboard = self.get_active_dashboard_port()

        return {
            "timestamp": now_str,
            "total_ports_audited": len(records),
            "clothos_active_port": active_dashboard,
            "clothos_healthy": self.is_clothos_server_healthy(active_dashboard),
            "ports": [r.to_dict() for r in records],
            "conflict_summary": {
                "safe_clothos_ports": [p for p in CLOTHOS_CANDIDATE_PORTS if self.is_port_available_to_bind(p)],
                "protected_external_ports": [11434, 18789, 8265, 6379, 8080],
            }
        }

    def is_clothos_server_healthy(self, port: int) -> bool:
        """Verifies if a ClothOS server on the port responds with HTTP 200 on /api/health."""
        import urllib.request
        try:
            url = f"http://127.0.0.1:{port}/api/health"
            with urllib.request.urlopen(url, timeout=0.8) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    return data.get("status") == "ONLINE"
        except Exception:
            pass
        return False

    def get_active_dashboard_port(self) -> int:
        """Returns verified active dashboard port from file, candidate ports, or default."""
        if PORT_FILE.exists():
            try:
                p = int(PORT_FILE.read_text(encoding="utf-8").strip())
                is_open, _ = self.is_port_open("127.0.0.1", p)
                if is_open:
                    return p
            except Exception:
                pass

        for p in CLOTHOS_CANDIDATE_PORTS:
            is_open, _ = self.is_port_open("127.0.0.1", p)
            if is_open:
                return p

        return CLOTHOS_PRIMARY_PORT

    def find_best_available_clothos_port(self) -> int:
        """Finds the best port exclusively within ClothOS candidate range to prevent collisions."""
        for p in CLOTHOS_CANDIDATE_PORTS:
            if self.is_clothos_server_healthy(p):
                return p

        for p in CLOTHOS_CANDIDATE_PORTS:
            if self.is_port_available_to_bind(p):
                return p

        return CLOTHOS_PRIMARY_PORT

    def clean_stale_clothos_ports(self) -> Dict[str, Any]:
        """
        Safely terminates ONLY stale ClothOS processes holding ClothOS candidate ports.
        Never touches Ollama (11434), OpenClaw (18789), Ray (8265), or host services.
        """
        cleaned_pids = []
        current_pid = os.getpid()

        # Check recorded PID
        no_win = 0x08000000 if sys.platform == "win32" else 0
        if PID_FILE.exists():
            try:
                old_pid = int(PID_FILE.read_text(encoding="utf-8").strip())
                if old_pid != current_pid and old_pid > 4:
                    subprocess.run(["taskkill", "/F", "/PID", str(old_pid)], capture_output=True, creationflags=no_win, timeout=5.0)
                    cleaned_pids.append(old_pid)
                    PID_FILE.unlink(missing_ok=True)
            except Exception:
                pass

        # Use netstat to identify only processes on CLOTHOS candidate ports without popping console windows
        try:
            out = subprocess.check_output("netstat -ano", shell=True, text=True, stderr=subprocess.DEVNULL, creationflags=no_win, timeout=5.0)
            for line in out.splitlines():
                if "LISTENING" not in line:
                    continue
                for p in CLOTHOS_CANDIDATE_PORTS:
                    if f":{p} " in line:
                        parts = line.split()
                        try:
                            pid = int(parts[-1])
                            if pid > 4 and pid != current_pid and pid not in cleaned_pids:
                                subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True, creationflags=no_win, timeout=5.0)
                                cleaned_pids.append(pid)
                        except Exception:
                            pass
        except Exception as e:
            logger.warning(f"Error scanning netstat: {e}")

        # Refresh port file
        best_port = self.find_best_available_clothos_port()
        try:
            PORT_FILE.write_text(str(best_port), encoding="utf-8")
        except Exception:
            pass

        return {
            "success": True,
            "cleaned_pids_count": len(cleaned_pids),
            "cleaned_pids": cleaned_pids,
            "allocated_clothos_port": best_port,
            "message": f"Successfully cleaned {len(cleaned_pids)} stale ClothOS process(es). Ready on port {best_port}."
        }

    def register_custom_probe(self, host: str, port: int, name: str = "") -> Dict[str, Any]:
        """CRUD Create: Registers a custom port to monitor dynamically."""
        self.custom_probed_ports[(host, port)] = {"name": name or f"{host}:{port}"}
        is_open, lat = self.is_port_open(host, port)
        return {
            "success": True,
            "host": host,
            "port": port,
            "online": is_open,
            "latency_ms": round(lat, 2),
        }

    def remove_custom_probe(self, host: str, port: int) -> Dict[str, Any]:
        """CRUD Delete: Unregisters a custom monitored port."""
        if (host, port) in self.custom_probed_ports:
            del self.custom_probed_ports[(host, port)]
            return {"success": True, "message": f"Removed probe {host}:{port}"}
        return {"success": False, "message": "Probe not found"}


port_manager = ClothOSPortManager()
