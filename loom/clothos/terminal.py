# Copyright (c) 2026 Najmos Sakib. All rights reserved.

# Proprietary and confidential. Commercial distribution prohibited.

"""

ClothOS High-Performance Terminal Engine (`loom/clothos/terminal.py`).



Transforms the ClothOS CLI into a commercial-grade 3rd-party terminal:

- Starship / Warp-style Powerline Prompt with git status, working directory, and cluster telemetry.

- Fish-style Autosuggestions (ghost text completion from history).

- Context-Aware Tab Completion (slash commands, filesystem paths, cluster nodes, models, git verbs).

- Persistent Session History with Ctrl+R reverse search.

- Dynamic Bottom Toolbar HUD (CPU, RAM, Mesh status, shortcut hints).

- Syntax Highlighting for code, shell pipelines, and parameters.

- Built-in Rich Terminal Utilities: cat with syntax highlighting, colorized ls/dir, neofetch-style sysinfo, ps, bench.

"""



from __future__ import annotations



import os

import sys

import re

import time

import shutil

import socket

import subprocess

from datetime import datetime

from pathlib import Path

from typing import Any, Dict, List, Optional, Tuple, Iterable



# prompt_toolkit

try:

    from prompt_toolkit import PromptSession

    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

    from prompt_toolkit.completion import Completer, Completion, PathCompleter

    from prompt_toolkit.document import Document

    from prompt_toolkit.formatted_text import HTML, to_formatted_text

    from prompt_toolkit.history import FileHistory

    from prompt_toolkit.key_binding import KeyBindings

    from prompt_toolkit.styles import Style

    HAS_PROMPT_TOOLKIT = True

except ImportError:
    HAS_PROMPT_TOOLKIT = False
    Completer = object
    Document = Any

    class HTML:
        def __init__(self, value: str = "") -> None:
            self.value = value
        def __str__(self) -> str:
            return self.value

    def to_formatted_text(value: Any) -> Any:
        return value

    class Style:
        @staticmethod
        def from_dict(mapping: Dict[str, str]) -> Dict[str, str]:
            return dict(mapping)

    class KeyBindings:
        def add(self, *args: Any, **kwargs: Any):
            def _decorator(fn: Any) -> Any:
                return fn
            return _decorator

    class PromptSession:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass
        def prompt(self, message: Any = "", **kwargs: Any) -> str:
            return input(getattr(message, "value", str(message)))

    class FileHistory:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

    class AutoSuggestFromHistory:
        pass

    class Completion:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            self.args = args
            self.kwargs = kwargs

    class PathCompleter:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass
        def get_completions(self, *args: Any, **kwargs: Any) -> Iterable[Any]:
            return []



try:

    from loom.clothos.activity_tracker import CurrentlyDoing

except ImportError:

    class CurrentlyDoing:

        @classmethod

        def get(cls): return "Idle / Ready"

        @classmethod

        def get_phase(cls): return "IDLE"

        @classmethod

        def get_elapsed_s(cls): return 0.0



# Ensure UTF-8 output streams on Windows

if sys.platform == "win32":

    try:

        if hasattr(sys.stdout, "reconfigure"):

            sys.stdout.reconfigure(encoding="utf-8", errors="replace")

        if hasattr(sys.stderr, "reconfigure"):

            sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    except Exception:

        pass



# Rich

from rich.console import Console

from rich.table import Table

from rich.panel import Panel

from rich.syntax import Syntax

from rich.text import Text

from rich import box



try:

    import psutil

    HAS_PSUTIL = True

except ImportError:

    HAS_PSUTIL = False



console = Console(legacy_windows=False)



# ── Available Slash Commands & Descriptions for Autocompletion ───────────────

