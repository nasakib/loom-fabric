# Copyright (c) 2026 Najmos Sakib. All rights reserved.

# Proprietary and confidential. Commercial distribution prohibited.

"""

ClothOS Directory Auto-Context & Scientific Action Recommender

==============================================================

Profiles the current working directory upon startup, extracting AST topology,

project taxonomy, git repository state, and synthesizing actionable engineering

recommendations in an 8-bit retro-scientific laboratory format.

"""



from __future__ import annotations



import os

import shutil

import subprocess

from pathlib import Path

from typing import Dict, Any, List, Optional

from rich.table import Table

from rich.panel import Panel

from rich.console import Console



console = Console(legacy_windows=False)





class DirectoryContextEngine:

    """Performs zero-config reconnaissance on any folder and generates actionable next steps."""



    CODE_EXTENSIONS = {

        ".py": "Python",

        ".rs": "Rust",

        ".ts": "TypeScript",

        ".js": "JavaScript",

        ".c": "C",

        ".cpp": "C++",

        ".go": "Go",

        ".sh": "Shell",

        ".ps1": "PowerShell",

        ".html": "HTML5",

        ".json": "JSON",

        ".toml": "TOML",

        ".yaml": "YAML",

        ".yml": "YAML",

    }



    IGNORE_DIRS = {

        ".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache",

        "dist", "build", "target", ".idea", ".vscode", "egg-info", "artifacts",

        "deliverables", "data", "vault", "sovereign_vault", "traces", "exports",

        ".clothos_sandbox", ".agent", ".sandbox", "clothos_root", "platforms"

    }



    @classmethod

    def scan_directory(cls, workspace_root: Path, max_depth: int = 4) -> Dict[str, Any]:

        """Scans the directory structure swiftly, detecting frameworks, LOC, git status, and test suites."""

        workspace = workspace_root.resolve()



        # 1. Project Taxonomy Identification

        manifests = []

        if (workspace / "pyproject.toml").exists() or (workspace / "requirements.txt").exists():

            manifests.append("Python")

        if (workspace / "Cargo.toml").exists():

            manifests.append("Rust")

        if (workspace / "package.json").exists():

            manifests.append("Node/TypeScript")

        if (workspace / "CMakeLists.txt").exists():

            manifests.append("C/C++")

        if (workspace / "go.mod").exists():

            manifests.append("Go")



        project_type = " / ".join(manifests) if manifests else "General Source Workspace"



        # 2. File & Line Enumeration with depth limiter

        lang_counts: Dict[str, int] = {}

        total_files = 0

        total_lines = 0

        test_files = []



        base_depth = len(workspace.parts)



        try:

            for root, dirs, files in os.walk(workspace):

                cur_depth = len(Path(root).parts) - base_depth

                if cur_depth >= max_depth:

                    dirs.clear()

                    continue



                dirs[:] = [d for d in dirs if d not in cls.IGNORE_DIRS and not d.startswith(".")]



                for f in files:

                    ext = Path(f).suffix.lower()

                    if ext in cls.CODE_EXTENSIONS:

                        lang = cls.CODE_EXTENSIONS[ext]

                        lang_counts[lang] = lang_counts.get(lang, 0) + 1

                        total_files += 1



                        if f.startswith("test_") or f.endswith("_test.py") or "test" in root.lower():

                            test_files.append(os.path.join(root, f))



                        # Sample line counts up to 400 files for instantaneous startup

                        if total_files <= 400:

                            f_path = os.path.join(root, f)

                            try:

                                with open(f_path, "r", encoding="utf-8", errors="ignore") as fh:

                                    total_lines += sum(1 for _ in fh)

                            except Exception:

                                pass

        except Exception:

            pass



        # 3. Git Repository Health & State

        git_info: Dict[str, Any] = {"is_repo": False, "branch": "unknown", "dirty_files": 0, "last_commit": "None"}

        if (workspace / ".git").exists() and shutil.which("git"):

            try:

                res_b = subprocess.run(["git", "branch", "--show-current"], cwd=str(workspace), capture_output=True, text=True, timeout=2)

                if res_b.returncode == 0:

                    git_info["is_repo"] = True

                    git_info["branch"] = res_b.stdout.strip() or "detached"



                res_s = subprocess.run(["git", "status", "--porcelain"], cwd=str(workspace), capture_output=True, text=True, timeout=2)

                if res_s.returncode == 0:

                    lines = [ln for ln in res_s.stdout.splitlines() if ln.strip()]

                    git_info["dirty_files"] = len(lines)



                res_l = subprocess.run(["git", "log", "-1", "--pretty=format:%s (%ar)"], cwd=str(workspace), capture_output=True, text=True, timeout=2)

                if res_l.returncode == 0:

                    git_info["last_commit"] = res_l.stdout.strip()

            except Exception:

                pass



        # 4. Synthesize Actionable Recommendations

        recommendations = []

        if git_info.get("dirty_files", 0) > 0:

            recommendations.append((

                "/git status",

                f"Audit and verify {git_info['dirty_files']} uncommitted modifications before advancing"

            ))



        if test_files:

            if "Python" in project_type:

                recommendations.append(("!pytest -v", f"Execute test suite ({len(test_files)} test files discovered)"))

            elif "Rust" in project_type:

                recommendations.append(("!cargo test", "Run Cargo verification and benchmark tests"))

            elif "Node" in project_type:

                recommendations.append(("!npm test", "Run JavaScript/TypeScript test runner"))

        else:

            recommendations.append(("/plan test_scaffold", "Synthesize unit test framework for codebase modules"))



        # Benchmark / Tool accuracy recommendation

        recommendations.append(("/bfcl", "Run Berkeley Function Calling Leaderboard accuracy verification"))



        # Documentation check

        if (workspace / "README.md").exists():

            recommendations.append(("/cat README.md", "Inspect architectural design document and subsystem manifests"))

        else:

            recommendations.append(("/plan architecture_doc", "Draft comprehensive architectural README.md"))



        # Hardware / GPU recommendation

        recommendations.append(("/gpu", "Inspect real-time GPU VRAM allocation and compute engines"))



        return {

            "workspace_name": workspace.name or str(workspace),

            "workspace_path": str(workspace),

            "project_type": project_type,

            "total_files": total_files,

            "total_lines": total_lines,

            "primary_languages": sorted(lang_counts.items(), key=lambda x: x[1], reverse=True)[:4],

            "test_file_count": len(test_files),

            "git_info": git_info,

            "recommendations": recommendations[:5]

        }



    @classmethod

    def render_context_panel(cls, workspace_root: Path) -> Panel:

        """Renders the professional directory context & recommendation card with theme support."""

        info = cls.scan_directory(workspace_root)



        theme_name = "production"
        try:
            from loom.clothos.theme import ThemeManager
            theme = ThemeManager.get_active()
            theme_name = theme.name
        except Exception:
            theme = None

        if theme_name == "scientific":
            prim, sec, acc, warn, border = "#00ff66", "#00f0ff", "#38bdf8", "#ffb000", "#00f0ff"
            title = "[bold #00ff66]■ CLOTHOS//SCIENTIFIC AUTO-RECONNAISSANCE ■[/bold #00ff66]"
            sub = "[dim #00f0ff]► Directory Context Engine · Press [Ctrl+C] Steer · Type command to execute ◄[/dim #00f0ff]"
        elif theme_name == "forest":
            prim, sec, acc, warn, border = "#22c55e", "#a855f7", "#c084fc", "#f59e0b", "#166534"
            title = "[bold #22c55e]■ CLOTHOS AUTO-RECONNAISSANCE & CODEBASE CONTEXT ■[/bold #22c55e]"
            sub = "[dim #a855f7]► Directory Context Engine · Press [Ctrl+C] Steer · Type command to execute ◄[/dim #a855f7]"
        else:
            # Production Industrial Slate theme (Executive, Minimalist)
            prim, sec, acc, warn, border = "#38bdf8", "#94a3b8", "#cbd5e1", "#f59e0b", "#334155"
            title = "[bold #38bdf8]■ REPOSITORY AUTO-RECONNAISSANCE & RUNTIME CONTEXT ■[/bold #38bdf8]"
            sub = "[dim #64748b]Directory Context Engine · Press [Ctrl+C] Steer · Type command to execute[/dim #64748b]"



        grid = Table.grid(padding=(0, 2))

        grid.add_column(style=f"bold {sec}", width=24)

        grid.add_column(style="bold white")



        # 1. Workspace Identity

        grid.add_row("[SYS//WORKSPACE]", f"[bold {prim}]{info['workspace_name']}[/bold {prim}] [dim white]({info['workspace_path']})[/dim white]")



        # 2. Project Classification

        grid.add_row("[AST//TAXONOMY]", f"[bold white]{info['project_type']}[/bold white]")



        # 3. Source Scale & Language Distribution

        langs_str = ", ".join([f"[{acc}]{l}[/{acc}] ({c} files)" for l, c in info['primary_languages']]) or "Text/Data"

        grid.add_row("[AST//SCALE]", f"[bold {prim}]{info['total_files']}[/bold {prim}] source files · [bold white]{info['total_lines']:,}[/bold white] LOC • {langs_str}")



        # 4. Git Version Control Telemetry

        git = info['git_info']

        if git["is_repo"]:

            dirty_badge = f"[bold {warn}]{git['dirty_files']} dirty files[/bold {warn}]" if git["dirty_files"] > 0 else f"[bold {prim}]Clean Tree[/bold {prim}]"

            last_c = f" · Last: \"{git['last_commit'][:38]}…\"" if git["last_commit"] != "None" else ""

            grid.add_row("[VCS//BRANCH]", f"[bold {sec}]{git['branch']}[/bold {sec}] [{dirty_badge}]{last_c}")

        else:

            grid.add_row("[VCS//BRANCH]", "[dim white]Non-git workspace (local sandbox directory)[/dim white]")



        # 5. Verification Test Harness

        test_badge = f"[bold {prim}]{info['test_file_count']} test suites active[/bold {prim}]" if info['test_file_count'] > 0 else f"[bold {warn}]No unit tests located[/bold {warn}]"

        grid.add_row("[TEST//HARNESS]", test_badge)



        # 6. Action Recommendations Header

        grid.add_row("", "")

        grid.add_row("[ACTION RECONNAISSANCE]", f"[dim {sec}]High-leverage engineering tasks detected for this directory:[/dim {sec}]")



        # Enumerate concrete recommendations

        for idx, (cmd, desc) in enumerate(info["recommendations"], 1):

            grid.add_row(

                f"  [{idx}] [bold {prim}]{cmd}[/bold {prim}]",

                f"[bold white]{desc}[/bold white]"

            )



        return Panel(

            grid,

            title=title,

            subtitle=sub,

            border_style=border,

            padding=(0, 1)

        )

