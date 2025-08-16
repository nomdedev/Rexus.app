# Setup dev environment: create venv, install package in editable mode and dev deps
param(
    [string]$venv = ".venv"
)

python -m venv $venv
. "$venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip
# Install project in editable mode
python -m pip install -e .
# Install project requirements (keep requirements.txt as source of truth)
if (Test-Path "requirements.txt") {
    python -m pip install -r requirements.txt
} else {
    # Fallback: install pytest at least
    python -m pip install pytest
}
Write-Host "Dev environment ready. Activate with: . $venv\Scripts\Activate.ps1 and run: python -m pytest" -ForegroundColor Green