SLASH_COMMAND_DOCS = {
    "/nexus": "Unified Sovereign Nexus 10-project mesh, Ratchet chain & deliberate mode",
    "/mesh": "Display Unified Sovereign Nexus mesh telemetry",
    "/deceit": "Scan text/prompt for adversarial deceit & injection vectors",
    "/verify": "Formal Z3/Kirchhoff + Active Inference + Typemetric Q12 Kuramoto verify",
    "/ujit": "Compile and run bare-metal Universal JIT native kernel",
    "/tmsync": "Typemetric Dozenal Q12 Kuramoto phase-lock synchronization",
    "/anthropic": "Mount or query Sovereign Anthropic :8002/v1/messages (zero API key)",
    "/tpu": "Inspect hardware systolic array & TPU MXU telemetry",
    "/toolbox": "Inspect live status across all 11 precision machine tools",
    "/weave": "Execute top-level cognitive weave across Loom harness",
    "/audit": "Epistemic reality guard (The Bullshit Meter)",
    "/mode": "Display active execution mode (WCOS Guest vs Bare-Metal Sovereign)",

    "/help": "Show full command reference and keyboard shortcuts",

    "/teach": "Teach the model computer wisdom, Windows CMD rules, and hardware engineering invariants",

    "/wisdom": "View ratified computer wisdom curriculum, Windows translation matrix, and hardware profile",

    "/curriculum": "Inspect ratified computer wisdom axioms and epistemic training dataset",

    "/context": "Zero-config auto-reconnaissance & action recommendations for current directory",

    "/recs": "View directory context and engineering recommendations",

    "/recon": "Run directory AST, LOC and Git health scan",

    "/bfcl": "Berkeley Function Calling Leaderboard accuracy verification benchmark",

    "/palette": "Show interactive categorized command palette and cheat sheet",

    "/cheatsheet": "Display fast visual command reference cheat sheet",

    "/copy": "Copy last agent response or code block to system clipboard",

    "/export": "Export current session conversation to markdown file",

    "/cluster": "Display real-time dual-GPU, RAM and storage telemetry HUD",

    "/gpu": "Inspect GPU VRAM, compute engines and hardware metrics",

    "/sessions": "List, browse, or resume saved conversation sessions",

    "/session": "Session manager (/session new, /session open ID)",

    "/steer": "Inject active operator steering vector into running task",

    "/doing": "View real-time Currently [doing] phase and elapsed telemetry",

    "/glow": "Display live sovereign glowing aura telemetry HUD",

    "/aura": "View live cognitive aura and shimmering activity wave",

    "/abort": "Immediately abort active task and retain session history",

    "/monitors": "Inspect multi-node monitor arrangement and switch KVM cursor",

    "/kvm": "Switch keyboard and cursor focus between Node 1 and Node 2",

    "/term": "Spawn interactive subshell (local or remote @node1)",

    "/sync": "Synchronize code and configs across all cluster nodes with progress bar",

    "/cat": "Colorized file viewer with line numbers and syntax highlighting",

    "/ls": "Colorized directory listing with classifications and sizes",

    "/consolidate": "Consolidate neural waveforms and art into 100MB+ master opuses",

    "/art": "Synthesize generative multi-movement artwork and explainer",

    "/node": "View mesh matrix or execute remote command",

    "/pull": "Pull and provision models locally for private/offline use",

    "/model": "Hot-swap, list, or inspect LLM heads (32B, 70B, 7B)",

    "/bicameral": "Toggle Fast Pilot (<300ms) + Heavy Flagship (deep code/proofs) dual cortex",

    "/mode": "Toggle between FULL ACCESS and isolated SANDBOX mode",

    "/git": "Inspect repository status, diffs, and branch states",

    "/share": "Toggle shared workspace (Documents/ClothOS_Shared)",

    "/leave": "Disconnect this node from the cluster mesh (Offline mode)",

    "/join": "Rejoin this node to the cluster mesh (Online mode)",

    "/cns": "View live Central Nervous System sensory streams",

    "/brain": "View digital brain neurobiological modulation state",

    "/verbose": "Toggle real-time thinking and action stream (Qwen style)",

    "/status": "Display node telemetry, runtimes, and sandbox state",

    "/history": "View indexed session conversation and command history",

    "/clear": "Clear current conversation memory context",

    "/exit": "Exit ClothOS session safely",

    "/bench": "Benchmark command execution duration and CPU time",

    "/sysinfo": "Display Neofetch-style ClothOS cluster system banner",

}



GIT_SUBCOMMANDS = [

    "status", "diff", "log", "commit", "push", "pull", "branch",

    "checkout", "fetch", "merge", "rebase", "stash", "add", "reset"

]



COMMON_EXECUTABLES = [

    "git", "python", "pip", "node", "npm", "pnpm", "yarn", "cargo",

    "docker", "curl", "wget", "ipconfig", "ifconfig", "ping", "netstat",

    "tasklist", "nvidia-smi", "ollama", "code", "nano", "vim", "cd",

    "ls", "dir", "cat", "type", "pwd", "mkdir", "rm", "cp", "mv",

    "clear", "cls", "echo", "touch", "sysinfo", "bench", "ps"

]





