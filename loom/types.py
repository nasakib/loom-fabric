"""
Protocol Interfaces (Traits) and Strict Data Transfer Objects (Structs) for Loom Fabric.

Rust & ClothOS Invariants:
    This file maps 1:1 to `loom-core/src/types.rs` in the native Rust / ClothOS codebase:
    - `typing.Protocol` maps to `pub trait TraitName`
    - `pydantic.BaseModel` with `frozen=True` maps to `#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)] pub struct`
    - Explicit enumerations map to `pub enum`
    - Generic `Result[T, E]` maps to `std::result::Result<T, E>`
"""

from __future__ import annotations

from enum import Enum
from typing import (
    Any,
    AsyncIterator,
    Callable,
    Dict,
    Generic,
    List,
    Mapping,
    Optional,
    Protocol,
    Tuple,
    TypeVar,
    Union,
    runtime_checkable,
)
from pydantic import BaseModel, ConfigDict, Field, field_validator


# ============================================================================
# DETERMINISTIC RESULT MONAD (Rust: std::result::Result<T, E>)
# ============================================================================

T = TypeVar("T")
E = TypeVar("E")


class Ok(Generic[T]):
    """Represents a successful outcome holding value of type T."""
    __slots__ = ("_value",)

    def __init__(self, value: T) -> None:
        self._value = value

    @property
    def value(self) -> T:
        return self._value

    def is_ok(self) -> bool:
        return True

    def is_err(self) -> bool:
        return False

    def unwrap(self) -> T:
        return self._value

    def unwrap_err(self) -> Any:
        raise ValueError("Called unwrap_err on Ok")

    def __repr__(self) -> str:
        return f"Ok({self._value!r})"


class Err(Generic[E]):
    """Represents a failed outcome holding error of type E."""
    __slots__ = ("_error",)

    def __init__(self, error: E) -> None:
        self._error = error

    @property
    def error(self) -> E:
        return self._error

    def is_ok(self) -> bool:
        return False

    def is_err(self) -> bool:
        return True

    def unwrap(self) -> Any:
        raise ValueError(f"Called unwrap on Err: {self._error!r}")

    def unwrap_err(self) -> E:
        return self._error

    def __repr__(self) -> str:
        return f"Err({self._error!r})"


Result = Union[Ok[T], Err[E]]


# ============================================================================
# ENUMERATIONS (Rust: pub enum)
# ============================================================================

class ExecutionTier(str, Enum):
    """Execution tiers for complexity routing and sovereign arbitrage."""
    TIER_1_LOCAL_RAPID = "tier_1_local_rapid"          # Low-latency RTX 3060 CUDA (14B/7B)
    TIER_2_DISTRIBUTED_DAG = "tier_2_distributed_dag"  # Heterogeneous Ray Cluster (Ryzen + RX 580)
    TIER_3_SOVEREIGN_CLOUD = "tier_3_sovereign_cloud"  # Scrubbed Zero-Trust Cloud Arbitrage (>300s compute)
    TIER_1_DETERMINISTIC = "tier_1_deterministic"      # Standard sequential inference on local RTX 3060
    TIER_2_THERMODYNAMIC = "tier_2_thermodynamic"      # Z3 SMT constraints / QUBO on simulated p-bit solvers
    TIER_3_QUANTUM_CLOUD = "tier_3_quantum_cloud"      # Quantum / Cloud fallback (>300s) with Zero-Trust scrub


class AcceleratorVendor(str, Enum):
    """Supported physical accelerator hardware vendors."""
    NVIDIA = "nvidia"
    AMD = "amd"
    INTEL = "intel"
    CPU_HOST = "cpu_host"


class ComputeBackend(str, Enum):
    """Kernel execution runtime backend."""
    CUDA = "cuda"
    VULKAN = "vulkan"
    ROCM = "rocm"
    CPU = "cpu"


class QuantizationType(str, Enum):
    """Supported GGUF weight quantization formats."""
    FP16 = "FP16"
    Q8_0 = "Q8_0"
    Q6_K = "Q6_K"
    Q5_K_M = "Q5_K_M"
    Q4_K_M = "Q4_K_M"
    Q4_0 = "Q4_0"
    Q3_K_M = "Q3_K_M"


# ============================================================================
# IMMUTABLE DATA TRANSFER OBJECTS (Rust: pub struct)
# ============================================================================

