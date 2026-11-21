@echo off
setlocal enabledelayedexpansion

title ClothOS React Native Universal Desktop App
echo ======================================================================
echo    CLOTHOS // REACT NATIVE UNIVERSAL DESKTOP APP
echo    Unified Desktop Client (Task Manager, Brain, Rosetta, Symbiosis)
echo    Dedicated Fiduciary Sovereign Companion for Najmos Sakib
echo ======================================================================

set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

set "PYTHON_EXE=%PROJECT_ROOT%.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" (
    set "PYTHON_EXE=python"
)

echo Starting ClothOS Desktop in React Native Mode...
"%PYTHON_EXE%" "apps\loom-desktop\launch_desktop.py" --mode=react-native

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [Fallback] Launching directly via default browser...
    start http://127.0.0.1:8080/app
)

exit /b 0
