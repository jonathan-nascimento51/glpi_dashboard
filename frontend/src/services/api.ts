import axios, { AxiosResponse } from 'axios';
import { SystemStatus, DateRange } from '../types';
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
import { RankingDebugger } from '../debug/rankingDebug';

const API_BASE_URL = 'http://localhost:5000/api';

// Configuração da instância do Axios com otimizações
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // Aumentado para 60 segundos para acomodar ranking lento
  headers: {
    'Cache-Control': 'public, max-age=30', // Cache HTTP de 30 segundos
    'Accept': 'application/json',
    'Content-Type': 'application/json'
  }
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    // Log mais detalhado do erro
    const errorInfo = {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      statusText: error.response?.statusText,
      message: error.message,
      code: error.code
    };
    
    if (error.code === 'ECONNABORTED') {
      console.warn('⏱️ Request timeout:', errorInfo.url);
    } else if (error.response?.status === 404) {
      console.warn('🔍 Endpoint not found:', errorInfo.url);
    } else if (error.response?.status >= 500) {
      console.error('🚨 Server error:', errorInfo);
    } else if (error.response?.status >= 400) {
      console.warn('⚠️ Client error:', errorInfo);
    } else {
      console.error('🔌 Network/Connection error:', errorInfo);
    }
    
    return Promise.reject(error);
  }
);

// API Response wrapper interface
interface ApiResponse<T> {
  success: boolean;
  data: T;
  error?: string;
}

