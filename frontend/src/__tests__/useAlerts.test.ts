/**
 * Testes para os hooks de alertas
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import {
  useAlerts,
  useAlertsByCategory,
  useAlertsByType,
  useAlertStats,
  useCriticalAlerts,
  useAlertConfig,
  useAlertNotifications
} from '../hooks/useAlerts';
import { alertService } from '../services/alertService';

// Mock do alertService
vi.mock('../services/alertService', () => ({
  alertService: {
    getAlerts: vi.fn(),
    getActiveAlerts: vi.fn(),
    resolveAlert: vi.fn(),
    resolveAllAlerts: vi.fn(),
    clearOldAlerts: vi.fn(),
    updateConfig: vi.fn(),
    getConfig: vi.fn(),
    createAlert: vi.fn(),
    start: vi.fn(),
    stop: vi.fn(),
    addListener: vi.fn(),
    removeListener: vi.fn()
  }
}));

const mockAlertService = alertService as any;

describe('useAlerts Hook', () => {
  const mockAlerts = [
    {
      id: 'alert-1',
      type: 'warning' as const,
      category: 'performance' as const,
      title: 'Performance Warning',
      message: 'High response time detected',
      timestamp: new Date('2024-01-01T10:00:00Z'),
      resolved: false
    },
    {
      id: 'alert-2',
      type: 'error' as const,
      category: 'cache' as const,
      title: 'Cache Error',
      message: 'Cache hit rate too low',
      timestamp: new Date('2024-01-01T11:00:00Z'),
      resolved: false
    },
    {
      id: 'alert-3',
      type: 'critical' as const,
      category: 'api' as const,
      title: 'API Critical',
      message: 'API endpoint down',
      timestamp: new Date('2024-01-01T12:00:00Z'),
      resolved: true
    }
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    mockAlertService.getAlerts.mockReturnValue(mockAlerts);
    mockAlertService.getActiveAlerts.mockReturnValue(mockAlerts.filter(a => !a.resolved));
    mockAlertService.getConfig.mockReturnValue({
      checkInterval: 30000,
      maxAlerts: 100,
      enableBrowserNotifications: true,
      enableSound: false,
      thresholds: []
    });
  });

  describe('useAlerts', () => {
    it('deve retornar todos os alertas', () => {
      const { result } = renderHook(() => useAlerts());
      
      expect(result.current.alerts).toEqual(mockAlerts);
      expect(result.current.alerts).toHaveLength(3);
    });

    it('deve retornar alertas ativos', () => {
      const { result } = renderHook(() => useAlerts());
      
      expect(result.current.activeAlerts).toHaveLength(2);
      result.current.activeAlerts.forEach(alert => {
        expect(alert.resolved).toBe(false);
      });
    });

    it('deve retornar configuração atual', () => {
      const { result } = renderHook(() => useAlerts());
      
      expect(result.current.config).toBeDefined();
      expect(result.current.isRunning).toBe(true);
    });

    it('deve permitir criar alertas manuais', () => {
      const { result } = renderHook(() => useAlerts());
      
      expect(typeof result.current.createAlert).toBe('function');
      expect(typeof result.current.startMonitoring).toBe('function');
      expect(typeof result.current.stopMonitoring).toBe('function');
    });

    it('deve calcular alertas ativos corretamente', () => {
      const { result } = renderHook(() => useAlerts());
      
      expect(result.current.activeAlerts).toHaveLength(2);
      result.current.activeAlerts.forEach(alert => {
        expect(alert.resolved).toBe(false);
      });
    });

    it('deve resolver alerta específico', () => {
      const { result } = renderHook(() => useAlerts());
      
      act(() => {
        result.current.resolveAlert('alert-1');
      });
      
      expect(mockAlertService.resolveAlert).toHaveBeenCalledWith('alert-1');
    });

    it('deve resolver todos os alertas', () => {
      const { result } = renderHook(() => useAlerts());
      
      act(() => {
        result.current.resolveAllAlerts();
      });
      
      expect(mockAlertService.resolveAllAlerts).toHaveBeenCalled();
    });

    it('deve limpar alertas antigos', () => {
      const { result } = renderHook(() => useAlerts());
      const maxAge = 24 * 60 * 60 * 1000; // 24 horas
      
      act(() => {
        result.current.clearOldAlerts(maxAge);
      });
      
      expect(mockAlertService.clearOldAlerts).toHaveBeenCalledWith(maxAge);
    });

    it('deve atualizar configuração', () => {
      const { result } = renderHook(() => useAlerts());
      const newConfig = { enableNotifications: false };
      
      act(() => {
        result.current.updateConfig(newConfig);
      });
      
      expect(mockAlertService.updateConfig).toHaveBeenCalledWith(newConfig);
    });

    it('deve criar alerta manual', () => {
      const { result } = renderHook(() => useAlerts());
      
      act(() => {
        result.current.createAlert('warning', 'performance', 'Test Alert', 'Test message');
      });
      
      expect(mockAlertService.createAlert).toHaveBeenCalledWith(
        'warning',
        'performance',
        'Test Alert',
        'Test message',
        undefined
      );
    });

    it('deve iniciar monitoramento', () => {
      const { result } = renderHook(() => useAlerts());
      
      act(() => {
        result.current.startMonitoring();
      });
      
      expect(mockAlertService.start).toHaveBeenCalled();
    });

    it('deve parar monitoramento', () => {
      const { result } = renderHook(() => useAlerts());
      
      act(() => {
        result.current.stopMonitoring();
      });
      
      expect(mockAlertService.stop).toHaveBeenCalled();
    });

    it('deve atualizar alertas quando listener é chamado', () => {
      let listener: Function;
      mockAlertService.addListener.mockImplementation((fn) => {
        listener = fn;
      });
      
      const { result, rerender } = renderHook(() => useAlerts());
      
      // Simular novo alerta
      const newAlert = {
        id: 'alert-4',
        type: 'info' as const,
        category: 'system' as const,
        title: 'New Alert',
        message: 'New alert message',
        timestamp: new Date(),
        resolved: false
      };
      
      mockAlertService.getAlerts.mockReturnValue([...mockAlerts, newAlert]);
      
      act(() => {
        listener!(newAlert);
      });
      
      rerender();
      
      expect(result.current.alerts).toHaveLength(4);
    });
  });

  describe('useAlertsByCategory', () => {
    it('deve retornar alertas filtrados por categoria', () => {
      const { result } = renderHook(() => useAlertsByCategory('performance'));
      
      expect(result.current.alerts).toHaveLength(1);
      expect(result.current.alerts[0].category).toBe('performance');
      expect(result.current.count).toBe(1);
    });

    it('deve retornar array vazio para categoria inexistente', () => {
      const { result } = renderHook(() => useAlertsByCategory('unknown' as any));
      
      expect(result.current.alerts).toHaveLength(0);
      expect(result.current.activeAlerts).toHaveLength(0);
      expect(result.current.count).toBe(0);
      expect(result.current.activeCount).toBe(0);
    });
  });

  describe('useAlertsByType', () => {
    it('deve retornar alertas filtrados por tipo', () => {
      const { result } = renderHook(() => useAlertsByType('critical'));
      
      expect(result.current.alerts).toHaveLength(1);
      expect(result.current.alerts[0].type).toBe('critical');
      expect(result.current.count).toBe(1);
    });

    it('deve retornar array vazio para tipo inexistente', () => {
      const { result } = renderHook(() => useAlertsByType('unknown' as any));
      
      expect(result.current.alerts).toHaveLength(0);
      expect(result.current.activeAlerts).toHaveLength(0);
      expect(result.current.count).toBe(0);
      expect(result.current.activeCount).toBe(0);
    });
  });

  describe('useAlertStats', () => {
    it('deve calcular estatísticas dos alertas', () => {
      const { result } = renderHook(() => useAlertStats());
      
      expect(result.current.total).toBe(3);
      expect(result.current.active).toBe(2);
      expect(result.current.resolved).toBe(1);
      expect(result.current.byType.warning).toBe(1);
      expect(result.current.byType.error).toBe(1);
      expect(result.current.byType.critical).toBe(1);
      expect(result.current.byType.info).toBeUndefined();
      expect(result.current.byCategory.performance).toBe(1);
      expect(result.current.byCategory.cache).toBe(1);
      expect(result.current.byCategory.api).toBe(1);
      expect(result.current.byCategory.system).toBeUndefined();
    });

    it('deve retornar estatísticas zeradas quando não há alertas', () => {
      mockAlertService.getAlerts.mockReturnValue([]);
      
      const { result } = renderHook(() => useAlertStats());
      
      expect(result.current.total).toBe(0);
      expect(result.current.active).toBe(0);
      expect(result.current.resolved).toBe(0);
      expect(Object.keys(result.current.byType)).toHaveLength(0);
      expect(Object.keys(result.current.byCategory)).toHaveLength(0);
      expect(result.current.recentCount).toBe(0);
    });
  });

  describe('useCriticalAlerts', () => {
    it('deve retornar apenas alertas críticos', () => {
      const { result } = renderHook(() => useCriticalAlerts());
      
      // Já existe um alerta crítico nos dados de mock (alert-3)
      expect(result.current.alerts).toHaveLength(1);
      expect(result.current.alerts[0].type).toBe('critical');
      expect(result.current.alerts[0].id).toBe('alert-3');
      expect(result.current.count).toBe(1);
      expect(result.current.hasUnresolved).toBe(false); // alert-3 está resolvido
    });

    it('deve retornar array vazio quando não há alertas críticos', () => {
      mockAlertService.getAlerts.mockReturnValue(
        mockAlerts.filter(a => a.type !== 'critical')
      );
      
      const { result } = renderHook(() => useCriticalAlerts());
      
      expect(result.current.alerts).toHaveLength(0);
      expect(result.current.count).toBe(0);
      expect(result.current.hasUnresolved).toBe(false);
    });
  });

  describe('useAlertConfig', () => {
    const mockConfig = {
      checkInterval: 30000,
      maxAlerts: 100,
      enableNotifications: true,
      enableSound: false,
      thresholds: []
    };

    beforeEach(() => {
      mockAlertService.getConfig.mockReturnValue(mockConfig);
    });

    it('deve retornar configuração atual', () => {
      const { result } = renderHook(() => useAlertConfig());
      
      expect(result.current.config).toEqual(mockConfig);
    });

    it('deve atualizar configuração', () => {
      const { result } = renderHook(() => useAlertConfig());
      const newConfig = { enableNotifications: false };
      
      act(() => {
        result.current.updateConfig(newConfig);
      });
      
      expect(mockAlertService.updateConfig).toHaveBeenCalledWith(newConfig);
    });
  });

  describe('useAlertNotifications', () => {
    beforeEach(() => {
      // Mock do Notification API
      global.Notification = {
        permission: 'granted',
        requestPermission: vi.fn().mockResolvedValue('granted')
      } as any;
    });

    it('deve verificar se notificações estão habilitadas', () => {
      mockAlertService.getConfig.mockReturnValue({
        enableBrowserNotifications: true,
        checkInterval: 30000,
        maxAlerts: 100,
        enableSound: false,
        thresholds: []
      });
      
      const { result } = renderHook(() => useAlertNotifications());
      
      expect(result.current.notificationsEnabled).toBe(true);
    });

    it('deve verificar se notificações estão desabilitadas', () => {
      mockAlertService.getConfig.mockReturnValue({
        enableBrowserNotifications: false,
        checkInterval: 30000,
        maxAlerts: 100,
        enableSound: false,
        thresholds: []
      });
      
      const { result } = renderHook(() => useAlertNotifications());
      
      expect(result.current.notificationsEnabled).toBe(false);
    });

    it('deve verificar se permissão foi concedida', () => {
      const { result } = renderHook(() => useAlertNotifications());
      
      expect(result.current.hasPermission).toBe(true);
    });

    it('deve verificar se permissão foi negada', () => {
      global.Notification.permission = 'denied';
      
      const { result } = renderHook(() => useAlertNotifications());
      
      expect(result.current.hasPermission).toBe(false);
    });

    it('deve solicitar permissão', async () => {
      const { result } = renderHook(() => useAlertNotifications());
      
      await act(async () => {
        await result.current.requestPermission();
      });
      
      expect(global.Notification.requestPermission).toHaveBeenCalled();
    });

    it('deve habilitar notificações', () => {
      const { result } = renderHook(() => useAlertNotifications());
      
      act(() => {
        result.current.enableNotifications();
      });
      
      expect(mockAlertService.updateConfig).toHaveBeenCalledWith({
        enableBrowserNotifications: true
      });
    });

    it('deve desabilitar notificações', () => {
      const { result } = renderHook(() => useAlertNotifications());
      
      act(() => {
        result.current.disableNotifications();
      });
      
      expect(mockAlertService.updateConfig).toHaveBeenCalledWith({
        enableBrowserNotifications: false
      });
    });
  });

  describe('Cleanup', () => {
    it('deve remover listener ao desmontar', () => {
      const { unmount } = renderHook(() => useAlerts());
      
      unmount();
      
      expect(mockAlertService.removeListener).toHaveBeenCalled();
    });

    it('deve remover listener correto ao desmontar múltiplos hooks', () => {
      const { unmount: unmount1 } = renderHook(() => useAlerts());
      const { unmount: unmount2 } = renderHook(() => useAlerts());
      
      unmount1();
      
      // Deve ter sido chamado apenas uma vez para o primeiro hook
      expect(mockAlertService.removeListener).toHaveBeenCalledTimes(1);
      
      unmount2();
      
      // Deve ter sido chamado novamente para o segundo hook
      expect(mockAlertService.removeListener).toHaveBeenCalledTimes(2);
    });
  });
});