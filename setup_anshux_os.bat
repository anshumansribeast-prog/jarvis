@echo off
setlocal
cd /d "%~dp0"

echo [AnshuX OS] Checking Python...
where py >nul 2>nul
if errorlevel 1 (
  echo Python launcher 'py' was not found. Install Python 3.11+ and try again.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo [AnshuX OS] Creating virtual environment...
  py -3 -m venv .venv
  if errorlevel 1 (
    echo Could not create the virtual environment.
    pause
    exit /b 1
  )
)

call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
python -m pip install -r requirements-os.txt
if errorlevel 1 (
  echo [AnshuX OS] Dependency installation failed.
  pause
  exit /b 1
)

python -m compileall -q anshux_os os_server.py app_controller.py system_controller.py
if errorlevel 1 (
  echo [AnshuX OS] Python compile check failed.
  pause
  exit /b 1
)

echo.
echo [AnshuX OS] Setup complete.
echo Run start_anshux_os.bat to launch the desktop.
pause
endlocal
