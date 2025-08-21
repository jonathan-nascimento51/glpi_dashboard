// ============================================================================
// SERVIÇOS DE API DO DASHBOARD GLPI
// Gerenciamento de chamadas para a API do GLPI
// ============================================================================

import { CONFIG } from '../config';
import { utils } from '../utils';

// ============================================================================
// TIPOS E INTERFACES
// ============================================================================

interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
  errors?: string[];
}

interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
  };
}

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  headers?: Record<string, string>;
  body?: any;
  timeout?: number;
  retries?: number;
}

interface Ticket {
  id: string;
  title: string;
  description: string;
  status: 'open' | 'pending' | 'resolved' | 'closed';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  category: string;
  assignee?: string;
  requester: string;
  createdAt: Date;
  updatedAt: Date;
  dueDate?: Date;
}

interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  department?: string;
  avatar?: string;
  isActive: boolean;
  lastLogin?: Date;
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

interface SystemInfo {
  version: string;
  uptime: number;
  memoryUsage: number;
  cpuUsage: number;
  diskUsage: number;
  activeConnections: number;
}

// ============================================================================
// CLASSE BASE PARA API
// ============================================================================

class ApiClient {
  private baseURL: string;
  private defaultHeaders: Record<string, string>;
  private cache: Map<string, { data: any; timestamp: number }> = new Map();

  constructor() {
    this.baseURL = CONFIG.API.BASE_URL;
    this.defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
  }

  /**
   * Define o token de autenticação
   */
  setAuthToken(token: string) {
    this.defaultHeaders['Authorization'] = `Bearer ${token}`;
  }

  /**
   * Remove o token de autenticação
   */
  clearAuthToken() {
    delete this.defaultHeaders['Authorization'];
  }

  /**
   * Gera chave de cache
   */
  private getCacheKey(url: string, options?: RequestOptions): string {
    const method = options?.method || 'GET';
    const body = options?.body ? JSON.stringify(options.body) : '';
    return `${method}:${url}:${body}`;
  }

  /**
   * Verifica se há dados em cache válidos
   */
  private getCachedData(key: string): any | null {
    const cached = this.cache.get(key);
    if (!cached) return null;

    const isExpired = Date.now() - cached.timestamp > CONFIG.API.CACHE_TTL;
    if (isExpired) {
      this.cache.delete(key);
      return null;
    }

    return cached.data;
  }

  /**
   * Armazena dados no cache
   */
  private setCachedData(key: string, data: any): void {
    // Limita o tamanho do cache
    if (this.cache.size >= CONFIG.CACHE.MAX_SIZE) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }

    this.cache.set(key, {
      data,
      timestamp: Date.now(),
    });
  }

  /**
   * Faz uma requisição HTTP
   */
  async request<T>(
    endpoint: string,
    options: RequestOptions = {}
  ): Promise<ApiResponse<T>> {
    const {
      method = 'GET',
      headers = {},
      body,
      timeout = CONFIG.API.TIMEOUT,
      retries = CONFIG.API.MAX_RETRIES,
    } = options;

    const url = `${this.baseURL}${endpoint}`;
    const cacheKey = this.getCacheKey(url, options);

    // Verifica cache para requisições GET
    if (method === 'GET' && CONFIG.API.ENABLE_CACHE) {
      const cachedData = this.getCachedData(cacheKey);
      if (cachedData) {
        return cachedData;
      }
    }

    const requestHeaders = {
      ...this.defaultHeaders,
      ...headers,
    };

    const requestOptions: RequestInit = {
      method,
      headers: requestHeaders,
      body: body ? JSON.stringify(body) : undefined,
    };

    let lastError: Error;

    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        const response = await fetch(url, {
          ...requestOptions,
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result: ApiResponse<T> = await response.json();

        // Armazena no cache se for GET e bem-sucedido
        if (method === 'GET' && CONFIG.API.ENABLE_CACHE && result.success) {
          this.setCachedData(cacheKey, result);
        }

        return result;
      } catch (error) {
        lastError = error as Error;
        
        // Se não é o último retry, aguarda antes de tentar novamente
        if (attempt < retries) {
          await new Promise(resolve => 
            setTimeout(resolve, Math.pow(2, attempt) * 1000)
          );
        }
      }
    }

    throw lastError!;
  }

  /**
   * Limpa o cache
   */
  clearCache(): void {
    this.cache.clear();
  }
}

// ============================================================================
// INSTÂNCIA GLOBAL DA API
// ============================================================================

const apiClient = new ApiClient();

// ============================================================================
// SERVIÇOS DE AUTENTICAÇÃO
// ============================================================================

