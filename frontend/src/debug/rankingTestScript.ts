// Script de teste para diagnosticar o problema do ranking que desaparece

import { RankingDebugger } from './rankingDebug';

interface TestScenario {
  name: string;
  description: string;
  steps: (() => Promise<void>)[];
}

class RankingTestRunner {
  private scenarios: TestScenario[] = [];
  private results: { [key: string]: any } = {};

  constructor() {
    this.setupScenarios();
  }

  private setupScenarios() {
    this.scenarios = [
      {
        name: 'initial_load',
        description: 'Teste de carregamento inicial do ranking',
        steps: [
          async () => {
            console.log('🔄 Iniciando teste de carregamento inicial...');
            RankingDebugger.log('test_start', { scenario: 'initial_load' }, 'test');
            
            // Simular carregamento inicial
            await this.waitForRankingData();
            
            const logs = RankingDebugger.getLogs();
            const rankingLogs = logs.filter(log => 
              log.event.includes('ranking') || log.event.includes('technician')
            );
            
            this.results.initial_load = {
              totalLogs: logs.length,
              rankingLogs: rankingLogs.length,
              hasRankingData: rankingLogs.some(log => 
                log.data && log.data.technicianRanking && log.data.technicianRanking.length > 0
              )
            };
            
            console.log('✅ Teste de carregamento inicial concluído:', this.results.initial_load);
          }
        ]
      },
      {
        name: 'refresh_simulation',
        description: 'Simulação de refresh da página',
        steps: [
          async () => {
            console.log('🔄 Iniciando simulação de refresh...');
            RankingDebugger.log('test_refresh_start', { scenario: 'refresh_simulation' }, 'test');
            
            // Simular limpeza de cache (como acontece no refresh)
            this.simulateCacheClear();
            
            // Aguardar recarregamento
            await this.waitForRankingData();
            
            const logs = RankingDebugger.getLogs();
            const postRefreshLogs = logs.filter(log => 
              log.timestamp > Date.now() - 10000 // últimos 10 segundos
            );
            
            this.results.refresh_simulation = {
              postRefreshLogs: postRefreshLogs.length,
              hasRankingAfterRefresh: postRefreshLogs.some(log => 
                log.data && log.data.technicianRanking && log.data.technicianRanking.length > 0
              )
            };
            
            console.log('✅ Simulação de refresh concluída:', this.results.refresh_simulation);
          }
        ]
      },
      {
        name: 'cache_behavior',
        description: 'Análise do comportamento do cache',
        steps: [
          async () => {
            console.log('🔄 Analisando comportamento do cache...');
            RankingDebugger.log('test_cache_analysis', { scenario: 'cache_behavior' }, 'test');
            
            const logs = RankingDebugger.getLogs();
            const cacheLogs = logs.filter(log => log.event.includes('cache'));
            
            const cacheHits = cacheLogs.filter(log => log.event.includes('hit'));
            const cacheMisses = cacheLogs.filter(log => log.event.includes('miss'));
            const cacheOperations = cacheLogs.filter(log => 
              log.event.includes('set') || log.event.includes('get')
            );
            
            this.results.cache_behavior = {
              totalCacheOperations: cacheLogs.length,
              cacheHits: cacheHits.length,
              cacheMisses: cacheMisses.length,
              cacheOperations: cacheOperations.length,
              hitRatio: cacheHits.length / (cacheHits.length + cacheMisses.length) || 0
            };
            
            console.log('✅ Análise de cache concluída:', this.results.cache_behavior);
          }
        ]
      },
      {
        name: 'api_calls_analysis',
        description: 'Análise das chamadas de API',
        steps: [
          async () => {
            console.log('🔄 Analisando chamadas de API...');
            RankingDebugger.log('test_api_analysis', { scenario: 'api_calls_analysis' }, 'test');
            
            const logs = RankingDebugger.getLogs();
            const apiLogs = logs.filter(log => log.source === 'api' || log.event.includes('api'));
            
            const successfulCalls = apiLogs.filter(log => 
              log.event.includes('success') || log.event.includes('mapped')
            );
            const failedCalls = apiLogs.filter(log => 
              log.event.includes('error') || log.event.includes('fail')
            );
            
            this.results.api_calls_analysis = {
              totalApiLogs: apiLogs.length,
              successfulCalls: successfulCalls.length,
              failedCalls: failedCalls.length,
              successRate: successfulCalls.length / apiLogs.length || 0
            };
            
            console.log('✅ Análise de API concluída:', this.results.api_calls_analysis);
          }
        ]
      }
    ];
  }

  private async waitForRankingData(timeout = 5000): Promise<void> {
    return new Promise((resolve) => {
      const startTime = Date.now();
      const checkInterval = setInterval(() => {
        const logs = RankingDebugger.getLogs();
        const hasRankingData = logs.some(log => 
          log.data && log.data.technicianRanking && log.data.technicianRanking.length > 0
        );
        
        if (hasRankingData || Date.now() - startTime > timeout) {
          clearInterval(checkInterval);
          resolve();
        }
      }, 100);
    });
  }

