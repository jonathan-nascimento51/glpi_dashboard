import { useEffect, Profiler, ProfilerOnRenderCallback } from 'react';
import { NotificationProvider } from './contexts/NotificationContext';
import { DashboardLayout } from './components/layout/DashboardLayout';
import { OverlayManager } from './components/layout/OverlayManager';
import { LoadingSpinner, SkeletonMetricsGrid, SkeletonLevelsSection, ErrorState } from './components/LoadingSpinner';
import { useDashboard } from './hooks/useDashboard';
import { useOverlayManager } from './hooks/useOverlayManager';
import { useFilterPerformance } from './hooks/usePerformanceMonitoring';
import { useCacheNotifications } from './hooks/useCacheNotifications';
import { usePerformanceProfiler } from './utils/performanceMonitor';
import { performanceMonitor } from './utils/performanceMonitor';
import { alertIntegration } from './utils/alertIntegration';
import { preDeliveryValidator } from './utils/preDeliveryValidator';
import { workflowOptimizer } from './utils/workflowOptimizer';
import { realTimeMonitor } from './utils/realTimeMonitor';
import { TicketStatus, Theme } from './types';

function App() {
  const {
    metrics,
    levelMetrics,
    systemStatus,
    technicianRanking,
    isLoading,
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
    updateFilters,
    updateFilterType,
    search,
    addNotification,
    removeNotification,
    changeTheme,
    updateDateRange,
    clearFilterCache,
    getCacheStats,
    getPerformanceMetrics,
    isFilterInProgress,
  } = useDashboard();

  const {
    overlayStates,
    toggleIntegrityMonitor,
    openPerformanceDashboard,
    closePerformanceDashboard,
    toggleChartExample,
    toggleCacheStats,
    togglePerformanceMonitor,
    toggleAdvancedSettings,
    toggleAlertCenter,
    openAlertCenter,
    closeAlertCenter,
  } = useOverlayManager();

  // Performance monitoring hooks
  const { onRenderCallback } = usePerformanceProfiler();
  const profilerCallback: ProfilerOnRenderCallback = (
    id,
    phase,
    actualDuration,
    baseDuration,
    startTime,
    commitTime
  ) => {
    // Converter phase para o tipo esperado pelo onRenderCallback
    const normalizedPhase = phase === 'nested-update' ? 'update' : phase;
    onRenderCallback(
      id,
      normalizedPhase,
      actualDuration,
      baseDuration,
      startTime,
      commitTime,
      new Set()
    );
  };

  // Inicialização do sistema de alertas integrado
  useEffect(() => {
    // Inicializar integração de alertas
    alertIntegration.initialize();
    
    return () => {
      // Limpar recursos ao desmontar
      alertIntegration.destroy();
    };
  }, []);

  // Configuração do validador pré-entrega
  useEffect(() => {
    // Disponibilizar validador globalmente para uso no console
    (window as any).preDeliveryValidator = preDeliveryValidator;
    (window as any).workflowOptimizer = workflowOptimizer;
    (window as any).realTimeMonitor = realTimeMonitor;

    // Configurar monitor em tempo real baseado no ambiente
    if (process.env.NODE_ENV === 'development') {
      // Configuração mais rigorosa para desenvolvimento
      realTimeMonitor.configure({
        enabled: true,
        checkInterval: 10000, // 10 segundos em dev
        alertThresholds: {
          consecutiveFailures: 2,
          responseTimeMs: 3000,
          zeroMetricsThreshold: 30, // 30 segundos
        },
        autoRecovery: {
          enabled: true,
          maxAttempts: 5,
          backoffMultiplier: 1.5,
        },
        notifications: {
          console: true,
          visual: true,
          sound: false,
        },
        healthChecks: {
          api: true,
          metrics: true,
          visual: true,
          performance: false, // Desabilitado em dev para reduzir ruído
        },
      });

      // Real-time monitor configured for development
      // Available commands: startMonitoring(), stopMonitoring(), getSystemStatus(), executeOptimizedWorkflow(), quickWorkflow()
    } else {
      // Configuração mais conservadora para produção
      realTimeMonitor.configure({
        enabled: true,
        checkInterval: 60000, // 1 minuto em produção
        alertThresholds: {
          consecutiveFailures: 3,
          responseTimeMs: 5000,
          zeroMetricsThreshold: 120, // 2 minutos
        },
        autoRecovery: {
          enabled: true,
          maxAttempts: 3,
          backoffMultiplier: 2,
        },
        notifications: {
          console: true,
          visual: false, // Sem alertas visuais em produção
          sound: false,
        },
        healthChecks: {
          api: true,
          metrics: true,
          visual: true,
          performance: true,
        },
      });
    }

    // Cleanup ao desmontar
    return () => {
      realTimeMonitor.stopMonitoring();
    };
  }, []);

  const { measureFilterOperation } = useFilterPerformance();

  // Cache notifications
  const { notifications: cacheNotifications, removeNotification: removeCacheNotification } =
    useCacheNotifications();

  // Load data on mount
  useEffect(() => {
    loadData();
  }, [loadData]);

  // Apply theme to body element
  useEffect(() => {
    document.body.className = theme === 'dark' ? 'dark' : '';
  }, [theme]);

  // Handle filter by status with performance monitoring
  const handleFilterByStatus = async (status: TicketStatus) => {
    await measureFilterOperation(`status-${status}`, async () => {
      performanceMonitor.startMeasure('filter-ui-update');

      updateFilters({ status: [status] });

      addNotification({
        id: Date.now().toString(),
        title: 'Filtro Aplicado',
        message: `Exibindo apenas chamados com status: ${getStatusLabel(status)}`,
        type: 'info',
        timestamp: new Date(),
        duration: 3000,
      });

      performanceMonitor.endMeasure('filter-ui-update');
    });
  };

  // Get status label in Portuguese
  const getStatusLabel = (status: TicketStatus): string => {
    const labels = {
      new: 'Novos',
      progress: 'Em Progresso',
      pending: 'Pendentes',
      resolved: 'Resolvidos',
    };
    return labels[status] || status;
  };

  // Show loading state on initial load
  if (isLoading && !levelMetrics) {
    return (
      <div className='min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50'>
        <div className='animate-pulse'>
          {/* Header skeleton */}
          <div className='bg-white/80 backdrop-blur-sm border-b border-gray-200 px-6 py-4'>
            <div className='flex items-center justify-between'>
              <div className='flex items-center space-x-4'>
                <div className='w-10 h-10 bg-gray-200 rounded-lg' />
                <div className='space-y-2'>
                  <div className='w-48 h-5 bg-gray-200 rounded' />
                  <div className='w-32 h-3 bg-gray-200 rounded' />
                </div>
              </div>
              <div className='flex items-center space-x-4'>
                <div className='w-64 h-10 bg-gray-200 rounded-lg' />
                <div className='w-32 h-8 bg-gray-200 rounded' />
              </div>
            </div>
          </div>

          {/* Content skeleton */}
          <div className='p-6 space-y-8'>
            <SkeletonMetricsGrid />
            <SkeletonLevelsSection />
          </div>
        </div>
      </div>
    );
  }

  // Show error state
  if (error && !levelMetrics) {
    return (
      <div className='min-h-screen bg-gradient-to-br from-red-50 via-white to-orange-50 flex items-center justify-center'>
        <ErrorState title='Erro ao Carregar Dashboard' message={error} onRetry={loadData} />
      </div>
    );
  }

  return (
    <NotificationProvider>
      <Profiler id='App' onRender={profilerCallback}>
        <DashboardLayout
          searchQuery={searchQuery}
          dateRange={filters?.dateRange || { startDate: '', endDate: '', label: 'Selecionar período' }}
          filterType={filterType}
          availableFilterTypes={availableFilterTypes}
          theme={theme as Theme}
          metrics={metrics}
          levelMetrics={levelMetrics}
          systemStatus={systemStatus}
          technicianRanking={technicianRanking}
          filters={filters}
          isLoading={isLoading}
          isPending={isPending}
          showChartExample={overlayStates.showChartExample}
          notifications={notifications}
          onSearch={search}
          onThemeChange={(newTheme: Theme) => changeTheme(newTheme)}
          onNotification={(title, message, type) =>
            addNotification({
              id: Date.now().toString(),
              title,
              message,
              type,
              timestamp: new Date(),
              duration: 3000,
            })
          }
          onDateRangeChange={updateDateRange}
          onFilterTypeChange={updateFilterType}
          onPerformanceDashboard={openPerformanceDashboard}
          onChartExample={toggleChartExample}
          onFilterByStatus={handleFilterByStatus}
          onRemoveNotification={removeNotification}
          onLoadData={loadData}
        />

        <OverlayManager
          dataIntegrityReport={dataIntegrityReport}
          showIntegrityMonitor={overlayStates.showIntegrityMonitor}
          onToggleIntegrityMonitor={toggleIntegrityMonitor}
          showPerformanceDashboard={overlayStates.showPerformanceDashboard}
          onClosePerformanceDashboard={closePerformanceDashboard}
          cacheNotifications={cacheNotifications}
          showCacheStats={overlayStates.showCacheStats}
          onCloseCacheStats={() => toggleCacheStats()}
          onRemoveCacheNotification={removeCacheNotification}
          clearFilterCache={clearFilterCache}
          getCacheStats={getCacheStats}
          showPerformanceMonitor={overlayStates.showPerformanceMonitor}
          onClosePerformanceMonitor={() => togglePerformanceMonitor()}
          getPerformanceMetrics={getPerformanceMetrics}
          isFilterInProgress={isFilterInProgress}
          showAdvancedSettings={overlayStates.showAdvancedSettings}
          onCloseAdvancedSettings={() => toggleAdvancedSettings()}
          showAlertCenter={overlayStates.showAlertCenter}
          onCloseAlertCenter={closeAlertCenter}
          onOpenAlertCenter={openAlertCenter}
          isDevelopment={process.env.NODE_ENV === 'development'}
          onToggleCacheStats={toggleCacheStats}
          onTogglePerformanceMonitor={togglePerformanceMonitor}
          onToggleAdvancedSettings={toggleAdvancedSettings}
          onToggleAlertCenter={toggleAlertCenter}
        />
      </Profiler>
    </NotificationProvider>
  );
}

export default App;
