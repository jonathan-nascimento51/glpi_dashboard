// Contextos da aplicação para gerenciamento de estado global

import React, { createContext, useContext, useReducer, useCallback, ReactNode } from 'react';
import { useNotifications, useTheme, useLocalCache } from '../hooks';
import type { DashboardMetrics, Filters, User, NotificationConfig } from '../types';

// Tipos para o estado da aplicação
interface AppState {
  user: User | null;
  dashboardData: DashboardMetrics | null;
  filters: Partial<Filters>;
  isLoading: boolean;
  error: string | null;
  lastUpdated: Date | null;
  settings: {
    autoRefresh: boolean;
    refreshInterval: number;
    theme: 'light' | 'dark';
    notifications: NotificationConfig;
    language: string;
    dateFormat: string;
  };
  cache: {
    enabled: boolean;
    stats: {
      hits: number;
      misses: number;
      size: number;
    };
  };
  performance: {
    monitoring: boolean;
    metrics: {
      responseTime: number;
      memoryUsage: number;
      renderCount: number;
    };
  };
}

// Ações disponíveis
type AppAction =
  | { type: 'SET_USER'; payload: User | null }
  | { type: 'SET_DASHBOARD_DATA'; payload: DashboardMetrics }
  | { type: 'SET_FILTERS'; payload: Partial<Filters> }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_LAST_UPDATED'; payload: Date }
  | { type: 'UPDATE_SETTINGS'; payload: Partial<AppState['settings']> }
  | { type: 'UPDATE_CACHE_STATS'; payload: Partial<AppState['cache']['stats']> }
  | { type: 'UPDATE_PERFORMANCE_METRICS'; payload: Partial<AppState['performance']['metrics']> }
  | { type: 'TOGGLE_PERFORMANCE_MONITORING' }
  | { type: 'TOGGLE_CACHE' }
  | { type: 'RESET_STATE' };

// Estado inicial
const initialState: AppState = {
  user: null,
  dashboardData: null,
  filters: {},
  isLoading: false,
  error: null,
  lastUpdated: null,
  settings: {
    autoRefresh: true,
    refreshInterval: 30000,
    theme: 'light',
    notifications: {
      enabled: true,
      duration: 5000,
      maxNotifications: 5,
    },
    language: 'pt-BR',
    dateFormat: 'DD/MM/YYYY HH:mm',
  },
  cache: {
    enabled: true,
    stats: {
      hits: 0,
      misses: 0,
      size: 0,
    },
  },
  performance: {
    monitoring: false,
    metrics: {
      responseTime: 0,
      memoryUsage: 0,
      renderCount: 0,
    },
  },
};

// Reducer para gerenciar o estado
const appReducer = (state: AppState, action: AppAction): AppState => {
  switch (action.type) {
    case 'SET_USER':
      return {
        ...state,
        user: action.payload,
      };

    case 'SET_DASHBOARD_DATA':
      return {
        ...state,
        dashboardData: action.payload,
        isLoading: false,
        error: null,
      };

    case 'SET_FILTERS':
      return {
        ...state,
        filters: action.payload,
      };

    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
        error: action.payload ? null : state.error,
      };

    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
        isLoading: false,
      };

    case 'SET_LAST_UPDATED':
      return {
        ...state,
        lastUpdated: action.payload,
      };

    case 'UPDATE_SETTINGS':
      return {
        ...state,
        settings: {
          ...state.settings,
          ...action.payload,
        },
      };

    case 'UPDATE_CACHE_STATS':
      return {
        ...state,
        cache: {
          ...state.cache,
          stats: {
            ...state.cache.stats,
            ...action.payload,
          },
        },
      };

    case 'UPDATE_PERFORMANCE_METRICS':
      return {
        ...state,
        performance: {
          ...state.performance,
          metrics: {
            ...state.performance.metrics,
            ...action.payload,
          },
        },
      };

    case 'TOGGLE_PERFORMANCE_MONITORING':
      return {
        ...state,
        performance: {
          ...state.performance,
          monitoring: !state.performance.monitoring,
        },
      };

    case 'TOGGLE_CACHE':
      return {
        ...state,
        cache: {
          ...state.cache,
          enabled: !state.cache.enabled,
        },
      };

    case 'RESET_STATE':
      return {
        ...initialState,
        settings: state.settings, // Manter configurações do usuário
      };

    default:
      return state;
  }
};

