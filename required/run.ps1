# PowerShell bootstrap to run the app with minimal setup
# - Creates a virtual environment in .venv if missing
# - Installs/updates dependencies from requirements.txt
# - Starts the Flask app (python app.py)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$venv = Join-Path $root '.venv'
$pyExe = Join-Path $venv 'Scripts/python.exe'

function Get-Python {
  $cmd = (Get-Command python -ErrorAction SilentlyContinue | Select-Object -First 1)
  if ($cmd) { return $cmd.Source }
  $cmd = (Get-Command py -ErrorAction SilentlyContinue | Select-Object -First 1)
  if ($cmd) { return $cmd.Source }
  throw 'Python not found on PATH. Please install Python 3 and try again.'
}

if (-not (Test-Path $pyExe)) {
  Write-Host 'Creating virtual environment (.venv)...'
  $py = Get-Python
  & $py -m venv $venv
}

# Ensure pip is present and up to date
& $pyExe -m pip install --upgrade pip setuptools wheel | Out-Null

# Install requirements
$req = Join-Path $root 'requirements.txt'
if (Test-Path $req) {
  Write-Host 'Installing dependencies from requirements.txt...'
  & $pyExe -m pip install -r $req
}

# Run the app
Write-Host 'Starting app at http://127.0.0.1:5000'
& $pyExe "$root/app.py"
