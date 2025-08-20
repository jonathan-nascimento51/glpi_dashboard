// Tipos específicos para testes

import type { MockTicket, MockUser, MockDashboardMetrics } from './mock';

// Tipos para API Client de teste
export interface TestApiClient {
  baseURL: string;
  token?: string | null;
  get(endpoint: string): Promise<any>;
  post(endpoint: string, data: any): Promise<any>;
  put(endpoint: string, data: any): Promise<any>;
  delete(endpoint: string): Promise<any>;
  request(endpoint: string, options?: any): Promise<any>;
  setToken(token: string): void;
}

// Tipos para componentes de teste
export interface TestComponentProps {
  [key: string]: any;
}

// Tipos para mocks de teste
export interface TestMocks {
  dashboardMetrics: MockDashboardMetrics;
  tickets: MockTicket[];
  users: MockUser[];
  performance: {
    avg_response_time: number;
    avg_resolution_time: number;
    tickets_created: number;
    tickets_resolved: number;
    sla_compliance: number;
    customer_satisfaction: number;
  };
}

// Tipos para handlers de teste
export interface TestHandler {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  path: string;
  response: any;
  status?: number;
  delay?: number;
}

// Tipos para configuração de teste
export interface TestConfig {
  baseURL: string;
  timeout: number;
  retries: number;
  mockData: TestMocks;
}

// Tipos para resultados de teste
export interface TestResult {
  success: boolean;
  data?: any;
  error?: string;
  duration: number;
}

// Tipos para métricas de teste
export interface TestMetrics {
  totalTests: number;
  passedTests: number;
  failedTests: number;
  skippedTests: number;
  duration: number;
  coverage: {
    lines: number;
    functions: number;
    branches: number;
    statements: number;
  };
}

// Tipos para snapshot de teste
export interface TestSnapshot {
  name: string;
  component: string;
  props: Record<string, any>;
  html: string;
  timestamp: string;
}

// Tipos para mock de funções
export interface MockFunction {
  (...args: any[]): any;
  mockReturnValue(value: any): MockFunction;
  mockResolvedValue(value: any): MockFunction;
  mockRejectedValue(error: any): MockFunction;
  mockImplementation(fn: (...args: any[]) => any): MockFunction;
  mockClear(): void;
  mockReset(): void;
  mockRestore(): void;
}

// Tipos para contexto de teste
export interface TestContext {
  apiClient: TestApiClient;
  mocks: TestMocks;
  config: TestConfig;
  utils: {
    waitFor: (
      callback: () => void | Promise<void>,
      options?: { timeout?: number }
    ) => Promise<void>;
    fireEvent: {
      click: (element: Element) => void;
      change: (element: Element, options: { target: { value: string } }) => void;
      submit: (element: Element) => void;
    };
    screen: {
      getByText: (text: string) => Element;
      getByRole: (role: string, options?: { name?: string }) => Element;
      getByTestId: (testId: string) => Element;
      queryByText: (text: string) => Element | null;
      queryByRole: (role: string, options?: { name?: string }) => Element | null;
      queryByTestId: (testId: string) => Element | null;
    };
  };
}

// Tipos para setup de teste
export interface TestSetup {
  beforeEach?: () => void | Promise<void>;
  afterEach?: () => void | Promise<void>;
  beforeAll?: () => void | Promise<void>;
  afterAll?: () => void | Promise<void>;
}

// Tipos para casos de teste
export interface TestCase {
  name: string;
  description?: string;
  setup?: TestSetup;
  test: (context: TestContext) => void | Promise<void>;
  expected: any;
  timeout?: number;
  skip?: boolean;
  only?: boolean;
}

// Tipos para suíte de testes
export interface TestSuite {
  name: string;
  description?: string;
  setup?: TestSetup;
  tests: TestCase[];
  config?: Partial<TestConfig>;
}

// Tipos para relatório de teste
export interface TestReport {
  suite: string;
  metrics: TestMetrics;
  results: TestResult[];
  errors: string[];
  warnings: string[];
  timestamp: string;
}

// Tipos para mock de dados
export interface MockDataGenerator {
  generateTicket(overrides?: Partial<MockTicket>): MockTicket;
  generateUser(overrides?: Partial<MockUser>): MockUser;
  generateMetrics(overrides?: Partial<MockDashboardMetrics>): MockDashboardMetrics;
  generateTickets(count: number): MockTicket[];
  generateUsers(count: number): MockUser[];
}

// Tipos para validação de teste
export interface TestValidator {
  validateResponse(response: any, schema: any): boolean;
  validateComponent(component: any, props: any): boolean;
  validateSnapshot(current: string, expected: string): boolean;
}

// Tipos para utilitários de teste
export interface TestUtils {
  mockApiClient: (config?: Partial<TestConfig>) => TestApiClient;
  createMockData: () => MockDataGenerator;
  createValidator: () => TestValidator;
  setupTestEnvironment: (config?: Partial<TestConfig>) => TestContext;
  cleanupTestEnvironment: () => void;
}

// Tipos para performance de teste
export interface TestPerformance {
  startTime: number;
  endTime: number;
  duration: number;
  memoryUsage: {
    heapUsed: number;
    heapTotal: number;
    external: number;
    rss: number;
  };
}

// Tipos para hook useCache
export interface CacheStats {
  metrics: {
    size: number;
    hitRate: number;
    missRate: number;
    totalRequests: number;
  };
  systemStatus: {
    size: number;
    hitRate: number;
    missRate: number;
    totalRequests: number;
  };
  technicianRanking: {
    size: number;
    hitRate: number;
    missRate: number;
    totalRequests: number;
  };
  newTickets: {
    size: number;
    hitRate: number;
    missRate: number;
    totalRequests: number;
  };
}

export interface CacheHookResult {
  stats: CacheStats;
  isLoading: boolean;
  updateStats: () => void;
  clearAll: () => Promise<void>;
  clearSpecificCache: (
    cacheType: 'metrics' | 'systemStatus' | 'technicianRanking' | 'newTickets'
  ) => void;
  refreshCache: (
    cacheType: 'metrics' | 'systemStatus' | 'technicianRanking' | 'newTickets'
  ) => Promise<void>;
  getCacheInfo: (cacheType: 'metrics' | 'systemStatus' | 'technicianRanking' | 'newTickets') => any;
}

export interface CacheData<T> {
  value: T;
  timestamp: number;
  ttl: number;
}

export interface CacheOptions {
  ttl?: number;
  key?: string;
  defaultValue?: any;
}

// Tipos para debugging de teste
export interface TestDebug {
  logs: string[];
  errors: Error[];
  warnings: string[];
  snapshots: TestSnapshot[];
  performance: TestPerformance;
}

// Tipos para configuração de mock
export interface MockConfig {
  enabled: boolean;
  baseURL: string;
  delay: number;
  errorRate: number;
  handlers: TestHandler[];
}

// Tipos para estado de teste
export interface TestState {
  isRunning: boolean;
  currentTest: string | null;
  results: TestResult[];
  errors: Error[];
  config: TestConfig;
  mocks: TestMocks;
}
