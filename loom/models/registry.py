"""
Model Registry & Preset Definitions for Loom Fabric.

Provides validated architecture metadata (layer counts, KV head dimensions,
parameter sizes, GGUF quantization weights) for leading local open-weights LLMs:
- Qwen-2.5-32B-Instruct
- DeepSeek-R1-Distill-Qwen-14B
- Qwen-2.5-7B-Instruct
- Llama-3.3-70B-Instruct

Rust Migration Blueprint:
    In the native `loom-core` Rust crate, this maps directly to:
    ```rust
    #[derive(Debug, Clone, Serialize, Deserialize)]
    pub struct ModelArchitecturePreset {
        pub id: String,
        pub display_name: String,
        pub total_layers: u32,
        pub context_length_default: u32,
        pub n_heads_kv: u32,
        pub d_head: u32,
        pub base_gguf_size_mb: f64,
        pub recommended_quant: String,
        pub ollama_tag: Option<String>,
        pub hf_repo: Option<String>,
    }
    ```
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ModelPreset(BaseModel):
    """Architectural profile and quantization metrics for a supported model."""
    id: str = Field(..., description="Unique slug or identifier, e.g. 'qwen-2.5-32b'")
    display_name: str = Field(..., description="Human-readable title")
    total_layers: int = Field(..., description="Total transformer decoder blocks/layers (N_total)")
    default_context_length: int = Field(8192, description="Target default KV context length (C)")
    n_heads_kv: int = Field(..., description="Number of Key/Value attention heads")
    d_head: int = Field(..., description="Head dimension (hidden_size / n_heads)")
    base_gguf_size_mb: float = Field(..., description="Approximate disk/VRAM size of quantized weights in MB")
    quant_label: str = Field("Q4_K_M", description="Recommended quantization format")
    ollama_tag: Optional[str] = Field(None, description="Matching local Ollama model tag if available")
    hf_repo: Optional[str] = Field(None, description="Hugging Face repo or GGUF URL")
    is_speculative_draft_candidate: bool = Field(False, description="Whether suitable as draft model")

    def to_architecture_profile(self, context_length: Optional[int] = None) -> "ModelArchitectureProfile":
        """Converts preset into full structural ModelArchitectureProfile for allocator."""
        from loom.stitch.allocator import ModelArchitectureProfile
        ctx = context_length or self.default_context_length
        # Approximate hidden_dim as n_heads_kv * 4 * d_head or standard 4096-8192
        hidden_dim = self.n_heads_kv * 8 * self.d_head if self.n_heads_kv <= 4 else self.n_heads_kv * 4 * self.d_head
        num_heads = hidden_dim // self.d_head
        return ModelArchitectureProfile(
            name=self.display_name,
            total_layers=self.total_layers,
            hidden_dim=hidden_dim,
            num_heads=num_heads,
            num_heads_kv=self.n_heads_kv,
            head_dim=self.d_head,
            model_size_mb=self.base_gguf_size_mb,
            quant_type=self.quant_label,
            context_length=ctx,
        )


BUILTIN_PRESETS: Dict[str, ModelPreset] = {
    "loom-sovereign:latest": ModelPreset(
        id="loom-sovereign:latest",
        display_name="ClothOS Loom Sovereign (32B Epistemic & Fiduciary)",
        total_layers=64,
        default_context_length=32768,
        n_heads_kv=8,
        d_head=128,
        base_gguf_size_mb=19800.0,
        quant_label="Q4_K_M",
        ollama_tag="loom-sovereign:latest",
        hf_repo="Qwen/Qwen2.5-32B-Instruct-GGUF",
        is_speculative_draft_candidate=False,
    ),
    "loom-sovereign-fast:latest": ModelPreset(
        id="loom-sovereign-fast:latest",
        display_name="ClothOS Loom Sovereign Fast (7B Epistemic)",
        total_layers=28,
        default_context_length=16384,
        n_heads_kv=4,
        d_head=128,
        base_gguf_size_mb=4700.0,
        quant_label="Q4_K_M",
        ollama_tag="loom-sovereign-fast:latest",
        hf_repo="Qwen/Qwen2.5-7B-Instruct-GGUF",
        is_speculative_draft_candidate=True,
    ),
    "loom-sovereign-70b:latest": ModelPreset(
        id="loom-sovereign-70b:latest",
        display_name="ClothOS Loom Sovereign 70B (Apex Epistemic & Sovereign Reasoning)",
        total_layers=80,
        default_context_length=32768,
        n_heads_kv=8,
        d_head=128,
        base_gguf_size_mb=42500.0,
        quant_label="Q4_K_M",
        ollama_tag="loom-sovereign-70b:latest",
        hf_repo="meta-llama/Llama-3.3-70B-Instruct-GGUF",
        is_speculative_draft_candidate=False,
    ),
    "loom-70b:latest": ModelPreset(
        id="loom-70b:latest",
        display_name="ClothOS Loom 70B Frontier",
        total_layers=80,
        default_context_length=32768,
        n_heads_kv=8,
        d_head=128,
        base_gguf_size_mb=42500.0,
        quant_label="Q4_K_M",
        ollama_tag="loom-70b:latest",
        hf_repo="meta-llama/Llama-3.3-70B-Instruct-GGUF",
        is_speculative_draft_candidate=False,
    ),
    "qwen2.5-coder:7b": ModelPreset(
        id="qwen2.5-coder:7b",
        display_name="Qwen 2.5 Coder 7B Instruct",
        total_layers=28,
        default_context_length=32768,
        n_heads_kv=4,
        d_head=128,
        base_gguf_size_mb=4700.0,
        quant_label="Q4_K_M",
        ollama_tag="qwen2.5-coder:7b",
        hf_repo="Qwen/Qwen2.5-Coder-7B-Instruct-GGUF",
        is_speculative_draft_candidate=True,
    ),
    "qwen2.5:32b": ModelPreset(
        id="qwen2.5:32b",
        display_name="Qwen 2.5 32B Instruct (Q4_K_M)",
        total_layers=64,
        default_context_length=8192,
        n_heads_kv=8,
        d_head=128,
        base_gguf_size_mb=19800.0,
        quant_label="Q4_K_M",
        ollama_tag="qwen2.5:32b",
        hf_repo="Qwen/Qwen2.5-32B-Instruct-GGUF",
        is_speculative_draft_candidate=False,
    ),
    "deepseek-r1:14b": ModelPreset(
        id="deepseek-r1:14b",
        display_name="DeepSeek R1 Distill Qwen 14B (Q4_K_M)",
        total_layers=48,
        default_context_length=8192,
        n_heads_kv=8,
        d_head=128,
        base_gguf_size_mb=9000.0,
        quant_label="Q4_K_M",
        ollama_tag="deepseek-r1:14b",
        hf_repo="deepseek-ai/DeepSeek-R1-Distill-Qwen-14B-GGUF",
        is_speculative_draft_candidate=False,
    ),
    "qwen2.5:7b": ModelPreset(
        id="qwen2.5:7b",
        display_name="Qwen 2.5 7B Instruct (Q4_K_M)",
        total_layers=28,
        default_context_length=8192,
        n_heads_kv=4,
        d_head=128,
        base_gguf_size_mb=4700.0,
        quant_label="Q4_K_M",
        ollama_tag="qwen2.5:7b",
        hf_repo="Qwen/Qwen2.5-7B-Instruct-GGUF",
        is_speculative_draft_candidate=True,
    ),
    "qwen2.5:3b": ModelPreset(
        id="qwen2.5:3b",
        display_name="Qwen 2.5 3B Instruct (Q4_K_M)",
        total_layers=36,
        default_context_length=8192,
        n_heads_kv=2,
        d_head=128,
        base_gguf_size_mb=1900.0,
        quant_label="Q4_K_M",
        ollama_tag="qwen2.5:3b",
        hf_repo="Qwen/Qwen2.5-3B-Instruct-GGUF",
        is_speculative_draft_candidate=True,
    ),
    "llama3.3:70b": ModelPreset(
        id="llama3.3:70b",
        display_name="Llama 3.3 70B Instruct (Q4_K_M)",
        total_layers=80,
        default_context_length=8192,
        n_heads_kv=8,
        d_head=128,
        base_gguf_size_mb=43000.0,
        quant_label="Q4_K_M",
        ollama_tag="llama3.3:70b",
        hf_repo="meta-llama/Llama-3.3-70B-Instruct-GGUF",
        is_speculative_draft_candidate=False,
    ),
    "auto": ModelPreset(
        id="auto",
        display_name="Loom Dynamic Compute Triage (Auto-Select)",
        total_layers=64,
        default_context_length=131072,
        n_heads_kv=8,
        d_head=128,
        base_gguf_size_mb=19800.0,
        quant_label="Adaptive",
        ollama_tag="auto",
        hf_repo=None,
        is_speculative_draft_candidate=True,
    ),
}


class ModelRegistry:
    """Manages available model architecture profiles and runtime resolutions."""

    @classmethod
    def list_models(cls) -> List[ModelPreset]:
        """Return all registered model presets."""
        return list(BUILTIN_PRESETS.values())

    @classmethod
    def get_model(cls, model_id_or_tag: str) -> Optional[ModelPreset]:
        """Find a model preset by ID or alias tag, ignoring any provider prefix."""
        normalized = model_id_or_tag.strip().lower()
        if "/" in normalized:
            normalized = normalized.split("/", 1)[1]
        if normalized in BUILTIN_PRESETS:
            return BUILTIN_PRESETS[normalized]
        for preset in BUILTIN_PRESETS.values():
            if preset.ollama_tag and preset.ollama_tag.lower() == normalized:
                return preset
            if preset.id.lower() == normalized:
                return preset
        return None

    @classmethod
    def register_custom(cls, preset: ModelPreset) -> None:
        """Register or override a custom model preset."""
        BUILTIN_PRESETS[preset.id.lower()] = preset
