# GLPI Dashboard - Makefile
# Comandos para desenvolvimento e segurança

.PHONY: help install dev test lint security security-quick clean docker-build docker-up docker-down health validate ci pre-commit

# Configurações
PYTHON := python
PIP := pip
BACKEND_DIR := backend
FRONTEND_DIR := frontend
SCRIPTS_DIR := scripts

help: ## Mostra esta ajuda
\t@echo "GLPI Dashboard - Comandos Disponíveis"
\t@echo "====================================="
\t@echo "install          Instala todas as dependências"
\t@echo "dev              Inicia ambiente de desenvolvimento"
\t@echo "test             Executa todos os testes"
\t@echo "test-coverage    Executa testes com cobertura"
\t@echo "lint             Executa linting (ruff + black + isort)"
\t@echo "security         Executa verificação completa de segurança"
\t@echo "security-quick   Executa verificação rápida de segurança"
\t@echo "security-bandit  Executa análise Bandit"
\t@echo "security-safety  Executa verificação Safety"
\t@echo "security-gitleaks Executa detecção GitLeaks"
\t@echo "security-semgrep Executa análise Semgrep"
\t@echo "pre-commit       Executa hooks de pre-commit"
\t@echo "validate         Executa lint + test + security-quick"
\t@echo "ci               Pipeline completa de CI"
\t@echo "clean            Remove arquivos temporários"
\t@echo "docker-build     Constrói imagens Docker"
\t@echo "docker-up        Inicia serviços Docker"
\t@echo "docker-down      Para serviços Docker"
\t@echo "health           Verifica saúde dos serviços"

install: ## Instala todas as dependências
\t@echo "Instalando dependências..."
cd $(BACKEND_DIR) && $(PIP) install -r requirements.txt
\t@echo "Dependências instaladas com sucesso!"

install-dev: ## Instala dependências de desenvolvimento
\t@echo "Instalando dependências de desenvolvimento..."
cd $(BACKEND_DIR) && $(PIP) install -r requirements-dev.txt
\t\$\(PIP) install pre-commit bandit safety semgrep
\tpre-commit install
\t@echo "Dependências de desenvolvimento instaladas!"

dev: ## Inicia ambiente de desenvolvimento
\t@echo "Iniciando ambiente de desenvolvimento..."
cd $(BACKEND_DIR) && $(PYTHON) -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

test: ## Executa todos os testes
\t@echo "Executando testes..."
cd $(BACKEND_DIR) && $(PYTHON) -m pytest tests/ -v

test-coverage: ## Executa testes com cobertura
\t@echo "Executando testes com cobertura..."
cd $(BACKEND_DIR) && $(PYTHON) -m pytest tests/ --cov=. --cov-report=html --cov-report=term

lint: ## Executa linting (ruff + black + isort)
\t@echo "Executando linting..."
cd $(BACKEND_DIR) && ruff check . --fix
cd $(BACKEND_DIR) && black . --line-length 100
cd $(BACKEND_DIR) && isort . --profile black
\t@echo "Linting concluído!"

security: ## Executa verificação completa de segurança
\t@echo "Executando verificação completa de segurança..."
\t\$\(PYTHON) $(SCRIPTS_DIR)/security_check.py
\t@echo "Verificação de segurança concluída!"

security-quick: ## Executa verificação rápida de segurança
\t@echo "Executando verificação rápida de segurança..."
\t\$\(PYTHON) $(SCRIPTS_DIR)/security_check.py --quick
\t@echo "Verificação rápida concluída!"

security-bandit: ## Executa análise Bandit
\t@echo "Executando análise Bandit..."
\tmkdir -p security_reports
bandit -r $(BACKEND_DIR) -f json -o security_reports/bandit_report.json -c bandit.yaml
\t@echo "Análise Bandit concluída!"

security-safety: ## Executa verificação Safety
\t@echo "Executando verificação Safety..."
\tmkdir -p security_reports
safety check --json --output security_reports/safety_report.json
\t@echo "Verificação Safety concluída!"

security-gitleaks: ## Executa detecção GitLeaks
\t@echo "Executando detecção GitLeaks..."
\tmkdir -p security_reports
\tgitleaks detect --config .gitleaks.toml --report-format json --report-path security_reports/gitleaks_report.json
\t@echo "Detecção GitLeaks concluída!"

security-semgrep: ## Executa análise Semgrep
\t@echo "Executando análise Semgrep..."
\tmkdir -p security_reports
\tsemgrep --config=auto --json --output=security_reports/semgrep_report.json $(BACKEND_DIR)
\t@echo "Análise Semgrep concluída!"

\tpre-commit: ## Executa hooks de pre-commit
\t@echo "Executando hooks de pre-commit..."
\tpre-commit run --all-files
\t@echo "Pre-commit hooks executados!"

validate: ## Executa lint + test + security-quick
\t@echo "Executando validação completa..."
\t\$\(MAKE) lint
\t\$\(MAKE) test
\t\$\(MAKE) security-quick
\t@echo "Validação concluída com sucesso!"

ci: ## Pipeline completa de CI
\t@echo "Executando pipeline de CI..."
\t\$\(MAKE) install-dev
\t\$\(MAKE) lint
\t\$\(MAKE) test-coverage
\t\$\(MAKE) security
\t@echo "Pipeline de CI concluída!"

clean: ## Remove arquivos temporários
\t@echo "Removendo arquivos temporários..."
\tfind . -type f -name "*.pyc" -delete
\tfind . -type d -name "__pycache__" -delete
\tfind . -type d -name ".pytest_cache" -delete
\trm -rf .coverage htmlcov/
\trm -rf security_reports/
\t@echo "Limpeza concluída!"

\tdocker-build: ## Constrói imagens Docker
\t@echo "Construindo imagens Docker..."
\tdocker-compose build
\t@echo "Imagens construídas!"

\tdocker-up: ## Inicia serviços Docker
\t@echo "Iniciando serviços Docker..."
\tdocker-compose up -d
\t@echo "Serviços iniciados!"

\tdocker-down: ## Para serviços Docker
\t@echo "Parando serviços Docker..."
\tdocker-compose down
\t@echo "Serviços parados!"

health: ## Verifica saúde dos serviços
\t@echo "Verificando saúde dos serviços..."
\t\$\(PYTHON) -c "import requests; print(\"API:\", requests.get(\"http://localhost:8000/health\").status_code)"
\t@echo "Verificação de saúde concluída!"
