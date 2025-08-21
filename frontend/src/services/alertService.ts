/**
 * Serviço de alertas para monitoramento de performance
 * 
 * Este serviço monitora métricas críticas do sistema e dispara alertas
 * quando detecta degradação de performance ou problemas operacionais.
 */

import { cacheManager, CacheAnalytics } from '../utils/cacheStrategies';
import { metricsCache, systemStatusCache } from './cache';

export interface Alert {
  id: string;
  type: 'warning' | 'error' | 'critical' | 'info';
  category: 'performance' | 'cache' | 'api' | 'system';
  title: string;
  message: string;
  timestamp: Date;
  resolved: boolean;
  metadata?: Record<string, any>;
}

export interface AlertThreshold {
  metric: string;
  warningValue: number;
  errorValue: number;
  criticalValue: number;
  operator: 'gt' | 'lt' | 'eq';
  enabled: boolean;
}

export interface AlertConfig {
  thresholds: AlertThreshold[];
  checkInterval: number;
  maxAlerts: number;
  enableNotifications: boolean;
  enableSound: boolean;
  enableBrowserNotifications: boolean;
}

const DEFAULT_CONFIG: AlertConfig = {
  thresholds: [
    {
      metric: 'responseTime',
      warningValue: 2000,
      errorValue: 5000,
      criticalValue: 10000,
      operator: 'gt',
      enabled: true
    },
    {
      metric: 'cacheHitRate',
      warningValue: 0.6,
      errorValue: 0.4,
      criticalValue: 0.2,
      operator: 'lt',
      enabled: true
    },
    {
      metric: 'errorRate',
      warningValue: 0.05,
      errorValue: 0.1,
      criticalValue: 0.2,
      operator: 'gt',
      enabled: true
    },
    {
      metric: 'memoryUsage',
      warningValue: 0.8,
      errorValue: 0.9,
      criticalValue: 0.95,
      operator: 'gt',
      enabled: true
    }
  ],
  checkInterval: 30000, // 30 segundos
  maxAlerts: 100,
  enableNotifications: true,
  enableSound: false,
  enableBrowserNotifications: false
};

type AlertListener = (alert: Alert) => void;

class AlertService {
  private alerts: Alert[] = [];
  private config: AlertConfig = DEFAULT_CONFIG;
  private listeners: AlertListener[] = [];
  private checkInterval: NodeJS.Timeout | null = null;
  private isRunning = false;
  private lastMetrics: Record<string, any> = {};

  constructor() {
    this.loadConfig();
    this.requestNotificationPermission();
  }

  /**
   * Iniciar o monitoramento de alertas
   */
  start(): void {
    if (this.isRunning) return;
    
    this.isRunning = true;
    this.checkInterval = setInterval(() => {
      this.checkAlerts();
    }, this.config.checkInterval);
    
    // Sistema de alertas iniciado
  }

  /**
   * Parar o monitoramento de alertas
   */
  stop(): void {
    if (!this.isRunning) return;
    
    this.isRunning = false;
    if (this.checkInterval) {
      clearInterval(this.checkInterval);
      this.checkInterval = null;
    }
    
    // Sistema de alertas parado
  }

  /**
   * Adicionar listener para novos alertas
   */
  addListener(listener: AlertListener): void {
    this.listeners.push(listener);
  }

  /**
   * Remover listener
   */
  removeListener(listener: AlertListener): void {
    const index = this.listeners.indexOf(listener);
    if (index > -1) {
      this.listeners.splice(index, 1);
    }
  }

  /**
   * Obter todos os alertas
   */
  getAlerts(): Alert[] {
    return [...this.alerts];
  }

  /**
   * Obter alertas não resolvidos
   */
  getActiveAlerts(): Alert[] {
    return this.alerts.filter(alert => !alert.resolved);
  }

  /**
   * Resolver um alerta
   */
  resolveAlert(alertId: string): void {
    const alert = this.alerts.find(a => a.id === alertId);
    if (alert) {
      alert.resolved = true;
      this.saveAlerts();
    }
  }

  /**
   * Resolver todos os alertas
   */
  resolveAllAlerts(): void {
    this.alerts.forEach(alert => {
      alert.resolved = true;
    });
    this.saveAlerts();
  }

