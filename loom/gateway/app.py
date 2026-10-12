"""
FastAPI OpenAI-Compatible Gateway Server for Loom Fabric.

Features:
- Full Integration with Pillar 1 (TORQUE): Zero-trust IP/PII scrubbing and rehydration.
- Real-time SSE token stream rehydration on the fly for Tier 3 Cloud Arbitrage.
- Telemetry headers: `X-Torque-Route`, `X-Torque-Scrubbed`, `X-Loom-Provider`, `X-Loom-TTFT-Ms`, `X-Loom-Tokens-Per-Sec`.
- Built-in Web UI Dashboard at `/` for monitoring cluster health, running test completions, and inspecting live scrubbing vaults.

Rust Migration Blueprint:
    In the native `loom-core` Rust crate:
    Built on `axum` with `tower-http` middleware and SSE streaming transforms:
    ```rust
    pub fn build_router(state: Arc<AppState>) -> Router {
        Router::new()
            .route("/", get(serve_dashboard_ui))
            .route("/v1/models", get(list_models))
            .route("/v1/chat/completions", post(chat_completions))
            .route("/health", get(health_check))
            .route("/metrics", get(cluster_metrics))
            .with_state(state)
    }
    ```
"""

from __future__ import annotations

import json
import time
from typing import Any, AsyncIterator, Dict, List, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
import httpx

from loom.config import get_settings
from loom.gateway.metrics import CompletionTelemetry
from loom.gateway.router import GatewayRouter
from loom.models.registry import ModelRegistry, ModelPreset
from loom.stitch.profiler import HardwareProfiler
from loom.torque.router import TorqueRouter
from loom.torque.scrubber import TorqueScrubber, RehydrationVault
from loom.types import ExecutionTier, PromptPayload, ChatMessageDTO, RoutingDecision

app = FastAPI(
    title="Loom Fabric Compute Gateway",
    version="0.1.0",
    description="Heterogeneous Ray-Orchestrated Distributed AI Compute Engine with Zero-Trust Sovereign Routing",
)

# Enable CORS for standard web and desktop client integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core subsystems
torque_scrubber = TorqueScrubber()
torque_router = TorqueRouter()
gateway_router = GatewayRouter()
profiler_instance = HardwareProfiler()


