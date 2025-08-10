# Script PowerShell para parar ambiente de preview

Write-Host "🛑 Parando Ambiente de Preview" -ForegroundColor Red
Write-Host "=============================" -ForegroundColor Red

# Parar backend
if (Test-Path "backend.pid") {
    $backendJobId = Get-Content "backend.pid"
    Write-Host "🔄 Parando backend (Job ID: $backendJobId)..." -ForegroundColor Cyan
    try {
        Stop-Job -Id $backendJobId -ErrorAction SilentlyContinue
        Remove-Job -Id $backendJobId -ErrorAction SilentlyContinue
        Write-Host "✅ Backend parado" -ForegroundColor Green
    } catch {
        Write-Host "  Erro ao parar job do backend" -ForegroundColor Yellow
    }
    Remove-Item "backend.pid" -ErrorAction SilentlyContinue
} else {
    Write-Host "  Arquivo backend.pid não encontrado" -ForegroundColor Yellow
}

# Parar processos Python relacionados
Write-Host " Parando processos Python..." -ForegroundColor Cyan
Get-Process | Where-Object {$_.ProcessName -like "*python*" -and $_.CommandLine -like "*main.py*"} | Stop-Process -Force -ErrorAction SilentlyContinue

# Parar frontend
if (Test-Path "frontend.pid") {
    $frontendJobId = Get-Content "frontend.pid"
    Write-Host " Parando frontend (Job ID: $frontendJobId)..." -ForegroundColor Cyan
    try {
        Stop-Job -Id $frontendJobId -ErrorAction SilentlyContinue
        Remove-Job -Id $frontendJobId -ErrorAction SilentlyContinue
        Write-Host " Frontend parado" -ForegroundColor Green
    } catch {
        Write-Host "  Erro ao parar job do frontend" -ForegroundColor Yellow
    }
    Remove-Item "frontend.pid" -ErrorAction SilentlyContinue
} else {
    Write-Host "  Arquivo frontend.pid não encontrado" -ForegroundColor Yellow
}

# Parar processos Node relacionados
Write-Host " Parando processos Node.js..." -ForegroundColor Cyan
Get-Process | Where-Object {$_.ProcessName -like "*node*" -and $_.CommandLine -like "*vite*"} | Stop-Process -Force -ErrorAction SilentlyContinue

# Limpar arquivos temporários
Write-Host " Limpando arquivos temporários..." -ForegroundColor Cyan
if (Test-Path "frontend\.env.local") {
    Remove-Item "frontend\.env.local" -ErrorAction SilentlyContinue
    Write-Host " Arquivo .env.local removido" -ForegroundColor Green
}

Write-Host "\n Ambiente de preview parado com sucesso!" -ForegroundColor Green
