/**
 * Sistema de monitoramento em tempo real para detectar inconsistências
 * Implementa verificações contínuas e alertas automáticos
 */

import { SystemStatus, TechnicianRanking } from '../types';
import { DashboardMetrics } from '../types/api';
import { DataIntegrityReport } from './dataValidation';
import { dataCacheManager } from './dataCache';

interface MonitoringRule {
  id: string;
  name: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  check: (data: {
    metrics: DashboardMetrics;
    systemStatus: SystemStatus;
    technicianRanking: TechnicianRanking[];
    validationReport: DataIntegrityReport;
  }) => {
    passed: boolean;
    message?: string;
    details?: any;
  };
}

interface MonitoringAlert {
  id: string;
  ruleId: string;
  ruleName: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  details: any;
  timestamp: Date;
  acknowledged: boolean;
}

class DataMonitor {
  private alerts: MonitoringAlert[] = [];
  private rules: MonitoringRule[] = [];
  private isMonitoring = false;
  private monitoringInterval: NodeJS.Timeout | null = null;
  private listeners: ((alerts: MonitoringAlert[]) => void)[] = [];
  private alertCounter = 0;

  constructor() {
    this.initializeRules();
  }

  /**
   * Inicializa as regras de monitoramento
   */
  private initializeRules(): void {
    this.rules = [
      {
        id: 'data-freshness',
        name: 'Atualização dos Dados',
        description: 'Verifica se os dados estão sendo atualizados regularmente',
        severity: 'high',
        check: ({ validationReport }) => {
          if (!validationReport || !validationReport.timestamp) {
            return {
              passed: false,
              message: 'Relatório de validação não disponível',
              details: { validationReport: !!validationReport },
            };
          }

          const now = Date.now();
          const lastUpdate = validationReport.timestamp.getTime();
          const age = now - lastUpdate;
          const maxAge = 5 * 60 * 1000; // 5 minutos

          return {
            passed: age <= maxAge,
            message:
              age > maxAge
                ? `Dados não atualizados há ${Math.round(age / 60000)} minutos`
                : undefined,
            details: { age, maxAge, lastUpdate },
          };
        },
      },

      {
        id: 'metrics-consistency',
        name: 'Consistência das Métricas',
        description: 'Verifica se as métricas estão consistentes entre si',
        severity: 'critical',
        check: ({ metrics }) => {
          if (!metrics || !metrics.niveis || !metrics.niveis.geral) {
            return {
              passed: false,
              message: 'Dados de métricas não disponíveis para verificação de consistência',
              details: { metrics },
            };
          }

          const total =
            (metrics.niveis.geral.novos || 0) +
            (metrics.niveis.geral.pendentes || 0) +
            (metrics.niveis.geral.progresso || 0) +
            (metrics.niveis.geral.resolvidos || 0);

          // Verificar se o total geral bate com a soma dos níveis
          let levelTotal = 0;
          Object.values(metrics.niveis).forEach(level => {
            levelTotal +=
              (level.novos || 0) +
              (level.pendentes || 0) +
              (level.progresso || 0) +
              (level.resolvidos || 0);
          });

          const discrepancy = Math.abs(total - levelTotal);
          const tolerance = Math.max(1, total * 0.05); // 5% de tolerância

          return {
            passed: discrepancy <= tolerance,
            message:
              discrepancy > tolerance
                ? `Inconsistência nas métricas: total geral (${total}) vs soma dos níveis (${levelTotal})`
                : undefined,
            details: { total, levelTotal, discrepancy, tolerance },
          };
        },
      },

      {
        id: 'system-connectivity',
        name: 'Conectividade do Sistema',
        description: 'Verifica se o sistema está respondendo adequadamente',
        severity: 'critical',
        check: ({ systemStatus }) => {
          if (!systemStatus) {
            return {
              passed: false,
              message: 'Status do sistema não disponível',
              details: { systemStatus },
            };
          }

          const isOnline = systemStatus.status === 'online';

          return {
            passed: isOnline,
            message: !isOnline ? 'Sistema offline' : undefined,
            details: { isOnline },
          };
        },
      },

      {
        id: 'technician-data-integrity',
        name: 'Integridade dos Dados de Técnicos',
        description: 'Verifica se os dados dos técnicos estão íntegros',
        severity: 'medium',
        check: ({ technicianRanking, metrics }) => {
          if (
            !technicianRanking ||
            !Array.isArray(technicianRanking) ||
            !metrics ||
            !metrics.niveis ||
            !metrics.niveis.geral
          ) {
            return {
              passed: false,
              message: 'Dados de técnicos ou métricas não disponíveis',
              details: { technicianRanking, metrics },
            };
          }

          // Verificar se há técnicos duplicados
          const technicianIds = technicianRanking.map(t => t?.id).filter(Boolean);
          const uniqueIds = new Set(technicianIds);
          const hasDuplicates = technicianIds.length !== uniqueIds.size;

          // Verificar se o total de tickets dos técnicos é razoável
          const totalTechnicianTickets = technicianRanking.reduce(
            (sum, t) => sum + (t?.total || 0),
            0
          );
          const totalSystemTickets =
            (metrics.niveis.geral.novos || 0) +
            (metrics.niveis.geral.pendentes || 0) +
            (metrics.niveis.geral.progresso || 0) +
            (metrics.niveis.geral.resolvidos || 0);

          const ratio = totalSystemTickets > 0 ? totalTechnicianTickets / totalSystemTickets : 0;
          const isReasonableRatio = ratio <= 2.0; // Máximo 200% (considerando tickets históricos)

          return {
            passed: !hasDuplicates && isReasonableRatio,
            message: hasDuplicates
              ? 'Técnicos duplicados encontrados'
              : !isReasonableRatio
                ? `Proporção de tickets suspeita: ${(ratio * 100).toFixed(1)}%`
                : undefined,
            details: {
              hasDuplicates,
              totalTechnicianTickets,
              totalSystemTickets,
              ratio,
            },
          };
        },
      },

      {
        id: 'cache-performance',
        name: 'Performance do Cache',
        description: 'Monitora a eficiência do sistema de cache',
        severity: 'low',
        check: () => {
          const cacheInfo = dataCacheManager.getInfo();
          const isEfficient = cacheInfo.hasData && cacheInfo.status !== 'expired';

          return {
            passed: isEfficient,
            message: !isEfficient ? 'Cache não está sendo utilizado eficientemente' : undefined,
            details: cacheInfo,
          };
        },
      },

      {
        id: 'validation-errors',
        name: 'Erros de Validação',
        description: 'Monitora erros críticos de validação de dados',
        severity: 'high',
        check: ({ validationReport }) => {
          if (
            !validationReport ||
            !validationReport.metrics ||
            !validationReport.systemStatus ||
            !validationReport.technicianRanking
          ) {
            return {
              passed: false,
              message: 'Relatório de validação não disponível',
              details: { validationReport },
            };
          }

          const totalErrors =
            (validationReport.metrics.errors?.length || 0) +
            (validationReport.systemStatus.errors?.length || 0) +
            (validationReport.technicianRanking.errors?.length || 0);

          return {
            passed: totalErrors === 0,
            message: totalErrors > 0 ? `${totalErrors} erros de validação encontrados` : undefined,
            details: {
              metricsErrors: validationReport.metrics.errors || [],
              systemStatusErrors: validationReport.systemStatus.errors || [],
              technicianRankingErrors: validationReport.technicianRanking.errors || [],
            },
          };
        },
      },
    ];
  }

