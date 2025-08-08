# GLPI Dashboard - Makefile
# Automatização de tarefas de desenvolvimento

.PHONY: help install install-dev test test-backend test-frontend lint lint-backend lint-frontend format format-backend format-frontend clean build run dev stop logs docker-build docker-up docker-down security audit coverage pre-commit setup-hooks release

# Configurações
PYTHON := python
PIP := pip
NPM := npm
DOCKER := docker
DOCKER_COMPOSE := docker-compose

# Cores para output
RED := \033[31m
GREEN := \033[32m
YELLOW := \033[33m
BLUE := \033[34m
MAGENTA := \033[35m
CYAN := \033[36m
WHITE := \033[37m
RESET := \033[0m

# Help
help: ## Mostra esta mensagem de ajuda
	@echo "$(CYAN)GLPI Dashboard - Comandos Disponíveis$(RESET)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Exemplos de uso:$(RESET)"
	@echo "  make install     # Instala todas as dependências"
	@echo "  make test        # Executa todos os testes"
	@echo "  make dev         # Inicia ambiente de desenvolvimento"
	@echo "  make lint        # Executa linting em todo o código"

# Instalação
install: ## Instala dependências de produção
	@echo "$(BLUE)Instalando dependências...$(RESET)"
	cd backend && $(PIP) install -r requirements.txt
	cd frontend && $(NPM) install --production
	@echo "$(GREEN)✓ Dependências instaladas$(RESET)"

install-dev: ## Instala dependências de desenvolvimento
	@echo "$(BLUE)Instalando dependências de desenvolvimento...$(RESET)"
	cd backend && $(PIP) install -r requirements-dev.txt
	cd frontend && $(NPM) install
	$(PIP) install pre-commit commitizen
	@echo "$(GREEN)✓ Dependências de desenvolvimento instaladas$(RESET)"

setup-hooks: ## Configura git hooks
	@echo "$(BLUE)Configurando git hooks...$(RESET)"
	pre-commit install
	pre-commit install --hook-type commit-msg
	@echo "$(GREEN)✓ Git hooks configurados$(RESET)"

# Testes
test: test-backend test-frontend ## Executa todos os testes

test-backend: ## Executa testes do backend
	@echo "$(BLUE)Executando testes do backend...$(RESET)"
	cd backend && $(PYTHON) -m pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing
	@echo "$(GREEN)✓ Testes do backend concluídos$(RESET)"

test-frontend: ## Executa testes do frontend
	@echo "$(BLUE)Executando testes do frontend...$(RESET)"
	cd frontend && $(NPM) test -- --coverage --watchAll=false
	@echo "$(GREEN)✓ Testes do frontend concluídos$(RESET)"

test-unit: ## Executa apenas testes unitários
	@echo "$(BLUE)Executando testes unitários...$(RESET)"
	cd backend && $(PYTHON) -m pytest tests/unit/ -v
	cd frontend && $(NPM) test -- --testPathPattern=".*\.test\.(ts|tsx)$$" --watchAll=false

test-integration: ## Executa apenas testes de integração
	@echo "$(BLUE)Executando testes de integração...$(RESET)"
	cd backend && $(PYTHON) -m pytest tests/integration/ -v

test-e2e: ## Executa testes end-to-end
	@echo "$(BLUE)Executando testes E2E...$(RESET)"
	cd frontend && $(NPM) run test:e2e

test-regression: ## Executa testes de regressão
	@echo "$(BLUE)Executando testes de regressão...$(RESET)"
	cd backend && $(PYTHON) -m pytest tests/ -m regression -v

test-performance: ## Executa testes de performance
	@echo "$(BLUE)Executando testes de performance...$(RESET)"
	cd backend && $(PYTHON) -m pytest tests/ -m performance -v

# Linting e Formatação
lint: lint-backend lint-frontend ## Executa linting em todo o código

lint-backend: ## Executa linting no backend
	@echo "$(BLUE)Executando linting no backend...$(RESET)"
	cd backend && flake8 .
	cd backend && black --check .
	cd backend && isort --check-only .
	cd backend && mypy .
	@echo "$(GREEN)✓ Linting do backend concluído$(RESET)"

lint-frontend: ## Executa linting no frontend
	@echo "$(BLUE)Executando linting no frontend...$(RESET)"
	cd frontend && $(NPM) run lint
	cd frontend && $(NPM) run type-check
	@echo "$(GREEN)✓ Linting do frontend concluído$(RESET)"

format: format-backend format-frontend ## Formata todo o código

format-backend: ## Formata código do backend
	@echo "$(BLUE)Formatando código do backend...$(RESET)"
	cd backend && black .
	cd backend && isort .
	@echo "$(GREEN)✓ Código do backend formatado$(RESET)"

format-frontend: ## Formata código do frontend
	@echo "$(BLUE)Formatando código do frontend...$(RESET)"
	cd frontend && $(NPM) run format
	@echo "$(GREEN)✓ Código do frontend formatado$(RESET)"

# Segurança
security: ## Executa verificações de segurança
	@echo "$(BLUE)Executando verificações de segurança...$(RESET)"
	cd backend && bandit -r . -f json -o bandit-report.json || true
	cd frontend && $(NPM) audit --audit-level=moderate
	trivy fs . --format table
	@echo "$(GREEN)✓ Verificações de segurança concluídas$(RESET)"

audit: ## Auditoria de dependências
	@echo "$(BLUE)Executando auditoria de dependências...$(RESET)"
	cd backend && safety check
	cd frontend && $(NPM) audit
	@echo "$(GREEN)✓ Auditoria concluída$(RESET)"

# Cobertura
coverage: ## Gera relatório de cobertura
	@echo "$(BLUE)Gerando relatório de cobertura...$(RESET)"
	cd backend && $(PYTHON) -m pytest tests/ --cov=. --cov-report=html --cov-report=xml
	cd frontend && $(NPM) test -- --coverage --watchAll=false
	@echo "$(GREEN)✓ Relatório de cobertura gerado$(RESET)"
	@echo "$(YELLOW)Backend: file://$(PWD)/backend/htmlcov/index.html$(RESET)"
	@echo "$(YELLOW)Frontend: file://$(PWD)/frontend/coverage/lcov-report/index.html$(RESET)"

# Desenvolvimento
dev: ## Inicia ambiente de desenvolvimento
	@echo "$(BLUE)Iniciando ambiente de desenvolvimento...$(RESET)"
	@echo "$(YELLOW)Backend: http://localhost:8000$(RESET)"
	@echo "$(YELLOW)Frontend: http://localhost:3000$(RESET)"
	@echo "$(MAGENTA)Pressione Ctrl+C para parar$(RESET)"
	$(MAKE) -j2 dev-backend dev-frontend

dev-backend: ## Inicia apenas o backend
	@echo "$(BLUE)Iniciando backend...$(RESET)"
	cd backend && $(PYTHON) -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Inicia apenas o frontend
	@echo "$(BLUE)Iniciando frontend...$(RESET)"
	cd frontend && $(NPM) run dev

run: ## Executa aplicação em modo produção
	@echo "$(BLUE)Executando aplicação...$(RESET)"
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✓ Aplicação executando$(RESET)"
	@echo "$(YELLOW)Acesse: http://localhost:3000$(RESET)"

stop: ## Para a aplicação
	@echo "$(BLUE)Parando aplicação...$(RESET)"
	$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✓ Aplicação parada$(RESET)"

logs: ## Mostra logs da aplicação
	$(DOCKER_COMPOSE) logs -f

# Docker
docker-build: ## Constrói imagens Docker
	@echo "$(BLUE)Construindo imagens Docker...$(RESET)"
	$(DOCKER_COMPOSE) build
	@echo "$(GREEN)✓ Imagens construídas$(RESET)"

docker-up: ## Inicia containers Docker
	@echo "$(BLUE)Iniciando containers...$(RESET)"
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✓ Containers iniciados$(RESET)"

docker-down: ## Para containers Docker
	@echo "$(BLUE)Parando containers...$(RESET)"
	$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✓ Containers parados$(RESET)"

docker-clean: ## Remove containers, volumes e imagens
	@echo "$(BLUE)Limpando Docker...$(RESET)"
	$(DOCKER_COMPOSE) down -v --rmi all
	$(DOCKER) system prune -f
	@echo "$(GREEN)✓ Docker limpo$(RESET)"

# Build
build: ## Constrói aplicação para produção
	@echo "$(BLUE)Construindo aplicação...$(RESET)"
	cd frontend && $(NPM) run build
	@echo "$(GREEN)✓ Build concluído$(RESET)"

# Limpeza
clean: ## Remove arquivos temporários e cache
	@echo "$(BLUE)Limpando arquivos temporários...$(RESET)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type f -name ".coverage" -delete
	rm -rf backend/htmlcov/
	rm -rf frontend/coverage/
	rm -rf frontend/dist/
	rm -rf frontend/node_modules/.cache/
	@echo "$(GREEN)✓ Limpeza concluída$(RESET)"

clean-all: clean ## Remove todas as dependências e cache
	@echo "$(BLUE)Removendo todas as dependências...$(RESET)"
	rm -rf frontend/node_modules/
	rm -rf backend/.venv/
	@echo "$(GREEN)✓ Limpeza completa concluída$(RESET)"

# Versionamento
release: ## Cria uma nova release
	@echo "$(BLUE)Criando nova release...$(RESET)"
	cz bump --changelog
	git push
	git push --tags
	@echo "$(GREEN)✓ Release criada$(RESET)"

changelog: ## Gera changelog
	@echo "$(BLUE)Gerando changelog...$(RESET)"
	cz changelog
	@echo "$(GREEN)✓ Changelog gerado$(RESET)"

# Pre-commit
pre-commit: ## Executa pre-commit em todos os arquivos
	@echo "$(BLUE)Executando pre-commit...$(RESET)"
	pre-commit run --all-files
	@echo "$(GREEN)✓ Pre-commit concluído$(RESET)"

# Validações
validate: lint test security ## Executa todas as validações
	@echo "$(GREEN)✓ Todas as validações passaram$(RESET)"

validate-env: ## Valida variáveis de ambiente
	@echo "$(BLUE)Validando variáveis de ambiente...$(RESET)"
	$(PYTHON) scripts/validate_env_vars.py
	@echo "$(GREEN)✓ Variáveis de ambiente validadas$(RESET)"

# Banco de dados
db-migrate: ## Executa migrações do banco
	@echo "$(BLUE)Executando migrações...$(RESET)"
	cd backend && alembic upgrade head
	@echo "$(GREEN)✓ Migrações executadas$(RESET)"

db-reset: ## Reseta banco de dados
	@echo "$(BLUE)Resetando banco de dados...$(RESET)"
	cd backend && alembic downgrade base
	cd backend && alembic upgrade head
	@echo "$(GREEN)✓ Banco resetado$(RESET)"

# Documentação
docs: ## Gera documentação
	@echo "$(BLUE)Gerando documentação...$(RESET)"
	cd backend && $(PYTHON) -m pydoc -w .
	cd frontend && $(NPM) run docs
	@echo "$(GREEN)✓ Documentação gerada$(RESET)"

docs-serve: ## Serve documentação localmente
	@echo "$(BLUE)Servindo documentação...$(RESET)"
	@echo "$(YELLOW)Documentação: http://localhost:8080$(RESET)"
	$(PYTHON) -m http.server 8080 -d docs/

# Monitoramento
health: ## Verifica saúde da aplicação
	@echo "$(BLUE)Verificando saúde da aplicação...$(RESET)"
	curl -f http://localhost:8000/health || echo "$(RED)Backend não está respondendo$(RESET)"
	curl -f http://localhost:3000 || echo "$(RED)Frontend não está respondendo$(RESET)"
	@echo "$(GREEN)✓ Verificação de saúde concluída$(RESET)"

status: ## Mostra status dos serviços
	@echo "$(BLUE)Status dos serviços:$(RESET)"
	$(DOCKER_COMPOSE) ps

# Backup
backup: ## Cria backup do banco de dados
	@echo "$(BLUE)Criando backup...$(RESET)"
	mkdir -p backups
	$(DOCKER_COMPOSE) exec -T postgres pg_dump -U postgres glpi_dashboard > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✓ Backup criado$(RESET)"

restore: ## Restaura backup do banco (uso: make restore BACKUP=arquivo.sql)
	@echo "$(BLUE)Restaurando backup...$(RESET)"
	$(DOCKER_COMPOSE) exec -T postgres psql -U postgres -d glpi_dashboard < $(BACKUP)
	@echo "$(GREEN)✓ Backup restaurado$(RESET)"

# Utilitários
shell-backend: ## Abre shell no container do backend
	$(DOCKER_COMPOSE) exec backend bash

shell-frontend: ## Abre shell no container do frontend
	$(DOCKER_COMPOSE) exec frontend sh

shell-db: ## Abre shell no banco de dados
	$(DOCKER_COMPOSE) exec postgres psql -U postgres -d glpi_dashboard

# Setup inicial
setup: install-dev setup-hooks ## Configuração inicial do projeto
	@echo "$(GREEN)✓ Projeto configurado com sucesso!$(RESET)"
	@echo "$(YELLOW)Próximos passos:$(RESET)"
	@echo "  1. Configure as variáveis de ambiente (.env)"
	@echo "  2. Execute 'make dev' para iniciar o desenvolvimento"
	@echo "  3. Execute 'make test' para verificar se tudo está funcionando"

# Informações
info: ## Mostra informações do projeto
	@echo "$(CYAN)GLPI Dashboard - Informações do Projeto$(RESET)"
	@echo "$(YELLOW)Versão:$(RESET) $(shell cat VERSION)"
	@echo "$(YELLOW)Python:$(RESET) $(shell $(PYTHON) --version)"
	@echo "$(YELLOW)Node.js:$(RESET) $(shell node --version)"
	@echo "$(YELLOW)NPM:$(RESET) $(shell $(NPM) --version)"
	@echo "$(YELLOW)Docker:$(RESET) $(shell $(DOCKER) --version)"
	@echo "$(YELLOW)Git:$(RESET) $(shell git --version)"
	@echo ""
	@echo "$(YELLOW)Estrutura do Projeto:$(RESET)"
	@echo "  backend/     - API Python (FastAPI)"
	@echo "  frontend/    - Interface React (TypeScript)"
	@echo "  docs/        - Documentação"
	@echo "  scripts/     - Scripts utilitários"
	@echo "  tests/       - Testes automatizados"

# Default target
.DEFAULT_GOAL := help