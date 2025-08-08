import axios, { AxiosResponse, AxiosError } from 'axios';
import { MetricsData, SystemStatus, DateRange } from '../types';
import type {
  ApiResult,
  DashboardMetrics,
  FilterParams,
  PerformanceMetrics
} from '../types/api';
import {
  isApiError,
  isApiResponse,
  transformLegacyData
} from '../types/api';
import { 
  metricsCache, 
  systemStatusCache, 
  technicianRankingCache, 
  newTicketsCache 
} from './cache';

// Tipos para melhor tipagem de erros
interface ApiErrorResponse {
  success: false;
  error: string;
  code?: string;
  details?: any;
}

interface RequestMetrics {
  startTime: number;
  endTime?: number;
  responseTime?: number;
  retryCount: number;
  endpoint: string;
  method: string;
}

// Configurações de retry
const RETRY_CONFIG = {
  maxRetries: 3,
  retryDelay: 1000, // 1 segundo
  retryMultiplier: 2,
  retryableStatuses: [408, 429, 500, 502, 503, 504]
};

// Função para delay entre retries
const delay = (ms: number): Promise<void> => 
  new Promise(resolve => setTimeout(resolve, ms));

// Função para validar resposta da API
const validateApiResponse = (data: any, endpoint: string): boolean => {
  if (!data) {
    console.warn(`[${endpoint}] Resposta vazia recebida`);
    return false;
  }
  
  if (typeof data !== 'object') {
    console.warn(`[${endpoint}] Resposta não é um objeto:`, typeof data);
    return false;
  }
  
  if (!('success' in data)) {
    console.warn(`[${endpoint}] Resposta não contém campo 'success'`);
    return false;
  }
  
  return true;
};

// Função para sanitizar dados de entrada
const sanitizeInput = (input: any): any => {
  if (typeof input === 'string') {
    return input.trim().replace(/[<>"'&]/g, '');
  }
  if (typeof input === 'object' && input !== null) {
    const sanitized: any = {};
    for (const [key, value] of Object.entries(input)) {
      sanitized[key] = sanitizeInput(value);
    }
    return sanitized;
  }
  return input;
};

// Função para categorizar erros
const categorizeError = (error: any): string => {
  if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
    return 'TIMEOUT';
  }
  if (error.code === 'NETWORK_ERROR' || error.message?.includes('Network Error')) {
    return 'NETWORK';
  }
  if (error.response?.status >= 500) {
    return 'SERVER_ERROR';
  }
  if (error.response?.status >= 400) {
    return 'CLIENT_ERROR';
  }
  return 'UNKNOWN';
};

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'User-Agent': 'GLPI-Dashboard/1.0'
  },
  validateStatus: (status) => status < 500, // Não rejeitar automaticamente para status 4xx
});

