@echo off
setlocal
set "LOOM_DIR=C:\Users\natsa\Documents\loom-fabric"
set "PYTHONPATH=%LOOM_DIR%;%PYTHONPATH%"
set "PYTHONIOENCODING=utf-8"

python -m loom.clothos.agent_cli --workspace "%CD%" --full-access %*
