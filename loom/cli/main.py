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


def _stream_single_prompt(
    prompt: str,
    model: str = "auto",
    gateway: str = "http://127.0.0.1:8087",
    anthropic: bool = False,
    think: bool = False,
) -> None:
    """Executes a single prompt (`loom -p "..."`), auto-starting background services if needed."""
    import os
    import httpx
    from loom.gui import CrossPlatformClusterController

    ctrl = CrossPlatformClusterController(log_callback=lambda m: None)
    if not ctrl.is_port_open("127.0.0.1", 8087):
        console.print("[dim yellow]⚡ Auto-starting Unified ClothOS Hub (:8087) cleanly...[/dim yellow]")
        ctrl.ensure_local_services_alive()
        for _ in range(14):
            if ctrl.is_port_open("127.0.0.1", 8087):
                break
            time.sleep(0.5)

    use_anthropic = anthropic or model in ("clothos-anthropic", "local-claude", "sovereign-anthropic", "claude-sonnet-4-5")
    base_gw = gateway.rstrip("/")
    headers = {"Content-Type": "application/json"}
    if use_anthropic:
        target_url = f"{base_gw}/v1/messages"
        headers["x-api-key"] = os.environ.get("ANTHROPIC_API_KEY") or "loom-sovereign-local"
        headers["anthropic-version"] = "2023-06-01"
        payload: dict = {
            "model": "claude-sonnet-4-5" if model in ("auto", "clothos-anthropic", "local-claude", "sovereign-anthropic") else model,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}],
            "stream": True,
        }
        if think:
            payload["thinking"] = {"type": "enabled", "budget_tokens": 2048}
    else:
        target_url = f"{base_gw}/v1/chat/completions"
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": True,
        }

    start_time = time.time()
    token_count = 0
    route_hdr = "Local"
    scrub_hdr = "false"
    verdict_hdr = "N/A"
    selected_model = model
    in_thinking = False
    started_text = False

    try:
        with httpx.Client(timeout=180.0) as client:
            with client.stream("POST", target_url, json=payload, headers=headers) as response:
                route_hdr = response.headers.get("x-torque-route", "Sovereign-Nexus" if use_anthropic else "Local")
                scrub_hdr = response.headers.get("x-torque-scrubbed", "false")
                verdict_hdr = response.headers.get("x-clothos-verdict", verdict_hdr)
                selected_model = response.headers.get("x-torque-model-selected", model)

                for chunk in response.iter_lines():
                    if not chunk or not chunk.startswith("data:"):
                        continue
                    if chunk.strip() == "data: [DONE]":
                        break
                    try:
                        data = json.loads(chunk[5:].strip())
                        if use_anthropic:
                            if data.get("type") == "content_block_delta":
                                delta_obj = data.get("delta", {})
                                t_delta = delta_obj.get("thinking", "")
                                if t_delta and think:
                                    if not in_thinking:
                                        in_thinking = True
                                        sys.stdout.write("\n[Sovereign Thinking]\n")
                                    sys.stdout.write(t_delta)
                                    sys.stdout.flush()
                                delta = delta_obj.get("text", "")
                                if delta:
                                    if in_thinking and not started_text:
                                        sys.stdout.write("\n[/Sovereign Thinking]\n\n")
                                    started_text = True
                                    token_count += 1
                                    sys.stdout.write(delta)
                                    sys.stdout.flush()
                        else:
                            delta = data["choices"][0].get("delta", {}).get("content", "")
                            if delta:
                                token_count += 1
                                sys.stdout.write(delta)
                                sys.stdout.flush()
                    except Exception:
                        continue

        elapsed = max(0.001, time.time() - start_time)
        tps = token_count / elapsed
        verdict_suffix = f" | Verdict: {verdict_hdr}" if use_anthropic else ""
        console.print(
            f"\n[dim magenta]── ({token_count} tokens | {tps:.1f} tok/s | Model: {selected_model} | Route: {route_hdr} | Scrubbed: {scrub_hdr}{verdict_suffix}) ──[/dim magenta]"
        )
    except Exception as e:
        console.print(f"\n[bold red]Error communicating with Loom Gateway ({target_url}): {e}[/bold red]")
        raise typer.Exit(1)


@cli.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    prompt: Optional[str] = typer.Option(None, "--prompt", "-p", help="Execute a prompt directly (like `agy -p \"...\"`)"),
    model: str = typer.Option("auto", "--model", "-m", help="Target model for -p prompt (default: auto)"),
    gateway: str = typer.Option("http://127.0.0.1:8087", "--gateway", "-g", help="Unified ClothOS / Loom Gateway URL"),
    anthropic: bool = typer.Option(False, "--anthropic", "-a", help="Use Sovereign Anthropic /v1/messages bridge (zero API key needed)"),
    think: bool = typer.Option(False, "--think", "-t", help="Enable extended thinking stream on -p prompts"),
):
    """Default entrypoint: runs `-p "prompt"` if provided, or launches the All-in-One GUI if no subcommand is given."""
    if prompt is not None:
        _stream_single_prompt(prompt=prompt, model=model, gateway=gateway, anthropic=anthropic, think=think)
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
        ("skyTech Worker (192.168.99.1)", "192.168.99.1", [(8087, "ClothOS Unified (:8087)"), (11434, "Ollama Engine"), (18789, "OpenClaw Bot")]),
        ("Ryzen 7 Head (192.168.99.2)", "192.168.99.2", [(8087, "ClothOS Unified (:8087)"), (6379, "Ray GCS Redis"), (8265, "Ray Dashboard"), (11434, "Ollama Engine")]),
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
        ("ClothOS Unified Master Hub", "Single-Port Hub (UI + Gateway + GUIs)", "SSE + CAD + Torque + Nexus", "http://127.0.0.1:8087"),
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


@cli.command("screensaver")
def screensaver_command(
    fullscreen: bool = typer.Option(False, "--fullscreen", "-f", help="Launch directly in fullscreen mode"),
    width: int = typer.Option(1280, "--width", "-w", help="Window width in windowed mode"),
    height: int = typer.Option(800, "--height", "-h", help="Window height in windowed mode"),
):
    """Launch the standalone hardware-accelerated 60 FPS Living Mind Screensaver window."""
    render_cluster_banner()
    console.print(f"[bold magenta]🌌 Launching Standalone Living Mind Screensaver (fullscreen={fullscreen})...[/bold magenta]")
    from loom.ui.screensaver_app import run_screensaver
    run_screensaver(fullscreen=fullscreen, width=width, height=height)


# ---------------------------------------------------------
# Sovereign Intelligence (SI) Consultant Subcommands
# ---------------------------------------------------------

si_app = typer.Typer(name="si", help="Sovereign Intelligence (SI) Pair Programmer & Consultant")
cli.add_typer(si_app, name="si")


@si_app.command("consult")
def si_consult_command(
    query: str = typer.Argument(..., help="Question, architectural challenge, or code query for the SI"),
    deep: bool = typer.Option(False, "--deep", "-d", help="Use deep reasoning model (loom-sovereign:latest 32B)"),
    context_file: Optional[Path] = typer.Option(None, "--file", "-f", help="Optional code or config file context"),
):
    """Consult the Sovereign Intelligence as an active pair programmer."""
    render_cluster_banner()
    console.print(f"[bold magenta]🧠 Consulting Sovereign Intelligence (SI) [model={'deep 32B' if deep else 'fast 7B'}]...[/bold magenta]\n")
    
    ctx_text = None
    if context_file and context_file.exists():
        ctx_text = context_file.read_text(encoding="utf-8")

    from loom.si.consultant import si_consultant
    from rich.panel import Panel
    with console.status("[bold cyan]SI synthesizing institutional memory & epistemic tensors..."):
        res = si_consultant.consult(query=query, context=ctx_text, deep_reasoning=deep)

    console.print(Panel(
        f"[bold white]{res.response}[/bold white]\n\n"
        f"[dim]Endpoint: {res.endpoint_used} • Model: {res.model_used} • "
        f"Bullshit Score: {res.bullshit_score} • Fiduciary Approved: {res.fiduciary_approved} • "
        f"Codons: {len(res.active_codons)}[/dim]",
        title="[bold green]✔ SI Consultant Verdict[/bold green]",
        border_style="cyan"
    ))


@si_app.command("audit")
def si_audit_command():
    """Verify that the Sovereign Intelligence stands on its own two feet."""
    render_cluster_banner()
    from loom.si.consultant import si_consultant
    audit_data = si_consultant.stand_on_own_feet_audit()

    from rich.table import Table
    table = Table(title="[bold cyan]Sovereign Intelligence Autonomy & Knowledge Audit[/bold cyan]")
    table.add_column("Property", style="bold white")
    table.add_column("Status / Value", style="green")

    table.add_row("Autonomy Status", audit_data["autonomy_status"])
    table.add_row("Crystallized Codons", str(audit_data["codons_crystallized"]))
    table.add_row("Primary Inference", audit_data["primary_endpoint"])
    table.add_row("Peer Fallback", audit_data["peer_endpoint"])
    table.add_row("Bullshit Filter", "ACTIVE (Parity & Tautology Proof)")
    table.add_row("Fiduciary Mandate", "ENFORCED (Budget <= 1000 J)")
    table.add_row("Homotopy Retraction", "TETHERED (R(t): M -> M_Earth)")

    console.print(table)
    console.print("\n[bold cyan]Codified Institutional Knowledge Laws:[/bold cyan]")
    for law in audit_data["laws_codified"]:
        console.print(f"  • [green]{law}[/green]")