// Interface do contexto
interface AppContextType {
  state: AppState;
  dispatch: React.Dispatch<AppAction>;
  actions: {
    setUser: (user: User | null) => void;
    setDashboardData: (data: DashboardMetrics) => void;
    setFilters: (filters: Partial<Filters>) => void;
    setLoading: (loading: boolean) => void;
    setError: (error: string | null) => void;
    updateSettings: (settings: Partial<AppState['settings']>) => void;
    updateCacheStats: (stats: Partial<AppState['cache']['stats']>) => void;
    updatePerformanceMetrics: (metrics: Partial<AppState['performance']['metrics']>) => void;
    togglePerformanceMonitoring: () => void;
    toggleCache: () => void;
    resetState: () => void;
    refreshData: () => Promise<void>;
    clearCache: () => void;
  };
  notifications: ReturnType<typeof useNotifications>;
  theme: ReturnType<typeof useTheme>;
}

// Criar o contexto
const AppContext = createContext<AppContextType | undefined>(undefined);

// Provider do contexto
interface AppProviderProps {
  children: ReactNode;
}

export const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState);
  const notifications = useNotifications(state.settings.notifications);
  const theme = useTheme();
  const { setCachedData, clearCache: clearLocalCache } = useLocalCache<DashboardMetrics>('dashboard-data');

  // Ações do contexto
  const actions = {
    setUser: useCallback((user: User | null) => {
      dispatch({ type: 'SET_USER', payload: user });
    }, []),

    setDashboardData: useCallback((data: DashboardMetrics) => {
      dispatch({ type: 'SET_DASHBOARD_DATA', payload: data });
      dispatch({ type: 'SET_LAST_UPDATED', payload: new Date() });
      
      // Salvar no cache se habilitado
      if (state.cache.enabled) {
        setCachedData(data);
        dispatch({ 
          type: 'UPDATE_CACHE_STATS', 
          payload: { size: state.cache.stats.size + 1 }
        });
      }
    }, [state.cache.enabled, setCachedData]),

    setFilters: useCallback((filters: Partial<Filters>) => {
      dispatch({ type: 'SET_FILTERS', payload: filters });
    }, []),

    setLoading: useCallback((loading: boolean) => {
      dispatch({ type: 'SET_LOADING', payload: loading });
    }, []),

    setError: useCallback((error: string | null) => {
      dispatch({ type: 'SET_ERROR', payload: error });
      if (error) {
        notifications.showError(error);
      }
    }, [notifications]),

    updateSettings: useCallback((settings: Partial<AppState['settings']>) => {
      dispatch({ type: 'UPDATE_SETTINGS', payload: settings });
      
      // Salvar configurações no localStorage
      try {
        const currentSettings = JSON.parse(localStorage.getItem('app-settings') || '{}');
        const newSettings = { ...currentSettings, ...settings };
        localStorage.setItem('app-settings', JSON.stringify(newSettings));
      } catch (error) {
          // Erro ao salvar configurações no localStorage
        }
    }, []),

    updateCacheStats: useCallback((stats: Partial<AppState['cache']['stats']>) => {
      dispatch({ type: 'UPDATE_CACHE_STATS', payload: stats });
    }, []),

    updatePerformanceMetrics: useCallback((metrics: Partial<AppState['performance']['metrics']>) => {
      dispatch({ type: 'UPDATE_PERFORMANCE_METRICS', payload: metrics });
    }, []),

    togglePerformanceMonitoring: useCallback(() => {
      dispatch({ type: 'TOGGLE_PERFORMANCE_MONITORING' });
      const newState = !state.performance.monitoring;
      notifications.showInfo(
        newState ? 'Monitoramento de performance ativado' : 'Monitoramento de performance desativado'
      );
    }, [state.performance.monitoring, notifications]),

    toggleCache: useCallback(() => {
      dispatch({ type: 'TOGGLE_CACHE' });
      const newState = !state.cache.enabled;
      notifications.showInfo(
        newState ? 'Cache ativado' : 'Cache desativado'
      );
      
      if (!newState) {
        clearLocalCache();
      }
    }, [state.cache.enabled, notifications, clearLocalCache]),

    resetState: useCallback(() => {
      dispatch({ type: 'RESET_STATE' });
      clearLocalCache();
      notifications.showInfo('Estado da aplicação resetado');
    }, [clearLocalCache, notifications]),

    refreshData: useCallback(async () => {
      try {
        dispatch({ type: 'SET_LOADING', payload: true });
        
        // Simular chamada à API
        const response = await fetch('/api/dashboard/metrics');
        if (!response.ok) {
          throw new Error(`Erro na API: ${response.status}`);
        }
        
        const data = await response.json();
        dispatch({ type: 'SET_DASHBOARD_DATA', payload: data });
        
        // Atualizar estatísticas de cache
        if (state.cache.enabled) {
          dispatch({ 
            type: 'UPDATE_CACHE_STATS', 
            payload: { hits: state.cache.stats.hits + 1 }
          });
        }
        
        notifications.showSuccess('Dados atualizados com sucesso');
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Erro desconhecido';
        dispatch({ type: 'SET_ERROR', payload: errorMessage });
        
        // Atualizar estatísticas de cache miss
        if (state.cache.enabled) {
          dispatch({ 
            type: 'UPDATE_CACHE_STATS', 
            payload: { misses: state.cache.stats.misses + 1 }
          });
        }
      }
    }, [state.cache.enabled, state.cache.stats, notifications]),

    clearCache: useCallback(() => {
      clearLocalCache();
      dispatch({ 
        type: 'UPDATE_CACHE_STATS', 
        payload: { hits: 0, misses: 0, size: 0 }
      });
      notifications.showSuccess('Cache limpo com sucesso');
    }, [clearLocalCache, notifications]),
  };

  // Carregar configurações salvas no localStorage
  React.useEffect(() => {
    try {
      const savedSettings = localStorage.getItem('app-settings');
      if (savedSettings) {
        const settings = JSON.parse(savedSettings);
        dispatch({ type: 'UPDATE_SETTINGS', payload: settings });
      }
    } catch (error) {
      // Erro ao carregar configurações do localStorage
    }
  }, []);

  // Sincronizar tema com configurações
  React.useEffect(() => {
    if (state.settings.theme !== theme.theme) {
      if (state.settings.theme === 'dark') {
        theme.setDarkTheme();
      } else {
        theme.setLightTheme();
      }
    }
  }, [state.settings.theme, theme]);

  const contextValue: AppContextType = {
    state,
    dispatch,
    actions,
    notifications,
    theme,
  };

  return (
    <AppContext.Provider value={contextValue}>
      {children}
    </AppContext.Provider>
  );
};

