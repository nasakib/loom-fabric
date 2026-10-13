@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%~dp0;%PYTHONPATH%"
set "PYTHONIOENCODING=utf-8"

if exist "%~dp0.venv\Scripts\pythonw.exe" (
    start "" "%~dp0.venv\Scripts\pythonw.exe" -m loom.gui
    exit /b 0
)
if exist "%USERPROFILE%\.loom\env\Scripts\pythonw.exe" (
    start "" "%USERPROFILE%\.loom\env\Scripts\pythonw.exe" -m loom.gui
    exit /b 0
)
if exist "%LOCALAPPDATA%\Programs\Python\Python312\pythonw.exe" (
    start "" "%LOCALAPPDATA%\Programs\Python\Python312\pythonw.exe" -m loom.gui
    exit /b 0
)
if exist "C:\Users\natsa\Documents\stitch-core\.fabric-env\Scripts\pythonw.exe" (
    start "" "C:\Users\natsa\Documents\stitch-core\.fabric-env\Scripts\pythonw.exe" -m loom.gui
    exit /b 0
)
start "" pythonw -m loom.gui
exit /b 0
