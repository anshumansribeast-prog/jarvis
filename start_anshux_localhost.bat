@echo off
setlocal EnableExtensions EnableDelayedExpansion
set "ROOT=%~dp0"
cd /d "%ROOT%"
set "PYTHON=%ROOT%.venv\Scripts\python.exe"
set "URL=http://127.0.0.1:8765/"
set "HEALTH=http://127.0.0.1:8765/api/os/status"

if not exist "%PYTHON%" (
  echo.
  echo [AnshuX OS] Virtual environment not found.
  echo Run setup_anshux_os.bat first.
  pause
  exit /b 1
)

echo.
echo ========================================
echo        ANSHUX OS - LOCALHOST
 echo ========================================
echo.
echo Starting server...
start "AnshuX OS Server" "%ComSpec%" /k "cd /d ""%ROOT%"" && ""%PYTHON%"" ""%ROOT%os_server.py"""

echo Waiting for the AnshuX server to become ready...
set "READY=0"
for /L %%N in (1,1,20) do (
  timeout /t 1 /nobreak >nul
  "%SystemRoot%\System32\curl.exe" -fsS "%HEALTH%" >nul 2>&1
  if not errorlevel 1 (
    set "READY=1"
    goto :ready
  )
  echo   Check %%N/20...
)

:failed
 echo.
echo [AnshuX OS] The server did not become ready.
echo.
echo The server window is still open so you can see the Python error.
echo Read the last lines in that window and send them to me.
echo.
echo Browser was NOT opened because localhost is not running.
pause
exit /b 1

:ready
echo.
echo [OK] AnshuX OS is running.
echo [OK] Localhost: %URL%
echo Opening your browser...
start "" "%URL%"
echo.
echo Keep the server window open while using AnshuX OS.
echo Close that server window to stop it.
endlocal
