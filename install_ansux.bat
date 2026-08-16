@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo ============================================
echo   ANSHUX - Personal AI System Installer
echo ============================================
echo.

if not exist ".env" (
  echo Creating .env from .env.example ...
  copy /Y ".env.example" ".env" >nul
)

echo [1/5] Creating virtual environment...
if not exist "venv\Scripts\python.exe" (
  python -m venv venv
  if errorlevel 1 (
    echo Failed to create venv. Install Python 3.12+ first.
    pause
    exit /b 1
  )
)

echo [2/5] Installing dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul
pip install -r requirements.txt
if errorlevel 1 (
  echo Dependency install failed.
  pause
  exit /b 1
)

echo [3/5] Downloading voice model...
if not exist "voices\en_US-lessac-medium.onnx" (
  mkdir voices 2>nul
  powershell -NoProfile -Command ^
    "Invoke-WebRequest -Uri 'https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx' -OutFile 'voices\en_US-lessac-medium.onnx'"
  powershell -NoProfile -Command ^
    "Invoke-WebRequest -Uri 'https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json' -OutFile 'voices\en_US-lessac-medium.onnx.json'"
)

echo [4/5] Creating desktop icon...
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\create_desktop_shortcut.ps1"
if errorlevel 1 (
  echo Desktop shortcut step failed.
)

echo [5/5] Running quick validation...
python -m unittest tests.test_ansux_core -q
if errorlevel 1 (
  echo Some tests failed, but install may still work on Windows.
)

echo.
echo ============================================
echo   AnshuX is installed!
echo ============================================
echo.
echo   Desktop: double-click the AnshuX icon
echo   Manual:  start_ansux.bat
echo   HUD:     http://127.0.0.1:8765
echo.
echo   Say "AnshuX" to wake the assistant.
echo.
pause
