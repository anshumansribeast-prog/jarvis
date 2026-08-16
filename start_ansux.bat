@echo off
title AnshuX - Personal AI System
cd /d "%~dp0"
if not exist "venv\Scripts\python.exe" (
  echo AnshuX: setting up environment...
  python -m venv venv
  call venv\Scripts\activate.bat
  pip install -r requirements.txt
) else (
  call venv\Scripts\activate.bat
)
python ansux.py
echo.
echo AnshuX stopped. Press any key to close this window.
pause >nul
