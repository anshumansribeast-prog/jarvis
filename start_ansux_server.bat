@echo off
title AnshuX Server
cd /d "%~dp0"
call venv\Scripts\activate.bat 2>nul
set ANSUX_HUD_HOST=0.0.0.0
set ANSUX_TEXT_ONLY=true
set ANSUX_OPEN_HUD_ON_START=false
echo AnshuX server starting on port %ANSUX_HUD_PORT%
if "%ANSUX_HUD_PORT%"=="" set ANSUX_HUD_PORT=8765
python -m ansux.server
pause
