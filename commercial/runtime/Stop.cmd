@echo off
setlocal
set "RUNTIME_DIR=%~dp0"
set "NODE_OPTIONS="
set "NODE_PATH="
set "PYTHONHOME="
set "PYTHONPATH="
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
set "PYTHONDONTWRITEBYTECODE=1"
set "PATH=%PATH%;%RUNTIME_DIR%bin"
set "AGENT_SYSTEM_NODE=%RUNTIME_DIR%bin\node.exe"
if exist "%RUNTIME_DIR%python\python.exe" set "AGENT_SYSTEM_PYTHON=%RUNTIME_DIR%python\python.exe"
"%RUNTIME_DIR%bin\node.exe" "%RUNTIME_DIR%control.mjs" stop %*
exit /b %errorlevel%
