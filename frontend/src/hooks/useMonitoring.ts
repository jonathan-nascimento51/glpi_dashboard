import { useEffect, useRef, useState } from 'react';
import { StructuredLogger, PerformanceMonitor, HealthCheckMonitor, AlertSystem } from '../utils/monitoring';

// Hook para monitoramento de componentes React
export function useComponentMonitoring(componentName: string) {
  const logger = StructuredLogger.getInstance();
  const mountTimeRef = useRef<string | null>(null);
  const renderCountRef = useRef(0);

  useEffect(() => {
    // Log de montagem do componente
    mountTimeRef.current = PerformanceMonitor.startMeasurement(`${componentName}_mount`);
    logger.info(`Component mounted: ${componentName}`);

    return () => {
      // Log de desmontagem do componente
      if (mountTimeRef.current) {
        PerformanceMonitor.endMeasurement(mountTimeRef.current, `${componentName}_mount`);
      }
      logger.info(`Component unmounted: ${componentName}`);
    };
  }, [componentName, logger]);

  useEffect(() => {
    // Contar renders
    renderCountRef.current++;
    if (renderCountRef.current > 10) {
      logger.warn(`High render count detected for ${componentName}`, {
        renderCount: renderCountRef.current,
      });
    }
  });

  const logError = (error: Error, context?: any) => {
    logger.error(`Error in ${componentName}`, error, context);
  };

  const logPerformance = (operation: string, duration: number, data?: any) => {
    logger.performance(`${componentName}_${operation}`, duration, data);
  };

  return {
    logError,
    logPerformance,
    renderCount: renderCountRef.current,
  };
}

// Hook para monitoramento de API calls
export function useApiMonitoring() {
  const logger = StructuredLogger.getInstance();
  const [apiStats, setApiStats] = useState({
    totalRequests: 0,
    successfulRequests: 0,
    failedRequests: 0,
    averageResponseTime: 0,
  });

  const monitorApiCall = async <T>(
    operation: string,
    apiCall: () => Promise<T>,
    options?: {
      timeout?: number;
      retries?: number;
      onError?: (error: Error) => void;
    }
  ): Promise<T> => {
    const measurementId = PerformanceMonitor.startMeasurement(`api_${operation}`);
    const startTime = Date.now();
    
    try {
      setApiStats(prev => ({ ...prev, totalRequests: prev.totalRequests + 1 }));
      
      let result: T;
      let retries = options?.retries || 0;
      
      while (true) {
        try {
          // Implementar timeout se especificado
          if (options?.timeout) {
            result = await Promise.race([
              apiCall(),
              new Promise<never>((_, reject) => 
                setTimeout(() => reject(new Error('Request timeout')), options.timeout)
              )
            ]);
          } else {
            result = await apiCall();
          }
          break;
        } catch (error) {
          if (retries > 0) {
            retries--;
            logger.warn(`API call failed, retrying: ${operation}`, {
              retriesLeft: retries,
              error: (error as Error).message,
            });
            await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1s before retry
          } else {
            throw error;
          }
        }
      }
      
      const duration = PerformanceMonitor.endMeasurement(measurementId, `api_${operation}`, {
        success: true,
      });
      
      setApiStats(prev => ({
        ...prev,
        successfulRequests: prev.successfulRequests + 1,
        averageResponseTime: (prev.averageResponseTime * (prev.totalRequests - 1) + duration) / prev.totalRequests,
      }));
      
      // Verificar tempo de resposta
      AlertSystem.checkResponseTime(duration, operation);
      
      return result;
    } catch (error) {
      const duration = PerformanceMonitor.endMeasurement(measurementId, `api_${operation}`, {
        success: false,
        error: (error as Error).message,
      });
      
      setApiStats(prev => ({
        ...prev,
        failedRequests: prev.failedRequests + 1,
        averageResponseTime: (prev.averageResponseTime * (prev.totalRequests - 1) + duration) / prev.totalRequests,
      }));
      
      logger.error(`API call failed: ${operation}`, error as Error);
      
      if (options?.onError) {
        options.onError(error as Error);
      }
      
      // Verificar taxa de erro
      AlertSystem.checkErrorRate(apiStats.failedRequests + 1, apiStats.totalRequests);
      
      throw error;
    }
  };

  return {
    monitorApiCall,
    apiStats,
  };
}

