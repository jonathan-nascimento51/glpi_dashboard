/**
 * Estratégias avançadas de cache com TTL dinâmico
 * 
 * Este arquivo demonstra como usar as funcionalidades avançadas de cache
 * implementadas no sistema, incluindo TTL dinâmico e priorização.
 */

import { LocalCache } from '../services/cache';

// Configurações de cache para diferentes cenários
export const cacheConfigurations = {
  // Cache para dados críticos com alta prioridade
  criticalData: {
    defaultTtl: 5 * 60 * 1000, // 5 minutos
    maxSize: 50,
    enableAutoActivation: true,
    activationThreshold: 500,
    enableDynamicTtl: true,
    minTtl: 2 * 60 * 1000, // 2 minutos mínimo
    maxTtl: 20 * 60 * 1000, // 20 minutos máximo
    ttlMultiplier: 2.0 // TTL aumenta rapidamente para dados frequentemente acessados
  },

  // Cache para dados de dashboard com prioridade média
  dashboardData: {
    defaultTtl: 3 * 60 * 1000, // 3 minutos
    maxSize: 100,
    enableAutoActivation: true,
    activationThreshold: 1000,
    enableDynamicTtl: true,
    minTtl: 1 * 60 * 1000, // 1 minuto mínimo
    maxTtl: 15 * 60 * 1000, // 15 minutos máximo
    ttlMultiplier: 1.5
  },

  // Cache para dados de relatórios com prioridade baixa
  reportData: {
    defaultTtl: 10 * 60 * 1000, // 10 minutos
    maxSize: 30,
    enableAutoActivation: true,
    activationThreshold: 2000,
    enableDynamicTtl: true,
    minTtl: 5 * 60 * 1000, // 5 minutos mínimo
    maxTtl: 60 * 60 * 1000, // 1 hora máximo
    ttlMultiplier: 1.2 // TTL aumenta lentamente
  }
};

/**
 * Classe para gerenciar múltiplas instâncias de cache com estratégias diferentes
 */
export class CacheManager {
  private caches: Map<string, LocalCache<any>> = new Map();

  constructor() {
    // Inicializar caches com configurações predefinidas
    this.caches.set('critical', new LocalCache(cacheConfigurations.criticalData));
    this.caches.set('dashboard', new LocalCache(cacheConfigurations.dashboardData));
    this.caches.set('reports', new LocalCache(cacheConfigurations.reportData));
  }

  /**
   * Obter uma instância de cache específica
   */
  getCache(type: 'critical' | 'dashboard' | 'reports'): LocalCache<any> {
    const cache = this.caches.get(type);
    if (!cache) {
      throw new Error(`Cache type '${type}' not found`);
    }
    return cache;
  }

  /**
   * Armazenar dados com prioridade específica
   */
  async storeWithPriority<T>(
    cacheType: 'critical' | 'dashboard' | 'reports',
    key: string,
    data: T,
    priority: 'high' | 'medium' | 'low' = 'medium',
    responseTime?: number
  ): Promise<void> {
    const cache = this.getCache(cacheType);
    await cache.set(key, data, undefined, responseTime);
  }

  /**
   * Recuperar dados do cache
   */
  async retrieve<T>(
    cacheType: 'critical' | 'dashboard' | 'reports',
    key: string
  ): Promise<T | null> {
    const cache = this.getCache(cacheType);
    return cache.get(key);
  }

  /**
   * Obter estatísticas de todos os caches
   */
  getAllStats(): Record<string, any> {
    const stats: Record<string, any> = {};
    
    for (const [type, cache] of this.caches.entries()) {
      stats[type] = cache.getStats();
    }
    
    return stats;
  }

  /**
   * Limpar todos os caches
   */
  clearAll(): void {
    for (const cache of this.caches.values()) {
      cache.clear();
    }
  }

  /**
   * Invalidar padrões específicos em todos os caches
   */
  invalidatePattern(pattern: string): void {
    for (const cache of this.caches.values()) {
      cache.invalidatePattern(pattern);
    }
  }

