import { alertService } from '../services/alertService';
import { performanceMonitor } from './performanceMonitor';
import { cacheManager } from './cacheStrategies';

/**
 * Integração entre o sistema de alertas e o monitoramento de performance
 */
export class AlertIntegration {
  private static instance: AlertIntegration;
  private isInitialized = false;
  private performanceCheckInterval?: NodeJS.Timeout;
  private cacheCheckInterval?: NodeJS.Timeout;

  static getInstance(): AlertIntegration {
    if (!AlertIntegration.instance) {
      AlertIntegration.instance = new AlertIntegration();
    }
    return AlertIntegration.instance;
  }

  /**
   * Inicializa a integração entre alertas e monitoramento
   */
  initialize(): void {
    if (this.isInitialized) {
      return;
    }

    // Iniciar monitoramento de alertas
    alertService.start();

    // Configurar verificações periódicas de performance
    this.setupPerformanceMonitoring();
    this.setupCacheMonitoring();
    this.setupErrorMonitoring();

    this.isInitialized = true;
    // Alert Integration inicializado
  }

  /**
   * Para a integração e limpa recursos
   */
  destroy(): void {
    if (!this.isInitialized) {
      return;
    }

    alertService.stop();
    
    if (this.performanceCheckInterval) {
      clearInterval(this.performanceCheckInterval);
    }
    
    if (this.cacheCheckInterval) {
      clearInterval(this.cacheCheckInterval);
    }

    this.isInitialized = false;
    // Alert Integration destruído
  }

  /**
   * Configura monitoramento de performance
   */
  private setupPerformanceMonitoring(): void {
    this.performanceCheckInterval = setInterval(() => {
      try {
        const metrics = performanceMonitor.getMetrics();
        
        // Verificar tempo de resposta
        if (metrics.responseTime) {
          if (metrics.responseTime > 5000) {
            alertService.createAlert(
              `Tempo de resposta crítico: ${metrics.responseTime}ms`,
              'critical',
              'performance',
              {
                responseTime: metrics.responseTime,
                threshold: 5000,
                source: 'performance_monitor'
              }
            );
          } else if (metrics.responseTime > 2000) {
            alertService.createAlert(
              `Tempo de resposta elevado: ${metrics.responseTime}ms`,
              'warning',
              'performance',
              {
                responseTime: metrics.responseTime,
                threshold: 2000,
                source: 'performance_monitor'
              }
            );
          }
        }

        // Verificar taxa de erro
        if (metrics.errorRate !== undefined) {
          if (metrics.errorRate > 10) {
            alertService.createAlert(
              `Taxa de erro crítica: ${metrics.errorRate.toFixed(1)}%`,
              'critical',
              'error',
              {
                errorRate: metrics.errorRate,
                threshold: 10,
                source: 'performance_monitor'
              }
            );
          } else if (metrics.errorRate > 5) {
            alertService.createAlert(
              `Taxa de erro elevada: ${metrics.errorRate.toFixed(1)}%`,
              'warning',
              'error',
              {
                errorRate: metrics.errorRate,
                threshold: 5,
                source: 'performance_monitor'
              }
            );
          }
        }

        // Verificar uso de memória
        if (metrics.memoryUsage !== undefined) {
          if (metrics.memoryUsage > 90) {
            alertService.createAlert(
              `Uso de memória crítico: ${metrics.memoryUsage.toFixed(1)}%`,
              'critical',
              'system',
              {
                memoryUsage: metrics.memoryUsage,
                threshold: 90,
                source: 'performance_monitor'
              }
            );
          } else if (metrics.memoryUsage > 70) {
            alertService.createAlert(
              `Uso de memória alto: ${metrics.memoryUsage.toFixed(1)}%`,
              'warning',
              'system',
              {
                memoryUsage: metrics.memoryUsage,
                threshold: 70,
                source: 'performance_monitor'
              }
            );
          }
        }
      } catch (error) {
        // Erro no monitoramento de performance
      }
    }, 30000); // Verificar a cada 30 segundos
  }

