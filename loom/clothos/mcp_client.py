"""
Model Context Protocol (MCP) Client & Tool Bridge (`loom/clothos/mcp_client.py`).

Adapted from Qwen-Agent's MCPManager:
- Connects to standard MCP servers (via stdio subprocess or HTTP/SSE).
- Dynamically discovers tools, inspects JSON schemas, and exposes them directly to Clothos.
- Enables plug-and-play integration with any standard MCP tool server (Postgres, SQLite, Git, Brave, etc.).
"""

from __future__ import annotations

import json
import logging
import subprocess
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("loom.clothos.mcp_client")


class StdioMCPServer:
    """Manages a local MCP server running over stdin/stdout JSON-RPC 2.0."""

    def __init__(self, name: str, command: str, args: Optional[List[str]] = None, env: Optional[Dict[str, str]] = None):
        self.name = name
        self.command = command
        self.args = args or []
        self.env = env
        self.proc: Optional[subprocess.Popen] = None
        self._request_id = 0
        self._lock = threading.Lock()
        self.tools: List[Dict[str, Any]] = []
        self.is_connected = False

    def start(self) -> bool:
        """Spawns the MCP server process and initializes session."""
        try:
            full_cmd = [self.command] + self.args
            self.proc = subprocess.Popen(
                full_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                env=self.env,
            )
            # Send MCP initialize request
            init_res = self._send_jsonrpc("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "ClothOS-Agent", "version": "1.0.0"},
            })
            if init_res and not init_res.get("error"):
                self.is_connected = True
                # Send initialized notification
                self._send_notification("notifications/initialized", {})
                self.refresh_tools()
                return True
            return False
        except Exception as exc:
            logger.error(f"Failed to start MCP server {self.name}: {exc}")
            return False

    def _send_jsonrpc(self, method: str, params: Dict[str, Any], timeout: float = 10.0) -> Optional[Dict[str, Any]]:
        with self._lock:
            if not self.proc or self.proc.poll() is not None:
                return None
            self._request_id += 1
            req_id = self._request_id
            payload = {
                "jsonrpc": "2.0",
                "id": req_id,
                "method": method,
                "params": params,
            }
            try:
                line = json.dumps(payload) + "\n"
                self.proc.stdin.write(line)
                self.proc.stdin.flush()

                # Read response
                resp_line = self.proc.stdout.readline()
                if resp_line:
                    return json.loads(resp_line.strip())
            except Exception as exc:
                logger.error(f"MCP RPC error [{self.name}.{method}]: {exc}")
            return None

    def _send_notification(self, method: str, params: Dict[str, Any]) -> None:
        with self._lock:
            if not self.proc or self.proc.poll() is not None:
                return
            payload = {
                "jsonrpc": "2.0",
                "method": method,
                "params": params,
            }
            try:
                line = json.dumps(payload) + "\n"
                self.proc.stdin.write(line)
                self.proc.stdin.flush()
            except Exception:
                pass

    def refresh_tools(self) -> List[Dict[str, Any]]:
        """Queries the server for its list of available tools."""
        res = self._send_jsonrpc("tools/list", {})
        if res and "result" in res and "tools" in res["result"]:
            self.tools = res["result"]["tools"]
        return self.tools

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Executes a specific tool on the MCP server."""
        res = self._send_jsonrpc("tools/call", {
            "name": tool_name,
            "arguments": arguments,
        })
        if not res:
            return {"error": f"MCP server '{self.name}' did not return a response."}
        if "error" in res:
            return {"error": res["error"]}
        return res.get("result", {})

    def stop(self) -> None:
        if self.proc and self.proc.poll() is None:
            try:
                self.proc.terminate()
                self.proc.wait(timeout=2.0)
            except Exception:
                self.proc.kill()
        self.is_connected = False


class MCPRegistry:
    """Central manager for all active MCP servers in ClothOS."""

    def __init__(self):
        self.servers: Dict[str, StdioMCPServer] = {}

    def register_server(self, name: str, command: str, args: Optional[List[str]] = None, env: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Registers and starts a new stdio MCP server."""
        if name in self.servers:
            return {"status": "ALREADY_REGISTERED", "name": name, "tools_count": len(self.servers[name].tools)}

        server = StdioMCPServer(name, command, args, env)
        ok = server.start()
        if ok:
            self.servers[name] = server
            return {
                "status": "ONLINE",
                "name": name,
                "tools_count": len(server.tools),
                "tools": [t.get("name") for t in server.tools],
            }
        else:
            return {"status": "FAILED", "name": name, "error": "Server failed initialization handshake."}

    def list_all_tools(self) -> List[Dict[str, Any]]:
        all_tools = []
        for sname, s in self.servers.items():
            for t in s.tools:
                all_tools.append({
                    "server": sname,
                    "name": t.get("name"),
                    "description": t.get("description", ""),
                    "inputSchema": t.get("inputSchema", {}),
                })
        return all_tools

    def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        server = self.servers.get(server_name)
        if not server:
            return {"error": f"MCP server '{server_name}' is not registered."}
        return server.call_tool(tool_name, arguments)


_MCP_REGISTRY = MCPRegistry()

def get_mcp_registry() -> MCPRegistry:
    return _MCP_REGISTRY
