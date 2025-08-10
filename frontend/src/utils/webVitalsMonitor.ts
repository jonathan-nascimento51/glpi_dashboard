/**
 * Sistema de Monitoramento Contínuo com Web Vitals
 * Implementa coleta automática de métricas e alertas
 */

import { getCLS, getFID, getFCP, getLCP, getTTFB, onINP } from 'web-vitals';

export interface WebVitalsMetric {
  name: 'CLS' | 'FID' | 'FCP' | 'LCP' | 'TTFB' | 'INP';
  value: number;
  rating: 'good' | 'needs-improvement' | 'poor';
  timestamp: number;
  id: string;
  navigationType?: string;
}

export interface WebVitalsAlert {
  metric: string;
  value: number;
  threshold: number;
  timestamp: number;
  severity: 'warning' | 'critical';
  message: string;
}

export interface WebVitalsConfig {
  enableAlerts: boolean;
  alertThresholds: {
    FID: number; // 200ms
    INP: number; // 200ms
    LCP: number; // 2500ms
    CLS: number; // 0.1
    TTFB: number; // 800ms
  };
  sendToBackend: boolean;
  backendEndpoint?: string;
  enableConsoleLogging: boolean;
}

class WebVitalsMonitor {
  private metrics: WebVitalsMetric[] = [];
  private alerts: WebVitalsAlert[] = [];
  private config: WebVitalsConfig = {
    enableAlerts: true,
    alertThresholds: {
      FID: 200, // 200ms conforme solicitado
      INP: 200, // 200ms conforme solicitado
      LCP: 2500,
      CLS: 0.1,
      TTFB: 800
    },
    sendToBackend: process.env.NODE_ENV === 'production',
    backendEndpoint: '/api/performance/web-vitals',
    enableConsoleLogging: process.env.NODE_ENV === 'development'
  };

  private alertCallbacks: ((alert: WebVitalsAlert) => void)[] = [];
  private metricCallbacks: ((metric: WebVitalsMetric) => void)[] = [];

  constructor() {
    this.initializeWebVitals();
  }

  /**
   * Inicializa coleta de Web Vitals
   */
  private initializeWebVitals(): void {
    // Core Web Vitals
    getCLS(this.handleMetric.bind(this));
    getFID(this.handleMetric.bind(this));
    getLCP(this.handleMetric.bind(this));
    
    // Outras métricas importantes
    getFCP(this.handleMetric.bind(this));
    getTTFB(this.handleMetric.bind(this));
    
    // INP (Interaction to Next Paint) - substituto do FID
    onINP(this.handleMetric.bind(this));

    if (this.config.enableConsoleLogging) {
      console.log('🔍 Web Vitals Monitor inicializado');
    }
  }

  /**
   * Processa uma métrica recebida
   */
  private handleMetric(metric: unknown): void {
    const webVitalMetric: WebVitalsMetric = {
      name: metric.name as WebVitalsMetric['name'],
      value: metric.value,
      rating: metric.rating,
      timestamp: Date.now(),
      id: metric.id,
      navigationType: metric.navigationType
    };

    this.metrics.push(webVitalMetric);
    
    // Manter apenas as últimas 100 métricas
    if (this.metrics.length > 100) {
      this.metrics = this.metrics.slice(-100);
    }

    // Verificar se precisa gerar alerta
    this.checkForAlert(webVitalMetric);

    // Enviar para backend se configurado
    if (this.config.sendToBackend) {
      this.sendToBackend(webVitalMetric);
    }

    // Log em desenvolvimento
    if (this.config.enableConsoleLogging) {
      this.logMetric(webVitalMetric);
    }

    // Notificar callbacks
    this.metricCallbacks.forEach(callback => callback(webVitalMetric));
  }

