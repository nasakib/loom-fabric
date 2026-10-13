<#
.SYNOPSIS
    Loom Fabric -- Windows One-Click Installer & Launcher
.DESCRIPTION
    Sets up the sovereign Python virtual environment, dependencies, CLI command aliases,
    and launches the hardware probe diagnostic on Windows 10/11.
#>

$ErrorActionPreference = "Stop"
$env:PYTHONIOENCODING = "utf-8"

Write-Host "==========================================================" -ForegroundColor Magenta
Write-Host "   LOOM FABRIC -- WINDOWS MECHANISTIC SYSTEM INSTALLER    " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Magenta

$RepoDir = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path "$RepoDir\pyproject.toml")) {
    $RepoDir = $PSScriptRoot
}
$env:PYTHONPATH = "$RepoDir;$env:PYTHONPATH"

# 1. Check for uv or existing .venv first
$UvExe = $null
if (Get-Command "uv.exe" -ErrorAction SilentlyContinue) {
    $UvExe = (Get-Command "uv.exe").Source
} elseif (Test-Path "$env:USERPROFILE\.local\bin\uv.exe") {
    $UvExe = "$env:USERPROFILE\.local\bin\uv.exe"
}

$VenvPython = $null

if (Test-Path "$RepoDir\.venv\Scripts\python.exe") {
    $VenvPython = "$RepoDir\.venv\Scripts\python.exe"
    Write-Host "[*] Found existing workspace virtual environment at $RepoDir\.venv" -ForegroundColor Green
    if ($UvExe) {
        Write-Host "[*] Synchronizing workspace dependencies with uv..." -ForegroundColor Cyan
        Push-Location $RepoDir
        try {
            & "$UvExe" sync --extra dev
        } catch {
            Write-Host "[i] Offline or cached uv environment active; continuing with installed packages." -ForegroundColor Yellow
        } finally {
            Pop-Location
        }
    }
} elseif ($UvExe) {
    Write-Host "[*] Creating workspace virtual environment via uv ($UvExe)..." -ForegroundColor Cyan
    Push-Location $RepoDir
    try {
        & "$UvExe" venv "$RepoDir\.venv"
        & "$UvExe" sync --extra dev
        $VenvPython = "$RepoDir\.venv\Scripts\python.exe"
    } finally {
        Pop-Location
    }
} else {
    # Fallback to standard Python venv in ~/.loom/env
    $PythonCmd = $null
    if (Test-Path "C:\Users\natsa\Documents\stitch-core\.fabric-env\Scripts\python.exe") {
        $PythonCmd = "C:\Users\natsa\Documents\stitch-core\.fabric-env\Scripts\python.exe"
    } elseif (Get-Command "py.exe" -ErrorAction SilentlyContinue) {
        $PythonCmd = "py.exe"
    } elseif (Get-Command "python.exe" -ErrorAction SilentlyContinue) {
        $PythonCmd = "python.exe"
    } else {
        throw "No Python 3.10+ or uv installation found on this machine."
    }

    $VenvDir = "$env:USERPROFILE\.loom\env"
    if (-not (Test-Path "$VenvDir\Scripts\python.exe")) {
        Write-Host "[*] Creating sovereign Python environment at $VenvDir..." -ForegroundColor Cyan
        & $PythonCmd -m venv $VenvDir
    }
    $VenvPython = "$VenvDir\Scripts\python.exe"
    Write-Host "[*] Installing core dependencies..." -ForegroundColor Cyan
    & "$VenvPython" -m pip install --upgrade pip
    & "$VenvPython" -m pip install -e "$RepoDir"
}

# 2. Create Windows CMD shims in ~/.loom/bin and ~/.local/bin
$BinDirs = @("$env:USERPROFILE\.loom\bin", "$env:USERPROFILE\.local\bin")
foreach ($BinDir in $BinDirs) {
    if (-not (Test-Path $BinDir)) {
        New-Item -ItemType Directory -Path $BinDir -Force | Out-Null
    }

    $ShimPath = "$BinDir\loom.cmd"
    $ShimContent = "@echo off`r`nset `"PYTHONPATH=$RepoDir;%PYTHONPATH%`"`r`nset `"PYTHONIOENCODING=utf-8`"`r`n`"$VenvPython`" -m loom.cli.main %*"
    [System.IO.File]::WriteAllText($ShimPath, $ShimContent)

    $GuiShimPath = "$BinDir\loom-gui.cmd"
    $GuiShimContent = "@echo off`r`ncall `"$RepoDir\Start-Loom-GUI.bat`""
    [System.IO.File]::WriteAllText($GuiShimPath, $GuiShimContent)
}

# 3. Add ~/.loom/bin to User PATH if not present
$PrimaryBin = "$env:USERPROFILE\.loom\bin"
$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($UserPath -notlike "*$PrimaryBin*") {
    [Environment]::SetEnvironmentVariable("Path", "$UserPath;$PrimaryBin", "User")
    Write-Host "[OK] Added $PrimaryBin to User PATH." -ForegroundColor Green
}

Write-Host "`n[OK] Loom Fabric successfully installed on Windows!" -ForegroundColor Green
Write-Host "[*] Executing hardware diagnostic probe...`n" -ForegroundColor Cyan

& "$VenvPython" -m loom.cli.main probe

Write-Host "`nLaunch Commands:" -ForegroundColor Yellow
Write-Host "    loom gui                  (Launch Native Desktop Control Center)" -ForegroundColor White
Write-Host "    loom serve --port 8002    (Start Sovereign Gateway on :8002)" -ForegroundColor White
Write-Host "    loom probe                (Inspect Physical Silicon and VRAM)" -ForegroundColor White
