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


@cli.command("run")
def run_command(
    model: str = typer.Argument("qwen2.5:32b", help="Model preset ID to chat with"),
):
    """Interactive streaming chat with automatic sharding and cluster routing."""
    import httpx
    render_cluster_banner()
    preset = ModelRegistry.get_model(model)
    display_title = preset.display_name if preset else model
    console.print(f"[bold cyan]Connecting to Loom Fabric runtime for '{display_title}'...[/bold cyan]")

    target_url = "http://127.0.0.1:8000/v1/chat/completions"
    history = []

    console.print("[bold green]Chat initialized! Type 'exit' or 'quit' to end session.[/bold green]\n")
    while True:
        try:
            prompt = console.input("[bold yellow]You > [/bold yellow]").strip()
            if not prompt:
                continue
            if prompt.lower() in ["exit", "quit", ":q"]:
                console.print("[bold red]Exiting session.[/bold red]")
                break

            history.append({"role": "user", "content": prompt})

            payload = {
                "model": model,
                "messages": history,
                "stream": False,
            }

            console.print(f"[bold cyan]{display_title} > [/bold cyan]", end="")
            with httpx.Client(timeout=300.0) as client:
                res = client.post(target_url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    reply = data["choices"][0]["message"]["content"]
                    console.print(reply)
                    history.append({"role": "assistant", "content": reply})
                else:
                    console.print(f"[bold red]Error ({res.status_code}): {res.text}[/bold red]")
            console.print()
        except KeyboardInterrupt:
            console.print("\n[bold red]Interrupted.[/bold red]")
            break
        except Exception as e:
            console.print(f"\n[bold red]Connection error: {e}[/bold red]")
            console.print("[dim yellow]Ensure 'loom serve' is running on port 8000.[/dim yellow]")


if __name__ == "__main__":
    cli()
