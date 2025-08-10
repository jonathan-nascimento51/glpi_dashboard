#!/bin/bash
# Script de Validação Local - Quality Gates
# Execute este script antes de fazer push para validar localmente

set -e  # Parar em caso de erro

echo " Iniciando validação local dos Quality Gates..."
echo "================================================"

# Cores para output
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m" # No Color

# Função para log colorido
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar se estamos no diretório correto
if [ ! -f "pyproject.toml" ] || [ ! -d "frontend" ] || [ ! -d "backend" ]; then
    log_error "Execute este script na raiz do projeto GLPI Dashboard"
    exit 1
fi

# Verificar dependências
log_info "Verificando dependências..."
command -v python3 >/dev/null 2>&1 || { log_error "Python3 não encontrado"; exit 1; }
command -v npm >/dev/null 2>&1 || { log_error "npm não encontrado"; exit 1; }

# Função para validar backend
validate_backend() {
    log_info " Validando Backend..."
    
    cd backend
    
    # Verificar se venv está ativo
    if [ -z "$VIRTUAL_ENV" ]; then
        log_warn "Virtual environment não detectado. Ativando..."
        if [ -f "../venv/bin/activate" ]; then
            source ../venv/bin/activate
        elif [ -f "../venv/Scripts/activate" ]; then
            source ../venv/Scripts/activate
        else
            log_error "Virtual environment não encontrado. Execute: python -m venv venv"
            exit 1
        fi
    fi
    
    # Instalar dependências se necessário
    log_info "Verificando dependências do backend..."
    pip install -q -r requirements.txt
    pip install -q ruff mypy bandit safety pytest-cov
    
    # Code Quality - Ruff
    log_info "Executando Ruff (formatação e linting)..."
    ruff check . || { log_error "Ruff check falhou"; exit 1; }
    ruff format --check . || { log_error "Ruff format check falhou"; exit 1; }
    
    # Type Checking - MyPy
    log_info "Executando MyPy (type checking)..."
    mypy . || { log_error "MyPy falhou"; exit 1; }
    
    # Security - Bandit
    log_info "Executando Bandit (security scan)..."
    bandit -r app/ -ll || { log_error "Bandit encontrou problemas de segurança"; exit 1; }
    
    # Dependency Security - Safety
    log_info "Executando Safety (dependency security)..."
    safety check || { log_warn "Safety encontrou vulnerabilidades conhecidas"; }
    
    # Tests with Coverage
    log_info "Executando testes com cobertura..."
    pytest --cov=app --cov-fail-under=80 --cov-report=term-missing || { log_error "Testes ou cobertura falharam"; exit 1; }
    
    cd ..
    log_info " Backend validado com sucesso!"
}

# Função para validar frontend
validate_frontend() {
    log_info " Validando Frontend..."
    
    cd frontend
    
    # Instalar dependências
    log_info "Instalando dependências do frontend..."
    npm ci
    
    # ESLint (zero warnings)
    log_info "Executando ESLint..."
    npm run lint -- --max-warnings 0 || { log_error "ESLint falhou"; exit 1; }
    
    # Prettier
    log_info "Verificando formatação com Prettier..."
    npm run format:check || { log_error "Prettier check falhou"; exit 1; }
    
    # TypeScript
    log_info "Executando TypeScript check..."
    npm run type-check || { log_error "TypeScript check falhou"; exit 1; }
    
    # Tests with Coverage
    log_info "Executando testes com cobertura..."
    npm run test:coverage || { log_error "Testes ou cobertura falharam"; exit 1; }
    
    # Build
    log_info "Verificando build..."
    npm run build || { log_error "Build falhou"; exit 1; }
    
    # Verificar tamanho do bundle
    BUNDLE_SIZE=$(du -sm dist/ | cut -f1)
    log_info "Tamanho do bundle: ${BUNDLE_SIZE}MB"
    if [ $BUNDLE_SIZE -gt 5 ]; then
        log_warn "Bundle size (${BUNDLE_SIZE}MB) excede 5MB"
    fi
    
    cd ..
    log_info " Frontend validado com sucesso!"
}

# Função para validar integração
validate_integration() {
    log_info " Validando Integração..."
    
    # Verificar se backend pode iniciar
    log_info "Testando inicialização do backend..."
    cd backend
    
    # Iniciar servidor em background
    uvicorn app.main:app --host 127.0.0.1 --port 8000 &
    SERVER_PID=$!
    
    # Aguardar servidor inicializar
    sleep 5
    
    # Verificar se API está respondendo
    if curl -f http://localhost:8000/docs >/dev/null 2>&1; then
        log_info " API docs acessível"
    else
        log_error "API docs não acessível"
        kill $SERVER_PID 2>/dev/null || true
        exit 1
    fi
    
    if curl -f http://localhost:8000/openapi.json >/dev/null 2>&1; then
        log_info " OpenAPI schema acessível"
    else
        log_error "OpenAPI schema não acessível"
        kill $SERVER_PID 2>/dev/null || true
        exit 1
    fi
    
    # Testar geração do cliente API
    cd ../frontend
    log_info "Testando geração do cliente API..."
    VITE_API_URL=http://localhost:8000 npm run gen:api || {
        log_error "Geração do cliente API falhou"
        kill $SERVER_PID 2>/dev/null || true
        exit 1
    }
    
    # Verificar se arquivo foi gerado
    if [ -f "src/api/generated/api.ts" ]; then
        log_info " Cliente API gerado com sucesso"
    else
        log_error "Arquivo do cliente API não foi gerado"
        kill $SERVER_PID 2>/dev/null || true
        exit 1
    fi
    
    # Parar servidor
    kill $SERVER_PID 2>/dev/null || true
    
    cd ..
    log_info " Integração validada com sucesso!"
}

# Função para verificar drift da API
validate_api_drift() {
    log_info " Verificando API Drift..."
    
    cd frontend
    npm run check:drift || { log_error "API drift detectado"; exit 1; }
    cd ..
    
    log_info " Nenhum API drift detectado!"
}

# Função principal
main() {
    local start_time=$(date +%s)
    
    # Verificar argumentos
    SKIP_BACKEND=false
    SKIP_FRONTEND=false
    SKIP_INTEGRATION=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-backend)
                SKIP_BACKEND=true
                shift
                ;;
            --skip-frontend)
                SKIP_FRONTEND=true
                shift
                ;;
            --skip-integration)
                SKIP_INTEGRATION=true
                shift
                ;;
            --help)
                echo "Uso: $0 [--skip-backend] [--skip-frontend] [--skip-integration]"
                echo "  --skip-backend     Pular validação do backend"
                echo "  --skip-frontend    Pular validação do frontend"
                echo "  --skip-integration Pular validação de integração"
                exit 0
                ;;
            *)
                log_error "Opção desconhecida: $1"
                exit 1
                ;;
        esac
    done
    
    # Executar validações
    if [ "$SKIP_BACKEND" = false ]; then
        validate_backend
    else
        log_warn "Pulando validação do backend"
    fi
    
    if [ "$SKIP_FRONTEND" = false ]; then
        validate_frontend
    else
        log_warn "Pulando validação do frontend"
    fi
    
    validate_api_drift
    
    if [ "$SKIP_INTEGRATION" = false ]; then
        validate_integration
    else
        log_warn "Pulando validação de integração"
    fi
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    echo ""
    echo " Todas as validações passaram com sucesso!"
    echo "  Tempo total: ${duration}s"
    echo " Pronto para push!"
}

# Executar função principal com todos os argumentos
main "$@"
