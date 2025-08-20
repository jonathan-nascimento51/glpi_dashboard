import { describe, it, expect, beforeAll, afterAll, vi } from 'vitest';
import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';
import { httpClient } from '../../services/httpClient';
import type {
  ApiContract,
  SchemaDefinition,
  ValidationResult,
  SchemaValidator,
} from '../../types/contract';

// Schemas de validação usando uma implementação simples
const createSchema = (schema: SchemaDefinition): SchemaValidator => ({
  validate: (data: any): ValidationResult => {
    try {
      validateObject(data, schema);
      return { success: true, data };
    } catch (error) {
      return { success: false, error: (error as Error).message };
    }
  },
});

const validateObject = (data: any, schema: SchemaDefinition): void => {
  if (schema.type === 'object') {
    if (typeof data !== 'object' || data === null) {
      throw new Error(`Expected object, got ${typeof data}`);
    }

    if (schema.required) {
      for (const field of schema.required) {
        if (!(field in data)) {
          throw new Error(`Missing required field: ${field}`);
        }
      }
    }

    if (schema.properties) {
      for (const [key, value] of Object.entries(schema.properties)) {
        if (key in data) {
          validateObject(data[key], value);
        }
      }
    }
  } else if (schema.type === 'array') {
    if (!Array.isArray(data)) {
      throw new Error(`Expected array, got ${typeof data}`);
    }

    if (schema.items) {
      for (const item of data) {
        validateObject(item, schema.items);
      }
    }
  } else if (schema.type === 'string') {
    if (typeof data !== 'string') {
      throw new Error(`Expected string, got ${typeof data}`);
    }

    if (schema.format === 'date-time' && !isValidDateTime(data)) {
      throw new Error(`Invalid date-time format: ${data}`);
    }

    if (schema.format === 'email' && !isValidEmail(data)) {
      throw new Error(`Invalid email format: ${data}`);
    }
  } else if (schema.type === 'number') {
    if (typeof data !== 'number') {
      throw new Error(`Expected number, got ${typeof data}`);
    }

    if (schema.minimum !== undefined && data < schema.minimum) {
      throw new Error(`Number ${data} is below minimum ${schema.minimum}`);
    }

    if (schema.maximum !== undefined && data > schema.maximum) {
      throw new Error(`Number ${data} is above maximum ${schema.maximum}`);
    }
  } else if (schema.type === 'boolean') {
    if (typeof data !== 'boolean') {
      throw new Error(`Expected boolean, got ${typeof data}`);
    }
  } else if (schema.type === 'integer') {
    if (!Number.isInteger(data)) {
      throw new Error(`Expected integer, got ${data}`);
    }
  }
};

const isValidDateTime = (dateString: string): boolean => {
  const date = new Date(dateString);
  return !isNaN(date.getTime()) && dateString.includes('T');
};

const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