class ChatMessageDTO(BaseModel):
    """Single chat message with multimodal block flattening."""
    model_config = ConfigDict(frozen=True)

    role: str = Field("user", description="Message author role: 'system', 'user', or 'assistant'")
    content: str = Field("", description="Raw flat text payload of the message")
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None

    @field_validator("content", mode="before")
    @classmethod
    def normalize_content(cls, v: Any) -> str:
        if v is None:
            return ""
        if isinstance(v, str):
            return v
        if isinstance(v, list):
            parts = []
            for item in v:
                if isinstance(item, dict) and item.get("type") == "text":
                    parts.append(str(item.get("text", "")))
                elif isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict) and "text" in item:
                    parts.append(str(item["text"]))
            return "\n".join(parts)
        return str(v)


class PromptPayload(BaseModel):
    """Complete incoming generation request DTO."""
    model_config = ConfigDict(frozen=True)

    model: str = Field(..., description="Model identifier requested by caller")
    messages: List[ChatMessageDTO] = Field(..., description="Chronological conversation transcript")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Sampling randomness")
    top_p: float = Field(0.95, ge=0.0, le=1.0, description="Nucleus sampling probability")
    max_tokens: int = Field(4096, ge=1, le=131072, description="Maximum completion tokens")
    stream: bool = Field(False, description="Whether to emit Server-Sent Events (SSE)")
    force_local: bool = Field(False, description="Forced override to bypass cloud routing")
    airgap: bool = Field(False, description="Strict air-gap flag: absolutely zero external egress")


class RoutingDecision(BaseModel):
    """Decision output generated by the Torque complexity router."""
    model_config = ConfigDict(frozen=True)

    tier: ExecutionTier = Field(..., description="Selected execution tier")
    estimated_duration_seconds: float = Field(..., description="Calculated duration heuristic")
    target_endpoint: str = Field(..., description="HTTP or RPC address where inference will execute")
    is_scrubbed: bool = Field(..., description="Whether prompt requires Vault anonymization")
    model_name: str = Field(..., description="Resolved model identifier")
    reasoning: str = Field(..., description="Audit rationale explaining the routing choice")
    circuit_breaker_triggered: bool = Field(False, description="Whether 300s limit tripped manual confirmation")
    requires_manual_approval: bool = Field(False, description="Whether user approval is needed before cloud dispatch")
    routing_alert: Optional[str] = Field(None, description="Optional security or cloud fallback alert message")
    task_id: Optional[str] = Field(None, description="Dispatched task identifier")


class SanitizedPayload(BaseModel):
    """Immutable DTO holding sanitized prompt payload with synthetic token mappings."""
    model_config = ConfigDict(frozen=True)

    original_text: str = Field(..., description="Original unscrubbed prompt text")
    sanitized_text: str = Field(..., description="Anonymized text containing synthetic tokens")
    replacements_count: int = Field(0, description="Total replacements performed")
    vault_token_map: Dict[str, str] = Field(
        default_factory=dict,
        description="Lookup mapping of {token_tag: original_sensitive_entity}",
    )
    contains_protected_ip: bool = Field(False, description="True if proprietary IP assets were detected")
    is_scrubbed: bool = Field(False, description="True if any sensitive entity was scrubbed")

    @property
    def scrubbed_text(self) -> str:
        """Compatibility property matching ScrubbedPayload."""
        return self.sanitized_text


class EnclaveToken(BaseModel):
    """Immutable synthetic token record managed by the RehydrationVault."""
    model_config = ConfigDict(frozen=True)

    token_tag: str = Field(..., description="Synthetic token identifier e.g. <<ENCLAVE_VAR_1>>")
    original_value: str = Field(..., description="Original sensitive IP or PII entity")
    category: str = Field("IP", description="Classification e.g. 'IP', 'PII', 'KEY'")
    created_at: float = Field(default=0.0, description="Timestamp token was registered")


class ScrubbedPayload(BaseModel):
    """Result of Torque zero-trust anonymization."""
    model_config = ConfigDict(frozen=True)

    original_text: str = Field(..., description="Original unscrubbed prompt text")
    scrubbed_text: str = Field(..., description="Anonymized text with synthetic vault tokens")
    replacements_count: int = Field(..., description="Number of sensitive entities replaced")
    vault_token_map: Dict[str, str] = Field(
        default_factory=dict,
        description="Lookup mapping of {token_tag: original_sensitive_entity}",
    )
    contains_protected_ip: bool = Field(False, description="True if proprietary IP assets were detected")


class GPUSpec(BaseModel):
    """Hardware descriptor for physical accelerator."""
    model_config = ConfigDict(frozen=True)

    index: int
    name: str
    vendor: AcceleratorVendor
    backend: ComputeBackend
    total_vram_mb: float
    free_vram_mb: float
    driver_version: Optional[str] = None
    compute_capability: Optional[str] = None
    is_primary_display: bool = False


