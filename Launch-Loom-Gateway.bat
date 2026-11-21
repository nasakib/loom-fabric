@echo off
title Loom Fabric Gateway - Port 8002
cd /d "%~dp0"
echo =========================================================================
echo    LOOM FABRIC GATEWAY - SOVEREIGN DISTRIBUTED COMPUTE ENGINE
echo    Host: 0.0.0.0 : Port: 8002
echo    Dual-GPU VRAM Mesh: RTX 3060 (CUDA) + RX 580 (OpenCL) + Ray Cluster
echo =========================================================================
echo.
"%~dp0.venv\Scripts\python.exe" -m uvicorn loom.gateway.app:app --host 0.0.0.0 --port 8002
pause
