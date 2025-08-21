// Utilitários complementares para API

import { API_CONFIG } from '../config/constants';
import { validateDashboardMetrics, validateFilters } from '../utils/validations';
import { formatApiError, isNetworkError } from '../utils/helpers';
import type { DashboardMetrics, Filters, User, TicketData } from '../types';

/**
 * Interface para resposta padronizada da API
 */
export interface StandardApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  error?: string;
  timestamp: string;
  version?: string;
}

/**
 * Interface para configuração de requisição
 */
export interface RequestConfig {
  timeout?: number;
  retries?: number;
  retryDelay?: number;
  cache?: boolean;
  validateResponse?: boolean;
}

/**
 * Classe para gerenciar configurações de requisição
 */
export class ApiRequestManager {
  private defaultConfig: RequestConfig = {
    timeout: API_CONFIG.TIMEOUT,
    retries: 3,
    retryDelay: 1000,
    cache: true,
    validateResponse: true,
  };

  /**
   * Criar configuração de requisição
   */
  createConfig(overrides: Partial<RequestConfig> = {}): RequestConfig {
    return { ...this.defaultConfig, ...overrides };
  }

  /**
   * Criar headers padrão
   */
  createHeaders(additionalHeaders: Record<string, string> = {}): Headers {
    const headers = new Headers({
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'X-Requested-With': 'XMLHttpRequest',
      'X-Client-Version': '1.0.0',
      ...additionalHeaders,
    });

    // Adicionar token de autenticação se disponível
    const token = localStorage.getItem('auth_token');
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }

    return headers;
  }

  /**
   * Criar URL com parâmetros
   */
  createUrl(endpoint: string, params?: Record<string, any>): string {
    const url = new URL(endpoint, API_CONFIG.BASE_URL);
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          url.searchParams.append(key, String(value));
        }
      });
    }

    return url.toString();
  }
}

/**
 * Instância global do gerenciador de requisições
 */
export const requestManager = new ApiRequestManager();

/**
 * Função para fazer requisições com retry automático
 */
export const makeRequestWithRetry = async <T>(
  url: string,
  options: RequestInit,
  config: RequestConfig = {}
): Promise<T> => {
  const finalConfig = requestManager.createConfig(config);
  let lastError: Error;

  for (let attempt = 1; attempt <= finalConfig.retries!; attempt++) {
    try {
      // Criar controller para timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), finalConfig.timeout);

      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      lastError = error instanceof Error ? error : new Error('Erro desconhecido');

      // Não fazer retry para erros que não são de rede
      if (!isNetworkError(lastError) || attempt === finalConfig.retries) {
        throw lastError;
      }

      // Aguardar antes da próxima tentativa
      await new Promise(resolve => 
        setTimeout(resolve, finalConfig.retryDelay! * attempt)
      );
    }
  }

  throw lastError!;
};

/**
 * Função para validar resposta da API
 */
export const validateApiResponse = <T>(
  data: any,
  validator?: (data: any) => { isValid: boolean; errors: string[] }
): StandardApiResponse<T> => {
  // Verificar estrutura básica
  if (!data || typeof data !== 'object') {
    throw new Error('Resposta da API inválida: dados não encontrados');
  }

  // Verificar se é uma resposta de erro
  if (data.error || data.success === false) {
    throw new Error(data.error || data.message || 'Erro desconhecido da API');
  }

  // Validar dados específicos se validator fornecido
  if (validator && data.data) {
    const validation = validator(data.data);
    if (!validation.isValid) {
      throw new Error(`Dados inválidos: ${validation.errors.join(', ')}`);
    }
  }

  return {
    success: true,
    data: data.data || data,
    message: data.message,
    timestamp: data.timestamp || new Date().toISOString(),
    version: data.version,
  };
};

/**
 * Função para criar filtros de URL
 */
export const createUrlFilters = (filters: Partial<Filters>): Record<string, string> => {
  const urlFilters: Record<string, string> = {};

  if (filters.searchQuery) {
    urlFilters.search = filters.searchQuery;
  }

  if (filters.status) {
    urlFilters.status = filters.status;
  }

  if (filters.priority !== undefined) {
    urlFilters.priority = filters.priority.toString();
  }

  if (filters.dateRange) {
    urlFilters.start_date = filters.dateRange.startDate;
    urlFilters.end_date = filters.dateRange.endDate;
  }

  if (filters.assignedTo) {
    urlFilters.assigned_to = filters.assignedTo.toString();
  }

  if (filters.category) {
    urlFilters.category = filters.category;
  }

  return urlFilters;
};

/**
 * Função para processar erros da API
 */
export const processApiError = (error: any): string => {
  if (error instanceof Error) {
    // Erro de rede
    if (error.name === 'AbortError') {
      return 'Requisição cancelada por timeout';
    }
    
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      return 'Erro de conexão com o servidor';
    }

    return error.message;
  }

  if (typeof error === 'string') {
    return error;
  }

  if (error && typeof error === 'object') {
    return error.message || error.error || 'Erro desconhecido';
  }

  return 'Erro desconhecido';
};

/**
 * Função para criar cache key
 */
