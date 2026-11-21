import sys
sys.stdout.reconfigure(encoding='utf-8')
with open('loom/fabric/dashboard_server.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = '/api/telemetry/sse'
idx = text.find(target)
while idx != -1:
    line_start = text.rfind('\n', 0, idx)
    line_end = text.find('\n', idx)
    print(f"Match at char {idx}: {text[line_start:line_end].strip()}")
    if '@app' in text[line_start-20:line_end+20]:
        print("Function definition:")
        print(text[line_start:line_start+1500])
        print("="*60)
    idx = text.find(target, idx + len(target))
