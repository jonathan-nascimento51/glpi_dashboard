# Plano de Ação UX/UI - Dashboard GLPI

## Visão Geral

Este plano de ação detalha a implementação das melhorias identificadas na auditoria UX/UI, organizadas por prioridade e impacto. O foco está em maximizar o retorno sobre investimento através de ganhos rápidos seguidos por melhorias estruturais.

---

## 🚀 Fase 1: Ganhos Rápidos (2-3 semanas)

### Sprint 1 (Semana 1)

#### 1.1 Indicadores de Tendência nos KPIs
**Prioridade:** Alta | **Esforço:** 2-3 dias | **Impacto:** Alto

**Arquivos a modificar:**
- `src/components/ui/LevelMetricsGrid.tsx`
- `src/types/dashboard.ts`
- `src/components/ui/StatusCard.tsx`

**Implementação:**
```typescript
// Adicionar ao tipo de métricas
interface MetricData {
  value: number;
  trend: 'up' | 'down' | 'stable';
  percentageChange: number;
  previousValue?: number;
}

// Componente de tendência
const TrendIndicator = ({ trend, percentage }: TrendProps) => {
  const icons = {
    up: <ArrowUp className="text-green-500" />,
    down: <ArrowDown className="text-red-500" />,
    stable: <Minus className="text-gray-500" />
  };
  
  return (
    <div className="flex items-center gap-1">
      {icons[trend]}
      <span className={`text-sm ${
        trend === 'up' ? 'text-green-500' : 
        trend === 'down' ? 'text-red-500' : 'text-gray-500'
      }`}>
        {percentage > 0 ? '+' : ''}{percentage}%
      </span>
    </div>
  );
};
```

**Critérios de Aceitação:**
- [ ] Todos os KPIs principais mostram tendência visual
- [ ] Percentual de mudança é calculado corretamente
- [ ] Cores seguem convenção (verde=positivo, vermelho=negativo)
- [ ] Testes unitários passam

#### 1.2 Melhorar Contraste de Cores nos Badges
**Prioridade:** Média | **Esforço:** 1 dia | **Impacto:** Médio

**Arquivos a modificar:**
- `src/config/constants.ts`
- `src/components/ui/Badge.tsx`

**Implementação:**
```typescript
// Paleta de cores otimizada para contraste
export const STATUS_COLORS = {
  success: {
    bg: 'bg-green-100 dark:bg-green-900/30',
    text: 'text-green-800 dark:text-green-200',
    border: 'border-green-200 dark:border-green-700'
  },
  warning: {
    bg: 'bg-amber-100 dark:bg-amber-900/30',
    text: 'text-amber-800 dark:text-amber-200',
    border: 'border-amber-200 dark:border-amber-700'
  },
  error: {
    bg: 'bg-red-100 dark:bg-red-900/30',
    text: 'text-red-800 dark:text-red-200',
    border: 'border-red-200 dark:border-red-700'
  },
  info: {
    bg: 'bg-blue-100 dark:bg-blue-900/30',
    text: 'text-blue-800 dark:text-blue-200',
    border: 'border-blue-200 dark:border-blue-700'
  }
};
```

**Critérios de Aceitação:**
- [ ] Contraste mínimo de 4.5:1 para texto normal
- [ ] Contraste mínimo de 3:1 para texto grande
- [ ] Funciona em ambos os temas (claro/escuro)
- [ ] Testes de acessibilidade passam

### Sprint 2 (Semana 2)

#### 2.1 Badges para Filtros Ativos
**Prioridade:** Alta | **Esforço:** 2 dias | **Impacto:** Médio-Alto

**Arquivos a modificar:**
- `src/components/dashboard/DashboardMetrics.tsx`
- `src/hooks/useDashboard.ts`
- `src/components/ui/FilterBadge.tsx` (novo)

