with open(r'C:\Program Files\WindowsApps\OpenClawFoundation.OpenClawGateway_2026.10.900.0_x64__rfcbke2p71se2\app\dist\model-picker-BoxD-5Kv.mjs', 'r', encoding='utf-8') as f:
    text = f.read()

import re
# look for export functions or functions that return models
for m in re.finditer(r'function ([a-zA-Z0-9_$]+)\s*\(', text):
    fname = m.group(1)
    p = m.start()
    snippet = text[p:min(len(text), p+300)]
    if 'model' in snippet.lower() or 'catalog' in snippet.lower() or 'picker' in snippet.lower():
        print(f'Function {fname}:', snippet[:180].replace('\n', ' '))
