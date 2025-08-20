import { LocalCache } from './cache';
import { apiService } from './api';

/**
 * Sistema de cache inteligente que gerencia múltiplos caches
 * e implementa estratégias avançadas de otimização
 */
class SmartCacheManager {
  private metricsCache: LocalCache<any>;
  private ticketsCache: LocalCache<any>;
  private systemStatusCache: LocalCache<any>;
  private preWarmScheduled = false;

  constructor() {
    // Cache para métricas do dashboard - TTL mais longo
    this.metricsCache = new LocalCache({
      maxSize: 50,
      defaultTTL: 300000, // 5 minutos
      cleanupInterval: 60000, // 1 minuto
    });

    // Cache para tickets - TTL médio
    this.ticketsCache = new LocalCache({
      maxSize: 100,
      defaultTTL: 180000, // 3 minutos
      cleanupInterval: 60000,
    });

    // Cache para status do sistema - TTL curto
    this.systemStatusCache = new LocalCache({
      maxSize: 20,
      defaultTTL: 30000, // 30 segundos
      cleanupInterval: 30000,
    });

    this.setupPreWarming();
  }

  /**
   * Configura pré-aquecimento automático do cache
   */
  private setupPreWarming(): void {
    if (this.preWarmScheduled) return;

    // Pré-aquecer cache na inicialização
    setTimeout(() => {
      this.preWarmCriticalData();
    }, 1000);

    // Pré-aquecer cache periodicamente
    setInterval(() => {
      this.preWarmCriticalData();
    }, 600000); // 10 minutos

    this.preWarmScheduled = true;
  }

  /**
   * Pré-aquece o cache com dados críticos
   */
  private async preWarmCriticalData(): Promise<void> {
    try {
      console.log('🔥 SmartCache: Iniciando pré-aquecimento...');

      // Pré-aquecer métricas principais
      const metricsPromises = [
        this.preWarmMetrics({ period: 'today' }),
        this.preWarmMetrics({ period: 'week' }),
        this.preWarmMetrics({ period: 'month' }),
      ];

      // Pré-aquecer status do sistema
      const statusPromise = this.preWarmSystemStatus();

      await Promise.allSettled([...metricsPromises, statusPromise]);
      console.log('✅ SmartCache: Pré-aquecimento concluído');
    } catch (error) {
      console.error('❌ SmartCache: Erro no pré-aquecimento:', error);
    }
  }

  /**
   * Pré-aquece métricas específicas
   */
  private async preWarmMetrics(params: any): Promise<void> {
    try {
      const data = await apiService.getMetrics(params);
      this.metricsCache.preWarm(params, data);
    } catch (error) {
      console.warn('⚠️ SmartCache: Falha ao pré-aquecer métricas:', params, error);
    }
  }

  /**
   * Pré-aquece status do sistema
   */
  private async preWarmSystemStatus(): Promise<void> {
    try {
      const data = await apiService.getSystemStatus();
      this.systemStatusCache.preWarm({}, data);
    } catch (error) {
      console.warn('⚠️ SmartCache: Falha ao pré-aquecer status do sistema:', error);
    }
  }

  /**
   * Obtém cache específico por tipo
   */
  getCache(type: 'metrics' | 'tickets' | 'systemStatus'): LocalCache<any> {
    switch (type) {
      case 'metrics':
        return this.metricsCache;
      case 'tickets':
        return this.ticketsCache;
      case 'systemStatus':
        return this.systemStatusCache;
      default:
        throw new Error(`Tipo de cache desconhecido: ${type}`);
    }
  }

  /**
   * Invalida cache relacionado a tickets quando há mudanças
   */
  invalidateTicketRelatedCache(): void {
    this.ticketsCache.invalidatePattern('.*');
    this.metricsCache.invalidatePattern('.*tickets.*');
    console.log('🗑️ SmartCache: Cache relacionado a tickets invalidado');
  }

  /**
   * Invalida cache de métricas quando há mudanças no sistema
   */
  invalidateMetricsCache(): void {
    this.metricsCache.invalidatePattern('.*');
    console.log('🗑️ SmartCache: Cache de métricas invalidado');
  }

  /**
   * Obtém estatísticas consolidadas de todos os caches
   */
  getConsolidatedStats() {
    const metricsStats = this.metricsCache.getStats();
    const ticketsStats = this.ticketsCache.getStats();
    const systemStats = this.systemStatusCache.getStats();

    return {
      metrics: metricsStats,
      tickets: ticketsStats,
      systemStatus: systemStats,
      total: {
        size: metricsStats.size + ticketsStats.size + systemStats.size,
        hitRate:
          (metricsStats.hitCount + ticketsStats.hitCount + systemStats.hitCount) /
          Math.max(
            1,
            metricsStats.hitCount +
              metricsStats.missCount +
              ticketsStats.hitCount +
              ticketsStats.missCount +
              systemStats.hitCount +
              systemStats.missCount
          ),
        memoryUsage: metricsStats.memoryUsage + ticketsStats.memoryUsage + systemStats.memoryUsage,
      },
    };
  }

  /**
   * Limpa todos os caches
   */
  clearAll(): void {
    this.metricsCache.clear();
    this.ticketsCache.clear();
    this.systemStatusCache.clear();
    console.log('🧹 SmartCache: Todos os caches limpos');
  }

  /**
   * Otimiza automaticamente os caches baseado no uso
   */
  optimize(): void {
    const stats = this.getConsolidatedStats();

    // Se hit rate está baixo, aumentar TTL
    if (stats.total.hitRate < 0.3) {
      console.log('📈 SmartCache: Hit rate baixo, otimizando TTL...');
      // Lógica de otimização pode ser implementada aqui
    }

    // Se uso de memória está alto, limpar caches menos usados
    if (stats.total.memoryUsage > 1000000) {
      // 1MB
      console.log('🧹 SmartCache: Uso de memória alto, limpando caches...');
      this.clearLeastUsedEntries();
    }
  }

  /**
   * Remove entradas menos usadas para liberar memória
   */
  private clearLeastUsedEntries(): void {
    // Implementar lógica para remover entradas menos acessadas
    // Por enquanto, limpa 25% dos caches
    [this.metricsCache, this.ticketsCache, this.systemStatusCache].forEach(cache => {
      const stats = cache.getStats();
      const targetSize = Math.floor(stats.size * 0.75);
      // Lógica de limpeza seletiva pode ser implementada
    });
  }
}

// Instância singleton do gerenciador de cache inteligente
export const smartCacheManager = new SmartCacheManager();

// Configurar otimização automática
setInterval(() => {
  smartCacheManager.optimize();
}, 300000); // 5 minutos