class ClothOSCompleter(Completer):

    """Context-aware auto-completer for the ClothOS Terminal."""



    def __init__(self, workspace_root: Path):

        self.workspace_root = workspace_root

        self.path_completer = PathCompleter(only_directories=False, expanduser=True)



    def set_workspace(self, new_dir: Path):

        self.workspace_root = new_dir.resolve()



    def get_completions(self, document: Document, complete_event: Any) -> Iterable[Completion]:

        text = document.text_before_cursor

        stripped = text.strip()

        word = document.get_word_before_cursor(WORD=True)



        # 1. Slash command autocompletion

        if text.startswith("/"):

            for cmd, desc in SLASH_COMMAND_DOCS.items():

                if cmd.startswith(text):

                    yield Completion(

                        cmd,

                        start_position=-len(text),

                        display=cmd,

                        display_meta=desc

                    )

            return



        # 2. Remote Node target autocompletion (!@... or @... or /node ...)

        if text.startswith("!@") or text.startswith("@") or text.startswith("/node "):

            prefix = ""

            if text.startswith("!@"):

                token = text[2:].strip()

                prefix = "!@"

            elif text.startswith("@"):

                token = text[1:].strip()

                prefix = "@"

            else:

                parts = text.split(maxsplit=2)

                token = parts[1] if len(parts) > 1 else ""

                prefix = "/node "



            nodes = {

                "node1": "skyTech Dual-GPU Worker (192.168.99.1)",

                "skytech": "skyTech Dual-GPU Worker (192.168.99.1)",

                "node2": "Ryzen 7 7730U Decider / Local (192.168.99.2)",

                "ryzen7": "Ryzen 7 7730U Decider / Local (192.168.99.2)",

                "node3": "Brother's PC (Stealth Sentry Node)",

                "peer": "Primary cluster peer bridge"

            }

            for n_id, n_desc in nodes.items():

                if n_id.startswith(token.lower()):

                    yield Completion(

                        prefix + n_id,

                        start_position=-len(text),

                        display=f"@{n_id}",

                        display_meta=n_desc

                    )

            return



        # 3. Model autocompletion (/model use ... or /pull ...)

        if text.startswith("/model use ") or text.startswith("/pull "):

            m_token = text.split()[-1] if len(text.split()) > 2 else ""

            models = {

                "loom-sovereign": "Qwen 2.5 32B Coder (Node 1 GPU)",

                "loom-sovereign-70b": "Llama 3.3 70B Heavy Reasoning (Node 1)",

                "loom-sovereign-fast": "Qwen 2.5 7B Fast Turnaround",

                "qwen2.5:7b": "Standard 7B local coding engine",

                "llama3.2:3b": "Ultra-lightweight 3B assistant",

                "deepseek-r1:8b": "DeepSeek R1 Distilled Reasoning",

                "gemini-flash": "Google Gemini 2.0 Flash Cloud API"

            }

            for m_tag, m_desc in models.items():

                if m_tag.startswith(m_token):

                    yield Completion(

                        m_tag,

                        start_position=-len(m_token),

                        display=m_tag,

                        display_meta=m_desc

                    )

            return



        # 4. Git subcommand autocompletion

        if stripped.startswith("git ") or stripped.startswith("!git ") or stripped.startswith("/git "):

            parts = stripped.split()

            if len(parts) == 2 and not text.endswith(" "):

                sub = parts[1]

                for sc in GIT_SUBCOMMANDS:

                    if sc.startswith(sub):

                        yield Completion(sc, start_position=-len(sub), display=sc, display_meta="git command")

                return



        # 5. File path autocompletion (after cd, cat, ls, dir, code, python, nano, etc.)

        tokens = stripped.split()

        if tokens and tokens[0].lower() in [

            "cd", "cat", "type", "ls", "dir", "code", "nano", "vim",

            "python", "py", "source", "open", "head", "tail", "rm", "cp", "mv"

        ]:

            # Use path completer in current workspace

            try:

                cur_dir = str(self.workspace_root)

                for comp in self.path_completer.get_completions(document, complete_event):

                    yield comp

            except Exception:

                pass

            return



        # 6. Top-level CLI executable autocompletion

        if " " not in stripped and stripped:

            for exe in COMMON_EXECUTABLES:

                if exe.startswith(stripped.lower()):

                    yield Completion(exe, start_position=-len(stripped), display=exe, display_meta="command")





# ── Terminal Styling (Cyberpunk Minimal Dark Theme) ──────────────────────────

TERMINAL_STYLE = Style.from_dict({
    "prompt.glyph": "bold #22c55e",
    "prompt.dir": "bold #f8fafc",
    "prompt.git": "bold #a855f7",
    "prompt.model": "bold #4ade80",
    "prompt.node": "#c084fc",
    "prompt.arrow": "bold #22c55e",
    "prompt.arrow.fail": "bold #ef4444",
    "bottom-toolbar": "bg:#0a1f14 #f8fafc",
    "bottom-toolbar.text": "#f8fafc",
    "bottom-toolbar.doing": "bold #22c55e",
    "bottom-toolbar.key": "bold #a855f7",
    "bottom-toolbar.alert": "bold #f59e0b",
    "completion-menu": "bg:#0f291e #f8fafc",
    "completion-menu.completion": "bg:#0f291e #4ade80",
    "completion-menu.completion.current": "bold bg:#581c87 #ffffff",
    "completion-menu.meta": "bg:#0a1f14 #c084fc italic",
    "auto-suggestion": "#64748b italic",
})





def get_git_branch(directory: Path) -> Optional[Tuple[str, bool]]:

    """Fast check for git branch and dirty status."""

    try:

        git_dir = directory / ".git"

        if not git_dir.exists():

            # Search upwards

            for parent in directory.parents:

                if (parent / ".git").exists():

                    git_dir = parent / ".git"

                    break

            else:

                return None



        # Fast read of HEAD

        head_file = git_dir / "HEAD"

        if not head_file.exists():

            return None



        head_content = head_file.read_text(encoding="utf-8").strip()

        if head_content.startswith("ref: refs/heads/"):

            branch = head_content[16:]

        else:

            branch = head_content[:7]



        # Check dirty state fast via git status -s

        is_dirty = False

        try:

            res = subprocess.run(

                ["git", "status", "--porcelain"],

                cwd=str(directory),

                capture_output=True,

                text=True,

                timeout=1

            )

            is_dirty = bool(res.stdout.strip())

        except Exception:

            pass



        return branch, is_dirty

    except Exception:

        return None





