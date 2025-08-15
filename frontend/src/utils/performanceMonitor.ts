/**
 * Sistema de Monitoramento de Performance para Dashboard GLPI
 * Implementa medicoes detalhadas usando Performance API e integracao com React DevTools
 */

export interface PerformanceMetric {
  name: string;
  startTime: number;
  endTime?: number;
  duration?: number;
  metadata?: Record<string, any>;
}

export interface PerformanceReport {
  timestamp: number;
  metrics: PerformanceMetric[];
  summary: {
    filterChangeTime: number;
    apiResponseTime: number;
    renderTime: number;
    totalOperationTime: number;
  };
  componentMetrics: ComponentMetric[];
}

export interface ComponentMetric {
  name: string;
  renderCount: number;
  totalRenderTime: number;
  averageRenderTime: number;
  lastRenderTime: number;
  props?: any;
}

class PerformanceMonitor {
  private metrics: Map<string, PerformanceMetric> = new Map();
  private componentMetrics: Map<string, ComponentMetric> = new Map();
  private isEnabled: boolean = process.env.NODE_ENV === 'development';
  private reports: PerformanceReport[] = [];

  constructor() {
    // Limpar marcacoes antigas ao inicializar
    if (typeof performance !== 'undefined' && performance.clearMarks) {
      performance.clearMarks();
      performance.clearMeasures();
    }
  }

  /**
   * Inicia uma medicao de performance
   */
  startMeasure(name: string, metadata?: Record<string, any>): void {
    if (!this.isEnabled) return;

    const markName = `${name}-start`;
    performance.mark(markName);
    
    this.metrics.set(name, {
      name,
      startTime: performance.now(),
      metadata
    });

    console.log(`🚀 Performance: Iniciando medicao '${name}'`, metadata);
  }

  /**
   * Finaliza uma medicao de performance
   */
  endMeasure(name: string, metadata?: Record<string, any>): number {
    if (!this.isEnabled) return 0;

    const metric = this.metrics.get(name);
    if (!metric) {
      console.warn(`⚠️ Performance: Medicao '${name}' nao foi iniciada`);
      return 0;
    }

    const endTime = performance.now();
    const duration = endTime - metric.startTime;
    
    const markStartName = `${name}-start`;
    const markEndName = `${name}-end`;
    const measureName = `${name}-duration`;
    
    performance.mark(markEndName);
    performance.measure(measureName, markStartName, markEndName);

    // Atualizar metrica
    metric.endTime = endTime;
    metric.duration = duration;
    if (metadata) {
      metric.metadata = { ...metric.metadata, ...metadata };
    }

    console.log(`✅ Performance: '${name}' concluido em ${duration.toFixed(2)}ms`, {
      duration,
      metadata: metric.metadata
    });

    return duration;
  }

  /**
   * Mede o tempo de uma operacao assincrona
   */
  async measureAsync<T>(
    name: string, 
    operation: () => Promise<T>, 
    metadata?: Record<string, any>
  ): Promise<T> {
    this.startMeasure(name, metadata);
    try {
      const result = await operation();
      this.endMeasure(name, { success: true });
      return result;
    } catch (error) {
      this.endMeasure(name, { success: false, error: error instanceof Error ? error.message : 'Unknown error' });
      throw error;
    }
  }

  /**
   * Registra metricas de componente React
   */
  recordComponentRender(
    componentName: string, 
    renderTime: number, 
    props?: any
  ): void {
    if (!this.isEnabled) return;

    const existing = this.componentMetrics.get(componentName);
    if (existing) {
      existing.renderCount++;
      existing.totalRenderTime += renderTime;
      existing.averageRenderTime = existing.totalRenderTime / existing.renderCount;
      existing.lastRenderTime = renderTime;
      existing.props = props;
    } else {
      this.componentMetrics.set(componentName, {
        name: componentName,
        renderCount: 1,
        totalRenderTime: renderTime,
        averageRenderTime: renderTime,
        lastRenderTime: renderTime,
        props
      });
    }

    console.log(`🎨 Component Render: ${componentName} - ${renderTime.toFixed(2)}ms`);
  }

  /**
   * Marca renderizacao de componente (alias para recordComponentRender)
   */
  markComponentRender(
    componentName: string,
    metadata?: Record<string, any>
  ): void {
    if (!this.isEnabled) return;
    
    const renderTime = performance.now();
    this.recordComponentRender(componentName, renderTime, metadata);
  }

  /**
   * Mede tempo de resposta da API
   */
  async measureApiCall<T>(
    endpoint: string,
    apiCall: () => Promise<T>
  ): Promise<T> {
    const measureName = `api-${endpoint}`;
    return this.measureAsync(measureName, apiCall, { endpoint, type: 'api-call' });
  }

  /**
   * Mede operacao completa de filtro
   */
  async measureFilterOperation<T>(
    filterType: string,
    operation: () => Promise<T>
  ): Promise<T> {
    const measureName = `filter-${filterType}`;
    return this.measureAsync(measureName, operation, { filterType, type: 'filter-operation' });
  }