  /**
   * Verifica se uma métrica deve gerar alerta
   */
  private checkForAlert(metric: WebVitalsMetric): void {
    if (!this.config.enableAlerts) return;

    const threshold = this.config.alertThresholds[metric.name];
    if (!threshold) return;

    let shouldAlert = false;
    let severity: 'warning' | 'critical' = 'warning';

    switch (metric.name) {
      case 'FID':
      case 'INP':
        shouldAlert = metric.value > threshold;
        severity = metric.value > threshold * 1.5 ? 'critical' : 'warning';
        break;
      case 'LCP':
        shouldAlert = metric.value > threshold;
        severity = metric.value > threshold * 1.2 ? 'critical' : 'warning';
        break;
      case 'CLS':
        shouldAlert = metric.value > threshold;
        severity = metric.value > threshold * 2 ? 'critical' : 'warning';
        break;
      case 'TTFB':
        shouldAlert = metric.value > threshold;
        severity = metric.value > threshold * 1.5 ? 'critical' : 'warning';
        break;
    }

    if (shouldAlert) {
      const alert: WebVitalsAlert = {
        metric: metric.name,
        value: metric.value,
        threshold,
        timestamp: metric.timestamp,
        severity,
        message: this.generateAlertMessage(metric, threshold, severity)
      };

      this.alerts.push(alert);
      
      // Manter apenas os últimos 50 alertas
      if (this.alerts.length > 50) {
        this.alerts = this.alerts.slice(-50);
      }

      // Notificar callbacks
      this.alertCallbacks.forEach(callback => callback(alert));

      // Log do alerta
      console.warn(`🚨 Web Vitals Alert [${severity.toUpperCase()}]:`, alert.message);
    }
  }

  /**
   * Gera mensagem de alerta
   */
  private generateAlertMessage(
    metric: WebVitalsMetric,
    threshold: number,
    severity: 'warning' | 'critical'
  ): string {
    const unit = metric.name === 'CLS' ? '' : 'ms';
    const exceedPercentage = ((metric.value - threshold) / threshold * 100).toFixed(1);
    
    return `${metric.name} de ${metric.value}${unit} excede o limite de ${threshold}${unit} em ${exceedPercentage}% (${severity})`;
  }

  /**
   * Envia métrica para backend
   */
  private async sendToBackend(metric: WebVitalsMetric): Promise<void> {
    if (!this.config.backendEndpoint) return;

    try {
      await fetch(this.config.backendEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          metric,
          userAgent: navigator.userAgent,
          url: window.location.href,
          timestamp: Date.now()
        })
      });
    } catch (error) {
      console.error('Erro ao enviar métrica para backend:', error);
    }
  }

  /**
   * Log formatado da métrica
   */
  private logMetric(metric: WebVitalsMetric): void {
    const unit = metric.name === 'CLS' ? '' : 'ms';
    const emoji = this.getMetricEmoji(metric.rating);
    
    console.log(
      `${emoji} ${metric.name}: ${metric.value}${unit} (${metric.rating})`,
      {
        id: metric.id,
        navigationType: metric.navigationType,
        timestamp: new Date(metric.timestamp).toISOString()
      }
    );
  }

  /**
   * Obtém emoji baseado no rating
   */
  private getMetricEmoji(rating: string): string {
    switch (rating) {
      case 'good': return '✅';
      case 'needs-improvement': return '⚠️';
      case 'poor': return '❌';
      default: return '📊';
    }
  }

  /**
   * Registra callback para alertas
   */
  onAlert(callback: (alert: WebVitalsAlert) => void): () => void {
    this.alertCallbacks.push(callback);
    
    // Retorna função para remover o callback
    return () => {
      const index = this.alertCallbacks.indexOf(callback);
      if (index > -1) {
        this.alertCallbacks.splice(index, 1);
      }
    };
  }

  /**
   * Registra callback para métricas
   */
  onMetric(callback: (metric: WebVitalsMetric) => void): () => void {
    this.metricCallbacks.push(callback);
    
    // Retorna função para remover o callback
    return () => {
      const index = this.metricCallbacks.indexOf(callback);
      if (index > -1) {
        this.metricCallbacks.splice(index, 1);
      }
    };
  }

  /**
   * Obtém todas as métricas coletadas
   */
  getMetrics(): WebVitalsMetric[] {
    return [...this.metrics];
  }

  /**
   * Obtém todos os alertas gerados
   */
  getAlerts(): WebVitalsAlert[] {
    return [...this.alerts];
  }

  /**
   * Obtém métricas resumidas
   */
  getSummary(): {
    totalMetrics: number;
    totalAlerts: number;
    criticalAlerts: number;
    averageValues: Record<string, number>;
    latestMetrics: Record<string, WebVitalsMetric | undefined>;
  } {
    const averageValues: Record<string, number> = {};
    const latestMetrics: Record<string, WebVitalsMetric | undefined> = {};
    
    // Calcular médias por tipo de métrica
    const metricTypes = ['CLS', 'FID', 'FCP', 'LCP', 'TTFB', 'INP'];
    
    metricTypes.forEach(type => {
      const metricsOfType = this.metrics.filter(m => m.name === type);
      if (metricsOfType.length > 0) {
        averageValues[type] = metricsOfType.reduce((sum, m) => sum + m.value, 0) / metricsOfType.length;
        latestMetrics[type] = metricsOfType[metricsOfType.length - 1];
      }
    });

    return {
      totalMetrics: this.metrics.length,
      totalAlerts: this.alerts.length,
      criticalAlerts: this.alerts.filter(a => a.severity === 'critical').length,
      averageValues,
      latestMetrics
    };
  }

  /**
   * Atualiza configuração
   */
  updateConfig(newConfig: Partial<WebVitalsConfig>): void {
    this.config = { ...this.config, ...newConfig };
    
    if (this.config.enableConsoleLogging) {
      console.log('🔧 Web Vitals Monitor configuração atualizada:', this.config);
    }
  }

  /**
   * Limpa métricas e alertas
   */
  clear(): void {
    this.metrics = [];
    this.alerts = [];
    
    if (this.config.enableConsoleLogging) {
      console.log('🧹 Web Vitals Monitor limpo');
    }
  }

  /**
   * Força coleta de métricas atuais
   */
  forceCollection(): void {
    // Re-inicializar coleta para capturar métricas atuais
    this.initializeWebVitals();
  }

  /**
   * Exporta dados para análise
   */
  exportData(): {
    metrics: WebVitalsMetric[];
    alerts: WebVitalsAlert[];
    summary: ReturnType<typeof this.getSummary>;
    config: WebVitalsConfig;
    exportTimestamp: number;
  } {
    return {
      metrics: this.getMetrics(),
      alerts: this.getAlerts(),
      summary: this.getSummary(),
      config: this.config,
      exportTimestamp: Date.now()
    };
  }
}