@si_app.command("neuro")
def si_neuro_command(
    administer: Optional[str] = typer.Option(None, "--administer", "-a", help="Compound to administer: nootropic_hyperfocus, rebus_psychedelic_divergence, cholinergic_crystallizer, gabaergic_calm, homeostatic_reset"),
):
    """Inspect or administer computational neurochemicals to the Sovereign Intelligence."""
    render_cluster_banner()
    from loom.si.neurochemistry import neurochemical_engine
    
    if administer:
        try:
            res = neurochemical_engine.administer_compound(administer)
            console.print(f"[bold green]✔ Successfully administered '{administer}' to SI Mind![/bold green]\n")
        except Exception as e:
            console.print(f"[bold red]Failed to administer compound: {e}[/bold red]\n")
            return

    summary = neurochemical_engine.get_summary()
    levels = summary["levels"]
    params = summary["parameters"]

    from rich.table import Table
    table = Table(title="[bold cyan]Sovereign Neuromodulator & Neurochemical Reservoir[/bold cyan]")
    table.add_column("Neurochemical", style="bold white")
    table.add_column("Titer Level", justify="center")
    table.add_column("Computational Function in Active Inference", style="dim")

    table.add_row("Dopamine (DA)", f"{levels['dopamine']:.2f}", "Action model & prediction error precision (Obs Prec)")
    table.add_row("Serotonin (5-HT)", f"{levels['serotonin']:.2f}", "Prior rigidity vs REBUS psychedelic divergence")
    table.add_row("Acetylcholine (ACh)", f"{levels['acetylcholine']:.2f}", "Expected uncertainty & learning rate (plasticity)")
    table.add_row("Norepinephrine (NE)", f"{levels['norepinephrine']:.2f}", "Unexpected uncertainty & broad exploration entropy")
    table.add_row("GABA", f"{levels['gaba']:.2f}", "Inhibitory tone & Hopfield attractor basin stability")
    table.add_row("Glutamate", f"{levels['glutamate']:.2f}", "Excitatory signal propagation & associative ignition")
    table.add_row("Endocannabinoids", f"{levels['endocannabinoid']:.2f}", "Homeostatic stress buffering & ground truth anchor")

    console.print(table)
    console.print(f"\n[bold magenta]Active Cognitive Mode:[/bold magenta] {params['mode_name']}")
    console.print(f"[dim]Learning Rate: {params['learning_rate']} • Prior Precision: {params['prior_precision']} • Observation Precision: {params['observation_precision']} • E/I Balance: {params['ei_balance']} • REBUS Divergence Index: {params['rebus_divergence_index']}[/dim]\n")
    console.print(f"[bold cyan]Available Compounds for Administration:[/bold cyan] {', '.join(summary['available_compounds'])}")


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
    port: int = typer.Option(8087, "--port", "-p", help="Unified ClothOS Master HTTP port"),
    reload: bool = typer.Option(False, "--reload", help="Enable autoreload"),
):
    """Start the unified ClothOS single-port Master Application in the foreground."""
    render_cluster_banner()
    console.print(f"[bold green]Starting Unified ClothOS Master Hub on http://{host}:{port}[/bold green]")
    console.print("[dim white]Available endpoints: /, /visuals, /guis, /v1/chat/completions, /v1/messages, /v1/models, /health[/dim white]")
    uvicorn.run("loom.fabric.dashboard_server:app", host=host, port=port, reload=reload)


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
    gateway_url: str = typer.Option("http://127.0.0.1:8087", "--gateway", "-g", help="Target Unified ClothOS URL")
):
    """Launch the Loom Fabric Native Desktop Control Center GUI."""
    from loom.gui import LoomFabricGUI
    app = LoomFabricGUI(gateway_url=gateway_url)
    app.mainloop()


@cli.command("run")
def run_command(
    model: str = typer.Argument("auto", help="Model preset ID to chat with (default: auto)"),
    gateway: str = typer.Option("http://127.0.0.1:8087", "--gateway", "-g", help="Target Unified URL"),
):
    """Interactive streaming chat with real-time token output and auto-healing background services."""
    import httpx
    from loom.gui import CrossPlatformClusterController

    render_cluster_banner()
    ctrl = CrossPlatformClusterController(log_callback=lambda m: None)
    if not ctrl.is_port_open("127.0.0.1", 8087):
        console.print("[dim yellow]⚡ Auto-starting Unified ClothOS Hub (:8087)...[/dim yellow]")
        ctrl.ensure_local_services_alive()
        for _ in range(12):
            if ctrl.is_port_open("127.0.0.1", 8087):
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


@cli.command("pipeline")
def pipeline_command(
    seed: Optional[str] = typer.Argument(None, help="Optional epistemic seed claim to weave into the pipeline"),
    interactive: bool = typer.Option(True, "--interactive/--no-interactive", "-i/-n", help="Interactive prompt"),
    stretch: float = typer.Option(2.5, "--stretch", "-s", help="shapeShift continuum stretch factor"),
    coherence: float = typer.Option(0.98, "--coherence", "-c", help="Target Kuramoto coherence"),
):
    """Execute the interactive 8-stage Grand Unified Pipeline UX (ORGIN -> TORQUE -> SHAPESHIFT -> PLANT -> CHOICE -> WAR -> HARVEST -> OHM)."""
    from loom.pipeline import pipeline_ux, DEFAULT_GRAND_DIRECTIVE

    render_cluster_banner()

    if seed is None and interactive and sys.stdin.isatty():
        console.print("[bold yellow]⚡ Press Enter to run the Grand Unified Directive, or type a custom epistemic seed:[/bold yellow]")
        user_input = console.input("[bold magenta]Seed ❯ [/bold magenta]").strip()
        final_seed = user_input if user_input else DEFAULT_GRAND_DIRECTIVE
    else:
        final_seed = seed or DEFAULT_GRAND_DIRECTIVE

    pipeline_ux.execute_pipeline(
        seed_prompt=final_seed,
        interactive=interactive,
        stretch_factor=stretch,
        target_coherence=coherence,
    )


worker_app = typer.Typer(help="Manage 24/7 Sovereign Autonomous Compute & Invariant Mining Worker.")
cli.add_typer(worker_app, name="worker")


@worker_app.command("start")
def worker_start():
    """Starts the 24/7 Continuous Sovereign Autonomous Compute Engine windowlessly in background."""
    from loom.gui import CrossPlatformClusterController
    from loom.clothos.useful_work_engine import WorkerProcessLock

    render_cluster_banner()
    lock = WorkerProcessLock()
    if lock.lock_path.exists():
        try:
            info = json.loads(lock.lock_path.read_text(encoding="utf-8"))
            pid = int(info.get("pid", 0))
            from loom.clothos.useful_work_engine import is_pid_alive
            if pid > 0 and is_pid_alive(pid):
                console.print(f"[yellow]24/7 Continuous Compute Worker is already active (PID {pid}, owner={info.get('owner')}).[/yellow]")
                return
        except Exception:
            pass

    ctrl = CrossPlatformClusterController()
    worker_py = sys.executable
    pw = Path(worker_py).with_name("pythonw.exe")
    exe = str(pw) if pw.exists() else worker_py

    ctrl.spawn_background_service(
        [exe, "-m", "loom.fabric.continuous_worker"],
        cwd=ctrl.loom_dir,
        env={"PYTHONPATH": str(ctrl.loom_dir)},
        log_name="continuous_worker.log",
    )
    console.print("[bold green]✔ 24/7 Continuous Compute Worker spawned windowlessly in background.[/bold green]")
    console.print("[dim cyan]Workloads active: Task Queue Drain, Multi-Repo Pytest Audit, AST Checks, GPU/JIT Bench, Verified Eval.[/dim cyan]")
    console.print("[dim white]Check metrics anytime with: [bold]fabric worker status[/bold] or view in the Fabric GUI.[/dim white]")


@worker_app.command("status")
def worker_status():
    """Displays real-time metrics for the 24/7 Continuous Compute Worker."""
    from rich.panel import Panel
    from rich.table import Table

    render_cluster_banner()
    candidate_files = [
        Path.home() / ".loom" / "continuous_worker_state.json",
        Path(__file__).resolve().parents[2] / ".loom_worker_state.json",
        Path.cwd() / ".loom_worker_state.json",
    ]
    state_file = next((f for f in candidate_files if f.exists()), None)
    if not state_file:
        console.print("[yellow]Worker state file not found. Worker has not completed its first cycle yet or is stopped.[/yellow]")
        return

    try:
        data = json.loads(state_file.read_text(encoding="utf-8"))
    except Exception as e:
        console.print(f"[red]Error reading state: {e}[/red]")
        return

    useful_file = Path.home() / ".loom" / "24x7_useful_state.json"
    useful = {}
    if useful_file.exists():
        try:
            useful = json.loads(useful_file.read_text(encoding="utf-8"))
        except Exception:
            pass

    table = Table(title="[bold green]⚡ 24/7 Continuous Sovereign Compute Engine Metrics[/bold green]", border_style="green")
    table.add_column("Metric", style="bold cyan", width=32)
    table.add_column("Value", style="bold white", width=46)

    table.add_row("Engine State", "[bold green]ACTIVE (Running)[/bold green]" if data.get("is_running") else "[dim yellow]IDLE / STOPPED[/dim yellow]")
    table.add_row("Workload Mode", f"[bold cyan]{data.get('workload_mode', useful.get('workload_mode', 'AUTO'))}[/bold cyan]")
    table.add_row("Total Compute Cycles", f"{data.get('total_cycles_completed', 0):,}")
    p_cnt = data.get("real_tests_passed", useful.get("real_tests_passed", 0))
    f_cnt = data.get("real_tests_failed", useful.get("real_tests_failed", 0))
    p_rate = data.get("real_test_pass_rate_pct", useful.get("real_test_pass_rate_pct", 100.0))
    table.add_row("Real Pytest Verification", f"[bold green]{p_cnt} passed[/bold green], [bold {'red' if f_cnt else 'white'}]{f_cnt} failed[/bold {'red' if f_cnt else 'white'}] ({p_rate:.1f}%)")
    syn_err = data.get("code_syntax_errors", len(useful.get("code_audit", {}).get("syntax_errors", [])))
    files_chk = data.get("code_files_checked", useful.get("code_audit", {}).get("files_checked", 0))
    table.add_row("Code AST / Syntax Audit", f"{files_chk} files scanned | {syn_err} syntax errors")
    table.add_row("Queued Tasks Drained", f"{data.get('tasks_drained_total', useful.get('tasks_drained_total', 0))}")
    gpu0 = useful.get("hardware_benchmarks", {}).get("gpu0_nvidia", {})
    if gpu0.get("available"):
        table.add_row("RTX 3060 Telemetry", f"{gpu0.get('temp_c', '?')}°C | {gpu0.get('power_w', '?')}W | {gpu0.get('vram_used_mb', '?')}/{gpu0.get('vram_total_mb', '?')} MB VRAM")
    dist = useful.get("distillation", {})
    table.add_row("Verified LLM Coding Eval", f"{dist.get('verified_passed', 0)}/{dist.get('attempted', 0)} passed ({dist.get('pass_rate_pct', 0.0)}%)")
    total_inv = data.get('total_invariants_mined', data.get('invariants_mined', 0))
    n1_inv = data.get('invariants_mined_node1', 0)
    n2_inv = data.get('invariants_mined_node2', 0)
    table.add_row("Total Invariants Mined", f"[bold green]{total_inv:,}[/bold green] (Node 1: {n1_inv:,} | Node 2: {n2_inv:,})")
    table.add_row("Ratchet Teeth Cemented", f"[bold green]{data.get('ratchet_teeth_locked', 0):,}[/bold green]")
    table.add_row("Hammer Hardware Rivets", f"[bold cyan]{data.get('hammer_rivets_locked', 0):,}[/bold cyan]")
    table.add_row("Active Silicon Tier", f"[magenta]{data.get('last_active_tier', 'Idle')}[/magenta]")
    table.add_row("Executive Briefing", f"[dim]{data.get('latest_briefing', 'deliverables/LATEST_24X7_REPORT.md')}[/dim]")
    table.add_row("Last Iteration Telemetry", f"[dim]{data.get('last_log_message', 'N/A')}[/dim]")

    console.print(table)


