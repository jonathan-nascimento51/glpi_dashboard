# Dashboard Domain

Este domínio contém todos os componentes, tipos, hooks e serviços relacionados ao dashboard do sistema GLPI.

## Estrutura

```
dashboard/
├── components/           # Componentes React refatorados
│   ├── DashboardCard.tsx        # Cards principais do dashboard
│   ├── MetricsGrid.tsx          # Grid de métricas por nível
│   ├── TechnicianRanking.tsx    # Ranking de técnicos
│   ├── SystemStatus.tsx        # Status do sistema
│   ├── *.stories.tsx           # Stories do Storybook
│   └── index.ts                # Exportações dos componentes
├── hooks/               # Hooks customizados
│   └── useDashboard.ts         # Hook principal do dashboard
├── services/            # Serviços de API
│   └── dashboardService.ts     # Chamadas de API do dashboard
├── types/               # Definições de tipos
│   └── dashboardTypes.ts       # Tipos TypeScript
└── index.ts             # Exportações do domínio
```

## Componentes

### DashboardCard

Componente base para exibir métricas individuais com suporte a:
- Diferentes variantes (default, primary, success, warning, danger)
- Indicadores de tendência (up, down, stable)
- Estados de carregamento e erro
- Animações com framer-motion

```tsx
import { DashboardCard } from '@/domains/dashboard';

<DashboardCard
  title="Total de Tickets"
  value="1,234"
  subtitle="Últimas 24 horas"
  icon="Ticket"
  variant="primary"
  trend="up"
  trendValue="+12%"
/>
```

### LevelCard

Componente especializado para exibir métricas por nível de suporte (N1-N4):

```tsx
import { LevelCard } from '@/domains/dashboard';

<LevelCard
  level="N1"
  total={145}
  resolved={98}
  pending={47}
  responseTime="2.3h"
/>
```

### MetricsGrid

Grid responsivo que organiza e exibe métricas do dashboard:
- Resumo geral
- Métricas por nível (N1-N4)
- Distribuição por status
- Versão compacta disponível

```tsx
import { MetricsGrid } from '@/domains/dashboard';

<MetricsGrid
  data={metricsData}
  showCompact={false}
  isLoading={false}
  hasError={false}
/>
```

### TechnicianRanking

Componentes para exibir ranking de técnicos:
- `TechnicianRankingComponent`: Versão completa
- `CompactTechnicianRanking`: Versão compacta (top 3)

```tsx
import { TechnicianRankingComponent, CompactTechnicianRanking } from '@/domains/dashboard';

// Versão completa
<TechnicianRankingComponent data={rankingData} />

// Versão compacta
<CompactTechnicianRanking data={rankingData} />
```

### SystemStatus

Componentes para exibir status do sistema:
- `SystemStatusComponent`: Versão completa com detalhes
- `CompactSystemStatus`: Versão compacta

```tsx
import { SystemStatusComponent, CompactSystemStatus } from '@/domains/dashboard';

// Versão completa
<SystemStatusComponent data={statusData} />

// Versão compacta
<CompactSystemStatus data={statusData} />
```

## Hooks

### useDashboard

Hook principal que gerencia o estado do dashboard:

```tsx
import { useDashboard } from '@/domains/dashboard';

const {
  metrics,
  ranking,
  systemStatus,
  isLoading,
  error,
  refetch,
  lastUpdated
} = useDashboard({
  refreshInterval: 30000, // 30 segundos
  filters: { dateRange: 'last7days' }
});
```

## Serviços

### dashboardService

Serviço que encapsula as chamadas de API:

```tsx
import { dashboardService } from '@/domains/dashboard';

// Buscar métricas
const metrics = await dashboardService.fetchMetrics(filters);

// Buscar ranking de técnicos
const ranking = await dashboardService.fetchTechnicianRanking();

// Buscar status do sistema
const status = await dashboardService.fetchSystemStatus();

// Health check
const health = await dashboardService.healthCheck();
```

## Tipos

Todos os tipos TypeScript estão definidos em `dashboardTypes.ts`:

- `DashboardCardProps`
- `LevelCardProps`
- `MetricsData`
- `TechnicianRankingData`
- `SystemStatusData`
- `DashboardFilters`
- `TrendDirection`
- E muitos outros...

## Estados de UI

Todos os componentes suportam estados consistentes:

- **Loading**: Skeleton/spinner durante carregamento
- **Error**: Mensagem de erro com opção de retry
- **Empty**: Estado vazio quando não há dados
- **Success**: Exibição normal dos dados

Estes estados são gerenciados pelo `StateWrapper` do domínio `shared`.

## Storybook

Todos os componentes possuem stories completas no Storybook:

```bash
npm run storybook
```

Navegue para a seção "Dashboard" para ver todos os componentes e seus estados.

## Animações

Os componentes utilizam `framer-motion` para animações suaves:

- Fade in/out
- Slide transitions
- Hover effects
- Loading states
- Stagger animations em listas

## Responsividade

Todos os componentes são responsivos e se adaptam a:

- Mobile (375px+)
- Tablet (768px+)
- Desktop (1024px+)
- Large screens (1200px+)

## Acessibilidade

- Suporte a screen readers
- Navegação por teclado
- Contraste adequado
- Labels descritivos
- Estados de foco visíveis

## Performance

- Lazy loading de componentes
- Memoização com React.memo
- Otimização de re-renders
- Debounce em filtros
- Cache de dados da API

## Testes

Para executar os testes dos componentes:

```bash
npm run test:dashboard
```

Os testes cobrem:
- Renderização de componentes
- Estados de loading/error/empty
- Interações do usuário
- Integração com hooks
- Responsividade

## Migração dos Componentes Antigos

Os componentes antigos em `src/components/dashboard/` foram refatorados e movidos para este domínio. Para migrar:

1. Substitua imports antigos:
   ```tsx
   // Antes
   import { KpiCard } from '@/components/dashboard/KpiCard';
   
   // Depois
   import { DashboardCard } from '@/domains/dashboard';
   ```

2. Atualize props conforme novos tipos
3. Remova componentes antigos após migração completa

## Contribuindo

1. Siga os padrões de código estabelecidos
2. Adicione stories para novos componentes
3. Mantenha tipos TypeScript atualizados
4. Teste responsividade e acessibilidade
5. Documente mudanças significativas

## Roadmap

- [ ] Adicionar mais variantes de componentes
- [ ] Implementar temas dark/light
- [ ] Adicionar mais animações
- [ ] Melhorar performance com virtualization
- [ ] Adicionar suporte a PWA
- [ ] Implementar offline-first