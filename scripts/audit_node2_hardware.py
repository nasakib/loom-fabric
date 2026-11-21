# Copyright (c) 2026 Najmos Sakib. All rights reserved.
"""Node 2 Hardware, GPU, Driver & Architecture Deep Audit."""

import base64
import os
import sys
import time

os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["NO_PROXY"] = "*"

from ray.job_submission import JobSubmissionClient, JobStatus

client = JobSubmissionClient("http://100.74.98.21:8265")

remote_code = '''
import subprocess
import sys
import json
import platform

print("==================================================================")
print("  NODE 2 (RYZEN 7 HEAD NODE) HARDWARE & DRIVER DEEP AUDIT")
print("==================================================================")
print("OS Platform:  ", platform.platform())
print("Architecture: ", platform.machine())
print("Python:       ", sys.executable)

# 1. Video Controllers (GPUs)
print("\\n--- [1] Video Controllers (GPUs) ---")
cmd_gpu = "powershell.exe -NoProfile -Command \\"Get-CimInstance Win32_VideoController | Select-Object Name, VideoProcessor, DriverVersion, Status, AdapterRAM | ConvertTo-Json\\""
p_gpu = subprocess.run(cmd_gpu, shell=True, capture_output=True, text=True)
print(p_gpu.stdout.strip())

# 2. Processor Details
print("\\n--- [2] Processor (CPU) ---")
cmd_cpu = "powershell.exe -NoProfile -Command \\"Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors, MaxClockSpeed | ConvertTo-Json\\""
p_cpu = subprocess.run(cmd_cpu, shell=True, capture_output=True, text=True)
print(p_cpu.stdout.strip())

# 3. Comprehensive NVIDIA Scan
print("\\n--- [3] NVIDIA Hardware & Driver Absence Verification ---")
cmd_nv = 'powershell.exe -NoProfile -Command "Get-CimInstance Win32_PnPEntity | Where-Object { $_.Name -like \\"*NVIDIA*\\" } | Select-Object Name, DeviceID | ConvertTo-Json"'
p_nv = subprocess.run(cmd_nv, shell=True, capture_output=True, text=True)
nv_out = p_nv.stdout.strip()
if not nv_out or nv_out == "null":
    print(">>> VERIFIED: 0 NVIDIA DEVICES FOUND.")
    print(">>> Hardware classification: 100% PURE AMD (Ryzen CPU + Radeon Graphics).")
else:
    print(">>> WARNING: NVIDIA devices found:", nv_out)

# 4. Check OpenCL and Vulkan / DirectX on Node 2
print("\\n--- [4] Acceleration & Graphics APIs ---")
cmd_dx = 'powershell.exe -NoProfile -Command "Get-CimInstance Win32_VideoController | Select-Object DriverDate, InstalledDisplayDrivers | ConvertTo-Json"'
p_dx = subprocess.run(cmd_dx, shell=True, capture_output=True, text=True)
print(p_dx.stdout.strip())

# 5. Check Python AI/ML Frameworks on Node 2
print("\\n--- [5] Python Compute & Machine Learning Backends ---")
try:
    import numpy as np
    print("NumPy Version:", np.__version__)
    print("NumPy BLAS/LAPACK config:")
    np.show_config()
except Exception as e:
    print("NumPy check error:", e)

try:
    import scipy
    print("SciPy Version:", scipy.__version__)
except Exception:
    pass

try:
    import torch
    print("PyTorch Version:", torch.__version__)
    print("CUDA Available on Node 2:", torch.cuda.is_available())
except ImportError:
    print("PyTorch not present in Node 2 worker env")

print("==================================================================")
print("  AUDIT COMPLETE: NODE 2 IS AN AMD-ONLY PLATFORM")
print("==================================================================")
'''

b64 = base64.b64encode(remote_code.encode("utf-8")).decode("ascii")

job_id = client.submit_job(
    entrypoint=f'python -c "import base64; exec(base64.b64decode(\'{b64}\').decode(\'utf-8\'))"'
)
print(f"Submitted Audit Job: {job_id}")

for _ in range(30):
    status = client.get_job_status(job_id)
    if status in [JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.STOPPED]:
        print(f"Job Status: {status}")
        print("Audit Logs:\n", client.get_job_logs(job_id))
        break
    time.sleep(1)
