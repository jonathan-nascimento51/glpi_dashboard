# Implementação do Filtro de Data - Dashboard GLPI

## Visão Geral

Este documento descreve como implementar o filtro de data para as métricas do "Modo TV" do dashboard GLPI, permitindo que os usuários filtrem os dados por qualquer período de tempo.

## Componentes Implementados

### 1. Frontend

#### `DateRangeFilter.tsx`
- Componente React para seleção de período
- Opções predefinidas: Hoje, 7 dias, 30 dias, Personalizado
- Interface intuitiva com calendário para datas customizadas

#### `SimplifiedDashboard.tsx` (Atualizado)
- Integração do filtro de data no cabeçalho
- Passa parâmetros de data para o hook `useDashboard`

#### `useDashboard.ts` (Atualizado)
- Gerencia estado do filtro de data
- Chama API com parâmetros de data
- Período padrão: últimos 30 dias

#### `api.ts` (Atualizado)
- Função `getMetrics()` aceita parâmetro `dateRange`
- Processa dados filtrados usando utilitários GLPI

### 2. Utilitários GLPI

#### `glpiDateFilter.ts`
- Funções para construir queries da API GLPI
- Processamento de dados por status e nível
- Formatação de datas para o padrão GLPI

## Como Funciona

### 1. Seleção de Data (Frontend)
```typescript
// Usuário seleciona período no DateRangeFilter
const dateRange = {
  startDate: '2024-01-01',
  endDate: '2024-01-31'
};
```

### 2. Construção da Query GLPI
```typescript
// Utiliza buildTicketSearchURL para criar URL da API
const searchURL = buildTicketSearchURL(
  '2024-01-01',
  '2024-01-31',
  [123, 456], // IDs dos grupos (opcional)
  15,         // ID do campo date_creation
  71          // ID do campo groups_id
);

// Resultado:
// /apirest.php/search/Ticket?
// is_deleted=0&
// glpilist_limit=10000&
// criteria[0][field]=15&criteria[0][searchtype]=morethan&criteria[0][value]=2024-01-01%2000:00:00&
// criteria[1][field]=15&criteria[1][searchtype]=lessthan&criteria[1][value]=2024-01-31%2023:59:59
```

### 3. Processamento dos Dados
```typescript
// Processa tickets retornados pela API
const statusCounts = processTicketsByStatus(tickets);
const levelCounts = processTicketsByLevel(tickets);

// Retorna métricas organizadas
return {
  novos: statusCounts.new,
  progresso: statusCounts.assigned + statusCounts.planned,
  pendentes: statusCounts.waiting,
  resolvidos: statusCounts.solved + statusCounts.closed,
  niveis: {
    n1: levelCounts.n1,
    n2: levelCounts.n2,
    n3: levelCounts.n3,
    n4: levelCounts.n4
  }
};
```

## Implementação no Backend

### 1. Endpoint da API

O backend deve implementar o endpoint `/api/metrics` que aceita parâmetros de data:

```javascript
// Exemplo em Node.js/Express
app.get('/api/metrics', async (req, res) => {
  const { start_date, end_date } = req.query;
  
  try {
    // Construir query GLPI
    const searchURL = buildTicketSearchURL(
      start_date,
      end_date,
      selectedGroupIds,
      dateFieldId,
      groupFieldId
    );
    
    // Fazer requisição para GLPI
    const response = await fetch(`${GLPI_URL}${searchURL}`, {
      headers: {
        'Session-Token': sessionToken,
        'App-Token': appToken
      }
    });
    
    const data = await response.json();
    const tickets = data.data || [];
    
    // Processar dados
    const metrics = {
      total: tickets.length,
      novos: tickets.filter(t => t.status === 1).length,
      progresso: tickets.filter(t => [2, 3].includes(t.status)).length,
      pendentes: tickets.filter(t => t.status === 4).length,
      resolvidos: tickets.filter(t => [5, 6].includes(t.status)).length,
      rawTickets: tickets // Para processamento adicional no frontend
    };
    
    res.json({
      success: true,
      data: metrics
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});
```