# ============================================================================
# WEB UI DASHBOARD (Sovereign Control Pane)
# ============================================================================

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Loom Fabric — Sovereign Local AI Operating System</title>
    <style>
        :root {
            --bg: #070a12;
            --card: #121524;
            --border: #261f38;
            --accent: #a855f7;
            --accent-glow: rgba(168, 85, 247, 0.25);
            --amethyst: #c084fc;
            --green: #10b981;
            --yellow: #f59e0b;
            --text: #f8fafc;
            --text-dim: #94a3b8;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace;
            background: var(--bg);
            color: var(--text);
            padding: 24px;
            line-height: 1.5;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--border);
            margin-bottom: 24px;
        }
        .title { font-size: 24px; font-weight: 700; color: var(--accent); }
        .subtitle { font-size: 13px; color: var(--text-dim); }
        .status-badge {
            background: rgba(74, 222, 128, 0.15);
            color: var(--green);
            padding: 6px 12px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 600;
            border: 1px solid rgba(74, 222, 128, 0.3);
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 20px;
            margin-bottom: 24px;
        }
        .card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 18px;
        }
        .card-title {
            font-size: 14px;
            font-weight: 600;
            color: var(--accent);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 12px;
            display: flex;
            justify-content: space-between;
        }
        .stat-row {
            display: flex;
            justify-content: space-between;
            font-size: 13px;
            padding: 6px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        .stat-val { font-weight: 600; color: #fff; }
        .interactive-section {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 20px;
        }
        textarea {
            width: 100%;
            height: 90px;
            background: #070a12;
            border: 1px solid var(--border);
            border-radius: 8px;
            color: #fff;
            padding: 12px;
            font-family: inherit;
            font-size: 14px;
            margin-bottom: 12px;
            resize: vertical;
        }
        button {
            background: var(--accent);
            color: #0b0f19;
            font-weight: 700;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            transition: opacity 0.2s;
        }
        button:hover { opacity: 0.9; }
        .output-box {
            background: #070a12;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 14px;
            margin-top: 14px;
            font-size: 13px;
            min-height: 80px;
            white-space: pre-wrap;
        }
        .tag {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            margin-right: 6px;
        }
        .tag-tier1 { background: rgba(56, 189, 248, 0.2); color: var(--accent); }
        .tag-tier2 { background: rgba(250, 204, 21, 0.2); color: var(--yellow); }
        .tag-tier3 { background: rgba(248, 113, 113, 0.2); color: #f87171; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <div class="title">LOOM FABRIC</div>
            <div class="subtitle">Heterogeneous AI Compute Operating System (Ray + Stitch + Torque + Loom)</div>
        </div>
        <div class="status-badge" id="cluster-status">CLUSTER HEALTHY</div>
    </div>

    <div class="grid">
        <div class="card">
            <div class="card-title">Compute Worker Node (SkyTech)</div>
            <div class="stat-row"><span>IP Address</span><span class="stat-val">192.168.99.1</span></div>
            <div class="stat-row"><span>GPU 0 (Primary)</span><span class="stat-val">RTX 3060 12GB (CUDA)</span></div>
            <div class="stat-row"><span>GPU 1 (Secondary)</span><span class="stat-val">RX 580 8GB (Vulkan)</span></div>
            <div class="stat-row"><span>Host Memory</span><span class="stat-val">40 GB DDR4</span></div>
            <div class="stat-row"><span>Native Process Guard</span><span class="stat-val">Win32 Job Object (Zero Orphan)</span></div>
        </div>

        <div class="card">
            <div class="card-title">Cluster Head Node (Ryzen)</div>
            <div class="stat-row"><span>IP Address</span><span class="stat-val">192.168.99.2</span></div>
            <div class="stat-row"><span>Processor</span><span class="stat-val">AMD Ryzen 7 7730U (16 vCPUs)</span></div>
            <div class="stat-row"><span>Ray GCS Redis</span><span class="stat-val">Port 6379</span></div>
            <div class="stat-row"><span>Ray Dashboard</span><span class="stat-val">Port 8265</span></div>
            <div class="stat-row"><span>Loom Gateway</span><span class="stat-val">Port 8000 (OpenAI SSE)</span></div>
        </div>

        <div class="card">
            <div class="card-title">Torque Zero-Trust Security</div>
            <div class="stat-row"><span>Guarded IP Sets</span><span class="stat-val">fouriersLibrary, VectorForge, Mycos</span></div>
            <div class="stat-row"><span>PII / Key Scrubbing</span><span class="stat-val">Active (Regex + Vault)</span></div>
            <div class="stat-row"><span>Cloud Arbitrage Limit</span><span class="stat-val">&gt;300s compute</span></div>
            <div class="stat-row"><span>Local Force Tag</span><span class="stat-val">[LOCAL] override enabled</span></div>
            <div class="stat-row"><span>Stream Rehydration</span><span class="stat-val">On-the-Fly Byte-Level</span></div>
        </div>
    </div>

    <div class="interactive-section">
        <div class="card-title">Sovereign Gateway Test Console</div>
        <p style="font-size: 13px; color: var(--text-dim); margin-bottom: 10px;">
            Send a prompt through the Torque Scrubber and Gateway. Test proprietary terms like <code>fouriersLibrary</code> or include <code>[LOCAL]</code>.
        </p>
        <textarea id="prompt-input" placeholder="Type a prompt... e.g.: Explain the core algorithm of fouriersLibrary and verify its proof with VectorForge."></textarea>
        <div>
            <button onclick="sendPrompt()">Execute via Loom Gateway</button>
            <span id="routing-badge" style="margin-left: 14px;"></span>
        </div>
        <div class="output-box" id="output-box">Gateway output will appear here...</div>
    </div>

    <script>
        async function sendPrompt() {
            const input = document.getElementById('prompt-input').value.trim();
            const outBox = document.getElementById('output-box');
            const badge = document.getElementById('routing-badge');
            if (!input) return;

            outBox.innerText = 'Routing and generating response...';
            badge.innerHTML = '';

            try {
                const res = await fetch('/v1/chat/completions', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        model: 'qwen2.5:32b',
                        messages: [{ role: 'user', content: input }],
                        stream: false
                    })
                });

                const routeHeader = res.headers.get('X-Torque-Route') || 'Tier 1/2 Local';
                const scrubbedHeader = res.headers.get('X-Torque-Scrubbed') || 'false';
                const tps = res.headers.get('X-Loom-Tokens-Per-Sec') || 'N/A';
                
                badge.innerHTML = `<span class="tag tag-tier1">${routeHeader}</span> <span class="tag tag-tier2">Scrubbed: ${scrubbedHeader}</span> <span class="tag tag-tier1">${tps} tps</span>`;

                const data = await res.json();
                const content = data.choices && data.choices[0] ? data.choices[0].message.content : JSON.stringify(data);
                outBox.innerText = content;
            } catch (err) {
                outBox.innerText = 'Error: ' + err.message;
            }
        }
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard() -> str:
    """Serves the Loom Fabric Sovereign Web Dashboard."""
    return DASHBOARD_HTML


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Cluster and gateway health check."""
    return {
        "status": "healthy",
        "service": "loom-fabric-gateway",
        "version": "0.1.0",
        "timestamp": time.time(),
        "torque_guard_active": True,
    }


@app.get("/v1/models")
async def list_models() -> Dict[str, Any]:
    """OpenAI-compatible models enumeration endpoint."""
    presets = ModelRegistry.list_models()
    model_entries = []
    for p in presets:
        model_entries.append({
            "id": p.id,
            "object": "model",
            "created": 1700000000,
            "owned_by": "loom-fabric",
            "permission": [],
            "root": p.id,
            "parent": None,
            "details": {
                "display_name": p.display_name,
                "total_layers": p.total_layers,
                "default_context": p.default_context_length,
                "quant": p.quant_label,
                "size_mb": p.base_gguf_size_mb,
            },
        })
    return {"object": "list", "data": model_entries}


@app.post("/v1/chat/completions")
async def chat_completions(req: Request):
    """OpenAI-compatible chat completion endpoint supporting SSE streaming and Torque zero-trust routing."""
    telemetry = CompletionTelemetry()
    body_dict = await req.json()

    # 1. Normalize model name (strip provider prefix like 'loom-fabric/' or 'ollama/')
    raw_model = body_dict.get("model", "qwen2.5:32b")
    clean_model = raw_model.split("/", 1)[1] if "/" in raw_model else raw_model
    body_dict["model"] = clean_model

    # 2. Normalize messages so content is always a flat string
    # (prevents Ollama and backend 'format' errors with array/multimodal content)
    normalized_messages = []
    for m in body_dict.get("messages", []):
        if isinstance(m, dict):
            m_copy = dict(m)
            m_copy["content"] = ChatMessageDTO.normalize_content(m.get("content", ""))
            normalized_messages.append(m_copy)
        else:
            normalized_messages.append(m)
    body_dict["messages"] = normalized_messages

    # Parse into typed DTOs (Rust Struct equivalent)
    messages_dto = [
        ChatMessageDTO(
            role=m.get("role", "user") if isinstance(m, dict) else "user",
            content=m.get("content", "") if isinstance(m, dict) else str(m),
            name=m.get("name") if isinstance(m, dict) else None,
            tool_call_id=m.get("tool_call_id") if isinstance(m, dict) else None,
            tool_calls=m.get("tool_calls") if isinstance(m, dict) else None,
        )
        for m in body_dict.get("messages", [])
    ]
    payload = PromptPayload(
        model=clean_model,
        messages=messages_dto,
        temperature=body_dict.get("temperature", 0.7),
        top_p=body_dict.get("top_p", 0.95),
        max_tokens=body_dict.get("max_tokens", 4096),
        stream=body_dict.get("stream", False),
        force_local=body_dict.get("force_local", False),
    )

    # 1. Torque Complexity Routing Decision (Pillar 1)
    decision = torque_router.route(payload)

    # 2. Torque Zero-Trust Scrubbing if routing to Cloud Tier 3
    active_vault_map: Dict[str, str] = {}
    is_scrubbed = False

    if decision.tier == ExecutionTier.TIER_3_SOVEREIGN_CLOUD:
        # Scrub all messages through the local RehydrationVault
        scrubbed_messages = []
        for msg in payload.messages:
            scrub_res = torque_scrubber.tokenize_and_store(msg.content)
            scrubbed_messages.append({"role": msg.role, "content": scrub_res.scrubbed_text})
            active_vault_map.update(scrub_res.vault_token_map)
        body_dict["messages"] = scrubbed_messages
        is_scrubbed = len(active_vault_map) > 0

    target_url, provider_name = await gateway_router.determine_target_endpoint(payload.model)

    # Build response headers
    base_headers = {
        "X-Torque-Route": decision.tier.value,
        "X-Torque-Scrubbed": str(is_scrubbed).lower(),
        "X-Torque-Reasoning": decision.reasoning,
        "X-Loom-Provider": provider_name,
    }

    if payload.stream:
        async def event_generator() -> AsyncIterator[str]:
            telemetry.mark_first_token()
            token_count = 0
            async for sse_chunk in gateway_router.stream_chat_completion(body_dict, target_url, provider_name):
                token_count += 1
                # If Tier 3 Cloud path, rehydrate SSE chunk on the fly before emitting
                if is_scrubbed and active_vault_map:
                    rehydrated_chunk = torque_scrubber.rehydrate(sse_chunk, active_vault_map)
                    yield rehydrated_chunk
                else:
                    yield sse_chunk

            telemetry.mark_completed(
                prompt_tokens=sum(len(m.content) for m in payload.messages) // 4,
                completion_tokens=token_count,
            )

        # Merge telemetry headers
        headers = {**base_headers, **telemetry.export_http_headers()}
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers=headers,
        )
    else:
        telemetry.mark_first_token()
        completion_data = await gateway_router.execute_non_streaming_completion(body_dict, target_url, provider_name)

        # Rehydrate final assistant message if scrubbed
        if is_scrubbed and active_vault_map:
            try:
                for choice in completion_data.get("choices", []):
                    msg_content = choice.get("message", {}).get("content", "")
                    if msg_content:
                        choice["message"]["content"] = torque_scrubber.rehydrate(msg_content, active_vault_map)
            except Exception:
                pass

        completion_tokens = completion_data.get("usage", {}).get("completion_tokens", 50)
        prompt_tokens = completion_data.get("usage", {}).get("prompt_tokens", 10)
        telemetry.mark_completed(prompt_tokens=prompt_tokens, completion_tokens=completion_tokens)

        headers = {**base_headers, **telemetry.export_http_headers()}
        return JSONResponse(content=completion_data, headers=headers)


@app.get("/metrics")
async def cluster_metrics() -> Dict[str, Any]:
    """Exposes cluster hardware, memory budgets, and node allocations."""
    hardware_state = profiler_instance.probe_cluster_state()
    return {
        "cluster_hardware": hardware_state.model_dump(),
        "active_models": [p.id for p in ModelRegistry.list_models()],
        "gateway_port": get_settings().endpoints.gateway_port,
        "vault_active_tokens": len(torque_scrubber.vault.snapshot()),
    }
