# Script de Validação do Dashboard GLPI
Write-Host "=== VALIDAÇÃO DO DASHBOARD GLPI ===" -ForegroundColor Green
Write-Host ""

# 1. Verificar Backend
Write-Host "1. Verificando Backend (porta 5000)..." -ForegroundColor Yellow
try {
    $backendTest = Invoke-RestMethod -Uri "http://localhost:5000/api/status" -Method GET -TimeoutSec 10
    Write-Host " Backend está respondendo" -ForegroundColor Green
    Write-Host "  Status: $($backendTest.status)" -ForegroundColor Cyan
} catch {
    Write-Host " Backend não está respondendo" -ForegroundColor Red
}

# 2. Verificar Métricas
Write-Host ""
Write-Host "2. Verificando Métricas..." -ForegroundColor Yellow
try {
    $metricsTest = Invoke-RestMethod -Uri "http://localhost:5000/api/metrics" -Method GET -TimeoutSec 10
    Write-Host " Métricas obtidas com sucesso" -ForegroundColor Green
    Write-Host "  Novos: $($metricsTest.data.novos)" -ForegroundColor Cyan
    Write-Host "  Pendentes: $($metricsTest.data.pendentes)" -ForegroundColor Cyan
    Write-Host "  Em Progresso: $($metricsTest.data.progresso)" -ForegroundColor Cyan
    Write-Host "  Resolvidos: $($metricsTest.data.resolvidos)" -ForegroundColor Cyan
} catch {
    Write-Host " Erro ao obter métricas" -ForegroundColor Red
}

# 3. Verificar Frontend
Write-Host ""
Write-Host "3. Verificando Frontend (porta 5173)..." -ForegroundColor Yellow
$frontendTest = Test-NetConnection -ComputerName localhost -Port 5173 -WarningAction SilentlyContinue
if ($frontendTest.TcpTestSucceeded) {
    Write-Host " Frontend está acessível" -ForegroundColor Green
    Write-Host "  URL: http://localhost:5173/" -ForegroundColor Cyan
} else {
    Write-Host " Frontend não está acessível" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== VALIDAÇÃO CONCLUÍDA ===" -ForegroundColor Green
Write-Host "Dashboard: http://localhost:5173/" -ForegroundColor Cyan
Write-Host "API: http://localhost:5000/api/" -ForegroundColor Cyan
