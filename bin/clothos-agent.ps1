$LoomDir = "C:\Users\natsa\Documents\loom-fabric"
$env:PYTHONPATH = "$LoomDir;$env:PYTHONPATH"
$env:PYTHONIOENCODING = "utf-8"
$VenvPy = "$LoomDir\.venv\Scripts\python.exe"
$CurrentDir = Get-Location

if (Test-Path $VenvPy) {
    & $VenvPy -m loom.clothos.agent_cli --workspace "$CurrentDir" @args
} else {
    & python -m loom.clothos.agent_cli --workspace "$CurrentDir" @args
}
