# GLPI Dashboard API Documentation

## Visão Geral

Esta documentação fornece informações completas sobre a API do GLPI Dashboard, incluindo todos os endpoints disponíveis, schemas de dados, exemplos de uso e guias de integração.

## Documentação Interativa (Swagger UI)

### Acesso Local
Quando o servidor estiver rodando localmente, acesse:
- **Swagger UI**: http://localhost:5000/api/docs
- **Especificação OpenAPI**: http://localhost:5000/api/openapi.yaml

### Acesso em Produção
- **Swagger UI**: https://api.glpi-dashboard.com/api/docs
- **Especificação OpenAPI**: https://api.glpi-dashboard.com/api/openapi.yaml

## Endpoints Principais

### 📊 Métricas
- `GET /api/metrics` - Métricas gerais do dashboard
- `GET /api/metrics/filtered` - Métricas com filtros de data

### 👥 Técnicos
- `GET /api/technicians/ranking` - Ranking de técnicos por performance

### 🎫 Tickets
- `GET /api/tickets/new` - Tickets novos no sistema

### 🚨 Alertas
- `GET /api/alerts` - Alertas do sistema

### 📈 Performance
- `GET /api/performance/stats` - Estatísticas de performance

### 🔧 Sistema
- `GET /api/status` - Status geral do sistema
- `GET /api/health` - Health check da API
- `GET /api/filter-types` - Tipos de filtros disponíveis

## Autenticação

A API utiliza autenticação baseada em tokens GLPI. Configure as seguintes variáveis de ambiente:

```bash
GLPI_URL=https://seu-glpi.com/apirest.php
GLPI_USER_TOKEN=seu_user_token_aqui
GLPI_APP_TOKEN=seu_app_token_aqui
```

### Obtendo Tokens GLPI

1. **User Token**: Acesse seu perfil no GLPI → Configurações → Tokens de API
2. **App Token**: Configuração → Geral → API → Tokens de aplicação

## Filtros de Data

A API suporta três tipos de filtros de data:

- `creation`: Filtro por data de criação (padrão)
- `modification`: Filtro por data de modificação  
- `current_status`: Filtro por status atual

### Exemplo de Uso

```bash
# Métricas dos últimos 7 dias por data de criação
GET /api/metrics/filtered?data_inicio=2024-01-01&data_fim=2024-01-07&tipo_filtro=creation

# Métricas por data de modificação
GET /api/metrics/filtered?data_inicio=2024-01-01&data_fim=2024-01-07&tipo_filtro=modification
```

## Schemas de Dados

### DashboardMetrics
```json
{
  "novos": 0,
  "pendentes": 0,
  "progresso": 0,
  "resolvidos": 0,
  "total": 0,
  "niveis": {
    "n1": {"novos": 0, "pendentes": 0, "progresso": 0, "resolvidos": 0},
    "n2": {"novos": 0, "pendentes": 0, "progresso": 0, "resolvidos": 0},
    "n3": {"novos": 0, "pendentes": 0, "progresso": 0, "resolvidos": 0},
    "n4": {"novos": 0, "pendentes": 0, "progresso": 0, "resolvidos": 0}
  },
  "tendencias": {
    "novos": "0",
    "pendentes": "0", 
    "progresso": "0",
    "resolvidos": "0"
  },
  "filters_applied": {
    "data_inicio": "2024-01-01",
    "data_fim": "2024-01-07"
  },
  "timestamp": "2024-01-01T12:00:00Z",
  "tempo_execucao": 1.23
}
```

### TechnicianRanking
```json
{
  "ranking": [
    {
      "tecnico_id": 123,
      "nome": "João Silva",
      "tickets_resolvidos": 45,
      "tempo_medio_resolucao": 2.5,
      "satisfacao_cliente": 4.8,
      "posicao": 1
    }
  ],
  "periodo": {
    "inicio": "2024-01-01",
    "fim": "2024-01-31"
  },
  "total_tecnicos": 10
}
```

## Cache

A API implementa cache inteligente com TTL configurável:

- **Métricas gerais**: 5 minutos
- **Ranking de técnicos**: 15 minutos
- **Alertas**: 2 minutos
- **Health checks**: 1 minuto

## Códigos de Status HTTP

- `200` - Sucesso
- `400` - Erro de validação nos parâmetros
- `401` - Não autorizado (token inválido)
- `404` - Recurso não encontrado
- `429` - Rate limit excedido
- `500` - Erro interno do servidor
- `503` - Serviço indisponível

## Rate Limiting

A API implementa rate limiting para proteger contra abuso:

- **Limite geral**: 1000 requisições por hora por IP
- **Endpoints de métricas**: 100 requisições por minuto
- **Health checks**: 60 requisições por minuto

## Exemplos de Integração

### Python
```python
import requests

base_url = "http://localhost:5000/api"

# Obter métricas gerais
response = requests.get(f"{base_url}/metrics")
metrics = response.json()

# Obter métricas filtradas
params = {
    "data_inicio": "2024-01-01",
    "data_fim": "2024-01-31",
    "tipo_filtro": "creation"
}
response = requests.get(f"{base_url}/metrics/filtered", params=params)
filtered_metrics = response.json()
```

### JavaScript
```javascript
const baseUrl = 'http://localhost:5000/api';

// Obter métricas gerais
fetch(`${baseUrl}/metrics`)
  .then(response => response.json())
  .then(data => console.log(data));

// Obter ranking de técnicos
fetch(`${baseUrl}/technicians/ranking`)
  .then(response => response.json())
  .then(data => console.log(data));
```

### cURL
```bash
# Métricas gerais
curl -X GET "http://localhost:5000/api/metrics"

# Métricas filtradas
curl -X GET "http://localhost:5000/api/metrics/filtered?data_inicio=2024-01-01&data_fim=2024-01-31"

# Health check
curl -X GET "http://localhost:5000/api/health"
```

## Monitoramento e Observabilidade

A API inclui métricas Prometheus para monitoramento:

- Tempo de resposta por endpoint
- Taxa de erro por endpoint
- Número de requisições por endpoint
- Status de saúde dos serviços

### Métricas Prometheus
```
# Tempo de resposta
api_request_duration_seconds{method="GET",endpoint="/metrics"}

# Taxa de erro
api_request_errors_total{method="GET",endpoint="/metrics",status="500"}

# Número de requisições
api_requests_total{method="GET",endpoint="/metrics"}
```

## Troubleshooting

### Problemas Comuns

1. **Erro 401 - Não autorizado**
   - Verifique se os tokens GLPI estão configurados corretamente
   - Confirme se os tokens não expiraram

2. **Erro 503 - Serviço indisponível**
   - Verifique a conectividade com o servidor GLPI
   - Confirme se o GLPI está respondendo

3. **Timeout nas requisições**
   - Verifique a latência de rede com o GLPI
   - Considere aumentar o timeout da aplicação

### Logs

Os logs da API estão disponíveis em:
- Desenvolvimento: Console
- Produção: `/var/log/glpi-dashboard/api.log`

## Suporte

Para suporte técnico:
- Email: support@glpi-dashboard.com
- Issues: GitHub Repository
- Documentação: Esta documentação

## Changelog

### v1.0.0
- Implementação inicial da API
- Endpoints básicos de métricas
- Documentação OpenAPI/Swagger
- Sistema de cache
- Rate limiting
- Monitoramento Prometheus