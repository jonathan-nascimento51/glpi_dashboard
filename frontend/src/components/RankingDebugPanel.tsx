import React, { useState, useEffect } from 'react';
import { technicianRankingCache } from '../services/cache';
import type { CacheMetrics, CacheAlert, CacheLog } from '../services/cache';

interface RankingDebugPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

const RankingDebugPanel: React.FC<RankingDebugPanelProps> = ({ isOpen, onClose }) => {
  const [metrics, setMetrics] = useState<CacheMetrics | null>(null);
  const [logs, setLogs] = useState<CacheLog[]>([]);
  const [alerts, setAlerts] = useState<CacheAlert[]>([]);
  const [refreshInterval, setRefreshInterval] = useState<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (isOpen) {
      // Atualizar métricas imediatamente
      updateMetrics();
      
      // Configurar atualização automática a cada 5 segundos
      const interval = setInterval(updateMetrics, 5000);
      setRefreshInterval(interval);
      
      return () => {
        if (interval) clearInterval(interval);
      };
    } else {
      if (refreshInterval) {
        clearInterval(refreshInterval);
        setRefreshInterval(null);
      }
    }
  }, [isOpen]);

  const updateMetrics = () => {
    try {
      const cacheMetrics = technicianRankingCache.getMetrics();
      const cacheLogs = technicianRankingCache.getLogs(50);
      const cacheAlerts = technicianRankingCache.getAlerts();
      
      setMetrics(cacheMetrics);
      setLogs(cacheLogs);
      setAlerts(cacheAlerts);
    } catch (error) {
      console.error('Erro ao obter métricas do cache:', error);
    }
  };

  const formatDuration = (ms: number): string => {
    if (ms < 1000) return `${ms.toFixed(0)}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
    return `${(ms / 60000).toFixed(1)}min`;
  };

  const formatBytes = (bytes: number): string => {
    if (bytes < 1024) return `${bytes}B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)}MB`;
  };

  const getPerformanceColor = (score: number): string => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getAlertColor = (severity: string): string => {
    switch (severity) {
      case 'high': return 'bg-red-100 border-red-500 text-red-700';
      case 'medium': return 'bg-yellow-100 border-yellow-500 text-yellow-700';
      case 'low': return 'bg-blue-100 border-blue-500 text-blue-700';
      default: return 'bg-gray-100 border-gray-500 text-gray-700';
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-gray-50 px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <h2 className="text-xl font-semibold text-gray-800">Dashboard de Métricas do Cache</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl font-bold"
          >
            ×
          </button>
        </div>

        <div className="p-6 overflow-y-auto max-h-[calc(90vh-80px)]">
          {metrics ? (
            <div className="space-y-6">
              {/* Performance Overview */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <h3 className="text-sm font-medium text-gray-500 mb-2">Performance Score</h3>
                  <div className={`text-2xl font-bold ${getPerformanceColor(metrics.performanceScore)}`}>
                    {metrics.performanceScore.toFixed(1)}%
                  </div>
                </div>
                
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <h3 className="text-sm font-medium text-gray-500 mb-2">Hit Rate</h3>
                  <div className="text-2xl font-bold text-green-600">
                    {(metrics.hitRate * 100).toFixed(1)}%
                  </div>
                  <div className="text-xs text-gray-500">
                    {metrics.hits} hits / {metrics.totalRequests} total
                  </div>
                </div>
                
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <h3 className="text-sm font-medium text-gray-500 mb-2">Tempo de Resposta</h3>
                  <div className="text-2xl font-bold text-blue-600">
                    {metrics.avgResponseTime.toFixed(0)}ms
                  </div>
                </div>
                
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <h3 className="text-sm font-medium text-gray-500 mb-2">Uso do Cache</h3>
                  <div className="text-2xl font-bold text-purple-600">
                    {metrics.cacheSize}/{metrics.maxSize}
                  </div>
                  <div className="text-xs text-gray-500">
                    {((metrics.cacheSize / metrics.maxSize) * 100).toFixed(1)}% usado
                  </div>
                </div>
              </div>

              {/* Detailed Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Cache Statistics */}
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">Estatísticas Detalhadas</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Idade Média dos Dados:</span>
                      <span className="font-medium">{formatDuration(metrics.avgDataAge)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Invalidações/min:</span>
                      <span className="font-medium">{metrics.invalidationFrequency}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Total de Sets:</span>
                      <span className="font-medium">{metrics.sets}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Total de Deletes:</span>
                      <span className="font-medium">{metrics.deletes}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Cache Clears:</span>
                      <span className="font-medium">{metrics.clears}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Status:</span>
                      <span className={`font-medium ${
                        metrics.isActive ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {metrics.isActive ? 'Ativo' : 'Inativo'}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Alerts */}
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">
                    Alertas ({alerts.length})
                  </h3>
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {alerts.length > 0 ? (
                      alerts.map((alert, index) => (
                        <div
                          key={index}
                          className={`p-3 rounded border-l-4 ${getAlertColor(alert.severity)}`}
                        >
                          <div className="flex justify-between items-start">
                            <div>
                              <div className="font-medium">{alert.message}</div>
                              <div className="text-xs opacity-75">
                                {alert.type} • {new Date(alert.timestamp).toLocaleTimeString()}
                              </div>
                            </div>
                            <span className="text-xs font-medium uppercase">
                              {alert.severity}
                            </span>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-gray-500 text-center py-4">
                        Nenhum alerta ativo
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Recent Logs */}
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">
                  Logs Recentes ({logs.length})
                </h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full text-sm">
                    <thead>
                      <tr className="border-b border-gray-200">
                        <th className="text-left py-2 px-3 font-medium text-gray-600">Timestamp</th>
                        <th className="text-left py-2 px-3 font-medium text-gray-600">Nível</th>
                        <th className="text-left py-2 px-3 font-medium text-gray-600">Evento</th>
                        <th className="text-left py-2 px-3 font-medium text-gray-600">Detalhes</th>
                      </tr>
                    </thead>
                    <tbody className="max-h-64 overflow-y-auto">
                      {logs.slice(-20).reverse().map((log, index) => (
                        <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
                          <td className="py-2 px-3 text-gray-600">
                            {new Date(log.timestamp).toLocaleTimeString()}
                          </td>
                          <td className="py-2 px-3">
                            <span className={`px-2 py-1 rounded text-xs font-medium ${
                              log.level === 'error' ? 'bg-red-100 text-red-700' :
                              log.level === 'warn' ? 'bg-yellow-100 text-yellow-700' :
                              log.level === 'info' ? 'bg-blue-100 text-blue-700' :
                              'bg-gray-100 text-gray-700'
                            }`}>
                              {log.level.toUpperCase()}
                            </span>
                          </td>
                          <td className="py-2 px-3 font-medium">{log.event}</td>
                          <td className="py-2 px-3 text-gray-600">
                            {log.data ? (
                              <pre className="text-xs bg-gray-50 p-1 rounded overflow-x-auto">
                                {JSON.stringify(log.data, null, 2)}
                              </pre>
                            ) : (
                              log.message || '-'
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-4">
                <button
                  onClick={() => {
                    technicianRankingCache.forceCleanup();
                    updateMetrics();
                  }}
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                >
                  Limpar Logs/Alertas
                </button>
                <button
                  onClick={() => {
                    technicianRankingCache.clear();
                    updateMetrics();
                  }}
                  className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
                >
                  Limpar Cache
                </button>
                <button
                  onClick={updateMetrics}
                  className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                >
                  Atualizar Métricas
                </button>
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <div className="text-gray-600">Carregando métricas...</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RankingDebugPanel;