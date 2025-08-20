import { describe, it, expect, beforeAll, afterAll, vi } from 'vitest';
import { getTechnicianRanking } from '../../services/api';
import { httpClient } from '../../services/httpClient';

// Mock do httpClient para testes de integração
vi.mock('../../services/httpClient', () => ({
  httpClient: {
    get: vi.fn(),
  },
  API_CONFIG: {
    BASE_URL: 'http://localhost:5000',
  },
  apiUtils: {},
  updateAuthTokens: vi.fn(),
}));

// Mock do sistema de cache
vi.mock('../../services/cache', () => ({
  technicianRankingCache: {
    get: vi.fn(() => null),
    set: vi.fn(),
    clear: vi.fn(),
    recordRequestTime: vi.fn(),
  },
  metricsCache: {
    get: vi.fn(() => null),
    set: vi.fn(),
    clear: vi.fn(),
  },
  systemStatusCache: {
    get: vi.fn(() => null),
    set: vi.fn(),
    clear: vi.fn(),
  },
  newTicketsCache: {
    get: vi.fn(() => null),
    set: vi.fn(),
    clear: vi.fn(),
  },
}));

const mockHttpClient = httpClient as any;

// Helper para configurar mock responses
const mockApiResponse = (data: any, success = true) => {
  mockHttpClient.get.mockResolvedValue({
    data: {
      success,
      data,
    },
  });
};

const mockApiError = () => {
  mockHttpClient.get.mockRejectedValue(new Error('API Error'));
};

