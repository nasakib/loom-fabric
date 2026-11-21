with open('loom/fabric/dashboard_server.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
scripts = re.findall(r'<script(?![^>]*src=)[^>]*>(.*?)</script>', text, re.DOTALL)
code = scripts[1]

brackets = {'(': ')', '[': ']', '{': '}'}
stack = []
in_str = None
escape = False
in_line_comment = False
in_block_comment = False

line_num = 1
col_num = 1
errors = []

i = 0
n = len(code)
while i < n:
    c = code[i]
    if c == '\n':
        line_num += 1
        col_num = 0
        in_line_comment = False
    col_num += 1

    if in_line_comment:
        i += 1
        continue
    if in_block_comment:
        if c == '*' and i + 1 < n and code[i+1] == '/':
            in_block_comment = False
            i += 2
            continue
        i += 1
        continue

    if in_str:
        if escape:
            escape = False
        elif c == '\\':
            escape = True
        elif c == in_str:
            in_str = None
        i += 1
        continue

    # Not in string or comment
    if c == '/' and i + 1 < n:
        if code[i+1] == '/':
            in_line_comment = True
            i += 2
            continue
        elif code[i+1] == '*':
            in_block_comment = True
            i += 2
            continue

    if c in ('"', "'", '`'):
        in_str = c
        escape = False
        i += 1
        continue

    if c in brackets.keys():
        stack.append((c, line_num, col_num))
    elif c in brackets.values():
        if not stack:
            errors.append(f"Unmatched closing {c} at line {line_num}:{col_num}")
        else:
            top, tl, tc = stack.pop()
            if brackets[top] != c:
                errors.append(f"Mismatched {top} from line {tl}:{tc} closed by {c} at line {line_num}:{col_num}")

    i += 1

if stack:
    for top, tl, tc in stack[-10:]:
        errors.append(f"Unclosed {top} from line {tl}:{tc}")

print(f"Bracket check errors: {len(errors)}")
for e in errors[:20]:
    print(e)
