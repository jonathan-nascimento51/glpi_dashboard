/**
 * Monitor em Tempo Real
 *
 * Sistema que detecta automaticamente quando métricas ficam zeradas
 * ou inconsistentes, acionando alertas e ações corretivas.
 */

import { preDeliveryValidator } from './preDeliveryValidator';
import { dataIntegrityMonitor } from './dataIntegrityMonitor';
import { visualValidator } from './visualValidator';
import { workflowOptimizer } from './workflowOptimizer';

export interface MonitorAlert {
  id: string;
  type: 'critical' | 'warning' | 'info';
  category: 'metrics' | 'api' | 'visual' | 'performance' | 'security';
  title: string;
  message: string;
  timestamp: string;
  source: string;
  data?: any;
  resolved: boolean;
  resolvedAt?: string;
  actions: AlertAction[];
}

export interface AlertAction {
  id: string;
  name: string;
  description: string;
  automated: boolean;
  executed: boolean;
  executedAt?: string;
  result?: any;
  error?: string;
}

export interface MonitoringMetrics {
  uptime: number;
  alertsGenerated: number;
  criticalAlerts: number;
  resolvedAlerts: number;
  averageResolutionTime: number;
  systemHealth: 'healthy' | 'degraded' | 'critical';
  lastCheck: string;
  checksPerformed: number;
  falsePositives: number;
}

export interface MonitorConfig {
  enabled: boolean;
  checkInterval: number; // milliseconds
  alertThresholds: {
    consecutiveFailures: number;
    responseTimeMs: number;
    zeroMetricsThreshold: number; // seconds
  };
  autoRecovery: {
    enabled: boolean;
    maxAttempts: number;
    backoffMultiplier: number;
  };
  notifications: {
    console: boolean;
    visual: boolean;
    sound: boolean;
    webhook?: string;
  };
  healthChecks: {
    api: boolean;
    metrics: boolean;
    visual: boolean;
    performance: boolean;
  };
}

class RealTimeMonitor {
  private config: MonitorConfig = {
    enabled: true,
    checkInterval: 30000, // 30 segundos
    alertThresholds: {
      consecutiveFailures: 3,
      responseTimeMs: 5000,
      zeroMetricsThreshold: 60, // 1 minuto
    },
    autoRecovery: {
      enabled: true,
      maxAttempts: 3,
      backoffMultiplier: 2,
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
      performance: true,
    },
  };

  private isMonitoring = false;
  private monitoringInterval: NodeJS.Timeout | null = null;
  private alerts: MonitorAlert[] = [];
  private metrics: MonitoringMetrics = {
    uptime: 0,
    alertsGenerated: 0,
    criticalAlerts: 0,
    resolvedAlerts: 0,
    averageResolutionTime: 0,
    systemHealth: 'healthy',
    lastCheck: new Date().toISOString(),
    checksPerformed: 0,
    falsePositives: 0,
  };

  private startTime: number = 0;
  private consecutiveFailures = 0;
  private lastMetricsCheck: any = null;
  private zeroMetricsStartTime: number | null = null;
  private recoveryAttempts = 0;

  /**
   * Inicia monitoramento em tempo real
   */
  startMonitoring(): void {
    if (this.isMonitoring) {
      // Monitor já está ativo
      return;
    }

    // Iniciando monitoramento em tempo real

    this.isMonitoring = true;
    this.startTime = Date.now();
    this.consecutiveFailures = 0;
    this.recoveryAttempts = 0;

    // Executar primeira verificação imediatamente
    this.performHealthCheck();

    // Configurar verificações periódicas
    this.monitoringInterval = setInterval(() => {
      this.performHealthCheck();
    }, this.config.checkInterval);

    // Configurar listeners de eventos
    this.setupEventListeners();

    // Monitor ativo
  }

  /**
   * Para monitoramento
   */
  stopMonitoring(): void {
    if (!this.isMonitoring) {
      // Monitor não está ativo
      return;
    }

    // Parando monitoramento

    this.isMonitoring = false;

    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
    }

    this.removeEventListeners();

