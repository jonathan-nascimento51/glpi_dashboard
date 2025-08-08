import { useState, useEffect, useCallback, useTransition } from 'react';
import { fetchDashboardMetrics } from '../services/api';
import type {
  FilterParams,
  PerformanceMetrics,
  CacheConfig,
  DashboardMetrics
} from '../types/api';
import { SystemStatus, NotificationData, Theme, TechnicianRanking, LevelMetrics } from '../types';
// import { dataMonitor, MonitoringAlert } from '../utils/dataMonitor';
// import { performanceMonitor } from '../utils/performanceMonitor';
// import { useApiPerformance } from './usePerformanceMonitoring';
// import { useDebouncedCallback, useThrottledCallback } from './useDebounce';

interface UseDashboardReturn {
  // Dados principais
  metrics: DashboardMetrics | null;
  levelMetrics: {
    niveis: {
      'Manutenção Geral': LevelMetrics;
      'Patrimônio': LevelMetrics;
      'Atendimento': LevelMetrics;
      'Mecanografia': LevelMetrics;
    };
    geral: LevelMetrics;
  } | null;
  systemStatus: SystemStatus | null;
  technicianRanking: TechnicianRanking[];
  
  // Estados de carregamento
  isLoading: boolean;
  isPending: boolean;
  error: string | null;
  
  // Notificações e busca
  notifications: NotificationData[];
  searchQuery: string;
  searchResults: any[];
  
  // Filtros e tema
  filters: FilterParams;
  theme: Theme;
  
  // Relatórios e alertas
  dataIntegrityReport: any | null;
  monitoringAlerts: any[];
  
  // Funções
  loadData: (newFilters?: FilterParams) => Promise<void>;
  forceRefresh: () => void;
  updateFilters: (newFilters: FilterParams) => void;
  search: () => void;
  addNotification: (notification: any) => void;
  removeNotification: (id: string) => void;
  changeTheme: (theme: Theme) => void;
  updateDateRange: (dateRange: any) => void;
  refreshData: (newFilters?: FilterParams) => Promise<void>;
  lastUpdated: Date | null;
  performance: PerformanceMetrics | null;
  cacheStatus: CacheConfig | null;
}

// const initialFilterState: FilterState = {
//   period: 'today',
//   levels: ['n1', 'n2', 'n3', 'n4'],
//   status: ['new', 'progress', 'pending', 'resolved'],
//   priority: ['high', 'medium', 'low'],
// };

const initialMetrics: DashboardMetrics = {
  novos: 0,
  pendentes: 0,
  progresso: 0,
  resolvidos: 0,
  total: 0,
  niveis: {
    'Manutenção Geral': {
      novos: 0,
      pendentes: 0,
      progresso: 0,
      resolvidos: 0,
      total: 0
    },
    'Patrimônio': {
      novos: 0,
      pendentes: 0,
      progresso: 0,
      resolvidos: 0,
      total: 0
    },
    'Atendimento': {
      novos: 0,
      pendentes: 0,
      progresso: 0,
      resolvidos: 0,
      total: 0
    },
    'Mecanografia': {
      novos: 0,
      pendentes: 0,
      progresso: 0,
      resolvidos: 0,
      total: 0
    }
  },
  tendencias: {
      novos: '0',
      pendentes: '0',
      progresso: '0',
      resolvidos: '0'
    }
};

const initialSystemStatus: SystemStatus = {
  status: 'offline',
  sistema_ativo: false,
  ultima_atualizacao: ''
};

// // Default date range - last 30 days
// const getDefaultDateRange = (): DateRange => ({
//   startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
//   endDate: new Date().toISOString().split('T')[0],
//   label: 'Últimos 30 dias'
// });

// const initialState: DashboardState = {
//   metrics: initialMetrics, // Usar métricas iniciais em vez de null
//   systemStatus: initialSystemStatus, // Usar status inicial em vez de null
//   technicianRanking: [],
//   isLoading: true,
//   error: null,
//   lastUpdated: null,
//   filters: initialFilterState,
//   searchQuery: '',
//   searchResults: [],
//   notifications: [],
//   theme: (localStorage.getItem('theme') as Theme) || 'light',
//
//   dataIntegrityReport: null,
//   monitoringAlerts: [],
//   dateRange: getDefaultDateRange(),
// };



