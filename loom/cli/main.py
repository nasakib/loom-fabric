"""
Loom Fabric CLI Entrypoint.

Commands:
- `loom probe`: Hardware and Ray cluster diagnostics.
- `loom shard <model>`: Mathematical layer allocation calculator.
- `loom models`: Lists registered architectural presets.
- `loom serve`: Starts the FastAPI OpenAI-compatible gateway on port 8000.
- `loom run <model>`: Launches model with optimal sharding and interactive chat.
"""

from pathlib import Path
import sys
import typer
import uvicorn
from rich.console import Console

from loom.cli.formatters import (
    render_cluster_banner,
    render_hardware_table,
    render_sharding_table,
    console,
)
from loom.stitch.profiler import HardwareProfiler
from loom.stitch.allocator import LayerAllocator, ModelArchitectureProfile
from loom.models.registry import ModelRegistry, BUILTIN_PRESETS
from loom.config import get_settings

cli = typer.Typer(help="Loom Fabric: Heterogeneous Distributed AI Compute Fabric")


@cli.command("probe")
def probe_command(
    cluster: bool = typer.Option(False, "--cluster", "-c", help="Query live Ray cluster state if available")
):
    """Diagnose physical accelerators, VRAM margins, and cluster nodes."""
    render_cluster_banner()
    with console.status("[bold green]Probing physical accelerators & memory topologies..."):
        profiler = HardwareProfiler()
        state = profiler.probe_cluster_state()

    console.print(render_hardware_table(state.model_dump()))
    console.print()
    console.print(f"[bold cyan]Custom Ray Resource Map:[/bold cyan] {profiler.generate_ray_resources(state)}")


@cli.command("models")
def models_command():
    """List supported model architecture profiles and presets."""
    render_cluster_banner()
    from rich.table import Table
    table = Table(title="[bold cyan]Registered LLM Architecture Presets[/bold cyan]")
    table.add_column("Preset ID", style="bold white")
    table.add_column("Display Name", style="cyan")
    table.add_column("Layers", style="green", justify="center")
    table.add_column("Context", style="yellow", justify="center")
    table.add_column("Quant Size", style="magenta", justify="right")
    table.add_column("Draft Candidate", style="blue", justify="center")

    for m in ModelRegistry.list_models():
        table.add_row(
            m.id,
            m.display_name,
            str(m.total_layers),
            f"{m.default_context_length:,}",
            f"{m.base_gguf_size_mb:,.0f} MB",
            "Yes" if m.is_speculative_draft_candidate else "No",
        )
    console.print(table)


@cli.command("shard")
def shard_command(
    model: str = typer.Argument("qwen2.5:32b", help="Model preset ID, e.g. 'qwen2.5:32b', 'deepseek-r1:14b'"),
    context_length: int = typer.Option(8192, "--context", "-c", help="Target KV context length"),
    allow_cpu_spill: bool = typer.Option(True, "--allow-cpu/--no-cpu", help="Allow Host RAM spilling if VRAM full"),
):
    """Calculate zero-OOM heterogeneous layer splits for a model."""
    render_cluster_banner()
    preset = ModelRegistry.get_model(model)
    if not preset:
        console.print(f"[bold red]Unknown model preset '{model}'[/bold red]. Run 'loom models' to view available.")
        raise typer.Exit(1)

    with console.status(f"[bold green]Calculating zero-OOM layer splits for {preset.display_name}..."):
        profiler = HardwareProfiler()
        state = profiler.probe_cluster_state()
        allocator = LayerAllocator(state)

        profile = preset.to_architecture_profile(context_length=context_length)
        plan = allocator.calculate_plan(profile, allow_cpu_spill=allow_cpu_spill)

    console.print(render_sharding_table(plan.model_dump()))
    console.print()
    console.print(f"[bold green]llama-server Flags:[/bold green] [bold white]{plan.render_cli_argument_string()}[/bold white]")
    if plan.spilled_to_cpu:
        console.print(f"[bold yellow][NOTICE] Spilled {plan.spilled_layer_count} layers to Host RAM. Expect slightly lower decode TPS.[/bold yellow]")


