# Serviços de API - Frontend

Este diretório contém a implementação refatorada dos serviços de API do frontend, com foco em modularidade, testabilidade e configuração via variáveis de ambiente.

## Estrutura dos Arquivos

### `httpClient.ts`
Cliente HTTP centralizado baseado no Axios com:
- **Configuração via variáveis de ambiente**: URL base, timeout, retry, tokens de autenticação
- **Interceptadores de requisição**: Autenticação automática e logging
- **Interceptadores de resposta**: Tratamento de erros e retry automático
- **Funções utilitárias**: GET, POST, PUT, DELETE, PATCH, HEAD

### `api.ts`
Serviços de API específicos do domínio:
- **apiService**: Métodos para métricas, status do sistema, ranking de técnicos, etc.
- **Integração com cache**: Sistema de cache inteligente
- **Monitoramento de performance**: Métricas de tempo de resposta
- **Fallbacks**: Dados de fallback em caso de falha

### `cache.ts`
Sistema de cache para otimização de performance:
- Cache em memória com TTL configurável
- Invalidação automática
- Métricas de hit/miss

## Configuração via Variáveis de Ambiente

### Variáveis Obrigatórias
```env
VITE_API_BASE_URL=http://localhost:5000/api
```

### Variáveis Opcionais
```env
# Configuração de Timeout e Retry
VITE_API_TIMEOUT=10000
VITE_API_RETRY_ATTEMPTS=3
VITE_API_RETRY_DELAY=1000

# Tokens de Autenticação
VITE_API_TOKEN=your-api-token
VITE_APP_TOKEN=your-app-token
VITE_USER_TOKEN=your-user-token

# Configurações de Debug
VITE_LOG_LEVEL=info
VITE_SHOW_API_CALLS=true
VITE_SHOW_PERFORMANCE=true
VITE_SHOW_CACHE_HITS=true
```

## Uso dos Serviços

### Uso Direto do httpClient
```typescript
import { httpClient } from './services/httpClient';

// GET request
const response = await httpClient.get('/endpoint');

// POST request
const response = await httpClient.post('/endpoint', data);
```

### Uso dos Serviços de API
```typescript
import { apiService } from './services/api';

// Buscar métricas
const metrics = await apiService.getMetrics({
  startDate: '2024-01-01',
  endDate: '2024-01-31'
});

// Verificar status do sistema
const status = await apiService.getSystemStatus();
```

### Uso com Hook useApi
```typescript
import { useApi } from '../hooks/useApi';
import { apiService } from '../services/api';

function MyComponent() {
  const { data, loading, error, execute } = useApi(apiService.getMetrics);

  const handleLoadData = () => {
    execute({ startDate: '2024-01-01', endDate: '2024-01-31' });
  };

  if (loading) return <div>Carregando...</div>;
  if (error) return <div>Erro: {error}</div>;
  if (data) return <div>{JSON.stringify(data)}</div>;

  return <button onClick={handleLoadData}>Carregar Dados</button>;
}
```

### Hooks Especializados
```typescript
import { useMetrics, useSystemStatus } from '../hooks/useApi';

// Auto-executar ao montar o componente
const { data: metrics } = useMetrics({ autoExecute: true });

// Executar quando dependências mudarem
const { data: status } = useSystemStatus({
  autoExecute: true,
  dependencies: [dateRange]
});
```

## Tratamento de Erros

O sistema trata automaticamente diferentes tipos de erro:

- **Timeout**: Retry automático com backoff exponencial
- **401 Unauthorized**: Log de erro de autenticação
- **403 Forbidden**: Log de erro de autorização
- **404 Not Found**: Log de recurso não encontrado
- **429 Too Many Requests**: Retry com delay
- **5xx Server Errors**: Retry automático
- **Erros de Rede**: Retry automático

## Sistema de Cache

- **Cache automático**: Respostas são automaticamente cacheadas
- **TTL configurável**: Tempo de vida configurável por endpoint
- **Invalidação**: Cache pode ser limpo manualmente
- **Métricas**: Estatísticas de hit/miss disponíveis

## Monitoramento de Performance

- **Métricas de tempo**: Tempo de resposta de cada requisição
- **Logging condicional**: Baseado em variáveis de ambiente
- **Estatísticas de cache**: Hit rate e miss rate
- **Alertas de performance**: Para requisições lentas

## Testes

Todos os serviços possuem testes abrangentes:

```bash
# Executar todos os testes
npm test

# Executar testes específicos
npm run test:run -- src/hooks/__tests__/useApi.test.tsx
npm run test:run -- src/components/__tests__/ApiConsumer.test.tsx
npm run test:run -- src/__tests__/integration/ApiIntegration.test.tsx
```

## Migração de Código Existente

Para migrar código existente:

1. **Substitua imports diretos do axios**:
   ```typescript
   // Antes
   import axios from 'axios';
   
   // Depois
   import { httpClient } from './services/httpClient';
   ```

2. **Use os serviços de API**:
   ```typescript
   // Antes
   const response = await axios.get('/api/metrics');
   
   // Depois
   const metrics = await apiService.getMetrics();
   ```

3. **Implemente hooks para gerenciamento de estado**:
   ```typescript
   // Antes
   const [data, setData] = useState(null);
   const [loading, setLoading] = useState(false);
   
   // Depois
   const { data, loading, error, execute } = useApi(apiService.getMetrics);
   ```

## Benefícios da Refatoração

- ✅ **Configuração centralizada** via variáveis de ambiente
- ✅ **Tratamento de erros robusto** com retry automático
- ✅ **Sistema de cache inteligente** para otimização
- ✅ **Monitoramento de performance** integrado
- ✅ **Testabilidade aprimorada** com mocks e testes de integração
- ✅ **Hooks reutilizáveis** para gerenciamento de estado
- ✅ **Autenticação automática** via tokens
- ✅ **Logging condicional** para debug
- ✅ **Compatibilidade mantida** com código existente