import { useState, useEffect, useRef, useCallback } from 'react';

/**
 * Hook para implementar debounce em valores
 * @param value - Valor a ser debounced
 * @param delay - Delay em milissegundos (padrão: 300ms)
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
 * @param callback - Função a ser debounced
 * @param delay - Delay em milissegundos (padrão: 300ms)
 * @returns Função debounced
 */
export function useDebouncedCallback<T extends (...args: any[]) => any>(
  callback: T,
  delay: number = 300
): T {
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const callbackRef = useRef(callback);

  // Atualizar a referência do callback apenas quando necessário
  callbackRef.current = callback;

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
 * @param callback - Função a ser throttled
 * @param delay - Delay em milissegundos (padrão: 100ms)
 * @returns Função throttled
 */
export function useThrottledCallback<T extends (...args: any[]) => any>(
  callback: T,
  delay: number = 100
): T {
  const lastCallRef = useRef<number>(0);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const callbackRef = useRef(callback);

  // Atualizar a referência do callback apenas quando necessário
  callbackRef.current = callback;

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
        // Agendar execução para o final do período de throttle
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
 * Útil para campos de busca que precisam de resposta rápida mas controlada
 * @param callback - Função a ser processada
 * @param debounceDelay - Delay do debounce (padrão: 300ms)
 * @param throttleDelay - Delay do throttle (padrão: 100ms)
 * @returns Objeto com funções debounced e throttled
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