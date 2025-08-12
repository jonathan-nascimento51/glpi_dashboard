.PHONY: help install dev-install lint format test test-cov clean run docker-build docker-up docker-down

# Variáveis
PYTHON := python
PIP := pip
PYTEST := pytest
RUFF := ruff
BLACK := black
ISORT := isort

# Ajuda
help:
@echo "Comandos disponíveis:"
@echo "  install      - Instalar dependências de produção"
@echo "  dev-install  - Instalar dependências de desenvolvimento"
@echo "  lint         - Executar linting (ruff)"
@echo "  format       - Formatar código (black + isort)"
@echo "  test         - Executar testes"
@echo "  test-cov     - Executar testes com cobertura"
@echo "  clean        - Limpar arquivos temporários"
@echo "  run          - Executar aplicação"
@echo "  docker-build - Build da imagem Docker"
@echo "  docker-up    - Subir containers"
@echo "  docker-down  - Parar containers"

# Instalação
install:
$(PIP) install -r requirements.txt

dev-install:
$(PIP) install -r requirements-dev.txt
$(PIP) install -e .

# Qualidade de código
lint:
$(RUFF) check .
$(RUFF) format --check .

format:
$(BLACK) --line-length 100 .
$(ISORT) .
$(RUFF) format .

# Testes
test:
$(PYTEST) -v

test-cov:
$(PYTEST) --cov=app --cov-report=html --cov-report=term-missing

# Limpeza
clean:
@echo "Limpando arquivos temporários..."
@if exist __pycache__ rmdir /s /q __pycache__
@if exist .pytest_cache rmdir /s /q .pytest_cache
@if exist htmlcov rmdir /s /q htmlcov
@if exist .coverage del .coverage
@for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
@for /r . %%f in (*.pyc) do @if exist "%%f" del "%%f"

# Execução
run:
$(PYTHON) main.py

# Docker
docker-build:
docker build -t glpi-dashboard-backend .

docker-up:
docker-compose up -d

docker-down:
docker-compose down

# Verificação completa
check: lint test
@echo "Verificação completa finalizada!"

# Setup completo para desenvolvimento
setup: dev-install
@echo "Setup de desenvolvimento concluído!"
@echo "Execute 'make help' para ver os comandos disponíveis."
