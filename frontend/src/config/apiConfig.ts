// Configuração centralizada da API para evitar problemas recorrentes

/**
 * Configurações de ambiente
 */
export const API_CONFIG = {
  // URLs base
  BASE_URL: import.meta.env.VITE_API_BASE_URL || '/api',
  VERSION: '/v1',
  
  // Timeouts
  DEFAULT_TIMEOUT: 30000,
  HEALTH_CHECK_TIMEOUT: 10000,
  
  // Retry configuration
  MAX_RETRIES: 3,
  RETRY_DELAY: 1000,
  
  // Monitoramento
  HEALTH_CHECK_INTERVAL: 30000, // 30 segundos
  ENABLE_MONITORING: import.meta.env.NODE_ENV === 'development',
} as const;

/**
 * Endpoints da API - SEMPRE usar essas constantes
 * NUNCA hardcode URLs nos componentes!
 */
export const API_ENDPOINTS = {
  // KPIs e Métricas
  KPIS: '/kpis',
  
  // Sistema
  SYSTEM_STATUS: '/system/status',
  HEALTH_CHECK: '/health',
  
  // Tickets
  TICKETS_NEW: '/tickets/new',
  TICKETS_SEARCH: '/tickets/search',
  
  // Técnicos
  TECHNICIANS_RANKING: '/technicians/ranking',
  
  // Cache
  CACHE_CLEAR: '/cache/clear',
} as const;

/**
 * Parâmetros padrão para diferentes tipos de requisição
 */
export const DEFAULT_PARAMS = {
  TICKETS_LIMIT: 6,
  RANKING_LIMIT: 10,
  SEARCH_LIMIT: 20,
} as const;

/**
 * Headers padrão
 */
export const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
} as const;

/**
 * Função para construir URL completa
 */
export function buildApiUrl(endpoint: string, params?: Record<string, any>): string {
  let url = endpoint;
  
  if (params && Object.keys(params).length > 0) {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, String(value));
      }
    });
    url += `?${searchParams.toString()}`;
  }
  
  return url;
}

/**
 * Validação de configuração
 */
export function validateApiConfig(): { valid: boolean; errors: string[] } {
  const errors: string[] = [];
  
  if (!API_CONFIG.BASE_URL) {
    errors.push('BASE_URL não está definida');
  }
  
  if (!API_CONFIG.BASE_URL.includes('/api')) {
    errors.push('BASE_URL deve conter "/api"');
  }
  
  if (API_CONFIG.DEFAULT_TIMEOUT < 5000) {
    errors.push('DEFAULT_TIMEOUT muito baixo (mínimo 5000ms)');
  }
  
  return {
    valid: errors.length === 0,
    errors
  };
}

/**
 * Configuração de desenvolvimento vs produção
 */
export const ENV_CONFIG = {
  isDevelopment: import.meta.env.NODE_ENV === 'development',
  isProduction: import.meta.env.NODE_ENV === 'production',
  enableLogging: import.meta.env.NODE_ENV === 'development',
  enableMonitoring: import.meta.env.NODE_ENV === 'development',
} as const;

/**
 * Tipos para TypeScript
 */
export type ApiEndpoint = typeof API_ENDPOINTS[keyof typeof API_ENDPOINTS];
export type ApiConfig = typeof API_CONFIG;
export type EnvConfig = typeof ENV_CONFIG;

/**
 * Função utilitária para log de debug
 */
export function debugLog(message: string, data?: any): void {
  if (ENV_CONFIG.enableLogging) {
    console.log(`🔧 [API Debug] ${message}`, data || '');
  }
}

/**
 * Função utilitária para log de erro
 */
export function errorLog(message: string, error?: any): void {
  console.error(`❌ [API Error] ${message}`, error || '');
}

/**
 * Função utilitária para log de sucesso
 */
export function successLog(message: string, data?: any): void {
  if (ENV_CONFIG.enableLogging) {
    console.log(`✅ [API Success] ${message}`, data || '');
  }
}