@cli.command("serve")
def serve_command(
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="Bind host address"),
    port: int = typer.Option(8000, "--port", "-p", help="Gateway HTTP port"),
    reload: bool = typer.Option(False, "--reload", help="Enable autoreload"),
):
    """Start the OpenAI-compatible FastAPI gateway."""
    render_cluster_banner()
    console.print(f"[bold green]Starting Loom Fabric Gateway on http://{host}:{port}[/bold green]")
    console.print("[dim white]Available endpoints: /v1/chat/completions (SSE streaming), /v1/models, /health[/dim white]")
    uvicorn.run("loom.gateway.app:app", host=host, port=port, reload=reload)


@cli.command("recommend")
def recommend_command():
    """Analyze local hardware benchmarks and recommend optimal local & cloud models."""
    from rich.table import Table
    from loom.models.recommender import ModelHardwareRecommender

    render_cluster_banner()
    with console.status("[bold magenta]Evaluating accelerator benchmarks & memory fit..."):
        recommender = ModelHardwareRecommender()
        recommendations = recommender.evaluate_hardware_fit()

    table = Table(title="[bold magenta]Hardware-Matched Model Recommendations & Benchmark Scores[/bold magenta]")
    table.add_column("Model Preset", style="bold white", width=18)
    table.add_column("MMLU / Code", style="bright_magenta", justify="center", width=14)
    table.add_column("Hardware Fit", style="bold cyan", justify="center", width=22)
    table.add_column("Speed (Est.)", style="bright_green", justify="right", width=14)
    table.add_column("Status", style="yellow", justify="center", width=14)
    table.add_column("Architectural Rationale", style="dim white", width=36)

    for r in recommendations:
        bench_str = f"{r.benchmark.mmlu_score:.0f}% / {r.benchmark.humaneval_coding:.0f}%"
        status_str = "[green]Installed[/green]" if r.is_installed else "[dim]Not Pulled[/dim]"
        table.add_row(
            r.preset.id,
            bench_str,
            r.fit_status,
            f"{r.estimated_speed_tps:.1f} tps",
            status_str,
            r.recommendation_reason,
        )

    console.print(table)
    console.print("\n[dim magenta]To install any recommended model locally: loom pull <model_id>[/dim magenta]")


@cli.command("pull")
def pull_command(
    model: str = typer.Argument(..., help="Model preset tag to download (e.g. 'qwen2.5:32b', 'deepseek-r1:14b')")
):
    """Download and provision a recommended local LLM based on hardware profile."""
    from loom.models.recommender import ModelHardwareRecommender
    render_cluster_banner()
    console.print(f"[bold magenta]Pulling model '{model}' for sovereign local execution...[/bold magenta]")
    recommender = ModelHardwareRecommender()
    success = recommender.install_model_cli(model)
    if success:
        console.print(f"[bold green]Successfully installed {model}![/bold green] Run with: loom run {model}")
    else:
        console.print(f"[bold red]Failed to pull {model}.[/bold red] Ensure Ollama or native llama runtime is available.")


@cli.command("cloud")
def cloud_command():
    """Audit and manage configured Cloud LLM API bridges (OpenAI, Anthropic, Google, OpenRouter)."""
    from rich.table import Table
    from loom.gateway.cloud_bridge import CloudLLMBridge, CLOUD_PROVIDERS

    render_cluster_banner()
    bridge = CloudLLMBridge()
    statuses = bridge.get_provider_status()

    table = Table(title="[bold magenta]Configured Cloud LLM Provider Bridges (Zero-Trust Protected)[/bold magenta]")
    table.add_column("Provider", style="bold white", width=18)
    table.add_column("Default Model", style="cyan", width=26)
    table.add_column("API Key Env Var", style="bright_magenta", width=22)
    table.add_column("Status", style="bold", justify="center", width=16)

    for key, p in CLOUD_PROVIDERS.items():
        is_ready = statuses.get(key, False)
        status_txt = "[green]CONFIGURED[/green]" if is_ready else "[red]KEY MISSING[/red]"
        table.add_row(
            p.name,
            p.default_model,
            f"${p.api_key_env_var}",
            status_txt,
        )

    console.print(table)
    console.print("\n[dim]All requests dispatched through Cloud Bridges are scrubbed by Torque before transit.[/dim]")


