$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if (Test-Path ".\.venv\Scripts\python.exe") {
  $python = ".\.venv\Scripts\python.exe"
} else {
  $python = "python"
}

& $python -m ruff check .
& $python -m pytest -q
& $python -m docpipe.cli templates --language zh-CN
& $python -m docpipe.cli demo --output outputs/demo --language zh-CN
