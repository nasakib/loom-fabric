with open(r'C:\Program Files\WindowsApps\OpenClawFoundation.OpenClawGateway_2026.10.900.0_x64__rfcbke2p71se2\app\dist\control-ui\assets\control-ui-boot-chat-JvQnPrTd.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
m = re.search(r'function ga\(', text)
if m:
    p = m.start()
    print('--- function ga ---')
    print(text[p:p+600])
else:
    print('function ga not found, searching ga=')
    matches = list(re.finditer(r'ga\s*=\s*', text))
    for m in matches[:5]:
        p = m.start()
        print(text[max(0, p-50):min(len(text), p+150)])
