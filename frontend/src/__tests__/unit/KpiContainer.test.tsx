import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, waitFor, cleanup } from '@testing-library/react';
import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';
import { KpiContainer } from '../../components/KpiContainer';

// Mock do Sentry
vi.mock('../../observability/sentry', () => ({
  initSentry: vi.fn()
}));

// Mock do Unleash flags
vi.mock('../../flags/unleash', () => {
  const mockUseFlag = vi.fn(() => false);
  return {
    FlagsProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
    useFlag: mockUseFlag
  };
});

const mockKpisV1Response = [
  {
    level: 'N1',
    total: 150,
    open: 45,
    in_progress: 60,
    closed: 45
  },
  {
    level: 'N2',
    total: 200,
    open: 50,
    in_progress: 80,
    closed: 70
  }
];

const mockKpisV2Response = [
  {
    level: 'N1',
    total: 180,
    open: 55,
    in_progress: 70,
    closed: 55
  },
  {
    level: 'N2',
    total: 220,
    open: 60,
    in_progress: 90,
    closed: 70
  }
];

const server = setupServer(
  http.get('http://localhost:8000/v1/kpis', () => {
    return HttpResponse.json(mockKpisV1Response);
  }),
  http.get('http://localhost:8000/v2/kpis', () => {
    return HttpResponse.json(mockKpisV2Response);
  })
);

