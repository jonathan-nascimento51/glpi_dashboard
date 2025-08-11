// Monitor específico para o problema do ranking que desaparece após refresh

import { RankingDebugger } from './rankingDebug';

interface RankingState {
  timestamp: number;
  hasData: boolean;
  dataLength: number;
  isLoading: boolean;
  error?: string;
  source: string;
  data?: any[];
}

class RankingMonitor {
  private states: RankingState[] = [];
  private isMonitoring = false;
  private observer?: MutationObserver;
  private intervalId?: number;

  startMonitoring() {
    if (this.isMonitoring) {
      console.log('⚠️ Monitor já está ativo');
      return;
    }

    this.isMonitoring = true;
    console.log('🔍 Iniciando monitoramento do ranking...');
    
    // Monitorar mudanças no DOM
    this.setupDOMObserver();
    
    // Monitorar estado periodicamente
    this.setupPeriodicCheck();
    
    // Monitorar eventos de navegação
    this.setupNavigationListeners();
    
    // Estado inicial
    this.captureState('initial');
  }

  stopMonitoring() {
    this.isMonitoring = false;
    
    if (this.observer) {
      this.observer.disconnect();
    }
    
    if (this.intervalId) {
      clearInterval(this.intervalId);
    }
    
    console.log('🛑 Monitoramento do ranking parado');
  }

