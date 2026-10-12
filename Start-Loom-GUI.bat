@echo off
setlocal
title Loom Fabric - Native Desktop Control Center

set "SCRIPT_DIR=%~dp0"
set "PYTHON_EXE=C:\Users\natsa\Documents\stitch-core\.fabric-env\Scripts\python.exe"

if not exist "%PYTHON_EXE%" (
    set "PYTHON_EXE=%USERPROFILE%\.loom\env\Scripts\python.exe"
)

if not exist "%PYTHON_EXE%" (
    set "PYTHON_EXE=python"
)

echo Starting Loom Fabric Native Desktop GUI...
start "" "%PYTHON_EXE%" -m loom.cli.main gui --gateway http://127.0.0.1:8002
exit /b 0
