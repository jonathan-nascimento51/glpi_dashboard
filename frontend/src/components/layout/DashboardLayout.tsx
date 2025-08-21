import React, { Suspense } from 'react';
import { Header } from '../Header';
import { NotificationCenter } from '../notifications/NotificationCenter';
import { NotificationSystem } from '../NotificationSystem';
import { ModernDashboard } from '../dashboard/ModernDashboard';
import { LoadingSpinner } from '../LoadingSpinner';
import { DashboardSkeleton } from '../LazyComponents';
import { LazyChartDashboardExample } from '../LazyComponents';
import { Theme, TicketStatus } from '../../types';
import type { DashboardMetrics, LevelMetrics, SystemStatus, TechnicianRanking, Filters, Notification } from '../../types';

interface DashboardLayoutProps {
  // Header props
  searchQuery: string;
  dateRange: { startDate: string; endDate: string; label: string };
  filterType: string;
  availableFilterTypes: string[];
  theme: Theme;
  
  // Dashboard props
  metrics?: DashboardMetrics;
  levelMetrics?: LevelMetrics;
  systemStatus?: SystemStatus;
  technicianRanking?: TechnicianRanking[];
  filters?: Filters;
  isLoading: boolean;
  isPending: boolean;
  showChartExample: boolean;
  
  // Notifications
  notifications: Notification[];
  
  // Event handlers
  onSearch: (query: string) => void;
  onThemeChange: (theme: Theme) => void;
  onNotification: (title: string, message: string, type: 'success' | 'error' | 'warning' | 'info') => void;
  onDateRangeChange: (range: { startDate: string; endDate: string; label: string }) => void;
  onFilterTypeChange: (type: string) => void;
  onPerformanceDashboard: () => void;
  onChartExample: () => void;
  onFilterByStatus: (status: TicketStatus) => void;
  onRemoveNotification: (id: string) => void;
  onLoadData: () => void;
}

export const DashboardLayout: React.FC<DashboardLayoutProps> = ({
  searchQuery,
  dateRange,
  filterType,
  availableFilterTypes,
  theme,
  metrics,
  levelMetrics,
  systemStatus,
  technicianRanking,
  filters,
  isLoading,
  isPending,
  showChartExample,
  notifications,
  onSearch,
  onThemeChange,
  onNotification,
  onDateRangeChange,
  onFilterTypeChange,
  onPerformanceDashboard,
  onChartExample,
  onFilterByStatus,
  onRemoveNotification,
  onLoadData,
}) => {
  return (
    <div className={`h-screen overflow-hidden transition-all duration-300 ${theme}`}>
      {/* Header */}
      <Header
        currentTime={new Date().toLocaleTimeString('pt-BR')}
        systemActive={true}
        searchQuery={searchQuery}
        searchResults={[]}
        dateRange={dateRange}
        filterType={filterType}
        availableFilterTypes={availableFilterTypes}
        onSearch={onSearch}
        theme={theme}
        onThemeChange={onThemeChange}
        onNotification={onNotification}
        onDateRangeChange={onDateRangeChange}
        onFilterTypeChange={onFilterTypeChange}
        onPerformanceDashboard={onPerformanceDashboard}
        onChartExample={onChartExample}
        showChartExample={showChartExample}
      />

      {/* Notification Center */}
      <NotificationCenter />

      {/* Dashboard Principal */}
      <div className='flex-1 overflow-hidden'>
        {showChartExample ? (
          <Suspense fallback={<DashboardSkeleton />}>
            <LazyChartDashboardExample />
          </Suspense>
        ) : levelMetrics ? (
          <ModernDashboard
            metrics={{
              novos: metrics?.novos || 0,
              pendentes: metrics?.pendentes || 0,
              progresso: metrics?.progresso || 0,
              resolvidos: metrics?.resolvidos || 0,
              tendencias: metrics?.tendencias || {},
            }}
            levelMetrics={levelMetrics}
            systemStatus={systemStatus}
            technicianRanking={technicianRanking}
            onFilterByStatus={onFilterByStatus}
            isLoading={isLoading}
            filters={filters}
          />
        ) : (
          <DashboardFallback onLoadData={onLoadData} />
        )}
      </div>

      {/* Loading overlay for refresh */}
      {isLoading && levelMetrics && (
        <div className='fixed top-20 right-6 z-50'>
          <div className='bg-white/90 backdrop-blur-sm rounded-xl shadow-lg p-4'>
            <LoadingSpinner size='sm' text='Atualizando...' />
          </div>
        </div>
      )}

      {/* Pending overlay for transitions */}
      {isPending && (
        <div className='fixed top-20 left-1/2 transform -translate-x-1/2 z-50'>
          <div className='bg-blue-500/90 backdrop-blur-sm rounded-xl shadow-lg p-3 text-white'>
            <div className='flex items-center space-x-2'>
              <div className='animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent'></div>
              <span className='text-sm font-medium'>Processando...</span>
            </div>
          </div>
        </div>
      )}

      {/* Notification System */}
      <NotificationSystem 
        notifications={notifications} 
        onRemoveNotification={onRemoveNotification} 
      />
    </div>
  );
};

// Componente de fallback quando não há dados
const DashboardFallback: React.FC<{ onLoadData: () => void }> = ({ onLoadData }) => (
  <div className='h-full bg-gradient-to-br from-gray-50 via-white to-gray-100 flex items-center justify-center'>
    <div className='text-center py-12'>
      <div className='w-24 h-24 bg-gray-200 rounded-full mx-auto mb-4 flex items-center justify-center'>
        <svg
          className='w-12 h-12 text-gray-400'
          fill='none'
          stroke='currentColor'
          viewBox='0 0 24 24'
        >
          <path
            strokeLinecap='round'
            strokeLinejoin='round'
            strokeWidth={2}
            d='M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z'
          />
        </svg>
      </div>
      <h3 className='text-lg font-semibold text-gray-900 mb-2'>Nenhum dado disponível</h3>
      <p className='text-gray-600 mb-4'>Não foi possível carregar os dados do dashboard.</p>
      <button
        onClick={onLoadData}
        className='px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors'
      >
        Tentar Novamente
      </button>
    </div>
  </div>
);