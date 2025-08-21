import { useCallback, useEffect, useState } from 'react';
import {
  clearAllCaches,
  getAllCacheStats,
  metricsCache,
  systemStatusCache,
  technicianRankingCache,
  newTicketsCache,
} from '../services/cache';

export interface CacheStats {
  metrics: {
    size: number;
    hitRate: number;
    missRate: number;
    totalRequests: number;
  };
  systemStatus: {
    size: number;
    hitRate: number;
    missRate: number;
    totalRequests: number;
  };
  technicianRanking: {
    size: number;
    hitRate: number;
    missRate: number;
    totalRequests: number;
  };
  newTickets: {
    size: number;
    hitRate: number;
    missRate: number;
    totalRequests: number;
  };
}

export const useCache = () => {
  const [stats, setStats] = useState<CacheStats | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Função para atualizar estatísticas
  const updateStats = useCallback(() => {
    const allStats = getAllCacheStats();
    // Transform stats to match CacheStats interface
    const transformedStats = {
      metrics: {
        size: allStats.metrics.size,
        hitRate: allStats.metrics.hitRate,
        missRate: 1 - allStats.metrics.hitRate,
        totalRequests: allStats.metrics.totalRequests,
      },
      systemStatus: {
        size: allStats.systemStatus.size,
        hitRate: allStats.systemStatus.hitRate,
        missRate: 1 - allStats.systemStatus.hitRate,
        totalRequests: allStats.systemStatus.totalRequests,
      },
      technicianRanking: {
        size: allStats.technicianRanking.size,
        hitRate: allStats.technicianRanking.hitRate,
        missRate: 1 - allStats.technicianRanking.hitRate,
        totalRequests: allStats.technicianRanking.totalRequests,
      },
      newTickets: {
        size: allStats.newTickets.size,
        hitRate: allStats.newTickets.hitRate,
        missRate: 1 - allStats.newTickets.hitRate,
        totalRequests: allStats.newTickets.totalRequests,
      },
    };
    setStats(transformedStats);
  }, []);

  // Função para limpar todos os caches
  const clearAll = useCallback(async () => {
    setIsLoading(true);
    try {
      clearAllCaches();
      updateStats();
      // Todos os caches foram limpos
    } catch (error) {
      console.error('Erro ao limpar caches:', error);
    } finally {
      setIsLoading(false);
    }
  }, [updateStats]);

  // Função para limpar cache específico
  const clearSpecificCache = useCallback(
    (cacheType: 'metrics' | 'systemStatus' | 'technicianRanking' | 'newTickets') => {
      try {
        switch (cacheType) {
          case 'metrics':
            metricsCache.clear();
            break;
          case 'systemStatus':
            systemStatusCache.clear();
            break;
          case 'technicianRanking':
            technicianRankingCache.clear();
            break;
          case 'newTickets':
            newTicketsCache.clear();
            break;
        }
        updateStats();
        // Cache foi limpo
      } catch (error) {
        console.error(`Erro ao limpar cache ${cacheType}:`, error);
      }
    },
    [updateStats]
  );

  // Função para forçar refresh de um cache específico
  const refreshCache = useCallback(
    async (cacheType: 'metrics' | 'systemStatus' | 'technicianRanking' | 'newTickets') => {
      try {
        switch (cacheType) {
          case 'metrics':
            await metricsCache.refresh({});
            break;
          case 'systemStatus':
            await systemStatusCache.refresh({});
            break;
          case 'technicianRanking':
            await technicianRankingCache.refresh({});
            break;
          case 'newTickets':
            await newTicketsCache.refresh({});
            break;
        }
        updateStats();
        // Cache foi atualizado
      } catch (error) {
        console.error(`Erro ao atualizar cache ${cacheType}:`, error);
      }
    },
    [updateStats]
  );

  // Função para obter informações detalhadas de um cache
  const getCacheInfo = useCallback(
    (cacheType: 'metrics' | 'systemStatus' | 'technicianRanking' | 'newTickets') => {
      switch (cacheType) {
        case 'metrics':
          return metricsCache.getStats();
        case 'systemStatus':
          return systemStatusCache.getStats();
        case 'technicianRanking':
          return technicianRankingCache.getStats();
        case 'newTickets':
          return newTicketsCache.getStats();
        default:
          return null;
      }
    },
    []
  );

  // Atualizar estatísticas automaticamente
  useEffect(() => {
    updateStats();

    // Atualizar estatísticas a cada 30 segundos
    const interval = setInterval(updateStats, 30000);

    return () => clearInterval(interval);
  }, [updateStats]);

  return {
    stats,
    isLoading,
    updateStats,
    clearAll,
    clearSpecificCache,
    refreshCache,
    getCacheInfo,
  };
};

export default useCache;
