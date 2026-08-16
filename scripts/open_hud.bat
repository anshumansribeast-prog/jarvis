@echo off
for /f "tokens=2 delims==" %%a in ('findstr /B "ANSUX_PUBLIC_URL" .env 2^>nul') do set PUBLIC_URL=%%a
if "%PUBLIC_URL%"=="" set PUBLIC_URL=https://anshux.punah.pro
start "" "%PUBLIC_URL%"
