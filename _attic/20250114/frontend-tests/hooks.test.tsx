import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useState, useEffect, useCallback, useRef } from 'react';

// Hook para gerenciar estado local com localStorage
export const useLocalStorage = <T>(
  key: string,
  initialValue: T
): [T, (value: T | ((prev: T) => T)) => void] => {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(`Erro ao ler localStorage para chave "${key}":`, error);
      return initialValue;
    }
  });

  const setValue = useCallback(
    (value: T | ((prev: T) => T)) => {
      try {
        const valueToStore = value instanceof Function ? value(storedValue) : value;
        setStoredValue(valueToStore);
        window.localStorage.setItem(key, JSON.stringify(valueToStore));
      } catch (error) {
        console.error(`Erro ao salvar no localStorage para chave "${key}":`, error);
      }
    },
    [key, storedValue]
  );

  return [storedValue, setValue];
};

// Hook para debounce
export const useDebounce = <T>(value: T, delay: number): T => {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};

// Hook para fazer requisicoes HTTP
export const useFetch = <T>(
  url: string,
  options?: RequestInit
): {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
} => {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(url, options);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
    } finally {
      setLoading(false);
    }
  }, [url, options]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
};

// Hook para gerenciar estado de formulario
export const useForm = <T extends Record<string, any>>(
  initialValues: T,
  validationRules?: Partial<Record<keyof T, (value: any) => string | null>>
) => {
  const [values, setValues] = useState<T>(initialValues);
  const [errors, setErrors] = useState<Partial<Record<keyof T, string>>>({});
  const [touched, setTouched] = useState<Partial<Record<keyof T, boolean>>>({});

  const setValue = useCallback(
    (name: keyof T, value: any) => {
      setValues(prev => ({ ...prev, [name]: value }));
      
      // Validar campo se ha regras de validacao
      if (validationRules?.[name]) {
        const error = validationRules[name]!(value);
        setErrors(prev => ({ ...prev, [name]: error || undefined }));
      }
    },
    [validationRules]
  );

  const setTouched = useCallback(
    (name: keyof T) => {
      setTouched(prev => ({ ...prev, [name]: true }));
    },
    []
  );

  const validate = useCallback(() => {
    if (!validationRules) return true;
    
    const newErrors: Partial<Record<keyof T, string>> = {};
    let isValid = true;
    
    Object.keys(validationRules).forEach(key => {
      const fieldKey = key as keyof T;
      const validator = validationRules[fieldKey]!;
      const error = validator(values[fieldKey]);
      
      if (error) {
        newErrors[fieldKey] = error;
        isValid = false;
      }
    });
    
    setErrors(newErrors);
    return isValid;
  }, [values, validationRules]);

  const reset = useCallback(() => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
  }, [initialValues]);

  return {
    values,
    errors,
    touched,
    setValue,
    setTouched,
    validate,
    reset,
    isValid: Object.keys(errors).length === 0
  };
};

// Hook para detectar clique fora do elemento
export const useClickOutside = (
  ref: React.RefObject<HTMLElement>,
  callback: () => void
) => {
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (ref.current && !ref.current.contains(event.target as Node)) {
        callback();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [ref, callback]);
};

