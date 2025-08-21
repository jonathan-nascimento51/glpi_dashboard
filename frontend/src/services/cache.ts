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
  lastAccessed?: number;
  accessCount?: number;
  originalTtl?: number;
  priority?: 'low' | 'medium' | 'high';
}

// Interface para configuração do cache
interface CacheConfig {
  ttl: number; // Time to live em milissegundos
  maxSize: number; // Tamanho máximo do cache
  autoActivate?: boolean;
  performanceThreshold?: number; // ms - tempo mínimo de resposta para ativar cache
  usageThreshold?: number; // número de chamadas repetidas para ativar cache
  enableDynamicTtl?: boolean; // Habilita TTL dinâmico
  minTtl?: number; // TTL mínimo em milissegundos
  maxTtl?: number; // TTL máximo em milissegundos
  ttlMultiplier?: number; // Multiplicador para TTL baseado na frequência
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
    clears: 0,
  };
  private requestTimes = new Map<string, number[]>(); // Armazena tempos de resposta por chave
  private requestCounts = new Map<string, number>(); // Conta requisições por chave
  private isActive = true; // Cache ativo por padrão

  constructor(config: Partial<CacheConfig> = {}) {
    this.config = {
      ttl: config.ttl || 5 * 60 * 1000, // 5 minutos por padrão
      maxSize: config.maxSize || 100, // Máximo 100 entradas
      autoActivate: config.autoActivate !== undefined ? config.autoActivate : true,
      performanceThreshold: config.performanceThreshold || 500, // 500ms
      usageThreshold: config.usageThreshold || 3, // 3 chamadas repetidas
      enableDynamicTtl: config.enableDynamicTtl !== undefined ? config.enableDynamicTtl : true,
      minTtl: config.minTtl || 30 * 1000, // 30 segundos mínimo
      maxTtl: config.maxTtl || 30 * 60 * 1000, // 30 minutos máximo
      ttlMultiplier: config.ttlMultiplier || 1.5, // Multiplicador de 1.5x
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

  /**
   * Calcula TTL dinâmico baseado na frequência de acesso
   */
  private calculateDynamicTtl(key: string, accessCount: number = 0): number {
    if (!this.config.enableDynamicTtl) {
      return this.config.ttl;
    }

    const baseTtl = this.config.ttl;
    const minTtl = this.config.minTtl!;
    const maxTtl = this.config.maxTtl!;
    const multiplier = this.config.ttlMultiplier!;

    // TTL baseado na frequência de acesso
    let dynamicTtl = baseTtl;

    if (accessCount > 10) {
      // Dados muito acessados: TTL maior
      dynamicTtl = Math.min(baseTtl * multiplier * 2, maxTtl);
    } else if (accessCount > 5) {
      // Dados moderadamente acessados: TTL aumentado
      dynamicTtl = Math.min(baseTtl * multiplier, maxTtl);
    } else if (accessCount < 2) {
      // Dados pouco acessados: TTL reduzido
      dynamicTtl = Math.max(baseTtl / multiplier, minTtl);
    }

    // Ajuste baseado no tempo de resposta médio
    const avgResponseTime = this.getAverageResponseTimeForKey(key);
    if (avgResponseTime > 1000) {
      // Respostas lentas: cache por mais tempo
      dynamicTtl = Math.min(dynamicTtl * 1.5, maxTtl);
    } else if (avgResponseTime < 200) {
      // Respostas rápidas: cache por menos tempo
      dynamicTtl = Math.max(dynamicTtl * 0.8, minTtl);
    }

    return Math.round(dynamicTtl);
  }

  /**
   * Obtém tempo de resposta médio para uma chave específica
   */
  private getAverageResponseTimeForKey(key: string): number {
    const times = this.requestTimes.get(key);
    if (!times || times.length === 0) return 0;
    return times.reduce((sum, time) => sum + time, 0) / times.length;
  }

  /**
   * Determina a prioridade de uma entrada baseada nos padrões de uso
   */
  private calculatePriority(accessCount: number, avgResponseTime: number): 'low' | 'medium' | 'high' {
    if (accessCount > 10 || avgResponseTime > 1000) {
      return 'high';
    } else if (accessCount > 5 || avgResponseTime > 500) {
      return 'medium';
    }
    return 'low';
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
    this.checkActivation(responseTime, count);
  }

  private checkActivation(responseTime: number, requestCount: number): void {
    if (this.isActive) return;

    const { performanceThreshold, usageThreshold } = this.config;

    // Ativa se a resposta for lenta OU se houver muitas requisições repetidas
    const shouldActivate = responseTime >= performanceThreshold! || requestCount >= usageThreshold!;

    if (shouldActivate) {
      this.isActive = true;
      // Cache ativado automaticamente para padrão detectado
    }
  }

  /**
   * Remove a entrada mais antiga se o cache estiver cheio
   */
  private evictOldest(): void {
    if (this.cache.size >= this.config.maxSize) {
      // Se TTL dinâmico estiver habilitado, remove a entrada com menor prioridade
      if (this.config.enableDynamicTtl) {
        let lowestPriorityKey: string | null = null;
        let lowestPriorityValue = 'high';
        
        for (const [key, entry] of this.cache.entries()) {
          const priorityOrder = { 'low': 0, 'medium': 1, 'high': 2 };
          const currentPriority = priorityOrder[entry.priority || 'low'];
          const lowestPriority = priorityOrder[lowestPriorityValue];
          
          if (currentPriority < lowestPriority) {
            lowestPriorityValue = entry.priority || 'low';
            lowestPriorityKey = key;
          }
        }
        
        if (lowestPriorityKey) {
          this.cache.delete(lowestPriorityKey);
          return;
        }
      }
      
      // Fallback: remove a entrada mais antiga
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
    // Cache: Tentando armazenar dados
    if (!this.isActive) {
      // Cache: Não armazenado - cache inativo
      return; // Não armazena se cache não estiver ativo
    }

    const key = this.generateKey(params);
    const now = Date.now();
    const existingEntry = this.cache.get(key);
    const accessCount = existingEntry?.accessCount || 0;
    const avgResponseTime = this.getAverageResponseTimeForKey(key);
    
    // Calcula TTL dinâmico
    const dynamicTtl = this.calculateDynamicTtl(key, accessCount);
    const priority = this.calculatePriority(accessCount, avgResponseTime);

    this.evictOldest();

    this.cache.set(key, {
      data,
      timestamp: now,
      expiresAt: now + dynamicTtl,
      lastAccessed: now,
      accessCount: accessCount,
      originalTtl: this.config.ttl,
      priority,
    });

    this.stats.sets++;
    // Cache: Dados armazenados com TTL dinâmico e prioridade calculada
  }

  /**
   * Recupera dados do cache se válidos
   */
  get(params: Record<string, any>): T | null {
    if (!this.isActive) {
      this.stats.misses++;
      return null; // Não recupera se cache não estiver ativo
    }

    const key = this.generateKey(params);
    const entry = this.cache.get(key);

    if (!entry) {
      this.stats.misses++;
      // Cache: Miss - entrada não encontrada
      return null;
    }

    if (this.isExpired(entry)) {
      this.cache.delete(key);
      this.stats.misses++;
      // Cache: Entrada expirada removida
      return null;
    }

    // Cache hit
    this.stats.hits++;
    const now = Date.now();
    
    // Atualizar estatísticas de acesso
    entry.lastAccessed = now;
    entry.accessCount = (entry.accessCount || 0) + 1;
    
    // Recalcular TTL dinâmico se habilitado
    if (this.config.enableDynamicTtl && entry.accessCount && entry.accessCount % 5 === 0) {
      const newTtl = this.calculateDynamicTtl(key, entry.accessCount);
      const avgResponseTime = this.getAverageResponseTimeForKey(key);
      entry.expiresAt = now + newTtl;
      entry.priority = this.calculatePriority(entry.accessCount, avgResponseTime);
      // Cache: TTL recalculado com nova prioridade
    }

    // Cache: Hit - dados recuperados com sucesso

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
    // Cache: Todos os dados foram limpos
  }

  /**
   * Remove uma entrada específica do cache
   */
  delete(params: Record<string, any>): boolean {
    const key = this.generateKey(params);
    const deleted = this.cache.delete(key);
    if (deleted) {
      this.stats.deletes++;
      // Cache: Entrada removida com sucesso
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
    isActive: boolean;
    totalRequests: number;
    avgResponseTime: number;
    memoryUsage: number;
    dynamicTtlEnabled?: boolean;
    priorityDistribution?: { high: number; medium: number; low: number };
    averageTtl?: number;
  } {
    const entries = Array.from(this.cache.entries()).map(([key, entry]) => ({
      key,
      timestamp: entry.timestamp,
      expiresAt: entry.expiresAt,
    }));

    const stats: any = {
      ...this.stats,
      size: this.cache.size,
      maxSize: this.config.maxSize,
      ttl: this.config.ttl,
      entries,
      hitRate: this.stats.hits / (this.stats.hits + this.stats.misses) || 0,
      isActive: this.isActive,
      totalRequests: Array.from(this.requestCounts.values()).reduce((sum, count) => sum + count, 0),
      avgResponseTime: this.getAverageResponseTime(),
      memoryUsage: this.getMemoryUsage(),
    };

    // Adicionar estatísticas de TTL dinâmico se habilitado
    if (this.config.enableDynamicTtl) {
      stats.dynamicTtlEnabled = true;
      
      // Distribuição de prioridades
      const priorityCount = { high: 0, medium: 0, low: 0 };
      let totalTtl = 0;
      let entryCount = 0;
      
      for (const entry of this.cache.values()) {
        const priority = entry.priority || 'low';
        priorityCount[priority]++;
        
        const entryTtl = entry.expiresAt - entry.timestamp;
        totalTtl += entryTtl;
        entryCount++;
      }
      
      stats.priorityDistribution = priorityCount;
      stats.averageTtl = entryCount > 0 ? totalTtl / entryCount : 0;
    }

    return stats;
  }

  private getMemoryUsage(): number {
    let totalSize = 0;
    for (const [key, entry] of this.cache.entries()) {
      totalSize += JSON.stringify({ key, entry }).length;
    }
    return totalSize;
  }

  /**
   * Método para pré-aquecer o cache com dados importantes
   */
  preWarm(params: Record<string, any>, data: T): void {
    this.set(params, data);
    // Cache: Dados pré-aquecidos
  }

  /**
   * Método para invalidar cache por padrão
   */
  invalidatePattern(pattern: string): void {
    const regex = new RegExp(pattern);
    let deletedCount = 0;
    for (const [key] of this.cache.entries()) {
      if (regex.test(key)) {
        this.cache.delete(key);
        deletedCount++;
      }
    }
    // Cache: Entradas invalidadas por padrão
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
    // Cache ativado manualmente
  }

  forceDeactivate(): void {
    this.isActive = false;
    this.clear();
    // Cache desativado manualmente
  }

  /**
   * Atualiza o TTL de uma entrada específica
   */
  refresh(params: Record<string, any>): boolean {
    const key = this.generateKey(params);
    const entry = this.cache.get(key);

    if (entry && !this.isExpired(entry)) {
      entry.expiresAt = Date.now() + this.config.ttl;
      // Cache: TTL renovado
      return true;
    }

    return false;
  }
}

// Instâncias de cache para diferentes tipos de dados
export const metricsCache = new LocalCache<any>({
  ttl: 5 * 60 * 1000, // 5 minutos
  maxSize: 100,
  autoActivate: true,
  performanceThreshold: 1000, // 1 segundo
  enableDynamicTtl: true,
  minTtl: 2 * 60 * 1000, // 2 minutos mínimo
  maxTtl: 15 * 60 * 1000, // 15 minutos máximo
  ttlMultiplier: 1.5
});

export const systemStatusCache = new LocalCache<any>({
  ttl: 30 * 1000, // 30 segundos
  maxSize: 50,
  autoActivate: true,
  performanceThreshold: 500, // 500ms
  enableDynamicTtl: true,
  minTtl: 15 * 1000, // 15 segundos mínimo
  maxTtl: 2 * 60 * 1000, // 2 minutos máximo
  ttlMultiplier: 2.0
});

export const technicianRankingCache = new LocalCache<any[]>({
  ttl: 10 * 60 * 1000, // 10 minutos
  maxSize: 20,
  autoActivate: true,
  performanceThreshold: 2000, // 2 segundos
  enableDynamicTtl: true,
  minTtl: 5 * 60 * 1000, // 5 minutos mínimo
  maxTtl: 30 * 60 * 1000, // 30 minutos máximo
  ttlMultiplier: 1.2
});

export const newTicketsCache = new LocalCache<any[]>({
  ttl: 2 * 60 * 1000, // 2 minutos
  maxSize: 200,
  autoActivate: true,
  performanceThreshold: 800, // 800ms
  enableDynamicTtl: true,
  minTtl: 1 * 60 * 1000, // 1 minuto mínimo
  maxTtl: 10 * 60 * 1000, // 10 minutos máximo
  ttlMultiplier: 1.8
});

// Utilitário para limpar todos os caches
export const clearAllCaches = (): void => {
  metricsCache.clear();
  systemStatusCache.clear();
  technicianRankingCache.clear();
  newTicketsCache.clear();
  // Cache: Todos os caches foram limpos
};

// Utilitário para obter estatísticas de todos os caches
export const getAllCacheStats = () => {
  return {
    metrics: metricsCache.getStats(),
    systemStatus: systemStatusCache.getStats(),
    technicianRanking: technicianRankingCache.getStats(),
    newTickets: newTicketsCache.getStats(),
  };
};

export { LocalCache };
export default LocalCache;
