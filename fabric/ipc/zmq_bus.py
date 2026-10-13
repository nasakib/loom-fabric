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
    """High-throughput ZeroMQ IPC telemetry bus with automatic in-memory ring-buffer fallback."""

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

        try:
            import zmq  # type: ignore

            self._zmq_ctx = zmq.Context.instance()
            self._pub_socket = self._zmq_ctx.socket(zmq.PUB)
            self._pub_socket.setsockopt(zmq.LINGER, 0)
        except Exception:
            self._zmq_ctx = None
            self._pub_socket = None

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

        return envelope

    def recent_frames(self, limit: int = 25, topic_prefix: Optional[str] = None) -> Tuple[TelemetryEnvelope, ...]:
        """Returns the most recent Torque-verified telemetry frames from the bus."""
        items = list(self._ring)
        if topic_prefix:
            items = [f for f in items if f.topic.startswith(topic_prefix)]
        return tuple(items[-limit:])
