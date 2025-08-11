import { ApiValidationMiddleware } from '../utils/validation-middleware';

// Sistema de logging estruturado
export class StructuredLogger {
  private static instance: StructuredLogger;
  private correlationId: string;
  private sessionId: string;

  private constructor() {
    this.correlationId = this.generateId();
    this.sessionId = this.generateId();
  }

  static getInstance(): StructuredLogger {
    if (!StructuredLogger.instance) {
      StructuredLogger.instance = new StructuredLogger();
    }
    return StructuredLogger.instance;
  }

  private generateId(): string {
    return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
  }

  private createLogEntry(level: string, message: string, data?: any) {
    return {
      timestamp: new Date().toISOString(),
      level,
      message,
      correlationId: this.correlationId,
      sessionId: this.sessionId,
      url: window.location.href,
      userAgent: navigator.userAgent,
      data,
    };
  }

  info(message: string, data?: any) {
    const logEntry = this.createLogEntry('INFO', message, data);
    console.log(' INFO:', logEntry);
    this.sendToMonitoring(logEntry);
  }

  warn(message: string, data?: any) {
    const logEntry = this.createLogEntry('WARN', message, data);
    console.warn(' WARN:', logEntry);
    this.sendToMonitoring(logEntry);
  }

  error(message: string, error?: Error, data?: any) {
    const logEntry = this.createLogEntry('ERROR', message, {
      error: error ? {
        name: error.name,
        message: error.message,
        stack: error.stack,
      } : undefined,
      ...data,
    });
    console.error(' ERROR:', logEntry);
    this.sendToMonitoring(logEntry);
  }

  performance(operation: string, duration: number, data?: any) {
    const logEntry = this.createLogEntry('PERFORMANCE', `${operation} completed`, {
      operation,
      duration,
      ...data,
    });
    console.log(' PERFORMANCE:', logEntry);
    this.sendToMonitoring(logEntry);
  }

  private sendToMonitoring(logEntry: any) {
    // Enviar para sistema de monitoramento externo
    if (window.Sentry) {
      window.Sentry.addBreadcrumb({
        message: logEntry.message,
        level: logEntry.level.toLowerCase() as any,
        data: logEntry.data,
        timestamp: Date.now() / 1000,
      });
    }

    // Enviar para endpoint de logs (se configurado)
    if (process.env.VITE_LOGGING_ENDPOINT) {
      fetch(process.env.VITE_LOGGING_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(logEntry),
      }).catch(err => {
        console.warn('Failed to send log to monitoring endpoint:', err);
      });
    }
  }

  newCorrelationId(): string {
    this.correlationId = this.generateId();
    return this.correlationId;
  }
}

// Sistema de métricas de performance
export class PerformanceMonitor {
  private static measurements: Map<string, number> = new Map();
  private static logger = StructuredLogger.getInstance();

  static startMeasurement(operation: string): string {
    const measurementId = `${operation}_${Date.now()}`;
    this.measurements.set(measurementId, performance.now());
    return measurementId;
  }

  static endMeasurement(measurementId: string, operation: string, data?: any): number {
    const startTime = this.measurements.get(measurementId);
    if (!startTime) {
      this.logger.warn(`Measurement not found: ${measurementId}`);
      return 0;
    }

    const duration = performance.now() - startTime;
    this.measurements.delete(measurementId);

    this.logger.performance(operation, duration, data);

    // Alertar se a operação demorou muito
    if (duration > 5000) { // 5 segundos
      this.logger.warn(`Slow operation detected: ${operation}`, {
        duration,
        threshold: 5000,
        ...data,
      });
    }

    return duration;
  }

  static measureAsync<T>(operation: string, fn: () => Promise<T>, data?: any): Promise<T> {
    const measurementId = this.startMeasurement(operation);
    return fn()
      .then(result => {
        this.endMeasurement(measurementId, operation, { success: true, ...data });
        return result;
      })
      .catch(error => {
        this.endMeasurement(measurementId, operation, { success: false, error: error.message, ...data });
        throw error;
      });
  }

  static measureSync<T>(operation: string, fn: () => T, data?: any): T {
    const measurementId = this.startMeasurement(operation);
    try {
      const result = fn();
      this.endMeasurement(measurementId, operation, { success: true, ...data });
      return result;
    } catch (error) {
      this.endMeasurement(measurementId, operation, { success: false, error: (error as Error).message, ...data });
      throw error;
    }
  }
}

// Sistema de Health Checks
export class HealthCheckMonitor {
  private static logger = StructuredLogger.getInstance();
  private static checkInterval: number | null = null;
  private static lastHealthStatus: HealthStatus = {
    api: 'unknown',
    frontend: 'healthy',
    timestamp: new Date().toISOString(),
  };

  static startMonitoring(intervalMs: number = 30000) {
    if (this.checkInterval) {
      clearInterval(this.checkInterval);
    }

    this.checkInterval = window.setInterval(() => {
      this.performHealthCheck();
    }, intervalMs);

    // Executar check inicial
    this.performHealthCheck();
  }

  static stopMonitoring() {
    if (this.checkInterval) {
      clearInterval(this.checkInterval);
      this.checkInterval = null;
    }
  }

