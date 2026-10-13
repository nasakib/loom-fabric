"""
Loom Fabric CLI Entrypoint (`loom` — `agy`-style ergonomics for Windows, macOS, and Linux).

Commands & Flags:
- `loom`                        : Ensures background services are running (0 terminals) and opens Loom Fabric Commander GUI.
- `loom -p "prompt"`            : Headless streaming prompt execution (just like `agy -p "..."`), auto-starting services if needed.
- `loom start [--both]`         : Sanitizes ports and starts all services silently in the background (zero terminal windows).
- `loom stop [--both]`          : Stops all managed services and sanitizes ports on this machine (or both machines).
- `loom restart [--both]`       : Sanitizes and restarts all services on this machine (or both machines).
- `loom status`                 : Displays live TCP port status across both 192.168.99.1 and 192.168.99.2.
- `loom run [model]`            : Interactive terminal streaming chat session.
- `loom gui`                    : Launches the native cross-platform GUI.
- `loom probe`                  : Hardware and Ray cluster diagnostics.
- `loom shard <model>`          : Mathematical layer allocation calculator.
- `loom models`                 : Lists registered architectural presets.
- `loom serve`                  : Starts the FastAPI OpenAI-compatible gateway in foreground.
- `loom triage <prompt>`        : Simulates dynamic compute triage and model delegation.
- `loom recommend`              : Hardware-matched model benchmark recommendations.
- `loom pull <model>`           : Downloads a model via Ollama.
- `loom cloud`                  : Audits configured zero-trust Cloud LLM bridges.
"""

from pathlib import Path
import json
import sys
import time
from typing import Optional
import typer
import uvicorn

from loom.cli.formatters import (
    render_cluster_banner,
    render_hardware_table,
    render_sharding_table,
    console,
)
from loom.stitch.profiler import HardwareProfiler
from loom.stitch.allocator import LayerAllocator
from loom.models.registry import ModelRegistry
from loom.config import get_settings

cli = typer.Typer(
    help="Loom Fabric: Sovereign Distributed AI Compute Fabric & Zero-Terminal Manager",
    invoke_without_command=True,
    no_args_is_help=False,
)


def _stream_single_prompt(prompt: str, model: str = "auto", gateway: str = "http://127.0.0.1:8002") -> None:
    """Executes a single prompt (`loom -p "..."`), auto-starting background services if needed."""
    import httpx
    from loom.gui import CrossPlatformClusterController

    ctrl = CrossPlatformClusterController(log_callback=lambda m: None)
    if not ctrl.is_port_open("127.0.0.1", 8002):
        console.print("[dim yellow]⚡ Auto-starting Loom Fabric background services (zero terminals)...[/dim yellow]")
        ctrl.ensure_local_services_alive()
        for _ in range(14):
            if ctrl.is_port_open("127.0.0.1", 8002):
                break
            time.sleep(0.5)

    target_url = f"{gateway.rstrip('/')}/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True,
    }

    start_time = time.time()
    token_count = 0
    route_hdr = "Local"
    scrub_hdr = "false"
    selected_model = model

    try:
        with httpx.Client(timeout=180.0) as client:
            with client.stream("POST", target_url, json=payload) as response:
                route_hdr = response.headers.get("x-torque-route", "Local")
                scrub_hdr = response.headers.get("x-torque-scrubbed", "false")
                selected_model = response.headers.get("x-torque-model-selected", model)

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
                            sys.stdout.write(delta)
                            sys.stdout.flush()
                    except Exception:
                        continue

        elapsed = max(0.001, time.time() - start_time)
        tps = token_count / elapsed
        console.print(
            f"\n[dim magenta]── ({token_count} tokens | {tps:.1f} tok/s | Model: {selected_model} | Route: {route_hdr} | Scrubbed: {scrub_hdr}) ──[/dim magenta]"
        )
    except Exception as e:
        console.print(f"\n[bold red]Error communicating with Loom Gateway ({target_url}): {e}[/bold red]")
        raise typer.Exit(1)