def format_powerline_prompt(

    workspace_root: Path,

    active_head: str,

    last_returncode: int = 0,

    is_full_access: bool = True

) -> HTML:

    """Renders a sleek Starship/Warp-style Powerline prompt themed in Green/White/Purple."""

    home = Path.home()

    try:

        if workspace_root == home:

            dir_disp = "~"

        elif home in workspace_root.parents:

            dir_disp = f"~/{workspace_root.relative_to(home).as_posix()}"

        else:

            dir_disp = workspace_root.as_posix()

    except Exception:

        dir_disp = str(workspace_root)



    # Truncate deep directories

    parts = dir_disp.split("/")

    if len(parts) > 3:

        dir_disp = f"…/{parts[-2]}/{parts[-1]}"



    try:
        from loom.clothos.theme import ThemeManager
        theme = ThemeManager.get_active()
    except Exception:
        theme = None

    brand_bg = theme.brand_primary if theme else "#38bdf8"
    brand_fg = "#090d16" if theme and theme.name in ("production", "scientific") else "#052e16"
    panel_bg = theme.bg_accent if theme else "#1e293b"
    vcs_bg = theme.bg_dark if theme else "#0f172a"
    vcs_fg = theme.brand_primary if theme else "#38bdf8"
    ready_color = theme.status_ready if theme else "#10b981"
    alert_color = theme.status_alert if theme else "#f59e0b"

    # Git branch
    git_info = get_git_branch(workspace_root)
    git_segment = ""
    if git_info:
        branch, is_dirty = git_info
        dirty_char = "*" if is_dirty else ""
        git_segment = f' <style bg="{vcs_bg}" fg="{vcs_fg}"><b> [VCS::{branch}{dirty_char}] </b></style>'

    # Access mode badge
    mode_text = "FULL_ACCESS" if is_full_access else "SANDBOX"
    mode_color = ready_color if is_full_access else alert_color

    # Arrow color based on last return code
    arrow_color = ready_color if last_returncode == 0 else "#ef4444"

    # Head label
    head_short = active_head.replace("loom-sovereign", "sovereign").replace("-fast", ":7b")

    prompt_html = (
        f'<style bg="{brand_bg}" fg="{brand_fg}"><b> ■ CLOTHOS </b></style>'
        f'<style bg="{panel_bg}" fg="#f8fafc"><b> [DIR::{dir_disp}] </b></style>'
        f'{git_segment}'
        f'<style bg="{vcs_bg}" fg="#cbd5e1"><b> [HEAD::{head_short}] </b></style> '
        f'<style fg="{mode_color}"><b>[{mode_text}]</b></style>\n'
        f'<style fg="{arrow_color}"><b>❯❯</b></style> '
    )

    return HTML(prompt_html)


def make_bottom_toolbar():
    """Generates a dynamic bottom status HUD toolbar with live Currently [doing] indicator."""
    cpu_pct = "?"
    ram_pct = "?"
    if HAS_PSUTIL:
        try:
            cpu_pct = f"{int(psutil.cpu_percent())}%"
            ram_pct = f"{int(psutil.virtual_memory().percent)}%"
        except Exception:
            pass

    try:
        from loom.clothos.theme import ThemeManager
        theme = ThemeManager.get_active()
    except Exception:
        theme = None

    brand_col = theme.brand_primary if theme else "#38bdf8"
    dim_col = theme.brand_dim if theme else "#64748b"
    ready_col = theme.status_ready if theme else "#10b981"
    accent_bg = theme.bg_accent if theme else "#1e293b"

    curr_task = CurrentlyDoing.get()
    curr_phase = CurrentlyDoing.get_phase()
    is_idle = curr_phase == "IDLE"
    doing_style = f'fg="{ready_col}"' if is_idle else f'fg="#f8fafc" bg="{accent_bg}"'

    glow_aura = ""
    if not is_idle:
        try:
            from loom.clothos.activity_tracker import GlowActivityIndicator
            wave = GlowActivityIndicator.get_glow_wave(width=8)
            import re
            clean_wave = re.sub(r"\[.*?\]", "", wave)
            glow_aura = f' <style fg="{brand_col}">■</style><style fg="{dim_col}"> {clean_wave}</style>'
        except Exception:
            glow_aura = f' <style fg="{dim_col}"> ▂▃▅▆█</style>'

    steer_badge = ""
    try:
        from loom.clothos.steering_controller import SteeringController
        if SteeringController.has_directives():
            first_d = SteeringController.get_active()[0]
            steer_badge = f' | <b>CTL:</b> <style fg="{brand_col}"><b>{first_d.directive[:18]}…</b></style>'
    except Exception:
        pass

    detail_badge = ""
    if not is_idle:
        try:
            details = CurrentlyDoing.get_details()
            sub_g = details.get("sub_goal")
            if sub_g:
                detail_badge = f' | <b>STEP:</b> <style fg="{brand_col}"><b>{sub_g[:24]}</b></style>'
        except Exception:
            pass

    cluster_lat = "0.8ms"
    try:
        from loom.clothos.mesh_discovery import get_mesh_beacon
        beacon = get_mesh_beacon()
        peers = beacon.get_live_peers()
        if peers:
            first_p = next(iter(peers.values()))
            lat = first_p.get("latency_ms")
            if lat is not None:
                cluster_lat = f"{lat}ms"
    except Exception:
        pass

    return HTML(
        f' <b>■ [CURRENT]:</b> <style {doing_style}><b> {curr_task} </b></style>{glow_aura}{detail_badge}{steer_badge} | '
        f'<b>CPU:</b> <style fg="{ready_col}">{cpu_pct}</style> | '
        f'<b>RAM:</b> <style fg="{brand_col}">{ram_pct}</style> | '
        f'<b>MESH:</b> <style fg="{ready_col}">2-Node ({cluster_lat})</style> | '
        f'<style fg="{dim_col}">[Ctrl+C] Quit · /context · /teach · /bfcl · /theme · ?</style> '
    )


