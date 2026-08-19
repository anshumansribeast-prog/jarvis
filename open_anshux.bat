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

where cursor >nul 2>&1
if %ERRORLEVEL%==0 (
  start "" cursor "%~dp0anshux.code-workspace"
  goto run
)
where code >nul 2>&1
if %ERRORLEVEL%==0 (
  start "" code "%~dp0anshux.code-workspace"
  goto run
)
echo Open anshux.code-workspace in Cursor: File ^> Open Workspace from File
:run
if not defined PYLAUNCH (
  echo Python not found — workspace may still have opened.
  pause
  exit /b 1
)
echo Type: python team.py
echo Not:  python team . py
echo.
%PYLAUNCH% "%~dp0team.py" status
echo.
echo Commands:  python team.py
echo            python team.py opencode
pause
