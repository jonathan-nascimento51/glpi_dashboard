// Tipos para a API do Dashboard GLPI

// Métricas por nível
export interface LevelMetrics {
  novos: number;
  progresso: number;
  pendentes: number;
  resolvidos: number;
  total: number;
}

// Níveis de métricas
export interface NiveisMetrics {
  'Manutenção Geral': LevelMetrics;
  'Patrimônio': LevelMetrics;
  'Atendimento': LevelMetrics;
  'Mecanografia': LevelMetrics;
  geral?: LevelMetrics;
}

// Tendências
export interface TendenciasMetrics {
  novos: string;
  pendentes: string;
  progresso: string;
  resolvidos: string;
}

// Métricas do dashboard
export interface DashboardMetrics {
  novos: number;
  pendentes: number;
  progresso: number;
  resolvidos: number;
  total: number;
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

// Ranking de técnicos
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

// Parâmetros de filtro
export interface FilterParams {
  period?: 'today' | 'week' | 'month';
  levels?: string[];
  status?: string[];
  priority?: string[];
  dateRange?: {
    startDate: string;
    endDate: string;
  };
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
  error: {
    message: string;
    code?: string;
  };
  details?: any;
  timestamp: string;
}

// Resultado da API (união de sucesso e erro)
export type ApiResult<T = any> = ApiResponse<T> | ApiError;

export interface LoadingState {
  isLoading: boolean;
  error: string | null;
  lastUpdated: Date | null;
}

// Configuração de cache
export interface CacheConfig {
  ttl: number; // Time to live em milissegundos
  maxSize: number; // Número máximo de entradas no cache
}

// Entrada do cache
export interface CacheEntry<T> {
  data: T;
  timestamp: number;
  key: string;
}

// Métricas de performance
export interface PerformanceMetrics {
  responseTime: number;
  cacheHit: boolean;
  timestamp: Date;
  endpoint: string;
}

// Configuração da aplicação
export interface AppConfig {
  apiBaseUrl: string;
  refreshInterval: number;
  cacheConfig: CacheConfig;
  enablePerformanceMonitoring: boolean;
  enableErrorReporting: boolean;
}

// Contexto do usuário
export interface UserContext {
  id?: string;
  name?: string;
  role?: string;
  permissions?: string[];
}

// Notificação
export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: Date;
  autoClose?: boolean;
  duration?: number;
}

// Tema da aplicação
export interface Theme {
  name: string;
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

// Preferências do usuário
export interface UserPreferences {
  theme: 'light' | 'dark' | 'auto';
  language: 'pt-BR' | 'en-US';
  refreshInterval: number;
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

// Validação de formulário - usando tipo genérico do dataValidation.ts
// export interface ValidationResult - removido para evitar conflito com tipo genérico

// Opções de exportação
export interface ExportOptions {
  format: 'csv' | 'xlsx' | 'pdf' | 'json';
  includeFilters: boolean;
  includeTimestamp: boolean;
  filename?: string;
}

// Histórico de ações
export interface ActionHistory {
  id: string;
  action: string;
  timestamp: Date;
  user?: string;
  details?: Record<string, any>;
}

// Type guards para verificação de tipos em runtime
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
    isValidLevelMetrics(data['Manutenção Geral']) &&
    isValidLevelMetrics(data['Patrimônio']) &&
    isValidLevelMetrics(data['Atendimento']) &&
    isValidLevelMetrics(data['Mecanografia']) &&
    isValidLevelMetrics(data.geral)
  );
};

// Utilitários de transformação
export const transformLegacyData = (legacyData: any): DashboardMetrics => {
  // Função para transformar dados legados em formato atual
  const defaultLevel: LevelMetrics = {
    novos: 0,
    pendentes: 0,
    progresso: 0,
    resolvidos: 0,
    total: 0
  };

  // Se os dados já vêm na estrutura correta da API
  if (legacyData?.niveis) {
    return {
      novos: legacyData.novos || 0,
      pendentes: legacyData.pendentes || 0,
      progresso: legacyData.progresso || 0,
      resolvidos: legacyData.resolvidos || 0,
      total: legacyData.total || 0,
      niveis: {
        'Manutenção Geral': legacyData.niveis['Manutenção Geral'] || defaultLevel,
        'Patrimônio': legacyData.niveis['Patrimônio'] || defaultLevel,
        'Atendimento': legacyData.niveis['Atendimento'] || defaultLevel,
        'Mecanografia': legacyData.niveis['Mecanografia'] || defaultLevel,
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
    novos: legacyData?.novos || 0,
    pendentes: legacyData?.pendentes || 0,
    progresso: legacyData?.progresso || 0,
    resolvidos: legacyData?.resolvidos || 0,
    total: legacyData?.total || 0,
    niveis: {
      'Manutenção Geral': legacyData?.['Manutenção Geral'] || defaultLevel,
      'Patrimônio': legacyData?.['Patrimônio'] || defaultLevel,
      'Atendimento': legacyData?.['Atendimento'] || defaultLevel,
      'Mecanografia': legacyData?.['Mecanografia'] || defaultLevel,
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