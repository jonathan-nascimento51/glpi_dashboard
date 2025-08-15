import { renderHook, act } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { useCache } from '../../../hooks/useCache';

// Mock do localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

describe('useCache Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.useRealTimers();
  });

  it('deve inicializar com valor padrao quando cache esta vazio', () => {
    localStorageMock.getItem.mockReturnValue(null);
    
    const { result } = renderHook(() => 
      useCache('test-key', 'default-value')
    );

    expect(result.current.value).toBe('default-value');
    expect(result.current.isExpired).toBe(false);
    expect(localStorageMock.getItem).toHaveBeenCalledWith('test-key');
  });

  it('deve carregar valor valido do cache', () => {
    const cachedData = {
      value: 'cached-value',
      timestamp: Date.now(),
      ttl: 5000
    };
    localStorageMock.getItem.mockReturnValue(JSON.stringify(cachedData));
    
    const { result } = renderHook(() => 
      useCache('test-key', 'default-value')
    );

    expect(result.current.value).toBe('cached-value');
    expect(result.current.isExpired).toBe(false);
  });

  it('deve detectar cache expirado', () => {
    const expiredData = {
      value: 'expired-value',
      timestamp: Date.now() - 10000, // 10 segundos atras
      ttl: 5000 // TTL de 5 segundos
    };
    localStorageMock.getItem.mockReturnValue(JSON.stringify(expiredData));
    
    const { result } = renderHook(() => 
      useCache('test-key', 'default-value')
    );

    expect(result.current.value).toBe('expired-value');
    expect(result.current.isExpired).toBe(true);
  });

  it('deve definir novo valor no cache', () => {
    localStorageMock.getItem.mockReturnValue(null);
    
    const { result } = renderHook(() => 
      useCache('test-key', 'default-value', { ttl: 5000 })
    );

    act(() => {
      result.current.setValue('new-value');
    });

    expect(result.current.value).toBe('new-value');
    expect(result.current.isExpired).toBe(false);
    
    const expectedCacheData = {
      value: 'new-value',
      timestamp: expect.any(Number),
      ttl: 5000
    };
    
    expect(localStorageMock.setItem).toHaveBeenCalledWith(
      'test-key',
      JSON.stringify(expectedCacheData)
    );
  });

  it('deve limpar cache', () => {
    const cachedData = {
      value: 'cached-value',
      timestamp: Date.now(),
      ttl: 5000
    };
    localStorageMock.getItem.mockReturnValue(JSON.stringify(cachedData));
    
    const { result } = renderHook(() => 
      useCache('test-key', 'default-value')
    );

    expect(result.current.value).toBe('cached-value');

    act(() => {
      result.current.clearCache();
    });

    expect(result.current.value).toBe('default-value');
    expect(result.current.isExpired).toBe(false);
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('test-key');
  });

  it('deve lidar com JSON invalido no localStorage', () => {
    localStorageMock.getItem.mockReturnValue('invalid-json');
    
    const { result } = renderHook(() => 
      useCache('test-key', 'default-value')
    );

    expect(result.current.value).toBe('default-value');
    expect(result.current.isExpired).toBe(false);
  });

  it('deve usar TTL personalizado', () => {
    localStorageMock.getItem.mockReturnValue(null);
    
    const { result } = renderHook(() => 
      useCache('test-key', 'default-value', { ttl: 10000 })
    );

    act(() => {
      result.current.setValue('test-value');
    });

    const expectedCacheData = {
      value: 'test-value',
      timestamp: expect.any(Number),
      ttl: 10000
    };
    
    expect(localStorageMock.setItem).toHaveBeenCalledWith(
      'test-key',
      JSON.stringify(expectedCacheData)
    );
  });

  it('deve funcionar com diferentes tipos de dados', () => {
    const testCases = [
      { value: 'string', expected: 'string' },
      { value: 123, expected: 123 },
      { value: true, expected: true },
      { value: null, expected: null },
      { value: { obj: 'test' }, expected: { obj: 'test' } },
      { value: [1, 2, 3], expected: [1, 2, 3] },
    ];

    testCases.forEach(({ value, expected }, index) => {
      localStorageMock.getItem.mockReturnValue(null);
      
      const { result } = renderHook(() => 
        useCache(`test-key-${index}`, 'default')
      );

      act(() => {
        result.current.setValue(value);
      });

      expect(result.current.value).toEqual(expected);
    });
  });

  it('deve atualizar isExpired quando o tempo passa', () => {
    const cachedData = {
      value: 'cached-value',
      timestamp: Date.now(),
      ttl: 1000 // 1 segundo
    };
    localStorageMock.getItem.mockReturnValue(JSON.stringify(cachedData));
    
    const { result } = renderHook(() => 
      useCache('test-key', 'default-value')
    );

    expect(result.current.isExpired).toBe(false);

    // Avanca o tempo em 2 segundos
    act(() => {
      vi.advanceTimersByTime(2000);
    });

    // Re-renderiza para verificar se isExpired foi atualizado
    const { result: newResult } = renderHook(() => 
      useCache('test-key', 'default-value')
    );

    expect(newResult.current.isExpired).toBe(true);
  });

  it('deve manter referencia estavel das funcoes', () => {
    localStorageMock.getItem.mockReturnValue(null);
    
    const { result, rerender } = renderHook(() => 
      useCache('test-key', 'default-value')
    );

    const firstSetValue = result.current.setValue;
    const firstClearCache = result.current.clearCache;

    rerender();

    expect(result.current.setValue).toBe(firstSetValue);
    expect(result.current.clearCache).toBe(firstClearCache);
  });

  it('deve lidar com erros do localStorage', () => {
    // Simula erro no localStorage.setItem
    localStorageMock.setItem.mockImplementation(() => {
      throw new Error('Storage quota exceeded');
    });
    
    const { result } = renderHook(() => 
      useCache('test-key', 'default-value')
    );

    // Nao deve lancar erro
    act(() => {
      result.current.setValue('new-value');
    });

    // Valor deve ser atualizado no estado mesmo com erro no localStorage
    expect(result.current.value).toBe('new-value');
  });

  it('deve funcionar sem TTL (cache permanente)', () => {
    localStorageMock.getItem.mockReturnValue(null);
    
    const { result } = renderHook(() => 
      useCache('test-key', 'default-value', { ttl: 0 })
    );

    act(() => {
      result.current.setValue('permanent-value');
    });

    const expectedCacheData = {
      value: 'permanent-value',
      timestamp: expect.any(Number),
      ttl: 0
    };
    
    expect(localStorageMock.setItem).toHaveBeenCalledWith(
      'test-key',
      JSON.stringify(expectedCacheData)
    );
  });

  it('deve verificar expiracao corretamente com TTL 0', () => {
    const permanentData = {
      value: 'permanent-value',
      timestamp: Date.now() - 100000, // Muito tempo atras
      ttl: 0 // Cache permanente
    };
    localStorageMock.getItem.mockReturnValue(JSON.stringify(permanentData));
    
    const { result } = renderHook(() => 
      useCache('test-key', 'default-value')
    );

    expect(result.current.value).toBe('permanent-value');
    expect(result.current.isExpired).toBe(false); // Nao deve expirar com TTL 0
  });

  it('deve permitir atualizacao de valor sem alterar timestamp', () => {
    const originalTimestamp = Date.now() - 1000;
    const cachedData = {
      value: 'old-value',
      timestamp: originalTimestamp,
      ttl: 5000
    };
    localStorageMock.getItem.mockReturnValue(JSON.stringify(cachedData));
    
    const { result } = renderHook(() => 
      useCache('test-key', 'default-value')
    );

    act(() => {
      result.current.setValue('new-value');
    });

    // Verifica se o timestamp foi atualizado
    const setItemCall = localStorageMock.setItem.mock.calls[0];
    const savedData = JSON.parse(setItemCall[1]);
    
    expect(savedData.value).toBe('new-value');
    expect(savedData.timestamp).toBeGreaterThan(originalTimestamp);
  });

  it('deve funcionar com chaves complexas', () => {
    const complexKey = 'user:123:dashboard:filters';
    localStorageMock.getItem.mockReturnValue(null);
    
    const { result } = renderHook(() => 
      useCache(complexKey, { filters: [] })
    );

    const newFilters = { filters: ['active', 'pending'] };
    
    act(() => {
      result.current.setValue(newFilters);
    });

    expect(result.current.value).toEqual(newFilters);
    expect(localStorageMock.setItem).toHaveBeenCalledWith(
      complexKey,
      expect.any(String)
    );
  });

  it('deve lidar com mudancas na chave do cache', () => {
    localStorageMock.getItem.mockReturnValue(null);
    
    const { result, rerender } = renderHook(
      ({ key }) => useCache(key, 'default-value'),
      { initialProps: { key: 'key1' } }
    );

    act(() => {
      result.current.setValue('value1');
    });

    expect(result.current.value).toBe('value1');

    // Muda a chave
    rerender({ key: 'key2' });

    // Deve voltar ao valor padrao para a nova chave
    expect(result.current.value).toBe('default-value');
    expect(localStorageMock.getItem).toHaveBeenCalledWith('key2');
  });
});