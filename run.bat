@echo off
setlocal ENABLEDELAYEDEXPANSION
REM Batch bootstrap to run the app with minimal setup
REM - Creates .venv if missing
REM - Installs requirements
REM - Runs python app.py

set DIR=%~dp0
set VENV=%DIR%.venv
set PYEXE=%VENV%\Scripts\python.exe

if not exist "%PYEXE%" (
  echo Creating virtual environment (.venv)...
  where py >nul 2>nul && ( py -3 -m venv "%VENV%" ) || ( python -m venv "%VENV%" )
)

"%PYEXE%" -m pip install --upgrade pip setuptools wheel >nul 2>nul
if exist "%DIR%requirements.txt" (
  echo Installing dependencies from requirements.txt...
  "%PYEXE%" -m pip install -r "%DIR%requirements.txt"
)

echo Starting app at http://127.0.0.1:5000
"%PYEXE%" "%DIR%app.py"

endlocal
