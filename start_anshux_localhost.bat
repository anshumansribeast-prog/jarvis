@echo off
setlocal
set "ROOT=%~dp0"
cd /d "%ROOT%"

if not exist "%ROOT%.venv\Scripts\python.exe" (
  echo AnshuX OS is not set up yet.
  echo Run setup_anshux_os.bat first.
  pause
  exit /b 1
)

echo Starting AnshuX OS on localhost...
start "AnshuX OS Server" "%ComSpec%" /k "cd /d ""%ROOT%"" && ""%ROOT%.venv\Scripts\python.exe"" ""%ROOT%os_server.py"""

timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:8765/"

echo.
echo AnshuX OS is running in your browser:
echo http://127.0.0.1:8765/
echo.
echo No native app is required. Keep the server window open while using AnshuX OS.
echo Close the server window to stop it.
endlocal
