/**
 * Tipos específicos do domínio Dashboard
 */

export interface LevelMetrics {
  N1: {
    total: number;
    abertos: number;
    fechados: number;
    pendentes: number;
    tempo_medio_resolucao: number;
  };
  N2: {
    total: number;
    abertos: number;
    fechados: number;
    pendentes: number;
    tempo_medio_resolucao: number;
  };
  N3: {
    total: number;
    abertos: number;
    fechados: number;
    pendentes: number;
    tempo_medio_resolucao: number;
  };
  N4: {
    total: number;
    abertos: number;
    fechados: number;
    pendentes: number;
    tempo_medio_resolucao: number;
  };
}

export interface TechnicianRanking {
  name: string;
  resolved_tickets: number;
  avg_resolution_time: number;
  satisfaction_score: number;
}

export interface TrendData {
  date: string;
  value: number;
  label: string;
}

export interface SystemStatus {
  api: 'online' | 'offline' | 'degraded';
  glpi: 'online' | 'offline' | 'degraded';
  glpi_message: string;
  glpi_response_time: number;
  last_update: string;
  version: string;
  status: 'online' | 'offline' | 'degraded';
  sistema_ativo: boolean;
  ultima_atualizacao: string;
}

export interface DashboardMetrics {
  niveis: LevelMetrics;
  systemStatus: SystemStatus;
  technicianRanking: TechnicianRanking[];
  trends?: TrendData[];
  last_updated?: string;
  system_status?: string;
}

export interface FilterParams {
  data_inicio?: string;
  data_fim?: string;
  nivel?: string;
  status?: string;
  tecnico?: string;
  categoria?: string;
  prioridade?: string;
  dateRange?: {
    start: string;
    end: string;
  };
}

export interface NotificationData {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  timestamp: Date;
  duration?: number;
}

/**
 * Tipos para componentes específicos do dashboard
 */
export interface DashboardCardProps {
  title: string;
  value: number | string;
  subtitle?: string;
  trend?: {
    value: number;
    direction: 'up' | 'down' | 'stable';
    period: string;
  };
  icon?: React.ReactNode;
  variant?: 'default' | 'compact' | 'detailed';
  isLoading?: boolean;
  error?: string;
}

export interface MetricsGridProps {
  metrics: LevelMetrics;
  isLoading?: boolean;
  error?: string;
  onLevelClick?: (level: string) => void;
}

export interface TechnicianRankingProps {
  ranking: TechnicianRanking[];
  isLoading?: boolean;
  error?: string;
  maxItems?: number;
}

export interface SystemStatusProps {
  status: SystemStatus;
  isLoading?: boolean;
  error?: string;
  showDetails?: boolean;
}

export interface TrendsChartProps {
  data: TrendData[];
  isLoading?: boolean;
  error?: string;
  height?: number;
  showLegend?: boolean;
}

/**
 * Tipos para filtros e configurações
 */
export interface DashboardFilters {
  dateRange: {
    start: Date;
    end: Date;
  };
  levels: string[];
  statuses: string[];
  technicians: string[];
  categories: string[];
  priorities: string[];
}

export interface DashboardConfig {
  refreshInterval: number;
  autoRefresh: boolean;
  theme: 'light' | 'dark' | 'auto';
  layout: 'grid' | 'list' | 'compact';
  showTrends: boolean;
  showRanking: boolean;
  maxRankingItems: number;
}

/**
 * Tipos para ações e eventos
 */
export interface DashboardAction {
  type: 'REFRESH' | 'FILTER_CHANGE' | 'THEME_CHANGE' | 'CONFIG_CHANGE';
  payload?: any;
}

export interface DashboardEvent {
  type: 'data_loaded' | 'error_occurred' | 'filter_applied' | 'refresh_triggered';
  timestamp: Date;
  data?: any;
}

/**
 * Tipos para API responses
 */
export interface DashboardApiResponse {
  success: boolean;
  data: DashboardMetrics;
  message?: string;
  timestamp: string;
}

export interface SystemStatusApiResponse {
  success: boolean;
  data: SystemStatus;
  message?: string;
  timestamp: string;
}

export interface TechnicianRankingApiResponse {
  success: boolean;
  data: TechnicianRanking[];
  message?: string;
  timestamp: string;
}