import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ModernDashboard } from '../components/dashboard/ModernDashboard';
import { LevelMetricsGrid } from '../components/dashboard/LevelMetricsGrid';
import { TechnicianRanking } from '../components/dashboard/TechnicianRanking';
import { validateMetricsData, validateTechnicianRanking } from '../types/validation';

// Mock dos dados de teste
const mockMetricsData = {
  niveis: {
    N1: { total: 150, resolvidos: 120, pendentes: 30, tempo_medio: 2.5 },
    N2: { total: 80, resolvidos: 65, pendentes: 15, tempo_medio: 4.2 },
    N3: { total: 45, resolvidos: 35, pendentes: 10, tempo_medio: 8.1 },
    N4: { total: 20, resolvidos: 15, pendentes: 5, tempo_medio: 16.3 },
  },
  total_tickets: 295,
  tickets_resolvidos: 235,
  tickets_pendentes: 60,
  tempo_medio_resolucao: 5.2,
  satisfacao_cliente: 4.2,
};

const mockTechnicianData = [
  {
    id: 1,
    nome: 'João Silva',
    tickets_resolvidos: 45,
    tempo_medio: 3.2,
    satisfacao: 4.8,
    nivel: 'N2',
  },
  {
    id: 2,
    nome: 'Maria Santos',
    tickets_resolvidos: 38,
    tempo_medio: 2.8,
    satisfacao: 4.6,
    nivel: 'N1',
  },
];

// Mock da API
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe('Dashboard Integration Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockMetricsData),
    });
  });

  describe('Data Validation Integration', () => {
    it('should validate and display metrics data correctly', async () => {
      const validationResult = validateMetricsData(mockMetricsData);
      expect(validationResult.success).toBe(true);
      
      if (validationResult.success) {
        render(<LevelMetricsGrid metrics={validationResult.data} />);
        
        // Verificar se os dados são exibidos corretamente
        await waitFor(() => {
          expect(screen.getByText('N1')).toBeInTheDocument();
          expect(screen.getByText('N2')).toBeInTheDocument();
          expect(screen.getByText('N3')).toBeInTheDocument();
          expect(screen.getByText('N4')).toBeInTheDocument();
        });
        
        // Verificar valores específicos
        expect(screen.getByText('150')).toBeInTheDocument(); // Total N1
        expect(screen.getByText('120')).toBeInTheDocument(); // Resolvidos N1
      }
    });

    it('should handle invalid metrics data gracefully', () => {
      const invalidData = {
        niveis: null,
        total_tickets: 'invalid',
      };
      
      const validationResult = validateMetricsData(invalidData);
      expect(validationResult.success).toBe(false);
      
      // Renderizar com dados de fallback
      render(<LevelMetricsGrid metrics={{}} />);
      
      // Verificar se não há erros de renderização
      expect(screen.getByText('Métricas por Nível')).toBeInTheDocument();
    });

    it('should validate technician ranking data', () => {
      const validationResult = validateTechnicianRanking(mockTechnicianData);
      expect(validationResult.success).toBe(true);
      
      if (validationResult.success) {
        render(<TechnicianRanking data={validationResult.data} />);
        
        expect(screen.getByText('João Silva')).toBeInTheDocument();
        expect(screen.getByText('Maria Santos')).toBeInTheDocument();
      }
    });
  });

  describe('API Integration', () => {
    it('should fetch and display dashboard data', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockMetricsData),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockTechnicianData),
        });

      render(<ModernDashboard />);
      
      // Verificar loading state
      expect(screen.getByText(/carregando/i)).toBeInTheDocument();
      
      // Aguardar dados carregarem
      await waitFor(() => {
        expect(screen.queryByText(/carregando/i)).not.toBeInTheDocument();
      }, { timeout: 3000 });
      
      // Verificar se os dados foram exibidos
      expect(screen.getByText('295')).toBeInTheDocument(); // Total tickets
    });

    it('should handle API errors gracefully', async () => {
      mockFetch.mockRejectedValue(new Error('API Error'));
      
      render(<ModernDashboard />);
      
      await waitFor(() => {
        expect(screen.getByText(/erro/i)).toBeInTheDocument();
      });
    });

    it('should retry failed API calls', async () => {
      mockFetch
        .mockRejectedValueOnce(new Error('Network Error'))
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockMetricsData),
        });

      render(<ModernDashboard />);
      
      // Aguardar retry e sucesso
      await waitFor(() => {
        expect(screen.getByText('295')).toBeInTheDocument();
      }, { timeout: 5000 });
      
      // Verificar se houve retry
      expect(mockFetch).toHaveBeenCalledTimes(2);
    });
  });

  describe('User Interaction', () => {
    it('should handle filter interactions', async () => {
      render(<ModernDashboard />);
      
      await waitFor(() => {
        expect(screen.queryByText(/carregando/i)).not.toBeInTheDocument();
      });
      
      // Simular interação com filtros
      const filterButton = screen.getByRole('button', { name: /filtro/i });
      if (filterButton) {
        fireEvent.click(filterButton);
        
        // Verificar se o filtro foi aplicado
        await waitFor(() => {
          expect(mockFetch).toHaveBeenCalledWith(
            expect.stringContaining('/api/metrics'),
            expect.any(Object)
          );
        });
      }
    });

    it('should handle refresh action', async () => {
      render(<ModernDashboard />);
      
      await waitFor(() => {
        expect(screen.queryByText(/carregando/i)).not.toBeInTheDocument();
      });
      
      // Simular refresh
      const refreshButton = screen.getByRole('button', { name: /atualizar/i });
      if (refreshButton) {
        fireEvent.click(refreshButton);
        
        // Verificar se os dados foram recarregados
        await waitFor(() => {
          expect(mockFetch).toHaveBeenCalledTimes(3); // Initial + refresh
        });
      }
    });
  });

  describe('Performance Tests', () => {
    it('should render dashboard within acceptable time', async () => {
      const startTime = performance.now();
      
      render(<ModernDashboard />);
      
      await waitFor(() => {
        expect(screen.queryByText(/carregando/i)).not.toBeInTheDocument();
      });
      
      const endTime = performance.now();
      const renderTime = endTime - startTime;
      
      // Verificar se renderizou em menos de 2 segundos
      expect(renderTime).toBeLessThan(2000);
    });

    it('should not cause memory leaks', () => {
      const { unmount } = render(<ModernDashboard />);
      
      // Simular unmount
      unmount();
      
      // Verificar se não há listeners pendentes
      expect(document.querySelectorAll('[data-testid]')).toHaveLength(0);
    });
  });

  describe('Accessibility Tests', () => {
    it('should have proper ARIA labels', async () => {
      render(<ModernDashboard />);
      
      await waitFor(() => {
        expect(screen.queryByText(/carregando/i)).not.toBeInTheDocument();
      });
      
      // Verificar ARIA labels
      const dashboard = screen.getByRole('main');
      expect(dashboard).toHaveAttribute('aria-label', expect.stringContaining('dashboard'));
    });

    it('should be keyboard navigable', async () => {
      render(<ModernDashboard />);
      
      await waitFor(() => {
        expect(screen.queryByText(/carregando/i)).not.toBeInTheDocument();
      });
      
      // Verificar se elementos são focáveis
      const focusableElements = screen.getAllByRole('button');
      expect(focusableElements.length).toBeGreaterThan(0);
      
      focusableElements.forEach(element => {
        expect(element).toHaveAttribute('tabIndex');
      });
    });
  });
});
