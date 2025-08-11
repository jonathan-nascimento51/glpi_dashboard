// Sistema de validação de API para evitar problemas recorrentes
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

// Lista de endpoints críticos que devem sempre funcionar
const CRITICAL_ENDPOINTS = [
  '/v1/kpis',
  '/v1/system/status',
  '/v1/technicians/ranking',
  '/v1/tickets/new?limit=5'
];

/**
 * Valida se um endpoint específico está funcionando
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
 * Executa health check completo de todos os endpoints críticos
 */
export async function performHealthCheck(): Promise<HealthCheckResult> {
  console.log('🏥 Iniciando health check dos endpoints críticos...');
  
  const results: ValidationResult[] = [];
  
  for (const endpoint of CRITICAL_ENDPOINTS) {
    const result = await validateEndpoint(endpoint);
    results.push(result);
    
    if (result.success) {
      console.log(`✅ ${endpoint} - OK (${result.responseTime?.toFixed(0)}ms)`);
    } else {
      console.error(`❌ ${endpoint} - FALHOU: ${result.error}`);
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
    console.log('🎉 Health check passou! Todos os endpoints estão funcionando.');
  } else {
    console.error('⚠️ Health check falhou! Alguns endpoints apresentaram problemas.');
  }
  
  return healthCheck;
}

/**
 * Valida se a configuração da API está correta
 */
export function validateApiConfiguration(): boolean {
  const issues: string[] = [];
  
  // Verificar se o baseURL está correto
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
    issues.push('Header Content-Type não está configurado para application/json');
  }
  
  if (issues.length > 0) {
    console.error('❌ Problemas na configuração da API:');
    issues.forEach(issue => console.error(`  - ${issue}`));
    return false;
  }
  
  console.log('✅ Configuração da API está correta');
  return true;
}

/**
 * Sistema de monitoramento contínuo
 */
export class ApiMonitor {
  private intervalId: NodeJS.Timeout | null = null;
  private lastHealthCheck: HealthCheckResult | null = null;
  
  /**
   * Inicia monitoramento contínuo
   */
  startMonitoring(intervalMs: number = 60000): void {
    if (this.intervalId) {
      console.warn('⚠️ Monitoramento já está ativo');
      return;
    }
    
    console.log(`🔄 Iniciando monitoramento contínuo (intervalo: ${intervalMs}ms)`);
    
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
        console.error('❌ Erro durante health check automático:', error);
      }
    }, intervalMs);
  }
  
  /**
   * Para o monitoramento contínuo
   */
  stopMonitoring(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
      console.log('🛑 Monitoramento parado');
    }
  }
  
  /**
   * Retorna o último resultado do health check
   */
  getLastHealthCheck(): HealthCheckResult | null {
    return this.lastHealthCheck;
  }
}

// Instância global do monitor
export const apiMonitor = new ApiMonitor();

/**
 * Função de inicialização que deve ser chamada no início da aplicação
 */
export async function initializeApiValidation(): Promise<boolean> {
  console.log('🚀 Inicializando sistema de validação da API...');
  
  // 1. Validar configuração
  const configValid = validateApiConfiguration();
  if (!configValid) {
    return false;
  }
  
  // 2. Executar health check inicial
  const healthCheck = await performHealthCheck();
  if (!healthCheck.overall) {
    console.error('❌ Health check inicial falhou. Verifique a conectividade com a API.');
    return false;
  }
  
  // 3. Iniciar monitoramento (opcional)
  if (process.env.NODE_ENV === 'development') {
    apiMonitor.startMonitoring(30000); // 30 segundos em desenvolvimento
  }
  
  console.log('✅ Sistema de validação da API inicializado com sucesso');
  return true;
}

/**
 * Hook para React que pode ser usado para monitorar a saúde da API
 */
export function useApiHealth() {
  // Este hook será implementado quando React estiver disponível
  // Por enquanto, retornamos uma implementação básica
  return {
    isHealthy: true,
    lastCheck: null as HealthCheckResult | null,
    checkHealth: performHealthCheck
  };
}