  /**
   * Limpar alertas antigos
   */
  clearOldAlerts(maxAge: number = 24 * 60 * 60 * 1000): void {
    const cutoff = new Date(Date.now() - maxAge);
    this.alerts = this.alerts.filter(alert => 
      alert.timestamp > cutoff || !alert.resolved
    );
    this.saveAlerts();
  }

  /**
   * Atualizar configuração
   */
  updateConfig(newConfig: Partial<AlertConfig>): void {
    this.config = { ...this.config, ...newConfig };
    this.saveConfig();
    
    // Reiniciar se necessário
    if (this.isRunning) {
      this.stop();
      this.start();
    }
  }

  /**
   * Obter configuração atual
   */
  getConfig(): AlertConfig {
    return { ...this.config };
  }

  /**
   * Criar alerta manualmente
   */
  createAlert(
    type: Alert['type'],
    category: Alert['category'],
    title: string,
    message: string,
    metadata?: Record<string, any>
  ): void {
    const alert: Alert = {
      id: this.generateAlertId(),
      type,
      category,
      title,
      message,
      timestamp: new Date(),
      resolved: false,
      metadata
    };
    
    this.addAlert(alert);
  }

  /**
   * Verificar alertas baseados nas métricas atuais
   */
  private async checkAlerts(): Promise<void> {
    try {
      // Coletar métricas atuais
      const metrics = await this.collectMetrics();
      
      // Verificar cada threshold
      for (const threshold of this.config.thresholds) {
        if (!threshold.enabled) continue;
        
        const value = this.getMetricValue(metrics, threshold.metric);
        if (value === undefined) continue;
        
        const alertType = this.evaluateThreshold(value, threshold);
        if (alertType) {
          this.createThresholdAlert(threshold, value, alertType, metrics);
        }
      }
      
      // Verificar tendências
      this.checkTrends(metrics);
      
      this.lastMetrics = metrics;
    } catch (error) {
      // Erro ao verificar alertas do sistema
      this.createAlert(
        'error',
        'system',
        'Erro no Sistema de Alertas',
        `Falha ao verificar alertas: ${error instanceof Error ? error.message : 'Erro desconhecido'}`,
        { error: error instanceof Error ? error.stack : error }
      );
    }
  }

  /**
   * Coletar métricas do sistema
   */
  private async collectMetrics(): Promise<Record<string, any>> {
    const cacheStats = cacheManager.getAllStats();
    const systemStats = systemStatusCache.getStats();
    const metricsStats = metricsCache.getStats();
    
    // Calcular métricas agregadas
    const totalHits = Object.values(cacheStats).reduce((sum, stats) => sum + stats.hits, 0);
    const totalMisses = Object.values(cacheStats).reduce((sum, stats) => sum + stats.misses, 0);
    const avgHitRate = totalHits + totalMisses > 0 ? totalHits / (totalHits + totalMisses) : 0;
    
    const avgResponseTime = Object.values(cacheStats)
      .reduce((sum, stats) => sum + stats.averageResponseTime, 0) / Object.keys(cacheStats).length;
    
    // Simular métricas de sistema (em um ambiente real, estas viriam de APIs)
    const memoryUsage = this.getMemoryUsage();
    const errorRate = this.calculateErrorRate();
    
    return {
      responseTime: avgResponseTime,
      cacheHitRate: avgHitRate,
      errorRate,
      memoryUsage,
      cacheStats,
      systemStats,
      metricsStats,
      timestamp: new Date()
    };
  }

  /**
   * Obter valor de uma métrica específica
   */
  private getMetricValue(metrics: Record<string, any>, metricName: string): number | undefined {
    switch (metricName) {
      case 'responseTime':
        return metrics.responseTime;
      case 'cacheHitRate':
        return metrics.cacheHitRate;
      case 'errorRate':
        return metrics.errorRate;
      case 'memoryUsage':
        return metrics.memoryUsage;
      default:
        return metrics[metricName];
    }
  }

  /**
   * Avaliar se um valor ultrapassa os thresholds
   */
  private evaluateThreshold(value: number, threshold: AlertThreshold): Alert['type'] | null {
    const { operator, warningValue, errorValue, criticalValue } = threshold;
    
    const compare = (a: number, b: number): boolean => {
      switch (operator) {
        case 'gt': return a > b;
        case 'lt': return a < b;
        case 'eq': return a === b;
        default: return false;
      }
    };
    
    if (compare(value, criticalValue)) return 'critical';
    if (compare(value, errorValue)) return 'error';
    if (compare(value, warningValue)) return 'warning';
    
    return null;
  }

