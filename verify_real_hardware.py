import httpx

# 1. List devices
r = httpx.get('http://127.0.0.1:8002/v1/csp/virtual-devices')
print('=== 1. Live Device List ===')
print('Status:', r.status_code)
for d in r.json()['devices']:
    print(f"  Device {d['device_index']}: {d['name']} ({d['total_memory_gb']} GB, Available: {d['available_memory_gb']} GB, Cores: {d['cpu_cores']})")

# 2. Test Real Physical OOM on Device 0 (Requesting 4GB when only ~1.8GB is free)
print('\n=== 2. Real Physical OOM on Device 0 (RTX 3060) ===')
oom_res = httpx.post('http://127.0.0.1:8002/v1/csp/virtual-devices/dispatch', json={
    'device_index': 0,
    'workload_id': 'test-real-gpu-oom',
    'required_vram_gb': 4.0,
    'prompt': 'Hello'
}).json()
print('OOM Response from Physical GPU:')
print('  ', oom_res.get('detail'))

# 3. Real GPU Dispatch on Device 0 within available VRAM (1.0 GB)
print('\n=== 3. Real GPU Dispatch within Available VRAM (Device 0) ===')
d0 = httpx.post('http://127.0.0.1:8002/v1/csp/virtual-devices/dispatch', json={
    'device_index': 0,
    'workload_id': 'test-real-gpu-ok',
    'required_vram_gb': 1.0,
    'prompt': 'Give me a 3-word slogan for VectorCore.'
}, timeout=30.0).json()
print('Target:', d0.get('execution_target'))
print('Speed:', d0.get('tokens_per_sec'), 'tok/s')
print('Response:', d0.get('response_text', '').strip())
print('Verified:', d0.get('real_hardware_verified'))

# 4. Dispatch to Device 1 (Real Physical Cluster WIN-7CMAQLVP8MV with 31.33 GB Memory)
print('\n=== 4. Real Physical Cluster Dispatch (Device 1) ===')
d1 = httpx.post('http://127.0.0.1:8002/v1/csp/virtual-devices/dispatch', json={
    'device_index': 1,
    'workload_id': 'test-real-cluster',
    'required_vram_gb': 4.0,  # 4GB succeeds seamlessly on Device 1!
    'iterations': 5000000
}, timeout=30.0).json()
print('Target:', d1.get('execution_target'))
print('Remote Host Executed:', d1.get('remote_host_executed'))
print('Checksum Verified:', d1.get('checksum_verified'))
print('Remote Compute Time:', d1.get('remote_compute_time_sec'), 's')
print('Total Roundtrip:', d1.get('total_network_roundtrip_sec'), 's')
print('Cluster Total Cores:', d1.get('cluster_total_cores'))
print('Verified:', d1.get('real_hardware_verified'))
