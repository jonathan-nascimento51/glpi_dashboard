import { QueryClient } from '@tanstack/react-query';

/**
 * Configuração do React Query com políticas padronizadas
 * - staleTime: 5 minutos para dados do dashboard
 * - cacheTime: 10 minutos para manter dados em cache
 * - retry: 3 tentativas com backoff exponencial
 * - refetchOnWindowFocus: false para evitar refetch desnecessário
 */
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Dados ficam "fresh" por 5 minutos
      staleTime: 5 * 60 * 1000, // 5 minutos
      
      // Cache mantido por 10 minutos após componente ser desmontado
      gcTime: 10 * 60 * 1000, // 10 minutos (gcTime substitui cacheTime no v5)
      
      // Retry com backoff exponencial
      retry: (failureCount, error: any) => {
        // Não retry em erros 4xx (client errors)
        if (error?.response?.status >= 400 && error?.response?.status < 500) {
          return false;
        }
        // Máximo 3 tentativas
        return failureCount < 3;
      },
      
      // Delay entre retries (backoff exponencial)
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      
      // Não refetch automaticamente ao focar na janela
      refetchOnWindowFocus: false,
      
      // Refetch ao reconectar
      refetchOnReconnect: true,
      
      // Não refetch automaticamente ao montar
      refetchOnMount: true,
    },
    mutations: {
      // Retry mutations apenas 1 vez
      retry: 1,
      
      // Delay para mutations
      retryDelay: 1000,
    },
  },
});

/**
 * Query keys padronizados para organização
 */
export const queryKeys = {
  // Dashboard
  dashboard: {
    all: ['dashboard'] as const,
    metrics: (filters?: Record<string, any>) => ['dashboard', 'metrics', filters] as const,
    levels: (filters?: Record<string, any>) => ['dashboard', 'levels', filters] as const,
    ranking: (filters?: Record<string, any>) => ['dashboard', 'ranking', filters] as const,
  },
  
  // Tickets
  tickets: {
    all: ['tickets'] as const,
    list: (filters?: Record<string, any>) => ['tickets', 'list', filters] as const,
    detail: (id: string) => ['tickets', 'detail', id] as const,
    summary: (filters?: Record<string, any>) => ['tickets', 'summary', filters] as const,
  },
  
  // System
  system: {
    all: ['system'] as const,
    status: () => ['system', 'status'] as const,
    health: () => ['system', 'health'] as const,
  },
} as const;

/**
 * Utilitários para invalidação de cache
 */
export const invalidateQueries = {
  dashboard: () => queryClient.invalidateQueries({ queryKey: queryKeys.dashboard.all }),
  tickets: () => queryClient.invalidateQueries({ queryKey: queryKeys.tickets.all }),
  system: () => queryClient.invalidateQueries({ queryKey: queryKeys.system.all }),
  all: () => queryClient.invalidateQueries(),
};

/**
 * Configurações específicas por tipo de query
 */
export const queryConfigs = {
  // Dados críticos que precisam estar sempre atualizados
  realTime: {
    staleTime: 30 * 1000, // 30 segundos
    gcTime: 2 * 60 * 1000, // 2 minutos
    refetchInterval: 60 * 1000, // Refetch a cada minuto
  },
  
  // Dados que mudam pouco (configurações, listas estáticas)
  static: {
    staleTime: 30 * 60 * 1000, // 30 minutos
    gcTime: 60 * 60 * 1000, // 1 hora
    refetchOnMount: false,
  },
  
  // Dados do dashboard (padrão)
  dashboard: {
    staleTime: 5 * 60 * 1000, // 5 minutos
    gcTime: 10 * 60 * 1000, // 10 minutos
  },
};