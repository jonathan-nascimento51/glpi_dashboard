// Sistema de validaÃ§Ã£o de API para evitar problemas recorrentes
import { httpClient } from '../services/httpClient';

export interface ValidationResult {
  success: boolean;
  endpoint: string;
  error?: string;
  responseTime?: number;
}

export interface HealthCheckResult {
  overall: boolean;
  results: ValidationResult[];
  timestamp: string;
}

// Lista de endpoints crÃ­ticos que devem sempre funcionar
const CRITICAL_ENDPOINTS = [
  '/api/v1/kpis',
  '/api/v1/system/status',
  '/api/v1/technicians/ranking',
  '/api/v1/tickets/new?limit=5'
];

/**
 * Valida se um endpoint especÃ­fico estÃ¡ funcionando
 */
export async function validateEndpoint(endpoint: string): Promise<ValidationResult> {
  const startTime = performance.now();
  
  try {
    const response = await httpClient.get(endpoint, { timeout: 10000 });
    const responseTime = performance.now() - startTime;
    
    if (response.status === 200 && response.data?.success) {
      return {
        success: true,
        endpoint,
        responseTime
      };
    } else {
      return {
        success: false,
        endpoint,
        error: `Invalid response: status=${response.status}, success=${response.data?.success}`,
        responseTime
      };
    }
  } catch (error: any) {
    const responseTime = performance.now() - startTime;
    return {
      success: false,
      endpoint,
      error: error.message || 'Unknown error',
      responseTime
    };
  }
}

/**
 * Executa health check completo de todos os endpoints crÃ­ticos
 */
export async function performHealthCheck(): Promise<HealthCheckResult> {
  console.log('ðŸ¥ Iniciando health check dos endpoints crÃ­ticos...');
  
  const results: ValidationResult[] = [];
  
  for (const endpoint of CRITICAL_ENDPOINTS) {
    const result = await validateEndpoint(endpoint);
    results.push(result);
    
    if (result.success) {
      console.log(`âœ… ${endpoint} - OK (${result.responseTime?.toFixed(0)}ms)`);
    } else {
      console.error(`âŒ ${endpoint} - FALHOU: ${result.error}`);
    }
  }
  
  const overall = results.every(r => r.success);
  const timestamp = new Date().toISOString();
  
  const healthCheck: HealthCheckResult = {
    overall,
    results,
    timestamp
  };
  
  if (overall) {
    console.log('ðŸŽ‰ Health check passou! Todos os endpoints estÃ£o funcionando.');
  } else {
    console.error('âš ï¸ Health check falhou! Alguns endpoints apresentaram problemas.');
  }
  
  return healthCheck;
}

/**
 * Valida se a configuraÃ§Ã£o da API estÃ¡ correta
 */
export function validateApiConfiguration(): boolean {
  const issues: string[] = [];
  
  // Verificar se o baseURL estÃ¡ correto
  const baseURL = httpClient.defaults.baseURL;
  if (!baseURL || !baseURL.includes('/api')) {
    issues.push(`BaseURL incorreta: ${baseURL}. Deveria conter '/api'`);
  }
  
  // Verificar timeout
  const timeout = httpClient.defaults.timeout;
  if (!timeout || timeout < 10000) {
    issues.push(`Timeout muito baixo: ${timeout}ms. Recomendado: >= 10000ms`);
  }
  
  // Verificar headers
  const headers = httpClient.defaults.headers;
  const contentType = headers?.['Content-Type'];
  if (!contentType || (typeof contentType === 'string' && !contentType.includes('application/json'))) {
    issues.push('Header Content-Type nÃ£o estÃ¡ configurado para application/json');
  }
  
  if (issues.length > 0) {
    console.error('âŒ Problemas na configuraÃ§Ã£o da API:');
    issues.forEach(issue => console.error(`  - ${issue}`));
    return false;
  }
  
  console.log('âœ… ConfiguraÃ§Ã£o da API estÃ¡ correta');
  return true;
}

/**
 * Sistema de monitoramento contÃ­nuo
 */
export class ApiMonitor {
  private intervalId: NodeJS.Timeout | null = null;
  private lastHealthCheck: HealthCheckResult | null = null;
  
  /**
   * Inicia monitoramento contÃ­nuo
   */
  startMonitoring(intervalMs: number = 60000): void {
    if (this.intervalId) {
      console.warn('âš ï¸ Monitoramento jÃ¡ estÃ¡ ativo');
      return;
    }
    
    console.log(`ðŸ”„ Iniciando monitoramento contÃ­nuo (intervalo: ${intervalMs}ms)`);
    
    this.intervalId = setInterval(async () => {
      try {
        this.lastHealthCheck = await performHealthCheck();
        
        if (!this.lastHealthCheck.overall) {
          // Disparar evento para notificar problemas
          window.dispatchEvent(new CustomEvent('api-health-check-failed', {
            detail: this.lastHealthCheck
          }));
        }
      } catch (error) {
        console.error('âŒ Erro durante health check automÃ¡tico:', error);
      }
    }, intervalMs);
  }
  
  /**
   * Para o monitoramento contÃ­nuo
   */
  stopMonitoring(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
      console.log('ðŸ›‘ Monitoramento parado');
    }
  }
  
  /**
   * Retorna o Ãºltimo resultado do health check
   */
  getLastHealthCheck(): HealthCheckResult | null {
    return this.lastHealthCheck;
  }
}

// InstÃ¢ncia global do monitor
export const apiMonitor = new ApiMonitor();

/**
 * FunÃ§Ã£o de inicializaÃ§Ã£o que deve ser chamada no inÃ­cio da aplicaÃ§Ã£o
 */
export async function initializeApiValidation(): Promise<boolean> {
  console.log('ðŸš€ Inicializando sistema de validaÃ§Ã£o da API...');
  
  // 1. Validar configuraÃ§Ã£o
  const configValid = validateApiConfiguration();
  if (!configValid) {
    return false;
  }
  
  // 2. Executar health check inicial
  const healthCheck = await performHealthCheck();
  if (!healthCheck.overall) {
    console.error('âŒ Health check inicial falhou. Verifique a conectividade com a API.');
    return false;
  }
  
  // 3. Iniciar monitoramento (opcional)
  if (process.env.NODE_ENV === 'development') {
    apiMonitor.startMonitoring(30000); // 30 segundos em desenvolvimento
  }
  
  console.log('âœ… Sistema de validaÃ§Ã£o da API inicializado com sucesso');
  return true;
}

/**
 * Hook para React que pode ser usado para monitorar a saÃºde da API
 */
export function useApiHealth() {
  // Este hook serÃ¡ implementado quando React estiver disponÃ­vel
  // Por enquanto, retornamos uma implementaÃ§Ã£o bÃ¡sica
  return {
    isHealthy: true,
    lastCheck: null as HealthCheckResult | null,
    checkHealth: performHealthCheck
  };
}
