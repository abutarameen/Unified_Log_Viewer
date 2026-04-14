# Crypt Mainica backend bootstrap for Windows PowerShell
# Usage: powershell -ExecutionPolicy Bypass -File .\crypt_mainica_backend\run_backend.ps1

$ErrorActionPreference = "Stop"

Write-Host "Installing backend dependencies via Python module launcher..."
if (Get-Command py -ErrorAction SilentlyContinue) {
    py -m pip install -r .\crypt_mainica_backend\requirements.txt
    py -m uvicorn crypt_mainica_backend.main:app --reload --host 0.0.0.0 --port 8000
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    python -m pip install -r .\crypt_mainica_backend\requirements.txt
    python -m uvicorn crypt_mainica_backend.main:app --reload --host 0.0.0.0 --port 8000
} else {
    throw "Python launcher not found. Install Python 3.10+ and add it to PATH."
}
