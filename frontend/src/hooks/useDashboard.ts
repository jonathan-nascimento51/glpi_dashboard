import { useState, useEffect, useCallback, useTransition } from 'react';
import { fetchDashboardMetrics } from '../services/api';
import type {
  DashboardMetrics,
  FilterParams,
  LoadingState,
  PerformanceMetrics,
  CacheConfig,
  ApiError
} from '../types/api';
import { DashboardState, MetricsData, SystemStatus, FilterState, NotificationData, Theme, TechnicianRanking, DateRange } from '../types';
import { apiService } from '../services/api';
import { dataMonitor, MonitoringAlert } from '../utils/dataMonitor';
import { performanceMonitor } from '../utils/performanceMonitor';
import { useApiPerformance } from './usePerformanceMonitoring';
import { useDebouncedCallback, useThrottledCallback } from './useDebounce';

interface UseDashboardReturn {
  data: DashboardMetrics | null;
  loading: boolean;
  error: string | null;
  refreshData: () => Promise<void>;
  lastUpdated: Date | null;
  performance: PerformanceMetrics | null;
  cacheStatus: CacheConfig | null;
  updateFilters: (newFilters: FilterParams) => void;
}

const initialFilterState: FilterState = {
  period: 'today',
  levels: ['n1', 'n2', 'n3', 'n4'],
  status: ['new', 'progress', 'pending', 'resolved'],
  priority: ['high', 'medium', 'low'],
};

const initialMetrics: MetricsData = {
  novos: 0,
  pendentes: 0,
  progresso: 0,
  resolvidos: 0,
  total: 0,
  niveis: {
    n1: {
      novos: 0,
      pendentes: 0,
      progresso: 0,
      resolvidos: 0
    },
    n2: {
      novos: 0,
      pendentes: 0,
      progresso: 0,
      resolvidos: 0
    },
    n3: {
      novos: 0,
      pendentes: 0,
      progresso: 0,
      resolvidos: 0
    },
    n4: {
      novos: 0,
      pendentes: 0,
      progresso: 0,
      resolvidos: 0
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

// Default date range - last 30 days
const getDefaultDateRange = (): DateRange => ({
  startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
  endDate: new Date().toISOString().split('T')[0],
  label: 'Últimos 30 dias'
});

const initialState: DashboardState = {
  metrics: initialMetrics, // Usar métricas iniciais em vez de null
  systemStatus: initialSystemStatus, // Usar status inicial em vez de null
  technicianRanking: [],
  isLoading: true,
  error: null,
  lastUpdated: null,
  filters: initialFilterState,
  searchQuery: '',
  searchResults: [],
  notifications: [],
  theme: 'light',

  dataIntegrityReport: null,
  monitoringAlerts: [],
  dateRange: getDefaultDateRange(),
};



// Função para verificações adicionais de consistência
const performConsistencyChecks = (
  metrics: MetricsData,
  systemStatus: SystemStatus,
  technicianRanking: TechnicianRanking[]
): string[] => {
  const errors: string[] = [];
  
  // Verificar se o sistema está ativo mas não há dados
  if (systemStatus.sistema_ativo && metrics.total === 0) {
    errors.push('Sistema ativo mas nenhum ticket encontrado');
  }
  
  // Verificar se há técnicos no ranking mas nenhum ticket
  if ((technicianRanking || []).length > 0 && metrics.total === 0) {
    errors.push('Técnicos encontrados mas nenhum ticket no sistema');
  }
  
  // Verificar se há inconsistência entre tickets totais e ranking
  const totalTicketsInRanking = (technicianRanking || []).reduce((sum, tech) => sum + tech.total, 0);
  if (totalTicketsInRanking > metrics.total * 2) { // Permitir alguma margem
    errors.push(`Total de tickets no ranking (${totalTicketsInRanking}) muito maior que total geral (${metrics.total})`);
  }
  
  // Verificar se há dados muito antigos
  if (systemStatus.ultima_atualizacao) {
    const lastUpdate = new Date(systemStatus.ultima_atualizacao);
    const now = new Date();
    const hoursDiff = (now.getTime() - lastUpdate.getTime()) / (1000 * 60 * 60);
    
    if (hoursDiff > 24) {
      errors.push(`Dados muito antigos: última atualização há ${Math.round(hoursDiff)} horas`);
    }
  }
  
  return errors;
};

export const useDashboard = (initialFilters: FilterParams = {}): UseDashboardReturn => {
  const [data, setData] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [performance, setPerformance] = useState<PerformanceMetrics | null>(null);
  const [cacheStatus, setCacheStatus] = useState<CacheConfig | null>(null);
  const [filters, setFilters] = useState<FilterParams>(initialFilters);
  const [isPending, startTransition] = useTransition();
  const { measureApiCall } = useApiPerformance();

  const loadData = useCallback(async (newFilters?: FilterParams) => {
    const filtersToUse = newFilters || filters;
    
    // console.log('🔄 useDashboard - Iniciando loadData com filtros:', filtersToUse);
    
    setLoading(true);
    setError(null);
    
    try {
      const startTime = window.performance.now();
      
      // Fazer chamadas paralelas para todos os endpoints
      const [metricsResult, systemStatusResult, technicianRankingResult] = await Promise.all([
        fetchDashboardMetrics(filtersToUse),
        import('../services/api').then(api => api.getSystemStatus()),
        import('../services/api').then(api => api.getTechnicianRanking())
      ]);
      
      // console.log('📥 useDashboard - Resultado recebido de fetchDashboardMetrics:', metricsResult);
      // console.log('📥 useDashboard - Resultado recebido de getSystemStatus:', systemStatusResult);
      // console.log('📥 useDashboard - Resultado recebido de getTechnicianRanking:', technicianRankingResult);
      
      const endTime = window.performance.now();
      const responseTime = endTime - startTime;
      
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
          ...metricsResult,
          systemStatus: systemStatusResult || initialSystemStatus,
          technicianRanking: technicianRankingResult || []
        };
        
        // console.log('✅ useDashboard - Definindo dados combinados no estado:', combinedData);
        setData(combinedData);
        setLastUpdated(new Date());
        setPerformance(perfMetrics);
        setError(null);
      } else {
        console.error('❌ useDashboard - Resultado de métricas é null/undefined');
        setError('Falha ao carregar dados do dashboard');
      }
    } catch (err) {
      console.error('❌ useDashboard - Erro ao carregar dados:', err);
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
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
    metrics: data?.niveis?.geral || initialMetrics,
    levelMetrics: {
      niveis: data?.niveis || {
        n1: initialMetrics,
        n2: initialMetrics,
        n3: initialMetrics,
        n4: initialMetrics,
        geral: initialMetrics
      }
    },
    systemStatus: data?.systemStatus || initialSystemStatus,
    technicianRanking: data?.technicianRanking || [],
    isLoading: loading,
    isPending,
    error,
    notifications: [],
    searchQuery: '',
    searchResults: [],
    filters,
    theme: 'light',
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
    changeTheme: () => {},
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