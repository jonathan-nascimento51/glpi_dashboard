// ============================================================================
// CONFIGURAÇÕES DO DASHBOARD GLPI
// Arquivo de configuração centralizada para toda a aplicação
// ============================================================================

// ============================================================================
// CONFIGURAÇÕES DA API
// ============================================================================
export const API_CONFIG = {
  BASE_URL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8080/api',
  TIMEOUT: 60000, // 60 segundos
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000, // 1 segundo
  CACHE_DURATION: 5 * 60 * 1000, // 5 minutos
  ENDPOINTS: {
    TICKETS: '/tickets',
    METRICS: '/metrics',
    USERS: '/users',
    TECHNICIANS: '/technicians',
    SYSTEM_STATUS: '/system/status',
    HEALTH_CHECK: '/health',
    SEARCH: '/search',
    NOTIFICATIONS: '/notifications',
  },
} as const;

// ============================================================================
// CONFIGURAÇÕES DO DASHBOARD
// ============================================================================
export const DASHBOARD_CONFIG = {
  REFRESH_INTERVAL: 30000, // 30 segundos
  MAX_CHART_POINTS: 100,
  DEFAULT_PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100,
  CHART_COLORS: {
    PRIMARY: '#3B82F6',
    SUCCESS: '#10B981',
    WARNING: '#F59E0B',
    DANGER: '#EF4444',
    INFO: '#6366F1',
    SECONDARY: '#6B7280',
  },
  PRIORITY_COLORS: {
    1: '#EF4444', // Muito Alta - Vermelho
    2: '#F59E0B', // Alta - Laranja
    3: '#10B981', // Média - Verde
    4: '#6B7280', // Baixa - Cinza
    5: '#3B82F6', // Muito Baixa - Azul
  },
  STATUS_COLORS: {
    'new': '#6366F1',
    'assigned': '#F59E0B',
    'planned': '#8B5CF6',
    'waiting': '#F97316',
    'solved': '#10B981',
    'closed': '#6B7280',
  },
} as const;

// ============================================================================
// CONFIGURAÇÕES DE TEMA
// ============================================================================
export const THEME_CONFIG = {
  DEFAULT_THEME: 'light' as const,
  STORAGE_KEY: 'glpi_dashboard_theme',
  THEMES: ['light', 'dark'] as const,
} as const;

// ============================================================================
// CONFIGURAÇÕES DE LOCALIZAÇÃO
// ============================================================================
export const LOCALE_CONFIG = {
  DEFAULT_LOCALE: 'pt-BR',
  SUPPORTED_LOCALES: ['pt-BR', 'en-US', 'es-ES', 'fr-FR'],
  STORAGE_KEY: 'glpi_dashboard_locale',
  DATE_FORMAT: 'dd/MM/yyyy',
  TIME_FORMAT: 'HH:mm:ss',
  DATETIME_FORMAT: 'dd/MM/yyyy HH:mm:ss',
} as const;

// ============================================================================
// CONFIGURAÇÕES DE CACHE
// ============================================================================
export const CACHE_CONFIG = {
  STORAGE_PREFIX: 'glpi_dashboard_',
  DEFAULT_TTL: 5 * 60 * 1000, // 5 minutos
  MAX_CACHE_SIZE: 50, // Máximo de 50 entradas
  CACHE_KEYS: {
    METRICS: 'metrics',
    TICKETS: 'tickets',
    TECHNICIANS: 'technicians',
    SYSTEM_STATUS: 'system_status',
    USER_PREFERENCES: 'user_preferences',
  },
} as const;

// ============================================================================
// CONFIGURAÇÕES DE NOTIFICAÇÃO
// ============================================================================
export const NOTIFICATION_CONFIG = {
  DEFAULT_DURATION: 5000, // 5 segundos
  MAX_NOTIFICATIONS: 5,
  POSITION: 'top-right' as const,
  TYPES: {
    SUCCESS: 'success',
    ERROR: 'error',
    WARNING: 'warning',
    INFO: 'info',
  } as const,
} as const;

// ============================================================================
// CONFIGURAÇÕES DE VALIDAÇÃO
// ============================================================================
export const VALIDATION_CONFIG = {
  MIN_PASSWORD_LENGTH: 8,
  MAX_DESCRIPTION_LENGTH: 1000,
  MAX_TITLE_LENGTH: 255,
  ALLOWED_FILE_TYPES: ['.pdf', '.doc', '.docx', '.txt', '.jpg', '.jpeg', '.png', '.gif'],
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
} as const;

// ============================================================================
// CONFIGURAÇÕES DE PERFORMANCE
// ============================================================================
export const PERFORMANCE_CONFIG = {
  DEBOUNCE_DELAY: 300, // 300ms
  THROTTLE_DELAY: 1000, // 1 segundo
  VIRTUAL_SCROLL_THRESHOLD: 100,
  LAZY_LOAD_THRESHOLD: 50,
  IMAGE_OPTIMIZATION: {
    QUALITY: 80,
    MAX_WIDTH: 1920,
    MAX_HEIGHT: 1080,
  },
} as const;

// ============================================================================
// CONFIGURAÇÕES DE DESENVOLVIMENTO
// ============================================================================
export const DEV_CONFIG = {
  ENABLE_LOGGING: process.env.NODE_ENV === 'development',
  ENABLE_REDUX_DEVTOOLS: process.env.NODE_ENV === 'development',
  MOCK_API: process.env.REACT_APP_MOCK_API === 'true',
  DEBUG_MODE: process.env.REACT_APP_DEBUG === 'true',
} as const;

// ============================================================================
// CONFIGURAÇÕES GERAIS
// ============================================================================
export const APP_CONFIG = {
  NAME: 'GLPI Dashboard',
  VERSION: process.env.REACT_APP_VERSION || '1.0.0',
  DESCRIPTION: 'Dashboard para monitoramento e análise de tickets GLPI',
  AUTHOR: 'Equipe de Desenvolvimento',
  CONTACT_EMAIL: 'suporte@empresa.com',
  DOCUMENTATION_URL: 'https://docs.empresa.com/glpi-dashboard',
  SUPPORT_URL: 'https://suporte.empresa.com',
} as const;

// ============================================================================
// EXPORTAÇÃO CONSOLIDADA
// ============================================================================
export const CONFIG = {
  API: API_CONFIG,
  DASHBOARD: DASHBOARD_CONFIG,
  THEME: THEME_CONFIG,
  LOCALE: LOCALE_CONFIG,
  CACHE: CACHE_CONFIG,
  NOTIFICATION: NOTIFICATION_CONFIG,
  VALIDATION: VALIDATION_CONFIG,
  PERFORMANCE: PERFORMANCE_CONFIG,
  DEV: DEV_CONFIG,
  APP: APP_CONFIG,
} as const;

export default CONFIG;

// ============================================================================
// TIPOS PARA TYPESCRIPT
// ============================================================================
export type ApiConfig = typeof API_CONFIG;
export type DashboardConfig = typeof DASHBOARD_CONFIG;
export type ThemeConfig = typeof THEME_CONFIG;
export type LocaleConfig = typeof LOCALE_CONFIG;
export type CacheConfig = typeof CACHE_CONFIG;
export type NotificationConfig = typeof NOTIFICATION_CONFIG;
export type ValidationConfig = typeof VALIDATION_CONFIG;
export type PerformanceConfig = typeof PERFORMANCE_CONFIG;
export type DevConfig = typeof DEV_CONFIG;
export type AppConfig = typeof APP_CONFIG;
export type Config = typeof CONFIG;