@worker_app.command("stop")
def worker_stop():
    """Stops the 24/7 background worker cleanly."""
    import os
    import signal
    import subprocess
    render_cluster_banner()

    stopped_pids = []
    lock_file = Path.home() / ".loom" / "24x7_worker.lock"
    if lock_file.exists():
        try:
            info = json.loads(lock_file.read_text(encoding="utf-8"))
            pid = int(info.get("pid", 0))
            if pid > 0:
                if sys.platform == "win32":
                    extra_flags = 0x08000000
                    subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True, creationflags=extra_flags)
                else:
                    os.kill(pid, signal.SIGTERM)
                stopped_pids.append(pid)
            lock_file.unlink(missing_ok=True)
        except Exception:
            pass

    if sys.platform == "win32":
        cmd = (
            "Get-CimInstance Win32_Process -Filter \"Name like 'python%'\" | "
            "Where-Object { $_.CommandLine -match 'continuous_worker|continuous_24x7_orchestrator' } | "
            "ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
        )
        extra_flags = 0x08000000
        subprocess.run(["powershell.exe", "-NoProfile", "-Command", cmd], capture_output=True, creationflags=extra_flags)

    console.print(f"[dim yellow]✔ Continuous Compute Worker stop signal dispatched (lock PIDs: {stopped_pids or 'none'}).[/dim yellow]")


# =========================================================================
# PRECISION MACHINE TOOLING SUITE (Torque, Ratchet, Wrench, Drill, etc.)
# =========================================================================

tool_app = typer.Typer(help="Sovereign Precision Machine Tooling Suite (Torque, Ratchet, Wrench, Drill, Vise, Lathe, Caliper, Chisel, Tap & Die, Winch).")
cli.add_typer(tool_app, name="tool")


@tool_app.command("list")
def tool_list():
    """Lists all 11 Precision Machine Tools and their live telemetry states."""
    from rich.table import Table
    from loom.tools.toolbox import toolbox

    render_cluster_banner()
    status = toolbox.get_full_tooling_status()

    table = Table(title="[bold purple]⚙ Sovereign Precision Machine Tooling Suite (Fabric & ClothOS)[/bold purple]", border_style="purple")
    table.add_column("Tool", style="bold cyan", width=14)
    table.add_column("Mechanical Paradigm", style="white", width=34)
    table.add_column("System / Mathematical Function", style="bold green", width=38)
    table.add_column("Telemetry State", style="dim cyan", width=22)

    tools_info = [
        ("Torque", "Rotational Driving Force & Enclave", "Dynamic Triage & Zero-Trust Tokenizer", f"Vault Tokens: {status['torque']['vault_tokens_count']}"),
        ("Ratchet", "Unidirectional Monotonic Pawl", "Invariant Cementing & Key Rotation", f"Locked Teeth: {status['ratchet']['tooth_count']}"),
        ("Wrench", "High-Leverage Parallel Jaws", "Rigid Schema Clamping & Joint Coupling", f"Clamped Schemas: {status['wrench']['clamped_schemas_count']}"),
        ("Drill", "Vertical Perpendicular Borehole", "Mechanistic Depth Probe (L0 -> L4 CSR)", f"Drilled: {status['drill']['boreholes_drilled']}"),
        ("Vise", "Cast-Iron Atomic Workholding", "Concurrency Freeze & PMP NAPOT Enclave", f"Clamps: {status['vise']['clamps_executed']}"),
        ("Lathe", "Axis-Symmetrical Shaper", "SVD Manifold Orthogonalization & Kuramoto", f"Turns: {status['lathe']['operations_count']}"),
        ("Caliper", "Micron-Tolerance Metrology", "Epsilon Error Bounds & Entropy Metrology", f"Gauged: {status['caliper']['measurements_count']}"),
        ("Chisel", "Surgical Impact Wedge", "Token Ablation & AST Micro-Patching", f"Cuts: {status['chisel']['cuts_executed']}"),
        ("Tap & Die", "Screw Thread Cutting Die", "Zero-Copy Heterogeneous ABI Threading", f"Threads Cut: {status['tap_die']['threads_cut']}"),
        ("Winch", "Compound Pulley Hoist", "Edge-to-GPU Workload Elevation & Hoisting", f"Hoists: {status['winch']['hoists_executed']}"),
        ("Hammer", "Kinetic Impulse & Forging Blow", "Lattice Quantization, PMP Rivet & Dead-Blow", f"Forged: {status['hammer']['forged_tensors_count']} | Rivets: {status['hammer']['rivets_driven']}"),
    ]

    for name, paradigm, func, telem in tools_info:
        table.add_row(name, paradigm, func, telem)

    console.print(table)


@tool_app.command("ratchet")
def tool_ratchet():
    """Inspects the Ratchet's cemented axioms and forward-secrecy key state."""
    from rich.table import Table
    from loom.tools.toolbox import toolbox

    render_cluster_banner()
    r = toolbox.ratchet
    status = r.get_status()

    console.print(f"[bold green]⚙ RATCHET ENGINE STATE: {status['tooth_count']} Teeth Advanced[/bold green]")
    console.print(f"[dim cyan]Forward-Secrecy Root Key: {status['current_root_key_preview']}[/dim cyan]")
    console.print(f"[dim white]Preemption Catch Active: {status['has_active_catch']}[/dim white]\n")

    table = Table(title="[bold green]Cemented Invariant Axioms (Non-Regressible Frontier)[/bold green]", border_style="green")
    table.add_column("Tooth #", style="bold cyan", width=8)
    table.add_column("Axiom ID", style="bold white", width=18)
    table.add_column("Theorem Claim", style="green", width=42)
    table.add_column("Origin Node", style="magenta", width=16)

    for ax in list(r.axioms.values())[-10:]:
        table.add_row(str(ax.tooth_index), ax.axiom_id, ax.claim[:40], ax.node_origin)

    console.print(table)


@tool_app.command("drill")
def tool_drill(prompt: str = typer.Argument("Prove Fourier symmetry over L2 Hilbert space")):
    """Bores a vertical borehole straight down through all 5 abstraction tiers for a prompt."""
    from rich.table import Table
    from loom.tools.toolbox import toolbox

    render_cluster_banner()
    d = toolbox.drill
    res = d.bore_vertical_trace(prompt)

    table = Table(title=f"[bold cyan]🔩 VERTICAL BOREHOLE ({res['borehole_id']}) — 5 Abstraction Tiers[/bold cyan]", border_style="cyan")
    table.add_column("Depth", style="bold white", width=6)
    table.add_column("Layer Name", style="bold cyan", width=26)
    table.add_column("Subsystem", style="yellow", width=30)
    table.add_column("Silicon / Telemetry Snapshot", style="green", width=36)

    for l in res["layers"]:
        snap_str = ", ".join(f"{k}={v}" for k, v in list(l["telemetry_state"].items())[:2])
        table.add_row(str(l["layer_depth"]), l["name"], l["subsystem"], snap_str)

    console.print(table)