// // Função para verificações adicionais de consistência
// const performConsistencyChecks = (
//   metrics: MetricsData,
//   systemStatus: SystemStatus,
//   technicianRanking: TechnicianRanking[]
// ): string[] => {
//   const errors: string[] = [];
//   
//   // Verificar se o sistema está ativo mas não há dados
//   if (systemStatus.sistema_ativo && metrics.total === 0) {
//     errors.push('Sistema ativo mas nenhum ticket encontrado');
//   }
//   
//   // Verificar se há técnicos no ranking mas nenhum ticket
//   if ((technicianRanking || []).length > 0 && metrics.total === 0) {
//     errors.push('Técnicos encontrados mas nenhum ticket no sistema');
//   }
//   
//   // Verificar se há inconsistência entre tickets totais e ranking
//   const totalTicketsInRanking = (technicianRanking || []).reduce((sum, tech) => sum + tech.total, 0);
//   if (totalTicketsInRanking > metrics.total * 2) { // Permitir alguma margem
//     errors.push(`Total de tickets no ranking (${totalTicketsInRanking}) muito maior que total geral (${metrics.total})`);
//   }
//   
//   // Verificar se há dados muito antigos
//   if (systemStatus.ultima_atualizacao) {
//     const lastUpdate = new Date(systemStatus.ultima_atualizacao);
//     const now = new Date();
//     const hoursDiff = (now.getTime() - lastUpdate.getTime()) / (1000 * 60 * 60);
//     
//     if (hoursDiff > 24) {
//       errors.push(`Dados muito antigos: última atualização há ${Math.round(hoursDiff)} horas`);
//     }
//   }
//   
//   return errors;
// };

