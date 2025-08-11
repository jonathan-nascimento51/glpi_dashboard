#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Orquestrador CI - Sobe servicos, espera saude, roda E2E e coleta artefatos

.DESCRIPTION
    Script completo que:
    1) Prepara ambiente e dependencias
    2) Sobe backend (FastAPI) e frontend (Vite) em segundo plano
    3) Espera saude da API (total>0) com timeout
    4) Executa testes E2E
    5) Coleta artefatos sempre (PASS ou FAIL)
    6) Encerra servicos e retorna sumario

.PARAMETER FrontendUrl
    URL do frontend (padrao: http://localhost:3000)

.PARAMETER BackendUrl
    URL do backend (padrao: http://localhost:8000)

.PARAMETER HealthTimeout
    Timeout em segundos para esperar saude (padrao: 120)

.EXAMPLE
    .\scripts\orchestrate-ci.ps1
    
.EXAMPLE
    .\scripts\orchestrate-ci.ps1 -HealthTimeout 180
#>

param(
    [string]$FrontendUrl = "http://localhost:3000",
    [string]$BackendUrl = "http://localhost:8000",
    [int]$HealthTimeout = 120
)

# Configuracoes
$ErrorActionPreference = "Continue"
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
    Write-ColorOutput "[OK] $Message" "Green"
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "[WARN] $Message" "Yellow"
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput "[ERROR] $Message" "Red"
}

# Configurar variaveis de ambiente
$env:FRONTEND_URL = $FrontendUrl
$env:BACKEND_URL = $BackendUrl

# Funcao para esperar saude da API
function Wait-Healthy {
    param(
        [string]$Url,
        [int]$TimeoutSec = 90
    )
    
    $start = Get-Date
    $attempts = 0
    
    while ((Get-Date) - $start -lt [TimeSpan]::FromSeconds($TimeoutSec)) {
        $attempts++
        try {
            Write-ColorOutput "Tentativa $attempts - Testando: $Url" "Blue"
            $response = Invoke-WebRequest $Url -UseBasicParsing -TimeoutSec 5
            
            if ($response.StatusCode -eq 200) {
                $json = $response.Content | ConvertFrom-Json -ErrorAction Stop
                
                if ($null -ne $json.total -and [int]$json.total -gt 0) {
                    Write-Success "API saudavel! Total: $($json.total)"
                    return $true
                } else {
                    Write-Warning "API respondeu mas total=$($json.total) (esperando >0)"
                }
            } else {
                Write-Warning "Status: $($response.StatusCode)"
            }
        } catch {
            Write-Warning "Erro: $($_.Exception.Message)"
        }
        
        Start-Sleep -Seconds 2
    }
    
    Write-Error "Timeout atingido apos $TimeoutSec segundos"
    return $false
}

# Funcao para coletar artefatos
function Collect-Artifacts {
    Write-Header "Coletando Artefatos"
    
    # Garantir que diretorio artifacts existe
    if (-not (Test-Path "artifacts")) {
        New-Item -ItemType Directory -Path "artifacts" -Force | Out-Null
    }
    
    # Coletar arquivos de evidencia gerados pelo E2E validator
    $evidenceFiles = @(
        "dashboard_*.png",
        "*report*.json",
        "api_response.json",
        "api_*_response.json",
        "html_snapshot*.html",
        "network*.har",
        "trace*.zip"
    )
    
    $collectedCount = 0
    foreach ($pattern in $evidenceFiles) {
        $files = Get-ChildItem -Path "." -Name $pattern -ErrorAction SilentlyContinue
        foreach ($file in $files) {
            try {
                Copy-Item $file "artifacts\" -Force
                Write-Success "Coletado: $file para artifacts\"
                $collectedCount++
            } catch {
                Write-Warning "Erro ao coletar $file : $($_.Exception.Message)"
            }
        }
    }
    
    if ($collectedCount -eq 0) {
        Write-Warning "Nenhum artefato encontrado para coletar"
        
        # Criar um relatorio basico de erro
        $errorReport = @{
            status = "FAIL"
            error = "Nenhum artefato gerado"
            timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
            frontend_url = $env:FRONTEND_URL
            backend_url = $env:BACKEND_URL
        }
        
        $errorReport | ConvertTo-Json | Out-File "artifacts\error_report.json" -Encoding UTF8
        Write-Success "Relatorio de erro criado: artifacts\error_report.json"
    } else {
        Write-Success "Total de artefatos coletados: $collectedCount"
    }
}

# Funcao para encerrar jobs
function Stop-AllJobs {
    Write-Header "Encerrando Servicos"
    
    $jobs = Get-Job -ErrorAction SilentlyContinue
    if ($jobs) {
        foreach ($job in $jobs) {
            Write-ColorOutput "Parando job: $($job.Name)" "Blue"
            Stop-Job $job -Force -ErrorAction SilentlyContinue
            Remove-Job $job -Force -ErrorAction SilentlyContinue
        }
        Write-Success "Todos os jobs foram encerrados"
    } else {
        Write-ColorOutput "Nenhum job ativo encontrado" "Blue"
    }
}

# Script principal
try {
    Write-Header "Orquestrador CI - GLPI Dashboard"
    Write-ColorOutput "Frontend URL: $FrontendUrl" "White"
    Write-ColorOutput "Backend URL: $BackendUrl" "White"
    Write-ColorOutput "Health Timeout: $HealthTimeout segundos" "White"
    
    # 1) Preparar ambiente
    Write-Header "Preparando Ambiente"
    
    # Instalar dependencias Node.js
    Write-ColorOutput "Instalando dependencias Node.js..." "Blue"
    try {
        npm ci 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "npm ci falhou, tentando npm install..."
            npm install
        }
    } catch {
        Write-Warning "Erro no npm, tentando npm install..."
        npm install
    }
    
    # Instalar Playwright
    Write-ColorOutput "Instalando Playwright..." "Blue"
    npm install -D @playwright/test
    npx playwright install --with-deps
    
    # Criar diretorio de artefatos
    if (-not (Test-Path "artifacts")) {
        New-Item -ItemType Directory -Path "artifacts" -Force | Out-Null
    }
    Write-Success "Ambiente preparado"
    
    # 2) Subir servicos
    Write-Header "Iniciando Servicos"
    
    # Backend (FastAPI)
    Write-ColorOutput "Iniciando backend..." "Blue"
    $backendJob = Start-Job -Name "backend" -ScriptBlock {
        Set-Location $using:PWD
        Set-Location backend
        
        # Ativar ambiente virtual se existir
        if (Test-Path ".venv\Scripts\Activate.ps1") {
            & ".venv\Scripts\Activate.ps1"
        }
        
        # Iniciar uvicorn
        uvicorn main:app --host 0.0.0.0 --port 8000 --log-level info
    }
    
    if ($backendJob) {
        Write-Success "Backend job iniciado (ID: $($backendJob.Id))"
    } else {
        Write-Error "Falha ao iniciar backend job"
    }
    
    # Frontend (Vite)
    Write-ColorOutput "Iniciando frontend..." "Blue"
    $frontendJob = Start-Job -Name "frontend" -ScriptBlock {
        Set-Location $using:PWD
        Set-Location frontend
        npm run dev
    }
    
    if ($frontendJob) {
        Write-Success "Frontend job iniciado (ID: $($frontendJob.Id))"
    } else {
        Write-Error "Falha ao iniciar frontend job"
    }
    
    # Aguardar um pouco para os servicos iniciarem
    Write-ColorOutput "Aguardando servicos iniciarem..." "Blue"
    Start-Sleep -Seconds 10
    
    # 3) Esperar saude
    Write-Header "Aguardando Saude da API"
    
    # Tentar frontend proxy primeiro, depois backend direto
    $healthOk = $false
    
    Write-ColorOutput "Testando via frontend proxy..." "Blue"
    $healthOk = Wait-Healthy "$FrontendUrl/api/metrics" -TimeoutSec $HealthTimeout
    
    if (-not $healthOk) {
        Write-ColorOutput "Frontend proxy falhou, testando backend direto..." "Blue"
        $healthOk = Wait-Healthy "$BackendUrl/api/metrics" -TimeoutSec 60
    }
    
    if (-not $healthOk) {
        Write-Error "Saude nao atingida (total>0). Gerando artefatos de erro..."
        
        # Mesmo com falha, tentar executar o validator para gerar screenshot
        Write-ColorOutput "Executando validator para capturar evidencias de erro..." "Yellow"
        try {
            node scripts\dashboard-e2e-validator.js
        } catch {
            Write-Warning "Validator falhou: $($_.Exception.Message)"
        }
        
        Collect-Artifacts
        Stop-AllJobs
        
        Write-Header "RESULTADO FINAL: FAIL"
        Write-Error "Pipeline falhou - saude da API nao atingida"
        exit 1
    }
    
    # 4) Executar testes E2E
    Write-Header "Executando Testes E2E"
    
    $testsPassed = $false
    
    # Tentar npm run e2e primeiro
    try {
        Write-ColorOutput "Executando: npm run e2e" "Blue"
        npm run e2e
        if ($LASTEXITCODE -eq 0) {
            $testsPassed = $true
            Write-Success "Testes E2E passaram via npm run e2e"
        } else {
            Write-Warning "npm run e2e falhou (codigo: $LASTEXITCODE), tentando validator direto..."
        }
    } catch {
        Write-Warning "Erro no npm run e2e: $($_.Exception.Message)"
    }
    
    # Se npm run e2e falhou, tentar validator direto
    if (-not $testsPassed) {
        try {
            Write-ColorOutput "Executando: node scripts\dashboard-e2e-validator.js" "Blue"
            node scripts\dashboard-e2e-validator.js
            if ($LASTEXITCODE -eq 0) {
                $testsPassed = $true
                Write-Success "Testes E2E passaram via validator direto"
            } else {
                Write-Warning "Validator direto tambem falhou (codigo: $LASTEXITCODE)"
            }
        } catch {
            Write-Warning "Erro no validator direto: $($_.Exception.Message)"
        }
    }
    
    # 5) Coletar artefatos (sempre, independente do resultado)
    Collect-Artifacts
    
    # 6) Encerrar servicos
    Stop-AllJobs
    
    # Resultado final
    Write-Header "RESULTADO FINAL"
    
    if ($testsPassed) {
        Write-Success "Pipeline PASSOU - Todos os testes foram executados com sucesso"
        Write-ColorOutput "Artefatos disponiveis em: .\artifacts\" "Green"
        exit 0
    } else {
        Write-Warning "Pipeline FALHOU - Testes E2E falharam, mas artefatos foram coletados"
        Write-ColorOutput "Artefatos disponiveis em: .\artifacts\" "Yellow"
        Write-ColorOutput "Verifique artifacts\report.json para detalhes" "Yellow"
        exit 1
    }
    
} catch {
    Write-Error "Erro fatal durante execucao: $($_.Exception.Message)"
    Write-ColorOutput $_.ScriptStackTrace "Red"
    
    # Tentar coletar artefatos mesmo com erro fatal
    try {
        Collect-Artifacts
    } catch {
        Write-Warning "Erro ao coletar artefatos: $($_.Exception.Message)"
    }
    
    Stop-AllJobs
    exit 1
} finally {
    # Garantir limpeza mesmo em caso de erro
    try {
        Stop-AllJobs
    } catch {
        # Silencioso
    }
}
