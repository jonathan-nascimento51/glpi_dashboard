#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Script para executar validação E2E do Dashboard GLPI

.DESCRIPTION
    Este script executa o agente de validação end-to-end do dashboard,
    verificando dependências, iniciando serviços se necessário e
    executando a validação completa.

.PARAMETER FrontendUrl
    URL do frontend (padrão: http://localhost:3000)

.PARAMETER SkipServiceStart
    Pula a inicialização automática dos serviços

.PARAMETER Headless
    Executa o navegador em modo headless (padrão: true)

.PARAMETER Timeout
    Timeout em segundos para cada etapa (padrão: 30)

.EXAMPLE
    .\run-dashboard-e2e-validation.ps1
    
.EXAMPLE
    .\run-dashboard-e2e-validation.ps1 -FrontendUrl "http://localhost:3001" -Headless $false
#>

param(
    [string]$FrontendUrl = "http://localhost:3000",
    [switch]$SkipServiceStart,
    [bool]$Headless = $true,
    [int]$Timeout = 30
)

# Configurações
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Cores para output
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    
    $colors = @{
        "Red" = [ConsoleColor]::Red
        "Green" = [ConsoleColor]::Green
        "Yellow" = [ConsoleColor]::Yellow
        "Blue" = [ConsoleColor]::Blue
        "Cyan" = [ConsoleColor]::Cyan
        "White" = [ConsoleColor]::White
    }
    
    Write-Host $Message -ForegroundColor $colors[$Color]
}

function Write-Header {
    param([string]$Title)
    Write-ColorOutput "`n=== $Title ===" "Cyan"
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "✓ $Message" "Green"
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "⚠ $Message" "Yellow"
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput "✗ $Message" "Red"
}