// Hook para gerenciar estado de loading
export const useAsync = <T, Args extends any[]>(
  asyncFunction: (...args: Args) => Promise<T>
) => {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const execute = useCallback(
    async (...args: Args) => {
      try {
        setLoading(true);
        setError(null);
        const result = await asyncFunction(...args);
        setData(result);
        return result;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido';
        setError(errorMessage);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [asyncFunction]
  );

  return { data, loading, error, execute };
};

// Hook para gerenciar paginacao
export const usePagination = (
  totalItems: number,
  itemsPerPage: number = 10
) => {
  const [currentPage, setCurrentPage] = useState(1);
  
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = Math.min(startIndex + itemsPerPage, totalItems);
  
  const goToPage = useCallback(
    (page: number) => {
      if (page >= 1 && page <= totalPages) {
        setCurrentPage(page);
      }
    },
    [totalPages]
  );
  
  const goToNext = useCallback(() => {
    goToPage(currentPage + 1);
  }, [currentPage, goToPage]);
  
  const goToPrevious = useCallback(() => {
    goToPage(currentPage - 1);
  }, [currentPage, goToPage]);
  
  const goToFirst = useCallback(() => {
    goToPage(1);
  }, [goToPage]);
  
  const goToLast = useCallback(() => {
    goToPage(totalPages);
  }, [goToPage, totalPages]);
  
  return {
    currentPage,
    totalPages,
    startIndex,
    endIndex,
    hasNext: currentPage < totalPages,
    hasPrevious: currentPage > 1,
    goToPage,
    goToNext,
    goToPrevious,
    goToFirst,
    goToLast
  };
};

// Hook para gerenciar filtros
export const useFilters = <T extends Record<string, any>>(initialFilters: T) => {
  const [filters, setFilters] = useState<T>(initialFilters);
  
  const setFilter = useCallback(
    (key: keyof T, value: any) => {
      setFilters(prev => ({ ...prev, [key]: value }));
    },
    []
  );
  
  const removeFilter = useCallback(
    (key: keyof T) => {
      setFilters(prev => {
        const newFilters = { ...prev };
        delete newFilters[key];
        return newFilters;
      });
    },
    []
  );
  
  const clearFilters = useCallback(() => {
    setFilters(initialFilters);
  }, [initialFilters]);
  
  const hasActiveFilters = Object.keys(filters).some(
    key => filters[key] !== initialFilters[key]
  );
  
  return {
    filters,
    setFilter,
    removeFilter,
    clearFilters,
    hasActiveFilters
  };
};

// Hook para detectar tamanho da tela
export const useMediaQuery = (query: string): boolean => {
  const [matches, setMatches] = useState<boolean>(() => {
    if (typeof window !== 'undefined') {
      return window.matchMedia(query).matches;
    }
    return false;
  });

  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    const mediaQuery = window.matchMedia(query);
    const handler = (event: MediaQueryListEvent) => {
      setMatches(event.matches);
    };

    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, [query]);

  return matches;
};

// Hook para gerenciar estado de toggle
export const useToggle = (initialValue: boolean = false) => {
  const [value, setValue] = useState<boolean>(initialValue);
  
  const toggle = useCallback(() => {
    setValue(prev => !prev);
  }, []);
  
  const setTrue = useCallback(() => {
    setValue(true);
  }, []);
  
  const setFalse = useCallback(() => {
    setValue(false);
  }, []);
  
  return { value, toggle, setTrue, setFalse, setValue };
};

// Hook para gerenciar intervalo
export const useInterval = (callback: () => void, delay: number | null) => {
  const savedCallback = useRef<() => void>();

  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  useEffect(() => {
    if (delay === null) return;
    
    const tick = () => {
      savedCallback.current?.();
    };
    
    const id = setInterval(tick, delay);
    return () => clearInterval(id);
  }, [delay]);
};

describe('Testes Unitarios de Hooks', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  describe('useLocalStorage', () => {
    it('deve inicializar com valor padrao', () => {
      const { result } = renderHook(() => useLocalStorage('test-key', 'default-value'));
      
      expect(result.current[0]).toBe('default-value');
    });

    it('deve salvar valor no localStorage', () => {
      const { result } = renderHook(() => useLocalStorage('test-key', 'initial'));
      
      act(() => {
        result.current[1]('new-value');
      });
      
      expect(result.current[0]).toBe('new-value');
      expect(localStorage.getItem('test-key')).toBe('"new-value"');
    });

    it('deve carregar valor existente do localStorage', () => {
      localStorage.setItem('existing-key', '"existing-value"');
      
      const { result } = renderHook(() => useLocalStorage('existing-key', 'default'));
      
      expect(result.current[0]).toBe('existing-value');
    });

    it('deve lidar com funcao como valor', () => {
      const { result } = renderHook(() => useLocalStorage('counter', 0));
      
      act(() => {
        result.current[1](prev => prev + 1);
      });
      
      expect(result.current[0]).toBe(1);
    });

    it('deve lidar com erro no localStorage', () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      
      // Simular erro no localStorage
      const originalSetItem = Storage.prototype.setItem;
      Storage.prototype.setItem = vi.fn(() => {
        throw new Error('Storage error');
      });
      
      const { result } = renderHook(() => useLocalStorage('error-key', 'default'));
      
      act(() => {
        result.current[1]('new-value');
      });
      
      expect(consoleSpy).toHaveBeenCalled();
      
      // Restaurar metodo original
      Storage.prototype.setItem = originalSetItem;
      consoleSpy.mockRestore();
    });
  });

  describe('useDebounce', () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    afterEach(() => {
      vi.useRealTimers();
    });

    it('deve retornar valor inicial imediatamente', () => {
      const { result } = renderHook(() => useDebounce('initial', 500));
      
      expect(result.current).toBe('initial');
    });

    it('deve debounce mudancas de valor', () => {
      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: 'initial', delay: 500 } }
      );
      
      expect(result.current).toBe('initial');
      
      rerender({ value: 'updated', delay: 500 });
      expect(result.current).toBe('initial'); // Ainda nao mudou
      
      act(() => {
        vi.advanceTimersByTime(500);
      });
      
      expect(result.current).toBe('updated');
    });

    it('deve cancelar timer anterior em mudancas rapidas', () => {
      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: 'initial', delay: 500 } }
      );
      
      rerender({ value: 'first', delay: 500 });
      
      act(() => {
        vi.advanceTimersByTime(250);
      });
      
      rerender({ value: 'second', delay: 500 });
      
      act(() => {
        vi.advanceTimersByTime(500);
      });
      
      expect(result.current).toBe('second');
    });
  });

  describe('useFetch', () => {
    beforeEach(() => {
      global.fetch = vi.fn();
    });

    it('deve fazer requisicao e retornar dados', async () => {
      const mockData = { id: 1, name: 'Test' };
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      });
      
      const { result } = renderHook(() => useFetch('/api/test'));
      
      expect(result.current.loading).toBe(true);
      expect(result.current.data).toBeNull();
      expect(result.current.error).toBeNull();
      
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });
      
      expect(result.current.data).toEqual(mockData);
      expect(result.current.error).toBeNull();
    });

    it('deve lidar com erro de requisicao', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found'
      });
      
      const { result } = renderHook(() => useFetch('/api/not-found'));
      
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });
      
      expect(result.current.data).toBeNull();
      expect(result.current.error).toBe('HTTP 404: Not Found');
    });

    it('deve permitir refetch', async () => {
      const mockData = { id: 1, name: 'Test' };
      (global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => mockData
      });
      
      const { result } = renderHook(() => useFetch('/api/test'));
      
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });
      
      act(() => {
        result.current.refetch();
      });
      
      expect(result.current.loading).toBe(true);
      
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });
      
      expect(global.fetch).toHaveBeenCalledTimes(2);
    });
  });

  describe('useForm', () => {
    const initialValues = {
      name: '',
      email: '',
      age: 0
    };

    const validationRules = {
      name: (value: string) => value.length < 2 ? 'Nome deve ter pelo menos 2 caracteres' : null,
      email: (value: string) => !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) ? 'Email invalido' : null,
      age: (value: number) => value < 18 ? 'Idade deve ser maior que 18' : null
    };

    it('deve inicializar com valores padrao', () => {
      const { result } = renderHook(() => useForm(initialValues));
      
      expect(result.current.values).toEqual(initialValues);
      expect(result.current.errors).toEqual({});
      expect(result.current.touched).toEqual({});
      expect(result.current.isValid).toBe(true);
    });

    it('deve atualizar valores', () => {
      const { result } = renderHook(() => useForm(initialValues));
      
      act(() => {
        result.current.setValue('name', 'John');
      });
      
      expect(result.current.values.name).toBe('John');
    });

    it('deve validar campos com regras', () => {
      const { result } = renderHook(() => useForm(initialValues, validationRules));
      
      act(() => {
        result.current.setValue('name', 'J');
      });
      
      expect(result.current.errors.name).toBe('Nome deve ter pelo menos 2 caracteres');
      expect(result.current.isValid).toBe(false);
    });

    it('deve marcar campos como touched', () => {
      const { result } = renderHook(() => useForm(initialValues));
      
      act(() => {
        result.current.setTouched('name');
      });
      
      expect(result.current.touched.name).toBe(true);
    });

    it('deve validar todos os campos', () => {
      const { result } = renderHook(() => useForm(initialValues, validationRules));
      
      act(() => {
        result.current.setValue('name', 'J');
        result.current.setValue('email', 'invalid-email');
        result.current.setValue('age', 16);
      });
      
      let isValid;
      act(() => {
        isValid = result.current.validate();
      });
      
      expect(isValid).toBe(false);
      expect(Object.keys(result.current.errors)).toHaveLength(3);
    });

    it('deve resetar formulario', () => {
      const { result } = renderHook(() => useForm(initialValues));
      
      act(() => {
        result.current.setValue('name', 'John');
        result.current.setTouched('name');
      });
      
      act(() => {
        result.current.reset();
      });
      
      expect(result.current.values).toEqual(initialValues);
      expect(result.current.errors).toEqual({});
      expect(result.current.touched).toEqual({});
    });
  });

  describe('useClickOutside', () => {
    it('deve chamar callback quando clica fora', () => {
      const callback = vi.fn();
      const ref = { current: document.createElement('div') };
      
      renderHook(() => useClickOutside(ref, callback));
      
      // Simular clique fora do elemento
      const outsideElement = document.createElement('div');
      document.body.appendChild(outsideElement);
      
      const event = new MouseEvent('mousedown', {
        bubbles: true,
        cancelable: true,
      });
      
      Object.defineProperty(event, 'target', {
        value: outsideElement,
        enumerable: true
      });
      
      document.dispatchEvent(event);
      
      expect(callback).toHaveBeenCalledTimes(1);
      
      document.body.removeChild(outsideElement);
    });

    it('nao deve chamar callback quando clica dentro', () => {
      const callback = vi.fn();
      const ref = { current: document.createElement('div') };
      const insideElement = document.createElement('span');
      ref.current.appendChild(insideElement);
      
      renderHook(() => useClickOutside(ref, callback));
      
      const event = new MouseEvent('mousedown', {
        bubbles: true,
        cancelable: true,
      });
      
      Object.defineProperty(event, 'target', {
        value: insideElement,
        enumerable: true
      });
      
      document.dispatchEvent(event);
      
      expect(callback).not.toHaveBeenCalled();
    });
  });

  describe('useAsync', () => {
    it('deve executar funcao assincrona com sucesso', async () => {
      const asyncFn = vi.fn().mockResolvedValue('success');
      const { result } = renderHook(() => useAsync(asyncFn));
      
      expect(result.current.loading).toBe(false);
      expect(result.current.data).toBeNull();
      expect(result.current.error).toBeNull();
      
      let returnValue;
      await act(async () => {
        returnValue = await result.current.execute('arg1', 'arg2');
      });
      
      expect(result.current.loading).toBe(false);
      expect(result.current.data).toBe('success');
      expect(result.current.error).toBeNull();
      expect(returnValue).toBe('success');
      expect(asyncFn).toHaveBeenCalledWith('arg1', 'arg2');
    });

    it('deve lidar com erro na funcao assincrona', async () => {
      const error = new Error('Async error');
      const asyncFn = vi.fn().mockRejectedValue(error);
      const { result } = renderHook(() => useAsync(asyncFn));
      
      await act(async () => {
        try {
          await result.current.execute();
        } catch (e) {
          // Erro esperado
        }
      });
      
      expect(result.current.loading).toBe(false);
      expect(result.current.data).toBeNull();
      expect(result.current.error).toBe('Async error');
    });
  });

  describe('usePagination', () => {
    it('deve inicializar com valores corretos', () => {
      const { result } = renderHook(() => usePagination(100, 10));
      
      expect(result.current.currentPage).toBe(1);
      expect(result.current.totalPages).toBe(10);
      expect(result.current.startIndex).toBe(0);
      expect(result.current.endIndex).toBe(10);
      expect(result.current.hasNext).toBe(true);
      expect(result.current.hasPrevious).toBe(false);
    });

    it('deve navegar entre paginas', () => {
      const { result } = renderHook(() => usePagination(100, 10));
      
      act(() => {
        result.current.goToNext();
      });
      
      expect(result.current.currentPage).toBe(2);
      expect(result.current.startIndex).toBe(10);
      expect(result.current.endIndex).toBe(20);
      
      act(() => {
        result.current.goToPrevious();
      });
      
      expect(result.current.currentPage).toBe(1);
    });

    it('deve ir para primeira e ultima pagina', () => {
      const { result } = renderHook(() => usePagination(100, 10));
      
      act(() => {
        result.current.goToLast();
      });
      
      expect(result.current.currentPage).toBe(10);
      expect(result.current.hasNext).toBe(false);
      
      act(() => {
        result.current.goToFirst();
      });
      
      expect(result.current.currentPage).toBe(1);
    });

    it('deve validar limites de pagina', () => {
      const { result } = renderHook(() => usePagination(100, 10));
      
      act(() => {
        result.current.goToPage(0); // Invalido
      });
      
      expect(result.current.currentPage).toBe(1);
      
      act(() => {
        result.current.goToPage(11); // Invalido
      });
      
      expect(result.current.currentPage).toBe(1);
    });
  });

  describe('useFilters', () => {
    const initialFilters = {
      status: '',
      priority: '',
      search: ''
    };

    it('deve inicializar com filtros padrao', () => {
      const { result } = renderHook(() => useFilters(initialFilters));
      
      expect(result.current.filters).toEqual(initialFilters);
      expect(result.current.hasActiveFilters).toBe(false);
    });

    it('deve definir filtro', () => {
      const { result } = renderHook(() => useFilters(initialFilters));
      
      act(() => {
        result.current.setFilter('status', 'open');
      });
      
      expect(result.current.filters.status).toBe('open');
      expect(result.current.hasActiveFilters).toBe(true);
    });

    it('deve remover filtro', () => {
      const { result } = renderHook(() => useFilters(initialFilters));
      
      act(() => {
        result.current.setFilter('status', 'open');
      });
      
      act(() => {
        result.current.removeFilter('status');
      });
      
      expect(result.current.filters.status).toBeUndefined();
    });

    it('deve limpar todos os filtros', () => {
      const { result } = renderHook(() => useFilters(initialFilters));
      
      act(() => {
        result.current.setFilter('status', 'open');
        result.current.setFilter('priority', 'high');
      });
      
      act(() => {
        result.current.clearFilters();
      });
      
      expect(result.current.filters).toEqual(initialFilters);
      expect(result.current.hasActiveFilters).toBe(false);
    });
  });

  describe('useMediaQuery', () => {
    it('deve detectar media query', () => {
      // Mock matchMedia
      const mockMatchMedia = vi.fn().mockImplementation(query => ({
        matches: query === '(min-width: 768px)',
        addEventListener: vi.fn(),
        removeEventListener: vi.fn()
      }));
      
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: mockMatchMedia
      });
      
      const { result } = renderHook(() => useMediaQuery('(min-width: 768px)'));
      
      expect(result.current).toBe(true);
      expect(mockMatchMedia).toHaveBeenCalledWith('(min-width: 768px)');
    });
  });

  describe('useToggle', () => {
    it('deve inicializar com valor padrao', () => {
      const { result } = renderHook(() => useToggle());
      
      expect(result.current.value).toBe(false);
    });

    it('deve inicializar com valor customizado', () => {
      const { result } = renderHook(() => useToggle(true));
      
      expect(result.current.value).toBe(true);
    });

    it('deve alternar valor', () => {
      const { result } = renderHook(() => useToggle(false));
      
      act(() => {
        result.current.toggle();
      });
      
      expect(result.current.value).toBe(true);
      
      act(() => {
        result.current.toggle();
      });
      
      expect(result.current.value).toBe(false);
    });

    it('deve definir valor como true', () => {
      const { result } = renderHook(() => useToggle(false));
      
      act(() => {
        result.current.setTrue();
      });
      
      expect(result.current.value).toBe(true);
    });

    it('deve definir valor como false', () => {
      const { result } = renderHook(() => useToggle(true));
      
      act(() => {
        result.current.setFalse();
      });
      
      expect(result.current.value).toBe(false);
    });
  });

  describe('useInterval', () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    afterEach(() => {
      vi.useRealTimers();
    });

    it('deve executar callback em intervalos', () => {
      const callback = vi.fn();
      
      renderHook(() => useInterval(callback, 1000));
      
      expect(callback).not.toHaveBeenCalled();
      
      act(() => {
        vi.advanceTimersByTime(1000);
      });
      
      expect(callback).toHaveBeenCalledTimes(1);
      
      act(() => {
        vi.advanceTimersByTime(1000);
      });
      
      expect(callback).toHaveBeenCalledTimes(2);
    });

    it('deve parar intervalo quando delay e null', () => {
      const callback = vi.fn();
      
      const { rerender } = renderHook(
        ({ delay }) => useInterval(callback, delay),
        { initialProps: { delay: 1000 } }
      );
      
      act(() => {
        vi.advanceTimersByTime(1000);
      });
      
      expect(callback).toHaveBeenCalledTimes(1);
      
      rerender({ delay: null });
      
      act(() => {
        vi.advanceTimersByTime(1000);
      });
      
      expect(callback).toHaveBeenCalledTimes(1); // Nao deve ter chamado novamente
    });
  });
});
