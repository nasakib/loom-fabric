# Check listening ports and Ray services on Node 2
import subprocess

try:
    net_cmd = [
        "powershell", "-NoProfile", "-Command",
        "Get-NetTCPConnection -State Listen | Where-Object { $_.LocalPort -in @(5555, 6379, 8265, 8085, 8088, 10001, 52365) } | Select-Object LocalAddress, LocalPort, OwningProcess | Format-Table -AutoSize"
    ]
    out = subprocess.check_output(net_cmd, text=True, errors="replace")
    print("=== LISTENING PORTS ON NODE 2 ===")
    print(out.strip())
except Exception as e:
    print(f"Error checking ports: {e}")

try:
    ps_cmd = [
        "powershell", "-NoProfile", "-Command",
        "Get-CimInstance Win32_Process | Where-Object { $_.Name -like '*python*' } | Select-Object ProcessId, CommandLine | Format-List"
    ]
    out_p = subprocess.check_output(ps_cmd, text=True, errors="replace")
    print("=== PYTHON PROCESSES ON NODE 2 ===")
    print(out_p.strip())
except Exception as e:
    print(f"Error checking python processes: {e}")
