import { renderHook, act, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { useApi } from '../../../hooks/useApi';
import { httpClient } from '../../../services/httpClient';

// Mock do httpClient
vi.mock('../../../services/httpClient', () => ({
  httpClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

describe('useApi Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('deve inicializar com estado padrão', () => {
    const apiFunction = vi.fn();
    const { result } = renderHook(() => useApi(apiFunction));

    expect(result.current.data).toBeNull();
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
    expect(typeof result.current.execute).toBe('function');
  });

  it('deve executar função da API com sucesso', async () => {
    const mockData = { id: 1, name: 'Test' };
    const apiFunction = vi.fn().mockResolvedValue(mockData);
    
    const { result } = renderHook(() => useApi(apiFunction));

    act(() => {
      result.current.execute();
    });

    // Verifica estado de loading
    expect(result.current.loading).toBe(true);
    expect(result.current.error).toBeNull();

    // Aguarda conclusão
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toEqual(mockData);
    expect(result.current.error).toBeNull();
    expect(apiFunction).toHaveBeenCalledTimes(1);
  });

  it('deve lidar com erros da API', async () => {
    const errorMessage = 'API Error';
    const apiFunction = vi.fn().mockRejectedValue(new Error(errorMessage));
    
    const { result } = renderHook(() => useApi(apiFunction));

    act(() => {
      result.current.execute();
    });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toBeNull();
    expect(result.current.error).toBe(errorMessage);
  });

  it('deve executar automaticamente quando autoExecute é true', async () => {
    const mockData = { test: 'data' };
    const apiFunction = vi.fn().mockResolvedValue(mockData);
    
    const { result } = renderHook(() => 
      useApi(apiFunction, { autoExecute: true })
    );

    // Deve começar em loading
    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toEqual(mockData);
    expect(apiFunction).toHaveBeenCalledTimes(1);
  });

  it('deve passar parâmetros para a função da API', async () => {
    const mockData = { result: 'success' };
    const apiFunction = vi.fn().mockResolvedValue(mockData);
    const params = { id: 123, filter: 'active' };
    
    const { result } = renderHook(() => useApi(apiFunction));

    act(() => {
      result.current.execute(params);
    });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(apiFunction).toHaveBeenCalledWith(params);
  });

  it('deve cancelar requisições pendentes ao desmontar', async () => {
    const apiFunction = vi.fn().mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 1000))
    );
    
    const { result, unmount } = renderHook(() => useApi(apiFunction));

    act(() => {
      result.current.execute();
    });

    expect(result.current.loading).toBe(true);

    // Desmonta o componente
    unmount();

    // Aguarda um pouco para verificar se não há vazamentos
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Não deve haver erros ou warnings sobre state updates
  });

  it('deve limpar erro ao executar nova requisição', async () => {
    const apiFunction = vi.fn()
      .mockRejectedValueOnce(new Error('First error'))
      .mockResolvedValueOnce({ success: true });
    
    const { result } = renderHook(() => useApi(apiFunction));

    // Primeira execução com erro
    act(() => {
      result.current.execute();
    });

    await waitFor(() => {
      expect(result.current.error).toBe('First error');
    });

    // Segunda execução com sucesso
    act(() => {
      result.current.execute();
    });

    // Erro deve ser limpo imediatamente
    expect(result.current.error).toBeNull();
    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toEqual({ success: true });
    expect(result.current.error).toBeNull();
  });

  it('deve lidar com múltiplas execuções concorrentes', async () => {
    let resolveFirst: (value: any) => void;
    let resolveSecond: (value: any) => void;

    const apiFunction = vi.fn()
      .mockImplementationOnce(() => new Promise(resolve => { resolveFirst = resolve; }))
      .mockImplementationOnce(() => new Promise(resolve => { resolveSecond = resolve; }));
    
    const { result } = renderHook(() => useApi(apiFunction));

    // Primeira execução
    act(() => {
      result.current.execute();
    });

    // Segunda execução antes da primeira terminar
    act(() => {
      result.current.execute();
    });

    // Resolve a segunda primeiro
    act(() => {
      resolveSecond!({ data: 'second' });
    });

    await waitFor(() => {
      expect(result.current.data).toEqual({ data: 'second' });
    });

    // Resolve a primeira depois
    act(() => {
      resolveFirst!({ data: 'first' });
    });

    // Deve manter o resultado da segunda (mais recente)
    expect(result.current.data).toEqual({ data: 'second' });
  });

  it('deve funcionar com diferentes tipos de dados', async () => {
    const testCases = [
      { input: 'string', expected: 'string' },
      { input: 123, expected: 123 },
      { input: true, expected: true },
      { input: null, expected: null },
      { input: undefined, expected: undefined },
      { input: [], expected: [] },
      { input: {}, expected: {} },
    ];

    for (const testCase of testCases) {
      const apiFunction = vi.fn().mockResolvedValue(testCase.input);
      const { result } = renderHook(() => useApi(apiFunction));

      act(() => {
        result.current.execute();
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.data).toEqual(testCase.expected);
    }
  });

  it('deve manter referência estável da função execute', () => {
    const apiFunction = vi.fn();
    const { result, rerender } = renderHook(() => useApi(apiFunction));

    const firstExecute = result.current.execute;

    // Re-renderiza
    rerender();

    const secondExecute = result.current.execute;

    // A função execute deve manter a mesma referência
    expect(firstExecute).toBe(secondExecute);
  });

  it('deve lidar com timeout de requisições', async () => {
    const apiFunction = vi.fn().mockImplementation(
      () => new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Request timeout')), 100)
      )
    );
    
    const { result } = renderHook(() => useApi(apiFunction));

    act(() => {
      result.current.execute();
    });

    await waitFor(() => {
      expect(result.current.error).toBe('Request timeout');
    }, { timeout: 200 });

    expect(result.current.loading).toBe(false);
    expect(result.current.data).toBeNull();
  });

  it('deve permitir retry manual após erro', async () => {
    const apiFunction = vi.fn()
      .mockRejectedValueOnce(new Error('Network error'))
      .mockResolvedValueOnce({ success: true });
    
    const { result } = renderHook(() => useApi(apiFunction));

    // Primeira tentativa (falha)
    act(() => {
      result.current.execute();
    });

    await waitFor(() => {
      expect(result.current.error).toBe('Network error');
    });

    // Retry manual
    act(() => {
      result.current.execute();
    });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toEqual({ success: true });
    expect(result.current.error).toBeNull();
    expect(apiFunction).toHaveBeenCalledTimes(2);
  });

  it('deve funcionar com funções assíncronas complexas', async () => {
    const complexApiFunction = async (params: any) => {
      // Simula operações complexas
      await new Promise(resolve => setTimeout(resolve, 10));
      
      if (params?.shouldFail) {
        throw new Error('Complex operation failed');
      }
      
      return {
        processed: true,
        timestamp: Date.now(),
        params
      };
    };
    
    const { result } = renderHook(() => useApi(complexApiFunction));

    // Teste com sucesso
    act(() => {
      result.current.execute({ data: 'test' });
    });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toMatchObject({
      processed: true,
      params: { data: 'test' }
    });

    // Teste com falha
    act(() => {
      result.current.execute({ shouldFail: true });
    });

    await waitFor(() => {
      expect(result.current.error).toBe('Complex operation failed');
    });
  });
});
