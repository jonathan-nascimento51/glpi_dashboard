/**
 * Sistema de Cache Local para API
 * 
 * Implementa um cache em memória com tempo de expiração para otimizar
 * chamadas da API baseadas em combinações de filtros.
 */

// Interface para entrada do cache
interface CacheEntry<T> {
  data: T;
  timestamp: number;
  expiresAt: number;
}

// Interface para configuração do cache
interface CacheConfig {
  ttl: number; // Time to live em milissegundos
  maxSize: number; // Tamanho máximo do cache
  autoActivate?: boolean;
  performanceThreshold?: number; // ms - tempo mínimo de resposta para ativar cache
  usageThreshold?: number; // número de chamadas repetidas para ativar cache
}

/**
 * Classe para gerenciar cache local com expiração automática
 */
class LocalCache<T> {
  private cache = new Map<string, CacheEntry<T>>();
  private config: CacheConfig;
  private stats = {
    hits: 0,
    misses: 0,
    sets: 0,
    deletes: 0,
    clears: 0
  };
  private requestTimes = new Map<string, number[]>(); // Armazena tempos de resposta por chave
  private requestCounts = new Map<string, number>(); // Conta requisições por chave
  private isActive = false; // Cache ativo ou não

  constructor(config: Partial<CacheConfig> = {}) {
    this.config = {
      ttl: config.ttl || 5 * 60 * 1000, // 5 minutos por padrão
      maxSize: config.maxSize || 100, // Máximo 100 entradas
      autoActivate: config.autoActivate !== undefined ? config.autoActivate : true,
      performanceThreshold: config.performanceThreshold || 500, // 500ms
      usageThreshold: config.usageThreshold || 3 // 3 chamadas repetidas
    };
    this.isActive = !this.config.autoActivate; // Se não é auto, fica sempre ativo

    // Limpar cache expirado a cada minuto
    setInterval(() => this.cleanExpired(), 60 * 1000);
  }

  /**
   * Gera uma chave única baseada nos parâmetros fornecidos
   */
  private generateKey(params: Record<string, any>): string {
    // Ordena as chaves para garantir consistência
    const sortedKeys = Object.keys(params).sort();
    const keyParts = sortedKeys.map(key => `${key}:${params[key]}`);
    return keyParts.join('|');
  }

  /**
   * Verifica se uma entrada está expirada
   */
  private isExpired(entry: CacheEntry<T>): boolean {
    return Date.now() > entry.expiresAt;
  }

  /**
   * Remove entradas expiradas do cache
   */
  private cleanExpired(): void {
    const now = Date.now();
    for (const [key, entry] of this.cache.entries()) {
      if (now > entry.expiresAt) {
        this.cache.delete(key);
      }
    }
  }

  // Monitora performance de uma requisição
  recordRequestTime(key: string, responseTime: number): void {
    if (!this.config.autoActivate) return;

    // Registra tempo de resposta
    if (!this.requestTimes.has(key)) {
      this.requestTimes.set(key, []);
    }
    const times = this.requestTimes.get(key)!;
    times.push(responseTime);
    
    // Mantém apenas os últimos 10 tempos
    if (times.length > 10) {
      times.shift();
    }

    // Conta requisições
    const count = (this.requestCounts.get(key) || 0) + 1;
    this.requestCounts.set(key, count);

    // Verifica se deve ativar o cache
    this.checkActivation(key, responseTime, count);
  }

  private checkActivation(_key: string, responseTime: number, requestCount: number): void {
    if (this.isActive) return;

    const { performanceThreshold, usageThreshold } = this.config;
    
    // Ativa se a resposta for lenta OU se houver muitas requisições repetidas
    const shouldActivate = 
      responseTime >= performanceThreshold! || 
      requestCount >= usageThreshold!;

    if (shouldActivate) {
      this.isActive = true;
      console.log(`🚀 Cache ativado automaticamente para padrão detectado: ${responseTime}ms, ${requestCount} requisições`);
    }
  }

  /**
   * Remove a entrada mais antiga se o cache estiver cheio
   */
  private evictOldest(): void {
    if (this.cache.size >= this.config.maxSize) {
      const oldestKey = this.cache.keys().next().value;
      if (oldestKey) {
        this.cache.delete(oldestKey);
      }
    }
  }

  /**
   * Armazena dados no cache
   */
  set(params: Record<string, any>, data: T): void {
    console.log(`📦 Cache: Tentando armazenar - ativo: ${this.isActive}, dados:`, data);
    if (!this.isActive) {
      console.log(`📦 Cache: Não armazenado - cache inativo`);
      return; // Não armazena se cache não estiver ativo
    }
    
    const key = this.generateKey(params);
    const now = Date.now();
    
    this.evictOldest();
    
    this.cache.set(key, {
      data,
      timestamp: now,
      expiresAt: now + this.config.ttl
    });

    this.stats.sets++;
    console.log(`📦 Cache: Armazenado dados para chave: ${key}`, data);
  }