  /**
   * Criar alerta de threshold
   */
  private createThresholdAlert(
    threshold: AlertThreshold,
    value: number,
    alertType: Alert['type'],
    metrics: Record<string, any>
  ): void {
    // Evitar alertas duplicados recentes
    const recentAlert = this.alerts.find(alert => 
      alert.category === 'performance' &&
      alert.metadata?.metric === threshold.metric &&
      alert.type === alertType &&
      !alert.resolved &&
      (Date.now() - alert.timestamp.getTime()) < 5 * 60 * 1000 // 5 minutos
    );
    
    if (recentAlert) return;
    
    const metricNames: Record<string, string> = {
      responseTime: 'Tempo de Resposta',
      cacheHitRate: 'Taxa de Hit do Cache',
      errorRate: 'Taxa de Erro',
      memoryUsage: 'Uso de Memória'
    };
    
    const metricName = metricNames[threshold.metric] || threshold.metric;
    const formattedValue = this.formatMetricValue(threshold.metric, value);
    const thresholdValue = this.formatMetricValue(
      threshold.metric, 
      alertType === 'critical' ? threshold.criticalValue :
      alertType === 'error' ? threshold.errorValue : threshold.warningValue
    );
    
    this.createAlert(
      alertType,
      'performance',
      `${metricName} ${alertType === 'critical' ? 'Crítico' : alertType === 'error' ? 'Alto' : 'Elevado'}`,
      `${metricName} está em ${formattedValue}, ultrapassando o limite de ${thresholdValue}`,
      {
        metric: threshold.metric,
        value,
        threshold: threshold,
        metrics
      }
    );
  }

  /**
   * Verificar tendências nas métricas
   */
  private checkTrends(currentMetrics: Record<string, any>): void {
    if (!this.lastMetrics.timestamp) return;
    
    const timeDiff = currentMetrics.timestamp.getTime() - this.lastMetrics.timestamp.getTime();
    if (timeDiff < 60000) return; // Verificar tendências apenas a cada minuto
    
    // Verificar degradação do cache
    const currentHitRate = currentMetrics.cacheHitRate;
    const lastHitRate = this.lastMetrics.cacheHitRate;
    
    if (lastHitRate && currentHitRate < lastHitRate - 0.2) {
      this.createAlert(
        'warning',
        'cache',
        'Degradação do Cache Detectada',
        `Taxa de hit do cache caiu de ${(lastHitRate * 100).toFixed(1)}% para ${(currentHitRate * 100).toFixed(1)}%`,
        {
          previousHitRate: lastHitRate,
          currentHitRate,
          degradation: lastHitRate - currentHitRate
        }
      );
    }
    
    // Verificar aumento no tempo de resposta
    const currentResponseTime = currentMetrics.responseTime;
    const lastResponseTime = this.lastMetrics.responseTime;
    
    if (lastResponseTime && currentResponseTime > lastResponseTime * 1.5) {
      this.createAlert(
        'warning',
        'performance',
        'Aumento no Tempo de Resposta',
        `Tempo de resposta aumentou de ${lastResponseTime.toFixed(0)}ms para ${currentResponseTime.toFixed(0)}ms`,
        {
          previousResponseTime: lastResponseTime,
          currentResponseTime,
          increase: ((currentResponseTime / lastResponseTime - 1) * 100).toFixed(1)
        }
      );
    }
  }

  /**
   * Adicionar alerta à lista
   */
  private addAlert(alert: Alert): void {
    this.alerts.unshift(alert);
    
    // Limitar número de alertas
    if (this.alerts.length > this.config.maxAlerts) {
      this.alerts = this.alerts.slice(0, this.config.maxAlerts);
    }
    
    // Notificar listeners
    this.listeners.forEach(listener => {
      try {
        listener(alert);
      } catch (error) {
        // Erro ao notificar listener de alerta
      }
    });
    
    // Enviar notificações
    if (this.config.enableNotifications) {
      this.sendNotification(alert);
    }
    
    this.saveAlerts();
  }

