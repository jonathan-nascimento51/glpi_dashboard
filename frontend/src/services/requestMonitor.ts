/**
 * Sistema de monitoramento de requisições para rastrear volume,
 * padrões e performance das chamadas à API
 */

interface RequestMetric {
  id: string;
  endpoint: string;
  method: string;
  params: any;
  startTime: number;
  endTime?: number;
  duration?: number;
  status: 'pending' | 'success' | 'error' | 'cached';
  error?: string;
  cacheHit?: boolean;
  responseSize?: number;
  userAgent?: string;
}

interface RequestStats {
  totalRequests: number;
  successfulRequests: number;
  failedRequests: number;
  cachedRequests: number;
  averageResponseTime: number;
  requestsPerMinute: number;
  topEndpoints: Array<{ endpoint: string; count: number; avgDuration: number }>;
  errorRate: number;
  cacheHitRate: number;
}

interface MonitorConfig {
  maxHistorySize: number;
  aggregationInterval: number;
  enableDetailedLogging: boolean;
  trackUserAgent: boolean;
}

class RequestMonitor {
  private requests: RequestMetric[] = [];
  private config: MonitorConfig;
  private aggregationTimer?: NodeJS.Timeout;
  private currentStats: RequestStats;

  constructor(config: Partial<MonitorConfig> = {}) {
    this.config = {
      maxHistorySize: 1000,
      aggregationInterval: 60000, // 1 minuto
      enableDetailedLogging: true,
      trackUserAgent: false,
      ...config,
    };

    this.currentStats = this.initializeStats();
    this.startAggregation();
  }

  /**
   * Inicia o rastreamento de uma nova requisição
   */
  startRequest(endpoint: string, method: string = 'GET', params: any = {}): string {
    const requestId = this.generateRequestId();

    const metric: RequestMetric = {
      id: requestId,
      endpoint,
      method,
      params,
      startTime: Date.now(),
      status: 'pending',
      userAgent: this.config.trackUserAgent ? navigator.userAgent : undefined,
    };

    this.requests.push(metric);
    this.trimHistory();

    if (this.config.enableDetailedLogging) {
      console.log(`📊 Monitor: Iniciada requisição ${requestId} para ${endpoint}`);
    }

    return requestId;
  }

  /**
   * Finaliza o rastreamento de uma requisição com sucesso
   */
  endRequest(requestId: string, responseSize?: number, cacheHit: boolean = false): void {
    const request = this.requests.find(r => r.id === requestId);
    if (!request) {
      console.warn(`⚠️ Monitor: Requisição ${requestId} não encontrada`);
      return;
    }

    const endTime = Date.now();
    request.endTime = endTime;
    request.duration = endTime - request.startTime;
    request.status = cacheHit ? 'cached' : 'success';
    request.responseSize = responseSize;
    request.cacheHit = cacheHit;

    if (this.config.enableDetailedLogging) {
      console.log(
        `✅ Monitor: Requisição ${requestId} concluída em ${request.duration}ms` +
          (cacheHit ? ' (cache hit)' : '')
      );
    }

    this.updateStats();
  }

  /**
   * Marca uma requisição como erro
   */
  errorRequest(requestId: string, error: string): void {
    const request = this.requests.find(r => r.id === requestId);
    if (!request) {
      console.warn(`⚠️ Monitor: Requisição ${requestId} não encontrada`);
      return;
    }

    const endTime = Date.now();
    request.endTime = endTime;
    request.duration = endTime - request.startTime;
    request.status = 'error';
    request.error = error;

    if (this.config.enableDetailedLogging) {
      console.error(`❌ Monitor: Requisição ${requestId} falhou: ${error}`);
    }

    this.updateStats();
  }

  /**
   * Obtém estatísticas atuais
   */
  getStats(): RequestStats {
    return { ...this.currentStats };
  }

