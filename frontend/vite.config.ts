import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  // PWA Configuration
  publicDir: "public",
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    // Code splitting otimizado
    rollupOptions: {
      output: {
        manualChunks: {
          // Vendor chunks separados
          'react-vendor': ['react', 'react-dom'],
          'ui-vendor': ['lucide-react', '@radix-ui/react-dialog', '@radix-ui/react-select'],
          'chart-vendor': ['recharts'],
          // Dashboard chunks por domínio
          'dashboard-core': [
            './src/domains/dashboard/components/DashboardCard',
            './src/domains/dashboard/components/MetricsGrid'
          ],
          'dashboard-advanced': [
            './src/components/dashboard/TicketChart',
            './src/components/dashboard/RankingTable'
          ]
        },
        // Nomes de chunk consistentes para cache
        chunkFileNames: 'assets/[name]-[hash].js',
        entryFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]'
      }
    },
    // Otimizações de minificação
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true
      }
    },
    // Target moderno para bundle menor
    target: 'es2020',
    // Source maps apenas em dev
    sourcemap: false
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
      }
    }
  },
  // Otimizações de dev
  optimizeDeps: {
    include: ['react', 'react-dom', 'lucide-react'],
    exclude: ['@vite/client', '@vite/env']
  }
})

