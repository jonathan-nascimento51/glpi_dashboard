import { useCallback, useState } from 'react';
import { useDashboardQuery } from '../../../shared/hooks/useQueryState';
import { queryKeys, invalidateQueries } from '../../../shared/services/queryClient';
import { fetchDashboardMetrics, getSystemStatus, getTechnicianRanking } from '../services/dashboardService';
import type { DashboardMetrics, FilterParams } from '../types/dashboardTypes';
import type { SystemStatus, TechnicianRanking, NotificationData } from '../../../shared/types/states';

interface UseDashboardReturn {
  // Estados padronizados
  isLoading: boolean;
  isPending: boolean;
  isRefetching: boolean;
  error: Error | null;
  isEmpty: boolean;
  hasData: boolean;
  
  // Dados
  metrics: DashboardMetrics | null;
  levelMetrics: any;
  systemStatus: SystemStatus;
  technicianRanking: TechnicianRanking[];
  
  // Estados locais
  notifications: NotificationData[];
  searchQuery: string;
  filters: FilterParams;
  theme: string;
  
  // Ações
  refetch: () => void;
  forceRefresh: () => Promise<void>;
  updateFilters: (newFilters: FilterParams) => void;
  search: (query: string) => void;
  addNotification: (notification: Partial<NotificationData>) => void;
  removeNotification: (id: string) => void;
  changeTheme: (theme: string) => void;
  updateDateRange: (dateRange: any) => void;
}

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

export const useDashboard = (): UseDashboardReturn => {
  // Estados locais
  const [notifications, setNotifications] = useState<NotificationData[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<FilterParams>({});
  const [theme, setTheme] = useState('light');

  // Query principal do dashboard com React Query
  const dashboardQuery = useDashboardQuery(
    queryKeys.dashboard.metrics(filters),
    async () => {
      console.log('🔄 Dashboard - Carregando dados com filtros:', filters);
      
      // Carregar dados sequencialmente para evitar sobrecarga
      const [metricsResult, systemStatusResult, technicianRankingResult] = await Promise.allSettled([
        fetchDashboardMetrics(filters),
        getSystemStatus(),
        getTechnicianRanking()
      ]);

      // Processar resultados
      const metrics = metricsResult.status === 'fulfilled' ? metricsResult.value : null;
      const systemStatus = systemStatusResult.status === 'fulfilled' 
        ? systemStatusResult.value 
        : initialSystemStatus;
      const technicianRanking = technicianRankingResult.status === 'fulfilled' 
        ? technicianRankingResult.value 
        : [];

      if (!metrics) {
        throw new Error('Falha ao carregar métricas do dashboard');
      }

      // Combinar dados
      const combinedData: DashboardMetrics = {
        ...metrics,
        systemStatus,
        technicianRanking
      };

      console.log('✅ Dashboard - Dados carregados:', {
        hasMetrics: !!metrics,
        hasNiveis: !!combinedData.niveis,
        systemStatus: systemStatus.status,
        technicianCount: technicianRanking.length
      });

      return combinedData;
    },
    {
      // Configurações específicas para dashboard
      staleTime: 5 * 60 * 1000, // 5 minutos
      refetchInterval: 5 * 60 * 1000, // Auto-refresh a cada 5 minutos
      retry: (failureCount, error) => {
        // Retry apenas para erros de rede
        if (error?.message?.includes('fetch')) {
          return failureCount < 3;
        }
        return false;
      },
    }
  );

  // Estados derivados
  const metrics = dashboardQuery.data;
  const levelMetrics = metrics?.niveis || null;
  const systemStatus = metrics?.systemStatus || initialSystemStatus;
  const technicianRanking = metrics?.technicianRanking || [];

  // Função para forçar refresh
  const forceRefresh = useCallback(async () => {
    console.log('🔄 Dashboard - Forçando refresh...');
    await invalidateQueries.dashboard();
    dashboardQuery.refetch();
  }, [dashboardQuery]);

  // Função para atualizar filtros
  const updateFilters = useCallback((newFilters: FilterParams) => {
    console.log('🔄 Dashboard - Atualizando filtros:', newFilters);
    setFilters(prev => ({ ...prev, ...newFilters }));
  }, []);

  // Função para busca
  const search = useCallback((query: string) => {
    setSearchQuery(query);
  }, []);

  // Gerenciamento de notificações
  const addNotification = useCallback((notification: Partial<NotificationData>) => {
    const completeNotification: NotificationData = {
      id: notification.id || Date.now().toString(),
      title: notification.title || 'Notificação',
      message: notification.message || '',
      type: notification.type || 'info',
      timestamp: notification.timestamp || new Date(),
      duration: notification.duration
    };
    setNotifications(prev => [...prev, completeNotification]);
  }, []);

  const removeNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  }, []);

  // Função para mudar tema
  const changeTheme = useCallback((newTheme: string) => {
    setTheme(newTheme);
  }, []);

  // Função para atualizar range de datas
  const updateDateRange = useCallback((dateRange: any) => {
    updateFilters({ dateRange });
  }, [updateFilters]);

  return {
    // Estados padronizados do React Query
    isLoading: dashboardQuery.isLoading,
    isPending: dashboardQuery.isPending || false,
    isRefetching: dashboardQuery.isRefetching || false,
    error: dashboardQuery.error,
    isEmpty: dashboardQuery.isEmpty,
    hasData: dashboardQuery.hasData,
    
    // Dados
    metrics,
    levelMetrics,
    systemStatus,
    technicianRanking,
    
    // Estados locais
    notifications,
    searchQuery,
    filters,
    theme,
    
    // Ações
    refetch: dashboardQuery.refetch,
    forceRefresh,
    updateFilters,
    search,
    addNotification,
    removeNotification,
    changeTheme,
    updateDateRange,
  };
};