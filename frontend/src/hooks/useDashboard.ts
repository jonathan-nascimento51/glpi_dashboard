import { useState, useEffect, useCallback } from 'react';
import { fetchDashboardMetrics } from '../services/api';
import type { DashboardMetrics, FilterParams } from '../types/api';
import { SystemStatus, NotificationData } from '../types';
import { useSmartRefresh } from './useSmartRefresh';
import { useFilterCache } from './useFilterCache';
import { useFilterPerformance } from './useFilterPerformance';
// Removed unused imports

interface UseDashboardReturn {
  metrics: DashboardMetrics | null;
  levelMetrics: any;
  systemStatus: SystemStatus;
  technicianRanking: any[];
  isLoading: boolean;
  isPending: boolean;
  error: string | null;
  notifications: any[];
  searchQuery: string;
  filters: FilterParams;
  theme: string;
  dataIntegrityReport: any;
  filterType: string;
  availableFilterTypes: Array<{
    key: string;
    name: string;
    description: string;
    default?: boolean;
  }>;
  loadData: () => Promise<void>;
  forceRefresh: () => Promise<void>;
  updateFilters: (newFilters: FilterParams) => void;
  updateFilterType: (type: string) => void;
  search: (query: string) => void;
  addNotification: (notification: any) => void;
  removeNotification: (id: string) => void;
  changeTheme: (theme: string) => void;
  updateDateRange: (dateRange: any) => void;
  clearFilterCache: () => void;
  getCacheStats: () => {
    size: number;
    hitRate: number;
    totalRequests: number;
    cacheHits: number;
  };
  getPerformanceMetrics: () => any;
  isFilterInProgress: boolean;
}

// Removed unused initialFilterState

// Removed unused initialMetrics

const initialSystemStatus: SystemStatus = {
  api: 'offline',
  glpi: 'offline',
  glpi_message: 'Sistema não conectado',
  glpi_response_time: 0,
  last_update: new Date().toISOString(),
  version: '1.0.0',
  status: 'offline',
  sistema_ativo: false,
  ultima_atualizacao: new Date().toISOString(),
};

// Removed unused getDefaultDateRange

// Removed unused initialState

// Removed unused performConsistencyChecks function

