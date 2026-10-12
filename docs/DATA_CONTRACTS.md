# Loom Fabric: Data Contracts & Type Specifications

This document defines the formal data schemas and trait protocols governing Loom Fabric.
Every data structure is defined as a frozen, immutable model with full type annotations.

---

## 1. Rust-Python Type Mapping Matrix

| Python (Loom Fabric) | Rust (`loom-core` / ClothOS) | Invariant |
| :--- | :--- | :--- |
| `typing.Protocol` | `pub trait TraitName` | Pure interface abstraction |
| `pydantic.BaseModel(frozen=True)` | `#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)] pub struct` | Immutable data transfer object |
| `enum.Enum` | `#[derive(Debug, Clone, Copy, PartialEq, Eq)] pub enum` | Strongly-typed enumeration |
| `Result[T, E]` | `std::result::Result<T, E>` | Explicit, deterministic error handling |

---

## 2. Core Protocol Traits

### `ScrubberProtocol`
```python
class ScrubberProtocol(Protocol):
    def scrub(self, text: str) -> ScrubbedPayload:
        """Sanitizes text by masking PII, secrets, and protected IP assets."""
        ...

    def rehydrate(self, text: str, token_map: Dict[str, str]) -> str:
        """Restores original sensitive entities from synthetic vault tokens."""
        ...
```

### `RouterProtocol`
```python
class RouterProtocol(Protocol):
    def route(self, payload: PromptPayload) -> RoutingDecision:
        """Determines execution tier, estimated latency, and target backend."""
        ...
```

### `MMUAllocatorProtocol`
```python
class MMUAllocatorProtocol(Protocol):
    def calculate_layer_split(self, profile: ModelArchitectureProfile) -> ShardingPlan:
        """Calculates zero-OOM layer splits across available VRAM and host RAM."""
        ...
```

---

## 3. Core Immutable DTO Schemas

### `ChatMessageDTO`
- `role: Literal["system", "user", "assistant", "tool"]`
- `content: str` (Guaranteed normalized flat string)
- `name: Optional[str]`
- `tool_call_id: Optional[str]`

### `PromptPayload`
- `model: str`
- `messages: Tuple[ChatMessageDTO, ...]`
- `temperature: float = 0.7`
- `top_p: float = 0.95`
- `max_tokens: int = 4096`
- `stream: bool = False`
- `force_local: bool = False`
- `airgap: bool = False`

### `RoutingDecision`
- `tier: ExecutionTier` (`TIER_1_LOCAL_RAPID`, `TIER_2_DISTRIBUTED_DAG`, `TIER_3_SOVEREIGN_CLOUD`)
- `model_name: str`
- `target_endpoint: str`
- `estimated_duration_seconds: float`
- `is_scrubbed: bool`
- `requires_manual_approval: bool`
- `reasoning: str`

### `ScrubbedPayload`
- `original_text: str`
- `scrubbed_text: str`
- `replacements_count: int`
- `vault_token_map: Mapping[str, str]`
- `contains_protected_ip: bool`

### `ShardingPlan`
- `model_name: str`
- `total_layers: int`
- `layers_on_gpu: int`
- `layers_on_cpu: int`
- `gpu_allocations: Tuple[DeviceAllocation, ...]`
- `vram_headroom_mb: float`
- `cli_args: Tuple[str, ...]`
