# Protocolo de Mudanças Seguras - GLPI Dashboard

## Visão Geral

O Protocolo de Mudanças Seguras é um sistema robusto para gerenciar mudanças no GLPI Dashboard de forma controlada, segura e auditável. Ele garante que todas as modificações passem por validações rigorosas antes de serem aplicadas.

## Objetivos

- **Segurança**: Backup automático antes de qualquer mudança
- **Qualidade**: Testes obrigatórios e validação de integridade
- **Rastreabilidade**: Auditoria completa de todas as mudanças
- **Recuperação**: Rollback rápido em caso de problemas
- **Compliance**: Atendimento a requisitos de governança

## Arquitetura

```text
Protocolo de Mudanças Seguras
  Backup Automático
  Testes Obrigatórios
  Validação de Integridade
  Aplicação Controlada
  Relatórios Detalhados
  Rollback Automático
```

## Estrutura de Arquivos

```text
glpi_dashboard/
 safe_change_protocol.py      # Módulo principal
 config_safe_changes.py       # Configurações
 example_safe_changes.py      # Exemplos de uso
 backups/changes/             # Backups automáticos
 reports/changes/             # Relatórios de mudanças
 logs/changes/                # Logs detalhados
 test_results/                # Resultados de testes
```

## Como Usar

### 1. Importar o Módulo

```python
from safe_change_protocol import SafeChangeProtocol, ChangeType
```

### 2. Criar Solicitação de Mudança

```python
protocol = SafeChangeProtocol()

change_request = protocol.create_change_request(
    title="Correção de cálculo de métricas",
    description="Corrigir algoritmo de contagem de tickets",
    change_type=ChangeType.METRIC_CALCULATION,
    affected_files=[
        "backend/app/services/metrics_service.py",
        "frontend/components/StatusMetricsCard.py"
    ],
    affected_metrics=["tickets_by_status", "total_open_tickets"],
    risk_level="HIGH",
    author="desenvolvedor"
)
```

### 3. Executar Protocolo Completo

```python
# Backup automático
protocol.backup_affected_files(change_request)

# Testes obrigatórios
test_results = protocol.run_mandatory_tests(change_request)

# Validação de integridade
validation_results = protocol.validate_integrity(change_request)

# Aplicar mudança (se tudo passou)
if test_results['overall_status'] == 'PASSED' and validation_results['overall_status'] == 'PASSED':
    protocol.apply_change(change_request)
    
# Gerar relatório
report = protocol.generate_change_report(change_request)
```

### 4. Exemplo Prático

```bash
# Executar exemplo completo
python example_safe_changes.py
```

## Configuração

Edite o arquivo `config_safe_changes.py` para personalizar:

```python
# Testes obrigatórios
MANDATORY_TESTS = [
    "test_api_endpoints",
    "test_database_integrity",
    "test_metrics_calculation",
    "test_frontend_rendering"
]

# Configurações de backup
BACKUP_RETENTION_DAYS = 30
BACKUP_COMPRESSION = True

# Configurações por ambiente
ENVIRONMENT_CONFIGS = {
    "production": {
        "require_approval": True,
        "auto_rollback": True,
        "require_peer_review": True
    }
}
```

## Tipos de Testes

### Testes Obrigatórios

- **API Endpoints**: Verificar se todas as rotas respondem corretamente
- **Integridade do Banco**: Validar estrutura e dados
- **Cálculo de Métricas**: Testar algoritmos de agregação
- **Renderização Frontend**: Verificar componentes visuais
- **Consistência de Dados**: Validar integridade referencial

### Validações de Integridade

- **Conexão com Banco**: Testar conectividade
- **Saúde da API**: Verificar endpoints críticos
- **Performance**: Medir tempos de resposta
- **Métricas Críticas**: Validar valores esperados

## Relatórios

O sistema gera relatórios em múltiplos formatos:

### Markdown (Legível)

