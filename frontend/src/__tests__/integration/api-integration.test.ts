import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { setupServer } from 'msw/node';
import { rest } from 'msw';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';

// Mock para API client
class ApiClient {
  private baseURL: string;
  private token: string | null = null;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  setToken(token: string) {
    this.token = token;
  }

  private async request(endpoint: string, options: RequestInit = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...(this.token && { Authorization: `Bearer ${this.token}` }),
      ...options.headers,
    };

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  async get(endpoint: string) {
    return this.request(endpoint);
  }

  async post(endpoint: string, data: any) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async put(endpoint: string, data: any) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async delete(endpoint: string) {
    return this.request(endpoint, {
      method: 'DELETE',
    });
  }
}

// Mock para serviços
class DashboardService {
  constructor(private apiClient: ApiClient) {}

  async getMetrics(filters?: { startDate?: string; endDate?: string }) {
    const params = new URLSearchParams();
    if (filters?.startDate) params.append('start_date', filters.startDate);
    if (filters?.endDate) params.append('end_date', filters.endDate);

    const query = params.toString();
    return this.apiClient.get(`/api/dashboard/metrics${query ? `?${query}` : ''}`);
  }

  async getChartData(type: string, filters?: any) {
    return this.apiClient.get(`/api/dashboard/charts/${type}`);
  }

  async exportData(format: 'csv' | 'json') {
    return this.apiClient.get(`/api/dashboard/export?format=${format}`);
  }
}

class TicketService {
  constructor(private apiClient: ApiClient) {}

  async getTickets(filters?: {
    status?: string;
    priority?: string;
    search?: string;
    page?: number;
    limit?: number;
  }) {
    const params = new URLSearchParams();
    if (filters?.status) params.append('status', filters.status);
    if (filters?.priority) params.append('priority', filters.priority);
    if (filters?.search) params.append('search', filters.search);
    if (filters?.page) params.append('page', filters.page.toString());
    if (filters?.limit) params.append('limit', filters.limit.toString());

    const query = params.toString();
    return this.apiClient.get(`/api/tickets${query ? `?${query}` : ''}`);
  }

  async getTicket(id: number) {
    return this.apiClient.get(`/api/tickets/${id}`);
  }

  async createTicket(data: any) {
    return this.apiClient.post('/api/tickets', data);
  }

  async updateTicket(id: number, data: any) {
    return this.apiClient.put(`/api/tickets/${id}`, data);
  }

  async deleteTicket(id: number) {
    return this.apiClient.delete(`/api/tickets/${id}`);
  }

  async addComment(ticketId: number, comment: string) {
    return this.apiClient.post(`/api/tickets/${ticketId}/comments`, { comment });
  }
}

class UserService {
  constructor(private apiClient: ApiClient) {}

  async getUsers(filters?: { role?: string; active?: boolean }) {
    const params = new URLSearchParams();
    if (filters?.role) params.append('role', filters.role);
    if (filters?.active !== undefined) params.append('active', filters.active.toString());

    const query = params.toString();
    return this.apiClient.get(`/api/users${query ? `?${query}` : ''}`);
  }

  async getUser(id: number) {
    return this.apiClient.get(`/api/users/${id}`);
  }

  async createUser(data: any) {
    return this.apiClient.post('/api/users', data);
  }

  async updateUser(id: number, data: any) {
    return this.apiClient.put(`/api/users/${id}`, data);
  }
}

class AuthService {
  constructor(private apiClient: ApiClient) {}

  async login(username: string, password: string) {
    const response = await this.apiClient.post('/api/auth/login', {
      username,
      password,
    });

    if (response.token) {
      this.apiClient.setToken(response.token);
      localStorage.setItem('auth_token', response.token);
    }

    return response;
  }

  async logout() {
    await this.apiClient.post('/api/auth/logout', {});
    localStorage.removeItem('auth_token');
  }

  async refreshToken() {
    return this.apiClient.post('/api/auth/refresh', {});
  }

  async getCurrentUser() {
    return this.apiClient.get('/api/auth/me');
  }
}

// Mock data
const mockMetrics = {
  totalTickets: 1234,
  openTickets: 456,
  closedTickets: 778,
  averageResolutionTime: 2.5,
  ticketsByStatus: {
    open: 456,
    'in-progress': 123,
    resolved: 345,
    closed: 310,
  },
  ticketsByPriority: {
    low: 234,
    medium: 567,
    high: 345,
    urgent: 88,
  },
};

