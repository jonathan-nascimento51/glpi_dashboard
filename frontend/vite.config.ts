import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react({
      // Otimizações do React
      fastRefresh: true
    })
  ],
  server: {
    port: 3001,
    host: true, // Permite acesso externo
    cors: true,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
        timeout: 60000, // 60 segundos
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false, // Desabilitar sourcemaps em produção para performance
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // Remove console.logs em produção
        drop_debugger: true,
      },
    },
    rollupOptions: {
      output: {
        // Code splitting para melhor cache
        manualChunks: {
          vendor: ['react', 'react-dom'],
          ui: ['@radix-ui/react-slot', 'class-variance-authority'],
          charts: ['recharts'],
          animations: ['framer-motion'],
          utils: ['axios', 'date-fns']
        },
      },
    },
    chunkSizeWarningLimit: 1000,
  },
  resolve: {
    alias: {
      '@': '/src',
    },
  },
  optimizeDeps: {
    // Pre-bundle dependencies para startup mais rápido
    include: [
      'react',
      'react-dom',
      'axios',
      'recharts',
      'framer-motion',
      '@radix-ui/react-slot',
      'class-variance-authority'
    ],
    // Força re-bundling de dependências
    force: false
  },
  esbuild: {
    // Otimizações do esbuild
    target: 'es2020',
    logOverride: { 'this-is-undefined-in-esm': 'silent' }
  }
})