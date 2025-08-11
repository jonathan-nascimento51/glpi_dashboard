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

// Interface para métricas de performance do cache
interface CacheMetrics {
  hitRate: number;
  missRate: number;
  avgResponseTime: number;
  avgDataAge: number;
  invalidationFrequency: number;
  cacheSize: number;
  maxSize: number;
  totalRequests: number;
  hits: number;
  misses: number;
  sets: number;
  deletes: number;
  clears: number;
  isActive: boolean;
  performanceScore: number; // 0-100
  alerts: CacheAlert[];
}

// Interface para alertas de cache
interface CacheAlert {
  type: 'low_hit_rate' | 'high_response_time' | 'old_data' | 'cache_full' | 'high_invalidation';
  severity: 'low' | 'medium' | 'high';
  message: string;
  timestamp: number;
  value?: number;
  threshold?: number;
}

// Interface para logs estruturados
interface CacheLog {
  timestamp: number;
  level: 'info' | 'warn' | 'error' | 'debug';
  event: string;
  data?: any;
  metrics?: Partial<CacheMetrics>;
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
  
  // Métricas avançadas
  private invalidationCount = 0;
  private invalidationTimes: number[] = [];
  private alerts: CacheAlert[] = [];
  private logs: CacheLog[] = [];
  private readonly MAX_LOGS = 1000;
  private readonly MAX_ALERTS = 50;
  
  // Thresholds para alertas
  private readonly ALERT_THRESHOLDS = {
    LOW_HIT_RATE: 0.5, // 50%
    HIGH_RESPONSE_TIME: 1000, // 1s
    OLD_DATA_AGE: 15 * 60 * 1000, // 15 minutos
    CACHE_FULL_RATIO: 0.9, // 90%
    HIGH_INVALIDATION_RATE: 10 // 10 invalidações por minuto
  };

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
    
    // Limpar logs e alertas antigos a cada hora
    setInterval(() => this.cleanOldLogs(), 60 * 60 * 1000);
    