# Função para verificar se um comando existe
function Test-Command {
    param([string]$Command)
    
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

# Função para verificar se um serviço está rodando
function Test-ServiceRunning {
    param([string]$Url)
    
    try {
        $response = Invoke-WebRequest -Uri $Url -Method GET -TimeoutSec 5 -UseBasicParsing
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

# Função para instalar dependências Node.js
function Install-NodeDependencies {
    Write-Header "Verificando Dependências Node.js"
    
    if (-not (Test-Command "node")) {
        Write-Error "Node.js não encontrado. Por favor, instale o Node.js primeiro."
        exit 1
    }
    
    if (-not (Test-Command "npm")) {
        Write-Error "npm não encontrado. Por favor, instale o npm primeiro."
        exit 1
    }
    
    Write-Success "Node.js e npm encontrados"
    
    # Verificar se playwright está instalado
    $playwrightInstalled = $false
    try {
        $result = npm list playwright --depth=0 2>$null
        if ($LASTEXITCODE -eq 0) {
            $playwrightInstalled = $true
        }
    } catch {
        # Ignorar erro
    }
    
    if (-not $playwrightInstalled) {
        Write-Warning "Playwright não encontrado. Instalando..."
        npm install playwright axios
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Falha ao instalar dependências"
            exit 1
        }
        
        Write-ColorOutput "Instalando navegadores do Playwright..." "Blue"
        npx playwright install chromium
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Falha ao instalar navegadores do Playwright"
            exit 1
        }
    }
    
    Write-Success "Dependências verificadas"
}

# Função para iniciar serviços
function Start-Services {
    if ($SkipServiceStart) {
        Write-Warning "Pulando inicialização de serviços (--SkipServiceStart)"
        return
    }
    
    Write-Header "Verificando Serviços"
    
    # Verificar se frontend está rodando
    $frontendRunning = Test-ServiceRunning $FrontendUrl
    if (-not $frontendRunning) {
        Write-Warning "Frontend não está rodando em $FrontendUrl"
        Write-ColorOutput "Tentando iniciar frontend..." "Blue"
        
        # Tentar iniciar frontend em background
        $frontendPath = Join-Path $PSScriptRoot "..\frontend"
        if (Test-Path $frontendPath) {
            Push-Location $frontendPath
            try {
                Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WindowStyle Hidden
                Write-ColorOutput "Aguardando frontend inicializar..." "Blue"
                
                # Aguardar até 30 segundos para o frontend inicializar
                $attempts = 0
                while ($attempts -lt 30 -and -not (Test-ServiceRunning $FrontendUrl)) {
                    Start-Sleep 1
                    $attempts++
                }
                
                if (Test-ServiceRunning $FrontendUrl) {
                    Write-Success "Frontend iniciado com sucesso"
                } else {
                    Write-Warning "Frontend pode não ter iniciado completamente"
                }
            } finally {
                Pop-Location
            }
        }
    } else {
        Write-Success "Frontend está rodando em $FrontendUrl"
    }
    
    # Verificar se backend está rodando
    $backendUrls = @("http://localhost:5000/api/status", "http://localhost:5000/api/test")
    $backendRunning = $false
    
    foreach ($url in $backendUrls) {
        if (Test-ServiceRunning $url) {
            Write-Success "Backend está rodando (testado via $url)"
            $backendRunning = $true
            break
        }
    }
    
    if (-not $backendRunning) {
        Write-Warning "Backend pode não estar rodando. A validação tentará usar dados de fallback."
    }
}

# Função principal de validação
function Invoke-DashboardValidation {
    Write-Header "Executando Validação E2E do Dashboard"
    
    # Definir variáveis de ambiente
    $env:FRONTEND_URL = $FrontendUrl
    $env:HEADLESS = $Headless.ToString().ToLower()
    $env:TIMEOUT = ($Timeout * 1000).ToString()  # Converter para ms
    
    # Caminho para o script de validação
    $validatorScript = Join-Path $PSScriptRoot "dashboard-e2e-validator.js"
    
    if (-not (Test-Path $validatorScript)) {
        Write-Error "Script de validação não encontrado: $validatorScript"
        exit 1
    }
    
    Write-ColorOutput "Iniciando validação..." "Blue"
    Write-ColorOutput "Frontend URL: $FrontendUrl" "White"
    Write-ColorOutput "Headless: $Headless" "White"
    Write-ColorOutput "Timeout: $Timeout segundos" "White"
    
    try {
        # Executar o validador
        $result = node $validatorScript
        $exitCode = $LASTEXITCODE
        
        Write-ColorOutput "`nSaída do validador:" "Blue"
        Write-Output $result
        
        if ($exitCode -eq 0) {
            Write-Success "`nValidação concluída com sucesso!"
            
            # Procurar arquivos de evidência gerados
            $reportFiles = Get-ChildItem -Path "." -Name "dashboard_validation_report_*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
            $screenshotFiles = Get-ChildItem -Path "." -Name "dashboard_*_*.png" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
            
            if ($reportFiles) {
                Write-Success "Relatório gerado: $reportFiles"
                
                # Mostrar resumo do relatório
                try {
                    $reportContent = Get-Content $reportFiles | ConvertFrom-Json
                    Write-ColorOutput "`nResumo da Validação:" "Cyan"
                    Write-ColorOutput "Status: $($reportContent.status)" $(if ($reportContent.status -eq "PASS") { "Green" } else { "Red" })
                    Write-ColorOutput "Mismatches: $($reportContent.mismatches.Count)" "White"
                    Write-ColorOutput "Notas: $($reportContent.notes.Count)" "White"
                    
                    if ($reportContent.mismatches.Count -gt 0) {
                        Write-ColorOutput "`nMismatches encontrados:" "Yellow"
                        foreach ($mismatch in $reportContent.mismatches) {
                            Write-ColorOutput "  - $($mismatch.field): $($mismatch.issue)" "Yellow"
                        }
                    }
                } catch {
                    Write-Warning "Não foi possível analisar o relatório JSON"
                }
            }
            
            if ($screenshotFiles) {
                Write-Success "Screenshot capturado: $screenshotFiles"
            }
            
        } else {
            Write-Error "Validação falhou (código de saída: $exitCode)"
            return $false
        }
        
        return $true
        
    } catch {
        Write-Error "Erro ao executar validação: $($_.Exception.Message)"
        return $false
    }
}

# Função para limpeza
function Invoke-Cleanup {
    Write-Header "Limpeza"
    
    # Remover variáveis de ambiente temporárias
    Remove-Item Env:FRONTEND_URL -ErrorAction SilentlyContinue
    Remove-Item Env:HEADLESS -ErrorAction SilentlyContinue
    Remove-Item Env:TIMEOUT -ErrorAction SilentlyContinue
    
    Write-Success "Limpeza concluída"
}

# Script principal
try {
    Write-Header "Dashboard E2E Validation Runner"
    Write-ColorOutput "Iniciando validação end-to-end do dashboard GLPI..." "Blue"
    
    # 1. Verificar e instalar dependências
    Install-NodeDependencies
    
    # 2. Iniciar serviços se necessário
    Start-Services
    
    # 3. Executar validação
    $success = Invoke-DashboardValidation
    
    # 4. Limpeza
    Invoke-Cleanup
    
    # 5. Resultado final
    if ($success) {
        Write-Header "Validação Concluída com Sucesso"
        Write-Success "Todos os testes foram executados. Verifique os arquivos de evidência gerados."
        exit 0
    } else {
        Write-Header "Validação Falhou"
        Write-Error "A validação encontrou problemas. Verifique os logs e evidências."
        exit 1
    }
    
} catch {
    Write-Error "Erro fatal durante execução: $($_.Exception.Message)"
    Write-ColorOutput $_.ScriptStackTrace "Red"
    exit 1
} finally {
    # Garantir limpeza mesmo em caso de erro
    Invoke-Cleanup
}