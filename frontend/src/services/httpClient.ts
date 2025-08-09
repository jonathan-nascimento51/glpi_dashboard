import axios, { AxiosInstance, AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios';

// Configuração da API usando variáveis de ambiente
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api',
  TIMEOUT: parseInt(import.meta.env.VITE_API_TIMEOUT || '30000'),
  RETRY_ATTEMPTS: parseInt(import.meta.env.VITE_API_RETRY_ATTEMPTS || '3'),
  RETRY_DELAY: parseInt(import.meta.env.VITE_API_RETRY_DELAY || '1000'),
};

// Interface para configuração de autenticação
export interface AuthConfig {
  apiToken?: string;
  appToken?: string;
  userToken?: string;
}

// Configuração de autenticação (pode ser definida via variáveis de ambiente)
export const authConfig: AuthConfig = {
  apiToken: import.meta.env.VITE_API_TOKEN,
  appToken: import.meta.env.VITE_APP_TOKEN,
  userToken: import.meta.env.VITE_USER_TOKEN,
};

// Função para atualizar tokens de autenticação
export const updateAuthTokens = (newAuthConfig: Partial<AuthConfig>) => {
  Object.assign(authConfig, newAuthConfig);
};

// Cliente HTTP centralizado
export const httpClient: AxiosInstance = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// Interceptador de requisição para autenticação e logging
httpClient.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    // Adicionar headers de autenticação se disponíveis
    if (authConfig.apiToken) {
      config.headers = {
        ...config.headers,
        'Authorization': `Bearer ${authConfig.apiToken}`
      };
    }
    
    if (authConfig.appToken) {
      config.headers = {
        ...config.headers,
        'App-Token': authConfig.appToken
      };
    }
    
    if (authConfig.userToken) {
      config.headers = {
        ...config.headers,
        'Session-Token': authConfig.userToken
      };
    }
    
    // Log da requisição
    const logLevel = import.meta.env.VITE_LOG_LEVEL || 'info';
    const showApiCalls = import.meta.env.VITE_SHOW_API_CALLS === 'true';
    
    if (showApiCalls || logLevel === 'debug') {
      console.log(`🚀 ${config.method?.toUpperCase()} ${config.url}`, {
        headers: config.headers,
        params: config.params,
        data: config.data
      });
    }
    
    return config;
  },
  (error: AxiosError) => {
    console.error('❌ Request error:', error);
    return Promise.reject(error);
  }
);

// Interceptador de resposta para tratamento de erros e logging
httpClient.interceptors.response.use(
  (response: AxiosResponse) => {
    const logLevel = import.meta.env.VITE_LOG_LEVEL || 'info';
    const showApiCalls = import.meta.env.VITE_SHOW_API_CALLS === 'true';
    
    if (showApiCalls || logLevel === 'debug') {
      console.log(`✅ ${response.config.method?.toUpperCase()} ${response.config.url} - ${response.status}`, {
        status: response.status,
        statusText: response.statusText,
        data: response.data
      });
    }
    
    return response;
  },
  async (error: AxiosError) => {
    const errorInfo = {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      statusText: error.response?.statusText,
      message: error.message,
      code: error.code,
      data: error.response?.data
    };
    
    // Tratamento específico por tipo de erro
    if (error.code === 'ECONNABORTED') {
      console.warn('⏱️ Request timeout:', errorInfo.url);
    } else if (error.response?.status === 401) {
      console.warn('🔐 Authentication error:', errorInfo.url);
      // Aqui poderia disparar um evento para renovar token ou redirecionar para login
      dispatchAuthError();
    } else if (error.response?.status === 403) {
      console.warn('🚫 Authorization error:', errorInfo.url);
    } else if (error.response?.status === 404) {
      console.warn('🔍 Endpoint not found:', errorInfo.url);
    } else if (error.response?.status === 429) {
      console.warn('🚦 Rate limit exceeded:', errorInfo.url);
    } else if (error.response?.status >= 500) {
      console.error('🚨 Server error:', errorInfo);
    } else if (error.response?.status >= 400) {
      console.warn('⚠️ Client error:', errorInfo);
    } else {
      console.error('🔌 Network/Connection error:', errorInfo);
    }
    
    // Implementar retry automático para erros temporários
    if (shouldRetry(error) && !error.config?.__retryCount) {
      return retryRequest(error);
    }
    
    return Promise.reject(error);
  }
);

// Função para determinar se deve tentar novamente
function shouldRetry(error: AxiosError): boolean {
  const retryableStatuses = [408, 429, 500, 502, 503, 504];
  const retryableCodes = ['ECONNABORTED', 'ENOTFOUND', 'ECONNRESET', 'ETIMEDOUT'];
  
  return (
    (error.response && retryableStatuses.includes(error.response.status)) ||
    (error.code && retryableCodes.includes(error.code))
  );
}

// Função para retry com backoff exponencial
async function retryRequest(error: AxiosError): Promise<AxiosResponse> {
  const config = error.config!;
  config.__retryCount = (config.__retryCount || 0) + 1;
  
  if (config.__retryCount > API_CONFIG.RETRY_ATTEMPTS) {
    return Promise.reject(error);
  }
  
  const delay = API_CONFIG.RETRY_DELAY * Math.pow(2, config.__retryCount - 1);
  
  console.log(`🔄 Retrying request (${config.__retryCount}/${API_CONFIG.RETRY_ATTEMPTS}) in ${delay}ms:`, config.url);
  
  await new Promise(resolve => setTimeout(resolve, delay));
  
  return httpClient.request(config);
}

// Função para disparar evento de erro de autenticação
function dispatchAuthError() {
  if (typeof window !== 'undefined') {
    window.dispatchEvent(new CustomEvent('auth-error', {
      detail: { message: 'Authentication failed' }
    }));
  }
}

// Estender a interface AxiosRequestConfig para incluir __retryCount
declare module 'axios' {
  interface AxiosRequestConfig {
    __retryCount?: number;
  }
}

// Funções utilitárias para requisições comuns
export const apiUtils = {
  // GET request
  get: <T = any>(url: string, config?: AxiosRequestConfig) => 
    httpClient.get<T>(url, config),
  
  // POST request
  post: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) => 
    httpClient.post<T>(url, data, config),
  
  // PUT request
  put: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) => 
    httpClient.put<T>(url, data, config),
  
  // DELETE request
  delete: <T = any>(url: string, config?: AxiosRequestConfig) => 
    httpClient.delete<T>(url, config),
  
  // PATCH request
  patch: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) => 
    httpClient.patch<T>(url, data, config),
  
  // HEAD request
  head: (url: string, config?: AxiosRequestConfig) => 
    httpClient.head(url, config),
};

export default httpClient;