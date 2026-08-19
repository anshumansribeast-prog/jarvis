@echo off
setlocal
cd /d "%~dp0"

set "PYLAUNCH="
where py >nul 2>&1
if %ERRORLEVEL%==0 set "PYLAUNCH=py -3"
if not defined PYLAUNCH (
  where python >nul 2>&1
  if %ERRORLEVEL%==0 set "PYLAUNCH=python"
)
if not defined PYLAUNCH (
  echo Python not found. Install from https://www.python.org/downloads/
  echo Check "Add python.exe to PATH".
  pause
  exit /b 1
)

REM Type:  python team.py
REM Not:   python team . py   (spaces break the filename)
%PYLAUNCH% "%~dp0team.py" %*
set ERR=%ERRORLEVEL%
if not "%ERR%"=="0" pause
exit /b %ERR%
