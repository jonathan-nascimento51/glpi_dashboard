import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import App from '../../App';
import { TechnicianRanking } from '@/types';

// Mock data para testes
const mockRankingData: TechnicianRanking[] = [
  {
    id: 1,
    name: 'João Silva',
    level: 'Sênior',
    tickets_count: 25,
    rank: 1
  },
  {
    id: 2,
    name: 'Maria Santos',
    level: 'Pleno',
    tickets_count: 20,
    rank: 2
  },
  {
    id: 3,
    name: 'Pedro Costa',
    level: 'Júnior',
    tickets_count: 15,
    rank: 3
  }
];

const mockFilteredRankingData: TechnicianRanking[] = [
  {
    id: 1,
    name: 'João Silva',
    level: 'Sênior',
    tickets_count: 25,
    rank: 1
  }
];

// Configuração do MSW (Mock Service Worker)
const server = setupServer(
  // Mock da API de métricas
  rest.get('/api/dashboard/metrics', (req, res, ctx) => {
    return res(
      ctx.json({
        success: true,
        data: {
          geral: {
            total_tickets: 100,
            open_tickets: 25,
            closed_tickets: 75,
            pending_tickets: 10,
            in_progress_tickets: 15
          },
          tendencias: {
            total_tickets: { valor: 5, tipo: 'aumento' },
            open_tickets: { valor: 2, tipo: 'aumento' },
            closed_tickets: { valor: 3, tipo: 'aumento' }
          }
        }
      })
    );
  }),

  // Mock da API de ranking sem filtros
  rest.get('/api/technicians/ranking', (req, res, ctx) => {
    const startDate = req.url.searchParams.get('start_date');
    const endDate = req.url.searchParams.get('end_date');
    const level = req.url.searchParams.get('level');
    const limit = req.url.searchParams.get('limit');

    // Se há filtros, retorna dados filtrados
    if (startDate || endDate || level || limit) {
      let filteredData = [...mockRankingData];
      
      if (level === 'Sênior') {
        filteredData = mockFilteredRankingData;
      }
      
      if (limit) {
        filteredData = filteredData.slice(0, parseInt(limit));
      }

      return res(
        ctx.json({
          success: true,
          data: filteredData,
          message: `Ranking obtido com filtros aplicados`
        })
      );
    }

    // Sem filtros, retorna todos os dados
    return res(
      ctx.json({
        success: true,
        data: mockRankingData,
        message: 'Ranking obtido com sucesso'
      })
    );
  }),

  // Mock de outras APIs necessárias
  rest.get('/api/system/status', (req, res, ctx) => {
    return res(
      ctx.json({
        success: true,
        data: { status: 'healthy' }
      })
    );
  }),

  rest.get('/api/tickets/new', (req, res, ctx) => {
    return res(
      ctx.json({
        success: true,
        data: []
      })
    );
  })
);

// Setup e teardown do servidor de mock
beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

// Mock do hook de performance
jest.mock('../../hooks/usePerformanceMonitoring', () => ({
  usePerformanceMonitoring: () => ({
    measureRender: jest.fn(),
    measureApiCall: jest.fn()
  })
}));

// Mock do monitor de performance
jest.mock('../../utils/performanceMonitor', () => ({
  performanceMonitor: {
    markComponentRender: jest.fn(),
    markApiCall: jest.fn()
  },
  usePerformanceProfiler: () => jest.fn()
}));

