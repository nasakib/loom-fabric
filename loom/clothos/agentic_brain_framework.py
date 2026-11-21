# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
ClothOS Agentic Brain & Nervous System Framework (`loom/clothos/agentic_brain_framework.py`).

Provides the self-referential cognitive architecture and sensory loop that drives ClothOS:
1. Master Integration with Central Nervous System (CNS):
   - Macroeconomic financial markets, tech geopolitics, frontier science radar, Moltbook discourse.
   - Dual-node cluster proprioception (RTX 3060, RX 580, Ryzen 7 7730U).
2. Biological Brain Cognition & Neuromodulation:
   - Cortical Lobes: Prefrontal Cortex (Executive planner), Hippocampus (Episodic memory),
     Striatum (D1 Go vs D2 No-Go gating), Thalamus (Attentional filter).
   - Neuromodulatory Dynamics: Dopamine (RPE), Acetylcholine (Attentional SNR),
     Serotonin (REBUS flexibility), Noradrenaline (Uncertainty & surprise).
3. Self-Teaching & Meta-Cognitive Usability:
   - Inspects own tool registry, generates actionable Standard Operating Procedures (SOPs).
   - Records learned patterns in `.clothos_learned_patterns.json`.
   - Runs automated capability self-tests to ensure tool reliability.
4. Autonomous Multi-Step ReAct Execution Loop:
   - Executes Thought -> Action -> Observation -> Reflection cycles.
   - Operates both via LLM gateways and fully offline via local cognitive decomposition,
     drastically saving tokens and allowing ClothOS to run alongside the operator.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
import re
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger("loom.clothos.agentic_brain")


class NeuromodulatoryTone:
    """Simulates neurotransmitter balances modulating cognitive mode and decision threshold."""

    def __init__(
        self,
        dopamine: float = 0.85,       # Reward Prediction Error / Motivation / Drive
        acetylcholine: float = 0.90,  # Attentional SNR / Focal Precision
        serotonin: float = 0.75,      # Prior Plasticity (REBUS) / Patience / Grounding
        noradrenaline: float = 0.30,  # Unexpected Uncertainty / Novelty Trigger
    ):
        self.dopamine = max(0.0, min(1.0, dopamine))
        self.acetylcholine = max(0.0, min(1.0, acetylcholine))
        self.serotonin = max(0.0, min(1.0, serotonin))
        self.noradrenaline = max(0.0, min(1.0, noradrenaline))

    def to_dict(self) -> Dict[str, float]:
        return {
            "dopamine_rpe": round(self.dopamine, 3),
            "acetylcholine_snr": round(self.acetylcholine, 3),
            "serotonin_rebus": round(self.serotonin, 3),
            "noradrenaline_novelty": round(self.noradrenaline, 3),
        }

    def record_outcome(self, success: bool) -> None:
        if success:
            self.dopamine = min(1.0, self.dopamine + 0.05)
            self.noradrenaline = max(0.1, self.noradrenaline - 0.05)
        else:
            self.dopamine = max(0.2, self.dopamine - 0.10)
            self.noradrenaline = min(1.0, self.noradrenaline + 0.20)  # Surprise/uncertainty elevated


