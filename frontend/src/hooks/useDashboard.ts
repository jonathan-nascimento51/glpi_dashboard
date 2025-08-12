import { useState, useEffect, useCallback } from 'react';
import { fetchDashboardMetrics, getSystemStatus, getTechnicianRanking } from '../services/api';
import type {
  DashboardMetrics,
  FilterParams
} from '../types/api';
import { SystemStatus, TechnicianRanking, NotificationData } from '../types';

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
  glpi_message: 'Sistema não verificado',
  glpi_response_time: 0,
  last_update: new Date().toISOString(),
  version: '1.0.0',
  status: 'offline',
  sistema_ativo: false,
  ultima_atualizacao: new Date().toISOString()
};

// Removed unused getDefaultDateRange

// Removed unused initialState

export const useDashboard = (): UseDashboardReturn => {
  const [data, setData] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(false);
  const [isPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notifications, setNotifications] = useState<NotificationData[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<FilterParams>({});
  const [theme, setTheme] = useState('light');
  const [dataIntegrityReport] = useState(null);

  // Derived state with detailed logging
  const levelMetrics = data?.niveis || null;
  const systemStatus = data?.systemStatus || initialSystemStatus;
  const technicianRanking = data?.technicianRanking || [];

  // Debug logs for derived state
  useEffect(() => {
    console.log('🔍 useDashboard - Estado derivado atualizado:', {
      hasData: !!data,
      hasLevelMetrics: !!levelMetrics,
      levelMetricsKeys: levelMetrics ? Object.keys(levelMetrics) : [],
      levelMetricsStructure: levelMetrics,
      hasSystemStatus: !!systemStatus,
      systemStatusStructure: systemStatus,
      hasTechnicianRanking: !!technicianRanking,
      technicianRankingLength: technicianRanking?.length || 0,
      technicianRankingFirst: technicianRanking?.[0]
    });
  }, [data, levelMetrics, systemStatus, technicianRanking]);

  const loadData = useCallback(async (filtersToUse: FilterParams = filters) => {
    console.log('🔄 useDashboard - Iniciando loadData com filtros:', filtersToUse);

    setLoading(true);
    setError(null);

    try {
      // Fazer chamadas sequenciais para evitar sobrecarga do servidor
      console.log('🔄 useDashboard - Iniciando carregamento sequencial de dados...');
      
      const metricsResult = await fetchDashboardMetrics(filtersToUse);
      console.log('📊 useDashboard - Métricas carregadas:', {
        hasResult: !!metricsResult,
        hasNiveis: !!metricsResult?.niveis,
        niveisKeys: metricsResult?.niveis ? Object.keys(metricsResult.niveis) : [],
        fullResult: metricsResult
      });
      
      // Aguardar um pouco antes da próxima requisição
      await new Promise(resolve => setTimeout(resolve, 200));
      
      const systemStatusResult = await getSystemStatus();
      console.log('🔧 useDashboard - Status do sistema carregado:', {
        hasResult: !!systemStatusResult,
        status: systemStatusResult?.status,
        fullResult: systemStatusResult
      });
      
      // Aguardar um pouco antes da próxima requisição
      await new Promise(resolve => setTimeout(resolve, 200));
      
      const technicianRankingResult = await getTechnicianRanking();
      console.log('👥 useDashboard - Ranking de técnicos carregado:', {
        hasResult: !!technicianRankingResult,
        length: technicianRankingResult?.length || 0,
        firstItem: technicianRankingResult?.[0],
        fullResult: technicianRankingResult
      });

      if (metricsResult) {
        // Combinar todos os dados em um objeto DashboardMetrics
        const combinedData: DashboardMetrics = {
          ...metricsResult,
          systemStatus: systemStatusResult || initialSystemStatus,
          technicianRanking: technicianRankingResult || []
        };

        console.log('🔗 useDashboard - Dados combinados finais:', {
          hasMetrics: !!metricsResult,
          hasNiveis: !!combinedData.niveis,
          niveisStructure: combinedData.niveis,
          hasSystemStatus: !!systemStatusResult,
          systemStatusStructure: combinedData.systemStatus,
          hasTechnicianRanking: !!technicianRankingResult,
          technicianRankingLength: combinedData.technicianRanking?.length || 0,
          technicianRankingFirst: combinedData.technicianRanking?.[0]
        });

        setData(combinedData);
        setError(null);
        console.log('✅ useDashboard - Estado atualizado com sucesso');
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

  // Removed unused forceRefresh function

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
        title: notification.title || 'Notifica��o',
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
      const updatedFilters = { ...filters, dateRange };
      setFilters(updatedFilters);
      loadData(updatedFilters);
    }
  };

  // Debug logs comentados para evitar erros de sintaxe
  // console.log('useDashboard - Retornando dados:', returnData);

  return returnData;
};
