with open('loom/fabric/dashboard_server.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re

# Find all onclick and onchange handlers
handlers = re.findall(r'on(?:click|change)=[\'"]([^\'"]+)[\'"]', text)
print(f"Found {len(handlers)} event handlers in HTML:")

# Extract function names called
called_funcs = set()
for h in handlers:
    m = re.match(r'([a-zA-Z0-9_]+)\s*\(', h.strip())
    if m:
        called_funcs.add(m.group(1))

# Find all defined functions in script
defined_funcs = set(re.findall(r'function\s+([a-zA-Z0-9_]+)\s*\(', text))

print(f"Called functions count: {len(called_funcs)}")
print(f"Defined functions count: {len(defined_funcs)}")

missing = called_funcs - defined_funcs
print("Missing functions called in HTML:", missing)
