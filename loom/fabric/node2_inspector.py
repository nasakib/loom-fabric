# Copyright (c) 2026 Najmos Sakib. All rights reserved.
"""
Comprehensive Node 2 Diagnostics & Driver Verification (`loom/fabric/node2_inspector.py`).
"""

import json
import os
import platform
import subprocess
import sys

def run_diagnostics():
    print("==================================================================")
    print("NODE 2 SYSTEM, HARDWARE & DRIVER DIAGNOSTICS")
    print(f"Platform: {platform.platform()} | Python: {platform.python_version()}")
    print("==================================================================")

    # 1. Inspect Video Controllers and Drivers
    print("\n--- GPU & DRIVER STATUS ---")
    try:
        wmi_cmd = 'powershell -NoProfile -Command "Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion, Status, PNPDeviceID | Format-List"'
        res = subprocess.check_output(wmi_cmd, shell=True, text=True, errors="replace")
        print(res.strip())
    except Exception as e:
        print(f"Failed to query video controllers: {e}")

    # 2. Inspect CPU and Memory via CIM
    print("\n--- CPU & MEMORY ---")
    try:
        cpu_cmd = 'powershell -NoProfile -Command "Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors | Format-List"'
        cpu_res = subprocess.check_output(cpu_cmd, shell=True, text=True, errors="replace")
        print(cpu_res.strip())
        mem_cmd = 'powershell -NoProfile -Command "Get-CimInstance Win32_OperatingSystem | Select-Object TotalVisibleMemorySize, FreePhysicalMemory | Format-List"'
        mem_res = subprocess.check_output(mem_cmd, shell=True, text=True, errors="replace")
        print(mem_res.strip())
    except Exception as e:
        print(f"CIM CPU/Mem error: {e}")

    # 3. Check Startup Folders and Run Keys (common culprit for flashing cmd windows)
    print("\n--- STARTUP ENTRIES & RUN KEYS ---")
    try:
        startup_cmd = (
            'powershell -NoProfile -Command "'
            'Get-ItemProperty \'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\' -ErrorAction SilentlyContinue | Format-List; '
            'Get-ItemProperty \'HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\' -ErrorAction SilentlyContinue | Format-List; '
            'Get-ChildItem \"$env:APPDATA\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\" -ErrorAction SilentlyContinue | Select-Object Name, FullName | Format-List; '
            'Get-ChildItem \"$env:ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\" -ErrorAction SilentlyContinue | Select-Object Name, FullName | Format-List'
            '"'
        )
        startup_res = subprocess.check_output(startup_cmd, shell=True, text=True, errors="replace")
        print(startup_res.strip())
    except Exception as e:
        print(f"Startup check error: {e}")

    # 4. Check specific tasks (StartCN, StartDVR, OpenClaw)
    print("\n--- TASK ACTIONS FOR SUSPICIOUS TASKS ---")
    for tname in ["StartCN", "StartDVR", "OpenClaw Gateway"]:
        try:
            task_cmd = f'powershell -NoProfile -Command "(Get-ScheduledTask -TaskName \'{tname}\' -ErrorAction SilentlyContinue).Actions | Format-List"'
            out = subprocess.check_output(task_cmd, shell=True, text=True, errors="replace").strip()
            print(f"Task '{tname}':\n{out if out else 'Not found'}")
        except Exception:
            pass

    # 5. Check all active processes running cmd, powershell, python, or conhost
    print("\n--- ACTIVE CMD / CONHOST / PYTHON PROCESSES ---")
    try:
        proc_cmd = (
            'powershell -NoProfile -Command "'
            'Get-CimInstance Win32_Process | '
            'Where-Object { $_.Name -match \'cmd|powershell|pwsh|conhost|python\' } | '
            'Select-Object ProcessId, ParentProcessId, Name, CommandLine | '
            'Format-List'
            '"'
        )
        proc_res = subprocess.check_output(proc_cmd, shell=True, text=True, errors="replace")
        print(proc_res.strip())
    except Exception as e:
        print(f"Process check error: {e}")

    print("\n==================================================================")
    print("NODE 2 DIAGNOSTICS COMPLETE")
    print("==================================================================")

if __name__ == "__main__":
    run_diagnostics()
