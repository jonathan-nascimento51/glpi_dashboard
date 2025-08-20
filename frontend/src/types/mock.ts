// Tipos para dados mockados e testes

export interface MockTicket {
  id: number;
  title: string;
  description: string;
  status: 'new' | 'open' | 'assigned' | 'pending' | 'solved' | 'closed';
  priority: 'low' | 'normal' | 'high' | 'urgent';
  category: 'hardware' | 'software' | 'network' | 'access' | 'other';
  assigned_to: MockUser;
  requester: MockUser;
  created_at: string;
  updated_at: string;
  due_date?: string;
  resolution_time?: number;
  satisfaction_rating?: number;
  tags?: string[];
  comments?: MockComment[];
  comments_count?: number;
  attachments_count?: number;
  time_spent?: number;
  estimated_time?: number;
}

export interface MockUser {
  id: number;
  name: string;
  email: string;
  role?: 'admin' | 'technician' | 'user';
  department?: string;
  active?: boolean;
  avatar?: string | null;
  phone?: string;
  created_at?: string;
}

export interface MockComment {
  id: number;
  content: string;
  author: MockUser;
  created_at: string;
  is_private: boolean;
}

export interface MockDashboardMetrics {
  total_tickets: number;
  open_tickets: number;
  closed_tickets: number;
  pending_tickets: number;
  overdue_tickets: number;
  avg_resolution_time: number;
  satisfaction_rate: number;
  tickets_by_priority: {
    low: number;
    normal: number;
    high: number;
    urgent: number;
  };
  tickets_by_status: {
    new: number;
    assigned: number;
    pending: number;
    solved: number;
    closed: number;
  };
  tickets_by_category: {
    hardware: number;
    software: number;
    network: number;
    access: number;
    other: number;
  };
  monthly_trends: MockMonthlyTrend[];
  response_time_metrics: {
    avg_first_response: number;
    avg_resolution: number;
    sla_compliance: number;
  };
  filtered?: boolean;
  start_date?: string;
  end_date?: string;
}

export interface MockMonthlyTrend {
  month: string;
  tickets: number;
  resolved: number;
}

export interface MockPerformanceMetrics {
  '7d': MockPeriodMetrics;
  '30d': MockPeriodMetrics;
  '90d': MockPeriodMetrics;
}

export interface MockPeriodMetrics {
  avg_response_time: number;
  avg_resolution_time: number;
  tickets_created: number;
  tickets_resolved: number;
  sla_compliance: number;
  customer_satisfaction: number;
  technician_workload: Record<string, number>;
}

export interface MockNotification {
  id: number;
  title: string;
  message: string;
  type: 'assignment' | 'warning' | 'success' | 'info';
  read: boolean;
  created_at: string;
  action_url: string;
}

export interface MockSettings {
  general: {
    company_name: string;
    timezone: string;
    language: string;
    date_format: string;
    time_format: string;
  };
  notifications: {
    email_enabled: boolean;
    push_enabled: boolean;
    sms_enabled: boolean;
    notification_types: Record<string, boolean>;
  };
  sla: {
    response_time: Record<string, number>;
    resolution_time: Record<string, number>;
  };
  security: {
    session_timeout: number;
    password_policy: {
      min_length: number;
      require_uppercase: boolean;
      require_lowercase: boolean;
      require_numbers: boolean;
      require_symbols: boolean;
    };
    two_factor_enabled: boolean;
    login_attempts: number;
  };
  integrations: {
    glpi: {
      enabled: boolean;
      url: string;
      sync_interval: number;
    };
    email: {
      enabled: boolean;
      smtp_server: string;
      smtp_port: number;
      use_tls: boolean;
    };
    ldap: {
      enabled: boolean;
      server: string;
      port: number;
      base_dn: string;
    };
  };
}

export interface MockData {
  dashboardMetrics: MockDashboardMetrics;
  tickets: MockTicket[];
  users: MockUser[];
  performanceMetrics: MockPerformanceMetrics;
  notifications: MockNotification[];
  settings: MockSettings;
  chartData?: {
    satisfaction_trend: Array<{ date: string; value: number }>;
  };
  trendsData: {
    tickets: Array<{ date: string; value: number }>;
    resolution_time: Array<{ date: string; value: number }>;
    satisfaction: Array<{ date: string; value: number }>;
  };
}

// Tipos para respostas da API mockada
export interface MockApiResponse<T = any> {
  success: boolean;
  data: T;
  timestamp?: string;
  pagination?: {
    page: number;
    limit: number;
    total: number;
    pages: number;
  };
  format?: string;
  query?: string;
  type?: string;
  total?: number;
}

export interface MockApiError {
  success: false;
  error: string;
  code?: string;
  details?: any;
}

export type MockApiResult<T = any> = MockApiResponse<T> | MockApiError;

// Tipos para parâmetros de requisição
export interface MockRequestParams {
  page?: string;
  limit?: string;
  status?: string;
  priority?: string;
  search?: string;
  start_date?: string;
  end_date?: string;
  type?: string;
  format?: string;
}

// Tipos para MSW handlers
export interface MockRequestInfo {
  url: URL;
  params: Record<string, string>;
  body?: any;
}

export interface MockResponseContext {
  delay: (ms: number) => any;
  status: (code: number) => any;
  json: (data: any) => any;
  text: (data: string) => any;
}

// Tipos para testes
export interface TestMetrics {
  totalTickets: number;
  openTickets: number;
  closedTickets: number;
  averageResolutionTime: number;
  ticketsByStatus: Record<string, number>;
  ticketsByPriority: Record<string, number>;
}

export interface TestTicket {
  id: number;
  title: string;
  description: string;
  status: string;
  priority: string;
  assignee: string;
  createdAt: string;
  updatedAt: string;
}

export interface TestUser {
  id: number;
  name: string;
  email: string;
  role: string;
  active: boolean;
  createdAt: string;
}

export interface TestPagination {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
}

export interface TestApiResponse<T = any> {
  data: T;
  pagination?: TestPagination;
}
