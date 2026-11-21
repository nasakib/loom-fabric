with open('loom/fabric/dashboard_server.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re

# Find all external scripts
scripts = re.findall(r'<script[^>]*src=[\'"]([^\'"]+)[\'"]', text)
print("External scripts in dashboard_server.py:")
for s in scripts:
    print("  ", s)

# Find all script blocks
inline_scripts = re.findall(r'<script(?![^>]*src=)[^>]*>(.*?)</script>', text, re.DOTALL)
print(f"Found {len(inline_scripts)} inline script blocks.")
for i, s in enumerate(inline_scripts):
    print(f"Block {i}: length {len(s)}")
    # Check if mermaid is referenced without typeof
    if 'mermaid.' in s:
        lines_with_mermaid = [l.strip() for l in s.splitlines() if 'mermaid.' in l]
        print(f"  Mermaid usages in block {i}:", lines_with_mermaid)
