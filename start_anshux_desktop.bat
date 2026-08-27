@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo AnshuX OS is not set up yet.
  echo Run setup_anshux_os.bat first.
  pause
  exit /b 1
)

start "AnshuX OS" cmd /k "cd /d "%~dp0" && .venv\Scripts\python.exe desktop_app.py"

echo AnshuX OS desktop is starting...
echo Backend: http://127.0.0.1:8765/
echo.
echo Close the AnshuX OS window to stop it.
endlocal
