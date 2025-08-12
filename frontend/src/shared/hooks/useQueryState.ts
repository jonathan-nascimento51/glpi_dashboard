import { useQuery, UseQueryOptions, UseQueryResult } from '@tanstack/react-query';
import { 
  ComponentState, 
  createInitialState, 
  createLoadingState, 
  createErrorState, 
  createEmptyState, 
  createSuccessState 
} from '../types/states';

/**
 * Hook que combina React Query com estados padronizados
 * Simplifica o uso de queries e garante consistência nos estados
 */
export function useQueryState<TData = unknown, TError = Error>(
  options: UseQueryOptions<TData, TError>
): ComponentState<TData> & {
  queryResult: UseQueryResult<TData, TError>;
  refetch: () => void;
} {
  const queryResult = useQuery(options);
  
  const {
    data,
    error,
    isLoading,
    isPending,
    isRefetching,
    isError,
    refetch,
  } = queryResult;

  // Determinar estado baseado no resultado da query
  let state: ComponentState<TData>;

  if (isLoading || isPending) {
    state = createLoadingState(data);
    state.isPending = isPending;
    state.isRefetching = isRefetching;
  } else if (isError && error) {
    state = createErrorState(error as Error, data);
  } else if (!data || (Array.isArray(data) && data.length === 0)) {
    state = createEmptyState();
  } else {
    state = createSuccessState(data);
  }

  return {
    ...state,
    queryResult,
    refetch: () => refetch(),
  };
}

/**
 * Hook específico para dados de dashboard com configurações otimizadas
 */
export function useDashboardQuery<TData = unknown>(
  queryKey: readonly unknown[],
  queryFn: () => Promise<TData>,
  options?: Partial<UseQueryOptions<TData, Error>>
) {
  return useQueryState({
    queryKey,
    queryFn,
    staleTime: 5 * 60 * 1000, // 5 minutos
    gcTime: 10 * 60 * 1000, // 10 minutos
    refetchOnWindowFocus: false,
    retry: 3,
    ...options,
  });
}

/**
 * Hook para dados em tempo real com refetch automático
 */
export function useRealTimeQuery<TData = unknown>(
  queryKey: readonly unknown[],
  queryFn: () => Promise<TData>,
  options?: Partial<UseQueryOptions<TData, Error>>
) {
  return useQueryState({
    queryKey,
    queryFn,
    staleTime: 30 * 1000, // 30 segundos
    gcTime: 2 * 60 * 1000, // 2 minutos
    refetchInterval: 60 * 1000, // Refetch a cada minuto
    refetchOnWindowFocus: true,
    retry: 2,
    ...options,
  });
}

/**
 * Hook para dados estáticos que mudam raramente
 */
export function useStaticQuery<TData = unknown>(
  queryKey: readonly unknown[],
  queryFn: () => Promise<TData>,
  options?: Partial<UseQueryOptions<TData, Error>>
) {
  return useQueryState({
    queryKey,
    queryFn,
    staleTime: 30 * 60 * 1000, // 30 minutos
    gcTime: 60 * 60 * 1000, // 1 hora
    refetchOnWindowFocus: false,
    refetchOnMount: false,
    retry: 1,
    ...options,
  });
}

/**
 * Hook para queries com paginação
 */
export function usePaginatedQuery<TData = unknown>(
  queryKey: readonly unknown[],
  queryFn: () => Promise<TData>,
  options?: Partial<UseQueryOptions<TData, Error>>
) {
  return useQueryState({
    queryKey,
    queryFn,
    staleTime: 2 * 60 * 1000, // 2 minutos
    gcTime: 5 * 60 * 1000, // 5 minutos
    refetchOnWindowFocus: false,
    retry: 2,
    keepPreviousData: true, // Mantém dados anteriores durante loading
    ...options,
  });
}

/**
 * Utilitários para trabalhar com estados
 */
export const queryStateUtils = {
  /**
   * Verifica se deve mostrar skeleton/loading
   */
  shouldShowLoading: (state: ComponentState) => {
    return state.isLoading && !state.hasData;
  },

  /**
   * Verifica se deve mostrar estado de erro
   */
  shouldShowError: (state: ComponentState) => {
    return state.isError && !state.hasData;
  },

  /**
   * Verifica se deve mostrar estado vazio
   */
  shouldShowEmpty: (state: ComponentState) => {
    return state.isEmpty && !state.isLoading && !state.isError;
  },

  /**
   * Verifica se deve mostrar dados
   */
  shouldShowData: (state: ComponentState) => {
    return state.hasData && !state.isEmpty;
  },

  /**
   * Verifica se está fazendo refetch (para mostrar indicador)
   */
  isRefetching: (state: ComponentState) => {
    return state.isRefetching && state.hasData;
  },
};