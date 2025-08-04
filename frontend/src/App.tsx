import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { MetricsGrid } from './components/MetricsGrid';
import { LevelsSection } from './components/LevelsSection';
import { FilterPanel } from './components/FilterPanel';
import { NotificationSystem } from './components/NotificationSystem';
import { SimplifiedDashboard } from './components/SimplifiedDashboard';
import { LoadingSpinner, SkeletonMetricsGrid, SkeletonLevelsSection, ErrorState } from './components/LoadingSpinner';
import { useDashboard } from './hooks/useDashboard';
import { TicketStatus } from './types';

function App() {
  const {
    metrics,
    systemStatus,
    isLoading,
    error,
    lastUpdated,
    filters,
    searchQuery,
    searchResults,
    notifications,
    theme,
    isSimplifiedMode,
    technicianRanking,
    loadData,
    forceRefresh,
    updateFilters,
    search,
    addNotification,
    removeNotification,
    changeTheme,
    toggleSimplifiedMode,
  } = useDashboard();

  const [showFilters, setShowFilters] = useState(false);
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
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="animate-pulse">
          {/* Header skeleton */}
          <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="w-10 h-10 bg-gray-200 dark:bg-gray-700 rounded-lg" />
                <div className="space-y-2">
                  <div className="w-48 h-5 bg-gray-200 dark:bg-gray-700 rounded" />
                  <div className="w-32 h-3 bg-gray-200 dark:bg-gray-700 rounded" />
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="w-64 h-10 bg-gray-200 dark:bg-gray-700 rounded-lg" />
                <div className="w-32 h-8 bg-gray-200 dark:bg-gray-700 rounded" />
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
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <ErrorState
          title="Erro ao Carregar Dashboard"
          message={error}
          onRetry={loadData}
        />
      </div>
    );
  }

  return (
    <div className={`min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200 ${theme}`}>
      {/* Header */}
      <Header
        currentTime={currentTime}
        systemActive={systemStatus?.sistema_ativo ?? false}
        theme={theme}
        searchQuery={searchQuery}
        searchResults={searchResults}
        isSimplifiedMode={isSimplifiedMode}
        onThemeChange={changeTheme}
        onSearch={search}
        onRefresh={handleRefresh}
        onToggleFilters={() => setShowFilters(!showFilters)}
        onToggleSimplifiedMode={toggleSimplifiedMode}
        onNotification={(title, message, type) => addNotification({ title, message, type, duration: 3000 })}
      />

      {/* Simplified Dashboard */}
      {isSimplifiedMode && metrics ? (
        <SimplifiedDashboard
          metrics={metrics}
          technicianRanking={technicianRanking}
          currentTime={currentTime}
          lastUpdated={lastUpdated}
        />
      ) : (
        <main className="p-6 space-y-8">
        {/* Loading overlay for refresh */}
        {isLoading && metrics && (
          <div className="fixed top-20 right-6 z-40">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-3">
              <LoadingSpinner size="sm" text="Atualizando..." />
            </div>
          </div>
        )}

        {/* Metrics Section */}
        {metrics && (
          <section>
            <div className="mb-6">
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                Dashboard de Métricas
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mt-2">
                Monitoramento em tempo real dos chamados de suporte
                {lastUpdated && (
                  <span className="ml-2 text-sm">
                    • Última atualização: {lastUpdated.toLocaleTimeString('pt-BR')}
                  </span>
                )}
              </p>
            </div>
            <MetricsGrid
              metrics={metrics}
              onFilterByStatus={handleFilterByStatus}
            />
          </section>
        )}

        {/* Levels Section */}
        {metrics && (
          <section>
            <LevelsSection metrics={metrics} />
          </section>
        )}

        {/* Empty state when no data */}
        {!metrics && !isLoading && !error && (
          <div className="text-center py-12">
            <div className="w-24 h-24 bg-gray-200 dark:bg-gray-700 rounded-full mx-auto mb-4 flex items-center justify-center">
              <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              Nenhum dado disponível
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              Não foi possível carregar os dados do dashboard.
            </p>
            <button onClick={loadData} className="btn-primary">
              Tentar Novamente
            </button>
          </div>
        )}
        </main>
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
    </div>
  );
}

export default App;