  /**
   * Recupera dados do cache se válidos
   */
  get(params: Record<string, any>): T | null {
    if (!this.isActive) return null; // Não recupera se cache não estiver ativo
    
    const key = this.generateKey(params);
    const entry = this.cache.get(key);

    if (!entry) {
      this.stats.misses++;
      console.log(`📦 Cache: Miss para chave: ${key}`);
      return null;
    }

    if (this.isExpired(entry)) {
      this.cache.delete(key);
      this.stats.misses++;
      console.log(`📦 Cache: Expirado para chave: ${key}`);
      return null;
    }

    this.stats.hits++;
    console.log(`📦 Cache: Hit para chave: ${key}`);
    return entry.data;
  }

  /**
   * Verifica se existe uma entrada válida no cache
   */
  has(params: Record<string, any>): boolean {
    return this.get(params) !== null;
  }

  /**
   * Limpa todo o cache
   */
  clear(): void {
    this.cache.clear();
    this.requestTimes.clear();
    this.requestCounts.clear();
    this.stats.clears++;
    console.log('🧹 Cache: Todos os dados foram limpos');
  }

  /**
   * Remove uma entrada específica do cache
   */
  delete(params: Record<string, any>): boolean {
    const key = this.generateKey(params);
    const deleted = this.cache.delete(key);
    if (deleted) {
      this.stats.deletes++;
      console.log(`📦 Cache: Removido dados para chave: ${key}`);
    }
    return deleted;
  }

  /**
   * Retorna estatísticas do cache
   */
  getStats(): {
    size: number;
    maxSize: number;
    ttl: number;
    entries: Array<{ key: string; timestamp: number; expiresAt: number }>;
    hits: number;
    misses: number;
    sets: number;
    deletes: number;
    clears: number;
    hitRate: number;
    missRate: number;
    isActive: boolean;
    totalRequests: number;
    avgResponseTime: number;
  } {
    const entries = Array.from(this.cache.entries()).map(([key, entry]) => ({
      key,
      timestamp: entry.timestamp,
      expiresAt: entry.expiresAt
    }));

    const totalRequests = this.stats.hits + this.stats.misses;
    return {
      ...this.stats,
      size: this.cache.size,
      maxSize: this.config.maxSize,
      ttl: this.config.ttl,
      entries,
      hitRate: totalRequests > 0 ? this.stats.hits / totalRequests : 0,
      missRate: totalRequests > 0 ? this.stats.misses / totalRequests : 0,
      isActive: this.isActive,
      totalRequests: Array.from(this.requestCounts.values()).reduce((sum, count) => sum + count, 0),
      avgResponseTime: this.getAverageResponseTime()
    };
  }

  private getAverageResponseTime(): number {
    const allTimes = Array.from(this.requestTimes.values()).flat();
    if (allTimes.length === 0) return 0;
    return allTimes.reduce((sum, time) => sum + time, 0) / allTimes.length;
  }

  isActivated(): boolean {
    return this.isActive;
  }

  forceActivate(): void {
    this.isActive = true;
    console.log('🔧 Cache ativado manualmente');
  }

  forceDeactivate(): void {
    this.isActive = false;
    this.clear();
    console.log('🔧 Cache desativado manualmente');
  }

  /**
   * Atualiza o TTL de uma entrada específica
   */
  refresh(params: Record<string, any>): boolean {
    const key = this.generateKey(params);
    const entry = this.cache.get(key);
    
    if (entry && !this.isExpired(entry)) {
      entry.expiresAt = Date.now() + this.config.ttl;
      console.log(`📦 Cache: TTL renovado para chave: ${key}`);
      return true;
    }
    
    return false;
  }
}

// Instâncias de cache para diferentes tipos de dados
export const metricsCache = new LocalCache<any>({
  ttl: 5 * 60 * 1000, // 5 minutos
  maxSize: 50
});

export const systemStatusCache = new LocalCache<any>({
  ttl: 2 * 60 * 1000, // 2 minutos
  maxSize: 10
});

export const technicianRankingCache = new LocalCache<any[]>({
  ttl: 10 * 60 * 1000, // 10 minutos
  maxSize: 20
});

export const newTicketsCache = new LocalCache<any[]>({
  ttl: 1 * 60 * 1000, // 1 minuto
  maxSize: 30
});

// Utilitário para limpar todos os caches
export const clearAllCaches = (): void => {
  metricsCache.clear();
  systemStatusCache.clear();
  technicianRankingCache.clear();
  newTicketsCache.clear();
  console.log('📦 Cache: Todos os caches foram limpos');
};

// Utilitário para obter estatísticas de todos os caches
export const getAllCacheStats = () => {
  return {
    metrics: metricsCache.getStats(),
    systemStatus: systemStatusCache.getStats(),
    technicianRanking: technicianRankingCache.getStats(),
    newTickets: newTicketsCache.getStats()
  };
};

export { LocalCache };
export default LocalCache;