import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { usePerformanceReports, usePerformanceDebug, useApiPerformance, useFilterPerformance } from "../hooks/usePerformanceMonitoring";
import { performanceMonitor } from '../utils/performanceMonitor';

interface PerformanceDashboardProps {
  isVisible: boolean;
  onClose: () => void;
}

type TabType = 'overview' | 'components' | 'api' | 'browser';

const formatTime = (time: number): string => {
  if (time < 1000) return `${time.toFixed(2)}ms`;
  return `${(time / 1000).toFixed(2)}s`;
};

const getPerformanceColor = (time: number): string => {
  if (time < 100) return 'text-green-600';
  if (time < 500) return 'text-yellow-600';
  return 'text-red-600';
};

const MetricCard = React.memo(({ title, value, description }: {
  title: string;
  value: number;
  description: string;
}) => (
  <div className="bg-white rounded-lg shadow-sm border p-4">
    <h4 className="text-sm font-medium text-gray-600 mb-1">{title}</h4>
    <p className={`text-2xl font-bold ${getPerformanceColor(value)}`}>
      {formatTime(value)}
    </p>
    <p className="text-xs text-gray-500 mt-1">{description}</p>
  </div>
));

const PerformanceDashboard: React.FC<PerformanceDashboardProps> = ({ isVisible, onClose }) => {
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  
  const { reports, generateReport, clearReports, averageMetrics, latestReport } = usePerformanceReports();
  const { isEnabled, toggleMonitoring, logMetrics, exportToAnalytics } = usePerformanceDebug();
  const { apiMetrics } = useApiPerformance();
  const { filterMetrics } = useFilterPerformance();

  const handleTabChange = useCallback((tab: TabType) => {
    setActiveTab(tab);
  }, []);

  const handleAutoRefreshToggle = useCallback(() => {
    setAutoRefresh(prev => !prev);
  }, []);

  const handleGenerateReport = useCallback(async () => {
    setIsGenerating(true);
    try {
      await generateReport();
    } finally {
      setIsGenerating(false);
    }
  }, [generateReport]);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (autoRefresh && isVisible) {
      interval = setInterval(() => {
        // Auto refresh logic here
      }, 5000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh, isVisible]);

  const ComponentMetricsTable = useMemo(() => (
    <div className="bg-white rounded-lg shadow-sm border">
      <div className="p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Component Performance</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Component
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Render Time
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Re-renders
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  Dashboard
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {formatTime(45)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  3
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                    Good
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  ), []);

  const browserMetricsData = useMemo(() => {
    if (typeof window === 'undefined') return null;
    
    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
    const paint = performance.getEntriesByType('paint');
    
    return {
      navigation,
      paint,
      memory: (performance as any).memory
    };
  }, []);

  const BrowserMetricsPanel = useMemo(() => {
    if (!browserMetricsData) {
      return (
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Browser Metrics</h3>
          <p className="text-gray-600">Métricas do navegador não disponíveis.</p>
        </div>
      );
    }

    const { navigation, paint, memory } = browserMetricsData;

    return (
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Navigation Metrics</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <MetricCard
              title="DOM Content Loaded"
              value={navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart}
              description="Tempo para carregar DOM"
            />
            <MetricCard
              title="Load Complete"
              value={navigation.loadEventEnd - navigation.loadEventStart}
              description="Tempo total de carregamento"
            />
            <MetricCard
              title="First Byte"
              value={navigation.responseStart - navigation.requestStart}
              description="Tempo até primeiro byte"
            />
            <MetricCard
              title="DNS Lookup"
              value={navigation.domainLookupEnd - navigation.domainLookupStart}
              description="Tempo de resolução DNS"
            />
          </div>
        </div>

        {paint.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Paint Metrics</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {paint.map((entry, index) => (
                <MetricCard
                  key={`paint-metric-${index}`}
                  title={entry.name}
                  value={entry.startTime}
                  description={`Tempo para ${entry.name}`}
                />
              ))}
            </div>
          </div>
        )}

        {memory && (
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Memory Usage</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <MetricCard
                title="Used JS Heap"
                value={memory.usedJSHeapSize / 1024 / 1024}
                description="MB de memória usada"
              />
              <MetricCard
                title="Total JS Heap"
                value={memory.totalJSHeapSize / 1024 / 1024}
                description="MB total de heap"
              />
              <MetricCard
                title="Heap Limit"
                value={memory.jsHeapSizeLimit / 1024 / 1024}
                description="MB limite de heap"
              />
            </div>
          </div>
        )}

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Recent Performance Measurements</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Metric
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Value
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                <tr>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    Time to Interactive
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatTime(navigation.domInteractive - navigation.navigationStart)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      (navigation.domInteractive - navigation.navigationStart) < 2000 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {(navigation.domInteractive - navigation.navigationStart) < 2000 ? 'Good' : 'Needs Improvement'}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    );
  }, [browserMetricsData]);

  if (!isVisible) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="bg-gray-100 rounded-lg shadow-xl w-full max-w-7xl h-full max-h-[90vh] overflow-hidden"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="bg-white border-b px-6 py-4 flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-gray-800">Performance Dashboard</h2>
              <p className="text-sm text-gray-600">Monitoramento em tempo real da aplicação</p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <label className="text-sm text-gray-600">Auto-refresh:</label>
                <button
                  onClick={handleAutoRefreshToggle}
                  className={`px-3 py-1 rounded text-xs font-medium ${
                    autoRefresh
                      ? 'bg-green-100 text-green-800'
                      : 'bg-gray-100 text-gray-600'
                  }`}
                >
                  {autoRefresh ? 'ON' : 'OFF'}
                </button>
              </div>
              <button
                onClick={toggleMonitoring}
                className={`px-3 py-1 rounded text-xs font-medium ${
                  isEnabled
                    ? 'bg-blue-100 text-blue-800'
                    : 'bg-gray-100 text-gray-600'
                }`}
              >
                Monitoring: {isEnabled ? 'ON' : 'OFF'}
              </button>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          <div className="bg-white border-b px-6">
            <nav className="flex space-x-8">
              {[
                { id: 'overview', label: 'Overview' },
                { id: 'components', label: 'Components' },
                { id: 'api', label: 'API Calls' },
                { id: 'browser', label: 'Browser Metrics' }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => handleTabChange(tab.id as TabType)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          <div className="flex-1 overflow-auto p-6">
            {activeTab === 'overview' && (
              <div className="space-y-6">
                <div className="flex flex-wrap gap-3">
                  <button
                    onClick={handleGenerateReport}
                    disabled={isGenerating}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                  >
                    {isGenerating ? 'Gerando...' : 'Gerar Relatório'}
                  </button>
                  <button
                    onClick={logMetrics}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                  >
                    Log Metrics
                  </button>
                  <button
                    onClick={clearReports}
                    className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                  >
                    Limpar Dados
                  </button>
                  <button
                    onClick={exportToAnalytics}
                    className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                  >
                    Export Analytics
                  </button>
                </div>

                {averageMetrics && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">Métricas Médias</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                      <MetricCard
                        title="Tempo de Filtro"
                        value={averageMetrics.filterChangeTime}
                        description="Média de tempo para aplicar filtros"
                      />
                      <MetricCard
                        title="Resposta da API"
                        value={averageMetrics.apiResponseTime}
                        description="Tempo médio de resposta da API"
                      />
                      <MetricCard
                        title="Renderização"
                        value={averageMetrics.renderTime}
                        description="Tempo médio de renderização"
                      />
                      <MetricCard
                        title="Operação Total"
                        value={averageMetrics.totalOperationTime}
                        description="Tempo total médio das operações"
                      />
                    </div>
                  </div>
                )}

                {latestReport && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">Último Relatório</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                      <MetricCard
                        title="Filtros"
                        value={latestReport.summary.filterChangeTime}
                        description="Último tempo de filtro"
                      />
                      <MetricCard
                        title="API"
                        value={latestReport.summary.apiResponseTime}
                        description="Última resposta da API"
                      />
                      <MetricCard
                        title="Render"
                        value={latestReport.summary.renderTime}
                        description="Último tempo de render"
                      />
                      <MetricCard
                        title="Total"
                        value={latestReport.summary.totalOperationTime}
                        description="Última operação total"
                      />
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'components' && ComponentMetricsTable}
            {activeTab === 'browser' && BrowserMetricsPanel}
            
            {activeTab === 'api' && (
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">API Performance</h3>
                <p className="text-gray-600">Métricas de chamadas de API serão exibidas aqui quando disponíveis.</p>
              </div>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default PerformanceDashboard;