// Instância singleton
export const webVitalsMonitor = new WebVitalsMonitor();

// Hook React para usar Web Vitals
export const useWebVitals = () => {
  const [metrics, setMetrics] = React.useState<WebVitalsMetric[]>([]);
  const [alerts, setAlerts] = React.useState<WebVitalsAlert[]>([]);
  const [summary, setSummary] = React.useState(webVitalsMonitor.getSummary());

  React.useEffect(() => {
    // Atualizar estado quando novas métricas chegarem
    const unsubscribeMetric = webVitalsMonitor.onMetric(() => {
      setMetrics(webVitalsMonitor.getMetrics());
      setSummary(webVitalsMonitor.getSummary());
    });

    // Atualizar estado quando novos alertas chegarem
    const unsubscribeAlert = webVitalsMonitor.onAlert(() => {
      setAlerts(webVitalsMonitor.getAlerts());
    });

    // Estado inicial
    setMetrics(webVitalsMonitor.getMetrics());
    setAlerts(webVitalsMonitor.getAlerts());

    return () => {
      unsubscribeMetric();
      unsubscribeAlert();
    };
  }, []);

  return {
    metrics,
    alerts,
    summary,
    clearData: () => webVitalsMonitor.clear(),
    exportData: () => webVitalsMonitor.exportData(),
    updateConfig: (config: Partial<WebVitalsConfig>) => webVitalsMonitor.updateConfig(config)
  };
};

// Utilitários para debugging
export const debugWebVitals = {
  getMetrics: () => webVitalsMonitor.getMetrics(),
  getAlerts: () => webVitalsMonitor.getAlerts(),
  getSummary: () => webVitalsMonitor.getSummary(),
  clear: () => webVitalsMonitor.clear(),
  exportData: () => webVitalsMonitor.exportData(),
  forceCollection: () => webVitalsMonitor.forceCollection()
};

// Expor no window para debugging em desenvolvimento
if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
  (window as any).debugWebVitals = debugWebVitals;
  (window as any).webVitalsMonitor = webVitalsMonitor;
}

// Importar React para o hook
import React from 'react';
