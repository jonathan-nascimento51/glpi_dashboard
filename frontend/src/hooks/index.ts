// Hooks customizados da aplicação

import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { debounce, throttle } from '../utils/helpers';
import { validateFilters, validateDashboardMetrics } from '../utils/validations';
import type { DashboardMetrics, Filters, NotificationConfig } from '../types';

/**
 * Hook para gerenciar estado de loading
 */
export const useLoading = (initialState = false) => {
  const [isLoading, setIsLoading] = useState(initialState);
  const [error, setError] = useState<string | null>(null);

  const startLoading = useCallback(() => {
    setIsLoading(true);
    setError(null);
  }, []);

  const stopLoading = useCallback(() => {
    setIsLoading(false);
  }, []);

  const setLoadingError = useCallback((errorMessage: string) => {
    setIsLoading(false);
    setError(errorMessage);
  }, []);

  const reset = useCallback(() => {
    setIsLoading(false);
    setError(null);
  }, []);

  return {
    isLoading,
    error,
    startLoading,
    stopLoading,
    setLoadingError,
    reset,
  };
};

/**
 * Hook para gerenciar dados do dashboard com cache
 */
export const useDashboardData = (refreshInterval = 30000) => {
  const [data, setData] = useState<DashboardMetrics | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const { isLoading, error, startLoading, stopLoading, setLoadingError } = useLoading();
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const fetchData = useCallback(async () => {
    try {
      startLoading();
      
      // Simular chamada à API
      const response = await fetch('/api/dashboard/metrics');
      if (!response.ok) {
        throw new Error(`Erro na API: ${response.status}`);
      }
      
      const metrics = await response.json();
      
      // Validar dados recebidos
      const validation = validateDashboardMetrics(metrics);
      if (!validation.isValid) {
        throw new Error(`Dados inválidos: ${validation.errors.join(', ')}`);
      }
      
      setData(metrics);
      setLastUpdated(new Date());
      stopLoading();
    } catch (err) {
      setLoadingError(err instanceof Error ? err.message : 'Erro desconhecido');
    }
  }, [startLoading, stopLoading, setLoadingError]);

  const startAutoRefresh = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
    
    intervalRef.current = setInterval(fetchData, refreshInterval);
  }, [fetchData, refreshInterval]);

  const stopAutoRefresh = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  const refresh = useCallback(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    fetchData();
    startAutoRefresh();
    
    return () => {
      stopAutoRefresh();
    };
  }, [fetchData, startAutoRefresh, stopAutoRefresh]);

  return {
    data,
    lastUpdated,
    isLoading,
    error,
    refresh,
    startAutoRefresh,
    stopAutoRefresh,
  };
};

/**
 * Hook para gerenciar filtros com debounce
 */
export const useFilters = (initialFilters: Partial<Filters> = {}, debounceMs = 300) => {
  const [filters, setFilters] = useState<Partial<Filters>>(initialFilters);
  const [debouncedFilters, setDebouncedFilters] = useState<Partial<Filters>>(initialFilters);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);

  // Debounce para filtros
  const debouncedSetFilters = useMemo(
    () => debounce((newFilters: Partial<Filters>) => {
      const validation = validateFilters(newFilters);
      setValidationErrors(validation.errors);
      
      if (validation.isValid) {
        setDebouncedFilters(newFilters);
      }
    }, debounceMs),
    [debounceMs]
  );

  const updateFilters = useCallback((newFilters: Partial<Filters>) => {
    setFilters(newFilters);
    debouncedSetFilters(newFilters);
  }, [debouncedSetFilters]);

  const updateFilter = useCallback((key: keyof Filters, value: any) => {
    const newFilters = { ...filters, [key]: value };
    updateFilters(newFilters);
  }, [filters, updateFilters]);

  const clearFilters = useCallback(() => {
    const clearedFilters = {};
    setFilters(clearedFilters);
    setDebouncedFilters(clearedFilters);
    setValidationErrors([]);
  }, []);

  const resetFilters = useCallback(() => {
    setFilters(initialFilters);
    setDebouncedFilters(initialFilters);
    setValidationErrors([]);
  }, [initialFilters]);

  return {
    filters,
    debouncedFilters,
    validationErrors,
    updateFilters,
    updateFilter,
    clearFilters,
    resetFilters,
    hasErrors: validationErrors.length > 0,
  };
};

