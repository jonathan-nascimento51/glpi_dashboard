import { useState, useEffect, useCallback } from 'react';
import { DashboardState, MetricsData, SystemStatus, FilterState, NotificationData, Theme, TechnicianRanking } from '../types';
import { apiService } from '../services/api';
import { validateAllData, generateIntegrityReport, DataIntegrityReport } from '../utils/dataValidation';
import { dataCacheManager } from '../utils/dataCache';
import { dataMonitor, MonitoringAlert } from '../utils/dataMonitor';

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

// Dados fictícios removidos - usando apenas dados reais da API GLPI

const initialState: DashboardState = {
  metrics: initialMetrics,
  systemStatus: initialSystemStatus,
  isLoading: true,
  error: null,
  lastUpdated: null,
  filters: initialFilterState,
  searchQuery: '',
  searchResults: [],
  notifications: [],
  theme: 'light',
  isSimplifiedMode: false,
  technicianRanking: [], // Inicializar vazio - será preenchido com dados reais da API
  dataIntegrityReport: null, // Relatório de integridade dos dados
  monitoringAlerts: [],
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
  if (technicianRanking.length > 0 && metrics.total === 0) {
    errors.push('Técnicos encontrados mas nenhum ticket no sistema');
  }
  
  // Verificar se há inconsistência entre tickets totais e ranking
  const totalTicketsInRanking = technicianRanking.reduce((sum, tech) => sum + tech.total, 0);
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

export const useDashboard = () => {
  const [state, setState] = useState<DashboardState>(initialState);

  // Load data from API with robust validation and intelligent caching
  const loadData = useCallback(async () => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      console.log('🔄 Iniciando carregamento de dados...');
      
      // Use intelligent cache system
      const result = await dataCacheManager.getOrFetch(async () => {
        console.log('🌐 Buscando dados das APIs...');
        const [rawMetrics, rawSystemStatus, rawTechnicianRanking] = await Promise.all([
          apiService.getMetrics(),
          apiService.getSystemStatus(),
          apiService.getTechnicianRanking(),
        ]);
        
        return {
          metrics: rawMetrics,
          systemStatus: rawSystemStatus,
          technicianRanking: rawTechnicianRanking
        };
      });
      
      console.log('📊 Dados obtidos:', {
        isFromCache: result.isFromCache,
        cacheStatus: result.cacheStatus,
        hasValidationReport: !!result.validationReport
      });
      
      // Additional consistency checks
      const consistencyErrors = performConsistencyChecks(
        result.metrics,
        result.systemStatus,
        result.technicianRanking
      );
      
      if (consistencyErrors.length > 0) {
        console.warn('🔧 Problemas de consistência detectados:', consistencyErrors);
      }
      
      // Execute monitoring checks
      const monitoringAlerts = dataMonitor.runChecks({
        metrics: result.metrics,
        systemStatus: result.systemStatus,
        technicianRanking: result.technicianRanking,
        validationReport: result.validationReport
      });
      
      if (monitoringAlerts.length > 0) {
        console.warn('🚨 Alertas de monitoramento gerados:', monitoringAlerts);
      }
      
      console.log('✅ Dados validados e prontos para uso:', {
        metrics: result.metrics,
        systemStatus: result.systemStatus,
        technicianRanking: result.technicianRanking,
        monitoringAlerts: monitoringAlerts.length
      });
      
      setState(prev => ({
        ...prev,
        metrics: result.metrics,
        systemStatus: result.systemStatus,
        technicianRanking: result.technicianRanking,
        dataIntegrityReport: result.validationReport,
        monitoringAlerts: dataMonitor.getAlerts(),
        isLoading: false,
        lastUpdated: new Date(),
        error: null
      }));
      
      // Show notification if there were warnings
      if (result.validationReport && result.validationReport.warnings && result.validationReport.warnings.length > 0) {
        addNotification({
          title: 'Dados Carregados com Avisos',
          message: `${result.validationReport.warnings.length} avisos de validação encontrados. Verifique o console para detalhes.`,
          type: 'warning',
          duration: 5000
        });
      } else {
        console.log(`✨ Dados carregados com sucesso ${result.isFromCache ? '(cache)' : '(API)'}!`);
      }
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Erro desconhecido';
      console.error('❌ Erro ao carregar dados:', error);
      
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));
      
      // Show error notification
      addNotification({
        title: 'Erro ao Carregar Dados',
        message: errorMessage,
        type: 'error',
        duration: 8000
      });
    }
  }, []);

  // Force refresh
  const forceRefresh = useCallback(() => {
    loadData();
  }, [loadData]);

  // Update filters
  const updateFilters = useCallback((newFilters: Partial<FilterState>) => {
    setState(prev => ({
      ...prev,
      filters: { ...prev.filters, ...newFilters },
    }));
  }, []);

  // Search functionality
  const search = useCallback(async (query: string) => {
    setState(prev => ({ ...prev, searchQuery: query }));
    
    if (query.trim() === '') {
      setState(prev => ({ ...prev, searchResults: [] }));
      return;
    }
    
    try {
      const results = await apiService.search(query);
      setState(prev => ({ ...prev, searchResults: results }));
    } catch (error) {
      console.error('Search error:', error);
    }
  }, []);

  // Add notification
  const addNotification = useCallback((notification: Omit<NotificationData, 'id' | 'timestamp'>) => {
    const newNotification: NotificationData = {
      ...notification,
      id: Date.now().toString(),
      timestamp: new Date(),
    };
    
    setState(prev => ({
      ...prev,
      notifications: [...prev.notifications, newNotification],
    }));
    
    // Auto-remove notification after duration
    if (notification.duration) {
      setTimeout(() => {
        removeNotification(newNotification.id);
      }, notification.duration);
    }
  }, []);

  // Remove notification
  const removeNotification = useCallback((id: string) => {
    setState(prev => ({
      ...prev,
      notifications: prev.notifications.filter(n => n.id !== id),
    }));
  }, []);

  // Change theme
  const changeTheme = useCallback((theme: Theme) => {
    setState(prev => ({ ...prev, theme }));
    localStorage.setItem('dashboard-theme', theme);
    
    // Apply theme to document
    document.documentElement.className = theme === 'dark' ? 'dark' : '';
  }, []);

  // Toggle simplified mode
  const toggleSimplifiedMode = useCallback(() => {
    setState(prev => ({ ...prev, isSimplifiedMode: !prev.isSimplifiedMode }));
    localStorage.setItem('dashboard-simplified-mode', (!state.isSimplifiedMode).toString());
  }, [state.isSimplifiedMode]);

  // Load saved theme and simplified mode on mount
  useEffect(() => {
    const savedTheme = localStorage.getItem('dashboard-theme') as Theme;
    if (savedTheme) {
      changeTheme(savedTheme);
    }
    
    const savedSimplifiedMode = localStorage.getItem('dashboard-simplified-mode');
    if (savedSimplifiedMode === 'true') {
      setState(prev => ({ ...prev, isSimplifiedMode: true }));
    }
  }, [changeTheme]);

  // Auto-refresh and monitoring setup
  useEffect(() => {
    // Initial load
    loadData();
    
    // Set up auto-refresh interval - aumentado para 2 minutos para reduzir carga
    const refreshInterval = setInterval(() => {
      if (!state.isLoading) {
        loadData();
      }
    }, 120000); // 2 minutos (120 segundos)
    
    // Start continuous monitoring - reduzido para 1 minuto
    dataMonitor.startMonitoring(60000); // Check every 1 minute
    
    // Listen for monitoring alerts
    const handleMonitoringAlerts = (alerts: MonitoringAlert[]) => {
      setState(prev => ({
        ...prev,
        monitoringAlerts: alerts
      }));
    };
    
    dataMonitor.addListener(handleMonitoringAlerts);
    
    // Cleanup function
    return () => {
      clearInterval(refreshInterval);
      dataMonitor.stopMonitoring();
      dataMonitor.removeListener(handleMonitoringAlerts);
    };
  }, [loadData, state.isLoading]);

  // Health check every 5 minutes - reduzido para diminuir carga
  useEffect(() => {
    const healthCheckInterval = setInterval(async () => {
      try {
        const isHealthy = await apiService.healthCheck();
        if (!isHealthy) {
          console.warn('Health check failed');
        }
      } catch (error) {
        console.error('Health check error:', error);
      }
    }, 300000); // 5 minutos
    
    return () => clearInterval(healthCheckInterval);
  }, []);

  return {
    ...state,
    loadData,
    forceRefresh,
    updateFilters,
    search,
    addNotification,
    removeNotification,
    changeTheme,
    toggleSimplifiedMode,
  };
};