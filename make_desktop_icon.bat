@echo off
cd /d "%~dp0"
echo Creating ANSHUX icons on your Desktop...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0make_desktop_icon.ps1"
echo.
pause
