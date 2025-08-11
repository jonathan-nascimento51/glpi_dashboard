import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { fetchDashboardMetrics, getSystemStatus, getTechnicianRanking } from '../services/api';
import type {
  DashboardMetrics,
  FilterParams
} from '../types/api';
import { SystemStatus, NotificationData } from '../types';
import { RankingDebugger } from '../debug/rankingDebug';

// Cache local para evitar re-renders desnecessários
const LOCAL_CACHE = new Map<string, { data: any; timestamp: number; ttl: number }>();
const CACHE_TTL = 30000; // 30 segundos

// Função para gerar chave de cache
const getCacheKey = (filters: FilterParams): string => {
  return JSON.stringify({
    dateRange: filters.dateRange,
    status: filters.status,
    level: filters.level
  });
};

// Função para verificar se cache é válido
const isCacheValid = (cacheKey: string): boolean => {
  const cached = LOCAL_CACHE.get(cacheKey);
  if (!cached) return false;
  return Date.now() - cached.timestamp < cached.ttl;
};

// Função para obter dados do cache
const getCachedData = (cacheKey: string): DashboardMetrics | null => {
  const cached = LOCAL_CACHE.get(cacheKey);
  if (!cached || !isCacheValid(cacheKey)) {
    LOCAL_CACHE.delete(cacheKey);
    return null;
  }
  return cached.data;
};

// Função para salvar no cache
const setCachedData = (cacheKey: string, data: DashboardMetrics): void => {
  LOCAL_CACHE.set(cacheKey, {
    data,
    timestamp: Date.now(),
    ttl: CACHE_TTL
  });
};

interface UseDashboardReturn {
  metrics: DashboardMetrics | null;
  levelMetrics: any;
  systemStatus: SystemStatus;
  technicianRanking: any[];
  isLoading: boolean;
  isPending: boolean;
  error: string | null;
  // Novos estados específicos do ranking
  rankingLoading: boolean;
  rankingError: string | null;
  notifications: any[];
  searchQuery: string;
  filters: FilterParams;
  theme: string;
  dataIntegrityReport: any;
  loadData: () => Promise<void>;
  forceRefresh: () => Promise<void>;
  // Nova função para atualizar apenas o ranking
  refreshRanking: () => Promise<void>;
  updateFilters: (newFilters: FilterParams) => void;
  search: (query: string) => void;
  addNotification: (notification: Partial<NotificationData>) => void;
  removeNotification: (id: string) => void;
  changeTheme: (theme: string) => void;
  updateDateRange: (dateRange: any) => void;
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
  ultima_atualizacao: new Date().toISOString()
};

// Removed unused getDefaultDateRange

// Removed unused initialState



// Removed unused performConsistencyChecks function

