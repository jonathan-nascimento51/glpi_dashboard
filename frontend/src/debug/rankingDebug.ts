/**
 * Debug utilities para investigar o problema do ranking de técnicos
 * que desaparece após o primeiro refresh
 */

export class RankingDebugger {
  private static logs: Array<{
    timestamp: string;
    event: string;
    data: any;
    source: string;
  }> = [];

  static log(event: string, data: any, source: string = 'unknown') {
    const logEntry = {
      timestamp: new Date().toISOString(),
      event,
      data: JSON.parse(JSON.stringify(data)), // Deep clone to avoid reference issues
      source
    };
    
    this.logs.push(logEntry);
    
    // Keep only last 100 logs
    if (this.logs.length > 100) {
      this.logs = this.logs.slice(-100);
    }
    
    console.log(`🔍 [${source}] ${event}:`, data);
  }

  static getLogs() {
    return [...this.logs];
  }

  static clearLogs() {
    this.logs = [];
  }

  static exportLogs() {
    const logsJson = JSON.stringify(this.logs, null, 2);
    const blob = new Blob([logsJson], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `ranking-debug-${new Date().toISOString().slice(0, 19)}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    
    URL.revokeObjectURL(url);
  }

  static analyzeRankingFlow() {
    const rankingLogs = this.logs.filter(log => 
      log.event.toLowerCase().includes('ranking') ||
      log.event.toLowerCase().includes('technician')
    );
    
    console.group('🔍 Análise do fluxo do ranking');
    console.log('Total de logs relacionados ao ranking:', rankingLogs.length);
    
    // Agrupar por fonte
    const bySource = rankingLogs.reduce((acc, log) => {
      if (!acc[log.source]) acc[log.source] = [];
      acc[log.source].push(log);
      return acc;
    }, {} as Record<string, typeof rankingLogs>);
    
    Object.entries(bySource).forEach(([source, logs]) => {
      console.group(`📍 ${source} (${logs.length} logs)`);
      logs.forEach(log => {
        console.log(`${log.timestamp}: ${log.event}`, log.data);
      });
      console.groupEnd();
    });
    
    console.groupEnd();
    
    return rankingLogs;
  }

  static trackRankingState(state: any, source: string) {
    this.log('ranking_state_change', {
      hasRanking: !!state.technicianRanking,
      rankingLength: state.technicianRanking?.length || 0,
      isLoading: state.isLoading,
      error: state.error,
      cacheInfo: this.getCacheInfo()
    }, source);
  }

  static trackApiCall(endpoint: string, params: any, result: any) {
    this.log('api_call', {
      endpoint,
      params,
      resultType: typeof result,
      resultLength: Array.isArray(result) ? result.length : 'not_array',
      hasData: !!result
    }, 'api');
  }

  static trackCacheOperation(operation: string, key: string, data?: any) {
    this.log('cache_operation', {
      operation,
      key,
      hasData: !!data,
      dataType: typeof data,
      timestamp: Date.now()
    }, 'cache');
  }

  private static getCacheInfo() {
    // Tentar acessar o cache local do useDashboard
    try {
      const cacheKeys = [];
      // Como o cache é privado, vamos tentar inferir informações
      return {
        available: 'unknown',
        keys: cacheKeys.length
      };
    } catch (error) {
      return {
        available: false,
        error: error instanceof Error ? error.message : 'unknown'
      };
    }
  }
}

// Adicionar ao window para debug no console
if (typeof window !== 'undefined') {
  (window as any).RankingDebugger = RankingDebugger;
}