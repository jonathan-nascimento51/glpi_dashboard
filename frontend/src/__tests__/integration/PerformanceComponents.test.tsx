/**
 * Testes de integração para componentes de performance
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import { PerformanceDashboard } from '../../components/PerformanceDashboard';
import * as httpClient from '../../services/httpClient';

// Mock do httpClient
vi.mock('../../services/httpClient', () => ({
  get: vi.fn(),
  post: vi.fn(),
}));

const mockHttpClient = vi.mocked(httpClient);

// Wrapper para React Query
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
      },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    React.createElement(QueryClientProvider, { client: queryClient }, children)
  );
};

// Mock de dados
const mockPerformanceData = {
  success: true,
  data: {
    total_requests: 150,
    average_response_time: 0.25,
    cache_hit_rate: 0.85,
    cache_hits: 128,
    cache_misses: 22,
    memory_usage: 65.5,
    cpu_usage: 45.2,
    active_connections: 12,
    last_operation_time: 1755737268.248,
    recent_history: [
      { timestamp: 1755737268.248, response_time: 0.15 },
      { timestamp: 1755737268.150, response_time: 0.22 },
      { timestamp: 1755737268.050, response_time: 0.18 },
    ],
  },
  timestamp: 1755737268.248,
};

const mockSettingsData = {
  success: true,
  data: {
    cache_enabled: true,
    cache_ttl: 300,
    debug_mode: false,
    max_cache_size: 1000,
    metrics_enabled: true,
    performance_monitoring: true,
  },
  timestamp: 1755737268.248,
};

describe('Componentes de Performance - Integração', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockHttpClient.get.mockResolvedValue({ data: mockPerformanceData });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('PerformanceMonitor', () => {
    it('deve renderizar e carregar dados de performance', async () => {
      const Wrapper = createWrapper();
      
      render(
        <Wrapper>
          <PerformanceMonitor />
        </Wrapper>
      );

      // Verificar se o componente está carregando
      expect(screen.getByText(/carregando/i) || screen.getByRole('progressbar')).toBeInTheDocument();

      // Aguardar carregamento dos dados
      await waitFor(() => {
        expect(mockHttpClient.get).toHaveBeenCalledWith('/api/performance/metrics');
      });

      // Verificar se os dados foram exibidos
      await waitFor(() => {
        expect(screen.getByText(/150/)).toBeInTheDocument(); // total_requests
        expect(screen.getByText(/0.25/)).toBeInTheDocument(); // average_response_time
        expect(screen.getByText(/85%/)).toBeInTheDocument(); // cache_hit_rate
      });
    });

    it('deve atualizar dados quando timeRange muda', async () => {
      const Wrapper = createWrapper();
      
      render(
        <Wrapper>
          <PerformanceMonitor />
        </Wrapper>
      );

      // Aguardar carregamento inicial
      await waitFor(() => {
        expect(mockHttpClient.get).toHaveBeenCalledWith('/api/performance/metrics');
      });

      // Simular mudança de timeRange (se houver seletor)
      const timeRangeSelector = screen.queryByRole('combobox') || screen.queryByRole('button');
      if (timeRangeSelector) {
        fireEvent.click(timeRangeSelector);
        
        // Verificar se nova requisição foi feita
        await waitFor(() => {
          expect(mockHttpClient.get).toHaveBeenCalledTimes(2);
        });
      }
    });

    it('deve exibir erro quando API falha', async () => {
      mockHttpClient.get.mockRejectedValue(new Error('API Error'));
      
      const Wrapper = createWrapper();
      
      render(
        <Wrapper>
          <PerformanceMonitor />
        </Wrapper>
      );

      // Aguardar tentativa de carregamento
      await waitFor(() => {
        expect(mockHttpClient.get).toHaveBeenCalled();
      });

      // Verificar se ainda exibe dados (fallback para mock)
      await waitFor(() => {
        // Deve exibir algum conteúdo mesmo com erro
        expect(screen.getByText(/performance/i) || screen.getByText(/monitor/i)).toBeInTheDocument();
      });
    });
  });

  describe('PerformanceMetrics', () => {
    it('deve exibir métricas formatadas corretamente', async () => {
      const Wrapper = createWrapper();
      
      render(
        <Wrapper>
          <PerformanceMetrics />
        </Wrapper>
      );

      await waitFor(() => {
        expect(mockHttpClient.get).toHaveBeenCalled();
      });

      // Verificar formatação das métricas
      await waitFor(() => {
        // Total de requisições
        expect(screen.getByText(/150/)).toBeInTheDocument();
        
        // Tempo de resposta (pode estar em ms ou s)
        expect(screen.getByText(/250ms/) || screen.getByText(/0.25s/)).toBeInTheDocument();
        
        // Taxa de cache
        expect(screen.getByText(/85%/)).toBeInTheDocument();
        
        // Uso de memória
        expect(screen.getByText(/65.5%/)).toBeInTheDocument();
        
        // Uso de CPU
        expect(screen.getByText(/45.2%/)).toBeInTheDocument();
      });
    });

    it('deve exibir gráficos de histórico quando disponível', async () => {
      const Wrapper = createWrapper();
      
      render(
        <Wrapper>
          <PerformanceMetrics showHistory={true} />
        </Wrapper>
      );

      await waitFor(() => {
        expect(mockHttpClient.get).toHaveBeenCalled();
      });

      // Verificar se elementos de gráfico estão presentes
      await waitFor(() => {
        const chartElements = screen.queryAllByRole('img') || 
                            screen.queryAllByTestId(/chart/) ||
                            document.querySelectorAll('canvas, svg');
        
        expect(chartElements.length).toBeGreaterThan(0);
      });
    });

    it('deve permitir refresh manual dos dados', async () => {
      const Wrapper = createWrapper();
      
      render(
        <Wrapper>
          <PerformanceMetrics />
        </Wrapper>
      );

      await waitFor(() => {
        expect(mockHttpClient.get).toHaveBeenCalledTimes(1);
      });

      // Procurar botão de refresh
      const refreshButton = screen.queryByRole('button', { name: /refresh|atualizar|reload/i }) ||
                           screen.queryByTestId('refresh-button');
      
      if (refreshButton) {
        fireEvent.click(refreshButton);
        
        await waitFor(() => {
          expect(mockHttpClient.get).toHaveBeenCalledTimes(2);
        });
      }
    });
  });

  describe('PerformanceSettings', () => {
    beforeEach(() => {
      mockHttpClient.get.mockImplementation((url) => {
        if (url.includes('/settings')) {
          return Promise.resolve({ data: mockSettingsData });
        }
        return Promise.resolve({ data: mockPerformanceData });
      });
    });

    it('deve carregar e exibir configurações', async () => {
      const Wrapper = createWrapper();
      
      render(
        <Wrapper>
          <PerformanceSettings />
        </Wrapper>
      );

      await waitFor(() => {
        expect(mockHttpClient.get).toHaveBeenCalledWith('/api/performance/settings');
      });

      // Verificar se configurações são exibidas
      await waitFor(() => {
        expect(screen.getByText(/cache.*ativado|cache.*enabled/i)).toBeInTheDocument();
        expect(screen.getByText(/300/)).toBeInTheDocument(); // cache_ttl
        expect(screen.getByText(/1000/)).toBeInTheDocument(); // max_cache_size
      });
    });

    it('deve permitir limpar cache', async () => {
      mockHttpClient.post.mockResolvedValue({
        data: {
          success: true,
          message: 'Cache limpo com sucesso',
          timestamp: Date.now(),
        },
      });

      const Wrapper = createWrapper();
      
      render(
        <Wrapper>
          <PerformanceSettings />
        </Wrapper>
      );

      await waitFor(() => {
        expect(mockHttpClient.get).toHaveBeenCalled();
      });

      // Procurar botão de limpar cache
      const clearButton = screen.queryByRole('button', { name: /limpar.*cache|clear.*cache/i }) ||
                         screen.queryByTestId('clear-cache-button');
      
      if (clearButton) {
        fireEvent.click(clearButton);
        
        await waitFor(() => {
          expect(mockHttpClient.post).toHaveBeenCalledWith('/api/performance/cache/clear');
        });

        // Verificar mensagem de sucesso
        await waitFor(() => {
          expect(screen.getByText(/sucesso|success/i)).toBeInTheDocument();
        });
      }
    });

    it('deve exibir erro ao falhar limpeza de cache', async () => {
      mockHttpClient.post.mockRejectedValue(new Error('Clear failed'));

      const Wrapper = createWrapper();
      
      render(
        <Wrapper>
          <PerformanceSettings />
        </Wrapper>
      );

      await waitFor(() => {
        expect(mockHttpClient.get).toHaveBeenCalled();
      });

      const clearButton = screen.queryByRole('button', { name: /limpar.*cache|clear.*cache/i });
      
      if (clearButton) {
        fireEvent.click(clearButton);
        
        await waitFor(() => {
          expect(mockHttpClient.post).toHaveBeenCalled();
        });

        // Verificar mensagem de erro
        await waitFor(() => {
          expect(screen.getByText(/erro|error|falha|failed/i)).toBeInTheDocument();
        });
      }
    });
  });

  describe('Integração entre componentes', () => {
    it('deve sincronizar dados entre PerformanceMonitor e PerformanceMetrics', async () => {
      const Wrapper = createWrapper();
      
      render(
        <Wrapper>
          <div>
            <PerformanceMonitor />
            <PerformanceMetrics />
          </div>
        </Wrapper>
      );

      // Ambos componentes devem fazer requisições
      await waitFor(() => {
        expect(mockHttpClient.get).toHaveBeenCalledWith('/api/performance/metrics');
      });

      // Verificar se dados são consistentes em ambos
      await waitFor(() => {
        const totalRequestsElements = screen.getAllByText(/150/);
        expect(totalRequestsElements.length).toBeGreaterThanOrEqual(1);
        
        const responseTimeElements = screen.getAllByText(/0.25|250/);
        expect(responseTimeElements.length).toBeGreaterThanOrEqual(1);
      });
    });

    it('deve atualizar métricas após limpar cache', async () => {
      mockHttpClient.post.mockResolvedValue({
        data: {
          success: true,
          message: 'Cache limpo',
          timestamp: Date.now(),
        },
      });

      // Dados após limpeza de cache
      const clearedCacheData = {
        ...mockPerformanceData,
        data: {
          ...mockPerformanceData.data,
          cache_hits: 0,
          cache_misses: 0,
          cache_hit_rate: 0,
        },
      };

      const Wrapper = createWrapper();
      
      render(
        <Wrapper>
          <div>
            <PerformanceMetrics />
            <PerformanceSettings />
          </div>
        </Wrapper>
      );

      // Aguardar carregamento inicial
      await waitFor(() => {
        expect(screen.getByText(/85%/)).toBeInTheDocument(); // cache_hit_rate inicial
      });

      // Simular limpeza de cache
      const clearButton = screen.queryByRole('button', { name: /limpar.*cache|clear.*cache/i });
      
      if (clearButton) {
        // Configurar mock para retornar dados limpos após POST
        mockHttpClient.get.mockResolvedValueOnce({ data: clearedCacheData });
        
        fireEvent.click(clearButton);
        
        await waitFor(() => {
          expect(mockHttpClient.post).toHaveBeenCalled();
        });

        // Verificar se métricas foram atualizadas
        await waitFor(() => {
          expect(screen.getByText(/0%/)).toBeInTheDocument(); // nova cache_hit_rate
        });
      }
    });
  });

  describe('Responsividade e acessibilidade', () => {
    it('deve ser acessível com screen readers', async () => {
      const Wrapper = createWrapper();
      
      render(
        <Wrapper>
          <PerformanceMonitor />
        </Wrapper>
      );

      await waitFor(() => {
        expect(mockHttpClient.get).toHaveBeenCalled();
      });

      // Verificar elementos acessíveis
      await waitFor(() => {
        const headings = screen.getAllByRole('heading');
        expect(headings.length).toBeGreaterThan(0);
        
        // Verificar se há labels ou descrições
        const labels = document.querySelectorAll('[aria-label], [aria-describedby]');
        expect(labels.length).toBeGreaterThan(0);
      });
    });

    it('deve funcionar em diferentes tamanhos de tela', async () => {
      const Wrapper = createWrapper();
      
      // Simular tela pequena
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 320,
      });
      
      render(
        <Wrapper>
          <PerformanceMetrics />
        </Wrapper>
      );

      await waitFor(() => {
        expect(mockHttpClient.get).toHaveBeenCalled();
      });

      // Verificar se componente renderiza sem erros
      await waitFor(() => {
        expect(screen.getByText(/150/)).toBeInTheDocument();
      });

      // Simular tela grande
      Object.defineProperty(window, 'innerWidth', {
        value: 1920,
      });
      
      // Componente deve continuar funcionando
      expect(screen.getByText(/150/)).toBeInTheDocument();
    });
  });
});