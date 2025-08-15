import { useState, useEffect, useRef, useCallback } from 'react';

/**
 * Hook para implementar debounce em valores
 * @param value - Valor a ser debounced
 * @param delay - Delay em milissegundos (padrao: 300ms)
 * @returns Valor debounced
 */
export function useDebounce<T>(value: T, delay: number = 300): T {
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
}

/**
 * Hook para implementar debounce em callbacks
 * @param callback - Funcao a ser debounced
 * @param delay - Delay em milissegundos (padrao: 300ms)
 * @returns Funcao debounced
 */
export function useDebouncedCallback<T extends (...args: any[]) => any>(
  callback: T,
  delay: number = 300
): T {
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const callbackRef = useRef(callback);

  // Atualizar a referencia do callback
  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);

  // Limpar timeout ao desmontar
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  return useCallback(
    ((...args: Parameters<T>) => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }

      timeoutRef.current = setTimeout(() => {
        callbackRef.current(...args);
      }, delay);
    }) as T,
    [delay]
  );
}

/**
 * Hook para implementar throttle em callbacks
 * @param callback - Funcao a ser throttled
 * @param delay - Delay em milissegundos (padrao: 100ms)
 * @returns Funcao throttled
 */
export function useThrottledCallback<T extends (...args: any[]) => any>(
  callback: T,
  delay: number = 100
): T {
  const lastCallRef = useRef<number>(0);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const callbackRef = useRef(callback);

  // Atualizar a referencia do callback
  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);

  // Limpar timeout ao desmontar
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  return useCallback(
    ((...args: Parameters<T>) => {
      const now = Date.now();
      const timeSinceLastCall = now - lastCallRef.current;

      if (timeSinceLastCall >= delay) {
        // Executar imediatamente se passou tempo suficiente
        lastCallRef.current = now;
        callbackRef.current(...args);
      } else {
        // Agendar execucao para o final do periodo de throttle
        if (timeoutRef.current) {
          clearTimeout(timeoutRef.current);
        }

        timeoutRef.current = setTimeout(() => {
          lastCallRef.current = Date.now();
          callbackRef.current(...args);
        }, delay - timeSinceLastCall);
      }
    }) as T,
    [delay]
  );
}

/**
 * Hook combinado para debounce com throttle
 * util para campos de busca que precisam de resposta rapida mas controlada
 * @param callback - Funcao a ser processada
 * @param debounceDelay - Delay do debounce (padrao: 300ms)
 * @param throttleDelay - Delay do throttle (padrao: 100ms)
 * @returns Objeto com funcoes debounced e throttled
 */
export function useDebounceThrottle<T extends (...args: any[]) => any>(
  callback: T,
  debounceDelay: number = 300,
  throttleDelay: number = 100
) {
  const debouncedCallback = useDebouncedCallback(callback, debounceDelay);
  const throttledCallback = useThrottledCallback(callback, throttleDelay);

  return {
    debounced: debouncedCallback,
    throttled: throttledCallback,
  };
}