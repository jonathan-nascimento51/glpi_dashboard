// Tipos para contratos de API e validação

// Interface para contratos da API
export interface ApiContract {
  endpoint: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  requestSchema?: SchemaDefinition;
  responseSchema: SchemaDefinition;
  statusCode: number;
  headers?: Record<string, string>;
}

// Definição de schema para validação
export interface SchemaDefinition {
  type: 'object' | 'array' | 'string' | 'number' | 'boolean' | 'integer';
  properties?: Record<string, SchemaDefinition>;
  items?: SchemaDefinition;
  required?: string[];
  enum?: string[];
  format?: string;
  minimum?: number;
  maximum?: number;
  minLength?: number;
  maxLength?: number;
  pattern?: string;
}

// Resultado de validação
export interface ValidationResult {
  success: boolean;
  data?: any;
  error?: string;
}

// Schema validator
export interface SchemaValidator {
  validate: (data: any) => ValidationResult;
}

// Tipos para testes de contrato
export interface ContractTestCase {
  name: string;
  contract: ApiContract;
  testData?: any;
  expectedResponse?: any;
  shouldFail?: boolean;
}

// Configuração de teste de contrato
export interface ContractTestConfig {
  baseUrl: string;
  timeout: number;
  retries: number;
  validateResponse: boolean;
  validateRequest: boolean;
}

// Resultado de teste de contrato
export interface ContractTestResult {
  contract: ApiContract;
  success: boolean;
  response?: any;
  error?: string;
  validationErrors?: string[];
  duration: number;
}

// Suite de testes de contrato
export interface ContractTestSuite {
  name: string;
  description?: string;
  contracts: ApiContract[];
  config?: Partial<ContractTestConfig>;
  setup?: () => void | Promise<void>;
  teardown?: () => void | Promise<void>;
}

// Relatório de testes de contrato
export interface ContractTestReport {
  suite: string;
  totalContracts: number;
  passedContracts: number;
  failedContracts: number;
  results: ContractTestResult[];
  duration: number;
  timestamp: string;
}

// Tipos para mock de servidor
export interface MockServerConfig {
  baseUrl: string;
  handlers: MockHandler[];
  fallbackHandler?: MockHandler;
}

export interface MockHandler {
  method: string;
  path: string;
  response: any;
  status?: number;
  delay?: number;
  headers?: Record<string, string>;
}

// Tipos para validação de dados
export interface DataValidator {
  validateSchema: (data: any, schema: SchemaDefinition) => ValidationResult;
  validateContract: (response: any, contract: ApiContract) => ValidationResult;
  validateRequest: (request: any, contract: ApiContract) => ValidationResult;
}

// Tipos para geração de dados de teste
export interface TestDataGenerator {
  generateFromSchema: (schema: SchemaDefinition) => any;
  generateValidData: (contract: ApiContract) => any;
  generateInvalidData: (contract: ApiContract) => any;
}

// Tipos para utilitários de teste
export interface ContractTestUtils {
  createValidator: () => DataValidator;
  createGenerator: () => TestDataGenerator;
  setupMockServer: (config: MockServerConfig) => any;
  runContractTests: (suite: ContractTestSuite) => Promise<ContractTestReport>;
}

// Tipos para configuração de ambiente
export interface TestEnvironment {
  baseUrl: string;
  apiKey?: string;
  timeout: number;
  retries: number;
  mockServer?: MockServerConfig;
  contracts: ApiContract[];
}

// Tipos para métricas de teste
export interface ContractTestMetrics {
  totalRequests: number;
  successfulRequests: number;
  failedRequests: number;
  averageResponseTime: number;
  minResponseTime: number;
  maxResponseTime: number;
  errorRate: number;
}

// Tipos para análise de cobertura
export interface ContractCoverage {
  totalEndpoints: number;
  testedEndpoints: number;
  coveragePercentage: number;
  untestedEndpoints: string[];
  methodCoverage: Record<string, number>;
}

// Tipos para relatório detalhado
export interface DetailedContractReport extends ContractTestReport {
  metrics: ContractTestMetrics;
  coverage: ContractCoverage;
  errors: {
    validationErrors: string[];
    networkErrors: string[];
    timeoutErrors: string[];
  };
  warnings: string[];
}

// Tipos para configuração avançada
export interface AdvancedContractConfig extends ContractTestConfig {
  parallelExecution: boolean;
  maxConcurrency: number;
  failFast: boolean;
  generateReport: boolean;
  reportFormat: 'json' | 'html' | 'xml';
  outputPath: string;
}

// Tipos para hooks de teste
export interface ContractTestHooks {
  beforeAll?: () => void | Promise<void>;
  afterAll?: () => void | Promise<void>;
  beforeEach?: (contract: ApiContract) => void | Promise<void>;
  afterEach?: (result: ContractTestResult) => void | Promise<void>;
  onError?: (error: Error, contract: ApiContract) => void;
  onSuccess?: (result: ContractTestResult) => void;
}

// Tipos para filtros de teste
export interface ContractTestFilters {
  methods?: string[];
  endpoints?: string[];
  tags?: string[];
  status?: number[];
  exclude?: {
    methods?: string[];
    endpoints?: string[];
    tags?: string[];
  };
}

// Tipos para execução de teste
export interface ContractTestExecution {
  suite: ContractTestSuite;
  config: AdvancedContractConfig;
  filters?: ContractTestFilters;
  hooks?: ContractTestHooks;
  environment: TestEnvironment;
}