**Implementação:**
```typescript
// Novo componente FilterBadge
const FilterBadge = ({ label, value, onRemove }: FilterBadgeProps) => {
  return (
    <Badge variant="secondary" className="flex items-center gap-2">
      <span>{label}: {value}</span>
      <button
        onClick={onRemove}
        className="hover:bg-gray-200 rounded-full p-1"
        aria-label={`Remover filtro ${label}`}
      >
        <X className="w-3 h-3" />
      </button>
    </Badge>
  );
};

// Área de filtros ativos
const ActiveFilters = ({ filters, onRemoveFilter, onClearAll }) => {
  const activeFilters = Object.entries(filters).filter(([_, value]) => value);
  
  if (activeFilters.length === 0) return null;
  
  return (
    <div className="flex flex-wrap gap-2 mb-4">
      <span className="text-sm text-gray-600 mr-2">Filtros ativos:</span>
      {activeFilters.map(([key, value]) => (
        <FilterBadge
          key={key}
          label={key}
          value={value}
          onRemove={() => onRemoveFilter(key)}
        />
      ))}
      <Button
        variant="ghost"
        size="sm"
        onClick={onClearAll}
        className="text-red-600 hover:text-red-800"
      >
        Limpar todos
      </Button>
    </div>
  );
};
```

**Critérios de Aceitação:**
- [ ] Filtros ativos são visualmente destacados
- [ ] Usuário pode remover filtros individualmente
- [ ] Botão "Limpar todos" funciona corretamente
- [ ] Interface responsiva em mobile

#### 2.2 Breadcrumbs no Header
**Prioridade:** Média | **Esforço:** 2 dias | **Impacto:** Médio

**Arquivos a modificar:**
- `src/components/layout/Header.tsx`
- `src/components/ui/Breadcrumb.tsx` (novo)
- `src/hooks/useBreadcrumb.ts` (novo)

**Implementação:**
```typescript
// Componente Breadcrumb
const Breadcrumb = ({ items }: BreadcrumbProps) => {
  return (
    <nav aria-label="Breadcrumb" className="flex items-center space-x-2">
      {items.map((item, index) => (
        <React.Fragment key={item.href || index}>
          {index > 0 && <ChevronRight className="w-4 h-4 text-gray-400" />}
          {item.href ? (
            <Link
              to={item.href}
              className="text-blue-600 hover:text-blue-800 text-sm"
            >
              {item.label}
            </Link>
          ) : (
            <span className="text-gray-600 text-sm">{item.label}</span>
          )}
        </React.Fragment>
      ))}
    </nav>
  );
};

// Hook para gerenciar breadcrumbs
const useBreadcrumb = () => {
  const location = useLocation();
  
  const getBreadcrumbItems = () => {
    const pathSegments = location.pathname.split('/').filter(Boolean);
    const items = [{ label: 'Home', href: '/' }];
    
    pathSegments.forEach((segment, index) => {
      const href = '/' + pathSegments.slice(0, index + 1).join('/');
      const label = segment.charAt(0).toUpperCase() + segment.slice(1);
      items.push({ label, href: index === pathSegments.length - 1 ? undefined : href });
    });
    
    return items;
  };
  
  return { items: getBreadcrumbItems() };
};
```

**Critérios de Aceitação:**
- [ ] Breadcrumbs refletem a navegação atual
- [ ] Links funcionam corretamente
- [ ] Acessível via teclado
- [ ] Responsivo em diferentes tamanhos de tela

---

## 🏗️ Fase 2: Melhorias Estruturais (4-8 semanas)

### Sprint 3-4 (Semanas 3-4)

#### 3.1 Sistema de Drill-down nos Gráficos
**Prioridade:** Alta | **Esforço:** 2 semanas | **Impacto:** Alto

**Arquivos a modificar:**
- `src/components/charts/LazyTicketChart.tsx`
- `src/pages/TicketDetails.tsx` (novo)
- `src/hooks/useChartNavigation.ts` (novo)
- `src/services/api/ticketService.ts`

