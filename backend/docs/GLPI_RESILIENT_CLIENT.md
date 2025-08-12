# Cliente GLPI Resiliente

Este documento descreve o cliente GLPI resiliente implementado para garantir alta disponibilidade e previsibilidade nas integrações com a API GLPI.

## Visão Geral

O cliente resiliente implementa os seguintes padrões:

- **Circuit Breaker**: Previne cascata de falhas
- **Retry com Backoff Exponencial**: Recuperação automática de falhas transitórias
- **Gerenciamento de Sessão**: Renovação automática de tokens
- **Métricas Prometheus**: Observabilidade completa
- **Paginação Padronizada**: Interface consistente para grandes datasets

## Componentes Principais

### 1. GLPIResilientClient

Cliente principal que orquestra todas as funcionalidades de resiliência.

```python
from adapters.glpi.resilient_client import create_glpi_client

# Configuração básica
client = create_glpi_client(
    base_url="https://glpi.example.com/apirest.php",
    app_token="your_app_token",
    user_token="your_user_token"
)

# Fazer requisições
response = await client.request("GET", "/Ticket")
```

### 2. Circuit Breaker

Previne sobrecarga do servidor GLPI em caso de falhas:

- **Fechado**: Requisições normais
- **Aberto**: Falha rápida por 60 segundos
- **Meio-Aberto**: Testa recuperação

```python
# Configuração personalizada
from adapters.glpi.resilient_client import CircuitBreakerConfig

config = CircuitBreakerConfig(
    failure_threshold=10,  # 10 falhas para abrir
    recovery_timeout=30,   # 30 segundos para tentar recuperar
    success_threshold=3    # 3 sucessos para fechar
)
```

### 3. Sistema de Retry

Retry automático com backoff exponencial:

- **Erros 5xx**: Retry automático
- **Timeout**: Retry automático
- **Rate Limit (429)**: Respeita header `Retry-After`
- **Erros 4xx**: Sem retry (exceto 401/403 para renovação de sessão)

```python
from adapters.glpi.resilient_client import RetryConfig

retry_config = RetryConfig(
    max_attempts=5,
    base_delay=1.0,
    max_delay=60.0,
    exponential_base=2.0
)
```

### 4. Gerenciamento de Sessão

Renovação automática de tokens:

- Detecta expiração por resposta 401/403
- Renovação thread-safe
- Métricas de sessão ativa

### 5. Paginação Padronizada

Interface consistente para grandes datasets:

```python
from adapters.glpi.pagination import PaginationParams, TicketFilters
from datetime import datetime, timedelta

# Filtros de tickets
filters = TicketFilters(
    status=[TicketStatus.NEW, TicketStatus.ASSIGNED],
    date_range=DateRange(
        start=datetime.now() - timedelta(days=30),
        end=datetime.now()
    ),
    priority=[TicketPriority.HIGH, TicketPriority.CRITICAL]
)

# Paginação
pagination = PaginationParams(
    page=1,
    page_size=50
)

# Buscar tickets
response = await client.get_tickets(filters=filters, pagination=pagination)
```

## Métricas e Observabilidade

### Métricas Prometheus

O cliente expõe métricas detalhadas:

```
# Requisições por operação
glpi_requests_total{operation="api_request",status="success"} 150
glpi_requests_total{operation="authentication",status="error"} 2

# Latência por percentil
glpi_request_duration_seconds{quantile="0.95"} 0.245

# Estado do Circuit Breaker
glpi_circuit_breaker_state{state="closed"} 1

# Sessões ativas
glpi_active_sessions 1

# Retries
glpi_retries_total{operation="api_request"} 5
```

### Endpoints de Métricas

- `GET /api/v1/metrics/prometheus` - Métricas Prometheus
- `GET /api/v1/metrics/summary` - Resumo JSON
- `GET /api/v1/metrics/health` - Status de saúde
- `GET /api/v1/metrics/structured` - Logs estruturados

## Use Cases Agregados

### Métricas por Nível de Serviço

