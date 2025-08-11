import { validateMetricsData, validateTechnicianRanking, validateSystemStatus } from '../types/validation';
import type { MetricsData, TechnicianRanking, SystemStatus } from '../types';

// Middleware para validação de dados da API
export class ApiValidationMiddleware {
  static validateApiResponse<T>(
    data: unknown,
    validator: (data: unknown) => T,
    fallback: T,
    endpoint: string
  ): T {
    try {
      const validatedData = validator(data);
      console.log(` Validation successful for ${endpoint}`);
      return validatedData;
    } catch (error) {
      console.error(` Validation failed for ${endpoint}:`, error);
      console.warn(` Using fallback data for ${endpoint}`);
      
      // Log para monitoramento
      this.logValidationError(endpoint, error, data);
      
      return fallback;
    }
  }

  static validateMetrics(data: unknown): MetricsData {
    return this.validateApiResponse(
      data,
      validateMetricsData,
      this.getMetricsFallback(),
      '/v1/kpis'
    );
  }

  static validateRanking(data: unknown): TechnicianRanking[] {
    return this.validateApiResponse(
      data,
      validateTechnicianRanking,
      [],
      '/v1/ranking'
    );
  }

  static validateStatus(data: unknown): SystemStatus {
    return this.validateApiResponse(
      data,
      validateSystemStatus,
      this.getStatusFallback(),
      '/v1/status'
    );
  }

  private static getMetricsFallback(): MetricsData {
    return {
      success: false,
      message: 'Fallback data - API validation failed',
      timestamp: new Date().toISOString(),
      tempo_execucao: 0,
      niveis: {
        N1: { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0, tendencia_novos: 0, tendencia_progresso: 0, tendencia_pendentes: 0, tendencia_resolvidos: 0 },
        N2: { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0, tendencia_novos: 0, tendencia_progresso: 0, tendencia_pendentes: 0, tendencia_resolvidos: 0 },
        N3: { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0, tendencia_novos: 0, tendencia_progresso: 0, tendencia_pendentes: 0, tendencia_resolvidos: 0 },
        N4: { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0, tendencia_novos: 0, tendencia_progresso: 0, tendencia_pendentes: 0, tendencia_resolvidos: 0 },
      },
    };
  }

  private static getStatusFallback(): SystemStatus {
    return {
      api_status: 'unknown',
      database_status: 'unknown',
      glpi_connection: false,
      ultima_atualizacao: new Date().toISOString(),
    };
  }

  private static logValidationError(endpoint: string, error: unknown, data: unknown): void {
    // Log estruturado para monitoramento
    const errorLog = {
      timestamp: new Date().toISOString(),
      level: 'ERROR',
      category: 'API_VALIDATION',
      endpoint,
      error: error instanceof Error ? error.message : String(error),
      receivedData: data,
      userAgent: navigator.userAgent,
      url: window.location.href,
    };

    console.error('API Validation Error:', errorLog);
    
    // Enviar para sistema de monitoramento (Sentry, etc.)
    if (window.Sentry) {
      window.Sentry.captureException(new Error(`API Validation Failed: ${endpoint}`), {
        tags: {
          category: 'api_validation',
          endpoint,
        },
        extra: errorLog,
      });
    }
  }
}

// Hook personalizado para validação de dados
export const useValidatedApiData = () => {
  const validateAndLog = <T>(
    data: unknown,
    validator: (data: unknown) => T,
    fallback: T,
    source: string
  ): T => {
    return ApiValidationMiddleware.validateApiResponse(data, validator, fallback, source);
  };

  return {
    validateMetrics: (data: unknown) => ApiValidationMiddleware.validateMetrics(data),
    validateRanking: (data: unknown) => ApiValidationMiddleware.validateRanking(data),
    validateStatus: (data: unknown) => ApiValidationMiddleware.validateStatus(data),
    validateAndLog,
  };
};

// Interceptor para fetch requests
export const createValidatedFetch = () => {
  const originalFetch = window.fetch;
  
  window.fetch = async (...args) => {
    try {
      const response = await originalFetch(...args);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      // Clone response para poder ler o body múltiplas vezes
      const clonedResponse = response.clone();
      
      try {
        const data = await clonedResponse.json();
        
        // Log de sucesso
        console.log(` API Request successful:`, {
          url: args[0],
          status: response.status,
          timestamp: new Date().toISOString(),
        });
        
        return response;
      } catch (jsonError) {
        console.warn('Response is not valid JSON:', jsonError);
        return response;
      }
    } catch (error) {
      // Log de erro
      console.error(` API Request failed:`, {
        url: args[0],
        error: error instanceof Error ? error.message : String(error),
        timestamp: new Date().toISOString(),
      });
      
      throw error;
    }
  };
};

// Inicializar interceptor
if (typeof window !== 'undefined') {
  createValidatedFetch();
}
