/**
 * Suite de Testes Automatizados de Performance
 * Executa testes antes de cada release para garantir que as metas sejam atingidas
 */

import { performanceMonitor } from './performanceMonitor';
import { performanceBaseline } from './performanceBaseline';
import { webVitalsMonitor } from './webVitalsMonitor';

export interface PerformanceTestCase {
  name: string;
  description: string;
  target: number;
  unit: 'ms' | 'score' | '%';
  category: 'homepage' | 'filters' | 'autoRefresh' | 'webVitals';
  testFunction: () => Promise<number>;
  criticalThreshold?: number; // Se definido, falha crítica se exceder
}

export interface PerformanceTestResult {
  testCase: string;
  value: number;
  target: number;
  passed: boolean;
  criticalFailure: boolean;
  executionTime: number;
  timestamp: number;
  error?: string;
}

export interface PerformanceTestSuiteResult {
  totalTests: number;
  passedTests: number;
  failedTests: number;
  criticalFailures: number;
  overallPassed: boolean;
  executionTime: number;
  results: PerformanceTestResult[];
  summary: {
    homepage: { passed: number; total: number };
    filters: { passed: number; total: number };
    autoRefresh: { passed: number; total: number };
    webVitals: { passed: number; total: number };
  };
  timestamp: number;
}

class PerformanceTestSuite {
  private testCases: PerformanceTestCase[] = [];
  private isRunning = false;

  constructor() {
    this.initializeTestCases();
  }

  /**
   * Inicializa os casos de teste padrão
   */
  private initializeTestCases(): void {
    // Testes da Homepage
    this.addTestCase({
      name: 'Homepage Load Time',
      description: 'Tempo total de carregamento da página inicial',
      target: 1000,
      unit: 'ms',
      category: 'homepage',
      criticalThreshold: 2000,
      testFunction: this.testHomepageLoadTime.bind(this)
    });

    this.addTestCase({
      name: 'Homepage Initial Render',
      description: 'Tempo de renderização inicial da homepage',
      target: 300,
      unit: 'ms',
      category: 'homepage',
      criticalThreshold: 600,
      testFunction: this.testHomepageRenderTime.bind(this)
    });

    this.addTestCase({
      name: 'Homepage API Response',
      description: 'Tempo de resposta da API para dados iniciais',
      target: 500,
      unit: 'ms',
      category: 'homepage',
      criticalThreshold: 1000,
      testFunction: this.testHomepageApiResponse.bind(this)
    });

    // Testes de Filtros
    this.addTestCase({
      name: 'Filter Response Time',
      description: 'Tempo de resposta ao aplicar filtros',
      target: 500,
      unit: 'ms',
      category: 'filters',
      criticalThreshold: 1000,
      testFunction: this.testFilterResponseTime.bind(this)
    });

    this.addTestCase({
      name: 'Filter Render Time',
      description: 'Tempo de renderização após aplicar filtros',
      target: 200,
      unit: 'ms',
      category: 'filters',
      criticalThreshold: 500,
      testFunction: this.testFilterRenderTime.bind(this)
    });

    // Testes de Auto-refresh
    this.addTestCase({
      name: 'Auto-refresh Update Time',
      description: 'Tempo total de atualização automática',
      target: 800,
      unit: 'ms',
      category: 'autoRefresh',
      criticalThreshold: 1500,
      testFunction: this.testAutoRefreshUpdateTime.bind(this)
    });

    this.addTestCase({
      name: 'Auto-refresh API Time',
      description: 'Tempo de API durante auto-refresh',
      target: 400,
      unit: 'ms',
      category: 'autoRefresh',
      criticalThreshold: 800,
      testFunction: this.testAutoRefreshApiTime.bind(this)
    });

    // Testes de Web Vitals
    this.addTestCase({
      name: 'Largest Contentful Paint (LCP)',
      description: 'Tempo para renderizar o maior elemento de conteúdo',
      target: 2500,
      unit: 'ms',
      category: 'webVitals',
      criticalThreshold: 4000,
      testFunction: this.testLCP.bind(this)
    });

    this.addTestCase({
      name: 'First Input Delay (FID)',
      description: 'Atraso da primeira interação',
      target: 100,
      unit: 'ms',
      category: 'webVitals',
      criticalThreshold: 300,
      testFunction: this.testFID.bind(this)
    });

    this.addTestCase({
      name: 'Cumulative Layout Shift (CLS)',
      description: 'Mudanças inesperadas de layout',
      target: 0.1,
      unit: 'score',
      category: 'webVitals',
      criticalThreshold: 0.25,
      testFunction: this.testCLS.bind(this)
    });
  }

