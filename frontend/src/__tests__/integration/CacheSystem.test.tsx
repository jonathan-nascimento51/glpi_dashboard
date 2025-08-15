import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { useApi } from '../../hooks/useApi';
import { useCache } from '../../hooks/useCache';
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

// Mock do localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Componente de teste que usa cache e API
const TestComponent: React.FC<{
  cacheKey: string;
  apiEndpoint: string;
  defaultValue?: any;
  ttl?: number;
}> = ({ cacheKey, apiEndpoint, defaultValue = null, ttl = 5000 }) => {
  const { value: cachedValue, setValue: setCachedValue, isExpired, clearCache } = useCache(
    cacheKey,
    defaultValue,
    { ttl }
  );

  const apiFunction = React.useCallback(
    () => httpClient.get(apiEndpoint),
    [apiEndpoint]
  );

  const { data: apiData, loading, error, execute } = useApi(apiFunction);

  // Efeito para sincronizar dados da API com cache
  React.useEffect(() => {
    if (apiData && !error) {
      setCachedValue(apiData);
    }
  }, [apiData, error, setCachedValue]);

  // Carrega dados da API se cache expirou ou esta vazio
  React.useEffect(() => {
    if (isExpired || (!cachedValue && !loading)) {
      execute();
    }
  }, [isExpired, cachedValue, loading, execute]);

  const handleRefresh = () => {
    clearCache();
    execute();
  };

  const handleClearCache = () => {
    clearCache();
  };

  return (
    <div>
      <div data-testid="loading">{loading ? 'Loading...' : 'Not Loading'}</div>
      <div data-testid="error">{error || 'No Error'}</div>
      <div data-testid="cached-value">
        {cachedValue ? JSON.stringify(cachedValue) : 'No Cached Value'}
      </div>
      <div data-testid="api-data">
        {apiData ? JSON.stringify(apiData) : 'No API Data'}
      </div>
      <div data-testid="is-expired">{isExpired ? 'Expired' : 'Not Expired'}</div>
      <button onClick={handleRefresh} data-testid="refresh-btn">
        Refresh
      </button>
      <button onClick={handleClearCache} data-testid="clear-cache-btn">
        Clear Cache
      </button>
    </div>
  );
};

