import '@testing-library/jest-dom';
import { vi, beforeAll, afterEach, afterAll } from 'vitest';
import { cleanup } from '@testing-library/react';
import { server } from './mocks/server';
import React from 'react';

// Configuração global para testes
beforeAll(() => {
  // Inicia o servidor de mocks MSW
  server.listen({ onUnhandledRequest: 'error' });

  // Mock do console para evitar logs desnecessários durante os testes
  vi.spyOn(console, 'log').mockImplementation(() => {});
  vi.spyOn(console, 'warn').mockImplementation(() => {});
  vi.spyOn(console, 'error').mockImplementation(() => {});

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
    writable: true,
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
    writable: true,
  });

  // Mock do matchMedia
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation(query => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(), // deprecated
      removeListener: vi.fn(), // deprecated
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  });

  // Mock do ResizeObserver
  global.ResizeObserver = vi.fn().mockImplementation(() => ({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn(),
  }));

  // Mock do IntersectionObserver
  global.IntersectionObserver = vi.fn().mockImplementation(() => ({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn(),
  }));

  // Mock do requestAnimationFrame
  global.requestAnimationFrame = vi.fn().mockImplementation(cb => {
    setTimeout(cb, 0);
    return 1;
  });

  global.cancelAnimationFrame = vi.fn();

  // Mock do URL.createObjectURL
  global.URL.createObjectURL = vi.fn().mockReturnValue('mocked-url');
  global.URL.revokeObjectURL = vi.fn();

  // Mock do fetch se não estiver sendo mockado pelo MSW
  if (!global.fetch) {
    global.fetch = vi.fn();
  }

  // Mock das variáveis de ambiente
  vi.stubEnv('VITE_API_BASE_URL', 'http://localhost:8000');
  vi.stubEnv('VITE_APP_NAME', 'GLPI Dashboard Test');
  vi.stubEnv('VITE_APP_VERSION', '1.0.0-test');
});

// Limpeza após cada teste
afterEach(() => {
  // Limpa todos os mocks
  vi.clearAllMocks();

  // Limpa o DOM
  cleanup();

  // Reseta handlers do MSW
  server.resetHandlers();

  // Limpa localStorage e sessionStorage mocks
  if (window.localStorage.clear) {
    (window.localStorage.clear as any).mockClear();
  }
  if (window.sessionStorage.clear) {
    (window.sessionStorage.clear as any).mockClear();
  }
});

// Limpeza final
afterAll(() => {
  // Para o servidor de mocks
  server.close();

  // Restaura todos os mocks
  vi.restoreAllMocks();

  // Limpa variáveis de ambiente
  vi.unstubAllEnvs();
});

// Configurações globais para testes

// Aumenta o timeout padrão para testes assíncronos
vi.setConfig({
  testTimeout: 10000,
  hookTimeout: 10000,
});

// Configuração para suprimir warnings específicos durante os testes
const originalError = console.error;
beforeAll(() => {
  console.error = (...args: any[]) => {
    if (
      typeof args[0] === 'string' &&
      (args[0].includes('Warning: ReactDOM.render is deprecated') ||
        args[0].includes('Warning: componentWillReceiveProps') ||
        args[0].includes('Warning: componentWillMount') ||
        args[0].includes('act(...) is not supported'))
    ) {
      return;
    }
    originalError.call(console, ...args);
  };
});

afterAll(() => {
  console.error = originalError;
});

// Helpers globais para testes
declare global {
  var testUtils: {
    waitForNextTick: () => Promise<void>;
    mockLocalStorage: (data?: Record<string, string>) => void;
    mockSessionStorage: (data?: Record<string, string>) => void;
    createMockFile: (name: string, content: string, type?: string) => File;
    createMockEvent: (type: string, data?: any) => Event;
  };
}

// Utilitários globais para testes
global.testUtils = {
  // Aguarda o próximo tick do event loop
  waitForNextTick: () => new Promise(resolve => setTimeout(resolve, 0)),

  // Mock do localStorage com dados específicos
  mockLocalStorage: (data = {}) => {
    const mockStorage = {
      ...window.localStorage,
      getItem: vi.fn((key: string) => data[key] || null),
      setItem: vi.fn(),
      removeItem: vi.fn(),
      clear: vi.fn(),
    };
    Object.defineProperty(window, 'localStorage', { value: mockStorage });
  },

  // Mock do sessionStorage com dados específicos
  mockSessionStorage: (data = {}) => {
    const mockStorage = {
      ...window.sessionStorage,
      getItem: vi.fn((key: string) => data[key] || null),
      setItem: vi.fn(),
      removeItem: vi.fn(),
      clear: vi.fn(),
    };
    Object.defineProperty(window, 'sessionStorage', { value: mockStorage });
  },

  // Cria um arquivo mock para testes de upload
  createMockFile: (name: string, content: string, type = 'text/plain') => {
    const blob = new Blob([content], { type });
    return new File([blob], name, { type });
  },

  // Cria um evento mock
  createMockEvent: (type: string, data = {}) => {
    const event = new Event(type, { bubbles: true, cancelable: true });
    Object.assign(event, data);
    return event;
  },
};