  /**
   * Obtém estatísticas detalhadas por período
   */
  getDetailedStats(periodMinutes: number = 60): {
    stats: RequestStats;
    timeline: Array<{ timestamp: number; count: number; avgDuration: number }>;
    errors: Array<{ endpoint: string; error: string; count: number }>;
  } {
    const cutoff = Date.now() - periodMinutes * 60 * 1000;
    const recentRequests = this.requests.filter(r => r.startTime >= cutoff);

    // Calcular estatísticas do período
    const stats = this.calculateStats(recentRequests);

    // Criar timeline (agrupado por minutos)
    const timeline = this.createTimeline(recentRequests, periodMinutes);

    // Agrupar erros
    const errors = this.groupErrors(recentRequests);

    return { stats, timeline, errors };
  }

  /**
   * Obtém requisições mais lentas
   */
  getSlowestRequests(limit: number = 10): RequestMetric[] {
    return this.requests
      .filter(r => r.duration !== undefined)
      .sort((a, b) => (b.duration || 0) - (a.duration || 0))
      .slice(0, limit);
  }

  /**
   * Obtém endpoints mais utilizados
   */
  getTopEndpoints(limit: number = 10): Array<{
    endpoint: string;
    count: number;
    avgDuration: number;
    errorRate: number;
  }> {
    const endpointMap = new Map<
      string,
      {
        count: number;
        totalDuration: number;
        errors: number;
      }
    >();

    this.requests.forEach(request => {
      const key = request.endpoint;
      const existing = endpointMap.get(key) || { count: 0, totalDuration: 0, errors: 0 };

      existing.count++;
      if (request.duration) {
        existing.totalDuration += request.duration;
      }
      if (request.status === 'error') {
        existing.errors++;
      }

      endpointMap.set(key, existing);
    });

    return Array.from(endpointMap.entries())
      .map(([endpoint, data]) => ({
        endpoint,
        count: data.count,
        avgDuration: data.count > 0 ? data.totalDuration / data.count : 0,
        errorRate: data.count > 0 ? data.errors / data.count : 0,
      }))
      .sort((a, b) => b.count - a.count)
      .slice(0, limit);
  }

  /**
   * Exporta dados para análise
   */
  exportData(): {
    requests: RequestMetric[];
    stats: RequestStats;
    config: MonitorConfig;
    exportTime: number;
  } {
    return {
      requests: [...this.requests],
      stats: this.getStats(),
      config: this.config,
      exportTime: Date.now(),
    };
  }

  /**
   * Limpa histórico de requisições
   */
  clear(): void {
    this.requests = [];
    this.currentStats = this.initializeStats();
    console.log('🧹 Monitor: Histórico de requisições limpo');
  }

