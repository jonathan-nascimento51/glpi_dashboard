/**
 * Hook personalizado para monitoramento de performance em componentes React
 * Integra com React DevTools Profiler e Performance API
 */

import { useEffect, useRef, useCallback, useState } from 'react';
import { performanceMonitor, PerformanceReport } from '../utils/performanceMonitor';

/**
 * Hook para monitorar performance de componentes
 */
export const usePerformanceMonitoring = (componentName: string) => {
  const renderStartTime = useRef<number>(0);
  const mountTime = useRef<number>(0);
  const renderCount = useRef<number>(0);

  useEffect(() => {
    mountTime.current = performance.now();
    performanceMonitor.startMeasure(`${componentName}-mount`);

    return () => {
      performanceMonitor.endMeasure(`${componentName}-mount`);
    };
  }, [componentName]);

  const startRender = useCallback(() => {
    renderStartTime.current = performance.now();
    renderCount.current++;
    performanceMonitor.startMeasure(`${componentName}-render-${renderCount.current}`);
  }, [componentName]);

  const endRender = useCallback(
    (props?: any) => {
      if (renderStartTime.current > 0) {
        const renderTime = performance.now() - renderStartTime.current;
        performanceMonitor.recordComponentRender(componentName, renderTime, props);
        performanceMonitor.endMeasure(`${componentName}-render-${renderCount.current}`);
        renderStartTime.current = 0;
      }
    },
    [componentName]
  );

  const measureRender = useCallback(
    (renderFunction: () => void) => {
      startRender();
      try {
        renderFunction();
      } finally {
        endRender();
      }
    },
    [startRender, endRender]
  );

  return {
    startRender,
    endRender,
    measureRender,
    renderCount: renderCount.current,
  };
};

/**
 * Hook para monitorar operações de filtro
 */
export const useFilterPerformance = () => {
  const [isFiltering, setIsFiltering] = useState(false);
  const [lastFilterTime, setLastFilterTime] = useState<number>(0);

  const measureFilterOperation = useCallback(
    async <T>(filterType: string, operation: () => Promise<T>): Promise<T> => {
      setIsFiltering(true);

      try {
        const result = await performanceMonitor.measureFilterOperation(filterType, operation);
        const duration = performanceMonitor.endMeasure(`filter-${filterType}`);
        setLastFilterTime(duration);
        return result;
      } finally {
        setIsFiltering(false);
      }
    },
    []
  );

  const measureSyncFilterOperation = useCallback(<T>(filterType: string, operation: () => T): T => {
    setIsFiltering(true);
    performanceMonitor.startMeasure(`filter-${filterType}-sync`);

    try {
      const result = operation();
      const duration = performanceMonitor.endMeasure(`filter-${filterType}-sync`);
      setLastFilterTime(duration);
      return result;
    } finally {
      setIsFiltering(false);
    }
  }, []);

  return {
    measureFilterOperation,
    measureSyncFilterOperation,
    isFiltering,
    lastFilterTime,
  };
};

/**
 * Hook para monitorar chamadas de API
 */
