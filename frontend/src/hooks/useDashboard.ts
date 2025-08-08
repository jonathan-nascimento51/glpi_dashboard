import { useState, useEffect, useCallback, useRef } from 'react';
import { fetchDashboardMetrics } from '../services/api';
import type {
  DashboardMetrics,
  FilterParams
} from '../types/api';
import { SystemStatus, NotificationData } from '../types';
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
  loadData: () => Promise<void>;
  forceRefresh: () => Promise<void>;
  updateFilters: (newFilters: FilterParams) => void;
  search: (query: string) => void;
  addNotification: (notification: any) => void;
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
  const [data, setData] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  // Removed unused state variables
  const [filters, setFilters] = useState<FilterParams>(initialFilters);
  // AbortController com debounce para evitar cancelamentos desnecessários
  const abortControllerRef = useRef<AbortController | null>(null);
  const loadDataTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  // Derivar dados dos resultados da API
  const levelMetrics = data?.niveis ? {
    ...data.niveis,
    tendencias: data.tendencias
  } : null;
  const systemStatus = data?.systemStatus || initialSystemStatus;
  const technicianRanking = data?.technicianRanking || [];
  const [isPending] = useState<boolean>(false);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [theme, setTheme] = useState<string>('light');
  const [dataIntegrityReport] = useState<any>(null);

  const loadData = useCallback(async (newFilters?: FilterParams) => {
    // Cancelar timeout anterior se existir
    if (loadDataTimeoutRef.current) {
      clearTimeout(loadDataTimeoutRef.current);
    }
    
    // Debounce de 300ms para evitar múltiplas chamadas rápidas
    return new Promise<void>((resolve) => {
      loadDataTimeoutRef.current = setTimeout(async () => {
        const filtersToUse = newFilters || filters;
        
        console.log('🔄 useDashboard - Carregando dados com filtros:', filtersToUse);
        console.log('📅 useDashboard - DateRange nos filtros:', filtersToUse.dateRange);
        
        // Cancelar requisição anterior apenas se ainda estiver em andamento
        if (abortControllerRef.current && !abortControllerRef.current.signal.aborted) {
          console.log('🚫 Cancelando requisição anterior');
          abortControllerRef.current.abort();
        }
        
        // Criar novo AbortController
        abortControllerRef.current = new AbortController();
        const signal = abortControllerRef.current.signal;
        
        setLoading(true);
        setError(null);
        
        try {
          // Fazer chamadas paralelas para todos os endpoints com signal de cancelamento
          const [metricsResult, systemStatusResult, technicianRankingResult] = await Promise.all([
            fetchDashboardMetrics(filtersToUse),
            import('../services/api').then(api => api.getSystemStatus()),
            import('../services/api').then(api => api.getTechnicianRanking(filtersToUse, signal))
          ]);
          
          // Verificar se a requisição foi cancelada
          if (signal.aborted) {
            console.log('🚫 Requisição foi cancelada');
            return;
          }
          
          // Performance metrics tracking removed for now
          
          if (metricsResult) {
            // Combinar todos os dados em um objeto DashboardMetrics
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
            
            // console.log('✅ useDashboard - Definindo dados combinados no estado:', combinedData);
            setData(combinedData);
            setError(null);
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
          setError(err instanceof Error ? err.message : 'Erro desconhecido');
        } finally {
          // Só atualizar loading se a requisição não foi cancelada
          if (!signal.aborted) {
            setLoading(false);
          }
        }
      
      resolve();
    }, 300); // Debounce de 300ms
  });
}, []); // Removida dependência de filters para evitar loop infinito

  // Removed unused forceRefresh function

  // Load data on mount
  useEffect(() => {
    loadData();
  }, []); // Executar apenas uma vez na montagem

  // Auto-refresh setup
  useEffect(() => {
    const refreshInterval = setInterval(() => {
      loadData(); // Usar a função atual sem dependência
    }, 300000); // 5 minutos
    
    return () => {
      clearInterval(refreshInterval);
      // Cancelar requisição em andamento quando o intervalo for limpo
       if (abortControllerRef.current && !abortControllerRef.current.signal.aborted) {
         abortControllerRef.current.abort();
       }
    };
  }, []); // Executar apenas uma vez na montagem
  
  // Cleanup ao desmontar o componente
  useEffect(() => {
    return () => {
      if (abortControllerRef.current && !abortControllerRef.current.signal.aborted) {
        console.log('🧹 Limpando AbortController no cleanup');
        abortControllerRef.current.abort();
      }
    };
  }, []);

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
    loadData,
    forceRefresh: loadData,
    updateFilters: (newFilters: FilterParams) => {
      const updatedFilters = { ...filters, ...newFilters };
      setFilters(updatedFilters);
      loadData(updatedFilters);
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
    changeTheme: (newTheme: string) => setTheme(newTheme),
    updateDateRange: (dateRange: any) => {
      console.log('🔄 useDashboard - updateDateRange chamado com:', dateRange);
      const updatedFilters = { ...filters, dateRange };
      console.log('📊 useDashboard - Filtros atualizados:', updatedFilters);
      setFilters(updatedFilters);
      loadData(updatedFilters);
    }
  };
  
  // Debug logs comentados para evitar erros de sintaxe
  // console.log('useDashboard - Retornando dados:', returnData);
  
  return returnData;
};