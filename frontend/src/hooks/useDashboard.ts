import { useState, useEffect, useCallback } from 'react';
import { DashboardState, MetricsData, SystemStatus, FilterState, NotificationData, Theme } from '../types';
import { apiService } from '../services/api';

const initialFilterState: FilterState = {
  period: 'today',
  levels: ['n1', 'n2', 'n3', 'n4'],
  status: ['new', 'progress', 'pending', 'resolved'],
  priority: ['high', 'medium', 'low'],
};

const initialMetrics: MetricsData = {
  novos: 0,
  pendentes: 0,
  progresso: 0,
  resolvidos: 0,
  total: 0,
  niveis: {
    n1: {
      novos: 0,
      pendentes: 0,
      progresso: 0,
      resolvidos: 0
    },
    n2: {
      novos: 0,
      pendentes: 0,
      progresso: 0,
      resolvidos: 0
    },
    n3: {
      novos: 0,
      pendentes: 0,
      progresso: 0,
      resolvidos: 0
    },
    n4: {
      novos: 0,
      pendentes: 0,
      progresso: 0,
      resolvidos: 0
    }
  },
  tendencias: {
    novos: '0',
    pendentes: '0',
    progresso: '0',
    resolvidos: '0'
  }
};

const initialSystemStatus: SystemStatus = {
  api: 'unknown',
  database: 'unknown',
  last_update: '',
  version: '1.0.0'
};

const initialState: DashboardState = {
  metrics: initialMetrics,
  systemStatus: initialSystemStatus,
  isLoading: true,
  error: null,
  lastUpdated: null,
  filters: initialFilterState,
  searchQuery: '',
  searchResults: [],
  notifications: [],
  theme: 'light',
};

export const useDashboard = () => {
  const [state, setState] = useState<DashboardState>(initialState);

  // Load data from API
  const loadData = useCallback(async () => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      const [metrics, systemStatus] = await Promise.all([
        apiService.getMetrics(),
        apiService.getSystemStatus(),
      ]);
      
      setState(prev => ({
        ...prev,
        metrics,
        systemStatus,
        isLoading: false,
        lastUpdated: new Date(),
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Erro desconhecido',
      }));
    }
  }, []);

  // Force refresh
  const forceRefresh = useCallback(() => {
    loadData();
  }, [loadData]);

  // Update filters
  const updateFilters = useCallback((newFilters: Partial<FilterState>) => {
    setState(prev => ({
      ...prev,
      filters: { ...prev.filters, ...newFilters },
    }));
  }, []);

  // Search functionality
  const search = useCallback(async (query: string) => {
    setState(prev => ({ ...prev, searchQuery: query }));
    
    if (query.trim() === '') {
      setState(prev => ({ ...prev, searchResults: [] }));
      return;
    }
    
    try {
      const results = await apiService.search(query);
      setState(prev => ({ ...prev, searchResults: results }));
    } catch (error) {
      console.error('Search error:', error);
    }
  }, []);

  // Add notification
  const addNotification = useCallback((notification: Omit<NotificationData, 'id' | 'timestamp'>) => {
    const newNotification: NotificationData = {
      ...notification,
      id: Date.now().toString(),
      timestamp: new Date(),
    };
    
    setState(prev => ({
      ...prev,
      notifications: [...prev.notifications, newNotification],
    }));
    
    // Auto-remove notification after duration
    if (notification.duration) {
      setTimeout(() => {
        removeNotification(newNotification.id);
      }, notification.duration);
    }
  }, []);

  // Remove notification
  const removeNotification = useCallback((id: string) => {
    setState(prev => ({
      ...prev,
      notifications: prev.notifications.filter(n => n.id !== id),
    }));
  }, []);

  // Change theme
  const changeTheme = useCallback((theme: Theme) => {
    setState(prev => ({ ...prev, theme }));
    localStorage.setItem('dashboard-theme', theme);
    
    // Apply theme to document
    document.documentElement.className = theme === 'dark' ? 'dark' : '';
  }, []);

  // Load saved theme on mount
  useEffect(() => {
    const savedTheme = localStorage.getItem('dashboard-theme') as Theme;
    if (savedTheme) {
      changeTheme(savedTheme);
    }
  }, [changeTheme]);

  // Initial data load
  useEffect(() => {
    loadData();
  }, [loadData]);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      if (!state.isLoading) {
        loadData();
      }
    }, 30000);
    
    return () => clearInterval(interval);
  }, [loadData, state.isLoading]);

  // Health check every minute
  useEffect(() => {
    const healthCheckInterval = setInterval(async () => {
      try {
        const isHealthy = await apiService.healthCheck();
        if (!isHealthy) {
          console.warn('Health check failed');
        }
      } catch (error) {
        console.error('Health check error:', error);
      }
    }, 60000);
    
    return () => clearInterval(healthCheckInterval);
  }, []);

  return {
    ...state,
    loadData,
    forceRefresh,
    updateFilters,
    search,
    addNotification,
    removeNotification,
    changeTheme,
  };
};