// Request interceptor com sanitização e logging
api.interceptors.request.use(
  (config) => {
    const requestId = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    config.metadata = { requestId, startTime: Date.now() };
    
    // Sanitizar dados de entrada
    if (config.data) {
      config.data = sanitizeInput(config.data);
    }
    
    if (config.params) {
      config.params = sanitizeInput(config.params);
    }
    
    console.log(`[${requestId}] 🚀 ${config.method?.toUpperCase()} ${config.url}`, {
      params: config.params,
      timeout: config.timeout
    });
    
    return config;
  },
  (error) => {
    console.error('❌ Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor com retry automático e validação
api.interceptors.response.use(
  (response: AxiosResponse) => {
    const requestId = response.config.metadata?.requestId || 'unknown';
    const startTime = response.config.metadata?.startTime || Date.now();
    const responseTime = Date.now() - startTime;
    
    console.log(`[${requestId}] ✅ ${response.status} ${response.config.url} (${responseTime}ms)`);
    
    // Validar estrutura da resposta
    if (!validateApiResponse(response.data, response.config.url || 'unknown')) {
      console.warn(`[${requestId}] ⚠️ Resposta com estrutura inválida`);
    }
    
    // Log de performance para requisições lentas
    if (responseTime > 5000) {
      console.warn(`[${requestId}] 🐌 Requisição lenta: ${responseTime}ms`);
    }
    
    return response;
  },
  async (error: AxiosError) => {
    const requestId = error.config?.metadata?.requestId || 'unknown';
    const startTime = error.config?.metadata?.startTime || Date.now();
    const responseTime = Date.now() - startTime;
    
    const errorCategory = categorizeError(error);
    const retryCount = error.config?.metadata?.retryCount || 0;
    
    const errorInfo = {
      requestId,
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      statusText: error.response?.statusText,
      message: error.message,
      code: error.code,
      category: errorCategory,
      responseTime,
      retryCount
    };
    
    console.error(`[${requestId}] ❌ ${errorCategory} Error:`, errorInfo);
    
    // Verificar se deve tentar novamente
    const shouldRetry = (
      retryCount < RETRY_CONFIG.maxRetries &&
      error.config &&
      (
        RETRY_CONFIG.retryableStatuses.includes(error.response?.status || 0) ||
        errorCategory === 'TIMEOUT' ||
        errorCategory === 'NETWORK'
      )
    );
    
    if (shouldRetry) {
      const delayTime = RETRY_CONFIG.retryDelay * Math.pow(RETRY_CONFIG.retryMultiplier, retryCount);
      
      console.log(`[${requestId}] 🔄 Tentativa ${retryCount + 1}/${RETRY_CONFIG.maxRetries} em ${delayTime}ms`);
      
      await delay(delayTime);
      
      // Atualizar metadata para próxima tentativa
      error.config.metadata = {
        ...error.config.metadata,
        retryCount: retryCount + 1,
        startTime: Date.now()
      };
      
      return api.request(error.config);
    }
    
    // Criar erro mais informativo
    const enhancedError = new Error(
      `${errorCategory}: ${error.message} (${retryCount} tentativas)`
    );
    enhancedError.name = 'ApiError';
    (enhancedError as any).originalError = error;
    (enhancedError as any).category = errorCategory;
    (enhancedError as any).requestId = requestId;
    
    return Promise.reject(enhancedError);
  }
);

// Adicionar tipos ao axios config
declare module 'axios' {
  interface AxiosRequestConfig {
    metadata?: {
      requestId: string;
      startTime: number;
      retryCount?: number;
    };
  }
}

// API Response wrapper interface
interface ApiResponse<T> {
  success: boolean;
  data: T;
  error?: string;
}

export const apiService = {
  // Get metrics data with optional date filter
  async getMetrics(dateRange?: DateRange): Promise<MetricsData> {
    const requestId = `metrics_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const startTime = Date.now();
    
    console.log(`[${requestId}] 🔄 Iniciando busca de métricas`, { dateRange });
    
    // Validar parâmetros de entrada
    if (dateRange) {
      if (dateRange.startDate && dateRange.endDate) {
        const start = new Date(dateRange.startDate);
        const end = new Date(dateRange.endDate);
        
        if (isNaN(start.getTime()) || isNaN(end.getTime())) {
          throw new Error('Datas inválidas fornecidas');
        }
        
        if (start > end) {
          throw new Error('Data inicial não pode ser posterior à data final');
        }
        
        // Verificar se o intervalo não é muito grande (máximo 2 anos)
        const diffTime = Math.abs(end.getTime() - start.getTime());
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        if (diffDays > 730) {
          throw new Error('Intervalo de datas não pode ser superior a 2 anos');
        }
      }
    }
    
    // Criar parâmetros para o cache
    const cacheParams = {
      endpoint: 'metrics',
      start_date: dateRange?.startDate || 'none',
      end_date: dateRange?.endDate || 'none'
    };

    // Verificar cache primeiro
    const cachedData = metricsCache.get(cacheParams);
    if (cachedData) {
      console.log(`[${requestId}] 📦 Dados encontrados no cache`);
      return cachedData;
    }

    try {
      let url = '/metrics';
      if (dateRange && dateRange.startDate && dateRange.endDate) {
        // Sanitizar parâmetros de data
        const sanitizedParams = {
          start_date: sanitizeInput(dateRange.startDate),
          end_date: sanitizeInput(dateRange.endDate)
        };
        
        const params = new URLSearchParams(sanitizedParams);
        url += `?${params.toString()}`;
      }
      
      console.log(`[${requestId}] 🌐 Fazendo requisição para: ${url}`);
      
      const response = await api.get(url);
      
      // Monitora performance
      const responseTime = Date.now() - startTime;
      const cacheKey = JSON.stringify(cacheParams);
      metricsCache.recordRequestTime(cacheKey, responseTime);
      
      console.log(`[${requestId}] ⚡ Resposta recebida em ${responseTime}ms`);
        
        // Validar resposta
        if (!response.data) {
          console.error(`[${requestId}] ❌ Resposta vazia recebida`);
          throw new Error('Resposta vazia do servidor');
        }
        
        if (!validateApiResponse(response.data, 'metrics')) {
          console.error(`[${requestId}] ❌ Estrutura de resposta inválida:`, response.data);
          throw new Error('Estrutura de resposta inválida');
        }
        
        if (response.data && response.data.success && response.data.data) {
          const rawData = response.data.data;
          
          console.log(`[${requestId}] 📊 Processando dados recebidos:`, rawData);
          
          // Verificar se há filtros aplicados (estrutura diferente)
          let processedData: { novos: number; pendentes: number; progresso: number; resolvidos: number; total: number };
          let processedNiveis: MetricsData['niveis'];
          
          if (rawData.general || rawData.by_level) {
            // Estrutura com filtros aplicados - grupos de manutenção
            processedNiveis = {
              'Manutenção Geral': { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0, total: 0 },
      'Patrimônio': { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0, total: 0 },
      'Atendimento': { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0, total: 0 },
      'Mecanografia': { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0, total: 0 }
            };

            // Processar dados da estrutura by_level
            if (rawData.by_level) {
              Object.entries(rawData.by_level).forEach(([level, data]: [string, any]) => {
                const levelKey = level.toLowerCase() as keyof typeof processedNiveis;
                if (processedNiveis[levelKey]) {
                  const novos = data['Novo'] || 0;
                  const progresso = (data['Processando (atribuído)'] || 0) + (data['Processando (planejado)'] || 0);
                  const pendentes = data['Pendente'] || 0;
                  const resolvidos = (data['Solucionado'] || 0) + (data['Fechado'] || 0);
                  processedNiveis[levelKey] = {
                    novos,
                    progresso,
                    pendentes,
                    resolvidos,
                    total: novos + progresso + pendentes + resolvidos
                  };
                }
              });
            }

            // Usar dados gerais se disponíveis, senão calcular dos níveis
            if (rawData.general) {
              const novos = rawData.general['Novo'] || 0;
              const pendentes = rawData.general['Pendente'] || 0;
              const progresso = (rawData.general['Processando (atribuído)'] || 0) + (rawData.general['Processando (planejado)'] || 0);
              const resolvidos = (rawData.general['Solucionado'] || 0) + (rawData.general['Fechado'] || 0);
              processedData = {
                novos,
                pendentes,
                progresso,
                resolvidos,
                total: novos + pendentes + progresso + resolvidos
              };
            } else {
              // Calcular totais dos níveis
              processedData = {
                novos: Object.values(processedNiveis).reduce((sum, nivel) => sum + nivel.novos, 0),
                pendentes: Object.values(processedNiveis).reduce((sum, nivel) => sum + nivel.pendentes, 0),
                progresso: Object.values(processedNiveis).reduce((sum, nivel) => sum + nivel.progresso, 0),
                resolvidos: Object.values(processedNiveis).reduce((sum, nivel) => sum + nivel.resolvidos, 0),
                total: 0
              };
            }

            processedData.total = processedData.novos + processedData.pendentes + processedData.progresso + processedData.resolvidos;
          } else {
            // Estrutura normal
            processedData = {
              novos: rawData.novos ?? 0,
              pendentes: rawData.pendentes ?? 0,
              progresso: rawData.progresso ?? 0,
              resolvidos: rawData.resolvidos ?? 0,
              total: rawData.total ?? 0
            };
            
            // Processar dados dos níveis
            if (rawData.niveis) {
              processedNiveis = rawData.niveis;
            } else if (rawData.levels) {
              // Caso os dados venham como 'levels' ao invés de 'niveis'
              processedNiveis = rawData.levels;
            } else {
              // Fallback com zeros - grupos de manutenção
              processedNiveis = {
                'Manutenção Geral': { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 },
                'Patrimônio': { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 },
                'Atendimento': { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 },
                'Mecanografia': { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 }
              };
            }
          }
          
          // Garantir que todos os campos necessários existam
          const data: MetricsData = {
            novos: processedData.novos,
            pendentes: processedData.pendentes,
            progresso: processedData.progresso,
            resolvidos: processedData.resolvidos,
            total: processedData.total,
            niveis: processedNiveis,
            tendencias: rawData.tendencias || {
              novos: '0',
              pendentes: '0',
              progresso: '0',
              resolvidos: '0'
            }
          };
          
          // Validar dados processados
          const requiredFields = ['novos', 'pendentes', 'progresso', 'resolvidos', 'total'];
          const missingFields = requiredFields.filter(field => typeof data[field] !== 'number');
          
          if (missingFields.length > 0) {
            console.warn(`[${requestId}] ⚠️ Campos ausentes ou inválidos:`, missingFields);
            // Corrigir campos ausentes
            missingFields.forEach(field => {
              data[field] = 0;
            });
          }
          
          // Verificar consistência dos totais
          const calculatedTotal = data.novos + data.pendentes + data.progresso + data.resolvidos;
          if (data.total !== calculatedTotal && calculatedTotal > 0) {
            console.warn(`[${requestId}] ⚠️ Inconsistência nos totais: declarado=${data.total}, calculado=${calculatedTotal}`);
            data.total = calculatedTotal; // Corrigir total
          }
          
          console.log(`[${requestId}] ✅ Dados validados e processados:`, data);
          
          // Armazenar no cache
          metricsCache.set(cacheParams, data);
          return data;
      } else {
        console.error(`[${requestId}] ❌ API retornou resposta sem sucesso:`, response.data);
        throw new Error(`API retornou erro: ${response.data?.error || 'Erro desconhecido'}`);
      }
    } catch (error: any) {
      const errorCategory = error.name === 'ApiError' ? error.category : categorizeError(error);
      
      console.error(`[${requestId}] ❌ Erro ao buscar métricas [${errorCategory}]:`, {
        message: error.message,
        category: errorCategory,
        requestId: error.requestId || requestId,
        stack: error.stack
      });
      
      // Criar dados de fallback
      const fallbackData: MetricsData = {
        novos: 0,
        pendentes: 0,
        progresso: 0,
        resolvidos: 0,
        total: 0,
        niveis: {
          'Manutenção Geral': { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 },
          'Patrimônio': { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 },
          'Atendimento': { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 },
          'Mecanografia': { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 }
        },
        tendencias: { novos: '0', pendentes: '0', progresso: '0', resolvidos: '0' }
      };
      
      // Decidir se deve retornar fallback ou propagar erro
      if (errorCategory === 'CLIENT_ERROR' && error.response?.status === 400) {
        // Para erros de validação, propagar o erro
        throw new Error(`Erro de validação: ${error.message}`);
      } else if (errorCategory === 'CLIENT_ERROR' && error.response?.status === 401) {
        // Para erros de autenticação, propagar o erro
        throw new Error('Erro de autenticação: Verifique suas credenciais');
      } else {
        // Para outros erros, retornar dados de fallback
        console.warn(`[${requestId}] 🔄 Retornando dados de fallback devido a erro ${errorCategory}`);
        return fallbackData;
      }
    }
  },

  // Get system status
  async getSystemStatus(): Promise<SystemStatus> {
    const startTime = Date.now();
    const cacheParams = { endpoint: 'status' };

    // Verificar cache primeiro
    const cachedData = systemStatusCache.get(cacheParams);
    if (cachedData) {
      return cachedData;
    }

    try {
      const response = await api.get<ApiResponse<SystemStatus>>('/status');
      
      // Monitora performance
      const responseTime = Date.now() - startTime;
      const cacheKey = JSON.stringify(cacheParams);
      systemStatusCache.recordRequestTime(cacheKey, responseTime);
      
      if (response.data.success && response.data.data) {
        const data = response.data.data;
        // Armazenar no cache
        systemStatusCache.set(cacheParams, data);
        return data;
      } else {
        console.error('API returned unsuccessful response:', response.data);
        // Return fallback data (não cachear)
        return {
          status: 'offline',
          sistema_ativo: false,
          ultima_atualizacao: ''
        };
      }
    } catch (error) {
      console.error('Error fetching system status:', error);
      // Return fallback data instead of throwing (não cachear)
      return {
        status: 'offline',
        sistema_ativo: false,
        ultima_atualizacao: ''
      };
    }
  },

  // Health check
  async healthCheck(): Promise<boolean> {
    try {
      await api.head('/status');
      return true;
    } catch (error) {
      console.error('Health check failed:', error);
      return false;
    }
  },

  // Get technician ranking
  async getTechnicianRanking(): Promise<any[]> {
    const startTime = Date.now();
    const cacheParams = { endpoint: 'technicians/ranking' };

    // Verificar cache primeiro
    const cachedData = technicianRankingCache.get(cacheParams);
    if (cachedData) {
      return cachedData;
    }

    try {
      const response = await api.get<ApiResponse<any[]>>('/technicians/ranking');
      
      // Monitora performance
      const responseTime = Date.now() - startTime;
      const cacheKey = JSON.stringify(cacheParams);
      technicianRankingCache.recordRequestTime(cacheKey, responseTime);
      
      if (response.data.success && response.data.data) {
        const data = response.data.data;
        // Armazenar no cache
        technicianRankingCache.set(cacheParams, data);
        return data;
      } else {
        console.error('API returned unsuccessful response:', response.data);
        return [];
      }
    } catch (error) {
      console.error('Error fetching technician ranking:', error);
      return [];
    }
  },

  // Get new tickets
  async getNewTickets(limit: number = 5): Promise<any[]> {
    const startTime = Date.now();
    const cacheParams = { endpoint: 'tickets/new', limit: limit.toString() };

    // Verificar cache primeiro
    const cachedData = newTicketsCache.get(cacheParams);
    if (cachedData) {
      console.log('📦 Retornando dados do cache para novos tickets');
      return cachedData;
    }

    try {
      const response = await api.get<ApiResponse<any[]>>(`/tickets/new?limit=${limit}`);
      
      // Monitora performance
      const responseTime = Date.now() - startTime;
      const cacheKey = JSON.stringify(cacheParams);
      newTicketsCache.recordRequestTime(cacheKey, responseTime);
      
      if (response.data.success && response.data.data) {
        const data = response.data.data;
        // Armazenar no cache
        newTicketsCache.set(cacheParams, data);
        return data;
      } else {
        console.error('API returned unsuccessful response:', response.data);
        // Return mock data as fallback (não cachear)
        return [
          {
            id: '12345',
            title: 'Problema com impressora',
            requester: 'João Silva',
            date: new Date().toISOString(),
            priority: 'Alta'
          },
          {
            id: '12346',
            title: 'Erro no sistema',
            requester: 'Maria Santos',
            date: new Date(Date.now() - 3600000).toISOString(),
            priority: 'Média'
          },
          {
            id: '12347',
            title: 'Solicitação de acesso',
            requester: 'Pedro Costa',
            date: new Date(Date.now() - 7200000).toISOString(),
            priority: 'Baixa'
          }
        ];
      }
    } catch (error) {
      console.error('Error fetching new tickets:', error);
      // Return mock data instead of throwing error (não cachear)
      return [
        {
          id: '12345',
          title: 'Problema com impressora',
          requester: 'João Silva',
          date: new Date().toISOString(),
          priority: 'Alta'
        },
        {
          id: '12346',
          title: 'Erro no sistema',
          requester: 'Maria Santos',
          date: new Date(Date.now() - 3600000).toISOString(),
          priority: 'Média'
        },
        {
          id: '12347',
          title: 'Solicitação de acesso',
          requester: 'Pedro Costa',
          date: new Date(Date.now() - 7200000).toISOString(),
          priority: 'Baixa'
        }
      ];
    }
  },

  // Search functionality (mock implementation)
  async search(query: string): Promise<any[]> {
    const startTime = Date.now();
    const cacheParams = { endpoint: 'search', query };

    // Verificar cache primeiro
    const cachedData = metricsCache.get(cacheParams);
    if (cachedData) {
      console.log('📦 Retornando dados do cache para busca');
      return cachedData;
    }

    try {
      // This would be a real API call in production
      // For now, return mock data based on query
      const mockResults = [
        {
          id: '1',
          type: 'ticket',
          title: `Chamado relacionado a: ${query}`,
          description: 'Descrição do chamado...',
          status: 'new'
        },
        {
          id: '2',
          type: 'technician',
          title: `Técnico: ${query}`,
          description: 'Informações do técnico...',
        }
      ];
      
      const data = mockResults.filter(result => 
        result.title.toLowerCase().includes(query.toLowerCase())
      );
      
      // Monitora performance
      const responseTime = Date.now() - startTime;
      const cacheKey = JSON.stringify(cacheParams);
      metricsCache.recordRequestTime(cacheKey, responseTime);
      
      // Armazenar no cache
      metricsCache.set(cacheParams, data);
      return data;
    } catch (error) {
      console.error('Error searching:', error);
      throw new Error('Falha na busca');
    }
  },

  // Clear all caches
  clearAllCaches(): void {
    console.log('🧹 Limpando todos os caches...');
    metricsCache.clear();
    systemStatusCache.clear();
    technicianRankingCache.clear();
    newTicketsCache.clear();
    console.log('✅ Todos os caches foram limpos');
  },
};

export default api;

// Named exports for individual functions
export const getMetrics = apiService.getMetrics;
export const getSystemStatus = apiService.getSystemStatus;
export const getTechnicianRanking = apiService.getTechnicianRanking;
export const getNewTickets = apiService.getNewTickets;
export const search = apiService.search;
export const healthCheck = apiService.healthCheck;
export const clearAllCaches = apiService.clearAllCaches;

// Função para buscar métricas do dashboard com tipagem forte
export const fetchDashboardMetrics = async (
  filters: FilterParams = {}
): Promise<DashboardMetrics | null> => {
  const requestId = `dashboard_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  let retryCount = 0;
  
  console.log(`[${requestId}] 🔄 Iniciando busca de métricas do dashboard`, { filters });
  
  // Função interna para fazer a requisição com retry
  const makeRequest = async (): Promise<DashboardMetrics | null> => {
    try {
      const queryParams = new URLSearchParams();
      
      // Mapear filtros para os nomes esperados pela API
      const filterMapping: Record<string, string> = {
        startDate: 'start_date',
        endDate: 'end_date',
        status: 'status',
        priority: 'priority',
        level: 'level'
      };
      
      // Validar e processar dateRange se presente
      if (filters.dateRange && filters.dateRange.startDate && filters.dateRange.endDate) {
        const start = new Date(filters.dateRange.startDate);
        const end = new Date(filters.dateRange.endDate);
        
        if (isNaN(start.getTime()) || isNaN(end.getTime())) {
          throw new Error('Datas inválidas nos filtros');
        }
        
        if (start > end) {
          throw new Error('Data inicial não pode ser posterior à data final');
        }
        
        console.log(`[${requestId}] 📅 Processando dateRange:`, filters.dateRange);
        queryParams.append('start_date', sanitizeInput(filters.dateRange.startDate));
        queryParams.append('end_date', sanitizeInput(filters.dateRange.endDate));
      } else if (filters.dateRange) {
        console.warn(`[${requestId}] ⚠️ dateRange incompleto:`, filters.dateRange);
      }
      
      // Adicionar filtros como parâmetros de query com validação de tipos
      Object.entries(filters).forEach(([key, value]) => {
        if (key === 'dateRange') return; // Já processado acima
        if (value !== null && value !== undefined && value !== '') {
          const apiKey = filterMapping[key] || key;
          const sanitizedValue = sanitizeInput(value.toString());
          queryParams.append(apiKey, sanitizedValue);
        }
      });
      
      const url = queryParams.toString() 
        ? `${API_BASE_URL}/metrics?${queryParams.toString()}`
        : `${API_BASE_URL}/metrics`;
      
      console.log(`[${requestId}] 🔍 URL construída:`, url);
      console.log(`[${requestId}] 🔍 Tentativa ${retryCount + 1}/${RETRY_CONFIG.maxRetries + 1}`);
      
      const startTime = performance.now();
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000);
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'User-Agent': 'GLPI-Dashboard/1.0'
        },
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      const endTime = performance.now();
      const responseTime = endTime - startTime;
      
      console.log(`[${requestId}] ⚡ Resposta recebida: ${response.status} (${responseTime.toFixed(2)}ms)`);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error(`[${requestId}] ❌ HTTP Error ${response.status}:`, errorText);
        
        // Verificar se deve tentar novamente
        if (RETRY_CONFIG.retryableStatuses.includes(response.status) && retryCount < RETRY_CONFIG.maxRetries) {
          const delayTime = RETRY_CONFIG.retryDelay * Math.pow(RETRY_CONFIG.retryMultiplier, retryCount);
          console.log(`[${requestId}] 🔄 Tentando novamente em ${delayTime}ms`);
          
          await delay(delayTime);
          retryCount++;
          return makeRequest();
        }
        
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const result: ApiResult<DashboardMetrics> = await response.json();
      
      // Validar estrutura da resposta
      if (!validateApiResponse(result, 'dashboard-metrics')) {
        throw new Error('Estrutura de resposta inválida');
      }
      
      console.log(`[${requestId}] 📊 Dados recebidos:`, result);
      
      // Log de performance
      const perfMetrics: PerformanceMetrics = {
        responseTime,
        cacheHit: false,
        timestamp: new Date(),
        endpoint: '/metrics'
      };
      
      if (responseTime > 5000) {
        console.warn(`[${requestId}] 🐌 Requisição lenta: ${responseTime.toFixed(2)}ms`);
      }
      
      // Verificar se a resposta é um erro
      if (isApiError(result)) {
        console.error(`[${requestId}] ❌ API retornou erro:`, result.error);
        throw new Error(`API Error: ${result.error}`);
      }
      
      // Verificar se é uma resposta de sucesso
      if (isApiResponse(result)) {
        // Processar dados para garantir estrutura consistente
        const processedData = transformLegacyData(result.data);
        
        // Validar dados processados
        if (!processedData || typeof processedData !== 'object') {
          throw new Error('Dados processados são inválidos');
        }
        
        console.log(`[${requestId}] ✅ Dados processados e validados:`, processedData);
        return processedData;
      }
      
      console.error(`[${requestId}] ❌ Resposta em formato inesperado:`, result);
      throw new Error('Formato de resposta inesperado');
      
    } catch (error: any) {
      const errorCategory = categorizeError(error);
      
      console.error(`[${requestId}] ❌ Erro na tentativa ${retryCount + 1} [${errorCategory}]:`, {
        message: error.message,
        category: errorCategory,
        stack: error.stack
      });
      
      // Verificar se deve tentar novamente
      const shouldRetry = (
        retryCount < RETRY_CONFIG.maxRetries &&
        (errorCategory === 'TIMEOUT' || errorCategory === 'NETWORK' || errorCategory === 'SERVER_ERROR')
      );
      
      if (shouldRetry) {
        const delayTime = RETRY_CONFIG.retryDelay * Math.pow(RETRY_CONFIG.retryMultiplier, retryCount);
        console.log(`[${requestId}] 🔄 Tentando novamente em ${delayTime}ms`);
        
        await delay(delayTime);
        retryCount++;
        return makeRequest();
      }
      
      // Se não deve tentar novamente, propagar o erro
      throw error;
    }
  };
  
  try {
    return await makeRequest();
  } catch (error: any) {
    console.error(`[${requestId}] ❌ Falha final após ${retryCount + 1} tentativas:`, error.message);
    return null;
  }
};