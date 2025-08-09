import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { httpClient } from '../../services/httpClient';
import { apiService } from '../../services/api';

// Mock do httpClient
vi.mock('../../services/httpClient', () => ({
  httpClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
  API_CONFIG: {
    BASE_URL: 'http://localhost:8000/v1',
    TIMEOUT: 30000,
    RETRY_ATTEMPTS: 3,
    RETRY_DELAY: 1000,
  },
  updateAuthTokens: vi.fn(),
}));

// Mock do apiService
vi.mock('../../services/api', () => ({
  apiService: {
    getMetrics: vi.fn(),
    getSystemStatus: vi.fn(),
    getTechnicianRanking: vi.fn(),
    getNewTickets: vi.fn(),
  },
}));

// Componente de teste que consome a API
const TestApiConsumer: React.FC = () => {
  const [data, setData] = React.useState<any>(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiService.getMetrics();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button onClick={fetchData} data-testid="fetch-button">
        Buscar Dados
      </button>
      
      {loading && <div data-testid="loading">Carregando...</div>}
      
      {error && (
        <div data-testid="error" role="alert">
          Erro: {error}
        </div>
      )}
      
      {data && (
        <div data-testid="success">
          <h2>Dados carregados com sucesso</h2>
          <pre>{JSON.stringify(data, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

describe('ApiConsumer Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  it('deve mostrar estado de loading durante a requisição', async () => {
    // Mock de uma requisição que demora para resolver
    const mockGetMetrics = vi.mocked(apiService.getMetrics);
    mockGetMetrics.mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve({ niveis: {} }), 100))
    );

    render(<TestApiConsumer />);
    
    const fetchButton = screen.getByTestId('fetch-button');
    fireEvent.click(fetchButton);

    // Verificar se o loading aparece
    expect(screen.getByTestId('loading')).toBeInTheDocument();
    expect(screen.getByText('Carregando...')).toBeInTheDocument();

    // Aguardar a requisição terminar
    await waitFor(() => {
      expect(screen.queryByTestId('loading')).not.toBeInTheDocument();
    });
  });

  it('deve mostrar dados de sucesso quando a API retorna dados válidos', async () => {
    const mockData = {
      niveis: {
        geral: { novos: 10, pendentes: 5, progresso: 3, resolvidos: 20, total: 38 },
        n1: { novos: 5, pendentes: 2, progresso: 1, resolvidos: 10, total: 18 },
        n2: { novos: 3, pendentes: 2, progresso: 1, resolvidos: 5, total: 11 },
        n3: { novos: 2, pendentes: 1, progresso: 1, resolvidos: 3, total: 7 },
        n4: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 2, total: 2 }
      },
      tendencias: { novos: '+5%', pendentes: '-2%', progresso: '+1%', resolvidos: '+10%' }
    };

    const mockGetMetrics = vi.mocked(apiService.getMetrics);
    mockGetMetrics.mockResolvedValue(mockData);

    render(<TestApiConsumer />);
    
    const fetchButton = screen.getByTestId('fetch-button');
    fireEvent.click(fetchButton);

    // Aguardar os dados aparecerem
    await waitFor(() => {
      expect(screen.getByTestId('success')).toBeInTheDocument();
    });

    expect(screen.getByText('Dados carregados com sucesso')).toBeInTheDocument();
    expect(screen.getByText(/"novos": 10/)).toBeInTheDocument();
  });

  it('deve mostrar erro quando a API falha', async () => {
    const errorMessage = 'Falha na conexão com o servidor';
    
    const mockGetMetrics = vi.mocked(apiService.getMetrics);
    mockGetMetrics.mockRejectedValue(new Error(errorMessage));

    render(<TestApiConsumer />);
    
    const fetchButton = screen.getByTestId('fetch-button');
    fireEvent.click(fetchButton);

    // Aguardar o erro aparecer
    await waitFor(() => {
      expect(screen.getByTestId('error')).toBeInTheDocument();
    });

    expect(screen.getByRole('alert')).toBeInTheDocument();
    expect(screen.getByText(`Erro: ${errorMessage}`)).toBeInTheDocument();
  });

  it('deve limpar erro anterior ao fazer nova requisição', async () => {
    const mockGetMetrics = vi.mocked(apiService.getMetrics);
    
    // Primeira requisição com erro
    mockGetMetrics.mockRejectedValueOnce(new Error('Primeiro erro'));
    
    render(<TestApiConsumer />);
    
    const fetchButton = screen.getByTestId('fetch-button');
    fireEvent.click(fetchButton);

    // Aguardar o erro aparecer
    await waitFor(() => {
      expect(screen.getByTestId('error')).toBeInTheDocument();
    });

    // Segunda requisição com sucesso
    mockGetMetrics.mockResolvedValueOnce({ niveis: {}, tendencias: {} });
    
    fireEvent.click(fetchButton);

    // Verificar que o erro foi limpo durante o loading
    expect(screen.getByTestId('loading')).toBeInTheDocument();
    expect(screen.queryByTestId('error')).not.toBeInTheDocument();

    // Aguardar sucesso
    await waitFor(() => {
      expect(screen.getByTestId('success')).toBeInTheDocument();
    });
  });

  it('deve não mostrar loading quando não há requisição ativa', () => {
    render(<TestApiConsumer />);
    
    expect(screen.queryByTestId('loading')).not.toBeInTheDocument();
    expect(screen.queryByTestId('error')).not.toBeInTheDocument();
    expect(screen.queryByTestId('success')).not.toBeInTheDocument();
  });
});

// Teste para verificar tratamento de diferentes tipos de erro
describe('API Error Handling', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('deve tratar erro de rede', async () => {
    const networkError = new Error('Network Error');
    networkError.name = 'NetworkError';
    
    const mockGetMetrics = vi.mocked(apiService.getMetrics);
    mockGetMetrics.mockRejectedValue(networkError);

    render(<TestApiConsumer />);
    
    const fetchButton = screen.getByTestId('fetch-button');
    fireEvent.click(fetchButton);

    await waitFor(() => {
      expect(screen.getByText('Erro: Network Error')).toBeInTheDocument();
    });
  });

  it('deve tratar timeout', async () => {
    const timeoutError = new Error('Request timeout');
    timeoutError.name = 'TimeoutError';
    
    const mockGetMetrics = vi.mocked(apiService.getMetrics);
    mockGetMetrics.mockRejectedValue(timeoutError);

    render(<TestApiConsumer />);
    
    const fetchButton = screen.getByTestId('fetch-button');
    fireEvent.click(fetchButton);

    await waitFor(() => {
      expect(screen.getByText('Erro: Request timeout')).toBeInTheDocument();
    });
  });

  it('deve tratar erro de autenticação', async () => {
    const authError = new Error('Authentication failed');
    authError.name = 'AuthenticationError';
    
    const mockGetMetrics = vi.mocked(apiService.getMetrics);
    mockGetMetrics.mockRejectedValue(authError);

    render(<TestApiConsumer />);
    
    const fetchButton = screen.getByTestId('fetch-button');
    fireEvent.click(fetchButton);

    await waitFor(() => {
      expect(screen.getByText('Erro: Authentication failed')).toBeInTheDocument();
    });
  });
});
