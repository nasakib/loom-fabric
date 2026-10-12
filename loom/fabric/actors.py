"""Distributed Stateful Ray Actors for Multi-Node Inference Orchestration.

Defines the core Ray Actors:
1. `InferenceDirector`: Resides on the Head node, manages global state, routing, and telemetry.
2. `WorkerNodeSupervisor`: Placed on the GPU worker node via `resources={"NODE_WORKER": 1}`,
   orchestrating local native processes and layer sharding.
3. `DraftInferenceActor`: Placed on CPU/Vulkan nodes for low-latency speculative draft token generation.

Architecture Note (Rust Migration Target):
    This module maps to `loom_fabric::actors` in Rust:
    - Actor state machines implemented via asynchronous Tokio channels and actor mailboxes.
    - Zero-allocation tensor buffers across actor boundaries.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any, AsyncIterator, Dict, List, Optional
import httpx
import ray

from ..stitch.profiler import HardwareProfiler, ClusterHardwareState
from ..stitch.allocator import LayerAllocator, ModelArchitectureProfile, LayerShardingPlan
from ..stitch.supervisor import NativeProcessSupervisor, ProcessHealthStatus

logger = logging.getLogger("loom.fabric.actors")


@ray.remote(resources={"NODE_WORKER": 1})
class WorkerNodeSupervisor:
    """Ray Actor executing on the GPU Worker node managing native llama-server instances."""

    def __init__(self, node_name: str = "skyTech"):
        """Initializes the worker supervisor actor."""
        self.node_name = node_name
        self.profiler = HardwareProfiler(node_name=self.node_name)
        self.current_hardware_state = self.profiler.probe_cluster_state()
        self.allocator = LayerAllocator(self.current_hardware_state)
        self.process_supervisor = NativeProcessSupervisor()
        self.active_plan: Optional[LayerShardingPlan] = None
        self.active_model_name: Optional[str] = None
        logger.info(f"WorkerNodeSupervisor actor initialized on {self.node_name}.")

    def probe_hardware(self) -> Dict[str, Any]:
        """Refreshes and returns the physical hardware state."""
        self.current_hardware_state = self.profiler.probe_cluster_state()
        return self.current_hardware_state.model_dump()

    def compute_sharding_plan(self, model_dict: Dict[str, Any], allow_cpu_spill: bool = True) -> Dict[str, Any]:
        """Calculates a zero-OOM layer sharding plan for the requested model."""
        model_profile = ModelArchitectureProfile(**model_dict)
        plan = self.allocator.calculate_plan(model_profile, allow_cpu_spill=allow_cpu_spill)
        return plan.model_dump()

    def launch_model(
        self,
        model_path_str: str,
        model_dict: Dict[str, Any],
        port: int = 8080,
    ) -> Dict[str, Any]:
        """Calculates sharding and spawns the native llama-server binary.

        Args:
            model_path_str: Path to the GGUF model file.
            model_dict: Structural architecture metrics for budgeting.
            port: Port for the native backend.

        Returns:
            Dictionary representation of ProcessHealthStatus.
        """
        # Terminate any previously running process
        self.process_supervisor.terminate()

        model_path = Path(model_path_str)
        model_profile = ModelArchitectureProfile(**model_dict)
        self.active_plan = self.allocator.calculate_plan(model_profile, allow_cpu_spill=True)
        self.active_model_name = model_profile.name

        status = self.process_supervisor.spawn(
            model_path=model_path,
            sharding_plan=self.active_plan,
            port=port,
        )

        return {
            "status": status.model_dump(),
            "sharding_plan": self.active_plan.model_dump(),
        }

    async def await_ready(self, timeout_seconds: float = 60.0) -> bool:
        """Asynchronously waits until the local llama-server passes health checks."""
        return await self.process_supervisor.wait_until_healthy(timeout_seconds=timeout_seconds)

    def get_status(self) -> Dict[str, Any]:
        """Returns the current execution and health status of the managed worker."""
        is_running = (
            self.process_supervisor.process is not None
            and self.process_supervisor.process.poll() is None
        )
        return {
            "node_name": self.node_name,
            "is_running": is_running,
            "active_model": self.active_model_name,
            "endpoint_url": self.process_supervisor.endpoint_url,
            "sharding_plan": self.active_plan.model_dump() if self.active_plan else None,
        }

    def terminate_backend(self) -> bool:
        """Terminates the local backend process."""
        self.process_supervisor.terminate()
        return True


@ray.remote(num_cpus=2)
class DraftInferenceActor:
    """Ray Actor running lightweight models for speculative decoding on the Head CPU or secondary GPU."""

    def __init__(self, draft_model_name: str = "qwen2.5:3b"):
        self.draft_model_name = draft_model_name
        self.is_ready = True
        logger.info(f"DraftInferenceActor initialized with draft model '{draft_model_name}'.")

    async def generate_draft_tokens(self, prompt: str, max_draft_tokens: int = 5) -> List[str]:
        """Generates speculative candidate tokens for rapid verification by the primary worker.

        Args:
            prompt: Text prefix.
            max_draft_tokens: Number of draft tokens to speculate.

        Returns:
            List of generated draft token strings.
        """
        # Connect to local Ollama on 127.0.0.1:11434 if available for rapid drafting
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.post(
                    "http://127.0.0.1:11434/api/generate",
                    json={
                        "model": self.draft_model_name,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"num_predict": max_draft_tokens, "temperature": 0.2},
                    },
                )
                if res.status_code == 200:
                    text = res.json().get("response", "")
                    return text.split()[:max_draft_tokens]
        except Exception:
            pass

        return []


@ray.remote(num_cpus=1)
class InferenceDirector:
    """Cluster Head Actor coordinating global routing, worker discovery, and completion dispatches."""

    def __init__(self):
        """Initializes the director actor on the Ray Head node."""
        self.worker_supervisor_handle: Optional[Any] = None
        self.draft_actor_handle: Optional[Any] = None
        self.active_model: Optional[str] = None
        self.worker_endpoint: str = "http://192.168.99.1:8080"
        logger.info("InferenceDirector initialized on cluster head.")

    def register_worker_supervisor(self, supervisor_handle: Any) -> bool:
        """Registers the active WorkerNodeSupervisor actor handle."""
        self.worker_supervisor_handle = supervisor_handle
        logger.info("WorkerNodeSupervisor successfully registered with InferenceDirector.")
        return True

    def register_draft_actor(self, draft_handle: Any) -> bool:
        """Registers the speculative DraftInferenceActor handle."""
        self.draft_actor_handle = draft_handle
        return True

    async def dispatch_completion(
        self,
        request_payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Dispatches an inference query to the active worker backend.

        Args:
            request_payload: OpenAI-compatible completion request body.

        Returns:
            Completion response payload.
        """
        # Forward to worker native endpoint
        target_url = f"{self.worker_endpoint}/v1/chat/completions"
        async with httpx.AsyncClient(timeout=300.0) as client:
            res = await client.post(target_url, json=request_payload)
            return res.json()

    def get_cluster_status(self) -> Dict[str, Any]:
        """Aggregates cluster health across all managed actors."""
        return {
            "director_status": "ONLINE",
            "has_worker_registered": self.worker_supervisor_handle is not None,
            "has_draft_registered": self.draft_actor_handle is not None,
            "worker_endpoint": self.worker_endpoint,
        }
