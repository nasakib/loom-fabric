"""Loom Fabric Configuration Module.

Defines global Pydantic v2 settings, network topology coordinates,
VRAM reservation constraints, and execution thresholds across the cluster.

Architecture Note (Rust Migration Target):
    This module mirrors the target Rust configuration crate `loom_core::config`:
    - `ClusterNodeConfig` -> `pub struct ClusterNodeConfig`
    - `MemoryBudgetConfig` -> `pub struct MemoryBudgetConfig`
    - `LoomGlobalSettings` -> `pub struct LoomGlobalSettings`
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class NodeEndpointConfig(BaseModel):
    """Network coordinate and hardware capability profile for a cluster node."""

    name: str = Field(..., description="Unique node identifier (e.g., 'skyTech', 'ryzenHead').")
    ip: str = Field(..., description="IPv4 address across the direct-wire or overlay mesh.")
    role: str = Field(..., description="Cluster role: 'head', 'worker', or 'hybrid'.")
    tailscale_ip: Optional[str] = Field(default="100.100.99.1", description="Secondary Tailscale overlay mesh IP.")
    wol_mac: Optional[str] = Field(default="00:D8:61:A4:7B:12", description="MAC address for Wake-on-LAN dispatch.")
    ray_port: int = Field(default=6379, description="Ray GCS connection port.")
    dashboard_port: int = Field(default=8265, description="Ray dashboard and job submission port.")
    stitch_port: int = Field(default=5555, description="Stitch Bridge node synchronization port.")
    gateway_port: int = Field(default=8002, description="Loom HTTP API Gateway port.")
    ollama_port: int = Field(default=11434, description="Local Ollama daemon port if present.")
    is_local: bool = Field(default=False, description="Whether this node corresponds to the local execution host.")


class MemoryBudgetConfig(BaseModel):
    """VRAM reservation and memory safety margins to prevent kernel driver OOM panics."""

    primary_display_reserved_mb: int = Field(
        default=1200,
        ge=256,
        description="VRAM in MB reserved for Windows DWM, display rasterization, and WDDM overhead on GPU 0.",
    )
    secondary_headless_reserved_mb: int = Field(
        default=300,
        ge=64,
        description="VRAM in MB reserved for secondary compute-only GPU (e.g., RX 580).",
    )
    system_ram_reserve_mb: int = Field(
        default=4096,
        ge=1024,
        description="Host system RAM in MB reserved for OS kernel, filesystem cache, and Ray daemons.",
    )
    kv_cache_quantization_bytes: int = Field(
        default=2,
        ge=1,
        le=4,
        description="Bytes per element in KV cache (2 for FP16/BF16, 1 for Q8_0/FP8, 0.5 for Q4_0).",
    )
    max_context_length_default: int = Field(
        default=32768,
        ge=2048,
        description="Default context window budget (tokens) if not overridden by model metadata.",
    )


class BinaryPathsConfig(BaseModel):
    """Filesystem locations of native binary runtimes."""

    bin_dir: Path = Field(
        default_factory=lambda: Path(os.path.expanduser("~/.loom/bin")),
        description="Directory containing native llama-server, rpc-server, and helper utilities.",
    )
    models_dir: Path = Field(
        default_factory=lambda: Path(os.path.expanduser("~/.loom/models")),
        description="Directory for cached GGUF model weight files.",
    )
    logs_dir: Path = Field(
        default_factory=lambda: Path(os.path.expanduser("~/.loom/logs")),
        description="Directory for rotating stdout/stderr process logs.",
    )

    @field_validator("bin_dir", "models_dir", "logs_dir", mode="after")
    @classmethod
    def ensure_directories_exist(cls, path: Path) -> Path:
        """Ensures that configured paths are expanded and created on the filesystem."""
        path.mkdir(parents=True, exist_ok=True)
        return path


class TorqueSecurityConfig(BaseModel):
    """Configuration for Zero-Trust Torque IP/PII Scrubber and Sovereign Router."""

    proprietary_terms: List[str] = Field(
        default_factory=lambda: [
            "fouriersLibrary",
            "Fourier's Library",
            "VectorForge",
            "Mycos",
            "BabelForge",
            "Gnorbit",
            "Spotlight Local",
            "ClothOS",
            "StitchBridge",
            "LoomFabric",
        ],
        description="Proprietary Protected IP keywords that must never leave sovereign local hardware.",
    )
    pii_patterns: Dict[str, str] = Field(
        default_factory=lambda: {
            "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,24}\b",
            "IPV4": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
            "API_KEY": r"\b(?:sk-[a-zA-Z0-9]{32,}|ghp_[a-zA-Z0-9]{36,}|AIzaSy[a-zA-Z0-9_-]{33})\b",
            "ETH_ADDR": r"\b0x[a-fA-F0-9]{40}\b",
        },
        description="Regular expressions for detecting sensitive tokens and secrets.",
    )
    ray_auth_token: str = Field(
        default="G-GzcZEzqteW241i720XeH5UNT73T6qk",
        description="Cluster-wide authentication token for Ray GCS, Job Submission, and ZeroMQ Bus.",
    )
    cloud_fallback_threshold_seconds: float = Field(
        default=300.0,
        description="Compute time threshold in seconds before offloading to cloud with scrubbing.",
    )
    cloud_api_url: str = Field(
        default="https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        description="Target upstream cloud endpoint for Tier 3 scrubbed queries.",
    )
    cloud_model: str = Field(
        default="gemini-2.5-flash",
        description="Upstream model to use for Tier 3 scrubbed completions.",
    )


class LoomSettings(BaseModel):
    """Global configuration object unifying Loom, Stitch, and Fabric subsystems."""

    torque: TorqueSecurityConfig = Field(default_factory=TorqueSecurityConfig, description="Torque zero-trust security configuration.")

    cluster_name: str = Field(default="loom-connectome", description="Identifier for the distributed compute fabric.")
    head_node: NodeEndpointConfig = Field(
        default_factory=lambda: NodeEndpointConfig(
            name="ryzenHead",
            ip="192.168.99.2",
            role="head",
            ray_port=6379,
            dashboard_port=8265,
            gateway_port=8000,
            is_local=False,
        ),
        description="Ray cluster head node coordinates.",
    )
    worker_nodes: List[NodeEndpointConfig] = Field(
        default_factory=lambda: [
            NodeEndpointConfig(
                name="skyTech",
                ip="192.168.99.1",
                role="worker",
                ray_port=6379,
                dashboard_port=8265,
                gateway_port=8000,
                is_local=True,
            )
        ],
        description="List of compute worker nodes registered in the cluster.",
    )
    memory: MemoryBudgetConfig = Field(default_factory=MemoryBudgetConfig, description="VRAM and RAM allocation guards.")
    paths: BinaryPathsConfig = Field(default_factory=BinaryPathsConfig, description="Filesystem paths for binaries and weights.")
    ray_init_timeout_seconds: int = Field(default=30, ge=5, description="Timeout for connecting to the Ray cluster head.")
    inference_timeout_seconds: int = Field(default=300, ge=30, description="Global timeout for generation requests.")

    @property
    def worker_native_url(self) -> str:
        """Returns the native worker HTTP endpoint URL."""
        worker = self.worker_nodes[0] if self.worker_nodes else self.head_node
        return f"http://{worker.ip}:8080"

    @property
    def endpoints(self) -> "LoomSettings":
        """Convenience accessor allowing settings.endpoints.worker_native_url."""
        return self

    @property
    def gateway_port(self) -> int:
        return self.head_node.gateway_port

    def get_node_by_name(self, name: str) -> Optional[NodeEndpointConfig]:
        """Looks up a cluster node by name."""
        if self.head_node.name.lower() == name.lower():
            return self.head_node
        for node in self.worker_nodes:
            if node.name.lower() == name.lower():
                return node
        return None

    def get_local_node(self) -> NodeEndpointConfig:
        """Returns the node flagged as local, or defaults to the first worker."""
        if self.head_node.is_local:
            return self.head_node
        for node in self.worker_nodes:
            if node.is_local:
                return node
        return self.worker_nodes[0]


# Global singleton settings instance
settings = LoomSettings()


def get_settings() -> LoomSettings:
    """Returns the global LoomSettings singleton instance."""
    return settings