**Implementação:**
```typescript
// Hook para navegação em gráficos
const useChartNavigation = () => {
  const navigate = useNavigate();
  
  const handleChartClick = (dataPoint: ChartDataPoint) => {
    const { type, id, filters } = dataPoint;
    
    switch (type) {
      case 'ticket':
        navigate(`/tickets/${id}`);
        break;
      case 'technician':
        navigate(`/technicians/${id}`);
        break;
      case 'category':
        navigate(`/dashboard?category=${id}`);
        break;
      default:
        navigate(`/details?${new URLSearchParams(filters).toString()}`);
    }
  };
  
  return { handleChartClick };
};

// Componente de gráfico interativo
const InteractiveChart = ({ data, type }: InteractiveChartProps) => {
  const { handleChartClick } = useChartNavigation();
  
  return (
    <div className="relative group">
      <Chart
        data={data}
        onClick={handleChartClick}
        className="cursor-pointer"
      />
      <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
        <Badge variant="secondary" className="text-xs">
          📊 Clique para detalhes
        </Badge>
      </div>
    </div>
  );
};
```

**Critérios de Aceitação:**
- [ ] Elementos de gráfico são clicáveis
- [ ] Navegação para páginas de detalhe funciona
- [ ] Indicadores visuais de interatividade
- [ ] Performance mantida com grandes datasets

#### 3.2 Redesign da Hierarquia Visual dos KPIs
**Prioridade:** Alta | **Esforço:** 1 semana | **Impacto:** Alto

**Arquivos a modificar:**
- `src/components/dashboard/KPICard.tsx` (novo)
- `src/components/dashboard/KPIDashboard.tsx` (novo)
- `src/styles/kpi-layout.css` (novo)

**Implementação:**
```typescript
// Componente KPI com hierarquia visual
const KPICard = ({ metric, size = 'medium', priority = 'normal' }: KPICardProps) => {
  const sizeClasses = {
    small: 'col-span-1 row-span-1',
    medium: 'col-span-2 row-span-1',
    large: 'col-span-3 row-span-2',
    hero: 'col-span-4 row-span-2'
  };
  
  const priorityClasses = {
    critical: 'ring-2 ring-red-500 shadow-lg',
    high: 'ring-1 ring-orange-300 shadow-md',
    normal: 'shadow-sm'
  };
  
  return (
    <Card className={`
      ${sizeClasses[size]} 
      ${priorityClasses[priority]}
      transition-all duration-200 hover:shadow-lg
    `}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className={`
            ${size === 'hero' ? 'text-lg' : size === 'large' ? 'text-base' : 'text-sm'}
          `}>
            {metric.title}
          </CardTitle>
          {metric.trend && <TrendIndicator {...metric.trend} />}
        </div>
      </CardHeader>
      <CardContent>
        <div className={`
          font-bold
          ${size === 'hero' ? 'text-4xl' : size === 'large' ? 'text-3xl' : 'text-2xl'}
        `}>
          {metric.value}
        </div>
        {metric.subtitle && (
          <p className="text-sm text-gray-600 mt-1">{metric.subtitle}</p>
        )}
      </CardContent>
    </Card>
  );
};

// Layout de KPIs com grid responsivo
const KPIDashboard = ({ metrics }: KPIDashboardProps) => {
  return (
    <div className="grid grid-cols-6 grid-rows-4 gap-4 mb-8">
      {/* KPI Principal - Hero */}
      <KPICard 
        metric={metrics.primary} 
        size="hero" 
        priority="critical"
      />
      
      {/* KPIs Secundários */}
      {metrics.secondary.map((metric, index) => (
        <KPICard 
          key={index}
          metric={metric} 
          size="large" 
          priority="high"
        />
      ))}
      
      {/* KPIs Terciários */}
      {metrics.tertiary.map((metric, index) => (
        <KPICard 
          key={index}
          metric={metric} 
          size="medium" 
          priority="normal"
        />
      ))}
    </div>
  );
};
```

**Critérios de Aceitação:**
- [ ] KPIs principais têm destaque visual claro
- [ ] Layout responsivo funciona em todos os dispositivos
- [ ] Hierarquia visual é intuitiva
- [ ] Performance otimizada

### Sprint 5-6 (Semanas 5-6)

#### 5.1 Sistema de Notificações em Tempo Real
**Prioridade:** Alta | **Esforço:** 2 semanas | **Impacto:** Alto

**Arquivos a modificar:**
- `src/services/websocket/notificationService.ts` (novo)
- `src/components/notifications/NotificationCenter.tsx` (novo)
- `src/hooks/useNotifications.ts` (novo)
- `src/contexts/NotificationContext.tsx` (novo)

