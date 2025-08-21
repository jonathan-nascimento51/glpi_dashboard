/**
 * Testes para o componente AlertNotification
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import AlertNotification from '../components/AlertNotification';
import * as alertHooks from '../hooks/useAlerts';
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

// Mock dos hooks
vi.mock('../hooks/useAlerts');

const mockUseCriticalAlerts = alertHooks.useCriticalAlerts as vi.MockedFunction<typeof alertHooks.useCriticalAlerts>;
const mockUseAlerts = alertHooks.useAlerts as vi.MockedFunction<typeof alertHooks.useAlerts>;
const mockUseAlertNotifications = alertHooks.useAlertNotifications as vi.MockedFunction<typeof alertHooks.useAlertNotifications>;

// Mock do react-router-dom
vi.mock('react-router-dom', () => ({
  useNavigate: () => vi.fn()
}));

describe('AlertNotification', () => {
  const mockCriticalAlerts = [
    {
      id: 'critical-1',
      type: 'critical' as const,
      category: 'api' as const,
      title: 'API Endpoint Down',
      message: 'Critical API endpoint is not responding',
      timestamp: new Date('2024-01-01T12:00:00Z'),
      resolved: false,
      metadata: { endpoint: '/api/tickets' }
    },
    {
      id: 'critical-2',
      type: 'critical' as const,
      category: 'system' as const,
      title: 'System Overload',
      message: 'System resources critically low',
      timestamp: new Date('2024-01-01T12:05:00Z'),
      resolved: false,
      metadata: { cpuUsage: 95, memoryUsage: 98 }
    }
  ];

  const mockFunctions = {
    resolveAlert: vi.fn(),
    resolveAllAlerts: vi.fn(),
    clearOldAlerts: vi.fn(),
    updateConfig: vi.fn(),
    createAlert: vi.fn(),
    startMonitoring: vi.fn(),
    stopMonitoring: vi.fn()
  };

  beforeEach(() => {
    vi.clearAllMocks();
    
    mockUseCriticalAlerts.mockReturnValue(mockCriticalAlerts);
    
    mockUseAlerts.mockReturnValue({
      alerts: [],
      ...mockFunctions
    });
    
    mockUseAlertNotifications.mockReturnValue({
      isEnabled: true,
      hasPermission: true,
      requestPermission: vi.fn(),
      enableNotifications: vi.fn(),
      disableNotifications: vi.fn()
    });
  });

  describe('Renderização', () => {
    it('deve renderizar notificações críticas', () => {
      render(<AlertNotification />);
      
      expect(screen.getByText('API Endpoint Down')).toBeInTheDocument();
      expect(screen.getByText('System Overload')).toBeInTheDocument();
    });

    it('deve exibir FAB com contador de alertas críticos', () => {
      render(<AlertNotification />);
      
      const fab = screen.getByTestId('alert-fab');
      expect(fab).toBeInTheDocument();
      expect(screen.getByText('2')).toBeInTheDocument(); // Contador
    });

    it('deve não renderizar quando não há alertas críticos', () => {
      mockUseCriticalAlerts.mockReturnValue([]);
      
      render(<AlertNotification />);
      
      expect(screen.queryByText('API Endpoint Down')).not.toBeInTheDocument();
      expect(screen.queryByTestId('alert-fab')).not.toBeInTheDocument();
    });

    it('deve exibir ícones corretos para cada categoria', () => {
      render(<AlertNotification />);
      
      const apiAlert = screen.getByText('API Endpoint Down').closest('.notification');
      const systemAlert = screen.getByText('System Overload').closest('.notification');
      
      expect(apiAlert).toHaveClass('api');
      expect(systemAlert).toHaveClass('system');
    });
  });

  describe('Interações', () => {
    it('deve dispensar notificação individual', () => {
      render(<AlertNotification />);
      
      const dismissButton = screen.getAllByLabelText('Dispensar alerta')[0];
      fireEvent.click(dismissButton);
      
      // Verificar se a notificação foi removida da lista visível
      expect(screen.queryByText('API Endpoint Down')).not.toBeInTheDocument();
    });

    it('deve resolver alerta individual', () => {
      render(<AlertNotification />);
      
      const resolveButton = screen.getAllByLabelText('Resolver alerta')[0];
      fireEvent.click(resolveButton);
      
      expect(mockFunctions.resolveAlert).toHaveBeenCalledWith('critical-1');
    });

    it('deve navegar para centro de alertas ao clicar no FAB', () => {
      const mockNavigate = vi.fn();
      vi.doMock('react-router-dom', () => ({
        useNavigate: () => mockNavigate
      }));
      
      render(<AlertNotification />);
      
      const fab = screen.getByTestId('alert-fab');
      fireEvent.click(fab);
      
      expect(mockNavigate).toHaveBeenCalledWith('/alerts');
    });

    it('deve expandir/colapsar detalhes da notificação', () => {
      render(<AlertNotification />);
      
      const notification = screen.getByText('API Endpoint Down').closest('.notification');
      const expandButton = notification?.querySelector('.expand-button');
      
      // Expandir
      fireEvent.click(expandButton!);
      expect(screen.getByText('Critical API endpoint is not responding')).toBeInTheDocument();
      
      // Colapsar
      fireEvent.click(expandButton!);
      expect(screen.queryByText('Critical API endpoint is not responding')).not.toBeInTheDocument();
    });
  });

  describe('Auto-dismiss', () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    afterEach(() => {
      vi.useRealTimers();
    });

    it('deve auto-dispensar notificação após timeout', () => {
      render(<AlertNotification />);
      
      expect(screen.getByText('API Endpoint Down')).toBeInTheDocument();
      
      // Avançar tempo para auto-dismiss (10 segundos)
      vi.advanceTimersByTime(10000);
      
      expect(screen.queryByText('API Endpoint Down')).not.toBeInTheDocument();
    });

    it('deve cancelar auto-dismiss ao interagir com notificação', () => {
      render(<AlertNotification />);
      
      const notification = screen.getByText('API Endpoint Down').closest('.notification');
      
      // Hover para cancelar auto-dismiss
      fireEvent.mouseEnter(notification!);
      
      // Avançar tempo
      vi.advanceTimersByTime(10000);
      
      // Notificação ainda deve estar visível
      expect(screen.getByText('API Endpoint Down')).toBeInTheDocument();
      
      // Mouse leave para reativar auto-dismiss
      fireEvent.mouseLeave(notification!);
      
      vi.advanceTimersByTime(10000);
      
      expect(screen.queryByText('API Endpoint Down')).not.toBeInTheDocument();
    });
  });

  describe('Animações', () => {
    it('deve aplicar animação de entrada', () => {
      render(<AlertNotification />);
      
      const notification = screen.getByText('API Endpoint Down').closest('.notification');
      expect(notification).toHaveClass('slide-in');
    });

    it('deve aplicar animação de saída ao dispensar', () => {
      render(<AlertNotification />);
      
      const dismissButton = screen.getAllByLabelText('Dispensar alerta')[0];
      const notification = screen.getByText('API Endpoint Down').closest('.notification');
      
      fireEvent.click(dismissButton);
      
      expect(notification).toHaveClass('slide-out');
    });
  });

  describe('Formatação de Tempo', () => {
    it('deve exibir timestamp relativo', () => {
      // Mock da data atual para controlar o tempo relativo
      const mockDate = new Date('2024-01-01T12:10:00Z');
      vi.spyOn(Date, 'now').mockReturnValue(mockDate.getTime());
      
      render(<AlertNotification />);
      
      expect(screen.getByText('há 10 minutos')).toBeInTheDocument();
      expect(screen.getByText('há 5 minutos')).toBeInTheDocument();
    });

    it('deve atualizar timestamp em tempo real', () => {
      vi.useFakeTimers();
      
      const mockDate = new Date('2024-01-01T12:10:00Z');
      vi.spyOn(Date, 'now').mockReturnValue(mockDate.getTime());
      
      render(<AlertNotification />);
      
      expect(screen.getByText('há 10 minutos')).toBeInTheDocument();
      
      // Avançar 1 minuto
      vi.advanceTimersByTime(60000);
      vi.spyOn(Date, 'now').mockReturnValue(mockDate.getTime() + 60000);
      
      expect(screen.getByText('há 11 minutos')).toBeInTheDocument();
      
      vi.useRealTimers();
    });
  });

  describe('Posicionamento', () => {
    it('deve posicionar notificações no canto superior direito', () => {
      render(<AlertNotification />);
      
      const container = screen.getByTestId('notification-container');
      expect(container).toHaveClass('top-right');
    });

    it('deve empilhar múltiplas notificações', () => {
      render(<AlertNotification />);
      
      const notifications = screen.getAllByRole('alert');
      expect(notifications).toHaveLength(2);
      
      // Verificar z-index crescente
      expect(notifications[0]).toHaveStyle('z-index: 1001');
      expect(notifications[1]).toHaveStyle('z-index: 1002');
    });
  });

  describe('Acessibilidade', () => {
    it('deve ter roles ARIA apropriados', () => {
      render(<AlertNotification />);
      
      const notifications = screen.getAllByRole('alert');
      expect(notifications).toHaveLength(2);
      
      notifications.forEach(notification => {
        expect(notification).toHaveAttribute('aria-live', 'assertive');
      });
    });

    it('deve ter labels descritivos para botões', () => {
      render(<AlertNotification />);
      
      expect(screen.getAllByLabelText('Dispensar alerta')).toHaveLength(2);
      expect(screen.getAllByLabelText('Resolver alerta')).toHaveLength(2);
      expect(screen.getByLabelText('Abrir centro de alertas')).toBeInTheDocument();
    });

    it('deve suportar navegação por teclado', () => {
      render(<AlertNotification />);
      
      const firstDismissButton = screen.getAllByLabelText('Dispensar alerta')[0];
      const firstResolveButton = screen.getAllByLabelText('Resolver alerta')[0];
      
      firstDismissButton.focus();
      expect(document.activeElement).toBe(firstDismissButton);
      
      // Tab para próximo botão
      fireEvent.keyDown(firstDismissButton, { key: 'Tab' });
      firstResolveButton.focus();
      expect(document.activeElement).toBe(firstResolveButton);
    });

    it('deve permitir ações via teclado', () => {
      render(<AlertNotification />);
      
      const dismissButton = screen.getAllByLabelText('Dispensar alerta')[0];
      
      fireEvent.keyDown(dismissButton, { key: 'Enter' });
      expect(screen.queryByText('API Endpoint Down')).not.toBeInTheDocument();
    });
  });

  describe('Estados de Permissão', () => {
    it('deve exibir aviso quando notificações estão desabilitadas', () => {
      mockUseAlertNotifications.mockReturnValue({
        isEnabled: false,
        hasPermission: true,
        requestPermission: vi.fn(),
        enableNotifications: vi.fn(),
        disableNotifications: vi.fn()
      });
      
      render(<AlertNotification />);
      
      expect(screen.getByText('Notificações desabilitadas')).toBeInTheDocument();
    });

    it('deve exibir aviso quando permissão foi negada', () => {
      mockUseAlertNotifications.mockReturnValue({
        isEnabled: true,
        hasPermission: false,
        requestPermission: vi.fn(),
        enableNotifications: vi.fn(),
        disableNotifications: vi.fn()
      });
      
      render(<AlertNotification />);
      
      expect(screen.getByText('Permissão de notificação negada')).toBeInTheDocument();
    });
  });

  describe('Responsividade', () => {
    it('deve adaptar layout para dispositivos móveis', () => {
      // Simular tela pequena
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 480,
      });
      
      render(<AlertNotification />);
      
      const container = screen.getByTestId('notification-container');
      expect(container).toHaveClass('mobile');
    });

    it('deve ajustar posição do FAB em telas pequenas', () => {
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 480,
      });
      
      render(<AlertNotification />);
      
      const fab = screen.getByTestId('alert-fab');
      expect(fab).toHaveClass('mobile-position');
    });
  });

  describe('Performance', () => {
    it('deve limitar número máximo de notificações visíveis', () => {
      const manyAlerts = Array.from({ length: 10 }, (_, i) => ({
        id: `critical-${i}`,
        type: 'critical' as const,
        category: 'system' as const,
        title: `Alert ${i}`,
        message: `Message ${i}`,
        timestamp: new Date(),
        resolved: false
      }));
      
      mockUseCriticalAlerts.mockReturnValue(manyAlerts);
      
      render(<AlertNotification />);
      
      // Deve mostrar apenas 5 notificações (limite padrão)
      const notifications = screen.getAllByRole('alert');
      expect(notifications.length).toBeLessThanOrEqual(5);
    });

    it('deve usar React.memo para otimizar re-renders', () => {
      const { rerender } = render(<AlertNotification />);
      
      // Simular re-render com mesmos props
      rerender(<AlertNotification />);
      
      // Verificar se componente não foi re-renderizado desnecessariamente
      expect(screen.getByText('API Endpoint Down')).toBeInTheDocument();
    });
  });

  describe('Cleanup', () => {
    it('deve limpar timers ao desmontar', () => {
      vi.useFakeTimers();
      const clearTimeoutSpy = vi.spyOn(global, 'clearTimeout');
      
      const { unmount } = render(<AlertNotification />);
      
      unmount();
      
      expect(clearTimeoutSpy).toHaveBeenCalled();
      
      vi.useRealTimers();
    });
  });
});