describe('Testes de Integração - Endpoint de Ranking', () => {
  beforeAll(() => {
    // Configurar URL base para testes
    process.env.VITE_API_URL = 'http://localhost:5000';
  });

  beforeEach(() => {
    // Limpar mocks entre testes
    vi.clearAllMocks();
  });

  afterAll(() => {
    vi.restoreAllMocks();
  });

  describe('Testes de Range de Tempo', () => {
    it('deve buscar ranking para 7 dias', async () => {
      const mockResponse = [
        {
          id: '1',
          name: 'João Silva',
          level: 'N3',
          total: 45,
          rank: 1,
        },
        {
          id: '2',
          name: 'Maria Santos',
          level: 'N2',
          total: 38,
          rank: 2,
        },
      ];

      mockApiResponse(mockResponse);

      const filters = {
        start_date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        end_date: new Date().toISOString().split('T')[0],
      };

      const result = await getTechnicianRanking(filters);

      expect(result).toEqual(mockResponse);
      expect(mockHttpClient.get).toHaveBeenCalledWith(
        expect.stringContaining('/technicians/ranking')
      );
    });

    it('deve buscar ranking para 14 dias', async () => {
      const mockResponse = [
        {
          id: '1',
          name: 'João Silva',
          level: 'N3',
          total: 89,
          rank: 1,
        },
        {
          id: '2',
          name: 'Maria Santos',
          level: 'N2',
          total: 76,
          rank: 2,
        },
        {
          id: '3',
          name: 'Pedro Costa',
          level: 'N4',
          total: 65,
          rank: 3,
        },
      ];

      mockApiResponse(mockResponse);

      const filters = {
        start_date: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        end_date: new Date().toISOString().split('T')[0],
      };

      const result = await getTechnicianRanking(filters);

      expect(result).toEqual(mockResponse);
      expect(result.length).toBe(3);
      expect(result[0].total).toBeGreaterThan(result[1].total);
    });

    it('deve buscar ranking para 30 dias', async () => {
      const mockResponse = [
        {
          id: '1',
          name: 'João Silva',
          level: 'N3',
          total: 156,
          rank: 1,
        },
        {
          id: '2',
          name: 'Maria Santos',
          level: 'N2',
          total: 142,
          rank: 2,
        },
        {
          id: '3',
          name: 'Pedro Costa',
          level: 'N4',
          total: 128,
          rank: 3,
        },
        {
          id: '4',
          name: 'Ana Oliveira',
          level: 'N1',
          total: 95,
          rank: 4,
        },
      ];

      mockApiResponse(mockResponse);

      const filters = {
        start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        end_date: new Date().toISOString().split('T')[0],
      };

      const result = await getTechnicianRanking(filters);

      expect(result).toEqual(mockResponse);
      expect(result.length).toBe(4);

      // Verificar ordenação por total (decrescente)
      for (let i = 0; i < result.length - 1; i++) {
        expect(result[i].total).toBeGreaterThanOrEqual(result[i + 1].total);
      }
    });
  });

  describe('Testes de Filtros por Nível', () => {
    it('deve filtrar ranking por nível N1', async () => {
      const mockResponse = [
        {
          id: '4',
          name: 'Ana Oliveira',
          level: 'N1',
          total: 95,
          rank: 1,
        },
        {
          id: '5',
          name: 'Carlos Lima',
          level: 'N1',
          total: 78,
          rank: 2,
        },
      ];

      mockApiResponse(mockResponse);

      const filters = {
        level: 'N1',
        start_date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        end_date: new Date().toISOString().split('T')[0],
      };

      const result = await getTechnicianRanking(filters);

      expect(result).toEqual(mockResponse);
      expect(result.every(tech => tech.level === 'N1')).toBe(true);
    });

    it('deve filtrar ranking por nível N4', async () => {
      const mockResponse = [
        {
          id: '3',
          name: 'Pedro Costa',
          level: 'N4',
          total: 128,
          rank: 1,
        },
      ];

      mockApiResponse(mockResponse);

      const filters = {
        level: 'N4',
        start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        end_date: new Date().toISOString().split('T')[0],
      };

      const result = await getTechnicianRanking(filters);

      expect(result).toEqual(mockResponse);
      expect(result.every(tech => tech.level === 'N4')).toBe(true);
    });
  });

  describe('Testes de Validação de Dados', () => {
    it('deve validar estrutura dos dados retornados', async () => {
      const mockResponse = [
        {
          id: '1',
          name: 'João Silva',
          level: 'N3',
          total: 45,
          rank: 1,
        },
      ];

      mockApiResponse(mockResponse);

      const result = await getTechnicianRanking({});

      expect(result).toBeInstanceOf(Array);
      expect(result[0]).toHaveProperty('id');
      expect(result[0]).toHaveProperty('name');
      expect(result[0]).toHaveProperty('level');
      expect(result[0]).toHaveProperty('total');
      expect(result[0]).toHaveProperty('rank');

      expect(typeof result[0].id).toBe('string');
      expect(typeof result[0].name).toBe('string');
      expect(typeof result[0].level).toBe('string');
      expect(typeof result[0].total).toBe('number');
      expect(typeof result[0].rank).toBe('number');
    });

    it('deve validar que totais são números positivos', async () => {
      const mockResponse = [
        {
          id: '1',
          name: 'João Silva',
          level: 'N3',
          total: 45,
          rank: 1,
        },
        {
          id: '2',
          name: 'Maria Santos',
          level: 'N2',
          total: 38,
          rank: 2,
        },
      ];

      mockApiResponse(mockResponse);

      const result = await getTechnicianRanking({});

      result.forEach(technician => {
        expect(technician.total).toBeGreaterThan(0);
        expect(Number.isInteger(technician.total)).toBe(true);
      });
    });

    it('deve validar que nomes não são vazios', async () => {
      const mockResponse = [
        {
          id: '1',
          name: 'João Silva',
          level: 'N3',
          total: 45,
          rank: 1,
        },
      ];

      mockApiResponse(mockResponse);

      const result = await getTechnicianRanking({});

      result.forEach(technician => {
        expect(technician.name).toBeTruthy();
        expect(technician.name.trim().length).toBeGreaterThan(0);
      });
    });
  });

  describe('Testes de Tratamento de Erros', () => {
    it('deve tratar erro do servidor', async () => {
      mockApiError();

      const result = await getTechnicianRanking({});
      expect(result).toEqual([]);
    });

    it('deve tratar resposta sem sucesso', async () => {
      mockApiResponse([], false);

      const result = await getTechnicianRanking({});
      expect(result).toEqual([]);
    });

    it('deve tratar resposta vazia', async () => {
      mockApiResponse([]);

      const result = await getTechnicianRanking({});

      expect(result).toEqual([]);
      expect(Array.isArray(result)).toBe(true);
    });
  });

  describe('Testes de Performance', () => {
    it('deve responder em tempo hábil', async () => {
      const mockResponse = Array.from({ length: 50 }, (_, index) => ({
        id: `tech-${index}`,
        name: `Técnico ${index}`,
        level: ['N1', 'N2', 'N3', 'N4'][index % 4],
        total: 100 - index,
        rank: index + 1,
      }));

      mockApiResponse(mockResponse);

      const startTime = performance.now();
      const result = await getTechnicianRanking({});
      const endTime = performance.now();

      expect(result).toEqual(mockResponse);
      expect(endTime - startTime).toBeLessThan(1000); // Menos de 1 segundo
    });
  });
});
