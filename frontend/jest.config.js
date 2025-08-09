/** @type {import('jest').Config} */
module.exports = {
  // Ambiente de teste
  testEnvironment: 'jsdom',
  
  // Configuração de setup
  setupFilesAfterEnv: ['<rootDir>/src/test-setup.tsx'],
  
  // Padrões de arquivos de teste
  testMatch: [
    '<rootDir>/src/**/__tests__/**/*.{js,jsx,ts,tsx}',
    '<rootDir>/src/**/*.{test,spec}.{js,jsx,ts,tsx}'
  ],
  
  // Extensões de arquivo
  moduleFileExtensions: ['js', 'jsx', 'ts', 'tsx', 'json'],
  
  // Transformações
  transform: {
    '^.+\\.(ts|tsx)$': 'ts-jest',
    '^.+\\.(js|jsx)$': 'babel-jest',
    '^.+\\.css$': 'jest-transform-css',
    '^.+\\.(png|jpg|jpeg|gif|webp|avif|ico|bmp|svg)$': 'jest-transform-file'
  },
  
  // Mapeamento de módulos
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '^@components/(.*)$': '<rootDir>/src/components/$1',
    '^@hooks/(.*)$': '<rootDir>/src/hooks/$1',
    '^@services/(.*)$': '<rootDir>/src/services/$1',
    '^@utils/(.*)$': '<rootDir>/src/utils/$1',
    '^@types/(.*)$': '<rootDir>/src/types/$1',
    '^@config/(.*)$': '<rootDir>/src/config/$1',
    '^@lib/(.*)$': '<rootDir>/src/lib/$1',
    '^@mocks/(.*)$': '<rootDir>/src/mocks/$1',
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy'
  },
  
  // Arquivos a serem ignorados
  testPathIgnorePatterns: [
    '<rootDir>/node_modules/',
    '<rootDir>/dist/',
    '<rootDir>/build/',
    '<rootDir>/coverage/'
  ],
  
  // Módulos a serem ignorados na transformação
  transformIgnorePatterns: [
    'node_modules/(?!(.*\\.mjs$|@testing-library|@babel|babel-runtime|react-chartjs-2|chart.js))'
  ],
  
  // Configuração de cobertura
  collectCoverage: true,
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/main.tsx',
    '!src/vite-env.d.ts',
    '!src/**/__tests__/**',
    '!src/**/*.test.{js,jsx,ts,tsx}',
    '!src/**/*.spec.{js,jsx,ts,tsx}',
    '!src/mocks/**',
    '!src/test/**',
    '!src/**/*.stories.{js,jsx,ts,tsx}'
  ],
  
  // Diretório de relatórios de cobertura
  coverageDirectory: 'coverage',
  
  // Formatos de relatório de cobertura
  coverageReporters: [
    'text',
    'text-summary',
    'html',
    'lcov',
    'json',
    'json-summary',
    'clover'
  ],
  
  // Limites de cobertura
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    },
    './src/components/': {
      branches: 85,
      functions: 85,
      lines: 85,
      statements: 85
    },
    './src/hooks/': {
      branches: 90,
      functions: 90,
      lines: 90,
      statements: 90
    },
    './src/utils/': {
      branches: 95,
      functions: 95,
      lines: 95,
      statements: 95
    }
  },
  
  // Configurações globais
  globals: {
    'ts-jest': {
      tsconfig: 'tsconfig.json',
      isolatedModules: true
    }
  },
  
  // Configuração de timeout
  testTimeout: 10000,
  
  // Configuração de cache
  cache: true,
  cacheDirectory: '<rootDir>/node_modules/.cache/jest',
  
  // Configuração de workers
  maxWorkers: '50%',
  
  // Configuração de verbose
  verbose: true,
  
  // Configuração de notificações
  notify: false,
  
  // Configuração de watch
  watchman: true,
  
  // Configuração de módulos mock
  moduleDirectories: ['node_modules', '<rootDir>/src'],
  
  // Configuração de resolução de módulos
  resolver: undefined,
  
  // Configuração de snapshot
  snapshotSerializers: [
    'jest-serializer-html'
  ],
  
  // Configuração de clear mocks
  clearMocks: true,
  restoreMocks: true,
  resetMocks: false,
  
  // Configuração de error on deprecated
  errorOnDeprecated: true,
  
  // Configuração de force exit
  forceExit: false,
  
  // Configuração de detect open handles
  detectOpenHandles: true,
  
  // Configuração de detect leaked timers
  detectLeakedTimers: true,
  
  // Configuração de projects para diferentes tipos de teste
  projects: [
    {
      displayName: 'unit',
      testMatch: ['<rootDir>/src/**/__tests__/unit/**/*.{js,jsx,ts,tsx}'],
      setupFilesAfterEnv: ['<rootDir>/src/test-setup.tsx']
    },
    {
      displayName: 'integration',
      testMatch: ['<rootDir>/src/**/__tests__/integration/**/*.{js,jsx,ts,tsx}'],
      setupFilesAfterEnv: ['<rootDir>/src/test-setup.tsx']
    },
    {
      displayName: 'accessibility',
      testMatch: ['<rootDir>/src/**/__tests__/accessibility/**/*.{js,jsx,ts,tsx}'],
      setupFilesAfterEnv: ['<rootDir>/src/test-setup.tsx']
    },
    {
      displayName: 'visual',
      testMatch: ['<rootDir>/src/**/__tests__/visual/**/*.{js,jsx,ts,tsx}'],
      setupFilesAfterEnv: ['<rootDir>/src/test-setup.tsx']
    },
    {
      displayName: 'mutation',
      testMatch: ['<rootDir>/src/**/__tests__/mutation/**/*.{js,jsx,ts,tsx}'],
      setupFilesAfterEnv: ['<rootDir>/src/test-setup.tsx']
    },
    {
      displayName: 'contract',
      testMatch: ['<rootDir>/src/**/__tests__/contract/**/*.{js,jsx,ts,tsx}'],
      setupFilesAfterEnv: ['<rootDir>/src/test-setup.tsx']
    },
    {
      displayName: 'snapshot',
      testMatch: ['<rootDir>/src/**/__tests__/snapshot/**/*.{js,jsx,ts,tsx}'],
      setupFilesAfterEnv: ['<rootDir>/src/test-setup.tsx']
    }
  ],
  
  // Configuração de reporters
  reporters: [
    'default',
    [
      'jest-html-reporters',
      {
        publicPath: './coverage/html-report',
        filename: 'report.html',
        expand: true,
        hideIcon: false,
        pageTitle: 'GLPI Dashboard - Test Report',
        logoImgPath: undefined,
        inlineSource: false
      }
    ],
    [
      'jest-junit',
      {
        outputDirectory: './coverage',
        outputName: 'junit.xml',
        ancestorSeparator: ' › ',
        uniqueOutputName: 'false',
        suiteNameTemplate: '{filepath}',
        classNameTemplate: '{classname}',
        titleTemplate: '{title}'
      }
    ]
  ]
};
