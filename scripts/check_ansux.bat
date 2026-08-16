@echo off
title AnshuX - Check Setup
cd /d "%~dp0"

echo === AnshuX Diagnostics ===
echo.

where python >nul 2>&1
if errorlevel 1 (
  echo [FAIL] Python not found. Install from https://python.org
) else (
  python --version
  echo [OK] Python found
)

if exist "venv\Scripts\python.exe" (
  echo [OK] Virtual environment exists
) else (
  echo [FAIL] No venv - run INSTALL_ANSHUX.bat
)

if exist "AnshuX.vbs" (
  echo [OK] Desktop launcher found
) else (
  echo [FAIL] AnshuX.vbs missing
)

if exist "voices\en_US-lessac-medium.onnx" (
  echo [OK] Voice model found
) else (
  echo [WARN] Voice model missing - text mode still works
)

echo.
echo Checking if server is running on port 8765...
powershell -NoProfile -Command "try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:8765/api/status' -UseBasicParsing -TimeoutSec 2; Write-Host '[OK] Server is RUNNING' } catch { Write-Host '[FAIL] Server is NOT running' ; Write-Host '       Fix: double-click AnshuX on Desktop or INSTALL_ANSHUX.bat' }"

echo.
pause
