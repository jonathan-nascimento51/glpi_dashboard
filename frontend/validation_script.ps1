# Script de Valida��o do Dashboard GLPI
Write-Host "=== VALIDA��O DO DASHBOARD GLPI ===" -ForegroundColor Green
Write-Host ""

# 1. Verificar Backend
Write-Host "1. Verificando Backend (porta 5000)..." -ForegroundColor Yellow
try {
    $backendTest = Invoke-RestMethod -Uri "http://localhost:5000/api/status" -Method GET -TimeoutSec 10
    Write-Host " Backend est� respondendo" -ForegroundColor Green
    Write-Host "  Status: $($backendTest.status)" -ForegroundColor Cyan
} catch {
    Write-Host " Backend n�o est� respondendo" -ForegroundColor Red
}

# 2. Verificar M�tricas
Write-Host ""
Write-Host "2. Verificando M�tricas..." -ForegroundColor Yellow
try {
    $metricsTest = Invoke-RestMethod -Uri "http://localhost:5000/api/metrics" -Method GET -TimeoutSec 10
    Write-Host " M�tricas obtidas com sucesso" -ForegroundColor Green
    Write-Host "  Novos: $($metricsTest.data.novos)" -ForegroundColor Cyan
    Write-Host "  Pendentes: $($metricsTest.data.pendentes)" -ForegroundColor Cyan
    Write-Host "  Em Progresso: $($metricsTest.data.progresso)" -ForegroundColor Cyan
    Write-Host "  Resolvidos: $($metricsTest.data.resolvidos)" -ForegroundColor Cyan
} catch {
    Write-Host " Erro ao obter m�tricas" -ForegroundColor Red
}

# 3. Verificar Frontend
Write-Host ""
Write-Host "3. Verificando Frontend (porta 5173)..." -ForegroundColor Yellow
$frontendTest = Test-NetConnection -ComputerName localhost -Port 5173 -WarningAction SilentlyContinue
if ($frontendTest.TcpTestSucceeded) {
    Write-Host " Frontend est� acess�vel" -ForegroundColor Green
    Write-Host "  URL: http://localhost:5173/" -ForegroundColor Cyan
} else {
    Write-Host " Frontend n�o est� acess�vel" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== VALIDA��O CONCLU�DA ===" -ForegroundColor Green
Write-Host "Dashboard: http://localhost:5173/" -ForegroundColor Cyan
Write-Host "API: http://localhost:5000/api/" -ForegroundColor Cyan