### 2. Descobrir IDs dos Campos

Antes de implementar, é necessário descobrir os IDs corretos dos campos:

```javascript
// Buscar opções de pesquisa disponíveis
const searchOptions = await fetch(`${GLPI_URL}/apirest.php/listSearchOptions/Ticket`, {
  headers: {
    'Session-Token': sessionToken,
    'App-Token': appToken
  }
});

const options = await searchOptions.json();

// Procurar pelos campos necessários:
// - date_creation (geralmente ID 15)
// - groups_id (geralmente ID 71)
// - status (geralmente ID 12)
console.log('Campos disponíveis:', options);
```

### 3. Configuração de Sessão GLPI

```javascript
// Inicializar sessão GLPI
const initSession = await fetch(`${GLPI_URL}/apirest.php/initSession`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'App-Token': APP_TOKEN
  },
  body: JSON.stringify({
    login: GLPI_USER,
    password: GLPI_PASSWORD
  })
});

const session = await initSession.json();
const sessionToken = session.session_token;
```

## Mapeamento de Status GLPI

| Status GLPI | Valor | Descrição |
|-------------|-------|----------|
| New | 1 | Novos |
| Processing (assigned) | 2 | Em Progresso |
| Planned | 3 | Planejados |
| Pending | 4 | Pendentes |
| Solved | 5 | Resolvidos |
| Closed | 6 | Fechados |

## Mapeamento de Níveis

O mapeamento de níveis deve ser configurado conforme a estrutura organizacional:

```typescript
function determineTicketLevel(ticket: any): string {
  const groupId = ticket.groups_id_assign || ticket.groups_id;
  
  // Exemplo de mapeamento - ajustar conforme necessário
  if (groupId >= 1 && groupId <= 10) return 'n1';   // Nível 1
  if (groupId >= 11 && groupId <= 20) return 'n2';  // Nível 2
  if (groupId >= 21 && groupId <= 30) return 'n3';  // Nível 3
  return 'n4';                                       // Nível 4
}
```

## Considerações Importantes

### 1. Performance
- Limite de resultados: `glpilist_limit=10000`
- Para volumes maiores, implementar paginação
- Cache de resultados para períodos frequentes

### 2. Timezone
- GLPI armazena datas em UTC ou timezone do servidor
- Sincronizar formatação de datas com configuração do servidor

### 3. Segurança
- Validar parâmetros de data no backend
- Limitar períodos máximos de consulta
- Implementar rate limiting

### 4. Fallback
- Sempre ter dados de fallback em caso de erro
- Logs detalhados para debugging
- Tratamento de erros de conexão

## Exemplo de Uso Completo

```typescript
// No componente React
const Dashboard = () => {
  const [dateRange, setDateRange] = useState({
    startDate: '2024-01-01',
    endDate: '2024-01-31'
  });
  
  const { metrics, isLoading } = useDashboard(dateRange);
  
  return (
    <div>
      <DateRangeFilter 
        dateRange={dateRange}
        onDateRangeChange={setDateRange}
      />
      <SimplifiedDashboard 
        metrics={metrics}
        isLoading={isLoading}
      />
    </div>
  );
};
```

## Próximos Passos

1. **Backend**: Implementar endpoint `/api/metrics` com suporte a filtros de data
2. **GLPI**: Descobrir IDs corretos dos campos usando `listSearchOptions`
3. **Testes**: Validar funcionamento com diferentes períodos
4. **Performance**: Otimizar queries para grandes volumes de dados
5. **UI/UX**: Ajustar interface conforme feedback dos usuários

## Recursos Adicionais

- [Documentação GLPI REST API](https://github.com/glpi-project/glpi/blob/master/apirest.md)
- [GLPI Search Engine](https://glpi-developer-documentation.readthedocs.io/en/master/devapi/search.html)
- [Fórum GLPI](https://forum.glpi-project.org/)