**Implementação:**
```typescript
// Serviço de notificações WebSocket
class NotificationService {
  private ws: WebSocket | null = null;
  private listeners: Map<string, Function[]> = new Map();
  
  connect() {
    this.ws = new WebSocket(process.env.VITE_WS_URL!);
    
    this.ws.onmessage = (event) => {
      const notification = JSON.parse(event.data);
      this.emit(notification.type, notification);
    };
  }
  
  subscribe(type: string, callback: Function) {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, []);
    }
    this.listeners.get(type)!.push(callback);
  }
  
  private emit(type: string, data: any) {
    const callbacks = this.listeners.get(type) || [];
    callbacks.forEach(callback => callback(data));
  }
}

// Hook para notificações
const useNotifications = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  
  useEffect(() => {
    const service = new NotificationService();
    service.connect();
    
    service.subscribe('ticket_update', (notification) => {
      setNotifications(prev => [notification, ...prev.slice(0, 9)]);
    });
    
    service.subscribe('system_alert', (notification) => {
      setNotifications(prev => [notification, ...prev.slice(0, 9)]);
    });
    
    return () => service.disconnect();
  }, []);
  
  const markAsRead = (id: string) => {
    setNotifications(prev => 
      prev.map(n => n.id === id ? { ...n, read: true } : n)
    );
  };
  
  return { notifications, markAsRead };
};

// Centro de notificações
const NotificationCenter = () => {
  const { notifications, markAsRead } = useNotifications();
  const [isOpen, setIsOpen] = useState(false);
  
  const unreadCount = notifications.filter(n => !n.read).length;
  
  return (
    <div className="relative">
      <Button
        variant="ghost"
        size="sm"
        onClick={() => setIsOpen(!isOpen)}
        className="relative"
      >
        <Bell className="w-5 h-5" />
        {unreadCount > 0 && (
          <Badge 
            variant="destructive" 
            className="absolute -top-2 -right-2 w-5 h-5 flex items-center justify-center p-0 text-xs"
          >
            {unreadCount}
          </Badge>
        )}
      </Button>
      
      {isOpen && (
        <Card className="absolute right-0 top-full mt-2 w-80 max-h-96 overflow-y-auto z-50">
          <CardHeader>
            <CardTitle className="text-sm">Notificações</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {notifications.length === 0 ? (
              <p className="text-center text-gray-500 py-4">Nenhuma notificação</p>
            ) : (
              notifications.map(notification => (
                <div
                  key={notification.id}
                  className={`p-3 border-b cursor-pointer hover:bg-gray-50 ${
                    !notification.read ? 'bg-blue-50' : ''
                  }`}
                  onClick={() => markAsRead(notification.id)}
                >
                  <div className="flex items-start gap-3">
                    <div className="flex-1">
                      <p className="text-sm font-medium">{notification.title}</p>
                      <p className="text-xs text-gray-600">{notification.message}</p>
                      <p className="text-xs text-gray-400 mt-1">
                        {formatDistanceToNow(new Date(notification.timestamp), { addSuffix: true })}
                      </p>
                    </div>
                    {!notification.read && (
                      <div className="w-2 h-2 bg-blue-500 rounded-full mt-1" />
                    )}
                  </div>
                </div>
              ))
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};
```

**Critérios de Aceitação:**
- [ ] Notificações em tempo real funcionam
- [ ] Interface de notificações é intuitiva
- [ ] Performance não é impactada
- [ ] Funciona offline (fallback)

### Sprint 7-8 (Semanas 7-8)

#### 7.1 Otimização de Performance dos Filtros
**Prioridade:** Média-Alta | **Esforço:** 2 semanas | **Impacto:** Médio-Alto

**Arquivos a modificar:**
- `src/hooks/useDashboard.ts`
- `src/hooks/useThrottledCallback.ts`
- `src/services/api/cacheService.ts` (novo)
- `src/utils/debounce.ts` (novo)