class HardwareProfile(BaseModel):
    """Probed physical hardware snapshot across node."""
    model_config = ConfigDict(frozen=True)

    node_name: str
    cpu_cores_logical: int
    total_ram_mb: float
    available_ram_mb: float
    gpus: List[GPUSpec] = Field(default_factory=list)


class ModelArchitectureProfile(BaseModel):
    """Mathematical parameter layout of an LLM."""
    model_config = ConfigDict(frozen=True)

    name: str
    total_layers: int
    hidden_dim: int
    num_heads: int
    num_heads_kv: int
    head_dim: int
    model_size_mb: float
    quant_type: str = "Q4_K_M"
    context_length: int = 8192
    bytes_per_kv_element: float = 2.0


class DeviceAllocation(BaseModel):
    """Layer sharding boundary assigned to a single physical device."""
    model_config = ConfigDict(frozen=True)

    device_id: str
    device_name: str
    device_backend: str
    layer_start_idx: int
    layer_end_idx: int
    layer_count: int
    weights_memory_mb: float
    kv_memory_mb: float
    total_memory_mb: float
    memory_headroom_mb: float


class ShardingPlan(BaseModel):
    """Zero-OOM mathematical placement plan."""
    model_config = ConfigDict(frozen=True)

    model_name: str
    total_layers: int
    context_length: int
    allocations: List[DeviceAllocation] = Field(default_factory=list)
    spilled_to_cpu: bool = False
    spilled_layer_count: int = 0
    calculated_at: float = 0.0

    def render_cli_argument_string(self) -> str:
        """Renders llama-server --tensor-split argument string."""
        gpu_allocs = [a for a in self.allocations if a.device_backend != "CPU"]
        if not gpu_allocs:
            return "-ngl 0"
        total_gpu_layers = sum(a.layer_count for a in gpu_allocs)
        total_mem = sum(a.total_memory_mb for a in gpu_allocs)
        if total_mem <= 0:
            return f"-ngl {total_gpu_layers}"
        fractions = [f"{a.total_memory_mb / total_mem:.3f}" for a in gpu_allocs]
        split_arg = ",".join(fractions)
        return f"-ngl {total_gpu_layers} --tensor-split {split_arg}"


# ============================================================================
# PROTOCOL INTERFACES (Rust: pub trait)
# ============================================================================

@runtime_checkable
class VaultProtocol(Protocol):
    """Rust Trait equivalent: `pub trait RehydrationVault`"""

    def get_or_create_token(self, original_value: str) -> str:
        """Returns existing synthetic tag for original_value or registers a new one."""
        ...

    def resolve(self, token: str) -> Optional[str]:
        """Resolves synthetic token back to original sovereign entity."""
        ...

    def snapshot(self) -> Dict[str, str]:
        """Returns an immutable copy of the active token map."""
        ...

    def clear(self) -> None:
        """Flushes the active vault."""
        ...


@runtime_checkable
class ScrubberProtocol(Protocol):
    """Rust Trait equivalent: `pub trait Scrubber`"""

    def tokenize_and_store(self, text: str) -> ScrubbedPayload:
        """Strips proprietary IP and PII, replacing them with synthetic tags stored in Vault."""
        ...

    def rehydrate(self, scrubbed_text: str, vault_map: Optional[Mapping[str, str]] = None) -> str:
        """Restores synthetic tags with original proprietary terms."""
        ...


@runtime_checkable
class EgressFirewallProtocol(Protocol):
    """Rust Trait equivalent: `pub trait EgressFirewall`"""

    def inspect_outbound_payload(self, destination_url: str, payload_text: str) -> bool:
        """Returns True if egress is permitted, or False if outbound transmission must be dropped."""
        ...


@runtime_checkable
class RouterProtocol(Protocol):
    """Rust Trait equivalent: `pub trait ComplexityRouter`"""

    def route(self, payload: PromptPayload) -> RoutingDecision:
        """Determines the optimal execution tier (Tier 1/2/3) based on heuristics and tags."""
        ...


@runtime_checkable
class AllocatorProtocol(Protocol):
    """Rust Trait equivalent: `pub trait LayerAllocator`"""

    def calculate_plan(
        self,
        profile: ModelArchitectureProfile,
        allow_cpu_spill: bool = True,
    ) -> ShardingPlan:
        """Calculates zero-OOM layer splits across available accelerators."""
        ...


@runtime_checkable
class SupervisorProtocol(Protocol):
    """Rust Trait equivalent: `pub trait ProcessSupervisor`"""

    def spawn(self, command: List[str]) -> bool:
        """Spawns sandboxed child process with kernel-level job object cleanup."""
        ...

    def terminate(self) -> None:
        """Immediately destroys the managed child process and all descendants."""
        ...

    def is_healthy(self) -> bool:
        """Returns True if the backend is actively responsive."""
        ...
