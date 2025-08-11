import { useState, useEffect, useCallback, useRef } from 'react';
import { fetchDashboardMetrics, getSystemStatus, getTechnicianRanking } from '../services/api';
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
  const [data, setData] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  // Removed unused state variables
  const [filters, setFilters] = useState<FilterParams>(initialFilters);
  // AbortController com debounce para evitar cancelamentos desnecessários
  const abortControllerRef = useRef<AbortController | null>(null);
  
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
  const [theme, setTheme] = useState<string>(() => {
    return localStorage.getItem('dashboard-theme') || 'light';
  });
  const [dataIntegrityReport] = useState<any>(null);

  const loadData = useCallback(async (newFilters?: FilterParams) => {
    const filtersToUse = newFilters || filters;
    
    console.log('🔄 useDashboard - Carregando dados com filtros:', filtersToUse);
    console.log('📅 useDashboard - DateRange nos filtros:', filtersToUse.dateRange);
    
    // Remover AbortController temporariamente para debug
    // const signal = abortControllerRef.current?.signal;
    
    setLoading(true);
    setError(null);
    
    try {
      // Fazer chamadas paralelas para todos os endpoints
      const [metricsResult, systemStatusResult, technicianRankingResult] = await Promise.all([
        fetchDashboardMetrics(filtersToUse),
        getSystemStatus(),
        getTechnicianRanking(filtersToUse)
      ]);
      
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
  }, [filters]); // Dependência de filters necessária

  // Removed unused forceRefresh function

  // Load data on mount
  // Load data when filters change or on mount
  useEffect(() => {
    console.log('🔄 useDashboard - Carregando dados (mount ou filtros mudaram):', filters);
    loadData();
  }, [filters, loadData]);

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