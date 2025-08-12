import React, { Suspense, useState } from 'react';
import ProfessionalDashboard from './components/ProfessionalDashboard';
import { DashboardSkeleton } from './components/LazyComponents';
import PWAManager from './components/PWAManager';
import { useResourcePreload } from './hooks/useResourcePreload';
import { useDashboard } from './hooks/useDashboard';
import { ThemeProvider } from './lib/theme-provider';
import type { DashboardMetrics } from './types/api';
import './App.css';

// Lazy loading dos componentes opcionais
const LazyDataIntegrityMonitor = React.lazy(() => import('./components/DataIntegrityMonitor'));
const LazyPerformanceDashboard = React.lazy(() => import('./components/PerformanceDashboard'));

function App() {
  const [showIntegrityMonitor, setShowIntegrityMonitor] = useState(false);
  const [showPerformanceDashboard, setShowPerformanceDashboard] = useState(false);
  
  // Hook para gerenciar dados do dashboard
  const {
    metrics,
    technicianRanking,
    isLoading,
    forceRefresh,
    updateDateRange
  } = useDashboard();

  // Ativar preload de recursos críticos
  useResourcePreload({ enabled: true, priority: 'high' });

  // Estado para controle de data range
  const [dateRange, setDateRange] = useState({
    startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    endDate: new Date().toISOString().split('T')[0],
    label: 'Últimos 30 dias'
  });

  const handleDateRangeChange = (newRange: any) => {
    setDateRange(newRange);
    updateDateRange(newRange);
  };

  // Converter DashboardMetrics para MetricsData
  const convertedMetrics = metrics ? {
    novos: metrics.niveis?.geral?.novos || 0,
    pendentes: metrics.niveis?.geral?.pendentes || 0,
    progresso: metrics.niveis?.geral?.progresso || 0,
    resolvidos: metrics.niveis?.geral?.resolvidos || 0,
    total: metrics.niveis?.geral?.total || 0,
    niveis: metrics.niveis || {
      n1: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 },
      n2: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 },
      n3: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 },
      n4: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 },
      geral: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 }
    },
    tendencias: metrics.tendencias || {
      novos: 'stable',
      pendentes: 'stable',
      progresso: 'stable',
      resolvidos: 'stable'
    }
  } : null;

  return (
    <ThemeProvider storageKey="glpi-dashboard-theme">
      <div className="App">
        <PWAManager />

        {/* Dashboard principal */}
        <Suspense fallback={<DashboardSkeleton />}>
          <ProfessionalDashboard 
            metrics={convertedMetrics}
            technicianRanking={technicianRanking}
            isLoading={isLoading}
            dateRange={dateRange}
            onDateRangeChange={handleDateRangeChange}
            onRefresh={forceRefresh}
          />
        </Suspense>

          {/* Controles para componentes opcionais */}
          <div 
            style={{ 
              position: 'fixed', 
              bottom: '20px', 
              left: '20px', 
              zIndex: 1000,
              display: 'flex',
              flexDirection: 'column',
              gap: '8px'
            }}
          >
            <button
              onClick={() => setShowIntegrityMonitor(!showIntegrityMonitor)}
              style={{ 
                margin: '0', 
                padding: '10px 16px',
                backgroundColor: 'var(--primary)',
                color: 'var(--primary-foreground)',
                border: 'none',
                borderRadius: 'var(--radius)',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '500'
              }}
              aria-label={`${showIntegrityMonitor ? 'Ocultar' : 'Mostrar'} Monitor de Integridade`}
            >
              {showIntegrityMonitor ? 'Ocultar' : 'Mostrar'} Monitor de Integridade
            </button>
            
            <button
              onClick={() => setShowPerformanceDashboard(!showPerformanceDashboard)}
              style={{ 
                margin: '0', 
                padding: '10px 16px',
                backgroundColor: 'var(--secondary)',
                color: 'var(--secondary-foreground)',
                border: 'none',
                borderRadius: 'var(--radius)',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '500'
              }}
              aria-label={`${showPerformanceDashboard ? 'Ocultar' : 'Mostrar'} Dashboard de Performance`}
            >
              {showPerformanceDashboard ? 'Ocultar' : 'Mostrar'} Dashboard de Performance
            </button>
          </div>

        {/* Componentes opcionais */}
        {showIntegrityMonitor && (
          <Suspense fallback={<div>Carregando Monitor de Integridade...</div>}>
            <LazyDataIntegrityMonitor 
              report={null}
              isVisible={showIntegrityMonitor}
              onToggleVisibility={() => setShowIntegrityMonitor(!showIntegrityMonitor)}
            />
          </Suspense>
        )}

        {showPerformanceDashboard && (
          <Suspense fallback={<div>Carregando Dashboard de Performance...</div>}>
            <LazyPerformanceDashboard 
              isVisible={showPerformanceDashboard}
              onClose={() => setShowPerformanceDashboard(false)}
            />
          </Suspense>
        )}
      </div>
    </ThemeProvider>
  );
}

export default App;
