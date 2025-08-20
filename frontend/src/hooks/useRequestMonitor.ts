/**
 * Hook para monitorar estatísticas de requisições
 */

import { useState, useEffect, useCallback } from 'react';
import { requestMonitor } from '../services/requestMonitor';

interface RequestStats {
  totalRequests: number;
  successfulRequests: number;
  failedRequests: number;
  cachedRequests: number;
  averageResponseTime: number;
  requestsPerMinute: number;
  topEndpoints: Array<{ endpoint: string; count: number; avgDuration: number }>;
  errorRate: number;
  cacheHitRate: number;
}

interface RequestMetric {
  id: string;
  endpoint: string;
  method: string;
  params: any;
  startTime: number;
  endTime?: number;
  duration?: number;
  status: 'pending' | 'success' | 'error' | 'cached';
  error?: string;
  cacheHit?: boolean;
  responseSize?: number;
}

interface UseRequestMonitorOptions {
  autoRefresh?: boolean;
  refreshInterval?: number;
  enableRealTimeUpdates?: boolean;
}

interface UseRequestMonitorReturn {
  stats: RequestStats;
  isLoading: boolean;
  error: string | null;
  slowestRequests: RequestMetric[];
  topEndpoints: Array<{
    endpoint: string;
    count: number;
    avgDuration: number;
    errorRate: number;
  }>;
  detailedStats: {
    stats: RequestStats;
    timeline: Array<{ timestamp: number; count: number; avgDuration: number }>;
    errors: Array<{ endpoint: string; error: string; count: number }>;
  } | null;
  refreshStats: () => void;
  clearHistory: () => void;
  exportData: () => any;
  getDetailedStats: (periodMinutes?: number) => void;
}

export const useRequestMonitor = ({
  autoRefresh = true,
  refreshInterval = 30000, // 30 segundos
  enableRealTimeUpdates = true,
}: UseRequestMonitorOptions = {}): UseRequestMonitorReturn => {
  const [stats, setStats] = useState<RequestStats>({
    totalRequests: 0,
    successfulRequests: 0,
    failedRequests: 0,
    cachedRequests: 0,
    averageResponseTime: 0,
    requestsPerMinute: 0,
    topEndpoints: [],
    errorRate: 0,
    cacheHitRate: 0,
  });

  const [slowestRequests, setSlowestRequests] = useState<RequestMetric[]>([]);
  const [topEndpoints, setTopEndpoints] = useState<
    Array<{
      endpoint: string;
      count: number;
      avgDuration: number;
      errorRate: number;
    }>
  >([]);

  const [detailedStats, setDetailedStats] = useState<{
    stats: RequestStats;
    timeline: Array<{ timestamp: number; count: number; avgDuration: number }>;
    errors: Array<{ endpoint: string; error: string; count: number }>;
  } | null>(null);

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Atualiza as estatísticas do monitor
   */
  const refreshStats = useCallback(() => {
    try {
      setIsLoading(true);
      setError(null);

      // Obter estatísticas básicas
      const currentStats = requestMonitor.getStats();
      setStats(currentStats);

      // Obter requisições mais lentas
      const slowest = requestMonitor.getSlowestRequests(10);
      setSlowestRequests(slowest);

      // Obter endpoints mais utilizados
      const topEps = requestMonitor.getTopEndpoints(10);
      setTopEndpoints(topEps);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao atualizar estatísticas');
      console.error('Erro ao atualizar estatísticas do monitor:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Obtém estatísticas detalhadas para um período específico
   */
  const getDetailedStats = useCallback((periodMinutes: number = 60) => {
    try {
      setIsLoading(true);
      const detailed = requestMonitor.getDetailedStats(periodMinutes);
      setDetailedStats(detailed);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao obter estatísticas detalhadas');
      console.error('Erro ao obter estatísticas detalhadas:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Limpa o histórico de requisições
   */
  const clearHistory = useCallback(() => {
    try {
      requestMonitor.clear();
      refreshStats();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao limpar histórico');
      console.error('Erro ao limpar histórico:', err);
    }
  }, [refreshStats]);

  /**
   * Exporta dados do monitor
   */
  const exportData = useCallback(() => {
    try {
      return requestMonitor.exportData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao exportar dados');
      console.error('Erro ao exportar dados:', err);
      return null;
    }
  }, []);

  // Auto-refresh das estatísticas
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(refreshStats, refreshInterval);
    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, refreshStats]);

  // Carregar estatísticas iniciais
  useEffect(() => {
    refreshStats();
  }, [refreshStats]);

  // Listener para atualizações em tempo real (se habilitado)
  useEffect(() => {
    if (!enableRealTimeUpdates) return;

    // Criar um listener personalizado para mudanças no monitor
    const handleStatsUpdate = () => {
      refreshStats();
    };

    // Simular listener através de polling mais frequente
    const realtimeInterval = setInterval(handleStatsUpdate, 5000); // 5 segundos

    return () => clearInterval(realtimeInterval);
  }, [enableRealTimeUpdates, refreshStats]);

  return {
    stats,
    isLoading,
    error,
    slowestRequests,
    topEndpoints,
    detailedStats,
    refreshStats,
    clearHistory,
    exportData,
    getDetailedStats,
  };
};

/**
 * Hook simplificado para obter apenas estatísticas básicas
 */
export const useRequestStats = () => {
  const { stats, isLoading, error, refreshStats } = useRequestMonitor({
    autoRefresh: true,
    refreshInterval: 60000, // 1 minuto
    enableRealTimeUpdates: false,
  });

  return {
    stats,
    isLoading,
    error,
    refresh: refreshStats,
  };
};

/**
 * Hook para monitorar performance de requisições
 */
export const useRequestPerformance = () => {
  const { stats, slowestRequests, topEndpoints, getDetailedStats, detailedStats } =
    useRequestMonitor({
      autoRefresh: true,
      refreshInterval: 30000,
      enableRealTimeUpdates: true,
    });

  const performanceScore =
    (stats.cacheHitRate * 0.4 +
      (1 - stats.errorRate) * 0.3 +
      Math.max(0, 1 - stats.averageResponseTime / 2000) * 0.3) *
    100;

  const isPerformanceGood = performanceScore >= 70;
  const isPerformanceFair = performanceScore >= 50;

  return {
    performanceScore: Math.round(performanceScore),
    isPerformanceGood,
    isPerformanceFair,
    averageResponseTime: stats.averageResponseTime,
    errorRate: stats.errorRate,
    cacheHitRate: stats.cacheHitRate,
    slowestRequests,
    topEndpoints,
    getDetailedStats,
    detailedStats,
  };
};
