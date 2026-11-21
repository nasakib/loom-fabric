"""
Real-time Streaming Compute Meter for Spotlight-Local CSP Nodes.

Tracks token throughput, active VRAM reservations, time-to-first-token (TTFT),
and Landauer thermodynamic energy expenditure with microsecond precision.
"""

from __future__ import annotations

import time
import uuid
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class ComputeMeterReading(BaseModel):
    """Immutable record of an executed compute slice."""
    meter_id: str = Field(default_factory=lambda: f"mtr-{uuid.uuid4().hex[:12]}")
    session_id: str = Field(..., description="Unique caller session identifier")
    model_id: str = Field(..., description="Target model served")
    caller_geohash: Optional[str] = Field(None, description="Consumer spatial coordinate")
    
    start_time_epoch: float = Field(default_factory=time.time)
    end_time_epoch: Optional[float] = None
    ttft_seconds: float = Field(0.0, description="Time to first token in seconds")
    
    prompt_tokens: int = Field(0, description="Total input/context tokens consumed")
    completion_tokens: int = Field(0, description="Total output tokens generated")
    allocated_vram_gb: float = Field(0.0, description="Allocated VRAM footprint during execution")
    
    # Thermodynamics
    landauer_energy_microjoules: float = Field(
        0.0,
        description="Estimated Landauer thermodynamic energy dissipation in microjoules"
    )

    @property
    def duration_seconds(self) -> float:
        if self.end_time_epoch is None:
            return max(0.0, time.time() - self.start_time_epoch)
        return max(0.0, self.end_time_epoch - self.start_time_epoch)

    @property
    def tokens_per_second(self) -> float:
        active_gen_time = max(0.001, self.duration_seconds - self.ttft_seconds)
        return round(self.completion_tokens / active_gen_time, 2)


class StreamingComputeMeter:
    """
    Active stateful meter managing concurrent inference sessions on a CSP node.
    """
    def __init__(self, node_id: str, landauer_rating_pj_per_mac: float = 1.2):
        self.node_id = node_id
        self.landauer_rating = landauer_rating_pj_per_mac
        self._active_sessions: Dict[str, ComputeMeterReading] = {}
        self._completed_history: list[ComputeMeterReading] = []

    def start_session(
        self,
        session_id: str,
        model_id: str,
        caller_geohash: Optional[str] = None,
        allocated_vram_gb: float = 12.0
    ) -> ComputeMeterReading:
        reading = ComputeMeterReading(
            session_id=session_id,
            model_id=model_id,
            caller_geohash=caller_geohash,
            allocated_vram_gb=allocated_vram_gb,
            start_time_epoch=time.time()
        )
        self._active_sessions[session_id] = reading
        return reading

    def record_first_token(self, session_id: str) -> None:
        if session_id in self._active_sessions:
            reading = self._active_sessions[session_id]
            reading.ttft_seconds = round(time.time() - reading.start_time_epoch, 4)

    def increment_tokens(
        self,
        session_id: str,
        completion_delta: int = 1,
        prompt_total: Optional[int] = None
    ) -> None:
        if session_id in self._active_sessions:
            reading = self._active_sessions[session_id]
            reading.completion_tokens += completion_delta
            if prompt_total is not None:
                reading.prompt_tokens = prompt_total
            
            # Approximate FLOPs and Landauer dissipation:
            # Approx 2 FLOPs per parameter per token; assume 7B default
            mac_ops = (prompt_total or reading.prompt_tokens or 2048) * 7e9 + reading.completion_tokens * 7e9
            reading.landauer_energy_microjoules = round((mac_ops * self.landauer_rating) * 1e-6, 4)

    def finalize_session(
        self,
        session_id: str,
        final_prompt_tokens: Optional[int] = None,
        final_completion_tokens: Optional[int] = None
    ) -> ComputeMeterReading:
        if session_id not in self._active_sessions:
            raise KeyError(f"Session {session_id} not actively tracked by meter.")
        
        reading = self._active_sessions.pop(session_id)
        reading.end_time_epoch = time.time()
        if final_prompt_tokens is not None:
            reading.prompt_tokens = final_prompt_tokens
        if final_completion_tokens is not None:
            reading.completion_tokens = final_completion_tokens
            
        self._completed_history.append(reading)
        # Keep bounded history of last 500 records
        if len(self._completed_history) > 500:
            self._completed_history.pop(0)
            
        return reading

    def get_active_session(self, session_id: str) -> Optional[ComputeMeterReading]:
        return self._active_sessions.get(session_id)

    def get_summary_metrics(self) -> Dict[str, Any]:
        total_prompt = sum(r.prompt_tokens for r in self._completed_history)
        total_completion = sum(r.completion_tokens for r in self._completed_history)
        total_sessions = len(self._completed_history)
        return {
            "active_sessions_count": len(self._active_sessions),
            "completed_sessions_count": total_sessions,
            "lifetime_prompt_tokens": total_prompt,
            "lifetime_completion_tokens": total_completion,
            "average_ttft_seconds": round(
                sum(r.ttft_seconds for r in self._completed_history) / max(1, total_sessions), 4
            )
        }
