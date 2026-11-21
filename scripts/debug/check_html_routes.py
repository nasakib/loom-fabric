with open('loom/fabric/dashboard_server.py', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('response_class=HTMLResponse')
while idx != -1:
    line_start = text.rfind('\n', 0, idx)
    line_end = text.find('\n', idx)
    print("HTML route:", text[line_start:line_end].strip())
    idx = text.find('response_class=HTMLResponse', idx + 1)
