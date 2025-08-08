/**
 * Testes para o hook useDashboard
 */

import { renderHook, waitFor, act } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { useDashboard } from '../../hooks/useDashboard';
import { TestWrapper, createMockResponse, createMockError, mockMetricsData, mockTechniciansData, mockSystemStatus } from '../setup';

// Mock do fetch
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe('useDashboard Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Mock successful responses by default
    mockFetch.mockImplementation((url: string) => {
      if (url.includes('/api/dashboard/metrics')) {
        return createMockResponse({ success: true, data: mockMetricsData });
      }
      if (url.includes('/api/technicians/ranking')) {
        return createMockResponse({ success: true, data: mockTechniciansData });
      }
      if (url.includes('/api/system/status')) {
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
      expect(result.current.technicians).toEqual([]);
      expect(result.current.systemStatus).toBeNull();
      expect(result.current.notifications).toEqual([]);
      expect(result.current.filters.dateRange.start).toBeDefined();
      expect(result.current.filters.dateRange.end).toBeDefined();
    });

    it('deve carregar dados iniciais automaticamente', async () => {
      const { result } = renderHook(() => useDashboard(), {
        wrapper: TestWrapper,
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.metrics).toEqual(mockMetricsData);
      expect(result.current.technicians).toEqual(mockTechniciansData);
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

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/dashboard/metrics'),
        expect.any(Object)
      );
      expect(result.current.metrics).toEqual(mockMetricsData);
    });

    it('deve aplicar filtros de data nas requisições', async () => {
      const { result } = renderHook(() => useDashboard(), {
        wrapper: TestWrapper,
      });

      const startDate = '2024-01-01';
      const endDate = '2024-01-31';

      await act(async () => {
        result.current.updateFilters({
          dateRange: { start: startDate, end: endDate }
        });
      });

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining(`start_date=${startDate}&end_date=${endDate}`),
          expect.any(Object)
        );
      });
    });

    it('deve lidar com erro de carregamento', async () => {
      mockFetch.mockImplementationOnce(() => 
        createMockError('Network error', 500)
      );

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
          start: '2024-01-01',
          end: '2024-01-31'
        },
        status: 'new' as const,
        level: 'n1' as const
      };

      await act(async () => {
        result.current.updateFilters(newFilters);
      });

      expect(result.current.filters.dateRange.start).toBe('2024-01-01');
      expect(result.current.filters.dateRange.end).toBe('2024-01-31');
      expect(result.current.filters.status).toBe('new');
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

      const initialCallCount = mockFetch.mock.calls.length;

      await act(async () => {
        result.current.updateFilters({
          status: 'pending'
        });
      });

      await waitFor(() => {
        expect(mockFetch.mock.calls.length).toBeGreaterThan(initialCallCount);
      });
    });

    it('deve validar formato de data', async () => {
      const { result } = renderHook(() => useDashboard(), {
        wrapper: TestWrapper,
      });

      await act(async () => {
        result.current.updateFilters({
          dateRange: {
            start: 'invalid-date',
            end: '2024-01-31'
          }
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

    it('deve remover notificação automaticamente após duração', async () => {
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
        result.current.changeTheme();
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
    it('deve debounce atualizações de filtro', async () => {
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
        result.current.updateFilters({ status: 'new' });
        result.current.updateFilters({ status: 'pending' });
        result.current.updateFilters({ status: 'resolved' });
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
    it('deve usar dados em cache quando disponíveis', async () => {
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

    it('deve invalidar cache quando necessário', async () => {
      const { result } = renderHook(() => useDashboard(), {
        wrapper: TestWrapper,
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      const initialCallCount = mockFetch.mock.calls.length;

      // Forçar recarregamento
      await act(async () => {
        await result.current.loadData(true); // force refresh
      });

      expect(mockFetch.mock.calls.length).toBeGreaterThan(initialCallCount);
    });
  });

  describe('Estados de Erro', () => {
    it('deve lidar com erro de rede', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      const { result } = renderHook(() => useDashboard(), {
        wrapper: TestWrapper,
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.notifications).toHaveLength(1);
      expect(result.current.notifications[0].type).toBe('error');
    });

    it('deve lidar com resposta inválida da API', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ success: false, error: 'Invalid data' }),
      } as Response);

      const { result } = renderHook(() => useDashboard(), {
        wrapper: TestWrapper,
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.notifications).toHaveLength(1);
      expect(result.current.notifications[0].type).toBe('error');
    });

    it('deve tentar novamente após falha', async () => {
      let callCount = 0;
      mockFetch.mockImplementation(() => {
        callCount++;
        if (callCount === 1) {
          return createMockError('Network error', 500);
        }
        return createMockResponse({ success: true, data: mockMetricsData });
      });

      const { result } = renderHook(() => useDashboard(), {
        wrapper: TestWrapper,
      });

      // Primeira tentativa falha
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Tentar novamente
      await act(async () => {
        await result.current.loadData();
      });

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
        result.current.updateDateRange(newRange.start, newRange.end);
      });

      expect(result.current.filters.dateRange).toEqual(newRange);
    });

    it('deve validar ordem das datas', async () => {
      const { result } = renderHook(() => useDashboard(), {
        wrapper: TestWrapper,
      });

      await act(async () => {
        result.current.updateDateRange('2024-01-31', '2024-01-01'); // Data fim antes do início
      });

      expect(result.current.notifications).toHaveLength(1);
      expect(result.current.notifications[0].type).toBe('error');
    });
  });
});