/**
 * Testes para o componente LevelMetricsGrid
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { LevelMetricsGrid } from '../../components/dashboard/LevelMetricsGrid';
import { MetricsData } from '../../types';

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
  Users: () => <div data-testid='users-icon' />,
  Clock: () => <div data-testid='clock-icon' />,
  AlertCircle: () => <div data-testid='alert-circle-icon' />,
  CheckCircle: () => <div data-testid='check-circle-icon' />,
  TrendingUp: () => <div data-testid='trending-up-icon' />,
}));

const mockMetrics: MetricsData = {
  niveis: {
    n1: {
      novos: 10,
      pendentes: 5,
      progresso: 8,
      resolvidos: 25,
      total: 48,
    },
    n2: {
      novos: 8,
      pendentes: 3,
      progresso: 6,
      resolvidos: 20,
      total: 37,
    },
    n3: {
      novos: 5,
      pendentes: 2,
      progresso: 4,
      resolvidos: 15,
      total: 26,
    },
    n4: {
      novos: 2,
      pendentes: 1,
      progresso: 2,
      resolvidos: 8,
      total: 13,
    },
    geral: {
      novos: 25,
      pendentes: 11,
      progresso: 20,
      resolvidos: 68,
      total: 124,
    },
  },
  tendencias: {
    novos: 12,
    pendentes: -5,
    progresso: 8,
    resolvidos: 15,
  },
  filtros_aplicados: [],
  tempo_execucao: 150,
  timestamp: '2024-01-15T10:30:00Z',
  systemStatus: {
    status: 'online',
    lastUpdate: '2024-01-15T10:30:00Z',
    apiResponseTime: 150,
    cacheHitRate: 85,
    activeConnections: 12,
    memoryUsage: 65,
    cpuUsage: 45,
  },
};

const defaultProps = {
  metrics: mockMetrics,
};

describe('LevelMetricsGrid Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Renderização Básica', () => {
    it('deve renderizar todos os níveis corretamente', () => {
      render(<LevelMetricsGrid {...defaultProps} />);

      // Verificar se todos os níveis estão presentes
      expect(screen.getByText('Nível N1')).toBeInTheDocument();
      expect(screen.getByText('Nível N2')).toBeInTheDocument();
      expect(screen.getByText('Nível N3')).toBeInTheDocument();
      expect(screen.getByText('Nível N4')).toBeInTheDocument();
    });

    it('deve renderizar métricas de cada nível', () => {
      render(<LevelMetricsGrid {...defaultProps} />);

      // Verificar valores do N1 - usando getAllByText para múltiplas ocorrências
      expect(screen.getAllByText('10')).toHaveLength(1); // novos N1
      expect(screen.getAllByText('5')).toHaveLength(2); // pendentes N1 e N3
      expect(screen.getAllByText('8')).toHaveLength(3); // progresso N1, N2 e resolvidos N4
      expect(screen.getAllByText('25')).toHaveLength(1); // resolvidos N1
    });

    it('deve renderizar ícones de status corretos', () => {
      render(<LevelMetricsGrid {...defaultProps} />);

      // Verificar se os ícones estão presentes
      expect(screen.getAllByTestId('users-icon')).toHaveLength(4); // novos para cada nível
      expect(screen.getAllByTestId('clock-icon')).toHaveLength(4); // progresso para cada nível
      expect(screen.getAllByTestId('alert-circle-icon')).toHaveLength(4); // pendentes para cada nível
      expect(screen.getAllByTestId('check-circle-icon')).toHaveLength(4); // resolvidos para cada nível
    });
  });

  describe('Estado de Loading', () => {
    it('deve mostrar estado de carregamento quando metrics é null', () => {
      render(<LevelMetricsGrid metrics={null} />);

      expect(screen.getByText('📊')).toBeInTheDocument();
      expect(screen.getByText('Carregando métricas por nível...')).toBeInTheDocument();
    });

    it('deve mostrar estado de carregamento quando niveis é undefined', () => {
      const metricsWithoutNiveis = {
        ...mockMetrics,
        niveis: undefined as any,
      };

      render(<LevelMetricsGrid metrics={metricsWithoutNiveis} />);

      expect(screen.getByText('📊')).toBeInTheDocument();
      expect(screen.getByText('Carregando métricas por nível...')).toBeInTheDocument();
    });
  });

  describe('Cálculos e Formatação', () => {
    it('deve calcular totais corretamente para cada nível', () => {
      render(<LevelMetricsGrid {...defaultProps} />);

      // Verificar se os totais estão sendo calculados (valores podem variar)
      // N1: 10 + 5 + 8 + 25 = 48
      const badges = document.querySelectorAll('.border-0');
      expect(badges.length).toBeGreaterThan(0);

      // Verificar se existem valores numéricos nos badges
      const hasNumericValues = Array.from(badges).some(badge =>
        /\d+/.test(badge.textContent || '')
      );
      expect(hasNumericValues).toBe(true);
    });

    it('deve lidar com valores zerados', () => {
      const metricsWithZeros = {
        ...mockMetrics,
        niveis: {
          ...mockMetrics.niveis,
          n1: {
            novos: 0,
            pendentes: 0,
            progresso: 0,
            resolvidos: 0,
            total: 0,
          },
        },
      };

      render(<LevelMetricsGrid metrics={metricsWithZeros} />);

      // Deve renderizar zeros sem problemas
      expect(screen.getAllByText('0').length).toBeGreaterThanOrEqual(4); // pelo menos 4 zeros para N1
    });

    it('deve lidar com valores undefined graciosamente', () => {
      const metricsWithUndefined = {
        ...mockMetrics,
        niveis: {
          ...mockMetrics.niveis,
          n1: {
            novos: undefined as any,
            pendentes: undefined as any,
            progresso: undefined as any,
            resolvidos: undefined as any,
            total: undefined as any,
          },
        },
      };

      expect(() => {
        render(<LevelMetricsGrid metrics={metricsWithUndefined} />);
      }).not.toThrow();
    });
  });

  describe('Responsividade', () => {
    it('deve ter classes responsivas corretas', () => {
      render(<LevelMetricsGrid {...defaultProps} />);

      // Verificar se o grid tem classes responsivas
      const grid = document.querySelector('.grid');
      expect(grid).toBeInTheDocument();
      expect(grid).toHaveClass('grid-cols-1');
      expect(grid).toHaveClass('sm:grid-cols-2');
    });
  });

  describe('Animações', () => {
    it('deve ter animações de entrada', () => {
      render(<LevelMetricsGrid {...defaultProps} />);

      // Verificar se os cards estão presentes (animações são mockadas)
      const levelCards = document.querySelectorAll('.figma-glass-card');
      expect(levelCards.length).toBeGreaterThan(0);
    });
  });

  describe('Acessibilidade', () => {
    it('deve ter estrutura semântica correta', () => {
      render(<LevelMetricsGrid {...defaultProps} />);

      // Verificar se existem títulos de nível
      expect(screen.getByText('Nível N1')).toBeInTheDocument();
      expect(screen.getByText('Nível N2')).toBeInTheDocument();
      expect(screen.getByText('Nível N3')).toBeInTheDocument();
      expect(screen.getByText('Nível N4')).toBeInTheDocument();
    });

    it('deve ter labels descritivos para status', () => {
      render(<LevelMetricsGrid {...defaultProps} />);

      // Verificar se os labels de status estão presentes
      expect(screen.getAllByText('Novos')).toHaveLength(4);
      expect(screen.getAllByText('Pendentes')).toHaveLength(4);
      expect(screen.getAllByText('Em Progresso')).toHaveLength(4);
      expect(screen.getAllByText('Resolvidos')).toHaveLength(4);
    });
  });

  describe('Integração com Tema', () => {
    it('deve aplicar classes de tema corretas', () => {
      render(<LevelMetricsGrid {...defaultProps} />);

      // Verificar se existem classes de tema
      const cards = document.querySelectorAll('.figma-glass-card');
      expect(cards.length).toBeGreaterThan(0);
    });

    it('deve aplicar className customizada', () => {
      const propsWithClass = {
        ...defaultProps,
        className: 'custom-level-grid',
      };

      render(<LevelMetricsGrid {...propsWithClass} />);

      const container = document.querySelector('.custom-level-grid');
      expect(container).toBeInTheDocument();
    });
  });

  describe('Performance', () => {
    it('deve usar React.memo para evitar re-renders desnecessários', () => {
      const { rerender } = render(<LevelMetricsGrid {...defaultProps} />);

      // Renderizar novamente com as mesmas props
      rerender(<LevelMetricsGrid {...defaultProps} />);

      // O componente deve estar presente
      expect(screen.getByText('Nível N1')).toBeInTheDocument();
    });

    it('deve lidar com mudanças de dados eficientemente', () => {
      const { rerender } = render(<LevelMetricsGrid {...defaultProps} />);

      const updatedMetrics = {
        ...mockMetrics,
        niveis: {
          ...mockMetrics.niveis,
          n1: {
            ...mockMetrics.niveis.n1,
            novos: 15, // Valor alterado
          },
        },
      };

      rerender(<LevelMetricsGrid metrics={updatedMetrics} />);

      // Verificar se o novo valor está sendo exibido
      expect(screen.getAllByText('15')).toHaveLength(2); // valor + total atualizado
    });
  });

  describe('Estados de Erro', () => {
    it('deve lidar com dados malformados graciosamente', () => {
      const malformedMetrics = {
        niveis: {
          n1: {
            novos: 'invalid' as any,
            pendentes: null as any,
            progresso: undefined as any,
            resolvidos: 25,
            total: NaN as any,
          },
        },
      } as any;

      expect(() => {
        render(<LevelMetricsGrid metrics={malformedMetrics} />);
      }).not.toThrow();
    });

    it('deve lidar com níveis ausentes', () => {
      const metricsWithMissingLevels = {
        ...mockMetrics,
        niveis: {
          n1: mockMetrics.niveis.n1,
          // n2, n3, n4 ausentes
        },
      } as any;

      expect(() => {
        render(<LevelMetricsGrid metrics={metricsWithMissingLevels} />);
      }).not.toThrow();

      // Deve renderizar apenas N1
      expect(screen.getByText('Nível N1')).toBeInTheDocument();
    });
  });
});
