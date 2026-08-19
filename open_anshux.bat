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
  echo Python not found.
  pause
  exit /b 1
)

REM Terminal work area (stays open like Codex). No spaces: team.py
%PYLAUNCH% "%~dp0team.py" %*
