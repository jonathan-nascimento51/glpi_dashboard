import { httpClient } from '../../../services/httpClient';
import { API_ENDPOINTS } from '../../../config/apiConfig';
import type { 
  DashboardMetrics, 
  FilterParams, 
  SystemStatus, 
  TechnicianRanking,
  DashboardApiResponse,
  SystemStatusApiResponse,
  TechnicianRankingApiResponse
} from '../types/dashboardTypes';
import { transformLegacyData } from '../../../types/api';

/**
 * Serviço para operações do dashboard
 * Encapsula todas as chamadas de API relacionadas ao dashboard
 */
export class DashboardService {
  /**
   * Busca métricas do dashboard com filtros opcionais
   */
  static async fetchMetrics(filters: FilterParams = {}): Promise<DashboardMetrics> {
    console.log('🔄 DashboardService - Buscando métricas com filtros:', filters);
    
    try {
      // Mapear filtros para os nomes esperados pela API
      const queryParams = new URLSearchParams();
      
      // Processar dateRange se presente
      if (filters.dateRange?.start && filters.dateRange?.end) {
        queryParams.append('start_date', filters.dateRange.start);
        queryParams.append('end_date', filters.dateRange.end);
      }
      
      // Processar outros filtros
      Object.entries(filters).forEach(([key, value]) => {
        if (key === 'dateRange') return; // Já processado acima
        if (value !== null && value !== undefined && value !== '') {
          queryParams.append(key, value.toString());
        }
      });
      
      const url = queryParams.toString() ? `/kpis?${queryParams.toString()}` : '/kpis';
      
      console.log('🔍 DashboardService - Fazendo requisição para:', url);
      
      const startTime = performance.now();
      const response = await httpClient.get(url);
      const responseTime = performance.now() - startTime;
      
      console.log('📊 DashboardService - Resposta recebida em', responseTime.toFixed(2), 'ms');
      console.log('📊 DashboardService - Dados brutos:', response.data);
      
      const rawData = response.data;
      
      // Verificar estrutura da resposta e processar dados
      if (rawData?.success && rawData?.data) {
        const processedData = transformLegacyData(rawData.data);
        console.log('✅ DashboardService - Dados processados:', processedData);
        return processedData;
      }
      
      if (Array.isArray(rawData)) {
        const processedData = this.transformArrayToMetrics(rawData);
        console.log('✅ DashboardService - Array transformado:', processedData);
        return processedData;
      }
      
      if (rawData && typeof rawData === 'object' && 'data' in rawData) {
        const processedData = transformLegacyData(rawData.data);
        console.log('✅ DashboardService - Dados legacy processados:', processedData);
        return processedData;
      }
      
      console.warn('⚠️ DashboardService - Formato de resposta inesperado, retornando dados padrão');
      return this.getDefaultMetrics();
      
    } catch (error) {
      console.error('❌ DashboardService - Erro ao buscar métricas:', error);
      throw new Error(`Falha ao carregar métricas: ${error instanceof Error ? error.message : 'Erro desconhecido'}`);
    }
  }
  
  /**
   * Busca status do sistema
   */
  static async fetchSystemStatus(): Promise<SystemStatus> {
    console.log('🔄 DashboardService - Buscando status do sistema...');
    
    try {
      const response = await httpClient.get(API_ENDPOINTS.SYSTEM_STATUS);
      
      console.log('🔧 DashboardService - Status do sistema recebido:', response.data);
      
      if (response.data?.success && response.data?.data) {
        const data = response.data.data.data || response.data.data;
        console.log('✅ DashboardService - Status processado:', data);
        return data;
      }
      
      console.warn('⚠️ DashboardService - Resposta de status inválida, retornando padrão');
      return this.getDefaultSystemStatus();
      
    } catch (error) {
      console.error('❌ DashboardService - Erro ao buscar status:', error);
      return this.getDefaultSystemStatus();
    }
  }
  
  /**
   * Busca ranking de técnicos
   */
  static async fetchTechnicianRanking(): Promise<TechnicianRanking[]> {
    console.log('🔄 DashboardService - Buscando ranking de técnicos...');
    
    try {
      const response = await httpClient.get(API_ENDPOINTS.TECHNICIANS_RANKING);
      
      console.log('👥 DashboardService - Ranking recebido:', response.data);
      
      if (response.data?.success && response.data?.data) {
        const data = response.data.data.data || response.data.data;
        console.log('✅ DashboardService - Ranking processado:', data);
        return Array.isArray(data) ? data : [];
      }
      
      console.warn('⚠️ DashboardService - Resposta de ranking inválida, retornando array vazio');
      return [];
      
    } catch (error) {
      console.error('❌ DashboardService - Erro ao buscar ranking:', error);
      return [];
    }
  }
  
  /**
   * Verifica saúde da API
   */
  static async healthCheck(): Promise<boolean> {
    try {
      await httpClient.head('/kpis');
      return true;
    } catch (error) {
      console.error('❌ DashboardService - Health check falhou:', error);
      return false;
    }
  }
  
  /**
   * Transforma array de dados em métricas do dashboard
   */
  private static transformArrayToMetrics(data: any[]): DashboardMetrics {
    const defaultLevel = {
      total: 0,
      abertos: 0,
      fechados: 0,
      pendentes: 0,
      tempo_medio_resolucao: 0
    };
    
    const processedNiveis = {
      N1: { ...defaultLevel },
      N2: { ...defaultLevel },
      N3: { ...defaultLevel },
      N4: { ...defaultLevel }
    };
    
    // Processar dados do array
    data.forEach((item: any) => {
      if (item.by_level) {
        Object.entries(item.by_level).forEach(([level, levelData]: [string, any]) => {
          const levelKey = level.toUpperCase() as keyof typeof processedNiveis;
          if (processedNiveis[levelKey]) {
            processedNiveis[levelKey] = {
              total: levelData.total || 0,
              abertos: levelData.abertos || levelData['Novo'] || 0,
              fechados: levelData.fechados || levelData['Resolvido'] || 0,
              pendentes: levelData.pendentes || levelData['Pendente'] || 0,
              tempo_medio_resolucao: levelData.tempo_medio_resolucao || 0
            };
          }
        });
      }
    });
    
    return {
      niveis: processedNiveis,
      systemStatus: this.getDefaultSystemStatus(),
      technicianRanking: [],
      last_updated: new Date().toISOString()
    };
  }
  
  /**
   * Retorna métricas padrão em caso de erro
   */
  private static getDefaultMetrics(): DashboardMetrics {
    const defaultLevel = {
      total: 0,
      abertos: 0,
      fechados: 0,
      pendentes: 0,
      tempo_medio_resolucao: 0
    };
    
    return {
      niveis: {
        N1: { ...defaultLevel },
        N2: { ...defaultLevel },
        N3: { ...defaultLevel },
        N4: { ...defaultLevel }
      },
      systemStatus: this.getDefaultSystemStatus(),
      technicianRanking: [],
      last_updated: new Date().toISOString()
    };
  }
  
  /**
   * Retorna status padrão do sistema
   */
  private static getDefaultSystemStatus(): SystemStatus {
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
}

// Exports para compatibilidade com o código existente
export const fetchDashboardMetrics = DashboardService.fetchMetrics;
export const getSystemStatus = DashboardService.fetchSystemStatus;
export const getTechnicianRanking = DashboardService.fetchTechnicianRanking;
export const healthCheck = DashboardService.healthCheck;