# Sistema de Observabilidade - GADPI API

## Visão Geral

Este documento descreve o sistema de observabilidade implementado na GADPI API para padronizar logs, métricas e tratamento de erros.

## Componentes

### 1. Logger JSON Estruturado (`observability/logger.py`)

#### Características:
- **Formato JSON**: Todos os logs são estruturados em JSON para facilitar parsing e análise
- **Request ID**: Cada requisição recebe um ID único para rastreamento
- **Context Variables**: Uso de `contextvars` para propagar informações entre threads
- **Níveis de Log**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Tipos de Eventos**: API, Business, Security

#### Uso:
```python
from observability import get_logger, set_request_context

logger = get_logger(__name__)

# Definir contexto da requisição
set_request_context(request_id="req-123", user_id="user-456")

# Logs estruturados
logger.info("Processando requisição", extra={"endpoint": "/api/v1/kpis"})
logger.api_request("/api/v1/kpis", "GET", {"level": "N1"})
logger.business("KPI calculado", {"level": "N1", "total": 150})
```

#### Estrutura do Log:
```json
{
  "timestamp": "2024-01-15T10:30:00.123Z",
  "level": "INFO",
  "logger": "api.endpoints",
  "message": "Processando requisição",
  "request_id": "req-123",
  "user_id": "user-456",
  "event_type": "api",
  "endpoint": "/api/v1/kpis"
}
```

### 2. Exception Handlers (`observability/exceptions.py`)

#### Classes de Exceção:
- **APIError**: Erros gerais da API (400-499)
- **BusinessError**: Violações de regras de negócio (422)
- **ExternalServiceError**: Falhas em serviços externos (502-503)
- **ValidationError**: Erros de validação de dados (400)

#### Estrutura de Resposta de Erro:
```json
{
  "error": {
    "code": "BUSINESS_RULE_VIOLATION",
    "message": "Feature não habilitada",
    "user_message": "Funcionalidade temporariamente indisponível",
    "request_id": "req-123",
    "timestamp": "2024-01-15T10:30:00.123Z",
    "details": {
      "flag": "use_v2_kpis",
      "enabled": false
    }
  }
}
```

#### Uso:
```python
from observability import BusinessError, ExternalServiceError

# Erro de regra de negócio
if not feature_enabled:
    raise BusinessError(
        message="Feature não habilitada",
        details={"flag": "use_v2_kpis", "enabled": False}
    )

# Erro de serviço externo
raise ExternalServiceError(
    service="GLPI",
    message="Timeout na conexão",
    status_code=502,
    details={"timeout": "30s"}
)
```

### 3. Middleware de Métricas (`observability/middleware.py`)

#### Métricas Coletadas:
- **http_requests_total**: Contador de requisições por método, endpoint e status
- **http_request_duration_seconds**: Histograma de latência de requisições
- **http_request_size_bytes**: Tamanho das requisições
- **http_response_size_bytes**: Tamanho das respostas
- **http_requests_active**: Gauge de requisições ativas
- **cache_operations_total**: Operações de cache (hits/misses)
- **external_api_calls_total**: Chamadas para APIs externas
- **external_api_duration_seconds**: Latência de APIs externas

#### Endpoints de Métricas:
- **GET /metrics**: Métricas no formato Prometheus
- **GET /metrics/summary**: Resumo das métricas em JSON

#### Uso das Métricas de Cache:
```python
from observability import CacheMetrics

cache_metrics = CacheMetrics()

# Registrar hit de cache
cache_metrics.record_hit("user_data")

# Registrar miss de cache
cache_metrics.record_miss("user_data")
```

#### Uso das Métricas de API Externa:
```python
from observability import ExternalAPIMetrics

api_metrics = ExternalAPIMetrics()

# Registrar chamada para API externa
with api_metrics.time_request("glpi", "/api/tickets"):
    response = await glpi_client.get_tickets()
```

## Configuração

### Integração na Aplicação FastAPI:
```python
from fastapi import FastAPI
from observability import setup_observability

app = FastAPI(title="GADPI API", version="1.1.0")

# Configurar observabilidade
setup_observability(app)
```

### Variáveis de Ambiente:
```bash
# Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Formato de log (json, text)
LOG_FORMAT=json

# Habilitar métricas Prometheus
ENABLE_METRICS=true
```

## Monitoramento e Alertas

### Métricas Importantes para Alertas:
1. **Taxa de Erro**: `rate(http_requests_total{status=~"5.."}[5m])`
2. **Latência P95**: `histogram_quantile(0.95, http_request_duration_seconds)`
3. **Requisições Ativas**: `http_requests_active > 100`
4. **Cache Miss Rate**: `rate(cache_operations_total{operation="miss"}[5m])`

### Logs Importantes para Monitoramento:
- **Erros de Serviço Externo**: `level="ERROR" AND event_type="external_service"`
- **Violações de Regra de Negócio**: `level="WARNING" AND event_type="business"`
- **Eventos de Segurança**: `event_type="security"`

## Testes

### Executar Testes:
```bash
# Todos os testes de observabilidade
pytest tests/observability/ -v

# Testes específicos de erro
pytest tests/observability/test_observability.py::TestErrorHandling -v

# Testes de métricas
pytest tests/observability/test_observability.py::TestMetricsCollection -v
```

### Validação de Payloads de Erro:
Os testes validam:
- Códigos de status HTTP corretos
- Estrutura padronizada de resposta de erro
- Presença de `request_id` em todas as respostas
- Detalhes específicos para cada tipo de erro
- Headers de observabilidade (`X-Request-ID`, `X-Response-Time`)

## Troubleshooting

### Problemas Comuns:

1. **Logs não aparecem em JSON**:
   - Verificar variável `LOG_FORMAT=json`
   - Confirmar que `setup_logging()` foi chamado

2. **Request ID não propaga**:
   - Verificar se middleware está configurado
   - Confirmar uso de `set_request_context()`

3. **Métricas não coletadas**:
   - Verificar se `ENABLE_METRICS=true`
   - Confirmar que middleware de métricas está ativo
   - Acessar `/metrics` para verificar endpoint

4. **Erros não estruturados**:
   - Verificar se `setup_exception_handlers()` foi chamado
   - Confirmar que exceções customizadas estão sendo usadas

### Debug de Logs:
```python
# Habilitar debug de logging
import logging
logging.getLogger("observability").setLevel(logging.DEBUG)

# Verificar contexto atual
from observability.logger import request_id_var, user_id_var
print(f"Request ID: {request_id_var.get(None)}")
print(f"User ID: {user_id_var.get(None)}")
```

## Roadmap

### Próximas Melhorias:
1. **Distributed Tracing**: Integração com OpenTelemetry
2. **Alertas Automáticos**: Webhooks para Slack/Teams
3. **Dashboard**: Grafana para visualização de métricas
4. **Log Aggregation**: Integração com ELK Stack
5. **Performance Profiling**: APM para análise de performance

---

**Versão**: 1.0.0  
**Data**: Janeiro 2024  
**Autor**: Sistema de Observabilidade GADPI
