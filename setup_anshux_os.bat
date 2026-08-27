@echo off
setlocal
cd /d "%~dp0"

echo [AnshuX OS] Checking Python...
where py >nul 2>nul
if errorlevel 1 (
  echo Python launcher 'py' was not found. Install Python 3.11+ and try again.
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo [AnshuX OS] Creating virtual environment...
  py -3 -m venv .venv
  if errorlevel 1 exit /b 1
)

call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo [AnshuX OS] Dependency installation failed.
  exit /b 1
)

echo.
echo [AnshuX OS] Setup complete.
echo Run start_anshux_os.bat to launch the desktop.
endlocal
