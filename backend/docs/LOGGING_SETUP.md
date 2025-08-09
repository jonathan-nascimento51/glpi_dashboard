# Configuração de Logging Estruturado - GLPI Dashboard

## Visão Geral

Este documento descreve como configurar e usar o sistema de logging estruturado implementado no GLPI Dashboard. O sistema fornece logs em formato JSON com contexto rico, facilitando análise, monitoramento e debugging.

## Características Principais

- **Logs em formato JSON**: Estruturados e facilmente parseáveis
- **Contexto rico**: Inclui timestamps, níveis, metadata e campos customizados
- **Performance tracking**: Monitoramento automático de tempo de execução
- **API call logging**: Registro detalhado de chamadas de API
- **Integração com serviços de monitoramento**: ELK Stack, Grafana Loki, Prometheus
- **Configuração por ambiente**: Desenvolvimento, produção e teste

## Estrutura dos Arquivos

```
backend/
 utils/
    structured_logger.py      # Módulo principal do logger
 config/
    logging_config.py         # Configurações de logging
 tests/
    test_structured_logger.py # Testes unitários
 docs/
     LOGGING_SETUP.md          # Este documento
```

## Configuração Básica

### 1. Importação e Uso Simples

```python
from utils.structured_logger import create_glpi_logger, log_api_call, log_performance

# Criar logger
logger = create_glpi_logger("INFO")

# Log simples
logger.info("Aplicação iniciada", version="1.0.0", environment="production")

# Log de erro
logger.error("Falha na conexão", error_code=500, endpoint="/api/tickets")
```

### 2. Uso com Decoradores

```python
class GLPIService:
    def __init__(self):
        self.structured_logger = create_glpi_logger()
    
    @log_api_call(structured_logger)
    @log_performance(structured_logger, threshold_seconds=2.0)
    def get_tickets(self, status=None):
        # Implementação do método
        pass
```

## Configuração por Ambiente

### Desenvolvimento

```python
from config.logging_config import LoggingConfig

# Configuração para desenvolvimento
dev_config = LoggingConfig.development()
dev_config.configure()
```

### Produção

```python
from config.logging_config import LoggingConfig

# Configuração para produção
prod_config = LoggingConfig.production(
    log_file_path="/var/log/glpi_dashboard/app.log"
)
prod_config.configure()
```

### Teste

```python
from config.logging_config import LoggingConfig

# Configuração para testes
test_config = LoggingConfig.testing()
test_config.configure()
```

## Integração com Serviços de Monitoramento

### ELK Stack (Elasticsearch, Logstash, Kibana)

#### 1. Configuração do Logstash

Crie um arquivo `logstash.conf`:

```ruby
input {
  file {
    path => "/var/log/glpi_dashboard/*.log"
    start_position => "beginning"
    codec => "json"
  }
}

filter {
  if [logger_name] == "glpi_service" {
    mutate {
      add_tag => ["glpi", "api"]
    }
  }
  
  if [level] == "ERROR" {
    mutate {
      add_tag => ["error"]
    }
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "glpi-dashboard-%{+YYYY.MM.dd}"
  }
}
```

#### 2. Configuração no Código

```python
from config.logging_config import MonitoringIntegration

# Configurar integração ELK
elk_config = MonitoringIntegration.elk_stack(
    elasticsearch_host="localhost:9200",
    index_pattern="glpi-dashboard"
)

# Aplicar configuração
elk_config.configure_elk_integration()
```

### Grafana Loki

#### 1. Configuração do Promtail

Crie um arquivo `promtail.yml`:

```yaml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://localhost:3100/loki/api/v1/push

scrape_configs:
  - job_name: glpi-dashboard
    static_configs:
      - targets:
          - localhost
        labels:
          job: glpi-dashboard
          __path__: /var/log/glpi_dashboard/*.log
    pipeline_stages:
      - json:
          expressions:
            level: level
            logger: logger_name
            message: message
            timestamp: timestamp
      - labels:
          level:
          logger:
```

#### 2. Configuração no Código

```python
from config.logging_config import MonitoringIntegration

# Configurar integração Loki
loki_config = MonitoringIntegration.grafana_loki(
    loki_url="http://localhost:3100",
    service_name="glpi-dashboard",
    environment="production"
)

# Aplicar configuração
loki_config.configure_loki_integration()
```

### Prometheus

#### 1. Configuração de Métricas

```python
from config.logging_config import MonitoringIntegration

# Configurar métricas Prometheus
prometheus_config = MonitoringIntegration.prometheus(
    pushgateway_url="http://localhost:9091",
    job_name="glpi-dashboard"
)

# Aplicar configuração
prometheus_config.configure_prometheus_integration()
```

#### 2. Exemplo de Uso com Métricas

