with open('temp_dashboard_script.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

import re

current_func = None
func_is_async = False
func_start_line = 0
brace_count = 0

issues = []

for idx, line in enumerate(lines, 1):
    # Detect function declaration
    m = re.search(r'(async\s+)?function\s+([a-zA-Z0-9_]+)\s*\(', line)
    if m:
        is_async = bool(m.group(1))
        name = m.group(2)
        current_func = name
        func_is_async = is_async
        func_start_line = idx

    # Check for await
    if re.search(r'\bawait\b', line):
        if not func_is_async:
            issues.append((idx, current_func, line.strip()))

print(f"Found {len(issues)} illegal await statements without async:")
for line_no, func_name, text in issues:
    print(f"Line {line_no} in function '{func_name}': {text}")