// Definição dos contratos da API
const apiContracts: ApiContract[] = [
  // Dashboard Metrics
  {
    endpoint: '/api/dashboard/metrics',
    method: 'GET',
    statusCode: 200,
    responseSchema: {
      type: 'object',
      required: ['totalTickets', 'openTickets', 'closedTickets', 'averageResolutionTime'],
      properties: {
        totalTickets: { type: 'integer', minimum: 0 },
        openTickets: { type: 'integer', minimum: 0 },
        closedTickets: { type: 'integer', minimum: 0 },
        averageResolutionTime: { type: 'number', minimum: 0 },
        ticketsByStatus: {
          type: 'object',
          properties: {
            open: { type: 'integer', minimum: 0 },
            inProgress: { type: 'integer', minimum: 0 },
            closed: { type: 'integer', minimum: 0 },
          },
        },
        ticketsByPriority: {
          type: 'object',
          properties: {
            high: { type: 'integer', minimum: 0 },
            medium: { type: 'integer', minimum: 0 },
            low: { type: 'integer', minimum: 0 },
          },
        },
      },
    },
  },

  // Tickets List
  {
    endpoint: '/api/tickets',
    method: 'GET',
    statusCode: 200,
    responseSchema: {
      type: 'object',
      required: ['data', 'pagination'],
      properties: {
        data: {
          type: 'array',
          items: {
            type: 'object',
            required: ['id', 'title', 'status', 'priority', 'createdAt'],
            properties: {
              id: { type: 'integer', minimum: 1 },
              title: { type: 'string' },
              description: { type: 'string' },
              status: { type: 'string', enum: ['open', 'in_progress', 'closed'] },
              priority: { type: 'string', enum: ['low', 'medium', 'high'] },
              assigneeId: { type: 'integer', minimum: 1 },
              createdAt: { type: 'string', format: 'date-time' },
              updatedAt: { type: 'string', format: 'date-time' },
            },
          },
        },
        pagination: {
          type: 'object',
          required: ['page', 'limit', 'total', 'totalPages'],
          properties: {
            page: { type: 'integer', minimum: 1 },
            limit: { type: 'integer', minimum: 1 },
            total: { type: 'integer', minimum: 0 },
            totalPages: { type: 'integer', minimum: 0 },
          },
        },
      },
    },
  },

  // Create Ticket
  {
    endpoint: '/api/tickets',
    method: 'POST',
    statusCode: 201,
    requestSchema: {
      type: 'object',
      required: ['title', 'description', 'priority'],
      properties: {
        title: { type: 'string', minLength: 1, maxLength: 255 },
        description: { type: 'string', minLength: 1 },
        priority: { type: 'string', enum: ['low', 'medium', 'high'] },
        assigneeId: { type: 'integer', minimum: 1 },
        categoryId: { type: 'integer', minimum: 1 },
      },
    },
    responseSchema: {
      type: 'object',
      required: ['id', 'title', 'status', 'priority', 'createdAt'],
      properties: {
        id: { type: 'integer', minimum: 1 },
        title: { type: 'string' },
        description: { type: 'string' },
        status: { type: 'string', enum: ['open', 'in_progress', 'closed'] },
        priority: { type: 'string', enum: ['low', 'medium', 'high'] },
        assigneeId: { type: 'integer', minimum: 1 },
        createdAt: { type: 'string', format: 'date-time' },
        updatedAt: { type: 'string', format: 'date-time' },
      },
    },
  },

  // Update Ticket
  {
    endpoint: '/api/tickets/:id',
    method: 'PUT',
    statusCode: 200,
    requestSchema: {
      type: 'object',
      properties: {
        title: { type: 'string', minLength: 1, maxLength: 255 },
        description: { type: 'string' },
        status: { type: 'string', enum: ['open', 'in_progress', 'closed'] },
        priority: { type: 'string', enum: ['low', 'medium', 'high'] },
        assigneeId: { type: 'integer', minimum: 1 },
      },
    },
    responseSchema: {
      type: 'object',
      required: ['id', 'title', 'status', 'priority', 'updatedAt'],
      properties: {
        id: { type: 'integer', minimum: 1 },
        title: { type: 'string' },
        description: { type: 'string' },
        status: { type: 'string', enum: ['open', 'in_progress', 'closed'] },
        priority: { type: 'string', enum: ['low', 'medium', 'high'] },
        assigneeId: { type: 'integer', minimum: 1 },
        createdAt: { type: 'string', format: 'date-time' },
        updatedAt: { type: 'string', format: 'date-time' },
      },
    },
  },

  // Delete Ticket
  {
    endpoint: '/api/tickets/:id',
    method: 'DELETE',
    statusCode: 204,
    responseSchema: null,
  },

  // Users List
  {
    endpoint: '/api/users',
    method: 'GET',
    statusCode: 200,
    responseSchema: {
      type: 'array',
      items: {
        type: 'object',
        required: ['id', 'name', 'email', 'role'],
        properties: {
          id: { type: 'integer', minimum: 1 },
          name: { type: 'string' },
          email: { type: 'string', format: 'email' },
          role: { type: 'string', enum: ['admin', 'technician', 'user'] },
          isActive: { type: 'boolean' },
          createdAt: { type: 'string', format: 'date-time' },
        },
      },
    },
  },

  // Performance Metrics
  {
    endpoint: '/api/performance/metrics',
    method: 'GET',
    statusCode: 200,
    responseSchema: {
      type: 'object',
      required: ['responseTime', 'throughput', 'errorRate'],
      properties: {
        responseTime: {
          type: 'object',
          required: ['average', 'p95', 'p99'],
          properties: {
            average: { type: 'number', minimum: 0 },
            p95: { type: 'number', minimum: 0 },
            p99: { type: 'number', minimum: 0 },
          },
        },
        throughput: { type: 'number', minimum: 0 },
        errorRate: { type: 'number', minimum: 0, maximum: 100 },
        uptime: { type: 'number', minimum: 0, maximum: 100 },
      },
    },
  },

  // Health Check
  {
    endpoint: '/api/health',
    method: 'GET',
    statusCode: 200,
    responseSchema: {
      type: 'object',
      required: ['status', 'timestamp'],
      properties: {
        status: { type: 'string', enum: ['healthy', 'unhealthy', 'degraded'] },
        timestamp: { type: 'string', format: 'date-time' },
        services: {
          type: 'object',
          properties: {
            database: { type: 'string', enum: ['up', 'down'] },
            glpi: { type: 'string', enum: ['up', 'down'] },
            cache: { type: 'string', enum: ['up', 'down'] },
          },
        },
        version: { type: 'string' },
      },
    },
  },

  // Error Responses
  {
    endpoint: '/api/tickets/999999',
    method: 'GET',
    statusCode: 404,
    responseSchema: {
      type: 'object',
      required: ['error', 'message'],
      properties: {
        error: { type: 'string' },
        message: { type: 'string' },
        code: { type: 'string' },
        timestamp: { type: 'string', format: 'date-time' },
      },
    },
  },
];

