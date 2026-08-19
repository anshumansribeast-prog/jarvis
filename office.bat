@echo off
cd /d "%~dp0"
echo Starting ANSHUX office SITE at http://127.0.0.1:8765/
echo The OpenCode chat panel is ON THAT PAGE. Leave this window open.
echo.
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:8765/"
py -3 "%~dp0team.py" office 2>nul
if errorlevel 1 python "%~dp0team.py" office
pause
