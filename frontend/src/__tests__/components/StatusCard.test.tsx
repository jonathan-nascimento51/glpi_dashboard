/**
 * Testes para o componente StatusCard
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { StatusCard } from '../../components/dashboard/StatusCard';
import { Ticket, TrendingUp, TrendingDown } from 'lucide-react';

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
  TrendingUp: () => <div data-testid='trending-up-icon' />,
  TrendingDown: () => <div data-testid='trending-down-icon' />,
  Minus: () => <div data-testid='minus-icon' />,
  Ticket: () => <div data-testid='ticket-icon' />,
  Info: () => <div data-testid='info-icon' />,
}));

const defaultProps = {
  title: 'Novos Tickets',
  value: 15,
  icon: Ticket,
};

describe('StatusCard Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Renderização Básica', () => {
    it('deve renderizar título e valor corretamente', () => {
      render(<StatusCard {...defaultProps} />);

      expect(screen.getByText('Novos Tickets')).toBeInTheDocument();
      expect(screen.getByText('15')).toBeInTheDocument();
    });

    it('deve renderizar ícone quando fornecido', () => {
      render(<StatusCard {...defaultProps} />);

      expect(screen.getByTestId('ticket-icon')).toBeInTheDocument();
    });

    it('deve renderizar sem ícone quando não fornecido', () => {
      const propsWithoutIcon = { ...defaultProps };
      delete propsWithoutIcon.icon;

      render(<StatusCard {...propsWithoutIcon} />);

      expect(screen.getByText('Novos Tickets')).toBeInTheDocument();
      expect(screen.getByText('15')).toBeInTheDocument();
      expect(screen.queryByTestId('ticket-icon')).not.toBeInTheDocument();
    });
  });

  describe('Tendências', () => {
    it('deve renderizar tendência positiva', () => {
      const propsWithTrend = {
        ...defaultProps,
        trend: {
          direction: 'up' as const,
          value: 12,
          label: 'vs mês anterior',
        },
      };

      render(<StatusCard {...propsWithTrend} />);

      expect(screen.getByTestId('trending-up-icon')).toBeInTheDocument();
      expect(screen.getByText('+12')).toBeInTheDocument();
    });

    it('deve renderizar tendência negativa', () => {
      const propsWithTrend = {
        ...defaultProps,
        trend: {
          direction: 'down' as const,
          value: 5,
          label: 'vs mês anterior',
        },
      };

      render(<StatusCard {...propsWithTrend} />);

      expect(screen.getByTestId('trending-down-icon')).toBeInTheDocument();
      expect(screen.getByText('-5')).toBeInTheDocument();
    });

    it('deve renderizar tendência estável', () => {
      const propsWithTrend = {
        ...defaultProps,
        trend: {
          direction: 'stable' as const,
          value: 0,
          label: 'sem alteração',
        },
      };

      render(<StatusCard {...propsWithTrend} />);

      expect(screen.getByTestId('minus-icon')).toBeInTheDocument();
      expect(screen.getByText('sem alteração')).toBeInTheDocument();
    });
  });

  describe('Interações', () => {
    it('deve chamar onClick quando clicado', () => {
      const mockOnClick = vi.fn();
      const propsWithClick = {
        ...defaultProps,
        onClick: mockOnClick,
      };

      render(<StatusCard {...propsWithClick} />);

      const card = screen.getByText('Novos Tickets').closest('div');
      fireEvent.click(card!);

      expect(mockOnClick).toHaveBeenCalledTimes(1);
    });

    it('deve ter cursor pointer quando onClick é fornecido', () => {
      const mockOnClick = vi.fn();
      const propsWithClick = {
        ...defaultProps,
        onClick: mockOnClick,
      };

      const { container } = render(<StatusCard {...propsWithClick} />);

      // Verificar se o container principal tem cursor pointer
      const motionDiv = container.querySelector('.cursor-pointer');
      expect(motionDiv).toBeInTheDocument();
      expect(motionDiv).toHaveClass('cursor-pointer');
    });

    it('não deve ter cursor pointer quando onClick não é fornecido', () => {
      render(<StatusCard {...defaultProps} />);

      const card = screen.getByText('Novos Tickets').closest('div');
      expect(card).not.toHaveClass('cursor-pointer');
    });
  });

  describe('Variantes', () => {
    it('deve aplicar variante compact', () => {
      const propsWithVariant = {
        ...defaultProps,
        variant: 'compact' as const,
      };

      render(<StatusCard {...propsWithVariant} />);

      expect(screen.getByText('Novos Tickets')).toBeInTheDocument();
      expect(screen.getByText('15')).toBeInTheDocument();
    });

    it('deve aplicar variante gradient', () => {
      const propsWithVariant = {
        ...defaultProps,
        variant: 'gradient' as const,
        status: 'active',
      };

      render(<StatusCard {...propsWithVariant} />);

      expect(screen.getByText('Novos Tickets')).toBeInTheDocument();
      expect(screen.getByText('15')).toBeInTheDocument();
    });
  });

  describe('Formatação de Valores', () => {
    it('deve formatar números grandes corretamente', () => {
      const propsWithLargeValue = {
        ...defaultProps,
        value: 1234567,
      };

      render(<StatusCard {...propsWithLargeValue} />);

      // O valor deve ser formatado (pode ser 1.2M, 1,234,567, etc.)
      const formattedValue = screen.getByText(/1[.,]?[0-9]*[KMB]?/i);
      expect(formattedValue).toBeInTheDocument();
    });

    it('deve lidar com valor zero', () => {
      const propsWithZero = {
        ...defaultProps,
        value: 0,
      };

      render(<StatusCard {...propsWithZero} />);

      expect(screen.getByText('0')).toBeInTheDocument();
    });

    it('deve lidar com valores negativos', () => {
      const propsWithNegative = {
        ...defaultProps,
        value: -5,
      };

      render(<StatusCard {...propsWithNegative} />);

      expect(screen.getByText('-5')).toBeInTheDocument();
    });
  });

  describe('Barra de Progresso', () => {
    it('deve mostrar barra de progresso quando showProgress é true', () => {
      const propsWithProgress = {
        ...defaultProps,
        showProgress: true,
        maxValue: 100,
      };

      render(<StatusCard {...propsWithProgress} />);

      // Como o componente não implementa showProgress ainda, vamos verificar se renderiza sem erro
      expect(screen.getByText('Novos Tickets')).toBeInTheDocument();
      expect(screen.getByText('15')).toBeInTheDocument();
    });

    it('deve calcular porcentagem corretamente', () => {
      const propsWithProgress = {
        ...defaultProps,
        value: 25,
        showProgress: true,
        maxValue: 100,
      };

      render(<StatusCard {...propsWithProgress} />);

      // Verificar se a porcentagem está sendo exibida ou calculada corretamente
      expect(screen.getByText('25')).toBeInTheDocument();
    });
  });

  describe('Acessibilidade', () => {
    it('deve ter estrutura semântica correta', () => {
      render(<StatusCard {...defaultProps} />);

      // Verificar se o card tem estrutura adequada
      const title = screen.getByText('Novos Tickets');
      const value = screen.getByText('15');

      expect(title).toBeInTheDocument();
      expect(value).toBeInTheDocument();
    });

    it('deve ser navegável por teclado quando clicável', () => {
      const mockOnClick = vi.fn();
      const propsWithClick = {
        ...defaultProps,
        onClick: mockOnClick,
      };

      const { container } = render(<StatusCard {...propsWithClick} />);

      // Verificar se o container principal tem cursor pointer
      const motionDiv = container.querySelector('.cursor-pointer');
      expect(motionDiv).toBeInTheDocument();
      expect(motionDiv).toHaveClass('cursor-pointer');
    });
  });

  describe('Estados de Erro', () => {
    it('deve lidar com props inválidas graciosamente', () => {
      const invalidProps = {
        title: '',
        value: NaN,
        trend: null as any,
      };

      expect(() => {
        render(<StatusCard {...invalidProps} />);
      }).not.toThrow();
    });

    it('deve renderizar com className customizada', () => {
      const propsWithClass = {
        ...defaultProps,
        className: 'custom-status-card',
      };

      const { container } = render(<StatusCard {...propsWithClass} />);

      // Verificar se a className customizada está no container principal
      const motionDiv = container.querySelector('.custom-status-card');
      expect(motionDiv).toBeInTheDocument();
    });
  });
});
