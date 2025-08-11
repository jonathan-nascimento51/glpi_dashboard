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
const PERSISTENT_CACHE_KEY = 'dashboard_ranking_persistent';
const PERSISTENT_CACHE_TTL = 300000; // 5 minutos para cache persistente
const MAX_RETRY_ATTEMPTS = 3;
const RETRY_DELAY = 1000; // 1 segundo

// Funções auxiliares para cache local
const generateCacheKey = (filters: FilterParams): string => {
  return `dashboard_${JSON.stringify(filters)}_${Date.now().toString().slice(0, -4)}`; // Remove últimos 4 dígitos para cache de ~10s
};

const getCachedData = (cacheKey: string): DashboardMetrics | null => {
  const cached = LOCAL_CACHE.get(cacheKey);
  if (cached && (Date.now() - cached.timestamp) < cached.ttl) {
    console.log('📦 Cache hit:', cacheKey);
    return cached.data;
  }
  return null;
};

const setCachedData = (cacheKey: string, data: DashboardMetrics): void => {
  LOCAL_CACHE.set(cacheKey, {
    data,
    timestamp: Date.now(),
    ttl: CACHE_TTL
  });
  console.log('💾 Cache saved:', cacheKey);
};

// Funções auxiliares para recovery de dados
const isValidCacheData = (data: any): boolean => {
  if (!data || typeof data !== 'object') {
    console.log('🔍 Recovery: Dados inválidos - não é objeto');
    return false;
  }
  
  if (!data.timestamp || typeof data.timestamp !== 'number') {
    console.log('🔍 Recovery: Dados inválidos - timestamp ausente ou inválido');
    return false;
  }
  
  if (!data.data || !Array.isArray(data.data)) {
    console.log('🔍 Recovery: Dados inválidos - data ausente ou não é array');
    return false;
  }
  
  const isExpired = (Date.now() - data.timestamp) > PERSISTENT_CACHE_TTL;
  if (isExpired) {
    console.log('🔍 Recovery: Cache expirado', {
      age: Date.now() - data.timestamp,
      ttl: PERSISTENT_CACHE_TTL
    });
    return false;
  }
  
  console.log('✅ Recovery: Dados válidos', {
    dataLength: data.data.length,
    age: Date.now() - data.timestamp
  });
  return true;
};

const sleep = (ms: number): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms));
};

interface UseDashboardReturn {
  data: DashboardMetrics | null;
  loading: boolean;
  error: string | null;
  searchQuery: string;
  filters: FilterParams;
  theme: string;
  notifications: NotificationData[];
  dataIntegrityReport: any;
  levelMetrics: any;
  systemStatus: SystemStatus;
  rankingState: {
    data: any[];
    loading: boolean;
    error: string | null;
    lastUpdated: Date | null;
  };
  loadData: (newFilters?: FilterParams, forceRefresh?: boolean) => Promise<void>;
  forceRefresh: (newFilters?: FilterParams) => Promise<void>;
  refreshRanking: () => Promise<void>;
  recoverRankingData: () => Promise<any[]>;
  updateFilters: (newFilters: Partial<FilterParams>) => void;
  search: (query: string) => void;
  addNotification: (notification: Partial<NotificationData>) => void;
  removeNotification: (id: string) => void;
  changeTheme: (newTheme?: string) => void;
  updateDateRange: (dateRange: any) => void;
}

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

