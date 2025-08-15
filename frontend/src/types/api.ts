// Tipos para a API do Dashboard GLPI

// Metricas por nivel
export interface LevelMetrics {
  novos: number;
  pendentes: number;
  progresso: number;
  resolvidos: number;
  total: number;
  abertos?: number;
  fechados?: number;
  atrasados?: number;
  tendencia_novos?: number;
  tendencia_pendentes?: number;
  tendencia_progresso?: number;
  tendencia_resolvidos?: number;
  tendencia_abertos?: number;
  tendencia_fechados?: number;
  tendencia_atrasados?: number;
}

// Metricas de niveis
export interface NiveisMetrics {
  n1: LevelMetrics;
  n2: LevelMetrics;
  n3: LevelMetrics;
  n4: LevelMetrics;
  geral: LevelMetrics;
}

// Tendencias
export interface TendenciasMetrics {
  novos: string;
  pendentes: string;
  progresso: string;
  resolvidos: string;
}

// Metricas do dashboard
export interface DashboardMetrics {
  niveis: NiveisMetrics;
  tendencias?: TendenciasMetrics;
  filtros_aplicados?: any;
  tempo_execucao?: number;
  timestamp?: string;
  systemStatus?: any;
  technicianRanking?: any[];
}

// Status do sistema
export interface SystemStatus {
  status: 'online' | 'offline' | 'maintenance';
  sistema_ativo: boolean;
  ultima_atualizacao: string;
}

// Ranking de tecnicos
export interface TechnicianRanking {
  id: string;
  name: string;
  nome?: string;
  level: string;
  rank: number;
  total: number;
  score?: number;
  ticketsResolved?: number;
  ticketsInProgress?: number;
  averageResolutionTime?: number;
}

// Parametros de filtro
export interface FilterParams {
  period?: 'today' | 'week' | 'month';
  levels?: string[];
  status?: string[];
  priority?: string[];
  dateRange?: {
    startDate: string;
    endDate: string;
    label?: string;
  };
  level?: string;
  technician?: string;
  category?: string;
  startDate?: string;
  endDate?: string;
}

// Resposta da API
export interface ApiResponse<T = any> {
  success: true;
  data: T;
  message?: string;
  timestamp?: string;
  performance?: PerformanceMetrics;
}

// Erro da API
export interface ApiError {
  success: false;
  error: string;
  details?: any;
  timestamp?: string;
  code?: string | number;
}

// Resultado da API (uniao de sucesso e erro)
export type ApiResult<T = any> = ApiResponse<T> | ApiError;

export interface LoadingState {
  isLoading: boolean;
  error: string | null;
  lastUpdated: Date | null;
}

// Configuracao de cache
export interface CacheConfig {
  enabled: boolean;
  ttl: number; // Time to live em milissegundos
  maxSize: number; // Numero maximo de entradas no cache
  strategy: string;
}

// Entrada do cache
export interface CacheEntry<T> {
  data: T;
  timestamp: number;
  key: string;
}

// Metricas de performance
export interface PerformanceMetrics {
  responseTime: number;
  cacheHit: boolean;
  timestamp: Date;
  endpoint: string;
}

// Configuracao da aplicacao
export interface AppConfig {
  theme: string;
  language: string;
  autoRefresh: boolean;
  refreshInterval: number;
  showPerformanceMetrics: boolean;
  enableNotifications: boolean;
  dateFormat: string;
  timeFormat: string;
  timezone: string;
}

// Contexto do usuario
export interface UserContext {
  id?: string;
  name?: string;
  role?: string;
  permissions?: string[];
}

// Notificacao
export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: Date;
  autoClose?: boolean;
  duration?: number;
}

// Tema da aplicacao
export interface Theme {
  name: string;
  displayName: string;
  colors: {
    primary: string;
    secondary: string;
    success: string;
    warning: string;
    error: string;
    info: string;
    background: string;
    surface: string;
    text: string;
  };
  spacing: {
    xs: string;
    sm: string;
    md: string;
    lg: string;
    xl: string;
  };
  borderRadius: {
    sm: string;
    md: string;
    lg: string;
  };
}

