with open(r'C:\Program Files\WindowsApps\OpenClawFoundation.OpenClawGateway_2026.10.900.0_x64__rfcbke2p71se2\app\dist\control-ui\assets\control-ui-boot-chat-JvQnPrTd.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
# look for chatModelCatalog or how models are added to the picker
for m in re.finditer(r'chatModelCatalog', text):
    p = m.start()
    print('--- chatModelCatalog ---')
    print(text[max(0, p-100):min(len(text), p+300)])
