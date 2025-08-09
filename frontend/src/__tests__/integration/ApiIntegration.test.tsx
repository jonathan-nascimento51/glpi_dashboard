import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import React from 'react';
import { httpClient } from '../../services/httpClient';
import { useApi } from '../../hooks/useApi';

// Mock do httpClient
vi.mock('../../services/httpClient', () => ({
  httpClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
  API_CONFIG: {
    BASE_URL: 'http://localhost:5000/api',
    TIMEOUT: 10000,
    RETRY_ATTEMPTS: 3,
    RETRY_DELAY: 1000,
  },
}));

// Componente de teste que usa o hook useApi
const TestComponent: React.FC<{ endpoint: string }> = ({ endpoint }) => {
  const apiFunction = async (params?: any) => {
    const response = await httpClient.get(endpoint, { params });
    return response.data;
  };

  const { data, loading, error, execute } = useApi(apiFunction);

  return (
    <div>
      <button onClick={() => execute({ test: 'param' })}>Carregar Dados</button>
      {loading && <div data-testid="loading">Carregando...</div>}
      {error && <div data-testid="error">Erro: {error}</div>}
      {data && (
        <div data-testid="data">
          {JSON.stringify(data)}
        </div>
      )}
    </div>
  );
};

// Componente que testa auto-execução
const AutoExecuteComponent: React.FC = () => {
  const apiFunction = async () => {
    const response = await httpClient.get('/metrics');
    return response.data;
  };

  const { data, loading, error } = useApi(apiFunction, { autoExecute: true });

  return (
    <div>
      {loading && <div data-testid="auto-loading">Auto Carregando...</div>}
      {error && <div data-testid="auto-error">Auto Erro: {error}</div>}
      {data && (
        <div data-testid="auto-data">
          {JSON.stringify(data)}
        </div>
      )}
    </div>
  );
};

// Componente que testa diferentes tipos de erro
const ErrorTestComponent: React.FC<{ errorType: string }> = ({ errorType }) => {
  const apiFunction = async () => {
    switch (errorType) {
      case 'network':
        throw new Error('Network Error');
      case 'timeout':
        throw new Error('Request timeout');
      case 'auth':
        throw new Error('Authentication failed');
      case 'server':
        throw new Error('Internal server error');
      default:
        const response = await httpClient.get('/test');
        return response.data;
    }
  };

  const { data, loading, error, execute } = useApi(apiFunction);

  return (
    <div>
      <button onClick={() => execute()}>Testar {errorType}</button>
      {loading && <div data-testid="error-loading">Carregando...</div>}
      {error && <div data-testid="error-message">{error}</div>}
      {data && <div data-testid="error-data">{JSON.stringify(data)}</div>}
    </div>
  );
};

