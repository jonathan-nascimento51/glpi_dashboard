// Configurações de otimização de recursos
export const RESOURCE_CONFIG = {
  // Configurações de imagem
  images: {
    // Formatos suportados em ordem de preferência
    formats: ['webp', 'avif', 'png', 'jpg'],
    // Qualidades para diferentes contextos
    quality: {
      thumbnail: 60,
      medium: 75,
      high: 85,
      lossless: 100
    },
    // Tamanhos responsivos
    sizes: {
      xs: 320,
      sm: 640,
      md: 768,
      lg: 1024,
      xl: 1280,
      xxl: 1920
    }
  },
  
  // Configurações de cache
  cache: {
    // TTL em segundos
    static: 31536000, // 1 ano
    api: 300,         // 5 minutos
    dynamic: 3600,    // 1 hora
    
    // Estratégias de cache
    strategies: {
      static: 'cache-first',
      api: 'network-first',
      dynamic: 'stale-while-revalidate'
    }
  },
  
  // Configurações de compressão
  compression: {
    gzip: {
      threshold: 1024, // bytes
      level: 6
    },
    brotli: {
      threshold: 1024,
      quality: 6
    }
  },
  
  // Configurações de lazy loading
  lazyLoading: {
    rootMargin: '50px',
    threshold: 0.1,
    // Placeholder para imagens
    placeholder: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZGRkIi8+PC9zdmc+'
  },
  
  // Configurações de preload
  preload: {
    // Recursos críticos para preload
    critical: [
      '/api/v1/metrics/levels/summary',
      '/api/v1/metrics/levels',
      '/api/v1/metrics/levels'
    ],
    // Recursos para prefetch
    prefetch: [
      '/api/v1/metrics/levels',
      '/api/v1/health/data',
      '/api/v1/metrics/levels/health'
    ]
  },
  
  // Configurações de bundle
  bundle: {
    // Tamanho máximo de chunk em KB
    maxChunkSize: 250,
    // Chunks para vendor
    vendor: {
      react: ['react', 'react-dom'],
      charts: ['recharts', 'chart.js'],
      ui: ['lucide-react', '@headlessui/react'],
      utils: ['date-fns', 'lodash']
    }
  }
};

// Utilitários para otimização
export const ResourceUtils = {
  // Gerar srcset para imagens responsivas
  generateSrcSet: (baseUrl: string, sizes: number[]) => {
    return sizes.map(size => `${baseUrl}?w=${size} ${size}w`).join(', ');
  },
  
  // Detectar suporte a formato de imagem
  supportsImageFormat: (format: string): Promise<boolean> => {
    return new Promise((resolve) => {
      const img = new Image();
      img.onload = () => resolve(true);
      img.onerror = () => resolve(false);
      
      const testImages = {
        webp: 'data:image/webp;base64,UklGRjoAAABXRUJQVlA4IC4AAACyAgCdASoCAAIALmk0mk0iIiIiIgBoSygABc6WWgAA/veff/0PP8bA//LwYAAA',
        avif: 'data:image/avif;base64,AAAAIGZ0eXBhdmlmAAAAAGF2aWZtaWYxbWlhZk1BMUIAAADybWV0YQAAAAAAAAAoaGRscgAAAAAAAAAAcGljdAAAAAAAAAAAAAAAAGxpYmF2aWYAAAAADnBpdG0AAAAAAAEAAAAeaWxvYwAAAABEAAABAAEAAAABAAABGgAAAB0AAAAoaWluZgAAAAAAAQAAABppbmZlAgAAAAABAABhdjAxQ29sb3IAAAAAamlwcnAAAABLaXBjbwAAABRpc3BlAAAAAAAAAAIAAAACAAAAEHBpeGkAAAAAAwgICAAAAAxhdjFDgQ0MAAAAABNjb2xybmNseAACAAIAAYAAAAAXaXBtYQAAAAAAAAABAAEEAQKDBAAAACVtZGF0EgAKCBgABogQEAwgMg8f8D///8WfhwB8+ErK42A='
      };
      
      img.src = testImages[format as keyof typeof testImages] || '';
    });
  },
  
  // Calcular tamanho otimizado de imagem
  calculateOptimalSize: (containerWidth: number, devicePixelRatio = 1) => {
    const targetWidth = containerWidth * devicePixelRatio;
    const sizes = Object.values(RESOURCE_CONFIG.images.sizes);
    
    // Encontrar o tamanho mais próximo
    return sizes.reduce((prev, curr) => 
      Math.abs(curr - targetWidth) < Math.abs(prev - targetWidth) ? curr : prev
    );
  },
  
  // Verificar se recurso deve ser preloaded
  shouldPreload: (url: string) => {
    return RESOURCE_CONFIG.preload.critical.some(pattern => 
      url.includes(pattern)
    );
  },
  
  // Verificar se recurso deve ser prefetched
  shouldPrefetch: (url: string) => {
    return RESOURCE_CONFIG.preload.prefetch.some(pattern => 
      url.includes(pattern)
    );
  }
};

export default RESOURCE_CONFIG;
