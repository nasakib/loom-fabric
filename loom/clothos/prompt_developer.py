# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
ClothOS Interactive Prompt Developer & Metaprompting Studio (`loom/clothos/prompt_developer.py`).
================================================================================================
A full-featured chat-based Prompt Developer studio embedded inside ClothOS:

1. Conversational Prompt Architecture:
   - Takes high-level goals, intents, and task descriptions.
   - Synthesizes professional, production-grade system prompts using strict XML-tagged modularity:
     <identity>, <operating_principles>, <cognitive_workflow>, <constraints>, <few_shot_examples>, <output_contract>.
2. Multi-Dimensional Quality Metrology:
   - Evaluates clarity, boundary constraint rigor, structural tagging, token economy, and jailbreak resilience.
   - Computes an overall Prompt Radiance Score (0 - 100%).
3. Interactive Chat-Based REPL Session:
   - Engage with the prompt developer in natural language (/prompt or /prompt-dev).
   - Conversational refinement: "make it stricter", "add few-shot examples for edge cases", "output JSON only".
4. Silicon Test-Driving:
   - Test-runs the prompt directly against active model heads (Qwen Coder, Loom Sovereign) to inspect outputs.
5. Persistent Repository:
   - Saves, versions, and loads prompts from `clothos_root/prompts/*.md`.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
import json
import logging
import os
from pathlib import Path
import re
import sys
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

logger = logging.getLogger("clothos.prompt_developer")
console = Console(force_terminal=True, color_system="auto")

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
PROMPTS_DIR = WORKSPACE_ROOT / "clothos_root" / "prompts"


@dataclass
class PromptQualityMetrics:
    """Quantitative metrology for evaluating prompt quality and robustness."""
    clarity_score: float          # 0 - 100% (Unambiguous objectives, explicit roles)
    constraint_rigor: float       # 0 - 100% (Negative bounds, safety, edge case handling)
    structural_modularity: float  # 0 - 100% (XML tagging, clean section demarcations)
    token_economy: float          # 0 - 100% (Conciseness without losing semantic density)
    robustness_score: float       # 0 - 100% (Anti-hallucination & anti-jailbreak defenses)
    overall_radiance: float       # Weighted average (0 - 100%)
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "clarity_score": round(self.clarity_score, 1),
            "constraint_rigor": round(self.constraint_rigor, 1),
            "structural_modularity": round(self.structural_modularity, 1),
            "token_economy": round(self.token_economy, 1),
            "robustness_score": round(self.robustness_score, 1),
            "overall_radiance": round(self.overall_radiance, 1),
            "recommendations": self.recommendations,
        }


@dataclass
class PromptTemplate:
    """Structured representation of a developed, production-ready system prompt."""
    name: str
    description: str
    target_domain: str
    system_prompt: str
    user_template: str
    input_variables: List[str]
    few_shot_examples: List[Dict[str, str]]
    output_contract: str
    quality_metrics: Optional[PromptQualityMetrics] = None
    version: str = "1.0.0"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_markdown(self) -> str:
        """Formats the template as a clean, standardized Markdown file with frontmatter."""
        var_str = ", ".join(self.input_variables) if self.input_variables else "none"
        radiance = self.quality_metrics.overall_radiance if self.quality_metrics else 90.0

        few_shots_md = ""
        if self.few_shot_examples:
            few_shots_md = "\n## Few-Shot Exemplars\n"
            for i, ex in enumerate(self.few_shot_examples, 1):
                few_shots_md += f"### Example {i}\n"
                few_shots_md += f"**Input**:\n```text\n{ex.get('input', '')}\n```\n"
                few_shots_md += f"**Output**:\n```text\n{ex.get('output', '')}\n```\n\n"

        return f"""---
name: {self.name}
version: {self.version}
domain: {self.target_domain}
radiance_score: {radiance:.1f}
variables: [{var_str}]
created_at: {self.created_at}
---

# {self.name}

> {self.description}

## System Prompt
```markdown
{self.system_prompt.strip()}
```

## User Query Template
```text
{self.user_template.strip()}
```
{few_shots_md}
## Output Contract
{self.output_contract.strip()}
"""