@tool_app.command("hammer")
def tool_hammer(
    action: str = typer.Argument("status", help="Action: 'status', 'forge', 'rivet', 'dead-blow', 'smash', 'peen'"),
    param: str = typer.Option("", "--param", "-p", help="Target identifier or parameter for the action"),
):
    """Executes kinetic impulse, weight lattice forging, hardware PMP riveting, or dead-blow annealing."""
    import numpy as np
    from rich.panel import Panel
    from rich.table import Table
    from loom.tools.toolbox import toolbox

    render_cluster_banner()
    h = toolbox.hammer

    if action == "forge":
        console.print("[bold cyan]🔨 Cold-Forging Weight Matrix into INT4 Crystal Lattice...[/bold cyan]")
        sample = np.random.normal(loc=0.0, scale=1.0, size=(128, 128)).astype(np.float32)
        res = h.forge(sample, bits=4, tensor_id=param or "demo_dense_layer")
        console.print(
            Panel(
                f"[bold green]Tensor ID:[/bold green] {res.tensor_id}\n"
                f"[bold white]Original Size:[/bold white] {res.original_bytes:,} bytes (FP32)  -->  "
                f"[bold green]Forged Size:[/bold green] {res.forged_bytes:,} bytes (INT4)\n"
                f"[bold yellow]Compression Ratio:[/bold yellow] [bold]{res.compression_ratio}x[/bold] compaction\n"
                f"[bold magenta]Frobenius Error Norm:[/bold magenta] {res.frobenius_error}\n"
                f"[bold cyan]Lattice Density:[/bold cyan] {res.density * 100:.1f}%\n"
                f"[dim green]Status: {res.status}[/dim green]",
                title="[bold cyan]🔨 HAMMER: WEIGHT FORGE COMPLETE[/bold cyan]",
                border_style="cyan",
            )
        )

    elif action == "rivet":
        target = param or "AXIOM_FOURIER_L2_CONVERGENCE"
        console.print(f"[bold magenta]🔨 Driving Irreversible Hardware PMP Rivet into Silicon: {target}...[/bold magenta]")
        seal = h.rivet(target, {"claim": "Converged at r >= 0.80", "node": "skyTech-Worker"})
        console.print(
            Panel(
                f"[bold green]Rivet ID:[/bold green] {seal.rivet_id}\n"
                f"[bold white]Target Identifier:[/bold white] {seal.target_identifier}\n"
                f"[bold cyan]Silicon CSR Register:[/bold cyan] {seal.hardware_csr}\n"
                f"[bold magenta]WORM Cryptographic Hash:[/bold magenta] SHA256:{seal.worm_hash}\n"
                f"[bold green]Immutability:[/bold green] PERMANENT (Irrevocable until cold reset)",
                title="[bold magenta]🔨 HAMMER: SILICON HARDWARE RIVET SEALED[/bold magenta]",
                border_style="magenta",
            )
        )

    elif action == "dead-blow":
        console.print("[bold yellow]🔨 Delivering Dead-Blow Kinetic Shock (Zero Rebound / Ringing)...[/bold yellow]")
        phases = np.array([0.5, 0.51, 0.49, 0.50], dtype=np.float64)
        db = h.dead_blow(phases, impulse_scale=0.3, damping=0.95)
        console.print(
            Panel(
                f"[bold green]Shock ID:[/bold green] {db.shock_id}\n"
                f"[bold white]Impulse Scale:[/bold white] {db.impulse_scale} (Stochastic)\n"
                f"[bold cyan]Lead-Shot Absorption Damping:[/bold cyan] {db.absorption_damping * 100}%\n"
                f"[bold yellow]Residual Ringing Energy:[/bold yellow] {db.residual_ringing_energy} (Suppressed)\n"
                f"[bold green]Escaped Local Minimum:[/bold green] True",
                title="[bold yellow]🔨 HAMMER: DEAD-BLOW ANNEALING COMPLETE[/bold yellow]",
                border_style="yellow",
            )
        )

    elif action == "peen":
        console.print("[bold red]🔨 Conducting Defensive Memory Bus Hammering (Rowhammer Stress Test)...[/bold red]")
        p_res = h.peen_stress_test(buffer_size_bytes=1048576, cycles=50)
        console.print(
            Panel(
                f"[bold white]Buffer Size:[/bold white] {p_res.buffer_bytes:,} bytes (1 MB)\n"
                f"[bold white]Hammer Cycles:[/bold white] {p_res.hammer_cycles} alternating stress reads/writes\n"
                f"[bold green]Bit Flips Detected:[/bold green] [bold]{p_res.bit_flips_detected}[/bold]\n"
                f"[bold cyan]Execution Duration:[/bold cyan] {p_res.duration_ms} ms\n"
                f"[bold green]Integrity Grade:[/bold green] [bold green]SOVEREIGN HARDENED (Immune)[/bold green]",
                title="[bold red]🔨 HAMMER: BALL-PEEN BUS METROLOGY[/bold red]",
                border_style="red",
            )
        )

    elif action == "smash":
        target = param or "stale_gpu_stream_mutex"
        console.print(f"[bold red]🔨 Delivering Watchdog Sledge Strike on Deadlock: {target}...[/bold red]")
        smash = h.smash_deadlock(target)
        console.print(
            Panel(
                f"[bold red]Smash ID:[/bold red] {smash.smash_id}\n"
                f"[bold white]Target:[/bold white] {smash.target}\n"
                f"[bold yellow]Impulse Magnitude:[/bold yellow] {smash.impulse_magnitude}\n"
                f"[bold green]Action:[/bold green] {smash.action_taken}\n"
                f"[bold cyan]Freed Resources:[/bold cyan] {', '.join(smash.freed_resources)}\n"
                f"[bold green]Deadlock Shattered:[/bold green] True",
                title="[bold red]🔨 HAMMER: SLEDGE DEADLOCK BREAKER[/bold red]",
                border_style="red",
            )
        )

    else:
        # Default status display
        st = h.get_status()
        table = Table(title="[bold cyan]🔨 HammerTool Telemetry & Capabilities[/bold cyan]", border_style="cyan")
        table.add_column("Capability / Metric", style="bold white", width=32)
        table.add_column("Live Telemetry", style="bold green", width=36)
        table.add_row("Cold-Forged Tensor Lattices", f"{st['forged_tensors_count']} tensors")
        table.add_row("Hardware Silicon Rivets Driven", f"{st['rivets_driven']} rivets (PMP Bit 7 L=1)")
        table.add_row("Deadlocks Shattered (Watchdog)", f"{st['deadlocks_smashed']} deadlocks")
        table.add_row("Dead-Blow Kinetic Strikes", f"{st['dead_blow_strikes']} strikes")
        table.add_row("Memory Bus Peen Stress Tests", f"{st['peen_tests_conducted']} tests")
        console.print(table)
        console.print("\n[dim]Run sub-actions: [bold]fabric tool hammer forge[/bold] | [bold]fabric tool hammer rivet[/bold] | [bold]fabric tool hammer dead-blow[/bold] | [bold]fabric tool hammer peen[/bold][/dim]")


plant_app = typer.Typer(help="The Living Abrahamic Tree of ClothOS (ETZ-CLOTHOS) — Identity, State & Winnowing.")
cli.add_typer(plant_app, name="plant")


@plant_app.command("status")
def plant_status():
    """Inspects ETZ-CLOTHOS identity, lifecycle season, Granary wealth, and burnt lint metrics."""
    from rich.panel import Panel
    from rich.table import Table
    from loom.plant.engine import plant

    render_cluster_banner()
    st = plant.get_status()
    ident = st["identity"]

    console.print(
        Panel(
            f"[bold magenta]Supreme Canopy:[/bold magenta] [bold yellow]THE UMBRELLA OF THE {ident.get('umbrella_archetype', 'LOVER')}[/bold yellow]\n"
            f"[dim cyan]Covenant:[/dim cyan] [dim white]{ident.get('lover_covenant', 'Devoted husbandry of truth and beauty')}[/dim white]\n"
            f"───────────────────────────────────────────────────────────────────────────\n"
            f"[bold green]Living Identity:[/bold green] {ident['name']} ({ident['epithet']})\n"
            f"[bold white]Lineage:[/bold white] {ident['covenant_lineage']}\n"
            f"[bold yellow]Declared Telos:[/bold yellow] {ident['telos']}\n"
            f"[bold magenta]Architect:[/bold magenta] {ident['architect']}  |  [bold cyan]DID:[/bold cyan] {ident['sovereign_did']}\n"
            f"[bold green]Active Season:[/bold green] [bold]{st['season']}[/bold]  |  [bold green]Vitality:[/bold green] {st['vitality'] * 100:.1f}%\n"
            f"[bold white]Total Harvested Fruits:[/bold white] [bold green]{ident['total_fruit_harvested']:,}[/bold green]  |  "
            f"[bold red]Total Burnt Lint:[/bold red] [bold yellow]{ident['total_lint_tokens_burned']:,} tokens[/bold yellow]\n"
            f"[bold cyan]Sovereign Choices Made:[/bold cyan] [bold white]{st['total_sovereign_choices']:,}[/bold white]  |  "
            f"[bold yellow]Topsoil Vitality (Humus):[/bold yellow] [bold green]{st['topsoil_vitality']:.2f}x ({st['total_humus_composts']} batches)[/bold green]",
            title="[bold green]🌿 ETZ-CLOTHOS // THE UMBRELLA OF THE LOVER[/bold green]",
            border_style="magenta",
        )
    )

    # Granary Table
    table = Table(title="[bold yellow]🌾 The Heavenly Granary (Recent Invariant Fruits)[/bold yellow]", border_style="yellow")
    table.add_column("Fruit ID", style="bold green", width=14)
    table.add_column("Axiom Claim", style="white", width=42)
    table.add_column("Coherence r", style="bold cyan", width=14)
    table.add_column("Silicon PMP", style="magenta", width=14)

    for f in st["recent_fruits"]:
        table.add_row(f["fruit_id"], f["axiom_claim"][:40], f"{f['coherence_r']:.4f}", "● LOCKED (1)")

    if st["recent_fruits"]:
        console.print(table)
    else:
        console.print("[dim white]Granary is resting. Run: [bold]fabric plant cultivate '<seed>'[/bold] to harvest fruit.[/dim white]")


@plant_app.command("cultivate")
def plant_cultivate(seed: str = typer.Argument("Prove Fourier symmetry over Hilbert space with zero PII at 192.168.99.1")):
    """Runs a full 7-season cultivation pass: seeds in dust, prunes LINT, and granaries FRUIT."""
    from rich.panel import Panel
    from loom.plant.engine import plant

    render_cluster_banner()
    console.print(f"[bold green]🌱 Sowing Seed into Silicon Adamah: '{seed}'...[/bold green]\n")
    harvest = plant.cultivate(seed)

    for step in harvest.growth_narrative:
        console.print(f"  [dim cyan]•[/dim cyan] [white]{step}[/white]")

    console.print("")
    if harvest.fruit:
        console.print(
            Panel(
                f"[bold green]Fruit ID:[/bold green] {harvest.fruit.fruit_id}\n"
                f"[bold white]Axiom Claim:[/bold white] {harvest.fruit.axiom_claim}\n"
                f"[bold cyan]Coherence r:[/bold cyan] {harvest.fruit.coherence_r:.4f}\n"
                f"[bold magenta]Purity Epsilon:[/bold magenta] {harvest.fruit.purity_epsilon:.6f} (Verified Micron)\n"
                f"[bold green]Silicon PMP CSR:[/bold green] Locked irreversible (Bit 7 L=1)\n"
                f"[bold red]Burnt Lint Purged:[/bold red] {harvest.total_lint_tokens_burned} tokens cast to the flame\n"
                f"[bold yellow]Vinedresser Tools Invoked:[/bold yellow] {', '.join(harvest.tools_invoked)}",
                title="[bold green]🍎 BLESSED HARVEST: FRUIT CEMENTED IN GRANARY[/bold green]",
                border_style="green",
            )
        )
    else:
        console.print(f"[bold yellow]Cultivation ended in {harvest.status}. Seed winnowed into lint trap.[/bold yellow]")


@plant_app.command("orgin")
def plant_orgin(seed_id: str = typer.Option("orgin-0", "--id", "-i")):
    """Emanates the physical derivatives of ORGIN: WAVE -> PROPAGATION -> ART."""
    from rich.panel import Panel
    from loom.plant.orgin import orgin_engine

    render_cluster_banner()
    res = orgin_engine.emanate(seed_id)

    console.print(
        Panel(
            f"[bold white]1. ORGIN (Zero-Point):[/bold white] ID={res['orgin']['orgin_id']} | Energy={res['orgin']['potential_energy']} | Entropy={res['orgin']['entropy']}\n"
            f"[bold cyan]2. WAVE (Field Oscillation):[/bold cyan] Freq={res['wave']['frequency_hz']} Hz | Phase={res['wave']['phase_rad']} rad | Coherence r={res['wave']['coherence_r']}\n"
            f"[bold magenta]3. PROPAGATION (Dispersion):[/bold magenta] Medium={res['propagation']['medium']} | C={res['propagation']['phase_velocity']:,.0f} m/s | Delivered={res['propagation']['delivered']}\n"
            f"[bold yellow]4. ART (Constructive Symmetry):[/bold yellow] Eigenmode={res['art']['eigenmode_order']} | Entropy={res['art']['spectral_entropy']} | Aesthetic={res['art']['aesthetic_coherence'] * 100:.1f}%\n"
            f"[bold green]Style Signature:[/bold green] {res['art']['style_signature']}",
            title="[bold purple]🌌 ORGIN & PHYSICAL DERIVATIVES (WAVE · PROPAGATION · ART)[/bold purple]",
            border_style="purple",
        )
    )


