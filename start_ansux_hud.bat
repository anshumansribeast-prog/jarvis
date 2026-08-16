@echo off
title AnshuX HUD (text-only)
cd /d "%~dp0"

echo ============================================
echo   AnshuX Dashboard - Text Mode
echo   http://127.0.0.1:8765
echo ============================================
echo.
echo KEEP THIS WINDOW OPEN. Do not close it.
echo.

if not exist "venv\Scripts\python.exe" (
  echo Run install_ansux.bat first.
  pause
  exit /b 1
)

call venv\Scripts\activate.bat

set ANSUX_TEXT_ONLY=true
set ANSUX_OPEN_HUD_ON_START=true
set ANSUX_PUBLIC_URL=http://127.0.0.1:8765

start "" cmd /c "timeout /t 3 /nobreak >nul && start http://127.0.0.1:8765"
python -m ansux.server

pause
