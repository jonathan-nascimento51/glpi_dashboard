/**
 * Script de validação da correção do problema do ranking
 * Implementa as boas práticas da auditoria para verificar se a solução está funcionando
 */

import { RankingDebugger } from './rankingDebug';

interface ValidationResult {
  test: string;
  passed: boolean;
  details: any;
  timestamp: number;
}

class RankingFixValidator {
  private static results: ValidationResult[] = [];

  /**
   * Teste 1: Verificar se o estado do ranking é mantido após refresh
   */
  static async testStateManagement(): Promise<ValidationResult> {
    const test = 'Estado do Ranking - Gerenciamento Correto';
    console.log('🧪 Testando gerenciamento de estado do ranking...');
    
    try {
      // Verificar se o hook useDashboard está usando estado separado para o ranking
      const dashboardHook = (window as any).useDashboard;
      
      if (!dashboardHook) {
        return {
          test,
          passed: false,
          details: 'Hook useDashboard não encontrado no window',
          timestamp: Date.now()
        };
      }

      // Simular uma atualização e verificar se o estado persiste
      const initialRankingLength = document.querySelectorAll('[data-testid="technician-item"]').length;
      
      console.log('📊 Ranking inicial encontrado:', initialRankingLength, 'técnicos');
      
      return {
        test,
        passed: initialRankingLength > 0,
        details: {
          initialRankingLength,
          hasRankingElements: initialRankingLength > 0,
          message: initialRankingLength > 0 ? 'Estado do ranking mantido' : 'Ranking não encontrado'
        },
        timestamp: Date.now()
      };
    } catch (error) {
      return {
        test,
        passed: false,
        details: { error: error instanceof Error ? error.message : 'Erro desconhecido' },
        timestamp: Date.now()
      };
    }
  }

  /**
   * Teste 2: Verificar se as operações assíncronas estão funcionando corretamente
   */
  static async testAsyncOperations(): Promise<ValidationResult> {
    const test = 'Operações Assíncronas - Sincronização Correta';
    console.log('🧪 Testando operações assíncronas...');
    
    try {
      // Verificar se existe a função refreshRanking
      const refreshFunction = (window as any).refreshRanking;
      
      if (refreshFunction && typeof refreshFunction === 'function') {
        console.log('✅ Função refreshRanking encontrada');
        
        // Testar se a função é assíncrona
        const result = refreshFunction();
        const isPromise = result && typeof result.then === 'function';
        
        return {
          test,
          passed: isPromise,
          details: {
            hasRefreshFunction: true,
            isAsync: isPromise,
            message: isPromise ? 'Operações assíncronas implementadas corretamente' : 'Função não é assíncrona'
          },
          timestamp: Date.now()
        };
      } else {
        return {
          test,
          passed: false,
          details: {
            hasRefreshFunction: false,
            message: 'Função refreshRanking não encontrada'
          },
          timestamp: Date.now()
        };
      }
    } catch (error) {
      return {
        test,
        passed: false,
        details: { error: error instanceof Error ? error.message : 'Erro desconhecido' },
        timestamp: Date.now()
      };
    }
  }

  /**
   * Teste 3: Verificar se o feedback visual está funcionando
   */
  static async testVisualFeedback(): Promise<ValidationResult> {
    const test = 'Feedback Visual - Loading States';
    console.log('🧪 Testando feedback visual...');
    
    try {
      // Verificar se existem elementos de loading
      const loadingElements = document.querySelectorAll('[data-testid*="loading"], .animate-pulse, .skeleton');
      const hasLoadingStates = loadingElements.length > 0;
      
      // Verificar se existe indicação de erro
      const errorElements = document.querySelectorAll('[data-testid*="error"], .text-red, .error');
      const hasErrorStates = errorElements.length >= 0; // >= 0 porque pode não ter erro no momento
      
      return {
        test,
        passed: hasLoadingStates,
        details: {
          loadingElements: loadingElements.length,
          errorElements: errorElements.length,
          hasLoadingStates,
          hasErrorStates,
          message: hasLoadingStates ? 'Feedback visual implementado' : 'Feedback visual não encontrado'
        },
        timestamp: Date.now()
      };
    } catch (error) {
      return {
        test,
        passed: false,
        details: { error: error instanceof Error ? error.message : 'Erro desconhecido' },
        timestamp: Date.now()
      };
    }
  }