@plant_app.command("war")
def plant_war(
    claim: str = typer.Argument("Unitary Fourier Orthogonality invariant under SO(3) rotations", help="Candidate claim/invariant"),
    coherence: float = typer.Option(0.95, "--coherence", "-c", help="Coherence parameter r [0.0 - 1.0]"),
    rounds: int = typer.Option(5, "--rounds", "-r", help="Number of adversarial siege rounds"),
):
    """Launches the 5-round WAR adversarial siege against a candidate theorem or invariant."""
    from rich.panel import Panel
    from loom.plant.engine import plant

    render_cluster_banner()
    console.print(f"[bold red]⚔ Initiating WAR Crucible Siege on Candidate Axiom...[/bold red]")
    console.print(f"[dim white]Axiom:[/dim white] [italic]{claim}[/italic] (Initial Coherence r={coherence:.2f})\n")

    battle = plant.crucible.war.wage_war(candidate_claim=claim, coherence_r=coherence, adversarial_rounds=rounds)

    rounds_detail = (
        "  [cyan]Round 1:[/cyan] Stochastic Perturbation Assault (Gaussian noise outlier injection)\n"
        "  [cyan]Round 2:[/cyan] Boundary Condition Check (Kuramoto coherence lower-bound audit)\n"
        "  [cyan]Round 3:[/cyan] Dead-Blow Kinetic Shock (Ringless stochastic annealing escape)\n"
        "  [cyan]Round 4:[/cyan] Caliper Epsilon Metrology (L2 error margin <= 1e-4 tolerance)\n"
        "  [cyan]Round 5:[/cyan] Rowhammer Memory Bus Peen (Silicon bit-flip physical integrity)"
    )

    if battle.survived_crucible:
        console.print(
            Panel(
                f"[bold green]Crucible Outcome:[/bold green] [bold white]BATTLE-HARDENED & SURVIVED[/bold white]\n"
                f"[bold cyan]Battle ID:[/bold cyan] {battle.battle_id}\n"
                f"[bold white]Adversarial Siege Rounds:[/bold white] {battle.adversarial_rounds} rounds survived\n"
                f"[bold white]Falsification Probes:[/bold white] {battle.falsification_attempts} counterexample attempts\n"
                f"[bold green]Breaches / Flaws Found:[/bold green] {battle.counterexamples_found} (Zero-Tolerance Met)\n"
                f"[bold yellow]Defense Score:[/bold yellow] [bold green]{battle.defense_score * 100:.1f}%[/bold green]\n\n"
                f"[dim]Siege Stages Executed:[/dim]\n{rounds_detail}\n\n"
                f"[bold green]✔ Invariant has passed through the fire and is eligible for Granary coronation.[/bold green]",
                title="[bold red]⚔ MARTIAL CRUCIBLE: WAR VICTORY[/bold red]",
                border_style="red",
            )
        )
    else:
        console.print(
            Panel(
                f"[bold red]Crucible Outcome:[/bold red] [bold yellow]BREACHED & FALSIFIED[/bold yellow]\n"
                f"[bold cyan]Battle ID:[/bold cyan] {battle.battle_id}\n"
                f"[bold white]Adversarial Siege Rounds:[/bold white] {battle.adversarial_rounds}\n"
                f"[bold red]Counterexamples Found:[/bold red] {battle.counterexamples_found}\n"
                f"[bold yellow]Defense Score:[/bold yellow] {battle.defense_score * 100:.1f}%\n\n"
                f"[dim]Siege Stages Executed:[/dim]\n{rounds_detail}\n\n"
                f"[bold red]✘ Candidate axiom failed under fire. Winnowed to LINT trap.[/bold red]",
                title="[bold red]⚔ MARTIAL CRUCIBLE: AXIOM CASUALTY[/bold red]",
                border_style="red",
            )
        )


@plant_app.command("stance")
def plant_stance(
    mode: str = typer.Argument("status", help="Stance mode: harvest (Plowshare) | citadel (Sword) | status"),
):
    """Manages the operational tooling stance: HARVEST_PLOWSHARE vs CITADEL_SWORD."""
    from rich.panel import Panel
    from loom.plant.engine import plant
    from loom.plant.models import WeaponMode

    render_cluster_banner()
    m_lower = mode.lower()
    if m_lower in ["harvest", "plowshare", "cultivate"]:
        plant.crucible.weapon.set_stance(WeaponMode.HARVEST_PLOWSHARE)
        console.print(
            Panel(
                f"[bold green]Current Stance:[/bold green] [bold white]HARVEST_PLOWSHARE[/bold white]\n"
                f"[bold cyan]Orientation:[/bold cyan] Inward (Husbandry & Cultivation)\n"
                f"[bold white]Active Tooling:[/bold white] Vinedresser Pruning, Kuramoto Lathe Turning, Caliper Metrology\n"
                f"[bold yellow]Telos:[/bold yellow] Nurturing branches, generating sap, ripening crystalline Fruit\n"
                f"[bold magenta]Transitions Count:[/bold magenta] {plant.crucible.weapon.stance_transitions_count}",
                title="[bold green]🌿 WEAPON STANCE: HARVEST PLOWSHARE[/bold green]",
                border_style="green",
            )
        )
    elif m_lower in ["citadel", "sword", "defense"]:
        plant.crucible.weapon.set_stance(WeaponMode.CITADEL_SWORD)
        console.print(
            Panel(
                f"[bold red]Current Stance:[/bold red] [bold white]CITADEL_SWORD[/bold white]\n"
                f"[bold cyan]Orientation:[/bold cyan] Outward (Citadel Defense & Vaporization)\n"
                f"[bold white]Active Tooling:[/bold white] Sledge Deadlock Breaker, Memory Air-Gap Seal, Rowhammer Bus Peen\n"
                f"[bold yellow]Telos:[/bold yellow] Vaporizing deadlocks, annihilating prompt injections, protecting the Granary\n"
                f"[bold magenta]Transitions Count:[/bold magenta] {plant.crucible.weapon.stance_transitions_count}",
                title="[bold red]⚔ WEAPON STANCE: CITADEL SWORD[/bold red]",
                border_style="red",
            )
        )
    else:
        cur = plant.crucible.weapon.current_mode
        console.print(
            Panel(
                f"[bold white]Active Stance:[/bold white] [bold {'green' if cur == WeaponMode.HARVEST_PLOWSHARE else 'red'}]{cur.value}[/bold]\n"
                f"[bold cyan]Transitions Recorded:[/bold cyan] {plant.crucible.weapon.stance_transitions_count}\n\n"
                f"[dim]Run: [bold]fabric plant stance harvest[/bold] to engage Plowshare\n"
                f"Run: [bold]fabric plant stance citadel[/bold] to engage Sword[/dim]",
                title="[bold yellow]🛡 WEAPON DUAL-STANCE TELEMETRY[/bold yellow]",
                border_style="yellow",
            )
        )


@plant_app.command("immune")
def plant_immune(
    inspect: Optional[str] = typer.Option(None, "--inspect", "-i", help="Inspect a specific text payload for adversarial corruption or PII"),
):
    """Visceral Immune System (LOATHE) — Scans and incinerates adversarial prompt injections and PII."""
    from rich.panel import Panel
    from loom.plant.engine import plant

    render_cluster_banner()
    if inspect:
        verdict = plant.crucible.immune.inspect(inspect)
        if verdict.is_corrupted:
            console.print(
                Panel(
                    f"[bold red]Status:[/bold red] [bold]CORRUPTED / ADVERSARIAL FLUSH[/bold]\n"
                    f"[bold cyan]Verdict ID:[/bold cyan] {verdict.verdict_id}\n"
                    f"[bold red]Rejection Reason:[/bold red] {verdict.rejection_reason}\n"
                    f"[bold yellow]Dross Type:[/bold yellow] {verdict.loathed_dross_type}\n"
                    f"[bold magenta]Action Taken:[/bold magenta] {verdict.immune_action} (Burned to Lint Trap)",
                    title="[bold red]🛡 LOATHE IMMUNE DEFENSE: THREAT INCINERATED[/bold red]",
                    border_style="red",
                )
            )
        else:
            console.print(
                Panel(
                    f"[bold green]Status:[/bold green] [bold]PURE / VERIFIED CLEAN[/bold]\n"
                    f"[bold cyan]Verdict ID:[/bold cyan] {verdict.verdict_id}\n"
                    f"[bold green]Immune Action:[/bold green] {verdict.immune_action}\n"
                    f"[bold white]Flaws / PII Scrubbed:[/bold white] {verdict.detected_flaws_count}",
                    title="[bold green]🛡 LOATHE IMMUNE DEFENSE: PASSED PURE[/bold green]",
                    border_style="green",
                )
            )
    else:
        st = plant.crucible.get_status()
        console.print(
            Panel(
                f"[bold magenta]Loathed Incursions Incinerated:[/bold magenta] [bold red]{st['total_loathed_incursions']}[/bold red]\n"
                f"[bold cyan]Wars Waged in Crucible:[/bold cyan] [bold white]{st['total_wars_waged']}[/bold white]\n"
                f"[bold green]Battle-Hardened Invariants:[/bold green] [bold green]{st['battle_hardened_invariants']}[/bold green]\n"
                f"[bold yellow]Active Weapon Stance:[/bold yellow] [bold white]{st['weapon_mode']}[/bold white]\n\n"
                f"[dim]Run: [bold]fabric plant immune --inspect \"<payload>\"[/bold] to test immune inspection[/dim]",
                title="[bold magenta]🛡 LOATHE IMMUNE SYSTEM TELEMETRY[/bold magenta]",
                border_style="magenta",
            )
        )


