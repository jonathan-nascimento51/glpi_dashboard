# Script PowerShell para execução do monitoramento GLPI Dashboard
# Criado automaticamente em 2025-08-16 23:47:58

$ErrorActionPreference = "Stop"
$BaseDir = "C:\Users\jonathan-moletta.PPIRATINI\projects\glpi_dashboard\backend"

try {
    Set-Location $BaseDir
    
    # Ativar ambiente virtual se existir
    if (Test-Path ".venv\Scripts\Activate.ps1") {
        & ".venv\Scripts\Activate.ps1"
    } elseif (Test-Path "..env\Scripts\Activate.ps1") {
        & "..env\Scripts\Activate.ps1"
    }
    
    # Executar monitoramento
    Write-Host "Iniciando monitoramento..." -ForegroundColor Green
    python monitoring_system.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Monitoramento executado com sucesso" -ForegroundColor Green
        Write-Host "Timestamp: $(Get-Date)" -ForegroundColor Gray
    } else {
        Write-Host "ERRO: Monitoramento falhou com código $LASTEXITCODE" -ForegroundColor Red
        Write-Host "Timestamp: $(Get-Date)" -ForegroundColor Gray
        exit $LASTEXITCODE
    }
} catch {
    Write-Host "ERRO: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Timestamp: $(Get-Date)" -ForegroundColor Gray
    exit 1
}
