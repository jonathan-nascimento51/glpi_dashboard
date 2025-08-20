import React, { useState, useEffect } from 'react';
import { requestMonitor } from '../services/requestMonitor';
import type { RequestStats, RequestMetric } from '../types';

interface RequestMonitorDashboardProps {
  className?: string;
}

const RequestMonitorDashboard: React.FC<RequestMonitorDashboardProps> = ({ className = '' }) => {
  const [stats, setStats] = useState<RequestStats | null>(null);
  const [slowestRequests, setSlowestRequests] = useState<RequestMetric[]>([]);
  const [isExpanded, setIsExpanded] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState(5000); // 5 segundos

  const updateStats = () => {
    const currentStats = requestMonitor.getStats();
    const slowest = requestMonitor.getSlowestRequests(5);
    setStats(currentStats);
    setSlowestRequests(slowest);
  };

  useEffect(() => {
    updateStats();
    const interval = setInterval(updateStats, refreshInterval);
    return () => clearInterval(interval);
  }, [refreshInterval]);

  const formatDuration = (ms: number) => {
    if (ms < 1000) return `${ms.toFixed(0)}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  const getStatusColor = (errorRate: number) => {
    if (errorRate === 0) return 'text-green-600';
    if (errorRate < 0.1) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (!stats) {
    return (
      <div className={`bg-white rounded-lg shadow p-4 ${className}`}>
        <div className='animate-pulse'>
          <div className='h-4 bg-gray-200 rounded w-1/4 mb-2'></div>
          <div className='h-8 bg-gray-200 rounded w-1/2'></div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg shadow ${className}`}>
      {/* Header */}
      <div
        className='p-4 border-b cursor-pointer hover:bg-gray-50 transition-colors'
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className='flex items-center justify-between'>
          <div className='flex items-center space-x-3'>
            <div className='w-3 h-3 bg-blue-500 rounded-full animate-pulse'></div>
            <h3 className='text-lg font-semibold text-gray-900'>Monitor de Requisições</h3>
          </div>
          <div className='flex items-center space-x-4'>
            <div className='text-sm text-gray-600'>{stats.totalRequests} requisições</div>
            <div className={`text-sm font-medium ${getStatusColor(stats.errorRate)}`}>
              {formatPercentage(stats.errorRate)} erros
            </div>
            <svg
              className={`w-5 h-5 text-gray-400 transition-transform ${
                isExpanded ? 'rotate-180' : ''
              }`}
              fill='none'
              stroke='currentColor'
              viewBox='0 0 24 24'
            >
              <path
                strokeLinecap='round'
                strokeLinejoin='round'
                strokeWidth={2}
                d='M19 9l-7 7-7-7'
              />
            </svg>
          </div>
        </div>
      </div>

      {/* Métricas principais */}
      <div className='p-4'>
        <div className='grid grid-cols-2 md:grid-cols-4 gap-4'>
          <div className='text-center'>
            <div className='text-2xl font-bold text-blue-600'>{stats.totalRequests}</div>
            <div className='text-sm text-gray-600'>Total</div>
          </div>

          <div className='text-center'>
            <div className='text-2xl font-bold text-green-600'>{stats.successfulRequests}</div>
            <div className='text-sm text-gray-600'>Sucesso</div>
          </div>

          <div className='text-center'>
            <div className='text-2xl font-bold text-orange-600'>{stats.cachedRequests}</div>
            <div className='text-sm text-gray-600'>Cache</div>
          </div>

          <div className='text-center'>
            <div className='text-2xl font-bold text-purple-600'>
              {formatDuration(stats.averageResponseTime)}
            </div>
            <div className='text-sm text-gray-600'>Tempo Médio</div>
          </div>
        </div>
      </div>

      {/* Detalhes expandidos */}
      {isExpanded && (
        <div className='border-t'>
          {/* Configurações */}
          <div className='p-4 bg-gray-50'>
            <div className='flex items-center justify-between mb-4'>
              <h4 className='font-medium text-gray-900'>Configurações</h4>
              <div className='flex items-center space-x-2'>
                <label className='text-sm text-gray-600'>Atualização:</label>
                <select
                  value={refreshInterval}
                  onChange={e => setRefreshInterval(Number(e.target.value))}
                  className='text-sm border rounded px-2 py-1'
                >
                  <option value={1000}>1s</option>
                  <option value={5000}>5s</option>
                  <option value={10000}>10s</option>
                  <option value={30000}>30s</option>
                </select>
              </div>
            </div>

            <div className='grid grid-cols-2 md:grid-cols-3 gap-4 text-sm'>
              <div>
                <span className='text-gray-600'>Taxa de Erro:</span>
                <span className={`ml-2 font-medium ${getStatusColor(stats.errorRate)}`}>
                  {formatPercentage(stats.errorRate)}
                </span>
              </div>
              <div>
                <span className='text-gray-600'>Cache Hit Rate:</span>
                <span className='ml-2 font-medium text-green-600'>
                  {formatPercentage(stats.cacheHitRate)}
                </span>
              </div>
              <div>
                <span className='text-gray-600'>Req/min:</span>
                <span className='ml-2 font-medium text-blue-600'>
                  {stats.requestsPerMinute.toFixed(1)}
                </span>
              </div>
            </div>
          </div>

          {/* Requisições mais lentas */}
          {slowestRequests.length > 0 && (
            <div className='p-4'>
              <h4 className='font-medium text-gray-900 mb-3'>Requisições Mais Lentas</h4>
              <div className='space-y-2'>
                {slowestRequests.map((request, index) => (
                  <div key={request.id} className='flex items-center justify-between text-sm'>
                    <div className='flex items-center space-x-2'>
                      <span className='w-4 h-4 bg-red-100 text-red-600 rounded-full flex items-center justify-center text-xs font-bold'>
                        {index + 1}
                      </span>
                      <span className='font-mono text-gray-600'>{request.method}</span>
                      <span className='text-gray-900 truncate max-w-xs'>{request.endpoint}</span>
                    </div>
                    <div className='flex items-center space-x-2'>
                      <span className='font-medium text-red-600'>
                        {formatDuration(request.duration || 0)}
                      </span>
                      {request.cacheHit && (
                        <span className='px-2 py-1 bg-green-100 text-green-600 rounded text-xs'>
                          Cache
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Endpoints mais utilizados */}
          {stats.topEndpoints.length > 0 && (
            <div className='p-4 border-t'>
              <h4 className='font-medium text-gray-900 mb-3'>Endpoints Mais Utilizados</h4>
              <div className='space-y-2'>
                {stats.topEndpoints.map((endpoint, index) => (
                  <div
                    key={endpoint.endpoint}
                    className='flex items-center justify-between text-sm'
                  >
                    <div className='flex items-center space-x-2'>
                      <span className='w-4 h-4 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-bold'>
                        {index + 1}
                      </span>
                      <span className='text-gray-900 truncate max-w-xs'>{endpoint.endpoint}</span>
                    </div>
                    <div className='flex items-center space-x-3'>
                      <span className='text-gray-600'>{endpoint.count} calls</span>
                      <span className='text-gray-600'>{formatDuration(endpoint.avgDuration)}</span>
                      <span className={`font-medium ${getStatusColor(endpoint.errorRate)}`}>
                        {formatPercentage(endpoint.errorRate)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Ações */}
          <div className='p-4 border-t bg-gray-50'>
            <div className='flex items-center justify-between'>
              <button
                onClick={() => requestMonitor.clear()}
                className='px-3 py-1 bg-red-100 text-red-600 rounded hover:bg-red-200 transition-colors text-sm'
              >
                Limpar Histórico
              </button>
              <button
                onClick={() => {
                  const data = requestMonitor.exportData();
                  const blob = new Blob([JSON.stringify(data, null, 2)], {
                    type: 'application/json',
                  });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `request-monitor-${new Date().toISOString().slice(0, 19)}.json`;
                  a.click();
                  URL.revokeObjectURL(url);
                }}
                className='px-3 py-1 bg-blue-100 text-blue-600 rounded hover:bg-blue-200 transition-colors text-sm'
              >
                Exportar Dados
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RequestMonitorDashboard;
