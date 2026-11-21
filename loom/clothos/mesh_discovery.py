"""
ClothOS Dynamic Zero-Config Mesh Discovery & Beacon Daemon
File: loom/clothos/mesh_discovery.py
"""

import socket
import json
import time
import threading
import os
from pathlib import Path
from typing import Dict, Any, List

DISCOVERY_PORT = 5556
BROADCAST_INTERVAL = 5.0
PAUSE_FILE = Path(os.environ.get("USERPROFILE", ".")) / ".loom" / ".mesh_disconnected"

class MeshBeacon:
    def __init__(self, node_info: Dict[str, Any] = None):
        self.node_info = node_info or {}
        self.peers: Dict[str, Dict[str, Any]] = {}
        self._running = False
        self._cached_profile = None
        self._last_profile_time = 0

    @classmethod
    def is_disconnected(cls) -> bool:
        return PAUSE_FILE.exists()

    @classmethod
    def disconnect(cls):
        PAUSE_FILE.parent.mkdir(parents=True, exist_ok=True)
        PAUSE_FILE.write_text(f"Disconnected at {time.time()}", encoding="utf-8")

    @classmethod
    def reconnect(cls):
        if PAUSE_FILE.exists():
            PAUSE_FILE.unlink()

    def get_local_profile(self) -> Dict[str, Any]:
        now = time.time()
        if not self._cached_profile or (now - self._last_profile_time > 60.0):
            try:
                from loom.clothos.hardware_profile import get_hardware_profile
                self._cached_profile = get_hardware_profile()
            except Exception:
                self._cached_profile = {}
            self._last_profile_time = now
        return self._cached_profile

    def start(self):
        """Starts beacon broadcaster and listener daemon threads."""
        self._running = True
        t_recv = threading.Thread(target=self._listen_loop, daemon=True, name="ClothOS-Mesh-Listener")
        t_recv.start()
        t_send = threading.Thread(target=self._broadcast_loop, daemon=True, name="ClothOS-Mesh-Broadcaster")
        t_send.start()

    def _listen_loop(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("", DISCOVERY_PORT))
            s.settimeout(2.0)
            while self._running:
                try:
                    data, addr = s.recvfrom(8192)
                    payload = json.loads(data.decode("utf-8"))
                    peer_id = payload.get("hostname") or addr[0]
                    if payload.get("hostname") == socket.gethostname():
                        continue
                    if payload.get("status") == "DISCONNECTED":
                        self.peers.pop(peer_id, None)
                        continue
                    payload["last_seen"] = time.time()
                    payload["ip"] = addr[0]
                    self.peers[peer_id] = payload
                except (socket.timeout, TimeoutError):
                    continue
                except Exception:
                    continue
        except Exception:
            pass

    def _broadcast_loop(self):
        while self._running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                
                is_off = self.is_disconnected()
                profile = self.get_local_profile() if not is_off else {}
                payload = {
                    "hostname": socket.gethostname(),
                    "timestamp": time.time(),
                    "status": "DISCONNECTED" if is_off else "ONLINE",
                # Check stealth sentry state (zero disruption to user)
                sentry_state = {}
                try:
                    from loom.clothos.stealth_sentry import get_stealth_sentry
                    sentry_state = get_stealth_sentry().evaluate_state()
                except Exception:
                    pass
                "role": os.environ.get("CLOTHOS_ROLE", "auto"),
                "sentry": sentry_state,
                    "bridge_port": 5555,
                    "ollama_port": 11434,
                    "hardware": profile,
                    **self.node_info
                }
                data = json.dumps(payload).encode("utf-8")
                
                targets = ["255.255.255.255", "192.168.99.255", "192.168.1.255"]
                for tgt in targets:
                    try:
                        s.sendto(data, (tgt, DISCOVERY_PORT))
                    except Exception:
                        pass
                s.close()
            except Exception:
                pass
            time.sleep(BROADCAST_INTERVAL)

    def get_live_peers(self, max_age_seconds: float = 20.0) -> Dict[str, Dict[str, Any]]:
        now = time.time()
        active = {}
        for pid, p in list(self.peers.items()):
            if now - p.get("last_seen", 0) <= max_age_seconds:
                active[pid] = p
            else:
                self.peers.pop(pid, None)
        return active

_global_mesh = None

def get_mesh_beacon(node_info: Dict[str, Any] = None) -> MeshBeacon:
    global _global_mesh
    if _global_mesh is None:
        _global_mesh = MeshBeacon(node_info)
        _global_mesh.start()
    return _global_mesh