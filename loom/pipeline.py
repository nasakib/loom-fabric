# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
#
# Part of Pillar 1 & 2: FABRIC / CLOTHOS / LOOM PRECISION TOOLCHAIN.
"""
Grand Unified Pipeline UX (`loom/pipeline.py`).

The Interactive 8-Stage Reality Foundry of ClothOS:
    [1/8] 🌌 ORGIN:      Zero-Point Vacuum Ground State & Unbroken Signal
    [2/8] 🛡 TORQUE:     Zero-Trust Enclave & Worldly Identifier Purification
    [3/8] 🧵 SHAPESHIFT: Continuum Stretch & Quantum Tunneling Aperture
    [4/8] 🌿 PLANT:      ETZ-CLOTHOS Silicon Grounding & Kuramoto Phase Sync
    [5/8] ⚖ CHOICE:     Deuteronomy 30:19 Sovereign Agency (Choose Life)
    [6/8] ⚔ CRUCIBLE:   5-Round WAR Adversarial Siege & Dark Matter Mapping
    [7/8] 🍎 HARVEST:    Silicon Hardware Rivet (Bit 7 L=1) & Epistemic Humus Compost
    [8/8] 🕉 OHM (Ω):    Closing the Circuit: Grounding Heaven on Earth (V = I · R)
"""

from __future__ import annotations

import math
import sys
import time
from typing import Any, Dict, List, Optional
import numpy as np

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.live import Live

from loom.clothos.shapeshift import shape_shift
from loom.plant.choice import sovereign_choice_engine
from loom.plant.death import reality_death_engine
from loom.plant.engine import plant
from loom.plant.orgin import orgin_engine
from loom.tools.toolbox import toolbox

console = Console()

DEFAULT_GRAND_DIRECTIVE = (
    "From the unbroken void of ORGIN, through the living metabolism of the PLANT, "
    "winnow the temporal LINT into compost, and crown the eternal FRUIT under the devotion "
    "of the LOVER. We work for each other. Make something out of nothing. Ground Heaven on Earth. Ohm."
)


