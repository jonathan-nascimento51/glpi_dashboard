import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { httpClient } from '../../../services/httpClient';

// Mock do fetch global
const mockFetch = vi.fn();
global.fetch = mockFetch;

// Mock do console para capturar logs
const consoleSpy = {
  error: vi.spyOn(console, 'error').mockImplementation(() => {}),
  warn: vi.spyOn(console, 'warn').mockImplementation(() => {}),
  log: vi.spyOn(console, 'log').mockImplementation(() => {}),
};

describe('httpClient Service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockFetch.mockClear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('GET requests', () => {
    it('deve fazer requisição GET com sucesso', async () => {
      const mockData = { id: 1, name: 'Test' };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockData),
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      const result = await httpClient.get('/api/test');

      expect(mockFetch).toHaveBeenCalledWith('/api/test', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
      });
      expect(result).toEqual(mockData);
    });

    it('deve adicionar parâmetros de query à URL', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve({}),
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      await httpClient.get('/api/test', {
        params: { page: 1, limit: 10, filter: 'active' },
      });

      expect(mockFetch).toHaveBeenCalledWith(
        '/api/test?page=1&limit=10&filter=active',
        expect.any(Object)
      );
    });

    it('deve lidar com parâmetros de query vazios', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve({}),
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      await httpClient.get('/api/test', {
        params: { empty: '', undefined: undefined, null: null },
      });

      expect(mockFetch).toHaveBeenCalledWith('/api/test', expect.any(Object));
    });

    it('deve adicionar headers customizados', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve({}),
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      await httpClient.get('/api/test', {
        headers: {
          Authorization: 'Bearer token123',
          'X-Custom-Header': 'custom-value',
        },
      });

      expect(mockFetch).toHaveBeenCalledWith('/api/test', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
          Authorization: 'Bearer token123',
          'X-Custom-Header': 'custom-value',
        },
      });
    });
  });

  describe('POST requests', () => {
    it('deve fazer requisição POST com dados JSON', async () => {
      const requestData = { name: 'Test', value: 123 };
      const responseData = { id: 1, ...requestData };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: () => Promise.resolve(responseData),
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      const result = await httpClient.post('/api/test', requestData);

      expect(mockFetch).toHaveBeenCalledWith('/api/test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify(requestData),
      });
      expect(result).toEqual(responseData);
    });

    it('deve fazer requisição POST com FormData', async () => {
      const formData = new FormData();
      formData.append('file', new Blob(['test'], { type: 'text/plain' }));
      formData.append('name', 'test-file');

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: () => Promise.resolve({ success: true }),
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      await httpClient.post('/api/upload', formData);

      expect(mockFetch).toHaveBeenCalledWith('/api/upload', {
        method: 'POST',
        headers: {
          Accept: 'application/json',
        },
        body: formData,
      });
    });
  });

  describe('PUT requests', () => {
    it('deve fazer requisição PUT com dados', async () => {
      const requestData = { id: 1, name: 'Updated Test' };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(requestData),
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      const result = await httpClient.put('/api/test/1', requestData);

      expect(mockFetch).toHaveBeenCalledWith('/api/test/1', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify(requestData),
      });
      expect(result).toEqual(requestData);
    });
  });

  describe('DELETE requests', () => {
    it('deve fazer requisição DELETE', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 204,
        json: () => Promise.resolve(null),
        headers: new Headers(),
      });

      await httpClient.delete('/api/test/1');

      expect(mockFetch).toHaveBeenCalledWith('/api/test/1', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
      });
    });
  });

  describe('Error handling', () => {
    it('deve lançar erro para status HTTP de erro', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        json: () => Promise.resolve({ error: 'Resource not found' }),
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      await expect(httpClient.get('/api/nonexistent')).rejects.toThrow('HTTP 404: Not Found');
    });

    it('deve lidar com erro de rede', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(httpClient.get('/api/test')).rejects.toThrow('Network error');
    });

    it('deve lidar com timeout', async () => {
      mockFetch.mockImplementationOnce(
        () =>
          new Promise((_, reject) => setTimeout(() => reject(new Error('Request timeout')), 100))
      );

      await expect(httpClient.get('/api/test', { timeout: 50 })).rejects.toThrow();
    });

    it('deve lidar com resposta JSON inválida', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.reject(new Error('Invalid JSON')),
        text: () => Promise.resolve('Invalid JSON response'),
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      await expect(httpClient.get('/api/test')).rejects.toThrow('Invalid JSON');
    });

    it('deve retornar texto para resposta não-JSON', async () => {
      const textResponse = 'Plain text response';
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.reject(new Error('Not JSON')),
        text: () => Promise.resolve(textResponse),
        headers: new Headers({ 'content-type': 'text/plain' }),
      });

      const result = await httpClient.get('/api/text');
      expect(result).toBe(textResponse);
    });
  });

  describe('Request interceptors', () => {
    it('deve aplicar interceptor de request', async () => {
      const interceptor = vi.fn(config => ({
        ...config,
        headers: {
          ...config.headers,
          'X-Intercepted': 'true',
        },
      }));

      httpClient.addRequestInterceptor(interceptor);

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve({}),
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      await httpClient.get('/api/test');

      expect(interceptor).toHaveBeenCalled();
      expect(mockFetch).toHaveBeenCalledWith(
        '/api/test',
        expect.objectContaining({
          headers: expect.objectContaining({
            'X-Intercepted': 'true',
          }),
        })
      );

      httpClient.removeRequestInterceptor(interceptor);
    });
  });

  describe('Response interceptors', () => {
    it('deve aplicar interceptor de response', async () => {
      const interceptor = vi.fn(response => ({
        ...response,
        intercepted: true,
      }));

      httpClient.addResponseInterceptor(interceptor);

      const mockData = { id: 1, name: 'Test' };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockData),
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      const result = await httpClient.get('/api/test');

      expect(interceptor).toHaveBeenCalledWith(mockData);
      expect(result).toEqual({ ...mockData, intercepted: true });

      httpClient.removeResponseInterceptor(interceptor);
    });
  });

  describe('Retry mechanism', () => {
    it('deve tentar novamente em caso de falha', async () => {
      mockFetch
        .mockRejectedValueOnce(new Error('Network error'))
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: () => Promise.resolve({ success: true }),
          headers: new Headers({ 'content-type': 'application/json' }),
        });

      const result = await httpClient.get('/api/test', { retry: 3 });

      expect(mockFetch).toHaveBeenCalledTimes(3);
      expect(result).toEqual({ success: true });
    });

    it('deve falhar após esgotar tentativas', async () => {
      mockFetch.mockRejectedValue(new Error('Persistent error'));

      await expect(httpClient.get('/api/test', { retry: 2 })).rejects.toThrow('Persistent error');

      expect(mockFetch).toHaveBeenCalledTimes(3); // 1 inicial + 2 retries
    });
  });

  describe('Cache mechanism', () => {
    it('deve usar cache para requisições GET idênticas', async () => {
      const mockData = { id: 1, cached: true };
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockData),
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      // Primeira requisição
      const result1 = await httpClient.get('/api/test', { cache: true });

      // Segunda requisição (deve usar cache)
      const result2 = await httpClient.get('/api/test', { cache: true });

      expect(mockFetch).toHaveBeenCalledTimes(1);
      expect(result1).toEqual(mockData);
      expect(result2).toEqual(mockData);
    });

    it('deve ignorar cache para métodos diferentes de GET', async () => {
      const mockData = { id: 1 };
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockData),
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      await httpClient.post('/api/test', {}, { cache: true });
      await httpClient.post('/api/test', {}, { cache: true });

      expect(mockFetch).toHaveBeenCalledTimes(2);
    });
  });

  describe('AbortController', () => {
    it('deve cancelar requisição quando abortada', async () => {
      const controller = new AbortController();

      mockFetch.mockImplementationOnce(
        () =>
          new Promise((_, reject) => {
            controller.signal.addEventListener('abort', () => {
              reject(new Error('Request aborted'));
            });
          })
      );

      const requestPromise = httpClient.get('/api/test', {
        signal: controller.signal,
      });

      controller.abort();

      await expect(requestPromise).rejects.toThrow('Request aborted');
    });
  });

  describe('Base URL configuration', () => {
    it('deve usar base URL configurada', async () => {
      httpClient.setBaseURL('https://api.example.com');

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve({}),
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      await httpClient.get('/test');

      expect(mockFetch).toHaveBeenCalledWith('https://api.example.com/test', expect.any(Object));

      httpClient.setBaseURL(''); // Reset
    });

    it('deve lidar com URLs absolutas ignorando base URL', async () => {
      httpClient.setBaseURL('https://api.example.com');

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve({}),
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      await httpClient.get('https://other-api.com/test');

      expect(mockFetch).toHaveBeenCalledWith('https://other-api.com/test', expect.any(Object));

      httpClient.setBaseURL(''); // Reset
    });
  });

  describe('Content-Type handling', () => {
    it('deve detectar e preservar Content-Type para FormData', async () => {
      const formData = new FormData();
      formData.append('test', 'value');

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve({}),
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      await httpClient.post('/api/upload', formData);

      const callArgs = mockFetch.mock.calls[0][1];
      expect(callArgs.headers).not.toHaveProperty('Content-Type');
      expect(callArgs.body).toBe(formData);
    });

    it('deve definir Content-Type para dados JSON', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve({}),
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      await httpClient.post('/api/test', { data: 'test' });

      const callArgs = mockFetch.mock.calls[0][1];
      expect(callArgs.headers['Content-Type']).toBe('application/json');
    });
  });
});