// Mock server para testes de contrato
const contractHandlers = [
  // Dashboard Metrics
  http.get('/api/dashboard/metrics', () => {
    return HttpResponse.json({
      totalTickets: 1234,
      openTickets: 456,
      closedTickets: 778,
      averageResolutionTime: 2.5,
      ticketsByStatus: {
        open: 456,
        inProgress: 123,
        closed: 655,
      },
      ticketsByPriority: {
        high: 89,
        medium: 567,
        low: 578,
      },
    });
  }),

  // Tickets List
  http.get('/api/tickets', () => {
    return HttpResponse.json({
      data: [
        {
          id: 1,
          title: 'Problema no sistema',
          description: 'Descrição do problema',
          status: 'open',
          priority: 'high',
          assigneeId: 1,
          createdAt: '2024-01-15T10:30:00Z',
          updatedAt: '2024-01-15T10:30:00Z',
        },
        {
          id: 2,
          title: 'Manutenção programada',
          description: 'Descrição da manutenção',
          status: 'in_progress',
          priority: 'medium',
          assigneeId: 2,
          createdAt: '2024-01-14T09:15:00Z',
          updatedAt: '2024-01-15T08:45:00Z',
        },
      ],
      pagination: {
        page: 1,
        limit: 10,
        total: 50,
        totalPages: 5,
      },
    });
  }),

  // Create Ticket
  http.post('/api/tickets', async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json(
      {
        id: 3,
        title: 'Novo ticket',
        description: 'Descrição do novo ticket',
        status: 'open',
        priority: 'medium',
        assigneeId: 1,
        createdAt: '2024-01-15T11:00:00Z',
        updatedAt: '2024-01-15T11:00:00Z',
      },
      { status: 201 }
    );
  }),

  // Update Ticket
  http.put('/api/tickets/:id', async ({ params, request }) => {
    const body = await request.json();
    return HttpResponse.json({
      id: 1,
      title: 'Ticket atualizado',
      description: 'Descrição atualizada',
      status: 'in_progress',
      priority: 'high',
      assigneeId: 2,
      createdAt: '2024-01-15T10:30:00Z',
      updatedAt: '2024-01-15T11:15:00Z',
    });
  }),

  // Delete Ticket
  http.delete('/api/tickets/:id', ({ params }) => {
    return new HttpResponse(null, { status: 204 });
  }),

  // Users List
  http.get('/api/users', () => {
    return HttpResponse.json([
      {
        id: 1,
        name: 'João Silva',
        email: 'joao@example.com',
        role: 'admin',
        isActive: true,
        createdAt: '2024-01-01T00:00:00Z',
      },
      {
        id: 2,
        name: 'Maria Santos',
        email: 'maria@example.com',
        role: 'technician',
        isActive: true,
        createdAt: '2024-01-02T00:00:00Z',
      },
    ]);
  }),

  // Performance Metrics
  http.get('/api/performance/metrics', () => {
    return HttpResponse.json({
      responseTime: {
        average: 150.5,
        p95: 300.2,
        p99: 500.8,
      },
      throughput: 1250.5,
      errorRate: 0.5,
      uptime: 99.9,
    });
  }),

  // Health Check
  http.get('/api/health', () => {
    return HttpResponse.json({
      status: 'healthy',
      timestamp: '2024-01-15T12:00:00Z',
      services: {
        database: 'up',
        glpi: 'up',
        cache: 'up',
      },
      version: '1.0.0',
    });
  }),

  // Error Response
  http.get('/api/tickets/999999', () => {
    return HttpResponse.json(
      {
        error: 'Not Found',
        message: 'Ticket not found',
        code: 'TICKET_NOT_FOUND',
        timestamp: '2024-01-15T12:00:00Z',
      },
      { status: 404 }
    );
  }),

  // Invalid Request
  http.post('/api/tickets/invalid', async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json({
      error: 'Bad Request',
      message: 'Invalid request data',
      code: 'VALIDATION_ERROR',
      timestamp: '2024-01-15T12:00:00Z',
      details: [
        {
          field: 'title',
          message: 'Title is required',
        },
        {
          field: 'priority',
          message: 'Priority must be one of: low, medium, high',
        },
      ],
    });
  }),

  // Unauthorized
  http.get('/api/admin/settings', () => {
    return HttpResponse.json(
      {
        error: 'Unauthorized',
        message: 'Authentication required',
        code: 'AUTH_REQUIRED',
        timestamp: '2024-01-15T12:00:00Z',
      },
      { status: 401 }
    );
  }),

  // Forbidden
  http.delete('/api/admin/users/:id', ({ params }) => {
    return HttpResponse.json(
      {
        error: 'Forbidden',
        message: 'Insufficient permissions',
        code: 'INSUFFICIENT_PERMISSIONS',
        timestamp: '2024-01-15T12:00:00Z',
      },
      { status: 403 }
    );
  }),

  // Server Error
  http.get('/api/reports/generate', () => {
    return HttpResponse.json(
      {
        error: 'Internal Server Error',
        message: 'An unexpected error occurred',
        code: 'INTERNAL_ERROR',
        timestamp: '2024-01-15T12:00:00Z',
      },
      { status: 500 }
    );
  }),
];

