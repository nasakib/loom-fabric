"""
Rich Terminal UI Formatters for Loom Fabric Commander.

Botanical Meadow & Floral Breeze Edition (Air, Breeze, Lawns, Flowers, Plants)
with mandated Royal Purple accents (Lavender, Wisteria, Amethyst).
Windows cp1252-safe with UTF-8 stream reconfiguration.
"""

import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

# Guarantee UTF-8 stream handling across Windows console hosts
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

console = Console(force_terminal=True, highlight=False)


def render_hardware_table(hardware_dict: dict) -> Table:
    """Builds a rich botanical table of detected accelerators and system memory."""
    table = Table(
        title="[bold green]Loom Fabric Cluster Accelerator Flora[/bold green] [bold magenta]*[/bold magenta]",
        show_header=True,
        border_style="green",
        header_style="bold magenta",
    )
    table.add_column("Node / Device", style="bold white", width=22)
    table.add_column("Architecture", style="bright_cyan", width=20)
    table.add_column("Total VRAM", style="magenta", justify="right", width=14)
    table.add_column("Free Margin", style="bold green", justify="right", width=14)
    table.add_column("Engine Backend", style="bright_magenta", width=18)

    # GPUs
    for gpu in hardware_dict.get("gpus", []):
        table.add_row(
            gpu.get("name", "Unknown GPU"),
            f"{gpu.get('vendor', '').upper()} ({gpu.get('driver_version', 'N/A')})",
            f"{gpu.get('total_vram_mb', 0):,.0f} MB",
            f"{gpu.get('free_vram_mb', 0):,.0f} MB",
            f"{gpu.get('backend', 'llama.cpp')}",
        )

    # Host RAM
    host_info = hardware_dict.get("host", {})
    table.add_row(
        f"Host Node ({hardware_dict.get('node_name', 'Local')})",
        f"DDR System ({host_info.get('cpu_cores_logical', 0)} vCPUs)",
        f"{host_info.get('total_ram_mb', 0):,.0f} MB",
        f"{host_info.get('available_ram_mb', 0):,.0f} MB",
        "Host RAM Tier 2/3",
    )

    return table


def render_sharding_table(plan_dict: dict) -> Table:
    """Builds a rich table visualizing calculated zero-OOM layer splits."""
    table = Table(
        title="[bold magenta]Zero-OOM Layer Allocation & Triage Matrix[/bold magenta] [bold green]*[/bold green]",
        show_header=True,
        border_style="green",
        header_style="bold bright_magenta",
    )
    table.add_column("Compute Tier", style="bold white", width=18)
    table.add_column("Target Silicon", style="bright_cyan", width=24)
    table.add_column("Assigned Layers", style="bright_yellow", justify="center", width=20)
    table.add_column("Memory Footprint", style="bold green", justify="right", width=20)
    table.add_column("Engine Backend", style="magenta", width=16)

    allocations = plan_dict.get("allocations", [])
    for alloc in allocations:
        layer_range = f"Layers {alloc.get('layer_start_idx', 0)} - {alloc.get('layer_end_idx', 0)} ({alloc.get('layer_count', 0)} total)"
        vram_str = f"{alloc.get('total_memory_mb', 0):,.0f} MB"
        table.add_row(
            alloc.get("device_backend", ""),
            alloc.get("device_name", ""),
            layer_range,
            vram_str,
            alloc.get("device_backend", ""),
        )

    return table


def render_cluster_banner() -> None:
    """Renders the Loom Fabric Commander botanical breeze terminal banner."""
    banner_text = Text()
    banner_text.append("LOOM FABRIC COMMANDER ", style="bold green")
    banner_text.append("v0.1.0 [Flora & Breeze]\n", style="bold bright_magenta")
    banner_text.append("Sovereign Heterogeneous AI Compute Fabric — Precursor to ClothOS\n", style="dim white")
    banner_text.append("Topology: ", style="bright_cyan")
    banner_text.append("RTX 3060 (12GB CUDA) + RX 580 (8GB Vulkan) + Ryzen 7 7730U Head (16 vCPUs)\n", style="white")
    banner_text.append("Invariants: ", style="magenta")
    banner_text.append("Zero-Trust Torque Enclave [Scrubbing] * Zero-OOM MMU Allocator * Air-Gap Moltbook", style="bold bright_magenta")
    console.print(Panel(banner_text, border_style="green", subtitle="[dim cyan]~ fresh meadow zephyr & wisteria accents ~[/dim cyan]"))