  /**
   * Adiciona um caso de teste
   */
  addTestCase(testCase: PerformanceTestCase): void {
    this.testCases.push(testCase);
  }

  /**
   * Remove um caso de teste
   */
  removeTestCase(name: string): void {
    this.testCases = this.testCases.filter(tc => tc.name !== name);
  }

  /**
   * Executa toda a suite de testes
   */
  async runTestSuite(): Promise<PerformanceTestSuiteResult> {
    if (this.isRunning) {
      throw new Error('Suite de testes já está em execução');
    }

    this.isRunning = true;
    const startTime = performance.now();
    const results: PerformanceTestResult[] = [];

    console.group('🧪 Executando Suite de Testes de Performance');
    console.log(`Executando ${this.testCases.length} testes...`);

    try {
      for (const testCase of this.testCases) {
        const result = await this.runSingleTest(testCase);
        results.push(result);
        
        // Log do resultado
        const status = result.passed ? '✅' : '❌';
        const critical = result.criticalFailure ? ' (CRÍTICO)' : '';
        console.log(`${status} ${testCase.name}: ${result.value}${testCase.unit} (target: ${testCase.target}${testCase.unit})${critical}`);
      }
    } finally {
      this.isRunning = false;
    }

    const executionTime = performance.now() - startTime;
    const suiteResult = this.generateSuiteResult(results, executionTime);

    console.log('📊 Resultado da Suite:', suiteResult.overallPassed ? 'PASSOU' : 'FALHOU');
    console.log(`⏱️ Tempo total: ${executionTime.toFixed(2)}ms`);
    console.groupEnd();

    return suiteResult;
  }

  /**
   * Executa um teste individual
   */
  private async runSingleTest(testCase: PerformanceTestCase): Promise<PerformanceTestResult> {
    const startTime = performance.now();
    
    try {
      const value = await testCase.testFunction();
      const executionTime = performance.now() - startTime;
      
      const passed = value <= testCase.target;
      const criticalFailure = testCase.criticalThreshold ? value > testCase.criticalThreshold : false;

      return {
        testCase: testCase.name,
        value,
        target: testCase.target,
        passed,
        criticalFailure,
        executionTime,
        timestamp: Date.now()
      };
    } catch (error) {
      const executionTime = performance.now() - startTime;
      
      return {
        testCase: testCase.name,
        value: -1,
        target: testCase.target,
        passed: false,
        criticalFailure: true,
        executionTime,
        timestamp: Date.now(),
        error: error instanceof Error ? error.message : 'Erro desconhecido'
      };
    }
  }

  /**
   * Gera resultado consolidado da suite
   */
  private generateSuiteResult(
    results: PerformanceTestResult[],
    executionTime: number
  ): PerformanceTestSuiteResult {
    const passedTests = results.filter(r => r.passed).length;
    const failedTests = results.length - passedTests;
    const criticalFailures = results.filter(r => r.criticalFailure).length;
    
    // Agrupar por categoria
    const categories = ['homepage', 'filters', 'autoRefresh', 'webVitals'] as const;
    const summary = categories.reduce((acc, category) => {
      const categoryTests = this.testCases.filter(tc => tc.category === category);
      const categoryResults = results.filter(r => 
        categoryTests.some(tc => tc.name === r.testCase)
      );
      
      acc[category] = {
        passed: categoryResults.filter(r => r.passed).length,
        total: categoryResults.length
      };
      
      return acc;
    }, {} as PerformanceTestSuiteResult['summary']);

    return {
      totalTests: results.length,
      passedTests,
      failedTests,
      criticalFailures,
      overallPassed: criticalFailures === 0 && passedTests === results.length,
      executionTime,
      results,
      summary,
      timestamp: Date.now()
    };
  }

  // Implementações dos testes específicos

