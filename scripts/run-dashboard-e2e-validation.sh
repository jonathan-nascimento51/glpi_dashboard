#!/bin/bash

# Dashboard E2E Validation Runner (Bash)
# Script para executar validação E2E do Dashboard GLPI em sistemas Unix/Linux

set -euo pipefail

# Configurações padrão
FRONTEND_URL="http://localhost:3000"
SKIP_SERVICE_START=false
HEADLESS=true
TIMEOUT=30

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Funções de output colorido
write_header() {
    echo -e "\n${CYAN}=== $1 ===${NC}"
}

write_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

write_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

write_error() {
    echo -e "${RED}✗ $1${NC}"
}

write_info() {
    echo -e "${BLUE}$1${NC}"
}

# Função para mostrar ajuda
show_help() {
    cat << EOF
Dashboard E2E Validation Runner

USO:
    $0 [OPÇÕES]

OPÇÕES:
    -u, --frontend-url URL    URL do frontend (padrão: http://localhost:3000)
    -s, --skip-service-start  Pula a inicialização automática dos serviços
    -n, --no-headless        Executa o navegador em modo visual (não headless)
    -t, --timeout SECONDS    Timeout em segundos para cada etapa (padrão: 30)
    -h, --help               Mostra esta ajuda

EXEMPLOS:
    $0
    $0 --frontend-url "http://localhost:3001" --no-headless
    $0 --skip-service-start --timeout 60

EOF
}

# Parse de argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        -u|--frontend-url)
            FRONTEND_URL="$2"
            shift 2
            ;;
        -s|--skip-service-start)
            SKIP_SERVICE_START=true
            shift
            ;;
        -n|--no-headless)
            HEADLESS=false
            shift
            ;;
        -t|--timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            write_error "Opção desconhecida: $1"
            show_help
            exit 1
            ;;
    esac
done

# Função para verificar se um comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Função para verificar se um serviço está rodando
test_service_running() {
    local url="$1"
    if command_exists curl; then
        curl -s --max-time 5 "$url" >/dev/null 2>&1
    elif command_exists wget; then
        wget -q --timeout=5 --tries=1 "$url" -O /dev/null >/dev/null 2>&1
    else
        write_warning "curl ou wget não encontrados. Não é possível testar serviços."
        return 1
    fi
}

# Função para instalar dependências Node.js
install_node_dependencies() {
    write_header "Verificando Dependências Node.js"
    
    if ! command_exists node; then
        write_error "Node.js não encontrado. Por favor, instale o Node.js primeiro."
        exit 1
    fi
    
    if ! command_exists npm; then
        write_error "npm não encontrado. Por favor, instale o npm primeiro."
        exit 1
    fi
    
    write_success "Node.js e npm encontrados"
    
    # Verificar se playwright está instalado
    if ! npm list playwright --depth=0 >/dev/null 2>&1; then
        write_warning "Playwright não encontrado. Instalando..."
        npm install playwright axios
        
        write_info "Instalando navegadores do Playwright..."
        npx playwright install chromium
    fi
    
    write_success "Dependências verificadas"
}

# Função para iniciar serviços
start_services() {
    if [ "$SKIP_SERVICE_START" = true ]; then
        write_warning "Pulando inicialização de serviços (--skip-service-start)"
        return
    fi
    
    write_header "Verificando Serviços"
    
    # Verificar se frontend está rodando
    if ! test_service_running "$FRONTEND_URL"; then
        write_warning "Frontend não está rodando em $FRONTEND_URL"
        write_info "Tentando iniciar frontend..."
        
        # Tentar iniciar frontend em background
        local frontend_path="$(dirname "$0")/../frontend"
        if [ -d "$frontend_path" ]; then
            (
                cd "$frontend_path"
                npm run dev >/dev/null 2>&1 &
            )
            
            write_info "Aguardando frontend inicializar..."
            
            # Aguardar até 30 segundos para o frontend inicializar
            local attempts=0
            while [ $attempts -lt 30 ] && ! test_service_running "$FRONTEND_URL"; do
                sleep 1
                attempts=$((attempts + 1))
            done
            
            if test_service_running "$FRONTEND_URL"; then
                write_success "Frontend iniciado com sucesso"
            else
                write_warning "Frontend pode não ter iniciado completamente"
            fi
        fi
    else
        write_success "Frontend está rodando em $FRONTEND_URL"
    fi
    
    # Verificar se backend está rodando
    local backend_running=false
    local backend_urls=("http://localhost:5000/api/status" "http://localhost:5000/api/test")
    
    for url in "${backend_urls[@]}"; do
        if test_service_running "$url"; then
            write_success "Backend está rodando (testado via $url)"
            backend_running=true
            break
        fi
    done
    
    if [ "$backend_running" = false ]; then
        write_warning "Backend pode não estar rodando. A validação tentará usar dados de fallback."
    fi
}