  private static async performHealthCheck() {
    const startTime = performance.now();
    
    try {
      // Check API health
      const apiHealth = await this.checkApiHealth();
      
      // Check frontend health
      const frontendHealth = this.checkFrontendHealth();
      
      const healthStatus: HealthStatus = {
        api: apiHealth,
        frontend: frontendHealth,
        timestamp: new Date().toISOString(),
        responseTime: performance.now() - startTime,
      };

      // Log mudanças de status
      if (healthStatus.api !== this.lastHealthStatus.api) {
        this.logger.info(`API health status changed: ${this.lastHealthStatus.api} -> ${healthStatus.api}`);
      }

      this.lastHealthStatus = healthStatus;

      // Disparar eventos customizados
      window.dispatchEvent(new CustomEvent('healthcheck', {
        detail: healthStatus,
      }));

    } catch (error) {
      this.logger.error('Health check failed', error as Error);
    }
  }

  private static async checkApiHealth(): Promise<'healthy' | 'degraded' | 'unhealthy'> {
    try {
      const response = await fetch('/api/health', {
        method: 'GET',
        timeout: 5000,
      } as any);

      if (response.ok) {
        const data = await response.json();
        return data.status === 'healthy' ? 'healthy' : 'degraded';
      } else {
        return 'degraded';
      }
    } catch (error) {
      return 'unhealthy';
    }
  }

  private static checkFrontendHealth(): 'healthy' | 'degraded' | 'unhealthy' {
    try {
      // Verificar se há erros JavaScript não tratados
      const errorCount = (window as any).__errorCount || 0;
      
      // Verificar performance da página
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      const loadTime = navigation.loadEventEnd - navigation.loadEventStart;
      
      if (errorCount > 5) {
        return 'unhealthy';
      } else if (errorCount > 2 || loadTime > 10000) {
        return 'degraded';
      } else {
        return 'healthy';
      }
    } catch (error) {
      return 'degraded';
    }
  }

  static getLastHealthStatus(): HealthStatus {
    return this.lastHealthStatus;
  }
}

// Tipos para health check
interface HealthStatus {
  api: 'healthy' | 'degraded' | 'unhealthy' | 'unknown';
  frontend: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  responseTime?: number;
}

// Sistema de alertas automáticos
export class AlertSystem {
  private static logger = StructuredLogger.getInstance();
  private static alertThresholds = {
    errorRate: 0.1, // 10% de erro
    responseTime: 5000, // 5 segundos
    memoryUsage: 0.8, // 80% da memória
  };

  static checkErrorRate(errors: number, total: number) {
    const errorRate = errors / total;
    if (errorRate > this.alertThresholds.errorRate) {
      this.logger.error(`High error rate detected: ${(errorRate * 100).toFixed(2)}%`, undefined, {
        errors,
        total,
        threshold: this.alertThresholds.errorRate,
      });
      
      this.sendAlert('HIGH_ERROR_RATE', {
        errorRate,
        errors,
        total,
      });
    }
  }

  static checkResponseTime(responseTime: number, operation: string) {
    if (responseTime > this.alertThresholds.responseTime) {
      this.logger.warn(`Slow response time detected for ${operation}: ${responseTime}ms`, {
        responseTime,
        operation,
        threshold: this.alertThresholds.responseTime,
      });
      
      this.sendAlert('SLOW_RESPONSE', {
        responseTime,
        operation,
      });
    }
  }

  static checkMemoryUsage() {
    if ('memory' in performance) {
      const memory = (performance as any).memory;
      const usageRatio = memory.usedJSHeapSize / memory.jsHeapSizeLimit;
      
      if (usageRatio > this.alertThresholds.memoryUsage) {
        this.logger.warn(`High memory usage detected: ${(usageRatio * 100).toFixed(2)}%`, {
          usedMemory: memory.usedJSHeapSize,
          totalMemory: memory.jsHeapSizeLimit,
          threshold: this.alertThresholds.memoryUsage,
        });
        
        this.sendAlert('HIGH_MEMORY_USAGE', {
          usageRatio,
          usedMemory: memory.usedJSHeapSize,
          totalMemory: memory.jsHeapSizeLimit,
        });
      }
    }
  }

  private static sendAlert(type: string, data: any) {
    // Enviar alerta para sistema de monitoramento
    if (window.Sentry) {
      window.Sentry.captureMessage(`Alert: ${type}`, 'warning');
    }

    // Disparar evento customizado
    window.dispatchEvent(new CustomEvent('systemAlert', {
      detail: {
        type,
        data,
        timestamp: new Date().toISOString(),
      },
    }));
  }
}

// Inicializar sistemas de monitoramento
if (typeof window !== 'undefined') {
  // Inicializar health check monitoring
  HealthCheckMonitor.startMonitoring();
  
  // Monitorar erros JavaScript não tratados
  let errorCount = 0;
  window.addEventListener('error', (event) => {
    errorCount++;
    (window as any).__errorCount = errorCount;
    
    StructuredLogger.getInstance().error('Unhandled JavaScript error', new Error(event.message), {
      filename: event.filename,
      lineno: event.lineno,
      colno: event.colno,
    });
  });
  
  // Monitorar promises rejeitadas
  window.addEventListener('unhandledrejection', (event) => {
    StructuredLogger.getInstance().error('Unhandled promise rejection', event.reason);
  });
  
  // Monitorar uso de memória periodicamente
  setInterval(() => {
    AlertSystem.checkMemoryUsage();
  }, 60000); // A cada minuto
}

export { StructuredLogger, PerformanceMonitor, HealthCheckMonitor, AlertSystem };