/**
 * Hook para gerenciar notificações
 */
export const useNotifications = (config: NotificationConfig = { enabled: true, duration: 5000 }) => {
  const [notifications, setNotifications] = useState<Array<{
    id: string;
    type: 'success' | 'error' | 'warning' | 'info';
    message: string;
    timestamp: Date;
  }>>([]);

  const addNotification = useCallback((type: 'success' | 'error' | 'warning' | 'info', message: string) => {
    if (!config.enabled) return;

    const id = `notification-${Date.now()}-${Math.random()}`;
    const notification = {
      id,
      type,
      message,
      timestamp: new Date(),
    };

    setNotifications(prev => [...prev, notification]);

    // Auto-remove após duração configurada
    if (config.duration && config.duration > 0) {
      setTimeout(() => {
        removeNotification(id);
      }, config.duration);
    }
  }, [config]);

  const removeNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id));
  }, []);

  const clearNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  const showSuccess = useCallback((message: string) => {
    addNotification('success', message);
  }, [addNotification]);

  const showError = useCallback((message: string) => {
    addNotification('error', message);
  }, [addNotification]);

  const showWarning = useCallback((message: string) => {
    addNotification('warning', message);
  }, [addNotification]);

  const showInfo = useCallback((message: string) => {
    addNotification('info', message);
  }, [addNotification]);

  return {
    notifications,
    addNotification,
    removeNotification,
    clearNotifications,
    showSuccess,
    showError,
    showWarning,
    showInfo,
  };
};

/**
 * Hook para gerenciar estado de performance
 */