  /**
   * Gera relatorio de performance
   */
  generateReport(): PerformanceReport {
    const timestamp = Date.now();
    const metrics = Array.from(this.metrics.values());
    const componentMetrics = Array.from(this.componentMetrics.values());

    // Calcular metricas resumidas
    const filterMetrics = metrics.filter(m => m.name.startsWith('filter-'));
    const apiMetrics = metrics.filter(m => m.name.startsWith('api-'));
    const renderMetrics = metrics.filter(m => m.name.includes('render'));

    const summary = {
      filterChangeTime: this.calculateAverage(filterMetrics.map(m => m.duration || 0)),
      apiResponseTime: this.calculateAverage(apiMetrics.map(m => m.duration || 0)),
      renderTime: this.calculateAverage(renderMetrics.map(m => m.duration || 0)),
      totalOperationTime: this.calculateAverage(metrics.map(m => m.duration || 0))
    };

    const report: PerformanceReport = {
      timestamp,
      metrics,
      summary,
      componentMetrics
    };

    this.reports.push(report);
    
    // Manter apenas os ultimos 10 relatorios
    if (this.reports.length > 10) {
      this.reports = this.reports.slice(-10);
    }

    return report;
  }

  /**
   * Obtem metricas do Performance API do navegador
   */
  getBrowserMetrics(): PerformanceEntry[] {
    if (typeof performance === 'undefined') return [];
    
    return [
      ...performance.getEntriesByType('mark'),
      ...performance.getEntriesByType('measure'),
      ...performance.getEntriesByType('navigation')
    ];
  }

  /**
   * Calcula percentil 95 de uma lista de valores
   */
  calculateP95(values: number[]): number {
    if (values.length === 0) return 0;
    
    const sorted = [...values].sort((a, b) => a - b);
    const index = Math.ceil(sorted.length * 0.95) - 1;
    return sorted[Math.max(0, index)];
  }

  /**
   * Calcula media de uma lista de valores
   */
  private calculateAverage(values: number[]): number {
    if (values.length === 0) return 0;
    return values.reduce((sum, val) => sum + val, 0) / values.length;
  }

  /**
   * Limpa todas as metricas
   */
  clear(): void {
    this.metrics.clear();
    this.componentMetrics.clear();
    if (typeof performance !== 'undefined') {
      performance.clearMarks();
      performance.clearMeasures();
    }
    console.log('🧹 Performance: Metricas limpas');
  }

  /**
   * Obtem estatisticas detalhadas
   */
  getDetailedStats(): {
    totalMeasurements: number;
    componentRenders: number;
    averageFilterTime: number;
    averageApiTime: number;
    p95FilterTime: number;
    p95ApiTime: number;
    topSlowComponents: ComponentMetric[];
  } {
    const metrics = Array.from(this.metrics.values());
    const filterTimes = metrics
      .filter(m => m.name.startsWith('filter-') && m.duration)
      .map(m => m.duration!);
    const apiTimes = metrics
      .filter(m => m.name.startsWith('api-') && m.duration)
      .map(m => m.duration!);
    
    const topSlowComponents = Array.from(this.componentMetrics.values())
      .sort((a, b) => b.averageRenderTime - a.averageRenderTime)
      .slice(0, 5);

    return {
      totalMeasurements: metrics.length,
      componentRenders: Array.from(this.componentMetrics.values())
        .reduce((sum, c) => sum + c.renderCount, 0),
      averageFilterTime: this.calculateAverage(filterTimes),
      averageApiTime: this.calculateAverage(apiTimes),
      p95FilterTime: this.calculateP95(filterTimes),
      p95ApiTime: this.calculateP95(apiTimes),
      topSlowComponents
    };
  }

  /**
   * Habilita/desabilita monitoramento
   */
  setEnabled(enabled: boolean): void {
    this.isEnabled = enabled;
    console.log(`🔧 Performance Monitor: ${enabled ? 'Habilitado' : 'Desabilitado'}`);
  }

  /**
   * Exporta dados para analytics (producao)
   */
  exportToAnalytics(): void {
    if (process.env.NODE_ENV !== 'production') return;
    
    const report = this.generateReport();
    
    // Em producao, enviar para servico de analytics
    // Exemplo: Google Analytics, DataDog, etc.
    console.log('📊 Enviando metricas para analytics:', report.summary);
    
    // Implementar integracao com servico de analytics aqui
    // gtag('event', 'performance_metric', {
    //   filter_time: report.summary.filterChangeTime,
    //   api_time: report.summary.apiResponseTime,
    //   render_time: report.summary.renderTime
    // });
  }
}

// Instancia singleton
export const performanceMonitor = new PerformanceMonitor();

// Hook para React DevTools Profiler
export const usePerformanceProfiler = () => {
  const onRenderCallback = (
    id: string,
    phase: 'mount' | 'update',
    actualDuration: number,
    baseDuration: number,
    startTime: number,
    commitTime: number,
    interactions: Set<any>
  ) => {
    performanceMonitor.recordComponentRender(
      id,
      actualDuration,
      {
        phase,
        baseDuration,
        startTime,
        commitTime,
        interactions: interactions ? interactions.size : 0
      }
    );
  };

  return { onRenderCallback };
};

// Utilitarios para debugging
export const debugPerformance = {
  logCurrentMetrics: () => {
    const stats = performanceMonitor.getDetailedStats();
    console.table(stats);
  },
  
  logComponentMetrics: () => {
    const components = Array.from(performanceMonitor['componentMetrics'].values());
    console.table(components);
  },
  
  generateReport: () => {
    return performanceMonitor.generateReport();
  },
  
  clear: () => {
    performanceMonitor.clear();
  }
};

// Expor no window para debugging em desenvolvimento
if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
  (window as any).debugPerformance = debugPerformance;
  (window as any).performanceMonitor = performanceMonitor;
}