import axios, { AxiosResponse } from 'axios';
import { MetricsData, SystemStatus } from '../types';
import { DateRange } from '@/types/dashboard';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
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
    console.error('API Response Error:', error);
    
    if (error.code === 'ECONNABORTED') {
      console.error('Request timeout');
    } else if (error.response?.status === 404) {
      console.error('Endpoint not found');
    } else if (error.response?.status >= 500) {
      console.error('Server error');
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
  async getMetrics(dateRange?: DateRange): Promise<MetricsData> {
    try {
      let url = '/metrics';
      if (dateRange && dateRange.startDate && dateRange.endDate) {
        const params = new URLSearchParams({
          start_date: dateRange.startDate,
          end_date: dateRange.endDate
        });
        url += `?${params.toString()}`;
        console.log('🔍 Chamando API com filtro de data:', { start_date: dateRange.startDate, end_date: dateRange.endDate });
      } else {
        console.log('🔍 Chamando API sem filtro de data');
      }
      const response = await api.get(url);
      
      if (response.data && response.data.success && response.data.data) {
        const data = response.data.data;
        return data;
      } else {
        console.error('API returned unsuccessful response:', response.data);
        // Return fallback data
        return {
          novos: 0,
          pendentes: 0,
          progresso: 0,
          resolvidos: 0,
          total: 0,
          niveis: {
            n1: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0 },
            n2: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0 },
            n3: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0 },
            n4: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0 }
          },
          tendencias: { novos: '0', pendentes: '0', progresso: '0', resolvidos: '0' }
        };
      }
    } catch (error) {
      console.error('Error fetching metrics:', error);
      // Return fallback data instead of throwing
      return {
        novos: 0,
        pendentes: 0,
        progresso: 0,
        resolvidos: 0,
        total: 0,
        niveis: {
          n1: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0 },
          n2: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0 },
          n3: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0 },
          n4: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0 }
        },
        tendencias: { novos: '0', pendentes: '0', progresso: '0', resolvidos: '0' }
      };
    }
  },

  // Get system status
  async getSystemStatus(): Promise<SystemStatus> {
    try {
      const response = await api.get<ApiResponse<SystemStatus>>('/status');
      
      if (response.data.success && response.data.data) {
        return response.data.data;
      } else {
        console.error('API returned unsuccessful response:', response.data);
        // Return fallback data
        return {
          api: 'unknown',
          database: 'unknown',
          last_update: '',
          version: '1.0.0'
        };
      }
    } catch (error) {
      console.error('Error fetching system status:', error);
      // Return fallback data instead of throwing
      return {
        api: 'offline',
        database: 'unknown',
        last_update: '',
        version: '1.0.0'
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
    try {
      const response = await api.get<ApiResponse<any[]>>('/technicians/ranking');
      
      if (response.data.success && response.data.data) {
        return response.data.data;
      } else {
        console.error('API returned unsuccessful response:', response.data);
        // Return empty array as fallback
        return [];
      }
    } catch (error) {
      console.error('Error fetching technician ranking:', error);
      // Return empty array instead of throwing
      return [];
    }
  },

  // Get new tickets
  async getNewTickets(limit: number = 5): Promise<any[]> {
    try {
      const response = await api.get<ApiResponse<any[]>>(`/tickets/new?limit=${limit}`);
      
      if (response.data.success && response.data.data) {
        return response.data.data;
      } else {
        console.error('API returned unsuccessful response:', response.data);
        // Return mock data as fallback
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
      // Return mock data instead of throwing error
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
      
      return mockResults.filter(result => 
        result.title.toLowerCase().includes(query.toLowerCase())
      );
    } catch (error) {
      console.error('Error searching:', error);
      throw new Error('Falha na busca');
    }
  },
};

export default api;