const server = setupServer(...contractHandlers);

describe('Testes de Contrato da API', () => {
  beforeAll(() => {
    server.listen({ onUnhandledRequest: 'warn' });
  });

  afterAll(() => {
    server.close();
  });

  describe('Validação de Contratos de Resposta', () => {
    apiContracts.forEach(contract => {
      it(`deve validar o contrato para ${contract.method} ${contract.endpoint}`, async () => {
        const url = contract.endpoint.replace(':id', '1');

        let response;
        switch (contract.method) {
          case 'GET':
            response = await httpClient.get(url);
            break;
          case 'POST': {
            const postData = contract.requestSchema
              ? generateValidData(contract.requestSchema)
              : {};
            response = await httpClient.post(url, postData);
            break;
          }
          case 'PUT': {
            const putData = contract.requestSchema ? generateValidData(contract.requestSchema) : {};
            response = await httpClient.put(url, putData);
            break;
          }
          case 'DELETE':
            response = await httpClient.delete(url);
            break;
          default:
            throw new Error(`Unsupported method: ${contract.method}`);
        }

        // Verificar status code
        expect(response.status).toBe(contract.statusCode);

        // Verificar headers se especificados
        if (contract.headers) {
          Object.entries(contract.headers).forEach(([key, value]) => {
            expect(response.headers[key.toLowerCase()]).toBe(value);
          });
        }

        // Validar schema da resposta
        if (contract.responseSchema) {
          const schema = createSchema(contract.responseSchema);
          const validation = schema.validate(response.data);

          if (!validation.success) {
            throw new Error(`Response schema validation failed: ${validation.error}`);
          }
        }
      });
    });
  });

  describe('Validação de Contratos de Requisição', () => {
    it('deve validar dados de criação de ticket', async () => {
      const validData = {
        title: 'Novo ticket de teste',
        description: 'Descrição detalhada do problema',
        priority: 'high',
        assigneeId: 1,
        categoryId: 2,
      };

      const response = await httpClient.post('/api/tickets', validData);
      expect(response.status).toBe(201);
      expect(response.data.title).toBe(validData.title);
      expect(response.data.priority).toBe(validData.priority);
    });

    it('deve validar dados de atualização de ticket', async () => {
      const updateData = {
        title: 'Ticket atualizado',
        status: 'in_progress',
        priority: 'medium',
      };

      const response = await httpClient.put('/api/tickets/1', updateData);
      expect(response.status).toBe(200);
      expect(response.data.title).toBe(updateData.title);
      expect(response.data.status).toBe(updateData.status);
    });
  });

  describe('Validação de Códigos de Erro', () => {
    it('deve retornar 404 para recurso não encontrado', async () => {
      try {
        await httpClient.get('/api/tickets/999999');
        expect.fail('Should have thrown an error');
      } catch (error: any) {
        expect(error.response.status).toBe(404);
        expect(error.response.data.error).toBe('Not Found');
        expect(error.response.data.code).toBe('TICKET_NOT_FOUND');
      }
    });

    it('deve retornar 400 para dados inválidos', async () => {
      try {
        await httpClient.post('/api/tickets/invalid', {});
        expect.fail('Should have thrown an error');
      } catch (error: any) {
        expect(error.response.status).toBe(400);
        expect(error.response.data.error).toBe('Bad Request');
        expect(error.response.data.code).toBe('VALIDATION_ERROR');
        expect(Array.isArray(error.response.data.details)).toBe(true);
      }
    });

    it('deve retornar 401 para acesso não autorizado', async () => {
      try {
        await httpClient.get('/api/admin/settings');
        expect.fail('Should have thrown an error');
      } catch (error: any) {
        expect(error.response.status).toBe(401);
        expect(error.response.data.error).toBe('Unauthorized');
        expect(error.response.data.code).toBe('AUTH_REQUIRED');
      }
    });

    it('deve retornar 403 para acesso proibido', async () => {
      try {
        await httpClient.delete('/api/admin/users/1');
        expect.fail('Should have thrown an error');
      } catch (error: any) {
        expect(error.response.status).toBe(403);
        expect(error.response.data.error).toBe('Forbidden');
        expect(error.response.data.code).toBe('INSUFFICIENT_PERMISSIONS');
      }
    });

    it('deve retornar 500 para erro interno do servidor', async () => {
      try {
        await httpClient.get('/api/reports/generate');
        expect.fail('Should have thrown an error');
      } catch (error: any) {
        expect(error.response.status).toBe(500);
        expect(error.response.data.error).toBe('Internal Server Error');
        expect(error.response.data.code).toBe('INTERNAL_ERROR');
      }
    });
  });

  describe('Validação de Tipos de Dados', () => {
    it('deve validar tipos de dados em métricas do dashboard', async () => {
      const response = await httpClient.get('/api/dashboard/metrics');
      const data = response.data;

      expect(typeof data.totalTickets).toBe('number');
      expect(typeof data.openTickets).toBe('number');
      expect(typeof data.closedTickets).toBe('number');
      expect(typeof data.averageResolutionTime).toBe('number');

      expect(data.totalTickets).toBeGreaterThanOrEqual(0);
      expect(data.openTickets).toBeGreaterThanOrEqual(0);
      expect(data.closedTickets).toBeGreaterThanOrEqual(0);
      expect(data.averageResolutionTime).toBeGreaterThanOrEqual(0);
    });

    it('deve validar formato de datas', async () => {
      const response = await httpClient.get('/api/tickets');
      const tickets = response.data.data;

      tickets.forEach((ticket: any) => {
        expect(isValidDateTime(ticket.createdAt)).toBe(true);
        expect(isValidDateTime(ticket.updatedAt)).toBe(true);

        const createdDate = new Date(ticket.createdAt);
        const updatedDate = new Date(ticket.updatedAt);

        expect(createdDate.getTime()).toBeLessThanOrEqual(updatedDate.getTime());
      });
    });

    it('deve validar formato de emails', async () => {
      const response = await httpClient.get('/api/users');
      const users = response.data;

      users.forEach((user: any) => {
        expect(isValidEmail(user.email)).toBe(true);
      });
    });
  });

  describe('Validação de Enums', () => {
    it('deve validar valores de status de ticket', async () => {
      const response = await httpClient.get('/api/tickets');
      const tickets = response.data.data;

      const validStatuses = ['open', 'in_progress', 'closed'];

      tickets.forEach((ticket: any) => {
        expect(validStatuses).toContain(ticket.status);
      });
    });

    it('deve validar valores de prioridade de ticket', async () => {
      const response = await httpClient.get('/api/tickets');
      const tickets = response.data.data;

      const validPriorities = ['low', 'medium', 'high'];

      tickets.forEach((ticket: any) => {
        expect(validPriorities).toContain(ticket.priority);
      });
    });

    it('deve validar valores de role de usuário', async () => {
      const response = await httpClient.get('/api/users');
      const users = response.data;

      const validRoles = ['admin', 'technician', 'user'];

      users.forEach((user: any) => {
        expect(validRoles).toContain(user.role);
      });
    });
  });

  describe('Validação de Paginação', () => {
    it('deve validar estrutura de paginação', async () => {
      const response = await httpClient.get('/api/tickets');
      const { pagination } = response.data;

      expect(typeof pagination.page).toBe('number');
      expect(typeof pagination.limit).toBe('number');
      expect(typeof pagination.total).toBe('number');
      expect(typeof pagination.totalPages).toBe('number');

      expect(pagination.page).toBeGreaterThanOrEqual(1);
      expect(pagination.limit).toBeGreaterThanOrEqual(1);
      expect(pagination.total).toBeGreaterThanOrEqual(0);
      expect(pagination.totalPages).toBeGreaterThanOrEqual(0);

      // Validar consistência
      const expectedTotalPages = Math.ceil(pagination.total / pagination.limit);
      expect(pagination.totalPages).toBe(expectedTotalPages);
    });
  });

  describe('Validação de Consistência de Dados', () => {
    it('deve validar consistência entre métricas do dashboard', async () => {
      const response = await httpClient.get('/api/dashboard/metrics');
      const data = response.data;

      // Total deve ser igual à soma de abertos e fechados
      const calculatedTotal = data.openTickets + data.closedTickets;
      expect(data.totalTickets).toBeGreaterThanOrEqual(calculatedTotal);

      // Verificar consistência dos tickets por status
      if (data.ticketsByStatus) {
        const statusTotal =
          data.ticketsByStatus.open + data.ticketsByStatus.inProgress + data.ticketsByStatus.closed;
        expect(statusTotal).toBeLessThanOrEqual(data.totalTickets);
      }
    });

    it('deve validar IDs únicos em listas', async () => {
      const response = await httpClient.get('/api/tickets');
      const tickets = response.data.data;

      const ids = tickets.map((ticket: any) => ticket.id);
      const uniqueIds = [...new Set(ids)];

      expect(ids.length).toBe(uniqueIds.length);
    });
  });
});

// Função auxiliar para gerar dados válidos baseados no schema
function generateValidData(schema: any): any {
  if (schema.type === 'object') {
    const data: any = {};

    if (schema.properties) {
      Object.entries(schema.properties).forEach(([key, propSchema]: [string, any]) => {
        if (schema.required && schema.required.includes(key)) {
          data[key] = generateValidData(propSchema);
        }
      });
    }

    return data;
  }

  if (schema.type === 'string') {
    if (schema.enum) {
      return schema.enum[0];
    }
    if (schema.format === 'email') {
      return 'test@example.com';
    }
    if (schema.format === 'date-time') {
      return new Date().toISOString();
    }
    return 'test string';
  }

  if (schema.type === 'number' || schema.type === 'integer') {
    const min = schema.minimum || 0;
    const max = schema.maximum || 100;
    return min + Math.floor(Math.random() * (max - min + 1));
  }

  if (schema.type === 'boolean') {
    return true;
  }

  if (schema.type === 'array') {
    return [];
  }

  return null;
}
