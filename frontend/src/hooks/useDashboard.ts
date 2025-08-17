import { useState, useEffect, useCallback } from 'react';
import { fetchDashboardMetrics } from '../services/api';
import type { DashboardMetrics, FilterParams } from '../types/api';
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
    async (newFilters?: FilterParams) => {
      const filtersToUse = newFilters || filters;

      console.log('🔄 useDashboard - Iniciando loadData com filtros:', filtersToUse);
      console.log('📅 useDashboard - DateRange específico:', filtersToUse.dateRange);

      setLoading(true);
      setError(null);

      try {
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

            console.log(
              '🎯 useDashboard - Aplicando filtros ao ranking de técnicos:',
              rankingFilters
            );
            return api.getTechnicianRanking(
              Object.keys(rankingFilters).length > 0 ? rankingFilters : undefined
            );
          }),
        ]);

        // console.log('📥 useDashboard - Resultado recebido de fetchDashboardMetrics:', metricsResult);
        // console.log('📥 useDashboard - Resultado recebido de getSystemStatus:', systemStatusResult);
        // console.log('📥 useDashboard - Resultado recebido de getTechnicianRanking:', technicianRankingResult);

        // Performance metrics tracking removed for now

        if (metricsResult) {
          // Combinar todos os dados em um objeto DashboardMetrics
          const combinedData: DashboardMetrics = {
            ...metricsResult,
            systemStatus: systemStatusResult || initialSystemStatus,
            technicianRanking: technicianRankingResult || [],
          };

          console.log('📊 useDashboard - Dados combinados:', {
            metrics: !!metricsResult,
            systemStatus: !!systemStatusResult,
            technicianRanking: technicianRankingResult?.length || 0,
          });

          // console.log('✅ useDashboard - Definindo dados combinados no estado:', combinedData);
          setData(combinedData);
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
    },
    [filters]
  );

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
      console.error('Erro ao buscar tipos de filtro:', error);
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

  // Função para atualizar o tipo de filtro
  const updateFilterType = useCallback(
    (type: string) => {
      setFilterType(type);
      const updatedFilters = { ...filters, filterType: type };
      setFilters(updatedFilters);
      loadData(updatedFilters);
    },
    [filters, loadData]
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
      loadData(updatedFilters);
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
      console.log('🔄 updateDateRange chamado com:', dateRange);
      const updatedFilters = { ...filters, dateRange };
      console.log('📝 Filtros atualizados:', updatedFilters);
      setFilters(updatedFilters);
      // Forçar recarregamento imediato com os novos filtros
      loadData(updatedFilters);
    },
  };

  // Debug logs comentados para evitar erros de sintaxe
  // console.log('useDashboard - Retornando dados:', returnData);

  return returnData;
};