// Hook para monitoramento de health status
export function useHealthMonitoring() {
  const [healthStatus, setHealthStatus] = useState(HealthCheckMonitor.getLastHealthStatus());
  const [alerts, setAlerts] = useState<Array<{
    id: string;
    type: string;
    message: string;
    timestamp: string;
    data?: any;
  }>>([]);

  useEffect(() => {
    const handleHealthCheck = (event: CustomEvent) => {
      setHealthStatus(event.detail);
    };

    const handleSystemAlert = (event: CustomEvent) => {
      const alert = {
        id: Math.random().toString(36).substring(2, 15),
        type: event.detail.type,
        message: `System alert: ${event.detail.type}`,
        timestamp: event.detail.timestamp,
        data: event.detail.data,
      };
      
      setAlerts(prev => [alert, ...prev.slice(0, 9)]); // Keep only last 10 alerts
    };

    window.addEventListener('healthcheck', handleHealthCheck as EventListener);
    window.addEventListener('systemAlert', handleSystemAlert as EventListener);

    return () => {
      window.removeEventListener('healthcheck', handleHealthCheck as EventListener);
      window.removeEventListener('systemAlert', handleSystemAlert as EventListener);
    };
  }, []);

  const dismissAlert = (alertId: string) => {
    setAlerts(prev => prev.filter(alert => alert.id !== alertId));
  };

  const clearAllAlerts = () => {
    setAlerts([]);
  };

  return {
    healthStatus,
    alerts,
    dismissAlert,
    clearAllAlerts,
  };
}

// Hook para monitoramento de performance de renderização
export function useRenderPerformance(componentName: string, dependencies: any[] = []) {
  const renderTimeRef = useRef<number>(0);
  const renderCountRef = useRef<number>(0);
  const logger = StructuredLogger.getInstance();

  useEffect(() => {
    const startTime = performance.now();
    renderTimeRef.current = startTime;
    renderCountRef.current++;

    return () => {
      const endTime = performance.now();
      const renderDuration = endTime - renderTimeRef.current;
      
      logger.performance(`${componentName}_render`, renderDuration, {
        renderCount: renderCountRef.current,
        dependencies: dependencies.length,
      });

      // Alertar sobre renders lentos
      if (renderDuration > 100) { // 100ms
        logger.warn(`Slow render detected in ${componentName}`, {
          renderDuration,
          renderCount: renderCountRef.current,
        });
      }

      // Alertar sobre muitos re-renders
      if (renderCountRef.current > 20) {
        logger.warn(`High render count in ${componentName}`, {
          renderCount: renderCountRef.current,
        });
      }
    };
  }, dependencies);

  return {
    renderCount: renderCountRef.current,
    lastRenderTime: renderTimeRef.current,
  };
}

// Hook para monitoramento de erros com Error Boundary
export function useErrorBoundary() {
  const [error, setError] = useState<Error | null>(null);
  const logger = StructuredLogger.getInstance();

  const resetError = () => {
    setError(null);
  };

  const captureError = (error: Error, errorInfo?: any) => {
    setError(error);
    logger.error('Error boundary caught error', error, errorInfo);
  };

  useEffect(() => {
    if (error) {
      // Enviar erro para sistema de monitoramento
      if (window.Sentry) {
        window.Sentry.captureException(error);
      }
    }
  }, [error]);

  return {
    error,
    resetError,
    captureError,
  };
}

export {
  useComponentMonitoring,
  useApiMonitoring,
  useHealthMonitoring,
  useRenderPerformance,
  useErrorBoundary,
};
