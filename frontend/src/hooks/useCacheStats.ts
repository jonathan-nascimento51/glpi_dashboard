import { useState, useEffect } from 'react';
import { smartCacheManager } from '../services/smartCache';

/**
 * Hook para monitorar estatísticas do cache inteligente
 */
export const useCacheStats = (refreshInterval: number = 5000) => {
  const [stats, setStats] = useState(() => smartCacheManager.getConsolidatedStats());
  const [isLoading, setIsLoading] = useState(false);

  const refreshStats = () => {
    setIsLoading(true);
    try {
      const newStats = smartCacheManager.getConsolidatedStats();
      setStats(newStats);
    } catch (error) {
      console.error('Erro ao obter estatísticas do cache:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    refreshStats();

    const interval = setInterval(refreshStats, refreshInterval);
    return () => clearInterval(interval);
  }, [refreshInterval]);

  const clearAllCaches = () => {
    smartCacheManager.clearAll();
    refreshStats();
  };

  const invalidateTicketCache = () => {
    smartCacheManager.invalidateTicketRelatedCache();
    refreshStats();
  };

  const invalidateMetricsCache = () => {
    smartCacheManager.invalidateMetricsCache();
    refreshStats();
  };

  const optimizeCaches = () => {
    smartCacheManager.optimize();
    refreshStats();
  };

  return {
    stats,
    isLoading,
    refreshStats,
    clearAllCaches,
    invalidateTicketCache,
    invalidateMetricsCache,
    optimizeCaches,
  };
};

/**
 * Hook simplificado para verificar se o cache está funcionando bem
 */
export const useCacheHealth = () => {
  const { stats } = useCacheStats(10000); // Atualiza a cada 10 segundos

  const health = {
    isHealthy: stats.total.hitRate > 0.5, // Hit rate acima de 50%
    hitRate: stats.total.hitRate,
    memoryUsage: stats.total.memoryUsage,
    totalEntries: stats.total.size,
    status:
      stats.total.hitRate > 0.7
        ? 'excellent'
        : stats.total.hitRate > 0.5
          ? 'good'
          : stats.total.hitRate > 0.3
            ? 'fair'
            : 'poor',
  };

  return health;
};
