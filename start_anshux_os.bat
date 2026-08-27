@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo AnshuX OS is not set up yet.
  echo Run setup_anshux_os.bat first.
  pause
  exit /b 1
)

start "AnshuX OS Server" cmd /k "cd /d "%~dp0" && .venv\Scripts\python.exe os_server.py"
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:8765/"

echo AnshuX OS is running at http://127.0.0.1:8765/
echo Keep the server window open while using the desktop.
endlocal