export const authService = {
  /**
   * Faz login do usuário
   */
  async login(email: string, password: string): Promise<{ user: User; token: string }> {
    const response = await apiClient.request<{ user: User; token: string }>(
      CONFIG.API.ENDPOINTS.AUTH.LOGIN,
      {
        method: 'POST',
        body: { email, password },
      }
    );

    if (response.success && response.data.token) {
      apiClient.setAuthToken(response.data.token);
      utils.setLocalStorage('auth_token', response.data.token);
    }

    return response.data;
  },

  /**
   * Faz logout do usuário
   */
  async logout(): Promise<void> {
    try {
      await apiClient.request(CONFIG.API.ENDPOINTS.AUTH.LOGOUT, {
        method: 'POST',
      });
    } finally {
      apiClient.clearAuthToken();
      utils.removeLocalStorage('auth_token');
      apiClient.clearCache();
    }
  },

  /**
   * Verifica se o token é válido
   */
  async validateToken(): Promise<User> {
    const response = await apiClient.request<User>(
      CONFIG.API.ENDPOINTS.AUTH.VALIDATE
    );
    return response.data;
  },

  /**
   * Solicita reset de senha
   */
  async requestPasswordReset(email: string): Promise<void> {
    await apiClient.request(CONFIG.API.ENDPOINTS.AUTH.RESET_PASSWORD, {
      method: 'POST',
      body: { email },
    });
  },

  /**
   * Redefine a senha
   */
  async resetPassword(token: string, newPassword: string): Promise<void> {
    await apiClient.request(CONFIG.API.ENDPOINTS.AUTH.CONFIRM_RESET, {
      method: 'POST',
      body: { token, password: newPassword },
    });
  },
};

// ============================================================================
// SERVIÇOS DE DASHBOARD
// ============================================================================

export const dashboardService = {
  /**
   * Obtém métricas do dashboard
   */
  async getMetrics(): Promise<DashboardMetrics> {
    const response = await apiClient.request<DashboardMetrics>(
      CONFIG.API.ENDPOINTS.DASHBOARD.METRICS
    );
    return response.data;
  },

  /**
   * Obtém dados para gráficos
   */
  async getChartData(type: string, period: string = '7d'): Promise<any[]> {
    const response = await apiClient.request<any[]>(
      `${CONFIG.API.ENDPOINTS.DASHBOARD.CHARTS}/${type}?period=${period}`
    );
    return response.data;
  },

  /**
   * Obtém atividades recentes
   */
  async getRecentActivity(limit: number = 10): Promise<any[]> {
    const response = await apiClient.request<any[]>(
      `${CONFIG.API.ENDPOINTS.DASHBOARD.ACTIVITY}?limit=${limit}`
    );
    return response.data;
  },
};

// ============================================================================
// SERVIÇOS DE TICKETS
// ============================================================================

export const ticketService = {
  /**
   * Lista tickets com paginação e filtros
   */
  async getTickets(
    page: number = 1,
    pageSize: number = CONFIG.DASHBOARD.DEFAULT_PAGE_SIZE,
    filters: Record<string, any> = {}
  ): Promise<PaginatedResponse<Ticket>> {
    const params = new URLSearchParams({
      page: page.toString(),
      pageSize: pageSize.toString(),
      ...filters,
    });

    const response = await apiClient.request<PaginatedResponse<Ticket>>(
      `${CONFIG.API.ENDPOINTS.TICKETS.LIST}?${params}`
    );
    return response;
  },

  /**
   * Obtém um ticket específico
   */
  async getTicket(id: string): Promise<Ticket> {
    const response = await apiClient.request<Ticket>(
      `${CONFIG.API.ENDPOINTS.TICKETS.DETAIL}/${id}`
    );
    return response.data;
  },

  /**
   * Cria um novo ticket
   */
  async createTicket(ticket: Omit<Ticket, 'id' | 'createdAt' | 'updatedAt'>): Promise<Ticket> {
    const response = await apiClient.request<Ticket>(
      CONFIG.API.ENDPOINTS.TICKETS.CREATE,
      {
        method: 'POST',
        body: ticket,
      }
    );
    return response.data;
  },

  /**
   * Atualiza um ticket
   */
  async updateTicket(id: string, updates: Partial<Ticket>): Promise<Ticket> {
    const response = await apiClient.request<Ticket>(
      `${CONFIG.API.ENDPOINTS.TICKETS.UPDATE}/${id}`,
      {
        method: 'PUT',
        body: updates,
      }
    );
    return response.data;
  },

  /**
   * Exclui um ticket
   */
  async deleteTicket(id: string): Promise<void> {
    await apiClient.request(
      `${CONFIG.API.ENDPOINTS.TICKETS.DELETE}/${id}`,
      { method: 'DELETE' }
    );
  },

  /**
   * Adiciona comentário ao ticket
   */
  async addComment(ticketId: string, comment: string): Promise<void> {
    await apiClient.request(
      `${CONFIG.API.ENDPOINTS.TICKETS.COMMENTS}/${ticketId}`,
      {
        method: 'POST',
        body: { comment },
      }
    );
  },
};

// ============================================================================
// SERVIÇOS DE USUÁRIOS
// ============================================================================

