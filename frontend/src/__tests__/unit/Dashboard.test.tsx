import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import React from 'react';
import Dashboard from '../../components/Dashboard';
import { httpClient } from '../../services/httpClient';

// Mock do httpClient
vi.mock('../../services/httpClient', () => ({
  httpClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

// Mock do Chart.js
vi.mock('react-chartjs-2', () => ({
  Bar: ({ data, options }: any) => (
    <div data-testid="bar-chart">
      {JSON.stringify({ data, options })}
    </div>
  ),
  Line: ({ data, options }: any) => (
    <div data-testid="line-chart">
      {JSON.stringify({ data, options })}
    </div>
  ),
  Doughnut: ({ data, options }: any) => (
    <div data-testid="doughnut-chart">
      {JSON.stringify({ data, options })}
    </div>
  ),
}));

// Mock do framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    h1: ({ children, ...props }: any) => <h1 {...props}>{children}</h1>,
    p: ({ children, ...props }: any) => <p {...props}>{children}</p>,
  },
  AnimatePresence: ({ children }: any) => <>{children}</>,
}));

const mockMetricsData = {
  level_metrics: {
    N1: {
      'Novo': 10,
      'Processando (atribuido)': 5,
      'Processando (planejado)': 3,
      'Pendente': 2,
      'Solucionado': 8,
      'Fechado': 12,
    },
    N2: {
      'Novo': 15,
      'Processando (atribuido)': 7,
      'Processando (planejado)': 4,
      'Pendente': 3,
      'Solucionado': 6,
      'Fechado': 9,
    },
    N3: {
      'Novo': 8,
      'Processando (atribuido)': 4,
      'Processando (planejado)': 2,
      'Pendente': 1,
      'Solucionado': 5,
      'Fechado': 7,
    },
    N4: {
      'Novo': 12,
      'Processando (atribuido)': 6,
      'Processando (planejado)': 3,
      'Pendente': 2,
      'Solucionado': 4,
      'Fechado': 8,
    },
  },
  general_metrics: {
    'Novo': 45,
    'Processando (atribuido)': 22,
    'Processando (planejado)': 12,
    'Pendente': 8,
    'Solucionado': 23,
    'Fechado': 36,
  },
};

