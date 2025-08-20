import { describe, it, expect, vi, beforeEach } from 'vitest';
import { requestBatcher, batchMetricsRequest } from '../requestBatcher';

// Mock do fetch global
global.fetch = vi.fn();
const mockFetch = vi.mocked(fetch);

describe('RequestBatcher', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    requestBatcher.clear();
  });

  it('deve agrupar múltiplas requisições de métricas', async () => {
    // Mock das respostas fetch
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ metric: 'value1' }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ metric: 'value2' }),
      } as Response);

    // Fazer múltiplas requisições simultaneamente
    const promises = [
      batchMetricsRequest({ type: 'cpu' }),
      batchMetricsRequest({ type: 'memory' }),
    ];

    const results = await Promise.all(promises);

    // Verificar os resultados
    expect(results[0]).toEqual({ metric: 'value1' });
    expect(results[1]).toEqual({ metric: 'value2' });

    // Verificar que as requisições foram feitas
    expect(mockFetch).toHaveBeenCalledTimes(2);
  });

  it('deve processar requisições quando fetch falha', async () => {
    // Mock do fetch falhando
    mockFetch.mockRejectedValueOnce(new Error('Network error'));

    const result = await batchMetricsRequest({ type: 'cpu' });

    // Deve retornar null quando há erro
    expect(result).toBeNull();
    expect(mockFetch).toHaveBeenCalledTimes(1);
  });

  it('deve obter estatísticas do batcher', () => {
    const stats = requestBatcher.getStats();

    expect(stats).toHaveProperty('totalPendingRequests');
    expect(stats).toHaveProperty('activeBatches');
    expect(stats).toHaveProperty('activeTimers');
    expect(stats).toHaveProperty('config');
    expect(stats.config).toHaveProperty('maxBatchSize');
    expect(stats.config).toHaveProperty('maxWaitTime');
  });

  it('deve limpar batches pendentes', () => {
    requestBatcher.clear();
    const stats = requestBatcher.getStats();

    expect(stats.totalPendingRequests).toBe(0);
    expect(stats.activeBatches).toBe(0);
    expect(stats.activeTimers).toBe(0);
  });
});
