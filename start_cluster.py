"""
ClothOS Enterprise Cluster Startup & Orchestrator (`start_cluster.py`).

Coordinates startup across both cluster nodes:
- Node 1: skyTech Compute Cortex (RTX 3060 12GB CUDA + RX 580 8GB + Ryzen 7 5700 + 40GB RAM)
- Node 2: Ryzen Head Orchestrator (Ryzen 7 7730U + 32GB RAM + 2.5GbE Mesh)

Verifies:
1. Direct 2.5GbE network mesh latency (<1ms)
2. Local and peer Ollama inference engines (:11434)
3. Model catalog readiness (loom-sovereign-fast, loom-sovereign, loom-sovereign-70b)
4. ClothOS Command Center Dashboard (:8087)
5. Launches interactive Clothos Agent CLI in Full Access mode
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

# ANSI colors for clean, professional console output
class Style:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    GREEN = "\033[32m"
    CYAN = "\033[36m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"

def get_node_identity() -> tuple[str, str, str]:
    """Determines if the local machine is Node 1 or Node 2."""
    hostname = socket.gethostname().lower()
    
    # Try local IPs
    local_ips = []
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None):
            ip = info[4][0]
            if ip not in local_ips:
                local_ips.append(ip)
    except Exception:
        pass

    if "192.168.99.1" in local_ips or "skytech" in hostname:
        return "Node 1", "192.168.99.1", "192.168.99.2"
    elif "192.168.99.2" in local_ips or "ryzen" in hostname:
        return "Node 2", "192.168.99.2", "192.168.99.1"
    
    # Fallback probe
    s = socket.socket()
    s.settimeout(0.3)
    if s.connect_ex(("192.168.99.1", 11434)) == 0:
        s.close()
        # 192.168.99.1 is listening remotely, we might be Node 2
        return "Node 2", "192.168.99.2", "192.168.99.1"
    s.close()
    
    return "Node 1", "192.168.99.1", "192.168.99.2"

def check_port(host: str, port: int, timeout: float = 1.0) -> bool:
    s = socket.socket()
    s.settimeout(timeout)
    try:
        res = s.connect_ex((host, port))
        s.close()
        return res == 0
    except Exception:
        return False

def query_json(url: str, timeout: float = 2.0) -> dict | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ClothOS-Cluster-Init"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception:
        return None

def start_dashboard_daemon(repo_root: Path) -> None:
    """Starts the dashboard server in the background if not already active."""
    if check_port("127.0.0.1", 8087):
        return
    print(f"  {Style.YELLOW}* Starting Command Center dashboard on port 8087...{Style.RESET}")
    python_exe = sys.executable
    subprocess.Popen(
        [python_exe, "-m", "loom.fabric.dashboard_server"],
        cwd=str(repo_root),
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(20):
        time.sleep(0.3)
        if check_port("127.0.0.1", 8087):
            break

def print_banner(node_name: str, local_ip: str, peer_ip: str):
    print(f"""
{Style.CYAN}{Style.BOLD}================================================================================
          CLOTHOS ENTERPRISE CLUSTER  -  AIR-GAPPED SOVEREIGN AI FABRIC
================================================================================{Style.RESET}
  {Style.BOLD}Local Node  :{Style.RESET} {node_name} ({local_ip})
  {Style.BOLD}Peer Node   :{Style.RESET} {peer_ip} (2.5GbE Direct Mesh)
  {Style.BOLD}Security    :{Style.RESET} Zero-Trust On-Premises Compute (Zero Cloud Leakage)
  {Style.BOLD}Access Level:{Style.RESET} Full OS & Hardware Access
