with open(r'C:\Program Files\WindowsApps\OpenClawFoundation.OpenClawGateway_2026.10.900.0_x64__rfcbke2p71se2\app\dist\model-picker-BoxD-5Kv.mjs', 'r', encoding='utf-8') as f:
    text = f.read()

import re
m = re.search(r'function maybeFilterModelsByProvider.*', text)
if m:
    print('--- maybeFilterModelsByProvider ---')
    print(text[m.start():m.start()+1200])

m2 = re.search(r'function createProviderAuthChecker.*', text)
if m2:
    print('--- createProviderAuthChecker ---')
    print(text[m2.start():m2.start()+1200])
