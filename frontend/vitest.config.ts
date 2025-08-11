import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      reportsDirectory: './coverage',
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.d.ts',
        '**/*.config.{js,ts}',
        '**/coverage/**',
        '**/dist/**',
        '**/.{eslint,prettier}rc.{js,cjs,yml}',
        '**/vite.config.ts',
        '**/playwright.config.ts',
        '**/*.stories.{js,ts,jsx,tsx}',
        '**/storybook-static/**',
        '**/.storybook/**'
      ],
      // Configuração de cobertura mÃ­nima
      thresholds: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80
        },
        // Cobertura mínima por arquivo
        perFile: {
          branches: 70,
          functions: 70,
          lines: 70,
          statements: 70
        },
        // Cobertura específica para arquivos core
        "./src/components/": {
          branches: 85,
          functions: 85,
          lines: 85,
          statements: 85
        },
        "./src/hooks/": {
          branches: 90,
          functions: 90,
          lines: 90,
          statements: 90
        },
        "./src/services/": {
          branches: 85,
          functions: 85,
          lines: 85,
          statements: 85
        }
      }
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  }
})

