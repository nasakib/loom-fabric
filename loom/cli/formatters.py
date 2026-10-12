"""
Rich Terminal UI Formatters for Loom Fabric.

Provides visual dashboards, colored hardware tables, sharding allocation bars,
and cluster health spinners.
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

console = Console()


def render_hardware_table(hardware_dict: dict) -> Table:
    """Builds a rich table of detected accelerators and system memory."""
    table = Table(title="[bold cyan]Loom Fabric Cluster Hardware Diagnostic[/bold cyan]", show_header=True)
    table.add_column("Node / Device", style="bold white", width=22)
    table.add_column("Type / Architecture", style="cyan", width=20)
    table.add_column("Total Memory", style="green", justify="right", width=14)
    table.add_column("Free / Usable", style="bright_green", justify="right", width=14)
    table.add_column("Engine Backend", style="magenta", width=16)

    # GPUs
    for gpu in hardware_dict.get("gpus", []):
        table.add_row(
            gpu.get("name", "Unknown GPU"),
            f"{gpu.get('vendor', '').upper()} ({gpu.get('driver_version', 'N/A')})",
            f"{gpu.get('total_vram_mb', 0):,.0f} MB",
            f"{gpu.get('free_vram_mb', 0):,.0f} MB",
            gpu.get("backend", "llama.cpp"),
        )

    # Host RAM
    host_info = hardware_dict.get("host", {})
    table.add_row(
        f"Host Node ({hardware_dict.get('node_name', 'Local')})",
        f"System DDR4/5 ({host_info.get('cpu_cores_logical', 0)} vCPUs)",
        f"{host_info.get('total_ram_mb', 0):,.0f} MB",
        f"{host_info.get('available_ram_mb', 0):,.0f} MB",
        "Host RAM Tier 3",
    )

    return table


def render_sharding_table(plan_dict: dict) -> Table:
    """Builds a rich table visualizing calculated layer splits."""
    table = Table(title="[bold yellow]Zero-OOM Layer Sharding Plan[/bold yellow]", show_header=True)
    table.add_column("Compute Tier", style="bold white", width=18)
    table.add_column("Target Hardware", style="cyan", width=24)
    table.add_column("Assigned Layers", style="bright_yellow", justify="center", width=18)
    table.add_column("VRAM / RAM Footprint", style="bright_green", justify="right", width=20)
    table.add_column("Backend", style="magenta", width=14)

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
    """Renders the Loom Fabric terminal banner."""
    banner_text = Text()
    banner_text.append("LOOM FABRIC ", style="bold magenta")
    banner_text.append("v0.1.0\n", style="bold bright_magenta")
    banner_text.append("Heterogeneous Distributed AI Compute Fabric (Ray + Stitch + Torque + Loom)\n", style="dim white")
    banner_text.append("NVIDIA RTX 3060 (CUDA) + AMD RX 580 (Vulkan) + AMD Ryzen 7 7730U Head", style="bright_magenta")
    console.print(Panel(banner_text, border_style="magenta"))
