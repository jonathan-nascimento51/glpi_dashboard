# Contratos de API - GLPI Dashboard

## 📋 Visão Geral

Este documento define os contratos de API do GLPI Dashboard, incluindo endpoints, schemas de requisição/resposta, códigos de status e exemplos de uso.

## 🔗 Base URL

- **Desenvolvimento**: `http://localhost:5000/api`
- **Produção**: `https://dashboard.example.com/api`

## 📊 Endpoints Principais

### 1. Métricas do Dashboard

#### `GET /api/metrics`

**Descrição**: Retorna métricas agregadas dos tickets do GLPI

**Parâmetros de Query**:

```typescript
interface MetricsParams {
  startDate?: string;     // ISO 8601 date (YYYY-MM-DD)
  endDate?: string;       // ISO 8601 date (YYYY-MM-DD)
  status?: string[];      // Array de status de tickets
  priority?: string[];    // Array de prioridades
  level?: string[];       // Array de níveis (n1, n2, n3, n4)
  technician?: string[];  // Array de IDs de técnicos
  category?: string[];    // Array de categorias
  limit?: number;         // Limite de resultados (padrão: 1000)
}
```

**Exemplo de Requisição**:

```bash
GET /api/metrics?startDate=2024-01-01&endDate=2024-01-31&level=n1,n2
```

**Schema de Resposta**:

```typescript
interface MetricsResponse {
  correlation_id: string;
  timestamp: string;
  data: {
    total: number;
    novos: number;
    pendentes: number;
    progresso: number;
    resolvidos: number;
    niveis: {
      n1: number;
      n2: number;
      n3: number;
      n4: number;
    };
    trends?: {
      total_change: number;
      percentage_change: number;
      period_comparison: string;
    };
  };
  metadata: {
    cache_hit: boolean;
    execution_time_ms: number;
    glpi_calls: number;
    filters_applied: string[];
  };
}
```

**Exemplo de Resposta**:

```json
{
  "correlation_id": "req_123456789",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "total": 150,
    "novos": 25,
    "pendentes": 45,
    "progresso": 60,
    "resolvidos": 20,
    "niveis": {
      "n1": 30,
      "n2": 45,
      "n3": 50,
      "n4": 25
    },
    "trends": {
      "total_change": 15,
      "percentage_change": 11.1,
      "period_comparison": "vs_previous_month"
    }
  },
  "metadata": {
    "cache_hit": true,
    "execution_time_ms": 45,
    "glpi_calls": 0,
    "filters_applied": ["date_range", "level"]
  }
}
```

**Códigos de Status**:
- `200` - Sucesso
- `400` - Parâmetros inválidos
- `500` - Erro interno do servidor
- `503` - GLPI indisponível

### 2. Ranking de Técnicos

#### `GET /api/ranking`

**Descrição**: Retorna ranking de técnicos por performance

**Parâmetros de Query**:

```typescript
interface RankingParams {
  startDate?: string;
  endDate?: string;
  metric?: 'resolved' | 'response_time' | 'satisfaction';
  limit?: number;         // Padrão: 10
  level?: string[];
}
```

**Schema de Resposta**:

```typescript
interface RankingResponse {
  correlation_id: string;
  timestamp: string;
  data: {
    ranking: Array<{
      technician_id: number;
      technician_name: string;
      score: number;
      tickets_resolved: number;
      avg_response_time: number;
      satisfaction_rate: number;
      level: string;
      position: number;
    }>;
    summary: {
      total_technicians: number;
      avg_score: number;
      top_performer: string;
    };
  };
  metadata: {
    cache_hit: boolean;
    execution_time_ms: number;
    metric_used: string;
  };
}
```

### 3. Status do Sistema

#### `GET /api/health`

**Descrição**: Verifica status de saúde do sistema

**Schema de Resposta**:

```typescript
interface HealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  services: {
    glpi: {
      status: 'up' | 'down';
      response_time_ms: number;
      last_check: string;
    };
    cache: {
      status: 'up' | 'down';
      memory_usage: number;
      hit_rate: number;
    };
    database: {
      status: 'up' | 'down';
      connections: number;
    };
  };
  version: string;
}
```

### 4. Configurações

#### `GET /api/config`

**Descrição**: Retorna configurações públicas do sistema

**Schema de Resposta**:

