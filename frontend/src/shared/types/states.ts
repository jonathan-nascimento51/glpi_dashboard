/**
 * Estados padronizados para componentes
 * Garante consistência em loading, empty e error states
 */

export type LoadingState = {
  isLoading: boolean;
  isPending?: boolean;
  isRefetching?: boolean;
};

export type ErrorState = {
  error: Error | null;
  errorMessage?: string;
  errorCode?: string | number;
  isError: boolean;
};

export type EmptyState = {
  isEmpty: boolean;
  emptyMessage?: string;
  emptyAction?: {
    label: string;
    onClick: () => void;
  };
};

export type DataState<T = any> = {
  data: T | null;
  hasData: boolean;
};

/**
 * Estado combinado para componentes que lidam com dados
 */
export type ComponentState<T = any> = LoadingState & ErrorState & EmptyState & DataState<T>;

/**
 * Estados específicos para diferentes tipos de componentes
 */
export type CardState<T = any> = ComponentState<T> & {
  variant?: 'default' | 'compact' | 'detailed';
  showSkeleton?: boolean;
};

export type GridState<T = any> = ComponentState<T[]> & {
  columns?: number;
  gap?: 'sm' | 'md' | 'lg';
  showSkeleton?: boolean;
};

export type ListState<T = any> = ComponentState<T[]> & {
  pagination?: {
    page: number;
    pageSize: number;
    total: number;
    hasNextPage: boolean;
    hasPreviousPage: boolean;
  };
  sorting?: {
    field: string;
    direction: 'asc' | 'desc';
  };
  filtering?: Record<string, any>;
};

/**
 * Helpers para criar estados iniciais
 */
export const createInitialState = <T = any>(): ComponentState<T> => ({
  isLoading: false,
  isPending: false,
  isRefetching: false,
  error: null,
  isError: false,
  isEmpty: false,
  data: null,
  hasData: false,
});

export const createLoadingState = <T = any>(data?: T): ComponentState<T> => ({
  isLoading: true,
  isPending: false,
  isRefetching: false,
  error: null,
  isError: false,
  isEmpty: false,
  data: data || null,
  hasData: !!data,
});

export const createErrorState = <T = any>(error: Error, data?: T): ComponentState<T> => ({
  isLoading: false,
  isPending: false,
  isRefetching: false,
  error,
  errorMessage: error.message,
  isError: true,
  isEmpty: false,
  data: data || null,
  hasData: !!data,
});

export const createEmptyState = <T = any>(): ComponentState<T> => ({
  isLoading: false,
  isPending: false,
  isRefetching: false,
  error: null,
  isError: false,
  isEmpty: true,
  data: null,
  hasData: false,
});

export const createSuccessState = <T = any>(data: T): ComponentState<T> => ({
  isLoading: false,
  isPending: false,
  isRefetching: false,
  error: null,
  isError: false,
  isEmpty: !data || (Array.isArray(data) && data.length === 0),
  data,
  hasData: !!data,
});

/**
 * Type guards para verificar estados
 */
export const isLoadingState = (state: ComponentState): boolean => {
  return state.isLoading || state.isPending || state.isRefetching;
};

export const isErrorState = (state: ComponentState): boolean => {
  return state.isError && !!state.error;
};

export const isEmptyState = (state: ComponentState): boolean => {
  return state.isEmpty && !state.hasData;
};

export const isSuccessState = (state: ComponentState): boolean => {
  return !isLoadingState(state) && !isErrorState(state) && state.hasData;
};

/**
 * Mensagens padrão para estados
 */
export const defaultMessages = {
  loading: 'Carregando...',
  empty: 'Nenhum dado encontrado',
  error: 'Erro ao carregar dados',
  retry: 'Tentar novamente',
  refresh: 'Atualizar',
} as const;