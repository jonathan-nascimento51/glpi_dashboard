// Script de diagnóstico específico para o problema do ranking que desaparece

import { RankingDebugger } from './rankingDebug';
import { getTechnicianRanking } from '../services/api';
import { FilterParams } from '../types/api';

interface DiagnosticResult {
  step: string;
  success: boolean;
  data?: any;
  error?: string;
  timestamp: number;
}

class RankingDiagnostic {
  private results: DiagnosticResult[] = [];
  private isRunning = false;

  private log(step: string, success: boolean, data?: any, error?: string) {
    const result: DiagnosticResult = {
      step,
      success,
      data,
      error,
      timestamp: Date.now()
    };
    this.results.push(result);
    console.log(`🔍 [DIAGNOSTIC] ${step}:`, success ? '✅' : '❌', data || error);
  }

  async runFullDiagnostic(): Promise<DiagnosticResult[]> {
    if (this.isRunning) {
      console.log('⚠️ Diagnóstico já está em execução');
      return this.results;
    }

    this.isRunning = true;
    this.results = [];
    
    console.log('🚀 Iniciando diagnóstico completo do ranking...');
    
    try {
      // 1. Verificar estado inicial
      await this.checkInitialState();
      
      // 2. Testar chamada da API diretamente
      await this.testDirectApiCall();
      
      // 3. Verificar cache
      await this.checkCacheState();
      
      // 4. Simular refresh da página
      await this.simulatePageRefresh();
      
      // 5. Verificar componentes React
      await this.checkReactComponents();
      
      // 6. Verificar localStorage
      await this.checkLocalStorage();
      
    } catch (error) {
      this.log('diagnostic_error', false, null, error instanceof Error ? error.message : 'Erro desconhecido');
    } finally {
      this.isRunning = false;
    }
    
    this.generateReport();
    return this.results;
  }

  private async checkInitialState() {
    try {
      // Verificar se o RankingDebugger está funcionando
      const logs = RankingDebugger.getLogs();
      this.log('ranking_debugger_active', true, { logCount: logs.length });
      
      // Verificar se há dados no DOM
      const rankingElements = document.querySelectorAll('[class*="ranking"], [class*="technician"]');
      this.log('dom_ranking_elements', true, { elementCount: rankingElements.length });
      
    } catch (error) {
      this.log('initial_state_check', false, null, error instanceof Error ? error.message : 'Erro');
    }
  }

  private async testDirectApiCall() {
    try {
      console.log('🔍 Testando chamada direta da API...');
      
      const filters: FilterParams = {
        dateRange: {
          startDate: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          endDate: new Date().toISOString().split('T')[0]
        }
      };
      
      const startTime = Date.now();
      const result = await getTechnicianRanking(filters);
      const duration = Date.now() - startTime;
      
      this.log('direct_api_call', true, {
        resultLength: result?.length || 0,
        duration: `${duration}ms`,
        sampleData: result?.[0],
        filters
      });
      
    } catch (error) {
      this.log('direct_api_call', false, null, error instanceof Error ? error.message : 'Erro na API');
    }
  }

  private async checkCacheState() {
    try {
      // Verificar cache do navegador
      const cacheNames = await caches.keys();
      this.log('browser_cache', true, { cacheNames });
      
      // Verificar localStorage
      const localStorageKeys = Object.keys(localStorage);
      const relevantKeys = localStorageKeys.filter(key => 
        key.includes('ranking') || key.includes('technician') || key.includes('dashboard')
      );
      
      this.log('local_storage_cache', true, { relevantKeys });
      
    } catch (error) {
      this.log('cache_state_check', false, null, error instanceof Error ? error.message : 'Erro');
    }
  }

