"""
Gateway Request Routing and Backend Dispatcher.

Directs incoming OpenAI completion requests dynamically:
- To Ray Cluster's InferenceDirector if Ray is connected and active.
- To local Stitch Worker supervisor if operating in standalone/direct mode.
- Fallback to local Ollama API (11434) if native llama-server is not running.

Rust Migration Blueprint:
    In the native `loom-core` Rust crate:
    ```rust
    pub struct GatewayRouter {
        pub director: Option<Arc<InferenceDirector>>,
        pub local_backend: Option<Arc<StitchSupervisor>>,
        pub fallback_ollama_url: String,
    }
    ```
"""

from __future__ import annotations

import json
import logging
from typing import Any, AsyncIterator, Dict, Optional, Tuple
import httpx

from loom.config import get_settings
from loom.fabric.cluster import RayClusterManager
from loom.models.registry import ModelRegistry

logger = logging.getLogger("loom.gateway.router")


class GatewayRouter:
    """Intelligent request router with multi-tier failover and streaming proxy support."""

    def __init__(self, ray_manager: Optional[RayClusterManager] = None):
        self.settings = get_settings()
        self.ray_manager = ray_manager or RayClusterManager()
        self.client = httpx.AsyncClient(timeout=httpx.Timeout(300.0, connect=5.0))

    async def determine_target_endpoint(
        self,
        model_name: str,
        tier: Optional[Any] = None,
        cloud_url: Optional[str] = None,
    ) -> Tuple[str, str]:
        """Determines the best available backend URL and provider name for the request.

        Returns:
            Tuple of (endpoint_url, provider_name)
        """
        # 0. Check if routed to Tier 3 Sovereign Cloud
        if tier and ("cloud" in str(tier).lower() or "tier_3" in str(tier).lower()):
            target = cloud_url or self.settings.torque.cloud_api_url
            return target, "Sovereign-Cloud-Arbitrage"

        # 1. Check if Ray cluster is active with registered director
        if self.ray_manager.is_connected:
            try:
                import ray
                from loom.fabric.actors import InferenceDirector
                director = ray.get_actor("InferenceDirector")
                status = ray.get(director.get_cluster_status.remote())
                if status.get("worker_endpoint"):
                    return status["worker_endpoint"], "Ray-Fabric-Cluster"
            except Exception as e:
                logger.debug(f"Ray director lookup skipped: {e}")

        # 2. Check primary Stitch native backend on desktop worker (port 8080)
        worker_endpoint = self.settings.endpoints.worker_native_url
        try:
            res = await self.client.get(f"{worker_endpoint}/health", timeout=1.0)
            if res.status_code == 200:
                return worker_endpoint, "Stitch-Native-Worker"
        except Exception:
            pass

        # 3. Check local Stitch native backend on localhost (port 8080)
        try:
            res = await self.client.get("http://127.0.0.1:8080/health", timeout=1.0)
            if res.status_code == 200:
                return "http://127.0.0.1:8080", "Stitch-Local-Direct"
        except Exception:
            pass

        # 4. Fallback to local Ollama on 127.0.0.1:11434 or 192.168.99.1:11434
        for ollama_host in ["http://127.0.0.1:11434", "http://192.168.99.1:11434"]:
            try:
                res = await self.client.get(f"{ollama_host}/api/version", timeout=1.0)
                if res.status_code == 200:
                    return ollama_host, "Ollama-Local-Fallback"
            except Exception:
                pass

        # Default fallback to configured worker endpoint
        return worker_endpoint, "Stitch-Default"

    async def stream_chat_completion(
        self,
        payload: Dict[str, Any],
        target_url: str,
        provider_name: str,
    ) -> AsyncIterator[str]:
        """Streams Server-Sent Events (SSE) from the underlying backend to the gateway client."""
        model_name = payload.get("model", "default")
        if "/" in model_name:
            model_name = model_name.split("/", 1)[1]
        preset = ModelRegistry.get_model(model_name)
        sharding_info = f"Layers: {preset.total_layers} ({preset.quant_label})" if preset else "Dynamic"

        if "Ollama" in provider_name:
            # Format request for Ollama /api/chat with streaming
            ollama_payload = {
                "model": preset.ollama_tag if preset and preset.ollama_tag else model_name,
                "messages": payload.get("messages", []),
                "stream": True,
                "options": {
                    "temperature": payload.get("temperature", 0.7),
                    "num_ctx": payload.get("max_tokens", 8192),
                },
            }
            async with self.client.stream(
                "POST",
                f"{target_url}/api/chat",
                json=ollama_payload,
                timeout=300.0,
            ) as response:
                async for chunk in response.aiter_lines():
                    if not chunk:
                        continue
                    try:
                        data = json.loads(chunk)
                        delta_content = data.get("message", {}).get("content", "")
                        done = data.get("done", False)

                        openai_chunk = {
                            "id": f"chatcmpl-{model_name}",
                            "object": "chat.completion.chunk",
                            "created": 1700000000,
                            "model": model_name,
                            "choices": [
                                {
                                    "index": 0,
                                    "delta": {"content": delta_content} if delta_content else {},
                                    "finish_reason": "stop" if done else None,
                                }
                            ],
                        }
                        yield f"data: {json.dumps(openai_chunk)}\n\n"
                        if done:
                            yield "data: [DONE]\n\n"
                            break
                    except Exception:
                        continue
        else:
            # Native llama-server or OpenAI-compatible backend
            async with self.client.stream(
                "POST",
                f"{target_url}/v1/chat/completions",
                json=payload,
                timeout=300.0,
            ) as response:
                async for chunk in response.aiter_lines():
                    if chunk:
                        yield f"{chunk}\n\n"

    async def execute_non_streaming_completion(
        self,
        payload: Dict[str, Any],
        target_url: str,
        provider_name: str,
    ) -> Dict[str, Any]:
        """Dispatches a synchronous/non-streaming completion request."""
        model_name = payload.get("model", "default")
        if "/" in model_name:
            model_name = model_name.split("/", 1)[1]
        preset = ModelRegistry.get_model(model_name)

        if "Ollama" in provider_name:
            ollama_payload = {
                "model": preset.ollama_tag if preset and preset.ollama_tag else model_name,
                "messages": payload.get("messages", []),
                "stream": False,
                "options": {
                    "temperature": payload.get("temperature", 0.7),
                    "num_ctx": payload.get("max_tokens", 8192),
                },
            }
            res = await self.client.post(f"{target_url}/api/chat", json=ollama_payload, timeout=300.0)
            res.raise_for_status()
            data = res.json()
            content = data.get("message", {}).get("content", "")
            return {
                "id": f"chatcmpl-{model_name}",
                "object": "chat.completion",
                "created": 1700000000,
                "model": model_name,
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": content},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": data.get("prompt_eval_count", 0),
                    "completion_tokens": data.get("eval_count", 0),
                    "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
                },
            }
        else:
            res = await self.client.post(f"{target_url}/v1/chat/completions", json=payload, timeout=300.0)
            res.raise_for_status()
            return res.json()
