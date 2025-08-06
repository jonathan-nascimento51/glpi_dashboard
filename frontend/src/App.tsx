import { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { FilterPanel } from './components/FilterPanel';
import { NotificationSystem } from './components/NotificationSystem';
import SimplifiedDashboard from './components/SimplifiedDashboard';
import DataIntegrityMonitor from './components/DataIntegrityMonitor';
import { ModernDashboard } from './components/dashboard/ModernDashboard';
import { LoadingSpinner, SkeletonMetricsGrid, SkeletonLevelsSection, ErrorState } from './components/LoadingSpinner';
import { useDashboard } from './hooks/useDashboard';
import { TicketStatus } from './types';

function App() {
  const {
    metrics,
    systemStatus,
    technicianRanking,
    isLoading,
    error,
    lastUpdated,
    filters,
    searchQuery,
    searchResults,
    notifications,
    theme,
    isSimplifiedMode,
    monitoringAlerts,
    dataIntegrityReport,
    dateRange,
    loadData,
    forceRefresh,
    updateFilters,
    search,
    addNotification,
    removeNotification,
    changeTheme,
    toggleSimplifiedMode,
    updateDateRange,
  } = useDashboard();

  const [showFilters, setShowFilters] = useState(false);
  const [showIntegrityMonitor, setShowIntegrityMonitor] = useState(true);
  const [showMonitoringAlerts, setShowMonitoringAlerts] = useState(true);
  const [currentTime, setCurrentTime] = useState('');

  // Update current time
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setCurrentTime(now.toLocaleTimeString('pt-BR', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      }));
    };

    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  // Handle filter by status
  const handleFilterByStatus = (status: TicketStatus) => {
    updateFilters({ status: [status] });
    setShowFilters(true);
    addNotification({
      title: 'Filtro Aplicado',
      message: `Exibindo apenas chamados com status: ${getStatusLabel(status)}`,
      type: 'info',
      duration: 3000,
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

  // Handle refresh with notification
  const handleRefresh = () => {
    forceRefresh();
    addNotification({
      title: 'Dados Atualizados',
      message: 'Dashboard atualizado com sucesso',
      type: 'success',
      duration: 2000,
    });
  };

  // Handle search with debouncing
  useEffect(() => {
    const debounceTimer = setTimeout(() => {
      if (searchQuery.trim()) {
        search(searchQuery);
      }
    }, 300);

    return () => clearTimeout(debounceTimer);
  }, [searchQuery, search]);

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Escape to close panels
      if (e.key === 'Escape') {
        setShowFilters(false);
      }
      
      // F5 or Ctrl/Cmd + R for refresh
      if (e.key === 'F5' || ((e.ctrlKey || e.metaKey) && e.key === 'r')) {
        e.preventDefault();
        handleRefresh();
      }
      
      // Number keys for quick period filters
      if (e.key >= '1' && e.key <= '3') {
        e.preventDefault();
        const periods = ['today', 'week', 'month'] as const;
        const periodIndex = parseInt(e.key) - 1;
        if (periods[periodIndex]) {
          updateFilters({ period: periods[periodIndex] });
          addNotification({
            title: 'Período Alterado',
            message: `Filtro alterado para: ${getPeriodLabel(periods[periodIndex])}`,
            type: 'info',
            duration: 2000,
          });
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [updateFilters, addNotification]);

  // Get period label
  const getPeriodLabel = (period: string): string => {
    const labels = {
      today: 'Hoje',
      week: 'Esta Semana',
      month: 'Este Mês',
    };
    return labels[period as keyof typeof labels] || period;
  };

  // Show loading state on initial load
  if (isLoading && !metrics) {
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
        currentTime={currentTime}
        systemActive={systemStatus?.sistema_ativo ?? false}
        theme={theme}
        searchQuery={searchQuery}
        searchResults={searchResults}
        isSimplifiedMode={isSimplifiedMode}
        showMonitoringAlerts={showMonitoringAlerts}
        alertsCount={monitoringAlerts.filter(alert => !alert.acknowledged).length}
        dateRange={dateRange}
        onDateRangeChange={updateDateRange}
        onThemeChange={changeTheme}
        onSearch={search}
        onRefresh={handleRefresh}
        onToggleFilters={() => setShowFilters(!showFilters)}
        onToggleSimplifiedMode={toggleSimplifiedMode}
        onToggleMonitoringAlerts={() => setShowMonitoringAlerts(!showMonitoringAlerts)}
        onNotification={(title, message, type) => addNotification({ title, message, type, duration: 3000 })}
        isLoading={isLoading}
        lastUpdated={lastUpdated}
      />

      {/* Dashboard Principal - Interface Fixa para TV */}
      <div className="flex-1 overflow-hidden">
        {!isSimplifiedMode && metrics ? (
          <ModernDashboard
            metrics={metrics}
            systemStatus={systemStatus}
            technicianRanking={technicianRanking}
            onFilterByStatus={handleFilterByStatus}
            isLoading={isLoading}
          />
        ) : isSimplifiedMode && metrics ? (
          <SimplifiedDashboard
            metrics={metrics}
            technicianRanking={technicianRanking}
            isLoading={isLoading}
            dateRange={dateRange}
            onDateRangeChange={updateDateRange}
          />
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
                onClick={loadData} 
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Tentar Novamente
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Loading overlay for refresh */}
      {isLoading && metrics && (
        <div className="fixed top-20 right-6 z-50">
          <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-lg p-4">
            <LoadingSpinner size="sm" text="Atualizando..." />
          </div>
        </div>
      )}

      {/* Filter Panel - Only show in normal mode */}
      {!isSimplifiedMode && (
        <FilterPanel
          isOpen={showFilters}
          filters={filters}
          onClose={() => setShowFilters(false)}
          onFiltersChange={updateFilters}
        />
      )}

      {/* Notification System */}
      <NotificationSystem
        notifications={notifications}
        onRemoveNotification={removeNotification}
      />
      
      {/* Data Integrity Monitor */}
      <DataIntegrityMonitor
        report={dataIntegrityReport}
        isVisible={showIntegrityMonitor}
        onToggleVisibility={() => setShowIntegrityMonitor(!showIntegrityMonitor)}
      />
    </div>
  );
};

export default App;