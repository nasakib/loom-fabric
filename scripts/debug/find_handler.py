import os, re

dist_path = r'C:\Program Files\WindowsApps\OpenClawFoundation.OpenClawGateway_2026.10.900.0_x64__rfcbke2p71se2\app\dist'

# Search files for models.list implementation
for fname in os.listdir(dist_path):
    if fname.endswith('.mjs') or fname.endswith('.js'):
        fpath = os.path.join(dist_path, fname)
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
            if 'models.list' in content and 'registerHandler' in content or 'registerMethod' in content or 'case "models.list"' in content or 'case `models.list`' in content:
                print('Found models.list handler in:', fname)
            if 'modelPicker' in content or 'resolveModelList' in content or 'buildModelCatalog' in content:
                print('Found catalog/picker in:', fname)
        except Exception:
            pass
