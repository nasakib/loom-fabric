"""
Multi-Agent Deliberation & Group Chat Engine (`loom/clothos/group_chat.py`).

Adapted from Qwen-Agent's GroupChat & GroupChatAutoRouter architectures:
- Facilitates structured multi-perspective deliberation between specialized agent personas.
- Personas: Architect, Software Engineer, Security SRE, and Critic/Verifier.
- Synthesizes complex architectural decisions, edge cases, and verification before code deployment.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("loom.clothos.group_chat")


class AgentPersona:
    def __init__(self, name: str, role: str, system_prompt: str):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt

    def to_dict(self) -> Dict[str, str]:
        return {"name": self.name, "role": self.role, "system_prompt": self.system_prompt}


DEFAULT_PERSONAS = [
    AgentPersona(
        name="Architect",
        role="System Architecture & High-Level Invariants",
        system_prompt=(
            "You are the Principal Systems Architect. Focus on modularity, scalability, "
            "cluster resource allocation, and maintaining system invariants without overcomplicating."
        ),
    ),
    AgentPersona(
        name="Lead_Engineer",
        role="Implementation, API Design & Tool Use",
        system_prompt=(
            "You are the Lead Software Engineer. Focus on concrete implementation, clean Python/Rust APIs, "
            "correct parameters, performance, and pragmatic execution."
        ),
    ),
    AgentPersona(
        name="Security_SRE",
        role="Air-Gapped Security, Reliability & Failure Modes",
        system_prompt=(
            "You are the Security SRE. Focus on air-gapped data integrity, zero cloud leakage, "
            "handling edge cases, preventing OOM crashes, and input sanitization."
        ),
    ),
    AgentPersona(
        name="Verifier_Critic",
        role="Independent Verification & Rigorous Review",
        system_prompt=(
            "You are the Independent Code & Logic Verifier. Scrutinize assumptions, identify hidden bugs, "
            "and suggest verification tests to ensure 100% correctness."
        ),
    ),
]


class GroupChatSession:
    """Manages multi-persona deliberation for complex coding, architectural, and operational tasks."""

    def __init__(
        self,
        personas: Optional[List[AgentPersona]] = None,
        query_llm_fn: Optional[Callable[[str, str], str]] = None,
    ):
        self.personas = personas or DEFAULT_PERSONAS
        self.query_llm_fn = query_llm_fn or self._default_llm_query
        self.conversation: List[Dict[str, str]] = []

    def _default_llm_query(self, prompt: str, system_prompt: str) -> str:
        """Invokes the active Clothos LLM gateway or ModelRouter."""
        try:
            from loom.clothos.agent_cli import ModelRouter
            # Combine system prompt + user prompt
            full_prompt = f"SYSTEM INSTRUCTION:\n{system_prompt}\n\nUSER QUERY:\n{prompt}"
            res = ModelRouter.dispatch_query(full_prompt)
            return res.get("text", "").strip()
        except Exception as e:
            return f"[Deliberation response generated locally: {e}]"

    def deliberate(self, task_description: str, max_rounds: int = 2) -> Dict[str, Any]:
        """Runs a multi-round deliberation between all personas on a given problem."""
        t0 = time.time()
        self.conversation = []

        context_history = f"TASK GOAL:\n{task_description}\n\n"

        for round_num in range(1, max_rounds + 1):
            for persona in self.personas:
                turn_prompt = (
                    f"{context_history}\n"
                    f"It is now your turn to speak as {persona.name} ({persona.role}).\n"
                    f"Review the conversation so far. Add your unique technical insights, critiques, "
                    f"or concrete recommendations. Keep your answer concise (2-4 paragraphs) and focused."
                )
                response = self.query_llm_fn(turn_prompt, persona.system_prompt)
                
                entry = {
                    "round": round_num,
                    "speaker": persona.name,
                    "role": persona.role,
                    "content": response,
                }
                self.conversation.append(entry)
                context_history += f"[{persona.name} - {persona.role}]:\n{response}\n\n"

        # Final Synthesis
        synth_prompt = (
            f"Here is the deliberation transcript between specialists:\n\n{context_history}\n"
            f"As the Lead Synthesizer, distill this deliberation into a single, cohesive, finalized action plan:\n"
            f"1. Executive Decision / Final Consensus\n"
            f"2. Core Architecture & Requirements\n"
            f"3. Concrete Implementation Steps\n"
            f"4. Testing & Verification Checklist\n"
        )
        final_verdict = self.query_llm_fn(synth_prompt, "You are the Lead Technical Synthesizer.")

        elapsed = round(time.time() - t0, 2)
        return {
            "success": True,
            "task": task_description,
            "rounds_run": max_rounds,
            "total_turns": len(self.conversation),
            "transcript": self.conversation,
            "final_consensus": final_verdict,
            "elapsed_seconds": elapsed,
        }
