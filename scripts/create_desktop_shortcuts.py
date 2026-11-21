# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
ClothOS Dual-Node Desktop Shortcut & GUI Generator (`scripts/create_desktop_shortcuts.py`).

Creates high-fidelity Windows Desktop shortcuts (.lnk and .bat launchers):
1. 'ClothOS Sovereign Mind & TPU Cockpit' -> Standalone App window to :8087/visuals
2. 'ClothOS Universal Mind App' -> Standalone App window to :8086
3. 'ClothOS Native Desktop Commander' -> Full native Tkinter GUI (-m loom.gui)
4. 'ClothOS Node 2 Remote Cockpit' -> Remote Node 2 dashboard (:8087/visuals or :8265)
5. 'ClothOS Interactive Shell (clothsh)' -> Dedicated sovereign CLI terminal
"""

import os
from pathlib import Path
import platform
import socket
import sys

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def get_desktop_dir() -> Path:
    """Finds the desktop directory across user profile configurations."""
    # Check OneDrive Desktop first if present
    onedrive_desktop = Path.home() / "OneDrive" / "Desktop"
    if onedrive_desktop.exists():
        return onedrive_desktop
    user_desktop = Path.home() / "Desktop"
    if user_desktop.exists():
        return user_desktop
    # Fallback
    return Path.home() / "Desktop"


def create_windows_shortcut(
    shortcut_path: Path,
    target_path: str,
    arguments: str = "",
    working_dir: str = "",
    description: str = "",
    icon_location: str = "",
):
    """Generates a Windows .lnk shortcut file using Windows WScript.Shell via PowerShell."""
    ps_script = f"""
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
$Shortcut.TargetPath = '{target_path}'
$Shortcut.Arguments = '{arguments}'
$Shortcut.WorkingDirectory = '{working_dir}'
$Shortcut.Description = '{description}'
"""
    if icon_location:
        ps_script += f"$Shortcut.IconLocation = '{icon_location}'\n"
    ps_script += "$Shortcut.Save()\n"

    # Write temporary powershell script and execute
    temp_ps1 = shortcut_path.parent / f"_temp_create_shortcut_{shortcut_path.stem}.ps1"
    temp_ps1.write_text(ps_script, encoding="utf-8")
    try:
        import subprocess
        subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(temp_ps1)], check=True, capture_output=True)
    finally:
        if temp_ps1.exists():
            temp_ps1.unlink()


def main():
    hostname = socket.gethostname()
    is_node2 = "win-7cmaqlvp8mv" in hostname.lower() or "ryzen" in hostname.lower() or "node2" in hostname.lower() or "skytech" not in hostname.lower()
    node_label = "Node 2 (Ryzen 7)" if is_node2 else "Node 1 (SkyTech)"

    workspace_root = Path(__file__).resolve().parents[1]
    desktop_dir = get_desktop_dir()
    desktop_dir.mkdir(parents=True, exist_ok=True)

    py_exe = workspace_root / ".venv" / "Scripts" / "python.exe"
    if not py_exe.exists():
        py_exe = Path(sys.executable)

    pythonw_exe = workspace_root / ".venv" / "Scripts" / "pythonw.exe"
    if not pythonw_exe.exists():
        pythonw_exe = py_exe

    launcher_script = workspace_root / "apps" / "loom-desktop" / "launch_desktop.py"

    print("=" * 70)
    print(f"Creating ClothOS Sovereign Desktop Shortcuts for {node_label}...")
    print(f"Desktop Path: {desktop_dir}")
    print(f"Workspace:    {workspace_root}")
    print(f"Python Exe:   {py_exe}")
    print("=" * 70)

    # 1. Primary Sovereign Mind & TPU Visual Cockpit (.lnk)
    lnk_mind = desktop_dir / f"ClothOS Sovereign Mind & TPU Cockpit ({node_label}).lnk"
    create_windows_shortcut(
        shortcut_path=lnk_mind,
        target_path=str(pythonw_exe),
        arguments=f'"{launcher_script}" --visuals',
        working_dir=str(workspace_root),
        description="ClothOS Sovereign Mind, Occipital Stream, NSDR, Working Memory & TPU Cockpit",
    )
    print(f"[OK] Created shortcut: {lnk_mind.name}")

    # 2. Universal React Native App (.lnk)
    lnk_rn = desktop_dir / f"ClothOS Universal Mind App ({node_label}).lnk"
    create_windows_shortcut(
        shortcut_path=lnk_rn,
        target_path=str(pythonw_exe),
        arguments=f'"{launcher_script}" --rn',
        working_dir=str(workspace_root),
        description="ClothOS Universal React Native Living Mind Application",
    )
    print(f"[OK] Created shortcut: {lnk_rn.name}")

    # 3. Native Desktop Commander GUI (-m loom.gui)
    lnk_native = desktop_dir / f"ClothOS Native Commander ({node_label}).lnk"
    create_windows_shortcut(
        shortcut_path=lnk_native,
        target_path=str(pythonw_exe),
        arguments='-m loom.gui',
        working_dir=str(workspace_root),
        description="ClothOS Native Tkinter Command Center (Shuttle, ClothOS, Weave, Torque, Spool, Neuro/TPU)",
    )
    print(f"[OK] Created shortcut: {lnk_native.name}")

    # 4. Peer Node Remote Cockpit (.lnk)
    peer_name = "Node 1 (SkyTech)" if is_node2 else "Node 2 (Ryzen 7)"
    peer_mode = "--node1" if is_node2 else "--node2"
    lnk_peer = desktop_dir / f"ClothOS Remote Peer ({peer_name}).lnk"
    create_windows_shortcut(
        shortcut_path=lnk_peer,
        target_path=str(pythonw_exe),
        arguments=f'"{launcher_script}" {peer_mode}',
        working_dir=str(workspace_root),
        description=f"Direct Remote Link to ClothOS Cockpit on {peer_name}",
    )
    print(f"[OK] Created shortcut: {lnk_peer.name}")

    # 5. Interactive ClothOS Sovereign Shell (clothsh)
    lnk_shell = desktop_dir / f"ClothOS Shell - clothsh ({node_label}).lnk"
    create_windows_shortcut(
        shortcut_path=lnk_shell,
        target_path="cmd.exe",
        arguments=f'/k ""{py_exe}" -m loom.clothos.shell"',
        working_dir=str(workspace_root),
        description="Interactive POSIX-Compatible ClothOS Sovereign Shell (clothsh)",
    )
    print(f"[OK] Created shortcut: {lnk_shell.name}")

    # 6. Also create convenient .bat double-clickable scripts on desktop
    bat_mind = desktop_dir / f"Launch_ClothOS_Mind_{hostname}.bat"
    bat_mind.write_text(f"""@echo off
title ClothOS Sovereign Mind & TPU Cockpit
cd /d "{workspace_root}"
start "" "{pythonw_exe}" "{launcher_script}" --visuals
""", encoding="utf-8")
    print(f"[OK] Created launcher batch: {bat_mind.name}")

    print("=" * 70)
    print(f"All Desktop shortcuts successfully generated for {node_label}!")
    print("=" * 70)


if __name__ == "__main__":
    main()
