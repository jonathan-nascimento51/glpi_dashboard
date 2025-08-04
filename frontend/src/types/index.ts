export interface MetricsData {
  novos: number;
  pendentes: number;
  progresso: number;
  resolvidos: number;
  total: number;
  niveis: {
    n1: LevelMetrics;
    n2: LevelMetrics;
    n3: LevelMetrics;
    n4: LevelMetrics;
  };
  tendencias: {
    novos: string;
    pendentes: string;
    progresso: string;
    resolvidos: string;
  };
}

export interface LevelMetrics {
  novos: number;
  progresso: number;
  pendentes: number;
  resolvidos: number;
}

export interface SystemStatus {
  status: 'online' | 'offline' | 'maintenance';
  sistema_ativo: boolean;
  ultima_atualizacao: string;
}

export interface SearchResult {
  id: string;
  type: 'ticket' | 'technician' | 'system';
  title: string;
  description?: string;
  status?: TicketStatus;
}

export type TicketStatus = 'new' | 'progress' | 'pending' | 'resolved';

export type Theme = 'light' | 'dark' | 'corporate' | 'tech';

export interface FilterState {
  period: 'today' | 'week' | 'month';
  levels: string[];
  status: TicketStatus[];
  priority: ('high' | 'medium' | 'low')[];
}

export interface NotificationData {
  id: string;
  title: string;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  timestamp: Date;
  duration?: number;
}

export interface ChartDataPoint {
  label: string;
  value: number;
  color?: string;
}

export interface TechnicianRanking {
  id: string;
  name: string;
  level: string;
  score: number;
  total?: number; // Campo adicional para compatibilidade com API
  ticketsResolved: number;
  ticketsInProgress: number;
  averageResolutionTime: number;
}

export interface DashboardState {
  metrics: MetricsData | null;
  systemStatus: SystemStatus | null;
  isLoading: boolean;
  error: string | null;
  lastUpdated: Date | null;
  filters: FilterState;
  searchQuery: string;
  searchResults: SearchResult[];
  notifications: NotificationData[];
  theme: Theme;
  isSimplifiedMode: boolean;
  technicianRanking: TechnicianRanking[];
}