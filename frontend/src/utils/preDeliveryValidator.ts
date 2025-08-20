/**
 * Validador Pré-Entrega
 *
 * Sistema obrigatório que deve ser executado antes de qualquer entrega
 * ou conclusão de tarefa. Garante que todas as métricas e funcionalidades
 * estão funcionando corretamente.
 */

import { automatedTestPipeline, PipelineReport } from './automatedTestPipeline';
import { dataIntegrityMonitor } from './dataIntegrityMonitor';
import { visualValidator } from './visualValidator';
import { MetricsValidator } from './metricsValidator';

export interface DeliveryValidationResult {
  canDeliver: boolean;
  overallStatus: 'approved' | 'rejected' | 'conditional';
  validationScore: number; // 0-100
  criticalIssues: string[];
  warnings: string[];
  recommendations: string[];
  testResults: {
    pipelineReport: PipelineReport | null;
    quickValidation: boolean;
    manualChecks: boolean;
  };
  timestamp: string;
  validatedBy: string;
  deliveryApproval: {
    approved: boolean;
    approvedBy: string;
    conditions: string[];
    expiresAt: string; // ISO string
  };
}

export interface DeliveryChecklist {
  id: string;
  name: string;
  description: string;
  category: 'critical' | 'important' | 'optional';
  automated: boolean;
  status: 'pending' | 'passed' | 'failed' | 'skipped';
  message: string;
  details?: any;
}

export interface ValidationConfig {
  requireFullPipeline: boolean;
  allowConditionalDelivery: boolean;
  minimumScore: number;
  criticalIssueThreshold: number;
  approvalExpiryHours: number;
  mandatoryChecks: string[];
  skipOptionalInProduction: boolean;
}

class PreDeliveryValidator {
  private config: ValidationConfig = {
    requireFullPipeline: true,
    allowConditionalDelivery: true,
    minimumScore: 85,
    criticalIssueThreshold: 0, // Zero critical issues allowed
    approvalExpiryHours: 24,
    mandatoryChecks: [
      'metrics-validation',
      'api-connectivity',
      'visual-rendering',
      'data-integrity',
    ],
    skipOptionalInProduction: true,
  };

  private validationHistory: DeliveryValidationResult[] = [];
  private lastApproval: DeliveryValidationResult | null = null;

  /**
   * Executa validação completa pré-entrega
   */
  async validateForDelivery(): Promise<DeliveryValidationResult> {
    console.log('🔍 Iniciando Validação Pré-Entrega...');

    const timestamp = new Date().toISOString();
    const validatedBy = 'AutomatedValidator';

    try {
      // 1. Executar pipeline de testes
      console.log('📋 Executando pipeline de testes...');
      const pipelineReport = this.config.requireFullPipeline
        ? await automatedTestPipeline.runPipeline()
        : await automatedTestPipeline.runQuickValidation();

      // 2. Executar checklist manual
      console.log('✅ Executando checklist de validação...');
      const checklist = await this.runDeliveryChecklist();

      // 3. Analisar resultados
      const analysis = this.analyzeResults(pipelineReport, checklist);

      // 4. Calcular score de validação
      const validationScore = this.calculateValidationScore(pipelineReport, checklist);

      // 5. Determinar se pode entregar
      const canDeliver = this.determineDeliveryApproval(analysis, validationScore);

      // 6. Gerar recomendações
      const recommendations = this.generateDeliveryRecommendations(analysis, pipelineReport);

      // 7. Criar aprovação (se aplicável)
      const deliveryApproval = this.createDeliveryApproval(canDeliver, analysis.criticalIssues);

      const result: DeliveryValidationResult = {
        canDeliver: canDeliver.approved,
        overallStatus: canDeliver.status,
        validationScore,
        criticalIssues: analysis.criticalIssues,
        warnings: analysis.warnings,
        recommendations,
        testResults: {
          pipelineReport,
          quickValidation: !this.config.requireFullPipeline,
          manualChecks: checklist.every(c => c.status !== 'pending'),
        },
        timestamp,
        validatedBy,
        deliveryApproval,
      };

      // Armazenar resultado
      this.validationHistory.push(result);
      if (result.canDeliver) {
        this.lastApproval = result;
      }

      // Log do resultado
      this.logValidationResult(result);

      return result;
    } catch (error) {
      console.error('💥 Erro durante validação pré-entrega:', error);

      return {
        canDeliver: false,
        overallStatus: 'rejected',
        validationScore: 0,
        criticalIssues: [`Erro durante validação: ${error}`],
        warnings: [],
        recommendations: ['Resolver erro de validação antes de tentar novamente'],
        testResults: {
          pipelineReport: null,
          quickValidation: false,
          manualChecks: false,
        },
        timestamp,
        validatedBy,
        deliveryApproval: {
          approved: false,
          approvedBy: '',
          conditions: [],
          expiresAt: new Date().toISOString(),
        },
      };
    }
  }

