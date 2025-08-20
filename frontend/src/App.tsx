import { useState, useEffect, Profiler, Suspense, ProfilerOnRenderCallback } from 'react';
import { Header } from './components/Header';
import { NotificationSystem } from './components/NotificationSystem';
import CacheNotification from './components/CacheNotification';
import { ModernDashboard } from './components/dashboard/ModernDashboard';
import {
  LoadingSpinner,
  SkeletonMetricsGrid,
  SkeletonLevelsSection,
  ErrorState,
} from './components/LoadingSpinner';
import { MetricsValidator } from './utils/metricsValidator';
import { visualValidator } from './utils/visualValidator';
import { dataIntegrityMonitor } from './utils/dataIntegrityMonitor';
import { preDeliveryValidator } from './utils/preDeliveryValidator';
import { workflowOptimizer } from './utils/workflowOptimizer';
import { realTimeMonitor } from './utils/realTimeMonitor';

// Componentes lazy centralizados
import {
  LazyDataIntegrityMonitor,
  LazyPerformanceDashboard,
  DashboardSkeleton,
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
    filterType,
    availableFilterTypes,
    loadData,
    // forceRefresh, // Não utilizado
    updateFilters,
    updateFilterType,
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

  // Validação automática de métricas (DESABILITADA TEMPORARIAMENTE)
  // useEffect(() => {
  //   if (metrics) {
  //     const frontendValidation = MetricsValidator.validateFrontendDataProcessing({
  //       novos: metrics.novos,
  //       pendentes: metrics.pendentes,
  //       progresso: metrics.progresso,
  //       resolvidos: metrics.resolvidos,
  //     });
  //
  //     if (!frontendValidation.isValid) {
  //       console.error('❌ VALIDAÇÃO FALHOU - Problemas encontrados:', frontendValidation.errors);
  //     }
  //   }
  // }, [metrics]);

  // Validação visual automática após renderização (DESABILITADA TEMPORARIAMENTE)
  useEffect(() => {
    if (metrics) {
      // Aguardar renderização completa antes de validar visualmente
      const timer = setTimeout(async () => {
        try {
          console.log('🎯 App.tsx - Validação visual desabilitada temporariamente');
          // const visualResult = await visualValidator.validateDashboardRendering();

          // if (visualResult.isValid) {
          //   console.log('✅ VALIDAÇÃO VISUAL PASSOU - Dashboard renderizado corretamente');
          // } else {
          //   console.error('❌ VALIDAÇÃO VISUAL FALHOU:', visualResult.errors);
          //   // Em desenvolvimento, mostrar alerta para problemas críticos
          //   if (process.env.NODE_ENV === 'development' && visualResult.errors.length > 0) {
          //     console.warn('🚨 ATENÇÃO: Problemas de renderização detectados!');
          //   }
          // }
        } catch (error) {
          console.error('💥 Erro durante validação visual:', error);
        }
      }, 1500); // Aguardar 1.5s para renderização completa

      return () => clearTimeout(timer);
    }
  }, [metrics]);

  // Monitoramento de integridade de dados em tempo real (DESABILITADO TEMPORARIAMENTE)
  // useEffect(() => {
  //   // Configurar alertas para problemas críticos
  //   dataIntegrityMonitor.onAlert(report => {
  //     if (report.overallStatus === 'critical') {
  //       console.error('🚨 ALERTA CRÍTICO: Problemas graves de integridade detectados!');
  //       console.error('📋 Relatório:', report);

  //       if (process.env.NODE_ENV === 'development') {
  //         const criticalIssues = report.checks
  //           .filter(c => !c.isValid && c.severity === 'critical')
  //           .map(c => c.name)
  //           .join(', ');
  //         alert(
  //           `🚨 PROBLEMAS CRÍTICOS DETECTADOS:\n${criticalIssues}\n\nVerifique o console para detalhes.`
  //         );
  //       }
  //     } else if (report.overallStatus === 'warning') {
  //       console.warn('⚠️ Avisos de integridade detectados:', report.summary);
  //     }
  //   });

  //   // Iniciar monitoramento (já configurado para auto-start em desenvolvimento)
  //   // Em produção, pode ser iniciado manualmente se necessário
  //   // DESABILITADO TEMPORARIAMENTE
  //   // if (process.env.NODE_ENV === 'production') {
  //   //   dataIntegrityMonitor.startMonitoring();
  //   // }

  //   // Cleanup ao desmontar
  //   return () => {
  //     dataIntegrityMonitor.stopMonitoring();
  //   };
  // }, []);

  // Configuração do validador pré-entrega
  useEffect(() => {
    // Disponibilizar validador globalmente para uso no console
    (window as any).preDeliveryValidator = preDeliveryValidator;

    // Configurar validador para ambiente de desenvolvimento
    if (process.env.NODE_ENV === 'development') {
      preDeliveryValidator.configure({
        requireFullPipeline: false, // Pipeline mais rápido em dev
        allowConditionalDelivery: true,
        minimumScore: 75, // Score mais baixo em dev
        criticalIssueThreshold: 0,
      });

      console.log('🔧 Validador Pré-Entrega configurado para desenvolvimento');
      console.log('Comandos disponíveis:');
      console.log('  - validateForDelivery() - Validação completa');
      console.log('  - quickValidation() - Validação rápida');
      console.log('  - hasValidApproval() - Verificar aprovação válida');
      console.log('  - getLastApproval() - Última aprovação');
    } else {
      // Configuração mais rigorosa para produção
      preDeliveryValidator.configure({
        requireFullPipeline: true,
        allowConditionalDelivery: false,
        minimumScore: 90,
        criticalIssueThreshold: 0,
      });
    }
  }, []);

  // Configuração do monitor em tempo real
  useEffect(() => {
    // Disponibilizar ferramentas globalmente
    (window as any).workflowOptimizer = workflowOptimizer;
    (window as any).realTimeMonitor = realTimeMonitor;

    // Configurar monitor para ambiente
    if (process.env.NODE_ENV === 'development') {
      realTimeMonitor.configure({
        enabled: true,
        checkInterval: 15000, // 15 segundos em dev
        alertThresholds: {
          consecutiveFailures: 2,
          responseTimeMs: 3000,
          zeroMetricsThreshold: 30, // 30 segundos
        },
        autoRecovery: {
          enabled: true,
          maxAttempts: 2,
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

      console.log('🔧 Monitor em Tempo Real configurado para desenvolvimento');
      console.log('Comandos disponíveis:');
      console.log('  - startMonitoring() - Iniciar monitoramento');
      console.log('  - stopMonitoring() - Parar monitoramento');
      console.log('  - getSystemStatus() - Status do sistema');
      console.log('  - executeOptimizedWorkflow() - Executar workflow otimizado');
      console.log('  - quickWorkflow() - Workflow rápido');

      // Iniciar monitoramento automaticamente em dev (DESABILITADO TEMPORARIAMENTE)
      // setTimeout(() => {
      //   realTimeMonitor.startMonitoring();
      // }, 2000); // Aguardar 2 segundos para o app carregar
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

      // Iniciar monitoramento em produção (DESABILITADO TEMPORARIAMENTE)
      // realTimeMonitor.startMonitoring();
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
    <div className={`h-screen overflow-hidden transition-all duration-300 ${theme}`}>
      {/* Header */}
      <Header
        currentTime={new Date().toLocaleTimeString('pt-BR')}
        systemActive={true}
        searchQuery={searchQuery}
        searchResults={[]}
        dateRange={
          filters?.dateRange || { startDate: '', endDate: '', label: 'Selecionar período' }
        }
        filterType={filterType}
        availableFilterTypes={availableFilterTypes}
        onSearch={search}
        theme={theme as Theme}
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
        onPerformanceDashboard={() => setShowPerformanceDashboard(true)}
      />

      {/* Dashboard Principal */}
      <div className='flex-1 overflow-hidden'>
        {levelMetrics ? (
          <Profiler id='ModernDashboard' onRender={profilerCallback}>
            {(() => {
              const dashboardMetrics = {
                novos: metrics?.novos || 0,
                pendentes: metrics?.pendentes || 0,
                progresso: metrics?.progresso || 0,
                resolvidos: metrics?.resolvidos || 0,
                tendencias: metrics?.tendencias || {},
              };
              console.log(
                '🎯 App.tsx - Métricas sendo passadas para ModernDashboard:',
                dashboardMetrics
              );
              console.log('🔍 App.tsx - Objeto metrics completo:', metrics);
              return (
                <ModernDashboard
                  metrics={dashboardMetrics}
                  levelMetrics={levelMetrics}
                  systemStatus={systemStatus}
                  technicianRanking={technicianRanking}
                  onFilterByStatus={handleFilterByStatus}
                  isLoading={isLoading}
                  filters={filters}
                />
              );
            })()}
          </Profiler>
        ) : (
          // Fallback para quando não há dados
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
                onClick={() => loadData()}
                className='px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors'
              >
                Tentar Novamente
              </button>
            </div>
          </div>
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
      <NotificationSystem notifications={notifications} onRemoveNotification={removeNotification} />

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
        <div
          key={notification.id}
          style={{ top: `${4 + index * 80}px` }}
          className='fixed right-4 z-50'
        >
          <CacheNotification
            message={notification.message}
            isVisible={true}
            onClose={() => removeCacheNotification(notification.id)}
          />
        </div>
      ))}
    </div>
  );
}

export default App;