```python
from prometheus_client import Counter, Histogram, push_to_gateway

# Métricas definidas na configuração
api_calls_total = Counter('api_calls_total', 'Total API calls', ['method', 'endpoint', 'status'])
api_duration = Histogram('api_call_duration_seconds', 'API call duration')

@log_api_call(logger)
def api_method():
    with api_duration.time():
        # Implementação
        api_calls_total.labels(method='GET', endpoint='/tickets', status='200').inc()
        return result
```

## Configuração de Variáveis de Ambiente

Crie um arquivo `.env` para configurações:

```bash
# Logging
LOG_LEVEL=INFO
LOG_FILE_PATH=/var/log/glpi_dashboard/app.log
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5

# ELK Stack
ELASTICSEARCH_HOST=localhost:9200
ELASTICSEARCH_INDEX=glpi-dashboard

# Grafana Loki
LOKI_URL=http://localhost:3100
LOKI_SERVICE_NAME=glpi-dashboard

# Prometheus
PROMETHEUS_PUSHGATEWAY_URL=http://localhost:9091
PROMETHEUS_JOB_NAME=glpi-dashboard
```

## Exemplos de Logs Gerados

### Log de Informação

```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "INFO",
  "logger_name": "glpi_service",
  "message": "Tickets retrieved successfully",
  "extra": {
    "user_id": 123,
    "endpoint": "/api/tickets",
    "count": 25,
    "execution_time": 0.45
  }
}
```

### Log de API Call

```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "INFO",
  "logger_name": "glpi_service",
  "message": "API call completed",
  "extra": {
    "function_name": "get_tickets",
    "parameters": {
      "status": "open",
      "limit": 10
    },
    "execution_time": 1.23,
    "status": "success",
    "result_size": 1024
  }
}
```

### Log de Erro

```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "ERROR",
  "logger_name": "glpi_service",
  "message": "API call failed",
  "extra": {
    "function_name": "authenticate",
    "error_type": "ConnectionError",
    "error_message": "Connection timeout",
    "endpoint": "/api/initSession",
    "retry_count": 3
  }
}
```

## Queries Úteis para Análise

### Elasticsearch/Kibana

```json
# Buscar erros nas últimas 24 horas
{
  "query": {
    "bool": {
      "must": [
        {"term": {"level": "ERROR"}},
        {"range": {"timestamp": {"gte": "now-24h"}}}
      ]
    }
  }
}

# Buscar chamadas de API lentas (> 2 segundos)
{
  "query": {
    "bool": {
      "must": [
        {"exists": {"field": "extra.execution_time"}},
        {"range": {"extra.execution_time": {"gt": 2.0}}}
      ]
    }
  }
}
```

### Grafana Loki

```logql
# Logs de erro
{job="glpi-dashboard"} | json | level="ERROR"

# Chamadas de API por endpoint
{job="glpi-dashboard"} | json | extra_endpoint!="" | count by (extra_endpoint)

# Performance por função
{job="glpi-dashboard"} | json | extra_execution_time > 1.0
```

## Troubleshooting

### Problemas Comuns

1. **Logs não aparecem no Elasticsearch**
   - Verificar se o Logstash está rodando
   - Verificar permissões do arquivo de log
   - Verificar formato JSON dos logs

2. **Performance degradada**
   - Ajustar nível de log para produção (INFO ou WARNING)
   - Configurar rotação de logs adequada
   - Monitorar uso de disco

3. **Logs duplicados**
   - Verificar configuração de handlers
   - Evitar múltiplas inicializações do logger

### Comandos de Diagnóstico

```bash
# Verificar formato dos logs
tail -f /var/log/glpi_dashboard/app.log | jq .

# Contar logs por nível
grep -o '"level":"[^"]*"' /var/log/glpi_dashboard/app.log | sort | uniq -c

# Verificar logs de erro
grep '"level":"ERROR"' /var/log/glpi_dashboard/app.log | jq .
```

## Melhores Práticas

1. **Use níveis de log apropriados**:
   - DEBUG: Informações detalhadas para desenvolvimento
   - INFO: Informações gerais sobre operações
   - WARNING: Situações que merecem atenção
   - ERROR: Erros que não impedem a execução
   - CRITICAL: Erros críticos que podem parar a aplicação

2. **Inclua contexto relevante**:
   - IDs de usuário, sessão, transação
   - Endpoints e parâmetros de API
   - Tempos de execução
   - Códigos de erro específicos

3. **Evite logs excessivos**:
   - Use throttling para logs repetitivos
   - Configure níveis apropriados por ambiente
   - Monitore volume de logs

4. **Segurança**:
   - Nunca logue senhas ou tokens
   - Mascare dados sensíveis
   - Use campos específicos para dados seguros

## Suporte

Para dúvidas ou problemas:
1. Consulte os testes em `tests/test_structured_logger.py`
2. Verifique a configuração em `config/logging_config.py`
3. Execute os testes: `python -m pytest tests/test_structured_logger.py -v`
