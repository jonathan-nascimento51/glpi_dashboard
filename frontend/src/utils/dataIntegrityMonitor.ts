/**
 * Sistema de Monitoramento de Integridade de Dados em Tempo Real
 *
 * Detecta inconsistências entre API e frontend, monitora anomalias
 * e garante a qualidade dos dados apresentados no dashboard.
 */

export interface IntegrityCheck {
  id: string;
  name: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  isValid: boolean;
  message: string;
  timestamp: string;
  data?: any;
}

export interface IntegrityReport {
  overallStatus: 'healthy' | 'warning' | 'critical';
  checks: IntegrityCheck[];
  summary: {
    total: number;
    passed: number;
    failed: number;
    critical: number;
  };
  recommendations: string[];
  timestamp: string;
}

export interface MonitoringConfig {
  enableRealTimeMonitoring: boolean;
  checkInterval: number; // ms
  apiEndpoint: string;
  alertThresholds: {
    zeroMetricsAlert: boolean;
    inconsistencyThreshold: number;
    responseTimeThreshold: number; // ms
  };
  retentionPeriod: number; // ms - quanto tempo manter histórico
}

class DataIntegrityMonitor {
  private config: MonitoringConfig = {
    enableRealTimeMonitoring: true,
    checkInterval: 30000, // 30 segundos
    apiEndpoint: '/api/metrics',
    alertThresholds: {
      zeroMetricsAlert: true,
      inconsistencyThreshold: 0,
      responseTimeThreshold: 5000,
    },
    retentionPeriod: 24 * 60 * 60 * 1000, // 24 horas
  };

  private monitoringInterval: NodeJS.Timeout | null = null;
  private lastApiData: any = null;
  private lastFrontendData: any = null;
  private checksHistory: IntegrityCheck[] = [];
  private alertCallbacks: ((report: IntegrityReport) => void)[] = [];

  /**
   * Inicia o monitoramento em tempo real
   */
  startMonitoring(): void {
    if (this.monitoringInterval) {
      console.log('⚠️ Monitoramento já está ativo');
      return;
    }

    console.log('🔄 Iniciando monitoramento de integridade de dados...');

    this.monitoringInterval = setInterval(async () => {
      try {
        const report = await this.runIntegrityChecks();
        this.processReport(report);
      } catch (error) {
        console.error('💥 Erro durante monitoramento:', error);
      }
    }, this.config.checkInterval);

    // Executar primeira verificação imediatamente
    setTimeout(() => this.runIntegrityChecks().then(report => this.processReport(report)), 1000);
  }

