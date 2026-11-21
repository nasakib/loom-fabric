@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
set "PYTHONIOENCODING=utf-8"

title ClothOS React Native Universal App
echo ======================================================================
echo    CLOTHOS UNIVERSAL REACT NATIVE APP (PORT 8086)
echo    Dedicated Fiduciary Sovereign Companion for Najmos Sakib
echo    Living Mind Screensaver Geometries & Task Manager Telemetry
echo ======================================================================

set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

set "PYTHON_EXE=%PROJECT_ROOT%.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" (
    set "PYTHON_EXE=python"
)

echo Starting React Native Universal Server on http://127.0.0.1:8086...
"%PYTHON_EXE%" "apps\loom-react-native\serve_rn.py"

exit /b 0
