import os
import sys

appdata = os.environ.get("APPDATA")
if appdata:
    startup_folder = os.path.join(appdata, "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
    vbs_path = os.path.join(startup_folder, "ClothOS_Node2_AutoStart.vbs")
    target_dir = r"C:\Users\natsa\Documents\loom-fabric"
    py_exe = r"C:\Users\natsa\AppData\Local\Programs\Python\Python312\python.exe"

    content = (
        'Set WshShell = CreateObject("WScript.Shell")\r\n'
        f'WshShell.CurrentDirectory = "{target_dir}"\r\n'
        f'WshShell.Run """{py_exe}""" & " -m loom.fabric.dashboard_server", 0, False\r\n'
    )

    with open(vbs_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"NODE2_STARTUP_ENABLED_SUCCESS: {vbs_path}")
else:
    print("APPDATA not set on Node 2.")
