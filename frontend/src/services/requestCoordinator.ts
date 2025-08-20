/**
 * Sistema centralizado de coordenação de requisições
 * Evita múltiplas chamadas simultâneas e implementa debouncing/throttling inteligente
 */

interface PendingRequest {
  promise: Promise<any>;
  timestamp: number;
  key: string;
}

interface RequestConfig {
  debounceMs?: number;
  throttleMs?: number;
  maxConcurrent?: number;
  cacheMs?: number;
}

class RequestCoordinator {
  private pendingRequests = new Map<string, PendingRequest>();
  private lastRequestTimes = new Map<string, number>();
  private requestCounts = new Map<string, number>();
  private cache = new Map<string, { data: any; timestamp: number }>();
  private readonly defaultConfig: RequestConfig = {
    debounceMs: 300,
    throttleMs: 1000,
    maxConcurrent: 3,
    cacheMs: 30000, // 30 segundos
  };

  /**
   * Coordena uma requisição com debouncing, throttling e cache
   */
  async coordinateRequest<T>(
    key: string,
    requestFn: () => Promise<T>,
    config: RequestConfig = {}
  ): Promise<T> {
    const finalConfig = { ...this.defaultConfig, ...config };
    const now = Date.now();

    // Verificar cache primeiro
    const cached = this.cache.get(key);
    if (cached && now - cached.timestamp < finalConfig.cacheMs!) {
      console.log(`📦 Cache hit para ${key}`);
      return cached.data;
    }

    // Verificar se já existe uma requisição pendente para a mesma chave
    const existing = this.pendingRequests.get(key);
    if (existing) {
      console.log(`⏳ Reutilizando requisição pendente para ${key}`);
      return existing.promise;
    }

    // Verificar throttling
    const lastRequestTime = this.lastRequestTimes.get(key) || 0;
    const timeSinceLastRequest = now - lastRequestTime;
    if (timeSinceLastRequest < finalConfig.throttleMs!) {
      const waitTime = finalConfig.throttleMs! - timeSinceLastRequest;
      console.log(`🚦 Throttling ${key} - aguardando ${waitTime}ms`);
      await new Promise(resolve => setTimeout(resolve, waitTime));
    }

    // Verificar limite de requisições concorrentes
    const currentConcurrent = this.pendingRequests.size;
    if (currentConcurrent >= finalConfig.maxConcurrent!) {
      console.log(
        `⚠️ Limite de requisições concorrentes atingido (${currentConcurrent}/${finalConfig.maxConcurrent})`
      );
      // Aguardar uma requisição terminar
      await Promise.race(Array.from(this.pendingRequests.values()).map(r => r.promise));
    }

    // Executar a requisição
    console.log(`🚀 Executando requisição para ${key}`);
    const promise = this.executeRequest(key, requestFn, finalConfig);

    this.pendingRequests.set(key, {
      promise,
      timestamp: now,
      key,
    });

    this.lastRequestTimes.set(key, now);
    this.incrementRequestCount(key);

    return promise;
  }

  private async executeRequest<T>(
    key: string,
    requestFn: () => Promise<T>,
    config: RequestConfig
  ): Promise<T> {
    try {
      const startTime = Date.now();
      const result = await requestFn();
      const duration = Date.now() - startTime;

      console.log(`✅ Requisição ${key} concluída em ${duration}ms`);

      // Armazenar no cache
      if (config.cacheMs! > 0) {
        this.cache.set(key, {
          data: result,
          timestamp: Date.now(),
        });
      }

      return result;
    } catch (error) {
      console.error(`❌ Erro na requisição ${key}:`, error);
      throw error;
    } finally {
      this.pendingRequests.delete(key);
    }
  }

  private incrementRequestCount(key: string): void {
    const current = this.requestCounts.get(key) || 0;
    this.requestCounts.set(key, current + 1);
  }

  /**
   * Obtém estatísticas de uso
   */
  getStats(): Record<string, any> {
    return {
      pendingRequests: this.pendingRequests.size,
      cacheEntries: this.cache.size,
      requestCounts: Object.fromEntries(this.requestCounts),
      lastRequestTimes: Object.fromEntries(this.lastRequestTimes),
    };
  }

  /**
   * Limpa o cache expirado
   */
  cleanExpiredCache(): void {
    const now = Date.now();
    for (const [key, entry] of this.cache.entries()) {
      if (now - entry.timestamp > this.defaultConfig.cacheMs!) {
        this.cache.delete(key);
      }
    }
  }

  /**
   * Invalida cache para uma chave específica
   */
  invalidateCache(key: string): void {
    this.cache.delete(key);
    console.log(`🗑️ Cache invalidado para ${key}`);
  }

  /**
   * Cancela todas as requisições pendentes
   */
  cancelAllRequests(): void {
    this.pendingRequests.clear();
    console.log('🛑 Todas as requisições pendentes foram canceladas');
  }
}

// Instância singleton
export const requestCoordinator = new RequestCoordinator();

// Limpeza automática do cache a cada 5 minutos
setInterval(() => {
  requestCoordinator.cleanExpiredCache();
}, 300000);

export default requestCoordinator;
