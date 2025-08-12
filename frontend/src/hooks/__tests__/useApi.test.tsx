import { renderHook, act, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { useApi } from '../useApi';
import { apiService } from '../../services/api';

// Mock do apiService
vi.mock('../../services/api', () => ({
  apiService: {
    getMetrics: vi.fn(),
    getSystemStatus: vi.fn(),
    getTechnicianRanking: vi.fn(),
    getNewTickets: vi.fn(),
  },
}));

describe('useApi Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('deve inicializar com estado correto', () => {
    const { result } = renderHook(() => useApi(apiService.getMetrics));

    expect(result.current.data).toBeNull();
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
    expect(typeof result.current.execute).toBe('function');
    expect(typeof result.current.reset).toBe('function');
  });

  it('deve gerenciar estado de loading corretamente', async () => {
    const mockData = { niveis: {}, tendencias: {} };
    const mockGetMetrics = vi.mocked(apiService.getMetrics);
    mockGetMetrics.mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve(mockData), 100))
    );

    const { result } = renderHook(() => useApi(apiService.getMetrics));

    // Estado inicial
    expect(result.current.loading).toBe(false);

    // Executar requisição
    act(() => {
      result.current.execute();
    });

    // Verificar loading ativo
    expect(result.current.loading).toBe(true);
    expect(result.current.error).toBeNull();

    // Aguardar conclusão
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toEqual(mockData);
    expect(result.current.error).toBeNull();
  });

  it('deve gerenciar estado de erro corretamente', async () => {
    const errorMessage = 'API Error';
    const mockGetMetrics = vi.mocked(apiService.getMetrics);
    mockGetMetrics.mockRejectedValue(new Error(errorMessage));

    const { result } = renderHook(() => useApi(apiService.getMetrics));

    // Executar requisição
    act(() => {
      result.current.execute();
    });

    // Aguardar erro
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toBeNull();
    expect(result.current.error).toBe(errorMessage);
  });

  it('deve limpar erro ao executar nova requisição', async () => {
    const mockGetMetrics = vi.mocked(apiService.getMetrics);
    
    // Primeira requisição com erro
    mockGetMetrics.mockRejectedValueOnce(new Error('First error'));
    
    const { result } = renderHook(() => useApi(apiService.getMetrics));

    // Executar primeira requisição
    act(() => {
      result.current.execute();
    });

    await waitFor(() => {
      expect(result.current.error).toBe('First error');
    });

    // Segunda requisição com sucesso
    mockGetMetrics.mockResolvedValueOnce({ niveis: {}, tendencias: {} });
    
    act(() => {
      result.current.execute();
    });

    // Verificar que erro foi limpo
    expect(result.current.error).toBeNull();
    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toEqual({ niveis: {}, tendencias: {} });
    expect(result.current.error).toBeNull();
  });

  it('deve resetar estado corretamente', async () => {
    const mockData = { niveis: {}, tendencias: {} };
    const mockGetMetrics = vi.mocked(apiService.getMetrics);
    mockGetMetrics.mockResolvedValue(mockData);

    const { result } = renderHook(() => useApi(apiService.getMetrics));

    // Executar requisição
    act(() => {
      result.current.execute();
    });

    await waitFor(() => {
      expect(result.current.data).toEqual(mockData);
    });

    // Resetar estado
    act(() => {
      result.current.reset();
    });

    expect(result.current.data).toBeNull();
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('deve aceitar parâmetros na função execute', async () => {
    const mockData = { niveis: {}, tendencias: {} };
    const mockGetMetrics = vi.mocked(apiService.getMetrics);
    mockGetMetrics.mockResolvedValue(mockData);

    const { result } = renderHook(() => useApi(apiService.getMetrics));

    const dateRange = {
      startDate: '2024-01-01',
      endDate: '2024-01-31'
    };

    // Executar com parâmetros
    act(() => {
      result.current.execute(dateRange);
    });

    await waitFor(() => {
      expect(result.current.data).toEqual(mockData);
    });

    expect(mockGetMetrics).toHaveBeenCalledWith(dateRange);
  });

  it('deve cancelar requisição anterior se nova for iniciada', async () => {
    const mockGetMetrics = vi.mocked(apiService.getMetrics);
    
    // Primeira requisição lenta
    mockGetMetrics.mockImplementationOnce(
      () => new Promise(resolve => setTimeout(() => resolve({ data: 'first' }), 200))
    );
    
    // Segunda requisição rápida
    mockGetMetrics.mockImplementationOnce(
      () => new Promise(resolve => setTimeout(() => resolve({ data: 'second' }), 50))
    );

    const { result } = renderHook(() => useApi(apiService.getMetrics));

    // Primeira requisição
    act(() => {
      result.current.execute();
    });

    expect(result.current.loading).toBe(true);

    // Segunda requisição antes da primeira terminar
    act(() => {
      result.current.execute();
    });

    // Aguardar segunda requisição
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    // Deve ter o resultado da segunda requisição
    expect(result.current.data).toEqual({ data: 'second' });
  });

  it('deve executar automaticamente se autoExecute for true', async () => {
    const mockData = { niveis: {}, tendencias: {} };
    const mockGetMetrics = vi.mocked(apiService.getMetrics);
    mockGetMetrics.mockResolvedValue(mockData);

    renderHook(() => useApi(apiService.getMetrics, { autoExecute: true }));

    await waitFor(() => {
      expect(mockGetMetrics).toHaveBeenCalledTimes(1);
    });
  });

  it('deve reexecutar quando dependências mudarem', async () => {
    const mockData = { niveis: {}, tendencias: {} };
    const mockGetMetrics = vi.mocked(apiService.getMetrics);
    mockGetMetrics.mockResolvedValue(mockData);

    let deps = ['dep1'];
    const { rerender } = renderHook(
      ({ dependencies }) => useApi(apiService.getMetrics, { 
        autoExecute: true, 
        dependencies 
      }),
      { initialProps: { dependencies: deps } }
    );

    await waitFor(() => {
      expect(mockGetMetrics).toHaveBeenCalledTimes(1);
    });

    // Mudar dependências
    deps = ['dep2'];
    rerender({ dependencies: deps });

    await waitFor(() => {
      expect(mockGetMetrics).toHaveBeenCalledTimes(2);
    });
  });
});
