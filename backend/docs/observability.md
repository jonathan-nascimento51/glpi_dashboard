# Sistema de Observabilidade - GLPI Dashboard

Este documento descreve o sistema de observabilidade implementado no GLPI Dashboard, incluindo métricas Prometheus, logging estruturado e sistema de alertas.

## Visão Geral

O sistema de observabilidade fornece:
- **Métricas Prometheus**: Coleta de métricas de performance e negócio
- **Logging Estruturado**: Logs em formato JSON com correlação de requisições
- **Sistema de Alertas**: Monitoramento automático com notificações
- **Health Checks**: Endpoints para verificação de saúde da aplicação

## Componentes

### 1. Métricas Prometheus (`prometheus_metrics.py`)

#### Métricas Coletadas

**Métricas de API:**
- `api_requests_total`: Total de requisições por endpoint e status
- `api_request_duration_seconds`: Duração das requisições (histograma)
- `api_active_requests`: Número de requisições ativas

**Métricas GLPI:**
- `glpi_requests_total`: Total de requisições à API GLPI
- `glpi_request_duration_seconds`: Duração das requisições GLPI
- `glpi_errors_total`: Total de erros por tipo

**Métricas de Sistema:**
- `system_info`: Informações do sistema (versão, ambiente)
- `active_connections`: Conexões ativas

**Métricas de Negócio:**
- `tickets_total`: Total de tickets por status
- `technician_performance`: Performance dos técnicos
- `response_time_p95`: Percentil 95 do tempo de resposta

#### Uso

```python
from backend.utils.prometheus_metrics import prometheus_metrics

# Decorador para monitorar endpoints
@prometheus_metrics.monitor_api_endpoint
def my_endpoint():
    return {"status": "ok"}

# Registro manual de métricas
prometheus_metrics.record_business_metric(
    metric_name="tickets_resolved",
    value=10,
    labels={"technician": "john", "priority": "high"}
)
```

### 2. Logging Estruturado (`structured_logging.py`)

#### Características

- **Formato JSON**: Logs estruturados para fácil parsing
- **Correlation ID**: Rastreamento de requisições end-to-end
- **Contexto de Operação**: Informações sobre a operação em execução
- **Sanitização**: Remoção automática de dados sensíveis
- **Integração Prometheus**: Métricas derivadas dos logs

#### Loggers Disponíveis

```python
from backend.utils.structured_logging import (
    api_logger,      # Para rotas da API
    glpi_logger,     # Para chamadas GLPI
    metrics_logger,  # Para processamento de métricas
    system_logger,   # Para eventos do sistema
    audit_logger     # Para auditoria
)
```

#### Uso

```python
# Logging com contexto
api_logger.log_operation_start(
    operation="get_metrics",
    context={"user_id": "123", "filters": filters}
)

# Logging de erro
api_logger.log_error(
    "Erro ao processar requisição",
    error=exception,
    context={"endpoint": "/api/metrics"}
)

# Decorador para instrumentação automática
@with_structured_logging
def process_data(data):
    return processed_data
```

### 3. Sistema de Alertas (`alerting_system.py`)

#### Regras de Alerta Padrão

1. **Tempo de Resposta Alto**
   - Threshold: > 300ms (P95)
   - Severidade: Warning/Critical

2. **Taxa de Erro Alta**
   - Threshold: > 5%
   - Severidade: Critical

3. **Tickets Zerados**
   - Threshold: 0 tickets por > 60s
   - Severidade: Warning

4. **Nomes Suspeitos**
   - Detecção de padrões suspeitos
   - Severidade: Warning

5. **IDs Não Resolvidos**
   - IDs que não puderam ser resolvidos
   - Severidade: Warning

#### Uso

```python
from backend.utils.alerting_system import alert_manager

# Registro de métrica para avaliação
alert_manager.record_metric("api_response_time", 450, {"endpoint": "/metrics"})

# Consulta de alertas ativos
active_alerts = alert_manager.get_active_alerts()

# Histórico de alertas
history = alert_manager.get_alert_history(hours=24)
```

### 4. Middleware de Observabilidade (`observability_middleware.py`)

#### Funcionalidades

- **Instrumentação Automática**: Todas as requisições são automaticamente instrumentadas
- **Correlation ID**: Geração e propagação automática
- **Métricas de Requisição**: Tempo de resposta, status codes, etc.
- **Health Checks**: Endpoints `/health` e `/health/glpi`
- **Endpoint de Métricas**: `/metrics` para Prometheus
- **Endpoint de Alertas**: `/alerts` para consulta de alertas