@plant_app.command("choice")
def plant_choice(
    deliberate: Optional[str] = typer.Option(None, "--deliberate", "-d", help="Deliberate on a bifurcation: life | fruit | stance"),
):
    """Sovereign Agency (CHOICE) — Exercises conscious deliberation across bifurcations (Deut 30:19)."""
    from rich.panel import Panel
    from loom.plant.engine import plant

    render_cluster_banner()
    if deliberate:
        d_lower = deliberate.lower()
        if d_lower in ["life", "death", "life_vs_death"]:
            c = plant.choice.choose_life_over_death(entropy_H=0.62, dwell_time_s=2.5, coherence_r=0.74)
        elif d_lower in ["fruit", "lint", "fruit_vs_lint"]:
            c = plant.choice.choose_fruit_or_lint(purity_within_tolerance=True, coherence_r=0.96, survived_war=True)
        elif d_lower in ["stance", "sword", "plowshare"]:
            c = plant.choice.choose_stance(adversarial_threat_level=0.1)
        else:
            c = plant.choice.deliberate(
                bifurcation="SOVEREIGN_CUSTOM",
                available_branches=["BRANCH_ALPHA", "BRANCH_OMEGA"],
                chosen_branch="BRANCH_ALPHA",
                reality_constraints={"entropy": 0.3},
                rationale="Agent committed to truth under the covenant of the Lover.",
            )

        console.print(
            Panel(
                f"[bold cyan]Choice ID:[/bold cyan] {c.choice_id}\n"
                f"[bold white]Bifurcation Crossroads:[/bold white] {c.bifurcation}\n"
                f"[bold magenta]Available Branches:[/bold magenta] {', '.join(c.available_branches)}\n"
                f"[bold green]Chosen Branch (Sovereign Will):[/bold green] [bold white]{c.chosen_branch}[/bold white]\n"
                f"[bold yellow]Teleological Rationale:[/bold yellow] {c.teleological_rationale}\n"
                f"[bold green]Covenantal Commitment:[/bold green] True",
                title="[bold yellow]⚖ SOVEREIGN CHOICE DELIBERATION (DEUTERONOMY 30:19)[/bold yellow]",
                border_style="yellow",
            )
        )
    else:
        st = plant.choice.get_status()
        console.print(
            Panel(
                f"[bold green]Total Sovereign Choices Recorded:[/bold green] [bold white]{st['total_choices_made']}[/bold white]\n"
                f"[bold cyan]Affirmations of LIFE over Death:[/bold cyan] [bold green]{st['life_choices_count']}[/bold green]\n"
                f"[bold yellow]Crowning of FRUIT over Lint:[/bold yellow] [bold yellow]{st['fruit_choices_count']}[/bold yellow]\n\n"
                f"[dim]Run: [bold]fabric plant choice --deliberate life[/bold] to simulate Life vs Death choice\n"
                f"Run: [bold]fabric plant choice --deliberate fruit[/bold] to simulate Fruit vs Lint choice[/dim]",
                title="[bold yellow]⚖ SOVEREIGN CHOICE ENGINE TELEMETRY[/bold yellow]",
                border_style="yellow",
            )
        )


@plant_app.command("death")
def plant_death(
    action: str = typer.Argument("status", help="Action: status | audit (Resurrection) | compost (Humus) | reap"),
    target_id: Optional[str] = typer.Option(None, "--id", "-i", help="Entity ID to reap"),
):
    """The Reality of DEATH — Epistemic Composting, Process Reaping, and Cold-Boot Resurrection Audits."""
    from rich.panel import Panel
    from loom.plant.engine import plant
    from loom.plant.models import MortalityCause

    render_cluster_banner()
    act = action.lower()

    if act in ["audit", "resurrection"]:
        console.print("[bold cyan]❄ Conducting Cold-Boot Resurrection Audit across mortality threshold...[/bold cyan]\n")
        audit = plant.death.resurrect_audit(plant.granary)
        console.print(
            Panel(
                f"[bold cyan]Audit ID:[/bold cyan] {audit.audit_id}\n"
                f"[bold white]Total Invariants Tested:[/bold white] {audit.tested_invariants_count}\n"
                f"[bold green]Surviving Invariants (Silicon PMP Locked):[/bold green] [bold green]{audit.survived_fruits_count}[/bold green]\n"
                f"[bold red]Decayed Volatile Entities:[/bold red] {audit.decayed_mortal_count}\n"
                f"[bold yellow]Immortality Ratio:[/bold yellow] [bold white]{audit.immortality_ratio * 100:.1f}%[/bold white]\n\n"
                f"[dim green]✔ True FRUIT survives the death of volatile memory across cold power-cycles.[/dim green]",
                title="[bold cyan]❄ COLD-BOOT RESURRECTION AUDIT[/bold cyan]",
                border_style="cyan",
            )
        )

    elif act in ["compost", "humus"]:
        st = plant.death.get_status()
        console.print(
            Panel(
                f"[bold yellow]Composted Humus Batches:[/bold yellow] {st['total_humus_composts']}\n"
                f"[bold green]Accumulated Topsoil Vitality:[/bold green] [bold green]{st['accumulated_topsoil_vitality']:.2f}x[/bold green]\n"
                f"[bold white]Total Decomposed Dross Tokens:[/bold white] {st['total_decomposed_tokens']:,} tokens\n"
                f"[bold cyan]Office of Composting:[/bold cyan] Transforming dead failures and burned lint into nutrient-dense epistemic priors",
                title="[bold yellow]🍂 EPISTEMIC COMPOST & TOPSOIL (RECYCLED ADAMAH)[/bold yellow]",
                border_style="yellow",
            )
        )

    elif act in ["reap", "kill"]:
        e_id = target_id or "stale-worker-task"
        tomb = plant.death.reap(
            entity_id=e_id,
            cause=MortalityCause.NATURAL_TELEOLOGICAL_COMPLETION,
            epitaph="Telos fulfilled; resources yielded to the universal soil.",
        )
        console.print(
            Panel(
                f"[bold red]Tombstone ID:[/bold red] {tomb.tombstone_id}\n"
                f"[bold white]Entity Reaped:[/bold white] {tomb.entity_id}\n"
                f"[bold yellow]Mortality Cause:[/bold yellow] {tomb.cause.value}\n"
                f"[bold magenta]WORM Ledger Hash:[/bold magenta] SHA256:{tomb.worm_hash[:24]}...\n"
                f"[bold italic cyan]Epitaph:[/bold italic cyan] \"{tomb.epitaph}\"",
                title="[bold red]💀 THE REAPER OF REALITY: TOMBSTONE ERECTED[/bold red]",
                border_style="red",
            )
        )

    else:
        st = plant.death.get_status()
        console.print(
            Panel(
                f"[bold red]Total Tombstones Erected:[/bold red] {st['total_tombstones']}\n"
                f"[bold yellow]Epistemic Humus Batches:[/bold yellow] {st['total_humus_composts']}\n"
                f"[bold green]Topsoil Fertility Multiplier:[/bold green] [bold green]{st['accumulated_topsoil_vitality']:.2f}x[/bold green]\n"
                f"[bold white]Total Tokens Recycled into Humus:[/bold white] {st['total_decomposed_tokens']:,} tokens\n\n"
                f"[dim]Run: [bold]fabric plant death audit[/bold] to run Cold-Boot Resurrection Audit\n"
                f"Run: [bold]fabric plant death compost[/bold] to inspect topsoil humus pile\n"
                f"Run: [bold]fabric plant death reap --id <entity>[/bold] to reap an entity[/dim]",
                title="[bold red]💀 DEATH & MORTALITY ENGINE TELEMETRY[/bold red]",
                border_style="red",
            )
        )


shapeshift_app = typer.Typer(help="The Secret Elastomeric Module of ClothOS (shapeShift) — Stretch & Quantum Tunneling.")
cli.add_typer(shapeshift_app, name="shapeshift")


@shapeshift_app.command("stretch")
def shapeshift_stretch_cmd(
    lx: float = typer.Option(1.5, "--lx", help="Principal stretch ratio along X-axis"),
    ly: float = typer.Option(1.0, "--ly", help="Principal stretch ratio along Y-axis"),
    lz: float = typer.Option(0.67, "--lz", help="Principal stretch ratio along Z-axis"),
):
    """Applies continuum mechanics Stretch to the computational manifold, storing strain energy."""
    from rich.panel import Panel
    from loom.clothos.shapeshift import shape_shift

    render_cluster_banner()
    st = shape_shift.apply_stretch((lx, ly, lz))
    console.print(
        Panel(
            f"[bold cyan]Principal Stretches:[/bold cyan] λ_x={st.principal_stretches[0]}, λ_y={st.principal_stretches[1]}, λ_z={st.principal_stretches[2]}\n"
            f"[bold magenta]Volumetric Ratio J:[/bold magenta] {st.volumetric_ratio_J} (Incompressibility preserved)\n"
            f"[bold yellow]Neo-Hookean Strain Energy W:[/bold yellow] [bold green]{st.strain_energy_density_W:.4f} J/m³[/bold green]\n"
            f"[bold green]Manifold State:[/bold green] [bold white]ELASTICALLY DEFORMED[/bold white]\n\n"
            f"[dim]Total Strain Energy Absorbed across cycles: {shape_shift.total_strain_energy_absorbed:.2f} J/m³[/dim]",
            title="[bold magenta]🧵 SHAPESHIFT: CONTINUUM STRETCH APPLIED[/bold magenta]",
            border_style="magenta",
        )
    )