def create_terminal_keybindings() -> KeyBindings:
    """Custom keybindings for modern terminal controls matching agy and codex."""
    kb = KeyBindings()

    @kb.add("c-l")
    def _clear_screen(event):
        """Ctrl+L clears screen cleanly."""
        os.system("cls" if os.name == "nt" else "clear")
        event.cli.renderer.erase()

    @kb.add("c-c")
    def _cancel_prompt(event):
        """Ctrl+C clears current input without killing the REPL session."""
        buf = event.app.current_buffer
        if buf.text:
            buf.reset()
        else:
            event.app.exit(result=None)

    @kb.add("escape", "enter")
    def _newline(event):
        """Alt+Enter or Esc+Enter inserts a literal newline for multi-line prompts."""
        event.app.current_buffer.insert_text("\n")

    return kb


def create_robust_output(stdout=None):
    """Ensures prompt_toolkit never crashes on Windows ConPTY or redirected output."""
    if stdout is None:
        stdout = sys.stdout
    try:
        from prompt_toolkit.output.defaults import create_output
        return create_output(stdout=stdout)
    except Exception:
        pass
    try:
        from prompt_toolkit.output.vt100 import Vt100_Output
        return Vt100_Output(stdout, lambda: shutil.get_terminal_size((80, 24)))
    except Exception:
        pass
    try:
        from prompt_toolkit.output.plain_text import PlainTextOutput
        return PlainTextOutput(stdout)
    except Exception:
        return None


def create_prompt_session(workspace_root: Path, history_file: Optional[Path] = None) -> Optional[Any]:
    """Robust factory for creating prompt_toolkit PromptSession on any Windows/Linux terminal."""
    if not HAS_PROMPT_TOOLKIT:
        return None
    if history_file is None:
        history_file = Path.home() / ".clothos_terminal_history"
    out = create_robust_output()
    try:
        completer = ClothOSCompleter(workspace_root)
        kwargs = {
            "history": FileHistory(str(history_file)),
            "auto_suggest": AutoSuggestFromHistory(),
            "completer": completer,
            "style": TERMINAL_STYLE,
            "key_bindings": create_terminal_keybindings(),
            "bottom_toolbar": make_bottom_toolbar,
        }
        if out is not None:
            kwargs["output"] = out
        return PromptSession(**kwargs)
    except Exception:
        try:
            return PromptSession(
                output=out,
                history=FileHistory(str(history_file)),
                auto_suggest=AutoSuggestFromHistory(),
                completer=ClothOSCompleter(workspace_root)
            )
        except Exception:
            return None


import difflib

# Rich console with legacy_windows=False to prevent cp1252 charmap encoding crash
safe_console = Console(legacy_windows=False, force_terminal=True)

GEAR_GLYPH = "*"
CHECK_GLYPH = "+"
CROSS_GLYPH = "x"

def render_tool_badge(tool_name: str, args: dict, status: str = "running", dur: float = 0.0, summary: str = ""):
    """Renders a sleek interactive tool status badge matching agy / codex CLI."""
    if status == "running":
        args_preview = ", ".join(f"{k}='{v}'" if isinstance(v, str) and len(v)<30 else f"{k}={v}" for k,v in list(args.items())[:3])
        if len(args_preview) > 60:
            args_preview = args_preview[:57] + "..."
        safe_console.print(f"  [bold #38bdf8]{GEAR_GLYPH} [TOOL][/bold #38bdf8] [bold white]{tool_name}[/bold white]([dim #94a3b8]{args_preview}[/dim #94a3b8]) [dim #64748b]...[/dim #64748b]")
    elif status == "success":
        safe_console.print(f"  [bold #10b981]{CHECK_GLYPH} [TOOL][/bold #10b981] [bold white]{tool_name}[/bold white] [dim white]({dur:.3f}s)[/dim white] [dim #10b981]-> {summary}[/dim #10b981]")
    elif status == "error":
        safe_console.print(f"  [bold #ef4444]{CROSS_GLYPH} [TOOL][/bold #ef4444] [bold white]{tool_name}[/bold white] [dim white]({dur:.3f}s)[/dim white] [bold #ef4444]FAILED -> {summary}[/bold #ef4444]")