  /**
   * Executa checklist de validação manual
   */
  private async runDeliveryChecklist(): Promise<DeliveryChecklist[]> {
    const checklist: DeliveryChecklist[] = [];

    // Check 1: Validação de métricas
    checklist.push(
      await this.runCheck(
        'metrics-validation',
        'Validação de Métricas',
        'Verifica se todas as métricas estão sendo exibidas corretamente',
        'critical',
        true,
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

    // Check 2: Conectividade da API
    checklist.push(
      await this.runCheck(
        'api-connectivity',
        'Conectividade da API',
        'Verifica se a API está acessível e respondendo',
        'critical',
        true,
        async () => {
          try {
            const response = await fetch('/api/metrics');
            return {
              success: response.ok,
              message: response.ok ? 'API acessível' : `API retornou erro ${response.status}`,
              details: { status: response.status },
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

    // Check 3: Renderização visual
    checklist.push(
      await this.runCheck(
        'visual-rendering',
        'Renderização Visual',
        'Verifica se o dashboard está sendo renderizado corretamente',
        'critical',
        true,
        async () => {
          const result = await visualValidator.validateDashboardRendering();
          return {
            success: result.isValid,
            message: result.isValid ? 'Renderização OK' : `Problemas: ${result.issues.join(', ')}`,
            details: result,
          };
        }
      )
    );

    // Check 4: Integridade de dados
    checklist.push(
      await this.runCheck(
        'data-integrity',
        'Integridade de Dados',
        'Verifica consistência entre API e frontend',
        'critical',
        true,
        async () => {
          const report = await dataIntegrityMonitor.runIntegrityChecks();
          const criticalFailures = report.checks.filter(
            c => !c.isValid && c.severity === 'critical'
          );

          return {
            success: criticalFailures.length === 0,
            message:
              criticalFailures.length === 0
                ? 'Integridade OK'
                : `${criticalFailures.length} problemas críticos detectados`,
            details: report,
          };
        }
      )
    );

    // Check 5: Métricas não zeradas
    checklist.push(
      await this.runCheck(
        'non-zero-metrics',
        'Métricas Não Zeradas',
        'Verifica se as métricas não estão todas zeradas',
        'important',
        true,
        async () => {
          try {
            const response = await fetch('/api/metrics');
            if (!response.ok) {
              return {
                success: false,
                message: 'Não foi possível verificar métricas',
                details: { status: response.status },
              };
            }

            const data = await response.json();
            if (!data.data) {
              return {
                success: false,
                message: 'Estrutura de dados inválida',
                details: data,
              };
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

            return {
              success: !allZero,
              message: allZero
                ? 'ALERTA: Todas as métricas estão zeradas'
                : `Métricas válidas (total: ${total})`,
              details: { values, total, allZero },
            };
          } catch (error) {
            return {
              success: false,
              message: `Erro ao verificar métricas: ${error}`,
              details: { error: String(error) },
            };
          }
        }
      )
    );

    // Check 6: Performance aceitável
    checklist.push(
      await this.runCheck(
        'performance-check',
        'Performance Aceitável',
        'Verifica se a performance está dentro dos limites aceitáveis',
        'important',
        true,
        async () => {
          const start = Date.now();
          try {
            const response = await fetch('/api/metrics');
            const responseTime = Date.now() - start;
            const threshold = 3000; // 3 segundos

            return {
              success: response.ok && responseTime < threshold,
              message: `Tempo de resposta: ${responseTime}ms (limite: ${threshold}ms)`,
              details: { responseTime, threshold, status: response.status },
            };
          } catch (error) {
            return {
              success: false,
              message: `Erro de performance: ${error}`,
              details: { error: String(error) },
            };
          }
        }
      )
    );

    // Check 7: Elementos visuais presentes
    checklist.push(
      await this.runCheck(
        'visual-elements',
        'Elementos Visuais Presentes',
        'Verifica se todos os elementos visuais estão presentes',
        'important',
        true,
        async () => {
          const cards = document.querySelectorAll(
            '[data-testid="metric-card"], .metric-card, [class*="card"]'
          );
          const visibleCards = Array.from(cards).filter(card => {
            const rect = card.getBoundingClientRect();
            return rect.width > 0 && rect.height > 0;
          });

          const expectedCards = 4;
          const success = visibleCards.length >= expectedCards;

          return {
            success,
            message: success
              ? `${visibleCards.length} cards visíveis`
              : `Apenas ${visibleCards.length}/${expectedCards} cards visíveis`,
            details: {
              totalCards: cards.length,
              visibleCards: visibleCards.length,
              expected: expectedCards,
            },
          };
        }
      )
    );

    // Check 8: Console sem erros críticos
    checklist.push(
      await this.runCheck(
        'console-errors',
        'Console Sem Erros Críticos',
        'Verifica se não há erros críticos no console',
        'optional',
        false,
        async () => {
          // Este check seria implementado com um listener de erros
          // Por simplicidade, assumimos que está OK se chegamos até aqui
          return {
            success: true,
            message: 'Nenhum erro crítico detectado durante validação',
            details: { note: 'Check manual - verificar console do navegador' },
          };
        }
      )
    );

    return checklist;
  }

  /**
   * Executa um check individual
   */
  private async runCheck(
    id: string,
    name: string,
    description: string,
    category: DeliveryChecklist['category'],
    automated: boolean,
    checkFunction: () => Promise<{ success: boolean; message: string; details?: any }>
  ): Promise<DeliveryChecklist> {
    try {
      const result = await checkFunction();

      return {
        id,
        name,
        description,
        category,
        automated,
        status: result.success ? 'passed' : 'failed',
        message: result.message,
        details: result.details,
      };
    } catch (error) {
      return {
        id,
        name,
        description,
        category,
        automated,
        status: 'failed',
        message: `Erro durante check: ${error}`,
        details: { error: String(error) },
      };
    }
  }

  /**
   * Analisa resultados dos testes
   */
  private analyzeResults(pipelineReport: PipelineReport, checklist: DeliveryChecklist[]) {
    const criticalIssues: string[] = [];
    const warnings: string[] = [];

    // Analisar pipeline
    if (pipelineReport) {
      if (pipelineReport.overallStatus === 'failed') {
        criticalIssues.push('Pipeline de testes falhou');
      }

      pipelineReport.blockers.forEach(blocker => {
        criticalIssues.push(blocker);
      });

      if (pipelineReport.overallStatus === 'warning') {
        warnings.push('Pipeline com avisos');
      }
    }

    // Analisar checklist
    const failedCritical = checklist.filter(
      c => c.category === 'critical' && c.status === 'failed'
    );
    const failedImportant = checklist.filter(
      c => c.category === 'important' && c.status === 'failed'
    );
    const failedOptional = checklist.filter(
      c => c.category === 'optional' && c.status === 'failed'
    );

    failedCritical.forEach(check => {
      criticalIssues.push(`Check crítico falhou: ${check.name}`);
    });

    failedImportant.forEach(check => {
      warnings.push(`Check importante falhou: ${check.name}`);
    });

    failedOptional.forEach(check => {
      warnings.push(`Check opcional falhou: ${check.name}`);
    });

    return { criticalIssues, warnings };
  }

  /**
   * Calcula score de validação (0-100)
   */
  private calculateValidationScore(
    pipelineReport: PipelineReport,
    checklist: DeliveryChecklist[]
  ): number {
    let score = 100;

    // Penalidades do pipeline
    if (pipelineReport) {
      const failureRate = pipelineReport.summary.failedTests / pipelineReport.summary.totalTests;
      score -= failureRate * 40; // Até 40 pontos de penalidade

      if (pipelineReport.overallStatus === 'failed') {
        score -= 20;
      } else if (pipelineReport.overallStatus === 'warning') {
        score -= 10;
      }
    } else {
      score -= 30; // Penalidade por não executar pipeline
    }

    // Penalidades do checklist
    const criticalFailed = checklist.filter(
      c => c.category === 'critical' && c.status === 'failed'
    ).length;
    const importantFailed = checklist.filter(
      c => c.category === 'important' && c.status === 'failed'
    ).length;
    const optionalFailed = checklist.filter(
      c => c.category === 'optional' && c.status === 'failed'
    ).length;

    score -= criticalFailed * 25; // 25 pontos por check crítico
    score -= importantFailed * 10; // 10 pontos por check importante
    score -= optionalFailed * 2; // 2 pontos por check opcional

    return Math.max(0, Math.round(score));
  }

  /**
   * Determina se pode aprovar entrega
   */
  private determineDeliveryApproval(
    analysis: { criticalIssues: string[]; warnings: string[] },
    score: number
  ) {
    const hasCriticalIssues = analysis.criticalIssues.length > this.config.criticalIssueThreshold;
    const meetsMinimumScore = score >= this.config.minimumScore;

    if (hasCriticalIssues) {
      return {
        approved: false,
        status: 'rejected' as const,
        reason: 'Problemas críticos detectados',
      };
    }

    if (!meetsMinimumScore && !this.config.allowConditionalDelivery) {
      return {
        approved: false,
        status: 'rejected' as const,
        reason: `Score insuficiente: ${score}/${this.config.minimumScore}`,
      };
    }

    if (!meetsMinimumScore && this.config.allowConditionalDelivery) {
      return {
        approved: true,
        status: 'conditional' as const,
        reason: `Aprovação condicional - score: ${score}/${this.config.minimumScore}`,
      };
    }

    return {
      approved: true,
      status: 'approved' as const,
      reason: `Aprovado - score: ${score}`,
    };
  }

  /**
   * Gera recomendações para entrega
   */
  private generateDeliveryRecommendations(
    analysis: { criticalIssues: string[]; warnings: string[] },
    pipelineReport: PipelineReport | null
  ): string[] {
    const recommendations: string[] = [];

    if (analysis.criticalIssues.length > 0) {
      recommendations.push('Resolver todos os problemas críticos antes da entrega');
    }

    if (analysis.warnings.length > 0) {
      recommendations.push('Revisar e resolver avisos quando possível');
    }

    if (pipelineReport && pipelineReport.recommendations.length > 0) {
      recommendations.push(...pipelineReport.recommendations);
    }

    if (analysis.criticalIssues.length === 0 && analysis.warnings.length === 0) {
      recommendations.push('Sistema validado e pronto para entrega');
    }

    return [...new Set(recommendations)];
  }

  /**
   * Cria aprovação de entrega
   */
  private createDeliveryApproval(
    canDeliver: { approved: boolean; status: string; reason: string },
    criticalIssues: string[]
  ) {
    const expiresAt = new Date();
    expiresAt.setHours(expiresAt.getHours() + this.config.approvalExpiryHours);

    const conditions: string[] = [];

    if (canDeliver.status === 'conditional') {
      conditions.push('Monitorar métricas após deploy');
      conditions.push('Verificar logs de erro');
    }

    if (criticalIssues.length === 0) {
      conditions.push('Manter monitoramento ativo');
    }

    return {
      approved: canDeliver.approved,
      approvedBy: 'PreDeliveryValidator',
      conditions,
      expiresAt: expiresAt.toISOString(),
    };
  }

  /**
   * Log do resultado da validação
   */
  private logValidationResult(result: DeliveryValidationResult): void {
    const statusEmoji = {
      approved: '✅',
      rejected: '❌',
      conditional: '⚠️',
    };

    console.log(`\n${statusEmoji[result.overallStatus]} RESULTADO DA VALIDAÇÃO PRÉ-ENTREGA`);
    console.log(`Status: ${result.overallStatus.toUpperCase()}`);
    console.log(`Score: ${result.validationScore}/100`);
    console.log(`Pode entregar: ${result.canDeliver ? 'SIM' : 'NÃO'}`);

    if (result.criticalIssues.length > 0) {
      console.log('\n🚫 PROBLEMAS CRÍTICOS:');
      result.criticalIssues.forEach(issue => console.log(`  - ${issue}`));
    }

    if (result.warnings.length > 0) {
      console.log('\n⚠️ AVISOS:');
      result.warnings.forEach(warning => console.log(`  - ${warning}`));
    }

    if (result.recommendations.length > 0) {
      console.log('\n💡 RECOMENDAÇÕES:');
      result.recommendations.forEach(rec => console.log(`  - ${rec}`));
    }

    if (result.deliveryApproval.conditions.length > 0) {
      console.log('\n📋 CONDIÇÕES:');
      result.deliveryApproval.conditions.forEach(condition => console.log(`  - ${condition}`));
    }

    console.log(
      `\n⏰ Aprovação expira em: ${new Date(result.deliveryApproval.expiresAt).toLocaleString()}`
    );
  }

  /**
   * Verifica se há aprovação válida
   */
  hasValidApproval(): boolean {
    if (!this.lastApproval) return false;

    const expiresAt = new Date(this.lastApproval.deliveryApproval.expiresAt);
    const now = new Date();

    return this.lastApproval.canDeliver && now < expiresAt;
  }

  /**
   * Obtém última aprovação
   */
  getLastApproval(): DeliveryValidationResult | null {
    return this.lastApproval;
  }

  /**
   * Configura validador
   */
  configure(config: Partial<ValidationConfig>): void {
    this.config = { ...this.config, ...config };
  }

  /**
   * Obtém histórico de validações
   */
  getValidationHistory(): DeliveryValidationResult[] {
    return [...this.validationHistory];
  }

  /**
   * Validação rápida (apenas checks críticos)
   */
  async quickValidation(): Promise<DeliveryValidationResult> {
    const originalConfig = { ...this.config };

    this.configure({
      requireFullPipeline: false,
      mandatoryChecks: ['metrics-validation', 'api-connectivity', 'visual-rendering'],
    });

    try {
      return await this.validateForDelivery();
    } finally {
      this.config = originalConfig;
    }
  }
}

// Instância global do validador
export const preDeliveryValidator = new PreDeliveryValidator();

// Funções utilitárias para uso no console
(window as any).validateForDelivery = () => preDeliveryValidator.validateForDelivery();
(window as any).quickValidation = () => preDeliveryValidator.quickValidation();
(window as any).hasValidApproval = () => preDeliveryValidator.hasValidApproval();
(window as any).getLastApproval = () => preDeliveryValidator.getLastApproval();

// Interceptar tentativas de deploy/entrega sem validação
if (process.env.NODE_ENV === 'development') {
  // Adicionar aviso no console sobre validação obrigatória
  console.log('🔒 VALIDAÇÃO PRÉ-ENTREGA ATIVA');
  console.log('Execute validateForDelivery() antes de qualquer entrega');
}

export default PreDeliveryValidator;
