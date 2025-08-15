# Plano de Execução - Reorganização de Scripts da Raiz
**Data:** 2025-01-14
**Status:** PRONTO PARA EXECUÇÃO

## 📋 RESUMO DA OPERAÇÃO

**Objetivo:** Reorganizar 8 dos 10 scripts Python da raiz para subdiretórios organizados

**Resultado Final:**
- Raiz: 10 → 2 arquivos Python (`app.py`, `trae_quick_check.py`)
- Nova estrutura: `trae/systems/`, `trae/config/`, `scripts/`, `scripts/validation/`

## 🎯 ETAPAS DE EXECUÇÃO

### ETAPA 1: Preparação e Backup
- [ ] Criar backup completo do estado atual
- [ ] Validar sistema integrado (AI Context, Monitoring, Safe Changes)
- [ ] Executar `python validate_system.py --full-check`
- [ ] Confirmar todos os 12 arquivos obrigatórios presentes

### ETAPA 2: Criação da Nova Estrutura
- [ ] Criar diretório `trae/`
- [ ] Criar subdiretório `trae/systems/`
- [ ] Criar subdiretório `trae/config/`
- [ ] Criar `__init__.py` nos novos diretórios

### ETAPA 3: Movimentação dos Arquivos (Fase 1 - Sistemas TRAE)
- [ ] Mover `ai_context_system.py` → `trae/systems/`
- [ ] Mover `monitoring_system.py` → `trae/systems/`
- [ ] Mover `safe_change_protocol.py` → `trae/systems/`
- [ ] Mover `config_ai_context.py` → `trae/config/ai_context.py`
- [ ] Mover `config_monitoring.py` → `trae/config/monitoring.py`
- [ ] Mover `config_safe_changes.py` → `trae/config/safe_changes.py`

### ETAPA 4: Movimentação dos Arquivos (Fase 2 - Utilitários)
- [ ] Mover `run_scripts.py` → `scripts/`
- [ ] Mover `trae_ai_integration_validator.py` → `scripts/validation/`

### ETAPA 5: Atualização de Referências
- [ ] Atualizar `trae-context.yml` (caminhos dos arquivos)
- [ ] Atualizar imports nos sistemas TRAE
- [ ] Atualizar documentação (READMEs)
- [ ] Atualizar scripts de validação

### ETAPA 6: Validação Final
- [ ] Executar `python validate_system.py --full-check`
- [ ] Testar comandos de emergência
- [ ] Validar funcionamento dos 3 sistemas integrados
- [ ] Executar testes de integração

## 🔍 ARQUIVOS QUE PRECISAM SER ATUALIZADOS

### trae-context.yml
```yaml
# ANTES:
config_file: "config_ai_context.py"
# DEPOIS:
config_file: "trae/config/ai_context.py"
```

### Imports nos Sistemas
```python
# ANTES:
from config_ai_context import AIContextConfig
# DEPOIS:
from trae.config.ai_context import AIContextConfig
```

### Comandos de Emergência
```python
# ANTES:
from ai_context_system import AIContextSystem
# DEPOIS:
from trae.systems.ai_context_system import AIContextSystem
```

## ⚠️ RISCOS E MITIGAÇÕES

### RISCO ALTO: Sistema Integrado Quebrar
**Mitigação:**
- Backup completo antes de iniciar
- Validação após cada etapa
- Rollback automático se falhar

### RISCO MÉDIO: Referências Hardcoded
**Mitigação:**
- Busca por todas as referências antes de mover
- Atualização sistemática de imports
- Testes de importação após cada mudança

### RISCO BAIXO: Documentação Desatualizada
**Mitigação:**
- Atualização simultânea da documentação
- Validação de links e referências

## 🚨 PLANO DE ROLLBACK

### Se Falhar na Etapa 1-2:
- Remover diretórios criados
- Restaurar estado original

### Se Falhar na Etapa 3-4:
- Mover arquivos de volta para raiz
- Restaurar nomes originais

### Se Falhar na Etapa 5-6:
- Executar `python safe_change_protocol.py --restore-latest`
- Reverter mudanças no trae-context.yml
- Restaurar imports originais

## 📊 MÉTRICAS DE SUCESSO

- [ ] Sistema integrado 100% funcional
- [ ] Todos os 3 sistemas ativos (AI Context, Monitoring, Safe Changes)
- [ ] Validação completa passa sem erros
- [ ] Raiz do projeto com apenas 2 arquivos Python
- [ ] Nova estrutura organizacional implementada
- [ ] Documentação atualizada e consistente

## 🔧 COMANDOS DE VALIDAÇÃO

```bash
# Validação completa do sistema
python validate_system.py --full-check

# Status dos sistemas integrados
python -c "
from trae.systems.ai_context_system import AIContextSystem
from trae.systems.monitoring_system import MonitoringSystem
from trae.systems.safe_change_protocol import SafeChangeProtocol
print('AI Context:', AIContextSystem().is_active())
print('Monitoring:', MonitoringSystem().is_active())
print('Safe Changes:', SafeChangeProtocol().is_active())
"

# Verificação da estrutura
ls -la trae/
ls -la trae/systems/
ls -la trae/config/
ls -la scripts/validation/
```

## ✅ CHECKLIST FINAL

- [ ] Backup criado e validado
- [ ] Nova estrutura criada
- [ ] 8 arquivos movidos com sucesso
- [ ] trae-context.yml atualizado
- [ ] Imports atualizados
- [ ] Documentação atualizada
- [ ] Sistema integrado funcional
- [ ] Validação completa passou
- [ ] Testes de integração OK
- [ ] Commit realizado

---

**PRÓXIMO PASSO:** Executar Etapa 1 - Preparação e Backup