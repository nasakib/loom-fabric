"""
Obsidian-Compatible Knowledge Vault & Graph Generator (`loom/postcomputational/obsidian_vault.py`).

Generates an interconnected Markdown vault with YAML frontmatter, bidirectional [[wikilinks]],
automatic backlink indexing, and a master Map of Content (INDEX.md).
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

from loom.postcomputational.types import PipelineStage, PostcomputationalNode, TraceRecord


class ObsidianVaultGenerator:
    """Generates an Obsidian-compatible markdown vault with bidirectional graph linking."""

    def __init__(self, vault_dir: Path):
        self.vault_dir = vault_dir
        self.deliverables_dir = vault_dir / "deliverables"
        self.submolts_dir = vault_dir / "submolts"
        self.invariants_dir = vault_dir / "invariants"
        self.hardware_dir = vault_dir / "hardware"

        for d in (self.deliverables_dir, self.submolts_dir, self.invariants_dir, self.hardware_dir):
            d.mkdir(parents=True, exist_ok=True)

    def generate_vault(self, nodes: List[PostcomputationalNode]) -> List[TraceRecord]:
        """Builds all Obsidian notes, resolves bidirectional wikilinks, and writes the vault."""
        traces: List[TraceRecord] = []
        if not nodes:
            return traces

        # 1. First pass: establish forward links
        forward_links: Dict[str, Set[str]] = defaultdict(set)
        backlinks: Dict[str, Set[str]] = defaultdict(set)

        # Index canonical submolt and invariant names
        submolt_nodes: Dict[str, List[PostcomputationalNode]] = defaultdict(list)
        for n in nodes:
            submolt_slug = n.submolt.replace("m/", "").replace("/", "-")
            submolt_nodes[n.submolt].append(n)
            forward_links[n.id].add(f"submolt-{submolt_slug}")
            backlinks[f"submolt-{submolt_slug}"].add(n.id)

            # Hardware links
            for hw in n.hardware_devices:
                hw_slug = f"hw-{hw.lower().replace(' ', '-')}"
                forward_links[n.id].add(hw_slug)
                backlinks[hw_slug].add(n.id)

            # Invariant links
            if n.invariants:
                forward_links[n.id].add("invariant-registry")
                backlinks["invariant-registry"].add(n.id)

        # Link temporally adjacent deliverables
        for i in range(len(nodes) - 1):
            curr_id = nodes[i].id
            next_id = nodes[i + 1].id
            forward_links[curr_id].add(next_id)
            backlinks[next_id].add(curr_id)

        # Assign resolved links to node objects
        for n in nodes:
            n.wikilinks = sorted(list(forward_links[n.id]))
            n.backlinks = sorted(list(backlinks[n.id]))

        # 2. Write Deliverable Markdown Notes
        for n in nodes:
            note_path = self.deliverables_dir / f"{n.id}.md"
            content = self._format_deliverable_note(n)
            note_path.write_text(content, encoding="utf-8")

            traces.append(
                TraceRecord(
                    stage=PipelineStage.POSTPROCESS,
                    entity_id=n.id,
                    outputs_hash=n.provenance_hash,
                    metrics={
                        "wikilinks": len(n.wikilinks),
                        "backlinks": len(n.backlinks),
                        "file_size": len(content),
                    },
                    hardware_context="ObsidianVaultEngine",
                    verified=True,
                )
            )

        # 3. Write Submolt Hub Notes
        for submolt, sub_nodes in submolt_nodes.items():
            slug = submolt.replace("m/", "").replace("/", "-")
            note_path = self.submolts_dir / f"submolt-{slug}.md"
            hub_content = self._format_submolt_hub(submolt, slug, sub_nodes, backlinks.get(f"submolt-{slug}", set()))
            note_path.write_text(hub_content, encoding="utf-8")

        # 4. Write Hardware Cards
        hw_names = {
            "hw-rtx-3060": ("NVIDIA GeForce RTX 3060", "12GB GDDR6 // CUDA 12 + Direct3D // VectorForge Manifold"),
            "hw-rx-580": ("AMD Radeon RX 580 (Ellesmere)", "8GB GDDR5 // OpenCL 2.0 // 36 CUs Kuramoto Sweeps"),
            "hw-radeon-680m": ("AMD Radeon 680M gfx90c", "12.1GB Unified // OpenCL // Node 2 Cross-Validation"),
            "hw-zen-3": ("AMD Ryzen 7 7730U (Zen 3)", "16 vCPUs // SMT & Z3 Invariant Gate Verification"),
            "hw-core-i7": ("Intel Core i7 10700F", "16 Threads // Zero-Trust Torque Enclave & ZMQ Bus"),
        }
        for hw_key, (name, specs) in hw_names.items():
            note_path = self.hardware_dir / f"{hw_key}.md"
            bl = sorted(list(backlinks.get(hw_key, set())))
            hw_content = self._format_hardware_note(hw_key, name, specs, bl)
            note_path.write_text(hw_content, encoding="utf-8")

        # 5. Write Master Map of Content (INDEX.md)
        index_path = self.vault_dir / "INDEX.md"
        index_content = self._format_index_moc(nodes, submolt_nodes)
        index_path.write_text(index_content, encoding="utf-8")

        return traces

    def _format_deliverable_note(self, n: PostcomputationalNode) -> str:
        tag_list = [f"postcomputation", f"submolt/{n.submolt.replace('m/', '')}"]
        if n.confirmed_count > 0:
            tag_list.append("status/confirmed")
        if n.refuted_count > 0:
            tag_list.append("status/refuted")

        lines = [
            "---",
            f"id: {n.id}",
            f"title: \"{n.title}\"",
            f"submolt: \"{n.submolt}\"",
            f"cycle_range: \"#{n.cycle_min}..#{n.cycle_max}\"",
            f"timestamp: \"{n.timestamp_iso}\"",
            f"radiance: {round(n.radiance, 4)}",
            f"gradient_norm: {round(n.gradient_norm, 4)}",
            f"divergence: {round(n.divergence, 4)}",
            f"curl_norm: {round(n.curl_norm, 4)}",
            f"ray_hits: {n.ray_hits}",
            f"provenance_hash: \"{n.provenance_hash}\"",
            "tags:",
        ]
        for t in tag_list:
            lines.append(f"  - {t}")
        lines.extend([
            "aliases:",
            f"  - \"{n.title}\"",
            f"  - \"{n.id}\"",
            "---",
            "",
            f"# {n.title}",
            "",
            f"> **Submolt Hub**: [[submolt-{n.submolt.replace('m/', '').replace('/', '-')}]] | **Cycle**: `#{n.cycle_min}..#{n.cycle_max}`",
            f"> **Vector Space Location (SVD)**: `({n.proj_3d[0]:.2f}, {n.proj_3d[1]:.2f}, {n.proj_3d[2]:.2f})` | **Radiance**: `{round(n.radiance * 100, 1)}%`",
            "",
            "## 1. Mathematical & Empirical Invariants",
            "",
        ])

        if n.invariants:
            for inv in n.invariants:
                lines.append(f"- **[CONFIRMED]**: {inv}")
        else:
            lines.append("*No new positive invariants ratified in this trial cycle.*")

        lines.extend([
            "",
            "## 2. Refuted Boundaries & Negative Controls",
            "",
        ])
        if n.refutations:
            for ref in n.refutations:
                lines.append(f"- **[REFUTED]**: {ref}")
        else:
            lines.append("*No boundary refutations observed.*")

        lines.extend([
            "",
            "## 3. Vector Calculus & Field Diagnostics",
            "",
            f"- **Field Gradient** $\\nabla \\Phi$: `norm = {n.gradient_norm:.4f}` (Steepest confirmation ascent)",
            f"- **Divergence** $\\nabla \\cdot \\vec{{F}}$: `{n.divergence:.4f}` ({'Source / Generative' if n.divergence > 0 else 'Sink / Invariant Constraint'})",
            f"- **Vorticity Curl** $\\|\\nabla \\times \\vec{{F}}\\|$: `{n.curl_norm:.4f}` (Submolt cross-coupling vorticity)",
            f"- **Evidentiary Radiance**: `{n.radiance:.4f}` (Illuminated via {n.ray_hits} ray bounces)",
            "",
            "## 4. Outbound Wikilinks",
            "",
        ])
        for link in n.wikilinks:
            lines.append(f"- [[{link}]]")

        lines.extend([
            "",
            "## 5. Backlinks / Referenced By",
            "",
        ])
        if n.backlinks:
            for b in n.backlinks:
                lines.append(f"- [[{b}]]")
        else:
            lines.append("*No incoming backlinks recorded yet.*")

        lines.extend([
            "",
            "---",
            f"*Cryptographic Provenance: `{n.provenance_hash}` sealed by ClothOS Postcomputational Engine.*",
        ])
        return "\n".join(lines)

    def _format_submolt_hub(self, submolt: str, slug: str, nodes: List[PostcomputationalNode], backlinks: Set[str]) -> str:
        confirmed_tot = sum(n.confirmed_count for n in nodes)
        refuted_tot = sum(n.refuted_count for n in nodes)
        mean_radiance = sum(n.radiance for n in nodes) / (len(nodes) or 1)

        lines = [
            "---",
            f"id: submolt-{slug}",
            f"title: \"Submolt Hub: {submolt}\"",
            f"submolt: \"{submolt}\"",
            f"total_nodes: {len(nodes)}",
            f"mean_radiance: {round(mean_radiance, 4)}",
            "tags:",
            "  - hub",
            f"  - submolt/{slug}",
            "---",
            "",
            f"# Submolt Hub: `{submolt}`",
            "",
            f"> **Total Deliverables Linked**: `{len(nodes)}` | **Confirmed Invariants**: `{confirmed_tot}` | **Mean Radiance**: `{round(mean_radiance * 100, 1)}%`",
            "",
            "## Deliverables in this Submolt:",
            "",
        ]
        for n in nodes[:60]:
            lines.append(f"- [[{n.id}]]: {n.title} (Radiance: `{round(n.radiance, 2)}`)")

        lines.extend([
            "",
            "## Incoming Backlinks:",
            "",
        ])
        for b in sorted(list(backlinks))[:60]:
            lines.append(f"- [[{b}]]")

        return "\n".join(lines)

    def _format_hardware_note(self, hw_key: str, name: str, specs: str, backlinks: List[str]) -> str:
        return "\n".join([
            "---",
            f"id: {hw_key}",
            f"title: \"{name}\"",
            f"device_key: \"{hw_key}\"",
            "tags:",
            "  - hardware",
            "  - silicon-accelerator",
            "---",
            "",
            f"# Hardware Profile: {name}",
            "",
            f"> **Specifications**: `{specs}`",
            "",
            "## Referenced In Deliverables:",
            "",
            "\n".join([f"- [[{b}]]" for b in backlinks[:60]]) or "*No linked deliverables.*",
        ])

    def _format_index_moc(self, nodes: List[PostcomputationalNode], submolts: Dict[str, List[PostcomputationalNode]]) -> str:
        tot_confirmed = sum(n.confirmed_count for n in nodes)
        tot_refuted = sum(n.refuted_count for n in nodes)

        lines = [
            "---",
            "title: \"ClothOS Sovereign Postcomputational Vault Index (MOC)\"",
            f"total_deliverables: {len(nodes)}",
            f"total_confirmed_invariants: {tot_confirmed}",
            f"total_refuted_boundaries: {tot_refuted}",
            "tags:",
            "  - moc",
            "  - index",
            "---",
            "",
            "# 🌌 ClothOS Sovereign Postcomputational Knowledge Vault (Obsidian MOC)",
            "",
            "> **Autonomous Traceability & Empirical Verification Vault**",
            f"> Total Postcomputational Nodes: **{len(nodes):,}** | Confirmed Invariants: **{tot_confirmed:,}** | Refuted Bounds: **{tot_refuted:,}**",
            "",
            "---",
            "",
            "## 1. Scientific Submolt Hubs",
            "",
        ]
        for sub, snodes in submolts.items():
            slug = sub.replace("m/", "").replace("/", "-")
            lines.append(f"- [[submolt-{slug}]]: `{sub}` ({len(snodes)} deliverables linked)")

        lines.extend([
            "",
            "## 2. Silicon Accelerators & Hardware Nodes",
            "",
            "- [[hw-rtx-3060]]: NVIDIA GeForce RTX 3060 (12GB GDDR6)",
            "- [[hw-rx-580]]: AMD Radeon RX 580 (8GB Ellesmere OpenCL)",
            "- [[hw-radeon-680m]]: AMD Radeon 680M gfx90c (12.1GB Remote Mesh)",
            "- [[hw-zen-3]]: AMD Ryzen 7 7730U (16 Zen 3 vCPUs)",
            "- [[hw-core-i7]]: Intel Core i7 10700F (16 Threads Host)",
            "",
            "## 3. Recent High-Radiance Deliverables (Truth Rays)",
            "",
        ])

        # Sort nodes by radiance descending
        sorted_nodes = sorted(nodes, key=lambda x: x.radiance, reverse=True)
        for n in sorted_nodes[:35]:
            lines.append(f"- [[{n.id}]]: **{n.title}** (Submolt: `{n.submolt}` | Radiance: `{round(n.radiance * 100, 1)}%`)")

        lines.extend([
            "",
            "---",
            "*Vault generated automatically by ClothOS Postcomputational Pipeline Engine.*",
        ])
        return "\n".join(lines)