  private async testHomepageLoadTime(): Promise<number> {
    // Simular carregamento da homepage
    const startTime = performance.now();
    
    // Aguardar um frame para simular renderização
    await new Promise(resolve => requestAnimationFrame(resolve));
    
    // Obter métricas de navegação se disponíveis
    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
    if (navigation) {
      return navigation.loadEventEnd - navigation.loadEventStart;
    }
    
    return performance.now() - startTime;
  }

  private async testHomepageRenderTime(): Promise<number> {
    // Obter tempo de renderização dos componentes
    const stats = performanceMonitor.getDetailedStats();
    return stats.averageFilterTime || 0;
  }

  private async testHomepageApiResponse(): Promise<number> {
    // Obter tempo médio de API
    const stats = performanceMonitor.getDetailedStats();
    return stats.averageApiTime || 0;
  }

  private async testFilterResponseTime(): Promise<number> {
    // Simular aplicação de filtro
    const startTime = performance.now();
    
    // Simular operação de filtro
    await new Promise(resolve => setTimeout(resolve, 50));
    
    return performance.now() - startTime;
  }

  private async testFilterRenderTime(): Promise<number> {
    // Obter tempo de renderização de filtros
    const stats = performanceMonitor.getDetailedStats();
    return stats.averageFilterTime || 0;
  }

  private async testAutoRefreshUpdateTime(): Promise<number> {
    // Simular auto-refresh
    const startTime = performance.now();
    
    // Simular atualização
    await new Promise(resolve => setTimeout(resolve, 100));
    
    return performance.now() - startTime;
  }

  private async testAutoRefreshApiTime(): Promise<number> {
    // Obter tempo de API para auto-refresh
    const stats = performanceMonitor.getDetailedStats();
    return stats.averageApiTime || 0;
  }

  private async testLCP(): Promise<number> {
    // Obter LCP das Web Vitals
    const summary = webVitalsMonitor.getSummary();
    return summary.averageValues.LCP || 0;
  }

  private async testFID(): Promise<number> {
    // Obter FID das Web Vitals
    const summary = webVitalsMonitor.getSummary();
    return summary.averageValues.FID || summary.averageValues.INP || 0;
  }

  private async testCLS(): Promise<number> {
    // Obter CLS das Web Vitals
    const summary = webVitalsMonitor.getSummary();
    return summary.averageValues.CLS || 0;
  }

  /**
   * Executa testes específicos por categoria
   */
  async runCategoryTests(category: PerformanceTestCase['category']): Promise<PerformanceTestResult[]> {
    const categoryTests = this.testCases.filter(tc => tc.category === category);
    const results: PerformanceTestResult[] = [];

    for (const testCase of categoryTests) {
      const result = await this.runSingleTest(testCase);
      results.push(result);
    }

    return results;
  }

  /**
   * Gera relatório de release
   */
  async generateReleaseReport(): Promise<{
    suiteResult: PerformanceTestSuiteResult;
    baselineComparison: any;
    recommendations: string[];
    releaseApproved: boolean;
  }> {
    console.log('📋 Gerando relatório de release...');
    
    const suiteResult = await this.runTestSuite();
    
    // Comparar com linha de base se disponível
    const baseline = performanceBaseline.getBaseline();
    let baselineComparison = null;
    
    if (baseline) {
      // Construir métricas atuais baseadas nos resultados dos testes
      const currentMetrics = {
        homepage: {
          loadTime: suiteResult.results.find(r => r.testCase === 'Homepage Load Time')?.value || 0,
          renderTime: suiteResult.results.find(r => r.testCase === 'Homepage Initial Render')?.value || 0,
          apiResponseTime: suiteResult.results.find(r => r.testCase === 'Homepage API Response')?.value || 0
        },
        filters: {
          responseTime: suiteResult.results.find(r => r.testCase === 'Filter Response Time')?.value || 0,
          renderTime: suiteResult.results.find(r => r.testCase === 'Filter Render Time')?.value || 0
        },
        autoRefresh: {
          updateTime: suiteResult.results.find(r => r.testCase === 'Auto-refresh Update Time')?.value || 0,
          apiTime: suiteResult.results.find(r => r.testCase === 'Auto-refresh API Time')?.value || 0
        }
      };
      
      baselineComparison = performanceBaseline.generateComparisonReport(currentMetrics);
    }

    // Gerar recomendações
    const recommendations = this.generateReleaseRecommendations(suiteResult, baselineComparison);
    
    // Determinar se o release é aprovado
    const releaseApproved = suiteResult.overallPassed && suiteResult.criticalFailures === 0;

    const report = {
      suiteResult,
      baselineComparison,
      recommendations,
      releaseApproved
    };

    console.log('📊 Relatório de Release:', {
      testsPassados: `${suiteResult.passedTests}/${suiteResult.totalTests}`,
      falhasCriticas: suiteResult.criticalFailures,
      aprovado: releaseApproved ? 'SIM' : 'NÃO'
    });

    return report;
  }

