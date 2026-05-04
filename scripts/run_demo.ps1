$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if (Test-Path ".\.venv\Scripts\python.exe") {
  $python = ".\.venv\Scripts\python.exe"
} else {
  $python = "python"
}

& $python -m docpipe.cli demo --output outputs/demo
