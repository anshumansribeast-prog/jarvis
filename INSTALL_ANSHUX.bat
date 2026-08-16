@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo ============================================
echo   ANSHUX - One-Click Install
echo ============================================
echo.
echo This will install AnshuX and put an icon on your Desktop.
echo The app opens as a desktop window (not a browser tab).
echo.

if not exist ".env" (
  echo Creating .env ...
  copy /Y ".env.example" ".env" >nul
)

echo [1/6] Checking Python...
where python >nul 2>&1
if errorlevel 1 (
  echo.
  echo ERROR: Python is not installed.
  echo Download Python 3.12+ from https://www.python.org/downloads/
  echo Check "Add Python to PATH" during install, then run this again.
  echo.
  pause
  exit /b 1
)
python --version

echo [2/6] Creating virtual environment...
if not exist "venv\Scripts\python.exe" (
  python -m venv venv
  if errorlevel 1 (
    echo Failed to create venv.
    pause
    exit /b 1
  )
)

echo [3/6] Installing dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul
pip install -r requirements.txt
if errorlevel 1 (
  echo Dependency install failed.
  pause
  exit /b 1
)

echo [4/6] Voice model (optional, skip if slow)...
if not exist "voices\en_US-lessac-medium.onnx" (
  echo Downloading voice files — text mode works without them.
  mkdir voices 2>nul
  powershell -NoProfile -Command ^
    "try { Invoke-WebRequest -Uri 'https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx' -OutFile 'voices\en_US-lessac-medium.onnx' } catch { Write-Host 'Voice download skipped' }"
  powershell -NoProfile -Command ^
    "try { Invoke-WebRequest -Uri 'https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json' -OutFile 'voices\en_US-lessac-medium.onnx.json' } catch { }"
) else (
  echo Voice model already present.
)

echo [5/6] Creating Desktop icon...
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\create_desktop_shortcut.ps1"
if errorlevel 1 (
  echo Desktop shortcut failed — you can still use AnshuX.vbs in this folder.
)

echo [6/6] Quick test...
set "PYTHONPATH=%CD%"
python -m unittest tests.test_ansux_core -q
if errorlevel 1 (
  echo Some tests failed — desktop app may still work.
)

echo.
echo ============================================
echo   Install complete!
echo ============================================
echo.
echo   Look for "AnshuX" on your Desktop and double-click it.
echo   It opens as a desktop app — no terminal needed.
echo.
echo   Opening AnshuX now...
echo.

wscript.exe "%~dp0AnshuX.vbs"

endlocal
