@echo off
cd /d "%~dp0"
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
python "%~dp0team.py" status
echo.
echo Commands: python team.py
echo           python team.py opencode
pause
