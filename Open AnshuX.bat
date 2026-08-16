@echo off
REM Opens AnshuX desktop app — no terminal window.
cd /d "%~dp0"
if not exist "venv\Scripts\pythonw.exe" (
  echo AnshuX is not installed. Double-click INSTALL_ANSHUX.bat first.
  pause
  exit /b 1
)
wscript.exe "%~dp0AnshuX.vbs"