  private async simulatePageRefresh() {
    try {
      console.log('🔄 Simulando comportamento após refresh...');
      
      // Limpar caches locais (simular refresh)
      const LOCAL_CACHE = (window as any).LOCAL_CACHE;
      if (LOCAL_CACHE && typeof LOCAL_CACHE.clear === 'function') {
        LOCAL_CACHE.clear();
        this.log('local_cache_cleared', true);
      }
      
      // Verificar se os dados ainda estão disponíveis
      const filters: FilterParams = {};
      const result = await getTechnicianRanking(filters);
      
      this.log('post_refresh_api_call', true, {
        resultLength: result?.length || 0,
        hasData: !!result && result.length > 0
      });
      
    } catch (error) {
      this.log('simulate_refresh', false, null, error instanceof Error ? error.message : 'Erro');
    }
  }

  private async checkReactComponents() {
    try {
      // Verificar se os componentes React estão montados
      const dashboardElement = document.querySelector('[class*="dashboard"]');
      const rankingElement = document.querySelector('[class*="ranking"]');
      
      this.log('react_components_mounted', true, {
        hasDashboard: !!dashboardElement,
        hasRanking: !!rankingElement,
        dashboardClasses: dashboardElement?.className,
        rankingClasses: rankingElement?.className
      });
      
    } catch (error) {
      this.log('react_components_check', false, null, error instanceof Error ? error.message : 'Erro');
    }
  }

  private async checkLocalStorage() {
    try {
      const storageData: Record<string, any> = {};
      
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && (key.includes('ranking') || key.includes('dashboard') || key.includes('cache'))) {
          try {
            storageData[key] = JSON.parse(localStorage.getItem(key) || '');
          } catch {
            storageData[key] = localStorage.getItem(key);
          }
        }
      }
      
      this.log('local_storage_data', true, storageData);
      
    } catch (error) {
      this.log('local_storage_check', false, null, error instanceof Error ? error.message : 'Erro');
    }
  }

  private generateReport() {
    console.log('\n📊 RELATÓRIO DE DIAGNÓSTICO DO RANKING');
    console.log('=' .repeat(50));
    
    const successCount = this.results.filter(r => r.success).length;
    const totalCount = this.results.length;
    
    console.log(`✅ Testes bem-sucedidos: ${successCount}/${totalCount}`);
    console.log(`❌ Testes falharam: ${totalCount - successCount}/${totalCount}`);
    console.log('');
    
    this.results.forEach((result, index) => {
      const status = result.success ? '✅' : '❌';
      console.log(`${index + 1}. ${status} ${result.step}`);
      if (result.error) {
        console.log(`   Erro: ${result.error}`);
      }
      if (result.data && typeof result.data === 'object') {
        console.log(`   Dados:`, result.data);
      }
    });
    
    console.log('\n🔍 POSSÍVEIS CAUSAS DO PROBLEMA:');
    this.analyzePossibleCauses();
  }

  private analyzePossibleCauses() {
    const failedSteps = this.results.filter(r => !r.success);
    
    if (failedSteps.length === 0) {
      console.log('✅ Nenhum problema detectado nos testes básicos.');
      console.log('💡 O problema pode estar relacionado a:');
      console.log('   - Timing de renderização do React');
      console.log('   - Dependências do useEffect');
      console.log('   - Estado assíncrono não sincronizado');
      return;
    }
    
    failedSteps.forEach(step => {
      console.log(`❌ ${step.step}: ${step.error}`);
      
      switch (step.step) {
        case 'direct_api_call':
          console.log('💡 Problema na API - verificar backend e conectividade');
          break;
        case 'cache_state_check':
          console.log('💡 Problema no cache - pode estar corrompido');
          break;
        case 'react_components_check':
          console.log('💡 Componentes React não estão montados corretamente');
          break;
        default:
          console.log('💡 Verificar logs detalhados para mais informações');
      }
    });
  }

  getResults(): DiagnosticResult[] {
    return this.results;
  }

  clearResults() {
    this.results = [];
  }
}

// Instância global para uso no console
const rankingDiagnostic = new RankingDiagnostic();

// Expor no window para uso no console do navegador
if (typeof window !== 'undefined') {
  (window as any).rankingDiagnostic = rankingDiagnostic;
  (window as any).runRankingDiagnostic = () => rankingDiagnostic.runFullDiagnostic();
}

export { RankingDiagnostic, rankingDiagnostic };
export default rankingDiagnostic;