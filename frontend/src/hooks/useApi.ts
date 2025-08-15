import { useState, useEffect, useCallback, useRef } from 'react';

/**
 * Opcoes para configurar o comportamento do hook useApi
 */
export interface UseApiOptions {
  /** Se deve executar automaticamente ao montar o componente */
  autoExecute?: boolean;
  /** Dependencias que, quando alteradas, reexecutam a funcao */
  dependencies?: any[];
  /** Callback executado quando a requisicao e bem-sucedida */
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
  /** Indica se ha uma requisicao em andamento */
  loading: boolean;
  /** Mensagem de erro, se houver */
  error: string | null;
  /** Funcao para executar a requisicao manualmente */
  execute: (...args: any[]) => Promise<void>;
  /** Funcao para resetar o estado */
  reset: () => void;
}

/**
 * Hook personalizado para gerenciar chamadas de API
 * 
 * @param apiFunction - Funcao da API a ser executada
 * @param options - Opcoes de configuracao
 * @returns Estado e funcoes para gerenciar a API
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
 * // Auto-executar com dependencias
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
  
  // Ref para controlar cancelamento de requisicoes
  const cancelRef = useRef<boolean>(false);
  const executionCountRef = useRef(0);

  /**
   * Executa a funcao da API
   */
  const execute = useCallback(async (...args: any[]) => {
    // Incrementar contador de execucao para cancelar requisicoes anteriores
    const currentExecution = ++executionCountRef.current;
    cancelRef.current = false;

    setLoading(true);
    setError(null);

    try {
      const result = await apiFunction(...args);
      
      // Verificar se esta execucao ainda e valida
      if (currentExecution === executionCountRef.current && !cancelRef.current) {
        setData(result);
        onSuccess?.(result);
      }
    } catch (err) {
      // Verificar se esta execucao ainda e valida
      if (currentExecution === executionCountRef.current && !cancelRef.current) {
        const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido';
        setError(errorMessage);
        onError?.(errorMessage);
      }
    } finally {
      // Verificar se esta execucao ainda e valida
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

  // Auto-executar quando as dependencias mudarem
  useEffect(() => {
    if (autoExecute) {
      execute();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [autoExecute, ...dependencies]);

  // Cancelar requisicoes pendentes quando o componente for desmontado
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
 * Hook especializado para metricas do dashboard
 */
export function useMetrics(options?: UseApiOptions) {
  // Importacao dinamica para evitar problemas de dependencia circular
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
 * Hook especializado para ranking de tecnicos
 */
export function useTechnicianRanking(options?: UseApiOptions) {
  const apiFunction = async (...args: any[]) => {
    const { apiService } = await import('../services/api');
    return apiService.getTechnicianRanking(...args);
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