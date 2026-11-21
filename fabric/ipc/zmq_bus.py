"""
Stitch ZeroMQ IPC & Telemetry Bus (`fabric/ipc/zmq_bus.py`).

Enforces two core invariants:
1. All telemetry state frames are immutable `ConfigDict(frozen=True)` Pydantic v2 models.
2. Every outbound telemetry frame passes through the Torque Zero-Trust Enclave before
   being published on the bus or rendered in the Fabric / ClothOS UI.
"""

from __future__ import annotations

from collections import deque
import json
import time
from typing import Deque, Dict, List, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field

from loom.torque.enclave import TorqueEnclave


class TelemetryEnvelope(BaseModel):
    """Immutable, Torque-scrubbed telemetry frame transmitted over the Stitch ZeroMQ IPC bus."""

    model_config = ConfigDict(frozen=True)

    topic: str = Field(..., description="ZeroMQ pub/sub topic channel (e.g., 'clothos.dag', 'stitch.vram').")
    source_node: str = Field(..., description="Originating node IP or hostname.")
    timestamp_epoch: float = Field(..., description="High-resolution UTC timestamp.")
    sequence_id: int = Field(..., ge=0, description="Monotonically increasing frame sequence number.")
    torque_verified: bool = Field(default=True, description="True after passing Torque Enclave de-identification.")
    payload_json: str = Field(..., description="Torque-scrubbed JSON string of the telemetry state.")


class StitchZMQTelemetryBus:
    """High-throughput ZeroMQ IPC telemetry bus with automatic in-memory ring-buffer and TCP fallback."""

    def __init__(
        self,
        endpoint: str = "tcp://127.0.0.1:5559",
        enclave: Optional[TorqueEnclave] = None,
        max_ring_size: int = 256,
    ):
        self.endpoint = endpoint
        self.enclave = enclave or TorqueEnclave()
        self._seq = 0
        self._ring: Deque[TelemetryEnvelope] = deque(maxlen=max_ring_size)
        self._zmq_ctx = None
        self._pub_socket = None
        self._tcp_server = None
        self._tcp_clients = set()
        self._tcp_lock = None

        # Parse host and port from endpoint (e.g., 'tcp://127.0.0.1:5559' or 'tcp://0.0.0.0:5559')
        raw = endpoint.replace("tcp://", "")
        parts = raw.split(":")
        self._host = parts[0] if parts[0] not in ("*", "") else "0.0.0.0"
        self._port = int(parts[1]) if len(parts) > 1 else 5559

        # Attempt 1: Real ZeroMQ PUB socket
        try:
            import zmq  # type: ignore

            self._zmq_ctx = zmq.Context.instance()
            self._pub_socket = self._zmq_ctx.socket(zmq.PUB)
            self._pub_socket.setsockopt(zmq.LINGER, 0)
            try:
                self._pub_socket.bind(self.endpoint)
            except Exception:
                # If already bound by broker_daemon, connect to existing broker
                try:
                    self._pub_socket.connect(self.endpoint)
                except Exception:
                    pass
        except Exception:
            self._zmq_ctx = None
            self._pub_socket = None

            # Attempt 2: Resilient Native Python TCP Telemetry Broadcaster
            try:
                import socket
                import threading

                self._tcp_lock = threading.Lock()
                srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                try:
                    srv.bind((self._host, self._port))
                    srv.listen(16)
                    self._tcp_server = srv

                    def _listen_loop():
                        while self._tcp_server:
                            try:
                                client_sock, _ = self._tcp_server.accept()
                                with self._tcp_lock:
                                    self._tcp_clients.add(client_sock)
                            except Exception:
                                break

                    t = threading.Thread(target=_listen_loop, daemon=True, name="zmq-tcp-fallback")
                    t.start()
                except Exception:
                    srv.close()
                    self._tcp_server = None
            except Exception:
                self._tcp_server = None

    def publish(self, topic: str, source_node: str, raw_payload: Dict[str, object]) -> TelemetryEnvelope:
        """Scrubs `raw_payload` through the Torque Enclave and publishes an immutable `TelemetryEnvelope`."""
        self._seq += 1
        raw_str = json.dumps(raw_payload, sort_keys=True, default=str)
        scrubbed = self.enclave.scrub_outbound(raw_str)

        envelope = TelemetryEnvelope(
            topic=topic,
            source_node=source_node,
            timestamp_epoch=time.time(),
            sequence_id=self._seq,
            torque_verified=True,
            payload_json=scrubbed.sanitized_text,
        )
        self._ring.append(envelope)

        if self._pub_socket is not None:
            try:
                wire = f"{topic} {envelope.model_dump_json()}".encode("utf-8")
                self._pub_socket.send(wire, flags=1)  # DONTWAIT
            except Exception:
                pass

        if self._tcp_server is not None and self._tcp_lock is not None:
            dead_clients = []
            msg = (f"{topic} {envelope.model_dump_json()}\n").encode("utf-8")
            with self._tcp_lock:
                for c in list(self._tcp_clients):
                    try:
                        c.sendall(msg)
                    except Exception:
                        dead_clients.append(c)
                for d in dead_clients:
                    self._tcp_clients.discard(d)
                    try:
                        d.close()
                    except Exception:
                        pass

        return envelope

    def close(self) -> None:
        """Closes sockets and frees networking resources."""
        if self._pub_socket is not None:
            try:
                self._pub_socket.close(linger=0)
            except Exception:
                pass
            self._pub_socket = None

        if self._tcp_server is not None:
            try:
                self._tcp_server.close()
            except Exception:
                pass
            self._tcp_server = None

        if self._tcp_lock is not None:
            with self._tcp_lock:
                for c in self._tcp_clients:
                    try:
                        c.close()
                    except Exception:
                        pass
                self._tcp_clients.clear()

    def recent_frames(self, limit: int = 25, topic_prefix: Optional[str] = None) -> Tuple[TelemetryEnvelope, ...]:
        """Returns the most recent Torque-verified telemetry frames from the bus."""
        items = list(self._ring)
        if topic_prefix:
            items = [f for f in items if f.topic.startswith(topic_prefix)]
        return tuple(items[-limit:])