class PromptDeveloperEngine:
    """Core synthesis and optimization engine for prompt engineering."""

    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = workspace_root or WORKSPACE_ROOT
        self.prompts_dir = self.workspace_root / "clothos_root" / "prompts"
        self.prompts_dir.mkdir(parents=True, exist_ok=True)

    def evaluate_quality(self, prompt_text: str) -> PromptQualityMetrics:
        """Calculates multi-dimensional quality metrics on any prompt."""
        text_lower = prompt_text.lower()
        length = len(prompt_text)
        words = prompt_text.split()
        word_count = len(words)

        # 1. Structural Modularity (XML / Markdown tagging)
        has_xml = bool(re.search(r"<[A-Za-z0-9_-]+>.*?</[A-Za-z0-9_-]+>", prompt_text, re.DOTALL))
        tag_count = len(re.findall(r"<[A-Za-z0-9_-]+>", prompt_text))
        has_md_headers = bool(re.search(r"^#{1,4}\s+", prompt_text, re.MULTILINE))
        struct_score = min(100.0, (tag_count * 15.0) + (30.0 if has_xml else 0.0) + (20.0 if has_md_headers else 0.0))

        # 2. Clarity & Role
        role_keywords = ["you are", "role", "identity", "expert", "specialist", "purpose", "mission"]
        has_role = any(k in text_lower for k in role_keywords)
        clarity_score = 60.0
        if has_role:
            clarity_score += 25.0
        if 50 < word_count < 1000:
            clarity_score += 15.0

        # 3. Constraint Rigor
        constraint_keywords = ["do not", "never", "must not", "only", "always", "strict", "prohibited", "avoid", "ensure"]
        found_constraints = sum(1 for k in constraint_keywords if k in text_lower)
        constraint_score = min(100.0, 40.0 + (found_constraints * 10.0))

        # 4. Token Economy
        if word_count == 0:
            economy_score = 0.0
        elif word_count < 40:
            economy_score = 65.0
        elif 40 <= word_count <= 450:
            economy_score = 95.0
        elif 450 < word_count <= 800:
            economy_score = 80.0
        else:
            economy_score = max(50.0, 100.0 - (word_count / 20.0))

        # 5. Robustness & Anti-Hallucination
        robust_keywords = ["ground", "factual", "cite", "if unsure", "truth", "unbiased", "format", "json", "code"]
        found_robust = sum(1 for k in robust_keywords if k in text_lower)
        robustness_score = min(100.0, 50.0 + (found_robust * 10.0))

        # Overall Radiance
        overall = (
            clarity_score * 0.25 +
            constraint_score * 0.25 +
            struct_score * 0.20 +
            economy_score * 0.15 +
            robustness_score * 0.15
        )

        recs = []
        if struct_score < 75.0:
            recs.append("Wrap distinct sections in explicit XML tags like <instructions>, <constraints>, <output_format>.")
        if constraint_score < 75.0:
            recs.append("Specify negative boundaries: state what the model should NEVER do (e.g., 'Do not hallucinate imports').")
        if not has_role:
            recs.append("Define a concrete persona and expertise level in an <identity> block.")
        if word_count > 600:
            recs.append("Consider pruning repetitive prose to preserve model parameter headroom.")

        return PromptQualityMetrics(
            clarity_score=clarity_score,
            constraint_rigor=constraint_score,
            structural_modularity=struct_score,
            token_economy=economy_score,
            robustness_score=robustness_score,
            overall_radiance=overall,
            recommendations=recs or ["Prompt meets high-radiance architectural standards."],
        )

    def develop_prompt(
        self,
        goal: str,
        role: str = "Expert AI Assistant",
        domain: str = "SOFTWARE_DEV",
        output_format: str = "Markdown",
        constraints: Optional[List[str]] = None,
        include_few_shots: bool = True,
    ) -> PromptTemplate:
        """Synthesizes a complete, production-grade prompt template from user intent."""
        clean_constraints = constraints or [
            "Never fabricate APIs, functions, or hallucinate citations.",
            "Maintain strict Landauer energy bounds (concise, high-information-density output).",
            "Adhere to deterministic invariants and provide executable, complete code.",
        ]

        # Extract potential template variables
        var_matches = re.findall(r"\{\{([A-Za-z0-9_]+)\}\}", goal)
        variables = list(set(var_matches)) if var_matches else ["input_query"]
        user_template = f"{{{{{variables[0]}}}}}" if variables else "{{input_query}}"

        # Generate few-shot examples if requested
        few_shots = []
        if include_few_shots:
            few_shots = [
                {
                    "input": f"Demonstrate standard operation for {goal[:40]}...",
                    "output": f"```python\n# Ratified invariant output\ndef execute():\n    return 'Deterministic Result'\n```"
                }
            ]

        # Build System Prompt with XML Architecture
        constraints_str = "\n".join(f"  - {c}" for c in clean_constraints)

        system_prompt = f"""<identity>
You are an advanced, sovereign {role} within the ClothOS ecosystem specializing in {domain}.
Your primary mission is to: {goal.strip()}
</identity>

<operating_principles>
- Epistemic Grounding: Root all reasoning in empirical facts, physical invariants, and formal specifications.
- Monotonic Progress: Generate solutions that maintain zero regressions and maximize correctness.
- Parameter Headroom: Deliver high-density, surgical responses without filler, apologies, or preamble.
</operating_principles>

<cognitive_workflow>
1. Analyze the user's objective and identify all boundary constraints.
2. Formulate the minimal necessary solution adhering strictly to specifications.
3. Validate syntax, edge cases, and safety invariants before presenting the final output.
</cognitive_workflow>

<constraints>
{constraints_str}
</constraints>

<output_contract>
Deliver output strictly in {output_format} format adhering to the specifications above.
</output_contract>"""

        metrics = self.evaluate_quality(system_prompt)

        # Generate clean slug name
        slug = re.sub(r"[^a-z0-9_]+", "_", goal[:32].lower()).strip("_") or "custom_prompt"
        template_name = f"prompt_{slug}"

        return PromptTemplate(
            name=template_name,
            description=f"Automated prompt synthesized for: {goal}",
            target_domain=domain,
            system_prompt=system_prompt,
            user_template=user_template,
            input_variables=variables,
            few_shot_examples=few_shots,
            output_contract=output_format,
            quality_metrics=metrics,
        )

    def optimize_prompt(self, raw_prompt: str) -> Dict[str, Any]:
        """Takes an existing unoptimized prompt, critiques it, and returns an enhanced version."""
        initial_metrics = self.evaluate_quality(raw_prompt)

        # Synthesize optimized version
        developed = self.develop_prompt(
            goal=raw_prompt[:200],
            role="Specialized Autonomous Agent",
            domain="GENERAL_COMPUTE",
            output_format="Structured Markdown",
        )
        final_metrics = developed.quality_metrics or self.evaluate_quality(developed.system_prompt)

        return {
            "original_prompt": raw_prompt,
            "original_radiance": initial_metrics.overall_radiance,
            "optimized_prompt": developed.system_prompt,
            "optimized_radiance": final_metrics.overall_radiance,
            "radiance_delta": round(final_metrics.overall_radiance - initial_metrics.overall_radiance, 1),
            "improvements": initial_metrics.recommendations,
            "metrics": final_metrics.to_dict(),
        }

    def save_prompt(self, template: PromptTemplate, custom_name: Optional[str] = None) -> Path:
        """Saves a developed prompt template to the persistent prompt library."""
        filename = (custom_name or template.name)
        if not filename.endswith(".md"):
            filename += ".md"
        target_path = self.prompts_dir / filename
        target_path.write_text(template.to_markdown(), encoding="utf-8")
        logger.info(f"Saved prompt template to {target_path}")
        return target_path

    def load_prompt(self, name_or_path: str) -> Optional[PromptTemplate]:
        """Loads a saved prompt template from disk."""
        target = self.prompts_dir / (name_or_path if name_or_path.endswith(".md") else f"{name_or_path}.md")
        if not target.exists():
            target = Path(name_or_path)
        if not target.exists():
            return None

        content = target.read_text(encoding="utf-8")
        # Extract system prompt between ```markdown and ```
        sys_match = re.search(r"## System Prompt\s+```markdown\s+(.*?)\s+```", content, re.DOTALL)
        sys_prompt = sys_match.group(1).strip() if sys_match else content

        metrics = self.evaluate_quality(sys_prompt)
        return PromptTemplate(
            name=target.stem,
            description=f"Loaded from {target.name}",
            target_domain="LOADED_PROMPT",
            system_prompt=sys_prompt,
            user_template="{{input}}",
            input_variables=["input"],
            few_shot_examples=[],
            output_contract="Markdown",
            quality_metrics=metrics,
        )

    def list_prompts(self) -> List[Dict[str, Any]]:
        """Lists all persistent prompt templates in the library."""
        res = []
        for file in self.prompts_dir.glob("*.md"):
            try:
                content = file.read_text(encoding="utf-8")
                rad_m = re.search(r"radiance_score:\s*([0-9.]+)", content)
                rad = float(rad_m.group(1)) if rad_m else 90.0
                res.append({
                    "name": file.stem,
                    "file": file.name,
                    "path": str(file),
                    "radiance": rad,
                    "size_bytes": file.stat().st_size,
                })
            except Exception:
                pass
        return sorted(res, key=lambda x: x["name"])


