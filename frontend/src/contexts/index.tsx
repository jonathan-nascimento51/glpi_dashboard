// ============================================================================
// CONTEXTOS REACT DO DASHBOARD GLPI
// Gerenciamento de estado global da aplicação
// ============================================================================

import React, { createContext, useContext, useReducer, ReactNode } from 'react';
import { CONFIG } from '../config';
import { utils } from '../utils';

// ============================================================================
// TIPOS E INTERFACES
// ============================================================================

interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  avatar?: string;
  permissions: string[];
}

interface DashboardMetrics {
  totalTickets: number;
  openTickets: number;
  closedTickets: number;
  pendingTickets: number;
  averageResolutionTime: number;
  userSatisfaction: number;
  systemUptime: number;
  activeUsers: number;
}

interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  timestamp: Date;
  read: boolean;
}

interface AppSettings {
  theme: 'light' | 'dark';
  language: string;
  refreshInterval: number;
  notificationsEnabled: boolean;
  soundEnabled: boolean;
}

// ============================================================================
// ESTADO DA APLICAÇÃO
// ============================================================================

interface AppState {
  // Autenticação
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  
  // Dashboard
  metrics: DashboardMetrics | null;
  lastUpdated: Date | null;
  
  // Notificações
  notifications: Notification[];
  unreadCount: number;
  
  // Configurações
  settings: AppSettings;
  
  // UI
  sidebarOpen: boolean;
  modalOpen: boolean;
  currentModal: string | null;
  
  // Erros
  error: string | null;
}

const initialState: AppState = {
  user: null,
  isAuthenticated: false,
  isLoading: false,
  metrics: null,
  lastUpdated: null,
  notifications: [],
  unreadCount: 0,
  settings: {
    theme: CONFIG.THEME.DEFAULT_THEME,
    language: CONFIG.LOCALIZATION.DEFAULT_LANGUAGE,
    refreshInterval: CONFIG.DASHBOARD.REFRESH_INTERVAL,
    notificationsEnabled: true,
    soundEnabled: true,
  },
  sidebarOpen: true,
  modalOpen: false,
  currentModal: null,
  error: null,
};

// ============================================================================
// AÇÕES
// ============================================================================

type AppAction =
  // Autenticação
  | { type: 'SET_USER'; payload: User }
  | { type: 'LOGOUT' }
  | { type: 'SET_LOADING'; payload: boolean }
  
  // Dashboard
  | { type: 'SET_METRICS'; payload: DashboardMetrics }
  | { type: 'UPDATE_LAST_UPDATED' }
  
  // Notificações
  | { type: 'ADD_NOTIFICATION'; payload: Omit<Notification, 'id' | 'timestamp' | 'read'> }
  | { type: 'REMOVE_NOTIFICATION'; payload: string }
  | { type: 'MARK_NOTIFICATION_READ'; payload: string }
  | { type: 'MARK_ALL_NOTIFICATIONS_READ' }
  | { type: 'CLEAR_NOTIFICATIONS' }
  
  // Configurações
  | { type: 'UPDATE_SETTINGS'; payload: Partial<AppSettings> }
  | { type: 'SET_THEME'; payload: 'light' | 'dark' }
  | { type: 'SET_LANGUAGE'; payload: string }
  
  // UI
  | { type: 'TOGGLE_SIDEBAR' }
  | { type: 'SET_SIDEBAR'; payload: boolean }
  | { type: 'OPEN_MODAL'; payload: string }
  | { type: 'CLOSE_MODAL' }
  
  // Erros
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'CLEAR_ERROR' };

// ============================================================================
// REDUCER
// ============================================================================