  /**
   * Para o monitoramento
   */
  stopMonitoring(): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
      console.log('⏹️ Monitoramento de integridade parado');
    }
  }

  /**
   * Executa todas as verificações de integridade
   */
  async runIntegrityChecks(): Promise<IntegrityReport> {
    const checks: IntegrityCheck[] = [];
    const timestamp = new Date().toISOString();

    // 1. Verificação de conectividade da API
    checks.push(await this.checkApiConnectivity());

    // 2. Verificação de estrutura de dados da API
    checks.push(await this.checkApiDataStructure());

    // 3. Verificação de valores zerados
    checks.push(await this.checkZeroMetrics());

    // 4. Verificação de consistência API vs Frontend
    checks.push(await this.checkApiVsFrontendConsistency());

    // 5. Verificação de performance da API
    checks.push(await this.checkApiPerformance());

    // 6. Verificação de renderização do DOM
    checks.push(await this.checkDOMRendering());

    // 7. Verificação de anomalias nos dados
    checks.push(await this.checkDataAnomalies());

    // Calcular status geral
    const failed = checks.filter(c => !c.isValid);
    const critical = failed.filter(c => c.severity === 'critical');

    let overallStatus: IntegrityReport['overallStatus'] = 'healthy';
    if (critical.length > 0) {
      overallStatus = 'critical';
    } else if (failed.length > 0) {
      overallStatus = 'warning';
    }

    // Gerar recomendações
    const recommendations = this.generateRecommendations(checks);

    const report: IntegrityReport = {
      overallStatus,
      checks,
      summary: {
        total: checks.length,
        passed: checks.filter(c => c.isValid).length,
        failed: failed.length,
        critical: critical.length,
      },
      recommendations,
      timestamp,
    };

    // Armazenar no histórico
    this.checksHistory.push(...checks);
    this.cleanupHistory();

    return report;
  }

  /**
   * Verifica conectividade com a API
   */
  private async checkApiConnectivity(): Promise<IntegrityCheck> {
    const check: IntegrityCheck = {
      id: 'api-connectivity',
      name: 'Conectividade da API',
      description: 'Verifica se a API está acessível e respondendo',
      severity: 'critical',
      isValid: false,
      message: '',
      timestamp: new Date().toISOString(),
    };

    try {
      const startTime = Date.now();
      const response = await fetch(this.config.apiEndpoint);
      const responseTime = Date.now() - startTime;

      if (response.ok) {
        check.isValid = true;
        check.message = `API acessível (${responseTime}ms)`;
        check.data = { responseTime, status: response.status };
      } else {
        check.message = `API retornou erro: ${response.status} ${response.statusText}`;
        check.data = { status: response.status, statusText: response.statusText };
      }
    } catch (error) {
      check.message = `Erro de conectividade: ${error}`;
      check.data = { error: String(error) };
    }

    return check;
  }

  /**
   * Verifica estrutura dos dados da API
   */
  private async checkApiDataStructure(): Promise<IntegrityCheck> {
    const check: IntegrityCheck = {
      id: 'api-data-structure',
      name: 'Estrutura de Dados da API',
      description: 'Verifica se a API retorna dados na estrutura esperada',
      severity: 'high',
      isValid: false,
      message: '',
      timestamp: new Date().toISOString(),
    };

    try {
      const response = await fetch(this.config.apiEndpoint);
      if (!response.ok) {
        check.message = 'API não acessível para verificação de estrutura';
        return check;
      }

      const data = await response.json();
      this.lastApiData = data;

      // Verificar estrutura esperada
      const requiredFields = ['success', 'data'];
      const dataFields = ['novos', 'pendentes', 'progresso', 'resolvidos'];

      const missingFields: string[] = [];

      requiredFields.forEach(field => {
        if (!(field in data)) {
          missingFields.push(field);
        }
      });

      if (data.data) {
        dataFields.forEach(field => {
          if (!(field in data.data)) {
            missingFields.push(`data.${field}`);
          }
        });
      }

      if (missingFields.length === 0) {
        check.isValid = true;
        check.message = 'Estrutura de dados válida';
      } else {
        check.message = `Campos obrigatórios ausentes: ${missingFields.join(', ')}`;
      }

      check.data = { structure: data, missingFields };
    } catch (error) {
      check.message = `Erro ao verificar estrutura: ${error}`;
      check.data = { error: String(error) };
    }

    return check;
  }

  /**
   * Verifica se todas as métricas estão zeradas
   */
  private async checkZeroMetrics(): Promise<IntegrityCheck> {
    const check: IntegrityCheck = {
      id: 'zero-metrics',
      name: 'Métricas Zeradas',
      description: 'Detecta se todas as métricas principais estão zeradas',
      severity: 'high',
      isValid: true,
      message: '',
      timestamp: new Date().toISOString(),
    };

    if (!this.lastApiData || !this.lastApiData.data) {
      check.message = 'Dados da API não disponíveis para verificação';
      check.severity = 'medium';
      return check;
    }

    const metrics = this.lastApiData.data;
    const values = [
      metrics.novos || 0,
      metrics.pendentes || 0,
      metrics.progresso || 0,
      metrics.resolvidos || 0,
    ];

    const allZero = values.every(v => v === 0);
    const totalValue = values.reduce((sum, v) => sum + v, 0);

    if (allZero && this.config.alertThresholds.zeroMetricsAlert) {
      check.isValid = false;
      check.message = 'ALERTA: Todas as métricas estão zeradas';
      check.severity = 'critical';
    } else {
      check.message = `Métricas válidas (total: ${totalValue})`;
    }

    check.data = { metrics: values, total: totalValue, allZero };
    return check;
  }

  /**
   * Verifica consistência entre API e Frontend
   */
  private async checkApiVsFrontendConsistency(): Promise<IntegrityCheck> {
    const check: IntegrityCheck = {
      id: 'api-frontend-consistency',
      name: 'Consistência API vs Frontend',
      description: 'Compara dados da API com valores renderizados no frontend',
      severity: 'high',
      isValid: true,
      message: '',
      timestamp: new Date().toISOString(),
    };

    try {
      // Extrair dados do DOM
      const domMetrics = this.extractMetricsFromDOM();
      this.lastFrontendData = domMetrics;

      if (!this.lastApiData || !this.lastApiData.data) {
        check.message = 'Dados da API não disponíveis para comparação';
        check.severity = 'medium';
        return check;
      }

      const apiMetrics = {
        novos: this.lastApiData.data.novos || 0,
        pendentes: this.lastApiData.data.pendentes || 0,
        progresso: this.lastApiData.data.progresso || 0,
        resolvidos: this.lastApiData.data.resolvidos || 0,
      };

      const inconsistencies: string[] = [];
      let maxDifference = 0;

      for (const [key, apiValue] of Object.entries(apiMetrics)) {
        const domValue = domMetrics[key as keyof typeof domMetrics] || 0;
        const difference = Math.abs(apiValue - domValue);

        if (difference > this.config.alertThresholds.inconsistencyThreshold) {
          inconsistencies.push(`${key}: API=${apiValue}, DOM=${domValue}`);
          maxDifference = Math.max(maxDifference, difference);
        }
      }

      if (inconsistencies.length === 0) {
        check.message = 'Dados consistentes entre API e Frontend';
      } else {
        check.isValid = false;
        check.message = `Inconsistências detectadas: ${inconsistencies.join('; ')}`;
        if (maxDifference > 100) {
          check.severity = 'critical';
        }
      }

      check.data = {
        api: apiMetrics,
        dom: domMetrics,
        inconsistencies,
        maxDifference,
      };
    } catch (error) {
      check.isValid = false;
      check.message = `Erro durante verificação de consistência: ${error}`;
      check.data = { error: String(error) };
    }

    return check;
  }

  /**
   * Verifica performance da API
   */
  private async checkApiPerformance(): Promise<IntegrityCheck> {
    const check: IntegrityCheck = {
      id: 'api-performance',
      name: 'Performance da API',
      description: 'Monitora tempo de resposta da API',
      severity: 'medium',
      isValid: true,
      message: '',
      timestamp: new Date().toISOString(),
    };

    try {
      const startTime = Date.now();
      const response = await fetch(this.config.apiEndpoint);
      const responseTime = Date.now() - startTime;

      if (responseTime > this.config.alertThresholds.responseTimeThreshold) {
        check.isValid = false;
        check.message = `API lenta: ${responseTime}ms (limite: ${this.config.alertThresholds.responseTimeThreshold}ms)`;
        if (responseTime > this.config.alertThresholds.responseTimeThreshold * 2) {
          check.severity = 'high';
        }
      } else {
        check.message = `Performance adequada: ${responseTime}ms`;
      }

      check.data = { responseTime, threshold: this.config.alertThresholds.responseTimeThreshold };
    } catch (error) {
      check.isValid = false;
      check.message = `Erro ao verificar performance: ${error}`;
      check.data = { error: String(error) };
    }

    return check;
  }

  /**
   * Verifica renderização do DOM
   */
  private async checkDOMRendering(): Promise<IntegrityCheck> {
    const check: IntegrityCheck = {
      id: 'dom-rendering',
      name: 'Renderização do DOM',
      description: 'Verifica se os elementos estão sendo renderizados corretamente',
      severity: 'high',
      isValid: true,
      message: '',
      timestamp: new Date().toISOString(),
    };

    try {
      const cards = document.querySelectorAll(
        '[data-testid="metric-card"], .metric-card, [class*="card"]'
      );

      if (cards.length < 4) {
        check.isValid = false;
        check.message = `Poucos cards encontrados: ${cards.length} (esperado: 4+)`;
      } else {
        // Verificar se cards estão visíveis
        let visibleCards = 0;
        cards.forEach(card => {
          const rect = card.getBoundingClientRect();
          if (rect.width > 0 && rect.height > 0) {
            visibleCards++;
          }
        });

        if (visibleCards < 4) {
          check.isValid = false;
          check.message = `Cards não visíveis: ${visibleCards}/${cards.length}`;
        } else {
          check.message = `Renderização OK: ${visibleCards} cards visíveis`;
        }
      }

      check.data = { totalCards: cards.length, visibleCards: cards.length };
    } catch (error) {
      check.isValid = false;
      check.message = `Erro ao verificar DOM: ${error}`;
      check.data = { error: String(error) };
    }

    return check;
  }

  /**
   * Verifica anomalias nos dados
   */
  private async checkDataAnomalies(): Promise<IntegrityCheck> {
    const check: IntegrityCheck = {
      id: 'data-anomalies',
      name: 'Anomalias nos Dados',
      description: 'Detecta padrões anômalos nos dados',
      severity: 'medium',
      isValid: true,
      message: '',
      timestamp: new Date().toISOString(),
    };

    if (!this.lastApiData || !this.lastApiData.data) {
      check.message = 'Dados não disponíveis para análise de anomalias';
      return check;
    }

    const metrics = this.lastApiData.data;
    const anomalies: string[] = [];

    // Verificar valores negativos
    Object.entries(metrics).forEach(([key, value]) => {
      if (typeof value === 'number' && value < 0) {
        anomalies.push(`Valor negativo em ${key}: ${value}`);
      }
    });

    // Verificar valores extremamente altos (possível erro)
    const threshold = 100000; // 100k tickets seria muito alto
    Object.entries(metrics).forEach(([key, value]) => {
      if (typeof value === 'number' && value > threshold) {
        anomalies.push(`Valor muito alto em ${key}: ${value}`);
      }
    });

    if (anomalies.length > 0) {
      check.isValid = false;
      check.message = `Anomalias detectadas: ${anomalies.join('; ')}`;
      if (anomalies.some(a => a.includes('negativo'))) {
        check.severity = 'high';
      }
    } else {
      check.message = 'Nenhuma anomalia detectada';
    }

    check.data = { anomalies, metrics };
    return check;
  }

  /**
   * Extrai métricas do DOM
   */
  private extractMetricsFromDOM(): {
    novos: number;
    pendentes: number;
    progresso: number;
    resolvidos: number;
  } {
    const metrics = { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0 };

    try {
      const cards = document.querySelectorAll(
        '[data-testid="metric-card"], .metric-card, [class*="card"]'
      );

      const metricKeywords = {
        novos: ['NOVOS', 'NEW', 'NOVO'],
        pendentes: ['PENDENTES', 'PENDING', 'PENDENTE'],
        progresso: ['PROGRESSO', 'PROGRESS', 'EM PROGRESSO'],
        resolvidos: ['RESOLVIDOS', 'RESOLVED', 'RESOLVIDO'],
      };

      cards.forEach(card => {
        const cardText = card.textContent || '';

        // Identificar tipo de métrica
        let metricType: keyof typeof metrics | null = null;
        for (const [type, keywords] of Object.entries(metricKeywords)) {
          if (keywords.some(keyword => cardText.toUpperCase().includes(keyword))) {
            metricType = type as keyof typeof metrics;
            break;
          }
        }

        if (metricType) {
          // Extrair valor numérico (considerando formatação brasileira com pontos)
          // Primeiro tenta encontrar números formatados (ex: 1.234, 9.778)
          const formattedNumberMatches = cardText.match(/\b\d{1,3}(?:\.\d{3})*\b/g);
          // Depois tenta números simples
          const simpleNumberMatches = cardText.match(/\b\d+\b/g);

          const numberMatches = formattedNumberMatches || simpleNumberMatches;

          if (numberMatches && numberMatches.length > 0) {
            // Remover pontos para parsing
            const rawValue = numberMatches[0].replace(/\./g, '');
            const value = parseInt(rawValue, 10);
            if (!isNaN(value)) {
              metrics[metricType] = value;
            }
          }
        }
      });
    } catch (error) {
      console.warn('Erro ao extrair métricas do DOM:', error);
    }

    return metrics;
  }

  /**
   * Gera recomendações baseadas nos checks
   */
  private generateRecommendations(checks: IntegrityCheck[]): string[] {
    const recommendations: string[] = [];
    const failedChecks = checks.filter(c => !c.isValid);

    failedChecks.forEach(check => {
      switch (check.id) {
        case 'api-connectivity':
          recommendations.push('Verificar se o backend está rodando e acessível');
          break;
        case 'api-data-structure':
          recommendations.push('Verificar estrutura de dados retornada pela API');
          break;
        case 'zero-metrics':
          recommendations.push('Investigar por que todas as métricas estão zeradas');
          break;
        case 'api-frontend-consistency':
          recommendations.push('Verificar mapeamento de dados entre API e frontend');
          break;
        case 'api-performance':
          recommendations.push('Otimizar performance da API ou verificar conectividade');
          break;
        case 'dom-rendering':
          recommendations.push('Verificar renderização dos componentes do dashboard');
          break;
        case 'data-anomalies':
          recommendations.push('Investigar anomalias nos dados da fonte');
          break;
      }
    });

    // Recomendações gerais
    if (failedChecks.length > 3) {
      recommendations.push('Considerar reiniciar o sistema devido a múltiplas falhas');
    }

    return [...new Set(recommendations)]; // Remover duplicatas
  }

  /**
   * Processa relatório e dispara alertas se necessário
   */
  private processReport(report: IntegrityReport): void {
    // Log do status
    const statusEmoji = {
      healthy: '✅',
      warning: '⚠️',
      critical: '🚨',
    };

    console.log(
      `${statusEmoji[report.overallStatus]} Status de Integridade: ${report.overallStatus.toUpperCase()}`
    );
    console.log(`📊 Resumo: ${report.summary.passed}/${report.summary.total} checks passaram`);

    if (report.summary.failed > 0) {
      console.warn('❌ Checks que falharam:');
      report.checks
        .filter(c => !c.isValid)
        .forEach(check => {
          console.warn(`  - ${check.name}: ${check.message}`);
        });
    }

    if (report.recommendations.length > 0) {
      console.log('💡 Recomendações:');
      report.recommendations.forEach(rec => {
        console.log(`  - ${rec}`);
      });
    }

    // Disparar callbacks de alerta
    this.alertCallbacks.forEach(callback => {
      try {
        callback(report);
      } catch (error) {
        console.error('Erro em callback de alerta:', error);
      }
    });
  }

  /**
   * Limpa histórico antigo
   */
  private cleanupHistory(): void {
    const cutoff = Date.now() - this.config.retentionPeriod;
    this.checksHistory = this.checksHistory.filter(check => {
      return new Date(check.timestamp).getTime() > cutoff;
    });
  }

  /**
   * Adiciona callback para alertas
   */
  onAlert(callback: (report: IntegrityReport) => void): void {
    this.alertCallbacks.push(callback);
  }

  /**
   * Configura o monitor
   */
  configure(config: Partial<MonitoringConfig>): void {
    this.config = { ...this.config, ...config };

    // Reiniciar monitoramento se configuração mudou
    if (this.monitoringInterval && config.checkInterval) {
      this.stopMonitoring();
      this.startMonitoring();
    }
  }

  /**
   * Obtém histórico de checks
   */
  getHistory(): IntegrityCheck[] {
    return [...this.checksHistory];
  }

  /**
   * Obtém último relatório
   */
  async getLastReport(): Promise<IntegrityReport> {
    return this.runIntegrityChecks();
  }
}

// Instância global do monitor
export const dataIntegrityMonitor = new DataIntegrityMonitor();

// Funções utilitárias para uso no console
(window as any).checkDataIntegrity = () => dataIntegrityMonitor.runIntegrityChecks();
(window as any).startIntegrityMonitoring = () => dataIntegrityMonitor.startMonitoring();
(window as any).stopIntegrityMonitoring = () => dataIntegrityMonitor.stopMonitoring();

// Auto-inicialização em desenvolvimento (DESABILITADO TEMPORARIAMENTE)
// if (process.env.NODE_ENV === 'development') {
//   // Iniciar monitoramento automático após carregamento
//   window.addEventListener('load', () => {
//     setTimeout(() => {
//       dataIntegrityMonitor.startMonitoring();
//     }, 3000); // Aguardar 3s após load
//   });
// }

export default DataIntegrityMonitor;
