# Sistema de Qualidade de Dados - GLPI Dashboard

## Visão Geral

Este sistema implementa validação automática de qualidade de dados para detectar e alertar sobre problemas como dados all-zero, anomalias e inconsistências no dashboard GLPI.

## Componentes Implementados

### 1. Data Quality Service (`services/data_quality_service.py`)

**Funcionalidades:**
- Detecção de dados all-zero
- Identificação de anomalias e picos
- Validação de consistência temporal
- Verificação de integridade de dados
- Cálculo de métricas de qualidade

**Classes principais:**
- `DataQualityLevel`: Enum com níveis de qualidade (excellent, good, fair, poor, critical)
- `DataQualityIssue`: Representa um problema encontrado
- `DataQualityReport`: Relatório consolidado de qualidade
- `DataQualityService`: Serviço principal de validação

### 2. Endpoint de Health Data (`/api/v1/health/data`)

**Endpoint:** `GET /api/v1/health/data`

**Resposta:**
```json
{
  "status": "ok|error",
  "quality_level": "excellent|good|fair|poor|critical",
  "all_zero": false,
  "anomalies": false,
  "issues_count": 0,
  "critical_issues": false,
  "timestamp": "2024-01-15T10:30:00Z",
  "metrics": {
    "total_fields": 12,
    "numeric_fields": 8,
    "data_completeness": 0.95
  },
  "issues": []
}
```

### 3. Testes E2E Anti-Zero Guard v2

**Arquivo:** `frontend/tests/e2e/anti-zero-guard-v2.spec.ts`

**Testes implementados:**
- Validação do endpoint `/api/v1/health/data`
- Detecção de dados all-zero via API
- Validação visual do dashboard
- Teste de falha intencional quando all-zero=true
- Validação de métricas de qualidade
- Teste de resiliência da API

### 4. Script de Validação Automatizada

**Arquivo:** `backend/validate-data-quality.py`

**Funcionalidades:**
- Aguarda serviços ficarem prontos
- Testa endpoint de health/data
- Gera relatórios de validação
- Falha automaticamente se detectar problemas críticos

## Como Usar

### 1. Executar Validação Manual

```bash
# No diretório backend
cd backend
python validate-data-quality.py
```

### 2. Executar Testes E2E

```bash
# No diretório frontend
cd frontend
npx playwright test anti-zero-guard-v2.spec.ts
```

### 3. Verificar Health via API

```bash
curl http://localhost:8000/api/v1/health/data
```

### 4. Integração com CI/CD

Adicione ao seu pipeline:

```yaml
# Exemplo GitHub Actions
- name: Validate Data Quality
  run: |
    cd backend
    python validate-data-quality.py
  continue-on-error: false
```

## Níveis de Qualidade

| Nível | Descrição | Ação |
|-------|-----------|-------|
| `excellent` | Dados perfeitos, sem problemas |  Continuar |
| `good` | Pequenos problemas não críticos |  Continuar |
| `fair` | Problemas moderados |  Investigar |
| `poor` | Problemas significativos |  Corrigir |
| `critical` | Problemas críticos (all-zero, etc.) |  Falhar |

## Tipos de Problemas Detectados

### All-Zero Detection
- **Descrição:** Todos os valores numéricos são zero
- **Severidade:** Critical
- **Ação:** Falha imediata

### Anomaly Detection
- **Descrição:** Picos anômalos nos dados
- **Severidade:** Warning
- **Ação:** Investigação

### Temporal Consistency
- **Descrição:** Problemas com timestamps
- **Severidade:** Warning
- **Ação:** Verificar fonte de dados

### Data Integrity
- **Descrição:** Campos obrigatórios ausentes
- **Severidade:** Error
- **Ação:** Corrigir estrutura de dados

## Configuração

### Variáveis de Ambiente

```bash
# Configurações de qualidade de dados
DATA_QUALITY_ENABLED=true
DATA_QUALITY_ALL_ZERO_THRESHOLD=0.8
DATA_QUALITY_ANOMALY_THRESHOLD=3.0
```

### Flags de Feature

```python
# Em flags.py
DATA_QUALITY_CHECKS = os.getenv("DATA_QUALITY_ENABLED", "true").lower() == "true"
```

## Monitoramento e Alertas

### Métricas Prometheus

```
# Métricas expostas
data_quality_level{level="excellent|good|fair|poor|critical"}
data_quality_issues_total{type="all_zero|anomaly|temporal|integrity"}
data_quality_check_duration_seconds
```

### Alertas Recomendados

```yaml
# Alerta para dados all-zero
- alert: DataAllZeroDetected
  expr: data_quality_issues_total{type="all_zero"} > 0
  for: 0m
  labels:
    severity: critical
  annotations:
    summary: "Dados all-zero detectados no dashboard GLPI"
```

## Troubleshooting

### Problema: Endpoint retorna erro 500

**Possíveis causas:**
- Serviço GLPI indisponível
- Erro na conexão com banco de dados
- Dados malformados

**Solução:**
1. Verificar logs do backend
2. Testar conectividade com GLPI
3. Validar estrutura dos dados

### Problema: Falsos positivos em all-zero

**Possíveis causas:**
- Período sem dados reais
- Filtros muito restritivos
- Problemas de timezone

**Solução:**
1. Ajustar threshold em `DATA_QUALITY_ALL_ZERO_THRESHOLD`
2. Verificar filtros de data
3. Validar configuração de timezone

### Problema: Testes E2E falhando

**Possíveis causas:**
- Serviços não iniciados
- Timeout insuficiente
- Problemas de rede

**Solução:**
1. Verificar se API e frontend estão rodando
2. Aumentar timeouts nos testes
3. Verificar conectividade de rede

## Roadmap

### Próximas Funcionalidades

- [ ] Dashboard de qualidade de dados
- [ ] Alertas via email/Slack
- [ ] Histórico de qualidade
- [ ] Machine learning para detecção de anomalias
- [ ] Integração com Grafana
- [ ] API para configuração dinâmica de thresholds

### Melhorias Planejadas

- [ ] Cache de resultados de qualidade
- [ ] Validação em tempo real
- [ ] Métricas mais granulares
- [ ] Suporte a múltiplas fontes de dados
- [ ] Interface web para configuração

## Contribuição

Para contribuir com o sistema de qualidade de dados:

1. Siga os padrões de código definidos
2. Adicione testes para novas funcionalidades
3. Atualize a documentação
4. Execute validação completa antes do commit

```bash
# Checklist antes do commit
make lint
make test
python validate-data-quality.py
npx playwright test anti-zero-guard-v2.spec.ts
```

## Licença

Este sistema segue a mesma licença do projeto principal GLPI Dashboard.
