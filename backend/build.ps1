# Backend Build Script for Windows
# PowerShell script

Write-Host "Installing backend dependencies..." -ForegroundColor Green
pip install -r requirements.lock

Write-Host "Running linting..." -ForegroundColor Green
ruff check .
black --check .
isort --check-only .

Write-Host "Running tests..." -ForegroundColor Green
pytest -v

Write-Host "Backend build completed successfully!" -ForegroundColor Green