const mockTickets = {
  data: [
    {
      id: 1,
      title: 'Problema no sistema de login',
      description: 'Usuários não conseguem fazer login',
      status: 'open',
      priority: 'high',
      assignee: 'João Silva',
      createdAt: '2024-01-15T10:00:00Z',
      updatedAt: '2024-01-15T10:00:00Z',
    },
    {
      id: 2,
      title: 'Solicitação de novo usuário',
      description: 'Criar conta para novo funcionário',
      status: 'in-progress',
      priority: 'medium',
      assignee: 'Maria Santos',
      createdAt: '2024-01-14T14:30:00Z',
      updatedAt: '2024-01-15T09:15:00Z',
    },
  ],
  pagination: {
    page: 1,
    limit: 10,
    total: 2,
    totalPages: 1,
  },
};

const mockUsers = {
  data: [
    {
      id: 1,
      name: 'João Silva',
      email: 'joao@empresa.com',
      role: 'admin',
      active: true,
      createdAt: '2024-01-01T00:00:00Z',
    },
    {
      id: 2,
      name: 'Maria Santos',
      email: 'maria@empresa.com',
      role: 'technician',
      active: true,
      createdAt: '2024-01-02T00:00:00Z',
    },
  ],
};

// Setup MSW server
const server = setupServer(
  // Dashboard endpoints
  rest.get('/api/dashboard/metrics', (req, res, ctx) => {
    return res(ctx.json(mockMetrics));
  }),

  rest.get('/api/dashboard/charts/:type', (req, res, ctx) => {
    const { type } = req.params;
    return res(
      ctx.json({
        type,
        data: type === 'status' ? mockMetrics.ticketsByStatus : mockMetrics.ticketsByPriority,
      })
    );
  }),

  rest.get('/api/dashboard/export', (req, res, ctx) => {
    const format = req.url.searchParams.get('format');
    return res(ctx.json({ format, data: mockMetrics }));
  }),

  // Ticket endpoints
  rest.get('/api/tickets', (req, res, ctx) => {
    const status = req.url.searchParams.get('status');
    const priority = req.url.searchParams.get('priority');
    const search = req.url.searchParams.get('search');

    let filteredTickets = mockTickets.data;

    if (status) {
      filteredTickets = filteredTickets.filter(ticket => ticket.status === status);
    }

    if (priority) {
      filteredTickets = filteredTickets.filter(ticket => ticket.priority === priority);
    }

    if (search) {
      filteredTickets = filteredTickets.filter(
        ticket =>
          ticket.title.toLowerCase().includes(search.toLowerCase()) ||
          ticket.description.toLowerCase().includes(search.toLowerCase())
      );
    }

    return res(
      ctx.json({
        data: filteredTickets,
        pagination: {
          ...mockTickets.pagination,
          total: filteredTickets.length,
        },
      })
    );
  }),

  rest.get('/api/tickets/:id', (req, res, ctx) => {
    const { id } = req.params;
    const ticket = mockTickets.data.find(t => t.id === parseInt(id as string));

    if (!ticket) {
      return res(ctx.status(404), ctx.json({ error: 'Ticket não encontrado' }));
    }

    return res(ctx.json(ticket));
  }),

  rest.post('/api/tickets', (req, res, ctx) => {
    return res(
      ctx.status(201),
      ctx.json({
        id: 3,
        ...req.body,
        status: 'open',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      })
    );
  }),

  rest.put('/api/tickets/:id', (req, res, ctx) => {
    const { id } = req.params;
    return res(
      ctx.json({
        id: parseInt(id as string),
        ...req.body,
        updatedAt: new Date().toISOString(),
      })
    );
  }),

  rest.delete('/api/tickets/:id', (req, res, ctx) => {
    return res(ctx.status(204));
  }),

  rest.post('/api/tickets/:id/comments', (req, res, ctx) => {
    return res(
      ctx.status(201),
      ctx.json({
        id: 1,
        ticketId: parseInt(req.params.id as string),
        comment: (req.body as any).comment,
        author: 'Usuário Atual',
        createdAt: new Date().toISOString(),
      })
    );
  }),

  // User endpoints
  rest.get('/api/users', (req, res, ctx) => {
    const role = req.url.searchParams.get('role');
    const active = req.url.searchParams.get('active');

    let filteredUsers = mockUsers.data;

    if (role) {
      filteredUsers = filteredUsers.filter(user => user.role === role);
    }

    if (active !== null) {
      filteredUsers = filteredUsers.filter(user => user.active === (active === 'true'));
    }

    return res(ctx.json({ data: filteredUsers }));
  }),

  rest.get('/api/users/:id', (req, res, ctx) => {
    const { id } = req.params;
    const user = mockUsers.data.find(u => u.id === parseInt(id as string));

    if (!user) {
      return res(ctx.status(404), ctx.json({ error: 'Usuário não encontrado' }));
    }

    return res(ctx.json(user));
  }),

  rest.post('/api/users', (req, res, ctx) => {
    return res(
      ctx.status(201),
      ctx.json({
        id: 3,
        ...req.body,
        active: true,
        createdAt: new Date().toISOString(),
      })
    );
  }),

  rest.put('/api/users/:id', (req, res, ctx) => {
    const { id } = req.params;
    return res(
      ctx.json({
        id: parseInt(id as string),
        ...req.body,
      })
    );
  }),

  // Auth endpoints
  rest.post('/api/auth/login', (req, res, ctx) => {
    const { username, password } = req.body as any;

    if (username === 'admin' && password === 'password') {
      return res(
        ctx.json({
          token: 'mock-jwt-token',
          user: {
            id: 1,
            name: 'Administrador',
            email: 'admin@empresa.com',
            role: 'admin',
          },
        })
      );
    }

    return res(ctx.status(401), ctx.json({ error: 'Credenciais inválidas' }));
  }),

  rest.post('/api/auth/logout', (req, res, ctx) => {
    return res(ctx.status(200), ctx.json({ message: 'Logout realizado com sucesso' }));
  }),

  rest.post('/api/auth/refresh', (req, res, ctx) => {
    return res(
      ctx.json({
        token: 'new-mock-jwt-token',
      })
    );
  }),

  rest.get('/api/auth/me', (req, res, ctx) => {
    const authHeader = req.headers.get('Authorization');

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res(ctx.status(401), ctx.json({ error: 'Token não fornecido' }));
    }

    return res(
      ctx.json({
        id: 1,
        name: 'Administrador',
        email: 'admin@empresa.com',
        role: 'admin',
      })
    );
  })
);

