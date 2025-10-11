# PowerShell script to create isolated venv for presentation and run generator
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$venv = Join-Path $dir '.venv'
$pyExe = Join-Path $venv 'Scripts/python.exe'

function Get-Python {
  $cmd = (Get-Command python -ErrorAction SilentlyContinue | Select-Object -First 1)
  if ($cmd) { return $cmd.Source }
  $cmd = (Get-Command py -ErrorAction SilentlyContinue | Select-Object -First 1)
  if ($cmd) { return $cmd.Source }
  throw 'Python not found on PATH.'
}

if (-not (Test-Path $pyExe)) {
  Write-Host 'Creating virtual environment (.venv) for presentation...'
  $py = Get-Python
  & $py -m venv $venv
}

& $pyExe -m pip install --upgrade pip setuptools wheel | Out-Null
& $pyExe -m pip install -r (Join-Path $dir 'requirements.txt')

& $pyExe (Join-Path $dir 'generate_ppt.py')