@cli.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    prompt: Optional[str] = typer.Option(None, "--prompt", "-p", help="Execute a prompt directly (like `agy -p \"...\"`)"),
    model: str = typer.Option("auto", "--model", "-m", help="Target model for -p prompt (default: auto)"),
    gateway: str = typer.Option("http://127.0.0.1:8002", "--gateway", "-g", help="Loom Gateway URL"),
):
    """Default entrypoint: runs `-p "prompt"` if provided, or launches the All-in-One GUI if no subcommand is given."""
    if prompt is not None:
        _stream_single_prompt(prompt=prompt, model=model, gateway=gateway)
        raise typer.Exit(0)

    if ctx.invoked_subcommand is None:
        from loom.gui import LoomFabricCommandCenter
        app = LoomFabricCommandCenter(gateway_url=gateway)
        app.mainloop()


@cli.command("start")
def start_command(
    both: bool = typer.Option(False, "--both", "-b", help="Start services on BOTH machines (192.168.99.1 & 192.168.99.2)"),
):
    """Start all Loom Fabric & Shuttle services silently in the background (zero terminal windows)."""
    from loom.gui import CrossPlatformClusterController
    render_cluster_banner()
    ctrl = CrossPlatformClusterController(log_callback=lambda msg: console.print(f"[cyan]{msg}[/cyan]"))
    ctrl.ensure_local_services_alive()
    console.print("[bold green]✔ Local services running silently in background (zero terminal windows).[/bold green]")
    if both:
        ctrl.trigger_peer_action("restart")


@cli.command("stop")
def stop_command(
    both: bool = typer.Option(False, "--both", "-b", help="Stop and sanitize ports on BOTH machines"),
):
    """Stop all services and sanitize ports (8000, 8002, 8080, 5555, 18789)."""
    from loom.gui import CrossPlatformClusterController, MANAGED_PORTS
    render_cluster_banner()
    ctrl = CrossPlatformClusterController(log_callback=lambda msg: console.print(f"[yellow]{msg}[/yellow]"))
    if both:
        ctrl.trigger_peer_action("stop")
    ctrl.sanitize_local_ports(ports=MANAGED_PORTS)
    console.print("[bold green]✔ Ports sanitized and services stopped.[/bold green]")


@cli.command("restart")
def restart_command(
    both: bool = typer.Option(True, "--both/--local-only", help="Restart services across both machines by default"),
):
    """Sanitize stale ports and cleanly restart all background services (zero terminal windows)."""
    from loom.gui import CrossPlatformClusterController
    render_cluster_banner()
    ctrl = CrossPlatformClusterController(log_callback=lambda msg: console.print(f"[magenta]{msg}[/magenta]"))
    ctrl.start_local_all(separate_gateway_window=False)
    if both:
        ctrl.trigger_peer_action("restart")
    console.print("[bold green]✔ Cluster restart complete (100% background daemons, zero terminal clutter).[/bold green]")


@cli.command("status")
def status_command():
    """Display live service & TCP port health across both 192.168.99.1 (skyTech) and 192.168.99.2 (Ryzen Head)."""
    from rich.table import Table
    from loom.gui import CrossPlatformClusterController
    render_cluster_banner()
    ctrl = CrossPlatformClusterController()

    table = Table(title="[bold magenta]Loom Fabric Dual-Machine Cluster Port Matrix[/bold magenta]")
    table.add_column("Node", style="bold white", width=26)
    table.add_column("Service", style="cyan", width=22)
    table.add_column("Endpoint", style="dim white", width=22)
    table.add_column("State", justify="center", width=14)

    nodes = [
        ("skyTech Worker (192.168.99.1)", "192.168.99.1", [(8002, "Loom Gateway"), (5555, "The Shuttle PWA"), (11434, "Ollama Engine"), (18789, "OpenClaw Bot")]),
        ("Ryzen 7 Head (192.168.99.2)", "192.168.99.2", [(8002, "Loom Gateway"), (5555, "The Shuttle PWA"), (6379, "Ray GCS Redis"), (8265, "Ray Dashboard"), (11434, "Ollama Engine"), (18789, "OpenClaw GW")]),
    ]

    for node_label, ip, ports in nodes:
        for port, svc_name in ports:
            probe_host = "127.0.0.1" if ip == ctrl.self_ip else ip
            is_up = ctrl.is_port_open(probe_host, port, timeout=0.6)
            state_str = "[bold green]● ONLINE[/bold green]" if is_up else "[bold red]○ OFFLINE[/bold red]"
            table.add_row(node_label, svc_name, f"{ip}:{port}", state_str)

    console.print(table)


