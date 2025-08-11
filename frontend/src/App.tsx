import { useState, useEffect, Profiler, Suspense, ProfilerOnRenderCallback, memo, lazy } from 'react';
import { Header } from './components/Header';
import { NotificationSystem } from './components/NotificationSystem';
import CacheNotification from './components/CacheNotification';
import { LoadingSpinner, SkeletonMetricsGrid, SkeletonLevelsSection, ErrorState } from './components/LoadingSpinner';

// Lazy loading otimizado para componentes pesados
const ModernDashboard = lazy(() => 
  import('./components/dashboard/ModernDashboard').then(module => ({
    default: module.ModernDashboard
  }))
);

// Componentes lazy centralizados
import { 
  LazyDataIntegrityMonitor, 
  LazyPerformanceDashboard,
  DashboardSkeleton 
} from './components/LazyComponents';


import { useDashboard } from './hooks/useDashboard';



import { useFilterPerformance } from './hooks/usePerformanceMonitoring';
import { useCacheNotifications } from './hooks/useCacheNotifications';
import { usePerformanceProfiler } from './utils/performanceMonitor';
import { performanceMonitor } from './utils/performanceMonitor';
import { TicketStatus, Theme } from './types';

// Debug tools (comentado para melhorar performance)
// import './debug/rankingDiagnostic';
// import { rankingMonitor } from './debug/rankingMonitor';
// import './debug/quickRankingTest';
// import './debug/testRankingAPI';
// import './debug/directAPITest';

// Script de correção simples
import './debug/simpleFix';
import './debug/rankingFixValidation';

