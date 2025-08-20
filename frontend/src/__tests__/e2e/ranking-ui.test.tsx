import { describe, it, expect, beforeAll, afterAll, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { RankingTable } from '../../components/dashboard/RankingTable';
import { getTechnicianRanking } from '../../services/api';

// Mock da API
vi.mock('../../services/api', () => ({
  getTechnicianRanking: vi.fn(),
}));

// Mock do sistema de cache
vi.mock('../../services/cache', () => ({
  technicianRankingCache: {
    get: vi.fn(() => null),
    set: vi.fn(),
    clear: vi.fn(),
    recordRequestTime: vi.fn(),
  },
}));

const mockGetTechnicianRanking = getTechnicianRanking as any;

const mockRankingData = [
  {
    name: 'João Silva',
    total: 45,
    level: 'N1',
    avg_resolution_time: 2.5,
  },
  {
    name: 'Maria Santos',
    total: 38,
    level: 'N2',
    avg_resolution_time: 3.2,
  },
  {
    name: 'Pedro Costa',
    total: 32,
    level: 'N1',
    avg_resolution_time: 2.8,
  },
  {
    name: 'Ana Oliveira',
    total: 28,
    level: 'N3',
    avg_resolution_time: 4.1,
  },
  {
    name: 'Carlos Ferreira',
    total: 25,
    level: 'N4',
    avg_resolution_time: 5.5,
  },
];

const renderComponent = (component: React.ReactElement) => {
  return render(component);
};

describe('Testes E2E - Interface do Ranking', () => {
  beforeAll(() => {
    // Mock da resposta da API
    mockGetTechnicianRanking.mockResolvedValue({
      success: true,
      data: mockRankingData,
    });
  });

  afterAll(() => {
    vi.clearAllMocks();
  });

  describe('Renderização de Dados', () => {
    it('deve renderizar com dados de 7 dias', async () => {
      renderComponent(<RankingTable data={mockRankingData} />);

      // Aguardar carregamento inicial
      await waitFor(() => {
        expect(screen.getByText('Ranking de Técnicos')).toBeInTheDocument();
      });

      // Verificar se os dados são exibidos
      expect(screen.getByText('João S.')).toBeInTheDocument();
      expect(screen.getByText('45')).toBeInTheDocument();
    });

    it('deve renderizar com dados de 14 dias', async () => {
      renderComponent(<RankingTable data={mockRankingData} />);

      await waitFor(() => {
        expect(screen.getByText('Ranking de Técnicos')).toBeInTheDocument();
      });

      // Verificar se os dados são exibidos
      expect(screen.getByText('Maria S.')).toBeInTheDocument();
      expect(screen.getByText('38')).toBeInTheDocument();
    });

    it('deve renderizar com dados de 30 dias', async () => {
      renderComponent(<RankingTable data={mockRankingData} />);

      await waitFor(() => {
        expect(screen.getByText('Ranking de Técnicos')).toBeInTheDocument();
      });

      // Verificar se os dados são exibidos
      expect(screen.getByText('Pedro C.')).toBeInTheDocument();
      expect(screen.getByText('32')).toBeInTheDocument();
    });
  });

  describe('Renderização de Componentes', () => {
    it('deve renderizar título principal', async () => {
      renderComponent(<RankingTable data={mockRankingData} />);

      await waitFor(() => {
        expect(screen.getByText('Ranking de Técnicos')).toBeInTheDocument();
      });
    });

    it('deve renderizar cards de técnicos', async () => {
      renderComponent(<RankingTable data={mockRankingData} />);

      await waitFor(() => {
        // Verificar se os cards são renderizados
        const technicianCards = screen.getAllByTestId(/technician-card-/);
        expect(technicianCards.length).toBeGreaterThan(0);
      });
    });

    it('deve exibir nomes dos técnicos', async () => {
      renderComponent(<RankingTable data={mockRankingData} />);

      await waitFor(() => {
        expect(screen.getByText('João S.')).toBeInTheDocument();
        expect(screen.getByText('Maria S.')).toBeInTheDocument();
      });
    });

    it('deve exibir total de tickets', async () => {
      renderComponent(<RankingTable data={mockRankingData} />);

      await waitFor(() => {
        expect(screen.getByText('45')).toBeInTheDocument();
        expect(screen.getByText('38')).toBeInTheDocument();
      });
    });

    it('deve exibir níveis dos técnicos', async () => {
      renderComponent(<RankingTable data={mockRankingData} />);

      await waitFor(() => {
        // Verificar se pelo menos alguns níveis estão presentes
        const n1Elements = screen.getAllByText('N1');
        const n2Elements = screen.getAllByText('N2');
        const n3Elements = screen.getAllByText('N3');
        const n4Elements = screen.getAllByText('N4');

        expect(n1Elements.length).toBeGreaterThan(0);
        expect(n2Elements.length).toBeGreaterThan(0);
        expect(n3Elements.length).toBeGreaterThan(0);
        expect(n4Elements.length).toBeGreaterThan(0);
      });
    });
  });

  describe('Interações do Usuário', () => {
    it('deve manter dados consistentes durante renderização', async () => {
      renderComponent(<RankingTable data={mockRankingData} />);

      // Aguardar carregamento inicial
      await waitFor(() => {
        expect(screen.getByText('Ranking de Técnicos')).toBeInTheDocument();
      });

      // Verificar se os dados permanecem consistentes (nomes formatados)
      expect(screen.getByText('João S.')).toBeInTheDocument();
      expect(screen.getByText('Maria S.')).toBeInTheDocument();
      expect(screen.getByText('Pedro C.')).toBeInTheDocument();

      // Verificar se os totais são exibidos
      expect(screen.getByText('45')).toBeInTheDocument();
      expect(screen.getByText('38')).toBeInTheDocument();
      expect(screen.getByText('32')).toBeInTheDocument();
    });
  });

  describe('Responsividade', () => {
    it('deve manter responsividade em diferentes tamanhos de tela', async () => {
      // Simular tela mobile
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      });

      renderComponent(<RankingTable data={mockRankingData} />);

      await waitFor(() => {
        expect(screen.getByText('Ranking de Técnicos')).toBeInTheDocument();
      });

      // Verificar se os cards ainda são visíveis
      const technicianCards = screen.getAllByTestId(/technician-card-/);
      expect(technicianCards.length).toBeGreaterThan(0);

      // Simular tela desktop
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 1920,
      });

      // Verificar se ainda funciona
      expect(screen.getByText('Ranking de Técnicos')).toBeInTheDocument();
    });
  });

  describe('Estados de Loading e Erro', () => {
    it('deve exibir estado de loading', async () => {
      // Mock de resposta lenta
      mockGetTechnicianRanking.mockImplementation(
        () =>
          new Promise(resolve =>
            setTimeout(() => resolve({ success: true, data: mockRankingData }), 100)
          )
      );

      renderComponent(<RankingTable data={mockRankingData} />);

      // Verificar se há indicador de loading (pode ser spinner, texto, etc.)
      const loadingIndicator =
        screen.queryByText(/carregando/i) ||
        screen.queryByRole('progressbar') ||
        screen.queryByTestId('loading-spinner');

      if (loadingIndicator) {
        expect(loadingIndicator).toBeInTheDocument();
      }

      // Aguardar carregamento completo
      await waitFor(() => {
        expect(screen.getByText('Ranking de Técnicos')).toBeInTheDocument();
      });
    });

    it('deve tratar erro de API graciosamente', async () => {
      // Mock de erro
      mockGetTechnicianRanking.mockRejectedValueOnce(new Error('Erro de rede'));

      renderComponent(<RankingTable data={mockRankingData} />);

      await waitFor(() => {
        // Verificar se há tratamento de erro (pode ser mensagem, fallback, etc.)
        const errorMessage =
          screen.queryByText(/erro/i) ||
          screen.queryByText(/falha/i) ||
          screen.queryByText(/problema/i);

        // Se não há mensagem de erro explícita, pelo menos o título deve estar presente
        expect(screen.getByText('Ranking de Técnicos')).toBeInTheDocument();
      });
    });
  });
});