export const useDashboard = (initialFilters: FilterParams = {}): UseDashboardReturn => {
  // Estados principais
  const [data, setData] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [filters, setFilters] = useState<FilterParams>(initialFilters);
  const [theme, setTheme] = useState<string>(() => {
    return localStorage.getItem('dashboard-theme') || 'light';
  });
  const [notifications, setNotifications] = useState<NotificationData[]>([]);
  
  // Estado unificado para ranking de técnicos
  const [rankingState, setRankingState] = useState({
    data: [] as any[],
    loading: false,
    error: null as string | null,
    lastUpdated: null as Date | null
  });
  
  // Refs para evitar dependências circulares
  const abortControllerRef = useRef<AbortController | null>(null);
  const filtersRef = useRef<FilterParams>(filters);
  const isInitialLoadRef = useRef<boolean>(true);
  const lastCacheKeyRef = useRef<string>('');
  
  // Atualizar filtersRef quando filters mudar
  useEffect(() => {
    filtersRef.current = filters;
  }, [filters]);
  
  // Derivação de dados usando useMemo
  const levelMetrics = useMemo(() => {
    if (!data?.niveis) return null;
    return {
      level1: data.niveis.n1?.total || 0,
      level2: data.niveis.n2?.total || 0,
      level3: data.niveis.n3?.total || 0
    };
  }, [data?.niveis]);
  
  const systemStatus = useMemo(() => {
    return data?.systemStatus || initialSystemStatus;
  }, [data?.systemStatus]);
  
  // Funções auxiliares estáveis
  const updateRankingState = useCallback((newData: any[]) => {
    setRankingState(prev => ({
      ...prev,
      data: newData,
      loading: false,
      error: null,
      lastUpdated: new Date()
    }));
  }, []);
  
  const setRankingLoading = useCallback((loading: boolean) => {
    setRankingState(prev => ({ ...prev, loading }));
  }, []);
  
  const setRankingError = useCallback((error: string | null) => {
    setRankingState(prev => ({ ...prev, error, loading: false }));
  }, []);
  
  const addErrorNotification = useCallback((title: string, message: string) => {
    const errorNotification: NotificationData = {
      id: Date.now().toString(),
      title,
      message,
      type: 'error',
      timestamp: new Date(),
      duration: 5000
    };
    setNotifications(prev => [...prev, errorNotification]);
  }, []);
  
  // Função para recuperar dados do ranking com fallbacks
  const recoverRankingData = useCallback(async (): Promise<any[]> => {
    console.log('🔄 Recovery: Iniciando recuperação de dados do ranking...');
    
    try {
      // 1. Primeiro tenta recuperar dados do localStorage persistente
      console.log('📦 Recovery: Tentando recuperar do localStorage...');
      const persistentData = localStorage.getItem(PERSISTENT_CACHE_KEY);
      
      if (persistentData) {
        try {
          const parsedData = JSON.parse(persistentData);
          console.log('📦 Recovery: Dados encontrados no localStorage', {
            timestamp: parsedData.timestamp,
            dataLength: parsedData.data?.length || 0
          });
          
          // 2. Valida se os dados em cache ainda são válidos
          if (isValidCacheData(parsedData)) {
            console.log('✅ Recovery: Cache persistente válido, retornando dados');
            RankingDebugger.log('recovery_success_cache', {
              source: 'localStorage',
              dataLength: parsedData.data.length
            }, 'useDashboard');
            return parsedData.data;
          }
        } catch (parseError) {
          console.warn('⚠️ Recovery: Erro ao parsear dados do localStorage:', parseError);
        }
      }
      
      console.log('🔄 Recovery: Cache inválido ou inexistente, tentando API...');
      
      // 3. Se cache inválido, busca da API como fallback com retry
      let lastError: Error | null = null;
      
      for (let attempt = 1; attempt <= MAX_RETRY_ATTEMPTS; attempt++) {
        try {
          console.log(`🔄 Recovery: Tentativa ${attempt}/${MAX_RETRY_ATTEMPTS} de busca na API...`);
          
          const rankingData = await getTechnicianRanking(filtersRef.current);
          
          if (rankingData && Array.isArray(rankingData) && rankingData.length > 0) {
            console.log('✅ Recovery: Dados obtidos da API com sucesso', {
              attempt,
              dataLength: rankingData.length
            });
            
            // Salva no cache persistente para próximas recuperações
            const cacheData = {
              data: rankingData,
              timestamp: Date.now()
            };
            
            try {
              localStorage.setItem(PERSISTENT_CACHE_KEY, JSON.stringify(cacheData));
              console.log('💾 Recovery: Dados salvos no cache persistente');
            } catch (storageError) {
              console.warn('⚠️ Recovery: Erro ao salvar no localStorage:', storageError);
            }
            
            RankingDebugger.log('recovery_success_api', {
              attempt,
              dataLength: rankingData.length
            }, 'useDashboard');
            
            return rankingData;
          } else {
            throw new Error('Dados da API inválidos ou vazios');
          }
        } catch (apiError) {
          lastError = apiError instanceof Error ? apiError : new Error('Erro desconhecido na API');
          console.warn(`⚠️ Recovery: Tentativa ${attempt} falhou:`, lastError.message);
          
          RankingDebugger.log('recovery_attempt_failed', {
            attempt,
            error: lastError.message
          }, 'useDashboard');
          
          // 4. Implementa retry automático com delay
          if (attempt < MAX_RETRY_ATTEMPTS) {
            const delay = RETRY_DELAY * attempt; // Delay progressivo
            console.log(`⏳ Recovery: Aguardando ${delay}ms antes da próxima tentativa...`);
            await sleep(delay);
          }
        }
      }
      
      // 5. Se todas as tentativas falharam, loga o erro final
      console.error('❌ Recovery: Todas as tentativas de recuperação falharam');
      RankingDebugger.log('recovery_failed', {
        totalAttempts: MAX_RETRY_ATTEMPTS,
        lastError: lastError?.message || 'Erro desconhecido'
      }, 'useDashboard');
      
      // 6. Retorna array vazio em último caso
      console.log('🔄 Recovery: Retornando array vazio como fallback final');
      return [];
      
    } catch (recoveryError) {
      console.error('❌ Recovery: Erro crítico durante recuperação:', recoveryError);
      RankingDebugger.log('recovery_critical_error', {
        error: recoveryError instanceof Error ? recoveryError.message : 'Erro crítico desconhecido'
      }, 'useDashboard');
      
      // Retorna array vazio mesmo em caso de erro crítico
      return [];
    }
  }, []);

  // Função para carregar dados do ranking
  const loadRankingData = useCallback(async () => {
    try {
      setRankingLoading(true);
      console.log('🔄 Carregando dados do ranking...');
      
      const rankingData = await getTechnicianRanking(filtersRef.current);
      
      if (rankingData && Array.isArray(rankingData)) {
        console.log('✅ Dados do ranking carregados:', rankingData.length, 'técnicos');
        updateRankingState(rankingData);
        RankingDebugger.log('ranking_loaded', {
          count: rankingData.length,
          data: rankingData
        }, 'useDashboard');
      } else {
        console.warn('⚠️ Dados do ranking inválidos:', rankingData);
        setRankingError('Dados do ranking inválidos');
      }
    } catch (err) {
      console.error('❌ Erro ao carregar ranking:', err);
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido';
      setRankingError(errorMessage);
      addErrorNotification('Erro ao carregar ranking', errorMessage);
    }
  }, [setRankingLoading, updateRankingState, setRankingError, addErrorNotification]);
  
  // Função principal para carregar dados
  const loadMainData = useCallback(async (filtersToUse: FilterParams, forceRefresh = false) => {
    // Cancelar requisição anterior se existir
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    // Criar novo AbortController
    abortControllerRef.current = new AbortController();
    const signal = abortControllerRef.current.signal;
    
    try {
      setLoading(true);
      setError(null);
      
      console.log('🔄 useDashboard - Carregando dados:', { filters: filtersToUse, forceRefresh });
      
      // Verificar cache primeiro (se não for refresh forçado)
      const cacheKey = generateCacheKey(filtersToUse);
      if (!forceRefresh && cacheKey === lastCacheKeyRef.current) {
        const cachedData = getCachedData(cacheKey);
        if (cachedData) {
          console.log('📦 useDashboard - Usando dados do cache');
          setData(cachedData);
          setLoading(false);
          return;
        }
      }
      
      lastCacheKeyRef.current = cacheKey;
      
      // Carregar dados principais e ranking em paralelo
      const [metricsResult, systemStatusResult] = await Promise.all([
        fetchDashboardMetrics(filtersToUse, signal),
        getSystemStatus(signal)
      ]);
      
      // Carregar ranking separadamente
      loadRankingData();
      
      // Verificar se a requisição foi cancelada
      if (signal.aborted) {
        console.log('🚫 Requisição cancelada');
        RankingDebugger.log('request_aborted', {}, 'useDashboard');
        return;
      }
      
      if (metricsResult) {
        // Combinar dados principais (ranking é gerenciado separadamente)
        const combinedData: DashboardMetrics = {
          ...metricsResult,
          systemStatus: systemStatusResult || initialSystemStatus
        };
        
        console.log('📊 useDashboard - Dados combinados:', {
          metrics: !!metricsResult,
          systemStatus: !!systemStatusResult,
          rankingLength: rankingState.data?.length || 0
        });
        
        RankingDebugger.log('data_combined', {
          hasMetrics: !!metricsResult,
          hasSystemStatus: !!systemStatusResult,
          rankingLength: rankingState.data?.length || 0,
          rankingData: rankingState.data
        }, 'useDashboard');
        
        // Salvar no cache local
        setCachedData(cacheKey, combinedData);
        RankingDebugger.trackCacheOperation('set', cacheKey, combinedData);
        
        // Atualizar estado principal
        setData(combinedData);
        setError(null);
        
        console.log('✅ Dados carregados com sucesso');
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
      
      addErrorNotification('Erro ao carregar dados', errorMessage);
    } finally {
      setLoading(false);
    }
  }, [updateRankingState, setRankingLoading, setRankingError, addErrorNotification, loadRankingData, rankingState.data]);
  
  // Função estável loadData que usa filtersRef para evitar dependências circulares
  const loadData = useCallback(async (newFilters?: FilterParams, forceRefresh = false) => {
    const filtersToUse = newFilters || filtersRef.current;
    await loadMainData(filtersToUse, forceRefresh);
  }, [loadMainData]);
  
  // Efeito para carregamento inicial
  useEffect(() => {
    if (isInitialLoadRef.current) {
      console.log('🔄 useDashboard - Carregamento inicial');
      loadData();
      isInitialLoadRef.current = false;
    }
  }, [loadData]);

  // Efeito para quando filtros mudam (exceto carregamento inicial)
  useEffect(() => {
    if (!isInitialLoadRef.current) {
      console.log('🔄 useDashboard - Filtros alterados:', { filters });
      filtersRef.current = filters;
      loadData(filters);
    }
  }, [filters, loadData]);

  // Efeito para atualização automática a cada 5 minutos
  useEffect(() => {
    const interval = setInterval(() => {
      // Verificar se há dados em cache válidos antes de fazer nova requisição
      const cacheKey = generateCacheKey(filtersRef.current);
      const cachedData = getCachedData(cacheKey);
      
      if (!cachedData) {
        console.log('🔄 Atualização automática - Cache expirado, recarregando dados');
        
        // Verificar se o usuário está ativo (não em idle)
        if (document.visibilityState === 'visible') {
          loadData();
        } else {
          console.log('⏸️ Página não está visível, pulando atualização automática');
        }
      } else {
        console.log('✅ Atualização automática - Cache ainda válido');
      }
    }, 5 * 60 * 1000); // 5 minutos

    return () => clearInterval(interval);
  }, [loadData]);

  // Cleanup do AbortController quando o componente é desmontado
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);
  
  // Função para refresh manual do ranking
  const refreshRanking = useCallback(async () => {
    console.log('🔄 Refresh manual do ranking solicitado');
    await loadRankingData();
  }, [loadRankingData]);
  
  // Função para atualizar filtros
  const updateFilters = useCallback((newFilters: Partial<FilterParams>) => {
    const updatedFilters = { ...filters, ...newFilters };
    setFilters(updatedFilters);
    filtersRef.current = updatedFilters;
  }, [filters]);
  
  return {
    data,
    loading,
    error,
    searchQuery,
    filters,
    theme,
    notifications,
    dataIntegrityReport: null,
    levelMetrics,
    systemStatus,
    rankingState,
    loadData,
    forceRefresh: useCallback((newFilters?: FilterParams) => loadData(newFilters, true), [loadData]),
    refreshRanking,
    recoverRankingData,
    updateFilters,
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
          addErrorNotification('Erro de Data', 'Formato de data inválido');
          return;
        }
        
        // Verificar ordem das datas
        if (startDate && endDate && startDate > endDate) {
          addErrorNotification('Erro de Data', 'A data de início não pode ser posterior à data de fim');
          return;
        }
      }
      
      const updatedFilters = { ...filters, dateRange };
      console.log('📊 useDashboard - Filtros atualizados:', updatedFilters);
      setFilters(updatedFilters);
    }
  };
};