Write-Host "=== VALIDAÇÃO DASHBOARD GLPI ===" -ForegroundColor Green
Write-Host ""

# Teste Backend (porta 5000)
Write-Host "Testando Backend (porta 5000)..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/metrics" -Method GET -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host " Backend funcionando (Status: $($response.StatusCode))" -ForegroundColor Green
        $data = $response.Content | ConvertFrom-Json
        $geral = $data.data.niveis.geral
        Write-Host "   Novos: $($geral.novos), Pendentes: $($geral.pendentes), Em Progresso: $($geral.progresso), Resolvidos: $($geral.resolvidos)" -ForegroundColor Cyan
    }
} catch {
    Write-Host " Backend não está respondendo: $($_.Exception.Message)" -ForegroundColor Red
}

# Teste Frontend (porta 5173)
Write-Host "\nTestando Frontend (porta 5173)..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5173" -Method GET -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host " Frontend acessível (Status: $($response.StatusCode))" -ForegroundColor Green
    }
} catch {
    Write-Host " Frontend não está acessível: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "\n=== FIM DA VALIDAÇÃO ===" -ForegroundColor Green