  private setupDOMObserver() {
    this.observer = new MutationObserver((mutations) => {
      let rankingChanged = false;
      
      mutations.forEach((mutation) => {
        if (mutation.type === 'childList') {
          const addedNodes = Array.from(mutation.addedNodes);
          const removedNodes = Array.from(mutation.removedNodes);
          
          const hasRankingChanges = [...addedNodes, ...removedNodes].some(node => {
            if (node.nodeType === Node.ELEMENT_NODE) {
              const element = node as Element;
              return element.className?.includes('ranking') || 
                     element.className?.includes('technician') ||
                     element.querySelector?.('[class*="ranking"], [class*="technician"]');
            }
            return false;
          });
          
          if (hasRankingChanges) {
            rankingChanged = true;
          }
        }
      });
      
      if (rankingChanged) {
        this.captureState('dom_change');
      }
    });
    
    this.observer.observe(document.body, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['class', 'style']
    });
  }

  private setupPeriodicCheck() {
    this.intervalId = window.setInterval(() => {
      this.captureState('periodic_check');
    }, 2000); // Verificar a cada 2 segundos
  }

  private setupNavigationListeners() {
    // Antes do refresh/navegação
    window.addEventListener('beforeunload', () => {
      this.captureState('before_unload');
      console.log('📊 Estados capturados antes do unload:', this.states.length);
    });
    
    // Após o carregamento
    window.addEventListener('load', () => {
      this.captureState('after_load');
    });
    
    // Mudanças de visibilidade
    document.addEventListener('visibilitychange', () => {
      this.captureState(`visibility_${document.visibilityState}`);
    });
  }

  private captureState(source: string) {
    try {
      // Buscar elementos do ranking no DOM
      const rankingElements = document.querySelectorAll('[class*="ranking"], [class*="technician"]');
      const rankingCards = document.querySelectorAll('[class*="technician-card"], [data-testid*="technician"]');
      
      // Verificar se há dados visíveis
      const hasVisibleData = rankingCards.length > 0;
      
      // Tentar acessar dados do React (se disponível)
      let reactData: any[] = [];
      try {
        const dashboardElement = document.querySelector('[class*="dashboard"]');
        if (dashboardElement && (dashboardElement as any)._reactInternalFiber) {
          // Tentar extrair dados do React (método pode variar)
          const fiber = (dashboardElement as any)._reactInternalFiber;
          // Implementação específica dependeria da estrutura do React
        }
      } catch (e) {
        // Ignorar erros de acesso ao React
      }
      
      // Verificar localStorage
      const cacheData = this.checkLocalStorageCache();
      
      const state: RankingState = {
        timestamp: Date.now(),
        hasData: hasVisibleData,
        dataLength: rankingCards.length,
        isLoading: this.checkLoadingState(),
        source,
        data: cacheData
      };
      
      this.states.push(state);
      
      // Log apenas mudanças significativas
      const lastState = this.states[this.states.length - 2];
      if (!lastState || 
          lastState.hasData !== state.hasData || 
          lastState.dataLength !== state.dataLength ||
          lastState.isLoading !== state.isLoading) {
        
        console.log(`🔍 [RANKING MONITOR] ${source}:`, {
          hasData: state.hasData,
          dataLength: state.dataLength,
          isLoading: state.isLoading,
          elementsFound: rankingElements.length,
          cacheEntries: cacheData?.length || 0
        });
        
        // Se os dados desapareceram, investigar mais
        if (lastState?.hasData && !state.hasData) {
          console.warn('⚠️ DADOS DO RANKING DESAPARECERAM!');
          this.investigateDataLoss();
        }
      }
      
      // Manter apenas os últimos 50 estados
      if (this.states.length > 50) {
        this.states = this.states.slice(-50);
      }
      
    } catch (error) {
      console.error('Erro ao capturar estado do ranking:', error);
    }
  }

  private checkLoadingState(): boolean {
    // Verificar indicadores de loading no DOM
    const loadingElements = document.querySelectorAll(
      '[class*="loading"], [class*="spinner"], [class*="skeleton"]'
    );
    return loadingElements.length > 0;
  }

  private checkLocalStorageCache(): any[] | null {
    try {
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.includes('ranking')) {
          const data = localStorage.getItem(key);
          if (data) {
            const parsed = JSON.parse(data);
            if (Array.isArray(parsed) || (parsed.data && Array.isArray(parsed.data))) {
              return Array.isArray(parsed) ? parsed : parsed.data;
            }
          }
        }
      }
    } catch (error) {
      console.error('Erro ao verificar cache:', error);
    }
    return null;
  }

  private investigateDataLoss() {
    console.log('🔍 Investigando perda de dados do ranking...');
    
    // Verificar se a API ainda responde
    this.testApiConnection();
    
    // Verificar estado do cache
    const cacheData = this.checkLocalStorageCache();
    console.log('💾 Dados em cache:', cacheData?.length || 0);
    
    // Verificar logs do RankingDebugger
    const debugLogs = RankingDebugger.getLogs();
    const recentLogs = debugLogs.slice(-10);
    console.log('📝 Logs recentes do debugger:', recentLogs);
    
    // Verificar erros no console
    const errors = this.getConsoleErrors();
    if (errors.length > 0) {
      console.log('❌ Erros recentes:', errors);
    }
  }

  private async testApiConnection() {
    try {
      const response = await fetch('/api/technicians/ranking?limit=1');
      console.log('🌐 Teste de API:', response.status, response.ok);
    } catch (error) {
      console.error('🌐 Erro na API:', error);
    }
  }

  private getConsoleErrors(): any[] {
    // Esta função seria mais efetiva se implementássemos um interceptor de console.error
    // Por enquanto, retornamos array vazio
    return [];
  }

  getStates(): RankingState[] {
    return this.states;
  }

  generateReport() {
    console.log('\n📊 RELATÓRIO DO MONITOR DE RANKING');
    console.log('=' .repeat(50));
    
    const totalStates = this.states.length;
    const statesWithData = this.states.filter(s => s.hasData).length;
    const statesWithoutData = totalStates - statesWithData;
    
    console.log(`📈 Total de estados capturados: ${totalStates}`);
    console.log(`✅ Estados com dados: ${statesWithData}`);
    console.log(`❌ Estados sem dados: ${statesWithoutData}`);
    
    if (totalStates > 0) {
      const firstState = this.states[0];
      const lastState = this.states[totalStates - 1];
      
      console.log(`\n⏰ Período monitorado: ${new Date(firstState.timestamp).toLocaleTimeString()} - ${new Date(lastState.timestamp).toLocaleTimeString()}`);
      
      // Identificar transições críticas
      const transitions = this.findCriticalTransitions();
      if (transitions.length > 0) {
        console.log('\n🔄 Transições críticas encontradas:');
        transitions.forEach((transition, index) => {
          console.log(`${index + 1}. ${transition.from.source} → ${transition.to.source}`);
          console.log(`   Dados: ${transition.from.hasData} → ${transition.to.hasData}`);
          console.log(`   Quantidade: ${transition.from.dataLength} → ${transition.to.dataLength}`);
        });
      }
    }
    
    return {
      totalStates,
      statesWithData,
      statesWithoutData,
      states: this.states
    };
  }

  private findCriticalTransitions() {
    const transitions = [];
    
    for (let i = 1; i < this.states.length; i++) {
      const prev = this.states[i - 1];
      const curr = this.states[i];
      
      // Transição de dados para sem dados
      if (prev.hasData && !curr.hasData) {
        transitions.push({ from: prev, to: curr, type: 'data_loss' });
      }
      
      // Transição de sem dados para dados
      if (!prev.hasData && curr.hasData) {
        transitions.push({ from: prev, to: curr, type: 'data_recovery' });
      }
    }
    
    return transitions;
  }

  clearStates() {
    this.states = [];
  }
}

// Instância global
const rankingMonitor = new RankingMonitor();

// Expor no window para uso no console
if (typeof window !== 'undefined') {
  (window as any).rankingMonitor = rankingMonitor;
  (window as any).startRankingMonitor = () => rankingMonitor.startMonitoring();
  (window as any).stopRankingMonitor = () => rankingMonitor.stopMonitoring();
  (window as any).rankingReport = () => rankingMonitor.generateReport();
}

export { RankingMonitor, rankingMonitor };
export default rankingMonitor;