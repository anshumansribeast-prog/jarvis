@echo off
title Open AnshuX Dashboard
cd /d "%~dp0"

set URL=http://127.0.0.1:8765
if exist .env (
  for /f "tokens=1,* delims==" %%a in ('findstr /B "ANSUX_PUBLIC_URL" .env') do set URL=%%b
)

echo Waiting for AnshuX server...
set /a tries=0
:waitloop
set /a tries+=1
powershell -NoProfile -Command "try { (Invoke-WebRequest -Uri 'http://127.0.0.1:8765/api/status' -UseBasicParsing -TimeoutSec 2).StatusCode } catch { exit 1 }" >nul 2>&1
if %errorlevel%==0 goto open
if %tries% geq 30 (
  echo AnshuX server is not running. Start it with start_ansux.bat first.
  pause
  exit /b 1
)
timeout /t 1 /nobreak >nul
goto waitloop

:open
echo Opening %URL%
start "" "%URL%"