export const useDashboard = (initialFilters: FilterParams = {}): UseDashboardReturn => {
  const [data, setData] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [performance, setPerformance] = useState<PerformanceMetrics | null>(null);
  const [cacheStatus] = useState<CacheConfig | null>(null);
  const [filters, setFilters] = useState<FilterParams>(initialFilters);
  const [theme, setTheme] = useState<Theme>((localStorage.getItem('theme') as Theme) || 'light');
  const [isPending] = useTransition();
  // const { measureApiCall } = useApiPerformance();

  const loadData = useCallback(async (newFilters?: FilterParams) => {
    const filtersToUse = newFilters || filters;
    const requestId = `dashboard_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    console.log(`[${requestId}] 🔄 Iniciando loadData com filtros:`, filtersToUse);
    
    setLoading(true);
    setError(null);
    
    try {
      // Validar filtros antes de fazer a requisição
      if (filtersToUse.dateRange) {
        const { startDate, endDate } = filtersToUse.dateRange;
        if (startDate && endDate) {
          const start = new Date(startDate);
          const end = new Date(endDate);
          
          if (isNaN(start.getTime()) || isNaN(end.getTime())) {
            throw new Error('Datas inválidas fornecidas nos filtros');
          }
          
          if (start > end) {
            throw new Error('Data inicial não pode ser posterior à data final');
          }
          
          // Verificar se o intervalo não é muito grande (máximo 1 ano)
          const diffTime = Math.abs(end.getTime() - start.getTime());
          const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
          if (diffDays > 365) {
            throw new Error('Intervalo de datas não pode ser superior a 1 ano');
          }
        }
      }
      
      const startTime = window.performance.now();
      
      // Fazer chamadas paralelas para todos os endpoints com timeout
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Timeout: Requisição demorou mais de 30 segundos')), 30000);
      });
      
      const [metricsResult] = await Promise.race([
        Promise.all([
          fetchDashboardMetrics(filtersToUse)
        ]),
        timeoutPromise
      ]) as [any];
      
      console.log(`[${requestId}] 📥 Resultado recebido:`, metricsResult);
      
      const endTime = window.performance.now();
      const responseTime = endTime - startTime;
      
      // Validar estrutura dos dados recebidos
      if (metricsResult && typeof metricsResult === 'object') {
        // Verificar se tem as propriedades essenciais
        const requiredProps = ['novos', 'pendentes', 'progresso', 'resolvidos', 'total'];
        const missingProps = requiredProps.filter(prop => !(prop in metricsResult));
        
        if (missingProps.length > 0) {
          console.warn(`[${requestId}] ⚠️ Propriedades ausentes nos dados:`, missingProps);
        }
        
        // Validar se os valores são números válidos
        const numericProps = ['novos', 'pendentes', 'progresso', 'resolvidos', 'total'];
        for (const prop of numericProps) {
          if (metricsResult[prop] !== undefined && (typeof metricsResult[prop] !== 'number' || isNaN(metricsResult[prop]))) {
            console.warn(`[${requestId}] ⚠️ Valor inválido para ${prop}:`, metricsResult[prop]);
            metricsResult[prop] = 0; // Valor padrão
          }
        }
        
        // Verificar consistência dos dados
        const calculatedTotal = (metricsResult.novos || 0) + (metricsResult.pendentes || 0) + 
                               (metricsResult.progresso || 0) + (metricsResult.resolvidos || 0);
        
        if (metricsResult.total !== calculatedTotal && calculatedTotal > 0) {
          console.warn(`[${requestId}] ⚠️ Inconsistência nos totais: declarado=${metricsResult.total}, calculado=${calculatedTotal}`);
        }
      }
      
      // Criar métricas de performance
      const perfMetrics: PerformanceMetrics = {
        responseTime,
        cacheHit: false, // TODO: implementar detecção de cache
        timestamp: new Date(),
        endpoint: '/metrics'
      };
      
      if (metricsResult) {
        // Combinar todos os dados em um objeto DashboardMetrics
        const combinedData: DashboardMetrics = {
          ...initialMetrics, // Usar valores padrão como base
          ...metricsResult   // Sobrescrever com dados recebidos
        };
        
        console.log(`[${requestId}] ✅ Dados processados e validados:`, combinedData);
        setData(combinedData);
        setLastUpdated(new Date());
        setPerformance(perfMetrics);
        setError(null);
        
        // Log de performance
        if (responseTime > 5000) {
          console.warn(`[${requestId}] ⚠️ Requisição lenta: ${responseTime.toFixed(2)}ms`);
        } else {
          console.log(`[${requestId}] ⚡ Requisição concluída em ${responseTime.toFixed(2)}ms`);
        }
      } else {
        console.error(`[${requestId}] ❌ Resultado de métricas é null/undefined`);
        setError('Falha ao carregar dados do dashboard - resposta vazia');
      }
    } catch (err) {
      console.error(`[${requestId}] ❌ Erro ao carregar dados:`, err);
      
      let errorMessage = 'Erro desconhecido';
      if (err instanceof Error) {
        errorMessage = err.message;
      } else if (typeof err === 'string') {
        errorMessage = err;
      }
      
      // Categorizar tipos de erro
      if (errorMessage.includes('timeout') || errorMessage.includes('Timeout')) {
        errorMessage = 'Timeout: O servidor demorou muito para responder';
      } else if (errorMessage.includes('network') || errorMessage.includes('fetch')) {
        errorMessage = 'Erro de rede: Verifique sua conexão com a internet';
      } else if (errorMessage.includes('401') || errorMessage.includes('403')) {
        errorMessage = 'Erro de autenticação: Verifique suas credenciais';
      } else if (errorMessage.includes('500')) {
        errorMessage = 'Erro interno do servidor: Tente novamente em alguns minutos';
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  // Force refresh
  const forceRefresh = useCallback(() => {
    loadData();
  }, [loadData]);

  // Load data on mount
  useEffect(() => {
    loadData();
  }, [loadData]);



  // Auto-refresh setup
  useEffect(() => {
    const refreshInterval = setInterval(() => {
      loadData();
    }, 300000); // 5 minutos
    
    return () => clearInterval(refreshInterval);
  }, [loadData]);

  const returnData = {
    metrics: data || initialMetrics,
    levelMetrics: {
      niveis: data?.niveis || {
        'Manutenção Geral': initialMetrics.niveis['Manutenção Geral'],
        'Patrimônio': initialMetrics.niveis['Patrimônio'],
        'Atendimento': initialMetrics.niveis['Atendimento'],
        'Mecanografia': initialMetrics.niveis['Mecanografia']
      },
      geral: {
        novos: data?.novos || 0,
        pendentes: data?.pendentes || 0,
        progresso: data?.progresso || 0,
        resolvidos: data?.resolvidos || 0,
        total: data?.total || 0
      }
    },
    systemStatus: initialSystemStatus,
    technicianRanking: [],
    isLoading: loading,
    isPending,
    error,
    notifications: [],
    searchQuery: '',
    searchResults: [],
    filters,
    theme,
    dataIntegrityReport: null,
    monitoringAlerts: [],
    loadData,
    forceRefresh,
    updateFilters: (newFilters: FilterParams) => {
      const updatedFilters = { ...filters, ...newFilters };
      setFilters(updatedFilters);
      loadData(updatedFilters);
    },
    search: () => {},
    addNotification: () => {},
    removeNotification: () => {},
    changeTheme: (newTheme: Theme) => {
      setTheme(newTheme);
      localStorage.setItem('theme', newTheme);
    },
    updateDateRange: (dateRange: any) => {
      console.log('🔄 updateDateRange chamado com:', dateRange);
      const updatedFilters = { ...filters, dateRange };
      console.log('🔄 Filtros atualizados:', updatedFilters);
      setFilters(updatedFilters);
      loadData(updatedFilters);
    },
    refreshData: loadData,
    lastUpdated,
    performance,
    cacheStatus
  };
  
  // Debug logs comentados para evitar erros de sintaxe
  // console.log('useDashboard - Retornando dados:', returnData);
  
  return returnData;
};