import type {
  AppConfig,
  CacheConfig,
  Theme,
  UserPreferences,
  ExportOptions
} from '../types/api';

/**
 * Constantes e configurações da aplicação
 */

// Configuração da API
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  TIMEOUT: 30000, // 30 segundos
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000, // 1 segundo
  ENDPOINTS: {
    METRICS: '/kpis',
    METRICS_FILTERED: '/kpis/filtered',
    HEALTH: '/health',
    TECHNICIAN_RANKING: '/technician-ranking',
    NEW_TICKETS: '/new-tickets'
  }
} as const;

// Configuração de cache
export const CACHE_CONFIG: CacheConfig = {
  enabled: true,
  ttl: 300000, // 5 minutos
  maxSize: 100,
  strategy: 'lru'
};

// Configuração padrão da aplicação
export const DEFAULT_APP_CONFIG: AppConfig = {
  theme: 'light',
  language: 'pt-BR',
  autoRefresh: true,
  refreshInterval: 30000, // 30 segundos
  showPerformanceMetrics: false,
  enableNotifications: true,
  dateFormat: 'DD/MM/YYYY',
  timeFormat: '24h',
  timezone: 'America/Sao_Paulo'
};

// Preferências padrão do usuário
export const DEFAULT_USER_PREFERENCES: UserPreferences = {
  theme: 'light',
  language: 'pt-BR',
  dateFormat: 'DD/MM/YYYY',
  timeFormat: '24h',
  autoRefresh: true,
  refreshInterval: 30000,
  showPerformanceMetrics: false,
  enableNotifications: true,
  dashboardLayout: 'grid',
  chartsEnabled: true,
  soundEnabled: false,
  emailNotifications: false,
  notifications: {
    enabled: true,
    types: ['success', 'error', 'warning', 'info']
  },
  dashboard: {
    defaultView: 'cards',
    autoRefresh: true,
    showTrends: true
  }
};

// Temas disponíveis
export const THEMES: Record<string, Theme> = {
  light: {
    name: 'light',
    displayName: 'Claro',
    colors: {
      primary: '#3B82F6',
      secondary: '#6B7280',
      success: '#10B981',
      warning: '#F59E0B',
      error: '#EF4444',
      info: '#3B82F6',
      background: '#FFFFFF',
      surface: '#F9FAFB',
      text: '#111827'
    },
    spacing: {
      xs: '0.25rem',
      sm: '0.5rem',
      md: '1rem',
      lg: '1.5rem',
      xl: '2rem'
    },
    borderRadius: {
      sm: '0.25rem',
      md: '0.5rem',
      lg: '0.75rem'
    }
  },
  dark: {
    name: 'dark',
    displayName: 'Escuro',
    colors: {
      primary: '#60A5FA',
      secondary: '#9CA3AF',
      success: '#34D399',
      warning: '#FBBF24',
      error: '#F87171',
      info: '#60A5FA',
      background: '#111827',
      surface: '#1F2937',
      text: '#F9FAFB'
    },
    spacing: {
      xs: '0.25rem',
      sm: '0.5rem',
      md: '1rem',
      lg: '1.5rem',
      xl: '2rem'
    },
    borderRadius: {
      sm: '0.25rem',
      md: '0.5rem',
      lg: '0.75rem'
    }
  },
  system: {
    name: 'system',
    displayName: 'Sistema',
    colors: {
      primary: '#3B82F6',
      secondary: '#6B7280',
      success: '#10B981',
      warning: '#F59E0B',
      error: '#EF4444',
      info: '#3B82F6',
      background: '#FFFFFF',
      surface: '#F9FAFB',
      text: '#111827'
    },
    spacing: {
      xs: '0.25rem',
      sm: '0.5rem',
      md: '1rem',
      lg: '1.5rem',
      xl: '2rem'
    },
    borderRadius: {
      sm: '0.25rem',
      md: '0.5rem',
      lg: '0.75rem'
    }
  }
};

// Opções de status
export const STATUS_OPTIONS = [
  { value: '', label: 'Todos' },
  { value: 'aberto', label: 'Aberto' },
  { value: 'fechado', label: 'Fechado' },
  { value: 'pendente', label: 'Pendente' },
  { value: 'atrasado', label: 'Atrasado' }
] as const;

// Opções de prioridade
export const PRIORITY_OPTIONS = [
  { value: '', label: 'Todas' },
  { value: 'baixa', label: 'Baixa' },
  { value: 'media', label: 'Média' },
  { value: 'alta', label: 'Alta' },
  { value: 'critica', label: 'Crítica' }
] as const;

// Opções de nível
export const LEVEL_OPTIONS = [
  { value: '', label: 'Todos' },
  { value: 'N1', label: 'Nível 1' },
  { value: 'N2', label: 'Nível 2' },
  { value: 'N3', label: 'Nível 3' },
  { value: 'N4', label: 'Nível 4' }
] as const;