    // Monitor parado
  }

  /**
   * Executa verificação completa de saúde
   */
  private async performHealthCheck(): Promise<void> {
    if (!this.isMonitoring) return;

    this.metrics.checksPerformed++;
    this.metrics.lastCheck = new Date().toISOString();
    this.metrics.uptime = Date.now() - this.startTime;

    try {
      const checks = await Promise.allSettled([
        this.config.healthChecks.api ? this.checkApiHealth() : Promise.resolve(true),
        this.config.healthChecks.metrics ? this.checkMetricsHealth() : Promise.resolve(true),
        this.config.healthChecks.visual ? this.checkVisualHealth() : Promise.resolve(true),
        this.config.healthChecks.performance
          ? this.checkPerformanceHealth()
          : Promise.resolve(true),
      ]);

      const failures = checks.filter(
        result =>
          result.status === 'rejected' || (result.status === 'fulfilled' && result.value === false)
      );

      if (failures.length > 0) {
        this.consecutiveFailures++;

        if (this.consecutiveFailures >= this.config.alertThresholds.consecutiveFailures) {
          await this.handleSystemDegradation(failures);
        }
      } else {
        // Sistema saudável - resetar contadores
        if (this.consecutiveFailures > 0) {
          console.log('✅ Sistema recuperado');
          this.consecutiveFailures = 0;
          this.recoveryAttempts = 0;
          this.zeroMetricsStartTime = null;
          this.updateSystemHealth('healthy');
        }
      }
    } catch (error) {
      console.error('💥 Erro durante verificação de saúde:', error);
      this.createAlert('critical', 'api', 'Erro no Monitor', `Falha na verificação: ${error}`);
    }
  }

  /**
   * Verifica saúde da API
   */
  private async checkApiHealth(): Promise<boolean> {
    try {
      const start = Date.now();
      const response = await fetch('/api/metrics');
      const responseTime = Date.now() - start;

      if (!response.ok) {
        this.createAlert(
          'critical',
          'api',
          'API Indisponível',
          `API retornou status ${response.status}`
        );
        return false;
      }

      if (responseTime > this.config.alertThresholds.responseTimeMs) {
        this.createAlert(
          'warning',
          'performance',
          'API Lenta',
          `Tempo de resposta: ${responseTime}ms`
        );
        return false;
      }

      return true;
    } catch (error) {
      this.createAlert(
        'critical',
        'api',
        'Erro de Conectividade',
        `Não foi possível conectar à API: ${error}`
      );
      return false;
    }
  }

  /**
   * Verifica saúde das métricas
   */
  private async checkMetricsHealth(): Promise<boolean> {
    try {
      const response = await fetch('/api/metrics');
      if (!response.ok) return false;

      const data = await response.json();
      if (!data.data) {
        this.createAlert(
          'critical',
          'metrics',
          'Estrutura de Dados Inválida',
          'API não retornou estrutura esperada'
        );
        return false;
      }

      const metrics = data.data;
      const values = [
        metrics.novos || 0,
        metrics.pendentes || 0,
        metrics.progresso || 0,
        metrics.resolvidos || 0,
      ];

      const allZero = values.every(v => v === 0);
      const total = values.reduce((sum, v) => sum + v, 0);

      // Detectar métricas zeradas
      if (allZero) {
        if (!this.zeroMetricsStartTime) {
          this.zeroMetricsStartTime = Date.now();
          console.log('⚠️ Métricas zeradas detectadas - iniciando monitoramento');
        } else {
          const zeroTime = Date.now() - this.zeroMetricsStartTime;
          const thresholdMs = this.config.alertThresholds.zeroMetricsThreshold * 1000;

          if (zeroTime > thresholdMs) {
            this.createAlert(
              'critical',
              'metrics',
              'Métricas Zeradas',
              `Todas as métricas estão zeradas há ${Math.round(zeroTime / 1000)}s`,
              { values, total, duration: zeroTime }
            );
            return false;
          }
        }
      } else {
        // Métricas OK - resetar timer
        if (this.zeroMetricsStartTime) {
          console.log('✅ Métricas recuperadas');
          this.zeroMetricsStartTime = null;
        }
      }

      // Detectar inconsistências
      if (this.lastMetricsCheck) {
        const lastTotal = this.lastMetricsCheck.total;
        const currentTotal = total;

        // Verificar se houve mudança drástica
        if (lastTotal > 0 && currentTotal === 0) {
          this.createAlert(
            'critical',
            'metrics',
            'Perda de Dados',
            `Métricas foram de ${lastTotal} para 0`,
            { previous: this.lastMetricsCheck, current: { values, total } }
          );
          return false;
        }
      }

      this.lastMetricsCheck = { values, total, timestamp: Date.now() };
      return true;
    } catch (error) {
      this.createAlert(
        'critical',
        'metrics',
        'Erro na Verificação de Métricas',
        `Falha ao verificar métricas: ${error}`
      );
      return false;
    }
  }

  /**
   * Verifica saúde visual
   */
  private async checkVisualHealth(): Promise<boolean> {
    try {
      const result = await visualValidator.validateDashboardRendering();

      if (!result.isValid) {
        this.createAlert(
          'warning',
          'visual',
          'Problemas de Renderização',
          `Problemas detectados: ${result.issues.join(', ')}`,
          result
        );
        return false;
      }

      return true;
    } catch (error) {
      this.createAlert(
        'warning',
        'visual',
        'Erro na Validação Visual',
        `Falha na validação: ${error}`
      );
      return false;
    }
  }

  /**
   * Verifica saúde de performance
   */
  private async checkPerformanceHealth(): Promise<boolean> {
    try {
      const start = Date.now();

      // Verificar performance da API
      const response = await fetch('/api/metrics');
      const apiTime = Date.now() - start;

      // Verificar performance do DOM
      const domStart = Date.now();
      const cards = document.querySelectorAll(
        '[data-testid="metric-card"], .metric-card, [class*="card"]'
      );
      const domTime = Date.now() - domStart;

      if (apiTime > this.config.alertThresholds.responseTimeMs) {
        this.createAlert(
          'warning',
          'performance',
          'Performance da API Degradada',
          `Tempo de resposta: ${apiTime}ms`,
          { apiTime, threshold: this.config.alertThresholds.responseTimeMs }
        );
        return false;
      }

      if (domTime > 100) {
        // 100ms para operações DOM
        this.createAlert(
          'info',
          'performance',
          'Performance do DOM Lenta',
          `Tempo de consulta DOM: ${domTime}ms`,
          { domTime, cardsFound: cards.length }
        );
      }

      return true;
    } catch (error) {
      this.createAlert(
        'warning',
        'performance',
        'Erro na Verificação de Performance',
        `Falha na verificação: ${error}`
      );
      return false;
    }
  }

  /**
   * Lida com degradação do sistema
   */
  private async handleSystemDegradation(failures: PromiseSettledResult<any>[]): Promise<void> {
    console.error(`🚨 Sistema degradado - ${failures.length} falhas consecutivas`);

    this.updateSystemHealth('degraded');

    // Tentar recuperação automática
    if (
      this.config.autoRecovery.enabled &&
      this.recoveryAttempts < this.config.autoRecovery.maxAttempts
    ) {
      await this.attemptAutoRecovery();
    } else {
      this.updateSystemHealth('critical');
      this.createAlert(
        'critical',
        'api',
        'Sistema Crítico',
        'Sistema em estado crítico - intervenção manual necessária'
      );
    }
  }

  /**
   * Tenta recuperação automática
   */
  private async attemptAutoRecovery(): Promise<void> {
    this.recoveryAttempts++;

    console.log(
      `🔄 Tentativa de recuperação ${this.recoveryAttempts}/${this.config.autoRecovery.maxAttempts}`
    );

    try {
      // Executar workflow de recuperação
      const result = await workflowOptimizer.quickWorkflow();

      if (result.deliveryApproved) {
        console.log('✅ Recuperação automática bem-sucedida');
        this.consecutiveFailures = 0;
        this.recoveryAttempts = 0;
        this.updateSystemHealth('healthy');

        this.createAlert(
          'info',
          'api',
          'Sistema Recuperado',
          'Recuperação automática bem-sucedida'
        );
      } else {
        throw new Error('Workflow de recuperação falhou');
      }
    } catch (error) {
      console.error(`❌ Recuperação ${this.recoveryAttempts} falhou:`, error);

      // Backoff exponencial
      const delay =
        this.config.checkInterval *
        Math.pow(this.config.autoRecovery.backoffMultiplier, this.recoveryAttempts - 1);

      setTimeout(() => {
        if (this.recoveryAttempts < this.config.autoRecovery.maxAttempts) {
          this.attemptAutoRecovery();
        }
      }, delay);
    }
  }

  /**
   * Cria alerta
   */
  private createAlert(
    type: MonitorAlert['type'],
    category: MonitorAlert['category'],
    title: string,
    message: string,
    data?: any
  ): MonitorAlert {
    const alert: MonitorAlert = {
      id: this.generateAlertId(),
      type,
      category,
      title,
      message,
      timestamp: new Date().toISOString(),
      source: 'RealTimeMonitor',
      data,
      resolved: false,
      actions: this.generateAlertActions(type, category),
    };

    this.alerts.push(alert);
    this.metrics.alertsGenerated++;

    if (type === 'critical') {
      this.metrics.criticalAlerts++;
    }

    // Notificar
    this.notifyAlert(alert);

    return alert;
  }

  /**
   * Gera ações para alerta
   */
  private generateAlertActions(
    type: MonitorAlert['type'],
    category: MonitorAlert['category']
  ): AlertAction[] {
    const actions: AlertAction[] = [];

    if (category === 'metrics') {
      actions.push({
        id: 'refresh-metrics',
        name: 'Atualizar Métricas',
        description: 'Força atualização das métricas',
        automated: true,
        executed: false,
      });
    }

    if (category === 'api') {
      actions.push({
        id: 'test-connectivity',
        name: 'Testar Conectividade',
        description: 'Testa conectividade com a API',
        automated: true,
        executed: false,
      });
    }

    if (type === 'critical') {
      actions.push({
        id: 'run-validation',
        name: 'Executar Validação',
        description: 'Executa validação completa do sistema',
        automated: false,
        executed: false,
      });
    }

    return actions;
  }

  /**
   * Notifica alerta
   */
  private notifyAlert(alert: MonitorAlert): void {
    const emoji = {
      critical: '🚨',
      warning: '⚠️',
      info: 'ℹ️',
    };

    if (this.config.notifications.console) {
      // Log de alerta removido para limpeza do código
    }

    if (this.config.notifications.visual && alert.type === 'critical') {
      // Mostrar notificação visual para alertas críticos
      if (process.env.NODE_ENV === 'development') {
        alert(`ALERTA CRÍTICO: ${alert.title}\n${alert.message}`);
      }
    }

    if (this.config.notifications.sound && alert.type === 'critical') {
      // Tocar som para alertas críticos (se suportado)
      try {
        const audio = new Audio(
          'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuBzvLZiTYIG2m98OScTgwOUarm7blmGgU7k9n1unEiBC13yO/eizEIHWq+8+OWT'
        );
        audio.play().catch(() => {}); // Ignorar erros de áudio
      } catch (error) {
        // Ignorar erros de áudio
      }
    }
  }

  /**
   * Atualiza saúde do sistema
   */
  private updateSystemHealth(health: MonitoringMetrics['systemHealth']): void {
    this.metrics.systemHealth = health;

    const emoji = {
      healthy: '💚',
      degraded: '💛',
      critical: '💔',
    };

    console.log(`${emoji[health]} Sistema: ${health.toUpperCase()}`);
  }

  /**
   * Configura listeners de eventos
   */
  private setupEventListeners(): void {
    // Listener para erros não capturados
    window.addEventListener('error', event => {
      this.createAlert(
        'warning',
        'api',
        'Erro JavaScript',
        `Erro não capturado: ${event.message}`,
        { filename: event.filename, lineno: event.lineno, colno: event.colno }
      );
    });

    // Listener para promises rejeitadas
    window.addEventListener('unhandledrejection', event => {
      this.createAlert(
        'warning',
        'api',
        'Promise Rejeitada',
        `Promise não tratada: ${event.reason}`,
        { reason: event.reason }
      );
    });
  }

  /**
   * Remove listeners de eventos
   */
  private removeEventListeners(): void {
    // Remover listeners seria implementado aqui
    // Por simplicidade, não implementado
  }

  /**
   * Gera ID único para alerta
   */
  private generateAlertId(): string {
    return `alert_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Métodos públicos
   */

  configure(config: Partial<MonitorConfig>): void {
    this.config = { ...this.config, ...config };
  }

  getAlerts(): MonitorAlert[] {
    return [...this.alerts];
  }

  getMetrics(): MonitoringMetrics {
    return { ...this.metrics };
  }

  isActive(): boolean {
    return this.isMonitoring;
  }

  resolveAlert(alertId: string): boolean {
    const alert = this.alerts.find(a => a.id === alertId);
    if (alert && !alert.resolved) {
      alert.resolved = true;
      alert.resolvedAt = new Date().toISOString();
      this.metrics.resolvedAlerts++;
      return true;
    }
    return false;
  }

  clearAlerts(): void {
    this.alerts = [];
    console.log('🧹 Alertas limpos');
  }

  getSystemStatus(): { health: string; uptime: number; alerts: number } {
    return {
      health: this.metrics.systemHealth,
      uptime: this.metrics.uptime,
      alerts: this.alerts.filter(a => !a.resolved).length,
    };
  }
}

// Instância global do monitor
export const realTimeMonitor = new RealTimeMonitor();

// Funções utilitárias para uso no console
(window as any).startMonitoring = () => realTimeMonitor.startMonitoring();
(window as any).stopMonitoring = () => realTimeMonitor.stopMonitoring();
(window as any).getMonitorAlerts = () => realTimeMonitor.getAlerts();
(window as any).getMonitorMetrics = () => realTimeMonitor.getMetrics();
(window as any).getSystemStatus = () => realTimeMonitor.getSystemStatus();
(window as any).clearAlerts = () => realTimeMonitor.clearAlerts();

export default RealTimeMonitor;
