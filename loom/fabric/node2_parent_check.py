# Check parent processes on Node 2
import subprocess

for pid in [38636, 26920]:
    try:
        ps_cmd = [
            "powershell", "-NoProfile", "-Command",
            f"(Get-CimInstance Win32_Process -Filter 'ProcessId = {pid}') | Select-Object ProcessId, ParentProcessId, Name, CommandLine, Path | Format-List"
        ]
        out = subprocess.check_output(ps_cmd, text=True, errors="replace")
        print(f"=== PID {pid} ===")
        print(out.strip())
    except Exception as e:
        print(f"Error checking PID {pid}: {e}")
