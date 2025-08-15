#!/usr/bin/env pwsh
# =============================================================================
# SCRIPT DE CONFIGURAÇÃO DO AMBIENTE GLPI DASHBOARD
# =============================================================================
# Este script configura o ambiente de desenvolvimento completo

param(
    [switch]$SkipDocker,
    [switch]$SkipDependencies,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

function Write-Status {
    param([string]$Message, [string]$Type = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Type) {
        "SUCCESS" { "Green" }
        "WARNING" { "Yellow" }
        "ERROR" { "Red" }
        default { "Cyan" }
    }
    Write-Host "[$timestamp] [$Type] $Message" -ForegroundColor $color
}

function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

function Test-Port {
    param([int]$Port)
    try {
        $connection = Test-NetConnection -ComputerName "localhost" -Port $Port -WarningAction SilentlyContinue
        return $connection.TcpTestSucceeded
    } catch {
        return $false
    }
}

Write-Status "Iniciando configuração do ambiente GLPI Dashboard" "SUCCESS"

# Verificar pré-requisitos
Write-Status "Verificando pré-requisitos..."

$prerequisites = @(
    @{Name="Docker"; Command="docker"; Required=$true},
    @{Name="Docker Compose"; Command="docker-compose"; Required=$true},
    @{Name="Node.js"; Command="node"; Required=$true},
    @{Name="NPM"; Command="npm"; Required=$true},
    @{Name="Python"; Command="python"; Required=$true}
)

$missingPrereqs = @()
foreach ($prereq in $prerequisites) {
    if (Test-Command $prereq.Command) {
        Write-Status "✓ $($prereq.Name) encontrado" "SUCCESS"
    } else {
        Write-Status "✗ $($prereq.Name) não encontrado" "ERROR"
        if ($prereq.Required) {
            $missingPrereqs += $prereq.Name
        }
    }
}

if ($missingPrereqs.Count -gt 0) {
    Write-Status "Pré-requisitos ausentes: $($missingPrereqs -join ', ')" "ERROR"
    Write-Status "Instale os pré-requisitos e execute novamente" "ERROR"
    exit 1
}

# Verificar arquivo .env
if (-not (Test-Path ".env")) {
    Write-Status "Arquivo .env não encontrado, copiando do template..." "WARNING"
    Copy-Item ".env.example" ".env"
    Write-Status "✓ Arquivo .env criado. Configure as variáveis antes de continuar" "SUCCESS"
}

# Configurar Docker Compose (Redis)
if (-not $SkipDocker) {
    Write-Status "Configurando serviços Docker..."
    
    # Verificar se Redis já está rodando
    if (Test-Port 6379) {
        Write-Status "Redis já está rodando na porta 6379" "WARNING"
    } else {
        Write-Status "Iniciando Redis via Docker Compose..."
        try {
            docker-compose up -d redis
            Start-Sleep -Seconds 5
            
            if (Test-Port 6379) {
                Write-Status "✓ Redis iniciado com sucesso" "SUCCESS"
            } else {
                Write-Status "✗ Falha ao iniciar Redis" "ERROR"
            }
        } catch {
            Write-Status "Erro ao iniciar Docker Compose: $($_.Exception.Message)" "ERROR"
        }
    }
}

# Instalar dependências do backend
if (-not $SkipDependencies) {
    Write-Status "Instalando dependências do backend..."
    try {
        Set-Location "backend"
        if (Test-Path "requirements.txt") {
            pip install -r requirements.txt
            Write-Status "✓ Dependências do backend instaladas" "SUCCESS"
        } elseif (Test-Path "pyproject.toml") {
            pip install -e .
            Write-Status "✓ Dependências do backend instaladas via pyproject.toml" "SUCCESS"
        }
        Set-Location ".."
    } catch {
        Write-Status "Erro ao instalar dependências do backend: $($_.Exception.Message)" "ERROR"
        Set-Location ".."
    }
    
    # Instalar dependências do frontend
    Write-Status "Instalando dependências do frontend..."
    try {
        Set-Location "frontend"
        npm install
        Write-Status "✓ Dependências do frontend instaladas" "SUCCESS"
        Set-Location ".."
    } catch {
        Write-Status "Erro ao instalar dependências do frontend: $($_.Exception.Message)" "ERROR"
        Set-Location ".."
    }
}

# Criar diretórios necessários
Write-Status "Criando diretórios necessários..."
$directories = @("temp", "logs", "artifacts")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Status "✓ Diretório '$dir' criado" "SUCCESS"
    }
}

# Testar conectividade com GLPI
Write-Status "Testando conectividade com GLPI..."
try {
    $envContent = Get-Content ".env" | Where-Object { $_ -match "^GLPI_" }
    $glpiUrl = ($envContent | Where-Object { $_ -match "^GLPI_URL=" }) -replace "GLPI_URL=", ""
    $userToken = ($envContent | Where-Object { $_ -match "^GLPI_USER_TOKEN=" }) -replace "GLPI_USER_TOKEN=", ""
    $appToken = ($envContent | Where-Object { $_ -match "^GLPI_APP_TOKEN=" }) -replace "GLPI_APP_TOKEN=", ""
    
    if ($glpiUrl -and $userToken -and $appToken) {
        $headers = @{
            "Content-Type" = "application/json"
            "Authorization" = "user_token $userToken"
            "App-Token" = $appToken
        }
        
        $response = Invoke-RestMethod -Uri "$glpiUrl/initSession" -Method POST -Headers $headers -TimeoutSec 10
        if ($response.session_token) {
            Write-Status "✓ Conectividade com GLPI OK" "SUCCESS"
        }
    } else {
        Write-Status "Configurações GLPI incompletas no .env" "WARNING"
    }
} catch {
    Write-Status "Erro ao testar GLPI: $($_.Exception.Message)" "WARNING"
}

Write-Status "Configuração do ambiente concluída!" "SUCCESS"
Write-Status "Próximos passos:" "INFO"
Write-Status "1. Configure as variáveis no arquivo .env" "INFO"
Write-Status "2. Execute: python app.py (backend)" "INFO"
Write-Status "3. Execute: cd frontend && npm run dev (frontend)" "INFO"
Write-Status "4. Acesse: http://localhost:3001 (frontend) e http://localhost:5000 (backend)" "INFO"