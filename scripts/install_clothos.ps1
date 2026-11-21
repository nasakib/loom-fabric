<#
.SYNOPSIS
    ClothOS & Loom Fabric -- Windows Sovereign One-Click Installer & Reinstaller
.DESCRIPTION
    Sets up the sovereign Python virtual environment, dependencies, ClothFS Virtual Filesystem,
    Sovereign RISC-V transition target, zero-window Windows Startup persistence, and desktop shortcuts.
.PARAMETER Reinstall
    Forces a clean wipe and reinstallation of all components.
.PARAMETER Clean
    Cleans stale process locks, ports, and temporary files before install.
#>

[CmdletBinding()]
param (
    [switch]$Reinstall,
    [switch]$Clean,
    [int]$Port = 0
)

$ErrorActionPreference = "Stop"
$env:PYTHONIOENCODING = "utf-8"

Write-Host "==========================================================" -ForegroundColor Magenta
Write-Host "   CLOTHOS & LOOM FABRIC -- SOVEREIGN SYSTEM INSTALLER    " -ForegroundColor Green
Write-Host "   Architect: Najmos Sakib | Fiduciary 0.00 Bound        " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Magenta

$RepoDir = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path "$RepoDir\pyproject.toml")) {
    $RepoDir = $PSScriptRoot
}
$env:PYTHONPATH = "$RepoDir;$env:PYTHONPATH"

# 1. Locate uv or Python runtime
$UvExe = $null
if (Get-Command "uv.exe" -ErrorAction SilentlyContinue) {
    $UvExe = (Get-Command "uv.exe").Source
} elseif (Test-Path "$env:USERPROFILE\.local\bin\uv.exe") {
    $UvExe = "$env:USERPROFILE\.local\bin\uv.exe"
}

$VenvDir = "$RepoDir\.venv"
$VenvPython = "$VenvDir\Scripts\python.exe"

if ($Reinstall -or $Clean) {
    Write-Host "[*] Reinstall requested: Cleaning volatile locks and caches..." -ForegroundColor Yellow
    Remove-Item -Path "$RepoDir\.loom_dashboard_pid" -ErrorAction SilentlyContinue
    Remove-Item -Path "$RepoDir\.loom_dashboard_port" -ErrorAction SilentlyContinue
}

# 2. Virtual Environment Setup / Verification
if (Test-Path $VenvPython) {
    Write-Host "[*] Found existing virtual environment at $VenvDir" -ForegroundColor Green
    if ($UvExe) {
        Write-Host "[*] Synchronizing workspace packages with uv..." -ForegroundColor Cyan
        Push-Location $RepoDir
        try {
            & "$UvExe" sync --extra dev
        } catch {
            Write-Host "[i] Offline / cached uv environment active; continuing." -ForegroundColor Yellow
        } finally {
            Pop-Location
        }
    }
} elseif ($UvExe) {
    Write-Host "[*] Creating fresh virtual environment with uv ($UvExe)..." -ForegroundColor Cyan
    Push-Location $RepoDir
    try {
        & "$UvExe" venv "$VenvDir"
        & "$UvExe" sync --extra dev
    } finally {
        Pop-Location
    }
} else {
    # System Python fallback
    $SysPython = $null
    if (Get-Command "py.exe" -ErrorAction SilentlyContinue) {
        $SysPython = "py.exe"
    } elseif (Get-Command "python.exe" -ErrorAction SilentlyContinue) {
        $SysPython = "python.exe"
    } else {
        throw "No Python 3.10+ or uv found on this machine. Please install Python 3.10+."
    }

    Write-Host "[*] Creating virtual environment at $VenvDir using $SysPython..." -ForegroundColor Cyan
    & $SysPython -m venv "$VenvDir"
    & "$VenvPython" -m pip install --upgrade pip
    & "$VenvPython" -m pip install -e "$RepoDir"
}

# 3. Run the Unified ClothOS Sovereign Python Installer
Write-Host "[*] Executing ClothOS Sovereign Installation Engine..." -ForegroundColor Cyan
$InstallerArgs = @("-m", "loom.fabric.installer")
if ($Reinstall) { $InstallerArgs += "--reinstall" }
if ($Clean) { $InstallerArgs += "--clean" }

& "$VenvPython" @InstallerArgs

# 4. Create Desktop Shortcuts for 1-Click Launching
try {
    $WshShell = New-Object -ComObject WScript.Shell
    $DesktopPath = [Environment]::GetFolderPath("Desktop")

    # Shortcut 1: ClothOS Command Center GUI
    $GuiShortcut = $WshShell.CreateShortcut("$DesktopPath\ClothOS Command Center.lnk")
    $GuiShortcut.TargetPath = "$RepoDir\Launch-Loom-GUI.bat"
    $GuiShortcut.WorkingDirectory = "$RepoDir"
    $GuiShortcut.Description = "ClothOS Sovereign Command Center (Task Manager GUI)"
    $GuiShortcut.Save()

    # Shortcut 2: ClothOS Universal React Native App
    $RnShortcut = $WshShell.CreateShortcut("$DesktopPath\ClothOS React Native.lnk")
    $RnShortcut.TargetPath = "$RepoDir\Launch-React-Native.bat"
    $RnShortcut.WorkingDirectory = "$RepoDir"
    $RnShortcut.Description = "ClothOS Universal React Native App (Port 8086)"
    $RnShortcut.Save()

    # Shortcut 3: ClothOS Interactive Shell (clothsh)
    $ShShortcut = $WshShell.CreateShortcut("$DesktopPath\ClothOS Shell (clothsh).lnk")
    $ShShortcut.TargetPath = "$env:USERPROFILE\.loom\bin\clothsh.cmd"
    $ShShortcut.WorkingDirectory = "$RepoDir"
    $ShShortcut.Description = "ClothOS Sovereign Shell Interpreter"
    $ShShortcut.Save()

    Write-Host "[OK] Created Desktop Shortcuts on $DesktopPath." -ForegroundColor Green
} catch {
    Write-Host "[i] Desktop shortcuts note: $_" -ForegroundColor Yellow
}

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host "   CLOTHOS & LOOM FABRIC INSTALLATION / REINSTALL COMPLETE" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  - Launch Command Center:     Launch-Loom-GUI.bat (or desktop shortcut)" -ForegroundColor White
Write-Host "  - Launch React Native App:   Launch-React-Native.bat (Port 8086)" -ForegroundColor White
Write-Host "  - Launch Interactive Shell:  clothsh (or 'python -m loom.clothos.shell')" -ForegroundColor White
Write-Host "  - RISC-V Migration Status:   clothsh riscv" -ForegroundColor White
Write-Host "==========================================================`n" -ForegroundColor Green
