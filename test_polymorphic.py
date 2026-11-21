import httpx

with httpx.Client(base_url='http://127.0.0.1:8002') as client:
    # 1. Check initial state
    r1 = client.get('/v1/csp/polymorphic/state')
    print('1. Initial State:', r1.json()['operating_mode'], 'VRAM Slice:', r1.json()['vram_slice'])

    # 2. Local Workload (8GB) - fits in local dual-GPU VRAM
    r2 = client.post('/v1/csp/polymorphic/workload', json={
        'consumer_id': 'local_user',
        'consumer_geohash': 'dn5bpq',
        'workload_type': 'ai_inference',
        'target_spec': {'required_vram_gb': 8.0, 'model_id': 'qwen2.5:7b'},
        'max_acceptable_rate_usd_hr': 0.50
    })
    job1 = r2.json()
    print('2. Workload 1 (8GB):', job1['role_adopted'])
    print('   Source:', job1['allocation_source'])
    print('   Remaining CSP VRAM:', job1['remaining_mesh_offered_vram_gb'], 'GB')

    # 3. Burst Workload (16GB) - exceeds remaining 12GB local capacity, triggers dynamic CSC Mesh Borrowing!
    r3 = client.post('/v1/csp/polymorphic/workload', json={
        'consumer_id': 'local_user',
        'consumer_geohash': 'dn5bpq',
        'workload_type': 'cloud_gaming',
        'target_spec': {'required_vram_gb': 16.0, 'target_resolution': '1440p120'},
        'max_acceptable_rate_usd_hr': 1.00
    })
    job2 = r3.json()
    print('3. Workload 2 (16GB Burst):', job2['role_adopted'])
    print('   Source:', job2['allocation_source'])
    print('   RTT Latency:', job2.get('ping_rtt_ms'), 'ms')

    # 4. Check state mid-execution
    r4 = client.get('/v1/csp/polymorphic/state')
    print('4. State Mid-Execution:', r4.json()['operating_mode'], '| Local Jobs:', r4.json()['active_local_workloads_count'])

    # 5. Release Workload 1
    job_id = job1['job_id']
    r5 = client.post(f'/v1/csp/polymorphic/release/{job_id}')
    print('5. Released Workload 1:', r5.json()['status'], '| Freed VRAM:', r5.json()['freed_vram_gb'], 'GB | New Offered CSP VRAM:', r5.json()['new_offered_csp_vram_gb'], 'GB')

    # 6. Final State
    r6 = client.get('/v1/csp/polymorphic/state')
    print('6. Final State:', r6.json()['operating_mode'], '| Offered CSP VRAM:', r6.json()['vram_slice']['offered_mesh_csp_gb'], 'GB')
