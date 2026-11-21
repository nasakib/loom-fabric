path = r'C:\Program Files\WindowsApps\OpenClawFoundation.OpenClawGateway_2026.10.900.0_x64__rfcbke2p71se2\app\dist\model-picker-BoxD-5Kv.mjs'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

print('Length:', len(text))
print(text[:1200])
