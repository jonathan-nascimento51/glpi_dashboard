import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { requestMonitor, instrumentRequest } from '../requestMonitor';

describe('RequestMonitor', () => {
  beforeEach(() => {
    // Limpar histórico antes de cada teste
    requestMonitor.clear();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('deve rastrear requisições bem-sucedidas', async () => {
    const mockRequest = vi.fn().mockResolvedValue({ data: 'test' });

    const result = await instrumentRequest('/api/test', mockRequest, 'GET', { param: 'value' });

    expect(result).toEqual({ data: 'test' });
    expect(mockRequest).toHaveBeenCalledTimes(1);

    const stats = requestMonitor.getStats();
    expect(stats.totalRequests).toBe(1);
    expect(stats.successfulRequests).toBe(1);
    expect(stats.failedRequests).toBe(0);
  });

  it('deve rastrear requisições com erro', async () => {
    const mockRequest = vi.fn().mockRejectedValue(new Error('Network error'));

    await expect(instrumentRequest('/api/test', mockRequest, 'GET')).rejects.toThrow(
      'Network error'
    );

    const stats = requestMonitor.getStats();
    expect(stats.totalRequests).toBe(1);
    expect(stats.successfulRequests).toBe(0);
    expect(stats.failedRequests).toBe(1);
    expect(stats.errorRate).toBe(1);
  });

  it('deve calcular estatísticas corretamente', async () => {
    const mockRequest1 = vi.fn().mockResolvedValue({ data: 'test1' });
    const mockRequest2 = vi.fn().mockResolvedValue({ data: 'test2' });
    const mockRequest3 = vi.fn().mockRejectedValue(new Error('Error'));

    await instrumentRequest('/api/test1', mockRequest1, 'GET');
    await instrumentRequest('/api/test2', mockRequest2, 'POST');

    try {
      await instrumentRequest('/api/test3', mockRequest3, 'GET');
    } catch {
      // Ignorar erro esperado
    }

    const stats = requestMonitor.getStats();
    expect(stats.totalRequests).toBe(3);
    expect(stats.successfulRequests).toBe(2);
    expect(stats.failedRequests).toBe(1);
    expect(stats.errorRate).toBeCloseTo(0.33, 2);
  });

  it('deve rastrear cache hits', () => {
    const requestId = requestMonitor.startRequest('/api/test', 'GET', {});
    requestMonitor.endRequest(requestId, 100, true); // cache hit

    const stats = requestMonitor.getStats();
    expect(stats.cachedRequests).toBe(1);
    expect(stats.cacheHitRate).toBe(1);
  });

  it('deve obter requisições mais lentas', async () => {
    const fastRequest = vi
      .fn()
      .mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve({ data: 'fast' }), 10))
      );
    const slowRequest = vi
      .fn()
      .mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve({ data: 'slow' }), 100))
      );

    await Promise.all([
      instrumentRequest('/api/fast', fastRequest, 'GET'),
      instrumentRequest('/api/slow', slowRequest, 'GET'),
    ]);

    const slowest = requestMonitor.getSlowestRequests(1);
    expect(slowest).toHaveLength(1);
    expect(slowest[0].endpoint).toBe('/api/slow');
    expect(slowest[0].duration).toBeGreaterThan(50);
  });

  it('deve obter endpoints mais utilizados', async () => {
    const mockRequest = vi.fn().mockResolvedValue({ data: 'test' });

    // Fazer múltiplas requisições para o mesmo endpoint
    await Promise.all([
      instrumentRequest('/api/popular', mockRequest, 'GET'),
      instrumentRequest('/api/popular', mockRequest, 'GET'),
      instrumentRequest('/api/other', mockRequest, 'GET'),
    ]);

    const topEndpoints = requestMonitor.getTopEndpoints(2);
    expect(topEndpoints).toHaveLength(2);
    expect(topEndpoints[0].endpoint).toBe('/api/popular');
    expect(topEndpoints[0].count).toBe(2);
    expect(topEndpoints[1].endpoint).toBe('/api/other');
    expect(topEndpoints[1].count).toBe(1);
  });

  it('deve obter estatísticas detalhadas por período', async () => {
    const mockRequest = vi.fn().mockResolvedValue({ data: 'test' });

    await instrumentRequest('/api/test', mockRequest, 'GET');

    const detailed = requestMonitor.getDetailedStats(60);
    expect(detailed.stats.totalRequests).toBe(1);
    expect(detailed.timeline).toBeDefined();
    expect(detailed.errors).toBeDefined();
  });

  it('deve limpar histórico corretamente', async () => {
    const mockRequest = vi.fn().mockResolvedValue({ data: 'test' });

    await instrumentRequest('/api/test', mockRequest, 'GET');
    expect(requestMonitor.getStats().totalRequests).toBe(1);

    requestMonitor.clear();
    expect(requestMonitor.getStats().totalRequests).toBe(0);
  });
});