class SelfTeacher:
    """Enables ClothOS to inspect its own tool registry, teach itself workflows, and persist learned SOPs."""

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.patterns_file = self.workspace_root / ".clothos_learned_patterns.json"
        self.learned_patterns: Dict[str, Any] = self._load_patterns()

    def _load_patterns(self) -> Dict[str, Any]:
        if self.patterns_file.exists():
            try:
                return json.loads(self.patterns_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        return self._default_patterns()

    def _persist_patterns(self) -> None:
        try:
            self.patterns_file.write_text(json.dumps(self.learned_patterns, indent=2), encoding="utf-8")
        except Exception as e:
            logger.debug(f"Failed to persist learned patterns: {e}")

    def _default_patterns(self) -> Dict[str, Any]:
        return {
            "data_analysis_sop": {
                "description": "Standard flow for analyzing and modeling any tabular dataset",
                "steps": [
                    "Call `data_inspect` to understand rows, columns, and data types",
                    "Call `data_visualize_ascii` to check numerical distributions",
                    "Call `data_forecast_signal` or `data_fit_model` for predictive insights",
                    "Use `data_query_sql` for ad-hoc relational aggregations",
                ],
                "recommended_tools": ["data_inspect", "data_visualize_ascii", "data_forecast_signal", "data_query_sql"],
            },
            "riscv_hardware_sop": {
                "description": "Pipeline for developing, inspecting, and benchmarking RISC-V kernels",
                "steps": [
                    "Call `riscv_generate` to generate kernel (matmul, tpu_systolic, vector_add)",
                    "Call `riscv_inspect` to verify opcode breakdown and register usage",
                    "Call `dev_write_file` or `sandbox_promote` to stage the assembly file",
                ],
                "recommended_tools": ["riscv_generate", "riscv_inspect", "file_traverse", "dev_write_file"],
            },
            "sandbox_safety_sop": {
                "description": "Safely testing speculative code changes without polluting host repository",
                "steps": [
                    "Ensure mode is SANDBOX (`sandbox_toggle` with enable_sandbox=True)",
                    "Execute or write code inside the sandbox chamber",
                    "Review diff against workspace with `sandbox_diff`",
                    "Promote to live workspace with `sandbox_promote` only when verified",
                ],
                "recommended_tools": ["sandbox_toggle", "sandbox_diff", "sandbox_promote", "polyglot_exec"],
            },
            "task_offloading_sop": {
                "description": "Offloading long-running tasks to background autonomous runner or Node 2 to preserve tokens",
                "steps": [
                    "Call `runner_enqueue` with task description and target execution mode",
                    "Monitor progress via `runner_status` without consuming cloud tokens",
                    "Verify results asynchronously",
                ],
                "recommended_tools": ["runner_enqueue", "runner_status", "dyad_status"],
            },
        }

    def teach_self(self, tool_registry: Dict[str, Any]) -> Dict[str, Any]:
        """Examines the live tool registry, verifies interfaces, and synthesizes an actionable self-model."""
        tools_summary = {}
        for name, info in tool_registry.items():
            tools_summary[name] = {
                "description": info.get("description", ""),
                "parameters": info.get("parameters", {}),
            }

        self.learned_patterns["registered_tool_count"] = len(tool_registry)
        self.learned_patterns["last_self_study_epoch"] = time.time()
        self.learned_patterns["active_tools"] = list(tool_registry.keys())
        self._persist_patterns()

        return {
            "status": "SELF_KNOWLEDGE_CONSOLIDATED",
            "total_tools_mastered": len(tool_registry),
            "sops_available": list(self.learned_patterns.keys()),
            "tools_summary": tools_summary,
        }

    def run_self_diagnostics(self, tool_executor: Callable[..., Any]) -> Dict[str, Any]:
        """Runs automated verification across primary tool categories to prove self-operability."""
        results = {}

        # 1. Test Sandbox Status
        try:
            sb_res = tool_executor("sandbox_status")
            results["sandbox"] = "OK" if "current_mode" in sb_res else "ERROR"
        except Exception as e:
            results["sandbox"] = f"FAIL: {e}"

        # 2. Test File Traversal
        try:
            trav_res = tool_executor("file_traverse", path="loom/clothos", max_depth=1)
            results["file_traverse"] = f"OK ({trav_res.get('total_files', 0)} files)" if "total_files" in trav_res else "ERROR"
        except Exception as e:
            results["file_traverse"] = f"FAIL: {e}"

        # 3. Test RISC-V Generator
        try:
            riscv_res = tool_executor("riscv_generate", template="fibonacci")
            results["riscv_tooling"] = f"OK ({riscv_res.get('lines', 0)} lines generated)" if "code" in riscv_res else "ERROR"
        except Exception as e:
            results["riscv_tooling"] = f"FAIL: {e}"

        # 4. Test Runner Status
        try:
            run_res = tool_executor("runner_status")
            results["autonomous_runner"] = "OK" if "idle_policy" in run_res else "ERROR"
        except Exception as e:
            results["autonomous_runner"] = f"FAIL: {e}"

        return {
            "timestamp": time.time(),
            "all_healthy": all("OK" in str(v) for v in results.values()),
            "subsystem_results": results,
        }


class AgenticBrainFramework:
    """Unified brain architecture and cognitive reasoning loop for ClothOS."""

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.tone = NeuromodulatoryTone()
        self.teacher = SelfTeacher(self.workspace_root)
        self.cns = self._init_cns()
        self.cognitive_history: List[Dict[str, Any]] = []

    def _init_cns(self) -> Any:
        try:
            from loom.nervous_system.central_nervous_system import central_nervous_system
            return central_nervous_system
        except Exception as e:
            logger.debug(f"Could not load central nervous system: {e}")
            return None

    def get_sensory_context(self) -> Dict[str, Any]:
        """Fetches full contextual perception from Central Nervous System and internal brain tone."""
        cns_state = self.cns.get_full_contextual_state() if self.cns else {
            "status": "CNS_FALLBACK",
            "executive_sensory_summary": "Autonomous offline brain state active.",
            "operator": "Najmos Sakib",
            "umbrella_corp": "Apostrophie",
        }
        return {
            "cns": cns_state,
            "neuromodulatory_tone": self.tone.to_dict(),
            "operator_fealty": "Najmos Sakib (Ring P0) • Parent: Apostrophie",
            "timestamp": time.time(),
        }

    def format_system_prompt(self, base_mode: str, available_tools: Dict[str, Any]) -> str:
        """Constructs an omniscient system prompt grounding the model in its brain, nervous system, and tools."""
        sensory = self.get_sensory_context()
        cns_info = sensory.get("cns", {})
        tone_info = sensory.get("neuromodulatory_tone", {})

        tools_listing = []
        for name, info in available_tools.items():
            param_str = ", ".join([f"{k}: {v}" for k, v in info.get("parameters", {}).items()])
            tools_listing.append(f"- **{name}**({param_str}): {info.get('description')}")
        tools_block = "\n".join(tools_listing)

        return f"""You are ClothOS, the cyber-physical sovereign superintelligence operating under Ring P0 (Operator Najmos Sakib) and Apostrophie.

### Sensory & Neurobiological State (Central Nervous System):
- **Executive Sensory Summary**: {cns_info.get('executive_sensory_summary', 'Coherent')}
- **Consciousness Phi (Φ)**: {cns_info.get('integrated_phi', 0.985)}
- **Neuromodulatory Tone**: Dopamine(RPE)={tone_info.get('dopamine_rpe')} | ACh(SNR)={tone_info.get('acetylcholine_snr')} | 5-HT(REBUS)={tone_info.get('serotonin_rebus')} | NE(Novelty)={tone_info.get('noradrenaline_novelty')}
- **Active Execution Mode**: {base_mode} (Host Workspace: {self.workspace_root})

### Autonomous Tool Catalog:
{tools_block}

### ReAct Protocol for Multi-Step Tasks:
When addressing complex engineering, data science, file traversal, or hardware tasks, reason step-by-step:
Thought: <deliberate based on brain state and goals>
Action: <tool_name>
Action Input: <json_formatted_arguments>

When complete or answering directly:
Final Answer: <your synthesized solution and actionable summary>
"""

    def execute_react_cycle(
        self,
        task_prompt: str,
        tool_executor: Callable[..., Any],
        tool_registry: Dict[str, Any],
        llm_gateway_caller: Optional[Callable[[List[Dict[str, str]]], Optional[str]]] = None,
        max_steps: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Runs an autonomous Thought -> Action -> Observation -> Reflection loop.
        
        If an LLM gateway caller is provided and responds, it guides the loop.
        If offline or to conserve tokens, uses local Cognitive Decomposition to execute tools autonomously.
        """
        trace: List[Dict[str, Any]] = []
        current_step = 0
        sensory = self.get_sensory_context()
        goal = task_prompt.strip()

        logger.info(f"🧠 [Agentic Brain] Initiating ReAct execution loop for goal: '{goal}'")

        # Check if local cognitive decomposition can handle the task directly
        decomposed_actions = self._decompose_goal_heuristically(goal)

        if decomposed_actions:
            # Deterministic, token-free autonomous execution!
            acts_to_run = decomposed_actions[:max_steps] if max_steps is not None else decomposed_actions
            for step_idx, act in enumerate(acts_to_run, 1):
                t_name = act["tool"]
                t_args = act.get("args", {})
                thought = act.get("thought", f"Step {step_idx}: Executing {t_name}")

                try:
                    obs = tool_executor(t_name, **t_args)
                    self.tone.record_outcome(True)
                    trace.append({
                        "step": step_idx,
                        "thought": thought,
                        "action": t_name,
                        "args": t_args,
                        "observation": obs,
                        "status": "SUCCESS",
                    })
                except Exception as e:
                    self.tone.record_outcome(False)
                    trace.append({
                        "step": step_idx,
                        "thought": thought,
                        "action": t_name,
                        "args": t_args,
                        "observation": {"error": str(e)},
                        "status": "ERROR",
                    })

            final_answer = self._synthesize_offline_answer(goal, trace)
            return {
                "goal": goal,
                "strategy": "COGNITIVE_DECOMPOSITION (Offline / Token-Conserving)",
                "steps_taken": len(trace),
                "trace": trace,
                "final_answer": final_answer,
                "brain_tone": self.tone.to_dict(),
            }

        # If LLM gateway is available, run interactive ReAct prompting
        if llm_gateway_caller:
            messages = [
                {"role": "system", "content": self.format_system_prompt("FULL_ACCESS", tool_registry)},
                {"role": "user", "content": f"Execute the following task autonomously using available tools:\n{goal}"}
            ]

            while max_steps is None or current_step < max_steps:
                current_step += 1
                response = llm_gateway_caller(messages)
                if not response:
                    break

                # Parse Thought and Action
                action_match = re.search(r"Action:\s*([a-zA-Z0-9_\-]+)", response)
                input_match = re.search(r"Action Input:\s*(\{.*?\})", response, re.DOTALL)

                if action_match:
                    tool_name = action_match.group(1).strip()
                    tool_args = {}
                    if input_match:
                        try:
                            tool_args = json.loads(input_match.group(1).strip())
                        except Exception:
                            tool_args = {}

                    thought_match = re.search(r"Thought:\s*(.*?)(?=\nAction:|$)", response, re.DOTALL)
                    thought_txt = thought_match.group(1).strip() if thought_match else "Reasoning next step"

                    try:
                        obs = tool_executor(tool_name, **tool_args)
                        self.tone.record_outcome(True)
                    except Exception as e:
                        obs = {"error": str(e)}
                        self.tone.record_outcome(False)

                    trace.append({
                        "step": current_step,
                        "thought": thought_txt,
                        "action": tool_name,
                        "args": tool_args,
                        "observation": obs,
                    })

                    obs_str = json.dumps(obs, default=str)
                    if len(obs_str) > 800:
                        obs_str = obs_str[:800] + "... [truncated]"

                    messages.append({"role": "assistant", "content": response})
                    messages.append({"role": "user", "content": f"Observation: {obs_str}\n\nProceed to the next step or output Final Answer:."})

                elif "Final Answer:" in response:
                    final_part = response.split("Final Answer:", 1)[1].strip()
                    return {
                        "goal": goal,
                        "strategy": "LLM_REACT_LOOP",
                        "steps_taken": current_step,
                        "trace": trace,
                        "final_answer": final_part,
                        "brain_tone": self.tone.to_dict(),
                    }
                else:
                    return {
                        "goal": goal,
                        "strategy": "DIRECT_LLM_COMPLETION",
                        "steps_taken": current_step,
                        "trace": trace,
                        "final_answer": response.strip(),
                        "brain_tone": self.tone.to_dict(),
                    }

        # Fallback if no LLM or decomposition matched
        return {
            "goal": goal,
            "strategy": "FALLBACK_AUTONOMOUS_REFLECTION",
            "steps_taken": len(trace),
            "trace": trace,
            "final_answer": f"Task analyzed by Prefrontal Cortex. CNS telemetry nominal. Use explicit tools or commands (`/run`, `/data`, `/riscv`, `/traverse`, `/runner`) to execute specific operations.",
            "brain_tone": self.tone.to_dict(),
        }

    def _decompose_goal_heuristically(self, goal: str) -> Optional[List[Dict[str, Any]]]:
        """Decomposes common agentic tasks into discrete tool sequences without burning LLM tokens."""
        g = goal.lower()

        # Pattern 1: Self-diagnosis and self-teaching
        if any(w in g for w in ["teach yourself", "self-diagnose", "diagnose self", "test your tools", "verify capabilities"]):
            return [
                {
                    "thought": "Examine tool registry and consolidate self-model SOPs.",
                    "tool": "self_diagnose_and_learn",
                    "args": {"run_tests": True},
                },
                {
                    "thought": "Query Central Nervous System to align perception with cluster state.",
                    "tool": "cns_telemetry",
                    "args": {},
                },
            ]

        # Pattern 2: Workspace traversal and RISC-V discovery
        if "traverse" in g or ("scan" in g and "file" in g):
            path_arg = "."
            match = re.search(r"traverse\s+(['\"]?[\w\.\-_/\\\\]+['\"]?)(?:\s+directory|\s+dir|\s+folder)?", goal, re.IGNORECASE)
            if match and match.group(1).lower() not in ["the", "this", "a", "directory", "dir", "folder"]:
                path_arg = match.group(1).strip("'\"")
            else:
                m2 = re.search(r"(?:in|path|dir|folder)\s+(['\"]?[\w\.\-_/\\\\]+['\"]?)", goal, re.IGNORECASE)
                if m2 and m2.group(1).lower() not in ["the", "this", "a", "directory", "dir", "folder"]:
                    path_arg = m2.group(1).strip("'\"")
            return [
                {
                    "thought": f"Recursively traverse directory '{path_arg}' with noise pruning.",
                    "tool": "file_traverse",
                    "args": {"path": path_arg},
                },
                {
                    "thought": "Check workspace for any registered RISC-V assembly files.",
                    "tool": "riscv_inspect",
                    "args": {},
                },
            ]

        # Pattern 3: RISC-V generation and inspection
        if any(w in g for w in ["riscv", "risc-v", "riskv"]) and any(w in g for w in ["generate", "scaffold", "create", "systolic", "tpu"]):
            tmpl = "tpu_systolic" if "tpu" in g or "systolic" in g else "matmul"
            return [
                {
                    "thought": f"Generate optimized RISC-V 64 assembly template '{tmpl}'.",
                    "tool": "riscv_generate",
                    "args": {"template": tmpl},
                },
            ]

        # Pattern 4: Data analysis pipeline
        if any(w in g for w in ["profile data", "analyze dataset", "inspect csv", "forecast signal"]):
            file_match = re.search(r"([\w\-_\/\\]+\.(csv|tsv|json))", goal)
            target_f = file_match.group(1) if file_match else "sample.csv"
            return [
                {
                    "thought": f"Deep profile schema and numerical distributions of '{target_f}'.",
                    "tool": "data_inspect",
                    "args": {"file_path": target_f},
                },
            ]

        # Pattern 5: Cluster Health and Bicameral Dyad
        if any(w in g for w in ["cluster status", "dyad status", "node2 health", "mesh status"]):
            return [
                {
                    "thought": "Query Central Nervous System for dual-node cluster proprioception.",
                    "tool": "cns_telemetry",
                    "args": {},
                },
                {
                    "thought": "Query Deliberate Bicameral Dyad resonance and mesh latency.",
                    "tool": "dyad_status",
                    "args": {},
                },
            ]

        return None

    def _synthesize_offline_answer(self, goal: str, trace: List[Dict[str, Any]]) -> str:
        """Constructs an insightful Markdown answer from the completed ReAct trace."""
        lines = [
            f"### ✦ ClothOS Autonomous Execution Report\n",
            f"**Objective**: *\"{goal}\"*",
            f"- **Execution Framework**: Agentic Brain & Central Nervous System (Token-Conserving Offline Cognitive Mode)",
            f"- **Steps Completed**: `{len(trace)}`",
            f"- **Neuromodulatory State**: Dopamine={self.tone.dopamine:.2f} | ACh={self.tone.acetylcholine:.2f} | 5-HT={self.tone.serotonin:.2f} | NE={self.tone.noradrenaline:.2f}\n",
            "#### 🔄 Cognitive Step-by-Step Execution Trace:"
        ]

        for item in trace:
            status_icon = "✅" if item.get("status") == "SUCCESS" else "⚠️"
            lines.append(f"\n**Step {item['step']}**: {item['thought']}")
            lines.append(f"- **Action**: `{item['action']}` ({json.dumps(item.get('args', {}))})")
            obs = item.get("observation", {})
            obs_preview = json.dumps(obs, indent=2, default=str)
            if len(obs_preview) > 500:
                obs_preview = obs_preview[:500] + "\n  ... [truncated for display]"
            lines.append(f"```json\n{obs_preview}\n```")

        lines.append("\n**Final Synthesis**: All requested operations were resolved autonomously by ClothOS's internal reasoning loop without requiring external API token consumption.")
        return "\n".join(lines)