// Configurações de exportação
export const EXPORT_OPTIONS: ExportOptions = {
  format: 'pdf',
  includeFilters: true,
  includeTimestamp: true,
  filename: 'dashboard-export'
};

// Configurações de performance
export const PERFORMANCE_CONFIG = {
  SLOW_REQUEST_THRESHOLD: 2000, // 2 segundos
  CACHE_HIT_RATE_THRESHOLD: 0.8, // 80%
  ERROR_RATE_THRESHOLD: 0.05, // 5%
  MEMORY_USAGE_THRESHOLD: 0.9, // 90%
  MONITORING_INTERVAL: 10000 // 10 segundos
} as const;

// Configurações de notificação
export const NOTIFICATION_CONFIG = {
  DEFAULT_DURATION: 5000, // 5 segundos
  MAX_NOTIFICATIONS: 5,
  POSITION: 'top-right',
  TYPES: {
    SUCCESS: 'success',
    ERROR: 'error',
    WARNING: 'warning',
    INFO: 'info'
  }
} as const;

// Configurações de validação
export const VALIDATION_CONFIG = {
  MAX_DATE_RANGE_DAYS: 365, // 1 ano
  MIN_REFRESH_INTERVAL: 5000, // 5 segundos
  MAX_REFRESH_INTERVAL: 300000, // 5 minutos
  MAX_FILTER_LENGTH: 100,
  REQUIRED_FIELDS: ['startDate', 'endDate']
} as const;

// Mensagens de erro padrão
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Erro de conexão com o servidor',
  TIMEOUT_ERROR: 'Tempo limite de requisição excedido',
  VALIDATION_ERROR: 'Dados inválidos fornecidos',
  PERMISSION_ERROR: 'Permissão negada',
  NOT_FOUND_ERROR: 'Recurso não encontrado',
  SERVER_ERROR: 'Erro interno do servidor',
  UNKNOWN_ERROR: 'Erro desconhecido',
  CACHE_ERROR: 'Erro no sistema de cache',
  PARSE_ERROR: 'Erro ao processar dados'
} as const;

// Configurações de debug
export const DEBUG_CONFIG = {
  ENABLED: import.meta.env.DEV,
  LOG_LEVEL: import.meta.env.VITE_LOG_LEVEL || 'info',
  SHOW_PERFORMANCE: import.meta.env.VITE_SHOW_PERFORMANCE === 'true',
  SHOW_API_CALLS: import.meta.env.VITE_SHOW_API_CALLS === 'true',
  SHOW_CACHE_HITS: import.meta.env.VITE_SHOW_CACHE_HITS === 'true'
} as const;

// Configurações de layout
export const LAYOUT_CONFIG = {
  SIDEBAR_WIDTH: 280,
  HEADER_HEIGHT: 64,
  FOOTER_HEIGHT: 48,
  CONTENT_PADDING: 24,
  CARD_BORDER_RADIUS: 8,
  ANIMATION_DURATION: 200
} as const;

// Breakpoints responsivos
export const BREAKPOINTS = {
  xs: 0,
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536
} as const;

// Configurações de gráficos
export const CHART_CONFIG = {
  DEFAULT_HEIGHT: 300,
  DEFAULT_COLORS: [
    '#3B82F6', // blue
    '#10B981', // green
    '#F59E0B', // yellow
    '#EF4444', // red
    '#8B5CF6', // purple
    '#06B6D4', // cyan
    '#F97316', // orange
    '#84CC16'  // lime
  ],
  ANIMATION_DURATION: 750,
  TOOLTIP_ENABLED: true,
  LEGEND_ENABLED: true,
  GRID_ENABLED: true
} as const;

// Configurações de paginação
export const PAGINATION_CONFIG = {
  DEFAULT_PAGE_SIZE: 20,
  PAGE_SIZE_OPTIONS: [10, 20, 50, 100],
  MAX_VISIBLE_PAGES: 5
} as const;

// Configurações de busca
export const SEARCH_CONFIG = {
  MIN_SEARCH_LENGTH: 2,
  DEBOUNCE_DELAY: 300,
  MAX_RESULTS: 50,
  HIGHLIGHT_MATCHES: true
} as const;

export default {
  API_CONFIG,
  CACHE_CONFIG,
  DEFAULT_APP_CONFIG,
  DEFAULT_USER_PREFERENCES,
  THEMES,
  STATUS_OPTIONS,
  PRIORITY_OPTIONS,
  LEVEL_OPTIONS,
  EXPORT_OPTIONS,
  PERFORMANCE_CONFIG,
  NOTIFICATION_CONFIG,
  VALIDATION_CONFIG,
  ERROR_MESSAGES,
  DEBUG_CONFIG,
  LAYOUT_CONFIG,
  BREAKPOINTS,
  CHART_CONFIG,
  PAGINATION_CONFIG,
  SEARCH_CONFIG
};
