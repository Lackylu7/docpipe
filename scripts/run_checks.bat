@echo off
setlocal
cd /d "%~dp0.."
if exist ".venv\Scripts\python.exe" (
  set "PY=.venv\Scripts\python.exe"
) else (
  set "PY=python"
)

"%PY%" -m ruff check . || exit /b 1
"%PY%" -m pytest -q || exit /b 1
"%PY%" -m docpipe.cli templates --language zh-CN || exit /b 1
"%PY%" -m docpipe.cli demo --output outputs/demo --language zh-CN || exit /b 1
