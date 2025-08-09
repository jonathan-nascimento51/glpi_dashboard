/**
 * Sistema de Linha de Base de Performance para GLPI Dashboard
 * Implementa comparação de métricas com valores de referência
 */

export interface PerformanceBaseline {
  homepage: {
    loadTime: number; // < 1000ms
    renderTime: number;
    apiResponseTime: number;
  };
  filters: {
    responseTime: number; // < 500ms
    renderTime: number;
  };
  autoRefresh: {
    updateTime: number; // < 800ms
    apiTime: number;
  };
  timestamp: number;
  version: string;
}

export interface PerformanceComparison {
  metric: string;
  current: number;
  baseline: number;
  difference: number;
  percentageChange: number;
  status: 'improved' | 'degraded' | 'stable';
  meetsTarget: boolean;
  target: number;
}

export interface PerformanceTargets {
  homepage: {
    loadTime: 1000; // 1 segundo
    renderTime: 300;
    apiResponseTime: 500;
  };
  filters: {
    responseTime: 500; // 500ms
    renderTime: 200;
  };
  autoRefresh: {
    updateTime: 800; // 800ms
    apiTime: 400;
  };
}

class PerformanceBaselineManager {
  private readonly STORAGE_KEY = 'glpi_performance_baseline';
  private readonly TARGETS: PerformanceTargets = {
    homepage: {
      loadTime: 1000,
      renderTime: 300,
      apiResponseTime: 500
    },
    filters: {
      responseTime: 500,
      renderTime: 200
    },
    autoRefresh: {
      updateTime: 800,
      apiTime: 400
    }
  };

  /**
   * Estabelece uma nova linha de base
   */
  setBaseline(metrics: Omit<PerformanceBaseline, 'timestamp' | 'version'>): void {
    const baseline: PerformanceBaseline = {
      ...metrics,
      timestamp: Date.now(),
      version: process.env.REACT_APP_VERSION || '1.0.0'
    };

    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(baseline));
    
