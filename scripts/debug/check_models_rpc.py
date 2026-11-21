import re

path = r'C:\Program Files\WindowsApps\OpenClawFoundation.OpenClawGateway_2026.10.900.0_x64__rfcbke2p71se2\app\openclaw.mjs'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

print('Total size of openclaw.mjs:', len(text))
matches = list(re.finditer(r'["\']models\.list["\']', text))
print('models.list occurrences:', len(matches))
for m in matches[:5]:
    p = m.start()
    print('--- MATCH ---')
    print(text[max(0, p-150):min(len(text), p+350)])
