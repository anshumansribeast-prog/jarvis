@echo off
REM Opens AnshuX Personal AI in your browser — no terminal window.
cd /d "%~dp0"
if not exist "venv\Scripts\pythonw.exe" (
  echo Run install_ansux.bat first.
  pause
  exit /b 1
)
wscript.exe "%~dp0AnshuX.vbs"