```typescript
interface ConfigResponse {
  api_version: string;
  features: {
    caching_enabled: boolean;
    metrics_enabled: boolean;
    ranking_enabled: boolean;
  };
  limits: {
    max_date_range_days: number;
    max_results_per_request: number;
    rate_limit_per_minute: number;
  };
  glpi: {
    version: string;
    available_fields: string[];
    supported_filters: string[];
  };
}
```

## 🔒 Autenticação

### Headers Obrigatórios

```http
Content-Type: application/json
X-Correlation-ID: req_123456789  # Opcional, gerado automaticamente se não fornecido
```

### Autenticação GLPI (Interna)

O backend gerencia automaticamente a autenticação com GLPI usando:

```http
App-Token: your_app_token
Authorization: user_token your_user_token
```

## ❌ Tratamento de Erros

### Schema de Erro Padrão

```typescript
interface ErrorResponse {
  error: {
    code: string;
    message: string;
    details?: any;
    correlation_id: string;
    timestamp: string;
  };
}
```

### Códigos de Erro Comuns

| Código | Descrição | Ação Recomendada |
|--------|-----------|-------------------|
| `INVALID_DATE_RANGE` | Intervalo de datas inválido | Verificar formato e lógica das datas |
| `GLPI_UNAVAILABLE` | GLPI não está respondendo | Tentar novamente em alguns minutos |
| `CACHE_ERROR` | Erro no sistema de cache | Requisição será processada sem cache |
| `RATE_LIMIT_EXCEEDED` | Muitas requisições | Aguardar antes de nova tentativa |
| `INVALID_FILTER` | Filtro não suportado | Verificar documentação de filtros |

### Exemplo de Resposta de Erro

```json
{
  "error": {
    "code": "INVALID_DATE_RANGE",
    "message": "Data de início deve ser anterior à data de fim",
    "details": {
      "start_date": "2024-01-31",
      "end_date": "2024-01-01"
    },
    "correlation_id": "req_123456789",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

## 📈 Rate Limiting

- **Limite padrão**: 100 requisições por minuto por IP
- **Headers de resposta**:
  - `X-RateLimit-Limit`: Limite total
  - `X-RateLimit-Remaining`: Requisições restantes
  - `X-RateLimit-Reset`: Timestamp do reset

## 🔄 Versionamento

- **Versão atual**: `v1`
- **Header de versão**: `API-Version: v1`
- **Compatibilidade**: Mantida por pelo menos 6 meses

## 📝 Logs e Observabilidade

### Correlation ID

Todas as requisições incluem um `correlation_id` para rastreamento:

```http
X-Correlation-ID: req_20240115_103000_abc123
```

### Métricas Expostas

- **Prometheus endpoint**: `/metrics`
- **Métricas principais**:
  - `http_requests_total{method, endpoint, status}`
  - `http_request_duration_seconds{method, endpoint}`
  - `glpi_api_calls_total{operation, status}`
  - `cache_operations_total{operation, result}`

## 🧪 Ambiente de Teste

### Mock Server

```bash
# Iniciar servidor mock
export FLASK_ENV=test
export USE_MOCK_DATA=true
python app.py
```

### Dados de Teste

O ambiente de teste usa dados sintéticos consistentes:

```json
{
  "metrics": {
    "total": 100,
    "novos": 20,
    "pendentes": 30,
    "progresso": 35,
    "resolvidos": 15
  }
}
```

## 📚 Exemplos de Uso

### JavaScript/TypeScript

```typescript
// Buscar métricas com filtros
const response = await fetch('/api/metrics?' + new URLSearchParams({
  startDate: '2024-01-01',
  endDate: '2024-01-31',
  level: 'n1,n2'
}));

const data: MetricsResponse = await response.json();
console.log(`Total de tickets: ${data.data.total}`);
```

### Python

```python
import requests

# Buscar ranking de técnicos
response = requests.get('http://localhost:5000/api/ranking', params={
    'startDate': '2024-01-01',
    'endDate': '2024-01-31',
    'metric': 'resolved',
    'limit': 5
})

data = response.json()
print(f"Top performer: {data['data']['summary']['top_performer']}")
```

### cURL

```bash
# Verificar status do sistema
curl -X GET "http://localhost:5000/api/health" \
  -H "Content-Type: application/json" \
  -H "X-Correlation-ID: test_123"
```

---

**AI Context Tags**: `api-contracts`, `rest-api`, `flask`, `glpi-integration`, `metrics`
**Related Files**: `backend/api/routes.py`, `backend/schemas/dashboard.py`, `frontend/src/services/api.ts`
**Last Updated**: 2024-01-15