export const useDashboard = (initialFilters: FilterParams = {}): UseDashboardReturn => {
  const [data, setData] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  // Removed unused state variables
  const [filters, setFilters] = useState<FilterParams>(initialFilters);
  
  // Cache para otimização de performance
  const { getCachedData, setCachedData, clearCache, getCacheStats } = useFilterCache({
    maxCacheSize: 30,
    cacheExpirationMs: 5 * 60 * 1000, // 5 minutos
    enableCache: true,
  });
  
  // Performance monitoring para filtros
  const { 
    debouncedFilter, 
    metrics: performanceMetrics, 
    startFilterTimer, 
    endFilterTimer,
    clearMetrics: clearPerformanceMetrics,
    isFilterInProgress 
  } = useFilterPerformance({
    debounceDelay: 500,
    throttleDelay: 100,
    maxHistorySize: 100,
    enableMetrics: true,
  });
  // Derivar dados dos resultados da API
  const levelMetrics = data?.niveis
    ? {
        ...data.niveis,
        tendencias: data.tendencias,
      }
    : null;
  const systemStatus = data?.systemStatus || initialSystemStatus;
  const technicianRanking = data?.technicianRanking || [];
  const [isPending] = useState<boolean>(false);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [theme, setTheme] = useState<string>('light');
  const [dataIntegrityReport] = useState<any>(null);
  const [filterType, setFilterType] = useState<string>(initialFilters.filterType || 'creation');
  const [availableFilterTypes, setAvailableFilterTypes] = useState<
    Array<{
      key: string;
      name: string;
      description: string;
      default?: boolean;
    }>
  >([]);

  const loadData = useCallback(
    async (newFilters?: FilterParams, forceRefresh: boolean = false) => {
      const filtersToUse = newFilters || filters;
      const timerId = startFilterTimer('dashboard-load');

      // Verificar cache primeiro (se não for refresh forçado)
      if (!forceRefresh) {
        const cachedData = getCachedData(filtersToUse);
        if (cachedData) {
          // Dados carregados do cache
          setData(cachedData);
          setLoading(false);
          setError(null);
          endFilterTimer(timerId, true); // Marcar como cached
          return;
        }
      }

      setLoading(true);
      setError(null);

      try {
        // Carregando dados da API
        // Fazer chamadas paralelas para todos os endpoints
        const [metricsResult, systemStatusResult, technicianRankingResult] = await Promise.all([
          fetchDashboardMetrics(filtersToUse),
          import('../services/api').then(api => api.getSystemStatus()),
          import('../services/api').then(api => {
            // Preparar filtros para o ranking de técnicos
            const rankingFilters: any = {};

            if (filtersToUse.dateRange?.startDate) {
              rankingFilters.start_date = filtersToUse.dateRange.startDate;
            }
            if (filtersToUse.dateRange?.endDate) {
              rankingFilters.end_date = filtersToUse.dateRange.endDate;
            }

            return api.getTechnicianRanking(
              Object.keys(rankingFilters).length > 0 ? rankingFilters : undefined
            );
          }),
        ]);

        // Performance metrics tracking removed for now

        if (metricsResult) {
          // Combinar todos os dados em um objeto DashboardMetrics
          const combinedData: DashboardMetrics = {
            ...metricsResult,
            systemStatus: systemStatusResult || initialSystemStatus,
            technicianRanking: technicianRankingResult || [],
          };

          // Combined data set in state
          setData(combinedData);
          setError(null);
          
          // Armazenar no cache
          setCachedData(filtersToUse, combinedData);
          // Dados armazenados no cache
          
          endFilterTimer(timerId, false); // Marcar como não cached
        } else {
          setError('Falha ao carregar dados do dashboard');
          endFilterTimer(timerId, false);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erro desconhecido');
        endFilterTimer(timerId, false);
      } finally {
        setLoading(false);
      }
    },
    [filters, getCachedData, setCachedData, startFilterTimer, endFilterTimer]
  );

  // Debounced version of loadData para filtros usando performance hook
  const debouncedLoadData = debouncedFilter((newFilters: FilterParams) => {
    loadData(newFilters, false);
  });

  // Removed unused forceRefresh function

  // Load data on mount
  useEffect(() => {
    loadData();
  }, [loadData]);

  // Smart refresh - coordenado e inteligente
  useSmartRefresh({
    refreshKey: 'dashboard-main',
    refreshFn: loadData,
    intervalMs: 300000, // 5 minutos
    immediate: false,
    enabled: true,
  });

  // Função para buscar tipos de filtro disponíveis
  const fetchFilterTypes = useCallback(async () => {
    try {
      const response = await fetch('/api/filter-types');
      if (response.ok) {
        const result = await response.json();
        if (result.success && result.data) {
          const types = Object.entries(result.data).map(([key, value]: [string, any]) => ({
            key,
            name: value.name,
            description: value.description,
            default: value.default,
          }));
          setAvailableFilterTypes(types);
        }
      }
    } catch (error) {
      // Failed to fetch filter types - using fallback
      // Fallback para tipos padrão
      setAvailableFilterTypes([
        {
          key: 'creation',
          name: 'Data de Criação',
          description: 'Filtra tickets criados no período',
          default: true,
        },
        {
          key: 'modification',
          name: 'Data de Modificação',
          description: 'Filtra tickets modificados no período',
          default: false,
        },
        {
          key: 'current_status',
          name: 'Status Atual',
          description: 'Mostra snapshot atual dos tickets',
          default: false,
        },
      ]);
    }
  }, []);

  // Buscar tipos de filtro na inicialização
  useEffect(() => {
    fetchFilterTypes();
  }, [fetchFilterTypes]);

  // Função para atualizar o tipo de filtro (com debounce)
  const updateFilterType = useCallback(
    (type: string) => {
      setFilterType(type);
      const updatedFilters = { ...filters, filterType: type };
      setFilters(updatedFilters);
      debouncedLoadData(updatedFilters);
    },
    [filters, debouncedLoadData]
  );

  const returnData: UseDashboardReturn = {
    metrics: data,
    levelMetrics,
    systemStatus,
    technicianRanking,
    isLoading: loading,
    isPending,
    error,
    notifications,
    searchQuery,
    filters,
    theme,
    dataIntegrityReport,
    filterType,
    availableFilterTypes,
    loadData,
    forceRefresh: loadData,
    updateFilters: (newFilters: FilterParams) => {
      const updatedFilters = { ...filters, ...newFilters };
      setFilters(updatedFilters);
      // Usar debounce para filtros normais, mas não para dateRange
      if (newFilters.dateRange) {
        loadData(updatedFilters, false); // Sem debounce para mudanças de data
      } else {
        debouncedLoadData(updatedFilters); // Com debounce para outros filtros
      }
    },
    updateFilterType,
    search: (query: string) => setSearchQuery(query),
    addNotification: (notification: Partial<NotificationData>) => {
      const completeNotification: NotificationData = {
        id: notification.id || Date.now().toString(),
        title: notification.title || 'Notificação',
        message: notification.message || '',
        type: notification.type || 'info',
        timestamp: notification.timestamp || new Date(),
        duration: notification.duration,
      };
      setNotifications(prev => [...prev, completeNotification]);
    },
    removeNotification: (id: string) => setNotifications(prev => prev.filter(n => n.id !== id)),
    changeTheme: (newTheme: string) => setTheme(newTheme),
    updateDateRange: (dateRange: any) => {
      const updatedFilters = { ...filters, dateRange };
      setFilters(updatedFilters);
      // Forçar recarregamento imediato com os novos filtros (sem cache)
      loadData(updatedFilters, true);
    },
    // Adicionar função para limpar cache quando necessário
    clearFilterCache: () => {
      clearCache();
      clearPerformanceMetrics();
    },
    // Adicionar função para obter estatísticas do cache
    getCacheStats,
    // Adicionar função para obter métricas de performance
    getPerformanceMetrics: () => performanceMetrics,
    // Adicionar indicador de filtro em progresso
    isFilterInProgress,
  };

  // Debug logs removidos para limpeza do código

  return returnData;
};
