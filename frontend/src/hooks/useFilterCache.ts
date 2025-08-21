import { useState, useCallback, useRef, useMemo } from 'react';
import { FilterParams, DashboardMetrics } from '../types/api';

interface CacheEntry {
  data: DashboardMetrics;
  timestamp: number;
  filters: FilterParams;
}

interface UseFilterCacheOptions {
  maxCacheSize?: number;
  cacheExpirationMs?: number;
  enableCache?: boolean;
}

interface UseFilterCacheReturn {
  getCachedData: (filters: FilterParams) => DashboardMetrics | null;
  setCachedData: (filters: FilterParams, data: DashboardMetrics) => void;
  clearCache: () => void;
  getCacheStats: () => {
    size: number;
    hitRate: number;
    totalRequests: number;
    cacheHits: number;
  };
  isCacheEnabled: boolean;
}

/**
 * Hook para gerenciar cache de dados de filtros do dashboard
 * Implementa LRU (Least Recently Used) cache com expiração por tempo
 */
export const useFilterCache = ({
  maxCacheSize = 50,
  cacheExpirationMs = 5 * 60 * 1000, // 5 minutos
  enableCache = true,
}: UseFilterCacheOptions = {}): UseFilterCacheReturn => {
  const [cache, setCache] = useState<Map<string, CacheEntry>>(new Map());
  const statsRef = useRef({
    totalRequests: 0,
    cacheHits: 0,
  });

  // Gerar chave única para os filtros
  const generateCacheKey = useCallback((filters: FilterParams): string => {
    // Normalizar filtros para gerar chave consistente
    const normalizedFilters = {
      ...filters,
      dateRange: filters.dateRange ? {
        startDate: filters.dateRange.startDate,
        endDate: filters.dateRange.endDate,
      } : null,
    };
    
    return JSON.stringify(normalizedFilters, Object.keys(normalizedFilters).sort());
  }, []);

  // Verificar se entrada do cache ainda é válida
  const isEntryValid = useCallback((entry: CacheEntry): boolean => {
    const now = Date.now();
    return (now - entry.timestamp) < cacheExpirationMs;
  }, [cacheExpirationMs]);

  // Limpar entradas expiradas
  const cleanExpiredEntries = useCallback(() => {
    setCache(prevCache => {
      const newCache = new Map(prevCache);
      const now = Date.now();
      
      for (const [key, entry] of newCache.entries()) {
        if ((now - entry.timestamp) >= cacheExpirationMs) {
          newCache.delete(key);
        }
      }
      
      return newCache;
    });
  }, [cacheExpirationMs]);

  // Implementar LRU - remover entrada menos recentemente usada
  const evictLRU = useCallback(() => {
    setCache(prevCache => {
      const newCache = new Map(prevCache);
      const firstKey = newCache.keys().next().value;
      if (firstKey) {
        newCache.delete(firstKey);
      }
      return newCache;
    });
  }, []);

  // Obter dados do cache
  const getCachedData = useCallback((filters: FilterParams): DashboardMetrics | null => {
    if (!enableCache) return null;
    
    statsRef.current.totalRequests++;
    
    const key = generateCacheKey(filters);
    const entry = cache.get(key);
    
    if (entry && isEntryValid(entry)) {
      // Mover para o final (mais recente) - LRU
      setCache(prevCache => {
        const newCache = new Map(prevCache);
        newCache.delete(key);
        newCache.set(key, entry);
        return newCache;
      });
      
      statsRef.current.cacheHits++;
      return entry.data;
    }
    
    // Remover entrada expirada se existir
    if (entry) {
      setCache(prevCache => {
        const newCache = new Map(prevCache);
        newCache.delete(key);
        return newCache;
      });
    }
    
    return null;
  }, [enableCache, generateCacheKey, cache, isEntryValid]);

  // Armazenar dados no cache
  const setCachedData = useCallback((filters: FilterParams, data: DashboardMetrics) => {
    if (!enableCache) return;
    
    const key = generateCacheKey(filters);
    const entry: CacheEntry = {
      data,
      timestamp: Date.now(),
      filters,
    };
    
    setCache(prevCache => {
      const newCache = new Map(prevCache);
      
      // Remover entrada existente se houver
      if (newCache.has(key)) {
        newCache.delete(key);
      }
      
      // Verificar se precisa fazer eviction
      if (newCache.size >= maxCacheSize) {
        // Remover a entrada mais antiga (LRU)
        const firstKey = newCache.keys().next().value;
        if (firstKey) {
          newCache.delete(firstKey);
        }
      }
      
      // Adicionar nova entrada
      newCache.set(key, entry);
      
      return newCache;
    });
    
    // Limpar entradas expiradas periodicamente
    if (Math.random() < 0.1) { // 10% de chance
      cleanExpiredEntries();
    }
  }, [enableCache, generateCacheKey, maxCacheSize, cleanExpiredEntries]);

  // Limpar todo o cache
  const clearCache = useCallback(() => {
    setCache(new Map());
    statsRef.current = {
      totalRequests: 0,
      cacheHits: 0,
    };
  }, []);

  // Obter estatísticas do cache
  const getCacheStats = useCallback(() => {
    const { totalRequests, cacheHits } = statsRef.current;
    const hitRate = totalRequests > 0 ? (cacheHits / totalRequests) * 100 : 0;
    
    return {
      size: cache.size,
      hitRate: Math.round(hitRate * 100) / 100,
      totalRequests,
      cacheHits,
    };
  }, [cache.size]);

  // Memoizar o retorno para evitar re-renders desnecessários
  const returnValue = useMemo(() => ({
    getCachedData,
    setCachedData,
    clearCache,
    getCacheStats,
    isCacheEnabled: enableCache,
  }), [getCachedData, setCachedData, clearCache, getCacheStats, enableCache]);

  return returnValue;
};

/**
 * Hook simplificado para cache de filtros com configurações padrão
 */
export const useSimpleFilterCache = () => {
  return useFilterCache({
    maxCacheSize: 20,
    cacheExpirationMs: 3 * 60 * 1000, // 3 minutos
    enableCache: true,
  });
};

/**
 * Hook para cache de filtros com configurações de alta performance
 */
export const useHighPerformanceFilterCache = () => {
  return useFilterCache({
    maxCacheSize: 100,
    cacheExpirationMs: 10 * 60 * 1000, // 10 minutos
    enableCache: true,
  });
};