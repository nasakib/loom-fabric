"""babelForge MCP Server for ClothOS.

Exposes deterministic topological state-space simulations, graph invariant verification,
and distributed ClothOS scheduling optimization via Model Context Protocol (MCP).
"""

from __future__ import annotations
import sys
import json
from typing import Any, Dict, Optional

# Import core algorithms
from servers.babelforge_mcp.algorithms import (
    validate_graph_invariants as alg_validate,
    simulate_subgraph_execution as alg_simulate,
    optimize_clothos_schedule as alg_optimize
)

try:
    from mcp.server.mcpserver import MCPServer
    HAS_MCP_LIB = True
except ImportError:
    HAS_MCP_LIB = False


if HAS_MCP_LIB:
    app = MCPServer("babelforge")

    @app.tool()
    def validate_graph_invariants(graph_json: Dict[str, Any]) -> Dict[str, Any]:
        """Validates topological and mathematical integrity of babelForge connectome graphs."""
        return alg_validate(graph_json)

    @app.tool()
    def simulate_subgraph_execution(
        subgraph_id: str,
        node_config: Dict[str, Any],
        timesteps: int = 100
    ) -> Dict[str, Any]:
        """Deterministically simulates Kuramoto oscillator phase locking across subgraph nodes."""
        return alg_simulate(subgraph_id=subgraph_id, node_config=node_config, timesteps=timesteps)

    @app.tool()
    def optimize_clothos_schedule(
        task_graph: Dict[str, Any],
        cluster_topology: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Uses babelForge routing algorithms to balance heterogeneous distributed compute across ClothOS workers."""
        return alg_optimize(task_graph=task_graph, cluster_topology=cluster_topology)

    def main():
        app.run(transport="stdio")

else:
    # Direct stdio JSON-RPC fallback
    def main():
        for line in sys.stdin:
            if not line.strip():
                continue
            try:
                req = json.loads(line)
                method = req.get("method")
                req_id = req.get("id")
                params = req.get("params", {})

                if method == "tools/list":
                    res = {
                        "tools": [
                            {"name": "validate_graph_invariants", "description": "Validate graph invariants"},
                            {"name": "simulate_subgraph_execution", "description": "Simulate Kuramoto phase locking"},
                            {"name": "optimize_clothos_schedule", "description": "Optimize ClothOS task schedule"}
                        ]
                    }
                elif method == "tools/call":
                    t_name = params.get("name")
                    args = params.get("arguments", {})
                    if t_name == "validate_graph_invariants":
                        out = alg_validate(args.get("graph_json", {}))
                    elif t_name == "simulate_subgraph_execution":
                        out = alg_simulate(args.get("subgraph_id", "subgraph_0"), args.get("node_config", {}), args.get("timesteps", 100))
                    elif t_name == "optimize_clothos_schedule":
                        out = alg_optimize(args.get("task_graph", {}), args.get("cluster_topology"))
                    else:
                        out = {"error": f"Unknown tool {t_name}"}
                    res = {"content": [{"type": "text", "text": json.dumps(out)}]}
                else:
                    res = {"error": "Unsupported method"}

                sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": req_id, "result": res}) + "\n")
                sys.stdout.flush()
            except Exception as e:
                sys.stderr.write(f"MCP error: {e}\n")


if __name__ == "__main__":
    main()
