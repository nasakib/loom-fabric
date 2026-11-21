import os, re

assets_dir = r'C:\Program Files\WindowsApps\OpenClawFoundation.OpenClawGateway_2026.10.900.0_x64__rfcbke2p71se2\app\dist\control-ui\assets'

for fname in os.listdir(assets_dir):
    if fname.endswith('.js'):
        fpath = os.path.join(assets_dir, fname)
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
            if 'model-picker' in content or 'modelPicker' in content or 'primaryModel' in content or 'modelSelector' in content:
                print('Found in:', fname)
                for m in re.finditer(r'modelpicker|model-picker|primarymodel', content, re.IGNORECASE):
                    p = m.start()
                    print('   ', content[max(0, p-60):min(len(content), p+120)])
        except Exception:
            pass