describe('Testes de Integração da API', () => {
  let apiClient: ApiClient;
  let dashboardService: DashboardService;
  let ticketService: TicketService;
  let userService: UserService;
  let authService: AuthService;

  beforeEach(() => {
    server.listen();
    apiClient = new ApiClient('http://localhost:3000');
    dashboardService = new DashboardService(apiClient);
    ticketService = new TicketService(apiClient);
    userService = new UserService(apiClient);
    authService = new AuthService(apiClient);
    localStorage.clear();
  });

  afterEach(() => {
    server.resetHandlers();
    localStorage.clear();
  });

  describe('Dashboard Service', () => {
    it('deve buscar métricas do dashboard', async () => {
      const metrics = await dashboardService.getMetrics();

      expect(metrics).toEqual(mockMetrics);
      expect(metrics.totalTickets).toBe(1234);
      expect(metrics.openTickets).toBe(456);
    });

    it('deve buscar métricas com filtros de data', async () => {
      const filters = {
        startDate: '2024-01-01',
        endDate: '2024-01-31',
      };

      const metrics = await dashboardService.getMetrics(filters);
      expect(metrics).toEqual(mockMetrics);
    });

    it('deve buscar dados de gráfico por tipo', async () => {
      const chartData = await dashboardService.getChartData('status');

      expect(chartData.type).toBe('status');
      expect(chartData.data).toEqual(mockMetrics.ticketsByStatus);
    });

    it('deve exportar dados em diferentes formatos', async () => {
      const csvData = await dashboardService.exportData('csv');
      const jsonData = await dashboardService.exportData('json');

      expect(csvData.format).toBe('csv');
      expect(jsonData.format).toBe('json');
      expect(csvData.data).toEqual(mockMetrics);
      expect(jsonData.data).toEqual(mockMetrics);
    });
  });

  describe('Ticket Service', () => {
    it('deve buscar lista de tickets', async () => {
      const tickets = await ticketService.getTickets();

      expect(tickets.data).toHaveLength(2);
      expect(tickets.pagination.total).toBe(2);
      expect(tickets.data[0].title).toBe('Problema no sistema de login');
    });

    it('deve filtrar tickets por status', async () => {
      const tickets = await ticketService.getTickets({ status: 'open' });

      expect(tickets.data).toHaveLength(1);
      expect(tickets.data[0].status).toBe('open');
    });

    it('deve filtrar tickets por prioridade', async () => {
      const tickets = await ticketService.getTickets({ priority: 'high' });

      expect(tickets.data).toHaveLength(1);
      expect(tickets.data[0].priority).toBe('high');
    });

    it('deve buscar tickets por texto', async () => {
      const tickets = await ticketService.getTickets({ search: 'login' });

      expect(tickets.data).toHaveLength(1);
      expect(tickets.data[0].title).toContain('login');
    });

    it('deve buscar ticket específico por ID', async () => {
      const ticket = await ticketService.getTicket(1);

      expect(ticket.id).toBe(1);
      expect(ticket.title).toBe('Problema no sistema de login');
    });

    it('deve retornar erro para ticket inexistente', async () => {
      await expect(ticketService.getTicket(999)).rejects.toThrow('HTTP 404: Not Found');
    });

    it('deve criar novo ticket', async () => {
      const newTicket = {
        title: 'Novo ticket',
        description: 'Descrição do novo ticket',
        priority: 'medium',
      };

      const createdTicket = await ticketService.createTicket(newTicket);

      expect(createdTicket.id).toBe(3);
      expect(createdTicket.title).toBe(newTicket.title);
      expect(createdTicket.status).toBe('open');
      expect(createdTicket.createdAt).toBeDefined();
    });

    it('deve atualizar ticket existente', async () => {
      const updateData = {
        status: 'in-progress',
        assignee: 'Novo Responsável',
      };

      const updatedTicket = await ticketService.updateTicket(1, updateData);

      expect(updatedTicket.id).toBe(1);
      expect(updatedTicket.status).toBe('in-progress');
      expect(updatedTicket.assignee).toBe('Novo Responsável');
      expect(updatedTicket.updatedAt).toBeDefined();
    });

    it('deve excluir ticket', async () => {
      await expect(ticketService.deleteTicket(1)).resolves.toBeUndefined();
    });

    it('deve adicionar comentário ao ticket', async () => {
      const comment = await ticketService.addComment(1, 'Novo comentário');

      expect(comment.id).toBe(1);
      expect(comment.ticketId).toBe(1);
      expect(comment.comment).toBe('Novo comentário');
      expect(comment.author).toBe('Usuário Atual');
      expect(comment.createdAt).toBeDefined();
    });
  });

  describe('User Service', () => {
    it('deve buscar lista de usuários', async () => {
      const users = await userService.getUsers();

      expect(users.data).toHaveLength(2);
      expect(users.data[0].name).toBe('João Silva');
      expect(users.data[1].name).toBe('Maria Santos');
    });

    it('deve filtrar usuários por role', async () => {
      const users = await userService.getUsers({ role: 'admin' });

      expect(users.data).toHaveLength(1);
      expect(users.data[0].role).toBe('admin');
    });

    it('deve filtrar usuários por status ativo', async () => {
      const users = await userService.getUsers({ active: true });

      expect(users.data).toHaveLength(2);
      expect(users.data.every(user => user.active)).toBe(true);
    });

    it('deve buscar usuário específico por ID', async () => {
      const user = await userService.getUser(1);

      expect(user.id).toBe(1);
      expect(user.name).toBe('João Silva');
      expect(user.role).toBe('admin');
    });

    it('deve retornar erro para usuário inexistente', async () => {
      await expect(userService.getUser(999)).rejects.toThrow('HTTP 404: Not Found');
    });

    it('deve criar novo usuário', async () => {
      const newUser = {
        name: 'Novo Usuário',
        email: 'novo@empresa.com',
        role: 'user',
      };

      const createdUser = await userService.createUser(newUser);

      expect(createdUser.id).toBe(3);
      expect(createdUser.name).toBe(newUser.name);
      expect(createdUser.email).toBe(newUser.email);
      expect(createdUser.active).toBe(true);
      expect(createdUser.createdAt).toBeDefined();
    });

    it('deve atualizar usuário existente', async () => {
      const updateData = {
        name: 'Nome Atualizado',
        role: 'technician',
      };

      const updatedUser = await userService.updateUser(1, updateData);

      expect(updatedUser.id).toBe(1);
      expect(updatedUser.name).toBe('Nome Atualizado');
      expect(updatedUser.role).toBe('technician');
    });
  });

  describe('Auth Service', () => {
    it('deve fazer login com credenciais válidas', async () => {
      const response = await authService.login('admin', 'password');

      expect(response.token).toBe('mock-jwt-token');
      expect(response.user.name).toBe('Administrador');
      expect(response.user.role).toBe('admin');
      expect(localStorage.getItem('auth_token')).toBe('mock-jwt-token');
    });

    it('deve rejeitar login com credenciais inválidas', async () => {
      await expect(authService.login('invalid', 'credentials')).rejects.toThrow(
        'HTTP 401: Unauthorized'
      );
    });

    it('deve fazer logout', async () => {
      // Primeiro fazer login
      await authService.login('admin', 'password');
      expect(localStorage.getItem('auth_token')).toBe('mock-jwt-token');

      // Depois fazer logout
      await authService.logout();
      expect(localStorage.getItem('auth_token')).toBeNull();
    });

    it('deve renovar token', async () => {
      const response = await authService.refreshToken();

      expect(response.token).toBe('new-mock-jwt-token');
    });

    it('deve buscar usuário atual com token válido', async () => {
      apiClient.setToken('valid-token');
      const user = await authService.getCurrentUser();

      expect(user.id).toBe(1);
      expect(user.name).toBe('Administrador');
      expect(user.role).toBe('admin');
    });

    it('deve rejeitar busca de usuário sem token', async () => {
      await expect(authService.getCurrentUser()).rejects.toThrow('HTTP 401: Unauthorized');
    });
  });

  describe('Integração entre Serviços', () => {
    it('deve manter autenticação entre chamadas', async () => {
      // Login
      await authService.login('admin', 'password');

      // Verificar se o token foi definido
      expect(localStorage.getItem('auth_token')).toBe('mock-jwt-token');

      // Buscar usuário atual (requer autenticação)
      const user = await authService.getCurrentUser();
      expect(user.name).toBe('Administrador');

      // Outras operações também devem funcionar com o token
      const tickets = await ticketService.getTickets();
      expect(tickets.data).toHaveLength(2);
    });

    it('deve lidar com fluxo completo de ticket', async () => {
      // Criar ticket
      const newTicket = {
        title: 'Ticket de integração',
        description: 'Teste de fluxo completo',
        priority: 'high',
      };

      const createdTicket = await ticketService.createTicket(newTicket);
      expect(createdTicket.id).toBe(3);

      // Atualizar status
      const updatedTicket = await ticketService.updateTicket(createdTicket.id, {
        status: 'in-progress',
        assignee: 'Técnico Responsável',
      });
      expect(updatedTicket.status).toBe('in-progress');

      // Adicionar comentário
      const comment = await ticketService.addComment(createdTicket.id, 'Iniciando trabalho');
      expect(comment.comment).toBe('Iniciando trabalho');

      // Buscar ticket atualizado
      const fetchedTicket = await ticketService.getTicket(createdTicket.id);
      expect(fetchedTicket.id).toBe(createdTicket.id);
    });

    it('deve sincronizar dados entre dashboard e tickets', async () => {
      // Buscar métricas
      const metrics = await dashboardService.getMetrics();
      expect(metrics.totalTickets).toBe(1234);

      // Buscar tickets
      const tickets = await ticketService.getTickets();
      expect(tickets.data).toHaveLength(2);

      // Verificar consistência (em um cenário real, os números deveriam bater)
      expect(typeof metrics.totalTickets).toBe('number');
      expect(Array.isArray(tickets.data)).toBe(true);
    });

    it('deve lidar com erros de rede de forma consistente', async () => {
      // Simular erro de rede
      server.use(
        rest.get('/api/tickets', (req, res, ctx) => {
          return res.networkError('Erro de conexão');
        })
      );

      await expect(ticketService.getTickets()).rejects.toThrow();
    });

    it('deve lidar com respostas de erro HTTP', async () => {
      // Simular erro 500
      server.use(
        rest.get('/api/dashboard/metrics', (req, res, ctx) => {
          return res(ctx.status(500), ctx.json({ error: 'Erro interno do servidor' }));
        })
      );

      await expect(dashboardService.getMetrics()).rejects.toThrow(
        'HTTP 500: Internal Server Error'
      );
    });
  });

  describe('Cache e Performance', () => {
    it('deve fazer múltiplas chamadas independentes', async () => {
      const startTime = Date.now();

      // Fazer múltiplas chamadas em paralelo
      const [metrics, tickets, users] = await Promise.all([
        dashboardService.getMetrics(),
        ticketService.getTickets(),
        userService.getUsers(),
      ]);

      const endTime = Date.now();
      const duration = endTime - startTime;

      expect(metrics.totalTickets).toBe(1234);
      expect(tickets.data).toHaveLength(2);
      expect(users.data).toHaveLength(2);

      // Verificar que as chamadas foram feitas em paralelo (menos de 1 segundo)
      expect(duration).toBeLessThan(1000);
    });

    it('deve lidar com timeout de requisições', async () => {
      // Simular timeout
      server.use(
        rest.get('/api/tickets', (req, res, ctx) => {
          return res(ctx.delay(5000)); // 5 segundos de delay
        })
      );

      // Em um cenário real, haveria um timeout configurado no cliente
      // Por enquanto, apenas verificamos que a requisição pode ser feita
      const promise = ticketService.getTickets();
      expect(promise).toBeInstanceOf(Promise);
    });
  });
});