describe('Dashboard Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('deve renderizar o dashboard corretamente', async () => {
    const mockGet = vi.mocked(httpClient.get);
    mockGet.mockResolvedValue({ data: mockMetricsData });

    render(<Dashboard />);

    // Verifica se o titulo esta presente
    expect(screen.getByText(/Dashboard GLPI/i)).toBeInTheDocument();

    // Aguarda o carregamento dos dados
    await waitFor(() => {
      expect(screen.queryByText(/Carregando/i)).not.toBeInTheDocument();
    });

    // Verifica se os graficos foram renderizados
    expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
    expect(screen.getByTestId('doughnut-chart')).toBeInTheDocument();
  });

  it('deve exibir estado de carregamento', () => {
    const mockGet = vi.mocked(httpClient.get);
    mockGet.mockImplementation(() => new Promise(() => {})); // Promise que nunca resolve

    render(<Dashboard />);

    expect(screen.getByText(/Carregando/i)).toBeInTheDocument();
  });

  it('deve exibir erro quando a API falha', async () => {
    const mockGet = vi.mocked(httpClient.get);
    mockGet.mockRejectedValue(new Error('API Error'));

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText(/Erro ao carregar dados/i)).toBeInTheDocument();
    });
  });

  it('deve atualizar dados quando o botao de refresh e clicado', async () => {
    const mockGet = vi.mocked(httpClient.get);
    mockGet.mockResolvedValue({ data: mockMetricsData });

    render(<Dashboard />);

    // Aguarda carregamento inicial
    await waitFor(() => {
      expect(screen.queryByText(/Carregando/i)).not.toBeInTheDocument();
    });

    // Clica no botao de refresh
    const refreshButton = screen.getByRole('button', { name: /atualizar/i });
    fireEvent.click(refreshButton);

    // Verifica se a API foi chamada novamente
    expect(mockGet).toHaveBeenCalledTimes(2);
  });

  it('deve filtrar dados por data', async () => {
    const mockGet = vi.mocked(httpClient.get);
    mockGet.mockResolvedValue({ data: mockMetricsData });

    render(<Dashboard />);

    // Aguarda carregamento inicial
    await waitFor(() => {
      expect(screen.queryByText(/Carregando/i)).not.toBeInTheDocument();
    });

    // Simula selecao de filtro de data
    const startDateInput = screen.getByLabelText(/Data inicial/i);
    const endDateInput = screen.getByLabelText(/Data final/i);

    fireEvent.change(startDateInput, { target: { value: '2024-01-01' } });
    fireEvent.change(endDateInput, { target: { value: '2024-01-31' } });

    const applyFilterButton = screen.getByRole('button', { name: /aplicar filtro/i });
    fireEvent.click(applyFilterButton);

    // Verifica se a API foi chamada com os parametros corretos
    await waitFor(() => {
      expect(mockGet).toHaveBeenCalledWith('/api/metrics', {
        params: {
          start_date: '2024-01-01',
          end_date: '2024-01-31',
        },
      });
    });
  });

  it('deve exibir metricas corretas nos cards', async () => {
    const mockGet = vi.mocked(httpClient.get);
    mockGet.mockResolvedValue({ data: mockMetricsData });

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.queryByText(/Carregando/i)).not.toBeInTheDocument();
    });

    // Verifica se os totais estao corretos
    expect(screen.getByText('45')).toBeInTheDocument(); // Total Novo
    expect(screen.getByText('22')).toBeInTheDocument(); // Total Processando (atribuido)
    expect(screen.getByText('23')).toBeInTheDocument(); // Total Solucionado
  });

  it('deve alternar entre visualizacoes de grafico', async () => {
    const mockGet = vi.mocked(httpClient.get);
    mockGet.mockResolvedValue({ data: mockMetricsData });

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.queryByText(/Carregando/i)).not.toBeInTheDocument();
    });

    // Verifica se o grafico de barras esta visivel inicialmente
    expect(screen.getByTestId('bar-chart')).toBeInTheDocument();

    // Clica no botao para alternar para grafico de linha
    const lineChartButton = screen.getByRole('button', { name: /grafico de linha/i });
    fireEvent.click(lineChartButton);

    // Verifica se o grafico de linha esta visivel
    expect(screen.getByTestId('line-chart')).toBeInTheDocument();
  });

  it('deve validar formato de data nos filtros', async () => {
    const mockGet = vi.mocked(httpClient.get);
    mockGet.mockResolvedValue({ data: mockMetricsData });

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.queryByText(/Carregando/i)).not.toBeInTheDocument();
    });

    // Tenta inserir data invalida
    const startDateInput = screen.getByLabelText(/Data inicial/i);
    fireEvent.change(startDateInput, { target: { value: 'data-invalida' } });

    const applyFilterButton = screen.getByRole('button', { name: /aplicar filtro/i });
    fireEvent.click(applyFilterButton);

    // Verifica se a mensagem de erro e exibida
    await waitFor(() => {
      expect(screen.getByText(/Formato de data invalido/i)).toBeInTheDocument();
    });
  });

  it('deve exibir tooltip nos graficos', async () => {
    const mockGet = vi.mocked(httpClient.get);
    mockGet.mockResolvedValue({ data: mockMetricsData });

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.queryByText(/Carregando/i)).not.toBeInTheDocument();
    });

    // Simula hover sobre elemento do grafico
    const chartElement = screen.getByTestId('bar-chart');
    fireEvent.mouseEnter(chartElement);

    // Verifica se o tooltip e exibido (implementacao especifica pode variar)
    // Esta verificacao depende da implementacao especifica do tooltip
  });

  it('deve ser responsivo em diferentes tamanhos de tela', async () => {
    const mockGet = vi.mocked(httpClient.get);
    mockGet.mockResolvedValue({ data: mockMetricsData });

    // Simula tela mobile
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375,
    });

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.queryByText(/Carregando/i)).not.toBeInTheDocument();
    });

    // Verifica se o layout mobile esta ativo
    const container = screen.getByTestId('dashboard-container');
    expect(container).toHaveClass('mobile-layout');
  });

  it('deve exportar dados quando solicitado', async () => {
    const mockGet = vi.mocked(httpClient.get);
    mockGet.mockResolvedValue({ data: mockMetricsData });

    // Mock da funcao de download
    const mockDownload = vi.fn();
    global.URL.createObjectURL = vi.fn();
    global.URL.revokeObjectURL = vi.fn();
    
    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.queryByText(/Carregando/i)).not.toBeInTheDocument();
    });

    // Clica no botao de exportar
    const exportButton = screen.getByRole('button', { name: /exportar/i });
    fireEvent.click(exportButton);

    // Verifica se a funcao de download foi chamada
    // (implementacao especifica pode variar)
  });

  it('deve manter estado dos filtros apos atualizacao', async () => {
    const mockGet = vi.mocked(httpClient.get);
    mockGet.mockResolvedValue({ data: mockMetricsData });

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.queryByText(/Carregando/i)).not.toBeInTheDocument();
    });

    // Define filtros
    const startDateInput = screen.getByLabelText(/Data inicial/i);
    fireEvent.change(startDateInput, { target: { value: '2024-01-01' } });

    // Atualiza dados
    const refreshButton = screen.getByRole('button', { name: /atualizar/i });
    fireEvent.click(refreshButton);

    // Verifica se o filtro foi mantido
    expect(startDateInput).toHaveValue('2024-01-01');
  });

  it('deve calcular percentuais corretamente', async () => {
    const mockGet = vi.mocked(httpClient.get);
    mockGet.mockResolvedValue({ data: mockMetricsData });

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.queryByText(/Carregando/i)).not.toBeInTheDocument();
    });

    // Verifica se os percentuais estao corretos
    // Total geral: 146 tickets
    // Novo: 45/146 ≈ 30.8%
    expect(screen.getByText(/30\.8%/)).toBeInTheDocument();
  });

  it('deve lidar com dados vazios graciosamente', async () => {
    const mockGet = vi.mocked(httpClient.get);
    mockGet.mockResolvedValue({ 
      data: {
        level_metrics: {},
        general_metrics: {}
      }
    });

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.queryByText(/Carregando/i)).not.toBeInTheDocument();
    });

    // Verifica se a mensagem de "sem dados" e exibida
    expect(screen.getByText(/Nenhum dado disponivel/i)).toBeInTheDocument();
  });
});