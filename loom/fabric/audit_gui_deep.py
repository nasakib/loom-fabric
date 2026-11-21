import re
from pathlib import Path

# 1. Get registered routes in dashboard_server.py
server_code = Path("loom/fabric/dashboard_server.py").read_text(encoding="utf-8")
registered_routes = set(re.findall(r'@app\.(?:get|post|put|delete)\("([^"]+)"\)', server_code))
print(f"Total registered backend endpoints: {len(registered_routes)}")

# 2. Check visual_dashboard.html
print("\n--- AUDITING visual_dashboard.html ---")
visual_html = Path("loom/fabric/visual_dashboard.html").read_text(encoding="utf-8")

# Find all fetch calls in visual_dashboard.html
visual_fetches = set(re.findall(r'fetch\([\'"`]([^\'"`?]+)', visual_html))
print(f"Total fetch endpoints in visual_dashboard.html: {len(visual_fetches)}")
for endpoint in sorted(visual_fetches):
    # Normalize endpoint
    clean_ep = endpoint
    # Match route patterns
    matched = False
    for r in registered_routes:
        # replace {param} with regex
        pattern = "^" + re.sub(r'\{[a-zA-Z0-9_]+\}', r'[^/]+', r) + "$"
        if re.match(pattern, clean_ep):
            matched = True
            break
    if not matched:
        print(f"  [MISSING IN BACKEND] {endpoint}")
    else:
        print(f"  [OK] {endpoint}")

# Check onclick handlers in visual_dashboard.html
print("\n--- Checking onclick functions in visual_dashboard.html ---")
onclicks = re.findall(r'onclick="([a-zA-Z0-9_]+)\(', visual_html)
for fn in set(onclicks):
    if f"function {fn}" not in visual_html and f"{fn} =" not in visual_html:
        print(f"  [UNDEFINED FUNCTION] {fn}")
    else:
        print(f"  [FUNCTION OK] {fn}")

# Check getElementById in visual_dashboard.html
print("\n--- Checking getElementById in visual_dashboard.html ---")
get_elems = set(re.findall(r'getElementById\([\'"]([^\'"]+)[\'"]\)', visual_html))
for elem_id in sorted(get_elems):
    if f'id="{elem_id}"' not in visual_html and f"id='{elem_id}'" not in visual_html:
        print(f"  [MISSING HTML ID] {elem_id}")

# 3. Check embedded UI in dashboard_server.py
print("\n--- AUDITING embedded UI in dashboard_server.py ---")
# Extract embedded UI
idx = server_code.find('def serve_dashboard_ui')
if idx != -1:
    embedded_html = server_code[idx:]
    emb_fetches = set(re.findall(r'fetch\([\'"`]([^\'"`?]+)', embedded_html))
    print(f"Total fetch endpoints in embedded UI: {len(emb_fetches)}")
    for endpoint in sorted(emb_fetches):
        # Handle string template interpolations like ${...}
        clean_pattern = "^" + re.sub(r'\$\{[^}]+\}', r'[^/]+', endpoint) + "$"
        matched = False
        for r in registered_routes:
            r_pattern = "^" + re.sub(r'\{[a-zA-Z0-9_]+\}', r'[^/]+', r) + "$"
            if re.match(r_pattern, endpoint) or re.match(clean_pattern, r):
                matched = True
                break
        if not matched:
            print(f"  [MISSING IN BACKEND] {endpoint}")

    emb_onclicks = re.findall(r'onclick="([a-zA-Z0-9_]+)\(', embedded_html)
    for fn in set(emb_onclicks):
        if f"function {fn}" not in embedded_html and f"{fn} =" not in embedded_html and f"async function {fn}" not in embedded_html:
            print(f"  [UNDEFINED FUNCTION in embedded] {fn}")

    emb_elems = set(re.findall(r'getElementById\([\'"]([^\'"]+)[\'"]\)', embedded_html))
    for elem_id in sorted(emb_elems):
        if f'id="{elem_id}"' not in embedded_html and f"id='{elem_id}'" not in embedded_html:
            print(f"  [MISSING HTML ID in embedded] {elem_id}")

    # Check tab buttons vs tab contents in embedded
    tab_btns = set(re.findall(r"switchTab\('([^']+)'", embedded_html))
    tab_contents = set(re.findall(r'id="tab-([^"]+)"', embedded_html))
    print(f"\nTab buttons in embedded ({len(tab_btns)}):", sorted(tab_btns))
    print(f"Tab contents in embedded ({len(tab_contents)}):", sorted(tab_contents))
    missing_tab_contents = tab_btns - tab_contents
    if missing_tab_contents:
        print("  [BROKEN TABS WITHOUT CONTENT]:", missing_tab_contents)
    missing_tab_btns = tab_contents - tab_btns
    if missing_tab_btns:
        print("  [TAB CONTENTS WITHOUT BUTTON]:", missing_tab_btns)

    # Check for unclosed tags or syntax issues in embedded
    print(f"\nEmbedded UI character count: {len(embedded_html)}")


# 4. Check apps/loom-react-native/dist/index.html
print("\n--- AUDITING apps/loom-react-native/dist/index.html ---")
rn_path = Path("apps/loom-react-native/dist/index.html")
if rn_path.exists():
    rn_html = rn_path.read_text(encoding="utf-8")
    rn_fetches = set(re.findall(r'fetch\([\'"`]([^\'"`?]+)', rn_html))
    print(f"Total fetch endpoints in React Native HTML: {len(rn_fetches)}")
    for raw_endpoint in sorted(rn_fetches):
        endpoint = raw_endpoint.replace("${BACKEND_URL}", "").replace("${host}", "127.0.0.1").replace("${p}", "8087")
        if endpoint.startswith("http://127.0.0.1:8087"):
            endpoint = endpoint[len("http://127.0.0.1:8087"):]
        clean_pattern = "^" + re.sub(r'\$\{[^}]+\}', r'[^/]+', endpoint) + "$"
        matched = False
        for r in registered_routes:
            r_pattern = "^" + re.sub(r'\{[a-zA-Z0-9_]+\}', r'[^/]+', r) + "$"
            if re.match(r_pattern, endpoint) or re.match(clean_pattern, r):
                matched = True
                break
        if not matched:
            print(f"  [MISSING IN BACKEND] {endpoint} (from: {raw_endpoint})")
        else:
            print(f"  [OK] {endpoint}")

    rn_tab_btns = set(re.findall(r"switchTab\('([^']+)'", rn_html))
    rn_tab_contents = set(re.findall(r'id="tab-([^"]+)"', rn_html))
    print(f"\nTab buttons in RN ({len(rn_tab_btns)}):", sorted(rn_tab_btns))
    print(f"Tab contents in RN ({len(rn_tab_contents)}):", sorted(rn_tab_contents))
    missing_rn_tab_contents = rn_tab_btns - rn_tab_contents
    if missing_rn_tab_contents:
        print("  [BROKEN RN TABS WITHOUT CONTENT]:", missing_rn_tab_contents)
    missing_rn_tab_btns = rn_tab_contents - rn_tab_btns
    if missing_rn_tab_btns:
        print("  [RN TAB CONTENTS WITHOUT BUTTON]:", missing_rn_tab_btns)