export const apiService = {
  // Get metrics data with optional date filter
  async getMetrics(dateRange?: DateRange): Promise<import('../types/api').DashboardMetrics> {
    const startTime = Date.now();
    
    // Criar parâmetros para o cache
    const cacheParams = {
      endpoint: 'metrics',
      start_date: dateRange?.startDate || 'none',
      end_date: dateRange?.endDate || 'none'
    };

    // Verificar cache primeiro
    const cachedData = metricsCache.get(cacheParams);
    if (cachedData) {
      console.log('📊 Métricas carregadas do cache');
      return cachedData;
    }

    try {
      let url = '/metrics';
      if (dateRange && dateRange.startDate && dateRange.endDate) {
        const params = new URLSearchParams({
          start_date: dateRange.startDate,
          end_date: dateRange.endDate
        });
        url += `?${params.toString()}`;
      }
      
      // Configurar headers condicionais
      const headers: any = {};
      const cacheKey = JSON.stringify(cacheParams);
      const existingCache = metricsCache.get(cacheParams);
      if (existingCache && (existingCache as any).etag) {
        headers['If-None-Match'] = (existingCache as any).etag;
      }
      
      const response = await api.get(url, { headers });
      
      // Se retornou 304 (Not Modified), usar cache
      if (response.status === 304 && existingCache) {
        console.log('📊 Dados não modificados, usando cache');
        return existingCache;
      }
      
      // Monitora performance
      const responseTime = Date.now() - startTime;
      metricsCache.recordRequestTime(cacheKey, responseTime);
        
        if (response.data && response.data.success && response.data.data) {
          const rawData = response.data.data;
          
          
          
          // Verificar se há filtros aplicados (estrutura diferente)
          let processedNiveis: import('../types/api').NiveisMetrics;
          
          if (rawData.general || rawData.by_level) {
            // Estrutura com filtros aplicados
            processedNiveis = {
              geral: { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0, total: 0 },
              n1: { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0, total: 0 },
              n2: { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0, total: 0 },
              n3: { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0, total: 0 },
              n4: { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0, total: 0 }
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

            // Calcular totais gerais dos níveis específicos (excluindo geral)
            const levelValues = Object.entries(processedNiveis)
              .filter(([key]) => key !== 'geral')
              .map(([, value]) => value);
            
            const geralTotals = {
              novos: levelValues.reduce((sum, nivel) => sum + nivel.novos, 0),
              pendentes: levelValues.reduce((sum, nivel) => sum + nivel.pendentes, 0),
              progresso: levelValues.reduce((sum, nivel) => sum + nivel.progresso, 0),
              resolvidos: levelValues.reduce((sum, nivel) => sum + nivel.resolvidos, 0)
            };
            
            // Atualizar o nível geral
            processedNiveis.geral = {
              ...geralTotals,
              total: geralTotals.novos + geralTotals.pendentes + geralTotals.progresso + geralTotals.resolvidos
            };
            
            // processedNiveis já está definido
          } else {
            // Estrutura normal
            
            // Processar dados dos níveis
            if (rawData.niveis) {
              processedNiveis = rawData.niveis;
            } else if (rawData.levels) {
              // Caso os dados venham como 'levels' ao invés de 'niveis'
              processedNiveis = rawData.levels;
            } else {
              // Fallback com zeros
              processedNiveis = {
                geral: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 },
                n1: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 },
                n2: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 },
                n3: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 },
                n4: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 }
              };
            }
          }
          
          // Garantir que todos os campos necessários existam
          const data: DashboardMetrics = {
            niveis: processedNiveis,
            tendencias: rawData.tendencias || {
              novos: '0',
              pendentes: '0',
              progresso: '0',
              resolvidos: '0'
            }
          };
          
          // Armazenar no cache com ETag
          const cacheData = { ...data, etag: response.headers.etag };
          metricsCache.set(cacheParams, cacheData);
          return data;
      } else {
        console.error('API returned unsuccessful response:', response.data);
         // Return fallback data
        const fallbackData: import('../types/api').DashboardMetrics = {
          niveis: {
            geral: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 },
            n1: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 },
            n2: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 },
            n3: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 },
            n4: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 }
          },
          tendencias: { novos: '0', pendentes: '0', progresso: '0', resolvidos: '0' }
        };
        // Não cachear dados de fallback
        return fallbackData;
      }
    } catch (error) {
      console.error('Error fetching metrics:', error);
      // Return fallback data instead of throwing
      const fallbackData: import('../types/api').DashboardMetrics = {
        niveis: {
          geral: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 },
          n1: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 },
          n2: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 },
          n3: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 },
          n4: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 }
        },
        tendencias: { novos: '0', pendentes: '0', progresso: '0', resolvidos: '0' }
      };
      // Não cachear dados de fallback
      return fallbackData;
    }
  },

  // Get system status
  async getSystemStatus(signal?: AbortSignal): Promise<SystemStatus> {
    const startTime = Date.now();
    const cacheParams = { endpoint: 'status' };

    // Verificar cache primeiro
    const cachedData = systemStatusCache.get(cacheParams);
    if (cachedData) {
      console.log('🔧 Status do sistema carregado do cache');
      return cachedData;
    }

    try {
      // Configurar headers condicionais
      const headers: any = {};
      if (cachedData && (cachedData as any).etag) {
        headers['If-None-Match'] = (cachedData as any).etag;
      }
      
      const response = await api.get<ApiResponse<SystemStatus>>('/status', { signal, headers });
      
      // Se retornou 304, usar cache
      if (response.status === 304 && cachedData) {
        console.log('🔧 Status não modificado, usando cache');
        return cachedData;
      }
      
      // Monitora performance
      const responseTime = Date.now() - startTime;
      const cacheKey = JSON.stringify(cacheParams);
      systemStatusCache.recordRequestTime(cacheKey, responseTime);
      
      if (response.data.success && response.data.data) {
        const data = response.data.data;
        // Armazenar no cache com ETag
        const cacheData = { ...data, etag: response.headers.etag };
        systemStatusCache.set(cacheParams, cacheData);
        return data;
      } else {
        console.error('API returned unsuccessful response:', response.data);
        // Return fallback data (não cachear)
        return {
          api: 'offline',
          glpi: 'offline',
          glpi_message: 'Sistema indisponível',
          glpi_response_time: 0,
          last_update: new Date().toISOString(),
          version: '1.0.0',
          status: 'offline',
          sistema_ativo: false,
          ultima_atualizacao: new Date().toISOString()
        };
      }
    } catch (error) {
      console.error('Error fetching system status:', error);
      // Return fallback data instead of throwing (não cachear)
      return {
        api: 'offline',
        glpi: 'offline',
        glpi_message: 'Sistema indisponível',
        glpi_response_time: 0,
        last_update: new Date().toISOString(),
        version: '1.0.0',
        status: 'offline',
        sistema_ativo: false,
        ultima_atualizacao: new Date().toISOString()
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
  async getTechnicianRanking(filters?: FilterParams, signal?: AbortSignal): Promise<any[]> {
    const startTime = Date.now();
    console.log('🔍 API - getTechnicianRanking chamado com filtros:', filters);
    
    RankingDebugger.log('api_getTechnicianRanking_start', {
      filters,
      hasSignal: !!signal
    }, 'api');
    
    // Construir parâmetros de query
    const queryParams = new URLSearchParams();
    
    // Aplicar filtros de data se fornecidos
    if (filters?.dateRange?.startDate && filters?.dateRange?.endDate) {
      queryParams.append('start_date', filters.dateRange.startDate);
      queryParams.append('end_date', filters.dateRange.endDate);
      console.log('📅 API - Adicionando start_date:', filters.dateRange.startDate);
      console.log('📅 API - Adicionando end_date:', filters.dateRange.endDate);
      console.log('📅 Aplicando filtros de data ao ranking de técnicos:', {
        start_date: filters.dateRange.startDate,
        end_date: filters.dateRange.endDate
      });
    }
    
    // Aplicar outros filtros se fornecidos
    if (filters?.level) {
      queryParams.append('level', filters.level);
    }
    if (filters?.limit) {
      queryParams.append('limit', filters.limit.toString());
    }
    
    const url = queryParams.toString() 
      ? `/technicians/ranking?${queryParams.toString()}`
      : '/technicians/ranking';
    
    const cacheParams = { endpoint: 'technicians/ranking', filters: filters || {} };

    // Verificar cache primeiro (com filtros)
    const cachedData = technicianRankingCache.get(cacheParams);
    if (cachedData) {
      console.log('👥 Ranking de técnicos carregado do cache');
      return cachedData;
    }

    try {
      console.log('🔍 Buscando ranking de técnicos com URL:', url);
      
      // Configurar headers condicionais
      const headers: any = {};
      if (cachedData && (cachedData as any).etag) {
        headers['If-None-Match'] = (cachedData as any).etag;
      }
      
      const response = await api.get<ApiResponse<any[]>>(url, {
        signal, // Passar o AbortSignal para o axios
        headers
      });
      
      // Se retornou 304, usar cache
      if (response.status === 304 && cachedData) {
        console.log('👥 Ranking não modificado, usando cache');
        return cachedData;
      }
      
      // Monitora performance
      const responseTime = Date.now() - startTime;
      const cacheKey = JSON.stringify(cacheParams);
      technicianRankingCache.recordRequestTime(cacheKey, responseTime);
      

      
      if (response.data.success && response.data.data) {
        const data = response.data.data;
        console.log('✅ Ranking de técnicos obtido com sucesso:', {
          count: data.length,
          filters: filters,
          responseTime: responseTime + 'ms'
        });
        
        // Mapear os dados para a estrutura esperada pelo frontend
        const mappedData = data.map((tech: any, index: number) => ({
          id: tech.id,
          name: tech.nome || tech.name, // Usar 'nome' do backend, fallback para 'name'
          level: tech.nivel || tech.level || 'N1', // Usar 'nivel' do backend, fallback para 'level'
          total: tech.total || tech.total_tickets || 0,
          rank: index + 1,
          score: tech.score || 0,
          tickets_abertos: tech.abertos || tech.tickets_abertos || 0,
          tickets_fechados: tech.fechados || tech.tickets_fechados || 0,
          tickets_pendentes: tech.pendentes || tech.tickets_pendentes || 0
        }))
        
        RankingDebugger.log('api_data_mapped', {
          originalDataLength: data.length,
          mappedDataLength: mappedData.length,
          sampleOriginal: data[0],
          sampleMapped: mappedData[0]
        }, 'api');
        
        // Armazenar no cache com ETag
        const cacheData = { ...mappedData, etag: response.headers.etag };
        technicianRankingCache.set(cacheParams, cacheData);
        RankingDebugger.trackCacheOperation('api_set', JSON.stringify(cacheParams), cacheData);
        return mappedData;
      } else {
        console.error('API returned unsuccessful response:', response.data);
        return [];
      }
    } catch (error) {
      // Se for um erro de cancelamento, não logar como erro
      if (error instanceof Error && error.name === 'CanceledError') {
        console.log('🚫 Requisição de ranking de técnicos cancelada');
        throw error; // Re-throw para que o useDashboard possa tratar
      }
      console.error('Error fetching technician ranking:', error);
      return [];
    }
  },

  // Get new tickets
  async getNewTickets(limit: number = 5): Promise<any[]> {
    const startTime = Date.now();
    const cacheParams = { endpoint: 'tickets/new', limit: limit.toString() };

    const cachedData = newTicketsCache.get(cacheParams);
    if (cachedData) {
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
        newTicketsCache.set(cacheParams, data);
        return data;
      } else {
        // Return mock data as fallback (não cachear)
        return [
          {
            id: '12345',
            title: 'Problema com impressora',
            description: 'Impressora não está funcionando corretamente',
            requester: 'João Silva',
            date: new Date().toISOString(),
            priority: 'Alta',
            status: 'Novo'
          },
          {
            id: '12346',
            title: 'Erro no sistema',
            description: 'Sistema apresentando lentidão',
            requester: 'Maria Santos',
            date: new Date(Date.now() - 3600000).toISOString(),
            priority: 'Média',
            status: 'Novo'
          },
          {
            id: '12347',
            title: 'Solicitação de acesso',
            description: 'Necessário acesso ao sistema financeiro',
            requester: 'Pedro Costa',
            date: new Date(Date.now() - 7200000).toISOString(),
            priority: 'Baixa',
            status: 'Novo'
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
          description: 'Impressora não está funcionando corretamente',
          requester: 'João Silva',
          date: new Date().toISOString(),
          priority: 'Alta',
          status: 'Novo'
        },
        {
          id: '12346',
          title: 'Erro no sistema',
          description: 'Sistema apresentando lentidão',
          requester: 'Maria Santos',
          date: new Date(Date.now() - 3600000).toISOString(),
          priority: 'Média',
          status: 'Novo'
        },
        {
          id: '12347',
          title: 'Solicitação de acesso',
          description: 'Necessário acesso ao sistema financeiro',
          requester: 'Pedro Costa',
          date: new Date(Date.now() - 7200000).toISOString(),
          priority: 'Baixa',
          status: 'Novo'
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
export const getTechnicianRanking = (filters?: FilterParams, signal?: AbortSignal): Promise<any[]> => {
  console.log('🔍 Export - getTechnicianRanking chamado com filtros:', filters);
  return apiService.getTechnicianRanking(filters, signal);
};
export const getNewTickets = apiService.getNewTickets;
export const search = apiService.search;
export const healthCheck = apiService.healthCheck;
export const clearAllCaches = apiService.clearAllCaches;

// Função para buscar métricas do dashboard com tipagem forte
export const fetchDashboardMetrics = async (
  filters: FilterParams = {},
  signal?: AbortSignal
): Promise<DashboardMetrics | null> => {
  const queryParams = new URLSearchParams();
  let url = '';
  
  try {
    
    // Mapear filtros para os nomes esperados pela API
    const filterMapping: Record<string, string> = {
      startDate: 'start_date',
      endDate: 'end_date',
      status: 'status',
      priority: 'priority',
      level: 'level'
    };
    
    // Processar dateRange se presente
    if (filters.dateRange && filters.dateRange.startDate && filters.dateRange.endDate) {
      console.log('📅 Processando dateRange:', filters.dateRange);
      queryParams.append('start_date', filters.dateRange.startDate);
      queryParams.append('end_date', filters.dateRange.endDate);
    } else {
      console.log('⚠️ dateRange não encontrado ou incompleto:', filters.dateRange);
    }
    
    // Adicionar filtros como parâmetros de query com validação de tipos
    Object.entries(filters).forEach(([key, value]) => {
      if (key === 'dateRange') return; // Já processado acima
      if (value !== null && value !== undefined && value !== '') {
        const apiKey = filterMapping[key] || key;
        queryParams.append(apiKey, value.toString());
      }
    });
    
    url = queryParams.toString() 
      ? `${API_BASE_URL}/metrics?${queryParams.toString()}`
      : `${API_BASE_URL}/metrics`;
    
    console.log('🔍 Filtros originais:', filters);
    console.log('🔍 Query params construídos:', queryParams.toString());
    console.log('🔍 Fazendo requisição para:', url);
    
    const startTime = performance.now();
    
    const response = await api.get('/metrics', {
      params: Object.fromEntries(queryParams),
      timeout: 60000,
      signal
    });
    
    const endTime = performance.now();
    const responseTime = endTime - startTime;
    
    const result: ApiResult<DashboardMetrics> = response.data;
    console.log('Resposta da API recebida:', result);
    
    // Log de performance
    const perfMetrics: PerformanceMetrics = {
      responseTime,
      cacheHit: false,
      timestamp: new Date(),
      endpoint: '/metrics'
    };
    console.log('Métricas de performance:', perfMetrics);
    
    // Verificar se a resposta é um erro
    if (isApiError(result)) {
      console.error('API retornou erro:', result.error);
      return null;
    }
    
    // Verificar se é uma resposta de sucesso
    if (isApiResponse(result)) {
      // Processar dados para garantir estrutura consistente
      const processedData = transformLegacyData(result.data);
      console.log('Dados processados:', processedData);
      
      return processedData;
    }
    
    console.error('Resposta da API em formato inesperado:', result);
    return null;
    
  } catch (error) {
    console.error('Erro ao buscar métricas:', error);
    console.error('Tipo do erro:', typeof error);
    console.error('Stack trace:', error instanceof Error ? error.stack : 'N/A');
    console.error('URL tentada:', url);
    return null;
  }
};