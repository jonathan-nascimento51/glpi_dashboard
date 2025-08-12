# GLPI Dashboard - Makefile
# Comandos para desenvolvimento e seguran�a

.PHONY: help install dev test lint security security-quick clean docker-build docker-up docker-down health validate ci pre-commit

# Configura��es
PYTHON := python
PIP := pip
BACKEND_DIR := backend
FRONTEND_DIR := frontend
SCRIPTS_DIR := scripts

help: ## Mostra esta ajuda
\t@echo "GLPI Dashboard - Comandos Dispon�veis"
\t@echo "====================================="
\t@echo "install          Instala todas as depend�ncias"
\t@echo "dev              Inicia ambiente de desenvolvimento"
\t@echo "test             Executa todos os testes"
\t@echo "test-coverage    Executa testes com cobertura"
\t@echo "lint             Executa linting (ruff + black + isort)"
\t@echo "security         Executa verifica��o completa de seguran�a"
\t@echo "security-quick   Executa verifica��o r�pida de seguran�a"
\t@echo "security-bandit  Executa an�lise Bandit"
\t@echo "security-safety  Executa verifica��o Safety"
\t@echo "security-gitleaks Executa detec��o GitLeaks"
\t@echo "security-semgrep Executa an�lise Semgrep"
\t@echo "pre-commit       Executa hooks de pre-commit"
\t@echo "validate         Executa lint + test + security-quick"
\t@echo "ci               Pipeline completa de CI"
\t@echo "clean            Remove arquivos tempor�rios"
\t@echo "docker-build     Constr�i imagens Docker"
\t@echo "docker-up        Inicia servi�os Docker"
\t@echo "docker-down      Para servi�os Docker"
\t@echo "health           Verifica sa�de dos servi�os"

install: ## Instala todas as depend�ncias
\t@echo "Instalando depend�ncias..."
cd $(BACKEND_DIR) && $(PIP) install -r requirements.txt
\t@echo "Depend�ncias instaladas com sucesso!"

install-dev: ## Instala depend�ncias de desenvolvimento
\t@echo "Instalando depend�ncias de desenvolvimento..."
cd $(BACKEND_DIR) && $(PIP) install -r requirements-dev.txt
\t\$\(PIP) install pre-commit bandit safety semgrep
\tpre-commit install
\t@echo "Depend�ncias de desenvolvimento instaladas!"

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
\t@echo "Linting conclu�do!"

security: ## Executa verifica��o completa de seguran�a
\t@echo "Executando verifica��o completa de seguran�a..."
\t\$\(PYTHON) $(SCRIPTS_DIR)/security_check.py
\t@echo "Verifica��o de seguran�a conclu�da!"

security-quick: ## Executa verifica��o r�pida de seguran�a
\t@echo "Executando verifica��o r�pida de seguran�a..."
\t\$\(PYTHON) $(SCRIPTS_DIR)/security_check.py --quick
\t@echo "Verifica��o r�pida conclu�da!"

security-bandit: ## Executa an�lise Bandit
\t@echo "Executando an�lise Bandit..."
\tmkdir -p security_reports
bandit -r $(BACKEND_DIR) -f json -o security_reports/bandit_report.json -c bandit.yaml
\t@echo "An�lise Bandit conclu�da!"

security-safety: ## Executa verifica��o Safety
\t@echo "Executando verifica��o Safety..."
\tmkdir -p security_reports
safety check --json --output security_reports/safety_report.json
\t@echo "Verifica��o Safety conclu�da!"

security-gitleaks: ## Executa detec��o GitLeaks
\t@echo "Executando detec��o GitLeaks..."
\tmkdir -p security_reports
\tgitleaks detect --config .gitleaks.toml --report-format json --report-path security_reports/gitleaks_report.json
\t@echo "Detec��o GitLeaks conclu�da!"

security-semgrep: ## Executa an�lise Semgrep
\t@echo "Executando an�lise Semgrep..."
\tmkdir -p security_reports
\tsemgrep --config=auto --json --output=security_reports/semgrep_report.json $(BACKEND_DIR)
\t@echo "An�lise Semgrep conclu�da!"

\tpre-commit: ## Executa hooks de pre-commit
\t@echo "Executando hooks de pre-commit..."
\tpre-commit run --all-files
\t@echo "Pre-commit hooks executados!"

validate: ## Executa lint + test + security-quick
\t@echo "Executando valida��o completa..."
\t\$\(MAKE) lint
\t\$\(MAKE) test
\t\$\(MAKE) security-quick
\t@echo "Valida��o conclu�da com sucesso!"

ci: ## Pipeline completa de CI
\t@echo "Executando pipeline de CI..."
\t\$\(MAKE) install-dev
\t\$\(MAKE) lint
\t\$\(MAKE) test-coverage
\t\$\(MAKE) security
\t@echo "Pipeline de CI conclu�da!"

clean: ## Remove arquivos tempor�rios
\t@echo "Removendo arquivos tempor�rios..."
\tfind . -type f -name "*.pyc" -delete
\tfind . -type d -name "__pycache__" -delete
\tfind . -type d -name ".pytest_cache" -delete
\trm -rf .coverage htmlcov/
\trm -rf security_reports/
\t@echo "Limpeza conclu�da!"

\tdocker-build: ## Constr�i imagens Docker
\t@echo "Construindo imagens Docker..."
\tdocker-compose build
\t@echo "Imagens constru�das!"

\tdocker-up: ## Inicia servi�os Docker
\t@echo "Iniciando servi�os Docker..."
\tdocker-compose up -d
\t@echo "Servi�os iniciados!"

\tdocker-down: ## Para servi�os Docker
\t@echo "Parando servi�os Docker..."
\tdocker-compose down
\t@echo "Servi�os parados!"

health: ## Verifica sa�de dos servi�os
\t@echo "Verificando sa�de dos servi�os..."
\t\$\(PYTHON) -c "import requests; print(\"API:\", requests.get(\"http://localhost:8000/health\").status_code)"
\t@echo "Verifica��o de sa�de conclu�da!"
