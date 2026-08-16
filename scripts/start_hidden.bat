@echo off
REM Starts AnshuX server in background (no window). Called by AnshuX.vbs.
setlocal EnableExtensions
cd /d "%~dp0.."

set "PYTHONPATH=%CD%"
set "ANSUX_TEXT_ONLY=true"
set "ANSUX_PUBLIC_URL=http://127.0.0.1:8765"
set "ANSUX_HUD_HOST=127.0.0.1"
set "ANSUX_OPEN_HUD_ON_START=false"

if exist "venv\Scripts\pythonw.exe" (
  start "" "venv\Scripts\pythonw.exe" -m ansux.server
) else (
  start "" pythonw.exe -m ansux.server
)

endlocal
