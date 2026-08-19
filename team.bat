@echo off
cd /d "%~dp0"
python team.py %*
if errorlevel 1 pause
