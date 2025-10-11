@echo off
setlocal ENABLEDELAYEDEXPANSION
REM Create isolated venv for presentation and run generator

set DIR=%~dp0
set VENV=%DIR%\.venv
set PYEXE=%VENV%\Scripts\python.exe

if not exist "%PYEXE%" (
  echo Creating virtual environment (.venv) for presentation...
  where python >nul 2>nul
  if %ERRORLEVEL%==0 (
    python -m venv "%VENV%"
  ) else (
    where py >nul 2>nul
    if %ERRORLEVEL%==0 (
      py -3 -m venv "%VENV%"
    ) else (
      echo Python not found on PATH.
      exit /b 1
    )
  )
)

"%PYEXE%" -m pip install --upgrade pip setuptools wheel >nul 2>nul
"%PYEXE%" -m pip install -r "%DIR%requirements.txt"

"%PYEXE%" "%DIR%generate_ppt.py"

endlocal
