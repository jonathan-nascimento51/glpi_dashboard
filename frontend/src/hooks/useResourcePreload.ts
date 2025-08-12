import { useEffect, useCallback, useState, useRef, useMemo } from 'react';
import { ResourceUtils, RESOURCE_CONFIG } from '../config/resources';

interface UseResourcePreloadOptions {
  enabled?: boolean;
  priority?: 'high' | 'low';
}

export const useResourcePreload = (options: UseResourcePreloadOptions = {}) => {
  const { enabled = true, priority = 'high' } = options;

  // Preload de recursos críticos
  const preloadResource = useCallback((url: string, type: 'script' | 'style' | 'image' | 'fetch' = 'fetch') => {
    if (!enabled) return;

    const link = document.createElement('link');
    link.rel = 'preload';
    link.href = url;
    link.as = type;
    
    if (priority === 'high') {
      link.setAttribute('importance', 'high');
    }

    // Para recursos de API, usar fetch
    if (type === 'fetch') {
      link.as = 'fetch';
      link.setAttribute('crossorigin', 'anonymous');
    }

    document.head.appendChild(link);

    return () => {
      if (document.head.contains(link)) {
        document.head.removeChild(link);
      }
    };
  }, [enabled, priority]);

  // Prefetch de recursos não críticos
  const prefetchResource = useCallback((url: string) => {
    if (!enabled) return;

    const link = document.createElement('link');
    link.rel = 'prefetch';
    link.href = url;
    link.setAttribute('importance', 'low');

    document.head.appendChild(link);

    return () => {
      if (document.head.contains(link)) {
        document.head.removeChild(link);
      }
    };
  }, [enabled]);

  // Preload automático de recursos críticos
  useEffect(() => {
    if (!enabled) return;

    const cleanupFunctions: (() => void)[] = [];

    // Preload recursos críticos
    RESOURCE_CONFIG.preload.critical.forEach(url => {
      const cleanup = preloadResource(url, 'fetch');
      if (cleanup) cleanupFunctions.push(cleanup);
    });

    // Prefetch recursos não críticos após um delay
    const prefetchTimer = setTimeout(() => {
      RESOURCE_CONFIG.preload.prefetch.forEach(url => {
        const cleanup = prefetchResource(url);
        if (cleanup) cleanupFunctions.push(cleanup);
      });
    }, 2000); // 2 segundos de delay

    return () => {
      clearTimeout(prefetchTimer);
      cleanupFunctions.forEach(cleanup => cleanup());
    };
  }, [enabled, preloadResource, prefetchResource]);

  return {
    preloadResource,
    prefetchResource
  };
};

// Hook para lazy loading de imagens
export const useLazyImage = (src: string, options: IntersectionObserverInit = {}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isInView, setIsInView] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const imgRef = useRef<HTMLImageElement>(null);

  const defaultOptions = {
    rootMargin: RESOURCE_CONFIG.lazyLoading.rootMargin,
    threshold: RESOURCE_CONFIG.lazyLoading.threshold,
    ...options
  };

  useEffect(() => {
    const img = imgRef.current;
    if (!img) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          observer.unobserve(img);
        }
      },
      defaultOptions
    );

    observer.observe(img);

    return () => {
      observer.unobserve(img);
    };
  }, [defaultOptions]);

  useEffect(() => {
    if (!isInView) return;

    const img = new Image();
    img.onload = () => setIsLoaded(true);
    img.onerror = () => setError('Falha ao carregar imagem');
    img.src = src;
  }, [isInView, src]);

  return {
    imgRef,
    isLoaded,
    isInView,
    error,
    src: isInView ? src : RESOURCE_CONFIG.lazyLoading.placeholder
  };
};

// Hook para otimização de imagens responsivas
export const useResponsiveImage = (baseUrl: string, alt: string = '') => {
  const [optimalFormat, setOptimalFormat] = useState<string>('jpg');
  const [containerWidth, setContainerWidth] = useState<number>(0);
  const containerRef = useRef<HTMLDivElement>(null);

  // Detectar melhor formato suportado
  useEffect(() => {
    const detectFormat = async () => {
      for (const format of RESOURCE_CONFIG.images.formats) {
        const isSupported = await ResourceUtils.supportsImageFormat(format);
        if (isSupported) {
          setOptimalFormat(format);
          break;
        }
      }
    };

    detectFormat();
  }, []);

  // Observar mudanças no tamanho do container
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const resizeObserver = new ResizeObserver(([entry]) => {
      setContainerWidth(entry.contentRect.width);
    });

    resizeObserver.observe(container);
    setContainerWidth(container.offsetWidth);

    return () => {
      resizeObserver.unobserve(container);
    };
  }, []);

  // Calcular tamanho otimizado
  const optimalSize = useMemo(() => {
    if (!containerWidth) return RESOURCE_CONFIG.images.sizes.md;
    return ResourceUtils.calculateOptimalSize(containerWidth);
  }, [containerWidth]);

  // Gerar URLs otimizadas
  const imageUrl = useMemo(() => {
    return `${baseUrl}?format=${optimalFormat}&w=${optimalSize}&q=${RESOURCE_CONFIG.images.quality.medium}`;
  }, [baseUrl, optimalFormat, optimalSize]);

  const srcSet = useMemo(() => {
    const sizes = Object.values(RESOURCE_CONFIG.images.sizes);
    return ResourceUtils.generateSrcSet(
      `${baseUrl}?format=${optimalFormat}&q=${RESOURCE_CONFIG.images.quality.medium}`,
      sizes
    );
  }, [baseUrl, optimalFormat]);

  return {
    containerRef,
    imageUrl,
    srcSet,
    alt,
    optimalFormat,
    optimalSize
  };
};

export default useResourcePreload;

