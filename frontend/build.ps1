# Frontend Build Script for Windows
# PowerShell script

Write-Host "Installing frontend dependencies..." -ForegroundColor Green
npm ci

Write-Host "Running security audit..." -ForegroundColor Green
npm audit --audit-level=high

Write-Host "Running linting..." -ForegroundColor Green
npm run lint

Write-Host "Running type checking..." -ForegroundColor Green
npm run type-check

Write-Host "Running tests..." -ForegroundColor Green
npm run test

Write-Host "Building for production..." -ForegroundColor Green
npm run build

Write-Host "Frontend build completed successfully!" -ForegroundColor Green