#### Configuração

```python
from backend.utils.observability_middleware import setup_observability

app = Flask(__name__)
setup_observability(app)
```

## Endpoints de Observabilidade

### `/metrics`
Exporta métricas no formato Prometheus

### `/health`
Health check básico da aplicação

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "environment": "production"
}
```

### `/health/glpi`
Health check específico da conexão GLPI

```json
{
  "status": "healthy",
  "glpi_connection": "ok",
  "response_time_ms": 150,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### `/alerts`
Consulta de alertas ativos e histórico

```json
{
  "active_alerts": [
    {
      "id": "alert_123",
      "rule_name": "high_response_time",
      "severity": "warning",
      "message": "Tempo de resposta alto detectado",
      "triggered_at": "2024-01-15T10:25:00Z",
      "metric_value": 450,
      "threshold": 300
    }
  ],
  "alert_history": [...]
}
```

## Configuração

### Variáveis de Ambiente

```bash
# Prometheus
PROMETHEUS_GATEWAY_URL=http://localhost:9091
PROMETHEUS_JOB_NAME=glpi_dashboard

# Logging
STRUCTURED_LOGGING=True
LOG_FILE_PATH=logs/app.log
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5

# Alertas
ALERT_RESPONSE_TIME_THRESHOLD=300
ALERT_ERROR_RATE_THRESHOLD=0.05
ALERT_ZERO_TICKETS_THRESHOLD=60
```

### Estrutura de Logs

Os logs são salvos em `logs/app.log` com rotação automática:

```json
{
  "timestamp": "2024-01-15T10:30:00.123Z",
  "level": "INFO",
  "logger": "api",
  "correlation_id": "req_abc123",
  "operation": "get_metrics",
  "message": "Operação iniciada",
  "context": {
    "endpoint": "/api/metrics",
    "method": "GET",
    "user_agent": "..."
  },
  "duration_ms": 150,
  "status_code": 200
}
```

## Monitoramento e Alertas

### Dashboards Recomendados

1. **Dashboard de API**
   - Taxa de requisições
   - Tempo de resposta (P50, P95, P99)
   - Taxa de erro
   - Requisições ativas

2. **Dashboard GLPI**
   - Latência das chamadas GLPI
   - Taxa de erro GLPI
   - Distribuição de tipos de erro

3. **Dashboard de Negócio**
   - Métricas de tickets
   - Performance dos técnicos
   - Tendências temporais

### Alertas Críticos

1. **API Indisponível**: Taxa de erro > 50%
2. **GLPI Indisponível**: Falha na conexão
3. **Performance Degradada**: P95 > 1000ms
4. **Dados Inconsistentes**: Tickets zerados por > 5 minutos

## Troubleshooting

### Logs Não Aparecem
1. Verificar se `STRUCTURED_LOGGING=True`
2. Verificar permissões do diretório `logs/`
3. Verificar se o path `LOG_FILE_PATH` está correto

### Métricas Não Coletadas
1. Verificar conexão com Prometheus Gateway
2. Verificar se `PROMETHEUS_GATEWAY_URL` está correto
3. Verificar logs de erro no sistema

### Alertas Não Funcionam
1. Verificar se as métricas estão sendo coletadas
2. Verificar thresholds configurados
3. Verificar logs do sistema de alertas

## Desenvolvimento

### Adicionando Novas Métricas

```python
# Em prometheus_metrics.py
new_metric = Counter(
    'new_metric_total',
    'Descrição da métrica',
    ['label1', 'label2']
)

# Uso
new_metric.labels(label1='value1', label2='value2').inc()
```

### Adicionando Novas Regras de Alerta

```python
# Em alerting_system.py
new_rule = AlertRule(
    name="new_alert",
    metric_name="new_metric",
    threshold=100,
    comparison="greater_than",
    severity=AlertSeverity.WARNING,
    message="Nova condição de alerta detectada"
)

alert_manager.add_rule(new_rule)
```

## Segurança

- **Sanitização**: Dados sensíveis são automaticamente removidos dos logs
- **Autenticação**: Endpoints de observabilidade podem ser protegidos
- **Rate Limiting**: Proteção contra abuso dos endpoints
- **Validação**: Entrada validada em todos os endpoints

## Performance

- **Sampling**: Logs podem ser amostrados em produção
- **Buffering**: Métricas são enviadas em lotes
- **Async**: Operações de I/O são assíncronas quando possível
- **Caching**: Resultados são cacheados quando apropriado