@cli.command("platforms")
def platforms_command():
    """List all cross-platform Loom Fabric editions (Windows, macOS, Linux, React Native Universal, and ClothOS RISC-V)."""
    from rich.table import Table
    render_cluster_banner()
    table = Table(title="[bold magenta]Loom Fabric All-in-One Cross-Platform & Sovereign Editions[/bold magenta]")
    table.add_column("Edition / Target", style="bold white", width=26)
    table.add_column("Architecture / Runtime", style="cyan", width=28)
    table.add_column("Enclave & Compute Backend", style="green", width=30)
    table.add_column("Entrypoint / Path", style="yellow", width=30)

    rows = [
        ("Windows 10/11 Native", "x86_64 / ARM64 (pythonw)", "CUDA 12 + Vulkan 1.3 + Win32 Job", "Start-Loom-GUI.bat / `loom`"),
        ("macOS Native (.app)", "Apple Silicon M-Series & Intel", "Metal Unified Memory + Sandbox", "scripts/install_macos.sh"),
        ("Linux / WSL2 Desktop", "x86_64 / aarch64 (.desktop)", "CUDA / ROCm / Vulkan + cgroups", "scripts/install_linux.sh"),
        ("React Native Universal", "iOS, Android, Windows, macOS, Web", "Expo + React Native Mesh Client", "apps/loom-react-native/App.tsx"),
        ("ClothOS Special Edition", "RISC-V (rv64gc + RVV 1.0 512b)", "Hardware PMP CSR (pmpcfg0=0x9B)", "platforms/clothos-riscv/ (`loom clothos`)"),
        ("The Shuttle PWA + Web", "Universal Browser / Mobile PWA", "SSE Token Stream + Torque Vault", "http://192.168.99.1:5555 & :8002"),
    ]
    for r in rows:
        table.add_row(*r)
    console.print(table)


@cli.command("clothos")
def clothos_command(
    prompt: Optional[str] = typer.Option(None, "--prompt", "-p", help="Execute prompt via ClothOS RISC-V RVV 1.0 + PMP Enclave"),
    model: str = typer.Option("qwen2.5:32b", "--model", "-m", help="Target model for RVV 1.0 layer sharding"),
):
    """ClothOS Special Edition (RISC-V RV64GC + RVV 1.0 Vector + Hardware PMP Zero-Trust Enclave)."""
    from rich.panel import Panel
    from rich.table import Table

    render_cluster_banner()
    profiler = HardwareProfiler()
    rv_state = profiler.probe_clothos_riscv_state()
    allocator = LayerAllocator(rv_state)
    preset = ModelRegistry.get_model(model) or ModelRegistry.get_model("qwen2.5:32b")
    plan = allocator.calculate_plan(preset.to_architecture_profile(context_length=16384), allow_cpu_spill=True)

    table = Table(title="[bold magenta]ClothOS RISC-V (RV64GC + RVV 1.0) Special Edition // Hardware & PMP Enclave[/bold magenta]")
    table.add_column("Subsystem", style="bold white", width=26)
    table.add_column("Specification / Telemetry", style="bright_green", width=58)

    table.add_row("Target ISA String", "rv64imafdcv_zicsr_zifencei_zfh_zba_zbb_zbc_zbs")
    table.add_row("Processor Topology", rv_state.host.cpu_model)
    table.add_row("Vector Matrix Unit", "RVV 1.0 (VLEN=512-bit, DLEN=256-bit, 64 INT8/Q8_0 lanes/Hart)")
    table.add_row("Torque Hardware Enclave", "RISC-V PMP Region #0 @ 0x80400000 (4 MiB NAPOT Locked, CSR pmpcfg0=0x9B)")
    rvv_layers = preset.total_layers - plan.spilled_layer_count
    table.add_row("Zero-OOM RVV Layer Split", f"{rvv_layers}/{preset.total_layers} layers on RVV 1.0 Silicon ({plan.render_cli_argument_string()})")
    table.add_row("Rust Source Package", "platforms/clothos-riscv/ (Cargo target: riscv64gc-unknown-clothos-elf)")
    console.print(table)

    if prompt:
        console.print(Panel(f"[bold cyan]Dispatching via ClothOS PMP Enclave & Loom Gateway:[/bold cyan]\n{prompt}", border_style="magenta"))
        _stream_single_prompt(prompt=prompt, model="auto")


