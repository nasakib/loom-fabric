#!/usr/bin/env python3
"""
ClothOS // Loom Fabric — Antigravity Desktop Startup & Legacy Cleanup Manager
Location: guis/desktop_startup_manager.py

Responsibilities:
1. Cleans up legacy desktop shortcuts (.lnk), batch files (.bat), and old startup scripts (.vbs).
2. Deploys modern Antigravity Desktop shortcuts for Web App Command Center, Desktop HUD, and Screensaver.
3. Configures Windows Startup (shell:startup) to launch the relevant desktop GUIs on user logon.
4. Spawns and monitors the single unified ClothOS Master App (8087).
5. Opens the relevant desktop GUIs in clean, borderless app-window mode.
"""

import os
import sys
import argparse
import subprocess
import socket
import time
from pathlib import Path
import urllib.request
import urllib.error

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

PORT_CLOTHOS_DAEMON = 8087
PORT_GUI_SERVER = 8087  # Unified single-port master application


def get_workspace_root() -> Path:
    return Path(__file__).resolve().parents[1]


def get_desktop_dirs() -> list:
    """Finds all applicable desktop directories (including OneDrive if present)."""
    desktops = []
    home = Path.home()
    
    onedrive_desktop = home / "OneDrive" / "Desktop"
    if onedrive_desktop.exists():
        desktops.append(onedrive_desktop)
        
    std_desktop = home / "Desktop"
    if std_desktop.exists() and std_desktop not in desktops:
        desktops.append(std_desktop)
        
    return desktops if desktops else [home / "Desktop"]


def get_startup_dir() -> Path:
    """Returns the Windows User Startup directory."""
    appdata = os.environ.get("APPDATA")
    if appdata:
        p = Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        if p.exists():
            return p
    return Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"


def is_port_listening(port: int) -> bool:
    """Checks if a local TCP port is currently open."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(('127.0.0.1', port)) == 0


def create_windows_shortcut(shortcut_path: Path, target_path: str, arguments: str = "", working_dir: str = "", description: str = "", icon_location: str = ""):
    """Creates a Windows .lnk shortcut via PowerShell WScript.Shell."""
    ps_cmd = f"""
