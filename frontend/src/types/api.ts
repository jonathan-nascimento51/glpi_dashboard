// Tipos para a API do Dashboard GLPI

// Métricas por nível
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

// Métricas de níveis
export interface NiveisMetrics {
  n1: LevelMetrics;
  n2: LevelMetrics;
  n3: LevelMetrics;
  n4: LevelMetrics;
  geral: LevelMetrics;
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

// Resultado da API (união de sucesso e erro)
export type ApiResult<T = any> = ApiResponse<T> | ApiError;

export interface LoadingState {
  isLoading: boolean;
  error: string | null;
  lastUpdated: Date | null;
}

// Configuração de cache
export interface CacheConfig {
  enabled: boolean;
  ttl: number; // Time to live em milissegundos
  maxSize: number; // Número máximo de entradas no cache
  strategy: string;
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

// Preferências do usuário
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

// Validação de formulário
export interface ValidationResult<T = any> {
  isValid: boolean;
  errors: string[];
  data?: T;
}

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
    isValidLevelMetrics(data.n1) &&
    isValidLevelMetrics(data.n2) &&
    isValidLevelMetrics(data.n3) &&
    isValidLevelMetrics(data.n4) &&
    isValidLevelMetrics(data.geral)
  );
};

// Utilitários de transformação
export const transformLegacyData = (legacyData: any): DashboardMetrics => {
  console.log("🔍 transformLegacyData input:", legacyData);
  
  // Função para transformar dados legados em formato atual
  const defaultLevel: LevelMetrics = {
    novos: 0,
    pendentes: 0,
    progresso: 0,
    resolvidos: 0,
    total: 0
  };

  // Função para calcular total de um nível
  const calculateTotal = (level: any): LevelMetrics => {
    const novos = level?.novos || 0;
    const pendentes = level?.pendentes || 0;
    const progresso = level?.progresso || 0;
    const resolvidos = level?.resolvidos || 0;
    return {
      novos,
      pendentes,
      progresso,
      resolvidos,
      total: novos + pendentes + progresso + resolvidos
    };
  };

  // Se os dados já vêm na estrutura correta da API
  if (legacyData?.niveis) {
    console.log("🔍 transformLegacyData - Dados com estrutura 'niveis' encontrada:", legacyData.niveis);
    
    const processedNiveis = {
      n1: calculateTotal(legacyData.niveis.n1),
      n2: calculateTotal(legacyData.niveis.n2),
      n3: calculateTotal(legacyData.niveis.n3),
      n4: calculateTotal(legacyData.niveis.n4),
      geral: calculateTotal(legacyData.niveis.geral)
    };
    
    // Se não há dados no geral, calcular a partir dos níveis
    if (processedNiveis.geral.total === 0) {
      const geralCalculado = {
        novos: processedNiveis.n1.novos + processedNiveis.n2.novos + processedNiveis.n3.novos + processedNiveis.n4.novos,
        pendentes: processedNiveis.n1.pendentes + processedNiveis.n2.pendentes + processedNiveis.n3.pendentes + processedNiveis.n4.pendentes,
        progresso: processedNiveis.n1.progresso + processedNiveis.n2.progresso + processedNiveis.n3.progresso + processedNiveis.n4.progresso,
        resolvidos: processedNiveis.n1.resolvidos + processedNiveis.n2.resolvidos + processedNiveis.n3.resolvidos + processedNiveis.n4.resolvidos
      };
      processedNiveis.geral = {
        ...geralCalculado,
        total: geralCalculado.novos + geralCalculado.pendentes + geralCalculado.progresso + geralCalculado.resolvidos
      };
    }
    
    console.log("🔍 transformLegacyData - Níveis processados:", processedNiveis);
    
    return {
      niveis: processedNiveis,
      tendencias: legacyData?.tendencias || {
        novos: '0',
        pendentes: '0',
        progresso: '0',
        resolvidos: '0'
      },
      filtros_aplicados: legacyData?.filtros_aplicados,
      tempo_execucao: legacyData?.tempo_execucao,
      timestamp: legacyData?.timestamp,
      systemStatus: legacyData?.systemStatus,
      technicianRanking: legacyData?.technicianRanking
    };
  }

  console.log("🔍 transformLegacyData - Estrutura 'niveis' não encontrada, usando fallback");
  
  // Fallback para dados legados
  return {
    niveis: {
      n1: calculateTotal(legacyData?.n1),
      n2: calculateTotal(legacyData?.n2),
      n3: calculateTotal(legacyData?.n3),
      n4: calculateTotal(legacyData?.n4),
      geral: calculateTotal(legacyData?.geral)
    },
    tendencias: legacyData?.tendencias || {
      novos: '0',
      pendentes: '0',
      progresso: '0',
      resolvidos: '0'
    },
    filtros_aplicados: legacyData?.filtros_aplicados,
    tempo_execucao: legacyData?.tempo_execucao,
    timestamp: legacyData?.timestamp,
    systemStatus: legacyData?.systemStatus,
    technicianRanking: legacyData?.technicianRanking
  };
};