  /**
   * Enviar notificação
   */
  private sendNotification(alert: Alert): void {
    // Notificação do browser
    if (this.config.enableBrowserNotifications && 'Notification' in window) {
      if (Notification.permission === 'granted') {
        new Notification(alert.title, {
          body: alert.message,
          icon: this.getAlertIcon(alert.type),
          tag: alert.id
        });
      }
    }
    
    // Som de alerta
    if (this.config.enableSound && alert.type === 'critical') {
      this.playAlertSound();
    }
    
    // Alerta crítico ou erro registrado para monitoramento
    if (alert.type === 'critical' || alert.type === 'error') {
      // Log de alerta crítico para monitoramento
    }
  }

  /**
   * Formatar valor da métrica para exibição
   */
  private formatMetricValue(metric: string, value: number): string {
    switch (metric) {
      case 'responseTime':
        return `${value.toFixed(0)}ms`;
      case 'cacheHitRate':
      case 'errorRate':
      case 'memoryUsage':
        return `${(value * 100).toFixed(1)}%`;
      default:
        return value.toString();
    }
  }

  /**
   * Obter ícone do alerta
   */
  private getAlertIcon(type: Alert['type']): string {
    switch (type) {
      case 'critical': return '🚨';
      case 'error': return '❌';
      case 'warning': return '⚠️';
      case 'info': return 'ℹ️';
      default: return '📢';
    }
  }

  /**
   * Reproduzir som de alerta
   */
  private playAlertSound(): void {
    try {
      const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuBzvLZiTYIG2m98OScTgwOUarm7blmGgU7k9n1unEiBC13yO/eizEIHWq+8+OWT');
      audio.volume = 0.3;
      audio.play().catch(() => {});
    } catch (error) {
      // Ignorar erros de áudio
    }
  }

  /**
   * Solicitar permissão para notificações
   */
  private async requestNotificationPermission(): Promise<void> {
    if ('Notification' in window && Notification.permission === 'default') {
      try {
        await Notification.requestPermission();
      } catch (error) {
        // Notification permission request failed - silent fail
      }
    }
  }

  /**
   * Simular uso de memória (em ambiente real, viria de uma API)
   */
  private getMemoryUsage(): number {
    if ('memory' in performance) {
      const memory = (performance as any).memory;
      return memory.usedJSHeapSize / memory.jsHeapSizeLimit;
    }
    return Math.random() * 0.5; // Valor simulado
  }

  /**
   * Calcular taxa de erro (em ambiente real, viria de métricas reais)
   */
  private calculateErrorRate(): number {
    // Simular taxa de erro baseada em estatísticas do cache
    const stats = metricsCache.getStats();
    const total = stats.hits + stats.misses;
    return total > 0 ? Math.min(stats.misses / total * 0.1, 0.05) : 0;
  }

  /**
   * Gerar ID único para alerta
   */
  private generateAlertId(): string {
    return `alert_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Salvar alertas no localStorage
   */
  private saveAlerts(): void {
    try {
      localStorage.setItem('glpi_dashboard_alerts', JSON.stringify(this.alerts));
    } catch (error) {
      // Failed to save alerts to localStorage - silent fail
    }
  }

  /**
   * Carregar alertas do localStorage
   */
  private loadAlerts(): void {
    try {
      const saved = localStorage.getItem('glpi_dashboard_alerts');
      if (saved) {
        const alerts = JSON.parse(saved);
        this.alerts = alerts.map((alert: any) => ({
          ...alert,
          timestamp: new Date(alert.timestamp)
        }));
      }
    } catch (error) {
      // Failed to load alerts from localStorage - silent fail
    }
  }

  /**
   * Salvar configuração no localStorage
   */
  private saveConfig(): void {
    try {
      localStorage.setItem('glpi_dashboard_alert_config', JSON.stringify(this.config));
    } catch (error) {
      // Failed to save alert config to localStorage - silent fail
    }
  }

  /**
   * Carregar configuração do localStorage
   */
  private loadConfig(): void {
    try {
      const saved = localStorage.getItem('glpi_dashboard_alert_config');
      if (saved) {
        const config = JSON.parse(saved);
        this.config = { ...DEFAULT_CONFIG, ...config };
      }
    } catch (error) {
      // Failed to load alert config from localStorage - silent fail
    }
  }
}

// Instância global do serviço de alertas
export const alertService = new AlertService();

// Auto-iniciar o serviço
alertService.start();