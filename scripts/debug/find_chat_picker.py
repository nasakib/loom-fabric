with open(r'C:\Program Files\WindowsApps\OpenClawFoundation.OpenClawGateway_2026.10.900.0_x64__rfcbke2p71se2\app\dist\control-ui\assets\control-ui-core-oy3eRRbJ.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
# look for chat composer or chat model selector
matches = list(re.finditer(r'chat\.modelControls|modelControls|modelPicker', text))
print('Matches in control-ui-core:', len(matches))
for m in matches[:5]:
    p = m.start()
    print('--- MATCH ---')
    print(text[max(0, p-100):min(len(text), p+300)])
