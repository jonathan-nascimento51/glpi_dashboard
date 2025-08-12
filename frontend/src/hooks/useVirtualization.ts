import { useState, useEffect, useMemo, useCallback } from 'react';

interface VirtualizationOptions {
  itemHeight: number;
  containerHeight: number;
  overscan?: number;
}

interface VirtualizationResult<T> {
  virtualItems: Array<{
    index: number;
    start: number;
    end: number;
    item: T;
  }>;
  totalHeight: number;
  scrollToIndex: (index: number) => void;
}

export function useVirtualization<T>(
  items: T[],
  options: VirtualizationOptions
): VirtualizationResult<T> {
  const { itemHeight, containerHeight, overscan = 5 } = options;
  const [scrollTop, setScrollTop] = useState(0);

  const totalHeight = items.length * itemHeight;
  
  const visibleRange = useMemo(() => {
    const start = Math.floor(scrollTop / itemHeight);
    const end = Math.min(
      start + Math.ceil(containerHeight / itemHeight),
      items.length - 1
    );
    
    return {
      start: Math.max(0, start - overscan),
      end: Math.min(items.length - 1, end + overscan)
    };
  }, [scrollTop, itemHeight, containerHeight, overscan, items.length]);

  const virtualItems = useMemo(() => {
    const result = [];
    for (let i = visibleRange.start; i <= visibleRange.end; i++) {
      result.push({
        index: i,
        start: i * itemHeight,
        end: (i + 1) * itemHeight,
        item: items[i]
      });
    }
    return result;
  }, [visibleRange, itemHeight, items]);

  const scrollToIndex = useCallback((index: number) => {
    const element = document.getElementById(`virtual-container`);
    if (element) {
      element.scrollTop = index * itemHeight;
    }
  }, [itemHeight]);

  return {
    virtualItems,
    totalHeight,
    scrollToIndex
  };
}

// Hook para detectar quando usar virtualização
export function useShouldVirtualize(itemCount: number, threshold = 100): boolean {
  return itemCount > threshold;
}
