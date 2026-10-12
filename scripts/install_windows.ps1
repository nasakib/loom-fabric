<#
.SYNOPSIS
    Loom Fabric — Windows One-Click Installer & Launcher
.DESCRIPTION
    Sets up the sovereign Python virtual environment, dependencies, CLI command aliases,
    and launches the hardware probe diagnostic on Windows 10/11.
#>

$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   LOOM FABRIC — WINDOWS SYSTEM INSTALLER                 " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Resolve Python
$PythonExe = "python.exe"
if (Get-Command "py.exe" -ErrorAction SilentlyContinue) {
    $PythonExe = "py.exe -3"
}

Write-Host "[*] Checking Python environment..." -ForegroundColor Gray
$PyCheck = Invoke-Expression "$PythonExe -c 'import sys; print(sys.version)'"
Write-Host "    $PyCheck" -ForegroundColor Green

# 2. Setup Venv
$VenvDir = "$env:USERPROFILE\.loom\env"
if (-not (Test-Path "$VenvDir\Scripts\python.exe")) {
    Write-Host "[*] Creating sovereign Python environment at $VenvDir..." -ForegroundColor Cyan
    Invoke-Expression "$PythonExe -m venv $VenvDir"
}

$VenvPython = "$VenvDir\Scripts\python.exe"

# 3. Install dependencies
Write-Host "[*] Installing core dependencies..." -ForegroundColor Cyan
& "$VenvPython" -m pip install --upgrade pip
& "$VenvPython" -m pip install fastapi uvicorn typer rich pydantic psutil httpx ray nvidia-ml-py

# 4. Install Loom in editable mode
$RepoDir = Split-Path -Parent $PSScriptRoot
Write-Host "[*] Registering Loom Fabric package from $RepoDir..." -ForegroundColor Cyan
& "$VenvPython" -m pip install -e "$RepoDir"

# 5. Create Windows CMD shim in user path
$BinDir = "$env:USERPROFILE\.loom\bin"
if (-not (Test-Path $BinDir)) {
    New-Item -ItemType Directory -Path $BinDir -Force | Out-Null
}

$ShimPath = "$BinDir\loom.cmd"
$ShimContent = "@echo off`r`n`"$VenvPython`" -m loom.cli.main %*"
[System.IO.File]::WriteAllText($ShimPath, $ShimContent)

# Add to user PATH if not present
$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($UserPath -notlike "*$BinDir*") {
    [Environment]::SetEnvironmentVariable("Path", "$UserPath;$BinDir", "User")
    Write-Host "[✓] Added $BinDir to User PATH." -ForegroundColor Green
}

Write-Host "`n[✓] Loom Fabric successfully installed on Windows!" -ForegroundColor Green
Write-Host "[*] Executing hardware diagnostic probe...`n" -ForegroundColor Cyan

& "$VenvPython" -m loom.cli.main probe

Write-Host "`nTo start the Sovereign Gateway on Windows:" -ForegroundColor Yellow
Write-Host "    loom serve --port 8000" -ForegroundColor White
Write-Host "Or browse to http://localhost:8000 for the Dashboard GUI." -ForegroundColor Cyan
