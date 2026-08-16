@echo off
title AnshuX - Personal AI System
cd /d "%~dp0"

echo ============================================
echo   Starting AnshuX...
echo   Dashboard: http://127.0.0.1:8765
echo ============================================
echo.
echo KEEP THIS WINDOW OPEN while using AnshuX.
echo.

if not exist "venv\Scripts\python.exe" (
  echo First run - creating environment...
  python -m venv venv
  if errorlevel 1 (
    echo ERROR: Python not found. Install Python 3.12+ from python.org
    pause
    exit /b 1
  )
)

call venv\Scripts\activate.bat
pip install -r requirements.txt -q

set ANSUX_OPEN_HUD_ON_START=true
set ANSUX_PUBLIC_URL=http://127.0.0.1:8765

python ansux.py
if errorlevel 1 (
  echo.
  echo ERROR: AnshuX crashed. See the message above.
  echo Try: start_ansux_hud.bat  ^(text-only, no voice^)
  pause
  exit /b 1
)

echo.
echo AnshuX stopped. Press any key to close.
pause >nul