@cli.command("gui")
def gui_command(
    gateway_url: str = typer.Option("http://127.0.0.1:8002", "--gateway", "-g", help="Target Loom Gateway URL")
):
    """Launch the Loom Fabric Native Desktop Control Center GUI."""
    from loom.gui import LoomFabricGUI
    render_cluster_banner()
    console.print(f"[bold green]Launching Loom Fabric Desktop GUI connecting to {gateway_url}...[/bold green]")
    app = LoomFabricGUI(gateway_url=gateway_url)
    app.mainloop()


@cli.command("run")
def run_command(
    model: str = typer.Argument("qwen2.5:32b", help="Model preset ID to chat with"),
    gateway: str = typer.Option("http://127.0.0.1:8002", "--gateway", "-g", help="Target Gateway URL"),
):
    """Interactive streaming chat with real-time token output and progress telemetry."""
    import httpx
    import json
    import time
    render_cluster_banner()
    preset = ModelRegistry.get_model(model)
    display_title = preset.display_name if preset else model
    console.print(f"[bold magenta]Connected to Loom Fabric for '[/bold magenta][bold white]{display_title}[/bold white][bold magenta]'[/bold magenta]")
    console.print(f"[dim]Gateway Target: {gateway} | Type 'exit', 'quit', or ':q' to leave[/dim]\n")

    target_url = f"{gateway.rstrip('/')}/v1/chat/completions"
    history = []

    while True:
        try:
            prompt = console.input("[bold magenta]You ❯ [/bold magenta]").strip()
            if not prompt:
                continue
            if prompt.lower() in ["exit", "quit", ":q"]:
                console.print("[bold red]Exiting Loom session.[/bold red]")
                break

            history.append({"role": "user", "content": prompt})

            payload = {
                "model": model,
                "messages": history,
                "stream": True,
            }

            console.print(f"[bold white]{display_title}[/bold white] [bold magenta]❯ [/bold magenta]", end="")

            assistant_reply = []
            start_time = time.time()
            token_count = 0

            with httpx.Client(timeout=180.0) as client:
                with client.stream("POST", target_url, json=payload) as response:
                    route_hdr = response.headers.get("x-torque-route", "Local")
                    scrub_hdr = response.headers.get("x-torque-scrubbed", "false")

                    for chunk in response.iter_lines():
                        if not chunk or not chunk.startswith("data:"):
                            continue
                        if chunk.strip() == "data: [DONE]":
                            break

                        try:
                            data = json.loads(chunk[5:].strip())
                            delta = data["choices"][0].get("delta", {}).get("content", "")
                            if delta:
                                token_count += 1
                                assistant_reply.append(delta)
                                sys.stdout.write(delta)
                                sys.stdout.flush()
                        except Exception:
                            continue

            full_text = "".join(assistant_reply)
            history.append({"role": "assistant", "content": full_text})

            elapsed = max(0.001, time.time() - start_time)
            tps = token_count / elapsed
            console.print(f"\n[dim magenta]── ({token_count} tokens | {tps:.1f} tokens/sec | Route: {route_hdr} | Scrubbed: {scrub_hdr}) ──[/dim magenta]\n")

        except KeyboardInterrupt:
            console.print("\n[bold red]Interrupted.[/bold red]")
            break
        except Exception as e:
            console.print(f"\n[bold red]Connection error: {e}[/bold red]")
            console.print("[dim yellow]Ensure Loom Fabric Gateway is active on port 8002.[/dim yellow]\n")


if __name__ == "__main__":
    cli()
