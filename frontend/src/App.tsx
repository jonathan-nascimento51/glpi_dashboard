import { useState, useEffect, Profiler, Suspense, ProfilerOnRenderCallback } from 'react';
import { Header } from './components/Header';
import { NotificationSystem } from './components/NotificationSystem';
import CacheNotification from './components/CacheNotification';
import { ModernDashboard } from './components/dashboard/ModernDashboard';
import { LoadingSpinner, SkeletonMetricsGrid, SkeletonLevelsSection, ErrorState } from './components/LoadingSpinner';

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
// import { clearAllCaches } from './services/api'; // Não utilizado

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
    loadData,
    // forceRefresh, // Não utilizado
    updateFilters,
    search,
    addNotification,
    removeNotification,
    changeTheme,
    updateDateRange,
  } = useDashboard();





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



  // Show loading state on initial load
  if (isLoading && !levelMetrics) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
        <div className="animate-pulse">
          {/* Header skeleton */}
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
          
          {/* Content skeleton */}
          <div className="p-6 space-y-8">
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


      
      {/* Dashboard Principal */}
      <div className="flex-1 overflow-hidden">
        {levelMetrics ? (
          <Profiler id="ModernDashboard" onRender={profilerCallback}>
            <ModernDashboard
              metrics={{
                ...levelMetrics?.geral || {},
                tendencias: levelMetrics?.tendencias || {}
              }}
              levelMetrics={levelMetrics}
              systemStatus={systemStatus}
              technicianRanking={technicianRanking}
              onFilterByStatus={handleFilterByStatus}
              isLoading={isLoading}
            />
          </Profiler>
        ) : (
          // Fallback para quando não há dados
          <div className="h-full bg-gradient-to-br from-gray-50 via-white to-gray-100 flex items-center justify-center">
            <div className="text-center py-12">
              <div className="w-24 h-24 bg-gray-200 rounded-full mx-auto mb-4 flex items-center justify-center">
                <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
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