// Hook para usar o contexto
export const useAppContext = (): AppContextType => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useAppContext deve ser usado dentro de um AppProvider');
  }
  return context;
};

// Hook para usar apenas o estado
export const useAppState = () => {
  const { state } = useAppContext();
  return state;
};

// Hook para usar apenas as ações
export const useAppActions = () => {
  const { actions } = useAppContext();
  return actions;
};

// Hook para usar notificações
export const useAppNotifications = () => {
  const { notifications } = useAppContext();
  return notifications;
};

// Hook para usar tema
export const useAppTheme = () => {
  const { theme } = useAppContext();
  return theme;
};

// Seletores para partes específicas do estado
export const useUser = () => {
  const { state } = useAppContext();
  return state.user;
};

export const useDashboardState = () => {
  const { state } = useAppContext();
  return {
    data: state.dashboardData,
    isLoading: state.isLoading,
    error: state.error,
    lastUpdated: state.lastUpdated,
  };
};

export const useFiltersState = () => {
  const { state } = useAppContext();
  return state.filters;
};

export const useSettingsState = () => {
  const { state } = useAppContext();
  return state.settings;
};

export const useCacheState = () => {
  const { state } = useAppContext();
  return state.cache;
};

export const usePerformanceState = () => {
  const { state } = useAppContext();
  return state.performance;
};