```markdown
# Relatório de Mudança

## Informações Gerais
- **ID**: change_20250114_143022_abc123
- **Título**: Correção de cálculo de métricas
- **Status**: SUCESSO
- **Risco**: HIGH

## Resultados dos Testes
 test_api_endpoints: PASSED
 test_database_integrity: PASSED
 test_metrics_calculation: PASSED
```

### JSON (Programático)

```json
{
  "change_id": "change_20250114_143022_abc123",
  "status": "SUCCESS",
  "tests": {
    "test_api_endpoints": {"status": "PASSED", "duration": 2.3}
  },
  "metrics": {
    "total_duration": 45.2,
    "files_backed_up": 3
  }
}
```

### HTML (Visual)

Relatório completo com gráficos e timeline visual.

## Rollback

### Rollback Automático

```python
# Em caso de falha, rollback é executado automaticamente
if AUTO_ROLLBACK_ON_FAILURE:
    protocol.rollback_change(change_request)
```

### Rollback Manual

```python
# Listar mudanças recentes
history = protocol.get_change_history()

# Fazer rollback de uma mudança específica
protocol.rollback_change(change_id="change_20250114_143022_abc123")
```

## Monitoramento

### Métricas Coletadas

- Tempo total de execução
- Taxa de sucesso/falha
- Número de rollbacks
- Performance dos testes
- Uso de recursos

### Alertas

- Falha em mudanças críticas
- Rollbacks executados
- Testes com performance degradada
- Validações falhando

## Segurança

### Controles Implementados

- **Backup obrigatório** antes de qualquer mudança
- **Testes automatizados** para validação
- **Auditoria completa** de todas as operações
- **Rollback rápido** em caso de problemas
- **Aprovação obrigatória** para mudanças de alto risco

### Compliance

- Documentação de todas as mudanças
- Trilha de auditoria completa
- Evidências de testes
- Capacidade de rollback
- Workflow de aprovação

## Troubleshooting

### Problemas Comuns

#### Testes Falhando

```bash
# Verificar logs detalhados
cat logs/changes/change_20250114_143022_abc123.log

# Executar testes individualmente
pytest tests/test_api_endpoints.py -v
```

#### Backup Falhando

```bash
# Verificar espaço em disco
df -h

# Verificar permissões
ls -la backups/changes/
```

#### Rollback Necessário

```python
# Listar mudanças recentes
protocol.get_change_history()

# Executar rollback
protocol.rollback_change(change_id)
```

## Exemplos Avançados

### Mudança com Aprovação

```python
# Criar mudança que requer aprovação
change_request = protocol.create_change_request(
    title="Mudança crítica em produção",
    risk_level="CRITICAL",
    require_approval=True
)

# Aguardar aprovação
protocol.wait_for_approval(change_request)

# Continuar com o protocolo
protocol.execute_change_protocol(change_request)
```

### Mudança com Peer Review

```python
# Configurar peer review
change_request.require_peer_review = True
change_request.reviewers = ["senior_dev1", "tech_lead"]

# Executar com revisão
protocol.execute_with_review(change_request)
```

### Integração com CI/CD

```yaml
# .github/workflows/safe-deploy.yml
name: Safe Deployment
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Execute Safe Change Protocol
        run: |
          python safe_change_protocol.py \
            --title "Deploy ${{ github.sha }}" \
            --type DEPLOYMENT \
            --risk-level MEDIUM
```

## Contribuindo

1. **Fork** o repositório
2. **Crie** uma branch para sua feature
3. **Implemente** seguindo o protocolo de mudanças
4. **Teste** usando o sistema de validação
5. **Submeta** um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para detalhes.

## Suporte

Para suporte e dúvidas:

- Email: [suporte@glpi-dashboard.com](mailto:suporte@glpi-dashboard.com)
- Documentação: [docs/TROUBLESHOOTING_METRICS.md](docs/TROUBLESHOOTING_METRICS.md)
- Issues: [GitHub Issues](https://github.com/projeto/glpi-dashboard/issues)

---

**Importante**: Sempre execute o protocolo de mudanças seguras antes de aplicar modificações em produção!
