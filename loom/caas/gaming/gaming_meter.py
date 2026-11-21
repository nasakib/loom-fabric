"""
VectorCore ClothOS Real-Time Gaming Stream Meter.

Meters cloud gaming sessions by frame throughput, resolution, bitrate,
network RTT, and hardware encoding overhead with sub-millisecond precision.
"""

from __future__ import annotations

import time
import uuid
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class GamingStreamMetrics(BaseModel):
    """Real-time metrics for an active cloud gaming stream."""
    session_id: str
    consumer_account_id: str
    provider_node_id: str
    resolution: str = "1920x1080"
    target_fps: int = 60
    bitrate_mbps: float = 25.0
    start_time_epoch: float = Field(default_factory=time.time)
    last_heartbeat_epoch: float = Field(default_factory=time.time)
    total_frames_rendered: int = 0
    dropped_frames: int = 0
    average_encode_latency_ms: float = 2.1
    network_rtt_ms: float = 1.2
    hourly_rate_usd: float = 0.45
    accumulated_cost_usd: float = 0.0

    @property
    def duration_seconds(self) -> float:
        return max(0.0, self.last_heartbeat_epoch - self.start_time_epoch)

    @property
    def effective_fps(self) -> float:
        if self.duration_seconds <= 0:
            return float(self.target_fps)
        return round(self.total_frames_rendered / self.duration_seconds, 1)

    @property
    def rate_per_second_usd(self) -> float:
        return round(self.hourly_rate_usd / 3600.0, 6)

    def to_dict(self) -> Dict[str, Any]:
        d = self.dict()
        d["duration_seconds"] = round(self.duration_seconds, 2)
        d["effective_fps"] = self.effective_fps
        d["rate_per_second_usd"] = self.rate_per_second_usd
        return d


class GamingStreamMeter:
    """Stateful meter for tracking active cloud gaming sessions."""

    def __init__(self, hourly_base_rate_usd: float = 0.45):
        self.hourly_base_rate = hourly_base_rate_usd
        self.active_sessions: Dict[str, GamingStreamMetrics] = {}

    def start_session(
        self,
        session_id: str,
        consumer_account_id: str,
        provider_node_id: str,
        resolution: str = "1920x1080",
        target_fps: int = 60,
        bitrate_mbps: float = 25.0,
        hourly_rate_override: Optional[float] = None,
    ) -> GamingStreamMetrics:
        rate = hourly_rate_override or self.hourly_base_rate
        # Higher tier resolutions/fps scale pricing moderately
        if "4K" in resolution or "3840" in resolution or target_fps >= 120:
            rate = round(rate * 1.5, 4)

        metrics = GamingStreamMetrics(
            session_id=session_id,
            consumer_account_id=consumer_account_id,
            provider_node_id=provider_node_id,
            resolution=resolution,
            target_fps=target_fps,
            bitrate_mbps=bitrate_mbps,
            hourly_rate_usd=rate,
        )
        self.active_sessions[session_id] = metrics
        return metrics

    def record_heartbeat(
        self,
        session_id: str,
        frames_increment: int,
        dropped_increment: int = 0,
        encode_latency_ms: float = 2.0,
        network_rtt_ms: float = 1.0,
    ) -> GamingStreamMetrics:
        if session_id not in self.active_sessions:
            raise KeyError(f"Gaming session {session_id} not found.")

        metrics = self.active_sessions[session_id]
        now = time.time()
        elapsed = max(0.0, now - metrics.last_heartbeat_epoch)
        metrics.last_heartbeat_epoch = now
        metrics.total_frames_rendered += frames_increment
        metrics.dropped_frames += dropped_increment
        metrics.average_encode_latency_ms = encode_latency_ms
        metrics.network_rtt_ms = network_rtt_ms

        # Calculate incremental cost
        cost_inc = round(elapsed * metrics.rate_per_second_usd, 6)
        metrics.accumulated_cost_usd = round(metrics.accumulated_cost_usd + cost_inc, 6)
        return metrics

    def finalize_session(self, session_id: str) -> GamingStreamMetrics:
        if session_id not in self.active_sessions:
            raise KeyError(f"Gaming session {session_id} not found.")
        metrics = self.active_sessions[session_id]
        metrics.last_heartbeat_epoch = time.time()
        return metrics