    this.log('info', 'cache_initialized', { config: this.config });
  }
  
  /**
   * Adiciona um log estruturado
   */
  private log(level: CacheLog['level'], event: string, data?: any, metrics?: Partial<CacheMetrics>): void {
    const logEntry: CacheLog = {
      timestamp: Date.now(),
      level,
      event,
      data,
      metrics
    };
    
    this.logs.push(logEntry);
    
    // Manter apenas os últimos logs
    if (this.logs.length > this.MAX_LOGS) {
      this.logs = this.logs.slice(-this.MAX_LOGS);
    }
    
    // Log no console em desenvolvimento
    if (process.env.NODE_ENV === 'development') {
      console.log(`[Cache ${level.toUpperCase()}] ${event}:`, data);
    }
  }
  
  /**
   * Adiciona um alerta
   */
  private addAlert(type: CacheAlert['type'], severity: CacheAlert['severity'], message: string, value?: number, threshold?: number): void {
    const alert: CacheAlert = {
      type,
      severity,
      message,
      timestamp: Date.now(),
      value,
      threshold
    };
    
    this.alerts.push(alert);
    
    // Manter apenas os últimos alertas
    if (this.alerts.length > this.MAX_ALERTS) {
      this.alerts = this.alerts.slice(-this.MAX_ALERTS);
    }
    
    this.log('warn', 'cache_alert_generated', { alert });
  }
  
  /**
   * Limpa logs e alertas antigos
   */
  private cleanOldLogs(): void {
    const oneHourAgo = Date.now() - (60 * 60 * 1000);
    
    this.logs = this.logs.filter(log => log.timestamp > oneHourAgo);
    this.alerts = this.alerts.filter(alert => alert.timestamp > oneHourAgo);
    
    this.log('debug', 'old_logs_cleaned', { 
      remainingLogs: this.logs.length, 
      remainingAlerts: this.alerts.length 
    });
  }

  /**
   * Gera uma chave única baseada nos parâmetros fornecidos
   */
  private generateKey(params: Record<string, any>): string {
    // Ordena as chaves para garantir consistência
    const sortedKeys = Object.keys(params).sort();
    const keyParts = sortedKeys.map(key => {
      const value = params[key];
      // Serializa objetos complexos corretamente
      const serializedValue = typeof value === 'object' && value !== null 
        ? JSON.stringify(value) 
        : String(value);
      return `${key}:${serializedValue}`;
    });
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
    const entries = Array.from(this.cache.entries());
    let expiredCount = 0;
    for (const [key, entry] of entries) {
      if (now > entry.expiresAt) {
        this.cache.delete(key);
        this.stats.deletes++;
        expiredCount++;
      }
    }
    
    if (expiredCount > 0) {
      this.log('debug', 'expired_entries_cleaned', { count: expiredCount });
    }
  }
  
  /**
   * Monitora e analisa a performance do cache
   */
  trackCachePerformance(): CacheMetrics {
    const now = Date.now();
    const totalRequests = this.stats.hits + this.stats.misses;
    const hitRate = totalRequests > 0 ? this.stats.hits / totalRequests : 0;
    const missRate = 1 - hitRate;
    
    // Calcular idade média dos dados
    const avgDataAge = this.calculateAverageDataAge();
    
    // Calcular frequência de invalidação (por minuto)
    const oneMinuteAgo = now - (60 * 1000);
    const recentInvalidations = this.invalidationTimes.filter(time => time > oneMinuteAgo).length;
    
    // Calcular score de performance (0-100)
    const performanceScore = this.calculatePerformanceScore(hitRate, avgDataAge, recentInvalidations);
    
    const metrics: CacheMetrics = {
      hitRate,
      missRate,
      avgResponseTime: this.getAverageResponseTime(),
      avgDataAge,
      invalidationFrequency: recentInvalidations,
      cacheSize: this.cache.size,
      maxSize: this.config.maxSize,
      totalRequests,
      hits: this.stats.hits,
      misses: this.stats.misses,
      sets: this.stats.sets,
      deletes: this.stats.deletes,
      clears: this.stats.clears,
      isActive: this.isActive,
      performanceScore,
      alerts: [...this.alerts]
    };
    
    // Verificar e gerar alertas
    this.checkAndGenerateAlerts(metrics);
    
    // Log das métricas
    this.log('info', 'performance_tracked', null, metrics);
    
    return metrics;
  }
  
  /**
   * Calcula a idade média dos dados no cache
   */
  private calculateAverageDataAge(): number {
    if (this.cache.size === 0) return 0;
    
    const now = Date.now();
    let totalAge = 0;
    
    for (const entry of this.cache.values()) {
      totalAge += now - entry.timestamp;
    }
    
    return totalAge / this.cache.size;
  }
  
  /**
   * Calcula o score de performance (0-100)
   */
  private calculatePerformanceScore(hitRate: number, avgDataAge: number, invalidationRate: number): number {
    let score = 100;
    
    // Penalizar baixo hit rate (peso: 40%)
    score -= (1 - hitRate) * 40;
    
    // Penalizar dados muito antigos (peso: 30%)
    const ageRatio = Math.min(avgDataAge / this.config.ttl, 1);
    score -= ageRatio * 30;
    
    // Penalizar alta frequência de invalidação (peso: 20%)
    const invalidationPenalty = Math.min(invalidationRate / this.ALERT_THRESHOLDS.HIGH_INVALIDATION_RATE, 1) * 20;
    score -= invalidationPenalty;
    
    // Penalizar cache cheio (peso: 10%)
    const fullnessRatio = this.cache.size / this.config.maxSize;
    if (fullnessRatio > this.ALERT_THRESHOLDS.CACHE_FULL_RATIO) {
      score -= (fullnessRatio - this.ALERT_THRESHOLDS.CACHE_FULL_RATIO) * 100;
    }
    
    return Math.max(0, Math.min(100, score));
  }
  
  /**
   * Verifica condições e gera alertas quando necessário
   */
  private checkAndGenerateAlerts(metrics: CacheMetrics): void {
    // Alerta de baixo hit rate
    if (metrics.hitRate < this.ALERT_THRESHOLDS.LOW_HIT_RATE && metrics.totalRequests > 10) {
      this.addAlert(
        'low_hit_rate',
        metrics.hitRate < 0.3 ? 'high' : 'medium',
        `Hit rate baixo: ${(metrics.hitRate * 100).toFixed(1)}%`,
        metrics.hitRate,
        this.ALERT_THRESHOLDS.LOW_HIT_RATE
      );
    }
    
    // Alerta de tempo de resposta alto
    if (metrics.avgResponseTime > this.ALERT_THRESHOLDS.HIGH_RESPONSE_TIME) {
      this.addAlert(
        'high_response_time',
        metrics.avgResponseTime > 2000 ? 'high' : 'medium',
        `Tempo de resposta alto: ${metrics.avgResponseTime.toFixed(0)}ms`,
        metrics.avgResponseTime,
        this.ALERT_THRESHOLDS.HIGH_RESPONSE_TIME
      );
    }
    
    // Alerta de dados antigos
    if (metrics.avgDataAge > this.ALERT_THRESHOLDS.OLD_DATA_AGE) {
      this.addAlert(
        'old_data',
        'medium',
        `Dados antigos no cache: ${(metrics.avgDataAge / (60 * 1000)).toFixed(1)} minutos`,
        metrics.avgDataAge,
        this.ALERT_THRESHOLDS.OLD_DATA_AGE
      );
    }
    
    // Alerta de cache cheio
    const fullnessRatio = metrics.cacheSize / metrics.maxSize;
    if (fullnessRatio > this.ALERT_THRESHOLDS.CACHE_FULL_RATIO) {
      this.addAlert(
        'cache_full',
        fullnessRatio > 0.95 ? 'high' : 'medium',
        `Cache quase cheio: ${(fullnessRatio * 100).toFixed(1)}%`,
        fullnessRatio,
        this.ALERT_THRESHOLDS.CACHE_FULL_RATIO
      );
    }
    
    // Alerta de alta frequência de invalidação
    if (metrics.invalidationFrequency > this.ALERT_THRESHOLDS.HIGH_INVALIDATION_RATE) {
      this.addAlert(
        'high_invalidation',
        metrics.invalidationFrequency > 20 ? 'high' : 'medium',
        `Alta frequência de invalidação: ${metrics.invalidationFrequency}/min`,
        metrics.invalidationFrequency,
        this.ALERT_THRESHOLDS.HIGH_INVALIDATION_RATE
      );
    }
  }

  /**
   * Calcula o tempo médio de resposta das operações de cache
   */
  private getAverageResponseTime(): number {
    // Para simplicidade, vamos simular um tempo baseado no hit rate
    // Em uma implementação real, você mediria o tempo real das operações
    const hitRate = this.stats.hits / (this.stats.hits + this.stats.misses || 1);
    
    // Cache hits são mais rápidos (1-5ms), misses são mais lentos (50-200ms)
    const avgHitTime = 3;
    const avgMissTime = 100;
    
    return (hitRate * avgHitTime) + ((1 - hitRate) * avgMissTime);
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
    this.log('debug', 'cache_set', { key, params, dataSize: JSON.stringify(data).length, ttl: this.config.ttl });
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
      this.log('debug', 'cache_miss', { key, params });
      console.log(`📦 Cache: Miss para chave: ${key}`);
      return null;
    }

    if (this.isExpired(entry)) {
      this.cache.delete(key);
      this.stats.misses++;
      this.invalidationCount++;
      this.invalidationTimes.push(Date.now());
      this.log('debug', 'cache_expired', { key, age: Date.now() - entry.timestamp });
      console.log(`📦 Cache: Expirado para chave: ${key}`);
      return null;
    }

    this.stats.hits++;
    this.log('debug', 'cache_hit', { key, age: Date.now() - entry.timestamp });
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
    const clearedCount = this.cache.size;
    this.cache.clear();
    this.requestTimes.clear();
    this.requestCounts.clear();
    this.stats.clears++;
    this.invalidationCount += clearedCount;
    this.invalidationTimes.push(Date.now());
    this.log('info', 'cache_cleared', { clearedCount });
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
      this.invalidationCount++;
      this.invalidationTimes.push(Date.now());
      this.log('debug', 'cache_delete', { key, params });
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
    isActive: boolean;
    totalRequests: number;
    avgResponseTime: number;
  } {
    const entries = Array.from(this.cache.entries()).map(([key, entry]) => ({
      key,
      timestamp: entry.timestamp,
      expiresAt: entry.expiresAt
    }));

    return {
      ...this.stats,
      size: this.cache.size,
      maxSize: this.config.maxSize,
      ttl: this.config.ttl,
      entries,
      hitRate: this.stats.hits / (this.stats.hits + this.stats.misses) || 0,
      isActive: this.isActive,
      totalRequests: Array.from(this.requestCounts.values()).reduce((sum, count) => sum + count, 0),
      avgResponseTime: this.getAverageResponseTime()
    };
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
   * Obtém métricas completas do cache
   */
  getMetrics(): CacheMetrics {
    return this.trackCachePerformance();
  }
  
  /**
   * Obtém logs recentes do cache
   */
  getLogs(limit: number = 100): CacheLog[] {
    return this.logs.slice(-limit);
  }
  
  /**
   * Obtém alertas ativos do cache
   */
  getAlerts(): CacheAlert[] {
    return [...this.alerts];
  }
  
  /**
   * Limpa alertas antigos
   */
  clearOldAlerts(maxAge: number = 5 * 60 * 1000): void {
    const now = Date.now();
    this.alerts = this.alerts.filter(alert => now - alert.timestamp < maxAge);
  }
  
  /**
   * Força a limpeza de logs e alertas antigos
   */
  forceCleanup(): void {
    this.cleanOldLogs();
    this.clearOldAlerts();
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

/**
 * Classe PersistentCache que estende LocalCache com persistência no localStorage
 * 
 * Funcionalidades:
 * - Salva dados automaticamente no localStorage quando set() é chamado
 * - Carrega dados do localStorage no constructor
 * - Validação robusta de dados corrompidos
 * - Limpeza automática de dados expirados
 * - Compatibilidade total com a interface LocalCache
 */
class PersistentCache<T> extends LocalCache<T> {
  private storageKey: string;
  private debugEnabled: boolean = true;
  private readonly STORAGE_VERSION = '1.1';
  private readonly MAX_STORAGE_SIZE = 5 * 1024 * 1024; // 5MB limite

  constructor(config: Partial<CacheConfig> = {}, storageKey: string) {
    super(config);
    this.storageKey = storageKey;
    this.validateStorageKey(storageKey);
    this.loadFromStorage();
    
    // Configurar limpeza automática mais frequente para dados persistentes
    setInterval(() => this.cleanExpiredFromStorage(), 5 * 60 * 1000); // A cada 5 minutos
  }

  /**
   * Valida se a chave de storage é válida
   */
  private validateStorageKey(key: string): void {
    if (!key || typeof key !== 'string' || key.trim().length === 0) {
      throw new Error('PersistentCache: storageKey deve ser uma string não vazia');
    }
  }

  /**
   * Log de debug com informações detalhadas
   */
  private debugLog(message: string, data?: any): void {
    if (this.debugEnabled) {
      const timestamp = new Date().toISOString();
      console.log(`[PersistentCache:${this.storageKey}][${timestamp}] ${message}`, data || '');
    }
  }

  /**
   * Valida se os dados do localStorage estão em formato válido
   */
  private validateStorageData(data: any): boolean {
    try {
      return (
        data &&
        typeof data === 'object' &&
        data.version &&
        data.cache &&
        typeof data.cache === 'object' &&
        data.timestamp &&
        typeof data.timestamp === 'number'
      );
    } catch {
      return false;
    }
  }

  /**
   * Carrega dados do localStorage com validação robusta
   */
  private loadFromStorage(): void {
    try {
      const stored = localStorage.getItem(this.storageKey);
      if (!stored) {
        this.debugLog('Nenhum dado encontrado no localStorage');
        return;
      }

      // Verificar tamanho dos dados
      if (stored.length > this.MAX_STORAGE_SIZE) {
        this.debugLog('Dados do localStorage excedem o tamanho máximo, removendo...');
        localStorage.removeItem(this.storageKey);
        return;
      }

      const parsedData = JSON.parse(stored);
      
      // Validar estrutura dos dados
      if (!this.validateStorageData(parsedData)) {
        this.debugLog('Dados do localStorage estão corrompidos, removendo...');
        localStorage.removeItem(this.storageKey);
        return;
      }

      // Verificar compatibilidade de versão
      if (parsedData.version !== this.STORAGE_VERSION) {
        this.debugLog(`Versão incompatível (${parsedData.version} vs ${this.STORAGE_VERSION}), removendo dados antigos...`);
        localStorage.removeItem(this.storageKey);
        return;
      }

      // Restaurar dados válidos e não expirados
      const now = Date.now();
      let restoredCount = 0;
      let expiredCount = 0;
      
      for (const [keyStr, entry] of Object.entries(parsedData.cache)) {
        try {
          const cacheEntry = entry as any;
          
          // Validar estrutura da entrada
          if (!cacheEntry || 
              typeof cacheEntry.expiresAt !== 'number' || 
              typeof cacheEntry.timestamp !== 'number' ||
              cacheEntry.data === undefined) {
            continue;
          }

          if (cacheEntry.expiresAt > now) {
            const params = JSON.parse(keyStr);
            super.set(params, cacheEntry.data);
            restoredCount++;
          } else {
            expiredCount++;
          }
        } catch (entryError) {
          this.debugLog(`Erro ao processar entrada do cache`, { keyStr, error: entryError });
        }
      }
      
      this.debugLog('Dados carregados do localStorage', { 
        restoredCount, 
        expiredCount,
        totalSize: stored.length 
      });
      
      // Se houve dados expirados, salvar o estado limpo
      if (expiredCount > 0) {
        this.saveToStorage();
      }
      
    } catch (error) {
      this.debugLog('Erro crítico ao carregar do localStorage', error);
      // Limpar dados corrompidos
      try {
        localStorage.removeItem(this.storageKey);
      } catch (removeError) {
        this.debugLog('Erro ao remover dados corrompidos', removeError);
      }
    }
  }

  /**
   * Salva dados no localStorage com validação de espaço
   */
  private saveToStorage(): void {
    try {
      const stats = super.getStats();
      const cacheData: Record<string, any> = {};
      
      // Converter entradas do cache para formato serializável
      for (const entry of stats.entries) {
        try {
          const data = super.get(JSON.parse(entry.key));
          if (data !== null) {
            cacheData[entry.key] = {
              data,
              timestamp: entry.timestamp,
              expiresAt: entry.expiresAt
            };
          }
        } catch (keyError) {
          this.debugLog('Erro ao processar chave para salvamento', { key: entry.key, error: keyError });
        }
      }

      const dataToStore = {
        cache: cacheData,
        timestamp: Date.now(),
        version: this.STORAGE_VERSION,
        metadata: {
          entries: Object.keys(cacheData).length,
          ttl: stats.ttl,
          maxSize: stats.maxSize
        }
      };

      const serializedData = JSON.stringify(dataToStore);
      
      // Verificar tamanho antes de salvar
      if (serializedData.length > this.MAX_STORAGE_SIZE) {
        this.debugLog('Dados excedem tamanho máximo, não salvando', { 
          size: serializedData.length, 
          maxSize: this.MAX_STORAGE_SIZE 
        });
        return;
      }

      localStorage.setItem(this.storageKey, serializedData);
      this.debugLog('Dados salvos no localStorage', { 
        entries: Object.keys(cacheData).length,
        size: serializedData.length
      });
      
    } catch (error) {
      this.debugLog('Erro ao salvar no localStorage', error);
      
      // Se erro de quota, tentar limpar outros caches antigos
      if (error instanceof DOMException && error.name === 'QuotaExceededError') {
        this.debugLog('Quota do localStorage excedida, tentando limpar espaço...');
        this.cleanOldStorageEntries();
      }
    }
  }

  /**
   * Remove dados expirados do localStorage
   */
  private cleanExpiredFromStorage(): void {
    try {
      const stored = localStorage.getItem(this.storageKey);
      if (!stored) return;

      const parsedData = JSON.parse(stored);
      if (!this.validateStorageData(parsedData)) return;

      const now = Date.now();
      let cleanedCount = 0;
      const cleanedCache: Record<string, any> = {};

      for (const [key, entry] of Object.entries(parsedData.cache)) {
        const cacheEntry = entry as any;
        if (cacheEntry.expiresAt > now) {
          cleanedCache[key] = entry;
        } else {
          cleanedCount++;
        }
      }

      if (cleanedCount > 0) {
        const updatedData = {
          ...parsedData,
          cache: cleanedCache,
          timestamp: Date.now()
        };
        
        localStorage.setItem(this.storageKey, JSON.stringify(updatedData));
        this.debugLog('Limpeza automática de dados expirados', { cleanedCount });
      }
    } catch (error) {
      this.debugLog('Erro na limpeza automática', error);
    }
  }

  /**
   * Tenta limpar entradas antigas de outros caches para liberar espaço
   */
  private cleanOldStorageEntries(): void {
    try {
      const keysToCheck = [];
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.includes('cache') && key !== this.storageKey) {
          keysToCheck.push(key);
        }
      }
      
      // Remove até 3 entradas antigas
      keysToCheck.slice(0, 3).forEach(key => {
        try {
          localStorage.removeItem(key);
          this.debugLog('Removida entrada antiga para liberar espaço', { key });
        } catch {}
      });
    } catch (error) {
      this.debugLog('Erro ao limpar entradas antigas', error);
    }
  }

  /**
   * Sobrescreve set() para incluir persistência automática
   */
  set(params: Record<string, any>, data: T): void {
    super.set(params, data);
    this.saveToStorage();
    this.debugLog('Dados adicionados ao cache persistente', { params });
  }

  /**
   * Sobrescreve delete() para incluir persistência automática
   */
  delete(params: Record<string, any>): boolean {
    const result = super.delete(params);
    if (result) {
      this.saveToStorage();
      this.debugLog('Dados removidos do cache persistente', { params });
    }
    return result;
  }

  /**
   * Sobrescreve clear() para limpar também o localStorage
   */
  clear(): void {
    super.clear();
    try {
      localStorage.removeItem(this.storageKey);
      this.debugLog('Cache e localStorage limpos completamente');
    } catch (error) {
      this.debugLog('Erro ao limpar localStorage', error);
    }
  }

  /**
   * Limpa apenas o localStorage, mantendo o cache em memória
   */
  clearStorage(): void {
    try {
      localStorage.removeItem(this.storageKey);
      this.debugLog('localStorage limpo (cache em memória mantido)');
    } catch (error) {
      this.debugLog('Erro ao limpar localStorage', error);
    }
  }

  /**
   * Força uma sincronização manual com o localStorage
   */
  syncToStorage(): void {
    this.saveToStorage();
  }

  /**
   * Recarrega dados do localStorage, sobrescrevendo o cache atual
   */
  reloadFromStorage(): void {
    super.clear();
    this.loadFromStorage();
    this.debugLog('Cache recarregado do localStorage');
  }

  /**
   * Retorna informações sobre o estado da persistência
   */
  getStorageInfo(): {
    storageKey: string;
    hasStoredData: boolean;
    storageSize: number;
    version: string;
  } {
    try {
      const stored = localStorage.getItem(this.storageKey);
      return {
        storageKey: this.storageKey,
        hasStoredData: !!stored,
        storageSize: stored ? stored.length : 0,
        version: this.STORAGE_VERSION
      };
    } catch {
      return {
        storageKey: this.storageKey,
        hasStoredData: false,
        storageSize: 0,
        version: this.STORAGE_VERSION
      };
    }
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

export const technicianRankingCache = new PersistentCache<any[]>({
  ttl: 30 * 60 * 1000, // 30 minutos
  maxSize: 20
}, 'dashboard_ranking_cache');

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

export { LocalCache, PersistentCache };
export default LocalCache;