describe('Technician Ranking Filters E2E', () => {
  beforeEach(() => {
    // Reset de mocks antes de cada teste
    jest.clearAllMocks();
  });

  it('deve exibir ranking sem filtros inicialmente', async () => {
    render(<App />);

    // Aguarda o carregamento dos dados
    await waitFor(() => {
      expect(screen.getByText('Ranking de Técnicos')).toBeInTheDocument();
    });

    // Verifica se todos os técnicos estão sendo exibidos
    await waitFor(() => {
      expect(screen.getByText('João Silva')).toBeInTheDocument();
      expect(screen.getByText('Maria Santos')).toBeInTheDocument();
      expect(screen.getByText('Pedro Costa')).toBeInTheDocument();
    });

    // Verifica se não há filtros sendo exibidos
    expect(screen.queryByText(/Filtros aplicados:/)).not.toBeInTheDocument();
  });

  it('deve aplicar filtros de data e exibir informações dos filtros', async () => {
    const user = userEvent.setup();
    render(<App />);

    // Aguarda o carregamento inicial
    await waitFor(() => {
      expect(screen.getByText('Ranking de Técnicos')).toBeInTheDocument();
    });

    // Procura pelos campos de filtro de data
    const startDateInput = screen.getByLabelText(/data de início/i) || screen.getByPlaceholderText(/início/i);
    const endDateInput = screen.getByLabelText(/data de fim/i) || screen.getByPlaceholderText(/fim/i);

    if (startDateInput && endDateInput) {
      // Aplica filtros de data
      await user.clear(startDateInput);
      await user.type(startDateInput, '2025-01-01');
      
      await user.clear(endDateInput);
      await user.type(endDateInput, '2025-12-31');

      // Aguarda a aplicação dos filtros
      await waitFor(() => {
        expect(screen.getByText(/Filtros aplicados:/)).toBeInTheDocument();
        expect(screen.getByText(/Data de início: 2025-01-01/)).toBeInTheDocument();
        expect(screen.getByText(/Data de fim: 2025-12-31/)).toBeInTheDocument();
      });
    }
  });

  it('deve aplicar filtro de nível e exibir apenas técnicos do nível selecionado', async () => {
    const user = userEvent.setup();
    render(<App />);

    // Aguarda o carregamento inicial
    await waitFor(() => {
      expect(screen.getByText('Ranking de Técnicos')).toBeInTheDocument();
    });

    // Procura pelo filtro de nível
    const levelFilter = screen.getByLabelText(/nível/i) || screen.getByDisplayValue(/todos/i);

    if (levelFilter) {
      // Seleciona nível Sênior
      await user.selectOptions(levelFilter, 'Sênior');

      // Aguarda a aplicação do filtro
      await waitFor(() => {
        expect(screen.getByText(/Nível: Sênior/)).toBeInTheDocument();
        expect(screen.getByText('João Silva')).toBeInTheDocument();
        expect(screen.queryByText('Maria Santos')).not.toBeInTheDocument();
        expect(screen.queryByText('Pedro Costa')).not.toBeInTheDocument();
      });
    }
  });

  it('deve aplicar limite e exibir apenas o número especificado de técnicos', async () => {
    const user = userEvent.setup();
    render(<App />);

    // Aguarda o carregamento inicial
    await waitFor(() => {
      expect(screen.getByText('Ranking de Técnicos')).toBeInTheDocument();
    });

    // Procura pelo campo de limite
    const limitInput = screen.getByLabelText(/limite/i) || screen.getByPlaceholderText(/limite/i);

    if (limitInput) {
      // Define limite de 2 técnicos
      await user.clear(limitInput);
      await user.type(limitInput, '2');

      // Aguarda a aplicação do filtro
      await waitFor(() => {
        const technicianElements = screen.getAllByText(/Silva|Santos|Costa/);
        expect(technicianElements.length).toBeLessThanOrEqual(2);
      });
    }
  });

  it('deve limpar filtros e voltar ao estado inicial', async () => {
    const user = userEvent.setup();
    render(<App />);

    // Aguarda o carregamento inicial
    await waitFor(() => {
      expect(screen.getByText('Ranking de Técnicos')).toBeInTheDocument();
    });

    // Aplica alguns filtros primeiro
    const startDateInput = screen.getByLabelText(/data de início/i) || screen.getByPlaceholderText(/início/i);
    if (startDateInput) {
      await user.type(startDateInput, '2025-01-01');
    }

    // Procura pelo botão de limpar filtros
    const clearButton = screen.getByText(/limpar/i) || screen.getByText(/reset/i);
    if (clearButton) {
      await user.click(clearButton);

      // Verifica se os filtros foram removidos
      await waitFor(() => {
        expect(screen.queryByText(/Filtros aplicados:/)).not.toBeInTheDocument();
        expect(screen.getByText('João Silva')).toBeInTheDocument();
        expect(screen.getByText('Maria Santos')).toBeInTheDocument();
        expect(screen.getByText('Pedro Costa')).toBeInTheDocument();
      });
    }
  });

  it('deve manter filtros aplicados após recarregamento de dados', async () => {
    const user = userEvent.setup();
    render(<App />);

    // Aguarda o carregamento inicial
    await waitFor(() => {
      expect(screen.getByText('Ranking de Técnicos')).toBeInTheDocument();
    });

    // Aplica filtros
    const startDateInput = screen.getByLabelText(/data de início/i) || screen.getByPlaceholderText(/início/i);
    if (startDateInput) {
      await user.type(startDateInput, '2025-01-01');

      // Aguarda a aplicação dos filtros
      await waitFor(() => {
        expect(screen.getByText(/Filtros aplicados:/)).toBeInTheDocument();
      });

      // Simula recarregamento (se houver botão de refresh)
      const refreshButton = screen.getByText(/atualizar/i) || screen.getByText(/refresh/i);
      if (refreshButton) {
        await user.click(refreshButton);

        // Verifica se os filtros ainda estão aplicados
        await waitFor(() => {
          expect(screen.getByText(/Filtros aplicados:/)).toBeInTheDocument();
          expect(screen.getByText(/Data de início: 2025-01-01/)).toBeInTheDocument();
        });
      }
    }
  });

  it('deve exibir mensagem apropriada quando não há dados com filtros aplicados', async () => {
    // Mock para retornar dados vazios
    server.use(
      rest.get('/api/technicians/ranking', (req, res, ctx) => {
        return res(
          ctx.json({
            success: true,
            data: [],
            message: 'Nenhum técnico encontrado com os filtros aplicados'
          })
        );
      })
    );

    const user = userEvent.setup();
    render(<App />);

    // Aguarda o carregamento inicial
    await waitFor(() => {
      expect(screen.getByText('Ranking de Técnicos')).toBeInTheDocument();
    });

    // Aplica filtros que não retornam resultados
    const startDateInput = screen.getByLabelText(/data de início/i) || screen.getByPlaceholderText(/início/i);
    if (startDateInput) {
      await user.type(startDateInput, '2025-01-01');

      // Verifica se a mensagem de "nenhum dado" é exibida
      await waitFor(() => {
        expect(screen.getByText(/Nenhum técnico encontrado/)).toBeInTheDocument();
      });
    }
  });
});