# Função principal de validação
invoke_dashboard_validation() {
    write_header "Executando Validação E2E do Dashboard"
    
    # Definir variáveis de ambiente
    export FRONTEND_URL="$FRONTEND_URL"
    export HEADLESS="$(echo "$HEADLESS" | tr '[:upper:]' '[:lower:]')"
    export TIMEOUT="$((TIMEOUT * 1000))"  # Converter para ms
    
    # Caminho para o script de validação
    local validator_script="$(dirname "$0")/dashboard-e2e-validator.js"
    
    if [ ! -f "$validator_script" ]; then
        write_error "Script de validação não encontrado: $validator_script"
        exit 1
    fi
    
    write_info "Iniciando validação..."
    echo "Frontend URL: $FRONTEND_URL"
    echo "Headless: $HEADLESS"
    echo "Timeout: $TIMEOUT segundos"
    
    # Executar o validador
    if node "$validator_script"; then
        write_success "\nValidação concluída com sucesso!"
        
        # Procurar arquivos de evidência gerados
        local report_file
        local screenshot_file
        
        report_file=$(find . -name "dashboard_validation_report_*.json" -type f -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -1 | cut -d' ' -f2-)
        screenshot_file=$(find . -name "dashboard_*_*.png" -type f -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -1 | cut -d' ' -f2-)
        
        if [ -n "$report_file" ] && [ -f "$report_file" ]; then
            write_success "Relatório gerado: $report_file"
            
            # Mostrar resumo do relatório se jq estiver disponível
            if command_exists jq; then
                echo -e "\n${CYAN}Resumo da Validação:${NC}"
                local status
                status=$(jq -r '.status' "$report_file")
                
                if [ "$status" = "PASS" ]; then
                    echo -e "Status: ${GREEN}$status${NC}"
                else
                    echo -e "Status: ${RED}$status${NC}"
                fi
                
                local mismatches_count
                local notes_count
                mismatches_count=$(jq '.mismatches | length' "$report_file")
                notes_count=$(jq '.notes | length' "$report_file")
                
                echo "Mismatches: $mismatches_count"
                echo "Notas: $notes_count"
                
                if [ "$mismatches_count" -gt 0 ]; then
                    echo -e "\n${YELLOW}Mismatches encontrados:${NC}"
                    jq -r '.mismatches[] | "  - " + .field + ": " + .issue' "$report_file"
                fi
            else
                write_info "Instale 'jq' para ver o resumo detalhado do relatório"
            fi
        fi
        
        if [ -n "$screenshot_file" ] && [ -f "$screenshot_file" ]; then
            write_success "Screenshot capturado: $screenshot_file"
        fi
        
        return 0
    else
        write_error "Validação falhou"
        return 1
    fi
}

# Função para limpeza
invoke_cleanup() {
    write_header "Limpeza"
    
    # Remover variáveis de ambiente temporárias
    unset FRONTEND_URL HEADLESS TIMEOUT
    
    write_success "Limpeza concluída"
}

# Função para capturar sinais e fazer limpeza
cleanup_on_exit() {
    echo
    write_warning "Interrompido pelo usuário"
    invoke_cleanup
    exit 130
}

# Configurar trap para limpeza em caso de interrupção
trap cleanup_on_exit INT TERM

# Script principal
main() {
    write_header "Dashboard E2E Validation Runner"
    write_info "Iniciando validação end-to-end do dashboard GLPI..."
    
    # 1. Verificar e instalar dependências
    install_node_dependencies
    
    # 2. Iniciar serviços se necessário
    start_services
    
    # 3. Executar validação
    if invoke_dashboard_validation; then
        # 4. Limpeza
        invoke_cleanup
        
        # 5. Resultado final
        write_header "Validação Concluída com Sucesso"
        write_success "Todos os testes foram executados. Verifique os arquivos de evidência gerados."
        exit 0
    else
        # 4. Limpeza
        invoke_cleanup
        
        # 5. Resultado final
        write_header "Validação Falhou"
        write_error "A validação encontrou problemas. Verifique os logs e evidências."
        exit 1
    fi
}

# Executar função principal
main "$@"