@cli.command("probe")
def probe_command(
    cluster: bool = typer.Option(False, "--cluster", "-c", help="Query live Ray cluster state if available"),
    riscv: bool = typer.Option(False, "--riscv", help="Inspect ClothOS RISC-V (RV64GC + RVV 1.0) silicon profile"),
):
    """Diagnose physical accelerators, VRAM margins, and cluster nodes."""
    render_cluster_banner()
    with console.status("[bold green]Probing physical accelerators & memory topologies..."):
        profiler = HardwareProfiler()
        state = profiler.probe_clothos_riscv_state() if riscv else profiler.probe_cluster_state()

    console.print(render_hardware_table(state.model_dump()))
    console.print()
    console.print(f"[bold cyan]Custom Ray Resource Map:[/bold cyan] {state.ray_custom_resources}")


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
    port: int = typer.Option(8002, "--port", "-p", help="Gateway HTTP port"),
    reload: bool = typer.Option(False, "--reload", help="Enable autoreload"),
):
    """Start the OpenAI-compatible FastAPI gateway in the foreground."""
    render_cluster_banner()
    console.print(f"[bold green]Starting Loom Fabric Gateway on http://{host}:{port}[/bold green]")
    console.print("[dim white]Available endpoints: /v1/chat/completions (SSE streaming), /v1/models, /health[/dim white]")
    uvicorn.run("loom.gateway.app:app", host=host, port=port, reload=reload)


@cli.command("triage")
def triage_command(
    prompt: str = typer.Argument(..., help="Prompt string or task description to evaluate"),
    force_local: bool = typer.Option(False, "--local", "-l", help="Force local sovereign execution"),
    max_tokens: int = typer.Option(4096, "--max-tokens", "-m", help="Anticipated max generation tokens"),
):
    """Simulate Loom's dynamic compute triage and model delegation for a prompt."""
    from rich.panel import Panel
    from rich.table import Table
    from loom.torque.router import TorqueRouter
    from loom.types import PromptPayload, ChatMessageDTO

    render_cluster_banner()
    router = TorqueRouter()
    payload = PromptPayload(
        model="auto",
        messages=[ChatMessageDTO(role="user", content=prompt)],
        max_tokens=max_tokens,
        force_local=force_local,
    )

    decision = router.route(payload)
    est_duration = router.estimate_compute_duration_seconds(payload)

    table = Table(title="[bold magenta]Loom Dynamic Compute Triage & Delegation[/bold magenta]")
    table.add_column("Property", style="bold white", width=24)
    table.add_column("Decision / Evaluation", style="cyan", width=50)

    table.add_row("Execution Tier", f"[bold yellow]{decision.tier.value}[/bold yellow]")
    table.add_row("Dispatched Model", f"[bold green]{decision.model_name}[/bold green]")
    table.add_row("Target Endpoint", decision.target_endpoint)
    table.add_row("Zero-Trust Scrubbed", "[red]Yes (Cloud Arbitrage)[/red]" if decision.is_scrubbed else "[green]No (Sovereign Local)[/green]")
    table.add_row("Estimated Compute Time", f"{est_duration:.2f} seconds")
    table.add_row("Routing Rationale", f"[dim white]{decision.reasoning}[/dim white]")

    console.print(table)
    console.print()
    console.print(Panel(f"[dim]Input Prompt:[/dim]\n{prompt}", title="[magenta]Inspected Payload[/magenta]", border_style="purple"))


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
    app = LoomFabricGUI(gateway_url=gateway_url)
    app.mainloop()