describe('KpiContainer', () => {
  beforeAll(() => {
    server.listen();
  });

  afterEach(() => {
    server.resetHandlers();
    vi.clearAllMocks();
    cleanup();
  });

  afterAll(() => {
    server.close();
  });

  it('deve renderizar estado de loading inicialmente', async () => {
    render(<KpiContainer />);
    
    expect(screen.getByText('Carregando...')).toBeInTheDocument();
  });

  it('deve renderizar KPIs corretamente após carregar dados v1', async () => {
    const { useFlag } = await import('../../flags/unleash');
    vi.mocked(useFlag).mockReturnValue(false); // usa v1
    
    render(<KpiContainer />);
    
    await waitFor(() => {
      expect(screen.queryByText('Carregando...')).not.toBeInTheDocument();
    });

    expect(screen.getByText('Flag use_v2_kpis: false')).toBeInTheDocument();
    expect(screen.getByText('N1')).toBeInTheDocument();
    expect(screen.getByText('N2')).toBeInTheDocument();
    expect(screen.getByText('Total: 150')).toBeInTheDocument();
    expect(screen.getByText('Total: 200')).toBeInTheDocument();
    expect(screen.getByText('Abertos: 45')).toBeInTheDocument();
    expect(screen.getByText('Abertos: 50')).toBeInTheDocument();
  });

  it('deve renderizar KPIs corretamente com dados v2', async () => {
    const { useFlag } = await import('../../flags/unleash');
    vi.mocked(useFlag).mockReturnValue(true); // usa v2
    
    render(<KpiContainer />);
    
    await waitFor(() => {
      expect(screen.queryByText('Carregando...')).not.toBeInTheDocument();
    });

    expect(screen.getByText('Flag use_v2_kpis: true')).toBeInTheDocument();
    expect(screen.getByText('N1')).toBeInTheDocument();
    expect(screen.getByText('N2')).toBeInTheDocument();
    expect(screen.getByText('Total: 180')).toBeInTheDocument();
    expect(screen.getByText('Total: 220')).toBeInTheDocument();
    expect(screen.getByText('Abertos: 55')).toBeInTheDocument();
    expect(screen.getByText('Abertos: 60')).toBeInTheDocument();
  });

  it('deve renderizar estado de erro quando API falha', async () => {
    const { useFlag } = await import('../../flags/unleash');
    vi.mocked(useFlag).mockReturnValue(false); // força v1
    
    server.use(
      http.get('http://localhost:8000/v1/kpis', () => {
        return new HttpResponse(null, { status: 500 });
      })
    );

    render(<KpiContainer />);

    await waitFor(() => {
      expect(screen.queryByText('Carregando...')).not.toBeInTheDocument();
    });

    expect(screen.getByText(/Erro:/)).toBeInTheDocument();
    expect(screen.queryByText('N1')).not.toBeInTheDocument();
    expect(screen.queryByText('N2')).not.toBeInTheDocument();
  });

  it('deve renderizar estado de erro quando API retorna JSON inválido', async () => {
    const { useFlag } = await import('../../flags/unleash');
    vi.mocked(useFlag).mockReturnValue(false); // força v1
    
    server.use(
      http.get('http://localhost:8000/v1/kpis', () => {
        return new HttpResponse('invalid json', {
          headers: { 'Content-Type': 'application/json' }
        });
      })
    );

    render(<KpiContainer />);

    await waitFor(() => {
      expect(screen.queryByText('Carregando...')).not.toBeInTheDocument();
    });

    expect(screen.getByText(/Erro:/)).toBeInTheDocument();
  });

  it('deve renderizar estado de erro quando API retorna 404', async () => {
    const { useFlag } = await import('../../flags/unleash');
    vi.mocked(useFlag).mockReturnValue(false); // força v1
    
    server.use(
      http.get('http://localhost:8000/v1/kpis', () => {
        return new HttpResponse(null, { status: 404 });
      })
    );

    render(<KpiContainer />);

    await waitFor(() => {
      expect(screen.queryByText('Carregando...')).not.toBeInTheDocument();
    });

    expect(screen.getByText(/Erro:/)).toBeInTheDocument();
    expect(screen.getByText(/HTTP 404/)).toBeInTheDocument();
  });

  it('deve renderizar grid com layout correto', async () => {
    render(<KpiContainer />);

    await waitFor(() => {
      expect(screen.queryByText('Carregando...')).not.toBeInTheDocument();
    });

    const gridElement = screen.getByText('N1').closest('div')?.parentElement;
    expect(gridElement).toHaveStyle({
      display: 'grid',
      gridTemplateColumns: 'repeat(2, 1fr)',
      gap: '12px'
    });
  });

  it('deve renderizar lista vazia quando API retorna array vazio', async () => {
    const { useFlag } = await import('../../flags/unleash');
    vi.mocked(useFlag).mockReturnValue(false); // força v1
    
    server.use(
      http.get('http://localhost:8000/v1/kpis', () => {
        return HttpResponse.json([]);
      })
    );

    render(<KpiContainer />);

    await waitFor(() => {
      expect(screen.queryByText('Carregando...')).not.toBeInTheDocument();
    });


    
    expect(screen.getByText('Flag use_v2_kpis: false')).toBeInTheDocument();
    expect(screen.queryByText('N1')).not.toBeInTheDocument();
    expect(screen.queryByText('N2')).not.toBeInTheDocument();
  });

  it('deve usar URL correta baseada na flag', async () => {
    const { useFlag } = await import('../../flags/unleash');
    // Teste com v1
    vi.mocked(useFlag).mockReturnValue(false);
    render(<KpiContainer />);
    
    await waitFor(() => {
      expect(screen.queryByText('Carregando...')).not.toBeInTheDocument();
    });
    
    expect(screen.getByText('Flag use_v2_kpis: false')).toBeInTheDocument();
  });

  it('deve renderizar múltiplos KpiCards corretamente', async () => {
    render(<KpiContainer />);

    await waitFor(() => {
      expect(screen.queryByText('Carregando...')).not.toBeInTheDocument();
    });

    // Verifica se ambos os cards est�o presentes
    expect(screen.getByText('N1')).toBeInTheDocument();
    expect(screen.getByText('N2')).toBeInTheDocument();
    
    // Verifica se os dados est�o corretos para cada card
    const n1Card = screen.getByText('N1').closest('div');
    const n2Card = screen.getByText('N2').closest('div');
    
    expect(n1Card).toHaveTextContent('Total: 150');
    expect(n1Card).toHaveTextContent('Abertos: 45');
    expect(n1Card).toHaveTextContent('Em Andamento: 60');
    expect(n1Card).toHaveTextContent('Fechados: 45');
    
    expect(n2Card).toHaveTextContent('Total: 200');
    expect(n2Card).toHaveTextContent('Abertos: 50');
    expect(n2Card).toHaveTextContent('Em Andamento: 80');
    expect(n2Card).toHaveTextContent('Fechados: 70');
  });
});
