@echo off
setlocal DisableDelayedExpansion
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1"
set "install_exit=%ERRORLEVEL%"
echo.
pause
exit /b %install_exit%
