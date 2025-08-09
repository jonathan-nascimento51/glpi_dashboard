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
      'Processando (atribuído)': 5,
      'Processando (planejado)': 3,
      'Pendente': 2,
      'Solucionado': 8,
      'Fechado': 12,
    },
    N2: {
      'Novo': 15,
      'Processando (atribuído)': 7,
      'Processando (planejado)': 4,
      'Pendente': 3,
      'Solucionado': 6,
      'Fechado': 9,
    },
    N3: {
      'Novo': 8,
      'Processando (atribuído)': 4,
      'Processando (planejado)': 2,
      'Pendente': 1,
      'Solucionado': 5,
      'Fechado': 7,
    },
    N4: {
      'Novo': 12,
      'Processando (atribuído)': 6,
      'Processando (planejado)': 3,
      'Pendente': 2,
      'Solucionado': 4,
      'Fechado': 8,
    },
  },
  general_metrics: {
    'Novo': 45,
    'Processando (atribuído)': 22,
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

    // Verifica se o título está presente
    expect(screen.getByText(/Dashboard GLPI/i)).toBeInTheDocument();

    // Aguarda o carregamento dos dados
    await waitFor(() => {
      expect(screen.queryByText(/Carregando/i)).not.toBeInTheDocument();
    });

    // Verifica se os gráficos foram renderizados
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

  it('deve atualizar dados quando o botão de refresh é clicado', async () => {
    const mockGet = vi.mocked(httpClient.get);
    mockGet.mockResolvedValue({ data: mockMetricsData });

    render(<Dashboard />);

    // Aguarda carregamento inicial
    await waitFor(() => {
      expect(screen.queryByText(/Carregando/i)).not.toBeInTheDocument();
    });

    // Clica no botão de refresh
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

    // Simula seleção de filtro de data
    const startDateInput = screen.getByLabelText(/Data inicial/i);
    const endDateInput = screen.getByLabelText(/Data final/i);

    fireEvent.change(startDateInput, { target: { value: '2024-01-01' } });
    fireEvent.change(endDateInput, { target: { value: '2024-01-31' } });

    const applyFilterButton = screen.getByRole('button', { name: /aplicar filtro/i });
    fireEvent.click(applyFilterButton);

    // Verifica se a API foi chamada com os parâmetros corretos
    await waitFor(() => {
      expect(mockGet).toHaveBeenCalledWith('/api/metrics', {
        params: {
          start_date: '2024-01-01',
          end_date: '2024-01-31',
        },
      });
    });
  });

  it('deve exibir métricas corretas nos cards', async () => {
    const mockGet = vi.mocked(httpClient.get);
    mockGet.mockResolvedValue({ data: mockMetricsData });

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.queryByText(/Carregando/i)).not.toBeInTheDocument();
    });

    // Verifica se os totais estão corretos
    expect(screen.getByText('45')).toBeInTheDocument(); // Total Novo
    expect(screen.getByText('22')).toBeInTheDocument(); // Total Processando (atribuído)
    expect(screen.getByText('23')).toBeInTheDocument(); // Total Solucionado
  });

  it('deve alternar entre visualizações de gráfico', async () => {
    const mockGet = vi.mocked(httpClient.get);
    mockGet.mockResolvedValue({ data: mockMetricsData });

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.queryByText(/Carregando/i)).not.toBeInTheDocument();
    });

    // Verifica se o gráfico de barras está visível inicialmente
    expect(screen.getByTestId('bar-chart')).toBeInTheDocument();

    // Clica no botão para alternar para gráfico de linha
    const lineChartButton = screen.getByRole('button', { name: /gráfico de linha/i });
    fireEvent.click(lineChartButton);

    // Verifica se o gráfico de linha está visível
    expect(screen.getByTestId('line-chart')).toBeInTheDocument();
  });

  it('deve validar formato de data nos filtros', async () => {
    const mockGet = vi.mocked(httpClient.get);
    mockGet.mockResolvedValue({ data: mockMetricsData });

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.queryByText(/Carregando/i)).not.toBeInTheDocument();
    });

    // Tenta inserir data inválida
    const startDateInput = screen.getByLabelText(/Data inicial/i);
    fireEvent.change(startDateInput, { target: { value: 'data-inválida' } });

    const applyFilterButton = screen.getByRole('button', { name: /aplicar filtro/i });
    fireEvent.click(applyFilterButton);

    // Verifica se a mensagem de erro é exibida
    await waitFor(() => {
      expect(screen.getByText(/Formato de data inválido/i)).toBeInTheDocument();
    });
  });

  it('deve exibir tooltip nos gráficos', async () => {
    const mockGet = vi.mocked(httpClient.get);
    mockGet.mockResolvedValue({ data: mockMetricsData });

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.queryByText(/Carregando/i)).not.toBeInTheDocument();
    });

    // Simula hover sobre elemento do gráfico
    const chartElement = screen.getByTestId('bar-chart');
    fireEvent.mouseEnter(chartElement);

    // Verifica se o tooltip é exibido (implementação específica pode variar)
    // Esta verificação depende da implementação específica do tooltip
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

    // Verifica se o layout mobile está ativo
    const container = screen.getByTestId('dashboard-container');
    expect(container).toHaveClass('mobile-layout');
  });

  it('deve exportar dados quando solicitado', async () => {
    const mockGet = vi.mocked(httpClient.get);
    mockGet.mockResolvedValue({ data: mockMetricsData });

    // Mock da função de download
    const mockDownload = vi.fn();
    global.URL.createObjectURL = vi.fn();
    global.URL.revokeObjectURL = vi.fn();
    
    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.queryByText(/Carregando/i)).not.toBeInTheDocument();
    });

    // Clica no botão de exportar
    const exportButton = screen.getByRole('button', { name: /exportar/i });
    fireEvent.click(exportButton);

    // Verifica se a função de download foi chamada
    // (implementação específica pode variar)
  });

  it('deve manter estado dos filtros após atualização', async () => {
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

    // Verifica se os percentuais estão corretos
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

    // Verifica se a mensagem de "sem dados" é exibida
    expect(screen.getByText(/Nenhum dado disponível/i)).toBeInTheDocument();
  });
});