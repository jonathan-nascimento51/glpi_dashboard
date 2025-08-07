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
}

/**
 * Classe para gerenciar cache local com expiração automática
 */
class LocalCache<T> {
  private cache = new Map<string, CacheEntry<T>>();
  private config: CacheConfig;

  constructor(config: Partial<CacheConfig> = {}) {
    this.config = {
      ttl: config.ttl || 5 * 60 * 1000, // 5 minutos por padrão
      maxSize: config.maxSize || 100 // Máximo 100 entradas
    };

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
    const key = this.generateKey(params);
    const now = Date.now();
    
    this.evictOldest();
    
    this.cache.set(key, {
      data,
      timestamp: now,
      expiresAt: now + this.config.ttl
    });

    console.log(`📦 Cache: Armazenado dados para chave: ${key}`);
  }

  /**
   * Recupera dados do cache se válidos
   */
  get(params: Record<string, any>): T | null {
    const key = this.generateKey(params);
    const entry = this.cache.get(key);

    if (!entry) {
      console.log(`📦 Cache: Miss para chave: ${key}`);
      return null;
    }

    if (this.isExpired(entry)) {
      this.cache.delete(key);
      console.log(`📦 Cache: Expirado para chave: ${key}`);
      return null;
    }

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
   * Remove uma entrada específica do cache
   */
  delete(params: Record<string, any>): boolean {
    const key = this.generateKey(params);
    const deleted = this.cache.delete(key);
    if (deleted) {
      console.log(`📦 Cache: Removido dados para chave: ${key}`);
    }
    return deleted;
  }

  /**
   * Limpa todo o cache
   */
  clear(): void {
    this.cache.clear();
    console.log('📦 Cache: Todos os dados foram limpos');
  }

  /**
   * Retorna estatísticas do cache
   */
  getStats(): {
    size: number;
    maxSize: number;
    ttl: number;
    entries: Array<{ key: string; timestamp: number; expiresAt: number }>;
  } {
    const entries = Array.from(this.cache.entries()).map(([key, entry]) => ({
      key,
      timestamp: entry.timestamp,
      expiresAt: entry.expiresAt
    }));

    return {
      size: this.cache.size,
      maxSize: this.config.maxSize,
      ttl: this.config.ttl,
      entries
    };
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