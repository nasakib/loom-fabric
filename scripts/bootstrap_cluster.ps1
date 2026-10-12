<#
.SYNOPSIS
    Loom Fabric Cluster Bootstrap Script for Windows / LAN.
.DESCRIPTION
    Initializes Ray Cluster Head Node or Worker Node with custom accelerator resource tags:
    - Head Node (Ryzen 7): ray start --head --port=6379 --resources='{"CPU_HEAD": 16}'
    - Worker Node (Desktop): ray start --address='192.168.99.2:6379' --resources='{"GPU_NVIDIA": 12, "GPU_AMD": 8}'
#>

param (
    [Parameter(Mandatory=$false)]
    [ValidateSet("head", "worker")]
    [string]$Role = "head",

    [Parameter(Mandatory=$false)]
    [string]$HeadAddress = "192.168.99.2:6379",

    [Parameter(Mandatory=$false)]
    [string]$PythonEnv = "C:\Users\natsa\Documents\stitch-core\.fabric-env\Scripts\python.exe"
)

Write-Host "==========================================================" -ForegroundColor Magenta
Write-Host " LOOM FABRIC CLUSTER BOOTSTRAP (Windows Bare-Metal)" -ForegroundColor Magenta
Write-Host " Role: $Role | Target: $HeadAddress" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Magenta

if ($Role -eq "head") {
    Write-Host "[*] Starting Ray Cluster Head Node on :6379..." -ForegroundColor Yellow
    & $PythonEnv -m ray start --head --port=6379 --dashboard-host=0.0.0.0 --dashboard-port=8265 --resources='{"CPU_HEAD": 16}' --block
} else {
    Write-Host "[*] Connecting Worker Node to Head at $HeadAddress..." -ForegroundColor Yellow
    & $PythonEnv -m ray start --address=$HeadAddress --resources='{"GPU_NVIDIA": 12, "GPU_AMD": 8}' --block
}