export const useApiPerformance = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [lastApiTime, setLastApiTime] = useState<number>(0);
  const [apiMetrics, setApiMetrics] = useState<
    {
      endpoint: string;
      duration: number;
      timestamp: number;
    }[]
  >([]);

  const measureApiCall = useCallback(
    async <T>(endpoint: string, apiCall: () => Promise<T>): Promise<T> => {
      setIsLoading(true);
      const startTime = performance.now();

      try {
        const result = await performanceMonitor.measureApiCall(endpoint, apiCall);
        const duration = performance.now() - startTime;

        setLastApiTime(duration);
        setApiMetrics(prev => [
          ...prev.slice(-9), // Manter apenas os últimos 10
          {
            endpoint,
            duration,
            timestamp: Date.now(),
          },
        ]);

        return result;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const getAverageApiTime = useCallback(() => {
    if (apiMetrics.length === 0) return 0;
    return apiMetrics.reduce((sum, metric) => sum + metric.duration, 0) / apiMetrics.length;
  }, [apiMetrics]);

  return {
    measureApiCall,
    isLoading,
    lastApiTime,
    apiMetrics,
    averageApiTime: getAverageApiTime(),
  };
};

/**
 * Hook para relatórios de performance
 */
export const usePerformanceReports = () => {
  const [reports, setReports] = useState<PerformanceReport[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);

  const generateReport = useCallback(async () => {
    setIsGenerating(true);

    try {
      // Aguardar um pouco para capturar métricas pendentes
      await new Promise(resolve => setTimeout(resolve, 100));

      const report = performanceMonitor.generateReport();
      setReports(prev => [...prev.slice(-9), report]); // Manter últimos 10

      // Log detalhado em desenvolvimento
      if (process.env.NODE_ENV === 'development') {
        console.group('📊 Performance Report');
        console.log('Summary:', report.summary);
        console.log('Component Metrics:', report.componentMetrics);
        console.log('All Metrics:', report.metrics);
        console.groupEnd();
      }

      return report;
    } finally {
      setIsGenerating(false);
    }
  }, []);

  const clearReports = useCallback(() => {
    setReports([]);
    performanceMonitor.clear();
  }, []);

  const exportToAnalytics = useCallback(() => {
    performanceMonitor.exportToAnalytics();
  }, []);

  const getLatestReport = useCallback(() => {
    return reports[reports.length - 1] || null;
  }, [reports]);

  const getAverageMetrics = useCallback(() => {
    if (reports.length === 0) return null;

    const totals = reports.reduce(
      (acc, report) => ({
        filterChangeTime: acc.filterChangeTime + report.summary.filterChangeTime,
        apiResponseTime: acc.apiResponseTime + report.summary.apiResponseTime,
        renderTime: acc.renderTime + report.summary.renderTime,
        totalOperationTime: acc.totalOperationTime + report.summary.totalOperationTime,
      }),
      { filterChangeTime: 0, apiResponseTime: 0, renderTime: 0, totalOperationTime: 0 }
    );

    const count = reports.length;
    return {
      filterChangeTime: totals.filterChangeTime / count,
      apiResponseTime: totals.apiResponseTime / count,
      renderTime: totals.renderTime / count,
      totalOperationTime: totals.totalOperationTime / count,
    };
  }, [reports]);

  return {
    reports,
    generateReport,
    clearReports,
    exportToAnalytics,
    isGenerating,
    latestReport: getLatestReport(),
    averageMetrics: getAverageMetrics(),
  };
};

/**
 * Hook para debugging de performance em desenvolvimento
 */
export const usePerformanceDebug = () => {
  const [isEnabled, setIsEnabled] = useState(process.env.NODE_ENV === 'development');
  const [debugInfo, setDebugInfo] = useState<any>(null);

  const toggleMonitoring = useCallback(() => {
    const newState = !isEnabled;
    setIsEnabled(newState);
    performanceMonitor.setEnabled(newState);
  }, [isEnabled]);

  const getDebugInfo = useCallback(() => {
    const stats = performanceMonitor.getDetailedStats();
    const browserMetrics = performanceMonitor.getBrowserMetrics();

    const info = {
      stats,
      browserMetrics: browserMetrics.slice(-10), // Últimas 10 métricas
      timestamp: new Date().toISOString(),
    };

    setDebugInfo(info);
    return info;
  }, []);

  const logMetrics = useCallback(() => {
    const info = getDebugInfo();
    console.group('🔍 Performance Debug Info');
    console.log('Stats:', info.stats);
    console.log('Browser Metrics:', info.browserMetrics);
    console.groupEnd();
  }, [getDebugInfo]);

  const clearMetrics = useCallback(() => {
    performanceMonitor.clear();
    setDebugInfo(null);
  }, []);

  return {
    isEnabled,
    toggleMonitoring,
    getDebugInfo,
    logMetrics,
    clearMetrics,
    debugInfo,
  };
};

/**
 * Hook para monitoramento automático de re-renderizações
 */
export const useRenderTracker = (componentName: string, dependencies: any[] = []) => {
  const renderCount = useRef(0);
  const lastRenderTime = useRef(0);
  const prevDeps = useRef(dependencies);

  const trackRender = useCallback(() => {
    renderCount.current++;
    const now = performance.now();
    const timeSinceLastRender = now - lastRenderTime.current;
    lastRenderTime.current = now;

    // Detectar mudanças nas dependências
    const depsChanged = dependencies.some((dep, index) => dep !== prevDeps.current[index]);

    prevDeps.current = dependencies;

    if (process.env.NODE_ENV === 'development') {
      console.log(`🔄 ${componentName} render #${renderCount.current}`, {
        timeSinceLastRender: timeSinceLastRender.toFixed(2) + 'ms',
        depsChanged,
        dependencies: depsChanged ? dependencies : 'unchanged',
      });
    }

    performanceMonitor.recordComponentRender(componentName, timeSinceLastRender, {
      renderNumber: renderCount.current,
      depsChanged,
      dependencies: depsChanged ? dependencies : null,
    });
  }, [componentName, dependencies]);

  return {
    trackRender,
    renderCount: renderCount.current,
    lastRenderTime: lastRenderTime.current,
  };
};