export const usePerformanceMonitor = (sampleInterval = 1000) => {
  const [metrics, setMetrics] = useState({
    responseTime: 0,
    memoryUsage: 0,
    cpuUsage: 0,
    renderTime: 0,
  });
  const [isMonitoring, setIsMonitoring] = useState(false);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const startTimeRef = useRef<number>(0);

  const startMonitoring = useCallback(() => {
    setIsMonitoring(true);
    startTimeRef.current = performance.now();
    
    intervalRef.current = setInterval(() => {
      // Simular coleta de métricas
      const now = performance.now();
      const responseTime = now - startTimeRef.current;
      
      setMetrics(prev => ({
        ...prev,
        responseTime,
        memoryUsage: (performance as any).memory?.usedJSHeapSize || 0,
        renderTime: now,
      }));
    }, sampleInterval);
  }, [sampleInterval]);

  const stopMonitoring = useCallback(() => {
    setIsMonitoring(false);
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  const resetMetrics = useCallback(() => {
    setMetrics({
      responseTime: 0,
      memoryUsage: 0,
      cpuUsage: 0,
      renderTime: 0,
    });
    startTimeRef.current = performance.now();
  }, []);

  useEffect(() => {
    return () => {
      stopMonitoring();
    };
  }, [stopMonitoring]);

  return {
    metrics,
    isMonitoring,
    startMonitoring,
    stopMonitoring,
    resetMetrics,
  };
};

/**
 * Hook para gerenciar cache local
 */
export const useLocalCache = <T>(key: string, ttl = 300000) => { // 5 minutos padrão
  const [data, setData] = useState<T | null>(null);
  const [isExpired, setIsExpired] = useState(false);

  const getCachedData = useCallback((): T | null => {
    try {
      const cached = localStorage.getItem(key);
      if (!cached) return null;

      const { data: cachedData, timestamp } = JSON.parse(cached);
      const now = Date.now();
      
      if (now - timestamp > ttl) {
        setIsExpired(true);
        localStorage.removeItem(key);
        return null;
      }

      setIsExpired(false);
      return cachedData;
    } catch {
      return null;
    }
  }, [key, ttl]);

  const setCachedData = useCallback((newData: T) => {
    try {
      const cacheEntry = {
        data: newData,
        timestamp: Date.now(),
      };
      localStorage.setItem(key, JSON.stringify(cacheEntry));
      setData(newData);
      setIsExpired(false);
    } catch (error) {
      console.warn('Erro ao salvar no cache:', error);
    }
  }, [key]);

  const clearCache = useCallback(() => {
    localStorage.removeItem(key);
    setData(null);
    setIsExpired(false);
  }, [key]);

  const refreshCache = useCallback(() => {
    const cachedData = getCachedData();
    setData(cachedData);
  }, [getCachedData]);

  useEffect(() => {
    refreshCache();
  }, [refreshCache]);

  return {
    data,
    isExpired,
    setCachedData,
    clearCache,
    refreshCache,
  };
};

/**
 * Hook para gerenciar estado de modal/overlay
 */
export const useModal = (initialState = false) => {
  const [isOpen, setIsOpen] = useState(initialState);
  const [data, setData] = useState<any>(null);

  const openModal = useCallback((modalData?: any) => {
    setData(modalData || null);
    setIsOpen(true);
  }, []);

  const closeModal = useCallback(() => {
    setIsOpen(false);
    setData(null);
  }, []);

  const toggleModal = useCallback(() => {
    setIsOpen(prev => !prev);
    if (isOpen) {
      setData(null);
    }
  }, [isOpen]);

  return {
    isOpen,
    data,
    openModal,
    closeModal,
    toggleModal,
  };
};

/**
 * Hook para gerenciar scroll infinito
 */
export const useInfiniteScroll = (callback: () => void, threshold = 100) => {
  const [isFetching, setIsFetching] = useState(false);
  const elementRef = useRef<HTMLElement | null>(null);

  const handleScroll = useMemo(
    () => throttle(() => {
      const element = elementRef.current;
      if (!element || isFetching) return;

      const { scrollTop, scrollHeight, clientHeight } = element;
      const isNearBottom = scrollHeight - scrollTop - clientHeight < threshold;

      if (isNearBottom) {
        setIsFetching(true);
        callback();
      }
    }, 200),
    [callback, isFetching, threshold]
  );

  const setElement = useCallback((element: HTMLElement | null) => {
    if (elementRef.current) {
      elementRef.current.removeEventListener('scroll', handleScroll);
    }

    elementRef.current = element;

    if (element) {
      element.addEventListener('scroll', handleScroll);
    }
  }, [handleScroll]);

  const stopFetching = useCallback(() => {
    setIsFetching(false);
  }, []);

  useEffect(() => {
    return () => {
      if (elementRef.current) {
        elementRef.current.removeEventListener('scroll', handleScroll);
      }
    };
  }, [handleScroll]);

  return {
    isFetching,
    setElement,
    stopFetching,
  };
};

/**
 * Hook para detectar clique fora do elemento
 */
export const useClickOutside = (callback: () => void) => {
  const ref = useRef<HTMLElement | null>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (ref.current && !ref.current.contains(event.target as Node)) {
        callback();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [callback]);

  return ref;
};

/**
 * Hook para gerenciar tema
 */
export const useTheme = () => {
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    const saved = localStorage.getItem('theme');
    return (saved as 'light' | 'dark') || 'light';
  });

  const toggleTheme = useCallback(() => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
  }, [theme]);

  const setLightTheme = useCallback(() => {
    setTheme('light');
    localStorage.setItem('theme', 'light');
    document.documentElement.setAttribute('data-theme', 'light');
  }, []);

  const setDarkTheme = useCallback(() => {
    setTheme('dark');
    localStorage.setItem('theme', 'dark');
    document.documentElement.setAttribute('data-theme', 'dark');
  }, []);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  return {
    theme,
    toggleTheme,
    setLightTheme,
    setDarkTheme,
    isDark: theme === 'dark',
    isLight: theme === 'light',
  };
};