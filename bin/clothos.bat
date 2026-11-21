@echo off
setlocal
set "LOOM_DIR=C:\Users\natsa\Documents\loom-fabric"
set "PYTHONPATH=%LOOM_DIR%;%PYTHONPATH%"
set "PYTHONIOENCODING=utf-8"

if exist "%LOOM_DIR%\.venv\Scripts\python.exe" (
    "%LOOM_DIR%\.venv\Scripts\python.exe" -m loom.clothos.agent_cli --workspace "%CD%" %*
) else (
    python -m loom.clothos.agent_cli --workspace "%CD%" %*
)
