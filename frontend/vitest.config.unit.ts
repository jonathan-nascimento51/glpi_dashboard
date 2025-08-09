import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    name: 'unit',
    environment: 'jsdom',
    setupFiles: ['./src/test-setup.ts'],
    include: [
      'src/**/*.unit.test.{ts,tsx}',
      'src/__tests__/unit/**/*.test.{ts,tsx}'
    ],
    exclude: [
      'node_modules/**',
      'dist/**',
      'coverage/**',
      'src/__tests__/integration/**'
    ],
    globals: true,
    css: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      reportsDirectory: './coverage/unit',
      include: [
        'src/**/*.{ts,tsx}'
      ],
      exclude: [
        'src/**/*.test.{ts,tsx}',
        'src/**/*.spec.{ts,tsx}',
        'src/test-setup.ts',
        'src/vite-env.d.ts',
        'src/**/*.d.ts',
        'src/__tests__/**'
      ],
      thresholds: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80
        },
        'src/hooks/**': {
          branches: 90,
          functions: 90,
          lines: 90,
          statements: 90
        },
        'src/services/**': {
          branches: 85,
          functions: 85,
          lines: 85,
          statements: 85
        },
        'src/utils/**': {
          branches: 85,
          functions: 85,
          lines: 85,
          statements: 85
        }
      }
    },
    testTimeout: 5000,
    hookTimeout: 5000,
    teardownTimeout: 2000,
    isolate: true,
    pool: 'threads',
    poolOptions: {
      threads: {
        singleThread: false,
        minThreads: 2,
        maxThreads: 6
      }
    },
    reporter: [
      'default',
      'json',
      'html'
    ],
    outputFile: {
      json: './test-results/unit-results.json',
      html: './test-results/unit-report.html'
    },
    watch: false,
    ui: false,
    open: false,
    logHeapUsage: true,
    sequence: {
      shuffle: true,
      concurrent: true
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@hooks': path.resolve(__dirname, './src/hooks'),
      '@services': path.resolve(__dirname, './src/services'),
      '@utils': path.resolve(__dirname, './src/utils'),
      '@types': path.resolve(__dirname, './src/types'),
      '@assets': path.resolve(__dirname, './src/assets')
    }
  },
  define: {
    'import.meta.env.VITE_API_BASE_URL': JSON.stringify('http://localhost:8000'),
    'import.meta.env.VITE_APP_NAME': JSON.stringify('GLPI Dashboard Test'),
    'import.meta.env.VITE_APP_VERSION': JSON.stringify('1.0.0-test')
  }
});