export const useDashboard = (initialFilters: FilterParams = {}): UseDashboardReturn => {
  // Estado centralizado - única fonte da verdade
  const [data, setData] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<FilterParams>(initialFilters);
  
  // Estado específico para o ranking de técnicos - CENTRALIZADO
  const [technicianRankingState, setTechnicianRankingState] = useState<{
    data: any[]
    loading: boolean
    error: string | null
  }>({ data: [], loading: false, error: null })

  // Função única para atualizar o estado do ranking
  const atualizarRankingCentralizado = useCallback((novosTecnicos: any[]) => {
    setTechnicianRankingState(prev => ({
      ...prev,
      data: novosTecnicos,
      loading: false,
      error: null
    }))
  }, [])
  
  // AbortController para cancelamento de requisições
  const abortControllerRef = useRef<AbortController | null>(null);
  
  // Derivar dados dos resultados da API
  const levelMetrics = data?.niveis ? {
    ...data.niveis,
    tendencias: data.tendencias
  } : null;
  const systemStatus = data?.systemStatus || initialSystemStatus;
  
  // Usar estado específico do ranking em vez de derivar dos dados

  const [isPending] = useState<boolean>(false);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [theme, setTheme] = useState<string>(() => {
    return localStorage.getItem('dashboard-theme') || 'light';
  });
  const [dataIntegrityReport] = useState<any>(null);

  // Função robusta de busca de dados do ranking com async/await
  const buscarDadosDoRankingRobusta = useCallback(async () => {
    try {
      // Atualiza estado para mostrar loading
      setTechnicianRankingState(prev => ({ ...prev, loading: true, error: null }))
      
      console.log('🔍 Buscando dados do ranking...')
      
      // Usar a função da API existente
      const novosTecnicos = await getTechnicianRanking(filters)
      
      console.log('✅ Ranking carregado com sucesso:', novosTecnicos?.length || 0, 'técnicos')
      
      // Passo mais importante: Atualiza o estado com os novos dados
      atualizarRankingCentralizado(novosTecnicos || [])
      
    } catch (error: any) {
      if (error.name !== 'AbortError') {
        console.error('Erro ao atualizar o ranking:', error)
        setTechnicianRankingState(prev => ({
          ...prev,
          loading: false,
          error: error.message || 'Erro ao carregar ranking'
        }))
        setNotifications(prev => [...prev, {
          id: Date.now().toString(),
          type: 'error',
          title: 'Erro no Ranking',
          message: 'Falha ao atualizar ranking de técnicos',
          timestamp: new Date(),
          duration: 5000
        }])
      }
    }
  }, [atualizarRankingCentralizado, filters])

  // Função para buscar dados do ranking (mantida para compatibilidade)
  const buscarDadosDoRanking = useCallback(async (currentFilters: FilterParams) => {
    // Redireciona para a função robusta
    await buscarDadosDoRankingRobusta()
  }, [buscarDadosDoRankingRobusta])

  const loadData = useCallback(async (newFilters?: FilterParams, forceRefresh = false) => {
    const filtersToUse = newFilters || filters;
    const cacheKey = getCacheKey(filtersToUse);
    
    RankingDebugger.log('loadData_start', {
      forceRefresh,
      filters: filtersToUse,
      cacheKey
    }, 'useDashboard');
    
    // Verificar cache local primeiro (se não for refresh forçado)
    if (!forceRefresh) {
      const cachedData = getCachedData(cacheKey);
      if (cachedData) {
        console.log('📦 useDashboard - Dados obtidos do cache local');
        RankingDebugger.log('cache_hit', {
          hasRanking: !!cachedData.technicianRanking,
          rankingLength: cachedData.technicianRanking?.length || 0
        }, 'useDashboard');
        setData(cachedData);
        // Atualizar o ranking separadamente do cache
        atualizarRankingCentralizado(cachedData.technicianRanking || []);
        setLoading(false);
        setError(null);
        return;
      } else {
        RankingDebugger.log('cache_miss', { cacheKey }, 'useDashboard');
      }
    }
    
    console.log('🔄 useDashboard - Carregando dados com filtros:', filtersToUse);
    console.log('📅 useDashboard - DateRange nos filtros:', filtersToUse.dateRange);
    
    // Cancelar requisição anterior se existir
    if (abortControllerRef.current && !abortControllerRef.current.signal.aborted) {
      abortControllerRef.current.abort();
    }
    
    // Criar novo AbortController
    abortControllerRef.current = new AbortController();
    const signal = abortControllerRef.current.signal;
    
    setLoading(true);
    setError(null);
    
    try {
      // Fazer chamadas paralelas para todos os endpoints com timeout
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Timeout: Requisição demorou mais que 60 segundos')), 60000);
      });
      
      // Fazer chamadas paralelas com a nova lógica de ranking
      const dataPromise = Promise.all([
        fetchDashboardMetrics(filtersToUse),
        getSystemStatus(),
        buscarDadosDoRankingRobusta() // Usar a função robusta
      ]);
      
      const [metricsResult, systemStatusResult, technicianRankingResult] = await Promise.race([
        dataPromise,
        timeoutPromise
      ]) as [any, any, any];
      
      // Verificar se a requisição foi cancelada
      if (signal.aborted) {
        console.log('🚫 Requisição cancelada');
        RankingDebugger.log('request_aborted', {}, 'useDashboard');
        return;
      }
      
      if (metricsResult) {
        // Combinar dados principais (sem incluir ranking aqui)
        const combinedData: DashboardMetrics = {
          ...metricsResult,
          systemStatus: systemStatusResult || initialSystemStatus,
          technicianRanking: technicianRankingResult || []
        };
        
        console.log('📊 useDashboard - Dados combinados:', {
          metrics: !!metricsResult,
          systemStatus: !!systemStatusResult,
          technicianRanking: technicianRankingResult?.length || 0
        });
        
        RankingDebugger.log('data_combined', {
          hasMetrics: !!metricsResult,
          hasSystemStatus: !!systemStatusResult,
          rankingLength: technicianRankingResult?.length || 0,
          rankingData: technicianRankingResult
        }, 'useDashboard');
        
        // Salvar no cache local
        setCachedData(cacheKey, combinedData);
        RankingDebugger.trackCacheOperation('set', cacheKey, combinedData);
        
        // Atualizar estado principal
        setData(combinedData);
        setError(null);
        
        // O ranking já foi atualizado pela função buscarDadosDoRanking
        console.log('✅ Dados carregados com sucesso - Ranking atualizado separadamente');
      } else {
        console.error('❌ useDashboard - Resultado de métricas é null/undefined');
        setError('Falha ao carregar dados do dashboard');
      }
    } catch (err) {
      // Ignorar erros de cancelamento (axios usa CanceledError, fetch usa AbortError)
      if (err instanceof Error && (err.name === 'AbortError' || err.name === 'CanceledError')) {
        console.log('🚫 Requisição cancelada pelo usuário');
        return;
      }
      
      console.error('❌ useDashboard - Erro ao carregar dados:', err);
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido';
      setError(errorMessage);
      
      // Adicionar notificação de erro
      const errorNotification: NotificationData = {
        id: Date.now().toString(),
        title: 'Erro ao carregar dados',
        message: errorMessage,
        type: 'error',
        timestamp: new Date(),
        duration: 5000
      };
      setNotifications(prev => [...prev, errorNotification]);
    } finally {
      setLoading(false);
    }
  }, [filters, buscarDadosDoRanking, atualizarRankingCentralizado]); // Dependências atualizadas

  // Removed unused forceRefresh function

  // Load data on mount
  // Load data when filters change or on mount
  useEffect(() => {
    console.log('🔄 useDashboard - Carregando dados (mount ou filtros mudaram):', filters);
    loadData();
  }, [filters, loadData]);

  // Auto-refresh setup com cache inteligente e atualização robusta do ranking
  useEffect(() => {
    const refreshInterval = setInterval(async () => {
      // Verificar se o usuário está ativo (evitar refresh em background)
      if (document.hidden) {
        console.log('📦 Auto-refresh: Página em background, pulando refresh');
        return;
      }
      
      // Só fazer refresh se não há dados em cache válidos
      const cacheKey = getCacheKey(filters);
      if (!isCacheValid(cacheKey)) {
        console.log('🔄 Auto-refresh: Cache expirado, recarregando dados');
        try {
          // Atualizar ranking separadamente para garantir consistência com função robusta
          await buscarDadosDoRankingRobusta();
          // Depois atualizar o resto dos dados
          loadData(filters, true); // Force refresh
        } catch (error) {
          console.error('❌ Erro no auto-refresh:', error);
        }
      } else {
        console.log('📦 Auto-refresh: Cache ainda válido, pulando refresh');
      }
    }, 300000); // Aumentado para 5 minutos para reduzir piscadas
    
    return () => {
      clearInterval(refreshInterval);
      // Cancelar requisição em andamento quando o intervalo for limpo
      if (abortControllerRef.current && !abortControllerRef.current.signal.aborted) {
        abortControllerRef.current.abort();
      }
    };
  }, [filters, buscarDadosDoRanking, loadData]); // Dependências atualizadas
  
  // Cleanup ao desmontar o componente
  useEffect(() => {
    return () => {
      if (abortControllerRef.current && !abortControllerRef.current.signal.aborted) {
        console.log('🧹 Limpando AbortController no cleanup');
        abortControllerRef.current.abort();
      }
    };
  }, []);

  // Debug: rastrear mudanças no estado do ranking (apenas em desenvolvimento)
  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      RankingDebugger.trackRankingState({
        data: technicianRankingState.data,
        loading: technicianRankingState.loading,
        error: technicianRankingState.error
      });
    }
  }, [technicianRankingState]);

  // Função para atualizar apenas o ranking
  const refreshRanking = useCallback(async () => {
    console.log('🔄 Atualizando apenas o ranking...');
    await buscarDadosDoRankingRobusta();
  }, [buscarDadosDoRankingRobusta]);

  const returnData: UseDashboardReturn = {
    metrics: data,
    levelMetrics,
    systemStatus,
    technicianRanking: technicianRankingState.data,
    isLoading: loading,
    isPending,
    error,
    // Novos estados específicos do ranking
    rankingLoading: technicianRankingState.loading,
    rankingError: technicianRankingState.error,
    notifications,
    searchQuery,
    filters,
    theme,
    dataIntegrityReport,
    loadData,
    forceRefresh: loadData,
    // Nova função para atualizar apenas o ranking
    refreshRanking,
    updateFilters: (newFilters: FilterParams) => {
      const updatedFilters = { ...filters, ...newFilters };
      setFilters(updatedFilters);
      // loadData será chamado automaticamente pelo useEffect quando filters mudar
    },
    search: (query: string) => setSearchQuery(query),
    addNotification: (notification: Partial<NotificationData>) => {
      const completeNotification: NotificationData = {
        id: notification.id || Date.now().toString(),
        title: notification.title || 'Notificação',
        message: notification.message || '',
        type: notification.type || 'info',
        timestamp: notification.timestamp || new Date(),
        duration: notification.duration
      };
      setNotifications(prev => [...prev, completeNotification]);
    },
    removeNotification: (id: string) => setNotifications(prev => prev.filter(n => n.id !== id)),
    changeTheme: (newTheme?: string) => {
      const themeToSet = newTheme || (theme === 'light' ? 'dark' : 'light');
      setTheme(themeToSet);
      localStorage.setItem('dashboard-theme', themeToSet);
    },
    updateDateRange: (dateRange: any) => {
      console.log('🔄 useDashboard - updateDateRange chamado com:', dateRange);
      
      // Validar formato e ordem das datas
      if (dateRange.start || dateRange.end) {
        const startDate = dateRange.start ? new Date(dateRange.start) : null;
        const endDate = dateRange.end ? new Date(dateRange.end) : null;
        
        // Verificar se as datas são válidas
        if ((startDate && isNaN(startDate.getTime())) || (endDate && isNaN(endDate.getTime()))) {
          const errorNotification: NotificationData = {
            id: Date.now().toString(),
            title: 'Erro de Data',
            message: 'Formato de data inválido',
            type: 'error',
            timestamp: new Date(),
            duration: 5000
          };
          setNotifications(prev => [...prev, errorNotification]);
          return;
        }
        
        // Verificar ordem das datas
        if (startDate && endDate && startDate > endDate) {
          const errorNotification: NotificationData = {
            id: Date.now().toString(),
            title: 'Erro de Data',
            message: 'A data de início não pode ser posterior à data de fim',
            type: 'error',
            timestamp: new Date(),
            duration: 5000
          };
          setNotifications(prev => [...prev, errorNotification]);
          return;
        }
      }
      
      const updatedFilters = { ...filters, dateRange };
      console.log('📊 useDashboard - Filtros atualizados:', updatedFilters);
      setFilters(updatedFilters);
      // loadData será chamado automaticamente pelo useEffect quando filters mudar
    }
  };
  
  // Debug logs comentados para evitar erros de sintaxe
  // console.log('useDashboard - Retornando dados:', returnData);
  
  return returnData;
};