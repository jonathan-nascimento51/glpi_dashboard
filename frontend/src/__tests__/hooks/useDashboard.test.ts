/**
 * Testes para o hook useDashboard
 */

import { renderHook, waitFor, act } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { useDashboard } from '../../hooks/useDashboard';
import { TestWrapper, createMockResponse, mockMetricsData, mockTechniciansData, mockSystemStatus } from '../setup';

// Mock do fetch
const mockFetch = vi.fn();
global.fetch = mockFetch;

// Mock das funções de API
vi.mock('../../services/api', async () => {
  const actual = await vi.importActual('../../services/api');
  return {
    ...actual,
    fetchDashboardMetrics: vi.fn(),
    getSystemStatus: vi.fn(),
    getTechnicianRanking: vi.fn(),
  };
});

import { fetchDashboardMetrics, getSystemStatus, getTechnicianRanking } from '../../services/api';

const mockFetchDashboardMetrics = fetchDashboardMetrics as any;
const mockGetSystemStatus = getSystemStatus as any;
const mockGetTechnicianRanking = getTechnicianRanking as any;

describe('useDashboard Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    
    // Mock das funções de API
    mockFetchDashboardMetrics.mockResolvedValue(mockMetricsData);
    mockGetSystemStatus.mockResolvedValue(mockSystemStatus);
    mockGetTechnicianRanking.mockResolvedValue(mockTechniciansData);
    
    // Mock successful responses by default
    mockFetch.mockImplementation((url: string) => {
      if (url.includes('/api/dashboard/metrics')) {
        return createMockResponse({ success: true, data: mockMetricsData });
      }
      if (url.includes('/api/technicians/ranking')) {
        return createMockResponse({ success: true, data: mockTechniciansData });
      }
      if (url.includes('/api/status')) {
        return createMockResponse({ success: true, data: mockSystemStatus });
      }
      return createMockResponse({ success: true, data: {} });
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Inicialização', () => {
    it('deve inicializar com estado padrão', () => {
      const { result } = renderHook(() => useDashboard(), {
        wrapper: TestWrapper,
      });

      expect(result.current.isLoading).toBe(true);
      expect(result.current.metrics).toBeNull();
      expect(result.current.technicianRanking).toEqual([]);
      expect(result.current.systemStatus).toMatchObject({
        api: 'offline',
        glpi: 'offline',
        status: 'offline',
        sistema_ativo: false
      });
      expect(result.current.notifications).toEqual([]);
      expect(result.current.filters).toEqual({});
    });

    it('deve carregar dados iniciais automaticamente', async () => {
      const { result } = renderHook(() => useDashboard(), {
        wrapper: TestWrapper,
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.metrics).toMatchObject(mockMetricsData);
      expect(result.current.technicianRanking).toEqual(mockTechniciansData);
      expect(result.current.systemStatus).toEqual(mockSystemStatus);
    });
  });

  describe('Carregamento de Dados', () => {
    it('deve chamar loadData e atualizar estado', async () => {
      const { result } = renderHook(() => useDashboard(), {
        wrapper: TestWrapper,
      });

      await act(async () => {
        await result.current.loadData();
      });

      expect(mockFetchDashboardMetrics).toHaveBeenCalled();
      expect(mockGetSystemStatus).toHaveBeenCalled();
      expect(mockGetTechnicianRanking).toHaveBeenCalled();
      expect(result.current.metrics).toMatchObject(mockMetricsData);
      expect(result.current.systemStatus).toEqual(mockSystemStatus);
      expect(result.current.technicianRanking).toEqual(mockTechniciansData);
    });

    it('deve aplicar filtros de data nas requisições', async () => {
      const { result } = renderHook(() => useDashboard(), {
        wrapper: TestWrapper,
      });

      const startDate = '2024-01-01';
      const endDate = '2024-01-31';

      await act(async () => {
        result.current.updateFilters({
          dateRange: { startDate: startDate, endDate: endDate }
        });
      });

      await waitFor(() => {
        expect(mockFetchDashboardMetrics).toHaveBeenCalledWith(
          expect.objectContaining({
            dateRange: { start: startDate, end: endDate }
          }),
          expect.any(Object)
        );
      });
    });

    it('deve lidar com erro de carregamento', async () => {
      mockFetchDashboardMetrics.mockRejectedValueOnce(new Error('Network error'));
      mockGetSystemStatus.mockRejectedValueOnce(new Error('Network error'));
      mockGetTechnicianRanking.mockRejectedValueOnce(new Error('Network error'));

      const { result } = renderHook(() => useDashboard(), {
        wrapper: TestWrapper,
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Deve adicionar notificação de erro
      expect(result.current.notifications).toHaveLength(1);
      expect(result.current.notifications[0].type).toBe('error');
    });
  });

  describe('Filtros', () => {
    it('deve atualizar filtros corretamente', async () => {
      const { result } = renderHook(() => useDashboard(), {
        wrapper: TestWrapper,
      });

      const newFilters = {
        dateRange: {
          startDate: '2024-01-01',
          endDate: '2024-01-31'
        },
        status: ['new'],
        level: 'n1' as const
      };

      await act(async () => {
        result.current.updateFilters(newFilters);
      });

      expect(result.current.filters.dateRange?.startDate).toBe('2024-01-01');
      expect(result.current.filters.dateRange?.endDate).toBe('2024-01-31');
      expect(result.current.filters.status).toEqual(['new']);
      expect(result.current.filters.level).toBe('n1');
    });

    it('deve recarregar dados quando filtros mudarem', async () => {
      const { result } = renderHook(() => useDashboard(), {
        wrapper: TestWrapper,
      });

      // Aguardar carregamento inicial
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      const initialCallCount = mockFetchDashboardMetrics.mock.calls.length;

      await act(async () => {
        result.current.updateFilters({
          status: ['pending']
        });
      });

      await waitFor(() => {
        expect(mockFetchDashboardMetrics.mock.calls.length).toBeGreaterThan(initialCallCount);
      });
    });

    it('deve validar formato de data', async () => {
      const { result } = renderHook(() => useDashboard(), {
        wrapper: TestWrapper,
      });

      await act(async () => {
        result.current.updateDateRange({
          start: 'invalid-date',
          end: '2024-01-31'
        });
      });

      // Deve adicionar notificação de erro
      expect(result.current.notifications).toHaveLength(1);
      expect(result.current.notifications[0].type).toBe('error');
      expect(result.current.notifications[0].message).toContain('data');
    });
  });

  describe('Notificações', () => {
    it('deve adicionar notificação', async () => {
      const { result } = renderHook(() => useDashboard(), {
        wrapper: TestWrapper,
      });

      const notification = {
        type: 'success' as const,
        message: 'Teste de notificação',
        duration: 3000
      };

      act(() => {
        result.current.addNotification(notification);
      });

      expect(result.current.notifications).toHaveLength(1);
      expect(result.current.notifications[0]).toMatchObject(notification);
      expect(result.current.notifications[0].id).toBeDefined();
    });

    it('deve remover notificação', async () => {
      const { result } = renderHook(() => useDashboard(), {
        wrapper: TestWrapper,
      });

      // Adicionar notificação
      act(() => {
        result.current.addNotification({
          type: 'info',
          message: 'Teste'
        });
      });

      const notificationId = result.current.notifications[0].id;

      // Remover notificação
      act(() => {
        result.current.removeNotification(notificationId);
      });

      expect(result.current.notifications).toHaveLength(0);
    });

    it.skip('deve remover notificação automaticamente após duração', async () => {
      vi.useFakeTimers();

      const { result } = renderHook(() => useDashboard(), {
        wrapper: TestWrapper,
      });

      act(() => {
        result.current.addNotification({
          type: 'info',
          message: 'Teste',
          duration: 1000
        });
      });

      expect(result.current.notifications).toHaveLength(1);

      // Avançar tempo
      act(() => {
        vi.advanceTimersByTime(1000);
      });

      await waitFor(() => {
        expect(result.current.notifications).toHaveLength(0);
      });

      vi.useRealTimers();
    });
  });

  describe('Tema', () => {
    it('deve alternar tema', () => {
      const { result } = renderHook(() => useDashboard(), {
        wrapper: TestWrapper,
      });

      const initialTheme = result.current.theme;

      act(() => {
        result.current.changeTheme('dark');
      });

      expect(result.current.theme).not.toBe(initialTheme);
    });

    it('deve definir tema específico', () => {
      const { result } = renderHook(() => useDashboard(), {
        wrapper: TestWrapper,
      });

      act(() => {
        result.current.changeTheme('dark');
      });

      expect(result.current.theme).toBe('dark');

      act(() => {
        result.current.changeTheme('light');
      });

      expect(result.current.theme).toBe('light');
    });

    it('deve persistir tema no localStorage', () => {
      const { result } = renderHook(() => useDashboard(), {
        wrapper: TestWrapper,
      });

      act(() => {
        result.current.changeTheme('dark');
      });

      expect(localStorage.setItem).toHaveBeenCalledWith(
        'dashboard-theme',
        'dark'
      );
    });
  });

  describe('Performance', () => {
    it.skip('deve debounce atualizações de filtro', async () => {
      vi.useFakeTimers();

      const { result } = renderHook(() => useDashboard(), {
        wrapper: TestWrapper,
      });

      // Aguardar carregamento inicial
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      const initialCallCount = mockFetch.mock.calls.length;

      // Fazer múltiplas atualizações rapidamente
      act(() => {
        result.current.updateFilters({ status: ['new'] });
        result.current.updateFilters({ status: ['pending'] });
        result.current.updateFilters({ status: ['resolved'] });
      });

      // Avançar tempo para trigger debounce
      act(() => {
        vi.advanceTimersByTime(500);
      });

      await waitFor(() => {
        // Deve ter feito apenas uma chamada adicional
        expect(mockFetch.mock.calls.length).toBe(initialCallCount + 3); // Uma para cada endpoint
      });

      vi.useRealTimers();
    });

    it('deve cancelar requisições em andamento', async () => {
      const abortSpy = vi.fn();
      const mockAbortController = {
        abort: abortSpy,
        signal: { aborted: false }
      };

      vi.spyOn(window, 'AbortController').mockImplementation(
        () => mockAbortController as any
      );

      const { result, unmount } = renderHook(() => useDashboard(), {
        wrapper: TestWrapper,
      });

      // Iniciar carregamento
      act(() => {
        result.current.loadData();
      });

      // Desmontar componente
      unmount();

      // Verificar que requisições foram canceladas
      expect(abortSpy).toHaveBeenCalled();
    });
  });

  describe('Cache', () => {
    it.skip('deve usar dados em cache quando disponíveis', async () => {
      // Primeiro render
      const { result: result1, unmount: unmount1 } = renderHook(() => useDashboard(), {
        wrapper: TestWrapper,
      });

      await waitFor(() => {
        expect(result1.current.isLoading).toBe(false);
      });

      const firstCallCount = mockFetch.mock.calls.length;
      unmount1();

      // Segundo render - deve usar cache
      const { result: result2 } = renderHook(() => useDashboard(), {
        wrapper: TestWrapper,
      });

      await waitFor(() => {
        expect(result2.current.isLoading).toBe(false);
      });

      // Não deve fazer novas chamadas se dados estão em cache
      expect(mockFetch.mock.calls.length).toBe(firstCallCount);
    });

    it.skip('deve invalidar cache quando necessário', async () => {
      const { result } = renderHook(() => useDashboard(), {
        wrapper: TestWrapper,
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      const initialCallCount = mockFetch.mock.calls.length;

      // Forçar recarregamento
      await act(async () => {
        await result.current.loadData(); // force refresh
      });

      expect(mockFetch.mock.calls.length).toBeGreaterThan(initialCallCount);
    });
  });

  describe('Estados de Erro', () => {
    it.skip('deve lidar com erro de rede', async () => {
      mockFetchDashboardMetrics.mockRejectedValueOnce(new Error('Network error'));

      const { result } = renderHook(() => useDashboard(), {
        wrapper: TestWrapper,
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.notifications).toHaveLength(1);
      expect(result.current.notifications[0].type).toBe('error');
    });

    it.skip('deve lidar com resposta inválida da API', async () => {
      mockFetchDashboardMetrics.mockRejectedValueOnce(new Error('Invalid data'));

      const { result } = renderHook(() => useDashboard(), {
        wrapper: TestWrapper,
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.notifications).toHaveLength(1);
      expect(result.current.notifications[0].type).toBe('error');
    });

    it.skip('deve permitir recarregar dados após erro', async () => {
      // Mock inicial com erro
      mockFetchDashboardMetrics.mockRejectedValueOnce(new Error('Network error'));
      
      const { result } = renderHook(() => useDashboard(), {
        wrapper: TestWrapper,
      });

      // Aguardar erro inicial
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      }, { timeout: 3000 });

      // Verificar que houve erro
      expect(result.current.error).toBeTruthy();
      expect(result.current.notifications).toHaveLength(1);
      expect(result.current.notifications[0].type).toBe('error');

      // Resetar para sucesso e tentar novamente
      mockFetchDashboardMetrics.mockResolvedValueOnce(mockMetricsData);
      
      await act(async () => {
        await result.current.loadData();
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      }, { timeout: 3000 });

      expect(result.current.error).toBeNull();
      expect(result.current.metrics).toEqual(mockMetricsData);
    });
  });

  describe('Integração com Date Range', () => {
    it('deve atualizar range de data corretamente', async () => {
      const { result } = renderHook(() => useDashboard(), {
        wrapper: TestWrapper,
      });

      const newRange = {
        start: '2024-01-01',
        end: '2024-01-31'
      };

      await act(async () => {
        result.current.updateDateRange(newRange);
      });

      expect(result.current.filters.dateRange).toEqual(newRange);
    });

    it('deve validar ordem das datas', async () => {
      const { result } = renderHook(() => useDashboard(), {
        wrapper: TestWrapper,
      });

      await act(async () => {
        result.current.updateDateRange({ start: '2024-01-31', end: '2024-01-01' }); // Data fim antes do início
      });

      expect(result.current.notifications).toHaveLength(1);
      expect(result.current.notifications[0].type).toBe('error');
    });
  });
});