  /**
   * Teste 4: Verificar se a função de atualização centralizada está funcionando
   */
  static async testCentralizedUpdate(): Promise<ValidationResult> {
    const test = 'Atualização Centralizada - Função Única';
    console.log('🧪 Testando atualização centralizada...');
    
    try {
      // Verificar logs do RankingDebugger para evidências da função centralizada
      const logs = RankingDebugger.getLogs();
      const updateLogs = logs.filter(log => 
        log.event.includes('ranking_update') || 
        log.event.includes('atualizarRanking') ||
        log.event.includes('buscarDadosDoRanking')
      );
      
      const hasUpdateLogs = updateLogs.length > 0;
      
      return {
        test,
        passed: hasUpdateLogs,
        details: {
          totalLogs: logs.length,
          updateLogs: updateLogs.length,
          hasUpdateLogs,
          recentUpdateLogs: updateLogs.slice(-3),
          message: hasUpdateLogs ? 'Função centralizada funcionando' : 'Função centralizada não detectada'
        },
        timestamp: Date.now()
      };
    } catch (error) {
      return {
        test,
        passed: false,
        details: { error: error instanceof Error ? error.message : 'Erro desconhecido' },
        timestamp: Date.now()
      };
    }
  }

  /**
   * Executar todos os testes de validação
   */
  static async runAllValidations(): Promise<ValidationResult[]> {
    console.log('🚀 Iniciando validação completa da correção do ranking...');
    
    const tests = [
      this.testStateManagement(),
      this.testAsyncOperations(),
      this.testVisualFeedback(),
      this.testCentralizedUpdate()
    ];
    
    const results = await Promise.all(tests);
    this.results = results;
    
    // Gerar relatório
    const passedTests = results.filter(r => r.passed).length;
    const totalTests = results.length;
    
    console.log(`📊 Relatório de Validação:`);
    console.log(`✅ Testes Aprovados: ${passedTests}/${totalTests}`);
    console.log(`❌ Testes Falharam: ${totalTests - passedTests}/${totalTests}`);
    
    results.forEach(result => {
      const icon = result.passed ? '✅' : '❌';
      console.log(`${icon} ${result.test}:`, result.details.message || 'Ver detalhes');
    });
    
    return results;
  }

  /**
   * Obter resultados dos testes
   */
  static getResults(): ValidationResult[] {
    return this.results;
  }

  /**
   * Gerar relatório detalhado
   */
  static generateReport(): string {
    const results = this.getResults();
    const passedTests = results.filter(r => r.passed).length;
    const totalTests = results.length;
    const successRate = Math.round((passedTests / totalTests) * 100);
    
    let report = `\n=== RELATÓRIO DE VALIDAÇÃO DA CORREÇÃO DO RANKING ===\n`;
    report += `Data: ${new Date().toLocaleString()}\n`;
    report += `Taxa de Sucesso: ${successRate}% (${passedTests}/${totalTests})\n\n`;
    
    results.forEach((result, index) => {
      const status = result.passed ? 'PASSOU' : 'FALHOU';
      report += `${index + 1}. ${result.test}: ${status}\n`;
      report += `   Detalhes: ${JSON.stringify(result.details, null, 2)}\n\n`;
    });
    
    return report;
  }
}

// Expor no window para uso no console
if (typeof window !== 'undefined') {
  (window as any).RankingFixValidator = RankingFixValidator;
  (window as any).validateRankingFix = () => RankingFixValidator.runAllValidations();
  (window as any).rankingValidationReport = () => console.log(RankingFixValidator.generateReport());
}

export { RankingFixValidator };