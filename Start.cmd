@echo off
setlocal
set "RUNTIME_ARCH=x64"
if /I "%PROCESSOR_ARCHITECTURE%"=="ARM64" set "RUNTIME_ARCH=arm64"
if /I "%PROCESSOR_ARCHITEW6432%"=="ARM64" set "RUNTIME_ARCH=arm64"
set "RUNTIME_NODE=%~dp0runtimes\win32-%RUNTIME_ARCH%\node\node.exe"
if not exist "%RUNTIME_NODE%" (
 echo Download the ready Universal installer from:
 echo https://github.com/alex-hohaizel/codex-agents/releases/latest
 pause
 exit /b 1
)
set "NODE_OPTIONS="
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
set "PYTHONDONTWRITEBYTECODE=1"
"%RUNTIME_NODE%" "%~dp0setup\launch.mjs" %*
set "SETUP_EXIT=%ERRORLEVEL%"
if not "%SETUP_EXIT%"=="0" pause
exit /b %SETUP_EXIT%