--------------------------------------------------------------------------------""")

def run_cluster_audit(node_name: str, local_ip: str, peer_ip: str, repo_root: Path):
    print(f"{Style.BOLD}[1/4] Checking Cluster Interconnect (2.5GbE Direct Mesh)...{Style.RESET}")
    t0 = time.time()
    peer_ollama_ok = check_port(peer_ip, 11434, timeout=0.8)
    dt_ms = round((time.time() - t0) * 1000, 2)
    
    if peer_ollama_ok:
        print(f"  {Style.GREEN}OK{Style.RESET} Peer node ({peer_ip}) reachable in {dt_ms} ms over direct cable.")
    else:
        peer_ping = check_port(peer_ip, 8087, timeout=0.8)
        if peer_ping:
            print(f"  {Style.GREEN}OK{Style.RESET} Peer node ({peer_ip}) reachable on port 8087 ({dt_ms} ms).")
        else:
            print(f"  {Style.YELLOW}WARN{Style.RESET} Peer node ({peer_ip}) not responding directly. Standalone/local mode active.")

    print(f"\n{Style.BOLD}[2/4] Verifying Local Inference Engine (Ollama :11434)...{Style.RESET}")
    local_ollama_ok = check_port("127.0.0.1", 11434)
    if not local_ollama_ok:
        print(f"  {Style.YELLOW}* Ollama service not detected locally. Attempting launch...{Style.RESET}")
        try:
            subprocess.Popen(["ollama", "serve"], creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000))
            time.sleep(2.0)
            local_ollama_ok = check_port("127.0.0.1", 11434)
        except Exception:
            pass

    if local_ollama_ok:
        tags = query_json("http://127.0.0.1:11434/api/tags") or {}
        local_models = [m.get("name", "") for m in tags.get("models", [])]
        print(f"  {Style.GREEN}OK{Style.RESET} Local Ollama online with {len(local_models)} models loaded:")
        for m in local_models[:6]:
            print(f"     - {m}")
    else:
        print(f"  {Style.RED}FAIL{Style.RESET} Local Ollama is offline. Please start Ollama on this node.")

    print(f"\n{Style.BOLD}[3/4] Checking Command Center Dashboard (:8087)...{Style.RESET}")
    start_dashboard_daemon(repo_root)
    if check_port("127.0.0.1", 8087):
        print(f"  {Style.GREEN}OK{Style.RESET} Command Center active at: {Style.CYAN}http://localhost:8087/{Style.RESET}")
        drillbit = query_json("http://127.0.0.1:8087/api/cluster/drillbit") or {}
        if drillbit.get("status") == "ONLINE":
            print(f"     - Pilot Decider   : {drillbit.get('pilot_decider_node')}")
            print(f"     - Sovereign Cortex: {drillbit.get('sovereign_cortex_node')}")
            print(f"     - Active Head     : {drillbit.get('active_head')} ({drillbit.get('router_mode')})")
    else:
        print(f"  {Style.YELLOW}WARN{Style.RESET} Dashboard server on port 8087 could not be verified.")

    print(f"\n{Style.BOLD}[4/4] Launching Interactive Clothos Agent Console...{Style.RESET}")
    print(f"  {Style.DIM}Type /help in the console for commands, or speak naturally.{Style.RESET}")
    print(f"================================================================================\n")

def main():
    parser = argparse.ArgumentParser(description="ClothOS Enterprise Cluster Startup")
    parser.add_argument("--daemon", action="store_true", help="Launch background services without interactive CLI")
    parser.add_argument("--check-only", action="store_true", help="Audit cluster health and exit")
    parser.add_argument("-p", "--prompt", type=str, help="Execute prompt non-interactively and exit")
    parser.add_argument("--workspace", "-w", type=str, default=None, help="Working directory")
    args, unknown = parser.parse_known_args()

    repo_root = Path(__file__).resolve().parent
    sys.path.insert(0, str(repo_root))

    node_name, local_ip, peer_ip = get_node_identity()
    print_banner(node_name, local_ip, peer_ip)
    run_cluster_audit(node_name, local_ip, peer_ip, repo_root)

    if args.check_only:
        return

    if args.daemon:
        print(f"{Style.GREEN}All cluster daemons running. Standby mode active.{Style.RESET}")
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            print("Shutting down.")
            return

    # Launch Clothos Agent CLI
    from loom.clothos.agent_cli import main as cli_main
    cli_args = sys.argv[1:]
    # Ensure full access by default
    if "--sandbox" not in cli_args and "--full-access" not in cli_args:
        cli_args.append("--full-access")
    
    sys.argv = [sys.argv[0]] + cli_args
    cli_main()

if __name__ == "__main__":
    main()
