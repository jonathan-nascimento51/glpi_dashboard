/**
 * Testes para o componente AlertCenter
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import AlertCenter from '../components/AlertCenter';
import * as alertHooks from '../hooks/useAlerts';
import { describe, it, expect, beforeEach, vi } from 'vitest';

// Mock dos hooks
vi.mock('../hooks/useAlerts');

const mockUseAlerts = alertHooks.useAlerts as any;
const mockUseAlertStats = alertHooks.useAlertStats as any;
const mockUseCriticalAlerts = alertHooks.useCriticalAlerts as any;
const mockUseAlertConfig = alertHooks.useAlertConfig as any;
const mockUseAlertNotifications = alertHooks.useAlertNotifications as any;

describe('AlertCenter', () => {
  const mockAlerts = [
    {
      id: 'alert-1',
      type: 'warning' as const,
      category: 'performance' as const,
      title: 'Performance Warning',
      message: 'High response time detected',
      timestamp: new Date('2024-01-01T10:00:00Z'),
      resolved: false,
      metadata: { responseTime: 2500 }
    },
    {
      id: 'alert-2',
      type: 'error' as const,
      category: 'cache' as const,
      title: 'Cache Error',
      message: 'Cache hit rate too low',
      timestamp: new Date('2024-01-01T11:00:00Z'),
      resolved: false,
      metadata: { hitRate: 0.3 }
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

  const mockStats = {
    total: 3,
    active: 2,
    resolved: 1,
    byType: {
      info: 0,
      warning: 1,
      error: 1,
      critical: 1
    },
    byCategory: {
      performance: 1,
      cache: 1,
      api: 1,
      system: 0
    }
  };

  const mockConfig = {
    checkInterval: 30000,
    maxAlerts: 100,
    enableNotifications: true,
    enableSound: false,
    thresholds: []
  };

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
    
    mockUseAlerts.mockReturnValue({
      alerts: mockAlerts,
      ...mockFunctions
    });
    
    mockUseAlertStats.mockReturnValue(mockStats);
    
    mockUseCriticalAlerts.mockReturnValue(
      mockAlerts.filter(a => a.type === 'critical' && !a.resolved)
    );
    
    mockUseAlertConfig.mockReturnValue({
      config: mockConfig,
      updateConfig: mockFunctions.updateConfig
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
    it('deve renderizar o componente corretamente', () => {
      render(<AlertCenter />);
      
      expect(screen.getByText('Centro de Alertas')).toBeInTheDocument();
      expect(screen.getByText('Performance Warning')).toBeInTheDocument();
      expect(screen.getByText('Cache Error')).toBeInTheDocument();
      expect(screen.getByText('API Critical')).toBeInTheDocument();
    });

    it('deve exibir estatísticas dos alertas', () => {
      render(<AlertCenter />);
      
      expect(screen.getByText('3')).toBeInTheDocument(); // Total
      expect(screen.getByText('2')).toBeInTheDocument(); // Ativos
      expect(screen.getByText('1')).toBeInTheDocument(); // Resolvidos
    });

    it('deve exibir ícones corretos para cada tipo de alerta', () => {
      render(<AlertCenter />);
      
      // Verificar se os ícones estão presentes (através de classes CSS ou data-testid)
      const warningAlert = screen.getByText('Performance Warning').closest('.alert-item');
      const errorAlert = screen.getByText('Cache Error').closest('.alert-item');
      const criticalAlert = screen.getByText('API Critical').closest('.alert-item');
      
      expect(warningAlert).toHaveClass('warning');
      expect(errorAlert).toHaveClass('error');
      expect(criticalAlert).toHaveClass('critical');
    });
  });

  describe('Filtros', () => {
    it('deve filtrar alertas por categoria', () => {
      render(<AlertCenter />);
      
      const categoryFilter = screen.getByLabelText('Filtrar por categoria');
      fireEvent.change(categoryFilter, { target: { value: 'performance' } });
      
      expect(screen.getByText('Performance Warning')).toBeInTheDocument();
      expect(screen.queryByText('Cache Error')).not.toBeInTheDocument();
      expect(screen.queryByText('API Critical')).not.toBeInTheDocument();
    });

    it('deve filtrar alertas por tipo', () => {
      render(<AlertCenter />);
      
      const typeFilter = screen.getByLabelText('Filtrar por tipo');
      fireEvent.change(typeFilter, { target: { value: 'error' } });
      
      expect(screen.queryByText('Performance Warning')).not.toBeInTheDocument();
      expect(screen.getByText('Cache Error')).toBeInTheDocument();
      expect(screen.queryByText('API Critical')).not.toBeInTheDocument();
    });

    it('deve filtrar apenas alertas ativos', () => {
      render(<AlertCenter />);
      
      const activeOnlyFilter = screen.getByLabelText('Apenas ativos');
      fireEvent.click(activeOnlyFilter);
      
      expect(screen.getByText('Performance Warning')).toBeInTheDocument();
      expect(screen.getByText('Cache Error')).toBeInTheDocument();
      expect(screen.queryByText('API Critical')).not.toBeInTheDocument();
    });

    it('deve limpar filtros', () => {
      render(<AlertCenter />);
      
      // Aplicar filtros
      const categoryFilter = screen.getByLabelText('Filtrar por categoria');
      fireEvent.change(categoryFilter, { target: { value: 'performance' } });
      
      // Limpar filtros
      const clearButton = screen.getByText('Limpar Filtros');
      fireEvent.click(clearButton);
      
      expect(screen.getByText('Performance Warning')).toBeInTheDocument();
      expect(screen.getByText('Cache Error')).toBeInTheDocument();
      expect(screen.getByText('API Critical')).toBeInTheDocument();
    });
  });

  describe('Ações de Alerta', () => {
    it('deve resolver alerta individual', () => {
      render(<AlertCenter />);
      
      const resolveButton = screen.getAllByText('Resolver')[0];
      fireEvent.click(resolveButton);
      
      expect(mockFunctions.resolveAlert).toHaveBeenCalledWith('alert-1');
    });

    it('deve resolver todos os alertas', () => {
      render(<AlertCenter />);
      
      const resolveAllButton = screen.getByText('Resolver Todos');
      fireEvent.click(resolveAllButton);
      
      expect(mockFunctions.resolveAllAlerts).toHaveBeenCalled();
    });

    it('deve limpar alertas antigos', () => {
      render(<AlertCenter />);
      
      const clearOldButton = screen.getByText('Limpar Antigos');
      fireEvent.click(clearOldButton);
      
      expect(mockFunctions.clearOldAlerts).toHaveBeenCalledWith(24 * 60 * 60 * 1000);
    });
  });

  describe('Detalhes do Alerta', () => {
    it('deve expandir detalhes do alerta', () => {
      render(<AlertCenter />);
      
      const expandButton = screen.getAllByText('Detalhes')[0];
      fireEvent.click(expandButton);
      
      expect(screen.getByText('High response time detected')).toBeInTheDocument();
      expect(screen.getByText('Tempo de Resposta: 2500ms')).toBeInTheDocument();
    });

    it('deve colapsar detalhes do alerta', () => {
      render(<AlertCenter />);
      
      const expandButton = screen.getAllByText('Detalhes')[0];
      
      // Expandir
      fireEvent.click(expandButton);
      expect(screen.getByText('High response time detected')).toBeInTheDocument();
      
      // Colapsar
      fireEvent.click(expandButton);
      expect(screen.queryByText('High response time detected')).not.toBeInTheDocument();
    });

    it('deve exibir metadados do alerta quando disponíveis', () => {
      render(<AlertCenter />);
      
      const expandButton = screen.getAllByText('Detalhes')[1]; // Cache error
      fireEvent.click(expandButton);
      
      expect(screen.getByText('Taxa de Hit: 30%')).toBeInTheDocument();
    });
  });

  describe('Configurações', () => {
    it('deve abrir modal de configurações', () => {
      render(<AlertCenter />);
      
      const configButton = screen.getByText('Configurações');
      fireEvent.click(configButton);
      
      expect(screen.getByText('Configurações de Alertas')).toBeInTheDocument();
    });

    it('deve atualizar intervalo de verificação', async () => {
      render(<AlertCenter />);
      
      const configButton = screen.getByText('Configurações');
      fireEvent.click(configButton);
      
      const intervalInput = screen.getByLabelText('Intervalo de Verificação (ms)');
      fireEvent.change(intervalInput, { target: { value: '60000' } });
      
      const saveButton = screen.getByText('Salvar');
      fireEvent.click(saveButton);
      
      await waitFor(() => {
        expect(mockFunctions.updateConfig).toHaveBeenCalledWith({
          checkInterval: 60000
        });
      });
    });

    it('deve alternar notificações', async () => {
      render(<AlertCenter />);
      
      const configButton = screen.getByText('Configurações');
      fireEvent.click(configButton);
      
      const notificationToggle = screen.getByLabelText('Habilitar Notificações');
      fireEvent.click(notificationToggle);
      
      const saveButton = screen.getByText('Salvar');
      fireEvent.click(saveButton);
      
      await waitFor(() => {
        expect(mockFunctions.updateConfig).toHaveBeenCalledWith({
          enableNotifications: false
        });
      });
    });

    it('deve fechar modal de configurações', () => {
      render(<AlertCenter />);
      
      const configButton = screen.getByText('Configurações');
      fireEvent.click(configButton);
      
      const closeButton = screen.getByText('Cancelar');
      fireEvent.click(closeButton);
      
      expect(screen.queryByText('Configurações de Alertas')).not.toBeInTheDocument();
    });
  });

  describe('Monitoramento', () => {
    it('deve iniciar monitoramento', () => {
      render(<AlertCenter />);
      
      const startButton = screen.getByText('Iniciar Monitoramento');
      fireEvent.click(startButton);
      
      expect(mockFunctions.startMonitoring).toHaveBeenCalled();
    });

    it('deve parar monitoramento', () => {
      render(<AlertCenter />);
      
      const stopButton = screen.getByText('Parar Monitoramento');
      fireEvent.click(stopButton);
      
      expect(mockFunctions.stopMonitoring).toHaveBeenCalled();
    });
  });

  describe('Estados Vazios', () => {
    it('deve exibir mensagem quando não há alertas', () => {
      mockUseAlerts.mockReturnValue({
        alerts: [],
        ...mockFunctions
      });
      
      mockUseAlertStats.mockReturnValue({
        total: 0,
        active: 0,
        resolved: 0,
        byType: { info: 0, warning: 0, error: 0, critical: 0 },
        byCategory: { performance: 0, cache: 0, api: 0, system: 0 }
      });
      
      render(<AlertCenter />);
      
      expect(screen.getByText('Nenhum alerta encontrado')).toBeInTheDocument();
    });

    it('deve exibir mensagem quando filtros não retornam resultados', () => {
      render(<AlertCenter />);
      
      const categoryFilter = screen.getByLabelText('Filtrar por categoria');
      fireEvent.change(categoryFilter, { target: { value: 'system' } });
      
      expect(screen.getByText('Nenhum alerta encontrado com os filtros aplicados')).toBeInTheDocument();
    });
  });

  describe('Formatação de Tempo', () => {
    it('deve formatar timestamp corretamente', () => {
      render(<AlertCenter />);
      
      // Verificar se os timestamps são exibidos em formato legível
      expect(screen.getByText(/há \d+ horas?/)).toBeInTheDocument();
    });
  });

  describe('Responsividade', () => {
    it('deve adaptar layout para telas pequenas', () => {
      // Simular tela pequena
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 768,
      });
      
      render(<AlertCenter />);
      
      const container = screen.getByTestId('alert-center');
      expect(container).toHaveClass('mobile-layout');
    });
  });

  describe('Acessibilidade', () => {
    it('deve ter labels apropriados para screen readers', () => {
      render(<AlertCenter />);
      
      expect(screen.getByLabelText('Filtrar por categoria')).toBeInTheDocument();
      expect(screen.getByLabelText('Filtrar por tipo')).toBeInTheDocument();
      expect(screen.getByLabelText('Apenas ativos')).toBeInTheDocument();
    });

    it('deve ter navegação por teclado', () => {
      render(<AlertCenter />);
      
      const firstResolveButton = screen.getAllByText('Resolver')[0];
      firstResolveButton.focus();
      
      expect(document.activeElement).toBe(firstResolveButton);
    });

    it('deve ter roles ARIA apropriados', () => {
      render(<AlertCenter />);
      
      expect(screen.getByRole('main')).toBeInTheDocument();
      expect(screen.getByRole('region', { name: 'Estatísticas de Alertas' })).toBeInTheDocument();
      expect(screen.getByRole('list', { name: 'Lista de Alertas' })).toBeInTheDocument();
    });
  });
});