    console.log('📊 Nova linha de base estabelecida:', baseline);
    this.logBaselineComparison(baseline);
  }

  /**
   * Obtém a linha de base atual
   */
  getBaseline(): PerformanceBaseline | null {
    try {
      const stored = localStorage.getItem(this.STORAGE_KEY);
      return stored ? JSON.parse(stored) : null;
    } catch (error) {
      console.error('Erro ao carregar linha de base:', error);
      return null;
    }
  }

  /**
   * Compara métricas atuais com a linha de base
   */
  compareWithBaseline(currentMetrics: Omit<PerformanceBaseline, 'timestamp' | 'version'>): PerformanceComparison[] {
    const baseline = this.getBaseline();
    if (!baseline) {
      console.warn('⚠️ Nenhuma linha de base encontrada. Estabelecendo nova linha de base...');
      this.setBaseline(currentMetrics);
      return [];
    }

    const comparisons: PerformanceComparison[] = [];

    // Comparar métricas da homepage
    comparisons.push(
      this.createComparison(
        'Homepage Load Time',
        currentMetrics.homepage.loadTime,
        baseline.homepage.loadTime,
        this.TARGETS.homepage.loadTime
      ),
      this.createComparison(
        'Homepage Render Time',
        currentMetrics.homepage.renderTime,
        baseline.homepage.renderTime,
        this.TARGETS.homepage.renderTime
      ),
      this.createComparison(
        'Homepage API Response',
        currentMetrics.homepage.apiResponseTime,
        baseline.homepage.apiResponseTime,
        this.TARGETS.homepage.apiResponseTime
      )
    );

    // Comparar métricas de filtros
    comparisons.push(
      this.createComparison(
        'Filter Response Time',
        currentMetrics.filters.responseTime,
        baseline.filters.responseTime,
        this.TARGETS.filters.responseTime
      ),
      this.createComparison(
        'Filter Render Time',
        currentMetrics.filters.renderTime,
        baseline.filters.renderTime,
        this.TARGETS.filters.renderTime
      )
    );

    // Comparar métricas de auto-refresh
    comparisons.push(
      this.createComparison(
        'Auto-refresh Update Time',
        currentMetrics.autoRefresh.updateTime,
        baseline.autoRefresh.updateTime,
        this.TARGETS.autoRefresh.updateTime
      ),
      this.createComparison(
        'Auto-refresh API Time',
        currentMetrics.autoRefresh.apiTime,
        baseline.autoRefresh.apiTime,
        this.TARGETS.autoRefresh.apiTime
      )
    );

    return comparisons;
  }

  /**
   * Cria uma comparação individual
   */
  private createComparison(
    metric: string,
    current: number,
    baseline: number,
    target: number
  ): PerformanceComparison {
    const difference = current - baseline;
    const percentageChange = baseline > 0 ? (difference / baseline) * 100 : 0;
    
    let status: 'improved' | 'degraded' | 'stable';
    if (Math.abs(percentageChange) < 5) {
      status = 'stable';
    } else if (difference < 0) {
      status = 'improved';
    } else {
      status = 'degraded';
    }

    return {
      metric,
      current,
      baseline,
      difference,
      percentageChange,
      status,
      meetsTarget: current <= target,
      target
    };
  }

  /**
   * Verifica se todas as metas foram atingidas
   */
  checkTargets(metrics: Omit<PerformanceBaseline, 'timestamp' | 'version'>): {
    allTargetsMet: boolean;
    failedTargets: string[];
    summary: Record<string, boolean>;
  } {
    const checks = {
      'Homepage Load Time': metrics.homepage.loadTime <= this.TARGETS.homepage.loadTime,
      'Homepage Render Time': metrics.homepage.renderTime <= this.TARGETS.homepage.renderTime,
      'Homepage API Response': metrics.homepage.apiResponseTime <= this.TARGETS.homepage.apiResponseTime,
      'Filter Response Time': metrics.filters.responseTime <= this.TARGETS.filters.responseTime,
      'Filter Render Time': metrics.filters.renderTime <= this.TARGETS.filters.renderTime,
      'Auto-refresh Update Time': metrics.autoRefresh.updateTime <= this.TARGETS.autoRefresh.updateTime,
      'Auto-refresh API Time': metrics.autoRefresh.apiTime <= this.TARGETS.autoRefresh.apiTime
    };

    const failedTargets = Object.entries(checks)
      .filter(([_, passed]) => !passed)
      .map(([metric]) => metric);

    return {
      allTargetsMet: failedTargets.length === 0,
      failedTargets,
      summary: checks
    };
  }

  /**
   * Gera relatório de comparação detalhado
   */
  generateComparisonReport(currentMetrics: Omit<PerformanceBaseline, 'timestamp' | 'version'>): {
    comparisons: PerformanceComparison[];
    targetCheck: ReturnType<typeof this.checkTargets>;
    recommendations: string[];
    timestamp: number;
  } {
    const comparisons = this.compareWithBaseline(currentMetrics);
    const targetCheck = this.checkTargets(currentMetrics);
    const recommendations = this.generateRecommendations(comparisons, targetCheck);

    const report = {
      comparisons,
      targetCheck,
      recommendations,
      timestamp: Date.now()
    };

    console.group('📊 Performance Comparison Report');
    console.log('Comparisons:', comparisons);
    console.log('Target Check:', targetCheck);
    console.log('Recommendations:', recommendations);
    console.groupEnd();

    return report;
  }

  /**
   * Gera recomendações baseadas nas comparações
   */
  private generateRecommendations(
    comparisons: PerformanceComparison[],
    targetCheck: ReturnType<typeof this.checkTargets>
  ): string[] {
    const recommendations: string[] = [];

    // Verificar métricas degradadas
    const degraded = comparisons.filter(c => c.status === 'degraded');
    if (degraded.length > 0) {
      recommendations.push(
        `⚠️ ${degraded.length} métrica(s) degradaram: ${degraded.map(d => d.metric).join(', ')}`
      );
    }

    // Verificar metas não atingidas
    if (!targetCheck.allTargetsMet) {
      recommendations.push(
        `🎯 ${targetCheck.failedTargets.length} meta(s) não atingida(s): ${targetCheck.failedTargets.join(', ')}`
      );
    }

    // Recomendações específicas
    const slowFilters = comparisons.find(c => c.metric.includes('Filter') && !c.meetsTarget);
    if (slowFilters) {
      recommendations.push('🔍 Considere implementar debounce nos filtros ou otimizar queries');
    }

    const slowHomepage = comparisons.find(c => c.metric.includes('Homepage') && !c.meetsTarget);
    if (slowHomepage) {
      recommendations.push('🏠 Considere lazy loading ou cache para a homepage');
    }

    const slowAutoRefresh = comparisons.find(c => c.metric.includes('Auto-refresh') && !c.meetsTarget);
    if (slowAutoRefresh) {
      recommendations.push('🔄 Otimize o auto-refresh com updates incrementais');
    }

    if (recommendations.length === 0) {
      recommendations.push('✅ Todas as métricas estão dentro dos targets!');
    }

    return recommendations;
  }

  /**
   * Log formatado da comparação com linha de base
   */
  private logBaselineComparison(baseline: PerformanceBaseline): void {
    console.group('📊 Performance Baseline vs Targets');
    
    console.log('🏠 Homepage:');
    console.log(`  Load Time: ${baseline.homepage.loadTime}ms (target: ${this.TARGETS.homepage.loadTime}ms)`);
    console.log(`  Render Time: ${baseline.homepage.renderTime}ms (target: ${this.TARGETS.homepage.renderTime}ms)`);
    console.log(`  API Response: ${baseline.homepage.apiResponseTime}ms (target: ${this.TARGETS.homepage.apiResponseTime}ms)`);
    
    console.log('🔍 Filters:');
    console.log(`  Response Time: ${baseline.filters.responseTime}ms (target: ${this.TARGETS.filters.responseTime}ms)`);
    console.log(`  Render Time: ${baseline.filters.renderTime}ms (target: ${this.TARGETS.filters.renderTime}ms)`);
    
    console.log('🔄 Auto-refresh:');
    console.log(`  Update Time: ${baseline.autoRefresh.updateTime}ms (target: ${this.TARGETS.autoRefresh.updateTime}ms)`);
    console.log(`  API Time: ${baseline.autoRefresh.apiTime}ms (target: ${this.TARGETS.autoRefresh.apiTime}ms)`);
    
    console.groupEnd();
  }

  /**
   * Reseta a linha de base
   */
  resetBaseline(): void {
    localStorage.removeItem(this.STORAGE_KEY);
    console.log('🧹 Linha de base resetada');
  }

  /**
   * Obtém os targets de performance
   */
  getTargets(): PerformanceTargets {
    return this.TARGETS;
  }
}

// Instância singleton
export const performanceBaseline = new PerformanceBaselineManager();

// Utilitários para debugging
export const debugBaseline = {
  setBaseline: (metrics: Omit<PerformanceBaseline, 'timestamp' | 'version'>) => {
    performanceBaseline.setBaseline(metrics);
  },
  
  getBaseline: () => {
    return performanceBaseline.getBaseline();
  },
  
  compareWithBaseline: (metrics: Omit<PerformanceBaseline, 'timestamp' | 'version'>) => {
    return performanceBaseline.compareWithBaseline(metrics);
  },
  
  checkTargets: (metrics: Omit<PerformanceBaseline, 'timestamp' | 'version'>) => {
    return performanceBaseline.checkTargets(metrics);
  },
  
  resetBaseline: () => {
    performanceBaseline.resetBaseline();
  }
};

// Expor no window para debugging em desenvolvimento
if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
  (window as any).debugBaseline = debugBaseline;
  (window as any).performanceBaseline = performanceBaseline;
}