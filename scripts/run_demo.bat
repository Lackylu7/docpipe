@echo off
setlocal
cd /d "%~dp0.."
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -m docpipe.cli demo --output outputs/demo
) else (
  python -m docpipe.cli demo --output outputs/demo
)
