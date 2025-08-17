import { setupServer } from 'msw/node';
import { rest } from 'msw';
import { handlers } from './handlers';

// Configura o servidor MSW para testes Node.js
export const server = setupServer(...handlers);

// Handlers adicionais para cenários específicos de teste
export const testHandlers = {
  // Handler para simular erro de rede
  networkError: rest.get('*', (req, res, ctx) => {
    return res.networkError('Network error');
  }),

  // Handler para simular timeout
  timeout: rest.get('*', (req, res, ctx) => {
    return res(ctx.delay('infinite'));
  }),

  // Handler para simular erro 500
  serverError: rest.get('*', (req, res, ctx) => {
    return res(
      ctx.status(500),
      ctx.json({
        error: 'Internal Server Error',
        message: 'Something went wrong on the server',
      })
    );
  }),

  // Handler para simular erro 404
  notFound: rest.get('*', (req, res, ctx) => {
    return res(
      ctx.status(404),
      ctx.json({
        error: 'Not Found',
        message: 'The requested resource was not found',
      })
    );
  }),

  // Handler para simular erro 401
  unauthorized: rest.get('*', (req, res, ctx) => {
    return res(
      ctx.status(401),
      ctx.json({
        error: 'Unauthorized',
        message: 'Authentication required',
      })
    );
  }),

  // Handler para simular erro 403
  forbidden: rest.get('*', (req, res, ctx) => {
    return res(
      ctx.status(403),
      ctx.json({
        error: 'Forbidden',
        message: 'Access denied',
      })
    );
  }),

  // Handler para simular resposta lenta
  slowResponse: rest.get('*', (req, res, ctx) => {
    return res(ctx.delay(3000), ctx.json({ message: 'Slow response' }));
  }),

  // Handler para simular resposta vazia
  emptyResponse: rest.get('*', (req, res, ctx) => {
    return res(ctx.status(200), ctx.json({}));
  }),

  // Handler para simular resposta com dados inválidos
  invalidData: rest.get('*', (req, res, ctx) => {
    return res(ctx.status(200), ctx.text('Invalid JSON response'));
  }),
};

// Utilitários para testes
export const testUtils = {
  // Usa um handler específico para o próximo request
  useHandler: (handler: any) => {
    server.use(handler);
  },

  // Reseta todos os handlers para o estado inicial
  resetHandlers: () => {
    server.resetHandlers();
  },

  // Adiciona handlers temporários
  addHandlers: (...handlers: any[]) => {
    server.use(...handlers);
  },

  // Simula erro de rede para todas as requisições
  simulateNetworkError: () => {
    server.use(testHandlers.networkError);
  },

  // Simula timeout para todas as requisições
  simulateTimeout: () => {
    server.use(testHandlers.timeout);
  },

  // Simula erro 500 para todas as requisições
  simulateServerError: () => {
    server.use(testHandlers.serverError);
  },

  // Simula erro 404 para todas as requisições
  simulateNotFound: () => {
    server.use(testHandlers.notFound);
  },

  // Simula erro 401 para todas as requisições
  simulateUnauthorized: () => {
    server.use(testHandlers.unauthorized);
  },

  // Simula erro 403 para todas as requisições
  simulateForbidden: () => {
    server.use(testHandlers.forbidden);
  },

  // Simula resposta lenta
  simulateSlowResponse: () => {
    server.use(testHandlers.slowResponse);
  },

  // Simula resposta vazia
  simulateEmptyResponse: () => {
    server.use(testHandlers.emptyResponse);
  },

  // Simula dados inválidos
  simulateInvalidData: () => {
    server.use(testHandlers.invalidData);
  },
};