  /**
   * Executa todas as regras de monitoramento
   */
  runChecks(data: {
    metrics: DashboardMetrics;
    systemStatus: SystemStatus;
    technicianRanking: TechnicianRanking[];
    validationReport: DataIntegrityReport;
  }): MonitoringAlert[] {
    const newAlerts: MonitoringAlert[] = [];

    this.rules.forEach(rule => {
      try {
        const result = rule.check(data);

        if (!result.passed) {
          const alert: MonitoringAlert = {
            id: `${rule.id}-${Date.now()}-${++this.alertCounter}`,
            ruleId: rule.id,
            ruleName: rule.name,
            severity: rule.severity,
            message: result.message || 'Verificação falhou',
            details: result.details,
            timestamp: new Date(),
            acknowledged: false,
          };

          newAlerts.push(alert);
        }
      } catch (error) {
        console.error(`Erro ao executar regra ${rule.id}:`, error);
      }
    });

    // Adicionar novos alertas à lista
    this.alerts.push(...newAlerts);

    // Limitar o número de alertas (manter apenas os últimos 100)
    if (this.alerts.length > 100) {
      this.alerts = this.alerts.slice(-100);
    }

    // Notificar listeners
    this.notifyListeners();

    return newAlerts;
  }

  /**
   * Inicia o monitoramento contínuo
   */
  startMonitoring(intervalMs: number = 30000): void {
    if (this.isMonitoring) {
      console.warn('Monitoramento já está ativo');
      return;
    }

    this.isMonitoring = true;

    this.monitoringInterval = setInterval(async () => {
      try {
        const cached = dataCacheManager.get();

        if (cached.metrics && cached.systemStatus && cached.validationReport) {
          const newAlerts = this.runChecks({
            metrics: cached.metrics,
            systemStatus: cached.systemStatus,
            technicianRanking: cached.technicianRanking,
            validationReport: cached.validationReport,
          });

          if (newAlerts.length > 0) {
            console.warn('🚨 Novos alertas de monitoramento:', newAlerts);
          }
        }
      } catch (error) {
        console.error('Erro durante monitoramento:', error);
      }
    }, intervalMs);

    console.log(`📊 Monitoramento iniciado (intervalo: ${intervalMs}ms)`);
  }

