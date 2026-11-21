import urllib.request
import json
import time

for port, name in [(8087, 'ClothOS Command Center'), (8086, 'ClothOS Universal React Native App')]:
    url = f'http://127.0.0.1:{port}/'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'WCOS-Probe/3.2'})
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            content = resp.read()
            print(f"OK: {name} on {url}: Status {resp.status}, Content Length {len(content)} bytes")
    except Exception as e:
        print(f"FAIL: {name} on {url}: Error {e}")

try:
    with urllib.request.urlopen('http://127.0.0.1:8087/api/telemetry/taskmanager', timeout=3.0) as resp:
        snap = json.loads(resp.read().decode('utf-8'))
        cpu_pct = snap.get('cpu', {}).get('overall_percent')
        pooled_gb = snap.get('memory', {}).get('total_pooled_gb')
        g0 = snap.get('gpu0', {}).get('name')
        print(f"OK: Telemetry API - Overall CPU: {cpu_pct}% | Pooled RAM: {pooled_gb} GB | GPU 0: {g0}")
except Exception as e:
    print(f"FAIL: Telemetry API: Error {e}")
