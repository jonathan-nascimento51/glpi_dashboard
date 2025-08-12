# 📋 Plano de Limpeza e Organização da Raiz do Projeto

## 🎯 Objetivo
Limpar e organizar a raiz do projeto seguindo a arquitetura definida em `docs/ESTRUTURA_PROJETO.md`.

## 📁 Análise da Situação Atual

### ✅ Arquivos que DEVEM permanecer na raiz:
- `.editorconfig` - Configuração do editor
- `.env.example` - Exemplo de variáveis de ambiente
- `.flake8` - Configuração do linter
- `.gitignore` - Configuração do Git
- `.gitleaks.toml` - Configuração de segurança
- `.isort.cfg` - Configuração de imports
- `.pre-commit-config.yaml` - Configuração de pre-commit
- `README.md` - Documentação principal
- `CHANGELOG.md` - Log de mudanças
- `CONTRIBUTING.md` - Guia de contribuição
- `SECURITY.md` - Política de segurança
- `Makefile` - Comandos de build
- `pyproject.toml` - Configuração Python
- `package.json` - Configuração Node.js
- `package-lock.json` - Lock de dependências Node.js
- `uv.lock` - Lock de dependências Python
- `app.py` - Ponto de entrada principal
- `run_scripts.py` - Script principal de execução

### 📂 Diretórios que DEVEM permanecer na raiz:
- `backend/` - Código do backend
- `frontend/` - Código do frontend
- `scripts/` - Scripts auxiliares
- `docs/` - Documentação
- `config/` - Configurações
- `tools/` - Ferramentas
- `monitoring/` - Monitoramento
- `.github/` - Configurações GitHub

### 🚨 Arquivos/Diretórios que PRECISAM ser movidos ou removidos:

#### Para `docs/`:
- `CI_README.md` → `docs/CI_README.md`
- `CI_SETUP.md` → `docs/CI_SETUP.md`
- `CONFIGURACAO_MOCK_DATA.md` → `docs/CONFIGURACAO_MOCK_DATA.md`
- `DEPENDENCIES.md` → `docs/DEPENDENCIES.md`
- `IMPLEMENTACAO_COMPLETA.md` → `docs/IMPLEMENTACAO_COMPLETA.md`
- `QUALITY_IMPLEMENTATION_PLAN.md` → `docs/QUALITY_IMPLEMENTATION_PLAN.md`
- `README-E2E-VALIDATOR.md` → `docs/README-E2E-VALIDATOR.md`
- `RECOVERY_LOG.md` → `docs/RECOVERY_LOG.md`

#### Para `config/`:
- `bandit.yaml` → `config/bandit.yaml`
- `codecov.yml` → `config/codecov.yml`
- `monitoring.yml` → `config/monitoring.yml`
- `openapi.json` → `config/openapi.json`

#### Para `scripts/`:
- `security.ps1` → `scripts/security/security.ps1`
- `proxy-server.js` → `scripts/development/proxy-server.js`
- `test_api_endpoints.js` → `scripts/testing/test_api_endpoints.js`
- `test_dashboard_data.js` → `scripts/testing/test_dashboard_data.js`

#### Para `temp/` (criar diretório):
- `git_history.txt` → `temp/git_history.txt`
- `network.har` → `temp/network.har`
- `e` (arquivo vazio) → remover

#### Para `artifacts/` (mover para `temp/artifacts/`):
- `artifacts/` → `temp/artifacts/`

#### Para `security_reports/` (mover para `temp/`):
- `security_reports/` → `temp/security_reports/`

#### Diretórios para análise/limpeza:
- `_kit_full/` - Verificar se é necessário ou mover para `temp/`
- `gadpi-robust-stack/` - Verificar se é necessário ou mover para `temp/`
- `.hypothesis/` - Cache de testes, pode ficar
- `.pytest_cache/` - Cache de testes, pode ficar
- `.ruff_cache/` - Cache do linter, pode ficar
- `.trae/` - Configuração da IDE, pode ficar

## 🔄 Plano de Execução

### Fase 1: Criar diretórios necessários
1. Criar `temp/` se não existir
2. Criar `scripts/security/` se não existir
3. Criar `scripts/development/` se não existir
4. Criar `scripts/testing/` se não existir

### Fase 2: Mover documentação
1. Mover arquivos `.md` específicos para `docs/`

### Fase 3: Mover configurações
1. Mover arquivos de configuração para `config/`

### Fase 4: Mover scripts
1. Mover scripts para subdiretórios apropriados em `scripts/`

### Fase 5: Mover arquivos temporários
1. Mover arquivos temporários e de debug para `temp/`

### Fase 6: Limpeza final
1. Remover arquivos desnecessários
2. Verificar diretórios vazios
3. Atualizar `.gitignore` se necessário

## 📝 Notas Importantes

- Fazer backup antes de mover arquivos importantes
- Verificar se há referências a caminhos nos arquivos antes de mover
- Atualizar documentação após reorganização
- Testar funcionamento após reorganização

---
*Plano criado em $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")*