const appReducer = (state: AppState, action: AppAction): AppState => {
  switch (action.type) {
    // Autenticação
    case 'SET_USER':
      return {
        ...state,
        user: action.payload,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      };
    
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        metrics: null,
        notifications: [],
        unreadCount: 0,
        error: null,
      };
    
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      };
    
    // Dashboard
    case 'SET_METRICS':
      return {
        ...state,
        metrics: action.payload,
        lastUpdated: new Date(),
        error: null,
      };
    
    case 'UPDATE_LAST_UPDATED':
      return {
        ...state,
        lastUpdated: new Date(),
      };
    
    // Notificações
    case 'ADD_NOTIFICATION': {
      const newNotification: Notification = {
        ...action.payload,
        id: utils.generateId(),
        timestamp: new Date(),
        read: false,
      };
      
      const notifications = [newNotification, ...state.notifications]
        .slice(0, CONFIG.NOTIFICATION.MAX_NOTIFICATIONS);
      
      return {
        ...state,
        notifications,
        unreadCount: state.unreadCount + 1,
      };
    }
    
    case 'REMOVE_NOTIFICATION': {
      const notifications = state.notifications.filter(n => n.id !== action.payload);
      const removedNotification = state.notifications.find(n => n.id === action.payload);
      const unreadCount = removedNotification && !removedNotification.read 
        ? state.unreadCount - 1 
        : state.unreadCount;
      
      return {
        ...state,
        notifications,
        unreadCount: Math.max(0, unreadCount),
      };
    }
    
    case 'MARK_NOTIFICATION_READ': {
      const notifications = state.notifications.map(n => 
        n.id === action.payload ? { ...n, read: true } : n
      );
      const wasUnread = state.notifications.find(n => n.id === action.payload && !n.read);
      
      return {
        ...state,
        notifications,
        unreadCount: wasUnread ? state.unreadCount - 1 : state.unreadCount,
      };
    }
    
    case 'MARK_ALL_NOTIFICATIONS_READ':
      return {
        ...state,
        notifications: state.notifications.map(n => ({ ...n, read: true })),
        unreadCount: 0,
      };
    
    case 'CLEAR_NOTIFICATIONS':
      return {
        ...state,
        notifications: [],
        unreadCount: 0,
      };
    
    // Configurações
    case 'UPDATE_SETTINGS':
      return {
        ...state,
        settings: {
          ...state.settings,
          ...action.payload,
        },
      };
    
    case 'SET_THEME':
      return {
        ...state,
        settings: {
          ...state.settings,
          theme: action.payload,
        },
      };
    
    case 'SET_LANGUAGE':
      return {
        ...state,
        settings: {
          ...state.settings,
          language: action.payload,
        },
      };
    
    // UI
    case 'TOGGLE_SIDEBAR':
      return {
        ...state,
        sidebarOpen: !state.sidebarOpen,
      };
    
    case 'SET_SIDEBAR':
      return {
        ...state,
        sidebarOpen: action.payload,
      };
    
    case 'OPEN_MODAL':
      return {
        ...state,
        modalOpen: true,
        currentModal: action.payload,
      };
    
    case 'CLOSE_MODAL':
      return {
        ...state,
        modalOpen: false,
        currentModal: null,
      };
    
    // Erros
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
        isLoading: false,
      };
    
    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
      };
    
    default:
      return state;
  }
};

// ============================================================================
// CONTEXTO DA APLICAÇÃO
// ============================================================================

interface AppContextType {
  state: AppState;
  dispatch: React.Dispatch<AppAction>;
  
  // Actions helpers
  login: (user: User) => void;
  logout: () => void;
  setLoading: (loading: boolean) => void;
  
  updateMetrics: (metrics: DashboardMetrics) => void;
  
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => void;
  removeNotification: (id: string) => void;
  markNotificationRead: (id: string) => void;
  markAllNotificationsRead: () => void;
  clearNotifications: () => void;
  
  updateSettings: (settings: Partial<AppSettings>) => void;
  setTheme: (theme: 'light' | 'dark') => void;
  toggleTheme: () => void;
  setLanguage: (language: string) => void;
  
  toggleSidebar: () => void;
  setSidebar: (open: boolean) => void;
  openModal: (modal: string) => void;
  closeModal: () => void;
  
