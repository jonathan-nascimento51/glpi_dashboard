import React, { Suspense, useState } from 'react';
import ProfessionalDashboard from './components/ProfessionalDashboard';
import { DashboardSkeleton } from './components/LazyComponents';
import PWAManager from './components/PWAManager';
import { useResourcePreload } from './hooks/useResourcePreload';
import { ThemeProvider } from './lib/theme-provider';
import { initializeAxe, AccessibilityValidator } from './lib/accessibility';
import './App.css';

// Lazy loading dos componentes opcionais
const LazyDataIntegrityMonitor = React.lazy(() => import('./components/DataIntegrityMonitor'));
const LazyPerformanceDashboard = React.lazy(() => import('./components/PerformanceDashboard'));

// Inicializar axe-core para validação de acessibilidade em desenvolvimento
if (process.env.NODE_ENV === 'development') {
  initializeAxe();
}

function App() {
  const [showIntegrityMonitor, setShowIntegrityMonitor] = useState(false);
  const [showPerformanceDashboard, setShowPerformanceDashboard] = useState(false);

  // Ativar preload de recursos críticos
  useResourcePreload({ enabled: true, priority: 'high' });

  return (
    <ThemeProvider defaultTheme="system" storageKey="glpi-dashboard-theme">
      <AccessibilityValidator name="app-root">
        <div className="App">
          <PWAManager />

          {/* Dashboard principal */}
          <Suspense fallback={<DashboardSkeleton />}>
            <AccessibilityValidator name="main-dashboard">
              <ProfessionalDashboard />
            </AccessibilityValidator>
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
              <AccessibilityValidator name="integrity-monitor">
                <LazyDataIntegrityMonitor />
              </AccessibilityValidator>
            </Suspense>
          )}

          {showPerformanceDashboard && (
            <Suspense fallback={<div>Carregando Dashboard de Performance...</div>}>
              <AccessibilityValidator name="performance-dashboard">
                <LazyPerformanceDashboard />
              </AccessibilityValidator>
            </Suspense>
          )}
        </div>
      </AccessibilityValidator>
    </ThemeProvider>
  );
}

export default App;