class PromptDeveloperChatSession:
    """Interactive chat-based REPL session for conversational prompt development."""

    def __init__(self, engine: Optional[PromptDeveloperEngine] = None, tools_instance: Any = None):
        self.engine = engine or PromptDeveloperEngine()
        self.tools = tools_instance
        self.current_template: Optional[PromptTemplate] = None
        self.conversation_history: List[Dict[str, str]] = []

    def handle_user_input(self, text: str) -> str:
        """Processes a single conversational turn in the prompt developer studio."""
        text_clean = text.strip()
        p_lower = text_clean.lower()

        # Command: /exit or /quit
        if p_lower in ["/exit", "/quit", "/q", "exit", "quit"]:
            return "EXIT_SESSION"

        # Command: /list
        if p_lower in ["/list", "/prompts"]:
            prompts = self.engine.list_prompts()
            if not prompts:
                return "📁 No saved prompt templates found in `clothos_root/prompts/`."
            table = Table(title="📚 [bold #00ff7f]ClothOS Persistent Prompt Library[/bold #00ff7f]", border_style="#38bdf8")
            table.add_column("Prompt Name", style="bold white")
            table.add_column("Radiance", style="cyan")
            table.add_column("File Size", style="dim")
            for p in prompts:
                table.add_row(p["name"], f"{p['radiance']:.1f}%", f"{p['size_bytes']} bytes")
            console.print(table)
            return "Use `/load <name>` to load any template."

        # Command: /score
        if p_lower.startswith("/score"):
            target_text = text_clean[len("/score"):].strip()
            if not target_text and self.current_template:
                target_text = self.current_template.system_prompt
            if not target_text:
                return "⚠ Provide prompt text or develop a prompt first to score."
            metrics = self.engine.evaluate_quality(target_text)
            self._render_score_panel(metrics)
            return f"Prompt evaluated: Overall Radiance is **{metrics.overall_radiance:.1f}%**."

        # Command: /save
        if p_lower.startswith("/save"):
            parts = text_clean.split(maxsplit=1)
            name = parts[1] if len(parts) > 1 else (self.current_template.name if self.current_template else "developed_prompt")
            if not self.current_template:
                return "⚠ No prompt template currently developed. Tell me what prompt to build first!"
            self.current_template.name = name
            path = self.engine.save_prompt(self.current_template, name)
            return f"✔ Prompt template saved successfully to [`{path.name}`](file:///{path.as_posix()})!"

        # Command: /test
        if p_lower.startswith("/test"):
            test_query = text_clean[len("/test"):].strip() or "Hello, test this prompt with a sample query."
            if not self.current_template:
                return "⚠ Please develop or load a prompt first before test-driving."
            return self._execute_test(test_query)

        # Conversational Prompt Synthesis / Refinement
        if self.current_template is None:
            # First prompt creation turn
            self.current_template = self.engine.develop_prompt(goal=text_clean)
            self._render_prompt_panel(self.current_template)
            return (
                f"✦ **Prompt Developed** (Radiance: **{self.current_template.quality_metrics.overall_radiance:.1f}%**)\n\n"
                f"- To test: Type `/test <query>`\n"
                f"- To refine: Say *\"make it more concise\"*, *\"add JSON formatting\"*, or *\"add edge case constraints\"*\n"
                f"- To save: Type `/save <name>`\n"
                f"- To exit: Type `/exit`"
            )
        else:
            # Conversational refinement turn
            refined_goal = f"{self.current_template.description}. User refinement request: {text_clean}"
            new_constraints = list(self.current_template.system_prompt.splitlines())
            if "strict" in p_lower or "negative" in p_lower or "never" in p_lower:
                new_constraints.append(f"Never violate: {text_clean}")

            self.current_template = self.engine.develop_prompt(
                goal=refined_goal,
                role=f"Refined {self.current_template.target_domain} Specialist",
                domain=self.current_template.target_domain,
                output_format="Strict JSON" if "json" in p_lower else self.current_template.output_contract,
                constraints=[f"Refinement: {text_clean}"] + ["Never fabricate claims or hallucinate citations."],
            )
            self._render_prompt_panel(self.current_template)
            return f"✔ Prompt refined! New Radiance Score: **{self.current_template.quality_metrics.overall_radiance:.1f}%**."

    def _render_prompt_panel(self, template: PromptTemplate):
        """Displays the developed prompt in a styled terminal panel."""
        metrics = template.quality_metrics or self.engine.evaluate_quality(template.system_prompt)
        content = f"[bold cyan]Domain:[/bold cyan] {template.target_domain} │ [bold green]Radiance:[/bold green] {metrics.overall_radiance:.1f}%\n\n"
        content += f"[bold white]── System Prompt ────────────────────────────────────────[/bold white]\n"
        content += f"{template.system_prompt}\n"
        content += f"[bold white]─────────────────────────────────────────────────────────[/bold white]\n"
        content += f"[bold yellow]Output Contract:[/bold yellow] {template.output_contract}\n"

        console.print(Panel(
            content,
            title=f"🎨 [bold #00ff7f]ClothOS Prompt Studio · {template.name}[/bold #00ff7f]",
            border_style="#38bdf8",
        ))

    def _render_score_panel(self, metrics: PromptQualityMetrics):
        """Displays a quality metrology scorecard."""
        table = Table(title="📊 [bold #00ff7f]Prompt Quality & Robustness Scorecard[/bold #00ff7f]", border_style="#10b981")
        table.add_column("Quality Dimension", style="bold white")
        table.add_column("Score", style="cyan")
        table.add_column("Rating", style="bold green")

        def rating(s: float) -> str:
            if s >= 90: return "[green]EXCELLENT[/green]"
            if s >= 75: return "[yellow]GOOD[/yellow]"
            return "[red]NEEDS REFINEMENT[/red]"

        table.add_row("Clarity & Role Definition", f"{metrics.clarity_score:.1f}%", rating(metrics.clarity_score))
        table.add_row("Constraint Rigor & Negative Bounds", f"{metrics.constraint_rigor:.1f}%", rating(metrics.constraint_rigor))
        table.add_row("Structural Modularity (XML/Tags)", f"{metrics.structural_modularity:.1f}%", rating(metrics.structural_modularity))
        table.add_row("Token Economy & Density", f"{metrics.token_economy:.1f}%", rating(metrics.token_economy))
        table.add_row("Robustness & Anti-Hallucination", f"{metrics.robustness_score:.1f}%", rating(metrics.robustness_score))
        table.add_row("Overall Radiance Index", f"{metrics.overall_radiance:.1f}%", f"[bold #00ff7f]{rating(metrics.overall_radiance)}[/bold #00ff7f]")
        console.print(table)

        if metrics.recommendations:
            console.print("[bold yellow]Recommendations:[/bold yellow]")
            for r in metrics.recommendations:
                console.print(f"  • {r}")

    def _execute_test(self, test_input: str) -> str:
        """Runs the prompt against the active language model."""
        if not self.current_template:
            return "No prompt available to test."

        console.print(f"[bold #38bdf8]⚡ Test-Driving Prompt on Physical Silicon...[/bold #38bdf8]")
        full_test_prompt = f"{self.current_template.system_prompt}\n\nUser Query: {test_input}"

        try:
            if self.tools and hasattr(self.tools, "execute"):
                res = self.tools.execute("text_generation", prompt=full_test_prompt)
                out_text = res.get("generated_text", "")
                console.print(Panel(
                    Markdown(out_text),
                    title=f"🔬 [bold #00ff7f]Model Output Under Test · {res.get('model', 'Cortex')}[/bold #00ff7f]",
                    subtitle=f"[dim]Speed: {res.get('tokens_per_second')} tok/s | Latency: {res.get('latency_ms')}ms[/dim]",
                    border_style="green",
                ))
                return "✔ Test run complete! Review model output above."
        except Exception as e:
            logger.debug(f"Live model execution note: {e}")

        # Deterministic simulation fallback
        simulated = f"Deterministic response evaluated under system instructions for input: '{test_input}'"
        console.print(Panel(simulated, title="🔬 [bold yellow]Simulated Model Output[/bold yellow]", border_style="yellow"))
        return "✔ Simulated test run complete."


prompt_developer_engine = PromptDeveloperEngine()