export const createCacheKey = (endpoint: string, params?: any): string => {
  const baseKey = endpoint.replace(/[^a-zA-Z0-9]/g, '_');
  
  if (!params) {
    return baseKey;
  }

  const paramString = JSON.stringify(params, Object.keys(params).sort());
  const paramHash = btoa(paramString).replace(/[^a-zA-Z0-9]/g, '');
  
  return `${baseKey}_${paramHash}`;
};

/**
 * Função para verificar se dados estão expirados
 */
export const isDataExpired = (timestamp: string | Date, ttl: number): boolean => {
  const dataTime = new Date(timestamp).getTime();
  const now = Date.now();
  return (now - dataTime) > ttl;
};

/**
 * Classe para gerenciar cache de API
 */
export class ApiCache {
  private cache = new Map<string, { data: any; timestamp: Date; ttl: number }>();
  private maxSize = 100;

  /**
   * Definir item no cache
   */
  set<T>(key: string, data: T, ttl = 300000): void { // 5 minutos padrão
    // Limpar cache se estiver cheio
    if (this.cache.size >= this.maxSize) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }

    this.cache.set(key, {
      data,
      timestamp: new Date(),
      ttl,
    });
  }

  /**
   * Obter item do cache
   */
  get<T>(key: string): T | null {
    const item = this.cache.get(key);
    
    if (!item) {
      return null;
    }

    // Verificar se expirou
    if (isDataExpired(item.timestamp, item.ttl)) {
      this.cache.delete(key);
      return null;
    }

    return item.data;
  }

  /**
   * Verificar se item existe no cache
   */
  has(key: string): boolean {
    return this.get(key) !== null;
  }

  /**
   * Remover item do cache
   */
  delete(key: string): boolean {
    return this.cache.delete(key);
  }

  /**
   * Limpar todo o cache
   */
  clear(): void {
    this.cache.clear();
  }

  /**
   * Obter estatísticas do cache
   */
  getStats(): { size: number; maxSize: number; keys: string[] } {
    return {
      size: this.cache.size,
      maxSize: this.maxSize,
      keys: Array.from(this.cache.keys()),
    };
  }

  /**
   * Limpar itens expirados
   */
  cleanup(): number {
    let removedCount = 0;
    
    for (const [key, item] of this.cache.entries()) {
      if (isDataExpired(item.timestamp, item.ttl)) {
        this.cache.delete(key);
        removedCount++;
      }
    }

    return removedCount;
  }
}

/**
 * Instância global do cache
 */
export const apiCache = new ApiCache();

/**
 * Função para fazer requisição com cache
 */
export const fetchWithCache = async <T>(
  url: string,
  options: RequestInit = {},
  config: RequestConfig & { cacheKey?: string; cacheTtl?: number } = {}
): Promise<T> => {
  const cacheKey = config.cacheKey || createCacheKey(url, options.body);
  
  // Verificar cache primeiro
  if (config.cache !== false) {
    const cachedData = apiCache.get<T>(cacheKey);
    if (cachedData) {
      return cachedData;
    }
  }

  // Fazer requisição
  const data = await makeRequestWithRetry<T>(url, options, config);
  
  // Salvar no cache
  if (config.cache !== false && data) {
    apiCache.set(cacheKey, data, config.cacheTtl);
  }

  return data;
};

/**
 * Função para invalidar cache por padrão
 */
export const invalidateCache = (pattern: string): number => {
  const stats = apiCache.getStats();
  let removedCount = 0;
  
  stats.keys.forEach(key => {
    if (key.includes(pattern)) {
      apiCache.delete(key);
      removedCount++;
    }
  });

  return removedCount;
};

/**
 * Função para monitorar performance de API
 */
export const monitorApiPerformance = () => {
  const originalFetch = window.fetch;
  const performanceData: Array<{
    url: string;
    method: string;
    duration: number;
    status: number;
    timestamp: Date;
  }> = [];

  window.fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
    const startTime = performance.now();
    const url = typeof input === 'string' ? input : input.toString();
    const method = init?.method || 'GET';

    try {
      const response = await originalFetch(input, init);
      const endTime = performance.now();
      
      performanceData.push({
        url,
        method,
        duration: endTime - startTime,
        status: response.status,
        timestamp: new Date(),
      });

      return response;
    } catch (error) {
      const endTime = performance.now();
      
      performanceData.push({
        url,
        method,
        duration: endTime - startTime,
        status: 0, // Erro de rede
        timestamp: new Date(),
      });

      throw error;
    }
  };

  return {
    getPerformanceData: () => [...performanceData],
    clearPerformanceData: () => performanceData.length = 0,
    getAverageResponseTime: () => {
      if (performanceData.length === 0) return 0;
      const total = performanceData.reduce((sum, item) => sum + item.duration, 0);
      return total / performanceData.length;
    },
  };
};

/**
 * Função para configurar interceptors globais
 */
export const setupGlobalInterceptors = () => {
  // Interceptor para adicionar timestamp em todas as requisições
  const originalFetch = window.fetch;
  
  window.fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = typeof input === 'string' ? input : input.toString();
    
    // Adicionar timestamp se for requisição para nossa API
    if (url.includes(API_CONFIG.BASE_URL)) {
      const headers = new Headers(init?.headers);
      headers.set('X-Request-Timestamp', Date.now().toString());
      
      init = {
        ...init,
        headers,
      };
    }
    
    return originalFetch(input, init);
  };
};

// Configurar interceptors na inicialização
setupGlobalInterceptors();