// Preferencias do usuario
export interface UserPreferences {
  theme: 'light' | 'dark' | 'auto';
  language: 'pt-BR' | 'en-US';
  dateFormat: string;
  timeFormat: string;
  autoRefresh: boolean;
  refreshInterval: number;
  showPerformanceMetrics: boolean;
  enableNotifications: boolean;
  dashboardLayout: string;
  chartsEnabled: boolean;
  soundEnabled: boolean;
  emailNotifications: boolean;
  notifications: {
    enabled: boolean;
    types: ('success' | 'error' | 'warning' | 'info')[];
  };
  dashboard: {
    defaultView: 'cards' | 'table' | 'chart';
    autoRefresh: boolean;
    showTrends: boolean;
  };
}

// Validacao de formulario
export interface ValidationResult<T = any> {
  isValid: boolean;
  errors: string[];
  data?: T;
}

// Opcoes de exportacao
export interface ExportOptions {
  format: 'csv' | 'xlsx' | 'pdf' | 'json';
  includeFilters: boolean;
  includeTimestamp: boolean;
  filename?: string;
}

// Historico de acoes
export interface ActionHistory {
  id: string;
  action: string;
  timestamp: Date;
  user?: string;
  details?: Record<string, any>;
}

// Type guards para verificacao de tipos em runtime
export const isApiError = (response: ApiResult): response is ApiError => {
  return response.success === false;
};

export const isApiResponse = <T>(response: ApiResult<T>): response is ApiResponse<T> => {
  return response.success === true;
};

export const isValidLevelMetrics = (data: any): data is LevelMetrics => {
  return (
    typeof data === 'object' &&
    typeof data.novos === 'number' &&
    typeof data.pendentes === 'number' &&
    typeof data.progresso === 'number' &&
    typeof data.resolvidos === 'number' &&
    typeof data.total === 'number'
  );
};

export const isValidNiveisMetrics = (data: any): data is NiveisMetrics => {
  return (
    typeof data === 'object' &&
    isValidLevelMetrics(data.n1) &&
    isValidLevelMetrics(data.n2) &&
    isValidLevelMetrics(data.n3) &&
    isValidLevelMetrics(data.n4) &&
    isValidLevelMetrics(data.geral)
  );
};

// Utilitarios de transformacao
export const transformLegacyData = (legacyData: any): DashboardMetrics => {
  // Funcao para transformar dados legados em formato atual
  const defaultLevel: LevelMetrics = {
    novos: 0,
    pendentes: 0,
    progresso: 0,
    resolvidos: 0,
    total: 0
  };

  // Se os dados ja vem na estrutura correta da API
  if (legacyData?.niveis) {
    return {
      niveis: {
        n1: legacyData.niveis.n1 || defaultLevel,
        n2: legacyData.niveis.n2 || defaultLevel,
        n3: legacyData.niveis.n3 || defaultLevel,
        n4: legacyData.niveis.n4 || defaultLevel,
        geral: legacyData.niveis.geral || defaultLevel
      },
      tendencias: legacyData?.tendencias,
      filtros_aplicados: legacyData?.filtros_aplicados,
      tempo_execucao: legacyData?.tempo_execucao,
      timestamp: legacyData?.timestamp,
      systemStatus: legacyData?.systemStatus,
      technicianRanking: legacyData?.technicianRanking
    };
  }

  // Fallback para dados legados
  return {
    niveis: {
      n1: legacyData?.n1 || defaultLevel,
      n2: legacyData?.n2 || defaultLevel,
      n3: legacyData?.n3 || defaultLevel,
      n4: legacyData?.n4 || defaultLevel,
      geral: legacyData?.geral || defaultLevel
    },
    tendencias: legacyData?.tendencias,
    filtros_aplicados: legacyData?.filtros_aplicados,
    tempo_execucao: legacyData?.tempo_execucao,
    timestamp: legacyData?.timestamp,
    systemStatus: legacyData?.systemStatus,
    technicianRanking: legacyData?.technicianRanking
  };
};