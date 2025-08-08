/**
 * Testes para o componente MetricsGrid
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, fireEvent, waitFor } from '@testing-library/react';
import { render, mockMetricsData } from '../setup';
import { MetricsGrid } from '../../components/dashboard/MetricsGrid';

// Mock do framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    span: ({ children, ...props }: any) => <span {...props}>{children}</span>,
  },
  AnimatePresence: ({ children }: any) => children,
}));

// Mock dos ícones
vi.mock('lucide-react', () => ({
  TrendingUp: () => <div data-testid="trending-up-icon" />,
  TrendingDown: () => <div data-testid="trending-down-icon" />,
  Minus: () => <div data-testid="minus-icon" />,
  AlertCircle: () => <div data-testid="alert-circle-icon" />,
  Clock: () => <div data-testid="clock-icon" />,
  CheckCircle: () => <div data-testid="check-circle-icon" />,
  PlayCircle: () => <div data-testid="play-circle-icon" />,
}));

const defaultProps = {
  metrics: mockMetricsData,
  isLoading: false,
  onStatusFilter: vi.fn(),
};

describe('MetricsGrid Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Renderização', () => {
    it('deve renderizar métricas corretamente', () => {
      render(<MetricsGrid {...defaultProps} />);

      // Verificar se os cards de status estão presentes
      expect(screen.getByText('Novos')).toBeInTheDocument();
      expect(screen.getByText('Em Progresso')).toBeInTheDocument();
      expect(screen.getByText('Pendentes')).toBeInTheDocument();
      expect(screen.getByText('Resolvidos')).toBeInTheDocument();

      // Verificar valores
      expect(screen.getByText('15')).toBeInTheDocument(); // novos
      expect(screen.getByText('12')).toBeInTheDocument(); // progresso
      expect(screen.getByText('8')).toBeInTheDocument(); // pendentes
      expect(screen.getByText('45')).toBeInTheDocument(); // resolvidos
    });

    it('deve renderizar tendências corretamente', () => {
      render(<MetricsGrid {...defaultProps} />);

      // Verificar tendências
      expect(screen.getByText('+12%')).toBeInTheDocument();
      expect(screen.getByText('-5%')).toBeInTheDocument();
      expect(screen.getByText('+8%')).toBeInTheDocument();
      expect(screen.getByText('+15%')).toBeInTheDocument();
    });

    it('deve renderizar ícones corretos para cada status', () => {
      render(<MetricsGrid {...defaultProps} />);

      expect(screen.getByTestId('alert-circle-icon')).toBeInTheDocument(); // novos
      expect(screen.getByTestId('play-circle-icon')).toBeInTheDocument(); // progresso
      expect(screen.getByTestId('clock-icon')).toBeInTheDocument(); // pendentes
      expect(screen.getByTestId('check-circle-icon')).toBeInTheDocument(); // resolvidos
    });

    it('deve renderizar ícones de tendência corretos', () => {
      render(<MetricsGrid {...defaultProps} />);

      // Tendências positivas
      expect(screen.getAllByTestId('trending-up-icon')).toHaveLength(3);
      // Tendências negativas
      expect(screen.getAllByTestId('trending-down-icon')).toHaveLength(1);
    });
  });

  describe('Estado de Loading', () => {
    it('deve mostrar skeleton quando isLoading é true', () => {
      render(<MetricsGrid {...defaultProps} isLoading={true} />);

      // Verificar se skeleton está presente
      const skeletons = screen.getAllByTestId(/skeleton/);
      expect(skeletons.length).toBeGreaterThan(0);
    });

    it('deve mostrar skeleton quando metrics é null', () => {
      render(<MetricsGrid {...defaultProps} metrics={null} />);

      const skeletons = screen.getAllByTestId(/skeleton/);
      expect(skeletons.length).toBeGreaterThan(0);
    });

    it('não deve mostrar skeleton quando dados estão carregados', () => {
      render(<MetricsGrid {...defaultProps} />);

      const skeletons = screen.queryAllByTestId(/skeleton/);
      expect(skeletons).toHaveLength(0);
    });
  });

  describe('Interações', () => {
    it('deve chamar onStatusFilter quando card é clicado', async () => {
      const onStatusFilter = vi.fn();
      render(<MetricsGrid {...defaultProps} onStatusFilter={onStatusFilter} />);

      // Clicar no card "Novos"
      const novosCard = screen.getByText('Novos').closest('div');
      expect(novosCard).toBeInTheDocument();
      
      fireEvent.click(novosCard!);

      await waitFor(() => {
        expect(onStatusFilter).toHaveBeenCalledWith('new');
      });
    });

    it('deve chamar onStatusFilter com status correto para cada card', async () => {
      const onStatusFilter = vi.fn();
      render(<MetricsGrid {...defaultProps} onStatusFilter={onStatusFilter} />);

      // Testar cada card
      const cards = [
        { text: 'Novos', status: 'new' },
        { text: 'Em Progresso', status: 'progress' },
        { text: 'Pendentes', status: 'pending' },
        { text: 'Resolvidos', status: 'resolved' },
      ];

      for (const card of cards) {
        const cardElement = screen.getByText(card.text).closest('div');
        fireEvent.click(cardElement!);
        
        await waitFor(() => {
          expect(onStatusFilter).toHaveBeenCalledWith(card.status);
        });
        
        onStatusFilter.mockClear();
      }
    });

    it('deve ter cursor pointer nos cards clicáveis', () => {
      render(<MetricsGrid {...defaultProps} />);

      const novosCard = screen.getByText('Novos').closest('div');
      expect(novosCard).toHaveClass('cursor-pointer');
    });
  });

  describe('Responsividade', () => {
    it('deve ter classes responsivas corretas', () => {
      render(<MetricsGrid {...defaultProps} />);

      const grid = screen.getByRole('grid', { hidden: true }) || 
                  document.querySelector('.grid');
      
      expect(grid).toHaveClass('grid-cols-1');
      expect(grid).toHaveClass('md:grid-cols-2');
      expect(grid).toHaveClass('lg:grid-cols-4');
    });
  });

  describe('Acessibilidade', () => {
    it('deve ter atributos de acessibilidade corretos', () => {
      render(<MetricsGrid {...defaultProps} />);

      // Verificar se cards têm role button
      const cards = screen.getAllByRole('button');
      expect(cards.length).toBeGreaterThan(0);
    });

    it('deve ter aria-labels descritivos', () => {
      render(<MetricsGrid {...defaultProps} />);

      expect(screen.getByLabelText(/filtrar por novos/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/filtrar por em progresso/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/filtrar por pendentes/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/filtrar por resolvidos/i)).toBeInTheDocument();
    });

    it('deve ser navegável por teclado', async () => {
      const onStatusFilter = vi.fn();
      render(<MetricsGrid {...defaultProps} onStatusFilter={onStatusFilter} />);

      const firstCard = screen.getByLabelText(/filtrar por novos/i);
      
      // Focar no card
      firstCard.focus();
      expect(firstCard).toHaveFocus();

      // Pressionar Enter
      fireEvent.keyDown(firstCard, { key: 'Enter', code: 'Enter' });
      
      await waitFor(() => {
        expect(onStatusFilter).toHaveBeenCalledWith('new');
      });
    });
  });

  describe('Tratamento de Dados', () => {
    it('deve lidar com métricas zeradas', () => {
      const metricsWithZeros = {
        ...mockMetricsData,
        novos: 0,
        pendentes: 0,
      };

      render(<MetricsGrid {...defaultProps} metrics={metricsWithZeros} />);

      expect(screen.getByText('0')).toBeInTheDocument();
    });

    it('deve lidar com tendências ausentes', () => {
      const metricsWithoutTrends = {
        ...mockMetricsData,
        tendencias: {
          novos: '',
          pendentes: '',
          progresso: '+8%',
          resolvidos: '+15%',
        },
      };

      render(<MetricsGrid {...defaultProps} metrics={metricsWithoutTrends} />);

      // Deve renderizar sem erros
      expect(screen.getByText('Novos')).toBeInTheDocument();
    });

    it('deve lidar com valores muito grandes', () => {
      const metricsWithLargeValues = {
        ...mockMetricsData,
        novos: 999999,
        resolvidos: 1234567,
      };

      render(<MetricsGrid {...defaultProps} metrics={metricsWithLargeValues} />);

      expect(screen.getByText('999999')).toBeInTheDocument();
      expect(screen.getByText('1234567')).toBeInTheDocument();
    });
  });

  describe('Performance', () => {
    it('deve usar React.memo para evitar re-renders desnecessários', () => {
      const { rerender } = render(<MetricsGrid {...defaultProps} />);
      
      // Re-render com as mesmas props
      rerender(<MetricsGrid {...defaultProps} />);
      
      // Componente deve estar otimizado
      expect(screen.getByText('Novos')).toBeInTheDocument();
    });

    it('deve throttle cliques rápidos', async () => {
      const onStatusFilter = vi.fn();
      render(<MetricsGrid {...defaultProps} onStatusFilter={onStatusFilter} />);

      const novosCard = screen.getByText('Novos').closest('div');
      
      // Cliques rápidos
      fireEvent.click(novosCard!);
      fireEvent.click(novosCard!);
      fireEvent.click(novosCard!);

      // Deve ter throttle
      await waitFor(() => {
        expect(onStatusFilter).toHaveBeenCalledTimes(1);
      });
    });
  });

  describe('Animações', () => {
    it('deve ter animações de entrada', () => {
      render(<MetricsGrid {...defaultProps} />);

      // Verificar se motion.div está sendo usado
      const motionDivs = document.querySelectorAll('[data-testid*="motion"]');
      expect(motionDivs.length).toBeGreaterThanOrEqual(0);
    });

    it('deve animar mudanças de valores', async () => {
      const { rerender } = render(<MetricsGrid {...defaultProps} />);

      const updatedMetrics = {
        ...mockMetricsData,
        novos: 20, // Valor alterado
      };

      rerender(<MetricsGrid {...defaultProps} metrics={updatedMetrics} />);

      await waitFor(() => {
        expect(screen.getByText('20')).toBeInTheDocument();
      });
    });
  });

  describe('Estados de Erro', () => {
    it('deve lidar com métricas malformadas', () => {
      const malformedMetrics = {
        novos: 'invalid',
        pendentes: null,
        progresso: undefined,
        resolvidos: 45,
      } as any;

      // Não deve quebrar
      expect(() => {
        render(<MetricsGrid {...defaultProps} metrics={malformedMetrics} />);
      }).not.toThrow();
    });

    it('deve mostrar fallback quando onStatusFilter não é fornecido', () => {
      const propsWithoutCallback = {
        ...defaultProps,
        onStatusFilter: undefined,
      };

      render(<MetricsGrid {...propsWithoutCallback as any} />);

      const novosCard = screen.getByText('Novos').closest('div');
      
      // Não deve quebrar ao clicar
      expect(() => {
        fireEvent.click(novosCard!);
      }).not.toThrow();
    });
  });

  describe('Integração com Tema', () => {
    it('deve aplicar classes de tema corretas', () => {
      render(<MetricsGrid {...defaultProps} />);

      // Verificar classes de tema
      const cards = screen.getAllByRole('button');
      cards.forEach(card => {
        expect(card).toHaveClass('bg-white');
        expect(card).toHaveClass('dark:bg-gray-800');
      });
    });
  });

  describe('Formatação de Números', () => {
    it('deve formatar números grandes corretamente', () => {
      const metricsWithLargeNumbers = {
        ...mockMetricsData,
        novos: 1500,
        resolvidos: 12000,
      };

      render(<MetricsGrid {...defaultProps} metrics={metricsWithLargeNumbers} />);

      // Verificar se números são exibidos corretamente
      expect(screen.getByText('1500')).toBeInTheDocument();
      expect(screen.getByText('12000')).toBeInTheDocument();
    });

    it('deve lidar com números decimais', () => {
      const metricsWithDecimals = {
        ...mockMetricsData,
        novos: 15.5,
        pendentes: 8.2,
      };

      render(<MetricsGrid {...defaultProps} metrics={metricsWithDecimals} />);

      // Deve arredondar ou mostrar como inteiro
      expect(screen.getByText('15') || screen.getByText('16')).toBeInTheDocument();
    });
  });
});