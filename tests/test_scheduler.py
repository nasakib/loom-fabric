"""
Test Suite: Torque 3-Tier Cascade Scheduler & 300s Arbitrage Governor.
"""

from loom.torque.scheduler import TorqueCascadeScheduler
from loom.types import ChatMessageDTO, ExecutionTier, PromptPayload


def test_scheduler_compaction_turn_triage():
    """Verify compaction prompts route to Tier 1 Qwen 2.5 7B for instant zero-timeout completion."""
    scheduler = TorqueCascadeScheduler()
    payload = PromptPayload(
        model="auto",
        messages=[
            ChatMessageDTO(role="user", content="Summarize the conversation and cut-point historical context turns.")
        ],
        max_tokens=4096,
    )

    decision = scheduler.route(payload)
    assert decision.tier == ExecutionTier.TIER_1_LOCAL_RAPID
    assert decision.model_name == "qwen2.5:7b"
    assert decision.is_scrubbed is False
    assert decision.circuit_breaker_triggered is False


def test_scheduler_formal_reasoning_triage():
    """Verify mathematical proof prompts route to DeepSeek R1 14B."""
    scheduler = TorqueCascadeScheduler()
    payload = PromptPayload(
        model="auto",
        messages=[
            ChatMessageDTO(role="user", content="Prove the Fourier transform convergence theorem using formal SMT constraints.")
        ],
        max_tokens=4096,
    )

    decision = scheduler.route(payload)
    assert decision.tier == ExecutionTier.TIER_1_LOCAL_RAPID
    assert decision.model_name == "deepseek-r1:14b"
    assert decision.is_scrubbed is False


def test_scheduler_heavy_code_distributed_dag_triage():
    """Verify large code synthesis prompts route to Tier 2 Ray Distributed DAG with Qwen 2.5 32B."""
    scheduler = TorqueCascadeScheduler()
    code_prompt = (
        "Please refactor the distributed Ray actor supervisor across the cluster. "
        "Here is the specification:\n```python\nclass Supervisor:\n    def manage(self):\n        pass\n```\n"
        "Ensure full zero-OOM memory sharding and Win32 Job Object isolation."
    )
    payload = PromptPayload(
        model="auto",
        messages=[ChatMessageDTO(role="user", content=code_prompt)],
        max_tokens=4096,
    )

    decision = scheduler.route(payload)
    assert decision.tier == ExecutionTier.TIER_2_DISTRIBUTED_DAG
    assert decision.model_name == "qwen2.5:32b"
    assert decision.is_scrubbed is False


def test_scheduler_circuit_breaker_tripped_on_extreme_load():
    """Verify that workloads exceeding 300s trip the Tier 3 Circuit-Breaker for manual confirmation."""
    scheduler = TorqueCascadeScheduler()
    # Construct a massive prompt exceeding 300s compute
    massive_words = "analyze and benchmark every component in depth " * 2500
    payload = PromptPayload(
        model="auto",
        messages=[ChatMessageDTO(role="user", content=massive_words)],
        max_tokens=8192,
    )

    decision = scheduler.route(payload)
    assert decision.tier == ExecutionTier.TIER_3_SOVEREIGN_CLOUD
    assert decision.circuit_breaker_triggered is True
    assert decision.requires_manual_approval is True
    assert decision.is_scrubbed is True


def test_scheduler_airgap_and_local_suppression_of_tier3():
    """Verify that [AIRGAP] or [LOCAL] permanently suppresses Tier 3 cloud fallback."""
    scheduler = TorqueCascadeScheduler()
    massive_words = "analyze and benchmark every component in depth " * 2500

    # Payload with airgap=True
    payload_airgap = PromptPayload(
        model="auto",
        messages=[ChatMessageDTO(role="user", content=massive_words)],
        max_tokens=8192,
        airgap=True,
    )
    decision_airgap = scheduler.route(payload_airgap)
    # Must NOT route to cloud
    assert decision_airgap.tier != ExecutionTier.TIER_3_SOVEREIGN_CLOUD
    assert decision_airgap.tier == ExecutionTier.TIER_2_DISTRIBUTED_DAG
    assert decision_airgap.circuit_breaker_triggered is False

    # Payload with [AIRGAP] tag in text
    payload_tagged = PromptPayload(
        model="auto",
        messages=[ChatMessageDTO(role="user", content=f"[AIRGAP] {massive_words}")],
        max_tokens=8192,
    )
    decision_tagged = scheduler.route(payload_tagged)
    assert decision_tagged.tier == ExecutionTier.TIER_2_DISTRIBUTED_DAG
