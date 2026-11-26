@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
set "PYTHONIOENCODING=utf-8"

title ClothOS React Native Universal App
echo ======================================================================
echo    CLOTHOS UNIVERSAL APP SUITE (UNIFIED PORT 8087)
echo    Dedicated Fiduciary Sovereign Companion for Najmos Sakib
echo    Living Mind Screensaver Geometries & Task Manager Telemetry
echo ======================================================================

set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

set "PYTHON_EXE=%PROJECT_ROOT%.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" (
    set "PYTHON_EXE=python"
)

echo Opening Unified ClothOS Universal App on http://127.0.0.1:8087/guis/react-native-app/ ...
start http://127.0.0.1:8087/guis/react-native-app/
"%PYTHON_EXE%" -m uvicorn loom.fabric.dashboard_server:app --host 0.0.0.0 --port 8087

exit /b 0