  private simulateCacheClear(): void {
    // Simular limpeza de cache local
    if (typeof window !== 'undefined' && window.localStorage) {
      const keys = Object.keys(window.localStorage);
      keys.forEach(key => {
        if (key.includes('dashboard') || key.includes('ranking')) {
          window.localStorage.removeItem(key);
        }
      });
    }
    
    RankingDebugger.log('cache_cleared', { 
      action: 'simulate_refresh_cache_clear',
      timestamp: Date.now()
    }, 'test');
  }

  async runAllTests(): Promise<void> {
    console.log('🚀 Iniciando bateria de testes do ranking...');
    RankingDebugger.clearLogs();
    
    for (const scenario of this.scenarios) {
      console.log(`\n📋 Executando cenário: ${scenario.name}`);
      console.log(`📝 Descrição: ${scenario.description}`);
      
      try {
        for (const step of scenario.steps) {
          await step();
        }
      } catch (error) {
        console.error(`❌ Erro no cenário ${scenario.name}:`, error);
        this.results[scenario.name] = { error: error.message };
      }
    }
    
    this.generateReport();
  }

  async runSingleTest(scenarioName: string): Promise<void> {
    const scenario = this.scenarios.find(s => s.name === scenarioName);
    if (!scenario) {
      console.error(`❌ Cenário '${scenarioName}' não encontrado`);
      return;
    }
    
    console.log(`🚀 Executando cenário: ${scenario.name}`);
    console.log(`📝 Descrição: ${scenario.description}`);
    
    try {
      for (const step of scenario.steps) {
        await step();
      }
    } catch (error) {
      console.error(`❌ Erro no cenário ${scenario.name}:`, error);
      this.results[scenario.name] = { error: error.message };
    }
  }

  private generateReport(): void {
    console.log('\n📊 RELATÓRIO DE TESTES DO RANKING');
    console.log('=' .repeat(50));
    
    Object.entries(this.results).forEach(([scenario, result]) => {
      console.log(`\n🔍 ${scenario.toUpperCase()}:`);
      console.log(JSON.stringify(result, null, 2));
    });
    
    // Análise consolidada
    const analysis = this.analyzeResults();
    console.log('\n🎯 ANÁLISE CONSOLIDADA:');
    console.log(JSON.stringify(analysis, null, 2));
    
    // Salvar relatório
    RankingDebugger.log('test_report', {
      results: this.results,
      analysis,
      timestamp: Date.now()
    }, 'test');
  }

  private analyzeResults(): any {
    const analysis: any = {
      summary: {},
      issues: [],
      recommendations: []
    };
    
    // Análise de carregamento inicial
    if (this.results.initial_load) {
      analysis.summary.initialLoad = this.results.initial_load.hasRankingData ? 'SUCCESS' : 'FAIL';
      if (!this.results.initial_load.hasRankingData) {
        analysis.issues.push('Ranking não carrega no carregamento inicial');
      }
    }
    
    // Análise de refresh
    if (this.results.refresh_simulation) {
      analysis.summary.refreshBehavior = this.results.refresh_simulation.hasRankingAfterRefresh ? 'SUCCESS' : 'FAIL';
      if (!this.results.refresh_simulation.hasRankingAfterRefresh) {
        analysis.issues.push('Ranking desaparece após refresh - PROBLEMA IDENTIFICADO!');
        analysis.recommendations.push('Verificar invalidação de cache no refresh');
        analysis.recommendations.push('Implementar persistência de dados entre refreshes');
      }
    }
    
    // Análise de cache
    if (this.results.cache_behavior) {
      const hitRatio = this.results.cache_behavior.hitRatio;
      analysis.summary.cacheEfficiency = hitRatio > 0.7 ? 'GOOD' : hitRatio > 0.4 ? 'MODERATE' : 'POOR';
      if (hitRatio < 0.5) {
        analysis.issues.push('Taxa de acerto do cache muito baixa');
        analysis.recommendations.push('Otimizar estratégia de cache');
      }
    }
    
    // Análise de API
    if (this.results.api_calls_analysis) {
      const successRate = this.results.api_calls_analysis.successRate;
      analysis.summary.apiReliability = successRate > 0.9 ? 'EXCELLENT' : successRate > 0.7 ? 'GOOD' : 'POOR';
      if (successRate < 0.8) {
        analysis.issues.push('Taxa de sucesso da API baixa');
        analysis.recommendations.push('Implementar retry automático para chamadas de API');
      }
    }
    
    return analysis;
  }

  getResults(): any {
    return this.results;
  }

  clearResults(): void {
    this.results = {};
  }
}

// Instância global para uso no console do navegador
const rankingTestRunner = new RankingTestRunner();

// Expor no window para acesso via console
if (typeof window !== 'undefined') {
  (window as any).rankingTestRunner = rankingTestRunner;
  (window as any).testRanking = {
    runAll: () => rankingTestRunner.runAllTests(),
    runSingle: (scenario: string) => rankingTestRunner.runSingleTest(scenario),
    getResults: () => rankingTestRunner.getResults(),
    clearResults: () => rankingTestRunner.clearResults()
  };
}

export { RankingTestRunner, rankingTestRunner };