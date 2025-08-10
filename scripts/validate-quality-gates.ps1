# Script de Validação Local - Quality Gates (PowerShell)
# Execute este script antes de fazer push para validar localmente

$ErrorActionPreference = "Stop"

Write-Host " Iniciando validação local dos Quality Gates..." -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green

function Write-Info($message) {
    Write-Host "[INFO] $message" -ForegroundColor Green
}

function Write-Warn($message) {
    Write-Host "[WARN] $message" -ForegroundColor Yellow
}

function Write-Error($message) {
    Write-Host "[ERROR] $message" -ForegroundColor Red
}

# Verificar se estamos no diretório correto
if (-not (Test-Path "pyproject.toml") -or -not (Test-Path "frontend") -or -not (Test-Path "backend")) {
    Write-Error "Execute este script na raiz do projeto GLPI Dashboard"
    exit 1
}

# Função para validar backend
function Validate-Backend {
    Write-Info "🐍 Validando Backend..."
    
    Push-Location backend
    
    try {
        # Verificar se venv está ativo
        if (-not $env:VIRTUAL_ENV) {
            Write-Warn "Virtual environment não detectado. Ative manualmente."
        }
        
        # Code Quality - Ruff
        Write-Info "Executando Ruff (formatação e linting)..."
        ruff check .
        ruff format --check .
        
        # Type Checking - MyPy
        Write-Info "Executando MyPy (type checking)..."
        mypy .
        
        # Security - Bandit
        Write-Info "Executando Bandit (security scan)..."
        bandit -r app/ -ll
        
        # Tests with Coverage
        Write-Info "Executando testes com cobertura..."
        pytest --cov=app --cov-fail-under=80 --cov-report=term-missing
        
        Write-Info "✅ Backend validado com sucesso!"
    }
    finally {
        Pop-Location
    }
}

# Função para validar frontend
function Validate-Frontend {
    Write-Info "⚛️ Validando Frontend..."
    
    Push-Location frontend
    
    try {
        # Instalar dependências
        Write-Info "Instalando dependências do frontend..."
        npm ci
        
        # ESLint (zero warnings)
        Write-Info "Executando ESLint..."
        npm run lint -- --max-warnings 0
        
        # Prettier
        Write-Info "Verificando formatação com Prettier..."
        npm run format:check
        
        # TypeScript
        Write-Info "Executando TypeScript check..."
        npm run type-check
        
        # Tests with Coverage
        Write-Info "Executando testes com cobertura..."
        npm run test:coverage
        
        # Build
        Write-Info "Verificando build..."
        npm run build
        
        Write-Info " Frontend validado com sucesso!"
    }
    finally {
        Pop-Location
    }
}

# Função para verificar drift da API
function Validate-ApiDrift {
    Write-Info " Verificando API Drift..."
    
    Push-Location frontend
    try {
        npm run check:drift
        Write-Info " Nenhum API drift detectado!"
    }
    finally {
        Pop-Location
    }
}

# Função principal
function Main {
    param(
        [switch]$SkipBackend,
        [switch]$SkipFrontend,
        [switch]$SkipIntegration
    )
    
    $startTime = Get-Date
    
    try {
        if (-not $SkipBackend) {
            Validate-Backend
        } else {
            Write-Warn "Pulando validação do backend"
        }
        
        if (-not $SkipFrontend) {
            Validate-Frontend
        } else {
            Write-Warn "Pulando validação do frontend"
        }
        
        Validate-ApiDrift
        
        $endTime = Get-Date
        $duration = ($endTime - $startTime).TotalSeconds
        
        Write-Host ""
        Write-Host " Todas as validações passaram com sucesso!" -ForegroundColor Green
        Write-Host "  Tempo total: $([math]::Round($duration, 2))s" -ForegroundColor Green
        Write-Host " Pronto para push!" -ForegroundColor Green
    }
    catch {
        Write-Error "Validação falhou: $_"
        exit 1
    }
}

# Executar função principal
Main @args
