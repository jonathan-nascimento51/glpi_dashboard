/**
 * Configuração global para testes do frontend
 */

import '@testing-library/jest-dom';
import { configure } from '@testing-library/react';
import { vi } from 'vitest';

// Configurar testing library
configure({ testIdAttribute: 'data-testid' });

// Mock do IntersectionObserver
Object.defineProperty(window, 'IntersectionObserver', {
  writable: true,
  value: vi.fn().mockImplementation((callback) => ({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn(),
    root: null,
    rootMargin: '',
    thresholds: [],
  })),
});

// Mock do ResizeObserver
Object.defineProperty(window, 'ResizeObserver', {
  writable: true,
  value: vi.fn().mockImplementation(() => ({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn(),
  })),
});

// Mock do matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock do localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
  length: 0,
  key: vi.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Mock do sessionStorage
const sessionStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
  length: 0,
  key: vi.fn(),
};
Object.defineProperty(window, 'sessionStorage', {
  value: sessionStorageMock,
});

// Mock do fetch
global.fetch = vi.fn();

// Mock do console para testes
const originalConsoleError = console.error;
beforeAll(() => {
  console.error = vi.fn();
});

afterAll(() => {
  console.error = originalConsoleError;
});

// Limpar mocks após cada teste
afterEach(() => {
  vi.clearAllMocks();
  localStorageMock.clear();
  sessionStorageMock.clear();
});

// Configurações globais para testes
export const testConfig = {
  apiBaseUrl: 'http://localhost:5000/api',
  timeout: 5000,
};

// Utilitários para testes
export const createMockResponse = (data: any, status = 200) => {
  return Promise.resolve({
    ok: status >= 200 && status < 300,
    status,
    json: () => Promise.resolve(data),
    text: () => Promise.resolve(JSON.stringify(data)),
  } as Response);
};

export const createMockError = (message: string, status = 500) => {
  const error = new Error(message) as any;
  error.status = status;
  return Promise.reject(error);
};

// Mock data para testes
export const mockMetricsData = {
  novos: 15,
  pendentes: 8,
  progresso: 12,
  resolvidos: 45,
  niveis: {
    n1: { novos: 5, pendentes: 2, progresso: 3, resolvidos: 15 },
    n2: { novos: 4, pendentes: 3, progresso: 4, resolvidos: 12 },
    n3: { novos: 3, pendentes: 2, progresso: 3, resolvidos: 10 },
    n4: { novos: 3, pendentes: 1, progresso: 2, resolvidos: 8 },
  },
  tendencias: {
    novos: '+12%',
    pendentes: '-5%',
    progresso: '+8%',
    resolvidos: '+15%',
  },
};

export const mockTechniciansData = [
  {
    id: 1,
    name: 'João Silva',
    score: 95.5,
    rank: 1,
    tickets_resolved: 25,
    avg_resolution_time: '2.5h',
    satisfaction_rate: 98,
  },
  {
    id: 2,
    name: 'Maria Santos',
    score: 92.3,
    rank: 2,
    tickets_resolved: 22,
    avg_resolution_time: '3.1h',
    satisfaction_rate: 95,
  },
  {
    id: 3,
    name: 'Pedro Costa',
    score: 89.7,
    rank: 3,
    tickets_resolved: 20,
    avg_resolution_time: '3.8h',
    satisfaction_rate: 92,
  },
];

export const mockSystemStatus = {
  status: 'online',
  api: 'online',
  glpi: 'online',
  last_update: '2024-01-15T10:30:00Z',
  response_time: 150,
  uptime: '99.9%',
};

// Helper para criar wrapper de testes com providers
import { ReactNode } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';

export const createTestQueryClient = () => {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  });
};

export const TestWrapper = ({ children }: { children: ReactNode }) => {
  const queryClient = createTestQueryClient();
  
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {children}
      </BrowserRouter>
    </QueryClientProvider>
  );
};

// Custom render function
import { render, RenderOptions } from '@testing-library/react';

interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  wrapper?: React.ComponentType<any>;
}

export const customRender = (
  ui: React.ReactElement,
  options: CustomRenderOptions = {}
) => {
  const { wrapper = TestWrapper, ...renderOptions } = options;
  return render(ui, { wrapper, ...renderOptions });
};

// Re-export everything from testing library
export * from '@testing-library/react';
export { customRender as render };