```python
from usecases.aggregated_metrics import AggregatedMetricsUseCase
from adapters.glpi.pagination import MetricPeriod

usecase = AggregatedMetricsUseCase(glpi_client)

# Métricas diárias (N1)
daily_metrics = await usecase.get_daily_metrics(
    date=datetime.now().date()
)

# Métricas semanais (N2)
weekly_metrics = await usecase.get_weekly_metrics(
    week_start=datetime.now().date()
)

# Métricas mensais (N3)
monthly_metrics = await usecase.get_monthly_metrics(
    month=datetime.now().date().replace(day=1)
)

# Comparativo (N4)
comparative_metrics = await usecase.get_comparative_metrics(
    current_period=MetricPeriod.WEEKLY,
    periods_back=4
)
```

## Testes de Resiliência

### Executar Testes

```bash
# Testes unitários
pytest tests/unit/test_resilient_client.py -v

# Testes de integração
pytest tests/integration/test_resilience.py -v

# Testes específicos
pytest tests/integration/test_resilience.py::test_circuit_breaker_opens_on_failures -v
```

### Cenários Testados

1. **Circuit Breaker**
   - Abertura após falhas consecutivas
   - Recuperação automática
   - Falha rápida quando aberto

2. **Retry**
   - Erros transitórios (5xx, timeout)
   - Rate limiting (429)
   - Backoff exponencial

3. **Sessão**
   - Renovação em 401/403
   - Concorrência thread-safe
   - Timeout de sessão

4. **Paginação**
   - Falhas intermitentes
   - Recuperação de circuit breaker
   - Grandes datasets

## Configuração de Produção

### Variáveis de Ambiente

```bash
# GLPI
GLPI_BASE_URL=https://glpi.company.com/apirest.php
GLPI_APP_TOKEN=your_app_token
GLPI_USER_TOKEN=your_user_token

# Circuit Breaker
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
CIRCUIT_BREAKER_RECOVERY_TIMEOUT=60
CIRCUIT_BREAKER_SUCCESS_THRESHOLD=2

# Retry
RETRY_MAX_ATTEMPTS=3
RETRY_BASE_DELAY=1.0
RETRY_MAX_DELAY=30.0

# Timeouts
REQUEST_TIMEOUT=30
SESSION_TIMEOUT=3600
```

### Monitoramento

1. **Alertas Prometheus**
   ```yaml
   # Circuit breaker aberto
   - alert: GLPICircuitBreakerOpen
     expr: glpi_circuit_breaker_state{state="open"} == 1
     for: 1m
   
   # Alta taxa de erro
   - alert: GLPIHighErrorRate
     expr: rate(glpi_requests_total{status="error"}[5m]) > 0.1
     for: 2m
   
   # Latência alta
   - alert: GLPIHighLatency
     expr: glpi_request_duration_seconds{quantile="0.95"} > 5
     for: 5m
   ```

2. **Logs Estruturados**
   ```json
   {
     "timestamp": "2024-01-15T10:30:00Z",
     "level": "ERROR",
     "operation": "api_request",
     "status": "circuit_breaker_open",
     "duration_seconds": 0.001,
     "error_type": "CircuitBreakerError"
   }
   ```

## Troubleshooting

### Problemas Comuns

1. **Circuit Breaker Sempre Aberto**
   - Verificar conectividade com GLPI
   - Validar credenciais
   - Ajustar threshold de falhas

2. **Muitos Retries**
   - Verificar latência de rede
   - Ajustar timeouts
   - Verificar carga do servidor GLPI

3. **Sessão Expirando Frequentemente**
   - Verificar configuração de timeout
   - Validar tokens
   - Verificar logs de autenticação

### Debug

```python
import logging

# Habilitar logs detalhados
logging.getLogger("adapters.glpi").setLevel(logging.DEBUG)

# Verificar métricas
from utils.metrics import get_metrics
metrics = get_metrics()
print(metrics.get_summary())
```

## Roadmap

- [ ] Cache inteligente com TTL
- [ ] Balanceamento de carga entre instâncias GLPI
- [ ] Compressão automática de payloads
- [ ] Métricas de negócio personalizadas
- [ ] Dashboard Grafana pré-configurado