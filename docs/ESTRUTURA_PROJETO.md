# 📁 Estrutura Organizada do Projeto

## 🎯 Organização Implementada

Este projeto agora segue uma estrutura organizada e padronizada:

```
glpi_dashboard/
  backend/              # Código do backend (Python/FastAPI)
  frontend/             # Código do frontend (React/TypeScript)
  scripts/              # Scripts de automação e ferramentas
     analysis/         # Scripts de análise e validação
     deployment/       # Scripts de deploy
     validation/       # Scripts de validação de qualidade
  docs/                 # Documentação do projeto
     assets/           # Imagens e recursos da documentação
    *.md                 # Arquivos de documentação
├── 📁 config/               # Arquivos de configuração
├── 📁 temp/                 # Arquivos temporários (ignorados no git)
├── 📁 tools/                # Ferramentas auxiliares
├── 📁 monitoring/           # Configurações de monitoramento
  .github/              # Configurações do GitHub (CI/CD)
```

##  Mudanças Realizadas

### Scripts Reorganizados
- `dashboard_analyzer.py`  `scripts/analysis/`
- `screenshot_validator.py`  `scripts/analysis/`
- `deploy.sh` → `scripts/deployment/`

### Documentação Organizada
- `TESTING_README.md` → `docs/`
- `dashboard_screenshot.png` → `docs/assets/`
- `dashboard_analysis.png`  `docs/assets/`

### Configurações Centralizadas
- `production.env` → `config/`
- `trae-context.yml` → `config/`

### Arquivos Temporários
- `recreate_locally_note.txt` → `temp/`
- `debug_technician_ranking.log` → `temp/`

## 📋 Diretrizes de Organização

### ✅ Onde Colocar Novos Arquivos

| Tipo de Arquivo | Diretório | Exemplo |
|----------------|-----------|----------|
| Scripts Python/Shell | `scripts/` | `scripts/backup.py` |
| Análise/Debug | `scripts/analysis/` | `scripts/analysis/performance.py` |
| Deploy/CI | `scripts/deployment/` | `scripts/deployment/staging.sh` |
| Documentação | `docs/` | `docs/API_GUIDE.md` |
| Imagens/Assets | `docs/assets/` | `docs/assets/architecture.png` |
| Configurações | `config/` | `config/staging.env` |
| Temporários | `temp/` | `temp/debug.log` |
| Ferramentas | `tools/` | `tools/data_migration/` |

###  Evitar na Raiz

- Scripts (.py, .sh, .ps1) - exceto `app.py` e `main.py`
- Arquivos de configuração específicos
- Imagens e assets
- Arquivos temporários ou de debug
- Logs e caches

###  Manutenção

1. **Novos scripts**: Sempre criar em `scripts/` com subdiretório apropriado
2. **Documentação**: Manter em `docs/` com assets em `docs/assets/`
3. **Configurações**: Centralizar em `config/`
4. **Temporários**: Usar `temp/` (ignorado no git)

## 🎯 Benefícios

-  **Navegação mais fácil**: Estrutura lógica e previsível
-  **Manutenção simplificada**: Arquivos organizados por função
-  **Colaboração melhorada**: Padrões claros para a equipe
- ✅ **CI/CD otimizado**: Caminhos organizados para automação
- ✅ **Documentação centralizada**: Fácil acesso à informação

---

*Estrutura implementada em $(Get-Date -Format "yyyy-MM-dd") como parte da metodologia de revisão em ciclos.*