@cli.command("run")
def run_command(
    model: str = typer.Argument("auto", help="Model preset ID to chat with (default: auto)"),
    gateway: str = typer.Option("http://127.0.0.1:8002", "--gateway", "-g", help="Target Gateway URL"),
):
    """Interactive streaming chat with real-time token output and auto-healing background services."""
    import httpx
    from loom.gui import CrossPlatformClusterController

    render_cluster_banner()
    ctrl = CrossPlatformClusterController(log_callback=lambda m: None)
    if not ctrl.is_port_open("127.0.0.1", 8002):
        console.print("[dim yellow]⚡ Auto-starting Loom Fabric background services...[/dim yellow]")
        ctrl.ensure_local_services_alive()
        for _ in range(12):
            if ctrl.is_port_open("127.0.0.1", 8002):
                break
            time.sleep(0.5)

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
            console.print("[dim yellow]Auto-healing Loom Fabric Gateway on port 8002...[/dim yellow]\n")
            ctrl.ensure_local_services_alive()


@cli.command("synergy")
def synergy_command():
    """Execute a ClothOS + Moltbook R&D Wisdom Bridge cycle, render live DAG telemetry, and sync .agent/STATUS.md."""
    from rich.panel import Panel
    from rich.table import Table
    from loom.clothos.kernel import ClothOSKernel

    render_cluster_banner()
    kernel = ClothOSKernel()
    status_path = kernel.sync_agent_status_markdown(probe_network=False)
    snap = kernel.snapshot(probe_network=False)

    console.print(
        Panel(
            f"[bold green]DAG Plan ID:[/bold green] {snap.latest_route.dag.plan_id}  |  "
            f"[bold magenta]QCT Route:[/bold magenta] {snap.latest_route.tier} ({snap.latest_route.target_model})  |  "
            f"[bold cyan]Entropy:[/bold cyan] {snap.latest_route.qct_entropy_score}  |  "
            f"[bold yellow]Critical Path:[/bold yellow] {snap.latest_route.dag.critical_path_ms} ms\n"
            f"[bold white]{snap.latest_route.dag.ascii_topology}[/bold white]",
            title="[bold green]ClothOS Live Directed Acyclic Graph (DAG) Telemetry[/bold green]",
            border_style="green",
        )
    )

    h_table = Table(
        title=f"[bold magenta]Moltbook R&D Wisdom Bridge ({snap.registration.agent_did})[/bold magenta]",
        border_style="magenta",
    )
    h_table.add_column("Hypothesis ID", style="bold cyan", width=15)
    h_table.add_column("Submolt", style="green", width=23)
    h_table.add_column("Architectural Pattern", style="bold white", width=44)
    h_table.add_column("Status", style="bold green", width=12)

    for h in snap.active_hypotheses:
        h_table.add_row(h.hypothesis_id, h.submolt, h.statement, f"● {h.sandbox_status}")

    console.print(h_table)
    console.print(f"[dim green]✔ Synced ClothOS & Moltbook R&D status to {status_path}[/dim green]")


app = cli

if __name__ == "__main__":
    cli()