**Implementação:**
```typescript
// Serviço de cache otimizado
class CacheService {
  private cache = new Map<string, { data: any; timestamp: number; ttl: number }>();
  
  set(key: string, data: any, ttl = 300000) { // 5 minutos default
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl
    });
  }
  
  get(key: string) {
    const item = this.cache.get(key);
    if (!item) return null;
    
    if (Date.now() - item.timestamp > item.ttl) {
      this.cache.delete(key);
      return null;
    }
    
    return item.data;
  }
  
  invalidate(pattern: string) {
    const regex = new RegExp(pattern);
    for (const key of this.cache.keys()) {
      if (regex.test(key)) {
        this.cache.delete(key);
      }
    }
  }
}

// Hook otimizado para dashboard
const useDashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({});
  const cacheService = useMemo(() => new CacheService(), []);
  
  const debouncedFetchData = useMemo(
    () => debounce(async (filterParams) => {
      const cacheKey = `dashboard_${JSON.stringify(filterParams)}`;
      const cachedData = cacheService.get(cacheKey);
      
      if (cachedData) {
        setData(cachedData);
        return;
      }
      
      setLoading(true);
      try {
        const response = await api.getDashboardData(filterParams);
        cacheService.set(cacheKey, response.data);
        setData(response.data);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    }, 300),
    [cacheService]
  );
  
  useEffect(() => {
    debouncedFetchData(filters);
  }, [filters, debouncedFetchData]);
  
  const updateFilters = useCallback((newFilters) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  }, []);
  
  const refreshData = useCallback(() => {
    cacheService.invalidate('dashboard_.*');
    debouncedFetchData(filters);
  }, [filters, debouncedFetchData, cacheService]);
  
  return {
    data,
    loading,
    filters,
    updateFilters,
    refreshData
  };
};
```

**Critérios de Aceitação:**
- [ ] Filtros respondem em menos de 300ms
- [ ] Cache funciona corretamente
- [ ] Debounce evita requisições excessivas
- [ ] Performance melhorada em 50%+

---

## 📊 Métricas de Sucesso

### KPIs de UX
- **Tempo para primeira interação:** < 2 segundos
- **Taxa de conclusão de tarefas:** > 90%
- **Satisfação do usuário (SUS):** > 80
- **Tempo médio para encontrar informação:** < 30 segundos

### KPIs Técnicos
- **Performance Score (Lighthouse):** > 90
- **Acessibilidade Score:** > 95
- **Tempo de resposta dos filtros:** < 300ms
- **Taxa de erro:** < 1%

### Ferramentas de Monitoramento
- Google Analytics para comportamento do usuário
- Lighthouse CI para performance
- axe-core para acessibilidade
- Sentry para monitoramento de erros

---

## 🧪 Estratégia de Testes

### Testes de Usabilidade
- **Teste A/B:** Comparar versões antes/depois
- **Teste de 5 segundos:** Verificar clareza da hierarquia
- **Teste de navegação:** Validar fluxos de drill-down
- **Teste de acessibilidade:** Validar com usuários com deficiência

### Testes Técnicos
- **Testes unitários:** Cobertura > 80%
- **Testes de integração:** Fluxos críticos
- **Testes E2E:** Cenários de usuário completos
- **Testes de performance:** Load testing

---

## 📅 Cronograma Detalhado

| Semana | Sprint | Entregáveis | Responsável |
|--------|--------|-------------|-------------|
| 1 | Sprint 1 | Indicadores de tendência, Contraste de cores | Dev Frontend |
| 2 | Sprint 2 | Filtros ativos, Breadcrumbs | Dev Frontend |
| 3-4 | Sprint 3-4 | Drill-down, Hierarquia KPIs | Dev Frontend + UX |
| 5-6 | Sprint 5-6 | Notificações tempo real | Dev Frontend + Backend |
| 7-8 | Sprint 7-8 | Otimização performance | Dev Frontend + DevOps |

---

## 🎯 Próximos Passos

1. **Aprovação do plano** com stakeholders
2. **Setup do ambiente** de desenvolvimento
3. **Criação das branches** para cada sprint
4. **Início do Sprint 1** com indicadores de tendência
5. **Setup de monitoramento** de métricas de sucesso

---

*Plano criado em: Janeiro 2025*
*Última atualização: Janeiro 2025*