def render_unified_diff(filename: str, old_text: str, new_text: str):
    """Renders a syntax-highlighted unified diff for code modifications."""
    diff = list(difflib.unified_diff(
        old_text.splitlines(keepends=True),
        new_text.splitlines(keepends=True),
        fromfile=f"a/{filename}",
        tofile=f"b/{filename}",
        n=3
    ))
    if not diff:
        return
    diff_text = "".join(diff)
    syntax = Syntax(diff_text, "diff", theme="monokai", line_numbers=True)
    safe_console.print(Panel(syntax, title=f"[bold #38bdf8]File Modification Unified Diff: {filename}[/bold #38bdf8]", border_style="#334155", padding=(0, 1)))





# ── Built-in Commercial Terminal Utilities ───────────────────────────────────



def clothos_cat(file_path_str: str, workspace_root: Path):

    """Rich colorized file viewer with line numbers and syntax highlighting."""

    target = (workspace_root / file_path_str).resolve()

    if not target.is_file():

        console.print(f"[red]Error: File not found: {file_path_str}[/red]")

        return



    try:

        content = target.read_text(encoding="utf-8", errors="replace")

        ext = target.suffix.lstrip(".").lower()

        lexer_map = {

            "py": "python", "js": "javascript", "ts": "typescript",

            "json": "json", "md": "markdown", "rs": "rust",

            "html": "html", "css": "css", "sh": "bash", "ps1": "powershell",

            "bat": "batch", "cmd": "batch", "sql": "sql", "yaml": "yaml", "yml": "yaml"

        }

        lexer = lexer_map.get(ext, "text")

        syntax = Syntax(

            content,

            lexer,

            theme="monokai",

            line_numbers=True,

            word_wrap=True

        )

        console.print(Panel(

            syntax,

            title=f"📄 [bold cyan]{target.name}[/bold cyan] ({len(content)} bytes)",

            border_style="cyan"

        ))

    except Exception as ex:

        console.print(f"[red]Failed to read file: {ex}[/red]")





def clothos_ls(dir_path_str: str, workspace_root: Path):

    """Rich colorized directory lister with file classifications and sizes."""

    target = (workspace_root / dir_path_str).resolve() if dir_path_str else workspace_root

    if not target.is_dir():

        console.print(f"[red]Error: Directory not found: {dir_path_str}[/red]")

        return



    table = Table(

        title=f"📁 {target}",

        box=box.SIMPLE_HEAVY,

        border_style="cyan"

    )

    table.add_column("Type", style="bold", width=4)

    table.add_column("Name", style="bold white")

    table.add_column("Size", justify="right", style="cyan")

    table.add_column("Modified", style="dim")



    try:

        entries = sorted(target.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))

        for p in entries:

            try:

                st = p.stat()

                mtime = datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M")

                if p.is_dir():

                    icon = "📁"

                    size_str = "<DIR>"

                    name_str = f"[bold cyan]{p.name}/[/bold cyan]"

                else:

                    ext = p.suffix.lower()

                    if ext in [".py", ".pyw"]: icon = "🐍"

                    elif ext in [".js", ".jsx", ".ts", ".tsx"]: icon = "📜"

                    elif ext in [".rs"]: icon = "🦀"

                    elif ext in [".json", ".yaml", ".yml", ".toml"]: icon = "⚙️"

                    elif ext in [".md", ".txt"]: icon = "📝"

                    elif ext in [".exe", ".bat", ".cmd", ".ps1"]: icon = "⚡"

                    elif ext in [".zip", ".tar", ".gz", ".7z"]: icon = "📦"

                    else: icon = "📄"



                    sz = st.st_size

                    if sz < 1024: size_str = f"{sz} B"

                    elif sz < 1024**2: size_str = f"{sz/1024:.1f} KB"

                    else: size_str = f"{sz/(1024**2):.1f} MB"

                    name_str = p.name



                table.add_row(icon, name_str, size_str, mtime)

            except Exception:

                continue



        console.print(table)

    except Exception as ex:

        console.print(f"[red]Failed to list directory: {ex}[/red]")