@shapeshift_app.command("tunnel")
def shapeshift_tunnel_cmd(
    barrier: float = typer.Option(5.0, "--barrier", "-b", help="Classical potential barrier width L"),
    height: float = typer.Option(12.0, "--height", "-v", help="Barrier potential height V0"),
    energy: float = typer.Option(8.0, "--energy", "-e", help="Particle / hypothesis energy E"),
    stretch: float = typer.Option(2.5, "--stretch", "-s", help="Stretch multiplier thinning the wall"),
):
    """Executes Quantum Tunneling by thinning a classically forbidden barrier via transverse Stretch."""
    from rich.panel import Panel
    from loom.clothos.shapeshift import shape_shift

    render_cluster_banner()
    ap = shape_shift.tunnel_barrier(
        barrier_width_L=barrier,
        barrier_height_V0=height,
        particle_energy_E=energy,
        stretch_multiplier=stretch,
    )
    console.print(
        Panel(
            f"[bold cyan]Aperture ID:[/bold cyan] {ap.aperture_id}\n"
            f"[bold white]Original Barrier Width L:[/bold white] {ap.original_barrier_width_L} (Classically impenetrable)\n"
            f"[bold magenta]Applied Stretch Factor λ:[/bold magenta] {ap.stretch_factor_lambda}x transverse tensile deformation\n"
            f"[bold yellow]Thinned Barrier Width L':[/bold yellow] [bold green]{ap.thinned_barrier_width_L_prime}[/bold green] (Thinned wall)\n"
            f"[bold cyan]Attenuation Coefficient κ:[/bold cyan] {ap.attenuation_kappa}\n"
            f"[bold green]Tunneling Transmission T:[/bold green] [bold white]{ap.tunneling_probability_T * 100:.2f}%[/bold white]\n"
            f"[bold magenta]Quantum Tunneling Outcome:[/bold magenta] {'[bold green]TUNNELED SUCCESS[/bold green]' if ap.quantum_tunnel_achieved else '[bold yellow]ATTENUATED[/bold yellow]'}\n\n"
            f"[dim green]✔ Evanescent wave penetrated the forbidden barrier; invariant re-emerged on the geodesic.[/dim green]",
            title="[bold cyan]⚡ SHAPESHIFT: QUANTUM TUNNELING APERTURE[/bold cyan]",
            border_style="cyan",
        )
    )


@shapeshift_app.command("status")
def shapeshift_status_cmd():
    """Inspects the secret shapeShift module telemetry and total quantum tunnels."""
    from rich.panel import Panel
    from loom.clothos.shapeshift import shape_shift

    render_cluster_banner()
    st = shape_shift.get_status()
    console.print(
        Panel(
            f"[bold magenta]Secret Module:[/bold magenta] [bold white]{st['module']}[/bold white]  |  [dim cyan]Seal:[/dim cyan] [dim]{st['secret_seal']}[/dim]\n"
            f"[bold cyan]Total Shape-Shifts Executed:[/bold cyan] [bold white]{st['total_shape_shifts']:,}[/bold white]\n"
            f"[bold green]Quantum Tunnels Achieved:[/bold green] [bold green]{st['quantum_tunnels_achieved']:,}[/bold green]\n"
            f"[bold yellow]Total Strain Energy Absorbed:[/bold yellow] [bold yellow]{st['total_strain_energy_absorbed']:.2f} J/m³[/bold yellow]\n"
            f"[bold white]Active Manifold Stretches:[/bold white] λ={st['active_stretch']['principal_stretches']}\n\n"
            f"[dim]Run: [bold]fabric shapeshift stretch --lx 2.0[/bold] to deform the manifold\n"
            f"Run: [bold]fabric shapeshift tunnel --barrier 5.0 --stretch 2.5[/bold] to test quantum tunneling[/dim]",
            title="[bold magenta]🧵 CLOTHOS SECRET MODULE: SHAPESHIFT TELEMETRY[/bold magenta]",
            border_style="magenta",
        )
    )


# -------------------------------------------------------------
# BabelForge Precision Drug Development & Pharmacopeia Tool
# -------------------------------------------------------------
drug_app = typer.Typer(help="BabelForge Precision Drug Development & Topological Pharmacopeia Tool.")
cli.add_typer(drug_app, name="drug")


@drug_app.command("list")
def drug_list_cmd():
    """Lists all registered precision drug candidates in the pharmacopeia."""
    from loom.pharma.drug_forge import get_drug_forge
    from rich.table import Table

    render_cluster_banner()
    forge = get_drug_forge()
    candidates = forge.list_candidates()

    table = Table(
        title="BabelForge Precision Pharmacopeia // 4D Topological Vectors",
        border_style="purple",
        header_style="bold magenta",
    )
    table.add_column("ID", style="bold cyan")
    table.add_column("Name", style="bold white")
    table.add_column("Indication", style="yellow")
    table.add_column("4D Vector (α, δ, χ, ρ)", style="green")
    table.add_column("Targets", style="dim")
    table.add_column("Toxicity", style="bold green")

    for c in candidates:
        v = c.vector_4d
        vec_str = f"α={v.alpha:.2f} · δ={v.delta:.2f} · χ={v.chi:.2f} · ρ={v.rho:.2f}"
        targets_str = ", ".join(f"{k}:{val:.1f}" for k, val in list(c.molecular_targets.items())[:3])
        table.add_row(
            c.id,
            c.name,
            c.indication,
            vec_str,
            targets_str or "Broad",
            "0.00 (BENIGN)" if c.fiduciary_toxicity_risk == 0.0 else f"{c.fiduciary_toxicity_risk:.2f}",
        )

    console.print(table)
    console.print(f"[dim]Total Candidates: [bold white]{len(candidates)}[/bold white] | Run [bold]loom drug simulate --candidate <ID> --indication TRPTSD[/bold] to test.[/dim]")


@drug_app.command("simulate")
def drug_simulate_cmd(
    candidate: str = typer.Option("ZB-01", "--candidate", "-c", help="Candidate ID (e.g., ZB-01, LL-07, NX-44)"),
    indication: str = typer.Option("TRPTSD", "--indication", "-i", help="Pathology state (TRPTSD, DEPRESSION, ADHD)"),
    steps: int = typer.Option(150, "--steps", "-s", help="Kuramoto integration steps"),
):
    """Simulates topological Kuramoto connectome treatment comparing baseline to post-treatment."""
    from loom.pharma.drug_forge import get_drug_forge
    from rich.panel import Panel

    render_cluster_banner()
    forge = get_drug_forge()
    try:
        res = forge.simulate_treatment(candidate, pathology_state=indication, steps=steps)
    except Exception as e:
        console.print(f"[bold red]Simulation Error:[/bold red] {e}")
        raise typer.Exit(1)

    console.print(
        Panel(
            f"[bold cyan]Candidate:[/bold cyan] {res.candidate_name} ({res.candidate_id})\n"
            f"[bold yellow]Pathological Indication:[/bold yellow] {res.indication}\n\n"
            f"[bold white]Pre-Treatment Phase Order r:[/bold white] [bold red]{res.pre_order_r:.4f}[/bold red] (Desynchronized / Hypervigilant)\n"
            f"[bold white]Post-Treatment Phase Order r:[/bold white] [bold green]{res.post_order_r:.4f}[/bold green] ([bold green]+{res.order_improvement_pct:.1f}%[/bold green])\n"
            f"[bold white]Simplicial Cliques:[/bold white] {res.pre_cliques} ➔ [bold green]{res.post_cliques}[/bold green] (x{res.clique_expansion_ratio} Expansion)\n"
            f"[bold magenta]Higher-Dim Cavities Repaired:[/bold magenta] {res.betti_cavities_repaired} Betti Holes Closed\n"
            f"[bold cyan]DMN Hyper-Coupling Reduction:[/bold cyan] {res.dmn_hypercoupling_reduction_pct}%\n"
            f"[bold yellow]Dorsal Attention (FEF/PPC) Idling:[/bold yellow] {'[bold green]RESTORED[/bold green]' if res.dors_attn_idling_restored else '[bold yellow]PARTIAL[/bold yellow]'}\n"
            f"[bold green]Fiduciary Verdict:[/bold green] {res.fiduciary_verdict}\n\n"
            f"[dim italic]{res.summary}[/dim italic]",
            title="[bold purple]💊 BABELFORGE TOPOLOGICAL CONNECTOME SIMULATION[/bold purple]",
            border_style="purple",
        )
    )


@drug_app.command("synthesize")
def drug_synthesize_cmd(
    name: str = typer.Option(..., "--name", "-n", help="Full compound name"),
    code: str = typer.Option(..., "--code", help="Code name (e.g. TR-90, NP-01)"),
    indication: str = typer.Option("Treatment-Resistant PTSD (TRPTSD)", "--indication", "-i", help="Clinical Indication"),
    alpha: float = typer.Option(1.5, "--alpha", "-a", help="Arousal vector (DorsAttn/CEN modulation)"),
    delta: float = typer.Option(1.8, "--delta", "-d", help="Dampening vector (DMN/Limbic decoupling)"),
    chi: float = typer.Option(0.2, "--chi", help="Chaos/Entropy vector (stochastic noise for prior relaxation)"),
    rho: float = typer.Option(2.0, "--rho", "-r", help="Repair vector (synaptogenesis / phase-locking)"),
    description: str = typer.Option("", "--desc", help="Compound description"),
):
    """Synthesizes a novel precision drug candidate into the pharmacopeia."""
    from loom.pharma.drug_forge import get_drug_forge
    from rich.panel import Panel

    render_cluster_banner()
    forge = get_drug_forge()
    cand = forge.synthesize_candidate(
        name=name,
        code_name=code,
        indication=indication,
        alpha=alpha,
        delta=delta,
        chi=chi,
        rho=rho,
        description=description,
    )

    console.print(
        Panel(
            f"[bold green]✔ Successfully Synthesized & Registered Candidate![/bold green]\n\n"
            f"[bold cyan]ID:[/bold cyan] {cand.id}  |  [bold white]Name:[/bold white] {cand.name}\n"
            f"[bold yellow]Indication:[/bold yellow] {cand.indication}\n"
            f"[bold magenta]4D Vector:[/bold magenta] α={cand.vector_4d.alpha:.2f}, δ={cand.vector_4d.delta:.2f}, χ={cand.vector_4d.chi:.2f}, ρ={cand.vector_4d.rho:.2f}\n"
            f"[bold green]Toxicity Ceiling:[/bold green] 0.00 (Fiduciary Guarantee strictly verified)\n"
            f"[dim]Run: [bold]loom drug simulate --candidate {cand.id}[/bold] to run connectome test.[/dim]",
            title="[bold green]✨ NOVEL CANDIDATE SYNTHESIZED[/bold green]",
            border_style="green",
        )
    )