describe('Integração API - Componentes com httpClient', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('deve fazer requisição GET com parâmetros corretamente', async () => {
    const mockData = { id: 1, name: 'Test Data' };
    const mockGet = vi.mocked(httpClient.get);
    mockGet.mockResolvedValue({ data: mockData });

    render(<TestComponent endpoint="/test-endpoint" />);

    const button = screen.getByText('Carregar Dados');
    fireEvent.click(button);

    // Verificar loading
    expect(screen.getByTestId('loading')).toBeInTheDocument();

    // Aguardar dados
    await waitFor(() => {
      expect(screen.getByTestId('data')).toBeInTheDocument();
    });

    // Verificar se a requisição foi feita corretamente
    expect(mockGet).toHaveBeenCalledWith('/test-endpoint', {
      params: { test: 'param' }
    });

    // Verificar dados renderizados
    expect(screen.getByTestId('data')).toHaveTextContent(JSON.stringify(mockData));
    expect(screen.queryByTestId('loading')).not.toBeInTheDocument();
    expect(screen.queryByTestId('error')).not.toBeInTheDocument();
  });

  it('deve executar automaticamente quando autoExecute é true', async () => {
    const mockData = { metrics: { total: 100 } };
    const mockGet = vi.mocked(httpClient.get);
    mockGet.mockResolvedValue({ data: mockData });

    render(<AutoExecuteComponent />);

    // Verificar loading inicial
    expect(screen.getByTestId('auto-loading')).toBeInTheDocument();

    // Aguardar dados
    await waitFor(() => {
      expect(screen.getByTestId('auto-data')).toBeInTheDocument();
    });

    // Verificar se a requisição foi feita automaticamente
    expect(mockGet).toHaveBeenCalledWith('/metrics');
    expect(screen.getByTestId('auto-data')).toHaveTextContent(JSON.stringify(mockData));
  });

  it('deve tratar erro de rede corretamente', async () => {
    render(<ErrorTestComponent errorType="network" />);

    const button = screen.getByText('Testar network');
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByTestId('error-message')).toBeInTheDocument();
    });

    expect(screen.getByTestId('error-message')).toHaveTextContent('Network Error');
    expect(screen.queryByTestId('error-loading')).not.toBeInTheDocument();
  });

  it('deve tratar erro de timeout corretamente', async () => {
    render(<ErrorTestComponent errorType="timeout" />);

    const button = screen.getByText('Testar timeout');
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByTestId('error-message')).toBeInTheDocument();
    });

    expect(screen.getByTestId('error-message')).toHaveTextContent('Request timeout');
  });

  it('deve tratar erro de autenticação corretamente', async () => {
    render(<ErrorTestComponent errorType="auth" />);

    const button = screen.getByText('Testar auth');
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByTestId('error-message')).toBeInTheDocument();
    });

    expect(screen.getByTestId('error-message')).toHaveTextContent('Authentication failed');
  });

  it('deve tratar erro de servidor corretamente', async () => {
    render(<ErrorTestComponent errorType="server" />);

    const button = screen.getByText('Testar server');
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByTestId('error-message')).toBeInTheDocument();
    });

    expect(screen.getByTestId('error-message')).toHaveTextContent('Internal server error');
  });

  it('deve limpar erro ao fazer nova requisição bem-sucedida', async () => {
    const mockGet = vi.mocked(httpClient.get);
    
    render(<TestComponent endpoint="/test" />);
    const button = screen.getByText('Carregar Dados');

    // Primeira requisição com erro
    mockGet.mockRejectedValueOnce(new Error('Primeiro erro'));
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByTestId('error')).toBeInTheDocument();
    });

    expect(screen.getByTestId('error')).toHaveTextContent('Erro: Primeiro erro');

    // Segunda requisição com sucesso
    const successData = { success: true };
    mockGet.mockResolvedValueOnce({ data: successData });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByTestId('data')).toBeInTheDocument();
    });

    expect(screen.getByTestId('data')).toHaveTextContent(JSON.stringify(successData));
    expect(screen.queryByTestId('error')).not.toBeInTheDocument();
  });

  it('deve cancelar requisição anterior quando nova é iniciada', async () => {
    const mockGet = vi.mocked(httpClient.get);
    
    render(<TestComponent endpoint="/slow-endpoint" />);
    const button = screen.getByText('Carregar Dados');

    // Primeira requisição lenta
    mockGet.mockImplementationOnce(
      () => new Promise(resolve => 
        setTimeout(() => resolve({ data: { result: 'first' } }), 200)
      )
    );

    // Segunda requisição rápida
    mockGet.mockImplementationOnce(
      () => new Promise(resolve => 
        setTimeout(() => resolve({ data: { result: 'second' } }), 50)
      )
    );

    // Primeira requisição
    fireEvent.click(button);
    expect(screen.getByTestId('loading')).toBeInTheDocument();

    // Segunda requisição antes da primeira terminar
    fireEvent.click(button);

    // Aguardar resultado
    await waitFor(() => {
      expect(screen.getByTestId('data')).toBeInTheDocument();
    }, { timeout: 300 });

    // Deve mostrar resultado da segunda requisição
    expect(screen.getByTestId('data')).toHaveTextContent('"result":"second"');
  });

  it('deve manter configuração do httpClient', async () => {
    const { API_CONFIG } = await import('../../services/httpClient');
    
    expect(API_CONFIG.BASE_URL).toBe('http://localhost:5000/api');
    expect(API_CONFIG.TIMEOUT).toBe(10000);
    expect(API_CONFIG.RETRY_ATTEMPTS).toBe(3);
    expect(API_CONFIG.RETRY_DELAY).toBe(1000);
  });
});