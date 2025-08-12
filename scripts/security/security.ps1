# GLPI Dashboard - Scripts de Segurança
# Alternativa ao Makefile para Windows PowerShell

function Show-Help {
    Write-Host "GLPI Dashboard - Comandos Disponíveis" -ForegroundColor Blue
    Write-Host "=====================================" -ForegroundColor Blue
    Write-Host "security         Executa verificação completa de segurança" -ForegroundColor Green
    Write-Host "security-quick   Executa verificação rápida de segurança" -ForegroundColor Green
    Write-Host "security-bandit  Executa análise Bandit" -ForegroundColor Green
    Write-Host "security-safety  Executa verificação Safety" -ForegroundColor Green
    Write-Host "security-gitleaks Executa detecção GitLeaks" -ForegroundColor Green
    Write-Host "security-semgrep Executa análise Semgrep" -ForegroundColor Green
    Write-Host "pre-commit       Executa hooks de pre-commit" -ForegroundColor Green
    Write-Host "lint             Executa linting (ruff + black + isort)" -ForegroundColor Green
    Write-Host "test             Executa todos os testes" -ForegroundColor Green
    Write-Host "validate         Executa lint + test + security-quick" -ForegroundColor Green
    Write-Host "clean            Remove arquivos temporários" -ForegroundColor Green
    Write-Host "" 
    Write-Host "Uso: .\\security.ps1 <comando>" -ForegroundColor Yellow
}

function Invoke-Security {
    Write-Host "Executando verificação completa de segurança..." -ForegroundColor Yellow
    python scripts/security_check.py
    Write-Host "Verificação de segurança concluída!" -ForegroundColor Green
}

function Invoke-SecurityQuick {
    Write-Host "Executando verificação rápida de segurança..." -ForegroundColor Yellow
    python scripts/security_check.py --quick
    Write-Host "Verificação rápida concluída!" -ForegroundColor Green
}

function Invoke-SecurityBandit {
    Write-Host "Executando análise Bandit..." -ForegroundColor Yellow
    if (!(Test-Path "security_reports")) { New-Item -ItemType Directory -Path "security_reports" }
    bandit -r backend -f json -o security_reports/bandit_report.json -c bandit.yaml
    Write-Host "Análise Bandit concluída!" -ForegroundColor Green
}

function Invoke-SecuritySafety {
    Write-Host "Executando verificação Safety..." -ForegroundColor Yellow
    if (!(Test-Path "security_reports")) { New-Item -ItemType Directory -Path "security_reports" }
    safety check --json > security_reports/safety_report.json
    Write-Host "Verificação Safety concluída!" -ForegroundColor Green
}

function Invoke-SecurityGitleaks {
    Write-Host "Executando detecção GitLeaks..." -ForegroundColor Yellow
    if (!(Test-Path "security_reports")) { New-Item -ItemType Directory -Path "security_reports" }
    gitleaks detect --config .gitleaks.toml --report-format json --report-path security_reports/gitleaks_report.json
    Write-Host "Detecção GitLeaks concluída!" -ForegroundColor Green
}

function Invoke-SecuritySemgrep {
    Write-Host "Executando análise Semgrep..." -ForegroundColor Yellow
    if (!(Test-Path "security_reports")) { New-Item -ItemType Directory -Path "security_reports" }
    semgrep --config=auto --json --output=security_reports/semgrep_report.json backend
    Write-Host "Análise Semgrep concluída!" -ForegroundColor Green
}

function Invoke-PreCommit {
    Write-Host "Executando hooks de pre-commit..." -ForegroundColor Yellow
    pre-commit run --all-files
    Write-Host "Pre-commit hooks executados!" -ForegroundColor Green
}

function Invoke-Lint {
    Write-Host "Executando linting..." -ForegroundColor Yellow
    Set-Location backend
    ruff check . --fix
    black . --line-length 100
    isort . --profile black
    Set-Location ..
    Write-Host "Linting concluído!" -ForegroundColor Green
}

function Invoke-Test {
    Write-Host "Executando testes..." -ForegroundColor Yellow
    Set-Location backend
    python -m pytest tests/ -v
    Set-Location ..
    Write-Host "Testes concluídos!" -ForegroundColor Green
}

function Invoke-Validate {
    Write-Host "Executando validação completa..." -ForegroundColor Yellow
    Invoke-Lint
    Invoke-Test
    Invoke-SecurityQuick
    Write-Host "Validação concluída com sucesso!" -ForegroundColor Green
}

function Invoke-Clean {
    Write-Host "Removendo arquivos temporários..." -ForegroundColor Yellow
    Get-ChildItem -Recurse -Name "*.pyc" | Remove-Item -Force
    Get-ChildItem -Recurse -Name "__pycache__" -Directory | Remove-Item -Recurse -Force
    Get-ChildItem -Recurse -Name ".pytest_cache" -Directory | Remove-Item -Recurse -Force
    if (Test-Path ".coverage") { Remove-Item ".coverage" -Force }
    if (Test-Path "htmlcov") { Remove-Item "htmlcov" -Recurse -Force }
    if (Test-Path "security_reports") { Remove-Item "security_reports" -Recurse -Force }
    Write-Host "Limpeza concluída!" -ForegroundColor Green
}

# Processamento de argumentos
if ($args.Count -eq 0) {
    Show-Help
    exit
}

switch ($args[0]) {
    "help" { Show-Help }
    "security" { Invoke-Security }
    "security-quick" { Invoke-SecurityQuick }
    "security-bandit" { Invoke-SecurityBandit }
    "security-safety" { Invoke-SecuritySafety }
    "security-gitleaks" { Invoke-SecurityGitleaks }
    "security-semgrep" { Invoke-SecuritySemgrep }
    "pre-commit" { Invoke-PreCommit }
    "lint" { Invoke-Lint }
    "test" { Invoke-Test }
    "validate" { Invoke-Validate }
    "clean" { Invoke-Clean }
    default {
        Write-Host "Comando desconhecido: $($args[0])" -ForegroundColor Red
        Write-Host "Use \"help\" para ver comandos disponíveis" -ForegroundColor Yellow
        Show-Help
    }
}