$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut('{shortcut_path}')
$s.TargetPath = '{target_path}'
$s.Arguments = '{arguments}'
$s.WorkingDirectory = '{working_dir}'
$s.Description = '{description}'
"""
    if icon_location:
        ps_cmd += f"$s.IconLocation = '{icon_location}'\n"
    ps_cmd += "$s.Save()\n"

    try:
        subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd], check=True, capture_output=True)
    except Exception as e:
        print(f"[!] Warning creating shortcut {shortcut_path.name}: {e}")


def clean_legacy_artifacts():
    """Removes obsolete/legacy desktop shortcuts, batch files, and startup entries."""
    print("\n--- [1/4] Undoing Legacy Shortcuts & Startup Scripts ---")
    
    legacy_file_patterns = [
        "ClothOS Sovereign Mind & TPU Cockpit*.lnk",
        "ClothOS Universal Mind App*.lnk",
        "ClothOS Native Commander*.lnk",
        "ClothOS Command Center*.lnk",
        "ClothOS Remote Peer*.lnk",
        "ClothOS Shell*.lnk",
        "ClothOS React Native.lnk",
        "Launch_ClothOS_Mind_*.bat",
        "Start-Loom-GUI.bat",
    ]

    # Clean from Desktops
    for desktop_dir in get_desktop_dirs():
        if not desktop_dir.exists():
            continue
        print(f"Scanning desktop directory: {desktop_dir}")
        for pattern in legacy_file_patterns:
            for item in desktop_dir.glob(pattern):
                try:
                    item.unlink()
                    print(f"  [-] Removed legacy desktop item: {item.name}")
                except Exception as e:
                    print(f"  [!] Could not remove {item.name}: {e}")

    # Clean from Windows Startup
    startup_dir = get_startup_dir()
    if startup_dir.exists():
        legacy_startup = [
            startup_dir / "ClothOS_AutoStart.vbs",
            startup_dir / "Fabric_Master_Stack.lnk",
        ]
        for f in legacy_startup:
            if f.exists():
                try:
                    f.unlink()
                    print(f"  [-] Removed legacy startup item: {f.name}")
                except Exception as e:
                    print(f"  [!] Could not remove {f.name}: {e}")


def create_modern_shortcuts():
    """Generates high-coherence Antigravity desktop shortcuts."""
    print("\n--- [2/4] Generating Modern Antigravity Desktop Shortcuts ---")
    ws = get_workspace_root()
    py_exe = ws / ".venv" / "Scripts" / "python.exe"
    if not py_exe.exists():
        py_exe = Path(sys.executable)

    pythonw_exe = ws / ".venv" / "Scripts" / "pythonw.exe"
    if not pythonw_exe.exists():
        pythonw_exe = py_exe

    hostname = socket.gethostname()
    is_node2 = "ryzen" in hostname.lower() or "win-7cmaqlvp8mv" in hostname.lower() or "skytech" not in hostname.lower()
    node_tag = "Node 2 Decider" if is_node2 else "Node 1 Thinker"

    startup_manager = ws / "guis" / "desktop_startup_manager.py"
    hud_launcher = ws / "guis" / "desktop-hud" / "launch_hud.py"

    for desktop_dir in get_desktop_dirs():
        desktop_dir.mkdir(parents=True, exist_ok=True)
        print(f"Installing shortcuts to: {desktop_dir}")

        # 1. Primary Web App Command Center
        lnk_command = desktop_dir / f"ClothOS Command Center ({node_tag}).lnk"
        create_windows_shortcut(
            shortcut_path=lnk_command,
            target_path=str(pythonw_exe),
            arguments=f'"{startup_manager}" --launch --web',
            working_dir=str(ws),
            description="ClothOS Antigravity Bicameral Command Center Web Application"
        )
        print(f"  [+] Created: {lnk_command.name}")

        # 2. Desktop Glassmorphic HUD Cockpit
        lnk_hud = desktop_dir / f"ClothOS Desktop HUD ({node_tag}).lnk"
        create_windows_shortcut(
            shortcut_path=lnk_hud,
            target_path=str(pythonw_exe),
            arguments=f'"{hud_launcher}"',
            working_dir=str(ws),
            description="ClothOS Antigravity Desktop Glassmorphic Floating HUD"
        )
        print(f"  [+] Created: {lnk_hud.name}")

        # 3. Master Portal Launchpad
        lnk_portal = desktop_dir / f"ClothOS Master Portal ({node_tag}).lnk"
        create_windows_shortcut(
            shortcut_path=lnk_portal,
            target_path=str(pythonw_exe),
            arguments=f'"{startup_manager}" --launch --portal',
            working_dir=str(ws),
            description="ClothOS Universal Antigravity Portal & GUI Suite Launchpad"
        )
        print(f"  [+] Created: {lnk_portal.name}")

        # 4. 60 FPS Neuro-Screensaver
        lnk_screen = desktop_dir / f"ClothOS 60fps Screensaver ({node_tag}).lnk"
        create_windows_shortcut(
            shortcut_path=lnk_screen,
            target_path=str(pythonw_exe),
            arguments=f'"{startup_manager}" --launch --screensaver',
            working_dir=str(ws),
            description="ClothOS 60 FPS Coupled Kuramoto Neuro-Oscillator Visualizer"
        )
        print(f"  [+] Created: {lnk_screen.name}")

        # 5. ClothOS Agent CLI (Dev & Data Science)
        lnk_agent = desktop_dir / f"ClothOS Agent CLI ({node_tag}).lnk"
        create_windows_shortcut(
            shortcut_path=lnk_agent,
            target_path="cmd.exe",
            arguments=f'/k "{ws / "clothos-agent.bat"}"',
            working_dir=str(ws),
            description="ClothOS Agentic Polyglot Development & Data Science CLI"
        )
        print(f"  [+] Created: {lnk_agent.name}")



def install_to_startup():
    """Installs the silent Antigravity startup script to Windows Startup folder."""
    print("\n--- [3/4] Configuring Windows Startup ---")
    startup_dir = get_startup_dir()
    startup_dir.mkdir(parents=True, exist_ok=True)

    ws = get_workspace_root()
    py_exe = ws / ".venv" / "Scripts" / "python.exe"
    if not py_exe.exists():
        py_exe = Path(sys.executable)

    manager_script = ws / "guis" / "desktop_startup_manager.py"
    vbs_path = startup_dir / "ClothOS_Antigravity_Startup.vbs"

    q = '"""'
    vbs_code = (
        "' ClothOS Antigravity Universal Desktop Startup\n"
        "Set WshShell = CreateObject(\"WScript.Shell\")\n"
        f"WshShell.CurrentDirectory = \"{ws}\"\n"
        f"WshShell.Run {q}{py_exe}{q} & \" \" & {q}{manager_script}{q} & \" --on-startup\", 0, False\n"
    )
    vbs_path.write_text(vbs_code, encoding="utf-8")
    print(f"  [+] Installed Windows Startup entry: {vbs_path}")


def uninstall_startup():
    """Removes the Antigravity startup script from Windows Startup folder."""
    startup_dir = get_startup_dir()
    vbs_path = startup_dir / "ClothOS_Antigravity_Startup.vbs"
    if vbs_path.exists():
        vbs_path.unlink()
        print(f"  [-] Uninstalled Windows Startup entry: {vbs_path}")
    else:
        print("  [*] No Antigravity startup entry found.")


def ensure_backend_services():
    """Verifies that the single-port Unified ClothOS Master App (8087) is running."""
    ws = get_workspace_root()
    py_exe = ws / ".venv" / "Scripts" / "python.exe"
    if not py_exe.exists():
        py_exe = Path(sys.executable)

    detach_flags = 0x00000008 | 0x00000200 if os.name == 'nt' else 0

    # 1. Unified ClothOS Master Application (port 8087 — Dashboard, Visuals, GUIs, Gateway, File & Media Studio)
    if not is_port_listening(PORT_CLOTHOS_DAEMON):
        print(f"[*] Starting Unified ClothOS Master App on port {PORT_CLOTHOS_DAEMON}...")
        cmd_daemon = f'"{py_exe}" -m uvicorn loom.fabric.dashboard_server:app --host 0.0.0.0 --port {PORT_CLOTHOS_DAEMON}'
        subprocess.Popen(cmd_daemon, cwd=str(ws), shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, close_fds=True, creationflags=detach_flags)
        time.sleep(1.5)
    else:
        print(f"[OK] Unified ClothOS Master App active on port {PORT_CLOTHOS_DAEMON}.")