export const userService = {
  /**
   * Lista usuários
   */
  async getUsers(
    page: number = 1,
    pageSize: number = CONFIG.DASHBOARD.DEFAULT_PAGE_SIZE,
    search: string = ''
  ): Promise<PaginatedResponse<User>> {
    const params = new URLSearchParams({
      page: page.toString(),
      pageSize: pageSize.toString(),
      search,
    });

    const response = await apiClient.request<PaginatedResponse<User>>(
      `${CONFIG.API.ENDPOINTS.USERS.LIST}?${params}`
    );
    return response;
  },

  /**
   * Obtém um usuário específico
   */
  async getUser(id: string): Promise<User> {
    const response = await apiClient.request<User>(
      `${CONFIG.API.ENDPOINTS.USERS.DETAIL}/${id}`
    );
    return response.data;
  },

  /**
   * Cria um novo usuário
   */
  async createUser(user: Omit<User, 'id'>): Promise<User> {
    const response = await apiClient.request<User>(
      CONFIG.API.ENDPOINTS.USERS.CREATE,
      {
        method: 'POST',
        body: user,
      }
    );
    return response.data;
  },

  /**
   * Atualiza um usuário
   */
  async updateUser(id: string, updates: Partial<User>): Promise<User> {
    const response = await apiClient.request<User>(
      `${CONFIG.API.ENDPOINTS.USERS.UPDATE}/${id}`,
      {
        method: 'PUT',
        body: updates,
      }
    );
    return response.data;
  },

  /**
   * Exclui um usuário
   */
  async deleteUser(id: string): Promise<void> {
    await apiClient.request(
      `${CONFIG.API.ENDPOINTS.USERS.DELETE}/${id}`,
      { method: 'DELETE' }
    );
  },
};

// ============================================================================
// SERVIÇOS DE SISTEMA
// ============================================================================

export const systemService = {
  /**
   * Obtém informações do sistema
   */
  async getSystemInfo(): Promise<SystemInfo> {
    const response = await apiClient.request<SystemInfo>(
      CONFIG.API.ENDPOINTS.SYSTEM.INFO
    );
    return response.data;
  },

  /**
   * Obtém logs do sistema
   */
  async getLogs(
    level: string = 'all',
    limit: number = 100
  ): Promise<any[]> {
    const params = new URLSearchParams({
      level,
      limit: limit.toString(),
    });

    const response = await apiClient.request<any[]>(
      `${CONFIG.API.ENDPOINTS.SYSTEM.LOGS}?${params}`
    );
    return response.data;
  },

  /**
   * Executa backup do sistema
   */
  async createBackup(): Promise<{ id: string; status: string }> {
    const response = await apiClient.request<{ id: string; status: string }>(
      CONFIG.API.ENDPOINTS.SYSTEM.BACKUP,
      { method: 'POST' }
    );
    return response.data;
  },

  /**
   * Verifica saúde do sistema
   */
  async checkHealth(): Promise<{ status: string; checks: Record<string, boolean> }> {
    const response = await apiClient.request<{ status: string; checks: Record<string, boolean> }>(
      CONFIG.API.ENDPOINTS.SYSTEM.HEALTH
    );
    return response.data;
  },
};

// ============================================================================
// SERVIÇOS DE NOTIFICAÇÕES
// ============================================================================

export const notificationService = {
  /**
   * Obtém notificações do usuário
   */
  async getNotifications(
    page: number = 1,
    pageSize: number = 20
  ): Promise<PaginatedResponse<any>> {
    const params = new URLSearchParams({
      page: page.toString(),
      pageSize: pageSize.toString(),
    });

    const response = await apiClient.request<PaginatedResponse<any>>(
      `${CONFIG.API.ENDPOINTS.NOTIFICATIONS.LIST}?${params}`
    );
    return response;
  },

  /**
   * Marca notificação como lida
   */
  async markAsRead(id: string): Promise<void> {
    await apiClient.request(
      `${CONFIG.API.ENDPOINTS.NOTIFICATIONS.MARK_READ}/${id}`,
      { method: 'PUT' }
    );
  },

  /**
   * Marca todas as notificações como lidas
   */
  async markAllAsRead(): Promise<void> {
    await apiClient.request(
      CONFIG.API.ENDPOINTS.NOTIFICATIONS.MARK_ALL_READ,
      { method: 'PUT' }
    );
  },

  /**
   * Exclui notificação
   */
  async deleteNotification(id: string): Promise<void> {
    await apiClient.request(
      `${CONFIG.API.ENDPOINTS.NOTIFICATIONS.DELETE}/${id}`,
      { method: 'DELETE' }
    );
  },
};

// ============================================================================
// INICIALIZAÇÃO
// ============================================================================

/**
 * Inicializa os serviços com token salvo
 */
export const initializeServices = () => {
  const token = utils.getLocalStorage('auth_token');
  if (token) {
    apiClient.setAuthToken(token);
  }
};

// ============================================================================
// EXPORTAÇÃO CONSOLIDADA
// ============================================================================
export const services = {
  auth: authService,
  dashboard: dashboardService,
  tickets: ticketService,
  users: userService,
  system: systemService,
  notifications: notificationService,
  initialize: initializeServices,
  clearCache: () => apiClient.clearCache(),
};

export default services;

// Tipos exportados
export type {
  ApiResponse,
  PaginatedResponse,
  RequestOptions,
  Ticket,
  User,
  DashboardMetrics,
  SystemInfo,
};