def clothos_sysinfo():

    """Neofetch / Fastfetch-style visual cluster system summary."""

    host = socket.gethostname()

    uname = os.name.upper()



    cpu_info = "AMD Ryzen 7 7730U (8c/16t)" if "ryzen" in host.lower() or host == "WIN-7CMAQLVP8MV" else "Host CPU"

    ram_info = f"{psutil.virtual_memory().total // (1024**3)} GB Total" if HAS_PSUTIL else "32 GB"



    BANNER = r"""

  ✦  ██████╗██╗      ██████╗ ████████╗██╗  ██╗ ██████╗ ███████╗

     ██╔════╝██║     ██╔═══██╗╚══██╔══╝██║  ██║██╔═══██╗██╔════╝

     ██║     ██║     ██║   ██║   ██║   ███████║██║   ██║███████╗

     ██║     ██║     ██║   ██║   ██║   ██╔══██║██║   ██║╚════██║

     ╚██████╗███████╗╚██████╔╝   ██║   ██║  ██║╚██████╔╝███████║

      ╚═════╝╚══════╝ ╚═════╝    ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝

"""



    grid = Table.grid(padding=2)

    grid.add_column(style="bold cyan")

    grid.add_column(style="white")



    info_text = (

        f"[bold cyan]OS:[/bold cyan] Windows 11 Enterprise (ClothOS Sovereign Substrate)\n"

        f"[bold cyan]Host:[/bold cyan] {host} (Node 2 — Orchestrator Decider)\n"

        f"[bold cyan]Kernel:[/bold cyan] ClothOS Polyglot Engine v0.2.0\n"

        f"[bold cyan]CPU:[/bold cyan] {cpu_info}\n"

        f"[bold cyan]Memory:[/bold cyan] {ram_info}\n"

        f"[bold cyan]Cluster Mesh:[/bold cyan] Node 1 (skyTech Dual-GPU) ⟵2.5GbE⟶ Node 2\n"

        f"[bold cyan]Mesh GPUs:[/bold cyan] NVIDIA RTX 3060 (12GB) + AMD RX 580 (8GB)\n"

        f"[bold cyan]Hosted Models:[/bold cyan] Sovereign 70B · Sovereign 32B · Sovereign 7B\n"

        f"[bold cyan]Terminal Engine:[/bold cyan] Prompt-Toolkit 3.0 + Rich + Starship Powerline\n"

        f"[bold cyan]Uptime:[/bold cyan] Active Session Verified"

    )



    grid.add_row(BANNER, info_text)

    console.print(Panel(grid, title="[bold #00ff7f]✦ CLOTHOS SYSTEM ARCHITECTURE[/bold #00ff7f]", border_style="#a855f7"))





