/**
 * Pipeline de Testes Automatizados
 *
 * Sistema completo de validação que executa testes visuais, funcionais
 * e de integridade antes de qualquer entrega ou deploy.
 */

import { visualValidator } from './visualValidator';
import { dataIntegrityMonitor, IntegrityReport } from './dataIntegrityMonitor';
import { MetricsValidator } from './metricsValidator';

export interface TestResult {
  id: string;
  name: string;
  category: 'visual' | 'functional' | 'integrity' | 'performance' | 'security';
  status: 'passed' | 'failed' | 'skipped' | 'warning';
  message: string;
  duration: number; // ms
  details?: any;
  timestamp: string;
}

export interface TestSuite {
  id: string;
  name: string;
  description: string;
  tests: TestResult[];
  status: 'passed' | 'failed' | 'warning';
  duration: number;
  coverage: {
    total: number;
    passed: number;
    failed: number;
    warnings: number;
  };
  timestamp: string;
}

export interface PipelineReport {
  overallStatus: 'passed' | 'failed' | 'warning';
  suites: TestSuite[];
  summary: {
    totalTests: number;
    passedTests: number;
    failedTests: number;
    warningTests: number;
    totalDuration: number;
  };
  recommendations: string[];
  blockers: string[];
  canDeploy: boolean;
  timestamp: string;
}

export interface PipelineConfig {
  enableVisualTests: boolean;
  enableFunctionalTests: boolean;
  enableIntegrityTests: boolean;
  enablePerformanceTests: boolean;
  enableSecurityTests: boolean;
  failOnWarnings: boolean;
  maxTestDuration: number; // ms
  retryFailedTests: boolean;
  maxRetries: number;
  parallelExecution: boolean;
}

class AutomatedTestPipeline {
  private config: PipelineConfig = {
    enableVisualTests: true,
    enableFunctionalTests: true,
    enableIntegrityTests: true,
    enablePerformanceTests: true,
    enableSecurityTests: false, // Pode ser habilitado conforme necessário
    failOnWarnings: false,
    maxTestDuration: 30000, // 30 segundos
    retryFailedTests: true,
    maxRetries: 2,
    parallelExecution: false, // Sequencial por padrão para evitar conflitos
  };

  private testHistory: PipelineReport[] = [];
  private isRunning = false;

  /**
   * Executa o pipeline completo de testes
   */
  async runPipeline(): Promise<PipelineReport> {
    if (this.isRunning) {
      throw new Error('Pipeline já está em execução');
    }

    this.isRunning = true;
    const startTime = Date.now();
    const timestamp = new Date().toISOString();

    console.log('🚀 Iniciando Pipeline de Testes Automatizados...');

    try {
      const suites: TestSuite[] = [];

      // Executar suites de teste
      if (this.config.enableVisualTests) {
        suites.push(await this.runVisualTestSuite());
      }

      if (this.config.enableFunctionalTests) {
        suites.push(await this.runFunctionalTestSuite());
      }

      if (this.config.enableIntegrityTests) {
        suites.push(await this.runIntegrityTestSuite());
      }

      if (this.config.enablePerformanceTests) {
        suites.push(await this.runPerformanceTestSuite());
      }

      if (this.config.enableSecurityTests) {
        suites.push(await this.runSecurityTestSuite());
      }

      // Calcular estatísticas
      const totalDuration = Date.now() - startTime;
      const allTests = suites.flatMap(suite => suite.tests);

      const summary = {
        totalTests: allTests.length,
        passedTests: allTests.filter(t => t.status === 'passed').length,
        failedTests: allTests.filter(t => t.status === 'failed').length,
        warningTests: allTests.filter(t => t.status === 'warning').length,
        totalDuration,
      };

      // Determinar status geral
      let overallStatus: PipelineReport['overallStatus'] = 'passed';
      const hasFailures = summary.failedTests > 0;
      const hasWarnings = summary.warningTests > 0;

      if (hasFailures) {
        overallStatus = 'failed';
      } else if (hasWarnings && this.config.failOnWarnings) {
        overallStatus = 'failed';
      } else if (hasWarnings) {
        overallStatus = 'warning';
      }

      // Gerar recomendações e blockers
      const { recommendations, blockers } = this.generateRecommendations(suites);
      const canDeploy = overallStatus !== 'failed' && blockers.length === 0;

      const report: PipelineReport = {
        overallStatus,
        suites,
        summary,
        recommendations,
        blockers,
        canDeploy,
        timestamp,
      };

      // Armazenar no histórico
      this.testHistory.push(report);
      this.cleanupHistory();

      // Log do resultado
      this.logPipelineResult(report);

      return report;
    } finally {
      this.isRunning = false;
    }
  }