  /**
   * Para o monitoramento contínuo
   */
  stopMonitoring(): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
    }

    this.isMonitoring = false;
    console.log('📊 Monitoramento parado');
  }

  /**
   * Obtém todos os alertas
   */
  getAlerts(): MonitoringAlert[] {
    return [...this.alerts];
  }

  /**
   * Obtém alertas por severidade
   */
  getAlertsBySeverity(severity: 'low' | 'medium' | 'high' | 'critical'): MonitoringAlert[] {
    return this.alerts.filter(alert => alert.severity === severity);
  }

  /**
   * Obtém alertas não reconhecidos
   */
  getUnacknowledgedAlerts(): MonitoringAlert[] {
    return this.alerts.filter(alert => !alert.acknowledged);
  }

  /**
   * Reconhece um alerta
   */
  acknowledgeAlert(alertId: string): void {
    const alert = this.alerts.find(a => a.id === alertId);
    if (alert) {
      alert.acknowledged = true;
      this.notifyListeners();
    }
  }

  /**
   * Limpa alertas antigos
   */
  clearOldAlerts(maxAgeMs: number = 24 * 60 * 60 * 1000): void {
    const cutoff = Date.now() - maxAgeMs;
    const initialCount = this.alerts.length;

    this.alerts = this.alerts.filter(alert => alert.timestamp.getTime() > cutoff);

    const removedCount = initialCount - this.alerts.length;
    if (removedCount > 0) {
      console.log(`🧹 ${removedCount} alertas antigos removidos`);
      this.notifyListeners();
    }
  }

  /**
   * Adiciona um listener para mudanças nos alertas
   */
  addListener(listener: (alerts: MonitoringAlert[]) => void): void {
    this.listeners.push(listener);
  }

  /**
   * Remove um listener
   */
  removeListener(listener: (alerts: MonitoringAlert[]) => void): void {
    const index = this.listeners.indexOf(listener);
    if (index > -1) {
      this.listeners.splice(index, 1);
    }
  }

  /**
   * Notifica todos os listeners
   */
  private notifyListeners(): void {
    this.listeners.forEach(listener => {
      try {
        listener([...this.alerts]);
      } catch (error) {
        console.error('Erro ao notificar listener:', error);
      }
    });
  }

  /**
   * Obtém estatísticas dos alertas
   */
  getStatistics(): {
    total: number;
    bySeverity: Record<string, number>;
    unacknowledged: number;
    recent: number; // últimas 24h
  } {
    const now = Date.now();
    const last24h = now - 24 * 60 * 60 * 1000;

    const stats = {
      total: this.alerts.length,
      bySeverity: {
        low: 0,
        medium: 0,
        high: 0,
        critical: 0,
      },
      unacknowledged: 0,
      recent: 0,
    };

    this.alerts.forEach(alert => {
      stats.bySeverity[alert.severity]++;

      if (!alert.acknowledged) {
        stats.unacknowledged++;
      }

      if (alert.timestamp.getTime() > last24h) {
        stats.recent++;
      }
    });

    return stats;
  }

  /**
   * Força uma verificação imediata
   */
  async forceCheck(): Promise<MonitoringAlert[]> {
    const cached = dataCacheManager.get();

    if (cached.metrics && cached.systemStatus && cached.validationReport) {
      return this.runChecks({
        metrics: cached.metrics,
        systemStatus: cached.systemStatus,
        technicianRanking: cached.technicianRanking,
        validationReport: cached.validationReport,
      });
    }

    return [];
  }
}

// Instância singleton do monitor
export const dataMonitor = new DataMonitor();

// Utilitários para debugging
export const debugMonitor = {
  getAlerts: () => dataMonitor.getAlerts(),
  getStats: () => dataMonitor.getStatistics(),
  forceCheck: () => dataMonitor.forceCheck(),
  clearOld: () => dataMonitor.clearOldAlerts(),
};

// Expor no window para debugging em desenvolvimento
if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
  (window as any).debugMonitor = debugMonitor;
}

// Tipos exportados
export type { MonitoringAlert, MonitoringRule };