  /**
   * Gera ID único para requisição
   */
  private generateRequestId(): string {
    return `req-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Inicializa estatísticas vazias
   */
  private initializeStats(): RequestStats {
    return {
      totalRequests: 0,
      successfulRequests: 0,
      failedRequests: 0,
      cachedRequests: 0,
      averageResponseTime: 0,
      requestsPerMinute: 0,
      topEndpoints: [],
      errorRate: 0,
      cacheHitRate: 0,
    };
  }

  /**
   * Atualiza estatísticas atuais
   */
  private updateStats(): void {
    this.currentStats = this.calculateStats(this.requests);
  }

  /**
   * Calcula estatísticas para um conjunto de requisições
   */
  private calculateStats(requests: RequestMetric[]): RequestStats {
    const total = requests.length;
    const successful = requests.filter(r => r.status === 'success').length;
    const failed = requests.filter(r => r.status === 'error').length;
    const cached = requests.filter(r => r.status === 'cached').length;

    const completedRequests = requests.filter(r => r.duration !== undefined);
    const totalDuration = completedRequests.reduce((sum, r) => sum + (r.duration || 0), 0);
    const avgResponseTime =
      completedRequests.length > 0 ? totalDuration / completedRequests.length : 0;

    // Calcular requisições por minuto (últimos 5 minutos)
    const fiveMinutesAgo = Date.now() - 5 * 60 * 1000;
    const recentRequests = requests.filter(r => r.startTime >= fiveMinutesAgo);
    const requestsPerMinute = recentRequests.length / 5;

    const topEndpoints = this.getTopEndpoints(5);

    return {
      totalRequests: total,
      successfulRequests: successful,
      failedRequests: failed,
      cachedRequests: cached,
      averageResponseTime: avgResponseTime,
      requestsPerMinute,
      topEndpoints,
      errorRate: total > 0 ? failed / total : 0,
      cacheHitRate: total > 0 ? cached / total : 0,
    };
  }

  /**
   * Cria timeline de requisições
   */
  private createTimeline(
    requests: RequestMetric[],
    periodMinutes: number
  ): Array<{ timestamp: number; count: number; avgDuration: number }> {
    const buckets = new Map<number, { count: number; totalDuration: number }>();
    const bucketSize = 60000; // 1 minuto

    requests.forEach(request => {
      const bucket = Math.floor(request.startTime / bucketSize) * bucketSize;
      const existing = buckets.get(bucket) || { count: 0, totalDuration: 0 };

      existing.count++;
      if (request.duration) {
        existing.totalDuration += request.duration;
      }

      buckets.set(bucket, existing);
    });

    return Array.from(buckets.entries())
      .map(([timestamp, data]) => ({
        timestamp,
        count: data.count,
        avgDuration: data.count > 0 ? data.totalDuration / data.count : 0,
      }))
      .sort((a, b) => a.timestamp - b.timestamp);
  }

  /**
   * Agrupa erros por endpoint e tipo
   */
  private groupErrors(requests: RequestMetric[]): Array<{
    endpoint: string;
    error: string;
    count: number;
  }> {
    const errorMap = new Map<string, number>();

    requests
      .filter(r => r.status === 'error' && r.error)
      .forEach(request => {
        const key = `${request.endpoint}:${request.error}`;
        errorMap.set(key, (errorMap.get(key) || 0) + 1);
      });

    return Array.from(errorMap.entries())
      .map(([key, count]) => {
        const [endpoint, error] = key.split(':');
        return { endpoint, error, count };
      })
      .sort((a, b) => b.count - a.count);
  }

  /**
   * Remove requisições antigas para manter o limite de histórico
   */
  private trimHistory(): void {
    if (this.requests.length > this.config.maxHistorySize) {
      const excess = this.requests.length - this.config.maxHistorySize;
      this.requests.splice(0, excess);
    }
  }

  /**
   * Inicia agregação periódica de estatísticas
   */
  private startAggregation(): void {
    this.aggregationTimer = setInterval(() => {
      this.updateStats();

      if (this.config.enableDetailedLogging) {
        const stats = this.currentStats;
        console.log(
          `📈 Monitor: Stats - Total: ${stats.totalRequests}, ` +
            `Sucesso: ${stats.successfulRequests}, ` +
            `Erro: ${stats.failedRequests}, ` +
            `Cache: ${stats.cachedRequests}, ` +
            `Avg: ${stats.averageResponseTime.toFixed(2)}ms`
        );
      }
    }, this.config.aggregationInterval);
  }

  /**
   * Para a agregação periódica
   */
  destroy(): void {
    if (this.aggregationTimer) {
      clearInterval(this.aggregationTimer);
      this.aggregationTimer = undefined;
    }
  }
}

// Instância singleton do monitor
export const requestMonitor = new RequestMonitor({
  maxHistorySize: 2000,
  aggregationInterval: 30000, // 30 segundos
  enableDetailedLogging: process.env.NODE_ENV === 'development',
  trackUserAgent: false,
});

// Função auxiliar para instrumentar requisições automaticamente
export const instrumentRequest = async <T>(
  endpoint: string,
  requestFn: () => Promise<T>,
  method: string = 'GET',
  params: any = {}
): Promise<T> => {
  const requestId = requestMonitor.startRequest(endpoint, method, params);

  try {
    const result = await requestFn();

    // Tentar calcular tamanho da resposta
    let responseSize: number | undefined;
    try {
      responseSize = JSON.stringify(result).length;
    } catch {
      // Ignorar se não conseguir serializar
    }

    requestMonitor.endRequest(requestId, responseSize);
    return result;
  } catch (error) {
    requestMonitor.errorRequest(requestId, error instanceof Error ? error.message : String(error));
    throw error;
  }
};

// Limpeza automática ao sair
window.addEventListener('beforeunload', () => {
  requestMonitor.destroy();
});
