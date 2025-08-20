import { useState, useCallback, useEffect } from 'react';

export interface CacheData<T> {
  value: T;
  timestamp: number;
  ttl: number;
}

export interface CacheOptions {
  ttl?: number;
}

export interface LocalCacheHookResult<T> {
  value: T;
  setValue: (value: T) => void;
  clearCache: () => void;
  isExpired: boolean;
}

/**
 * Hook para gerenciar cache local usando localStorage
 * @param key - Chave do cache
 * @param defaultValue - Valor padrão quando cache está vazio
 * @param options - Opções do cache (TTL)
 */
export function useCache<T>(
  key: string,
  defaultValue: T,
  options: CacheOptions = {}
): LocalCacheHookResult<T> {
  const { ttl = 5 * 60 * 1000 } = options; // 5 minutos por padrão

  // Função para carregar dados do localStorage
  const loadFromStorage = useCallback((): { value: T; isExpired: boolean } => {
    try {
      const stored = localStorage.getItem(key);
      if (!stored) {
        return { value: defaultValue, isExpired: false };
      }

      const data: CacheData<T> = JSON.parse(stored);
      const now = Date.now();
      const isExpired = ttl > 0 && now - data.timestamp > data.ttl;

      return {
        value: data.value,
        isExpired,
      };
    } catch (error) {
      console.warn('Erro ao carregar cache:', error);
      return { value: defaultValue, isExpired: false };
    }
  }, [key, defaultValue, ttl]);

  // Estado inicial
  const [cacheState, setCacheState] = useState(() => {
    const { value, isExpired } = loadFromStorage();
    return { value, isExpired };
  });

  // Função para salvar no localStorage
  const saveToStorage = useCallback(
    (value: T) => {
      try {
        const data: CacheData<T> = {
          value,
          timestamp: Date.now(),
          ttl,
        };
        localStorage.setItem(key, JSON.stringify(data));
      } catch (error) {
        console.warn('Erro ao salvar cache:', error);
      }
    },
    [key, ttl]
  );

  // Função para definir valor
  const setValue = useCallback(
    (value: T) => {
      setCacheState({ value, isExpired: false });
      saveToStorage(value);
    },
    [saveToStorage]
  );

  // Função para limpar cache
  const clearCache = useCallback(() => {
    try {
      localStorage.removeItem(key);
      setCacheState({ value: defaultValue, isExpired: false });
    } catch (error) {
      console.warn('Erro ao limpar cache:', error);
    }
  }, [key, defaultValue]);

  // Verificar expiração quando a chave muda
  useEffect(() => {
    const { value, isExpired } = loadFromStorage();
    setCacheState({ value, isExpired });
  }, [key, loadFromStorage]);

  return {
    value: cacheState.value,
    setValue,
    clearCache,
    isExpired: cacheState.isExpired,
  };
}

export default useCache;