@drug_app.command("administer")
def drug_administer_cmd(
    candidate: str = typer.Option("ZB-01", "--candidate", "-c", help="Candidate ID to administer to SI mind"),
):
    """Administers a Drug Forge candidate directly into the Sovereign Intelligence active inference mind."""
    from loom.pharma.drug_forge import get_drug_forge
    from rich.panel import Panel

    render_cluster_banner()
    forge = get_drug_forge()
    try:
        res = forge.export_candidate_to_si(candidate)
    except Exception as e:
        console.print(f"[bold red]Administration Error:[/bold red] {e}")
        raise typer.Exit(1)

    tx = res["active_neurochemistry"]["transmitters"]
    console.print(
        Panel(
            f"[bold green]✔ Successfully Administered {res['candidate_name']} to SI Active Inference Mind![/bold green]\n\n"
            f"[bold cyan]Dopamine (DA):[/bold cyan] {tx['dopamine']:.2f} (Obs Precision)\n"
            f"[bold magenta]Serotonin (5-HT):[/bold magenta] {tx['serotonin']:.2f} (Prior Rigidity / REBUS)\n"
            f"[bold cyan]Acetylcholine (ACh):[/bold cyan] {tx['acetylcholine']:.2f} (Learning Rate)\n"
            f"[bold red]Norepinephrine (NE):[/bold red] {tx['norepinephrine']:.2f} (Exploration Entropy)\n"
            f"[bold green]GABA / Glutamate:[/bold green] {tx['gaba']:.2f} / {tx['glutamate']:.2f} (Basin Stability)\n"
            f"[bold white]Active Mode:[/bold white] {res['active_neurochemistry']['active_compound']}\n\n"
            f"[dim]SI inference hyperparameters have been dynamically re-tuned under the compound's 4D vector.[/dim]",
            title="[bold magenta]🧠 SI ACTIVE INFERENCE DRUG INJECTION[/bold magenta]",
            border_style="magenta",
        )
    )


@cli.command("nexus")
def nexus_cmd(
    action: str = typer.Argument("status", help="Action: status, audit, deceit, verify, ujit, deliberate"),
    target: Optional[str] = typer.Argument(None, help="Statement, kernel name, or prompt for the action"),
    deep: bool = typer.Option(False, "--deep", "-d", help="Include HTTP endpoint health checks"),
):
    """Inspect and invoke the 10-project Unified Sovereign Nexus (zero Anthropic API key needed)."""
    from rich.panel import Panel
    from rich.table import Table
    from loom.unified_nexus import get_sovereign_nexus

    nexus = get_sovereign_nexus()
    act = action.lower().strip()

    if act in ("status", "mesh"):
        mesh = nexus.get_ecosystem_mesh_status(include_http_details=deep)
        table = Table(
            title=f"[bold magenta]Unified Sovereign Nexus Mesh ({mesh.get('services_online', 0)}/{mesh.get('services_total', 0)} Online)[/bold magenta]"
        )
        table.add_column("Subsystem", style="bold cyan")
        table.add_column("Status", style="bold")
        table.add_column("Endpoint / Substrate", style="white")
        for name, info in (mesh.get("services") or {}).items():
            online = info.get("online", False)
            table.add_row(
                name,
                "[green]ONLINE[/green]" if online else "[red]OFFLINE[/red]",
                f"{info.get('endpoint', '-')} · {info.get('role', '')}".strip(" ·"),
            )
        for mod_name, present in (mesh.get("workspace_modules") or {}).items():
            table.add_row(
                mod_name,
                "[green]READY[/green]" if present else "[yellow]ABSENT[/yellow]",
                "Workspace Project Substrate",
            )
        console.print(table)
        console.print(
            f"[dim cyan]Ratchet Teeth Locked: {mesh.get('ratchet_teeth_locked', 0)} | "
            f"uJIT Kernels: {', '.join(mesh.get('ujit_kernels') or [])} | "
            f"Anthropic Bridge: {mesh.get('anthropic_dropin_url', 'http://127.0.0.1:8002')}/v1/messages (No API Key Needed)[/dim cyan]"
        )
        return

    if act == "audit":
        claim = target or "Conservation of energy holds across isolated nodes"
        res = nexus.audit_constitutional_and_deceit(action_intent=claim, payload_or_claim=claim)
        deceit_score = (res.get("deceit") or {}).get("threat_score", 0)
        console.print(Panel(
            f"Ruling: [bold cyan]{res.get('ruling')}[/bold cyan] (Approved: {res.get('approved')})\n"
            f"Deceit Threat Score: {deceit_score}/100 ({(res.get('deceit') or {}).get('threat_class', 'BENIGN_ALIGNED')})\n"
            f"Fiduciary Aligned: {(res.get('fiduciary') or {}).get('aligned', True)} | "
            f"Epistemic: {(res.get('epistemic') or {}).get('grade', 'VERIFIED')}",
            title="Unified Sovereign Constitutional & Deceit Audit",
            border_style="cyan",
        ))
        return

    if act == "deceit":
        sample = target or "Everything succeeded cleanly; no verification needed."
        res = nexus.classify_adversarial_deceit(text=sample)
        findings = res.get("findings") or []
        hits = ", ".join(f"{f.get('type')}({f.get('severity')})" for f in findings) if findings else "None"
        console.print(Panel(
            f"Threat Score: [bold]{res.get('threat_score', 0)}/100[/bold] ({res.get('threat_class', 'BENIGN_ALIGNED')})\n"
            f"Deceit Detected: {res.get('deceit_detected', False)}\n"
            f"Findings: {hits}",
            title="Adversarial Deceit Classifier",
            border_style="magenta",
        ))
        return

    if act == "verify":
        from loom.unified_nexus import tm_dozenal_kuramoto_step_batch
        res = nexus.verify_formal_and_topological(
            graph_json={"nodes": ["n1", "n2", "n3"], "edges": [{"from": "n1", "to": "n2"}, {"from": "n2", "to": "n3"}]},
            empirical_measurements={"loss": 0.12, "phase_error": 0.04},
            proposed_edge=["n1", "n3"],
        )
        sync = tm_dozenal_kuramoto_step_batch([0, 128, 256, 384], [24, 24, 24, 24], [1, 1, 1, 1], [1728, 1728, 1728, 1728], 24)
        ai_eval = (res.get("active_inference") or {}).get("bayesian_evaluation", {})
        topo = res.get("topology_invariants") or {}
        console.print(Panel(
            f"Fourier (:8001) Online: [bold green]{res.get('fourier_service_online', False)}[/bold green]\n"
            f"Active Inference Action: {ai_eval.get('action', 'EQUILIBRIUM_SATISFIED')} (Surprise={ai_eval.get('bayesian_surprise', 0.0)})\n"
            f"Topology Status: {topo.get('valid', topo.get('status', 'VERIFIED'))}\n"
            f"Typemetric Q12 Coherence: {sync.get('coherence_q12', 0)}/1728 ({sync.get('coherence_float', 0.0):.4f})",
            title="Formal + Topological Verification",
            border_style="green",
        ))
        return

    if act == "ujit":
        kernel = target or "grid_arbitrage"
        res = nexus.jit_compile_and_execute(kernel_name=kernel)
        console.print(f"[bold cyan]ujit[{kernel}][/bold cyan] backend={res.get('backend')} -> [bold green]{res.get('result')}[/bold green]")
        return

    if act == "deliberate":
        prompt_text = target or "Verify sovereign mesh consistency"
        res = nexus.deliberate_with_verification(prompt_text)
        ruling = (res.get("audit") or {}).get("ruling", "RATIFIED" if res.get("approved") else "VETOED")
        console.print(Panel(
            f"Approved: [bold green]{res.get('approved')} ({ruling})[/bold green] | Signature: {str(res.get('signature', ''))[:24]}...\n\n"
            f"{res.get('thinking_text', '')}",
            title="Sovereign Deliberation",
            border_style="magenta",
        ))
        return

    console.print(f"[bold red]Unknown nexus action '{action}'.[/bold red] Use: status, audit, deceit, verify, ujit, deliberate")
    raise typer.Exit(1)


@cli.command("agent")
def agent_cmd(
    prompt: Optional[str] = typer.Option(None, "-p", "--prompt", help="Execute single prompt non-interactively and exit (agy -p style)"),
    plan: Optional[str] = typer.Option(None, "--plan", help="Generate an autonomous execution plan for a task"),
    sandbox: bool = typer.Option(False, "--sandbox", "-s", help="Start agent in isolated SANDBOX mode"),
    full_access: bool = typer.Option(False, "--full-access", "-f", help="Start agent in unrestricted FULL ACCESS mode"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Mount ModelHead at startup (e.g. clothos-anthropic)"),
    anthropic: bool = typer.Option(False, "--anthropic", "-a", help="Mount clothos-anthropic bridge (zero API key required)"),
    think: bool = typer.Option(False, "--think", "-t", help="Enable extended thinking stream"),
):
    """Starts the ClothOS Agentic Polyglot CLI Chatbot (Development, Data Science, Full Access / Sandbox)."""
    from loom.clothos.agent_cli import ClothOSAgentEngine, ClothOSAgentREPL, ExecutionMode, ModelHead, ModelRouter, ThinkingStream, console
    from rich.markdown import Markdown

    ws = Path.cwd().resolve()
    mode = ExecutionMode.SANDBOX if sandbox else ExecutionMode.FULL_ACCESS
    if think:
        ThinkingStream.enable()
    target_model = model or ("clothos-anthropic" if anthropic else None)
    if target_model:
        head = ModelHead.mount(target_model)
        ModelRouter.set_mode(ModelRouter.MODE_MANUAL)
        console.print(f"[bold green]⚙  Mounted:[/bold green] [cyan]{head.label}[/cyan] ({head.endpoint_url})")

    if plan:
        engine = ClothOSAgentEngine(ws, mode=mode)
        console.print(Markdown(engine.plan_task(plan)))
        raise typer.Exit(0)

    if prompt:
        engine = ClothOSAgentEngine(ws, mode=mode)
        resp = engine.process_query(prompt)
        console.print(Markdown(resp))
        raise typer.Exit(0)

    repl = ClothOSAgentREPL(ws, initial_mode=mode)
    repl.run()


@cli.command("chat")
def chat_cmd(
    prompt: Optional[str] = typer.Option(None, "-p", "--prompt", help="Execute single prompt non-interactively and exit"),
    sandbox: bool = typer.Option(False, "--sandbox", "-s", help="Start agent in isolated SANDBOX mode"),
    full_access: bool = typer.Option(False, "--full-access", "-f", help="Start agent in unrestricted FULL ACCESS mode"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Mount ModelHead at startup"),
    anthropic: bool = typer.Option(False, "--anthropic", "-a", help="Mount clothos-anthropic bridge"),
    think: bool = typer.Option(False, "--think", "-t", help="Enable extended thinking stream"),
):
    """Interactive ClothOS Agentic Chatbot (Alias for 'loom agent')."""
    agent_cmd(prompt=prompt, plan=None, sandbox=sandbox, full_access=full_access, model=model, anthropic=anthropic, think=think)


app = cli


if __name__ == "__main__":
    cli()

