# Regras Integradas do Sistema - Trae AI

## 1. Sistema de AI Context (OBRIGATÓRIO)

### Configuração Automática
- **SEMPRE** verificar se o AI Context está ativo antes de qualquer operação
- **SEMPRE** usar as configurações do `config_ai_context.py`
- **SEMPRE** registrar contexto em `ai_context_storage/`

### Comandos de Verificação
```bash
# Verificar status do AI Context
python example_ai_context.py

# Validar configurações
python -c "from config_ai_context import AIContextConfig; print('AI Context OK')"
```

### MCPs Obrigatórios
- `filesystem_mcp`: Monitoramento de arquivos
- `git_mcp`: Controle de versão
- `knowledge_graph_mcp`: Grafo de conhecimento
- `code_analysis_mcp`: Análise de código
- `documentation_mcp`: Documentação automática
- `metrics_collector_mcp`: Coleta de métricas
- `api_monitor_mcp`: Monitoramento de APIs

## 2. Sistema de Monitoramento (OBRIGATÓRIO)

### Verificações Automáticas
- **SEMPRE** verificar métricas antes de mudanças
- **SEMPRE** validar logs em `logs/monitoring.log`
- **SEMPRE** usar alertas configurados

### Comandos de Verificação
```bash
# Verificar sistema de monitoramento
python example_monitoring.py

# Validar configurações
python -c "from config_monitoring import MonitoringConfig; print('Monitoring OK')"
```

### Métricas Obrigatórias
- Performance de APIs
- Contagem de tickets
- Status de serviços
- Uso de recursos
- Tempo de resposta

## 3. Protocolo de Mudanças Seguras (OBRIGATÓRIO)

### Processo Obrigatório
1. **SEMPRE** criar backup antes de mudanças
2. **SEMPRE** executar validações
3. **SEMPRE** ter plano de rollback
4. **SEMPRE** documentar mudanças

### Comandos de Verificação
```bash
# Verificar protocolo de mudanças
python example_safe_changes.py

# Validar configurações
python -c "from config_safe_changes import SafeChangesConfig; print('Safe Changes OK')"
```

### Validações Obrigatórias
- Lint (ruff, black, isort)
- Testes unitários
- Testes de integração
- Verificação de dependências
- Validação de métricas

## 4. Integração com Trae AI

### Antes de Qualquer Operação
```bash
# Script de validação completa
python validate_system.py
```

### Fluxo de Trabalho Obrigatório
1. **Verificar sistemas ativos**
   - AI Context funcionando
   - Monitoramento ativo
   - Protocolo de mudanças configurado

2. **Executar validações**
   - Todos os 12 arquivos presentes
   - Configurações válidas
   - MCPs funcionando

3. **Registrar contexto**
   - Salvar estado atual
   - Documentar mudanças
   - Atualizar métricas

4. **Aplicar mudanças com segurança**
   - Backup automático
   - Validações contínuas
   - Rollback se necessário

## 5. Arquivos Críticos (NÃO MODIFICAR SEM VALIDAÇÃO)

### Sistema AI Context
- `ai_context_system.py`
- `config_ai_context.py`
- `example_ai_context.py`
- `README_AI_CONTEXT.md`

### Sistema de Monitoramento
- `monitoring_system.py`
- `config_monitoring.py`
- `example_monitoring.py`
- `README_MONITORING.md`

### Protocolo de Mudanças
- `safe_change_protocol.py`
- `config_safe_changes.py`
- `example_safe_changes.py`
- `README_SAFE_CHANGES.md`

## 6. Comandos de Emergência

### Restaurar Sistema
```bash
# Restaurar do backup mais recente
python safe_change_protocol.py --restore-latest

# Verificar integridade
python validate_system.py --full-check
```

### Diagnóstico Rápido
```bash
# Status completo do sistema
python -c "
from ai_context_system import AIContextSystem
from monitoring_system import MonitoringSystem
from safe_change_protocol import SafeChangeProtocol
print('=== STATUS DO SISTEMA ===')
print('AI Context:', AIContextSystem().is_active())
print('Monitoring:', MonitoringSystem().is_active())
print('Safe Changes:', SafeChangeProtocol().is_active())
"
```

## 7. Regras de Segurança

### NUNCA fazer sem validação:
- Modificar arquivos de configuração
- Alterar estrutura de MCPs
- Desabilitar monitoramento
- Pular protocolo de mudanças
- Ignorar backups

### SEMPRE fazer:
- Verificar sistemas antes de operar
- Registrar todas as ações
- Manter logs atualizados
- Validar após mudanças
- Documentar problemas

## 8. Integração com Custom Instructions

Este sistema está **100% integrado** com as Custom Instructions do usuário:
- Segue padrões de código (Python 3.11+, ruff, black, isort)
- Usa type hints e docstrings Google
- Implementa testes com pytest
- Mantém logs estruturados
- Segue fluxo Git com branches
- Gera documentação automática
- Implementa observabilidade completa
- Valida visualmente dashboards
- Mantém UX corporativo limpo

## 9. Validação Contínua

### IMPORTANTE
Estas regras são **OBRIGATÓRIAS** e devem ser seguidas pelo Trae AI em **TODAS** as operações. O sistema foi projetado para ser **100% integrado** e **auto-validável**.