function App() {
  const {
    data: metrics,
    loading: isLoading,
    error,
    levelMetrics,
    systemStatus,
    rankingState,
    notifications,
    searchQuery,
    filters,
    theme,
    dataIntegrityReport,
    loadData,
    updateFilters,
    search,
    addNotification,
    removeNotification,
    changeTheme,
    updateDateRange,
  } = useDashboard();

  // Extrair dados do ranking do estado unificado
  const technicianRanking = rankingState.data;
  const rankingLoading = rankingState.loading;
  const rankingError = rankingState.error;
  const isPending = false; // Removido pois não está mais sendo usado





  const [showIntegrityMonitor, setShowIntegrityMonitor] = useState(true);
  const [showPerformanceDashboard, setShowPerformanceDashboard] = useState(false);
  
  // Performance monitoring hooks
  const { onRenderCallback } = usePerformanceProfiler();
  const profilerCallback: ProfilerOnRenderCallback = (id, phase, actualDuration, baseDuration, startTime, commitTime) => {
    // Converter phase para o tipo esperado pelo onRenderCallback
    const normalizedPhase = phase === 'nested-update' ? 'update' : phase;
    onRenderCallback(id, normalizedPhase, actualDuration, baseDuration, startTime, commitTime, new Set());
  };
  const { measureFilterOperation } = useFilterPerformance();
  
  // Cache notifications
  const { notifications: cacheNotifications, removeNotification: removeCacheNotification } = useCacheNotifications();

  // Data loading is handled by useDashboard hook
  // Removed duplicate loadData call to prevent loops

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



  // Loading otimizado com skeleton mais leve
  if (isLoading && !metrics) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
        <div className="animate-pulse">
          {/* Header skeleton simplificado */}
          <div className="bg-white/80 backdrop-blur-sm border-b border-gray-200 px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="w-10 h-10 bg-gray-200 rounded-lg" />
                <div className="space-y-2">
                  <div className="w-48 h-5 bg-gray-200 rounded" />
                  <div className="w-32 h-3 bg-gray-200 rounded" />
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="w-64 h-10 bg-gray-200 rounded-lg" />
                <div className="w-32 h-8 bg-gray-200 rounded" />
              </div>
            </div>
          </div>
          
          {/* Content skeleton otimizado */}
          <div className="p-6 space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="h-32 bg-gray-200 rounded-lg" />
              ))}
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="h-64 bg-gray-200 rounded-lg" />
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Show error state
  if (error && !metrics) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 via-white to-orange-50 flex items-center justify-center">
        <ErrorState
          title="Erro ao Carregar Dashboard"
          message={error}
          onRetry={loadData}
        />
      </div>
    );
  }

  return (
    <div className={`h-screen overflow-hidden transition-all duration-300 ${theme}`}>
      {/* Header */}
      <Header
        currentTime={new Date().toLocaleTimeString('pt-BR')}
        systemActive={true}
        searchQuery={searchQuery}
        searchResults={[]}
        dateRange={filters?.dateRange || { startDate: '', endDate: '', label: 'Selecionar período' }}
        onSearch={search}
        theme={theme as Theme}
        onThemeChange={(newTheme: Theme) => changeTheme(newTheme)}
        onNotification={(title, message, type) => addNotification({ 
          id: Date.now().toString(),
          title, 
          message, 
          type, 
          timestamp: new Date(),
          duration: 3000 
        })}
        onDateRangeChange={updateDateRange}
        onPerformanceDashboard={() => setShowPerformanceDashboard(true)}
      />


      
      {/* Dashboard Principal com Suspense otimizado */}
      <div className="flex-1 overflow-hidden">
        {metrics ? (
          <Suspense fallback={
            <div className="p-6 space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {[...Array(4)].map((_, i) => (
                  <div key={i} className="h-32 bg-gray-100 rounded-lg animate-pulse" />
                ))}
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="h-64 bg-gray-100 rounded-lg animate-pulse" />
                ))}
              </div>
            </div>
          }>
            <Profiler id="ModernDashboard" onRender={profilerCallback}>
              <ModernDashboard
                metrics={{
                  novos: metrics?.niveis?.geral?.novos || 0,
                  pendentes: metrics?.niveis?.geral?.pendentes || 0,
                  progresso: metrics?.niveis?.geral?.progresso || 0,
                  resolvidos: metrics?.niveis?.geral?.resolvidos || 0,
                  total: (metrics?.niveis?.geral?.novos || 0) + (metrics?.niveis?.geral?.pendentes || 0) + (metrics?.niveis?.geral?.progresso || 0) + (metrics?.niveis?.geral?.resolvidos || 0),
                  niveis: metrics?.niveis || {},
                  tendencias: metrics?.tendencias || {
                    novos: '0%',
                    pendentes: '0%',
                    progresso: '0%',
                    resolvidos: '0%'
                  }
                }}
                levelMetrics={{
                  niveis: levelMetrics || {}
                }}
                systemStatus={systemStatus}
                technicianRanking={technicianRanking}
                onFilterByStatus={handleFilterByStatus}
                isLoading={isLoading}
                // Novos props para estados específicos do ranking
                rankingLoading={rankingLoading}
                rankingError={rankingError}
                rankingLastUpdated={rankingState.lastUpdated}
                rankingIsUpdating={rankingState.loading && technicianRanking.length > 0}
              />
            </Profiler>
          </Suspense>
        ) : (
          // Fallback otimizado para quando não há dados
          <div className="h-full bg-gradient-to-br from-gray-50 via-white to-gray-100 flex items-center justify-center">
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-gray-200 rounded-full mx-auto mb-4 flex items-center justify-center">
                <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Nenhum dado disponível
              </h3>
              <p className="text-gray-600 mb-4">
                Não foi possível carregar os dados do dashboard.
              </p>
              <button 
                onClick={() => loadData()} 
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                Tentar Novamente
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Loading overlay for refresh */}
      {(isLoading && levelMetrics) && (
        <div className="fixed top-20 right-6 z-50">
          <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-lg p-4">
            <LoadingSpinner size="sm" text="Atualizando..." />
          </div>
        </div>
      )}
      
      {/* Pending overlay for transitions */}
      {isPending && (
        <div className="fixed top-20 left-1/2 transform -translate-x-1/2 z-50">
          <div className="bg-blue-500/90 backdrop-blur-sm rounded-xl shadow-lg p-3 text-white">
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
              <span className="text-sm font-medium">Processando...</span>
            </div>
          </div>
        </div>
      )}



      {/* Notification System */}
      <NotificationSystem
        notifications={notifications}
        onRemoveNotification={removeNotification}
      />
      
      {/* Data Integrity Monitor */}
      <Suspense fallback={<DashboardSkeleton />}>
        <LazyDataIntegrityMonitor
          report={dataIntegrityReport}
          isVisible={showIntegrityMonitor}
          onToggleVisibility={() => setShowIntegrityMonitor(!showIntegrityMonitor)}
        />
      </Suspense>
      
      {/* Performance Dashboard */}
      {showPerformanceDashboard && (
        <Suspense fallback={<DashboardSkeleton />}>
          <LazyPerformanceDashboard
            isVisible={showPerformanceDashboard}
            onClose={() => setShowPerformanceDashboard(false)}
          />
        </Suspense>
      )}
      
      {/* Cache Notifications */}
      {cacheNotifications.map((notification, index) => (
        <div key={notification.id} style={{ top: `${4 + index * 80}px` }} className="fixed right-4 z-50">
          <CacheNotification
            message={notification.message}
            isVisible={true}
            onClose={() => removeCacheNotification(notification.id)}
          />
        </div>
      ))}

    </div>
  );
};

export default App;