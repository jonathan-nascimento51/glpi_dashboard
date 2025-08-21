import { useState, useCallback, useRef, useEffect } from 'react';
import { useDebouncedCallback, useThrottledCallback } from './useDebounce';

interface FilterPerformanceMetrics {
  totalFilters: number;
  averageResponseTime: number;
  slowestFilter: number;
  fastestFilter: number;
  lastFilterTime: number;
  filterHistory: Array<{
    timestamp: number;
    responseTime: number;
    filterType: string;
    cached: boolean;
  }>;
}

interface UseFilterPerformanceOptions {
  debounceDelay?: number;
  throttleDelay?: number;
  maxHistorySize?: number;
  enableMetrics?: boolean;
}

interface UseFilterPerformanceReturn {
  // Funções de filtro otimizadas
  debouncedFilter: <T extends (...args: any[]) => any>(callback: T) => T;
  throttledFilter: <T extends (...args: any[]) => any>(callback: T) => T;
  
  // Métricas de performance
  metrics: FilterPerformanceMetrics;
  
  // Funções de controle
  startFilterTimer: (filterType: string) => string;
  endFilterTimer: (timerId: string, cached?: boolean) => void;
  clearMetrics: () => void;
  
  // Status
  isFilterInProgress: boolean;
}

/**
 * Hook para monitorar e otimizar performance de filtros
 * Combina debounce, throttle e coleta de métricas de performance
 */
export const useFilterPerformance = ({
  debounceDelay = 500,
  throttleDelay = 100,
  maxHistorySize = 100,
  enableMetrics = true,
}: UseFilterPerformanceOptions = {}): UseFilterPerformanceReturn => {
  const [metrics, setMetrics] = useState<FilterPerformanceMetrics>({
    totalFilters: 0,
    averageResponseTime: 0,
    slowestFilter: 0,
    fastestFilter: 0,
    lastFilterTime: 0,
    filterHistory: [],
  });
  
  const [isFilterInProgress, setIsFilterInProgress] = useState(false);
  const activeTimersRef = useRef<Map<string, { startTime: number; filterType: string }>>(new Map());
  
  // Função para iniciar timer de filtro
  const startFilterTimer = useCallback((filterType: string): string => {
    if (!enableMetrics) return '';
    
    const timerId = `${Date.now()}-${Math.random()}`;
    const startTime = performance.now();
    
    activeTimersRef.current.set(timerId, { startTime, filterType });
    setIsFilterInProgress(true);
    
    return timerId;
  }, [enableMetrics]);
  
  // Função para finalizar timer de filtro
  const endFilterTimer = useCallback((timerId: string, cached: boolean = false) => {
    if (!enableMetrics || !timerId) return;
    
    const timerData = activeTimersRef.current.get(timerId);
    if (!timerData) return;
    
    const endTime = performance.now();
    const responseTime = endTime - timerData.startTime;
    
    // Remover timer ativo
    activeTimersRef.current.delete(timerId);
    
    // Verificar se ainda há timers ativos
    setIsFilterInProgress(activeTimersRef.current.size > 0);
    
    // Atualizar métricas
    setMetrics(prevMetrics => {
      const newHistory = [
        ...prevMetrics.filterHistory,
        {
          timestamp: Date.now(),
          responseTime,
          filterType: timerData.filterType,
          cached,
        },
      ].slice(-maxHistorySize); // Manter apenas os últimos N registros
      
      const totalFilters = prevMetrics.totalFilters + 1;
      const totalResponseTime = newHistory.reduce((sum, entry) => sum + entry.responseTime, 0);
      const averageResponseTime = totalResponseTime / newHistory.length;
      
      const responseTimes = newHistory.map(entry => entry.responseTime);
      const slowestFilter = Math.max(...responseTimes, prevMetrics.slowestFilter);
      const fastestFilter = Math.min(...responseTimes, prevMetrics.fastestFilter || Infinity);
      
      return {
        totalFilters,
        averageResponseTime: Math.round(averageResponseTime * 100) / 100,
        slowestFilter: Math.round(slowestFilter * 100) / 100,
        fastestFilter: Math.round(fastestFilter * 100) / 100,
        lastFilterTime: Math.round(responseTime * 100) / 100,
        filterHistory: newHistory,
      };
    });
  }, [enableMetrics, maxHistorySize]);
  
  // Função debounced otimizada
  const debouncedFilter = useCallback(<T extends (...args: any[]) => any>(callback: T): T => {
    return useDebouncedCallback(((...args: Parameters<T>) => {
      const timerId = startFilterTimer('debounced');
      
      try {
        const result = callback(...args);
        
        // Se for uma Promise, aguardar conclusão
        if (result && typeof result.then === 'function') {
          result
            .then(() => endFilterTimer(timerId))
            .catch(() => endFilterTimer(timerId));
        } else {
          endFilterTimer(timerId);
        }
        
        return result;
      } catch (error) {
        endFilterTimer(timerId);
        throw error;
      }
    }) as T, debounceDelay);
  }, [debounceDelay, startFilterTimer, endFilterTimer]);
  
  // Função throttled otimizada
  const throttledFilter = useCallback(<T extends (...args: any[]) => any>(callback: T): T => {
    return useThrottledCallback(((...args: Parameters<T>) => {
      const timerId = startFilterTimer('throttled');
      
      try {
        const result = callback(...args);
        
        // Se for uma Promise, aguardar conclusão
        if (result && typeof result.then === 'function') {
          result
            .then(() => endFilterTimer(timerId))
            .catch(() => endFilterTimer(timerId));
        } else {
          endFilterTimer(timerId);
        }
        
        return result;
      } catch (error) {
        endFilterTimer(timerId);
        throw error;
      }
    }) as T, throttleDelay);
  }, [throttleDelay, startFilterTimer, endFilterTimer]);
  
  // Limpar métricas
  const clearMetrics = useCallback(() => {
    setMetrics({
      totalFilters: 0,
      averageResponseTime: 0,
      slowestFilter: 0,
      fastestFilter: 0,
      lastFilterTime: 0,
      filterHistory: [],
    });
    activeTimersRef.current.clear();
    setIsFilterInProgress(false);
  }, []);
  
  // Cleanup ao desmontar
  useEffect(() => {
    return () => {
      activeTimersRef.current.clear();
    };
  }, []);
  
  return {
    debouncedFilter,
    throttledFilter,
    metrics,
    startFilterTimer,
    endFilterTimer,
    clearMetrics,
    isFilterInProgress,
  };
};

/**
 * Hook simplificado para performance de filtros com configurações padrão
 */
export const useSimpleFilterPerformance = () => {
  return useFilterPerformance({
    debounceDelay: 300,
    throttleDelay: 100,
    maxHistorySize: 50,
    enableMetrics: true,
  });
};

/**
 * Hook para filtros de alta frequência (ex: busca em tempo real)
 */
export const useHighFrequencyFilterPerformance = () => {
  return useFilterPerformance({
    debounceDelay: 150,
    throttleDelay: 50,
    maxHistorySize: 200,
    enableMetrics: true,
  });
};