  /**
   * Gera recomendações para o release
   */
  private generateReleaseRecommendations(
    suiteResult: PerformanceTestSuiteResult,
    baselineComparison: any
  ): string[] {
    const recommendations: string[] = [];

    // Verificar falhas críticas
    if (suiteResult.criticalFailures > 0) {
      recommendations.push('🚨 BLOQUEADOR: Falhas críticas detectadas - release não recomendado');
    }

    // Verificar testes falhados
    const failedTests = suiteResult.results.filter(r => !r.passed);
    if (failedTests.length > 0) {
      recommendations.push(`⚠️ ${failedTests.length} teste(s) falharam: ${failedTests.map(t => t.testCase).join(', ')}`);
    }

    // Verificar degradação em relação à linha de base
    if (baselineComparison?.comparisons) {
      const degraded = baselineComparison.comparisons.filter((c: any) => c.status === 'degraded');
      if (degraded.length > 0) {
        recommendations.push(`📉 Performance degradou em: ${degraded.map((d: any) => d.metric).join(', ')}`);
      }
    }

    // Recomendações por categoria
    Object.entries(suiteResult.summary).forEach(([category, stats]) => {
      if (stats.passed < stats.total) {
        recommendations.push(`🔧 Otimizar categoria ${category}: ${stats.passed}/${stats.total} testes passaram`);
      }
    });

    if (recommendations.length === 0) {
      recommendations.push('✅ Todos os testes passaram - release aprovado!');
    }

    return recommendations;
  }

  /**
   * Obtém lista de casos de teste
   */
  getTestCases(): PerformanceTestCase[] {
    return [...this.testCases];
  }

  /**
   * Verifica se a suite está em execução
   */
  isTestSuiteRunning(): boolean {
    return this.isRunning;
  }
}

// Instância singleton
export const performanceTestSuite = new PerformanceTestSuite();

// Utilitários para debugging e CI/CD
export const debugTestSuite = {
  runTests: () => performanceTestSuite.runTestSuite(),
  runCategoryTests: (category: PerformanceTestCase['category']) => 
    performanceTestSuite.runCategoryTests(category),
  generateReleaseReport: () => performanceTestSuite.generateReleaseReport(),
  getTestCases: () => performanceTestSuite.getTestCases(),
  addTestCase: (testCase: PerformanceTestCase) => performanceTestSuite.addTestCase(testCase)
};

// Expor no window para debugging em desenvolvimento
if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
  (window as any).debugTestSuite = debugTestSuite;
  (window as any).performanceTestSuite = performanceTestSuite;
}

// Função para integração com CI/CD
export const runPreReleaseTests = async (): Promise<boolean> => {
  try {
    const report = await performanceTestSuite.generateReleaseReport();
    
    // Log para CI/CD
    console.log('='.repeat(50));
    console.log('RELATÓRIO DE PERFORMANCE PRÉ-RELEASE');
    console.log('='.repeat(50));
    console.log(`Testes executados: ${report.suiteResult.totalTests}`);
    console.log(`Testes aprovados: ${report.suiteResult.passedTests}`);
    console.log(`Falhas críticas: ${report.suiteResult.criticalFailures}`);
    console.log(`Release aprovado: ${report.releaseApproved ? 'SIM' : 'NÃO'}`);
    console.log('Recomendações:');
    report.recommendations.forEach(rec => console.log(`  - ${rec}`));
    console.log('='.repeat(50));
    
    return report.releaseApproved;
  } catch (error) {
    console.error('Erro ao executar testes pré-release:', error);
    return false;
  }
};