  /**
   * Configura monitoramento de cache
   */
  private setupCacheMonitoring(): void {
    this.cacheCheckInterval = setInterval(() => {
      try {
        const analytics = cacheManager.getAnalytics();
        const report = analytics.generateReport();
        const allStats = cacheManager.getAllStats();
        
        // Verificar se há atividade no cache antes de avaliar performance
        let totalRequests = 0;
        let hasActiveCache = false;
        
        for (const [cacheType, stats] of Object.entries(allStats)) {
          if (stats && typeof stats.hits === 'number' && typeof stats.misses === 'number') {
            totalRequests += stats.hits + stats.misses;
            if (stats.hits + stats.misses > 0) {
              hasActiveCache = true;
            }
          }
        }
        
        // Só avaliar performance se houver atividade suficiente no cache
        if (!hasActiveCache || totalRequests < 10) {
          // Cache ainda não tem dados suficientes para avaliação
          return;
        }

        // Verificar taxa de hit geral apenas se há dados suficientes
        if (report.overallHitRate < 30) {
          alertService.createAlert(
            `Taxa de hit do cache crítica: ${report.overallHitRate.toFixed(1)}%, ultrapassando o limite de 30%`,
            'critical',
            'cache',
            {
              hitRate: report.overallHitRate,
              threshold: 30,
              totalRequests,
              source: 'cache_monitor'
            }
          );
        } else if (report.overallHitRate < 60) {
          alertService.createAlert(
            `Taxa de hit do cache baixa: ${report.overallHitRate.toFixed(1)}%, abaixo do ideal de 60%`,
            'warning',
            'cache',
            {
              hitRate: report.overallHitRate,
              threshold: 60,
              totalRequests,
              source: 'cache_monitor'
            }
          );
        }

        // Verificar caches individuais com problemas
        Object.entries(report.cacheDetails).forEach(([cacheName, details]) => {
          if (details.hitRate < 20) {
            alertService.createAlert(
              `Cache ${cacheName} com taxa de hit crítica: ${details.hitRate.toFixed(1)}%`,
              'critical',
              'cache',
              {
                cacheName,
                hitRate: details.hitRate,
                threshold: 20,
                source: 'cache_monitor'
              }
            );
          }
        });

        // Verificar tendências de degradação
        if (report.trends.degradingCaches.length > 0) {
          alertService.createAlert(
            `Degradação detectada em ${report.trends.degradingCaches.length} cache(s)`,
            'warning',
            'cache',
            {
              degradingCaches: report.trends.degradingCaches,
              source: 'cache_monitor'
            }
          );
        }
      } catch (error) {
        // Erro no monitoramento de cache
      }
    }, 60000); // Verificar a cada 60 segundos
  }

  /**
   * Configurar monitoramento de erros
   */
  private setupErrorMonitoring(): void {
    // Interceptar erros globais
    const originalConsoleError = console.error;
    let isProcessingError = false; // Proteção contra loops infinitos
    
    console.error = (...args: any[]) => {
      // Chamar console.error original
      originalConsoleError.apply(console, args);
      
      // Evitar loops infinitos
      if (isProcessingError) return;
      
      try {
        isProcessingError = true;
        
        // Criar alerta para erros críticos
        const errorMessage = args.join(' ');
        if (this.shouldCreateErrorAlert(errorMessage)) {
          alertService.createAlert(
            `Erro detectado: ${errorMessage.substring(0, 100)}...`,
            'warning',
            'error',
            {
              fullError: errorMessage,
              timestamp: new Date().toISOString(),
              source: 'error_monitor'
            }
          );
        }
      } catch (error) {
        // Silenciosamente ignorar erros no sistema de alertas para evitar loops
      } finally {
        isProcessingError = false;
      }
    };

    // Interceptar erros não capturados
    window.addEventListener('error', (event) => {
      alertService.createAlert(
        `Erro não capturado: ${event.message}`,
        'critical',
        'error',
        {
          filename: event.filename,
          lineno: event.lineno,
          colno: event.colno,
          error: event.error?.toString(),
          source: 'error_monitor'
        }
      );
    });

    // Interceptar promises rejeitadas
    window.addEventListener('unhandledrejection', (event) => {
      alertService.createAlert(
        `Promise rejeitada: ${event.reason}`,
        'critical',
        'error',
        {
          reason: event.reason?.toString(),
          source: 'error_monitor'
        }
      );
    });
  }

  /**
   * Determina se um erro deve gerar um alerta
   */
  private shouldCreateErrorAlert(errorMessage: string): boolean {
    // Filtrar erros conhecidos ou menos críticos
    const ignoredPatterns = [
      'ResizeObserver loop limit exceeded',
      'Non-Error promise rejection captured',
      'Script error',
      'Network request failed', // Pode ser temporário
      'Maximum update depth exceeded', // Erro de React que estamos corrigindo
      'Warning: Maximum update depth exceeded',
      'useEffect either doesn\'t have a dependency array',
      'dependencies changes on every render',
      'Objects are not valid as React child',
      'React Hook useEffect has missing dependencies',
      'React Hook useCallback has missing dependencies',
      'React Hook useMemo has missing dependencies'
    ];

    return !ignoredPatterns.some(pattern => 
      errorMessage.toLowerCase().includes(pattern.toLowerCase())
    );
  }

  /**
   * Cria alertas manuais para eventos específicos
   */
  createCustomAlert(
    message: string,
    severity: 'info' | 'warning' | 'critical',
    category: 'performance' | 'cache' | 'system' | 'error',
    metadata?: Record<string, any>
  ): void {
    alertService.createAlert(message, severity, category, {
      ...metadata,
      source: 'custom',
      manual: true
    });
  }

  /**
   * Obtém estatísticas de integração
   */
  getIntegrationStats() {
    return {
      isInitialized: this.isInitialized,
      alertServiceActive: alertService.isMonitoring(),
      performanceMonitoringActive: !!this.performanceCheckInterval,
      cacheMonitoringActive: !!this.cacheCheckInterval,
      totalAlerts: alertService.getAlerts().length,
      criticalAlerts: alertService.getAlerts().filter(a => a.severity === 'critical' && !a.resolved).length
    };
  }
}

// Instância singleton
export const alertIntegration = AlertIntegration.getInstance();

// Auto-inicializar em desenvolvimento
if (process.env.NODE_ENV === 'development') {
  // Aguardar um pouco para garantir que outros serviços estejam prontos
  setTimeout(() => {
    alertIntegration.initialize();
  }, 2000);
}

// Limpar recursos ao sair
if (typeof window !== 'undefined') {
  window.addEventListener('beforeunload', () => {
    alertIntegration.destroy();
  });
}