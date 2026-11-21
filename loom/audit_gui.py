import re
from pathlib import Path

server_code = Path("loom/fabric/dashboard_server.py").read_text(encoding="utf-8")
routes = re.findall(r'@app\.(get|post|put|delete)\("([^"]+)"\)', server_code)
print(f"Total routes in dashboard_server.py: {len(routes)}")

html_routes = [r for r in routes if r[1] in ("/", "/dashboard", "/visual", "/gui") or "html" in r[1]]
print("HTML/root routes:", html_routes)

# Check all routes serving HTMLResponse
for match in re.finditer(r'@app\.(get|post)\("([^"]+)".*?def\s+([a-zA-Z0-9_]+)\(.*?\)\s*(?:->\s*HTMLResponse)?:', server_code, re.DOTALL):
    snippet = server_code[match.start():match.start()+300]
    if "HTMLResponse" in snippet or "html" in match.group(2):
        print(f"Route: {match.group(2)} -> Function: {match.group(3)}")