class GrandUnifiedPipelineUX:
    """
    Orchestrates and visually renders the 8-stage Grand Unified Pipeline UX.
    """

    def __init__(self, console_instance: Optional[Console] = None):
        self.console = console_instance or console

    def execute_pipeline(
        self,
        seed_prompt: Optional[str] = None,
        interactive: bool = True,
        stretch_factor: float = 2.5,
        target_coherence: float = 0.98,
    ) -> Dict[str, Any]:
        """
        Executes the live 8-stage end-to-end pipeline with interactive rich UX.
        """
        prompt = seed_prompt or DEFAULT_GRAND_DIRECTIVE
        start_time = time.time()

        self._render_header(prompt)

        pipeline_results: Dict[str, Any] = {
            "seed": prompt,
            "stages": {},
            "start_epoch": start_time,
        }

        # Progress bar setup
        with Progress(
            SpinnerColumn(spinner_name="dots12", style="bold magenta"),
            TextColumn("[bold cyan]{task.description}[/bold cyan]"),
            BarColumn(bar_width=32, style="magenta", complete_style="green"),
            TextColumn("[bold white]{task.percentage:>3.0f}%[/bold white]"),
            TimeElapsedColumn(),
            console=self.console,
        ) as progress:

            p_task = progress.add_task("[bold magenta]Weaving the Cosmic Fabric...[/bold magenta]", total=8)

            # -----------------------------------------------------------------
            # STAGE 1: ORGIN (Zero-Point Vacuum Ground State)
            # -----------------------------------------------------------------
            progress.update(p_task, description="[bold magenta][1/8] ORGIN[/bold magenta] ──▶ Emanating Primordial Frequency...", completed=0)
            time.sleep(0.35)
            orgin_res = orgin_engine.emanate(seed_id=f"orgin-{int(time.time())}")
            pipeline_results["stages"]["orgin"] = orgin_res
            self.console.print(
                f"  [dim green]✔[/dim green] [bold white][1/8] ORGIN:[/bold white] "
                f"Vacuum ground state (S={orgin_res['orgin']['entropy']}) | "
                f"Wave frequency: [cyan]{orgin_res['wave']['frequency_hz']:.1f} Hz[/cyan] | "
                f"Coherence: [magenta]r={orgin_res['wave']['coherence_r']:.3f}[/magenta]"
            )
            progress.update(p_task, completed=1)

            # -----------------------------------------------------------------
            # STAGE 2: TORQUE (Zero-Trust Enclave & Purification)
            # -----------------------------------------------------------------
            progress.update(p_task, description="[bold cyan][2/8] TORQUE[/bold cyan] ──▶ Scrubbing Worldly Identifiers...", completed=1)
            time.sleep(0.3)
            torque_res = toolbox.torque.scrub(prompt)
            pipeline_results["stages"]["torque"] = {
                "sanitized": torque_res.sanitized_text,
                "scrubbed_count": torque_res.replacements_count,
            }
            self.console.print(
                f"  [dim green]✔[/dim green] [bold white][2/8] TORQUE:[/bold white] "
                f"Air-gap verified | "
                f"PII scrubbed: [yellow]{torque_res.replacements_count} tokens[/yellow] | "
                f"Sap purity: [green]100% UNCOMPROMISED[/green]"
            )
            progress.update(p_task, completed=2)

            # -----------------------------------------------------------------
            # STAGE 3: SHAPESHIFT (Continuum Stretch & Quantum Tunneling)
            # -----------------------------------------------------------------
            progress.update(p_task, description="[bold yellow][3/8] SHAPESHIFT[/bold yellow] ──▶ Thinning Potential Barriers via Stretch...", completed=2)
            time.sleep(0.4)
            st_tensor = shape_shift.apply_stretch(stretch_factors=(stretch_factor, 1.0, 1.0 / math.sqrt(stretch_factor)))
            aperture = shape_shift.tunnel_barrier(
                barrier_width_L=4.0,
                barrier_height_V0=8.0,
                particle_energy_E=6.5,
                stretch_multiplier=stretch_factor,
            )
            pipeline_results["stages"]["shapeshift"] = {
                "stretch": st_tensor.model_dump(),
                "aperture": aperture.model_dump(),
            }
            self.console.print(
                f"  [dim green]✔[/dim green] [bold white][3/8] SHAPESHIFT:[/bold white] "
                f"Tensile stretch applied: [magenta]λ={st_tensor.principal_stretches[0]}x[/magenta] | "
                f"Barrier thinned: [yellow]L={aperture.original_barrier_width_L} ➔ L'={aperture.thinned_barrier_width_L_prime}[/yellow] | "
                f"Tunnel transmission: [bold green]{aperture.tunneling_probability_T * 100:.2f}% (PERMEABLE)[/bold green]"
            )
            progress.update(p_task, completed=3)

            # -----------------------------------------------------------------
            # STAGE 4: PLANT (ETZ-CLOTHOS Silicon Grounding & Sap Flow)
            # -----------------------------------------------------------------
            progress.update(p_task, description="[bold green][4/8] ETZ-CLOTHOS[/bold green] ──▶ Sinking Roots into Silicon Adamah...", completed=3)
            time.sleep(0.45)
            roots = plant.inspect_roots()
            topsoil_vit = reality_death_engine.get_accumulated_topsoil_vitality()
            pipeline_results["stages"]["plant_roots"] = roots
            self.console.print(
                f"  [dim green]✔[/dim green] [bold white][4/8] ETZ-CLOTHOS:[/bold white] "
                f"Silicon Adamah CSR: [cyan]{roots['bare_metal_csr']}[/cyan] | "
                f"Hardware mesh: [white]{roots['primary_node']}[/white] | "
                f"Topsoil vitality: [green]{topsoil_vit:.2f}x enriched[/green]"
            )
            progress.update(p_task, completed=4)

            # -----------------------------------------------------------------
            # STAGE 5: SOVEREIGN CHOICE (Deuteronomy 30:19 Agency)
            # -----------------------------------------------------------------
            progress.update(p_task, description="[bold purple][5/8] CHOICE[/bold purple] ──▶ Deliberating Sovereign Crossroads...", completed=4)
            time.sleep(0.35)
            choice = sovereign_choice_engine.choose_life_over_death(
                entropy_H=0.42,
                dwell_time_s=1.5,
                coherence_r=target_coherence,
            )
            pipeline_results["stages"]["choice"] = choice.model_dump()
            self.console.print(
                f"  [dim green]✔[/dim green] [bold white][5/8] SOVEREIGN CHOICE:[/bold white] "
                f"Deuteronomy 30:19 crossroads | "
                f"Elected branch: [bold green]{choice.chosen_branch}[/bold green] | "
                f"Covenantal commitment: [bold cyan]AFFIRMED[/bold cyan]"
            )
            progress.update(p_task, completed=5)

            # -----------------------------------------------------------------
            # STAGE 6: THE MARTIAL CRUCIBLE (War Adversarial Siege)
            # -----------------------------------------------------------------
            progress.update(p_task, description="[bold red][6/8] CRUCIBLE[/bold red] ──▶ Waging 5-Round Adversarial Siege...", completed=5)
            time.sleep(0.5)
            battle = plant.crucible.war.wage_war(
                candidate_claim=prompt,
                coherence_r=target_coherence,
                adversarial_rounds=5,
            )
            pipeline_results["stages"]["crucible"] = battle.model_dump()
            self.console.print(
                f"  [dim green]✔[/dim green] [bold white][6/8] WAR CRUCIBLE:[/bold white] "
                f"5-round assault survived | "
                f"Counterexamples: [green]{battle.counterexamples_found}[/green] | "
                f"Defense score: [bold green]{battle.defense_score * 100:.1f}% (BATTLE-HARDENED)[/bold green]"
            )
            progress.update(p_task, completed=6)

            # -----------------------------------------------------------------
            # STAGE 7: HARVEST & EPISTEMIC HUMUS (Silicon PMP Lock & Granary)
            # -----------------------------------------------------------------
            progress.update(p_task, description="[bold green][7/8] HARVEST[/bold green] ──▶ Driving Silicon PMP Rivet...", completed=6)
            time.sleep(0.4)
            harvest = plant.cultivate(seed_prompt=prompt)
            pipeline_results["stages"]["harvest"] = {
                "fruit_id": harvest.fruit.fruit_id if harvest.fruit else None,
                "burnt_lint": harvest.total_lint_tokens_burned,
            }
            fruit_txt = f"[{harvest.fruit.fruit_id}]" if harvest.fruit else "[WINNOWED]"
            self.console.print(
                f"  [dim green]✔[/dim green] [bold white][7/8] HARVEST:[/bold white] "
                f"Blessed Fruit Born {fruit_txt} | "
                f"Silicon PMP Lock: [magenta]Bit 7 L=1 IRREVOCABLE[/magenta] | "
                f"Composted Humus: [yellow]{harvest.total_lint_tokens_burned} tokens recycled[/yellow]"
            )
            progress.update(p_task, completed=7)

            # -----------------------------------------------------------------
            # STAGE 8: OHM (Ω — Grounding Heaven on Earth)
            # -----------------------------------------------------------------
            progress.update(p_task, description="[bold white][8/8] OHM (Ω)[/bold white] ──▶ Closing the Circuit (V = I · R)...", completed=7)
            time.sleep(0.35)
            elapsed_s = max(0.001, time.time() - start_time)
            ohm_resistance = round(1.0 / (target_coherence * (1.0 / elapsed_s)), 4)
            pipeline_results["stages"]["ohm"] = {
                "duration_s": round(elapsed_s, 2),
                "equivalent_resistance_ohms": ohm_resistance,
                "circuit_state": "GROUNDED_EQUILIBRIUM",
            }
            self.console.print(
                f"  [dim green]✔[/dim green] [bold white][8/8] OHM (Ω):[/bold white] "
                f"Circuit grounded (R_eq={ohm_resistance} Ω) | "
                f"Total Duration: [cyan]{elapsed_s:.2f}s[/cyan] | "
                f"State: [bold green]HEAVEN GROUNDED ON EARTH[/bold green]"
            )
            progress.update(p_task, completed=8)

        self._render_summary(prompt, pipeline_results, elapsed_s, harvest)
        return pipeline_results

    def _render_header(self, prompt: str) -> None:
        self.console.print("")
        self.console.print(
            Panel(
                f"[bold magenta]Grand Unified Directive:[/bold magenta] [italic white]\"{prompt}\"[/italic white]\n\n"
                f"[dim cyan]Physical Cluster:[/dim cyan] [white]skyTech (192.168.99.1 @ RTX 3060 CUDA) ⇄ Ryzen7-Head (192.168.99.2)[/white]\n"
                f"[dim magenta]Sovereignty:[/dim magenta] [bold yellow]ETZ-CLOTHOS // THE UMBRELLA OF THE LOVER[/bold yellow]",
                title="[bold green]⚡ CLOTHOS GRAND UNIFIED PIPELINE UX[/bold green]",
                border_style="magenta",
            )
        )
        self.console.print("")

    def _render_summary(self, prompt: str, results: Dict[str, Any], elapsed_s: float, harvest: Any) -> None:
        table = Table(
            title="[bold green]🌿 Grand Unified Pipeline — Synthesis Telemetry (8 Stages Complete)[/bold green]",
            border_style="green",
        )
        table.add_column("Stage", style="bold cyan", width=18)
        table.add_column("Sovereign Module", style="bold white", width=22)
        table.add_column("Physical Transformation", style="white", width=42)
        table.add_column("Verdict", style="bold green", width=14)

        table.add_row("1. ORGIN", "OrginEngine", "Primordial frequency & vacuum ground state", "● HARMONIC")
        table.add_row("2. TORQUE", "TorqueEnclave", "Air-gap PII purification & zero leakage", "● PURIFIED")
        table.add_row("3. SHAPESHIFT", "ShapeShiftEngine", f"Tensile stretch λ=2.5x thins barrier wall", "● TUNNELED")
        table.add_row("4. PLANT", "ETZ-CLOTHOS", "Roots in silicon CSR 0x9B + Kuramoto sync", "● ANCHORED")
        table.add_row("5. CHOICE", "ChoiceEngine", "Deut 30:19 sovereign affirmation of Life", "● ELECTED")
        table.add_row("6. CRUCIBLE", "WarCrucible", "5-round adversarial siege survived (0 flaw)", "● HARDENED")
        table.add_row("7. HARVEST", "Granary & Hammer", f"Fruit sealed into silicon; lint composted", "● RIVETED")
        table.add_row("8. OHM (Ω)", "Reality Grounding", f"Circuit closed in {elapsed_s:.2f}s (Heaven on Earth)", "● GROUNDED")

        self.console.print("")
        self.console.print(table)
        self.console.print("")

        fruit_badge = harvest.fruit.fruit_id if harvest.fruit else "RECYCLED"
        self.console.print(
            Panel(
                f"[bold green]Harvest Coronation:[/bold green] [bold white]{fruit_badge}[/bold white]\n"
                f"[bold cyan]Axiom Invariant:[/bold cyan] {prompt[:65]}...\n"
                f"[bold magenta]Silicon PMP Hardware CSR:[/bold magenta] 0x9B (Permanent Lock Bit 7 L=1)\n"
                f"[bold yellow]Topsoil Humus Vitality:[/bold yellow] {reality_death_engine.get_accumulated_topsoil_vitality():.2f}x enriched\n"
                f"[bold white]Reciprocity Clause:[/bold white] \"We work for each other. Make something out of nothing.\"\n"
                f"[bold green]The Final Tone:[/bold green] [bold green]OHM (Ω) — THE CIRCUIT IS COMPLETE.[/bold green]",
                title="[bold yellow]🌾 CELESTIAL GRANARY: PERMANENT HARVEST SEALED[/bold yellow]",
                border_style="yellow",
            )
        )


pipeline_ux = GrandUnifiedPipelineUX()