def clothos_ps():

    """Displays active running processes sorted by memory usage."""

    if not HAS_PSUTIL:

        console.print("[yellow]psutil not installed.[/yellow]")

        return



    table = Table(title="Top Processes by Memory Usage", border_style="#a855f7", box=box.SIMPLE)

    table.add_column("PID", style="cyan", justify="right")

    table.add_column("Name", style="bold white")

    table.add_column("CPU %", justify="right", style="green")

    table.add_column("Memory %", justify="right", style="yellow")

    table.add_column("RAM (MB)", justify="right", style="magenta")



    procs = []

    for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info']):

        try:

            procs.append(p.info)

        except Exception:

            continue



    procs.sort(key=lambda x: (x.get('memory_percent') or 0), reverse=True)

    for p in procs[:15]:

        mem_mb = (p.get('memory_info').rss // (1024**2)) if p.get('memory_info') else 0

        table.add_row(

            str(p.get('pid')),

            str(p.get('name'))[:30],

            f"{p.get('cpu_percent') or 0:.1f}",

            f"{p.get('memory_percent') or 0:.1f}%",

            f"{mem_mb} MB"

        )



    console.print(table)





def clothos_bench(cmd: str, workspace_root: Path):

    """Benchmarks command execution with millisecond precision."""

    console.print(f"[bold cyan]⏱ Benchmarking:[/bold cyan] [dim]{cmd}[/dim]")

    t0 = time.perf_counter()

    res = subprocess.run(cmd, cwd=str(workspace_root), shell=True, capture_output=True, text=True)

    dur = time.perf_counter() - t0



    if res.stdout:

        console.print(res.stdout.rstrip())

    if res.stderr:

        console.print(f"[yellow]{res.stderr.rstrip()}[/yellow]")



    color = "green" if res.returncode == 0 else "red"

    console.print(f"\n[bold {color}]Return Code: {res.returncode}[/bold {color}] | [bold cyan]Elapsed Time: {dur:.4f}s[/bold cyan] ({dur*1000:.2f}ms)")





def clothos_monitors(sub_cmd: Optional[str] = None):

    """Visually represents the physical arrangement of multi-node monitors and handles focus switching."""

    import webbrowser

    from rich.columns import Columns



    sub = (sub_cmd or "").strip().lower()



    if sub in ["gui", "open", "web", "matrix"]:

        gui_path = Path("C:/Users/natsa/Documents/loom-fabric/guis/desktop-hud/monitors.html")

        if gui_path.exists():

            console.print(f"[bold green]✦ Opening Interactive Visual Monitor Matrix:[/bold green] [cyan]{gui_path.as_uri()}[/cyan]")

            webbrowser.open(gui_path.as_uri())

            return

        else:

            console.print("[yellow]Visual monitors GUI not found.[/yellow]")

            return



    if sub in ["1", "node1", "skytech", "switch 1", "switch node1"]:

        try:

            from loom.clothos.input_bridge import send_hotkey

            console.print("[bold cyan]⚡ Switching Focus ➔ Node 1 (skyTech Dual-GPU Desktop)[/bold cyan]")

            send_hotkey(["ctrl", "alt", "f1"])

            console.print("[green]✔ Hotkey [Ctrl+Alt+F1] triggered. Cursor & keyboard warped to Node 1.[/green]")

        except Exception as ex:

            console.print(f"[red]Failed to trigger hotkey: {ex}[/red]")

        return



    if sub in ["2", "node2", "ryzen7", "laptop", "switch 2", "switch node2"]:

        try:

            from loom.clothos.input_bridge import send_hotkey

            console.print("[bold cyan]⚡ Switching Focus ➔ Node 2 (Ryzen 7 7730U Laptop)[/bold cyan]")

            send_hotkey(["ctrl", "alt", "f2"])

            console.print("[green]✔ Hotkey [Ctrl+Alt+F2] triggered. Cursor & keyboard warped to Node 2.[/green]")

        except Exception as ex:

            console.print(f"[red]Failed to trigger hotkey: {ex}[/red]")

        return



    # Visual ASCII representation

    card_node2 = Panel(

        "[bold cyan]💻 NODE 2 (Laptop Display)[/bold cyan]\n"

        "[dim]Host: WIN-7CMAQLVP8MV[/dim]\n\n"

        "📐 [bold white]1280 × 720[/bold white] (Primary)\n"

        "🎮 AMD Radeon 7730U APU\n"

        "🌐 192.168.99.2 (Decider)\n\n"

        "📍 [bold green]ACTIVE LOCAL HEAD[/bold green]\n"

        "🎯 [bold gold1]Hotkey: Ctrl + Alt + F2[/bold gold1]",

        title="[bold cyan]Screen 1[/bold cyan]",

        border_style="cyan",

        width=32

    )



    card_bridge1 = Panel(

        "\n\n[bold green]⟷⟷⟷[/bold green]\n"

        "[dim]Glide[/dim]\n"

        "[dim]Edge[/dim]",

        border_style="dim",

        width=11

    )



    card_node1_p = Panel(

        "[bold green]🖥️ NODE 1 (Gaming Display 1)[/bold green]\n"

        "[dim]Host: skyTech Worker[/dim]\n\n"

        "📐 [bold white]1920 × 1080[/bold white] (FHD)\n"

        "🎮 NVIDIA RTX 3060 (12GB)\n"

        "🌐 192.168.99.1 (2.5GbE)\n\n"

        "🧠 70B & 32B VRAM Resident\n"

        "🎯 [bold gold1]Hotkey: Ctrl + Alt + F1[/bold gold1]",

        title="[bold green]Screen 2[/bold green]",

        border_style="green",

        width=34

    )



    card_bridge2 = Panel(

        "\n\n[bold green]⟷⟷⟷[/bold green]\n"

        "[dim]Glide[/dim]\n"

        "[dim]Edge[/dim]",

        border_style="dim",

        width=11

    )



    card_node1_s = Panel(

        "[bold green]🖥️ NODE 1 (Aux Display 2)[/bold green]\n"

        "[dim]Host: skyTech Auxiliary[/dim]\n\n"

        "📐 [bold white]1536 × 864[/bold white] (Aux)\n"

        "🎮 AMD RX 580 (8GB)\n"

        "🌐 192.168.99.1 (Secondary)\n\n"

        "📊 Telemetry & HUD Monitor\n"

        "🎯 [bold gold1]Hotkey: Ctrl + Alt + F1[/bold gold1]",

        title="[bold green]Screen 3[/bold green]",

        border_style="green",

        width=32

    )



    console.print("\n[bold cyan]✦ Physical Desk Monitor Arrangement & KVM Switching Matrix:[/bold cyan]\n")

    console.print(Columns([card_node2, card_bridge1, card_node1_p, card_bridge2, card_node1_s]))

    console.print(

        "\n[dim]Quick Actions:[/dim]\n"

        "  • [bold cyan]/monitors switch 1[/bold cyan] (or [bold cyan]/kvm 1[/bold cyan]) — Jump cursor & keyboard to Node 1\n"

        "  • [bold cyan]/monitors switch 2[/bold cyan] (or [bold cyan]/kvm 2[/bold cyan]) — Jump cursor & keyboard to Node 2\n"

        "  • [bold cyan]/monitors gui[/bold cyan]               — Open interactive drag-and-drop Visual Monitor Canvas\n"

        "  • [bold yellow]Physical Mouse Glide[/bold yellow]       — Move cursor off the right edge of screen 1 to enter screen 2\n"

    )
