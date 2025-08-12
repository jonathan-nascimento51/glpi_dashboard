import { useState, useEffect, useCallback, useRef } from 'react';

/**
 * Opções para configurar o comportamento do hook useApi
 */
export interface UseApiOptions {
  /** Se deve executar automaticamente ao montar o componente */
  autoExecute?: boolean;
  /** Dependências que, quando alteradas, reexecutam a função */
  dependencies?: any[];
  /** Callback executado quando a requisição é bem-sucedida */
  onSuccess?: (data: any) => void;
  /** Callback executado quando ocorre um erro */
  onError?: (error: string) => void;
}

/**
 * Estado retornado pelo hook useApi
 */
export interface UseApiState<T> {
  /** Dados retornados pela API */
  data: T | null;
  /** Indica se há uma requisição em andamento */
  loading: boolean;
  /** Mensagem de erro, se houver */
  error: string | null;
  /** Função para executar a requisição manualmente */
  execute: (...args: any[]) => Promise<void>;
  /** Função para resetar o estado */
  reset: () => void;
}

/**
 * Hook personalizado para gerenciar chamadas de API
 * 
 * @param apiFunction - Função da API a ser executada
 * @param options - Opções de configuração
 * @returns Estado e funções para gerenciar a API
 * 
 * @example
 * ```tsx
 * const { data, loading, error, execute } = useApi(apiService.getMetrics);
 * 
 * // Executar manualmente
 * const handleClick = () => {
 *   execute({ startDate: '2024-01-01', endDate: '2024-01-31' });
 * };
 * 
 * // Auto-executar com dependências
 * const { data } = useApi(apiService.getMetrics, {
 *   autoExecute: true,
 *   dependencies: [dateRange]
 * });
 * ```
 */
export function useApi<T = any>(
  apiFunction: (...args: any[]) => Promise<T>,
  options: UseApiOptions = {}
): UseApiState<T> {
  const {
    autoExecute = false,
    dependencies = [],
    onSuccess,
    onError
  } = options;

  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Ref para controlar cancelamento de requisições
  const cancelRef = useRef<boolean>(false);
  const executionCountRef = useRef(0);

  /**
   * Executa a função da API
   */
  const execute = useCallback(async (...args: any[]) => {
    // Incrementar contador de execução para cancelar requisições anteriores
    const currentExecution = ++executionCountRef.current;
    cancelRef.current = false;

    setLoading(true);
    setError(null);

    try {
      const result = await apiFunction(...args);
      
      // Verificar se esta execução ainda é válida
      if (currentExecution === executionCountRef.current && !cancelRef.current) {
        setData(result);
        onSuccess?.(result);
      }
    } catch (err) {
      // Verificar se esta execução ainda é válida
      if (currentExecution === executionCountRef.current && !cancelRef.current) {
        const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido';
        setError(errorMessage);
        onError?.(errorMessage);
      }
    } finally {
      // Verificar se esta execução ainda é válida
      if (currentExecution === executionCountRef.current && !cancelRef.current) {
        setLoading(false);
      }
    }
  }, [apiFunction, onSuccess, onError]);

  /**
   * Reseta o estado para os valores iniciais
   */
  const reset = useCallback(() => {
    cancelRef.current = true;
    setData(null);
    setLoading(false);
    setError(null);
  }, []);

  // Auto-executar quando as dependências mudarem
  useEffect(() => {
    if (autoExecute) {
      execute();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [autoExecute, ...dependencies]);

  // Cancelar requisições pendentes quando o componente for desmontado
  useEffect(() => {
    return () => {
      cancelRef.current = true;
    };
  }, []);

  return {
    data,
    loading,
    error,
    execute,
    reset
  };
}

/**
 * Hook especializado para métricas do dashboard
 */
export function useMetrics(options?: UseApiOptions) {
  // Importação dinâmica para evitar problemas de dependência circular
  const apiFunction = async (...args: any[]) => {
    const { apiService } = await import('../services/api');
    return apiService.getMetrics(...args);
  };
  return useApi(apiFunction, options);
}

/**
 * Hook especializado para status do sistema
 */
export function useSystemStatus(options?: UseApiOptions) {
  const apiFunction = async (...args: any[]) => {
    const { apiService } = await import('../services/api');
    return apiService.getSystemStatus(...args);
  };
  return useApi(apiFunction, options);
}

/**
 * Hook especializado para ranking de técnicos
 */
export function useTechnicianRanking(filters?: {
  start_date?: string;
  end_date?: string;
  level?: string;
  limit?: number;
}, options?: UseApiOptions) {
  const apiFunction = async () => {
    const { apiService } = await import('../services/api');
    return apiService.getTechnicianRanking(filters);
  };
  return useApi(apiFunction, options);
}

/**
 * Hook especializado para novos tickets
 */
export function useNewTickets(options?: UseApiOptions) {
  const apiFunction = async (...args: any[]) => {
    const { apiService } = await import('../services/api');
    return apiService.getNewTickets(...args);
  };
  return useApi(apiFunction, options);
}

export default useApi;