describe('Cache System Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
    localStorageMock.getItem.mockReturnValue(null);
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.useRealTimers();
  });

  it('deve carregar dados da API quando cache esta vazio', async () => {
    const mockApiData = { id: 1, name: 'Test Data' };
    (httpClient.get as any).mockResolvedValueOnce(mockApiData);

    render(
      <TestComponent 
        cacheKey="test-cache" 
        apiEndpoint="/api/test" 
        defaultValue={null}
      />
    );

    // Inicialmente deve mostrar loading
    expect(screen.getByTestId('loading')).toHaveTextContent('Loading...');
    expect(screen.getByTestId('cached-value')).toHaveTextContent('No Cached Value');

    // Aguarda a requisicao da API
    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('Not Loading');
    });

    // Verifica se os dados foram carregados e salvos no cache
    expect(screen.getByTestId('api-data')).toHaveTextContent(JSON.stringify(mockApiData));
    expect(screen.getByTestId('cached-value')).toHaveTextContent(JSON.stringify(mockApiData));
    expect(localStorageMock.setItem).toHaveBeenCalled();
  });

  it('deve usar dados do cache quando disponiveis e validos', async () => {
    const cachedData = { id: 2, name: 'Cached Data' };
    const cacheEntry = {
      value: cachedData,
      timestamp: Date.now(),
      ttl: 5000
    };
    
    localStorageMock.getItem.mockReturnValue(JSON.stringify(cacheEntry));

    render(
      <TestComponent 
        cacheKey="test-cache" 
        apiEndpoint="/api/test" 
      />
    );

    // Deve usar dados do cache imediatamente
    expect(screen.getByTestId('cached-value')).toHaveTextContent(JSON.stringify(cachedData));
    expect(screen.getByTestId('is-expired')).toHaveTextContent('Not Expired');
    expect(screen.getByTestId('loading')).toHaveTextContent('Not Loading');
    
    // Nao deve fazer requisicao a API
    expect(httpClient.get).not.toHaveBeenCalled();
  });

  it('deve recarregar dados quando cache expira', async () => {
    const expiredData = { id: 3, name: 'Expired Data' };
    const newData = { id: 4, name: 'Fresh Data' };
    
    const expiredCacheEntry = {
      value: expiredData,
      timestamp: Date.now() - 10000, // 10 segundos atras
      ttl: 5000 // TTL de 5 segundos
    };
    
    localStorageMock.getItem.mockReturnValue(JSON.stringify(expiredCacheEntry));
    (httpClient.get as any).mockResolvedValueOnce(newData);

    render(
      <TestComponent 
        cacheKey="test-cache" 
        apiEndpoint="/api/test" 
      />
    );

    // Inicialmente mostra dados expirados
    expect(screen.getByTestId('cached-value')).toHaveTextContent(JSON.stringify(expiredData));
    expect(screen.getByTestId('is-expired')).toHaveTextContent('Expired');
    expect(screen.getByTestId('loading')).toHaveTextContent('Loading...');

    // Aguarda nova requisicao
    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('Not Loading');
    });

    // Verifica se dados foram atualizados
    expect(screen.getByTestId('cached-value')).toHaveTextContent(JSON.stringify(newData));
    expect(screen.getByTestId('api-data')).toHaveTextContent(JSON.stringify(newData));
    expect(httpClient.get).toHaveBeenCalledWith('/api/test');
  });

  it('deve permitir refresh manual dos dados', async () => {
    const cachedData = { id: 5, name: 'Cached Data' };
    const freshData = { id: 6, name: 'Fresh Data' };
    
    const cacheEntry = {
      value: cachedData,
      timestamp: Date.now(),
      ttl: 5000
    };
    
    localStorageMock.getItem.mockReturnValue(JSON.stringify(cacheEntry));
    (httpClient.get as any).mockResolvedValueOnce(freshData);

    render(
      <TestComponent 
        cacheKey="test-cache" 
        apiEndpoint="/api/test" 
      />
    );

    // Inicialmente usa cache
    expect(screen.getByTestId('cached-value')).toHaveTextContent(JSON.stringify(cachedData));
    expect(httpClient.get).not.toHaveBeenCalled();

    // Clica no botao de refresh
    const refreshBtn = screen.getByTestId('refresh-btn');
    act(() => {
      refreshBtn.click();
    });

    // Deve mostrar loading
    expect(screen.getByTestId('loading')).toHaveTextContent('Loading...');

    // Aguarda nova requisicao
    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('Not Loading');
    });

    // Verifica se dados foram atualizados
    expect(screen.getByTestId('cached-value')).toHaveTextContent(JSON.stringify(freshData));
    expect(httpClient.get).toHaveBeenCalledWith('/api/test');
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('test-cache');
  });

  it('deve limpar cache manualmente', async () => {
    const cachedData = { id: 7, name: 'Cached Data' };
    const cacheEntry = {
      value: cachedData,
      timestamp: Date.now(),
      ttl: 5000
    };
    
    localStorageMock.getItem.mockReturnValue(JSON.stringify(cacheEntry));

    render(
      <TestComponent 
        cacheKey="test-cache" 
        apiEndpoint="/api/test" 
        defaultValue="Default Value"
      />
    );

    // Inicialmente usa cache
    expect(screen.getByTestId('cached-value')).toHaveTextContent(JSON.stringify(cachedData));

    // Clica no botao de limpar cache
    const clearCacheBtn = screen.getByTestId('clear-cache-btn');
    act(() => {
      clearCacheBtn.click();
    });

    // Deve voltar ao valor padrao
    expect(screen.getByTestId('cached-value')).toHaveTextContent('"Default Value"');
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('test-cache');
  });

  it('deve lidar com erros da API mantendo cache', async () => {
    const cachedData = { id: 8, name: 'Cached Data' };
    const expiredCacheEntry = {
      value: cachedData,
      timestamp: Date.now() - 10000,
      ttl: 5000
    };
    
    localStorageMock.getItem.mockReturnValue(JSON.stringify(expiredCacheEntry));
    (httpClient.get as any).mockRejectedValueOnce(new Error('API Error'));

    render(
      <TestComponent 
        cacheKey="test-cache" 
        apiEndpoint="/api/test" 
      />
    );

    // Deve tentar recarregar devido ao cache expirado
    expect(screen.getByTestId('loading')).toHaveTextContent('Loading...');

    // Aguarda erro da API
    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('Not Loading');
    });

    // Deve manter dados do cache mesmo com erro
    expect(screen.getByTestId('cached-value')).toHaveTextContent(JSON.stringify(cachedData));
    expect(screen.getByTestId('error')).toHaveTextContent('API Error');
    expect(screen.getByTestId('is-expired')).toHaveTextContent('Expired');
  });

  it('deve funcionar com multiplas instancias usando chaves diferentes', async () => {
    const data1 = { id: 9, name: 'Data 1' };
    const data2 = { id: 10, name: 'Data 2' };
    
    (httpClient.get as any)
      .mockResolvedValueOnce(data1)
      .mockResolvedValueOnce(data2);

    const { container } = render(
      <div>
        <div data-testid="component-1">
          <TestComponent 
            cacheKey="cache-1" 
            apiEndpoint="/api/data1" 
          />
        </div>
        <div data-testid="component-2">
          <TestComponent 
            cacheKey="cache-2" 
            apiEndpoint="/api/data2" 
          />
        </div>
      </div>
    );

    // Aguarda ambas as requisicoes
    await waitFor(() => {
      const component1 = container.querySelector('[data-testid="component-1"]');
      const component2 = container.querySelector('[data-testid="component-2"]');
      
      expect(component1?.querySelector('[data-testid="loading"]'))
        .toHaveTextContent('Not Loading');
      expect(component2?.querySelector('[data-testid="loading"]'))
        .toHaveTextContent('Not Loading');
    });

    // Verifica se cada componente tem seus proprios dados
    const component1 = container.querySelector('[data-testid="component-1"]');
    const component2 = container.querySelector('[data-testid="component-2"]');
    
    expect(component1?.querySelector('[data-testid="cached-value"]'))
      .toHaveTextContent(JSON.stringify(data1));
    expect(component2?.querySelector('[data-testid="cached-value"]'))
      .toHaveTextContent(JSON.stringify(data2));

    // Verifica se foram feitas requisicoes separadas
    expect(httpClient.get).toHaveBeenCalledWith('/api/data1');
    expect(httpClient.get).toHaveBeenCalledWith('/api/data2');
    expect(httpClient.get).toHaveBeenCalledTimes(2);
  });

  it('deve sincronizar cache entre componentes com mesma chave', async () => {
    const sharedData = { id: 11, name: 'Shared Data' };
    const cacheEntry = {
      value: sharedData,
      timestamp: Date.now(),
      ttl: 5000
    };
    
    localStorageMock.getItem.mockReturnValue(JSON.stringify(cacheEntry));

    const { container } = render(
      <div>
        <div data-testid="component-a">
          <TestComponent 
            cacheKey="shared-cache" 
            apiEndpoint="/api/shared" 
          />
        </div>
        <div data-testid="component-b">
          <TestComponent 
            cacheKey="shared-cache" 
            apiEndpoint="/api/shared" 
          />
        </div>
      </div>
    );

    // Ambos componentes devem usar o mesmo cache
    const componentA = container.querySelector('[data-testid="component-a"]');
    const componentB = container.querySelector('[data-testid="component-b"]');
    
    expect(componentA?.querySelector('[data-testid="cached-value"]'))
      .toHaveTextContent(JSON.stringify(sharedData));
    expect(componentB?.querySelector('[data-testid="cached-value"]'))
      .toHaveTextContent(JSON.stringify(sharedData));

    // Nao deve fazer requisicoes desnecessarias
    expect(httpClient.get).not.toHaveBeenCalled();
  });

  it('deve respeitar TTL personalizado', async () => {
    const shortTtlData = { id: 12, name: 'Short TTL Data' };
    const newData = { id: 13, name: 'New Data' };
    
    const shortTtlEntry = {
      value: shortTtlData,
      timestamp: Date.now() - 1500, // 1.5 segundos atras
      ttl: 1000 // TTL de 1 segundo
    };
    
    localStorageMock.getItem.mockReturnValue(JSON.stringify(shortTtlEntry));
    (httpClient.get as any).mockResolvedValueOnce(newData);

    render(
      <TestComponent 
        cacheKey="short-ttl-cache" 
        apiEndpoint="/api/test" 
        ttl={1000}
      />
    );

    // Cache deve estar expirado devido ao TTL curto
    expect(screen.getByTestId('is-expired')).toHaveTextContent('Expired');
    expect(screen.getByTestId('loading')).toHaveTextContent('Loading...');

    // Aguarda nova requisicao
    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('Not Loading');
    });

    // Verifica se dados foram atualizados
    expect(screen.getByTestId('cached-value')).toHaveTextContent(JSON.stringify(newData));
    expect(httpClient.get).toHaveBeenCalledWith('/api/test');
  });

  it('deve funcionar com cache permanente (TTL = 0)', async () => {
    const permanentData = { id: 14, name: 'Permanent Data' };
    const permanentEntry = {
      value: permanentData,
      timestamp: Date.now() - 100000, // Muito tempo atras
      ttl: 0 // Cache permanente
    };
    
    localStorageMock.getItem.mockReturnValue(JSON.stringify(permanentEntry));

    render(
      <TestComponent 
        cacheKey="permanent-cache" 
        apiEndpoint="/api/test" 
        ttl={0}
      />
    );

    // Cache nunca deve expirar
    expect(screen.getByTestId('is-expired')).toHaveTextContent('Not Expired');
    expect(screen.getByTestId('cached-value')).toHaveTextContent(JSON.stringify(permanentData));
    expect(screen.getByTestId('loading')).toHaveTextContent('Not Loading');
    
    // Nao deve fazer requisicao
    expect(httpClient.get).not.toHaveBeenCalled();
  });
});