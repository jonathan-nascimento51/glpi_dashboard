/**
 * Dashboard de Performance - Exibe métricas em tempo real
 * Integra com React DevTools Profiler e Performance API
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  usePerformanceReports,
  usePerformanceDebug,
  useApiPerformance,
  useFilterPerformance
} from '../hooks/usePerformanceMonitoring';
import { performanceMonitor } from '../utils/performanceMonitor';

interface PerformanceDashboardProps {
  isVisible: boolean;
  onClose: () => void;
}

const PerformanceDashboard: React.FC<PerformanceDashboardProps> = ({
  isVisible,
  onClose
}) => {
  const {
    reports,
    generateReport,
    clearReports,
    exportToAnalytics,
    isGenerating,
    latestReport,
    averageMetrics
  } = usePerformanceReports();

  const {
    isEnabled,
    toggleMonitoring,
    getDebugInfo,
    logMetrics,
    clearMetrics,
    debugInfo
  } = usePerformanceDebug();

  const [activeTab, setActiveTab] = useState<'overview' | 'components' | 'api' | 'browser'>('overview');
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState(5000);

  // Auto-refresh
  useEffect(() => {
    if (!autoRefresh || !isVisible) return;

    const interval = setInterval(() => {
      generateReport();
      getDebugInfo();
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, isVisible, generateReport, getDebugInfo]);

  // Gerar relatório inicial
  useEffect(() => {
    if (isVisible && reports.length === 0) {
      generateReport();
    }
  }, [isVisible, reports.length, generateReport]);

  const formatTime = (time: number) => {
    if (time < 1) return `${(time * 1000).toFixed(0)}μs`;
    if (time < 1000) return `${time.toFixed(2)}ms`;
    return `${(time / 1000).toFixed(2)}s`;
  };

  const getPerformanceColor = (time: number, thresholds = { good: 100, warning: 500 }) => {
    if (time <= thresholds.good) return 'text-green-600';
    if (time <= thresholds.warning) return 'text-yellow-600';
    return 'text-red-600';
  };

  const MetricCard: React.FC<{
    title: string;
    value: number;
    unit?: string;
    description?: string;
    trend?: 'up' | 'down' | 'stable';
  }> = ({ title, value, unit = 'ms', description, trend }) => (
    <motion.div
      className="bg-white rounded-lg p-4 shadow-sm border"
      whileHover={{ scale: 1.02 }}
      transition={{ duration: 0.2 }}
    >
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-medium text-gray-700">{title}</h3>
        {trend && (
          <span className={`text-xs ${
            trend === 'up' ? 'text-red-500' :
            trend === 'down' ? 'text-green-500' :
            'text-gray-500'
          }`}>
            {trend === 'up' ? '↗' : trend === 'down' ? '↘' : '→'}
          </span>
        )}
      </div>
      <div className={`text-2xl font-bold ${getPerformanceColor(value)}`}>
        {formatTime(value)}
      </div>
      {description && (
        <p className="text-xs text-gray-500 mt-1">{description}</p>
      )}
    </motion.div>
  );

  const ComponentMetricsTable: React.FC = () => {
    const componentMetrics = latestReport?.componentMetrics || [];
    const sortedComponents = [...componentMetrics]
      .sort((a, b) => b.averageRenderTime - a.averageRenderTime);

    return (
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-4 border-b">
          <h3 className="text-lg font-semibold text-gray-800">Component Performance</h3>
          <p className="text-sm text-gray-600">Componentes ordenados por tempo médio de renderização</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Componente
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Renders
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tempo Médio
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Último Render
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tempo Total
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {sortedComponents.map((component, index) => (
                <tr key={component.name} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                  <td className="px-4 py-3 text-sm font-medium text-gray-900">
                    {component.name}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-700">
                    {component.renderCount}
                  </td>
                  <td className={`px-4 py-3 text-sm font-medium ${
                    getPerformanceColor(component.averageRenderTime, { good: 16, warning: 50 })
                  }`}>
                    {formatTime(component.averageRenderTime)}
                  </td>
                  <td className={`px-4 py-3 text-sm ${
                    getPerformanceColor(component.lastRenderTime, { good: 16, warning: 50 })
                  }`}>
                    {formatTime(component.lastRenderTime)}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-700">
                    {formatTime(component.totalRenderTime)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  const BrowserMetricsPanel: React.FC = () => {
    const browserMetrics = performanceMonitor.getBrowserMetrics();
    const navigationMetrics = browserMetrics.filter(m => m.entryType === 'navigation');
    const measureMetrics = browserMetrics.filter(m => m.entryType === 'measure').slice(-10);

    return (
      <div className="space-y-6">
        {/* Navigation Metrics */}
        {navigationMetrics.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm border">
            <div className="p-4 border-b">
              <h3 className="text-lg font-semibold text-gray-800">Navigation Metrics</h3>
            </div>
            <div className="p-4">
              {navigationMetrics.map((metric: any, index) => (
                <div key={index} className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <MetricCard
                    title="DOM Content Loaded"
                    value={metric.domContentLoadedEventEnd - metric.domContentLoadedEventStart}
                    description="Tempo para carregar DOM"
                  />
                  <MetricCard
                    title="Load Complete"
                    value={metric.loadEventEnd - metric.loadEventStart}
                    description="Tempo total de carregamento"
                  />
                  <MetricCard
                    title="DNS Lookup"
                    value={metric.domainLookupEnd - metric.domainLookupStart}
                    description="Resolução DNS"
                  />
                  <MetricCard
                    title="Connect Time"
                    value={metric.connectEnd - metric.connectStart}
                    description="Tempo de conexão"
                  />
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Performance Measures */}
        <div className="bg-white rounded-lg shadow-sm border">
          <div className="p-4 border-b">
            <h3 className="text-lg font-semibold text-gray-800">Recent Measurements</h3>
            <p className="text-sm text-gray-600">Últimas 10 medições de performance</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Nome
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Duração
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Início
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {measureMetrics.map((metric, index) => (
                  <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">
                      {metric.name}
                    </td>
                    <td className={`px-4 py-3 text-sm font-medium ${
                      getPerformanceColor(metric.duration)
                    }`}>
                      {formatTime(metric.duration)}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-700">
                      {formatTime(metric.startTime)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    );
  };

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
          {/* Header */}
          <div className="bg-white border-b px-6 py-4 flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-gray-800">Performance Dashboard</h2>
              <p className="text-sm text-gray-600">Monitoramento em tempo real da aplicação</p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <label className="text-sm text-gray-600">Auto-refresh:</label>
                <button
                  onClick={() => setAutoRefresh(!autoRefresh)}
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

          {/* Tabs */}
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
                  onClick={() => setActiveTab(tab.id as any)}
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

          {/* Content */}
          <div className="flex-1 overflow-auto p-6">
            {activeTab === 'overview' && (
              <div className="space-y-6">
                {/* Action Buttons */}
                <div className="flex flex-wrap gap-3">
                  <button
                    onClick={generateReport}
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

                {/* Summary Metrics */}
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

                {/* Latest Report Summary */}
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

            {activeTab === 'components' && <ComponentMetricsTable />}
            {activeTab === 'browser' && <BrowserMetricsPanel />}
            
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