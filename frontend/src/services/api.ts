import { httpClient, apiUtils, API_CONFIG, updateAuthTokens } from './httpClient';
import { SystemStatus, DateRange } from '../types';
import type {
  ApiResult,
  DashboardMetrics,
  FilterParams,
  PerformanceMetrics,
  LevelMetrics
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
import { API_ENDPOINTS, buildApiUrl, DEFAULT_PARAMS, debugLog, errorLog, successLog } from '../config/apiConfig';

// Base URL for API (mantido para compatibilidade)
const API_BASE_URL = API_CONFIG.BASE_URL;

// Cliente HTTP (alias para compatibilidade)
const api = httpClient;

// Os interceptadores agora estão centralizados no httpClient.ts

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

    // Cache completamente desabilitado para forçar novas requisições
    console.log('🚫 Cache completamente desabilitado - sempre buscando dados frescos');

    try {
      let url = '/kpis';
      if (dateRange && dateRange.startDate && dateRange.endDate) {
        const params = new URLSearchParams({
          start_date: dateRange.startDate,
          end_date: dateRange.endDate
        });
        url += `?${params.toString()}`;
      }
      
      const response = await api.get(url);
      
      // Monitora performance
      const responseTime = Date.now() - startTime;
      const cacheKey = JSON.stringify(cacheParams);
      metricsCache.recordRequestTime(cacheKey, responseTime);
        
        if (response.data && response.data.success && response.data.data) {
          // A API retorna dados em response.data.data
          const rawData = response.data.data.data || response.data.data;
          
          console.log('🔍 API Service - rawData:', rawData);
          console.log('🔍 API Service - rawData.niveis:', rawData.niveis);
          console.log('🔍 API Service - Keys de rawData:', Object.keys(rawData || {}));
          
          if (rawData.niveis) {
            console.log('🔍 API Service - Dados dos níveis encontrados:', rawData.niveis);
          } else {
            console.log('🔍 API Service - PROBLEMA: rawData.niveis não existe!');
          }
          
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
              
              // Garantir que todos os níveis tenham a propriedade 'total'
              Object.keys(processedNiveis).forEach(nivel => {
                const nivelData = processedNiveis[nivel as keyof typeof processedNiveis];
                if (nivelData && typeof nivelData === 'object') {
                  nivelData.total = nivelData.novos + nivelData.progresso + nivelData.pendentes + nivelData.resolvidos;
                }
              });
              
              console.log('🔍 API Service - Níveis processados com totais:', processedNiveis);
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
          
          // Armazenar no cache
          metricsCache.set(cacheParams, data);
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
  async getSystemStatus(): Promise<SystemStatus> {
    const startTime = Date.now();
    const cacheParams = { endpoint: 'status' };

    // Verificar cache primeiro
    const cachedData = systemStatusCache.get(cacheParams);
    if (cachedData) {
      return cachedData;
    }

    try {
      debugLog('getSystemStatus - Buscando status do sistema...');
      const response = await api.get<ApiResponse<SystemStatus>>(API_ENDPOINTS.SYSTEM_STATUS);
      
      // Monitora performance
      const responseTime = Date.now() - startTime;
      const cacheKey = JSON.stringify(cacheParams);
      systemStatusCache.recordRequestTime(cacheKey, responseTime);
      
      if (response.data.success && response.data.data) {
        const data = response.data.data.data || response.data.data;
        // Armazenar no cache
        systemStatusCache.set(cacheParams, data);
        successLog('getSystemStatus - Status do sistema obtido com sucesso');
        return data;
      } else {
        errorLog('getSystemStatus - API returned unsuccessful response:', response.data);
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
      errorLog('getSystemStatus - Error fetching system status:', error);
      // Return fallback data instead of throwing (não cachear)
      return {
        api: 'offline',
        glpi: 'offline',
        glpi_message: 'Erro de conexão',
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
      await api.head('/kpis');
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
      debugLog('getTechnicianRanking - Buscando ranking de técnicos...');
      const response = await api.get<ApiResponse<any[]>>(API_ENDPOINTS.TECHNICIANS_RANKING);
      
      // Monitora performance
      const responseTime = Date.now() - startTime;
      const cacheKey = JSON.stringify(cacheParams);
      technicianRankingCache.recordRequestTime(cacheKey, responseTime);
      
      if (response.data.success && response.data.data) {
        const data = response.data.data.data || response.data.data;
        // Armazenar no cache
        technicianRankingCache.set(cacheParams, data);
        successLog('getTechnicianRanking - Ranking de técnicos obtido com sucesso');
        return data;
      } else {
        errorLog('getTechnicianRanking - API returned unsuccessful response:', response.data);
        return [];
      }
    } catch (error) {
      errorLog('getTechnicianRanking - Error fetching technician ranking:', error);
      return [];
    }
  },

  // Get new tickets
  async getNewTickets(limit: number = DEFAULT_PARAMS.TICKETS_LIMIT): Promise<any[]> {
    const startTime = Date.now();
    const cacheParams = { endpoint: 'tickets/new', limit: limit.toString() };

    // Verificar cache primeiro
    const cachedData = newTicketsCache.get(cacheParams);
    if (cachedData) {
      debugLog('getNewTickets - Retornando dados do cache para novos tickets');
      return cachedData;
    }

    try {
      debugLog('getNewTickets - Buscando novos tickets...', { limit });
      const url = buildApiUrl(API_ENDPOINTS.TICKETS_NEW, { limit });
      const response = await api.get<ApiResponse<any[]>>(url);
      
      // Monitora performance
      const responseTime = Date.now() - startTime;
      const cacheKey = JSON.stringify(cacheParams);
      newTicketsCache.recordRequestTime(cacheKey, responseTime);
      
      if (response.data.success && response.data.data) {
        const data = response.data.data.data || response.data.data;
        // Armazenar no cache
        newTicketsCache.set(cacheParams, data);
        successLog('getNewTickets - Novos tickets obtidos com sucesso', { count: data.length });
        return data;
      } else {
        errorLog('getNewTickets - API returned unsuccessful response:', response.data);
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
      errorLog('getNewTickets - Error fetching new tickets:', error);
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


// Fun��o para transformar array da API em m�tricas do dashboard
const transformArrayToMetrics = (data: any[]): DashboardMetrics => {
  const defaultLevel: LevelMetrics = {
    novos: 0,
    progresso: 0,
    pendentes: 0,
    resolvidos: 0,
    total: 0
  };

  const processedNiveis = {
    n1: { ...defaultLevel },
    n2: { ...defaultLevel },
    n3: { ...defaultLevel },
    n4: { ...defaultLevel },
    geral: { ...defaultLevel }
  };

  // Processar dados do array
  data.forEach((item: any) => {
    if (item.by_level) {
      Object.entries(item.by_level).forEach(([level, levelData]: [string, any]) => {
        const levelKey = level.toLowerCase() as keyof typeof processedNiveis;
        if (processedNiveis[levelKey]) {
          const novos = levelData['Novo'] || 0;
          const progresso = (levelData['Processando (atribu�do)'] || 0) + (levelData['Processando (planejado)'] || 0);
          const pendentes = levelData['Pendente'] || 0;
          const resolvidos = (levelData['Solucionado'] || 0) + (levelData['Fechado'] || 0);
          
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
  });

  return {
    niveis: processedNiveis,
    tendencias: {
      novos: '0',
      progresso: '0',
      pendentes: '0',
      resolvidos: '0'
    }
  };
};

// Export utilities from httpClient
export { updateAuthTokens, apiUtils, API_CONFIG } from './httpClient';

// Export the centralized HTTP client
export { httpClient } from './httpClient';

// Função para buscar métricas do dashboard com tipagem forte
export const fetchDashboardMetrics = async (
  filters: FilterParams = {}
): Promise<DashboardMetrics | null> => {
  console.log(" fetchDashboardMetrics chamada com filtros:", filters);
  try {
    
    // Mapear filtros para os nomes esperados pela API
    const filterMapping: Record<string, string> = {
      startDate: 'start_date',
      endDate: 'end_date',
      status: 'status',
      priority: 'priority',
      level: 'level'
    };
    const queryParams = new URLSearchParams();

    // Mapear filtros para os nomes esperados pela API
    // Processar dateRange se presente
    if (filters.dateRange && filters.dateRange.startDate && filters.dateRange.endDate) {
      console.log(" Processando dateRange:", filters.dateRange);
      queryParams.append("start_date", filters.dateRange.startDate);
      queryParams.append("end_date", filters.dateRange.endDate);
    } else {
      console.log(" dateRange n�o encontrado ou incompleto:", filters.dateRange);
    }
    Object.entries(filters).forEach(([key, value]) => {
      if (key === 'dateRange') return; // Já processado acima
      if (value !== null && value !== undefined && value !== '') {
        const apiKey = filterMapping[key] || key;
        queryParams.append(apiKey, value.toString());
      }
    });
    
    const url = queryParams.toString() 
      ? `/api/v1/metrics/levels?${queryParams.toString()}`
      : `/api/v1/metrics/levels`;
    
    console.log('🔍 fetchDashboardMetrics - Filtros originais:', filters);
    console.log('🔍 fetchDashboardMetrics - Query params construídos:', queryParams.toString());
    console.log('🔍 fetchDashboardMetrics - Fazendo requisição para:', url);
    
    const startTime = performance.now();
    
    const response = await httpClient.get(url);
    
    const endTime = performance.now();
    const responseTime = endTime - startTime;
    
    console.log('🔍 fetchDashboardMetrics - Resposta da API recebida:', response.data);
    const rawData = response.data;
    
    // Log de performance
    const perfMetrics: PerformanceMetrics = {
      responseTime,
      cacheHit: false,
      timestamp: new Date(),
      endpoint: '/kpis'
    };
    console.log('🔍 fetchDashboardMetrics - Métricas de performance:', perfMetrics);
    
    // Verificar se a resposta tem a estrutura esperada
    if (rawData && rawData.success && rawData.data) {
      console.log('🔍 fetchDashboardMetrics - Dados extraídos de rawData.data:', rawData.data);
      // Os dados estão em rawData.data, que já contém niveis e tendencias
      const processedData = transformLegacyData(rawData.data);
      console.log('🔍 fetchDashboardMetrics - Dados processados com transformLegacyData:', processedData);
      return processedData;
    }
    
    if (Array.isArray(rawData)) {
      console.log('🔍 fetchDashboardMetrics - Dados são array, processando com transformArrayToMetrics');
      const processedData = transformArrayToMetrics(rawData);
      console.log('🔍 fetchDashboardMetrics - Dados processados:', processedData);
      return processedData;
    }

    if (rawData && typeof rawData === 'object' && 'data' in rawData) {
      console.log('🔍 fetchDashboardMetrics - Dados têm propriedade data, processando com transformLegacyData');
      const processedData = transformLegacyData(rawData.data);
      console.log('🔍 fetchDashboardMetrics - Dados processados:', processedData);
      return processedData;
    }

    console.error('🔍 fetchDashboardMetrics - Resposta da API em formato inesperado:', rawData);
    return null;
    
  } catch (error) {
    console.error('🔍 fetchDashboardMetrics - Erro ao buscar métricas:', error);
    console.error('🔍 fetchDashboardMetrics - Tipo do erro:', typeof error);
    console.error('🔍 fetchDashboardMetrics - Stack trace:', error instanceof Error ? error.stack : 'N/A');
    console.error('🔍 fetchDashboardMetrics - URL tentada:', '/api/v1/metrics/levels');
    return null;
  }
};












