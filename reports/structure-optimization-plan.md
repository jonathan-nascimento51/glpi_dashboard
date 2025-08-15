# Plano de Otimização da Estrutura do Projeto
**Data:** 2025-01-14
**Análise:** Identificação de pastas e scripts obsoletos/não utilizados

##  Situação Atual

### Pastas Identificadas (24 total)
```
.github/          # CI/CD - MANTER
.pytest_cache/    # Cache pytest - MANTER (gitignore)
.trae/            # Sistema TRAE - MANTER
.vscode/          # IDE config - MANTER
__pycache__/      # Cache Python - MANTER (gitignore)
_attic/           #  REMOVER - Arquivos obsoletos
ai_context_storage/ #  AVALIAR - Usado pelo sistema TRAE
alerts/           #  REMOVER - Logs antigos específicos
artifacts/        #  MANTER - Artefatos de build/teste
backend/          #  MANTER - Core do projeto
backups/          #  REMOVER - Backups antigos
changes/          #  REMOVER - Logs de mudanças antigas
config/           #  MANTER - Configurações do projeto
docs/             #  MANTER - Documentação
frontend/         #  MANTER - Core do projeto
htmlcov/          #  MANTER - Relatórios de cobertura (gitignore)
logs/             #  MANTER - Logs ativos do sistema
node_modules/     #  MANTER - Dependências Node (gitignore)
reports/          #  MANTER - Relatórios de análise
scripts/          #  MANTER - Scripts utilitários
temp/             #  REMOVER - Arquivos temporários
tests/            #  MANTER - Testes do projeto
tools/            #  REMOVER - Ferramentas obsoletas
venv/             #  MANTER - Ambiente virtual (gitignore)
```

##  PLANO DE OTIMIZAÇÃO

### REMOÇÃO SEGURA (6 pastas obsoletas)
1. **_attic/** - Backups antigos não referenciados
2. **temp/** - Arquivos temporários regeneráveis
3. **alerts/** - Logs de data específica (20250814)
4. **changes/** - Log de mudança já aplicada
5. **backups/** - Backups obsoletos
6. **tools/** - Ferramentas não utilizadas

### BENEFÍCIOS ESPERADOS
- **Redução:** 24  18 pastas (-25%)
- **Navegação mais clara**
- **Builds mais rápidos**
- **Manutenção simplificada**

### SCRIPTS MANTIDOS (22 ativos)
- Validação: validate_system.py, enhanced_validation.py
- Debug: debug_metrics.py, debug_trends.py
- TRAE: trae_quick_check.py, trae_ai_integration_validator.py
- Utilitários: run_scripts.py, update_docs.py

##  EXECUÇÃO SEGURA
1. Backup Git antes da remoção
2. Verificação de referências
3. Validação pós-limpeza
4. Rollback disponível