  /**
   * Obter analytics do cache com relatório de performance
   */
  getAnalytics(): {
    generateReport(): {
      overallHitRate: number;
      cacheDetails: Record<string, any>;
      summary: string;
      overallRecommendations: string[];
    }
  } {
    return {
      generateReport: () => {
        const allStats = this.getAllStats();
        const report = CacheAnalytics.generatePerformanceReport(allStats);
        
        // Calcular taxa de hit geral
        let totalHitRate = 0;
        let cacheCount = 0;
        
        for (const [cacheType, stats] of Object.entries(allStats)) {
          if (stats && typeof stats.hitRate === 'number') {
            totalHitRate += stats.hitRate;
            cacheCount++;
          }
        }
        
        const overallHitRate = cacheCount > 0 ? (totalHitRate / cacheCount) * 100 : 0;
        
        return {
          overallHitRate,
          cacheDetails: report.details,
          summary: report.summary,
          overallRecommendations: report.overallRecommendations
        };
      }
    };
  }
}

// Instância global do gerenciador de cache
export const cacheManager = new CacheManager();

/**
 * Utilitários para análise de performance do cache
 */
export class CacheAnalytics {
  /**
   * Analisar eficiência do cache
   */
  static analyzeCacheEfficiency(stats: any): {
    efficiency: 'excellent' | 'good' | 'fair' | 'poor';
    recommendations: string[];
  } {
    const { hitRate, averageResponseTime, size, maxSize } = stats;
    const recommendations: string[] = [];
    
    let efficiency: 'excellent' | 'good' | 'fair' | 'poor';
    
    if (hitRate >= 0.8) {
      efficiency = 'excellent';
    } else if (hitRate >= 0.6) {
      efficiency = 'good';
      recommendations.push('Considere aumentar o TTL para dados frequentemente acessados');
    } else if (hitRate >= 0.4) {
      efficiency = 'fair';
      recommendations.push('Revise as estratégias de TTL dinâmico');
      recommendations.push('Considere aumentar o tamanho máximo do cache');
    } else {
      efficiency = 'poor';
      recommendations.push('Cache pode não estar sendo efetivo para este tipo de dados');
      recommendations.push('Considere desabilitar o cache ou revisar completamente a estratégia');
    }
    
    if (averageResponseTime > 2000) {
      recommendations.push('Tempo de resposta alto - considere otimizar as operações de cache');
    }
    
    if (size / maxSize > 0.9) {
      recommendations.push('Cache próximo do limite - considere aumentar maxSize ou revisar TTL');
    }
    
    return { efficiency, recommendations };
  }

  /**
   * Gerar relatório de performance do cache
   */
  static generatePerformanceReport(allStats: Record<string, any>): {
    summary: string;
    details: Record<string, any>;
    overallRecommendations: string[];
  } {
    const details: Record<string, any> = {};
    const overallRecommendations: string[] = [];
    let totalHitRate = 0;
    let cacheCount = 0;
    
    for (const [cacheType, stats] of Object.entries(allStats)) {
      const analysis = this.analyzeCacheEfficiency(stats);
      details[cacheType] = {
        ...stats,
        analysis
      };
      
      totalHitRate += stats.hitRate || 0;
      cacheCount++;
    }
    
    const averageHitRate = cacheCount > 0 ? totalHitRate / cacheCount : 0;
    
    let summary: string;
    if (averageHitRate >= 0.7) {
      summary = 'Sistema de cache funcionando eficientemente';
    } else if (averageHitRate >= 0.5) {
      summary = 'Sistema de cache com performance moderada';
      overallRecommendations.push('Considere ajustar configurações de TTL dinâmico');
    } else {
      summary = 'Sistema de cache precisa de otimização';
      overallRecommendations.push('Revise completamente as estratégias de cache');
      overallRecommendations.push('Considere implementar cache warming para dados críticos');
    }
    
    return {
      summary,
      details,
      overallRecommendations
    };
  }
}

/**
 * Hook para usar cache com estratégias avançadas
 */
export function useCacheStrategy(type: 'critical' | 'dashboard' | 'reports') {
  const cache = cacheManager.getCache(type);
  
  return {
    get: <T>(key: string) => cache.get<T>(key),
    set: <T>(key: string, data: T, ttl?: number, responseTime?: number) => 
      cache.set(key, data, ttl, responseTime),
    has: (key: string) => cache.has(key),
    delete: (key: string) => cache.delete(key),
    clear: () => cache.clear(),
    getStats: () => cache.getStats(),
    invalidatePattern: (pattern: string) => cache.invalidatePattern(pattern)
  };
}