// Configuração para Chart.js (se usado)
vi.mock('chart.js', () => ({
  Chart: vi.fn(),
  registerables: [],
}));

// Mock para react-chartjs-2
vi.mock('react-chartjs-2', () => ({
  Line: vi.fn(({ data, options }) => {
    return React.createElement('div', {
      'data-testid': 'line-chart',
      'data-chart-data': JSON.stringify(data),
      'data-chart-options': JSON.stringify(options),
    });
  }),
  Bar: vi.fn(({ data, options }) => {
    return React.createElement('div', {
      'data-testid': 'bar-chart',
      'data-chart-data': JSON.stringify(data),
      'data-chart-options': JSON.stringify(options),
    });
  }),
  Pie: vi.fn(({ data, options }) => {
    return React.createElement('div', {
      'data-testid': 'pie-chart',
      'data-chart-data': JSON.stringify(data),
      'data-chart-options': JSON.stringify(options),
    });
  }),
  Doughnut: vi.fn(({ data, options }) => {
    return React.createElement('div', {
      'data-testid': 'doughnut-chart',
      'data-chart-data': JSON.stringify(data),
      'data-chart-options': JSON.stringify(options),
    });
  }),
}));

// Mock para framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    div: vi.fn(({ children, ...props }) => React.createElement('div', props, children)),
    span: vi.fn(({ children, ...props }) => React.createElement('span', props, children)),
    button: vi.fn(({ children, ...props }) => React.createElement('button', props, children)),
    section: vi.fn(({ children, ...props }) => React.createElement('section', props, children)),
    article: vi.fn(({ children, ...props }) => React.createElement('article', props, children)),
  },
  AnimatePresence: vi.fn(({ children }) => children),
  useAnimation: vi.fn(() => ({
    start: vi.fn(),
    stop: vi.fn(),
    set: vi.fn(),
  })),
  useInView: vi.fn(() => true),
}));

// Mock para lucide-react icons
vi.mock('lucide-react', () => {
  const createMockIcon = (name: string) =>
    vi.fn((props: any) =>
      React.createElement('div', { 'data-testid': `${name.toLowerCase()}-icon`, ...props })
    );

  return {
    Search: createMockIcon('Search'),
    Filter: createMockIcon('Filter'),
    Download: createMockIcon('Download'),
    Upload: createMockIcon('Upload'),
    Edit: createMockIcon('Edit'),
    Delete: createMockIcon('Delete'),
    Plus: createMockIcon('Plus'),
    Minus: createMockIcon('Minus'),
    Check: createMockIcon('Check'),
    X: createMockIcon('X'),
    ChevronDown: createMockIcon('ChevronDown'),
    ChevronUp: createMockIcon('ChevronUp'),
    ChevronLeft: createMockIcon('ChevronLeft'),
    ChevronRight: createMockIcon('ChevronRight'),
    Calendar: createMockIcon('Calendar'),
    Clock: createMockIcon('Clock'),
    User: createMockIcon('User'),
    Users: createMockIcon('Users'),
    Settings: createMockIcon('Settings'),
    Home: createMockIcon('Home'),
    Dashboard: createMockIcon('Dashboard'),
    BarChart: createMockIcon('BarChart'),
    LineChart: createMockIcon('LineChart'),
    PieChart: createMockIcon('PieChart'),
    TrendingUp: createMockIcon('TrendingUp'),
    TrendingDown: createMockIcon('TrendingDown'),
    AlertCircle: createMockIcon('AlertCircle'),
    CheckCircle: createMockIcon('CheckCircle'),
    XCircle: createMockIcon('XCircle'),
    Info: createMockIcon('Info'),
    Warning: createMockIcon('Warning'),
    Error: createMockIcon('Error'),
    Success: createMockIcon('Success'),
    Loading: createMockIcon('Loading'),
    Refresh: createMockIcon('Refresh'),
    Save: createMockIcon('Save'),
    Cancel: createMockIcon('Cancel'),
    Menu: createMockIcon('Menu'),
    MoreVertical: createMockIcon('MoreVertical'),
    MoreHorizontal: createMockIcon('MoreHorizontal'),
    Eye: createMockIcon('Eye'),
    EyeOff: createMockIcon('EyeOff'),
    Lock: createMockIcon('Lock'),
    Unlock: createMockIcon('Unlock'),
    Mail: createMockIcon('Mail'),
    Phone: createMockIcon('Phone'),
    MapPin: createMockIcon('MapPin'),
    Tag: createMockIcon('Tag'),
    Tags: createMockIcon('Tags'),
    File: createMockIcon('File'),
    FileText: createMockIcon('FileText'),
    Image: createMockIcon('Image'),
    Video: createMockIcon('Video'),
    Music: createMockIcon('Music'),
    Archive: createMockIcon('Archive'),
    Copy: createMockIcon('Copy'),
    Share: createMockIcon('Share'),
    Link: createMockIcon('Link'),
    ExternalLink: createMockIcon('ExternalLink'),
  };
});