def launch_desktop_gui(url: str, app_name: str, window_size: str = "1280,820", window_pos: str = ""):
    """Launches a URL in borderless app-window mode via Edge, Chrome, or default browser."""
    browser_commands = [
        ["msedge", f"--app={url}", f"--window-size={window_size}"],
        ["chrome", f"--app={url}", f"--window-size={window_size}"],
    ]
    if window_pos:
        for c in browser_commands:
            c.append(f"--window-position={window_pos}")

    detach_flags = 0x00000008 | 0x00000200 if os.name == 'nt' else 0  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP

    for cmd in browser_commands:
        try:
            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                close_fds=True,
                creationflags=detach_flags
            )
            print(f"[OK] Launched {app_name} via {cmd[0]} app window: {url}")
            return True
        except FileNotFoundError:
            continue

    import webbrowser
    print(f"[*] Opening {app_name} in default browser: {url}")
    webbrowser.open(url)
    return True


def launch_relevant_guis(mode: str = "all"):
    """Opens the unified ClothOS Master Application on port 8087."""
    print("\n--- [4/4] Launching Unified Master Interface (:8087) ---")
    ensure_backend_services()

    base_url = f"http://localhost:{PORT_CLOTHOS_DAEMON}"

    if mode in ["all", "web", "command"]:
        launch_desktop_gui(
            url=f"{base_url}/",
            app_name="ClothOS Master Command Center",
            window_size="1380,880",
            window_pos="80,40"
        )
    elif mode == "hud":
        launch_desktop_gui(
            url=f"{base_url}/guis/desktop-hud/index.html",
            app_name="Desktop Glassmorphic HUD",
            window_size="440,110",
            window_pos="50,30"
        )
    elif mode == "portal":
        launch_desktop_gui(
            url=f"{base_url}/guis/index.html",
            app_name="ClothOS Antigravity Portal",
            window_size="1240,800"
        )
    elif mode == "screensaver":
        launch_desktop_gui(
            url=f"{base_url}/guis/neuro-screensaver/index.html",
            app_name="ClothOS 60fps Neuro-Screensaver",
            window_size="1280,720"
        )


def main():
    parser = argparse.ArgumentParser(description="ClothOS Desktop Startup & Legacy Cleanup Manager")
    parser.add_argument("--setup", action="store_true", help="Clean legacy, create modern shortcuts, register startup, and launch")
    parser.add_argument("--on-startup", action="store_true", help="Invoked automatically by Windows Startup on logon")
    parser.add_argument("--clean-legacy", action="store_true", help="Undo legacy shortcuts and startup scripts")
    parser.add_argument("--create-shortcuts", action="store_true", help="Create modern Antigravity shortcuts")
    parser.add_argument("--install-startup", action="store_true", help="Install to Windows Startup")
    parser.add_argument("--uninstall-startup", action="store_true", help="Remove from Windows Startup")
    parser.add_argument("--launch", action="store_true", help="Launch relevant desktop GUIs")
    parser.add_argument("--web", action="store_true", help="Target Web App Command Center")
    parser.add_argument("--hud", action="store_true", help="Target Desktop HUD")
    parser.add_argument("--portal", action="store_true", help="Target Master Portal")
    parser.add_argument("--screensaver", action="store_true", help="Target 60fps Neuro-Screensaver")

    args = parser.parse_args()

    # Determine launch target mode
    target_mode = "all"
    if args.web: target_mode = "web"
    elif args.hud: target_mode = "hud"
    elif args.portal: target_mode = "portal"
    elif args.screensaver: target_mode = "screensaver"

    if args.on_startup:
        print("[ClothOS Startup] System Boot / Logon event detected.")
        clean_legacy_artifacts()
        create_modern_shortcuts()
        launch_relevant_guis(mode="all")
        return

    if args.setup:
        clean_legacy_artifacts()
        create_modern_shortcuts()
        install_to_startup()
        launch_relevant_guis(mode="all")
        print("\n==================================================================")
        print("✓ ClothOS Desktop Suite Setup & Legacy Cleanup COMPLETE!")
        print("==================================================================")
        return

    if args.clean_legacy:
        clean_legacy_artifacts()
        return

    if args.create_shortcuts:
        create_modern_shortcuts()
        return

    if args.install_startup:
        install_to_startup()
        return

    if args.uninstall_startup:
        uninstall_startup()
        return

    if args.launch:
        launch_relevant_guis(mode=target_mode)
        return

    # Default action if no flags provided: perform full setup
    clean_legacy_artifacts()
    create_modern_shortcuts()
    install_to_startup()
    launch_relevant_guis(mode="all")


if __name__ == "__main__":
    main()
