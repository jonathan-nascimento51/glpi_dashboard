# CI/CD Pipeline - GLPI Dashboard

Este documento descreve a configuração e uso do pipeline de Integração Contínua (CI) para o projeto GLPI Dashboard.

## 📋 Visão Geral

O pipeline CI está configurado com GitHub Actions e inclui:

- ✅ **Testes Backend**: Python com pytest
- ✅ **Testes Frontend**: TypeScript/React com Vitest
- ✅ **Linting**: flake8, isort, black (Python) + ESLint, Prettier (TypeScript)
- ✅ **Análise de Segurança**: Bandit, Safety
- ✅ **Relatórios de Cobertura**: Coverage.py (backend) + Vitest (frontend)
- ✅ **Testes de Integração**: Com Redis
- ✅ **Deploy Automático**: Para branch main

## 🚀 Estrutura do Pipeline

### Jobs Principais

1. **backend-tests**: Testa o código Python
2. **frontend-tests**: Testa o código TypeScript/React
3. **integration-tests**: Testa a integração entre componentes
4. **security-scan**: Análise de segurança
5. **code-quality**: Análise de qualidade (SonarCloud)
6. **build-and-deploy**: Build e deploy (apenas main)
7. **notify**: Notificações de resultado

### Triggers

- **Push**: branches `main` e `develop`
- **Pull Request**: para branches `main` e `develop`

## 🛠️ Configuração Local

### Backend (Python)

```bash
# Instalar dependências de desenvolvimento
pip install flake8 black isort pytest pytest-cov bandit safety

# Executar linting
flake8 backend/
isort --check-only --diff backend/
black --check --diff backend/

# Executar testes com cobertura
cd backend
pytest --cov=. --cov-report=html --cov-report=term-missing

# Análise de segurança
bandit -r backend/
safety check -r requirements.txt
```

### Frontend (TypeScript/React)

```bash
# Instalar dependências
cd frontend
npm install

# Executar linting e formatação
npm run lint
npm run format:check
npm run type-check

# Executar testes com cobertura
npm test

# Build para produção
npm run build
```

## 📊 Relatórios de Cobertura

### Backend (Python)

O pipeline gera relatórios de cobertura em múltiplos formatos:

```bash
# Executar testes com cobertura
pytest --cov=. --cov-report=xml --cov-report=html --cov-report=term-missing

# Arquivos gerados:
# - coverage.xml (para Codecov)
# - htmlcov/ (relatório HTML)
# - Terminal output com linhas não cobertas
```

**Configuração de Cobertura** (pyproject.toml):
- Fonte: `backend/`
- Exclusões: testes, migrações, venv
- Meta: >80% de cobertura
- Relatório HTML em `htmlcov/`

### Frontend (TypeScript/React)

```bash
# Executar testes com cobertura
npm test -- --coverage

# Arquivos gerados:
# - coverage/lcov.info (para Codecov)
# - coverage/ (relatório HTML)
```

**Configuração de Cobertura** (vitest.config.ts):
- Cobertura com V8
- Formatos: text, json, html, lcov
- Exclusões: node_modules, dist, tests

## 🔧 Configurações de Ferramentas

### Python Tools

**flake8** (`.flake8`):
- Max line length: 127
- Max complexity: 10
- Ignora E203, E501, W503, W504

**black** (pyproject.toml):
- Line length: 127
- Target: Python 3.11

**isort** (pyproject.toml):
- Profile: black
- Line length: 127
- Known first party: backend, config, utils, services, models, tests

### TypeScript/React Tools

**ESLint**:
- TypeScript parser
- React hooks plugin
- Max warnings: 0

**Prettier** (`.prettierrc`):
- Single quotes
- Semicolons
- Print width: 100
- Tab width: 2

## 🔐 Secrets Necessários

Para funcionalidade completa, configure estes secrets no GitHub:

```yaml
# Obrigatórios para testes de integração
GLPI_URL: "https://seu-glpi.com/apirest.php"
GLPI_APP_TOKEN: "seu_app_token"
GLPI_USER_TOKEN: "seu_user_token"

# Opcionais para análise de qualidade
SONAR_TOKEN: "seu_sonar_token"  # Para SonarCloud
CODECOV_TOKEN: "seu_codecov_token"  # Para Codecov (opcional)
```

## 📈 Monitoramento e Métricas

### Codecov Integration

- Upload automático de relatórios de cobertura
- Comentários em PRs com mudanças de cobertura
- Dashboards de tendências

### SonarCloud Integration

- Análise de qualidade de código
- Detecção de code smells
- Análise de segurança
- Métricas de maintainability

### Artifacts

O pipeline salva os seguintes artifacts:

- **backend-coverage-html**: Relatório HTML de cobertura do backend
- **frontend-coverage-html**: Relatório HTML de cobertura do frontend
- **security-reports**: Relatórios de segurança (Bandit)
- **deployment-package**: Pacote de deploy (apenas main)

## 🚨 Troubleshooting

### Falhas Comuns

1. **Testes falhando**:
   ```bash
   # Executar localmente primeiro
   pytest backend/tests/ -v
   npm test
   ```

2. **Linting errors**:
   ```bash
   # Corrigir automaticamente
   black backend/
   isort backend/
   npm run lint:fix
   npm run format
   ```

3. **Cobertura baixa**:
   ```bash
   # Verificar linhas não cobertas
   pytest --cov=. --cov-report=term-missing
   ```

4. **Dependências desatualizadas**:
   ```bash
   # Backend
   pip list --outdated
   
   # Frontend
   npm outdated
   ```

### Debug do Pipeline

1. Verificar logs detalhados no GitHub Actions
2. Executar comandos localmente antes do push
3. Usar `act` para testar GitHub Actions localmente:
   ```bash
   # Instalar act
   # https://github.com/nektos/act
   
   # Executar pipeline localmente
   act push
   ```

## 📝 Contribuindo

### Pre-commit Hooks (Recomendado)

```bash
# Instalar pre-commit
pip install pre-commit

# Configurar hooks
pre-commit install

# Executar em todos os arquivos
pre-commit run --all-files
```

### Workflow para Contribuições

1. Criar branch feature: `git checkout -b feature/nova-funcionalidade`
2. Fazer alterações e commits
3. Executar testes localmente: `pytest && npm test`
4. Executar linting: `flake8 && npm run lint`
5. Push e criar Pull Request
6. Aguardar CI passar
7. Review e merge

## 🔄 Atualizações do Pipeline

Para modificar o pipeline:

1. Editar `.github/workflows/ci.yml`
2. Testar localmente com `act`
3. Fazer commit e push
4. Verificar execução no GitHub Actions

### Versionamento

- Actions: Usar versões específicas (ex: `@v4`)
- Dependencies: Manter atualizadas
- Python/Node: Versões LTS recomendadas

---

**Documentação atualizada em**: $(date)
**Versão do Pipeline**: 1.0.0