  /**
   * Suite de testes visuais
   */
  private async runVisualTestSuite(): Promise<TestSuite> {
    const startTime = Date.now();
    const tests: TestResult[] = [];

    console.log('👁️ Executando testes visuais...');

    // Teste 1: Validação de renderização do dashboard
    tests.push(
      await this.runTest(
        'visual-dashboard-rendering',
        'Renderização do Dashboard',
        'visual',
        async () => {
          const result = await visualValidator.validateDashboardRendering();
          return {
            success: result.isValid,
            message: result.isValid
              ? 'Dashboard renderizado corretamente'
              : `Problemas: ${result.issues.join(', ')}`,
            details: result,
          };
        }
      )
    );

    // Teste 2: Validação de elementos visuais
    tests.push(
      await this.runTest(
        'visual-elements-validation',
        'Validação de Elementos Visuais',
        'visual',
        async () => {
          const cards = document.querySelectorAll(
            '[data-testid="metric-card"], .metric-card, [class*="card"]'
          );
          const visibleCards = Array.from(cards).filter(card => {
            const rect = card.getBoundingClientRect();
            return rect.width > 0 && rect.height > 0;
          });

          const success = visibleCards.length >= 4;
          return {
            success,
            message: success
              ? `${visibleCards.length} cards visíveis`
              : `Apenas ${visibleCards.length} cards visíveis (esperado: 4+)`,
            details: { totalCards: cards.length, visibleCards: visibleCards.length },
          };
        }
      )
    );

    // Teste 3: Validação de responsividade
    tests.push(
      await this.runTest('visual-responsiveness', 'Responsividade', 'visual', async () => {
        const viewport = {
          width: window.innerWidth,
          height: window.innerHeight,
        };

        const isMobile = viewport.width < 768;
        const isTablet = viewport.width >= 768 && viewport.width < 1024;
        const isDesktop = viewport.width >= 1024;

        // Verificar se layout se adapta ao viewport
        const container = document.querySelector(
          '.dashboard-container, [class*="dashboard"], main'
        );
        const containerWidth = container?.getBoundingClientRect().width || 0;

        const success = containerWidth <= viewport.width;
        return {
          success,
          message: success
            ? 'Layout responsivo funcionando'
            : 'Problemas de responsividade detectados',
          details: {
            viewport,
            containerWidth,
            deviceType: isMobile ? 'mobile' : isTablet ? 'tablet' : 'desktop',
          },
        };
      })
    );

    const duration = Date.now() - startTime;
    const failed = tests.filter(t => t.status === 'failed').length;
    const warnings = tests.filter(t => t.status === 'warning').length;

    return {
      id: 'visual-tests',
      name: 'Testes Visuais',
      description: 'Validação de renderização e elementos visuais',
      tests,
      status: failed > 0 ? 'failed' : warnings > 0 ? 'warning' : 'passed',
      duration,
      coverage: {
        total: tests.length,
        passed: tests.filter(t => t.status === 'passed').length,
        failed,
        warnings,
      },
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Suite de testes funcionais
   */
  private async runFunctionalTestSuite(): Promise<TestSuite> {
    const startTime = Date.now();
    const tests: TestResult[] = [];

    console.log('⚙️ Executando testes funcionais...');

    // Teste 1: Validação de métricas
    tests.push(
      await this.runTest(
        'functional-metrics-validation',
        'Validação de Métricas',
        'functional',
        async () => {
          const result = await MetricsValidator.validateCompleteFlow();
          return {
            success: result.success,
            message: result.message,
            details: result,
          };
        }
      )
    );

    // Teste 2: Conectividade da API
    tests.push(
      await this.runTest(
        'functional-api-connectivity',
        'Conectividade da API',
        'functional',
        async () => {
          try {
            const response = await fetch('/api/metrics');
            const success = response.ok;
            return {
              success,
              message: success
                ? `API acessível (${response.status})`
                : `API inacessível (${response.status})`,
              details: { status: response.status, statusText: response.statusText },
            };
          } catch (error) {
            return {
              success: false,
              message: `Erro de conectividade: ${error}`,
              details: { error: String(error) },
            };
          }
        }
      )
    );

    // Teste 3: Estrutura de dados da API
    tests.push(
      await this.runTest(
        'functional-api-data-structure',
        'Estrutura de Dados da API',
        'functional',
        async () => {
          try {
            const response = await fetch('/api/metrics');
            if (!response.ok) {
              return {
                success: false,
                message: 'API não acessível para verificação de estrutura',
                details: { status: response.status },
              };
            }

            const data = await response.json();
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

            const success = missingFields.length === 0;
            return {
              success,
              message: success
                ? 'Estrutura de dados válida'
                : `Campos ausentes: ${missingFields.join(', ')}`,
              details: { structure: data, missingFields },
            };
          } catch (error) {
            return {
              success: false,
              message: `Erro ao verificar estrutura: ${error}`,
              details: { error: String(error) },
            };
          }
        }
      )
    );

    // Teste 4: Processamento de dados no frontend
    tests.push(
      await this.runTest(
        'functional-frontend-data-processing',
        'Processamento de Dados no Frontend',
        'functional',
        async () => {
          const result = await MetricsValidator.validateFrontendDataProcessing({
            novos: 0,
            pendentes: 0,
            progresso: 0,
            resolvidos: 0,
          });
          return {
            success: result.success,
            message: result.message,
            details: result,
          };
        }
      )
    );

    const duration = Date.now() - startTime;
    const failed = tests.filter(t => t.status === 'failed').length;
    const warnings = tests.filter(t => t.status === 'warning').length;

    return {
      id: 'functional-tests',
      name: 'Testes Funcionais',
      description: 'Validação de funcionalidades e fluxos de dados',
      tests,
      status: failed > 0 ? 'failed' : warnings > 0 ? 'warning' : 'passed',
      duration,
      coverage: {
        total: tests.length,
        passed: tests.filter(t => t.status === 'passed').length,
        failed,
        warnings,
      },
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Suite de testes de integridade
   */
  private async runIntegrityTestSuite(): Promise<TestSuite> {
    const startTime = Date.now();
    const tests: TestResult[] = [];

    console.log('🔍 Executando testes de integridade...');

    // Executar verificações de integridade
    const integrityReport = await dataIntegrityMonitor.runIntegrityChecks();

    // Converter checks de integridade em testes
    integrityReport.checks.forEach(check => {
      tests.push({
        id: check.id,
        name: check.name,
        category: 'integrity',
        status: check.isValid ? 'passed' : check.severity === 'critical' ? 'failed' : 'warning',
        message: check.message,
        duration: 0, // Não medimos duração individual dos checks
        details: check.data,
        timestamp: check.timestamp,
      });
    });

    const duration = Date.now() - startTime;
    const failed = tests.filter(t => t.status === 'failed').length;
    const warnings = tests.filter(t => t.status === 'warning').length;

    return {
      id: 'integrity-tests',
      name: 'Testes de Integridade',
      description: 'Verificações de integridade de dados e consistência',
      tests,
      status: failed > 0 ? 'failed' : warnings > 0 ? 'warning' : 'passed',
      duration,
      coverage: {
        total: tests.length,
        passed: tests.filter(t => t.status === 'passed').length,
        failed,
        warnings,
      },
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Suite de testes de performance
   */
  private async runPerformanceTestSuite(): Promise<TestSuite> {
    const startTime = Date.now();
    const tests: TestResult[] = [];

    console.log('⚡ Executando testes de performance...');

    // Teste 1: Tempo de resposta da API
    tests.push(
      await this.runTest(
        'performance-api-response-time',
        'Tempo de Resposta da API',
        'performance',
        async () => {
          const start = Date.now();
          try {
            const response = await fetch('/api/metrics');
            const responseTime = Date.now() - start;
            const threshold = 2000; // 2 segundos

            const success = response.ok && responseTime < threshold;
            return {
              success,
              message: `Tempo de resposta: ${responseTime}ms (limite: ${threshold}ms)`,
              details: { responseTime, threshold, status: response.status },
            };
          } catch (error) {
            return {
              success: false,
              message: `Erro na requisição: ${error}`,
              details: { error: String(error) },
            };
          }
        }
      )
    );

    // Teste 2: Tempo de renderização
    tests.push(
      await this.runTest(
        'performance-render-time',
        'Tempo de Renderização',
        'performance',
        async () => {
          const start = Date.now();

          // Simular re-renderização forçando um reflow
          const cards = document.querySelectorAll(
            '[data-testid="metric-card"], .metric-card, [class*="card"]'
          );
          cards.forEach(card => {
            card.getBoundingClientRect(); // Força reflow
          });

          const renderTime = Date.now() - start;
          const threshold = 100; // 100ms

          const success = renderTime < threshold;
          return {
            success,
            message: `Tempo de renderização: ${renderTime}ms (limite: ${threshold}ms)`,
            details: { renderTime, threshold, elementsCount: cards.length },
          };
        }
      )
    );

    // Teste 3: Uso de memória (básico)
    tests.push(
      await this.runTest('performance-memory-usage', 'Uso de Memória', 'performance', async () => {
        if ('memory' in performance) {
          const memory = (performance as any).memory;
          const usedMB = Math.round(memory.usedJSHeapSize / 1024 / 1024);
          const limitMB = Math.round(memory.jsHeapSizeLimit / 1024 / 1024);
          const usagePercent = (usedMB / limitMB) * 100;

          const threshold = 80; // 80% do limite
          const success = usagePercent < threshold;

          return {
            success,
            message: `Uso de memória: ${usedMB}MB (${usagePercent.toFixed(1)}% do limite)`,
            details: { usedMB, limitMB, usagePercent, threshold },
          };
        } else {
          return {
            success: true,
            message: 'Informações de memória não disponíveis neste navegador',
            details: { available: false },
          };
        }
      })
    );

    const duration = Date.now() - startTime;
    const failed = tests.filter(t => t.status === 'failed').length;
    const warnings = tests.filter(t => t.status === 'warning').length;

    return {
      id: 'performance-tests',
      name: 'Testes de Performance',
      description: 'Validação de performance e responsividade',
      tests,
      status: failed > 0 ? 'failed' : warnings > 0 ? 'warning' : 'passed',
      duration,
      coverage: {
        total: tests.length,
        passed: tests.filter(t => t.status === 'passed').length,
        failed,
        warnings,
      },
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Suite de testes de segurança (básica)
   */
  private async runSecurityTestSuite(): Promise<TestSuite> {
    const startTime = Date.now();
    const tests: TestResult[] = [];

    console.log('🔒 Executando testes de segurança...');

    // Teste 1: Verificação de HTTPS (se aplicável)
    tests.push(
      await this.runTest('security-https-check', 'Verificação HTTPS', 'security', async () => {
        const isHttps = location.protocol === 'https:';
        const isLocalhost = location.hostname === 'localhost' || location.hostname === '127.0.0.1';

        // Em produção, HTTPS deve ser obrigatório
        const success = isHttps || isLocalhost || process.env.NODE_ENV === 'development';

        return {
          success,
          message: isHttps
            ? 'Conexão segura (HTTPS)'
            : isLocalhost
              ? 'Localhost (OK para desenvolvimento)'
              : 'Conexão insegura (HTTP)',
          details: { protocol: location.protocol, hostname: location.hostname },
        };
      })
    );

    // Teste 2: Verificação de cabeçalhos de segurança (básico)
    tests.push(
      await this.runTest(
        'security-headers-check',
        'Cabeçalhos de Segurança',
        'security',
        async () => {
          try {
            const response = await fetch('/api/metrics');
            const headers = response.headers;

            const securityHeaders = {
              'x-content-type-options': headers.get('x-content-type-options'),
              'x-frame-options': headers.get('x-frame-options'),
              'x-xss-protection': headers.get('x-xss-protection'),
            };

            const presentHeaders = Object.entries(securityHeaders).filter(
              ([_, value]) => value !== null
            );
            const success = presentHeaders.length > 0;

            return {
              success,
              message: success
                ? `${presentHeaders.length} cabeçalhos de segurança encontrados`
                : 'Nenhum cabeçalho de segurança encontrado',
              details: securityHeaders,
            };
          } catch (error) {
            return {
              success: false,
              message: `Erro ao verificar cabeçalhos: ${error}`,
              details: { error: String(error) },
            };
          }
        }
      )
    );

    const duration = Date.now() - startTime;
    const failed = tests.filter(t => t.status === 'failed').length;
    const warnings = tests.filter(t => t.status === 'warning').length;

    return {
      id: 'security-tests',
      name: 'Testes de Segurança',
      description: 'Verificações básicas de segurança',
      tests,
      status: failed > 0 ? 'failed' : warnings > 0 ? 'warning' : 'passed',
      duration,
      coverage: {
        total: tests.length,
        passed: tests.filter(t => t.status === 'passed').length,
        failed,
        warnings,
      },
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Executa um teste individual com retry e timeout
   */
  private async runTest(
    id: string,
    name: string,
    category: TestResult['category'],
    testFunction: () => Promise<{ success: boolean; message: string; details?: any }>
  ): Promise<TestResult> {
    const startTime = Date.now();
    let attempt = 0;
    let lastError: any = null;

    while (attempt <= this.config.maxRetries) {
      try {
        // Timeout para o teste
        const timeoutPromise = new Promise((_, reject) => {
          setTimeout(() => reject(new Error('Timeout do teste')), this.config.maxTestDuration);
        });

        const testPromise = testFunction();
        const result = (await Promise.race([testPromise, timeoutPromise])) as {
          success: boolean;
          message: string;
          details?: any;
        };

        const duration = Date.now() - startTime;

        return {
          id,
          name,
          category,
          status: result.success ? 'passed' : 'failed',
          message: result.message,
          duration,
          details: result.details,
          timestamp: new Date().toISOString(),
        };
      } catch (error) {
        lastError = error;
        attempt++;

        if (attempt <= this.config.maxRetries && this.config.retryFailedTests) {
          console.warn(`⚠️ Teste ${name} falhou (tentativa ${attempt}), tentando novamente...`);
          await new Promise(resolve => setTimeout(resolve, 1000)); // Aguardar 1s antes de retry
        }
      }
    }

    // Se chegou aqui, todas as tentativas falharam
    const duration = Date.now() - startTime;
    return {
      id,
      name,
      category,
      status: 'failed',
      message: `Teste falhou após ${this.config.maxRetries + 1} tentativas: ${lastError}`,
      duration,
      details: { error: String(lastError), attempts: attempt },
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Gera recomendações e blockers baseados nos resultados
   */
  private generateRecommendations(suites: TestSuite[]): {
    recommendations: string[];
    blockers: string[];
  } {
    const recommendations: string[] = [];
    const blockers: string[] = [];

    suites.forEach(suite => {
      const failedTests = suite.tests.filter(t => t.status === 'failed');
      const warningTests = suite.tests.filter(t => t.status === 'warning');

      failedTests.forEach(test => {
        switch (test.category) {
          case 'visual':
            if (test.id.includes('rendering')) {
              blockers.push('Problemas críticos de renderização detectados');
              recommendations.push('Verificar componentes do dashboard e CSS');
            }
            break;
          case 'functional':
            if (test.id.includes('api')) {
              blockers.push('API não está funcionando corretamente');
              recommendations.push('Verificar se o backend está rodando e acessível');
            }
            if (test.id.includes('metrics')) {
              blockers.push('Validação de métricas falhou');
              recommendations.push('Verificar fluxo de dados entre API e frontend');
            }
            break;
          case 'integrity':
            if (test.name.includes('Conectividade')) {
              blockers.push('Conectividade com API comprometida');
            }
            if (test.name.includes('Métricas Zeradas')) {
              recommendations.push('Investigar por que métricas estão zeradas');
            }
            break;
          case 'performance':
            if (test.id.includes('response-time')) {
              recommendations.push('Otimizar performance da API');
            }
            if (test.id.includes('memory')) {
              recommendations.push('Verificar vazamentos de memória');
            }
            break;
        }
      });

      warningTests.forEach(test => {
        recommendations.push(`Atenção: ${test.message}`);
      });
    });

    // Recomendações gerais
    const totalFailures = suites.reduce((sum, suite) => sum + suite.coverage.failed, 0);
    if (totalFailures > 5) {
      recommendations.push('Múltiplas falhas detectadas - considerar revisão completa do sistema');
    }

    return {
      recommendations: [...new Set(recommendations)],
      blockers: [...new Set(blockers)],
    };
  }

  /**
   * Log do resultado do pipeline
   */
  private logPipelineResult(report: PipelineReport): void {
    const statusEmoji = {
      passed: '✅',
      failed: '❌',
      warning: '⚠️',
    };

    console.log(`\n${statusEmoji[report.overallStatus]} RESULTADO DO PIPELINE DE TESTES`);
    console.log(`Status: ${report.overallStatus.toUpperCase()}`);
    console.log(`Duração total: ${report.summary.totalDuration}ms`);
    console.log(`Testes: ${report.summary.passedTests}/${report.summary.totalTests} passaram`);

    if (report.summary.failedTests > 0) {
      console.log(`❌ Falhas: ${report.summary.failedTests}`);
    }

    if (report.summary.warningTests > 0) {
      console.log(`⚠️ Avisos: ${report.summary.warningTests}`);
    }

    console.log(`🚀 Pode fazer deploy: ${report.canDeploy ? 'SIM' : 'NÃO'}`);

    if (report.blockers.length > 0) {
      console.log('\n🚫 BLOCKERS:');
      report.blockers.forEach(blocker => console.log(`  - ${blocker}`));
    }

    if (report.recommendations.length > 0) {
      console.log('\n💡 RECOMENDAÇÕES:');
      report.recommendations.forEach(rec => console.log(`  - ${rec}`));
    }

    // Log detalhado por suite
    report.suites.forEach(suite => {
      console.log(
        `\n📋 ${suite.name}: ${statusEmoji[suite.status]} (${suite.coverage.passed}/${suite.coverage.total})`
      );

      const failedTests = suite.tests.filter(t => t.status === 'failed');
      if (failedTests.length > 0) {
        failedTests.forEach(test => {
          console.log(`  ❌ ${test.name}: ${test.message}`);
        });
      }
    });
  }

  /**
   * Limpa histórico antigo
   */
  private cleanupHistory(): void {
    const maxHistory = 50;
    if (this.testHistory.length > maxHistory) {
      this.testHistory = this.testHistory.slice(-maxHistory);
    }
  }

  /**
   * Configura o pipeline
   */
  configure(config: Partial<PipelineConfig>): void {
    this.config = { ...this.config, ...config };
  }

  /**
   * Obtém histórico de execuções
   */
  getHistory(): PipelineReport[] {
    return [...this.testHistory];
  }

  /**
   * Verifica se pode fazer deploy
   */
  async canDeploy(): Promise<boolean> {
    const report = await this.runPipeline();
    return report.canDeploy;
  }

  /**
   * Execução rápida (apenas testes críticos)
   */
  async runQuickValidation(): Promise<PipelineReport> {
    const originalConfig = { ...this.config };

    // Configuração para validação rápida
    this.configure({
      enableVisualTests: true,
      enableFunctionalTests: true,
      enableIntegrityTests: false,
      enablePerformanceTests: false,
      enableSecurityTests: false,
      retryFailedTests: false,
    });

    try {
      const report = await this.runPipeline();
      return report;
    } finally {
      // Restaurar configuração original
      this.config = originalConfig;
    }
  }
}

// Instância global do pipeline
export const automatedTestPipeline = new AutomatedTestPipeline();

// Funções utilitárias para uso no console
(window as any).runTestPipeline = () => automatedTestPipeline.runPipeline();
(window as any).runQuickValidation = () => automatedTestPipeline.runQuickValidation();
(window as any).canDeploy = () => automatedTestPipeline.canDeploy();
(window as any).getTestHistory = () => automatedTestPipeline.getHistory();

export default AutomatedTestPipeline;
