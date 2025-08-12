import { useMemo, useCallback, useRef, useEffect, useState } from 'react';

// Hook para memoização seletiva de dados
export function useSelectiveMemo<T>(
  data: T,
  selector: (data: T) => any,
  deps?: React.DependencyList
) {
  return useMemo(() => selector(data), deps ? [data, ...deps] : [data]);
}

// Hook para callbacks estáveis
export function useStableCallback<T extends (...args: any[]) => any>(
  callback: T
): T {
  const callbackRef = useRef(callback);
  
  useEffect(() => {
    callbackRef.current = callback;
  });
  
  return useCallback((...args: Parameters<T>) => {
    return callbackRef.current(...args);
  }, []) as T;
}

// Hook para debounce de valores
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value);
  
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);
    
    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);
  
  return debouncedValue;
}

// Hook para memoização de computações pesadas
export function useHeavyComputation<T, R>(
  data: T,
  computeFn: (data: T) => R,
  deps: React.DependencyList = []
): R {
  return useMemo(() => {
    console.log('Computing heavy operation...');
    return computeFn(data);
  }, [data, ...deps]);
}

// Hook para otimizar listas grandes
export function useOptimizedList<T>(
  items: T[],
  filterFn?: (item: T) => boolean,
  sortFn?: (a: T, b: T) => number
) {
  return useMemo(() => {
    let result = items;
    
    if (filterFn) {
      result = result.filter(filterFn);
    }
    
    if (sortFn) {
      result = [...result].sort(sortFn);
    }
    
    return result;
  }, [items, filterFn, sortFn]);
}

// Hook para detectar mudanças específicas em objetos
export function useShallowCompare<T extends Record<string, any>>(
  obj: T,
  keys: (keyof T)[]
): T {
  return useMemo(() => {
    const result = {} as T;
    keys.forEach(key => {
      result[key] = obj[key];
    });
    return result;
  }, keys.map(key => obj[key]));
}

// Hook para cache com TTL
export function useCachedValue<T>(
  key: string,
  computeFn: () => T,
  ttl: number = 5000
): T {
  const cacheRef = useRef<Map<string, { value: T; timestamp: number }>>(new Map());
  
  return useMemo(() => {
    const now = Date.now();
    const cached = cacheRef.current.get(key);
    
    if (cached && (now - cached.timestamp) < ttl) {
      return cached.value;
    }
    
    const value = computeFn();
    cacheRef.current.set(key, { value, timestamp: now });
    
    return value;
  }, [key, ttl]);
}