  setError: (error: string | null) => void;
  clearError: () => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

// ============================================================================
// PROVIDER
// ============================================================================

interface AppProviderProps {
  children: ReactNode;
}

export const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState);
  
  // Action helpers
  const login = (user: User) => dispatch({ type: 'SET_USER', payload: user });
  const logout = () => dispatch({ type: 'LOGOUT' });
  const setLoading = (loading: boolean) => dispatch({ type: 'SET_LOADING', payload: loading });
  
  const updateMetrics = (metrics: DashboardMetrics) => 
    dispatch({ type: 'SET_METRICS', payload: metrics });
  
  const addNotification = (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => 
    dispatch({ type: 'ADD_NOTIFICATION', payload: notification });
  const removeNotification = (id: string) => 
    dispatch({ type: 'REMOVE_NOTIFICATION', payload: id });
  const markNotificationRead = (id: string) => 
    dispatch({ type: 'MARK_NOTIFICATION_READ', payload: id });
  const markAllNotificationsRead = () => 
    dispatch({ type: 'MARK_ALL_NOTIFICATIONS_READ' });
  const clearNotifications = () => 
    dispatch({ type: 'CLEAR_NOTIFICATIONS' });
  
  const updateSettings = (settings: Partial<AppSettings>) => 
    dispatch({ type: 'UPDATE_SETTINGS', payload: settings });
  const setTheme = (theme: 'light' | 'dark') => 
    dispatch({ type: 'SET_THEME', payload: theme });
  const toggleTheme = () => 
    setTheme(state.settings.theme === 'light' ? 'dark' : 'light');
  const setLanguage = (language: string) => 
    dispatch({ type: 'SET_LANGUAGE', payload: language });
  
  const toggleSidebar = () => dispatch({ type: 'TOGGLE_SIDEBAR' });
  const setSidebar = (open: boolean) => dispatch({ type: 'SET_SIDEBAR', payload: open });
  const openModal = (modal: string) => dispatch({ type: 'OPEN_MODAL', payload: modal });
  const closeModal = () => dispatch({ type: 'CLOSE_MODAL' });
  
  const setError = (error: string | null) => dispatch({ type: 'SET_ERROR', payload: error });
  const clearError = () => dispatch({ type: 'CLEAR_ERROR' });
  
  const value: AppContextType = {
    state,
    dispatch,
    login,
    logout,
    setLoading,
    updateMetrics,
    addNotification,
    removeNotification,
    markNotificationRead,
    markAllNotificationsRead,
    clearNotifications,
    updateSettings,
    setTheme,
    toggleTheme,
    setLanguage,
    toggleSidebar,
    setSidebar,
    openModal,
    closeModal,
    setError,
    clearError,
  };
  
  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
};

// ============================================================================
// HOOK PARA USAR O CONTEXTO
// ============================================================================

export const useApp = (): AppContextType => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp deve ser usado dentro de um AppProvider');
  }
  return context;
};

// ============================================================================
// HOOKS ESPECÍFICOS
// ============================================================================

/**
 * Hook para gerenciar autenticação
 */
export const useAuth = () => {
  const { state, login, logout, setLoading } = useApp();
  
  return {
    user: state.user,
    isAuthenticated: state.isAuthenticated,
    isLoading: state.isLoading,
    login,
    logout,
    setLoading,
  };
};

/**
 * Hook para gerenciar métricas do dashboard
 */
export const useDashboard = () => {
  const { state, updateMetrics } = useApp();
  
  return {
    metrics: state.metrics,
    lastUpdated: state.lastUpdated,
    updateMetrics,
  };
};

/**
 * Hook para gerenciar notificações
 */
export const useNotifications = () => {
  const { 
    state, 
    addNotification, 
    removeNotification, 
    markNotificationRead, 
    markAllNotificationsRead, 
    clearNotifications 
  } = useApp();
  
  return {
    notifications: state.notifications,
    unreadCount: state.unreadCount,
    addNotification,
    removeNotification,
    markNotificationRead,
    markAllNotificationsRead,
    clearNotifications,
  };
};

/**
 * Hook para gerenciar configurações
 */
export const useSettings = () => {
  const { state, updateSettings, setTheme, toggleTheme, setLanguage } = useApp();
  
  return {
    settings: state.settings,
    updateSettings,
    setTheme,
    toggleTheme,
    setLanguage,
  };
};

/**
 * Hook para gerenciar UI
 */
export const useUI = () => {
  const { 
    state, 
    toggleSidebar, 
    setSidebar, 
    openModal, 
    closeModal, 
    setError, 
    clearError 
  } = useApp();
  
  return {
    sidebarOpen: state.sidebarOpen,
    modalOpen: state.modalOpen,
    currentModal: state.currentModal,
    error: state.error,
    toggleSidebar,
    setSidebar,
    openModal,
    closeModal,
    setError,
    clearError,
  };
};

// ============================================================================
// EXPORTAÇÃO CONSOLIDADA
// ============================================================================
export const contexts = {
  AppProvider,
  useApp,
  useAuth,
  useDashboard,
  useNotifications,
  useSettings,
  useUI,
};

export default contexts;

// Tipos exportados
export type {
  User,
  DashboardMetrics,
  Notification,
  AppSettings,
  AppState,
  AppAction,
  AppContextType,
};